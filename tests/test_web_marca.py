"""M5 na webapp: carregar e remover o logotipo, e o logotipo e a cor chegarem a pre-visualizacao e ao PDF."""
import io
import time
import urllib.parse
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
CAMPOS = dict(nome="Rifa", inicio="1", fim="5", digitos="4", modo="unico", max_ficheiro="300", papel="A4", margem="5", porfolha="")


def _logo(formato="PNG") -> bytes:
    b = io.BytesIO()
    Image.new("RGBA" if formato == "PNG" else "RGB", (300, 150), (10, 90, 200, 255) if formato == "PNG" else (10, 90, 200)).save(b, formato)
    return b.getvalue()


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def c(tmp_path, motor):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor)) as cliente:
        yield cliente


def _sessao(c) -> str:
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    cab = {"X-Nome": urllib.parse.quote("t.pdf"), "Content-Type": "application/octet-stream", "X-Lingua": "pt"}
    assert c.put(f"/api/sessoes/{s}/template", content=(FX / "template_exemplo_1_rifa.pdf").read_bytes(), headers=cab).status_code == 200
    assert c.put(f"/api/sessoes/{s}/algarismos", content=(FX / "digitos_exemplo.pdf").read_bytes(), headers=cab).json()["pronto"]
    return s


def _subir(c, s, dados, nome="meu logo.png", lg="pt"):
    return c.put(f"/api/sessoes/{s}/logotipo", content=dados, headers={"X-Nome": urllib.parse.quote(nome), "Content-Type": "application/octet-stream", "X-Lingua": lg})


def test_carregar_e_remover_o_logotipo(c):
    s = _sessao(c)
    assert c.get(f"/api/sessoes/{s}").json()["logotipo"] == ""
    r = _subir(c, s, _logo())
    assert r.status_code == 200 and r.json()["logotipo"] == "meu logo.png"
    assert c.get(f"/api/sessoes/{s}").json()["logotipo"] == "meu logo.png"
    r2 = _subir(c, s, _logo("JPEG"), "outro.jpg")                                     # trocar: fica so um ficheiro
    assert r2.json()["logotipo"] == "outro.jpg"
    r3 = c.delete(f"/api/sessoes/{s}/logotipo")
    assert r3.status_code == 200 and r3.json()["logotipo"] == ""


def test_o_que_nao_e_uma_imagem_ou_e_grande_demais_e_recusado_sem_mexer_no_que_ja_la_esta(c):
    s = _sessao(c)
    assert _subir(c, s, _logo()).status_code == 200
    mau = _subir(c, s, b"%PDF-1.4 isto nao e uma imagem", "x.png", "en")
    assert mau.status_code == 422 and mau.json()["tipo"] == "aviso" and "PNG or JPG" in mau.json()["detail"]
    assert _subir(c, s, b"\x89PNG\r\n\x1a\n" + b"0" * (2 * 1024 * 1024 + 10), "g.png").status_code == 413
    assert c.get(f"/api/sessoes/{s}").json()["logotipo"] == "meu logo.png"             # o anterior continua


def test_o_logotipo_e_a_cor_chegam_a_previa_e_ao_pdf(c):
    s = _sessao(c)
    _subir(c, s, _logo())
    h = {"X-Lingua": "pt"}
    campos = {**CAMPOS, "cor_numeros": "#0000FF", "logo_posicao": "ie", "logo_tamanho": "30"}
    assert c.post(f"/api/sessoes/{s}/previa", json=campos, headers=h).status_code == 200
    previa = PdfReader(io.BytesIO(c.get(f"/api/sessoes/{s}/previa.pdf").content)).pages[0]
    conteudo = previa.get_contents().get_data().decode("latin-1")
    assert conteudo.count("/Logo Do") == 5 and "0 0 1 rg" in conteudo
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"
    corpo = c.get(f"/api/sessoes/{s}/descarregar").content
    assert b"%PDF" in corpo[:8] or corpo[:2] == b"PK"
    # depois de remover o logotipo a pre-visualizacao ja nao o tem
    c.delete(f"/api/sessoes/{s}/logotipo")
    c.post(f"/api/sessoes/{s}/previa", json=campos, headers=h)
    sem = PdfReader(io.BytesIO(c.get(f"/api/sessoes/{s}/previa.pdf").content)).pages[0].get_contents().get_data().decode("latin-1")
    assert "/Logo Do" not in sem and "0 0 1 rg" in sem


def test_cor_invalida_e_um_aviso_traduzido(c):
    s = _sessao(c)
    r = c.post(f"/api/sessoes/{s}/calcular", json={**CAMPOS, "cor_numeros": "azul"}, headers={"X-Lingua": "en"}).json()
    assert r["resumo"]["aviso"] and "#RRGGBB" in r["resumo"]["texto"]
    assert c.post(f"/api/sessoes/{s}/previa", json={**CAMPOS, "cor_numeros": "azul"}, headers={"X-Lingua": "en"}).status_code == 422
    assert c.post(f"/api/sessoes/{s}/gerar", json={**CAMPOS, "cor_numeros": "#12"}, headers={"X-Lingua": "en"}).status_code == 422
