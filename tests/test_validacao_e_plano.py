"""Caracterizacao: validacao do pedido (validar), plano de ficheiros (planear), nomes e linhas de numeros."""
from pathlib import Path

import pytest

import core
from conftest import erro_de

T = core.Trabalho
SAIDA = Path("out")


def _t(**kw):
    base = dict(saida=SAIDA, nome="n", inicio=1, fim=10)
    base.update(kw)
    return T(**base)


# ------------------------------------------------------------------ nome_seguro
@pytest.mark.parametrize("entrada, esperado", [
    ("Rifa Natal 2026", "Rifa Natal 2026"),
    ('  a<b>c:d"e/f\\g|h?i*j.. ', "abcdefghij"),     # tira os caracteres proibidos no Windows e os espacos/pontos das pontas
    ("...", ""),
    ("   ", ""),
    ("a\tb\x00c", "abc"),                              # caracteres de controlo desaparecem
    ("a/b", "ab"),                                     # a barra NAO separa pastas: e apagada
    ("..\\..\\x", "x"),
    ("Ação — ñ", "Ação — ñ"),                          # unicode mantem-se
    ("CON", "CON"),                                    # nomes reservados do Windows NAO sao tratados
])
def test_nome_seguro(entrada, esperado):
    assert core.nome_seguro(entrada) == esperado


# ------------------------------------------------------------------ validar
def test_validar_aceita_pedido_normal():
    core.validar(_t(), 5)
    core.validar(_t(por_ficheiro=10), 5)


@pytest.mark.parametrize("tr, por_pagina, chave, params", [
    (_t(nome=""), 5, "err_nome", {}),
    (_t(nome="  ... "), 5, "err_nome", {}),               # um nome que fica vazio depois de limpo
    (_t(inicio=-1), 5, "err_intervalo", {}),
    (_t(inicio=5, fim=4), 5, "err_intervalo", {}),
    (_t(digitos=0), 5, "err_digitos", {"max": 12}),
    (_t(digitos=13), 5, "err_digitos", {"max": 12}),
    (_t(por_ficheiro=0), 5, "err_max", {}),
    (_t(por_ficheiro=-5), 5, "err_max", {}),
    (_t(por_ficheiro=7), 5, "err_max_multiplo", {"max": 7, "n": 5, "sug": 5}),
    (_t(por_ficheiro=1), 5, "err_max_multiplo", {"max": 1, "n": 5, "sug": 5}),   # a sugestao nunca desce abaixo de n
    (_t(por_ficheiro=12), 5, "err_max_multiplo", {"max": 12, "n": 5, "sug": 10}),  # sugere o multiplo de baixo
    (_t(por_ficheiro=3), 24, "err_max_multiplo", {"max": 3, "n": 24, "sug": 24}),
])
def test_validar_erros(tr, por_pagina, chave, params):
    assert erro_de(core.validar, tr, por_pagina) == ("ErroRifas", chave, params)


def test_validar_quirks_aceites_hoje():
    core.validar(_t(inicio=0, fim=0), 5)         # o numero 0 e permitido
    core.validar(_t(digitos=12), 5)              # o maximo de algarismos e 12 (MAX_DIGITOS)
    core.validar(_t(por_ficheiro=3), 1)          # com 1 por pagina qualquer maximo serve
    assert core.MAX_DIGITOS == 12


def test_validar_ordem_das_verificacoes():
    # o nome e verificado primeiro, depois o intervalo, os algarismos e por fim o maximo por ficheiro
    assert erro_de(core.validar, _t(nome="", inicio=9, fim=1), 5)[1] == "err_nome"
    assert erro_de(core.validar, _t(inicio=9, fim=1, digitos=0), 5)[1] == "err_intervalo"
    assert erro_de(core.validar, _t(digitos=0, por_ficheiro=0), 5)[1] == "err_digitos"


def test_erro_rifas_guarda_chave_e_traduz_na_hora():
    from core import i18n
    e = core.ErroRifas("err_digitos", max=12)
    assert (e.chave, e.params) == ("err_digitos", {"max": 12})
    pt = str(e)
    i18n.definir("en")
    assert str(e) != pt            # a traducao e feita ao converter para texto (com a lingua GLOBAL de agora)
    assert "12" in str(e) and "12" in pt


def test_cancelado_e_um_erro_rifas():
    e = core.Cancelado()
    assert isinstance(e, core.ErroRifas) and e.chave == "cancelado"


# ------------------------------------------------------------------ planear
def _planear(tr, por_pagina=5):
    return [(p.as_posix(), a, b) for p, a, b in core.planear(tr, por_pagina)]


def test_planear_varios_ficheiros_ultimo_mais_curto():
    assert _planear(_t(nome="Rifa", fim=1203, por_ficheiro=500)) == [
        ("out/Rifa - 0001 - 0500.pdf", 1, 500),
        ("out/Rifa - 0501 - 1000.pdf", 501, 1000),
        ("out/Rifa - 1001 - 1203.pdf", 1001, 1203)]


def test_planear_ficheiro_unico():
    assert _planear(_t(nome="Rifa", fim=30, digitos=2)) == [("out/Rifa - 01 - 30.pdf", 1, 30)]


def test_planear_largura_e_o_maximo_entre_digitos_e_tamanho_do_fim():
    # digitos=4 mas o fim tem 5 algarismos -> os nomes passam a ter 5 (e nao 4)
    assert _planear(_t(nome="R", fim=12000, por_ficheiro=5000)) == [
        ("out/R - 00001 - 05000.pdf", 1, 5000),
        ("out/R - 05001 - 10000.pdf", 5001, 10000),
        ("out/R - 10001 - 12000.pdf", 10001, 12000)]


def test_planear_largura_ignora_o_inicio():
    assert _planear(_t(nome="R", inicio=7, fim=12, por_ficheiro=4, digitos=3), 2) == [
        ("out/R - 007 - 010.pdf", 7, 10), ("out/R - 011 - 012.pdf", 11, 12)]


def test_planear_comeca_em_zero_e_limpa_o_nome():
    assert _planear(_t(nome="R/ifa:x", inicio=0, fim=9, digitos=1), 1) == [("out/Rifax - 0 - 9.pdf", 0, 9)]


def test_planear_valida_primeiro():
    assert erro_de(core.planear, _t(por_ficheiro=7), 5)[1] == "err_max_multiplo"
    assert erro_de(core.planear, _t(nome=""), 5)[1] == "err_nome"


def test_planear_usa_a_pasta_de_saida():
    p, _, _ = core.planear(_t(saida=Path("x") / "y"), 5)[0]
    assert p.parent == Path("x") / "y" and p.suffix == ".pdf"


# ------------------------------------------------------------------ linhas_de_numeros
def test_linhas_de_numeros():
    assert core.linhas_de_numeros(1, 7, 3, 2) == [["01", "02", "03"], ["04", "05", "06"], ["07"]]   # a ultima linha pode ser curta
    assert core.linhas_de_numeros(8, 10, 1, 1) == [["8"], ["9"], ["10"]]                            # a largura e um minimo
    assert core.linhas_de_numeros(99, 101, 2, 2) == [["99", "100"], ["101"]]
    assert core.linhas_de_numeros(5, 4, 3, 2) == []                                                   # intervalo vazio


def test_constantes_do_motor():
    assert core.DIGITOS == "0123456789"
    assert core.AVISO_POR_PAGINA == 24 and core.MARGEM_MM == 5
    assert core.PAPEIS["A4"] == pytest.approx((595.276, 841.89))
    assert sorted(core.PAPEIS) == ["A3", "A4", "A5", "Legal", "Letter"]
    assert core.MM == pytest.approx(72 / 25.4)
    assert core.PADRAO_EXEMPLO.findall("0001 001 01 00001 10001 a0002b 12345") == ["0001", "001", "00001", "0002"]    # «a0002b» tambem conta: so importam digitos nos lados
