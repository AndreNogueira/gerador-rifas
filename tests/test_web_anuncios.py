"""AdSense: desligado por omissao (nada da Google em lado nenhum), e com ADSENSE_CLIENTE o script no <head> das paginas publicas, o /ads.txt, o que o
frontend recebe em /api/publico e a Politica de privacidade a dizer a verdade nas 18 linguas."""

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import config, legal_anuncios, textos_legais
from web.app import criar_app
from web.trabalhos import Motor

CLIENTE = "ca-pub-1234567890123456"
GOOGLE = "pagead2.googlesyndication.com"


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def c(tmp_path, motor):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor)) as cliente:
        yield cliente


@pytest.fixture
def com_anuncios(monkeypatch):
    monkeypatch.setenv("ADSENSE_CLIENTE", CLIENTE)
    monkeypatch.setenv("ADSENSE_SLOT", "9876543210")


# ------------------------------------------------------------------ desligado
def test_sem_configuracao_nao_ha_anuncios_em_lado_nenhum(c, monkeypatch):
    monkeypatch.delenv("ADSENSE_CLIENTE", raising=False)
    monkeypatch.delenv("ADSENSE_SLOT", raising=False)
    for caminho in ("/", "/tutorial", "/en/sorteio"):
        assert GOOGLE not in c.get(caminho).text
    assert c.get("/ads.txt").status_code == 404
    assert c.get("/api/publico").json()["anuncios_cliente"] == "" and c.get("/api/publico").json()["anuncios_slot"] == ""
    assert "anúncios" in " ".join(textos_legais.pagina("privacidade", "pt")["seccoes"][0]["paragrafos"])      # «sem anúncios»: continua verdade


@pytest.mark.parametrize("valor", ["ca-pub-123", "pub-1234567890123456", "ca-pub-12345678901234567890123", "<script>", "ca-pub-1234567890123456 x"])
def test_identificadores_invalidos_sao_ignorados(monkeypatch, valor):
    monkeypatch.setenv("ADSENSE_CLIENTE", valor)
    monkeypatch.setenv("ADSENSE_SLOT", "9876543210")
    assert config.adsense_cliente() == "" and config.adsense_slot() == ""


def test_o_bloco_sem_identificador_nao_vale(monkeypatch):
    monkeypatch.delenv("ADSENSE_CLIENTE", raising=False)
    monkeypatch.setenv("ADSENSE_SLOT", "9876543210")
    assert config.adsense_slot() == ""
    monkeypatch.setenv("ADSENSE_CLIENTE", CLIENTE)
    monkeypatch.setenv("ADSENSE_SLOT", "abc")
    assert config.adsense_slot() == ""


# ------------------------------------------------------------------ ligado
def test_o_script_vai_no_head_das_paginas_publicas_e_nunca_no_painel_nem_no_404(c, com_anuncios, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "um-token-de-teste-longo")
    for caminho in ("/", "/tutorial", "/sorteio", "/editor", "/changelog", "/ja/tutorial"):
        h = c.get(caminho).text
        assert h.count(f"{GOOGLE}/pagead/js/adsbygoogle.js?client={CLIENTE}") == 1, caminho
        assert h.index(GOOGLE) < h.index("</head>")
    assert GOOGLE not in c.get("/admin").text
    r = c.get("/nao-existe")
    assert r.status_code == 404 and GOOGLE not in r.text


def test_ads_txt_so_com_o_identificador(c, com_anuncios):
    r = c.get("/ads.txt")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    assert r.text == "google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0\n"


def test_o_frontend_recebe_o_identificador_e_o_bloco(c, com_anuncios):
    assert c.get("/api/publico").json() | {} == {**c.get("/api/publico").json(), "anuncios_cliente": CLIENTE, "anuncios_slot": "9876543210"}


def test_a_pagina_de_verificacao_de_bilhetes_nunca_leva_anuncios(c, com_anuncios):
    assert GOOGLE not in c.get("/v/qualquer-coisa").text


# ------------------------------------------------------------------ privacidade
@pytest.mark.parametrize("lg", list(i18n.LINGUAS))
def test_a_privacidade_com_anuncios_diz_a_verdade_em_todas_as_linguas(lg, com_anuncios, monkeypatch):
    com = textos_legais.pagina("privacidade", lg)
    monkeypatch.delenv("ADSENSE_CLIENTE")
    sem = textos_legais.pagina("privacidade", lg)
    assert len(com["seccoes"]) == len(sem["seccoes"]) + 1
    d = legal_anuncios.TEXTOS[lg]
    assert com["seccoes"][3]["titulo"] == d["seccao"]["titulo"] and len(com["seccoes"][3]["paragrafos"]) == 3
    resumo, browser = com["seccoes"][0]["paragrafos"][0], com["seccoes"][2]["paragrafos"][-1]
    assert resumo.startswith(d["resumo"]) and browser.endswith(d["cookies"])
    # so mudou a 1.a frase do resumo e a ultima do browser: o resto fica (o tempo de apagamento continua no resumo)
    assert sem["seccoes"][0]["paragrafos"][0] != resumo and str(textos_legais.config.validade_min()) in resumo
    assert sem["seccoes"][2]["paragrafos"][-1] != browser and com["seccoes"][1] == sem["seccoes"][1]
    for seccao in com["seccoes"]:
        for t in seccao["paragrafos"]:
            assert "{" not in t and "}" not in t


def test_cada_lingua_tem_o_seu_texto_de_anuncios_e_so_essas():
    assert set(legal_anuncios.TEXTOS) == set(i18n.LINGUAS)


def test_a_api_da_privacidade_e_o_seo_usam_o_texto_com_anuncios(c, com_anuncios):
    d = c.get("/api/pagina/privacidade", headers={"X-Lingua": "en"}).json()
    assert [s["titulo"] for s in d["seccoes"]].count("Advertising") == 1
    assert "Advertising" in c.get("/en/privacidade").text or "Advertising" in c.get("/en/privacidade", follow_redirects=True).text
