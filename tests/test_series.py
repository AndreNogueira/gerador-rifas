"""M1: series, prefixos, numeros a saltar e cor por serie. A logica pura (series.py) e a geracao real de PDFs com os fixtures."""
from pathlib import Path

import pytest
from pypdf import PdfReader

import core
from core import pedido, series
from conftest import erro_de, numeros_pdf, textos_pdf


def _t(**kw):
    kw.setdefault("saida", Path("out"))
    kw.setdefault("nome", "R")
    return core.Trabalho(**kw)


# ------------------------------------------------------------------ ler os campos
def test_ler_prefixos():
    assert series.ler_prefixos("") == () and series.ler_prefixos("  ,, ") == ()
    assert series.ler_prefixos("A-") == ("A-",)
    assert series.ler_prefixos(" A- , B-,C- ") == ("A-", "B-", "C-")
    assert series.ler_prefixos("Serie ") == ("Serie",)                            # as pontas sem espaco: o separador escreve-se (A-)


@pytest.mark.parametrize("txt", ["A1", "ABCDEFG", "Ç", "A-,A.", "A,a-b,A", ",".join("ABCDEFGHIJKLM")])
def test_prefixos_invalidos(txt):
    e = erro_de(series.ler_prefixos, txt)
    assert e[1] == "err_prefixo" and e[2] == {"max": 6, "series": 12}


def test_ler_saltar():
    assert series.ler_saltar("") == ()
    assert series.ler_saltar("13, 100-110 , 666 ,7 - 9") == ((13, 13), (100, 110), (666, 666), (7, 9))


@pytest.mark.parametrize("txt", ["a", "5-3", "1-2-3", "-5", "1e3", ",".join(str(i) for i in range(51))])
def test_saltar_invalido(txt):
    assert erro_de(series.ler_saltar, txt)[1] == "err_saltar"


def test_numeros_e_contar():
    assert series.numeros(1, 6) == [1, 2, 3, 4, 5, 6]
    assert series.numeros(1, 10, ((3, 3), (7, 9))) == [1, 2, 4, 5, 6, 10]
    assert series.contar(_t(inicio=1, fim=10)) == 10
    assert series.contar(_t(inicio=1, fim=10, saltar=((3, 3),), prefixos=("A-", "B-"))) == 18          # 9 numeros x 2 series


def test_cor_por_serie_so_com_varias_series():
    assert series.cor_da_serie(_t(prefixos=("A", "B", "C"), cor_por_serie=True), 1) == series.PALETA[1]
    assert series.cor_da_serie(_t(prefixos=("A", "B", "C")), 1) is None                       # desligada
    assert series.cor_da_serie(_t(prefixos=("A",), cor_por_serie=True), 0) is None            # uma serie so
    assert series.cor_da_serie(_t(prefixos=tuple("ABCDEFGH"), cor_por_serie=True), 7) == series.PALETA[7 % len(series.PALETA)]


# ------------------------------------------------------------------ o plano de ficheiros
@pytest.mark.parametrize("kw,por_pagina", [
    (dict(fim=1203, por_ficheiro=500), 5), (dict(fim=30, digitos=2), 5), (dict(fim=12000, por_ficheiro=5000), 5),
    (dict(inicio=7, fim=12, por_ficheiro=4, digitos=3), 2), (dict(inicio=0, fim=9, digitos=1), 1),
])
def test_sem_extras_o_plano_e_igual_ao_de_sempre(kw, por_pagina):
    tr = _t(**kw)
    antigo = [(p, a, b) for p, a, b in core.planear(tr, por_pagina)]
    novo = [(p.destino, p.numeros[0], p.numeros[-1]) for p in series.planear_partes(tr, por_pagina)]
    assert novo == antigo
    assert all(p.prefixo == "" and p.cor is None for p in series.planear_partes(tr, por_pagina))


def test_varias_series_cada_uma_com_os_seus_ficheiros():
    partes = series.planear_partes(_t(fim=12, por_ficheiro=5, prefixos=("A-", "B-"), cor_por_serie=True), 5)
    assert [(p.destino.as_posix(), p.numeros[0], p.numeros[-1], p.prefixo, p.cor is not None) for p in partes] == [
        ("out/R - A - 0001 - 0005.pdf", 1, 5, "A-", True), ("out/R - A - 0006 - 0010.pdf", 6, 10, "A-", True),
        ("out/R - A - 0011 - 0012.pdf", 11, 12, "A-", True), ("out/R - B - 0001 - 0005.pdf", 1, 5, "B-", True),
        ("out/R - B - 0006 - 0010.pdf", 6, 10, "B-", True), ("out/R - B - 0011 - 0012.pdf", 11, 12, "B-", True)]
    assert partes[0].cor != partes[3].cor


def test_um_pdf_por_serie_no_modo_unico_e_um_prefixo_so_nao_muda_os_nomes():
    unico = series.planear_partes(_t(fim=12, prefixos=("A-", "B-")), 5)
    assert [p.destino.name for p in unico] == ["R - A - 0001 - 0012.pdf", "R - B - 0001 - 0012.pdf"]
    um = series.planear_partes(_t(fim=12, prefixos=("A-",)), 5)
    assert [(p.destino.name, p.prefixo) for p in um] == [("R - 0001 - 0012.pdf", "A-")]


def test_os_numeros_saltados_nao_entram_e_os_nomes_usam_o_1_e_o_ultimo_impressos():
    partes = series.planear_partes(_t(fim=8, por_ficheiro=5, saltar=((1, 1), (3, 3))), 5)
    assert [(p.destino.name, p.numeros) for p in partes] == [("R - 0002 - 0007.pdf", [2, 4, 5, 6, 7]), ("R - 0008 - 0008.pdf", [8])]


def test_validacao_dos_extras():
    assert erro_de(series.planear_partes, _t(fim=3, saltar=((1, 3),)), 5)[1] == "err_intervalo"       # os saltos comem tudo
    assert erro_de(core.planear, _t(fim=9, prefixos=("A1",)), 5)[1] == "err_prefixo"
    assert erro_de(core.planear, _t(fim=9, prefixos=("A-", "A.")), 5)[1] == "err_prefixo"             # o mesmo nome de ficheiro
    assert erro_de(core.planear, _t(fim=9, saltar=((5, 2),)), 5)[1] == "err_saltar"


# ------------------------------------------------------------------ os campos de texto e o resumo
def _campos(**kw):
    base = dict(saida="", nome="R", inicio="1", fim="12", max_ficheiro="5", digitos="4", modo="varios")
    return {**base, **kw}


def test_trabalho_de_campos_com_extras_e_a_ordem_dos_erros():
    tr = pedido.trabalho_de_campos(**_campos(prefixos="A-, B-", saltar="3, 7-8", cor_serie=True))
    assert (tr.prefixos, tr.saltar, tr.cor_por_serie) == (("A-", "B-"), ((3, 3), (7, 8)), True)
    assert pedido.trabalho_de_campos(**_campos()).prefixos == ()
    assert erro_de(pedido.trabalho_de_campos, **_campos(prefixos="9"))[1] == "err_prefixo"
    assert erro_de(pedido.trabalho_de_campos, **_campos(saltar="x"))[1] == "err_saltar"
    assert erro_de(pedido.trabalho_de_campos, **_campos(inicio="x", prefixos="9"))[1] == "int_invalido"       # os numeros leem-se primeiro


def test_resumo_com_series_e_saltos():
    r = lambda **kw: pedido.resumo_do_pedido(pedido.trabalho_de_campos(**_campos(**kw)), 5, True)
    assert r(prefixos="A-, B-") == ("24 números · 6 PDF(s) · 6 páginas no total", False)
    assert r(prefixos="A-, B-", max_ficheiro="10")[0] == "24 números · 4 PDF(s) · 6 páginas no total"
    assert r(prefixos="A-, B-", modo="unico")[0] == "24 números · 2 PDF(s) · 6 páginas no total"           # um PDF por serie
    assert r(saltar="1-2", max_ficheiro="10")[0] == "10 números · 1 PDF(s) · 2 páginas no total"
    assert r(modo="unico")[0] == "12 números · 1 PDF com 3 páginas"                                        # sem extras, igual a sempre
    assert erro_de(pedido.resumo_do_pedido, pedido.trabalho_de_campos(**_campos(fim="3", saltar="1-3")), 5, True)[1] == "err_intervalo"


# ------------------------------------------------------------------ gerar a serio
@pytest.fixture(scope="module")
def prep5(fx):
    return core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))            # letra vetorial


@pytest.fixture(scope="module")
def prep5_img(fx):
    return core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.png"))            # algarismos em imagem


@pytest.fixture(scope="module")
def prep1(fx):
    return core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf"))


def _conteudo(caminho) -> str:
    return PdfReader(str(caminho)).pages[0].get_contents().get_data().decode("latin-1")


def test_gerar_duas_series_com_saltos_e_cor(tmp_path, prep5):
    tr = core.Trabalho(tmp_path, "R", 1, 6, digitos=4, prefixos=("A-", "B-"), saltar=((3, 3),), cor_por_serie=True)
    r = core.gerar(tr, prep5)
    assert [(x.caminho.name, x.paginas, x.ok) for x in r] == [("R - A - 0001 - 0006.pdf", 1, True), ("R - B - 0001 - 0006.pdf", 1, True)]
    a, b = (textos_pdf(x.caminho)[0] for x in r)
    assert "A-" in a and "B-" not in a and "B-" in b and "A-" not in b
    for x in r:
        assert numeros_pdf(x.caminho, 4)[0] == sorted(f"{n:04d}" for n in (1, 2, 4, 5, 6) for _ in range(2))     # o 3 nao saiu
    assert "0.78 0.16 0.16 rg" in _conteudo(r[0].caminho) and "0.08 0.4 0.75 rg" in _conteudo(r[1].caminho)    # a cor da serie
    assert "0.78 0.16 0.16 rg" not in _conteudo(r[1].caminho)


def test_o_prefixo_acaba_antes_do_1_algarismo(tmp_path, prep5):
    import pypdfium2 as pdfium
    r = core.gerar(core.Trabalho(tmp_path, "R", 1, 5, prefixos=("AB-",)), prep5)
    doc = pdfium.PdfDocument(str(r[0].caminho))
    try:
        tp = doc[0].get_textpage()
        texto = tp.get_text_range()
        i_prefixo, i_digito = texto.index("AB-"), texto.index("0001")
        direita_do_prefixo = tp.get_charbox(i_prefixo + 2)[2]              # a borda direita do hifen
        esquerda_do_digito = tp.get_charbox(i_digito)[0]
        assert direita_do_prefixo <= esquerda_do_digito + 1.0, (direita_do_prefixo, esquerda_do_digito)
        tp.close()
    finally:
        doc.close()


def test_sem_prefixo_o_pdf_e_igual_ao_de_sempre(tmp_path, prep5):
    a = core.gerar(core.Trabalho(tmp_path / "a", "R", 1, 10), prep5)[0].caminho
    b = core.gerar(core.Trabalho(tmp_path / "b", "R", 1, 10, prefixos=(), saltar=(), cor_por_serie=True), prep5)[0].caminho
    assert textos_pdf(a) == textos_pdf(b) and _conteudo(a) == _conteudo(b)


def test_algarismos_em_imagem_aceitam_prefixo_e_cor_nova(tmp_path, prep5_img):
    r = core.gerar(core.Trabalho(tmp_path, "R", 1, 5, prefixos=("X", "Y"), cor_por_serie=True), prep5_img)
    assert [x.ok for x in r] == [True, True] and "X" in textos_pdf(r[0].caminho)[0] and "Y" in textos_pdf(r[1].caminho)[0]
    # a cor da serie vira um conjunto novo de 10 algarismos (imagens), e so quando e preciso: sem cor por serie nao ha mais imagens
    com_cor = len(PdfReader(str(r[0].caminho)).pages[0]["/Resources"]["/XObject"])
    sem = core.gerar(core.Trabalho(tmp_path / "sem", "R", 1, 5, prefixos=("X", "Y")), prep5_img)[0].caminho
    assert com_cor == len(PdfReader(str(sem)).pages[0]["/Resources"]["/XObject"]) + 10


def test_folha_de_uma_rifa_com_prefixo(tmp_path, prep1):
    p = prep1.com_folha("A4", 5)
    r = core.gerar(core.Trabalho(tmp_path, "R", 1, p.por_pagina, prefixos=("Z-",)), p)
    # uma vez em cada um dos numeros de cada rifa (o PDFium troca por vezes o hifen por um marcador no fim da linha: conta-se o «Z»)
    assert r[0].ok and textos_pdf(r[0].caminho)[0].count("Z") == p.por_pagina * p.info.n_numeros.get(1, 1)


def test_previa_com_prefixo_cor_e_saltos(prep5):
    pdf = core.pdf_da_previa(prep5, 1, 4, fim=10, prefixo="A-", cor=series.PALETA[0], saltar=((2, 3),))
    import io

    import pypdfium2 as pdfium
    assert PdfReader(io.BytesIO(pdf)).pages[0].get_contents().get_data().count(b"0.78 0.16 0.16 rg") > 0
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        tp = doc[0].get_textpage()
        texto = tp.get_text_range()
        tp.close()
    finally:
        doc.close()
    assert "A-" in texto and "0001" in texto and "0004" in texto and "0002" not in texto and "0003" not in texto
