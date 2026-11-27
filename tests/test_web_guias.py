"""As páginas de «como fazer» (escolas e associações): 18 línguas com a mesma estrutura, a API, o HTML estático para os motores de pesquisa e o sitemap."""
import html
import re

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import guias, seo
from web.app import criar_app
from web.trabalhos import Motor

URL = "https://rifas.exemplo.pt"
LINGUAS = list(i18n.LINGUAS)


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def c(tmp_path, motor, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", URL)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor)) as cliente:
        yield cliente


@pytest.mark.parametrize("nome", guias.NOMES)
def test_cada_guia_tem_as_18_linguas(nome):
    assert set(guias.DADOS[nome]) == set(LINGUAS)


@pytest.mark.parametrize("nome", guias.NOMES)
@pytest.mark.parametrize("lg", LINGUAS)
def test_estrutura_igual_em_todas_as_linguas(nome, lg):
    g = guias.guia(nome, lg)
    assert 8 <= len(g["titulo"]) <= 60 and len(g["intro"]) > 60 and len(g["fim"]) > 10
    assert len(g["passos"]) == guias.N_PASSOS and len(g["dicas"]) == guias.N_DICAS
    for p in g["passos"]:
        assert 3 <= len(p["titulo"]) <= 70 and len(p["texto"]) > 50, (lg, p["titulo"])
    for texto in [g["titulo"], g["intro"], g["fim"], *g["dicas"], *(p["titulo"] + p["texto"] for p in g["passos"])]:
        assert "{" not in texto and "}" not in texto and "<" not in texto, (lg, texto[:40])


@pytest.mark.parametrize("nome", guias.PARA_PUBLICOS)
def test_o_primeiro_passo_manda_confirmar_a_licenca_porque_as_regras_variam(nome):
    # nao se afirma nada sobre a lei: o 1.o passo (em todas as linguas) tem de mencionar a autoridade local/licenca; verifica-se so que nao e igual ao dos outros passos
    for lg in LINGUAS:
        passos = guias.guia(nome, lg)["passos"]
        assert len({p["texto"] for p in passos}) == guias.N_PASSOS
    texto = guias.guia(nome, "pt")["passos"][0]["texto"]
    if nome == "igrejas":
        # neutralizado de proposito: a autoridade competente nao e sempre a câmara municipal (varia entre Portugal e o Brasil)
        assert "autoridade competente" in texto and "câmara municipal" not in texto
    else:
        assert "câmara municipal" in texto


def test_as_linguas_nao_traduzidas_caem_no_portugues():
    assert guias.guia("escolas", "xx") == guias.guia("escolas", "pt")


def test_a_api_entrega_o_guia_na_lingua_do_pedido(c):
    r = c.get("/api/guia/escolas", headers={"X-Lingua": "en"})
    assert r.status_code == 200 and r.json()["titulo"] == "How to run a raffle for your school"
    assert len(r.json()["passos"]) == 5 and r.headers["vary"].startswith("X-Lingua")
    assert c.get("/api/guia/associacoes", headers={"X-Lingua": "ja"}).json()["titulo"].startswith("協会")
    assert c.get("/api/guia/nao-existe").status_code == 404
    assert c.get("/api/guia/..%2Fadmin").status_code == 404


@pytest.mark.parametrize("nome", guias.NOMES)
def test_o_html_estatico_leva_o_guia_inteiro_em_cada_lingua(c, nome):
    caminho = guias.CAMINHOS[nome]
    for lg in LINGUAS:
        url = caminho if lg == "pt" else f"/{lg}{caminho}"
        h = c.get(url).text
        g = guias.guia(nome, lg)
        corpo = h.split('<div class="seo-estatico">')[1]
        propria, outros = corpo.split("<h2>", 1)[0], corpo.split("<h2>", 1)[1]        # o guia, e a seguir «Outros guias» (ligações aos restantes)
        assert len(re.findall(r"<h1>", corpo)) == 1 and propria.count("<li>") == guias.N_PASSOS + guias.N_DICAS, (lg, nome)
        assert outros.count("<li>") == len(guias.NOMES) - 1 and f'href="{url}"' not in outros, (lg, nome)
        assert html.escape(g["titulo"]) in corpo and f"<title>{html.escape(g['titulo'])}" in h
        assert f'<link rel="canonical" href="{URL}{url}" />' in h


def test_os_guias_estao_no_sitemap_e_na_navegacao_do_servidor(c):
    sitemap = c.get("/sitemap.xml").text
    for nome in guias.NOMES:
        assert f"{URL}{guias.CAMINHOS[nome]}</loc>" in sitemap and f"{URL}/en{guias.CAMINHOS[nome]}</loc>" in sitemap
        assert guias.CAMINHOS[nome] in seo.ROTAS
