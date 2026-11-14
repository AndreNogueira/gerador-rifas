"""As miniaturas do seletor de templates da galeria (`src/web/frontend/public/galeria/<id>.webp`): cada desenho de `core/galeria.py` com o texto de exemplo.

Estáticas de propósito: o seletor mostra as 24 de uma vez e o servidor não deve desenhar 24 PNG (o motor é um só processo, com fila).
Voltar a correr quando se mexe em `core/galeria.py` (cores, enfeites, desenho da rifa) ou se acrescenta um desenho:

    uv run python scripts/gerar_miniaturas_galeria.py

`tests/test_galeria_miniaturas.py` verifica que cada desenho tem a sua miniatura (e que não sobram ficheiros).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from core import galeria, png_de_pagina  # noqa: E402
from PIL import Image  # noqa: E402

SAIDA = RAIZ / "src" / "web" / "frontend" / "public" / "galeria"
LARGURA = 288      # px: o dobro do que o seletor mostra (144 px), para ecrãs de alta densidade


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    esperados = set()
    total = 0
    for d in galeria.DESENHOS:
        pdf = galeria.criar_template(d.id, galeria.Textos())             # sem texto escrito: sai o de exemplo
        png = png_de_pagina(pdf, 144)                                     # 535 pt a 2 px/pt, depois reduz-se com qualidade
        imagem = Image.open(io.BytesIO(png)).convert("RGB")
        altura = round(imagem.height * LARGURA / imagem.width)
        imagem = imagem.resize((LARGURA, altura), Image.Resampling.LANCZOS)
        destino = SAIDA / f"{d.id}.webp"
        imagem.save(destino, "WEBP", quality=82, method=6)
        esperados.add(destino.name)
        total += destino.stat().st_size
    for velho in SAIDA.glob("*.webp"):
        if velho.name not in esperados:
            velho.unlink()
    print(f"{len(esperados)} miniaturas, {total / 1024:.0f} KB em {SAIDA}")


if __name__ == "__main__":
    main()
