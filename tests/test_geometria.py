"""Caracterizacao: geometria do texto, nomes de letras e ajuste de tamanho (funcoes puras de core.py)."""
import pytest

import core
from core import Slot


def _slot(rot=0, origem=(100.0, 200.0), tamanho=20.0, texto="0001", avanco=50.0):
    return Slot(campo=1, texto=texto, origem=origem, rot=rot, tamanho=tamanho, cor=(0, 0, 0), fonte="f", avanco=avanco)


def test_rot_de_direcao():
    assert [core._rot_de(d) for d in ((1, 0), (0, 1), (-1, 0), (0, -1))] == [0, 90, 180, 270]
    assert core._rot_de((1, 0.2)) == 0 and core._rot_de((0.9, 0.9)) == 0 and core._rot_de((0, 0)) == 0   # arredonda ao quarto de volta


def test_eixos_uv_xy():
    assert [core._uv((3, 4), r) for r in (0, 90, 180, 270)] == [(3, 4), (-4, 3), (-3, -4), (4, -3)]
    assert [core._xy(3, 4, r) for r in (0, 90, 180, 270)] == [(3, 4), (4, -3), (-3, -4), (-4, 3)]
    for r in (0, 90, 180, 270):
        assert core._uv(core._xy(3, 4, r), r) == (3, 4)       # sao inversas uma da outra


def test_formatacao_de_numeros_f():
    assert core._f(0) == "0" and core._f(1.5) == "1.5" and core._f(10) == "10" and core._f(100.0) == "100"
    assert core._f(1.23456789) == "1.2346"            # 4 casas
    assert core._f(-0.00001) == "-0"                  # quirk: um negativo minusculo escreve-se «-0»


def test_matriz_texto():
    assert [core._matriz_texto(r, 10, 20.5) for r in (0, 90, 180, 270)] == [
        "1 0 0 1 10 20.5 Tm", "0 1 -1 0 10 20.5 Tm", "-1 0 0 -1 10 20.5 Tm", "0 -1 1 0 10 20.5 Tm"]


def test_slot_vertical_e_caixa():
    assert _slot(90).vertical and _slot(270).vertical and not _slot(0).vertical and not _slot(180).vertical
    c = _slot(0).caixa(0)
    assert (c.x0, c.y0, c.x1, c.y1) == (100.0, 178.0, 150.0, 208.0)     # de -1.1*tam a +0.4*tam em v; 0..avanco em u
    c = _slot(0).caixa()                                                 # margem por defeito = 3
    assert (c.x0, c.y0, c.x1, c.y1) == (97.0, 175.0, 153.0, 211.0)
    c = _slot(90).caixa(0)
    assert (c.x0, c.y0, c.x1, c.y1) == (78.0, 150.0, 108.0, 200.0)
    assert (c.width, c.height) == (30.0, 50.0)


def test_origem_pdf_centra_o_numero_novo():
    caixa = (0, 0, 595, 842)
    assert core._origem_pdf(_slot(0), 40, caixa) == (105.0, 642.0)          # y do PDF = altura - y da pagina
    assert core._origem_pdf(_slot(90), 40, caixa, 2.0) == (102.0, 647.0)
    # a caixa (MediaBox) com origem fora de (0,0) desloca o resultado
    assert core._origem_pdf(_slot(0), 40, (10, 20, 605, 862)) == (115.0, 662.0)


def test_fator_ajuste_so_encolhe():
    s = _slot()
    assert core.fator_ajuste(s, "0001") == 1.0
    assert core.fator_ajuste(s, "001") == 1.0            # menos algarismos: nao aumenta
    assert core.fator_ajuste(s, "00001") == pytest.approx(0.8)
    assert core.fator_ajuste(s, "00000001") == pytest.approx(0.5)
    assert core.fator_ajuste(s, "") == 1.0


def test_nomes_de_letra():
    assert core.limpar_nome_fonte("ABCDEF+Arial-Bold") == "Arial-Bold"
    assert core.limpar_nome_fonte("abcdef+Arial") == "abcdef+Arial"      # so tira prefixos de 6 MAIUSCULAS
    assert core.limpar_nome_fonte("ABCDE+X") == "ABCDE+X"
    assert core.normalizar("ABCDEF+Comic Sans MS") == "comicsansms"
    assert core._mesma_letra("Comic Sans MS Regular", "ComicSansMS")
    assert not core._mesma_letra("Arial", "Verdana")
    assert core._mesma_letra("", "x")                                     # quirk: o vazio «e prefixo» de tudo
