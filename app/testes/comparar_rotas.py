"""Compara, pagina a pagina (1.a, tercos, ultima), a rota vetorial (pdf) com a rota por imagem (png).
Uso: python comparar_rotas.py <pasta_out> <n_bilhetes_por_pagina>   (pasta_out criada por teste_5000.py)"""
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import ImageChops

out, n = Path(sys.argv[1]), int(sys.argv[2])
fa = next((out / f"n{n}_pdf_unico").glob("*.pdf"))
fb = next((out / f"n{n}_png_unico").glob("*.pdf"))
a, b = pdfium.PdfDocument(str(fa)), pdfium.PdfDocument(str(fb))
assert len(a) == len(b), (len(a), len(b))


def render(d, i):
    return d[i].render(scale=300 / 72).to_pil().convert("RGB")


pior = 0.0
for i in sorted({0, len(a) // 3, len(a) // 2, len(a) - 1}):
    x, y = render(a, i), render(b, i)
    h = ImageChops.difference(x, y).convert("L").histogram()
    tot = x.width * x.height
    f40, f128 = sum(h[40:]) / tot * 100, sum(h[128:]) / tot * 100
    pior = max(pior, f128)
    print(f"n={n} pagina {i + 1}/{len(a)}: >=40: {f40:.4f}%  >=128: {f128:.4f}%")
print("RESULTADO:", "OK" if pior < 1.0 else "DIFERENTE")
