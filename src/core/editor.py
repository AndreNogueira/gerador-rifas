"""X1: o editor de templates. Em vez de um template do Canva, a pessoa desenha UMA rifa (com ou sem talão) no site: retângulos, linhas, textos e
o número 0001 (uma ou duas vezes, como o motor exige), e daqui sai o PDF do template — o mesmo que a galeria (`galeria.py`) cria, mas com
os elementos escolhidos por quem usa. A letra é a Vera (Bitstream Vera, que vem com o reportlab); os algarismos 0-9 são os de `galeria.criar_algarismos()`.

Coordenadas em pt, com a origem no canto de cima à esquerda (y para baixo), como no ecrã. Um texto (e o número) ancora-se no ponto (x, y) da
LINHA DE BASE: `alinhamento` diz se esse ponto é o início («e»), o meio («c») ou o fim («d») do texto, e `rot` (0 ou 90, anti-horário) gira-o à volta dele.
O reportlab só se importa ao desenhar.

O motor encontra o número pelos algarismos (0 seguido de, pelo menos, 2 algarismos), por isso um texto que tenha uma sequência assim («0123») seria
confundido com o número: recusa-se (`err_editor_digitos`).
"""
from __future__ import annotations

import base64
import binascii
import io
import math
import re
from dataclasses import dataclass

from . import galeria
from .motor import PADRAO_EXEMPLO, ErroRifas

LARGURA_MIN, LARGURA_MAX = 120.0, 800.0
ALTURA_MIN, ALTURA_MAX = 50.0, 500.0
MAX_ELEMENTOS = 40
MAX_TEXTO = 80
TAMANHO_MIN, TAMANHO_MAX = 4.0, 120.0
ASCENTE = 0.8                      # o que o editor do browser usa para pôr o topo de um texto: linha de base = topo + 0,8 × tamanho
TIPOS = ("retangulo", "linha", "texto", "numero", "imagem")
MAX_IMAGENS = 5
MAX_IMAGEM_BYTES = 1_000_000        # a imagem (PNG ou JPG) que o browser envia, ja reduzida
MAX_IMAGEM_LADO = 2000              # pixeis
_COR = re.compile(r"^#[0-9a-fA-F]{6}$")
_TIPO_NUMERO = "numero"
NUMERO = "0001"


@dataclass(frozen=True)
class Elemento:
    tipo: str
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0                # retângulo e linha (a linha vai de (x, y) a (x+w, y+h): w e h podem ser negativos)
    h: float = 0.0
    cor: str = ""                 # preenchimento do retângulo («» = sem) ou cor do texto/número
    contorno: str = ""            # contorno do retângulo ou cor da linha («» = sem)
    espessura: float = 1.0
    raio: float = 0.0             # cantos do retângulo
    tracejado: bool = False
    texto: str = ""
    tamanho: float = 12.0
    negrito: bool = False
    alinhamento: str = "e"        # e | c | d
    rot: int = 0                  # 0 | 90
    imagem: bytes = b""           # so a imagem: o PNG (validado e recodificado) que se desenha em (x, y, w, h)


@dataclass(frozen=True)
class Desenho:
    largura: float
    altura: float
    fundo: str
    elementos: tuple


def _num(v, nome: str, minimo: float, maximo: float) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        raise ErroRifas("err_editor_limite", campo=nome) from None
    if not math.isfinite(f) or not minimo <= f <= maximo:
        raise ErroRifas("err_editor_limite", campo=nome)
    return f


def _cor(v, nome: str, pode_vazia: bool) -> str:
    v = "" if v is None else str(v)
    if v == "" and pode_vazia:
        return ""
    if not _COR.match(v):
        raise ErroRifas("err_editor_limite", campo=nome)
    return v.lower()


def _letras(texto: str) -> None:
    """A Vera tem todas as letras do texto? (se não, `err_editor_letra`)."""
    galeria._registar()
    from reportlab.pdfbase import pdfmetrics
    face = pdfmetrics.getFont("Vera").face
    for c in texto:
        if c != " " and (not c.isprintable() or ord(c) not in face.charToGlyph):
            raise ErroRifas("err_editor_letra", car=c)


def _imagem(dados) -> bytes:
    """O PNG recodificado de uma imagem `data:image/png|jpeg;base64,…`: só PNG ou JPG a sério (o tipo real, não o que o nome diz), com tetos de tamanho;
    recodificar tira metadados (EXIF) e qualquer coisa que não seja pixeis. `err_editor_imagem` se não presta."""
    from PIL import Image, UnidentifiedImageError
    m = re.fullmatch(r"data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=\s]+)", dados) if isinstance(dados, str) else None
    if not m or len(m.group(2)) > MAX_IMAGEM_BYTES * 4 // 3 + 8:
        raise ErroRifas("err_editor_imagem")
    try:
        bruto = base64.b64decode(m.group(2), validate=False)
        if len(bruto) > MAX_IMAGEM_BYTES:
            raise ErroRifas("err_editor_imagem")
        with Image.open(io.BytesIO(bruto)) as im:
            if im.format not in ("PNG", "JPEG") or max(im.size) > MAX_IMAGEM_LADO or min(im.size) < 1:
                raise ErroRifas("err_editor_imagem")
            im.load()
            saida = io.BytesIO()
            im.convert("RGBA").save(saida, "PNG")
    except (binascii.Error, UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ErroRifas("err_editor_imagem") from None
    return saida.getvalue()


def _elemento(d: dict) -> Elemento:
    if not isinstance(d, dict):
        raise ErroRifas("err_editor_limite", campo="elemento")
    tipo = d.get("tipo")
    if tipo not in TIPOS:
        raise ErroRifas("err_editor_limite", campo="tipo")
    e = dict(
        tipo=tipo, x=_num(d.get("x", 0), "x", -200, 1200), y=_num(d.get("y", 0), "y", -200, 800),
        espessura=_num(d.get("espessura", 1), "espessura", 0, 20), tracejado=bool(d.get("tracejado", False)))
    if tipo == "imagem":
        e["w"], e["h"] = _num(d.get("w", 0), "w", 1, 1200), _num(d.get("h", 0), "h", 1, 800)
        e["imagem"] = _imagem(d.get("dados", ""))
        return Elemento(**e)
    if tipo in ("retangulo", "linha"):
        e["w"], e["h"] = _num(d.get("w", 0), "w", -1200, 1200), _num(d.get("h", 0), "h", -800, 800)
        e["contorno"] = _cor(d.get("contorno", ""), "contorno", True)
        if tipo == "retangulo":
            e["cor"] = _cor(d.get("cor", ""), "cor", True)
            e["raio"] = _num(d.get("raio", 0), "raio", 0, 100)
        elif not e["contorno"]:
            raise ErroRifas("err_editor_limite", campo="contorno")
        return Elemento(**e)
    # texto e numero
    e["cor"] = _cor(d.get("cor", "#000000"), "cor", False)
    e["tamanho"] = _num(d.get("tamanho", 12), "tamanho", TAMANHO_MIN, TAMANHO_MAX)
    e["alinhamento"] = d.get("alinhamento", "e") if d.get("alinhamento", "e") in ("e", "c", "d") else "e"
    rot = d.get("rot", 0)
    if rot not in (0, 90):
        raise ErroRifas("err_editor_limite", campo="rot")
    e["rot"] = int(rot)
    if tipo == "numero":
        e["texto"], e["negrito"] = NUMERO, True       # o número é sempre o 0001 na letra dos algarismos (Vera negrito)
        return Elemento(**e)
    texto = str(d.get("texto", ""))
    if len(texto) > MAX_TEXTO or "\n" in texto or "\r" in texto:
        raise ErroRifas("err_editor_limite", campo="texto")
    _letras(texto)
    if PADRAO_EXEMPLO.search(texto):
        raise ErroRifas("err_editor_digitos", texto=texto[:30])
    e["texto"], e["negrito"] = texto, bool(d.get("negrito", False))
    return Elemento(**e)


def de_dict(d: dict) -> Desenho:
    """Valida e converte o desenho vindo do browser (um dicionário de números, cores «#rrggbb» e textos). `ErroRifas` se algo não presta."""
    if not isinstance(d, dict):
        raise ErroRifas("err_editor_limite", campo="desenho")
    elementos = d.get("elementos", [])
    if not isinstance(elementos, (list, tuple)) or len(elementos) > MAX_ELEMENTOS:
        raise ErroRifas("err_editor_limite", campo="elementos")
    desenho = Desenho(
        largura=_num(d.get("largura", 535), "largura", LARGURA_MIN, LARGURA_MAX),
        altura=_num(d.get("altura", 152), "altura", ALTURA_MIN, ALTURA_MAX),
        fundo=_cor(d.get("fundo", "#ffffff"), "fundo", False),
        elementos=tuple(_elemento(x) for x in elementos))
    if sum(1 for x in desenho.elementos if x.tipo == "imagem") > MAX_IMAGENS:
        raise ErroRifas("err_editor_limite", campo="imagens")
    n = sum(1 for x in desenho.elementos if x.tipo == _TIPO_NUMERO)
    if n not in (1, 2):
        raise ErroRifas("err_editor_numero")
    return desenho


def _rgb(hexa: str) -> tuple:
    return tuple(int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))


def criar_template(d: Desenho) -> bytes:
    """O PDF do template: uma página do tamanho do desenho, com os elementos pela ordem dada (o último fica por cima)."""
    galeria._registar()
    from reportlab.pdfgen import canvas
    saida = io.BytesIO()
    c = canvas.Canvas(saida, pagesize=(d.largura, d.altura), pageCompression=1, invariant=1)   # invariant: os mesmos bytes para o mesmo desenho
    H = d.altura
    c.setFillColorRGB(*_rgb(d.fundo))
    c.rect(0, 0, d.largura, H, stroke=0, fill=1)
    for e in d.elementos:
        c.saveState()
        if e.tipo == "retangulo":
            if e.contorno:
                c.setStrokeColorRGB(*_rgb(e.contorno))
                c.setLineWidth(e.espessura)
            if e.tracejado:
                c.setDash(3, 3)
            x, y, w, h = min(e.x, e.x + e.w), min(e.y, e.y + e.h), abs(e.w), abs(e.h)
            if e.cor:
                c.setFillColorRGB(*_rgb(e.cor))
            stroke = 1 if e.contorno and e.espessura > 0 else 0
            if e.raio > 0:
                c.roundRect(x, H - y - h, w, h, min(e.raio, w / 2, h / 2), stroke=stroke, fill=1 if e.cor else 0)
            else:
                c.rect(x, H - y - h, w, h, stroke=stroke, fill=1 if e.cor else 0)
        elif e.tipo == "imagem":
            from reportlab.lib.utils import ImageReader
            c.drawImage(ImageReader(io.BytesIO(e.imagem)), e.x, H - e.y - e.h, e.w, e.h, mask="auto")
        elif e.tipo == "linha":
            c.setStrokeColorRGB(*_rgb(e.contorno))
            c.setLineWidth(max(e.espessura, 0.1))
            if e.tracejado:
                c.setDash(3, 3)
            c.line(e.x, H - e.y, e.x + e.w, H - (e.y + e.h))
        else:
            fonte = "VeraBd" if e.negrito else "Vera"
            c.setFillColorRGB(*_rgb(e.cor))
            c.setFont(fonte, e.tamanho)
            c.translate(e.x, H - e.y)
            if e.rot:
                c.rotate(e.rot)
            if e.alinhamento == "c":
                c.drawCentredString(0, 0, e.texto)
            elif e.alinhamento == "d":
                c.drawRightString(0, 0, e.texto)
            else:
                c.drawString(0, 0, e.texto)
        c.restoreState()
    c.save()
    return saida.getvalue()


def largura_do_texto(texto: str, negrito: bool, tamanho: float) -> float:
    """A largura (pt) que o texto ocupa na Vera (para os testes e para o browser comparar)."""
    galeria._registar()
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(texto, "VeraBd" if negrito else "Vera", tamanho)
