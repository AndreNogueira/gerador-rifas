"""Tutorial, video e ficheiros estaticos da webapp (src/web/rotas_ajuda.py e os `mount` de app.py)."""
import io

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from PIL import Image

from core import i18n, tutorial
from web.app import criar_app
from web.rotas_ajuda import _recorte


@pytest.fixture
def cliente(tmp_path):
    # sem `with`: nao arranca o processo do motor (estas rotas nao o usam)
    return TestClient(criar_app(frontend=tmp_path, armazenamento=tmp_path / "dados"))


def test_tutorial_tem_os_topicos_na_lingua_pedida(cliente):
    pt = cliente.get("/api/tutorial", headers={"X-Lingua": "pt"}).json()
    assert len(pt["topicos"]) == 8 + len(tutorial.funcionalidades("web"))
    assert pt["topicos"][0]["titulo"] == i18n.TEXTOS["pt"]["tut_t0"]
    for t in pt["topicos"]:
        assert t["menu"] and t["titulo"] and t["texto"] and "{" not in t["texto"]      # sem marcadores por substituir
    en = cliente.get("/api/tutorial", headers={"X-Lingua": "en"}).json()
    assert [t["titulo"] for t in en["topicos"]] != [t["titulo"] for t in pt["topicos"]]


@pytest.mark.parametrize("lingua", list(i18n.LINGUAS))
def test_tutorial_em_todas_as_linguas_com_imagens_que_existem(cliente, lingua):
    d = cliente.get("/api/tutorial", headers={"X-Lingua": lingua}).json()
    assert len(d["topicos"]) == 8 + len(tutorial.funcionalidades("web"))
    urls = [i["url"] for t in d["topicos"] for i in t["imagens"]]
    assert len(urls) >= 8
    for url in urls:
        r = cliente.get(url)
        assert r.status_code == 200 and r.headers["content-type"].startswith("image/"), (lingua, url)


def test_imagens_recortadas_tem_largura_logica_e_sao_png(cliente):
    d = cliente.get("/api/tutorial", headers={"X-Lingua": "pt"}).json()
    recortes = [i for t in d["topicos"] for i in t["imagens"] if "/recorte/" in i["url"]]
    assert recortes and all(i["largura"] and i["largura"] > 100 for i in recortes)
    fixas = [i for t in d["topicos"] for i in t["imagens"] if i["url"].startswith("/ajuda/")]
    assert fixas and all(i["largura"] is None for i in fixas)
    for img in recortes:
        r = cliente.get(img["url"])
        assert r.content.startswith(b"\x89PNG") and "max-age" in r.headers["cache-control"]
        with Image.open(io.BytesIO(r.content)) as im:
            assert im.width >= img["largura"]                      # a largura logica nunca passa a do ficheiro (capturas 1x, 2x ou 3x)


@pytest.mark.parametrize("caminho", ["/api/tutorial/recorte/xx/a/c1.png", "/api/tutorial/recorte/pt/z/c1.png",
                                     "/api/tutorial/recorte/pt/a/nao_existe.png", "/api/tutorial/recorte/pt/a/..%2f..%2fx.png",
                                     "/api/tutorial/recorte/pt/a/C1.png"])
def test_recorte_invalido_da_404(cliente, caminho):
    r = cliente.get(caminho)
    assert r.status_code == 404


def test_o_recorte_e_calculado_uma_vez_por_imagem(cliente):
    _recorte.cache_clear()
    for _ in range(3):
        cliente.get("/api/tutorial/recorte/pt/a/c1.png")
    assert _recorte.cache_info().hits >= 2


def test_video_em_portugues_e_ingles(cliente):
    assert cliente.get("/api/tutorial", headers={"X-Lingua": "pt"}).json()["video"] == "/videos/tutorial_pt.mp4"
    assert cliente.get("/api/tutorial", headers={"X-Lingua": "en"}).json()["video"] == "/videos/tutorial_en.mp4"


def test_video_e_servido_com_suporte_a_range(cliente):
    r = cliente.get("/videos/tutorial_pt.mp4", headers={"Range": "bytes=0-99"})
    assert r.status_code == 206 and r.headers["content-type"] == "video/mp4" and len(r.content) == 100
    assert r.headers["content-range"].startswith("bytes 0-99/")


def test_ajuda_e_videos_ficam_em_cache_um_dia_nunca_para_sempre(cliente):
    # nome fixo (nao tem hash como /assets): pode ser substituido noutro deploy (captura nova, video regravado), por isso
    # nunca "immutable" - so um dia, para poupar o pedido a quem volta a ver o tutorial no mesmo dia
    for caminho in ("/videos/tutorial_pt.mp4", "/ajuda/digitos.png"):
        cc = cliente.get(caminho).headers.get("cache-control", "")
        assert cc == "public, max-age=86400", caminho


def test_video_inexistente_nas_linguas_sem_ficheiro(cliente, monkeypatch):
    monkeypatch.setattr(tutorial, "ficheiro_video", lambda pasta, lingua: None)
    assert cliente.get("/api/tutorial", headers={"X-Lingua": "pt"}).json()["video"] == ""


def test_ficheiros_estaticos_nao_deixam_sair_da_pasta(cliente):
    for caminho in ("/ajuda/../../pyproject.toml", "/ajuda/%2e%2e/%2e%2e/pyproject.toml", "/videos/..%2f..%2fpyproject.toml"):
        r = cliente.get(caminho)
        assert "requires-python" not in r.text, caminho


def test_assets_por_variavel_de_ambiente(tmp_path, monkeypatch):
    (tmp_path / "ajuda").mkdir()
    (tmp_path / "ajuda" / "so_este.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.setenv("RIFAS_ASSETS", str(tmp_path))
    c = TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "dados"))
    assert c.get("/ajuda/so_este.png").status_code == 200
    assert c.get("/ajuda/digitos.png").status_code in (404, 503)       # nao e a pasta de assets por defeito
