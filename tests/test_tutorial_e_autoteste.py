"""Testes de core.tutorial (conteudo do tutorial e verificacao das imagens) e core.autoteste (exemplos do auto-teste).
Antes viviam em ajuda.py (lista_de_topicos, _caixas) e app.py (verificar_ajuda, selftest)."""
from pathlib import Path

from core import autoteste, i18n, tutorial

ASSETS = Path(__file__).resolve().parent.parent / "app" / "assets"


def test_lista_de_topicos_estrutura():
    top = tutorial.lista_de_topicos()
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
    assert probs[6:] == [f"falta a captura {lg}_{e}" for lg in ("pt", "en") for e in "abc"]


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
