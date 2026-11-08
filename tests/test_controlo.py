"""M2: o CSV da lista e a folha de controlo de vendas (PDF), sem web."""
import io
import time
from pathlib import Path

import pypdfium2 as pdfium

import core
from core import controlo, series


def _t(**kw):
    kw.setdefault("saida", Path("out"))
    kw.setdefault("nome", "R")
    return core.Trabalho(**kw)


# ------------------------------------------------------------------ os bilhetes
def test_bilhetes_sem_prefixo_com_prefixo_e_com_series():
    assert series.bilhetes(_t(inicio=1, fim=3, digitos=3)) == [("", "001"), ("", "002"), ("", "003")]
    assert series.bilhetes(_t(inicio=1, fim=2, digitos=2, prefixos=("A-",))) == [("A", "A-01"), ("A", "A-02")]
    assert series.bilhetes(_t(inicio=1, fim=3, digitos=2, prefixos=("A-", "B-"), saltar=((2, 2),))) == [
        ("A", "A-01"), ("A", "A-03"), ("B", "B-01"), ("B", "B-03")]
    assert series.bilhetes(_t(inicio=1, fim=12000, digitos=2))[-1] == ("", "12000")        # a largura cresce com o fim


# ------------------------------------------------------------------ CSV
def test_csv_utf8_com_bom_ponto_e_virgula_e_colunas_em_branco():
    dados = controlo.csv_da_lista([("A", "A-0001"), ("B", "B-0001")], ("Série", "Número", "Nome", "Contacto", "Pago"))
    assert dados.startswith("﻿".encode())
    linhas = dados.decode("utf-8-sig").split("\r\n")
    assert linhas == ["Série;Número;Nome;Contacto;Pago", "A;A-0001;;;", "B;B-0001;;;", ""]


def test_csv_nao_deixa_o_prefixo_virar_formula():
    linhas = controlo.csv_da_lista([("", "-X0001"), ("", "=1+1"), ("", "0001")], ("a", "b", "c", "d", "e")).decode("utf-8-sig").split("\r\n")
    assert linhas[1].startswith(";'-X0001") and linhas[2].startswith(";'=1+1") and linhas[3].startswith(";0001")


def test_csv_de_30000_bilhetes_e_rapido():
    t0 = time.perf_counter()
    dados = controlo.csv_da_lista([("", f"{i:05d}") for i in range(1, 30001)], ("a", "b", "c", "d", "e"))
    assert dados.count(b"\r\n") == 30001 and time.perf_counter() - t0 < 2


# ------------------------------------------------------------------ texto_cabe
def test_texto_cabe_na_helvetica_so_com_letras_do_windows_ocidental():
    assert controlo.texto_cabe("Série Número Contacto Pagó ñ ç") and controlo.texto_cabe("")
    assert not controlo.texto_cabe("Σειρά") and not controlo.texto_cabe("系列") and not controlo.texto_cabe("Zapłacono") and not controlo.texto_cabe("Číslo")


# ------------------------------------------------------------------ folha de controlo
def _textos(pdf: bytes) -> list:
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        saida = []
        for pg in doc:
            tp = pg.get_textpage()
            saida.append(tp.get_text_range())
            tp.close()
        return saida
    finally:
        doc.close()


def test_folha_com_o_titulo_cabecalhos_numeros_e_paginas():
    nums = [f"A-{i:04d}" for i in range(1, 76)]                                        # 75 -> 3 paginas de 36 (36 + 36 + 3)
    pdf = controlo.folha_de_controlo("Rifa de Natal: Controlo", nums, ("Número", "Nome", "Contacto", "Pago"))
    paginas = _textos(pdf)
    assert len(paginas) == 3
    p1, p2, p3 = paginas
    assert "Rifa de Natal: Controlo" in p1 and "1 / 3" in p1 and "3 / 3" in p3
    for cab in ("Número", "Nome", "Contacto", "Pago"):
        assert cab in p1 and cab in p3
    assert "A-0001" in p1 and "A-0036" in p1 and "A-0037" not in p1 and "A-0037" in p2 and "A-0075" in p3 and "A-0076" not in p3
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        assert [round(v) for v in doc[0].get_size()] == [595, 842]                       # A4
    finally:
        doc.close()


def test_folha_vazia_tem_uma_pagina_e_o_texto_perigoso_nao_parte_o_pdf():
    assert len(_textos(controlo.folha_de_controlo("x", [], ("a", "b", "c", "d")))) == 1
    pdf = controlo.folha_de_controlo("Rifa (2026) \\ 系列", ["A)-1", "(B"], ("N", "Nome", "C", "P"))   # parenteses, barra e chines
    texto = _textos(pdf)[0]
    assert "Rifa (2026)" in texto and "A)-1" in texto and "(B" in texto and "?" in texto


def test_folha_de_30000_bilhetes_e_rapida_e_tem_834_paginas():
    t0 = time.perf_counter()
    pdf = controlo.folha_de_controlo("T", [f"{i:05d}" for i in range(1, 30001)], ("N", "Nome", "C", "P"))
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        assert len(doc) == 834 and time.perf_counter() - t0 < 15                         # 30 000 / 36 = 833,3
    finally:
        doc.close()
