"""Caracterizacao: gerar (escrever PDFs), verificar (reler), pre-visualizacao e Documento. Faz E/S real em tmp_path."""
import io
import threading
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

import core
from core import i18n
from conftest import erro_de, numeros_pdf, textos_pdf


@pytest.fixture(scope="module")
def prep5(fx):
    """Template com 5 rifas por pagina, algarismos em PDF (letra vetorial)."""
    return core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))


@pytest.fixture(scope="module")
def prep1(fx):
    """Template de uma so rifa, algarismos em PDF."""
    return core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf"))


def _paginas(caminho):
    rd = PdfReader(str(caminho))
    return len(rd.pages), [float(v) for v in rd.pages[0].mediabox]


# ------------------------------------------------------------------ gerar: ficheiro unico
def test_gerar_ficheiro_unico(tmp_path, prep5):
    logs, prog = [], []
    r = core.gerar(core.Trabalho(tmp_path / "a", "Teste", 1, 12), prep5, log=logs.append, progresso=lambda a, b: prog.append((a, b)))
    assert [(x.caminho.name, x.paginas, x.erros, x.ok) for x in r] == [("Teste - 0001 - 0012.pdf", 3, [], True)]
    assert r[0].caminho.parent == tmp_path / "a" and r[0].caminho.exists()      # a pasta e criada
    assert _paginas(r[0].caminho) == (3, [0.0, 0.0, 595.0, 842.0])
    assert prog == [(1, 3), (2, 3), (3, 3)]                                     # conta paginas
    assert logs[0] == "⚠ 12 números não é múltiplo de 5; na última página alguns bilhetes ficam sem número."
    assert logs[1] == "A gerar «Teste - 0001 - 0012.pdf» (3 páginas)…"
    assert logs[2].startswith("✔ Teste - 0001 - 0012.pdf: 3 páginas, ")


def test_numeros_escritos_em_cada_pagina(tmp_path, prep5):
    r = core.gerar(core.Trabalho(tmp_path, "T", 1, 12), prep5)
    pags = numeros_pdf(r[0].caminho, 4)
    # cada numero aparece 2x (talao + parte principal); a ultima pagina so tem os 2 numeros pedidos
    assert pags[0] == sorted(f"{n:04d}" for n in range(1, 6) for _ in range(2))
    assert pags[1] == sorted(f"{n:04d}" for n in range(6, 11) for _ in range(2))
    assert pags[2] == ["0011", "0011", "0012", "0012"]
    assert "RIFA DE EXEMPLO" in textos_pdf(r[0].caminho)[0]


def test_gerar_varios_ficheiros(tmp_path, prep5):
    r = core.gerar(core.Trabalho(tmp_path, "Teste", 1, 12, por_ficheiro=5, digitos=6), prep5)
    assert [(x.caminho.name, x.paginas, x.ok) for x in r] == [
        ("Teste - 000001 - 000005.pdf", 1, True), ("Teste - 000006 - 000010.pdf", 1, True), ("Teste - 000011 - 000012.pdf", 1, True)]


def test_gerar_com_digitos_a_mais_avisa_e_reduz(tmp_path, prep5):
    logs = []
    core.gerar(core.Trabalho(tmp_path, "T", 1, 5, digitos=6), prep5, log=logs.append)
    assert "⚠ O template foi desenhado para 4 algarismos e vai usar 6; o tamanho dos números foi reduzido para 67% para caberem." in logs


def test_gerar_valida_antes_de_escrever(tmp_path, prep5):
    assert erro_de(core.gerar, core.Trabalho(tmp_path / "c", "Teste", 1, 12, por_ficheiro=3), prep5)[1] == "err_max_multiplo"
    assert not (tmp_path / "c").exists()
    assert erro_de(core.gerar, core.Trabalho(tmp_path / "c", "", 1, 12), prep5)[1] == "err_nome"


def test_gerar_cancelado_nao_escreve_pdfs(tmp_path, prep5):
    ev = threading.Event()
    ev.set()
    assert erro_de(core.gerar, core.Trabalho(tmp_path / "c", "Teste", 1, 12), prep5, cancelar=ev)[:2] == ("Cancelado", "cancelado")
    assert list((tmp_path / "c").glob("*.pdf")) == []          # a pasta chega a ser criada, mas fica vazia


def test_gerar_cancelar_a_meio(tmp_path, prep5):
    ev = threading.Event()
    def prog(feitas, total):
        if feitas == 2:
            ev.set()
    assert erro_de(core.gerar, core.Trabalho(tmp_path, "T", 1, 50), prep5, progresso=prog, cancelar=ev)[0] == "Cancelado"
    assert list(tmp_path.glob("*.pdf")) == []


def test_gerar_pasta_impossivel(tmp_path, prep5):
    (tmp_path / "f.txt").write_text("x")
    assert erro_de(core.gerar, core.Trabalho(tmp_path / "f.txt" / "sub", "T", 1, 5), prep5)[:2] == ("ErroRifas", "err_pasta")


def test_gerar_com_algarismos_em_imagem(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.png"))
    r = core.gerar(core.Trabalho(tmp_path, "I", 1, 10), prep)
    assert [(x.paginas, x.ok) for x in r] == [(2, True)]
    assert numeros_pdf(r[0].caminho, 4)[0] == sorted(f"{n:04d}" for n in range(1, 6) for _ in range(2))


@pytest.mark.parametrize("semente, n, digitos", [(1, 2, 4), (3, 8, 4), (5, 24, 4), (9, 12, 8), (10, 1, 4)])
@pytest.mark.parametrize("ext", ["pdf", "png"])
def test_gerar_templates_aleatorios(tmp_path, fx, semente, n, digitos, ext):
    prep = core.preparar(fx(f"aleatorio_s{semente}.pdf"), fx(f"aleatorio_s{semente}_algarismos.{ext}"))
    fim = 3 * n + 1                                              # 4 paginas, a ultima com 1 numero
    r = core.gerar(core.Trabalho(tmp_path, "A", 1, fim, digitos=digitos), prep)
    assert [(x.paginas, x.erros) for x in r] == [(4, [])]


# ------------------------------------------------------------------ gerar: uma so rifa por template (folha)
def test_gerar_folha_a4_enche_a_pagina(tmp_path, prep1):
    p = prep1.com_folha("A4", 5)
    logs = []
    r = core.gerar(core.Trabalho(tmp_path, "Um", 1, 12), p, log=logs.append)
    assert [(x.paginas, x.erros) for x in r] == [(3, [])]          # 12 numeros / 5 por folha
    n, caixa = _paginas(r[0].caminho)
    assert n == 3 and caixa == pytest.approx([0.0, 0.0, 595.276, 841.89])
    assert logs[0] == "Folha A4: 5 rifas por folha (190 × 55 mm cada)."
    pags = numeros_pdf(r[0].caminho, 4)
    assert pags[0] == sorted(f"{k:04d}" for k in range(1, 6) for _ in range(2))
    assert pags[2] == ["0011", "0011", "0012", "0012"]


def test_gerar_folha_com_menos_rifas_do_que_o_maximo(tmp_path, prep1):
    p = prep1.com_folha("A4", 5, 3)
    logs = []
    r = core.gerar(core.Trabalho(tmp_path, "Um", 1, 10), p, log=logs.append)
    assert r[0].paginas == 4 and r[0].ok
    assert "⚠ 10 números não é múltiplo de 3; na última página alguns bilhetes ficam sem número." in logs


def test_gerar_folha_a3_pede_mais_do_que_cabe(tmp_path, prep1):
    p = prep1.com_folha("A3", 5, 30)                              # pede 30, cabem 10: fica 10
    assert (p.por_pagina, p.disp.maximo) == (10, 10)
    logs = []
    r = core.gerar(core.Trabalho(tmp_path, "Um", 1, 30), p, log=logs.append)
    assert r[0].paginas == 3 and r[0].ok
    assert logs[0] == "Folha A3: 10 rifas por folha (190 × 55 mm cada)."
    assert not any("muitas" in l for l in logs)                   # 10 <= AVISO_POR_PAGINA (24)


def test_gerar_aviso_de_muitas_rifas_por_folha(tmp_path, prep1):
    from dataclasses import replace
    pequena = replace(prep1.info, celula=core.Ret(0, 0, 70 * core.MM, 20 * core.MM))      # rifa mais pequena => >24 por folha
    p = replace(prep1, info=pequena).com_folha("A4", 5)
    assert p.por_pagina > core.AVISO_POR_PAGINA
    logs = []
    core.gerar(core.Trabalho(tmp_path, "Um", 1, 3), p, log=logs.append)
    assert i18n.t("aviso_muitas", n=p.por_pagina) in logs


def test_gerar_folha_com_algarismos_em_imagem_e_mais_digitos(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.png")).com_folha("A4", 5)
    logs = []
    r = core.gerar(core.Trabalho(tmp_path, "Um", 1, 7, digitos=6), prep, log=logs.append)
    assert [(x.paginas, x.erros) for x in r] == [(2, [])]
    assert any("reduzido para 67%" in l for l in logs)


# ------------------------------------------------------------------ verificar
def test_verificar_aceita_o_que_foi_gerado(tmp_path, prep5):
    r = core.gerar(core.Trabalho(tmp_path, "T", 1, 10, digitos=6), prep5)
    assert core.verificar(r[0].caminho, core.linhas_de_numeros(1, 10, 5, 6), prep5, 6) == []


def test_verificar_deteta_paginas_a_mais_e_numeros_trocados(tmp_path, prep5):
    r = core.gerar(core.Trabalho(tmp_path, "T", 1, 5, digitos=6), prep5)
    assert core.verificar(r[0].caminho, core.linhas_de_numeros(1, 10, 5, 6), prep5, 6) == ["páginas: 1 em vez de 2"]
    erros = core.verificar(r[0].caminho, core.linhas_de_numeros(6, 10, 5, 6), prep5, 6)
    assert len(erros) == 1 and erros[0].startswith("página 1: esperado ['000006', '000006'")
    assert "mas tem ['000001', '000001', '000002'" in erros[0]


def test_resultado_ok_depende_dos_erros():
    assert core.Resultado(Path("x.pdf"), 1, []).ok and not core.Resultado(Path("x.pdf"), 1, ["e"]).ok


# ------------------------------------------------------------------ Documento
def test_documento_gravar_para_bytes_e_para_ficheiro(tmp_path, prep5):
    doc = core.Documento(prep5)
    doc.adicionar_linha(["0001", "0002", "0003", "0004", "0005"])
    doc.adicionar_linha(["0006"])                                 # linha curta: so o 1.o bilhete tem numero
    buf = io.BytesIO()
    doc.gravar(buf)
    assert buf.getvalue()[:5] == b"%PDF-" and len(PdfReader(io.BytesIO(buf.getvalue())).pages) == 2
    destino = tmp_path / "d.pdf"
    doc.gravar(destino)
    assert numeros_pdf(destino, 4)[1] == ["0006", "0006"]


def test_documento_guarda_o_fundo_uma_so_vez(prep5):
    doc = core.Documento(prep5)
    for _ in range(3):
        doc.adicionar_linha(["0001"])
    buf = io.BytesIO()
    doc.gravar(buf)
    rd = PdfReader(io.BytesIO(buf.getvalue()))
    assert len(rd.pages) == 3
    assert rd.pages[0]["/Resources"].get_object()["/XObject"].get_object()["/Bg"] == rd.pages[2]["/Resources"].get_object()["/XObject"].get_object()["/Bg"]


def test_matriz_da_rifa_na_folha(prep1):
    doc = core.Documento(prep1.com_folha("A4", 5))
    m0 = doc._matriz_rifa(10, 20, 0).split()
    m90 = doc._matriz_rifa(10, 20, 90).split()
    assert m0[:4] == ["1", "0", "0", "1"] and m90[:4] == ["0", "1", "-1", "0"]
    assert float(m0[4]) == pytest.approx(10.0) and float(m0[5]) == pytest.approx(841.89 - 20 - 156)


# ------------------------------------------------------------------ pre-visualizacao e imagens
def test_pagina_previa_e_um_png_da_primeira_pagina(prep5):
    png = core.pagina_previa(prep5, 1, 4)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert Image.open(io.BytesIO(png)).size == (1323, 1872)       # 595x842 pt a 160 dpi
    assert Image.open(io.BytesIO(core.pagina_previa(prep5, 1, 4, dpi=72))).size == (595, 842)


def test_pagina_previa_com_fim_curto_e_folha(prep5, prep1):
    assert core.pagina_previa(prep5, 998, 4, fim=1000)[:4] == b"\x89PNG"
    im = Image.open(io.BytesIO(core.pagina_previa(prep1.com_folha("A4", 5), 1, 4, dpi=72)))
    assert im.size == (596, 842)                                  # a folha A4 (595.276 pt arredonda para cima), nao o tamanho da rifa


def test_pagina_template_e_imagem_de_pdf(fx):
    assert Image.open(io.BytesIO(core.pagina_template(fx("template_exemplo.pdf")))).size == (744, 1053)    # 90 dpi
    assert core.png_de_pagina(fx("digitos_exemplo.pdf"), 72)[:4] == b"\x89PNG"
    assert core.imagem_de_pdf(fx("digitos_exemplo.pdf")).size == (4334, 917)


def test_gerar_aceita_qualquer_evento_com_is_set(tmp_path, prep5):
    """O cancelamento so usa `.is_set()`: um multiprocessing.Event (processo de trabalho) serve tal como um threading.Event."""
    import multiprocessing
    ev = multiprocessing.Event()
    ev.set()
    assert erro_de(core.gerar, core.Trabalho(tmp_path, "T", 1, 12), prep5, cancelar=ev)[:2] == ("Cancelado", "cancelado")

    class Falso:
        def is_set(self):
            return False
    assert core.gerar(core.Trabalho(tmp_path / "x", "T", 1, 5), prep5, cancelar=Falso())[0].ok
