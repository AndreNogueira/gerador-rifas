"""SEO: <head> por rota, texto estatico para robos, robots.txt, sitemap.xml, 404 a serio e o que nao deve ser indexado."""
import json
import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import app as modulo_app
from core import i18n, tutorial
from web import changelog, guias, seo
from web.app import criar_app

INDEX = (
    '<!doctype html><html lang="pt"><head><meta charset="UTF-8" />\n    <!--seo:cabecalho-->\n</head>'
    '<body><noscript>JS</noscript><div id="raiz"><!--seo:corpo--></div><script type="module" src="/assets/a.js"></script></body></html>'
)
URL = "https://rifas.exemplo.pt"


@pytest.fixture(autouse=True)
def sem_url_do_ambiente(monkeypatch):
    for nome in ("PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def cliente(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    (dist / "assets" / "a.js").write_text("1", encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"))


@pytest.fixture
def publico(cliente, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", URL)
    return cliente


def _meta(html: str, atributo: str, nome: str) -> str:
    m = re.search(rf'<meta {atributo}="{re.escape(nome)}" content="([^"]*)"', html)
    assert m, f"falta <meta {atributo}={nome}>"
    return m.group(1)


@pytest.mark.parametrize("caminho", list(seo.ROTAS))
def test_cada_pagina_tem_titulo_descricao_canonico_og_e_um_h1(publico, caminho):
    r = publico.get(caminho)
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    h = r.text
    titulo = re.search(r"<title>([^<]+)</title>", h).group(1)
    descricao = _meta(h, "name", "description")
    assert 10 <= len(titulo) <= 65, (caminho, len(titulo))
    assert 60 <= len(descricao) <= 160, (caminho, len(descricao))
    esperado = f"{URL}/" if caminho == "/" else f"{URL}{caminho}"
    assert f'<link rel="canonical" href="{esperado}" />' in h
    assert _meta(h, "property", "og:url") == esperado
    assert _meta(h, "property", "og:title") == titulo and _meta(h, "property", "og:description") == descricao
    assert _meta(h, "property", "og:image") == f"{URL}/og-imagem.png"
    assert _meta(h, "name", "twitter:card") == "summary_large_image"
    assert "index,follow" in _meta(h, "name", "robots")
    assert h.count("<title>") == 1 and h.count('rel="canonical"') == 1             # nada duplicado
    corpo = h.split('<div id="raiz">')[1].split("</div><script")[0]
    assert corpo.count("<h1>") == 1 and "seo-estatico" in corpo
    assert "<!--seo:" not in h


CODIGO_GOOGLE = "aB3_dE-fG7hI9jK1lM2nO4pQ6rS8tU0vW"


def test_verificacao_do_google_so_na_pagina_inicial_e_so_se_definida(publico, monkeypatch):
    monkeypatch.delenv("GOOGLE_VERIFICACAO", raising=False)
    assert "google-site-verification" not in publico.get("/").text
    monkeypatch.setenv("GOOGLE_VERIFICACAO", CODIGO_GOOGLE)
    for caminho in ("/", "/en"):
        h = publico.get(caminho).text
        assert _meta(h, "name", "google-site-verification") == CODIGO_GOOGLE
        assert h.count("google-site-verification") == 1
    assert "google-site-verification" not in publico.get("/tutorial").text


@pytest.mark.parametrize("valor", ['curto', 'x" /><script>alert(1)</script>' + "a" * 30, "tem espacos " * 4, "a" * 200])
def test_verificacao_do_google_invalida_e_ignorada(publico, monkeypatch, valor):
    monkeypatch.setenv("GOOGLE_VERIFICACAO", valor)
    assert "google-site-verification" not in publico.get("/").text


def test_a_pagina_inicial_tem_dados_estruturados_validos(publico):
    h = publico.get("/").text
    blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h)
    assert len(blocos) == 1
    d = json.loads(blocos[0])
    assert d["@context"] == "https://schema.org"
    grafo = {bloco["@type"]: bloco for bloco in d["@graph"]}
    assert set(grafo) == {"WebApplication", "Organization", "WebSite"}
    app_ = grafo["WebApplication"]
    assert app_["url"] == f"{URL}/" and app_["offers"]["price"] == "0"
    assert len(app_["inLanguage"]) == len(i18n.LINGUAS) and app_["image"] == f"{URL}/og-imagem.png"
    org = grafo["Organization"]
    assert org["name"] == "Gerador de Rifas" and org["url"] == f"{URL}/" and org["logo"] == f"{URL}/icone-512.png"
    assert "aggregateRating" not in app_ and "review" not in app_
    site = grafo["WebSite"]
    assert site["url"] == f"{URL}/" and "potentialAction" not in site
    for caminho in ("/tutorial", "/video", "/sobre", "/sorteio", "/editor", "/termos", "/privacidade", "/contacto", "/changelog"):
        assert "ld+json" not in publico.get(caminho).text


def test_o_tutorial_leva_o_texto_real_de_todos_os_topicos(publico):
    h = publico.get("/tutorial").text
    assert h.count("<section><h2>") == len(tutorial.lista_de_topicos("web")) == 8 + len(tutorial.funcionalidades("web")) and "{" not in h.split('<div id="raiz">')[1].split("<script")[0]


def test_robots_txt(publico):
    r = publico.get("/robots.txt")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    linhas = r.text.splitlines()
    assert "User-agent: *" in linhas and "Disallow: /api/" in linhas and "Disallow: /admin" in linhas
    assert f"Sitemap: {URL}/sitemap.xml" in linhas
    assert not any(l.strip() == "Disallow: /" or "/assets" in l for l in linhas)   # os robos precisam do JS e do CSS


def test_robots_txt_deixa_entrar_nas_rotas_que_o_react_precisa_e_na_doc_da_api_publica(publico):
    # dentro de /api/ (que fica bloqueado): o que o proprio site pede ao reescrever a pagina com JS, e a doc da API v1
    # (RFC 9309: a regra Allow mais longa ganha a Disallow: /api/, por isso continuam acessiveis a quem respeita o robots.txt)
    linhas = publico.get("/robots.txt").text.splitlines()
    for rota in ("/api/linguas", "/api/textos/", "/api/guia/", "/api/guias", "/api/v1/docs", "/api/v1/openapi.json"):
        assert f"Allow: {rota}" in linhas, rota


def test_sitemap_so_tem_as_paginas_publicas(publico):
    r = publico.get("/sitemap.xml")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [e.text for e in ElementTree.fromstring(r.text).findall("s:url/s:loc", ns)]
    paginas = ["/", "/tutorial", "/video", "/sobre", "/sorteio", "/editor", "/como-fazer", "/rifas-para-escolas", "/rifas-para-associacoes", "/rifas-para-clubes", "/rifas-para-bombeiros", "/rifas-para-festas", "/rifas-para-igrejas", "/precario", "/como-fazer-o-precario-de-uma-festa", "/como-numerar-bilhetes-de-rifa", "/sorteio-de-rifa-verificavel", "/quantos-bilhetes-de-rifa-fazer", "/termos", "/privacidade", "/contacto", "/changelog"]
    assert urls[::len(i18n.LINGUAS)] == [f"{URL}{c}" for c in paginas]                    # por pagina: primeiro o portugues (sem prefixo), depois as outras com prefixo (ver test_web_seo_linguas.py)
    assert len(urls) == 22 * len(i18n.LINGUAS) and len(set(urls)) == len(urls)


def test_sitemap_tem_lastmod_da_versao_atual(publico):
    r = publico.get("/sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    raiz = ElementTree.fromstring(r.text)
    datas = {e.text for e in raiz.findall("s:url/s:lastmod", ns)}
    assert datas == {changelog.entradas("pt")[0].data}                # a data da versao atual (CHANGELOG.md), igual em todas as paginas
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", datas.pop())
    for url in raiz.findall("s:url", ns):                             # <lastmod> logo depois de <loc>, antes das alternativas de lingua
        filhos = [e.tag.split("}")[-1] for e in url]
        assert filhos[:2] == ["loc", "lastmod"]


def test_llms_txt(publico):
    r = publico.get("/llms.txt")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    assert f"{URL}/como-fazer" in r.text and f"{URL}/api/v1/docs" in r.text


def test_rotas_desconhecidas_sao_404_a_serio_e_nao_se_indexam(publico):
    for caminho in ("/nao-existe", "/tutorial/x", "/admin/x", "/index.php"):
        r = publico.get(caminho)
        assert r.status_code == 404, caminho
        assert "noindex" in _meta(r.text, "name", "robots") and 'rel="canonical"' not in r.text


def test_barra_final_redireciona_e_index_html_e_a_pagina_inicial(publico):
    r = publico.get("/tutorial/", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/tutorial"
    r = publico.get("/index.html")
    assert r.status_code == 200 and f'<link rel="canonical" href="{URL}/" />' in r.text
    assert publico.get("/tutorial?p=3").status_code == 200                           # a query nao conta


def test_a_api_nao_se_indexa(publico):
    assert publico.get("/api/linguas").headers["x-robots-tag"] == "noindex, nofollow"
    assert publico.get("/health").headers["x-robots-tag"] == "noindex, nofollow"
    assert "x-robots-tag" not in publico.get("/tutorial").headers


def test_o_canonico_nao_se_deixa_envenenar_pelo_cabecalho_host(publico):
    h = publico.get("/", headers={"Host": "evil.example", "X-Forwarded-Host": "evil.example"}).text
    assert "evil.example" not in h and f'href="{URL}/"' in h


def test_sem_url_configurado_usa_o_do_pedido(cliente):
    h = cliente.get("/").text
    assert 'rel="canonical" href="http://testserver/"' in h


def test_render_external_url_serve_de_reserva(cliente, monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://gerador-rifas.onrender.com/")
    assert 'href="https://gerador-rifas.onrender.com/"' in cliente.get("/").text
    monkeypatch.setenv("PUBLIC_URL", URL)                                          # PUBLIC_URL ganha
    assert f'href="{URL}/"' in cliente.get("/").text


@pytest.mark.parametrize("valor", ["javascript:alert(1)", "ftp://x", "https://a b", "https://x/<script>", ""])
def test_url_publico_invalido_e_ignorado(cliente, monkeypatch, valor):
    monkeypatch.setenv("PUBLIC_URL", valor)
    assert "http://testserver/" in cliente.get("/").text


def test_o_html_nao_se_deixa_injetar_pelo_titulo_nem_pelo_url(publico):
    h = seo.renderizar(INDEX, seo.Pagina("/x", "d_inicio", lambda lg: "<h1>x</h1>", titulo_fixo='a"><script>alert(1)</script>'), 'https://a"b')
    assert "<script>alert" not in h and "&quot;&gt;&lt;script&gt;" in h


def test_o_index_real_tem_os_marcadores():
    """O frontend de verdade (`src/web/frontend/index.html`) tem de ter os dois marcadores que o servidor preenche."""
    fonte = Path(modulo_app.__file__).parent / "frontend" / "index.html"
    html = fonte.read_text(encoding="utf-8")
    assert seo.MARCADOR_CABECALHO in html and seo.MARCADOR_CORPO in html and "<title>" not in html


def test_a_pagina_inicial_liga_aos_guias_em_todas_as_linguas(cliente):
    """Os guias saíram do rodapé (vivem num menu do cabeçalho): o HTML estático da página inicial é o que os liga para os robôs."""
    for lg in i18n.LINGUAS:
        caminho = "/" if lg == "pt" else f"/{lg}/"
        html = cliente.get(caminho).text
        for destino in ("escolas", "associacoes", "clubes", "bombeiros", "festas", "igrejas", "numerar", "sorteio", "quantos", "precario"):
            caminho_guia = guias.CAMINHOS[destino]
            esperado = caminho_guia if lg == "pt" else f"/{lg}{caminho_guia}"
            assert f'href="{esperado}"' in html, (lg, destino)


def test_a_pagina_inicial_liga_tambem_ao_indice_dos_guias(cliente):
    """`/como-fazer` (o índice) não é só um guia: sem esta ligação não tinha nenhuma entrada a partir da página inicial."""
    assert 'href="/como-fazer"' in cliente.get("/").text
    assert 'href="/en/como-fazer"' in cliente.get("/en/").text


def test_os_guias_de_sorteio_e_precario_ligam_a_sua_propria_ferramenta(cliente):
    """Ao contrário dos outros guias (por público, que ligam ao gerador «/»), estes dois guias são por TEMA e têm a sua própria página."""
    sorteio = cliente.get(guias.CAMINHOS["sorteio"]).text
    assert 'href="/sorteio"' in sorteio
    precario = cliente.get(guias.CAMINHOS["precario"]).text
    assert 'href="/precario"' in precario
    escolas = cliente.get(guias.CAMINHOS["escolas"]).text
    assert 'href="/"' in escolas


# ------------------------------------------------------------------ o índice de guias, as ligações entre guias e as migalhas de pão
def test_o_indice_lista_todos_os_guias_e_cada_guia_liga_aos_outros_e_ao_indice(cliente, publico):
    from web import guias

    indice = cliente.get("/como-fazer").text
    for nome in guias.NOMES:
        assert f'href="{guias.CAMINHOS[nome]}"' in indice
    assert "<h1>Como fazer uma rifa: guias passo a passo</h1>" in indice and f'<link rel="canonical" href="{URL}/como-fazer" />' in indice
    en = cliente.get("/en/como-fazer").text
    assert 'href="/en/rifas-para-escolas"' in en and "<h1>How to run a raffle: step-by-step guides</h1>" in en
    escolas = cliente.get("/rifas-para-escolas").text
    assert "<h2>Outros guias</h2>" in escolas and 'href="/como-fazer"' in escolas
    assert 'href="/rifas-para-clubes"' in escolas and 'href="/rifas-para-escolas"' not in escolas.split("<h2>Outros guias</h2>")[1]       # liga aos outros, nunca a si próprio


def test_as_migalhas_de_pao_dos_guias_e_do_indice():
    import json
    import re

    def migalhas(html):
        m = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        return next(x for x in m if x["@type"] == "BreadcrumbList")

    from web import seo
    base = "https://rifas.exemplo.pt"
    html_base = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'
    guia = migalhas(seo.renderizar(html_base, seo.ROTAS["/rifas-para-escolas"], base, "pt"))
    assert [i["name"] for i in guia["itemListElement"]] == ["Gerador de Rifas", "Como fazer uma rifa: guias passo a passo", "Como fazer uma rifa para a escola"]
    assert [i["item"] for i in guia["itemListElement"]] == [f"{base}/", f"{base}/como-fazer", f"{base}/rifas-para-escolas"] and [i["position"] for i in guia["itemListElement"]] == [1, 2, 3]
    en = migalhas(seo.renderizar(html_base, seo.ROTAS["/rifas-para-escolas"], base, "en"))
    assert en["itemListElement"][2]["item"] == f"{base}/en/rifas-para-escolas"
    assert len(migalhas(seo.renderizar(html_base, seo.ROTAS["/como-fazer"], base, "pt"))["itemListElement"]) == 2
    assert not re.findall(r"BreadcrumbList", seo.renderizar(html_base, seo.ROTAS["/tutorial"], base, "pt"))                              # só nos guias e no índice


# ------------------------------------------------------------------ Article (D1) e Organization (D2)
def _grafo(html):
    blocos = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    return next(b for b in blocos if "@graph" in b and any(n.get("@type") == "Article" for n in b["@graph"]))


def test_os_guias_tem_article_nunca_howto(publico):
    base = URL
    h = publico.get("/rifas-para-escolas").text
    grafo = _grafo(h)
    artigo = next(n for n in grafo["@graph"] if n["@type"] == "Article")
    org = next(n for n in grafo["@graph"] if n["@type"] == "Organization")
    assert artigo["headline"] == "Como fazer uma rifa para a escola"
    assert artigo["url"] == f"{base}/rifas-para-escolas" and artigo["mainEntityOfPage"] == artigo["url"]
    assert artigo["inLanguage"] == "pt" and artigo["image"] == f"{base}/og-imagem.png"
    assert artigo["publisher"] == {"@id": f"{base}/#organizacao"} and org["@id"] == f"{base}/#organizacao"
    assert artigo["datePublished"] == guias.DATAS_CRIACAO["escolas"]
    for caminho in seo.ROTAS:
        assert "HowTo" not in publico.get(caminho).text, caminho               # tipo descontinuado: nunca usar


def test_os_guias_sem_article_fora_das_paginas_de_guia(publico):
    assert '"@type":"Article"' not in publico.get("/tutorial").text
    assert '"@type":"Article"' not in publico.get("/").text


def test_todos_os_guias_tem_data_de_criacao_honesta_no_ficheiro():
    assert set(guias.DATAS_CRIACAO) == set(guias.CAMINHOS), "guia novo: acrescenta a data do commit que o cria a guias.DATAS_CRIACAO"
    for nome, data in guias.DATAS_CRIACAO.items():
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", data), (nome, data)


def test_o_autor_do_artigo_so_aparece_com_responsavel_configurado(publico, monkeypatch):
    monkeypatch.delenv("RESPONSAVEL", raising=False)
    artigo = next(n for n in _grafo(publico.get("/rifas-para-escolas").text)["@graph"] if n["@type"] == "Article")
    assert "author" not in artigo
    monkeypatch.setenv("RESPONSAVEL", "Ana Silva")
    artigo = next(n for n in _grafo(publico.get("/rifas-para-escolas").text)["@graph"] if n["@type"] == "Article")
    assert artigo["author"] == {"@type": "Person", "name": "Ana Silva"}


def test_a_organizacao_tem_sameas_e_so_tem_founder_e_contactpoint_configurados(publico, monkeypatch):
    monkeypatch.delenv("RESPONSAVEL", raising=False)
    monkeypatch.delenv("CONTACTO_EMAIL", raising=False)
    h = publico.get("/").text
    blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h)
    org = next(json.loads(x)["@graph"] for x in blocos if '"@type":"WebApplication"' in x)
    org = next(n for n in org if n["@type"] == "Organization")
    assert org["sameAs"] == ["https://github.com/AndreNogueira/gerador-rifas-windows"]
    assert "founder" not in org and "contactPoint" not in org
    monkeypatch.setenv("RESPONSAVEL", "Ana Silva")
    monkeypatch.setenv("CONTACTO_EMAIL", "ola@exemplo.pt")
    org = next(json.loads(x)["@graph"] for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', publico.get("/").text) if '"@type":"WebApplication"' in x)
    org = next(n for n in org if n["@type"] == "Organization")
    assert org["founder"] == {"@type": "Person", "name": "Ana Silva"}
    assert org["contactPoint"] == {"@type": "ContactPoint", "email": "ola@exemplo.pt", "contactType": "customer support"}


def test_a_api_dos_guias_devolve_titulo_e_resumo_na_lingua(cliente):
    pt = cliente.get("/api/guias", headers={"X-Lingua": "pt"}).json()["guias"]
    assert [g["nome"] for g in pt] == ["escolas", "associacoes", "clubes", "bombeiros", "festas", "igrejas", "numerar", "sorteio", "quantos", "precario"] and pt[0]["caminho"] == "/rifas-para-escolas"
    assert pt[0]["titulo"] == "Como fazer uma rifa para a escola" and pt[0]["resumo"].endswith(".") and len(pt[0]["resumo"]) <= 175
    assert cliente.get("/api/guias", headers={"X-Lingua": "en"}).json()["guias"][0]["titulo"] == "How to run a raffle for your school"
