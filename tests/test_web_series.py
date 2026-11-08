"""Series, prefixos e saltos ate ao fim: o pedido da webapp (calcular, pre-visualizar, gerar) e o ZIP que se descarrega."""
import io
import time
import urllib.parse
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
CAMPOS = dict(nome="Rifa", inicio="1", fim="12", digitos="4", modo="varios", max_ficheiro="5", papel="A4", margem="5", porfolha="")


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def c(tmp_path, motor, monkeypatch):
    monkeypatch.setenv("MAX_NUMEROS", "100")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor)) as cliente:
        yield cliente


def _sessao_pronta(c) -> str:
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    cab = {"X-Nome": urllib.parse.quote("t.pdf"), "Content-Type": "application/octet-stream", "X-Lingua": "pt"}
    assert c.put(f"/api/sessoes/{s}/template", content=(FX / "template_exemplo.pdf").read_bytes(), headers=cab).status_code == 200
    assert c.put(f"/api/sessoes/{s}/algarismos", content=(FX / "digitos_exemplo.pdf").read_bytes(), headers=cab).json()["pronto"]
    return s


def test_o_resumo_conta_series_e_saltos(c):
    s = _sessao_pronta(c)
    r = c.post(f"/api/sessoes/{s}/calcular", json={**CAMPOS, "prefixos": "A-, B-", "saltar": "3"}, headers={"X-Lingua": "pt"}).json()
    assert r["resumo"]["texto"] == "22 números · 6 PDF(s) · 6 páginas no total"      # 11 por serie x 2; 3 ficheiros de 5, 5 e 1 por serie
    erro = c.post(f"/api/sessoes/{s}/calcular", json={**CAMPOS, "prefixos": "A1"}, headers={"X-Lingua": "pt"}).json()["resumo"]
    assert erro["aviso"] and "prefixo" in erro["texto"]
    en = c.post(f"/api/sessoes/{s}/calcular", json={**CAMPOS, "saltar": "x"}, headers={"X-Lingua": "en"}).json()["resumo"]
    assert en["aviso"] and "Skip" in en["texto"]                                     # traduzido para a lingua do pedido


def test_o_teto_de_numeros_conta_as_series(c):
    s = _sessao_pronta(c)
    campos = {**CAMPOS, "fim": "60", "prefixos": "A,B,C"}                           # 180 > 100
    texto = c.post(f"/api/sessoes/{s}/calcular", json=campos, headers={"X-Lingua": "pt"}).json()["resumo"]
    assert texto["aviso"] and "100" in texto["texto"]
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers={"X-Lingua": "pt"}).status_code == 422


def test_previa_e_gerar_com_series_dao_um_zip_com_um_pdf_por_serie(c):
    s = _sessao_pronta(c)
    h = {"X-Lingua": "pt"}
    campos = {**CAMPOS, "fim": "6", "max_ficheiro": "5", "prefixos": "A-, B-", "saltar": "3", "cor_serie": "1"}
    assert c.post(f"/api/sessoes/{s}/previa", json=campos, headers=h).status_code == 200
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"
    z = zipfile.ZipFile(io.BytesIO(c.get(f"/api/sessoes/{s}/descarregar").content))
    assert sorted(z.namelist()) == ["Rifa - A - 0001 - 0006.pdf", "Rifa - B - 0001 - 0006.pdf"]
