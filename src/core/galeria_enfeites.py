"""Os enfeites dos 20 desenhos novos da galeria (`galeria.py`): cada um é um ícone junto ao título e uma faixa decorativa no topo e/ou em baixo da parte
principal da rifa. Tudo desenhado aqui, com as primitivas do reportlab (linhas, círculos, polígonos): **originais deste projeto**, sem imagens, clipart
nem letras de fora. Só formas: nunca algarismos (o motor procura o número da rifa pelos algarismos; um enfeite com algarismos contava como número).

Geometria (pt, y para cima, a rifa mede 535 × 152): o ícone centra-se em (bx + 18, yb + h − 33) e cabe num quadrado de 34; a faixa de cima fica entre
yb + h − 12 e yb + h − 4 (por cima do título) e a de baixo entre yb + 3 e yb + 9 (por baixo da data), ambas entre o talão e o campo do número.
As cores de cada desenho vêm de `Desenho` (`principal`, `destaque`, `talao`, `papel`); aqui só se juntam tons fixos quando o tema o pede (o verde das folhas, o vermelho do tomate…).
"""
from __future__ import annotations

import math

# ------------------------------------------------------------------ cores fixas (RGB 0-1) usadas pelos motivos
VERDE, VERDE_ESC = (0.20, 0.55, 0.25), (0.10, 0.38, 0.18)
VERMELHO, AZUL, AMARELO, LARANJA, ROSA, ROXO, CASTANHO = (0.82, 0.12, 0.18), (0.15, 0.40, 0.75), (0.98, 0.78, 0.12), (0.93, 0.47, 0.08), (0.93, 0.42, 0.62), (0.45, 0.25, 0.65), (0.45, 0.28, 0.12)
BRANCO, PRETO = (1.0, 1.0, 1.0), (0.1, 0.1, 0.1)


def _cor(c, rgb, traco: bool = False) -> None:
    (c.setStrokeColorRGB if traco else c.setFillColorRGB)(*rgb)


def _poligono(c, pontos, preenche: bool = True, contorno: bool = False) -> None:
    p = c.beginPath()
    p.moveTo(*pontos[0])
    for q in pontos[1:]:
        p.lineTo(*q)
    p.close()
    c.drawPath(p, stroke=1 if contorno else 0, fill=1 if preenche else 0)


# ------------------------------------------------------------------ faixas (decoração ao longo da margem)
def _bandeirinhas(c, x0, x1, ytopo, alt, cores, passo=14.0) -> None:
    """Fio com bandeirinhas triangulares penduradas (arraial, santos populares, festa)."""
    c.setLineWidth(0.8)
    _cor(c, (0.35, 0.35, 0.35), True)
    c.line(x0, ytopo, x1, ytopo)
    i, x = 0, x0 + 2
    while x + passo <= x1:
        _cor(c, cores[i % len(cores)])
        _poligono(c, [(x, ytopo), (x + passo - 2, ytopo), (x + (passo - 2) / 2, ytopo - alt)])
        x += passo
        i += 1


def _riscas(c, x0, x1, y, alt, a, b, passo=10.0) -> None:
    n, i = int((x1 - x0) // passo), 0
    for i in range(n):
        _cor(c, a if i % 2 == 0 else b)
        c.rect(x0 + i * passo, y, passo, alt, stroke=0, fill=1)


def _pontos(c, x0, x1, y, raio, cores, passo=11.0) -> None:
    x, i = x0 + raio, 0
    while x + raio <= x1:
        _cor(c, cores[i % len(cores)])
        c.circle(x, y, raio, stroke=0, fill=1)
        x += passo
        i += 1


def _zigue(c, x0, x1, y, alt, cor, passo=9.0) -> None:
    _cor(c, cor)
    x = x0
    while x + passo <= x1:
        _poligono(c, [(x, y), (x + passo, y), (x + passo / 2, y + alt)])
        x += passo


def _onda(c, x0, x1, y, amp, cor, larg=1.6, passo=16.0) -> None:
    _cor(c, cor, True)
    c.setLineWidth(larg)
    p = c.beginPath()
    p.moveTo(x0, y)
    x, cima = x0, True
    while x + passo / 2 <= x1:
        p.curveTo(x + passo / 6, y + (amp if cima else -amp), x + passo / 3, y + (amp if cima else -amp), x + passo / 2, y)
        x, cima = x + passo / 2, not cima
    c.drawPath(p, stroke=1, fill=0)


def _filete(c, x0, x1, y, cor, larg=0.8) -> None:
    _cor(c, cor, True)
    c.setLineWidth(larg)
    c.line(x0, y, x1, y)


# ------------------------------------------------------------------ ícones
def _ovo(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.ellipse(cx - 11, cy - 15, cx + 11, cy + 15, stroke=0, fill=1)
    _cor(c, BRANCO, True)
    c.setLineWidth(2)
    p = c.beginPath()
    p.moveTo(cx - 10, cy - 2)
    for k in range(5):
        p.lineTo(cx - 10 + (k + 0.5) * 4, cy + (4 if k % 2 == 0 else -2))
    p.lineTo(cx + 10, cy - 2)
    c.drawPath(p, stroke=1, fill=0)
    _cor(c, d.principal)
    for dx, dy in ((-4, 8), (4, 10), (0, -9)):
        c.circle(cx + dx, cy + dy, 1.8, stroke=0, fill=1)


def _confetis(c, cx, cy, d) -> None:
    cores = (d.destaque, d.principal, AMARELO, ROSA, AZUL)
    for k, (dx, dy) in enumerate(((-12, 8), (4, 13), (13, 2), (-6, -6), (8, -11), (-14, -10), (0, 2))):
        _cor(c, cores[k % len(cores)])
        c.saveState()
        c.translate(cx + dx, cy + dy)
        c.rotate(k * 40)
        c.rect(-2.5, -1.5, 5, 3, stroke=0, fill=1)
        c.restoreState()
    _cor(c, d.principal, True)
    c.setLineWidth(1.2)
    p = c.beginPath()
    p.moveTo(cx - 14, cy + 14)
    p.curveTo(cx - 6, cy + 18, cx - 8, cy + 4, cx, cy + 8)
    c.drawPath(p, stroke=1, fill=0)


def _manjerico(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    _poligono(c, [(cx - 11, cy - 4), (cx + 11, cy - 4), (cx + 8, cy - 16), (cx - 8, cy - 16)])
    _cor(c, VERDE)
    for dx, dy, r in ((-8, 2, 6), (0, 8, 7), (8, 2, 6), (0, -1, 6)):
        c.circle(cx + dx, cy + dy, r, stroke=0, fill=1)
    _cor(c, VERMELHO)
    c.circle(cx, cy + 14, 2.2, stroke=0, fill=1)


def _coracao(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.circle(cx - 6.5, cy + 5, 8, stroke=0, fill=1)
    c.circle(cx + 6.5, cy + 5, 8, stroke=0, fill=1)
    _poligono(c, [(cx - 13.7, cy + 2), (cx + 13.7, cy + 2), (cx, cy - 15)])
    _cor(c, BRANCO)
    c.circle(cx - 8, cy + 8, 2, stroke=0, fill=1)


def _sol(c, cx, cy, d) -> None:
    _cor(c, d.destaque, True)
    c.setLineWidth(2)
    for k in range(10):
        a = k * math.pi / 5
        c.line(cx + 11 * math.cos(a), cy + 11 * math.sin(a), cx + 16 * math.cos(a), cy + 16 * math.sin(a))
    _cor(c, d.destaque)
    c.circle(cx, cy, 8.5, stroke=0, fill=1)
    _cor(c, d.principal, True)
    c.setLineWidth(1.4)
    _onda(c, cx - 16, cx + 16, cy - 15, 2, d.principal, 1.4, 8)


def _abobora(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.ellipse(cx - 15, cy - 11, cx + 15, cy + 9, stroke=0, fill=1)
    c.ellipse(cx - 8, cy - 11, cx + 8, cy + 9, stroke=0, fill=1)
    _cor(c, d.principal)
    c.rect(cx - 2, cy + 8, 4, 8, stroke=0, fill=1)
    _cor(c, d.talao)
    _poligono(c, [(cx - 7, cy + 1), (cx - 3, cy + 5), (cx - 3, cy - 1)])
    _poligono(c, [(cx + 7, cy + 1), (cx + 3, cy + 5), (cx + 3, cy - 1)])
    _poligono(c, [(cx - 7, cy - 4), (cx + 7, cy - 4), (cx + 4, cy - 8), (cx, cy - 6), (cx - 4, cy - 8)])


def _folha(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.saveState()
    c.translate(cx, cy)
    c.rotate(35)
    c.ellipse(-8, -15, 8, 15, stroke=0, fill=1)
    _cor(c, d.talao, True)
    c.setLineWidth(1.2)
    c.line(0, -15, 0, 13)
    for k in (-8, -2, 4):
        c.line(0, k, 6, k + 5)
        c.line(0, k, -6, k + 5)
    c.restoreState()
    _cor(c, CASTANHO)
    c.circle(cx - 12, cy - 12, 4.5, stroke=0, fill=1)


def _bola(c, cx, cy, d) -> None:
    _cor(c, BRANCO)
    c.circle(cx, cy, 14, stroke=0, fill=1)
    _cor(c, d.principal, True)
    c.setLineWidth(1.6)
    c.circle(cx, cy, 14, stroke=1, fill=0)
    _cor(c, d.principal)
    pent = [(cx + 6 * math.cos(math.radians(90 + 72 * k)), cy + 6 * math.sin(math.radians(90 + 72 * k))) for k in range(5)]
    _poligono(c, pent)
    for a in range(5):
        ang = math.radians(90 + 72 * a)
        c.setLineWidth(1.2)
        c.line(cx + 6 * math.cos(ang), cy + 6 * math.sin(ang), cx + 13 * math.cos(ang), cy + 13 * math.sin(ang))


def _lapis(c, cx, cy, d) -> None:
    c.saveState()
    c.translate(cx, cy)
    c.rotate(45)
    _cor(c, d.destaque)
    c.rect(-4, -12, 8, 20, stroke=0, fill=1)
    _cor(c, d.principal)
    c.rect(-4, 8, 8, 4, stroke=0, fill=1)
    _cor(c, (0.95, 0.85, 0.65))
    _poligono(c, [(-4, -12), (4, -12), (0, -19)])
    _cor(c, PRETO)
    _poligono(c, [(-1.4, -16.5), (1.4, -16.5), (0, -19)])
    c.restoreState()


def _nota(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.ellipse(cx - 11, cy - 13, cx - 1, cy - 7, stroke=0, fill=1)
    c.ellipse(cx + 4, cy - 10, cx + 14, cy - 4, stroke=0, fill=1)
    _cor(c, d.destaque, True)
    c.setLineWidth(2)
    c.line(cx - 2, cy - 10, cx - 2, cy + 13)
    c.line(cx + 13, cy - 7, cx + 13, cy + 10)
    _poligono(c, [(cx - 2, cy + 13), (cx + 13, cy + 10), (cx + 13, cy + 5), (cx - 2, cy + 8)])


def _laco(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    _poligono(c, [(cx, cy), (cx - 15, cy + 10), (cx - 15, cy - 10)])
    _poligono(c, [(cx, cy), (cx + 15, cy + 10), (cx + 15, cy - 10)])
    _cor(c, d.principal)
    c.circle(cx, cy, 4.5, stroke=0, fill=1)
    _poligono(c, [(cx - 3, cy - 4), (cx - 8, cy - 16), (cx - 1, cy - 12)])
    _poligono(c, [(cx + 3, cy - 4), (cx + 8, cy - 16), (cx + 1, cy - 12)])


def _cruz(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.circle(cx, cy, 15, stroke=0, fill=1)
    _cor(c, BRANCO)
    c.rect(cx - 3.5, cy - 11, 7, 22, stroke=0, fill=1)
    c.rect(cx - 11, cy - 3.5, 22, 7, stroke=0, fill=1)
    _cor(c, d.destaque)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _poligono(c, [(cx + sx * 11, cy + sy * 3.5), (cx + sx * 11, cy + sy * 0), (cx + sx * 8, cy + sy * 3.5)])


def _sol_retro(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    c.circle(cx, cy + 2, 13, stroke=0, fill=1)
    _cor(c, d.papel)
    for k, alt in enumerate((1.2, 1.8, 2.6, 3.4)):
        c.rect(cx - 14, cy - 10 + k * 4.2 - 0.0, 28, alt, stroke=0, fill=1)
    _cor(c, d.principal, True)
    c.setLineWidth(1.4)
    c.line(cx - 16, cy - 13, cx + 16, cy - 13)


def _aro(c, cx, cy, d) -> None:
    _cor(c, d.destaque, True)
    c.setLineWidth(1.2)
    c.circle(cx, cy, 13, stroke=1, fill=0)
    c.circle(cx, cy, 7, stroke=1, fill=0)
    _cor(c, d.destaque)
    c.circle(cx, cy, 2, stroke=0, fill=1)


def _uvas(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    for fila, n in enumerate((4, 3, 2, 1)):
        for k in range(n):
            c.circle(cx + (k - (n - 1) / 2) * 7.5, cy + 8 - fila * 6.5, 3.8, stroke=0, fill=1)
    _cor(c, VERDE)
    _poligono(c, [(cx, cy + 14), (cx + 12, cy + 18), (cx + 9, cy + 9)])
    _cor(c, CASTANHO, True)
    c.setLineWidth(1.6)
    c.line(cx, cy + 12, cx - 1, cy + 17)


def _balao(c, cx, cy, d) -> None:
    for dx, dy, cor in ((-7, 3, d.destaque), (6, 6, d.principal), (0, -3, AMARELO)):
        _cor(c, cor)
        c.ellipse(cx + dx - 6, cy + dy - 7, cx + dx + 6, cy + dy + 7, stroke=0, fill=1)
        _cor(c, (0.4, 0.4, 0.4), True)
        c.setLineWidth(0.7)
        c.line(cx + dx, cy + dy - 7, cx + dx + 1, cy + dy - 17)


def _marca_x(c, cx, cy, d) -> None:
    _cor(c, d.talao)
    c.roundRect(cx - 15, cy - 13, 30, 26, 3, stroke=0, fill=1)
    _cor(c, d.principal, True)
    c.setLineWidth(1)
    c.setDash(2, 2)
    p = c.beginPath()
    p.moveTo(cx - 12, cy - 8)
    p.curveTo(cx - 4, cy + 10, cx + 2, cy - 12, cx + 10, cy + 6)
    c.drawPath(p, stroke=1, fill=0)
    c.setDash()
    _cor(c, d.destaque, True)
    c.setLineWidth(3)
    c.line(cx + 6, cy + 10, cx + 14, cy + 2)
    c.line(cx + 6, cy + 2, cx + 14, cy + 10)


def _flor(c, cx, cy, d) -> None:
    _cor(c, d.destaque)
    for k in range(6):
        a = k * math.pi / 3
        c.circle(cx + 8 * math.cos(a), cy + 8 * math.sin(a), 5.2, stroke=0, fill=1)
    _cor(c, AMARELO)
    c.circle(cx, cy, 5, stroke=0, fill=1)


def _floco(c, cx, cy, d) -> None:
    _cor(c, d.destaque, True)
    c.setLineWidth(2)
    for k in range(3):
        a = k * math.pi / 3
        c.line(cx - 15 * math.cos(a), cy - 15 * math.sin(a), cx + 15 * math.cos(a), cy + 15 * math.sin(a))
    c.setLineWidth(1.2)
    for k in range(6):
        a = k * math.pi / 3
        px, py = cx + 10 * math.cos(a), cy + 10 * math.sin(a)
        c.line(px, py, px + 4 * math.cos(a + 2.4), py + 4 * math.sin(a + 2.4))
        c.line(px, py, px + 4 * math.cos(a - 2.4), py + 4 * math.sin(a - 2.4))


def _claquete(c, cx, cy, d) -> None:
    _cor(c, d.principal)
    c.roundRect(cx - 15, cy - 13, 30, 19, 2, stroke=0, fill=1)
    _cor(c, d.destaque)
    c.saveState()
    c.translate(cx - 15, cy + 8)
    c.rotate(8)
    c.rect(0, 0, 30, 7, stroke=0, fill=1)
    _cor(c, d.principal)
    for k in range(4):
        _poligono(c, [(k * 8 + 2, 0), (k * 8 + 7, 0), (k * 8 + 10, 7), (k * 8 + 5, 7)])
    c.restoreState()
    _cor(c, d.destaque)
    for k in range(3):
        c.rect(cx - 12 + k * 9, cy - 8, 6, 3, stroke=0, fill=1)


# ------------------------------------------------------------------ os 20 desenhos: ícone + faixas
def _topo(x, yb, w, h):
    return x + 62 + 12, x + w - 148 - 8, yb + h - 12            # entre o talão e o campo do número, por cima do título


def _base(x, yb, w, h):
    return x + 62 + 12, x + w - 12, yb + 3


def pascoa(c, d, x, yb, w, h, bx):
    _ovo(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 2.6, (d.destaque, d.principal, AMARELO, ROSA), 12)
    a, b, y0 = _base(x, yb, w, h)
    _zigue(c, a, b, y0, 5, d.destaque, 8)


def carnaval(c, d, x, yb, w, h, bx):
    _confetis(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _bandeirinhas(c, x0, x1, y + 8, 8, (d.destaque, d.principal, AMARELO, ROSA, AZUL), 11)
    a, b, y0 = _base(x, yb, w, h)
    _pontos(c, a, b, y0 + 3, 2, (d.principal, AMARELO, d.destaque, AZUL), 9)


def santos(c, d, x, yb, w, h, bx):
    _manjerico(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _bandeirinhas(c, x0, x1, y + 8, 9, (VERMELHO, AMARELO, VERDE, AZUL, ROSA), 14)
    a, b, y0 = _base(x, yb, w, h)
    _riscas(c, a, b, y0, 5, d.principal, d.papel, 9)


def coracao(c, d, x, yb, w, h, bx):
    _coracao(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 2, (d.destaque, d.principal), 10)
    a, b, y0 = _base(x, yb, w, h)
    _onda(c, a, b, y0 + 3, 2.4, d.destaque, 1.4, 14)


def praia(c, d, x, yb, w, h, bx):
    _sol(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _onda(c, x0, x1, y + 4, 3, d.principal, 1.8, 18)
    a, b, y0 = _base(x, yb, w, h)
    _onda(c, a, b, y0 + 4, 2.6, d.destaque, 1.6, 15)
    _onda(c, a, b, y0 + 1, 2.2, d.principal, 1.2, 15)


def halloween(c, d, x, yb, w, h, bx):
    _abobora(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _zigue(c, x0, x1, y, 8, d.principal, 10)
    a, b, y0 = _base(x, yb, w, h)
    _riscas(c, a, b, y0, 5, d.destaque, d.principal, 10)


def magusto(c, d, x, yb, w, h, bx):
    _folha(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 2.4, (d.destaque, LARANJA, CASTANHO, AMARELO), 13)
    a, b, y0 = _base(x, yb, w, h)
    _zigue(c, a, b, y0, 5, CASTANHO, 8)


def futebol(c, d, x, yb, w, h, bx):
    _bola(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _riscas(c, x0, x1, y, 8, d.destaque, d.principal, 12)
    a, b, y0 = _base(x, yb, w, h)
    _filete(c, a, b, y0 + 4, d.principal, 1.6)
    _filete(c, a, b, y0 + 7, d.principal, 0.8)


def escola(c, d, x, yb, w, h, bx):
    _lapis(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 2.4, (d.destaque, d.principal, AMARELO, VERDE), 12)
    a, b, y0 = _base(x, yb, w, h)
    _filete(c, a, b, y0 + 6, d.principal, 0.7)
    _filete(c, a, b, y0 + 3, d.principal, 0.7)


def festival(c, d, x, yb, w, h, bx):
    _nota(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _onda(c, x0, x1, y + 4, 3, d.destaque, 1.6, 13)
    a, b, y0 = _base(x, yb, w, h)
    _pontos(c, a, b, y0 + 3, 2, (d.destaque, d.principal), 10)


def solidaria(c, d, x, yb, w, h, bx):
    _laco(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _filete(c, x0, x1, y + 4, d.destaque, 2.2)
    _pontos(c, x0, x1, y + 8, 1.4, (d.destaque,), 8)
    a, b, y0 = _base(x, yb, w, h)
    _filete(c, a, b, y0 + 4, d.destaque, 2.2)


def bombeiros(c, d, x, yb, w, h, bx):
    _cruz(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _riscas(c, x0, x1, y, 8, d.destaque, PRETO, 14)
    a, b, y0 = _base(x, yb, w, h)
    _riscas(c, a, b, y0, 5, d.destaque, d.papel, 10)


def retro(c, d, x, yb, w, h, bx):
    _sol_retro(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    for k, cor in enumerate((d.destaque, d.principal, AMARELO)):
        _filete(c, x0, x1, y + 2 + k * 3, cor, 1.6)
    a, b, y0 = _base(x, yb, w, h)
    _zigue(c, a, b, y0, 5, d.principal, 12)


def minimal(c, d, x, yb, w, h, bx):
    _aro(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _filete(c, x0, x1, y + 5, d.destaque, 0.6)
    a, b, y0 = _base(x, yb, w, h)
    _filete(c, a, b, y0 + 5, d.destaque, 0.6)


def vindima(c, d, x, yb, w, h, bx):
    _uvas(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 2.6, (d.destaque, d.principal, VERDE), 12)
    a, b, y0 = _base(x, yb, w, h)
    _onda(c, a, b, y0 + 4, 2.4, VERDE, 1.6, 14)


def arraial(c, d, x, yb, w, h, bx):
    _balao(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _bandeirinhas(c, x0, x1, y + 8, 8, (d.destaque, d.principal, AMARELO, ROSA), 12)
    a, b, y0 = _base(x, yb, w, h)
    _pontos(c, a, b, y0 + 3, 2.2, (AMARELO, d.destaque, d.principal), 11)


def tesouro(c, d, x, yb, w, h, bx):
    _marca_x(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    c.setDash(3, 3)
    _filete(c, x0, x1, y + 4, d.principal, 1.2)
    c.setDash()
    a, b, y0 = _base(x, yb, w, h)
    _zigue(c, a, b, y0, 5, d.principal, 9)


def primavera(c, d, x, yb, w, h, bx):
    _flor(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 2.4, (d.destaque, AMARELO, ROSA, d.principal), 12)
    a, b, y0 = _base(x, yb, w, h)
    _zigue(c, a, b, y0, 5, VERDE, 7)


def inverno(c, d, x, yb, w, h, bx):
    _floco(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _pontos(c, x0, x1, y + 4, 1.8, (d.destaque, d.principal), 9)
    a, b, y0 = _base(x, yb, w, h)
    _zigue(c, a, b, y0, 7, d.destaque, 16)


def cinema(c, d, x, yb, w, h, bx):
    _claquete(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _cor(c, d.principal)
    c.rect(x0, y, x1 - x0, 8, stroke=0, fill=1)
    _cor(c, d.papel)
    xx = x0 + 3
    while xx + 5 <= x1:
        c.rect(xx, y + 2, 5, 4, stroke=0, fill=1)
        xx += 10
    a, b, y0 = _base(x, yb, w, h)
    _filete(c, a, b, y0 + 4, d.destaque, 1.4)


def aniversario(c, d, x, yb, w, h, bx):
    _balao(c, bx + 18, yb + h - 33, d)
    x0, x1, y = _topo(x, yb, w, h)
    _bandeirinhas(c, x0, x1, y + 6, 6, (d.destaque, d.principal, AMARELO), 12)
    a, b, y0 = _base(x, yb, w, h)
    _pontos(c, a, b, y0 + 3, 2, (d.principal, d.destaque, AMARELO), 10)


MOTIVOS = {f.__name__: f for f in (pascoa, carnaval, santos, coracao, praia, halloween, magusto, futebol, escola, festival, solidaria, bombeiros,
                                   retro, minimal, vindima, arraial, tesouro, primavera, inverno, cinema, aniversario)}
