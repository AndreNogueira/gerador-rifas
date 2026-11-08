"""M2: a lista de bilhetes em CSV e a folha de controlo de vendas imprimivel (PDF), sem web e sem template.

Quem vende rifas precisa de saber quem ficou com que numero e se ja pagou: o CSV abre-se no Excel/Calc e a folha imprime-se e
preenche-se a caneta. Ambos saem dos mesmos bilhetes que os PDFs das rifas (`series.bilhetes`): prefixos, series e numeros saltados incluidos.
A folha usa a Helvetica do PDF (WinAnsi): numa lingua cujas letras nao cabem nela (grego, russo, chines, polaco...) os textos
saem em ingles (`texto_cabe`); o CSV e UTF-8 com BOM e serve qualquer lingua.
"""
from __future__ import annotations

import csv
import io

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

A4 = (595.276, 841.89)
MARGEM = 36.0
ALTURA_LINHA = 20.0
LINHAS_POR_PAGINA = 36
_LARGURAS = (100.0, 200.0, 150.0, A4[0] - 2 * MARGEM - 450.0)       # numero, nome, contacto, pago
_TITULO_MAX = 70


def csv_da_lista(bilhetes: list, cabecalhos: tuple) -> bytes:
    """`bilhetes` = [(serie, numero)]; `cabecalhos` = (Serie, Numero, Nome, Contacto, Pago). UTF-8 com BOM, separado por «;»
    (o que o Excel em portugues e noutras linguas europeias espera) e com as colunas em branco para preencher."""
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";", lineterminator="\r\n")
    escritor.writerow(cabecalhos)
    for serie, numero in bilhetes:
        escritor.writerow([_sem_formulas(serie), _sem_formulas(numero), "", "", ""])
    return ("﻿" + saida.getvalue()).encode("utf-8")


def _sem_formulas(texto: str) -> str:
    """Uma folha de calculo executa o que comeca por = + - @ : o prefixo «-» (permitido) nao pode virar uma formula."""
    return "'" + texto if texto[:1] in ("=", "+", "-", "@", "\t", "\r") else texto


def texto_cabe(*textos: str) -> bool:
    """Se todos estes textos se escrevem com a Helvetica do PDF (WinAnsi, a codificacao do Windows em Europa Ocidental)."""
    try:
        for t in textos:
            t.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def _pdf_texto(texto: str) -> str:
    """Um texto como cadeia literal de PDF (latin-1; o que nao cabe em WinAnsi vira «?»)."""
    seguro = texto.encode("cp1252", "replace").decode("latin-1")
    return "(" + seguro.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ")"


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".") if v else "0"


def _pagina(numeros: list, titulo: str, cabecalhos: tuple, n: int, total: int) -> bytes:
    largura, altura = A4
    topo_tabela = altura - 62.0
    x = [MARGEM]
    for w in _LARGURAS:
        x.append(x[-1] + w)
    fundo = topo_tabela - ALTURA_LINHA - LINHAS_POR_PAGINA * ALTURA_LINHA
    ops = [f"BT /FB 14 Tf {_f(MARGEM)} {_f(altura - 42)} Td {_pdf_texto(titulo[:_TITULO_MAX])} Tj ET",
           f"BT /F 9 Tf {_f(largura - MARGEM - 40)} {_f(altura - 42)} Td {_pdf_texto(f'{n} / {total}')} Tj ET",
           f"0.9 g {_f(MARGEM)} {_f(topo_tabela - ALTURA_LINHA)} {_f(sum(_LARGURAS))} {_f(ALTURA_LINHA)} re f 0 g",
           "0.5 w"]
    for i, cab in enumerate(cabecalhos):
        ops.append(f"BT /FB 9 Tf {_f(x[i] + 5)} {_f(topo_tabela - ALTURA_LINHA + 6)} Td {_pdf_texto(cab)} Tj ET")
    for k in range(LINHAS_POR_PAGINA + 1):                                        # linhas horizontais (a 1.a e a do cabecalho)
        y = topo_tabela - ALTURA_LINHA - k * ALTURA_LINHA
        ops.append(f"{_f(MARGEM)} {_f(y)} m {_f(x[-1])} {_f(y)} l S")
    ops.append(f"{_f(MARGEM)} {_f(topo_tabela)} m {_f(x[-1])} {_f(topo_tabela)} l S")
    for cx in x:                                                                  # linhas verticais
        ops.append(f"{_f(cx)} {_f(topo_tabela)} m {_f(cx)} {_f(fundo)} l S")
    for k, numero in enumerate(numeros):
        y = topo_tabela - ALTURA_LINHA - (k + 1) * ALTURA_LINHA
        ops.append(f"BT /F 10 Tf {_f(x[0] + 5)} {_f(y + 6)} Td {_pdf_texto(numero)} Tj ET")
        ops.append(f"{_f(x[3] + _LARGURAS[3] / 2 - 5)} {_f(y + 5)} 10 10 re S")      # a caixa de «pago»
    return "\n".join(ops).encode("latin-1")


def folha_de_controlo(titulo: str, bilhetes: list, cabecalhos: tuple) -> bytes:
    """O PDF A4 da folha de controlo: `bilhetes` = [numero formatado] (p.ex. «A-0001»); `cabecalhos` = (Numero, Nome, Contacto, Pago).
    36 linhas por pagina, com o titulo e «n / N» no topo."""
    w = PdfWriter()
    fonte = lambda base: DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),   # noqa: E731
                                           NameObject("/BaseFont"): NameObject(base), NameObject("/Encoding"): NameObject("/WinAnsiEncoding")})
    recursos = w._add_object(DictionaryObject({NameObject("/Font"): DictionaryObject({
        NameObject("/F"): w._add_object(fonte("/Helvetica")), NameObject("/FB"): w._add_object(fonte("/Helvetica-Bold"))})}))
    grupos = [bilhetes[i:i + LINHAS_POR_PAGINA] for i in range(0, len(bilhetes), LINHAS_POR_PAGINA)] or [[]]
    for n, grupo in enumerate(grupos, 1):
        pg = w.add_blank_page(width=A4[0], height=A4[1])
        st = DecodedStreamObject()
        st.set_data(_pagina(grupo, titulo, cabecalhos, n, len(grupos)))
        pg[NameObject("/Contents")] = w._add_object(st.flate_encode())
        pg[NameObject("/Resources")] = recursos
    saida = io.BytesIO()
    w.write(saida)
    return saida.getvalue()
