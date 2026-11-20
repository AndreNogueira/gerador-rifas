"""Fase 7 na webapp: a pre-visualizacao PNG do vale, «criar vales numerados» na sessao (e gerar a partir dela, com series e QR) e a privacidade das metricas."""
import json
import time

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

PNG = b"\x89PNG\r\n\x1a\n"
VALE = dict(desenho="arraial", titulo="VALE", organizacao="Associação de Exemplo", moeda="ficha", moeda_plural="fichas", quantidade=2, nota="Só na festa")


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


def test_previa_png_do_vale(c):
    r = c.post("/api/vales/previa.png", json=VALE)
    assert r.status_code == 200 and r.content[:8] == PNG and r.headers["content-type"] == "image/png"
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("campo, valor", [("quantidade", 0), ("quantidade", 100), ("titulo", "VALE 0123"), ("desenho", "nao-existe"), ("titulo", "हिन्दी")])
def test_um_vale_que_nao_presta_e_um_aviso_traduzido(c, campo, valor):
    r = c.post("/api/vales/previa.png", json={**VALE, campo: valor}, headers={"X-Lingua": "en"})
    assert r.status_code == 422 and r.json()["tipo"] == "aviso"
    if campo == "quantidade":
        assert "between 1 and 99" in r.json()["detail"]


def test_campos_acima_dos_limites_do_pedido_sao_recusados(c):
    assert c.post("/api/vales/previa.png", json={**VALE, "titulo": "x" * 80}).status_code == 422
    assert c.post("/api/vales/previa.png", json={**VALE, "quantidade": 5000}).status_code == 422


def test_criar_os_vales_deixa_a_sessao_pronta_e_gera_com_series(c):
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    r = c.post(f"/api/sessoes/{s}/vales", json=VALE, headers=h)
    assert r.status_code == 200
    d = r.json()
    assert d["template"]["estado"] == "ok" and d["algarismos"]["estado"] == "ok" and d["pronto"] and d["info"]["n_campos"] == 1
    assert d["info"]["tem_folha"] and d["template"]["nome"] == "vales-arraial.pdf"
    campos = dict(nome="Vales", inicio="1", fim="20", digitos="4", modo="unico", max_ficheiro="300", papel="A4", margem="5", porfolha="", prefixos="A-")
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"


def test_criar_com_dados_invalidos_nao_mexe_na_sessao(c):
    h = {"X-Lingua": "en"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    r = c.post(f"/api/sessoes/{s}/vales", json={**VALE, "quantidade": 0}, headers=h)
    assert r.status_code == 422 and "between 1 and 99" in r.json()["detail"]
    assert c.get(f"/api/sessoes/{s}").json()["template"]["estado"] == "vazio"
    assert c.post("/api/sessoes/nao-existe/vales", json=VALE).status_code == 404


def test_as_metricas_so_levam_o_desenho_e_a_quantidade(c):
    s = c.post("/api/sessoes").json()["sessao"]
    c.post(f"/api/sessoes/{s}/vales", json={**VALE, "titulo": "Segredo", "organizacao": "Associacao Secreta", "moeda": "tostao", "moeda_plural": "tostoes"})
    serv = c.app.state.servico
    serv.metricas.descarregar(tudo=True)
    linhas = serv.metricas._consultar("SELECT tipo, a, b, c FROM eventos WHERE tipo='vales'")
    assert linhas == [("vales", "arraial", "", "")]
    tudo = json.dumps(serv.metricas._consultar("SELECT * FROM eventos"), ensure_ascii=False).lower()
    for segredo in ("segredo", "secreta", "tostao", "tostoes", "só na festa"):
        assert segredo not in tudo
