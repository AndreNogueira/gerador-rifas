"""M6 na webapp: o QR so existe com VERIFICACAO_CHAVE, e a pagina /V/<codigo> confirma (ou nao) os codigos emitidos."""
import io
import time
import urllib.parse
from pathlib import Path

import pytest
from pypdf import PdfReader

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import qr
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
CHAVE = "chave-secreta-do-servidor-123456"
CAMPOS = dict(nome="Rifa de Natal", inicio="1", fim="5", digitos="4", modo="unico", max_ficheiro="300", papel="A4", margem="5", porfolha="")


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    monkeypatch.delenv("VERIFICACAO_CHAVE", raising=False)
    monkeypatch.setenv("PUBLIC_URL", "https://rifas.exemplo.pt")


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


def test_sem_chave_nao_ha_qr_e_pedi_lo_e_um_aviso(c):
    assert c.get("/api/publico").json()["qr"] is False
    s = _sessao(c)
    r = c.post(f"/api/sessoes/{s}/previa", json={**CAMPOS, "qr": "1"}, headers={"X-Lingua": "en"})
    assert r.status_code == 422 and "not available" in r.json()["detail"]
    assert c.post(f"/api/sessoes/{s}/gerar", json={**CAMPOS, "qr": "1"}, headers={"X-Lingua": "en"}).status_code == 422
    assert c.post(f"/api/sessoes/{s}/previa", json=CAMPOS).status_code == 200                       # sem QR continua tudo igual
    r = c.get("/V/ABC.DEF", headers={"Accept-Language": "en"})
    assert r.status_code == 404 and "not available" in r.text


def test_com_chave_a_previa_e_a_geracao_levam_o_qr(c, monkeypatch):
    monkeypatch.setenv("VERIFICACAO_CHAVE", CHAVE)
    assert c.get("/api/publico").json()["qr"] is True
    s = _sessao(c)
    h = {"X-Lingua": "pt"}
    campos = {**CAMPOS, "qr": "1", "qr_posicao": "id", "qr_tamanho": "30"}
    assert c.post(f"/api/sessoes/{s}/previa", json=campos, headers=h).status_code == 200
    pagina = PdfReader(io.BytesIO(c.get(f"/api/sessoes/{s}/previa.pdf").content)).pages[0]
    assert pagina.get_contents().get_data().count(b"1 g ") >= 5
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"


def _codigo(serie="A-", numero="0001", evento="Rifa de Natal") -> str:
    return qr.codigo(CHAVE.encode(), evento, serie, numero)


def test_a_pagina_confirma_um_codigo_emitido_com_o_aviso_e_sem_indexar(c, monkeypatch):
    monkeypatch.setenv("VERIFICACAO_CHAVE", CHAVE)
    r = c.get(f"/V/{_codigo()}", headers={"Accept-Language": "pt-PT"})
    assert r.status_code == 200 and "Código válido" in r.text and "Bilhete A-0001" in r.text and "Rifa: Rifa de Natal" in r.text
    assert "Não prova que o bilhete foi pago" in r.text
    assert r.headers["cache-control"] == "no-store" and "noindex" in r.headers["x-robots-tag"] and 'content="noindex,nofollow"' in r.text
    assert c.get(f"/v/{_codigo().lower()}", headers={"Accept-Language": "en"}).text.count("Valid code") == 1          # minusculas e noutra lingua
    sem_evento = c.get(f"/V/{_codigo(evento='')}", headers={"Accept-Language": "pt"}).text
    assert "Código válido" in sem_evento and "Rifa:" not in sem_evento


@pytest.mark.parametrize("codigo", ["", "LIXO", "AAAA.BBBB", "MFRGG.AAAAAAAAAAAAAAAA", "A" * 200])
def test_um_codigo_invalido_ou_alterado_nao_valida(c, monkeypatch, codigo):
    monkeypatch.setenv("VERIFICACAO_CHAVE", CHAVE)
    r = c.get(f"/V/{codigo}" if codigo else "/V/x", headers={"Accept-Language": "pt"})
    assert r.status_code == 404 and "Código inválido ou alterado" in r.text and "Código válido" not in r.text
    alterado = _codigo()[:-1] + ("A" if _codigo()[-1] != "A" else "B")
    assert c.get(f"/V/{alterado}").status_code == 404
    assert c.get(f"/V/{qr.codigo(b'outra-chave-completamente-diferente', 'x', 'A-', '0001')}").status_code == 404


def test_robots_nao_deixa_indexar_as_verificacoes_e_as_metricas_so_levam_o_resultado(c, monkeypatch):
    monkeypatch.setenv("VERIFICACAO_CHAVE", CHAVE)
    assert "Disallow: /v/" in c.get("/robots.txt").text and "Disallow: /V/" in c.get("/robots.txt").text
    c.get(f"/V/{_codigo()}")
    c.get("/V/lixo")
    serv = c.app.state.servico
    serv.metricas.descarregar(tudo=True)
    linhas = serv.metricas._consultar("SELECT tipo, a, b, c FROM eventos WHERE tipo='verificacao' ORDER BY a")
    assert linhas == [("verificacao", "invalido", "", ""), ("verificacao", "ok", "", "")]            # nunca o numero, a serie nem o evento


def test_o_qr_tem_um_teto_de_numeros_proprio(c, monkeypatch):
    monkeypatch.setenv("VERIFICACAO_CHAVE", CHAVE)
    monkeypatch.setenv("MAX_NUMEROS_QR", "20")
    s = _sessao(c)
    h = {"X-Lingua": "pt"}
    maior = {**CAMPOS, "fim": "50", "qr": "1"}
    resumo = c.post(f"/api/sessoes/{s}/calcular", json=maior, headers=h).json()["resumo"]
    assert resumo["aviso"] and "20" in resumo["texto"]
    r = c.post(f"/api/sessoes/{s}/gerar", json=maior, headers=h)
    assert r.status_code == 422 and "20" in r.json()["detail"]
    assert c.post(f"/api/sessoes/{s}/calcular", json={**maior, "qr": ""}, headers=h).json()["resumo"]["aviso"] is False      # sem QR o teto e o de sempre
