"""M4 na webapp: a pre-visualizacao PNG, «usar este template» na sessao e os erros dos textos."""
import time

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

PNG = b"\x89PNG\r\n\x1a\n"
TEXTOS = dict(titulo="Rifa de Natal", organizacao="Associação de Exemplo", premios=["1.º Prémio: Um cabaz"], data="Sorteio: 24/12/26")


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


@pytest.mark.parametrize("desenho", ["bosque", "quermesse", "natal", "gala"])
def test_previa_png_de_cada_desenho(c, desenho):
    r = c.get("/api/galeria/previa.png", params={"desenho": desenho, "t": "Rifa de Natal", "o": "Associação", "p1": "1.º Prémio", "d": "24/12/26"})
    assert r.status_code == 200 and r.content[:8] == PNG and r.headers["content-type"] == "image/png"
    assert r.headers["x-content-type-options"] == "nosniff"


def test_previa_com_textos_invalidos_ou_desenho_desconhecido_e_um_aviso_traduzido(c):
    r = c.get("/api/galeria/previa.png", params={"desenho": "bosque", "t": "हिन्दी"}, headers={"X-Lingua": "en"})
    assert r.status_code == 422 and r.json()["tipo"] == "aviso" and "supported letters" in r.json()["detail"] and "ह" in r.json()["detail"]
    assert c.get("/api/galeria/previa.png", params={"desenho": "nao-existe"}).status_code == 422
    assert c.get("/api/galeria/previa.png", params={"desenho": "bosque", "t": "x" * 41}).status_code == 422       # acima do limite do campo


def test_usar_o_template_da_galeria_deixa_a_sessao_pronta_e_gera(c):
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    r = c.post(f"/api/sessoes/{s}/galeria", json={"desenho": "gala", **TEXTOS}, headers=h)
    assert r.status_code == 200
    d = r.json()
    assert d["template"]["estado"] == "ok" and d["algarismos"]["estado"] == "ok" and d["pronto"] and d["info"]["n_campos"] == 1
    assert d["info"]["tem_folha"] and d["template"]["nome"] == "galeria-gala.pdf"
    campos = dict(nome="Rifa", inicio="1", fim="10", digitos="4", modo="unico", max_ficheiro="300", papel="A4", margem="5", porfolha="")
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"


def test_usar_com_textos_que_a_letra_nao_tem_nao_mexe_na_sessao(c):
    h = {"X-Lingua": "en"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    r = c.post(f"/api/sessoes/{s}/galeria", json={"desenho": "natal", "titulo": "हिन्दी"}, headers=h)
    assert r.status_code == 422 and "supported letters" in r.json()["detail"]
    assert c.get(f"/api/sessoes/{s}").json()["template"]["estado"] == "vazio"
    assert c.post(f"/api/sessoes/{s}/galeria", json={"desenho": "natal", "premios": ["a", "b", "c", "d"]}, headers=h).status_code == 422


def test_o_metrico_da_galeria_so_leva_o_id_do_desenho(c, tmp_path):
    s = c.post("/api/sessoes").json()["sessao"]
    c.post(f"/api/sessoes/{s}/galeria", json={"desenho": "bosque", "titulo": "Segredo da associacao"})
    serv = c.app.state.servico
    serv.metricas.descarregar(tudo=True)
    linhas = serv.metricas._consultar("SELECT tipo, a, b, c FROM eventos WHERE tipo='galeria'")
    assert linhas == [("galeria", "bosque", "", "")]
