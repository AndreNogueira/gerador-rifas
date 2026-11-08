"""M3 na webapp: as marcas de corte vao do formulario ao PDF, e a margem curta e um aviso."""
import io
import time
import urllib.parse
import zipfile
from pathlib import Path

import pytest
from pypdf import PdfReader

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
CAMPOS = dict(nome="Rifa", inicio="1", fim="5", digitos="4", modo="unico", max_ficheiro="300", papel="A4", margem="5", porfolha="")


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


def _sessao_de_uma_rifa(c) -> str:
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    cab = {"X-Nome": urllib.parse.quote("t.pdf"), "Content-Type": "application/octet-stream", "X-Lingua": "pt"}
    assert c.put(f"/api/sessoes/{s}/template", content=(FX / "template_exemplo_1_rifa.pdf").read_bytes(), headers=cab).status_code == 200
    assert c.put(f"/api/sessoes/{s}/algarismos", content=(FX / "digitos_exemplo.pdf").read_bytes(), headers=cab).json()["pronto"]
    return s


def test_margem_curta_com_marcas_e_um_aviso_no_painel_da_folha_e_ao_gerar(c):
    s = _sessao_de_uma_rifa(c)
    h = {"X-Lingua": "en"}
    r = c.post(f"/api/sessoes/{s}/calcular", json={**CAMPOS, "margem": "2", "marcas": "1"}, headers=h).json()
    assert r["folha"]["erro"] and "Crop marks need a margin of at least 3 mm" in r["folha"]["texto"]
    ok = c.post(f"/api/sessoes/{s}/calcular", json={**CAMPOS, "margem": "3", "marcas": "1"}, headers=h).json()
    assert not ok["folha"]["erro"]
    assert c.post(f"/api/sessoes/{s}/gerar", json={**CAMPOS, "margem": "2", "marcas": "1"}, headers=h).status_code == 422


def test_previa_e_geracao_levam_as_marcas(c):
    s = _sessao_de_uma_rifa(c)
    h = {"X-Lingua": "pt"}
    campos = {**CAMPOS, "marcas": "1"}
    assert c.post(f"/api/sessoes/{s}/previa", json=campos, headers=h).status_code == 200
    pdf = c.get(f"/api/sessoes/{s}/previa.pdf").content
    assert b"0.4 w" in PdfReader(io.BytesIO(pdf)).pages[0].get_contents().get_data()
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"
    corpo = c.get(f"/api/sessoes/{s}/descarregar").content
    pdf_final = corpo if corpo[:4] == b"%PDF" else zipfile.ZipFile(io.BytesIO(corpo)).read(zipfile.ZipFile(io.BytesIO(corpo)).namelist()[0])
    assert b"0.4 w" in PdfReader(io.BytesIO(pdf_final)).pages[0].get_contents().get_data()
    sem = c.post(f"/api/sessoes/{s}/previa", json=CAMPOS, headers=h)
    assert sem.status_code == 200 and b"0.4 w" not in PdfReader(io.BytesIO(c.get(f"/api/sessoes/{s}/previa.pdf").content)).pages[0].get_contents().get_data()
