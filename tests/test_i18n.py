"""Caracterizacao: textos das 18 linguas (idiomas/) e i18n.t / i18n.definir.

Nota: o teste de paridade abaixo verifica os DADOS (i18n.TEXTOS). A mesma verificacao existe em app.verificar_traducoes(),
mas essa vive em app.py (Tkinter) e por isso nao se importa aqui - ver «Não testável ainda» no docs/MIGRATION_PLAN.md.
"""
import re

import pytest

import core
import i18n
from idiomas import NOMES, ORDEM, TEXTOS

PARAMS = re.compile(r"\{(\w+)\}")


def test_linguas_e_ordem():
    assert ORDEM == ["pt", "en", "es", "fr", "de", "it", "nl", "pl", "sv", "cs", "ro", "el", "ru", "tr", "zh", "ja", "ko", "hi"]
    assert list(NOMES) == ORDEM and list(TEXTOS) == ORDEM
    assert list(i18n.LINGUAS.items())[:3] == [("pt", "Português"), ("en", "English"), ("es", "Español")]
    assert NOMES["zh"] == "简体中文" and NOMES["hi"] == "हिन्दी"


def test_todas_as_linguas_tem_150_chaves_iguais_ao_portugues():
    ref = TEXTOS["pt"]
    assert len(ref) == 150
    for lg, textos in TEXTOS.items():
        assert textos.keys() == ref.keys(), lg


def test_todas_as_linguas_tem_os_mesmos_parametros_que_o_portugues():
    ref = TEXTOS["pt"]
    for lg, textos in TEXTOS.items():
        for k, v in textos.items():
            assert set(PARAMS.findall(v)) == set(PARAMS.findall(ref[k])), f"{lg}: {k}"


def test_nenhum_texto_vazio():
    for lg, textos in TEXTOS.items():
        assert all(isinstance(v, str) and v.strip() for v in textos.values()), lg


def test_t_na_lingua_atual_e_com_parametros():
    assert i18n.atual() == "pt"
    assert i18n.t("nenhum") == "nenhum"
    assert i18n.t("err_digitos", max=12) == "O número de algarismos tem de estar entre 1 e 12."
    i18n.definir("en")
    assert i18n.atual() == "en"
    assert i18n.t("err_digitos", max=12) == TEXTOS["en"]["err_digitos"].format(max=12)
    assert i18n.t("err_digitos", max=12) != TEXTOS["pt"]["err_digitos"].format(max=12)


def test_definir_lingua_desconhecida_volta_ao_portugues():
    i18n.definir("en")
    i18n.definir("xx")
    assert i18n.atual() == "pt"


def test_chave_inexistente_levanta_keyerror():
    with pytest.raises(KeyError):
        i18n.t("chave_que_nao_existe")


def test_falta_numa_lingua_usa_o_portugues(monkeypatch):
    monkeypatch.delitem(TEXTOS["en"], "nenhum")
    i18n.definir("en")
    assert i18n.t("nenhum") == "nenhum"        # cai no texto em portugues


def test_t_sem_parametros_nao_aplica_format():
    # sem kwargs devolve o texto tal e qual, mesmo com {chaves}
    assert "{max}" in i18n.t("err_digitos")


def test_t_com_parametro_em_falta_levanta_keyerror():
    with pytest.raises(KeyError):
        i18n.t("err_digitos", outro=1)


def test_cada_erro_do_motor_tem_texto_em_todas_as_linguas():
    chaves = ["err_nome", "err_intervalo", "err_digitos", "err_max", "err_max_multiplo", "err_abrir_template",
              "err_sem_paginas", "err_sem_exemplos", "err_sequencia", "err_apagar", "err_folha_varias",
              "err_rifa_grande", "err_sem_ficheiro_algarismos", "err_ficheiro_inexistente", "err_formato",
              "err_usar_ficheiro", "err_img_simbolos", "err_pasta", "err_gravar", "cancelado"]
    for lg in TEXTOS:
        for k in chaves:
            assert k in TEXTOS[lg], (lg, k)


def test_detetar_devolve_uma_lingua_suportada():
    # a parte do Windows (kernel32) nao se testa; so se garante que o resultado e sempre uma lingua valida
    assert i18n.detetar() in i18n.LINGUAS


def test_erro_rifas_traduz_com_a_lingua_global():
    e = core.ErroRifas("err_nome")
    pt = str(e)
    i18n.definir("de")
    assert str(e) != pt
