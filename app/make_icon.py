"""Gera assets/icon.ico e assets/icon.png a partir do icone da marca (os dois bilhetes com o 7 da sorte).

A fonte unica do desenho e `src/web/frontend/public/icone.svg`; o PNG de 512 px (`icone-512.png`, com cantos transparentes)
sai dele. Correr uma vez, ou depois de mudar o icone: .venv/Scripts/python.exe make_icon.py
"""
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
ORIGEM = AQUI.parent / "src" / "web" / "frontend" / "public" / "icone-512.png"

im = Image.open(ORIGEM).convert("RGBA")
(AQUI / "assets").mkdir(exist_ok=True)
im.save(AQUI / "assets" / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
im.resize((256, 256), Image.LANCZOS).save(AQUI / "assets" / "icon.png")
print("assets/icon.ico e assets/icon.png gerados a partir de", ORIGEM.name)
