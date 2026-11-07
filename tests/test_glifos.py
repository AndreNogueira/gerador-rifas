"""Testes unitarios dos algarismos em imagem (mascara, segmentacao, glifos) com imagens sinteticas.
Antes so se exercitavam indirectamente (preparar com PNG)."""
import pytest
from PIL import Image, ImageDraw

import core
from core import motor
from conftest import erro_de


def barras(n=10, w=20, gap=10, h=40, fundo=(255, 255, 255), tinta=(0, 0, 0), alturas=None, pad=10):
    """Imagem com `n` barras (os «algarismos») da mesma largura, alinhadas pela base."""
    W, H = pad * 2 + n * w + (n - 1) * gap, h + 2 * pad
    im = Image.new("RGB", (W, H), fundo)
    d = ImageDraw.Draw(im)
    for i in range(n):
        x = pad + i * (w + gap)
        hh = alturas[i] if alturas else h
        d.rectangle([x, pad + (h - hh), x + w - 1, pad + h - 1], fill=tinta)
    return im


def test_mascara_tinta_escura_em_fundo_claro():
    m = core.mascara_de_imagem(barras())
    assert m.mode == "L" and m.size == (310, 60)
    assert m.getextrema() == (0, 255) and m.getpixel((0, 0)) == 0 and m.getpixel((15, 25)) == 255


def test_mascara_tinta_clara_em_fundo_escuro_e_igual():
    m = core.mascara_de_imagem(barras(fundo=(0, 0, 0), tinta=(255, 255, 255)))
    assert m.getextrema() == (0, 255) and len(motor._segmentar(m)) == 10


def test_mascara_usa_a_transparencia_quando_existe():
    rgba = Image.new("RGBA", (60, 30), (0, 0, 0, 0))
    ImageDraw.Draw(rgba).rectangle([10, 5, 30, 25], fill=(255, 0, 0, 255))
    m = core.mascara_de_imagem(rgba)
    assert m.getpixel((20, 15)) == 255 and m.getpixel((0, 0)) == 0


def test_mascara_de_imagem_sem_tinta():
    assert erro_de(core.mascara_de_imagem, Image.new("RGB", (50, 20), (255, 255, 255))) == ("ErroRifas", "err_img_vazia", {})


def test_segmentar_acha_os_grupos_de_tinta():
    m = core.mascara_de_imagem(barras())
    assert motor._segmentar(m) == [(10 + 30 * i, 30 + 30 * i) for i in range(10)]
    assert motor._segmentar(Image.new("L", (30, 30), 0)) == []


def test_segmentar_ignora_pontinhos():
    m = core.mascara_de_imagem(barras(11, alturas=[40] * 10 + [3]))        # o 11.o e baixo demais (< 15% da altura maxima)
    assert len(motor._segmentar(m)) == 10


def test_extrair_glifos_dez_e_mesma_faixa_vertical():
    g = core.extrair_glifos(core.mascara_de_imagem(barras()))
    assert len(g) == 10 and all(isinstance(x, core.Glifo) for x in g)
    assert (g[0].w, g[0].topo, g[0].base, g[0].mascara.size) == (20, 0.0, 40.0, (20, 40))
    v = core.extrair_glifos(core.mascara_de_imagem(barras(alturas=[40, 20] * 5)))
    assert v[0].mascara.height == v[1].mascara.height == 40                    # a linha de base preserva-se
    assert [(x.topo, x.base) for x in v[:2]] == [(0.0, 40.0), (20.0, 40.0)]


@pytest.mark.parametrize("n", [9, 11])
def test_extrair_glifos_exige_exatamente_dez(n):
    assert erro_de(core.extrair_glifos, core.mascara_de_imagem(barras(n))) == ("ErroRifas", "err_img_simbolos", {"n": n})


def test_extrair_glifos_reduz_imagens_muito_altas():
    g = core.extrair_glifos(core.mascara_de_imagem(barras(h=600, w=60, gap=20)))
    assert core.LIMITE_ALTURA_GLIFO == 300
    assert g[0].mascara.size == (30, 300) and (g[0].topo, g[0].base) == (0.0, 300.0)


def test_glifos_de_imagem_png_e_jpeg(tmp_path):
    barras().save(tmp_path / "d.png")
    barras().convert("L").save(tmp_path / "g.jpg")
    logs = []
    gi = core.glifos_de_imagem(tmp_path / "d.png", logs.append)
    assert type(gi).__name__ == "GlifosImagem" and not gi.vetorial
    assert (gi.descricao, gi.altura_faixa, len(gi.glifos)) == ("imagem d.png", 40, 10)
    assert logs == ["Imagem dos algarismos: 10 símbolos reconhecidos (altura 40px)."]
    assert len(core.glifos_de_imagem(tmp_path / "g.jpg", lambda s: None).glifos) == 10


def test_glifos_de_imagem_erros(tmp_path):
    with pytest.raises(Exception):
        core.glifos_de_imagem(tmp_path / "nao_existe.png", lambda s: None)
    barras(9).save(tmp_path / "nove.png")
    assert erro_de(core.glifos_de_imagem, tmp_path / "nove.png", lambda s: None) == ("ErroRifas", "err_img_simbolos", {"n": 9})
