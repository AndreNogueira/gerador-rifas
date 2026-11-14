"""Termos, privacidade e contacto: o texto vem de uma so fonte, nada pessoal esta no repositorio e a configuracao (env) e validada."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import config, textos_legais
from web.app import criar_app


PT = {"X-Lingua": "pt"}          # sem cabeçalho a língua é a do browser (inglês por omissão): estes testes verificam o texto português


@pytest.fixture
def c(tmp_path):
    with TestClient(criar_app(armazenamento=tmp_path)) as cliente:
        yield cliente


def test_sem_configuracao_nao_ha_donativo_nem_contacto(c, monkeypatch):
    for v in ("DONATIVO_URL", "CONTACTO_EMAIL", "RESPONSAVEL"):
        monkeypatch.delenv(v, raising=False)
    assert c.get("/api/publico").json() == {"donativo_url": "", "contacto": False, "qr": False, "anuncios_cliente": "", "anuncios_slot": "", "partilha_editor": False}
    d = c.get("/api/pagina/contacto", headers=PT).json()
    assert "não há um contacto público" in d["seccoes"][0]["paragrafos"][0]


def test_a_configuracao_aparece_e_so_se_for_valida(c, monkeypatch):
    monkeypatch.setenv("DONATIVO_URL", "https://exemplo.pt/doar")
    monkeypatch.setenv("CONTACTO_EMAIL", "ola@exemplo.pt")
    monkeypatch.setenv("RESPONSAVEL", "Ana <b>Silva</b>\nOutra linha")
    assert c.get("/api/publico").json() == {"donativo_url": "https://exemplo.pt/doar", "contacto": True, "qr": False, "anuncios_cliente": "", "anuncios_slot": "", "partilha_editor": False}
    texto = str(c.get("/api/pagina/termos", headers=PT).json()) + str(c.get("/api/pagina/contacto", headers=PT).json())
    assert "ola@exemplo.pt" in texto and "Ana bSilva/bOutra linha" in texto and "<b>" not in texto
    for mau in ("http://inseguro.pt", "javascript:alert(1)", "https://a b.pt", ""):
        monkeypatch.setenv("DONATIVO_URL", mau)
        assert config.donativo_url() == ""
    for mau in ("sem-arroba", "a@b", "a@b.pt\nBcc: x@y.pt", "<a@b.pt>"):
        monkeypatch.setenv("CONTACTO_EMAIL", mau)
        assert config.contacto_email() == ""


def test_paginas_de_texto_tem_titulo_e_seccoes_e_o_desconhecido_e_404(c):
    for nome in textos_legais.PAGINAS:
        d = c.get(f"/api/pagina/{nome}", headers=PT).json()
        assert d["titulo"] and d["seccoes"] and all(s["titulo"] and s["paragrafos"] for s in d["seccoes"])
    assert c.get("/api/pagina/segredo").status_code == 404
    assert "provisória" in c.get("/api/pagina/termos", headers=PT).json()["aviso"]       # o aviso de que falta revisao juridica nao pode desaparecer


def test_o_texto_estatico_do_seo_escapa_html(monkeypatch, tmp_path):
    monkeypatch.setenv("RESPONSAVEL", "A&B")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados")) as c:
        h = c.get("/termos").text
        assert "A&amp;B" in h and "A&B" not in h.split('<div id="raiz">')[1]


def test_o_repositorio_nao_tem_dados_pessoais_nas_paginas():
    for f in textos_legais.PAGINAS.values():
        assert "@" not in str(f()) or config.contacto_email(), "nenhum e-mail escrito no codigo"
