"""Testes de core.tutorial (conteudo do tutorial e verificacao das imagens) e core.autoteste (exemplos do auto-teste).
Antes viviam em ajuda.py (lista_de_topicos, _caixas) e app.py (verificar_ajuda, selftest)."""
from pathlib import Path

import pytest

from core import autoteste, i18n, tutorial

ASSETS = Path(__file__).resolve().parent.parent / "app" / "assets"


def test_lista_de_topicos_estrutura():
    top = tutorial.lista_de_topicos()[:tutorial.N_BASE]            # os de base; os das funcionalidades vem a seguir (ver test_funcionalidades.py)
    assert len(top) == 8 and tutorial.TOPICO_ALGARISMOS == 3
    for titulo_menu, titulo, texto, imagens in top:
        assert titulo_menu.strip() and titulo and texto
        for im in imagens:
            assert im[0] in ("fixa", "rec") and (len(im) == 2 if im[0] == "fixa" else len(im) == 3)
    assert top[tutorial.TOPICO_ALGARISMOS][3] == [("fixa", "digitos.png"), ("rec", "a", "c2")]    # o topico «2 Algarismos»
    assert top[-1][3] == []                                                    # a ultima pagina (dicas) nao tem imagens


def test_lista_de_topicos_muda_com_a_lingua_e_sem_marcadores_por_substituir():
    pt = tutorial.lista_de_topicos()
    i18n.definir("en")
    en = tutorial.lista_de_topicos()
    assert pt != en and len(pt) == len(en)
    for lg in ("pt", "en", "ja"):
        i18n.definir(lg)
        for _, titulo, texto, _ in tutorial.lista_de_topicos():
            assert "{" not in texto and "{" not in titulo, lg


def test_ficheiros_do_tutorial_da_app_existem_para_todas_as_linguas():
    # o mesmo que app.verificar_ajuda(), com os assets reais da app Windows
    assert tutorial.verificar_ajuda(ASSETS / "ajuda", ASSETS / "video", i18n.LINGUAS) == []


def test_verificar_ajuda_pastas_vazias(tmp_path):
    probs = tutorial.verificar_ajuda(tmp_path, tmp_path, ["pt", "en"])
    assert probs[:4] == ["falta modelo.jpg", "falta modelo1.jpg", "falta digitos.png", "falta folha.png"]
    assert probs[4:6] == ["falta o video tutorial_pt.mp4", "falta o video tutorial_en.mp4"]
    n_func = sum(len(f.plataformas) for f in tutorial.FUNCIONALIDADES) * 2          # um video em pt e um em en por funcionalidade e plataforma
    assert all(p.startswith("falta o video ") for p in probs[6:6 + n_func]) and len(probs[6:6 + n_func]) == n_func       # ver test_funcionalidades.py
    assert probs[6 + n_func:] == [f"falta a captura {lg}_{e}" for lg in ("pt", "en") for e in ("wa", "wb", "wc", "a", "b", "c")]       # as do site e as da app Windows


def test_verificar_ajuda_video_pequeno_conta_como_em_falta(tmp_path):
    (tmp_path / "tutorial_pt.mp4").write_bytes(b"x" * 99_999)
    (tmp_path / "tutorial_en.mp4").write_bytes(b"x" * 100_000)
    probs = tutorial.verificar_ajuda(tmp_path, tmp_path, [])
    assert "falta o video tutorial_pt.mp4" in probs and "falta o video tutorial_en.mp4" not in probs


def test_caixas(tmp_path):
    assert tutorial.caixas(tmp_path) == {}
    (tmp_path / "ajuda.json").write_text("nao e json")
    assert tutorial.caixas(tmp_path) == {}
    (tmp_path / "ajuda.json").write_text('{"pt": {"a": {"c1": [0, 1, 2, 3]}}}')
    assert tutorial.caixas(tmp_path) == {"pt": {"a": {"c1": [0, 1, 2, 3]}}}


def test_autoteste_gerar_exemplos(tmp_path, fx):
    linhas, codigo = autoteste.gerar_exemplos(fx("template_exemplo.pdf").parent, tmp_path)
    assert codigo == 0
    assert linhas == [
        "digitos_exemplo.png: ok (13 paginas)",
        "digitos_exemplo.pdf: ok (13 paginas)",
        "1 rifa, A4, margem 5, digitos_exemplo.png: ok (5 por folha, 5 paginas)",
        "1 rifa, A3, margem 5, digitos_exemplo.png: ok (10 por folha, 3 paginas)",
        "1 rifa, A4, margem 12, digitos_exemplo.png: ok (3 por folha, 8 paginas)",
        "1 rifa, A4, margem 5, digitos_exemplo.pdf: ok (5 por folha, 5 paginas)",
        "1 rifa, A3, margem 5, digitos_exemplo.pdf: ok (10 por folha, 3 paginas)",
        "1 rifa, A4, margem 12, digitos_exemplo.pdf: ok (3 por folha, 8 paginas)"]
    assert len(list((tmp_path / "folha").glob("*.pdf"))) == 6


# ------------------------------------------------------------------ recorte (imagens do tutorial na webapp)
def test_recorte_devolve_png_e_largura_logica():
    from PIL import Image
    import io
    png, largura = tutorial.recorte(ASSETS / "ajuda", "pt", "a", "c1")
    assert png.startswith(b"\x89PNG")
    box = tutorial.caixas(ASSETS / "ajuda")["pt"]["a"]
    x0, y0, x1, y1 = box["c1"]
    with Image.open(io.BytesIO(png)) as im:
        assert im.size == (x1 - x0, y1 - y0)
    assert largura == pytest.approx((x1 - x0) / float(box["escala"]))


def test_recorte_lingua_sem_imagens_cai_no_ingles_ou_portugues():
    assert tutorial.recorte(ASSETS / "ajuda", "xx", "a", "c1") == tutorial.recorte(ASSETS / "ajuda", "en", "a", "c1")


@pytest.mark.parametrize("estado, zona", [("a", "zona_que_nao_existe"), ("z", "c1")])
def test_recorte_inexistente_devolve_none(estado, zona):
    assert tutorial.recorte(ASSETS / "ajuda", "pt", estado, zona) is None


def test_recorte_pasta_sem_ajuda_devolve_none(tmp_path):
    assert tutorial.recorte(tmp_path, "pt", "a", "c1") is None


# ------------------------------------------------------------------ capturas do site (e2e/capturas.spec.ts) em vez das da app Windows
def _estados(plataforma):
    return {im[1] for _, _, _, imgs in tutorial.lista_de_topicos(plataforma)[:tutorial.N_BASE] for im in imgs if im[0] == "rec"}


def test_o_site_usa_as_suas_capturas_e_a_app_windows_as_dela():
    assert _estados("web") == {"wa", "wb", "wc"} and _estados("windows") == {"a", "b", "c"}
    web, windows = tutorial.lista_de_topicos("web")[:tutorial.N_BASE], tutorial.lista_de_topicos("windows")[:tutorial.N_BASE]
    assert [[("rec", im[1][1:], im[2]) if im[0] == "rec" else im for im in t[3]] for t in web] == [t[3] for t in windows]      # mesma estrutura


@pytest.mark.parametrize("lg", [x for x in i18n.LINGUAS if x not in tutorial.SEM_CAPTURAS_PROPRIAS])
def test_as_capturas_do_site_existem_e_as_zonas_cabem_na_imagem(lg):
    from PIL import Image
    zonas = tutorial.caixas(ASSETS / "ajuda")[lg]
    for estado in tutorial.ESTADOS_WEB:
        with Image.open(ASSETS / "ajuda" / f"{lg}_{estado}.png") as im:
            largura, altura = im.size
        for nome, caixa in ((k, v) for k, v in zonas[estado].items() if k != "escala"):
            x0, y0, x1, y1 = caixa
            assert 0 <= x0 < x1 <= largura and 0 <= y0 < y1 <= altura and x1 - x0 > 50 and y1 - y0 > 20, (lg, estado, nome, caixa, im.size)


def test_verificar_ajuda_exige_as_capturas_da_plataforma(tmp_path):
    so_web = tutorial.verificar_ajuda(tmp_path, tmp_path, ["pt"], ("web",))
    so_windows = tutorial.verificar_ajuda(tmp_path, tmp_path, ["pt"], ("windows",))
    assert "falta a captura pt_wa" in so_web and "falta a captura pt_a" not in so_web
    assert "falta a captura pt_a" in so_windows and "falta a captura pt_wa" not in so_windows
