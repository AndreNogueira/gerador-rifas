"""Fase 7 do preçário: os vales de fichas. O vale e um template de uma peça com o numero 0001 uma so vez; o motor das rifas numera-o com
series e QR de verificacao, e os textos validam-se contra a letra e contra a regra dos algarismos (o motor nao pode confundi-los com o numero)."""
import io

import pypdfium2 as pdfium
import pytest
from conftest import numeros_pdf

import core
from core import galeria, qr, vales
from core.vales import Vale

pytest.importorskip("segno")

VALE = Vale("arraial", "VALE", "Associação Imaginária", "ficha", "fichas", 2, "Válido só na festa")


def _texto(pdf: bytes) -> str:
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        tp = doc[0].get_textpage()
        t = tp.get_text_range()
        tp.close()
        return t
    finally:
        doc.close()


@pytest.fixture(scope="module")
def algarismos(tmp_path_factory):
    p = tmp_path_factory.mktemp("vales") / "algarismos.pdf"
    p.write_bytes(vales.criar_algarismos())
    return p


def _preparar(tmp_path, desenho="arraial"):
    t = tmp_path / "vale.pdf"
    t.write_bytes(vales.criar_template(Vale(desenho, "VALE", "Festa", "ficha", "fichas", 1)))
    a = tmp_path / "alg.pdf"
    a.write_bytes(vales.criar_algarismos())
    return core.preparar(t, a)


def test_o_valor_usa_o_plural_so_quando_a_quantidade_nao_e_um():
    assert Vale(moeda="ficha", moeda_plural="fichas", quantidade=1).valor_texto() == "1 ficha"
    assert Vale(moeda="ficha", moeda_plural="fichas", quantidade=5).valor_texto() == "5 fichas"
    assert Vale(moeda="ficha", quantidade=5).valor_texto() == "5 ficha"          # sem plural, o mesmo nome


def test_os_textos_escritos_aparecem_no_pdf_e_sem_nada_sai_o_exemplo():
    t = _texto(vales.criar_template(VALE))
    for esperado in ("VALE", "Associação Imaginária", "2 fichas", "Válido só na festa"):
        assert esperado in t
    ex = _texto(vales.criar_template(Vale()))
    assert "VALE" in ex and "1 ficha" in ex and "EXEMPLO" in ex.upper()


@pytest.mark.parametrize("desenho", [d.id for d in galeria.DESENHOS])
def test_cada_desenho_da_galeria_da_um_vale_que_o_motor_aceita(tmp_path, desenho):
    prep = _preparar(tmp_path, desenho)
    assert prep.info.n_campos == 1 and prep.info.n_numeros == {1: 1} and prep.info.primeiro == "0001"
    assert prep.info.fontes == ["BitstreamVeraSans-Bold"]


def test_o_motor_numera_os_vales_com_series_e_o_numero_do_vale_sai_certo(tmp_path):
    prep = _preparar(tmp_path).com_folha("A4", 8)
    assert prep.por_pagina >= 8                                              # 9 vales de 304 x 134 pt cabem numa folha A4
    r = core.gerar(core.Trabalho(tmp_path / "out", "V", 1, 20, digitos=4, prefixos=["A-", "B-"]), prep)
    assert [x.ok for x in r] == [True, True]                                  # um ficheiro por serie, cada um com os numeros 1 a 20
    assert [" A " in x.caminho.name for x in r] == [True, False] and [" B " in x.caminho.name for x in r] == [False, True]
    primeira_folha = numeros_pdf(r[0].caminho, 4)[0]
    assert primeira_folha == [f"{n:04d}" for n in range(1, prep.por_pagina + 1)]


def test_com_qr_de_verificacao_cada_vale_leva_o_seu_codigo(tmp_path):
    prep = _preparar(tmp_path).com_folha("A4", 8)
    q = qr.Qr("https://rifas.exemplo.pt", b"chave-de-teste-0123456789", "Festa", "id", 28)
    r = core.gerar(core.Trabalho(tmp_path / "out", "V", 1, 5, qr=q), prep)
    assert all(x.ok for x in r)


@pytest.mark.parametrize("quantidade", [0, -3, 100, 1000, True, 1.5, "2", None])
def test_quantidade_fora_dos_limites_e_recusada(quantidade):
    with pytest.raises(core.ErroRifas) as e:
        vales.criar_template(Vale("arraial", "VALE", "", "ficha", "fichas", quantidade))
    assert e.value.chave == "err_vale_quantidade"


@pytest.mark.parametrize("campo, valor, chave", [
    ("titulo", "VALE 0123", "err_editor_digitos"),                   # 0 seguido de 3 algarismos: o motor confundia-o com o numero
    ("organizacao", "Clube 007", "err_editor_digitos"),
    ("nota", "x" * 61, "err_galeria_texto"),
    ("moeda", "ficha de ouro de 18", "err_galeria_texto"),            # grande demais
    ("titulo", "VALE\nNOVO", "err_galeria_texto"),
    ("titulo", "वाउचर", "err_galeria_texto"),                         # sem letra para o hindi
])
def test_textos_invalidos_sao_recusados(campo, valor, chave):
    base = {"desenho": "arraial", "titulo": "VALE", "organizacao": "", "moeda": "ficha", "moeda_plural": "fichas", "quantidade": 1, "nota": ""}
    base[campo] = valor
    with pytest.raises(core.ErroRifas) as e:
        vales.criar_template(vales.de_dict(base))
    assert e.value.chave == chave


def test_desenho_desconhecido_e_recusado():
    with pytest.raises(core.ErroRifas):
        vales.criar_template(Vale("nao-existe", "VALE", "", "ficha", "fichas", 1))


def test_de_dict_so_aceita_dicionarios_com_textos():
    assert vales.de_dict({}).desenho == "arraial"
    for mau in ([], "x", None, {"titulo": 5}, {"moeda": ["a"]}):
        with pytest.raises(core.ErroRifas):
            vales.de_dict(mau)


def test_os_mesmos_textos_dao_os_mesmos_bytes():
    assert vales.criar_template(VALE) == vales.criar_template(VALE)


def test_o_quadro_negro_do_preçário_vira_um_desenho_claro_no_vale():
    assert vales.desenho_do_vale("quadro") == "arraial" and vales.desenho_do_vale("") == "arraial" and vales.desenho_do_vale("natal") == "natal"
    assert vales.de_dict({"desenho": "quadro", "moeda": "ficha"}).desenho == "arraial"
