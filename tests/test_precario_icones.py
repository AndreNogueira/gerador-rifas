"""As imagens dos artigos do preçário (`core/icones_precario/`, `public/precario/`): existem para todos os emojis do catálogo, com o tamanho certo, e a licença vai ao lado."""
from pathlib import Path

from core import precario_catalogo as cat
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "src" / "core" / "icones_precario"
WEB = RAIZ / "src" / "web" / "frontend" / "public" / "precario"
CODIGOS = sorted({e for a in cat.ARTIGOS.values() for e in a.icones})            # a de omissão e as alternativas de cada artigo


def test_cada_emoji_do_catalogo_tem_a_imagem_do_pdf_e_a_miniatura_da_pagina():
    assert not [c for c in CODIGOS if not (PDF / f"{c}.png").is_file()], "corre scripts/gerar_icones_precario.py"
    assert not [c for c in CODIGOS if not (WEB / f"{c}.webp").is_file()]
    assert not [f.name for f in PDF.glob("*.png") if f.stem not in CODIGOS], "imagem a mais (artigo apagado?)"


def test_tamanho_e_peso_das_imagens():
    for c in CODIGOS:
        with Image.open(PDF / f"{c}.png") as im:
            assert im.size == (256, 256) and "A" in im.convert("RGBA").getbands(), c          # 256 px: 25 mm a 260 dpi
        assert 1_500 < (PDF / f"{c}.png").stat().st_size < 30_000, c
        with Image.open(WEB / f"{c}.webp") as im:
            assert im.size == (96, 96), c
    assert sum(f.stat().st_size for f in PDF.glob("*.png")) < 2_500_000                         # a imagem Docker e o .exe não engordam


def test_a_licenca_das_imagens_vai_com_elas():
    texto = (PDF / "LICENSE.txt").read_text(encoding="utf-8")
    assert "Noto Emoji" in texto and "Google" in texto and "Open Font License" in texto
