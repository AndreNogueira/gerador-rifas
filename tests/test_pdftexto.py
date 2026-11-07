"""Caracterizacao: o interpretador de content streams (pdftexto.py), puro (so pypdf)."""
import re

import pytest

import core
import pdftexto


def test_mul_composicao_de_matrizes():
    assert pdftexto.mul((1, 0, 0, 1, 5, 6), (2, 0, 0, 3, 1, 1)) == (2, 0, 0, 3, 11, 19)
    assert pdftexto.mul(pdftexto.IDENT, (2, 0, 0, 3, 1, 1)) == (2, 0, 0, 3, 1, 1)
    assert pdftexto._trans(3, 4) == (1.0, 0.0, 0.0, 1.0, 3, 4)


def test_utf16_hex():
    assert pdftexto._utf16("0041") == "A"
    assert pdftexto._utf16("zz") == ""                     # hexadecimal invalido -> vazio
    assert pdftexto._utf16("004") == "@"                   # quirk: um numero impar de digitos e completado com 0 («0040»)


def test_parse_tounicode_char_range_e_lista():
    cmap = (b"begincmap 1 begincodespacerange <00> <FF> endcodespacerange "
            b"2 beginbfchar <01> <0030> <02> <0031> endbfchar "
            b"1 beginbfrange <10> <12> <0041> endbfrange "
            b"1 beginbfrange <20> <22> [<0058> <0059> <005A>] endbfrange endcmap")
    assert pdftexto.parse_tounicode(cmap) == {1: "0", 2: "1", 16: "A", 17: "B", 18: "C", 32: "X", 33: "Y", 34: "Z"}
    assert pdftexto.parse_tounicode(b"sem cmap") == {}


def test_cmyk_para_rgb_simples():
    assert pdftexto._cmyk(0, 0, 0, 1) == (0, 0, 0)
    assert pdftexto._cmyk(1, 0, 0, 0) == (0, 1, 1)
    assert pdftexto._cmyk(0, 0, 0, 0) == (1, 1, 1)


def test_extrator_le_as_corridas_e_os_tokens(fx):
    rd = core._abrir_leitor(fx("template_exemplo.pdf"))
    ex = pdftexto.Extrator(rd, rd.pages[0])
    assert len(ex.corridas) == 60
    numeros = [c for c in ex.corridas if re.fullmatch(r"0\d{3}", c.texto)]
    assert len(numeros) == 10 and {c.tamanho for c in numeros} == {19.0, 20.0}
    assert sorted({c.direcao for c in numeros}) == [(0.0, 1.0), (1.0, 0.0)]       # talao a subir, numero principal na horizontal
    toks = ex.tokens(core.PADRAO_EXEMPLO)
    assert [(t.texto, round(t.avanco, 2)) for t in toks[:4]] == [("0001", 52.88), ("0001", 55.66), ("0002", 52.88), ("0002", 55.66)]
    assert sorted(t.texto for t in toks) == ["0001", "0001", "0002", "0002", "0003", "0003", "0004", "0004", "0005", "0005"]


def test_extrator_do_ficheiro_de_algarismos(fx):
    rd = core._abrir_leitor(fx("digitos_exemplo.pdf"))
    ex = pdftexto.Extrator(rd, rd.pages[0])
    assert [c.texto for c in ex.corridas] == ["0123456789"]
    f = ex.corridas[0].fonte
    assert f.nome == "BitstreamVeraSans-Bold" and f.largura(ord("0")) == pytest.approx(695.8008)


def test_apagar_remove_so_os_tokens_pedidos(fx):
    rd = core._abrir_leitor(fx("template_exemplo.pdf"))
    from pypdf import PdfWriter
    w = PdfWriter()
    w.add_page(rd.pages[0])
    ex = pdftexto.Extrator(w, w.pages[0])
    toks = ex.tokens(core.PADRAO_EXEMPLO)
    ex.apagar([t for t in toks if t.texto == "0001"])
    ex2 = pdftexto.Extrator(w, w.pages[0])
    restantes = sorted(t.texto for t in ex2.tokens(core.PADRAO_EXEMPLO))
    assert restantes == ["0002", "0002", "0003", "0003", "0004", "0004", "0005", "0005"]
