"""Ficheiros do frontend compilado: versoes comprimidas (.br/.gz) por Accept-Encoding, sem mapas, e o `dist` real (se existir)."""
import gzip
import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import app as modulo_app
from web.app import _aceita, criar_app

JS = b"console.log('ola');" * 40


@pytest.fixture
def dist(tmp_path):
    pasta = tmp_path / "dist"
    (pasta / "assets").mkdir(parents=True)
    (pasta / "index.html").write_text("<!doctype html><title>x</title>" * 20, encoding="utf-8")
    (pasta / "assets" / "app-abc.js").write_bytes(JS)
    (pasta / "assets" / "app-abc.js.gz").write_bytes(gzip.compress(JS))
    (pasta / "assets" / "app-abc.js.br").write_bytes(b"BR-FALSO")          # o servidor so entrega, nao descodifica
    (pasta / "assets" / "app-abc.js.map").write_text("{}", encoding="utf-8")
    (pasta / "assets" / "sem-comprimir.css").write_text("a{color:red}", encoding="utf-8")
    return pasta


@pytest.fixture
def cliente(dist, tmp_path):
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"))


def test_entrega_brotli_a_quem_o_aceita(cliente):
    r = cliente.get("/assets/app-abc.js", headers={"Accept-Encoding": "gzip, deflate, br"})
    assert r.status_code == 200 and r.headers["content-encoding"] == "br" and r.content == b"BR-FALSO"
    assert "javascript" in r.headers["content-type"] and r.headers["vary"] == "Accept-Encoding"
    assert "immutable" in r.headers["cache-control"]


def test_cai_para_gzip_sem_brotli(cliente):
    r = cliente.get("/assets/app-abc.js", headers={"Accept-Encoding": "gzip"})
    assert r.headers["content-encoding"] == "gzip"
    assert r.content == JS                                  # o cliente de teste descomprime o gzip sozinho


def test_sem_accept_encoding_entrega_o_original(cliente):
    r = cliente.get("/assets/app-abc.js", headers={"Accept-Encoding": "identity"})
    assert "content-encoding" not in r.headers and r.content == JS and r.headers["vary"] == "Accept-Encoding"


def test_q_zero_recusa_a_codificacao(cliente):
    r = cliente.get("/assets/app-abc.js", headers={"Accept-Encoding": "br;q=0, gzip;q=0.5"})
    assert r.headers["content-encoding"] == "gzip"


def test_ficheiro_sem_versao_comprimida_vai_normal(cliente):
    r = cliente.get("/assets/sem-comprimir.css", headers={"Accept-Encoding": "br, gzip"})
    assert "content-encoding" not in r.headers and r.text == "a{color:red}" and "vary" not in r.headers


def test_ficheiro_fora_de_assets_fica_em_cache_um_dia_nunca_para_sempre(dist, cliente):
    # nome fixo (sem hash), por isso nunca "immutable": pode ser substituido noutro deploy (p.ex. gerar_miniaturas_galeria.py)
    (dist / "icone.svg").write_text("<svg></svg>", encoding="utf-8")
    assert cliente.get("/icone.svg").headers["cache-control"] == "public, max-age=86400"


def test_o_index_tambem_se_entrega_e_nao_fica_em_cache(cliente):
    r = cliente.get("/", headers={"Accept-Encoding": "identity"})
    assert r.status_code == 200 and r.headers["cache-control"] == "no-cache" and "<title>x</title>" in r.text


@pytest.mark.parametrize("caminho", ["/assets/app-abc.js.map", "/assets/app-abc.js.br", "/assets/app-abc.js.gz"])
def test_mapas_e_comprimidos_nao_se_servem_soltos(cliente, caminho):
    assert cliente.get(caminho).status_code == 404


@pytest.mark.parametrize("cabecalho,codificacao,esperado", [
    ("gzip, deflate, br", "br", True), ("gzip", "br", False), ("br;q=0", "br", False), ("br;q=0.2", "br", True),
    ("BR", "br", True), ("", "gzip", False), ("*", "br", False), ("br;q=abc", "br", False),
])
def test_aceita(cabecalho, codificacao, esperado):
    assert _aceita(cabecalho, codificacao) is esperado


def test_o_dist_real_tem_um_js_principal_um_css_sem_mapas_e_so_as_partes_conhecidas(tmp_path):
    """Se o frontend foi compilado (`pnpm build`), confere o que o `verificar-dist.mjs` garante (nao falha se nao houver `dist`)."""
    dist_real = Path(modulo_app.__file__).parent / "frontend" / "dist"
    if not (dist_real / "index.html").is_file():
        pytest.skip("frontend por compilar")
    assets = dist_real / "assets"
    todos = sorted(f.name for f in assets.glob("*.js"))
    principais = [n for n in todos if n.startswith("index-")]
    assert len(principais) == 1 and len(list(assets.glob("*.css"))) == 1
    assert {n.split("-")[0] for n in todos} == {"index", "Admin", "Editor", "Precario", "Sorteio", "jsx"}           # o principal, as 4 paginas a parte e o pedaco partilhado: mais nada
    assert not list(dist_real.rglob("*.map"))
    html = (dist_real / "index.html").read_text(encoding="utf-8")
    assert len(re.findall(r'<script[^>]+src="', html)) == 1 and len(re.findall(r'rel="stylesheet"', html)) == 1 and principais[0] in html
    assert not any(n in html for n in todos if not n.startswith(("index-", "jsx-")))                    # a pagina inicial nao liga as partes: carregam-se quando se abre a pagina
    c = TestClient(criar_app(frontend=dist_real, armazenamento=tmp_path / "dados"))
    for nome in todos:
        r = c.get(f"/assets/{nome}", headers={"Accept-Encoding": "br"})
        assert r.status_code == 200 and r.headers["content-encoding"] == "br" and r.headers["content-type"].startswith("text/javascript"), nome
        assert len(r.content) < (assets / nome).stat().st_size / 2 or (assets / nome).stat().st_size < 20000, nome
