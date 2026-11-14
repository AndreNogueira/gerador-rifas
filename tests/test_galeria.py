"""M4: a galeria de templates: cada desenho e uma rifa com talao que o motor aceita, e os textos sao validados contra a letra."""
import io
from pathlib import Path

import pypdfium2 as pdfium
import pytest

import core
from core import galeria
from conftest import erro_de, numeros_pdf

TEXTOS = galeria.Textos("Rifa de Natal", "Associação Cultural de Exemplo", ("1.º Prémio: Um cabaz", "2.º Prémio: Um vale"), "Sorteio: 24/12/26")


@pytest.fixture(scope="module")
def algarismos(tmp_path_factory):
    p = tmp_path_factory.mktemp("galeria") / "algarismos.pdf"
    p.write_bytes(galeria.criar_algarismos())
    return p


def _template(tmp_path, desenho, textos=TEXTOS) -> Path:
    p = tmp_path / f"{desenho}.pdf"
    p.write_bytes(galeria.criar_template(desenho, textos))
    return p


def _texto(pdf: bytes) -> str:
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        tp = doc[0].get_textpage()
        t = tp.get_text_range()
        tp.close()
        return t
    finally:
        doc.close()


@pytest.mark.parametrize("desenho", [d.id for d in galeria.DESENHOS])
def test_cada_desenho_e_uma_rifa_com_talao_que_o_motor_aceita_e_enche_a_folha(tmp_path, algarismos, desenho):
    logs = []
    prep = core.preparar(_template(tmp_path, desenho), algarismos, logs.append)
    assert prep.info.n_campos == 1 and prep.info.n_numeros == {1: 2} and prep.info.primeiro == "0001"
    assert not any("diferente" in str(m) for m in logs)                                     # os algarismos estao na mesma letra do numero
    folha = prep.com_folha("A4", 5)
    assert folha.por_pagina == 5
    r = core.gerar(core.Trabalho(tmp_path / "out", "R", 1, 10, digitos=4), folha)
    assert [x.ok for x in r] == [True]
    assert numeros_pdf(r[0].caminho, 4)[0] == sorted(f"{n:04d}" for n in range(1, 6) for _ in range(2))      # talao e parte principal


def test_os_textos_escritos_aparecem_no_pdf():
    t = _texto(galeria.criar_template("natal", TEXTOS))
    for esperado in ("Rifa de Natal", "Associação Cultural de Exemplo", "1.º Prémio: Um cabaz", "2.º Prémio: Um vale", "Sorteio: 24/12/26"):
        assert esperado in t
    assert "3.º" not in t and "EXEMPLO" not in t


def test_sem_nada_escrito_sai_o_texto_de_exemplo_e_so_o_que_se_escreve_aparece():
    assert "RIFA DE EXEMPLO" in _texto(galeria.criar_template("gala", galeria.Textos()))
    so_titulo = _texto(galeria.criar_template("gala", galeria.Textos(titulo="Só o título")))
    assert "Só o título" in so_titulo and "Sorteio" not in so_titulo and "Prémio" not in so_titulo


def test_um_titulo_muito_longo_encolhe_ate_caber():
    longo = "W" * galeria.MAX_TITULO
    assert longo in _texto(galeria.criar_template("bosque", galeria.Textos(titulo=longo))).replace("\n", "").replace("\r", "")


def test_os_mesmos_textos_dao_os_mesmos_bytes():
    assert galeria.criar_template("quermesse", TEXTOS) == galeria.criar_template("quermesse", TEXTOS)
    assert galeria.criar_template("quermesse", TEXTOS) != galeria.criar_template("natal", TEXTOS)


@pytest.mark.parametrize("textos,car", [
    (galeria.Textos(titulo="हिन्दी"), "ह"),                                                       # nenhuma letra tem devanagari (precisa de «shaping»)
    (galeria.Textos(organizacao="العربية"), "ا"),
    (galeria.Textos(titulo="日本語 हि"), "ह"),                                                       # tudo no mesmo texto tem de existir numa so familia
    (galeria.Textos(premios=("ok", "x\x00y")), "\x00"),
    (galeria.Textos(titulo="A" * (galeria.MAX_TITULO + 1)), "A" * 14 + "…"),                  # demasiado comprido
    (galeria.Textos(premios=tuple(str(i) for i in range(galeria.MAX_PREMIOS + 1))), "…"),                  # 11 premios: mais do que o maximo
])
def test_textos_que_a_letra_nao_tem_ou_que_nao_cabem_sao_um_erro(textos, car):
    e = erro_de(galeria.criar_template, "bosque", textos)
    assert e[:2] == ("ErroRifas", "err_galeria_texto") and e[2]["car"] == car


def test_desenho_desconhecido_e_acentos_e_simbolos_latinos():
    assert erro_de(galeria.criar_template, "nao-existe", TEXTOS)[1] == "err_galeria_texto"
    assert galeria.criar_template("bosque", galeria.Textos(titulo="Ação Ñandú Çéíóú Ø € ½ & % # (1)")).startswith(b"%PDF")


PREMIOS_10 = tuple(f"{i}.º Prémio: " + "Cabaz de mantimentos e vinhos"[: galeria.MAX_PREMIO - 14] for i in range(1, 11))     # o 10.º tem algarismos: o motor nao pode confundi-lo com o numero


@pytest.mark.parametrize("n", [3, 5, 6, 10])
@pytest.mark.parametrize("desenho", [d.id for d in galeria.DESENHOS])
def test_de_3_a_10_premios_em_todos_os_desenhos_o_motor_continua_a_ver_so_o_numero(tmp_path, algarismos, desenho, n):
    textos = galeria.Textos("RIFA GRANDE", "Associação de Exemplo · Festa Grande", PREMIOS_10[:n], "Sorteio: 31/12/2099")
    prep = core.preparar(_template(tmp_path, desenho, textos), algarismos)
    assert prep.info.n_campos == 1 and prep.info.n_numeros == {1: 2} and prep.info.primeiro == "0001"
    texto = _texto(galeria.criar_template(desenho, textos))
    assert all(f"{i}.º Prémio" in texto for i in range(1, n + 1))                           # todos os premios estao desenhados


def test_o_maximo_de_premios_e_10_e_o_minimo_pedido_3():
    assert (galeria.MIN_PREMIOS, galeria.MAX_PREMIOS) == (3, 10)
    assert galeria.criar_template("bosque", galeria.Textos(premios=PREMIOS_10)).startswith(b"%PDF")
