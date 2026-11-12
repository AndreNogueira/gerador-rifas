"""X1 na webapp: a pre-visualizacao PNG do desenho, «usar este template» na sessao (e gerar com ele), os avisos traduzidos e a privacidade do evento."""
import time

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.trabalhos import Motor

PNG = b"\x89PNG\r\n\x1a\n"


def desenho(**extra) -> dict:
    elementos = [
        dict(tipo="retangulo", x=2, y=2, w=531, h=148, cor="#fffdf5", contorno="#0f6e73", espessura=2, raio=10),
        dict(tipo="texto", x=84, y=40, texto="Segredo da associacao 2026", tamanho=18, cor="#0f6e73", negrito=True),
        dict(tipo="numero", x=412, y=56, tamanho=20, cor="#c2410c"),
        dict(tipo="numero", x=42, y=112, tamanho=19, cor="#c2410c", rot=90),
    ]
    return dict(largura=535, altura=152, fundo="#ffffff", elementos=elementos) | extra


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


def test_previa_png_do_desenho(c):
    r = c.post("/api/editor/previa.png", json=desenho())
    assert r.status_code == 200 and r.content[:8] == PNG and r.headers["content-type"] == "image/png"
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["cache-control"] == "no-store"


def test_desenhos_que_nao_prestam_dao_um_aviso_traduzido_em_vez_de_uma_imagem(c):
    h = {"X-Lingua": "en"}
    sem_numero = desenho(elementos=[dict(tipo="texto", x=1, y=10, texto="x")])
    r = c.post("/api/editor/previa.png", json=sem_numero, headers=h)
    assert r.status_code == 422 and r.json()["tipo"] == "aviso" and "0001" in r.json()["detail"] and "once, or twice" in r.json()["detail"]
    parecido = desenho()
    parecido["elementos"].append(dict(tipo="texto", x=1, y=10, texto="Ref 0123"))
    r = c.post("/api/editor/previa.png", json=parecido, headers=h)
    assert r.status_code == 422 and "0123" in r.json()["detail"]
    fora = desenho(largura=5000)
    assert c.post("/api/editor/previa.png", json=fora, headers=h).status_code == 422
    assert c.post("/api/editor/previa.png", json=desenho(elementos=[dict(tipo="numero")] * 60), headers=h).status_code == 422


def test_usar_o_desenho_deixa_a_sessao_pronta_e_gera(c):
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    r = c.post(f"/api/sessoes/{s}/editor", json=desenho(), headers=h)
    assert r.status_code == 200
    d = r.json()
    assert d["template"]["estado"] == "ok" and d["algarismos"]["estado"] == "ok" and d["pronto"] and d["info"]["n_campos"] == 1
    assert d["info"]["tem_folha"] and d["template"]["nome"] == "editor.pdf"
    campos = dict(nome="Rifa", inicio="1", fim="10", digitos="4", modo="unico", max_ficheiro="300", papel="A4", margem="5", porfolha="")
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] == "ok"


def test_usar_um_desenho_invalido_nao_mexe_na_sessao(c):
    h = {"X-Lingua": "pt"}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    r = c.post(f"/api/sessoes/{s}/editor", json=desenho(elementos=[]), headers=h)
    assert r.status_code == 422 and "0001" in r.json()["detail"]
    assert c.get(f"/api/sessoes/{s}").json()["template"]["estado"] == "vazio"


def test_o_evento_do_editor_so_leva_codigos_e_numeros(c):
    s = c.post("/api/sessoes").json()["sessao"]
    assert c.post(f"/api/sessoes/{s}/editor", json=desenho()).status_code == 200
    serv = c.app.state.servico
    serv.metricas.descarregar(tudo=True)
    linhas = serv.metricas._consultar("SELECT tipo, a, b, c, v1 FROM eventos WHERE tipo='editor'")
    assert linhas == [("editor", "usar", "", "", 4.0)]            # nada do que se escreveu («Segredo da associacao»)
