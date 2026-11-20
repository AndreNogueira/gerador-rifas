"""Gera as imagens dos artigos do preçário a partir do Noto Emoji (Google; imagens sob a Apache 2.0 / OFL 1.1, que permitem redistribuir: ver `src/core/icones_precario/LICENSE.txt`).

Para cada emoji do catálogo, o de omissão e as alternativas de cada artigo (`core/precario_catalogo.py`): descarrega o PNG de 512 px do repositório `googlefonts/noto-emoji`, e grava
- `src/core/icones_precario/<codigo>.png` (256 px, paleta de 256 cores: o que se desenha no PDF; ~10 KB) e
- `src/web/frontend/public/precario/<codigo>.webp` (96 px: as miniaturas da página).

Corre-se à mão quando se acrescenta um artigo com um emoji novo: `uv run --with pillow python scripts/gerar_icones_precario.py [pasta_de_cache]` (precisa de rede; as imagens ficam no repositório).
"""
from __future__ import annotations

import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from core import precario_catalogo  # noqa: E402
from PIL import Image  # noqa: E402

ORIGEM = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/png/512/emoji_u{codigo}.png"
LICENCA = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/LICENSE"
PASTA_PDF = RAIZ / "src" / "core" / "icones_precario"
PASTA_WEB = RAIZ / "src" / "web" / "frontend" / "public" / "precario"


def descarregar(url: str, destino: Path) -> None:
    if destino.exists() and destino.stat().st_size > 100:
        return
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "gerador-rifas-icones"}), timeout=60) as r:
        destino.write_bytes(r.read())


def main(cache: Path) -> int:
    PASTA_PDF.mkdir(parents=True, exist_ok=True)
    PASTA_WEB.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    codigos = sorted({e for a in precario_catalogo.ARTIGOS.values() for e in a.icones})    # a de omissão e as alternativas de cada artigo
    faltam = []
    for codigo in codigos:
        bruto = cache / f"{codigo}.png"
        try:
            descarregar(ORIGEM.format(codigo=codigo), bruto)
        except urllib.error.URLError as e:
            faltam.append((codigo, str(e)))
            continue
        with Image.open(bruto) as im:
            im = im.convert("RGBA")
            grande = im.resize((256, 256), Image.LANCZOS).quantize(colors=256, method=Image.Quantize.FASTOCTREE)
            grande.save(PASTA_PDF / f"{codigo}.png", optimize=True)
            im.resize((96, 96), Image.LANCZOS).save(PASTA_WEB / f"{codigo}.webp", quality=82, method=6)
    descarregar(LICENCA, cache / "LICENSE")
    (PASTA_PDF / "LICENSE.txt").write_text(
        "As imagens desta pasta são do projeto Noto Emoji (https://github.com/googlefonts/noto-emoji), Copyright Google LLC, redimensionadas e com paleta reduzida.\n"
        "O README do projeto diz que as imagens estão sob a licença Apache 2.0 e as fontes sob a SIL Open Font License 1.1; o ficheiro LICENSE do repositório (copiado abaixo) é a OFL 1.1.\n"
        "As duas permitem usar e redistribuir as imagens (aqui, dentro dos PDFs e do site).\n\n" + (cache / "LICENSE").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{len(codigos) - len(faltam)} de {len(codigos)} imagens em {PASTA_PDF}")
    for c, e in faltam:
        print("FALTA", c, e)
    return 1 if faltam else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / "noto_emoji_512"))
