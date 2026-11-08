"""Reduz as capturas do tutorial do site (`app/assets/ajuda/<lg>_w?.png`, tiradas por `pnpm capturas`) a 256 cores: 28 MB passam a ~6 MB, sem diferença visível
(o octree mantém o preto puro; o *median cut* tornava-o roxo). Idempotente: as que já são de paleta ficam como estão. Corre-se a seguir às capturas."""
from pathlib import Path

from PIL import Image

PASTA = Path(__file__).resolve().parent.parent / "app" / "assets" / "ajuda"


def otimizar(ficheiro: Path) -> tuple[int, int]:
    antes = ficheiro.stat().st_size
    with Image.open(ficheiro) as im:
        if im.mode == "P":
            return antes, antes
        q = im.convert("RGB").quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    q.save(ficheiro, "PNG", optimize=True)
    return antes, ficheiro.stat().st_size


if __name__ == "__main__":
    total = [0, 0]
    for f in sorted(PASTA.glob("*_w?.png")):
        a, d = otimizar(f)
        total[0] += a
        total[1] += d
    print(f"capturas do site: {total[0] / 1e6:.1f} MB -> {total[1] / 1e6:.1f} MB")
