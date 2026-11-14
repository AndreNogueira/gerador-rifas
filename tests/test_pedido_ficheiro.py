"""Guardar/abrir o pedido num ficheiro (app Windows 2.6): só os campos conhecidos e válidos, nada de caminhos, e um ficheiro estragado ou alheio é recusado."""
import json

import pytest

import core
from core import pedido_ficheiro as pf

COMPLETO = {"inicio": "1", "fim": "500", "digitos": "4", "max_ficheiro": "300", "modo": "unico", "papel": "A3", "margem": "7.5", "porfolha": "12",
            "nome": "Rifa Natal", "prefixos": "A-, B-", "saltar": "13, 100-110", "cor_serie": True, "marcas": True, "cor_numeros": "#c2410c",
            "logo_pos": "ie", "logo_tam": "30"}


def test_ida_e_volta_de_todos_os_campos():
    dados = pf.para_bytes(COMPLETO)
    assert dados.startswith(b"{") and len(dados) < pf.MAX_BYTES
    assert pf.de_bytes(dados) == COMPLETO


def test_o_ficheiro_nunca_leva_caminhos_nem_o_template():
    sujo = {**COMPLETO, "template": r"C:\Users\x\rifa.pdf", "alg": r"C:\a.pdf", "saida": r"C:\saida", "logo": r"C:\logo.png"}
    texto = pf.para_bytes(sujo).decode("utf-8")
    assert "Users" not in texto and "template" not in texto and "saida" not in texto and "logo.png" not in texto
    assert set(json.loads(texto)["campos"]) == set(COMPLETO)


def test_valores_invalidos_ficam_de_fora_ao_guardar_e_ao_abrir():
    mau = {"inicio": "abc", "fim": "10", "modo": "outro", "papel": "A0", "cor_numeros": "vermelho", "logo_pos": "xx", "marcas": "sim", "nome": "x" * 500}
    assert set(json.loads(pf.para_bytes(mau))["campos"]) == {"fim"}
    ficheiro = json.dumps({"formato": pf.FORMATO, "versao": 1, "campos": {**mau, "campo_novo": 1}}).encode()
    assert pf.de_bytes(ficheiro) == {"fim": "10"}


def test_a_margem_com_virgula_normaliza_se():
    f = json.dumps({"formato": pf.FORMATO, "campos": {"margem": "7,5"}}).encode()
    assert pf.de_bytes(f) == {"margem": "7.5"}


@pytest.mark.parametrize("dados", [
    b"", b"nao e json", b"[]", b'{"formato": "outro", "campos": {"fim": "1"}}', b'{"formato": "gerador-de-rifas-pedido"}',
    b'{"formato": "gerador-de-rifas-pedido", "campos": {}}', b'{"formato": "gerador-de-rifas-pedido", "campos": {"fim": 5}}',
    b"\xff\xfe\x00", b"{" + b" " * (pf.MAX_BYTES + 5) + b"}", "texto".encode("utf-16"),
])
def test_ficheiros_alheios_ou_estragados_dao_err_pedido_ficheiro(dados):
    with pytest.raises(core.ErroRifas) as e:
        pf.de_bytes(dados)
    assert e.value.chave == "err_pedido_ficheiro"


def test_os_campos_abertos_servem_ao_pedido_do_motor():
    campos = pf.de_bytes(pf.para_bytes(COMPLETO))
    tr = core.pedido.trabalho_de_campos("", campos["nome"], campos["inicio"], campos["fim"], campos["max_ficheiro"], campos["digitos"], campos["modo"],
                                        campos["prefixos"], campos["saltar"], campos["cor_serie"], campos["cor_numeros"])
    assert tr.inicio == 1 and tr.fim == 500
