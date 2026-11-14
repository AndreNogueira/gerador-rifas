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
from web import seo
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
    assert d["@type"] == "WebApplication" and d["url"] == f"{URL}/" and d["offers"]["price"] == "0"
    assert len(d["inLanguage"]) == len(i18n.LINGUAS) and d["image"] == f"{URL}/og-imagem.png"
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


def test_sitemap_so_tem_as_paginas_publicas(publico):
    r = publico.get("/sitemap.xml")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [e.text for e in ElementTree.fromstring(r.text).findall("s:url/s:loc", ns)]
    paginas = ["/", "/tutorial", "/video", "/sobre", "/sorteio", "/editor", "/rifas-para-escolas", "/rifas-para-associacoes", "/rifas-para-clubes", "/rifas-para-bombeiros", "/rifas-para-festas", "/rifas-para-igrejas", "/termos", "/privacidade", "/contacto", "/changelog"]
    assert urls[::len(i18n.LINGUAS)] == [f"{URL}{c}" for c in paginas]                    # por pagina: primeiro o portugues (sem prefixo), depois as outras com prefixo (ver test_web_seo_linguas.py)
    assert len(urls) == 16 * len(i18n.LINGUAS) and len(set(urls)) == len(urls)


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
        for destino in ("escolas", "associacoes", "clubes", "bombeiros", "festas", "igrejas"):
            esperado = f"/rifas-para-{destino}" if lg == "pt" else f"/{lg}/rifas-para-{destino}"
            assert f'href="{esperado}"' in html, (lg, destino)
