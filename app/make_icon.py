"""Gera assets/icon.ico (bilhete de rifa). Correr uma vez: .venv/Scripts\python.exe make_icon.py"""
from PIL import Image, ImageDraw
S = 512
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((20, 110, S - 20, S - 110), radius=46, fill=(176, 58, 46, 255))
d.rounded_rectangle((44, 134, S - 44, S - 134), radius=30, outline=(235, 200, 120, 255), width=8)
for y in range(150, S - 150, 30):          # picotado do talao
    d.ellipse((150, y, 162, y + 12), fill=(235, 200, 120, 255))
for x0 in (205, 275, 345):                  # tres "algarismos"
    d.rounded_rectangle((x0, 215, x0 + 50, 297), radius=24, outline=(255, 255, 255, 255), width=14)
d.ellipse((60, 235, 100, 275), fill=(0, 0, 0, 0))
im.save("assets/icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
im.resize((256, 256)).save("assets/icon.png")
