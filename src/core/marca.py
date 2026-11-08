"""M5: marca propria: o logotipo da associacao em cada rifa e a cor dos numeros.

O logotipo (PNG ou JPG, ate 2 MB) desenha-se num canto de CADA rifa quando o template e de uma so rifa (a que a folha repete): e a unica
situacao em que se sabe onde a rifa comeca e acaba. Reduz-se a 800 px (de sobra para imprimir em 15 mm a 300 dpi) e a transparencia
do PNG mantem-se. A cor dos numeros e um `#RRGGBB`; com series coloridas (M1) a cor da serie ganha.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass

from .motor import ErroRifas

MAX_MB = 2
MAX_LADO_PX = 6000               # acima disto recusa-se (uma imagem enorme comia a memoria so a abrir)
LADO_FINAL_PX = 800
POSICOES = ("se", "sd", "ie", "id")          # superior esquerdo/direito, inferior esquerdo/direito
TAMANHO_MIN, TAMANHO_MAX, TAMANHO_PADRAO = 10, 40, 25     # % da altura da rifa


@dataclass(frozen=True)
class Marca:
    """O logotipo pronto a embeber: pixeis RGB (e a transparencia, se havia) ja reduzidos, e onde e quao grande."""
    rgb: bytes
    alfa: bytes | None
    largura: int
    altura: int
    posicao: str = "sd"
    tamanho: int = TAMANHO_PADRAO


def ler_logotipo(dados: bytes, posicao: str = "sd", tamanho: int = TAMANHO_PADRAO) -> Marca:
    """Valida e prepara o logotipo. Levanta `err_logotipo` (nao e PNG/JPG, e grande demais ou esta estragado)."""
    from PIL import Image, UnidentifiedImageError
    if len(dados) > MAX_MB * 1024 * 1024 or not (dados.startswith(b"\x89PNG\r\n\x1a\n") or dados.startswith(b"\xff\xd8\xff")):
        raise ErroRifas("err_logotipo", mb=MAX_MB)
    try:
        im = Image.open(io.BytesIO(dados))
        if max(im.size) > MAX_LADO_PX or min(im.size) < 1:
            raise ErroRifas("err_logotipo", mb=MAX_MB)
        im.load()
    except ErroRifas:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ErroRifas("err_logotipo", mb=MAX_MB) from None
    if posicao not in POSICOES:
        posicao = "sd"
    tamanho = min(max(int(tamanho), TAMANHO_MIN), TAMANHO_MAX)
    im = im.convert("RGBA")
    if max(im.size) > LADO_FINAL_PX:
        im.thumbnail((LADO_FINAL_PX, LADO_FINAL_PX), Image.LANCZOS)
    alfa = im.getchannel("A")
    tem_alfa = alfa.getextrema()[0] < 255
    fundo = Image.new("RGB", im.size, (255, 255, 255))
    fundo.paste(im, mask=alfa)                                   # sem transparencia a embeber, os pixeis transparentes viram branco
    rgb = Image.merge("RGB", im.split()[:3]).tobytes() if tem_alfa else fundo.tobytes()
    return Marca(rgb, alfa.tobytes() if tem_alfa else None, im.width, im.height, posicao, tamanho)


def cor_de_hex(txt: str) -> tuple | None:
    """«#RRGGBB» -> (r, g, b) em 0..1; vazio -> None (a cor do template). Levanta `err_cor`."""
    txt = txt.strip()
    if not txt:
        return None
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", txt):
        raise ErroRifas("err_cor")
    return tuple(round(int(txt[i:i + 2], 16) / 255, 3) for i in (1, 3, 5))
