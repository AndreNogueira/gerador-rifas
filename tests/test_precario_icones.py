"""As imagens dos artigos do preçário (`core/icones_precario/`, `public/precario/`): existem para todos os emojis do catálogo, com o tamanho certo, e a licença vai ao lado.

Dois conjuntos: o Noto Emoji curado (`core/icones_precario/<código>.png`, sempre presente) e, para quem tiver, o Fluent Emoji 3D (`core/icones_precario/fluent/<código>.png`,
acrescentado sozinho pelo catálogo como alternativa extra — `core.precario_catalogo._alternativas_extra`). Nenhum dos dois troca o outro.
"""
from pathlib import Path

from core import precario_catalogo as cat
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "src" / "core" / "icones_precario"
WEB = RAIZ / "src" / "web" / "frontend" / "public" / "precario"
NOTO = sorted({e for a in cat.ARTIGOS.values() for e in a.icones if ":" not in e})            # a de omissão e as alternativas de cada artigo
FLUENT = sorted({e.split(":", 1)[1] for a in cat.ARTIGOS.values() for e in a.icones if e.startswith("fluent:")})


def test_cada_emoji_do_catalogo_tem_a_imagem_do_pdf_e_a_miniatura_da_pagina():
    assert not [c for c in NOTO if not (PDF / f"{c}.png").is_file()], "corre scripts/gerar_icones_precario.py"
    assert not [c for c in NOTO if not (WEB / f"{c}.webp").is_file()]
    assert not [f.name for f in PDF.glob("*.png") if f.stem not in NOTO], "imagem a mais (artigo apagado?)"


def test_tamanho_e_peso_das_imagens():
    for c in NOTO:
        with Image.open(PDF / f"{c}.png") as im:
            assert im.size == (256, 256) and "A" in im.convert("RGBA").getbands(), c          # 256 px: 25 mm a 260 dpi
        assert 1_500 < (PDF / f"{c}.png").stat().st_size < 30_000, c
        with Image.open(WEB / f"{c}.webp") as im:
            assert im.size == (96, 96), c
    assert sum(f.stat().st_size for f in PDF.glob("*.png")) < 2_500_000                         # a imagem Docker e o .exe não engordam


def test_a_licenca_das_imagens_vai_com_elas():
    texto = (PDF / "LICENSE.txt").read_text(encoding="utf-8")
    assert "Noto Emoji" in texto and "Google" in texto and "Open Font License" in texto


# ------------------------------------------------------------------ Fluent Emoji 3D (alternativas extra, automáticas)
def test_cada_codigo_fluent_do_catalogo_tem_imagem_e_nenhuma_a_mais():
    assert FLUENT, "nenhum artigo ganhou uma alternativa Fluent: corre scripts/gerar_icones_precario.py"
    assert not [c for c in FLUENT if not (PDF / "fluent" / f"{c}.png").is_file()]
    assert not [c for c in FLUENT if not (WEB / "fluent" / f"{c}.webp").is_file()]
    assert not [f.name for f in (PDF / "fluent").glob("*.png") if f.stem not in FLUENT]


def test_tamanho_e_peso_das_imagens_fluent():
    for c in FLUENT:
        with Image.open(PDF / "fluent" / f"{c}.png") as im:
            assert im.size == (256, 256) and "A" in im.convert("RGBA").getbands(), c
        with Image.open(WEB / "fluent" / f"{c}.webp") as im:
            assert im.size == (96, 96), c
    assert sum(f.stat().st_size for f in (PDF / "fluent").glob("*.png")) < 2_500_000


def test_a_licenca_do_fluent_vai_com_ele():
    texto = (PDF / "fluent" / "LICENSE.txt").read_text(encoding="utf-8")
    assert "Fluent Emoji" in texto and "Microsoft" in texto and "MIT License" in texto


def test_nenhum_codigo_fluent_troca_o_noto_do_mesmo_artigo():
    """As alternativas extra juntam-se às do Noto, nunca as tiram: o primeiro ícone (a de omissão) continua sempre Noto."""
    for a in cat.ARTIGOS.values():
        assert ":" not in a.icones[0]
        assert a.emoji == a.icones[0]
