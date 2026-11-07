"""Cria os ficheiros de exemplo da app (em exemplos/) com uma rifa INVENTADA, para o tutorial e os testes.

Nada aqui e de uma associacao, escola ou patrocinador reais: e o desenho generico «Rifa de Exemplo».
Usa o reportlab (licenca BSD, so para criar exemplos; nao faz parte da app) e a letra Vera, que vem com o reportlab
(licenca livre). Cria:
  template_exemplo.pdf          5 rifas numa folha A4 (numeros de exemplo 0001..0005, cada um 2x)
  template_exemplo_1_rifa.pdf   UMA rifa com o tamanho da pagina (a app enche a folha com copias)
  template_exemplo_1_rifa_a4.pdf   a mesma rifa no meio de uma folha A4 (a app recorta a zona desenhada)
  digitos_exemplo.pdf / .png    os algarismos 0-9 na mesma letra

Uso:  python testes/fazer_exemplos.py [pasta]      (por defeito: exemplos/)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PASTA_FONTES = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(PASTA_FONTES / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("VeraBd", str(PASTA_FONTES / "VeraBd.ttf")))

VERDE = (0.06, 0.43, 0.45)
LARANJA = (0.93, 0.47, 0.08)
CREME = (1.0, 0.95, 0.85)
CINZA = (0.35, 0.35, 0.35)
W_RIFA, H_RIFA = 535.0, 152.0          # tamanho da rifa (pt): 189 x 54 mm
LARG_TALAO = 62.0


def estrela(c, cx: float, cy: float, r: float) -> None:
    p = c.beginPath()
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        raio = r if i % 2 == 0 else r * 0.45
        x, y = cx + raio * math.cos(ang), cy + raio * math.sin(ang)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def rifa(c, x: float, yb: float, w: float, h: float, numero: str, fundo_cheio: bool = False) -> None:
    """Uma rifa com o canto inferior esquerdo em (x, yb)."""
    c.saveState()
    c.setLineWidth(2)
    c.setStrokeColorRGB(*VERDE)
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(x, yb, w, h, 10, stroke=1, fill=1)
    # talao (esquerda), tracejado a separar
    c.setFillColorRGB(*CREME)
    c.setLineWidth(0)
    c.roundRect(x + 1, yb + 1, LARG_TALAO, h - 2, 9, stroke=0, fill=1)
    c.rect(x + LARG_TALAO - 12, yb + 1, 12, h - 2, stroke=0, fill=1)
    c.setStrokeColorRGB(*VERDE)
    c.setLineWidth(1)
    c.setDash(3, 3)
    c.line(x + LARG_TALAO, yb + 6, x + LARG_TALAO, yb + h - 6)
    c.setDash()
    # numero do talao (a subir)
    c.setFillColorRGB(*LARANJA)
    c.saveState()
    c.translate(x + LARG_TALAO / 2 + 6, yb + h / 2 - 25)
    c.rotate(90)
    c.setFont("VeraBd", 19)
    c.drawString(0, 0, numero)
    c.restoreState()
    c.setFillColorRGB(*CINZA)
    c.saveState()
    c.translate(x + LARG_TALAO / 2 - 12, yb + h / 2 - 8)
    c.rotate(90)
    c.setFont("Vera", 9)
    c.drawString(0, 0, "Nº")
    c.restoreState()
    # parte principal: titulo, premios, sorteio
    bx = x + LARG_TALAO + 14
    c.setFillColorRGB(*LARANJA)
    estrela(c, bx + 18, yb + h - 33, 17)
    c.setFillColorRGB(1, 1, 1)
    c.circle(bx + 18, yb + h - 33, 5.5, stroke=0, fill=1)
    c.setFillColorRGB(*VERDE)
    c.setFont("VeraBd", 21)
    c.drawString(bx + 44, yb + h - 33, "RIFA DE EXEMPLO")
    c.setFillColorRGB(*CINZA)
    c.setFont("Vera", 8.5)
    c.drawString(bx + 44, yb + h - 47, "Associação Imaginária · Festa de Exemplo")
    c.setFont("Vera", 9.5)
    c.setFillColorRGB(0.15, 0.15, 0.15)
    for i, linha in enumerate(("1.º Prémio: Cabaz de exemplo", "2.º Prémio: Vale de exemplo",
                               "3.º Prémio: Livro de exemplo")):
        c.drawString(bx, yb + h - 70 - i * 13, linha)
    c.setFillColorRGB(*VERDE)
    c.setFont("VeraBd", 10.5)
    c.drawString(bx, yb + 14, "Sorteio: 31/12/2099")
    # numero na parte principal (caixa laranja) + campos a preencher
    ex = x + w - 148
    c.setFillColorRGB(*CINZA)
    c.setFont("Vera", 11)
    c.drawString(ex - 6, yb + h - 41, "Nº")
    c.setStrokeColorRGB(*LARANJA)
    c.setLineWidth(2.5)
    c.setFillColorRGB(1, 0.97, 0.9)
    c.roundRect(ex + 14, yb + h - 52, 100, 30, 8, stroke=1, fill=1)
    c.setFillColorRGB(*LARANJA)
    c.setFont("VeraBd", 20)
    c.drawString(ex + 14 + (100 - pdfmetrics.stringWidth(numero, "VeraBd", 20)) / 2, yb + h - 44, numero)
    c.setFillColorRGB(*CINZA)
    c.setFont("Vera", 8)
    c.setLineWidth(0.6)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setDash(1, 2)
    for i, rotulo in enumerate(("Nome:", "Telemóvel:")):
        yy = yb + h - 76 - i * 24
        c.drawString(ex - 6, yy, rotulo)
        c.line(ex + 44, yy - 2, x + w - 14, yy - 2)
    c.setDash()
    c.restoreState()


def folha_de_5(destino: Path) -> None:
    W, H = 595.0, 842.0
    c = canvas.Canvas(str(destino), pagesize=(W, H))
    c.setFillColorRGB(0.88, 0.95, 0.94)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColorRGB(0.80, 0.91, 0.90)
    for i in range(0, 60):         # fundo decorativo: circulos
        c.circle((i * 97) % W, (i * 173) % H, 9 + (i * 7) % 14, stroke=0, fill=1)
    x = (W - W_RIFA) / 2
    for k in range(5):
        rifa(c, x, H - 25 - (k + 1) * H_RIFA - k * 8, W_RIFA, H_RIFA, f"{k + 1:04d}")
    c.save()


def uma_rifa(destino: Path, pagina_a4: bool = False) -> None:
    if pagina_a4:
        W, H = 595.0, 842.0
        c = canvas.Canvas(str(destino), pagesize=(W, H))
        rifa(c, (W - W_RIFA) / 2, (H - H_RIFA) / 2 + 150, W_RIFA, H_RIFA, "0001")
    else:      # a pagina tem o tamanho da rifa (no Canva: «Tamanho personalizado»)
        c = canvas.Canvas(str(destino), pagesize=(W_RIFA + 4, H_RIFA + 4))
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, W_RIFA + 4, H_RIFA + 4, stroke=0, fill=1)
        rifa(c, 2, 2, W_RIFA, H_RIFA, "0001")
    c.save()


def algarismos(pasta: Path) -> None:
    d = canvas.Canvas(str(pasta / "digitos_exemplo.pdf"), pagesize=(520, 110))
    d.setFont("VeraBd", 54)
    d.drawString(20, 35, "0123456789")
    d.save()
    tmp = pasta / "_tmp_digitos.pdf"
    d2 = canvas.Canvas(str(tmp), pagesize=(900, 110))      # um espaco visivel entre algarismos (para o PNG)
    d2.setFont("VeraBd", 54)
    x = 20.0
    for ch in "0123456789":
        d2.drawString(x, 35, ch)
        x += pdfmetrics.stringWidth(ch, "VeraBd", 54) + 14
    d2.save()
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(tmp))
    doc[0].render(scale=8).to_pil().convert("RGB").save(pasta / "digitos_exemplo.png", optimize=True)
    doc.close()
    tmp.unlink()


def criar(pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    folha_de_5(pasta / "template_exemplo.pdf")
    uma_rifa(pasta / "template_exemplo_1_rifa.pdf")
    uma_rifa(pasta / "template_exemplo_1_rifa_a4.pdf", pagina_a4=True)
    algarismos(pasta)


if __name__ == "__main__":
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "exemplos"
    criar(destino)
    print("exemplos criados em", destino)
