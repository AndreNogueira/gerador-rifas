"""PWA: o service worker tem de chegar sempre fresco ao browser; os ficheiros com hash continuam em cache para sempre."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app


@pytest.fixture
def c(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    (dist / "sw.js").write_text("// sw", encoding="utf-8")
    (dist / "assets" / "a.js").write_text("1", encoding="utf-8")
    (dist / "og-imagem.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados")) as cliente:
        yield cliente


def test_o_service_worker_nunca_fica_em_cache_no_browser(c):
    r = c.get("/sw.js")
    assert r.status_code == 200 and r.headers["cache-control"] == "no-cache"
    assert "javascript" in r.headers["content-type"]


def test_os_ficheiros_com_hash_ficam_em_cache_para_sempre(c):
    assert "immutable" in c.get("/assets/a.js").headers["cache-control"]


def test_a_imagem_og_fica_uma_semana_em_cache_sem_nome_com_hash(c):
    r = c.get("/og-imagem.png")
    assert r.status_code == 200 and r.headers["cache-control"] == "public, max-age=604800"
