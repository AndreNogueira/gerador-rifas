"""Icones desenhados com Pillow em grelha 24x24 e sobre-amostragem de 8x (bordos suaves, sem pixeis).

`icone("mais", 16)` devolve uma CTkImage que muda sozinha entre o tema claro e o escuro.
"""
from __future__ import annotations

import functools

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

import tema

SUPER = 8          # sobre-amostragem
RESOLUCAO = 4      # a imagem guardada tem 4x o tamanho logico (o CTk reduz para o ecra, mesmo com escala de 150%)


class _G:
    """Pincel: coordenadas na grelha 24x24, desenha numa imagem RGBA."""

    def __init__(self, px: int, cor: tuple, espessura: float = 1.9):
        self.n = px * SUPER
        self.k = self.n / 24
        self.im = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.cor = cor + (255,)
        self.w = espessura * self.k

    def _p(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def ponto(self, x, y, r):
        k = self.k
        self.d.ellipse((x * k - r, y * k - r, x * k + r, y * k + r), fill=self.cor)

    def linha(self, pts, w=None):
        w = w or self.w
        p = self._p(pts)
        self.d.line(p, fill=self.cor, width=int(round(w)), joint="curve")
        for x, y in p:                                # extremos e juntas redondos
            self.d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=self.cor)

    def circulo(self, cx, cy, r, cheio=False, cor=None):
        k = self.k
        box = (cx * k - r * k, cy * k - r * k, cx * k + r * k, cy * k + r * k)
        if cheio:
            self.d.ellipse(box, fill=cor or self.cor)
        else:
            self.d.ellipse(box, outline=cor or self.cor, width=int(round(self.w)))

    def elipse(self, x0, y0, x1, y1):
        k = self.k
        self.d.ellipse((x0 * k, y0 * k, x1 * k, y1 * k), outline=self.cor, width=int(round(self.w)))

    def ret(self, x0, y0, x1, y1, r=2.0, cheio=False, cor=None):
        k = self.k
        if cheio:
            self.d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), radius=r * k, fill=cor or self.cor)
        else:
            self.d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), radius=r * k, outline=cor or self.cor,
                                     width=int(round(self.w)))

    def poligono(self, pts, cor=None):
        self.d.polygon(self._p(pts), fill=cor or self.cor)

    def apagar_circulo(self, cx, cy, r):
        k = self.k
        self.d.ellipse((cx * k - r * k, cy * k - r * k, cx * k + r * k, cy * k + r * k), fill=(0, 0, 0, 0))

    def texto(self, s, cx, cy, tam):
        try:
            f = ImageFont.truetype("segoeuib.ttf", int(tam * self.k))
        except OSError:
            f = ImageFont.load_default()
        self.d.text((cx * self.k, cy * self.k), s, font=f, fill=self.cor, anchor="mm")

    def pronto(self, px: int) -> Image.Image:
        return self.im.resize((px, px), Image.LANCZOS)


# ------------------------------------------------------------------ desenhos
def _mais(g):
    g.linha([(12, 5), (12, 19)]); g.linha([(5, 12), (19, 12)])


def _menos(g):
    g.linha([(5, 12), (19, 12)])


def _fechar(g):
    g.linha([(6, 6), (18, 18)]); g.linha([(18, 6), (6, 18)])


def _ajustar(g):
    for pts in (((4, 9), (4, 4), (9, 4)), ((15, 4), (20, 4), (20, 9)),
                ((20, 15), (20, 20), (15, 20)), ((9, 20), (4, 20), (4, 15))):
        g.linha(list(pts))


def _expandir(g):
    g.linha([(14, 10), (20, 4)]); g.linha([(15, 4), (20, 4), (20, 9)])
    g.linha([(10, 14), (4, 20)]); g.linha([(4, 15), (4, 20), (9, 20)])


def _reduzir(g):
    g.linha([(20, 4), (14, 10)]); g.linha([(14, 5), (14, 10), (19, 10)])
    g.linha([(4, 20), (10, 14)]); g.linha([(10, 19), (10, 14), (5, 14)])


def _globo(g):
    g.circulo(12, 12, 9)
    g.elipse(7.6, 3, 16.4, 21)
    g.linha([(3, 12), (21, 12)])
    g.linha([(5.2, 7.5), (18.8, 7.5)]); g.linha([(5.2, 16.5), (18.8, 16.5)])


def _sol(g):
    import math
    g.circulo(12, 12, 4.2)
    for i in range(8):
        a = math.radians(i * 45)
        g.linha([(12 + 7 * math.cos(a), 12 + 7 * math.sin(a)), (12 + 9.4 * math.cos(a), 12 + 9.4 * math.sin(a))])


def _lua(g):
    g.circulo(12, 12, 8.5, cheio=True)
    g.apagar_circulo(16.4, 8.6, 7.4)


def _pasta(g):
    g.linha([(3, 7), (3, 18), (21, 18), (21, 9), (11, 9), (9, 6), (3, 6), (3, 7)])


def _olho(g):
    g.elipse(2.5, 6.5, 21.5, 17.5)
    g.circulo(12, 12, 3.3, cheio=True)


def _ajuda(g):
    g.circulo(12, 12, 9.2)
    g.texto("?", 12, 12.6, 14)


def _info(g):
    g.circulo(12, 12, 9.2)
    g.linha([(12, 11), (12, 16.5)]); g.ponto(12, 7.8, 1.25 * g.k)


def _ok(g):
    g.linha([(5, 12.5), (10, 17.5), (19, 7)], w=2.3 * g.k)


def _doc(g):
    g.linha([(6, 3), (6, 21), (18, 21), (18, 8), (13, 3), (6, 3)])
    g.linha([(13, 3), (13, 8), (18, 8)])
    g.linha([(9, 13), (15, 13)]); g.linha([(9, 17), (15, 17)])


def _gerar(g):
    g.poligono([(7, 4.5), (19.5, 12), (7, 19.5)])


def _setas(g):
    g.linha([(5, 12), (19, 12)]); g.linha([(13, 6), (19, 12), (13, 18)])


def _teclado(g):
    g.ret(2.5, 6, 21.5, 18, r=2.2)
    for x in (6.5, 10, 13.5, 17): g.ponto(x, 10, 0.9 * g.k)
    g.linha([(7, 14.2), (17, 14.2)])


_DESENHOS = {"mais": _mais, "menos": _menos, "fechar": _fechar, "ajustar": _ajustar, "expandir": _expandir,
             "reduzir": _reduzir, "globo": _globo, "sol": _sol, "lua": _lua, "pasta": _pasta, "olho": _olho,
             "ajuda": _ajuda, "info": _info, "ok": _ok, "doc": _doc, "gerar": _gerar, "seta": _setas,
             "teclado": _teclado}


def desenhar(nome: str, cor_rgb: tuple, px: int) -> Image.Image:
    g = _G(px, cor_rgb)
    _DESENHOS[nome](g)
    return g.pronto(px)


def bilhete(px: int, cor_corpo: tuple, cor_detalhe: tuple = (255, 255, 255)) -> Image.Image:
    """Logotipo: bilhete de rifa com picotado e dois 'numeros'."""
    g = _G(px, cor_corpo)
    g.ret(1.5, 5.5, 22.5, 18.5, r=2.8, cheio=True)
    g.apagar_circulo(1.5, 12, 2.1)
    g.apagar_circulo(22.5, 12, 2.1)
    det = cor_detalhe + (255,)
    for y in (8.2, 10.6, 13.0, 15.4):
        g.circulo(7.6, y, 0.55, cheio=True, cor=det)
    g.ret(11, 8.8, 19.2, 10.6, r=0.9, cheio=True, cor=det)
    g.ret(11, 12.6, 16.2, 14.4, r=0.9, cheio=True, cor=det)
    return g.pronto(px)


# ------------------------------------------------------------------ CTkImage
@functools.lru_cache(maxsize=256)
def _cached(nome: str, claro: str, escuro: str, tam: int) -> ctk.CTkImage:
    px = tam * RESOLUCAO
    if nome == "bilhete":
        a = bilhete(px, tema._rgb(claro), tema._rgb(tema.texto_sobre(tema._rgb(claro))))
        b = bilhete(px, tema._rgb(escuro), tema._rgb(tema.texto_sobre(tema._rgb(escuro))))
    else:
        a, b = desenhar(nome, tema._rgb(claro), px), desenhar(nome, tema._rgb(escuro), px)
    return ctk.CTkImage(light_image=a, dark_image=b, size=(tam, tam))


def icone(nome: str, tam: int = 18, cor: tuple | None = None) -> ctk.CTkImage:
    """cor = (hex claro, hex escuro); por defeito a cor do texto."""
    cor = cor or tema.C["texto"]
    return _cached(nome, cor[0], cor[1], tam)


def pil(nome: str, tam: int, hexcor: str) -> Image.Image:
    return desenhar(nome, tema._rgb(hexcor), tam)
