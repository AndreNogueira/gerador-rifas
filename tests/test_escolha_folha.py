"""Testes de core.escolha_folha: papel, margem e rifas por folha escritos pelo utilizador. Antes vivia em app.py
(App._recalcular_folha, _render_folha, _prep_atual)."""
import pytest

import core
from core import escolha_folha as ef
from conftest import erro_de


@pytest.fixture(scope="module")
def info1(fx):
    return core.analisar_template(fx("template_exemplo_1_rifa.pdf"))       # rifa de 190 x 55 mm


@pytest.fixture(scope="module")
def info5(fx):
    return core.analisar_template(fx("template_exemplo.pdf"))


def test_tem_folha(info1, info5):
    assert ef.tem_folha(info1)
    assert not ef.tem_folha(info5) and not ef.tem_folha(None)
    from dataclasses import replace
    assert not ef.tem_folha(replace(info1, celula=None))


# ------------------------------------------------------------------ margem
@pytest.mark.parametrize("txt, valor", [("5", 5), (" 0 ", 0), ("50", 50), ("+7", 7)])
def test_ler_margem_valida(txt, valor):
    assert ef.ler_margem(txt) == valor


@pytest.mark.parametrize("txt", ["", "-1", "51", "5.5", "abc", "100"])
def test_ler_margem_invalida(txt):
    e = erro_de(ef.ler_margem, txt)
    assert e[:2] == ("ErroRifas", "int_invalido") and e[2]["campo"].startswith("Margem")


# ------------------------------------------------------------------ escolher_folha
def test_porfolha_vazio_e_o_maximo(info1):
    r = ef.escolher_folha(info1, "A4", "5", "")
    assert (r.disp.n, r.disp.maximo, r.acima) == (5, 5, False)
    assert ef.escolher_folha(info1, "A4", "5", "   ").disp.n == 5


def test_porfolha_menor_igual_e_maior_que_o_maximo(info1):
    r = ef.escolher_folha(info1, "A4", "5", "3")
    assert (r.disp.n, r.disp.maximo, r.acima) == (3, 5, False)
    assert ef.escolher_folha(info1, "A4", "5", "5").acima is False
    r = ef.escolher_folha(info1, "A4", "5", "9")
    assert (r.disp.n, r.disp.maximo, r.acima) == (5, 5, True)       # fica no maximo mas avisa


def test_papel_e_margem_mudam_o_resultado(info1):
    assert ef.escolher_folha(info1, "A3", "5", "").disp.n == 10
    assert ef.escolher_folha(info1, "A4", "12", "").disp.n == 3
    assert ef.escolher_folha(info1, "Letter", "0", "").disp.papel == "Letter"


@pytest.mark.parametrize("porfolha", ["0", "-2", "x", "1.5"])
def test_porfolha_invalido(info1, porfolha):
    e = erro_de(ef.escolher_folha, info1, "A4", "5", porfolha)
    assert e[:2] == ("ErroRifas", "int_invalido") and e[2]["campo"].startswith("Rifas por folha")


def test_a_margem_e_verificada_antes_das_rifas_por_folha(info1):
    e = erro_de(ef.escolher_folha, info1, "A4", "99", "x")
    assert e[2]["campo"].startswith("Margem")


def test_erros_do_motor_passam(info1, info5):
    assert erro_de(ef.escolher_folha, info5, "A4", "5", "")[1] == "err_folha_varias"
    assert erro_de(ef.escolher_folha, info1, "A5", "50", "")[1] == "err_rifa_grande"        # 50 mm de margem em cada lado: nao cabe


# ------------------------------------------------------------------ texto da folha
def test_texto_da_folha_normal(info1):
    r = ef.escolher_folha(info1, "A4", "5", "")
    txt, aviso = ef.texto_da_folha(r.disp, r.acima)
    assert not aviso and "A4" in txt and "190" in txt and "55" in txt and "\n" not in txt


def test_texto_da_folha_acima_do_maximo_e_muitas(info1):
    r = ef.escolher_folha(info1, "A4", "5", "9")
    txt, aviso = ef.texto_da_folha(r.disp, r.acima)
    assert aviso and txt.count("\n") == 1 and txt.endswith(core.i18n.t("lay_acima", max=5))
    from dataclasses import replace
    pequena = replace(info1, celula=core.Ret(0, 0, 70 * core.MM, 20 * core.MM))
    r = ef.escolher_folha(pequena, "A4", "5", "")
    assert r.disp.n > core.AVISO_POR_PAGINA
    txt, aviso = ef.texto_da_folha(r.disp, r.acima)
    assert aviso and txt.endswith(core.i18n.t("aviso_muitas", n=r.disp.n))


def test_texto_da_folha_recortada_e_rodadas(fx):
    info = core.analisar_template(fx("template_exemplo_1_rifa_a4.pdf"))        # a rifa ocupa so parte da pagina
    r = ef.escolher_folha(info, "A4", "5", "")
    txt, _ = ef.texto_da_folha(r.disp, r.acima)
    assert core.i18n.t("lay_recortada") in txt
    r = ef.escolher_folha(core.analisar_template(fx("template_exemplo_1_rifa.pdf")), "A3", "5", "")
    assert r.disp.rodadas == 0 and core.i18n.t("lay_rodadas", r=1) not in ef.texto_da_folha(r.disp, False)[0]


# ------------------------------------------------------------------ preparado_com_folha
def test_preparado_com_folha(fx):
    p5 = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    p1 = core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf"))
    assert ef.preparado_com_folha(None, None) is None
    assert ef.preparado_com_folha(p5, None) is p5                    # varias rifas por pagina: o proprio
    disp = ef.escolher_folha(p1.info, "A4", "5", "").disp
    p = ef.preparado_com_folha(p1, disp)
    assert p is not p1 and p.disp is disp and p.por_pagina == 5 and p1.disp is None


def test_preparado_com_folha_sem_folha_valida(fx):
    p1 = core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf"))
    assert erro_de(ef.preparado_com_folha, p1, None) == ("ErroRifas", "erro_inesperado", {"erro": "?"})
    erro = core.ErroRifas("int_invalido", campo="Margem")
    with pytest.raises(core.ErroRifas) as e:
        ef.preparado_com_folha(p1, None, erro)
    assert e.value is erro                                           # devolve o erro da folha, para a interface o mostrar
