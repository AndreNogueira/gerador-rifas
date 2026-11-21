"""M4: galeria de templates prontos, para quem nao sabe fazer o template no Canva.

Cada desenho e UMA rifa (535 x 152 pt, 189 x 54 mm) com talao: o numero 0001 aparece duas vezes (talao e parte principal), como o motor
exige, e a webapp enche a folha com copias. Os textos (titulo, organizacao, premios, data) escreve-os quem usa. A letra e a Vera
(Bitstream Vera, que vem com o reportlab: livre, pode-se embeber em PDFs) e os algarismos 0-9 vem noutro PDF na mesma letra.
Os desenhos sao originais deste projeto (nada de associacoes, marcas nem do Canva). O reportlab so se importa ao usar a galeria.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass
from pathlib import Path

from . import galeria_enfeites, letras
from .motor import ErroRifas

LARGURA, ALTURA = 535.0, 152.0           # a rifa (pt)
MARGEM = 2.0
TALAO = 62.0                             # largura do talao (esquerda)
MAX_TITULO, MAX_ORGANIZACAO, MAX_PREMIO, MAX_DATA = 40, 60, 50, 60
MIN_PREMIOS, MAX_PREMIOS = 3, 10         # quantos premios a pessoa pode escolher (as caixas na interface); a rifa tambem sai bem com menos
POR_COLUNA = 5                           # ate 5 premios numa coluna; de 6 a 10 passam a duas colunas
EXEMPLO = ("RIFA DE EXEMPLO", "Associação Imaginária · Festa de Exemplo",
           ("1.º Prémio: Cabaz de exemplo", "2.º Prémio: Vale de exemplo", "3.º Prémio: Livro de exemplo"), "Sorteio: 31/12/2099")


@dataclass(frozen=True)
class Textos:
    titulo: str = ""
    organizacao: str = ""
    premios: tuple = ()
    data: str = ""

    def vazio(self) -> bool:
        return not (self.titulo.strip() or self.organizacao.strip() or any(p.strip() for p in self.premios) or self.data.strip())

    def ou_exemplo(self) -> "Textos":
        """Sem nada escrito, o texto de exemplo (a mesma rifa inventada dos ficheiros de exemplo)."""
        return Textos(*EXEMPLO) if self.vazio() else self


@dataclass(frozen=True)
class Desenho:
    id: str
    nome: str                  # nome proprio: nao se traduz (como os temas visuais)
    principal: tuple           # cor do titulo e dos contornos
    destaque: tuple            # cor dos numeros e do enfeite
    talao: tuple               # fundo do talao
    papel: tuple               # fundo da rifa
    enfeite: str               # estrela | riscas | flocos | losangos (os 4 de base) ou o nome de um motivo de `galeria_enfeites.MOTIVOS`


DESENHOS = (
    Desenho("bosque", "Bosque", (0.06, 0.43, 0.45), (0.93, 0.47, 0.08), (1.0, 0.95, 0.85), (1.0, 1.0, 1.0), "estrela"),
    Desenho("quermesse", "Quermesse", (0.75, 0.10, 0.18), (0.89, 0.55, 0.0), (1.0, 0.93, 0.62), (1.0, 0.98, 0.90), "riscas"),
    Desenho("natal", "Natal", (0.05, 0.38, 0.20), (0.78, 0.10, 0.12), (0.88, 0.96, 0.90), (1.0, 1.0, 1.0), "flocos"),
    Desenho("gala", "Gala", (0.09, 0.14, 0.34), (0.75, 0.58, 0.18), (0.93, 0.91, 0.84), (0.99, 0.98, 0.95), "losangos"),
)
DESENHOS += (
    Desenho("pascoa", "Páscoa", (0.45, 0.35, 0.7), (0.96, 0.55, 0.6), (1.0, 0.96, 0.8), (1.0, 1.0, 0.96), "pascoa"),
    Desenho("carnaval", "Carnaval", (0.55, 0.1, 0.55), (0.95, 0.35, 0.15), (0.99, 0.92, 0.7), (1.0, 0.99, 0.95), "carnaval"),
    Desenho("santos", "Santos Populares", (0.78, 0.15, 0.18), (0.15, 0.5, 0.25), (1.0, 0.93, 0.75), (1.0, 0.99, 0.93), "santos"),
    Desenho("coracao", "Coração", (0.7, 0.1, 0.3), (0.9, 0.25, 0.4), (1.0, 0.9, 0.92), (1.0, 0.98, 0.98), "coracao"),
    Desenho("praia", "Praia", (0.0, 0.45, 0.6), (0.98, 0.6, 0.15), (0.99, 0.93, 0.75), (0.97, 1.0, 1.0), "praia"),
    Desenho("halloween", "Halloween", (0.25, 0.12, 0.35), (0.95, 0.5, 0.1), (0.99, 0.88, 0.7), (1.0, 0.98, 0.94), "halloween"),
    Desenho("magusto", "Magusto", (0.5, 0.25, 0.1), (0.8, 0.4, 0.1), (0.97, 0.9, 0.75), (1.0, 0.98, 0.93), "magusto"),
    Desenho("futebol", "Futebol", (0.05, 0.4, 0.15), (0.15, 0.6, 0.25), (0.88, 0.96, 0.88), (1.0, 1.0, 1.0), "futebol"),
    Desenho("escola", "Escola", (0.1, 0.3, 0.65), (0.9, 0.3, 0.2), (1.0, 0.95, 0.78), (1.0, 1.0, 0.98), "escola"),
    Desenho("festival", "Festival", (0.35, 0.1, 0.55), (0.95, 0.2, 0.55), (0.95, 0.88, 1.0), (0.99, 0.97, 1.0), "festival"),
    Desenho("solidaria", "Solidária", (0.05, 0.35, 0.35), (0.85, 0.2, 0.25), (0.88, 0.96, 0.95), (1.0, 1.0, 1.0), "solidaria"),
    Desenho("bombeiros", "Bombeiros", (0.15, 0.15, 0.15), (0.8, 0.1, 0.1), (1.0, 0.9, 0.88), (1.0, 1.0, 1.0), "bombeiros"),
    Desenho("retro", "Retro", (0.2, 0.1, 0.45), (0.95, 0.35, 0.6), (1.0, 0.93, 0.7), (0.99, 0.96, 0.9), "retro"),
    Desenho("minimal", "Minimalista", (0.15, 0.15, 0.15), (0.45, 0.45, 0.45), (0.95, 0.95, 0.95), (1.0, 1.0, 1.0), "minimal"),
    Desenho("vindima", "Vindima", (0.35, 0.1, 0.3), (0.45, 0.15, 0.5), (0.96, 0.9, 0.8), (0.99, 0.98, 0.94), "vindima"),
    Desenho("arraial", "Arraial", (0.75, 0.2, 0.1), (0.15, 0.45, 0.8), (1.0, 0.93, 0.75), (1.0, 0.99, 0.94), "arraial"),
    Desenho("tesouro", "Tesouro", (0.4, 0.25, 0.1), (0.75, 0.15, 0.15), (0.96, 0.88, 0.68), (0.99, 0.96, 0.88), "tesouro"),
    Desenho("primavera", "Primavera", (0.2, 0.5, 0.25), (0.92, 0.35, 0.55), (0.92, 0.98, 0.88), (1.0, 1.0, 0.98), "primavera"),
    Desenho("inverno", "Inverno", (0.1, 0.3, 0.55), (0.35, 0.6, 0.85), (0.9, 0.95, 1.0), (0.98, 0.99, 1.0), "inverno"),
    Desenho("cinema", "Cinema", (0.1, 0.1, 0.15), (0.85, 0.65, 0.1), (0.95, 0.92, 0.82), (0.99, 0.98, 0.95), "cinema"),
    Desenho("aniversario", "Aniversário", (0.85, 0.15, 0.45), (0.05, 0.6, 0.6), (1.0, 0.95, 0.78), (1.0, 0.99, 0.96), "aniversario"),
)
POR_ID = {d.id: d for d in DESENHOS}
assert len(POR_ID) == len(DESENHOS) == 25
_REGISTADA = False             # (a registar das letras e do `core.letras`)


def _fontes() -> Path:
    import reportlab
    return Path(reportlab.__file__).parent / "fonts"


def _registar() -> None:
    """Regista as letras (Vera, DejaVu e as Noto de chinês, japonês e coreano; ver `core.letras`)."""
    letras.registar()


def _largura(texto: str, fonte: str, tamanho: float) -> float:
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(texto, fonte, tamanho)


def _ajustar(texto: str, fonte: str, tamanho: float, maximo: float, minimo: float) -> float:
    """O tamanho da letra (entre `minimo` e `tamanho`) com que o texto cabe em `maximo` pt."""
    while tamanho > minimo and _largura(texto, fonte, tamanho) > maximo:
        tamanho -= 0.5
    return tamanho


def validar(textos: Textos) -> None:
    """Os textos cabem e ha letra para todos (latinas, gregas, cirilicas, vietnamitas, chines, japones e coreano: `core.letras`). Levanta err_galeria_texto."""
    _registar()
    todos = [textos.titulo, textos.organizacao, *textos.premios, textos.data]
    limites = [MAX_TITULO, MAX_ORGANIZACAO, *([MAX_PREMIO] * len(textos.premios)), MAX_DATA]
    if len(textos.premios) > MAX_PREMIOS:
        raise ErroRifas("err_galeria_texto", car="…")
    for t, m in zip(todos, limites, strict=True):
        if len(t) > m:
            raise ErroRifas("err_galeria_texto", car=t[:14] + "…")
        falta = letras.em_falta(t)
        if falta:
            raise ErroRifas("err_galeria_texto", car=falta)


# ------------------------------------------------------------------ o desenho
def _estrela(c, cx: float, cy: float, r: float) -> None:
    p = c.beginPath()
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        raio = r if i % 2 == 0 else r * 0.45
        x, y = cx + raio * math.cos(ang), cy + raio * math.sin(ang)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def _enfeite(c, d: Desenho, x: float, yb: float, w: float, h: float, bx: float) -> None:
    """O enfeite do desenho: a estrela, as riscas do toldo, a neve ou os losangos (dentro da parte principal)."""
    if d.enfeite in galeria_enfeites.MOTIVOS:                         # os 20 desenhos novos: ver galeria_enfeites.py
        c.saveState()
        galeria_enfeites.MOTIVOS[d.enfeite](c, d, x, yb, w, h, bx)
        c.restoreState()
        return
    c.saveState()
    c.setFillColorRGB(*d.destaque)
    c.setStrokeColorRGB(*d.destaque)
    if d.enfeite == "estrela":
        _estrela(c, bx + 18, yb + h - 33, 17)
        c.setFillColorRGB(*d.papel)
        c.circle(bx + 18, yb + h - 33, 5.5, stroke=0, fill=1)
    elif d.enfeite == "riscas":                                       # toldo de feira: riscas na margem de cima
        largura = 14.0
        n = int((w - TALAO - 24) // largura)
        for i in range(n):
            c.setFillColorRGB(*(d.principal if i % 2 == 0 else d.papel))
            c.rect(x + TALAO + 12 + i * largura, yb + h - 12, largura, 9, stroke=0, fill=1)
        c.setFillColorRGB(*d.destaque)
        c.circle(bx + 18, yb + h - 36, 11, stroke=0, fill=1)
    elif d.enfeite == "flocos":                                       # neve a cair: pontos claros, sempre os mesmos sitios (nada aleatorio)
        c.setFillColorRGB(*[1 - (1 - v) * 0.22 for v in d.principal])
        semente = 7
        for i in range(34):
            semente = (semente * 1103515245 + 12345) % 2147483648
            px = x + TALAO + 12 + (semente % 10000) / 10000 * (w - TALAO - 24)
            semente = (semente * 1103515245 + 12345) % 2147483648
            py = yb + 8 + (semente % 10000) / 10000 * (h - 16)
            c.circle(px, py, 1.4 + (i % 3) * 0.8, stroke=0, fill=1)
        c.setFillColorRGB(*d.principal)
        for k in range(3):                                            # um pinheiro
            c.saveState()
            p = c.beginPath()
            p.moveTo(bx + 18, yb + h - 20 - k * 9)
            p.lineTo(bx + 8 - k * 2, yb + h - 33 - k * 9)
            p.lineTo(bx + 28 + k * 2, yb + h - 33 - k * 9)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
            c.restoreState()
    else:                                                             # losangos art deco
        c.setLineWidth(1)
        c.setFillColorRGB(*d.destaque)
        for ox, oy in ((x + TALAO + 14, yb + h - 14), (x + w - 14, yb + h - 14), (x + w - 14, yb + 14)):
            p = c.beginPath()
            p.moveTo(ox, oy + 6)
            p.lineTo(ox + 6, oy)
            p.lineTo(ox, oy - 6)
            p.lineTo(ox - 6, oy)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
        c.setStrokeColorRGB(*d.destaque)
        c.rect(x + TALAO + 6, yb + 6, w - TALAO - 12, h - 12, stroke=1, fill=0)
    c.restoreState()


def _rifa(c, d: Desenho, x: float, yb: float, w: float, h: float, textos: Textos, numero: str = "0001") -> None:
    c.saveState()
    c.setLineWidth(2)
    c.setStrokeColorRGB(*d.principal)
    c.setFillColorRGB(*d.papel)
    c.roundRect(x, yb, w, h, 10, stroke=1, fill=1)
    # talao (esquerda), tracejado a separar
    c.setFillColorRGB(*d.talao)
    c.setLineWidth(0)
    c.roundRect(x + 1, yb + 1, TALAO, h - 2, 9, stroke=0, fill=1)
    c.rect(x + TALAO - 12, yb + 1, 12, h - 2, stroke=0, fill=1)
    c.setStrokeColorRGB(*d.principal)
    c.setLineWidth(1)
    c.setDash(3, 3)
    c.line(x + TALAO, yb + 6, x + TALAO, yb + h - 6)
    c.setDash()
    # numero do talao (a subir)
    c.setFillColorRGB(*d.destaque)
    c.saveState()
    c.translate(x + TALAO / 2 + 6, yb + h / 2 - 25)
    c.rotate(90)
    c.setFont("VeraBd", 19)
    c.drawString(0, 0, numero)
    c.restoreState()
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.saveState()
    c.translate(x + TALAO / 2 - 12, yb + h / 2 - 8)
    c.rotate(90)
    c.setFont("Vera", 9)
    c.drawString(0, 0, "Nº")
    c.restoreState()
    # parte principal
    bx = x + TALAO + 14
    _enfeite(c, d, x, yb, w, h, bx)
    largura_titulo = (w - 148 - 12) - (bx + 44)
    if textos.titulo.strip():
        f = letras.fonte(textos.titulo, True)
        tam = _ajustar(textos.titulo, f, 21, largura_titulo, 11)
        c.setFillColorRGB(*d.principal)
        c.setFont(f, tam)
        c.drawString(bx + 44, yb + h - 33, textos.titulo)
    if textos.organizacao.strip():
        f = letras.fonte(textos.organizacao)
        tam = _ajustar(textos.organizacao, f, 8.5, largura_titulo, 5.5)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        c.setFont(f, tam)
        c.drawString(bx + 44, yb + h - 47, textos.organizacao)
    c.setFillColorRGB(0.15, 0.15, 0.15)
    premios = [p for p in textos.premios if p.strip()]
    colunas = 2 if len(premios) > POR_COLUNA else 1
    espaco = w - 148 - 12 - bx + x                                    # a largura que ha para os premios
    larg_coluna = (espaco - 12) / 2 if colunas == 2 else espaco
    for i, linha in enumerate(premios):
        coluna, fila = divmod(i, POR_COLUNA) if colunas == 2 else (0, i)
        f = letras.fonte(linha)
        tam = _ajustar(linha, f, 9.5 if colunas == 1 else 8, larg_coluna, 6 if colunas == 1 else 4.5)
        c.setFont(f, tam)
        c.drawString(bx + coluna * (larg_coluna + 12), yb + h - 70 - fila * 13, linha)
    if textos.data.strip():
        f = letras.fonte(textos.data, True)
        tam = _ajustar(textos.data, f, 10.5, w - 148 - 12 - bx + x, 7)
        c.setFillColorRGB(*d.principal)
        c.setFont(f, tam)
        c.drawString(bx, yb + 14, textos.data)
    # o numero na parte principal (caixa) e os campos a preencher
    ex = x + w - 148
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.setFont("Vera", 11)
    c.drawString(ex - 6, yb + h - 41, "Nº")
    c.setStrokeColorRGB(*d.destaque)
    c.setLineWidth(2.5)
    c.setFillColorRGB(*d.talao)
    c.roundRect(ex + 14, yb + h - 52, 100, 30, 8, stroke=1, fill=1)
    c.setFillColorRGB(*d.destaque)
    c.setFont("VeraBd", 20)
    c.drawString(ex + 14 + (100 - _largura(numero, "VeraBd", 20)) / 2, yb + h - 44, numero)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.setFont("Vera", 8)
    c.setLineWidth(0.6)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setDash(1, 2)
    for i, rotulo in enumerate(("Nome:", "Tel.:")):
        yy = yb + h - 76 - i * 24
        c.drawString(ex - 6, yy, rotulo)
        c.line(ex + 30, yy - 2, x + w - 14, yy - 2)
    c.setDash()
    c.restoreState()


def criar_template(desenho: str, textos: Textos) -> bytes:
    """O PDF do template (a pagina e a rifa, com 2 pt de folga): 1 rifa com talao, numero 0001 duas vezes. `ErroRifas` se o desenho nao existe
    ou os textos nao cabem na letra."""
    d = POR_ID.get(desenho)
    if d is None:
        raise ErroRifas("err_galeria_texto", car="?")
    textos = textos.ou_exemplo()
    validar(textos)
    from reportlab.pdfgen import canvas
    saida = io.BytesIO()
    c = canvas.Canvas(saida, pagesize=(LARGURA + 2 * MARGEM, ALTURA + 2 * MARGEM), pageCompression=1, invariant=1)   # invariant: mesmos bytes para os mesmos textos
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, LARGURA + 2 * MARGEM, ALTURA + 2 * MARGEM, stroke=0, fill=1)
    _rifa(c, d, MARGEM, MARGEM, LARGURA, ALTURA, textos)
    c.save()
    return saida.getvalue()


def criar_algarismos() -> bytes:
    """O PDF com os algarismos 0-9 na mesma letra do numero do template (VeraBd)."""
    _registar()
    from reportlab.pdfgen import canvas
    saida = io.BytesIO()
    c = canvas.Canvas(saida, pagesize=(520, 110), pageCompression=1, invariant=1)
    c.setFont("VeraBd", 54)
    c.drawString(20, 35, "0123456789")
    c.save()
    return saida.getvalue()
