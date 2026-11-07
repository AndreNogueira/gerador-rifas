"""Lingua por pedido (contextvars) e mensagens estruturadas (Mensagem): o que a webapp precisa e a app Windows nao usa.
O comportamento global (i18n.definir / i18n.t) nao mudou: ver tests/test_i18n.py."""
import copy
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import core
from core import i18n
from core.i18n import Mensagem, msg, traduzir


def test_traduzir_e_pura():
    assert traduzir("err_digitos", "en", max=12) == i18n.TEXTOS["en"]["err_digitos"].format(max=12)
    assert traduzir("err_digitos", "xx", max=12) == traduzir("err_digitos", "pt", max=12)      # lingua desconhecida: portugues
    i18n.definir("de")
    assert traduzir("nenhum", "pt") == "nenhum"                                               # nao depende da lingua global


def test_com_lingua_so_vale_dentro_do_with():
    assert i18n.atual() == "pt"
    with i18n.com_lingua("en"):
        assert i18n.atual() == "en"
        assert i18n.t("nenhum") != "nenhum"
        with i18n.com_lingua("de"):
            assert i18n.atual() == "de"
        assert i18n.atual() == "en"
    assert i18n.atual() == "pt" and i18n.t("nenhum") == "nenhum"


def test_com_lingua_nao_mexe_na_lingua_global():
    i18n.definir("fr")
    with i18n.com_lingua("ja"):
        assert i18n.atual() == "ja"
    assert i18n.atual() == "fr"
    with i18n.com_lingua("klingon"):
        assert i18n.atual() == "pt"                           # desconhecida = portugues, como em definir()


def test_com_lingua_repoe_mesmo_com_excecao():
    with pytest.raises(RuntimeError):
        with i18n.com_lingua("en"):
            raise RuntimeError
    assert i18n.atual() == "pt"


def test_pedidos_concorrentes_nao_se_atropelam():
    """Cada thread tem a sua lingua; todas veem a que definiram, mesmo a correr ao mesmo tempo."""
    linguas = ["pt", "en", "es", "fr", "de", "it", "nl", "pl"] * 5
    barreira = threading.Barrier(8)

    def pedido(lg):
        with i18n.com_lingua(lg):
            try:
                barreira.wait(timeout=5)
            except threading.BrokenBarrierError:
                pass
            return [str(core.ErroRifas("err_nome")) for _ in range(50)], lg
    with ThreadPoolExecutor(max_workers=8) as pool:
        resultados = list(pool.map(pedido, linguas))
    for textos, lg in resultados:
        assert set(textos) == {traduzir("err_nome", lg)}


def test_a_lingua_do_pedido_nao_passa_para_outra_thread():
    visto = []
    with i18n.com_lingua("en"):
        th = threading.Thread(target=lambda: visto.append(i18n.atual()))
        th.start()
        th.join()
    assert visto == ["pt"]               # quem cria uma thread/processo tem de usar com_lingua la dentro


def test_erro_rifas_traduz_na_lingua_do_pedido_e_em():
    e = core.ErroRifas("err_digitos", max=12)
    with i18n.com_lingua("en"):
        assert str(e) == traduzir("err_digitos", "en", max=12)
    assert str(e) == traduzir("err_digitos", "pt", max=12)
    assert e.em("de") == traduzir("err_digitos", "de", max=12)
    assert core.Cancelado().em("en") == traduzir("cancelado", "en")


# ------------------------------------------------------------------ Mensagem
def test_mensagem_e_um_str_com_chave_e_parametros():
    m = msg("aviso_multiplo", qtd=12, n=5)
    assert isinstance(m, str) and isinstance(m, Mensagem)
    assert m == "⚠ 12 números não é múltiplo de 5; na última página alguns bilhetes ficam sem número."
    assert (m.chave, m.params) == ("aviso_multiplo", {"qtd": 12, "n": 5})
    assert m.em("en") == traduzir("aviso_multiplo", "en", qtd=12, n=5) and m.em("en") != m


def test_mensagem_usa_a_lingua_do_pedido_ao_ser_criada():
    with i18n.com_lingua("en"):
        m = msg("nenhum")
    assert m == traduzir("nenhum", "en") and m.em("pt") == "nenhum"


@pytest.mark.parametrize("copiar", [copy.copy, copy.deepcopy, lambda m: pickle.loads(pickle.dumps(m))])
def test_mensagem_sobrevive_a_copy_e_pickle(copiar):
    m = msg("log_a_gerar", nome="X.pdf", paginas=3)
    c = copiar(m)
    assert c == m and isinstance(c, Mensagem) and (c.chave, c.params) == (m.chave, m.params)
    assert c.em("en") == m.em("en")


def test_o_motor_emite_mensagens_estruturadas(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    logs = []
    r = core.gerar(core.Trabalho(tmp_path, "T", 1, 12, digitos=6), prep, log=logs.append)
    assert logs and all(isinstance(m, Mensagem) for m in logs)
    assert [m.chave for m in logs] == ["aviso_algarismos", "aviso_multiplo", "log_a_gerar", "log_pronto_ok"]
    assert logs[0].params == {"exemplo": 4, "largura": 6, "pct": 67}
    assert logs[2].em("en") == traduzir("log_a_gerar", "en", nome="T - 000001 - 000012.pdf", paginas=3)
    assert r[0].ok


def test_o_log_do_preparar_tambem_e_estruturado(fx):
    logs = []
    core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.png"), log=logs.append)
    assert [m.chave for m in logs] == ["log_template", "log_imagem_ok", "info_dpi"] and all(isinstance(m, Mensagem) for m in logs)


def test_erros_de_verificacao_sao_mensagens(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    r = core.gerar(core.Trabalho(tmp_path, "T", 1, 5, digitos=6), prep)
    erros = core.verificar(r[0].caminho, core.linhas_de_numeros(1, 10, 5, 6), prep, 6)
    assert len(erros) == 1 and isinstance(erros[0], Mensagem) and erros[0].chave == "ver_paginas"
    assert erros[0].params == {"tem": 1, "esperado": 2} and erros[0].em("en") != erros[0]


def test_geracao_inteira_na_lingua_do_pedido(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    logs = []
    with i18n.com_lingua("en"):
        core.gerar(core.Trabalho(tmp_path, "T", 1, 12), prep, log=logs.append)
    assert logs[0] == traduzir("aviso_multiplo", "en", qtd=12, n=5) and logs[0] != traduzir("aviso_multiplo", "pt", qtd=12, n=5)
    assert i18n.atual() == "pt"
