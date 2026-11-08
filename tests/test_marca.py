"""M5: marca propria: o logotipo em cada rifa (templates de uma rifa) e a cor dos numeros."""
import io
import re

import pytest
from PIL import Image
from pypdf import PdfReader

import core
from core import marca
from conftest import erro_de


def _png(tamanho=(400, 200), transparente=True, modo="RGBA") -> bytes:
    cor = (200, 30, 30, 0) if transparente else (200, 30, 30, 255)
    im = Image.new(modo, tamanho, cor if modo == "RGBA" else cor[:3])
    for x in range(40, 120):                                   # um retangulo opaco: o «logotipo»
        for y in range(40, 120):
            im.putpixel((x, y), (20, 80, 200, 255) if modo == "RGBA" else (20, 80, 200))
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def _jpg(tamanho=(300, 150)) -> bytes:
    b = io.BytesIO()
    Image.new("RGB", tamanho, (10, 120, 60)).save(b, "JPEG")
    return b.getvalue()


# ------------------------------------------------------------------ ler o logotipo
def test_png_com_transparencia_guarda_o_alfa_e_o_jpg_nao_tem():
    m = marca.ler_logotipo(_png())
    assert (m.largura, m.altura) == (400, 200) and m.alfa is not None and len(m.alfa) == 400 * 200 and len(m.rgb) == 400 * 200 * 3
    assert m.posicao == "sd" and m.tamanho == 25
    j = marca.ler_logotipo(_jpg(), "ie", 15)
    assert j.alfa is None and (j.posicao, j.tamanho) == ("ie", 15) and len(j.rgb) == 300 * 150 * 3
    assert marca.ler_logotipo(_png(transparente=False)).alfa is None                     # opaco: sem mascara


def test_imagens_grandes_reduzem_se_e_posicao_e_tamanho_invalidos_voltam_ao_normal():
    m = marca.ler_logotipo(_png((2400, 1200)))
    assert max(m.largura, m.altura) == 800 and m.largura / m.altura == pytest.approx(2.0, abs=0.01)
    assert marca.ler_logotipo(_png(), "xx", 99).posicao == "sd" and marca.ler_logotipo(_png(), "id", 99).tamanho == 40
    assert marca.ler_logotipo(_png(), "id", 1).tamanho == 10


@pytest.mark.parametrize("dados", [b"", b"%PDF-1.4 nao e uma imagem", b"\x89PNG\r\n\x1a\nlixo", b"\xff\xd8\xffestragado", b"GIF89a....."])
def test_o_que_nao_e_png_ou_jpg_ou_esta_estragado_e_err_logotipo(dados):
    assert erro_de(marca.ler_logotipo, dados) == ("ErroRifas", "err_logotipo", {"mb": 2})


def test_grande_demais_em_bytes_ou_em_pixeis_e_err_logotipo():
    assert erro_de(marca.ler_logotipo, b"\x89PNG\r\n\x1a\n" + b"0" * (2 * 1024 * 1024))[1] == "err_logotipo"
    b = io.BytesIO()
    Image.new("L", (marca.MAX_LADO_PX + 1, 10)).save(b, "PNG")
    assert erro_de(marca.ler_logotipo, b.getvalue())[1] == "err_logotipo"


def test_cor_de_hex():
    assert marca.cor_de_hex("#FF8000") == (1.0, 0.502, 0.0) and marca.cor_de_hex(" #0a141e ") == (0.039, 0.078, 0.118)
    assert marca.cor_de_hex("") is None and marca.cor_de_hex("   ") is None
    for mau in ("FF8000", "#FFF", "#GG0000", "#FF8000FF", "red"):
        assert erro_de(marca.cor_de_hex, mau)[1] == "err_cor"


# ------------------------------------------------------------------ gerar
@pytest.fixture(scope="module")
def prep1(fx):
    return core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf")).com_folha("A4", 5)


@pytest.fixture(scope="module")
def prep5(fx):
    return core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))


def _pagina(caminho):
    return PdfReader(str(caminho)).pages[0]


def _gerar(tmp_path, prep, **kw):
    r = core.gerar(core.Trabalho(tmp_path, "R", 1, 5, **kw), prep)
    assert r[0].ok
    return r[0].caminho


def _logos(pagina) -> list:
    conteudo = pagina.get_contents().get_data().decode("latin-1")
    return [tuple(float(v) for v in m) for m in re.findall(r"q (\S+) 0 0 (\S+) (\S+) (\S+) cm /Logo Do Q", conteudo)]


def test_o_logotipo_aparece_em_cada_rifa_da_folha_com_transparencia(tmp_path, prep1):
    pagina = _pagina(_gerar(tmp_path, prep1, marca=marca.ler_logotipo(_png(), "sd", 25)))
    logos = _logos(pagina)
    assert len(logos) == 5                                                              # uma por rifa da folha
    cel = prep1.disp.celula
    for lar, alt, x, y in logos:                                                        # em coordenadas do template (dentro da rifa)
        assert alt == pytest.approx(cel.height * 0.25, abs=0.1) and lar == pytest.approx(alt * 2, abs=0.1)
        assert x + lar <= cel.width + 4 and y + alt <= cel.height + 4 and x > cel.width / 2 and y > cel.height / 2     # canto superior direito
    img = pagina["/Resources"]["/XObject"]["/Logo"].get_object()
    assert img["/Width"] == 400 and img["/Height"] == 200 and "/SMask" in img


@pytest.mark.parametrize("posicao,esquerda,cima", [("se", True, True), ("sd", False, True), ("ie", True, False), ("id", False, False)])
def test_os_quatro_cantos(tmp_path, prep1, posicao, esquerda, cima):
    lar, alt, x, y = _logos(_pagina(_gerar(tmp_path / posicao, prep1, marca=marca.ler_logotipo(_jpg(), posicao, 20))))[0]
    cel = prep1.disp.celula
    assert (x < cel.width / 2) is esquerda and (y > cel.height / 2) is cima


def test_sem_logotipo_nada_muda_e_num_template_de_varias_rifas_o_logotipo_e_ignorado(tmp_path, prep1, prep5):
    a, b = _gerar(tmp_path / "a", prep1), _gerar(tmp_path / "b", prep1, marca=None)
    assert "/Logo" not in _pagina(a)["/Resources"]["/XObject"] and _pagina(a).get_contents().get_data() == _pagina(b).get_contents().get_data()
    c = _gerar(tmp_path / "c", prep5, marca=marca.ler_logotipo(_png()))
    assert _logos(_pagina(c)) == [] and "/Logo" not in _pagina(c)["/Resources"]["/XObject"]


def test_cor_dos_numeros_e_a_da_serie_ganha(tmp_path, prep1):
    azul = marca.cor_de_hex("#0000FF")
    pdf = _gerar(tmp_path / "azul", prep1, cor_numeros=azul)
    assert "0 0 1 rg" in _pagina(pdf).get_contents().get_data().decode("latin-1")
    series = core.gerar(core.Trabalho(tmp_path / "s", "R", 1, 5, prefixos=("A-", "B-"), cor_por_serie=True, cor_numeros=azul), prep1)
    conteudo = [_pagina(r.caminho).get_contents().get_data().decode("latin-1") for r in series]
    assert "0.78 0.16 0.16 rg" in conteudo[0] and "0 0 1 rg" not in conteudo[0]          # a cor da serie ganha
    sem_cor_serie = core.gerar(core.Trabalho(tmp_path / "t", "R", 1, 5, prefixos=("A-", "B-"), cor_numeros=azul), prep1)
    assert all("0 0 1 rg" in _pagina(r.caminho).get_contents().get_data().decode("latin-1") for r in sem_cor_serie)


def test_previa_com_logotipo_e_cor(prep1):
    pdf = core.pdf_da_previa(prep1, 1, 4, marca=marca.ler_logotipo(_png(), "id", 30), cor=marca.cor_de_hex("#FF0000"))
    pagina = PdfReader(io.BytesIO(pdf)).pages[0]
    assert len(_logos(pagina)) == 5 and "1 0 0 rg" in pagina.get_contents().get_data().decode("latin-1")
