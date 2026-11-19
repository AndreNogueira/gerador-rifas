"""SEO por língua: um URL por língua (`/en/tutorial`), HTML na língua do URL, `hreflang`, canónico e sitemap com as 18 alternativas."""
import re
import unicodedata
from pathlib import Path
from xml.etree import ElementTree

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import changelog, seo, seo_textos
from web.app import criar_app

INDEX = (
    '<!doctype html><html lang="pt"><head><meta charset="UTF-8" />\n    <!--seo:cabecalho-->\n</head>'
    '<body><noscript>JS</noscript><div id="raiz"><!--seo:corpo--></div><script type="module" src="/assets/a.js"></script></body></html>'
)
URL = "https://rifas.exemplo.pt"
LINGUAS = list(i18n.LINGUAS)
OUTRAS = [lg for lg in LINGUAS if lg != "pt"]
TRADUZIDAS = [lg for lg in OUTRAS if lg != "pt-br"]            # o português do Brasil deriva-se do de Portugal (`core/ptbr.py`): pode coincidir em textos sem vocabulário próprio
RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def c(tmp_path, monkeypatch):
    for nome in ("RENDER_EXTERNAL_URL", "ADMIN_TOKEN"):
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setenv("PUBLIC_URL", URL)
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"))


def _meta(h: str, atributo: str, nome: str) -> str:
    m = re.search(rf'<meta {atributo}="{re.escape(nome)}" content="([^"]*)"', h)
    assert m, f"falta <meta {atributo}={nome}>"
    return m.group(1)


# ------------------------------------------------------------------ os textos
def test_cada_texto_de_seo_tem_as_18_linguas_e_os_mesmos_parametros():
    marcador = re.compile(r"\{(\w+)\}")
    for chave, por_lingua in seo_textos.CHAVES.items():
        assert set(por_lingua) == set(LINGUAS), chave
        for lg, t in por_lingua.items():
            assert t.strip(), (chave, lg)
            assert set(marcador.findall(t)) == set(marcador.findall(por_lingua["pt"])), (chave, lg)
    assert set(seo_textos.LOCALE_OG) == set(LINGUAS)


@pytest.mark.parametrize("lg", TRADUZIDAS)
def test_os_textos_de_seo_estao_traduzidos_e_nao_sao_o_portugues(lg):
    for chave, por_lingua in seo_textos.CHAVES.items():
        assert por_lingua[lg] != por_lingua["pt"], (chave, lg)


def test_a_lista_de_linguas_do_router_do_frontend_e_a_do_servidor():
    fonte = (RAIZ / "src" / "web" / "frontend" / "src" / "rota.tsx").read_text(encoding="utf-8")
    m = re.search(r"LINGUAS_COM_PREFIXO\s*=\s*\[([^\]]*)\]", fonte)
    assert m, "rota.tsx tem de declarar LINGUAS_COM_PREFIXO"
    assert re.findall(r'"([a-z]{2}(?:-[a-z]{2})?)"', m.group(1)) == list(seo.LINGUAS_URL)


# ------------------------------------------------------------------ as páginas
@pytest.mark.parametrize("lg", LINGUAS)
@pytest.mark.parametrize("caminho", list(seo.ROTAS))
def test_cada_pagina_sai_na_lingua_do_url_com_canonico_hreflang_e_h1(c, caminho, lg):
    url = seo.caminho_na_lingua(caminho, lg)
    r = c.get(url)
    assert r.status_code == 200 and r.headers["content-language"] == i18n.bcp47(lg), (url, r.status_code)
    h = r.text
    assert f'<html lang="{i18n.bcp47(lg)}"' in h
    esperado = f"{URL}/" if url == "/" else f"{URL}{url}"
    assert f'<link rel="canonical" href="{esperado}" />' in h
    assert _meta(h, "property", "og:locale") == seo_textos.LOCALE_OG[lg] and _meta(h, "property", "og:url") == esperado
    alternativas = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)" />', h)
    assert [a for a, _ in alternativas] == [i18n.bcp47(x) for x in LINGUAS] + ["x-default"]
    assert dict(alternativas)["x-default"] == (f"{URL}/" if caminho == "/" else f"{URL}{caminho}")        # o x-default é o português, sem prefixo
    assert dict(alternativas)[i18n.bcp47(lg)] == esperado
    titulo = re.search(r"<title>([^<]+)</title>", h).group(1)
    descricao = _meta(h, "name", "description")
    assert 8 <= len(titulo) <= 90 and 20 <= len(descricao) <= 200, (url, len(titulo), len(descricao))
    assert len(re.findall(r"<h1>", h)) == 1 and "{" not in h.split('<div class="seo-estatico">')[1], url
    if lg not in ("pt", "pt-br"):                  # o do Brasil deriva-se do de Portugal (core/ptbr.py): pode coincidir
        pt = c.get(caminho).text
        assert re.search(r"<title>([^<]+)</title>", pt).group(1) != titulo or caminho == "/changelog"
        assert _meta(pt, "name", "description") != descricao


def test_o_titulo_da_pagina_inicial_leva_o_nome_da_app_na_lingua(c):
    assert "くじ券ジェネレーター" in c.get("/ja").text and "Gerador de Rifas" in c.get("/").text and "Raffle" in c.get("/en").text
    assert "くじ券ジェネレーター" in re.search(r"<title>([^<]+)</title>", c.get("/ja/tutorial").text).group(1)


def test_o_tutorial_e_o_changelog_em_html_vem_traduzidos(c):
    assert "Step by step" in c.get("/en/tutorial").text or "step by step" in c.get("/en/tutorial").text.lower()
    primeira = changelog.entradas("en")[0]
    assert primeira.seccoes[0].itens[0][:30].replace("**", "") in c.get("/en/changelog").text.replace("**", "")
    assert "Terms" in re.search(r"<h1>([^<]+)</h1>", c.get("/en/termos").text).group(1)


def test_os_links_do_corpo_levam_o_prefixo_da_lingua(c):
    h = c.get("/en").text
    assert 'href="/en/tutorial"' in h and 'href="/en/video"' in h and 'href="/tutorial"' not in h
    assert 'href="/tutorial"' in c.get("/").text


def test_o_json_ld_da_pagina_inicial_e_na_lingua(c):
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', c.get("/es").text).group(1)
    assert f'"url":"{URL}/es"' in ld and '"inLanguage"' in ld and "Rifas numeradas" in ld


# ------------------------------------------------------------------ redirecionamentos e 404
@pytest.mark.parametrize("pedido, destino", [("/pt/tutorial", "/tutorial"), ("/pt", "/"), ("/pt/", "/"), ("/en/", "/en"),
                                              ("/en/tutorial/", "/en/tutorial"), ("/pt/tutorial/", "/tutorial")])
def test_um_so_url_por_pagina_e_lingua(c, pedido, destino):
    r = c.get(pedido, follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == destino


@pytest.mark.parametrize("caminho", ["/xx/tutorial", "/en/nao-existe", "/en/admin", "/en/api/linguas", "/EN/tutorial", "/en/en", "/en/tutorial/x"])
def test_o_que_nao_existe_nas_linguas_e_404_a_serio(c, caminho):
    r = c.get(caminho)
    assert r.status_code == 404 and "noindex" in _meta(r.text, "name", "robots") and 'rel="canonical"' not in r.text


def test_o_painel_nao_tem_versao_por_lingua_nem_com_token(c, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "um-token-de-teste-com-16+")
    assert c.get("/admin").status_code == 200 and c.get("/en/admin").status_code == 404


def test_sem_prefixo_e_sempre_portugues_mesmo_com_accept_language(c):
    r = c.get("/tutorial", headers={"Accept-Language": "en-US,en;q=0.9"})
    assert r.status_code == 200 and '<html lang="pt"' in r.text and r.headers["content-language"] == "pt"


# ------------------------------------------------------------------ sitemap
def test_o_sitemap_lista_cada_pagina_em_todas_as_linguas_com_as_alternativas(c):
    r = c.get("/sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
    raiz = ElementTree.fromstring(r.text)
    entradas = raiz.findall("s:url", ns)
    assert len(entradas) == len(seo.ROTAS) * len(i18n.LINGUAS)
    for e in entradas:
        links = e.findall("x:link", ns)
        assert [(lk.get("hreflang")) for lk in links] == [i18n.bcp47(x) for x in LINGUAS] + ["x-default"]
        assert e.find("s:loc", ns).text in [lk.get("href") for lk in links]
    locs = [e.find("s:loc", ns).text for e in entradas]
    assert f"{URL}/en" in locs and f"{URL}/ja/tutorial" in locs and f"{URL}/tutorial" in locs and f"{URL}/pt/tutorial" not in locs


def test_o_robots_nao_bloqueia_as_linguas(c):
    r = c.get("/robots.txt").text
    assert "Allow: /" in r and "Disallow: /en" not in r and f"Sitemap: {URL}/sitemap.xml" in r


def _largura(texto: str) -> int:
    """Largura aproximada no resultado de pesquisa: os caracteres CJK ocupam o dobro."""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in texto)


@pytest.mark.parametrize("lg", LINGUAS)
def test_titulos_e_descricoes_cabem_no_resultado_de_pesquisa(lg):
    """O Google corta os títulos por volta dos 60 caracteres e as descrições por volta dos 155 (CJK conta a dobrar)."""
    for caminho, pagina in seo.ROTAS.items():
        assert _largura(pagina.titulo(lg)) <= 66, (lg, caminho, pagina.titulo(lg))
        assert 50 <= _largura(pagina.descricao(lg)) <= 158, (lg, caminho, _largura(pagina.descricao(lg)))


@pytest.mark.parametrize("lg", [lg for lg in LINGUAS if lg != "pt"])
def test_as_descricoes_usam_o_nome_do_produto_nessa_lingua(lg):
    """Quem vem do Google lê o nome da app na língua; o texto não pode chamar-lhe outra coisa (ex. «Los-Generator» vs «Tombola-Generator»)."""
    nome = i18n.traduzir("app_nome", lg).lower()
    for chave in ("d_sobre", "d_termos", "d_privacidade", "d_contacto", "d_changelog"):
        t = seo_textos.CHAVES[chave][lg].lower()
        raiz = nome.split()[-1][:5]          # a palavra distintiva (declina em pl, cs, ru, el, tr), sem o fim
        assert raiz in t, (lg, chave, nome)
