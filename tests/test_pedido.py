"""Testes de core.pedido: o pedido (campos de texto -> Trabalho) e o resumo. Logica que antes vivia em app.py (App._trabalho, _resumo)."""
from pathlib import Path

import pytest

import core
from core import pedido
from conftest import erro_de


def _campos(**kw):
    base = dict(saida="C:/x", nome=" Rifa ", inicio="1", fim="100", max_ficheiro="50", digitos="4", modo="varios")
    base.update(kw)
    return base


# ------------------------------------------------------------------ ler_inteiro
@pytest.mark.parametrize("txt, valor", [("5", 5), (" 12 ", 12), ("+5", 5), ("-3", -3), ("1_000", 1000), ("007", 7), ("\t9\n", 9)])
def test_ler_inteiro_aceita_o_que_o_int_aceita(txt, valor):
    assert pedido.ler_inteiro(txt, "De") == valor


@pytest.mark.parametrize("txt", ["", "  ", "1.0", "1,5", "abc", "1 2", "0x10", "٣٣٣x"])
def test_ler_inteiro_recusa_o_resto(txt):
    assert erro_de(pedido.ler_inteiro, txt, "De") == ("ErroRifas", "int_invalido", {"campo": "De"})


def test_ler_inteiro_aceita_algarismos_unicode():
    assert pedido.ler_inteiro("٣٣", "x") == 33        # quirk herdado do int(): digitos arabes tambem servem


# ------------------------------------------------------------------ trabalho_de_campos
def test_trabalho_de_campos_varios():
    tr = pedido.trabalho_de_campos(**_campos())
    assert tr == core.Trabalho(saida=Path("C:/x"), nome="Rifa", inicio=1, fim=100, por_ficheiro=50, digitos=4)


def test_trabalho_de_campos_unico_ignora_o_maximo():
    tr = pedido.trabalho_de_campos(**_campos(modo="unico", max_ficheiro="lixo"))
    assert tr.por_ficheiro is None and (tr.inicio, tr.fim) == (1, 100)


def test_trabalho_de_campos_pasta_vazia_vira_path_vazio_e_nome_sem_espacos():
    tr = pedido.trabalho_de_campos(**_campos(saida="   ", nome="  A  B  "))
    assert tr.saida == Path("") and tr.nome == "A  B"
    # o nome NAO passa por nome_seguro aqui (so no validar/planear)
    assert pedido.trabalho_de_campos(**_campos(nome="a/b")).nome == "a/b"


@pytest.mark.parametrize("campos, rotulo", [
    (dict(inicio="x"), "De"),
    (dict(fim="x"), "Até"),
    (dict(max_ficheiro="x"), "Máximo de números por ficheiro"),
    (dict(digitos="x"), "Algarismos"),
])
def test_trabalho_de_campos_erro_com_o_rotulo_traduzido(campos, rotulo):
    e = erro_de(pedido.trabalho_de_campos, **_campos(**campos))
    assert e[:2] == ("ErroRifas", "int_invalido") and e[2]["campo"].startswith(rotulo)


def test_trabalho_de_campos_ordem_dos_erros():
    # o 1.o campo mal escrito (De, Ate, Maximo, Algarismos) e o que se reporta
    e = erro_de(pedido.trabalho_de_campos, **_campos(inicio="x", fim="y", max_ficheiro="z", digitos="w"))
    assert e[2]["campo"].startswith("De")
    e = erro_de(pedido.trabalho_de_campos, **_campos(fim="y", max_ficheiro="z", digitos="w"))
    assert e[2]["campo"].startswith("Até")
    e = erro_de(pedido.trabalho_de_campos, **_campos(max_ficheiro="z", digitos="w"))
    assert e[2]["campo"].startswith("Máximo")
    # no modo «unico» o maximo nem se le
    e = erro_de(pedido.trabalho_de_campos, **_campos(modo="unico", max_ficheiro="z", digitos="w"))
    assert e[2]["campo"].startswith("Algarismos")


def test_trabalho_de_campos_rotulo_muda_com_a_lingua():
    from core import i18n
    i18n.definir("en")
    e = erro_de(pedido.trabalho_de_campos, **_campos(inicio="x"))
    assert e[2]["campo"] == i18n.t("de") and e[2]["campo"] != "De"


# ------------------------------------------------------------------ rifas_por_pagina
def test_rifas_por_pagina(fx):
    info5 = core.analisar_template(fx("template_exemplo.pdf"))
    info1 = core.analisar_template(fx("template_exemplo_1_rifa.pdf"))
    assert pedido.rifas_por_pagina(None, None) == 1
    assert pedido.rifas_por_pagina(None, info5) == 5
    assert pedido.rifas_por_pagina(None, info1) == 1
    disp = core.disposicao_da_folha(info1, "A4", 5)
    assert pedido.rifas_por_pagina(disp, info1) == 5                 # a folha escolhida manda
    assert pedido.rifas_por_pagina(disp, None) == 5


# ------------------------------------------------------------------ resumo_do_pedido
def _tr(**kw):
    base = dict(saida=Path("x"), nome="n", inicio=1, fim=100, por_ficheiro=None, digitos=4)
    base.update(kw)
    return core.Trabalho(**base)


def test_resumo_ficheiro_unico():
    assert pedido.resumo_do_pedido(_tr(), 5, True) == ("100 números · 1 PDF com 20 páginas", False)
    assert pedido.resumo_do_pedido(_tr(fim=12), 5, True) == ("12 números · 1 PDF com 3 páginas", False)   # arredonda para cima


def test_resumo_varios_ficheiros():
    assert pedido.resumo_do_pedido(_tr(por_ficheiro=50), 5, True) == ("100 números · 2 PDF(s) · 20 páginas no total", False)
    assert pedido.resumo_do_pedido(_tr(fim=101, por_ficheiro=50), 1, True)[0] == "101 números · 3 PDF(s) · 101 páginas no total"


def test_resumo_aviso_de_multiplo_so_com_template():
    assert pedido.resumo_do_pedido(_tr(por_ficheiro=12), 5, True) == (
        "O máximo por ficheiro tem de ser múltiplo de 5.", True)
    # sem template carregado nao ha aviso (n vale 1 por defeito) e mostra-se o resumo normal
    assert pedido.resumo_do_pedido(_tr(por_ficheiro=12), 5, False) == ("100 números · 9 PDF(s) · 20 páginas no total", False)


def test_resumo_erros_e_a_ordem():
    assert erro_de(pedido.resumo_do_pedido, _tr(inicio=9, fim=1), 5, True) == ("ErroRifas", "err_intervalo", {})
    assert erro_de(pedido.resumo_do_pedido, _tr(por_ficheiro=0), 5, True) == ("ErroRifas", "err_max", {})
    assert erro_de(pedido.resumo_do_pedido, _tr(por_ficheiro=-1), 5, True) == ("ErroRifas", "err_max", {})
    # o intervalo e verificado antes do maximo por ficheiro
    assert erro_de(pedido.resumo_do_pedido, _tr(inicio=9, fim=1, por_ficheiro=0), 5, True)[1] == "err_intervalo"


def test_resumo_nao_chama_validar():
    # o resumo nao valida o nome, os algarismos nem inicio < 0: so o intervalo e o maximo
    texto, aviso = pedido.resumo_do_pedido(_tr(nome="", digitos=99, inicio=-5, fim=4), 5, True)
    assert texto == "10 números · 1 PDF com 2 páginas" and not aviso
    assert erro_de(core.validar, _tr(nome="", digitos=99, inicio=-5, fim=4), 5)[1] == "err_nome"


def test_resumo_um_numero_so():
    assert pedido.resumo_do_pedido(_tr(inicio=7, fim=7), 5, True)[0] == "1 números · 1 PDF com 1 páginas"
