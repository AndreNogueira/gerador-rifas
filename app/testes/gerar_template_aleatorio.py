"""Gera templates de rifa ALEATORIOS (so para testar a app) + o ficheiro com os algarismos 0-9.
(Usa reportlab, licenca BSD; nao faz parte da app.)

Cada template tem N bilhetes por pagina, tamanho de pagina, grelha, cores, tipo de letra, orientacao do
talao e fundo aleatorios, com os numeros de exemplo 0001..000N (ou com mais algarismos) escritos 2x
(talao + parte principal) e numeros fixos que NAO sao de exemplo (ano, telefone a comecar por 0) para
garantir que a app os deixa em paz.

Uso:  python gerar_template_aleatorio.py <pasta_saida> <semente> <bilhetes_por_pagina> [rotacao_talao|-] [algarismos] [LxH em pt]
"""
from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# pasta das letras do sistema: variavel RIFAS_FONTES, ou %WINDIR%\Fonts
PASTA_FONTES = Path(os.environ.get("RIFAS_FONTES") or Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts")
FONTES = ["arial.ttf", "arialbd.ttf", "georgia.ttf", "georgiab.ttf", "times.ttf", "timesbd.ttf",
          "verdana.ttf", "verdanab.ttf", "impact.ttf", "comic.ttf", "trebuc.ttf", "tahoma.ttf",
          "calibri.ttf", "candara.ttf", "corbel.ttf", "consola.ttf", "cour.ttf", "palab.ttf", "segoeui.ttf"]
PAGINAS = {"A4": (595.0, 842.0), "A4 paisagem": (842.0, 595.0), "A5": (420.0, 595.0), "Letter": (612.0, 792.0)}


def _cor(rnd: random.Random, claro: bool) -> tuple:
    if claro:
        return tuple(rnd.uniform(0.82, 1.0) for _ in range(3))
    return tuple(rnd.uniform(0.0, 0.7) for _ in range(3))


def _grelha(n: int, rnd: random.Random) -> tuple:
    if n <= 4:
        return 1, n
    if n <= 12:
        return rnd.choice([(1, n), (2, -(-n // 2))])
    return rnd.choice([(2, -(-n // 2)), (3, -(-n // 3))])


def criar(destino: Path, semente: int, n: int, talao_rot: int | None = None, ndig: int = 4,
          tamanho: tuple | None = None) -> dict:
    """`tamanho` = (largura, altura) da pagina em pt: com n=1 serve para criar uma pagina do tamanho da rifa."""
    rnd = random.Random(semente)
    destino.mkdir(parents=True, exist_ok=True)
    nome_pag = rnd.choice(list(PAGINAS))
    W, H = PAGINAS[nome_pag]
    if n > 8 and W > H:       # muitos bilhetes: pagina em altura
        nome_pag, (W, H) = "A4", PAGINAS["A4"]
    if tamanho is not None:
        nome_pag, (W, H) = "rifa", tamanho
    fonte_ttf = PASTA_FONTES / rnd.choice(FONTES)
    if not fonte_ttf.exists():       # sem as letras do Windows (p.ex. Linux): usa as que o reportlab traz (Vera / Vera Bold)
        fonte_ttf = Path(reportlab.__file__).parent / "fonts" / ("VeraBd.ttf" if fonte_ttf.stem.endswith("bd") else "Vera.ttf")
    cols, rows = _grelha(n, rnd)
    margem, gap = (3.0 if tamanho is not None else 18.0), 8.0
    tw = (W - 2 * margem - gap * (cols - 1)) / cols
    th = (H - 2 * margem - gap * (rows - 1)) / rows
    talao_lado = rnd.choice(["esq", "dir"])
    sorteado = rnd.choice([90, 270, 90, 0])
    talao_rot = sorteado if talao_rot is None else talao_rot
    talao_w = tw * rnd.uniform(0.14, 0.22) if talao_rot != 0 else tw * 0.2
    cor_num, cor_pag = _cor(rnd, False), _cor(rnd, True)
    cor_bil, cor_borda = _cor(rnd, True), _cor(rnd, False)
    tam_main = max(7.0, min(26.0, th * rnd.uniform(0.16, 0.30), tw * 0.12))
    tam_talao = max(6.0, min(tam_main * rnd.uniform(0.8, 1.0), talao_w * 0.55 if talao_rot else 14))
    if ndig > 4:                # mais algarismos: reduz o corpo para caberem
        tam_main *= 4 / ndig * 1.2
        tam_talao *= 4 / ndig * 1.2
    nome_fonte = f"FT{semente}"
    pdfmetrics.registerFont(TTFont(nome_fonte, str(fonte_ttf)))
    larg = lambda s, tam: pdfmetrics.stringWidth(s, nome_fonte, tam)

    pdf = destino / f"template_{n}_por_pagina_{ndig}dig_s{semente}.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(W, H))
    c.setFillColorRGB(*cor_pag)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    for _ in range(rnd.randint(8, 24)):          # fundo "decorado": circulos com transparencia
        c.setFillColorRGB(*_cor(rnd, rnd.random() < 0.5))
        c.setFillAlpha(rnd.uniform(0.15, 0.5))
        c.circle(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(10, 60), stroke=0, fill=1)
    c.setFillAlpha(1)
    titulos = ["Grande Rifa", "Rifa de Natal", "Sorteio Solidário", "Tombola", "Lotería Benéfica"]
    campo = 0
    for r in range(rows):
        for col in range(cols):
            campo += 1
            if campo > n:
                break
            x0 = margem + col * (tw + gap)
            y0 = margem + r * (th + gap)           # y para baixo (convertido ao desenhar)
            yb = H - y0 - th
            c.setStrokeColorRGB(*cor_borda)
            c.setFillColorRGB(*cor_bil)
            c.setLineWidth(1.2)
            c.roundRect(x0, yb, tw, th, min(tw, th) * 0.06, stroke=1, fill=1)
            if talao_lado == "esq":
                t0, t1, p0, p1 = x0, x0 + talao_w, x0 + talao_w, x0 + tw
                xl = t1
            else:
                t0, t1, p0, p1 = x0 + tw - talao_w, x0 + tw, x0, x0 + tw - talao_w
                xl = t0
            c.setLineWidth(0.8)
            c.setDash(2, 3)
            c.line(xl, yb + 3, xl, yb + th - 3)
            c.setDash()
            # texto fixo + numeros fixos que nao sao de exemplo
            c.setFillColorRGB(*cor_borda)
            c.setFont("Helvetica-Bold", tam_main * 0.9)
            c.drawString(p0 + 8, yb + th - 6 - tam_main, rnd.choice(titulos))
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", tam_main * 0.55)
            c.drawString(p0 + 8, yb + th - 6 - tam_main * 2.4, "Sorteio: 12/12/2026")
            c.setFont("Helvetica", tam_main * 0.5)
            c.drawString(p0 + 8, yb + 8, "Tel. 0912345678")
            texto = f"{campo:0{ndig}d}"
            # numero na parte principal (horizontal), canto direito-inferior
            c.setFillColorRGB(*cor_num)
            c.setFont(nome_fonte, tam_main)
            c.drawString(p1 - larg(texto, tam_main) - 10, yb + 10 + tam_main * 0.2, texto)
            # numero no talao (rodado)
            lt = larg(texto, tam_talao)
            cx, cy = (t0 + t1) / 2, yb + th / 2
            c.saveState()
            c.setFont(nome_fonte, tam_talao)
            if talao_rot == 90:
                c.translate(cx + tam_talao * 0.35, cy - lt / 2)
            elif talao_rot == 270:
                c.translate(cx - tam_talao * 0.35, cy + lt / 2)
            elif talao_rot == 180:
                c.translate(cx + lt / 2, cy + tam_talao * 0.35)
            else:
                c.translate(cx - lt / 2, cy - tam_talao * 0.35)
            c.rotate(talao_rot)
            c.drawString(0, 0, texto)
            c.restoreState()
    c.save()

    # ficheiro com os algarismos (o que o utilizador forneceria): PDF com texto + PNG espacado
    dpdf = destino / f"algarismos_s{semente}.pdf"
    d = canvas.Canvas(str(dpdf), pagesize=(520, 110))
    d.setFont(nome_fonte, 54)
    d.drawString(20, 35, "0123456789")
    d.save()
    dpng = destino / f"algarismos_s{semente}.png"
    d2 = canvas.Canvas(str(destino / f"_tmp_{semente}.pdf"), pagesize=(900, 110))
    d2.setFont(nome_fonte, 54)
    x = 20.0
    for ch in "0123456789":
        d2.drawString(x, 35, ch)
        x += larg(ch, 54) + 14
    d2.save()
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(destino / f"_tmp_{semente}.pdf"))
    doc[0].render(scale=8).to_pil().convert("RGB").save(dpng)
    doc.close()
    (destino / f"_tmp_{semente}.pdf").unlink()
    meta = {"template": pdf.name, "algarismos_pdf": dpdf.name, "algarismos_png": dpng.name, "n": n, "ndig": ndig,
            "pagina": f"{nome_pag} {W:.0f}x{H:.0f}", "grelha": f"{cols}x{rows}", "fonte": fonte_ttf.name,
            "talao": f"{talao_lado} rot={talao_rot}", "tam_main": round(tam_main, 1), "tam_talao": round(tam_talao, 1)}
    (destino / f"meta_s{semente}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return meta


if __name__ == "__main__":
    a = sys.argv
    tam = tuple(float(v) for v in a[6].lower().split("x")) if len(a) > 6 else None      # ex.: 480x150
    print(criar(Path(a[1]), int(a[2]), int(a[3]), int(a[4]) if len(a) > 4 and a[4] != "-" else None,
                int(a[5]) if len(a) > 5 else 4, tam))
