"""Gera as letras CJK que o editor e a galeria embebem nos PDFs (`src/core/fontes/NotoSans{SC,JP,KR}.ttf`) a partir das Noto Sans (SIL OFL) da Google.

As Noto Sans CJK completas têm 10-18 MB cada: aqui instancia-se o peso 400 e cortam-se aos carateres de uso corrente (GB 2312 para o chinês simplificado, JIS X 0208 para o
japonês, KS X 1001 para o coreano, mais ASCII e latim estendido (Latin-1 e Extended-A), pontuação e formas de largura inteira), ficando 1-3 MB cada. Só se corre uma vez (o resultado vai para o repositório) e só precisa
de `fonttools`:

    mkdir fontes-noto && cd fontes-noto
    curl -LO "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"     (idem notosansjp, notosanskr)
    uv run --with fonttools python scripts/gerar_fontes.py fontes-noto src/core/fontes

Licença das Noto Sans: SIL Open Font License 1.1 (`src/core/fontes/LICENCA-NotoSans.txt`).
"""
from __future__ import annotations

import sys
from pathlib import Path

ASCII = {chr(c) for c in range(0x20, 0x7F)} | {chr(c) for c in range(0xA0, 0x180)}     # ASCII, Latin-1 e Latin Extended-A: um texto chines com «São» ou «é» tem de caber na mesma familia
PONTUACAO = {chr(c) for c in range(0x2000, 0x2070)} | {chr(c) for c in range(0x3000, 0x3040)} | {chr(c) for c in range(0xFF00, 0xFFF0)} | set("°×÷±€£¥©®™·•…«»")


def _de_codec(codec: str, altos: range, baixos: range) -> set[str]:
    out = set()
    for a in altos:
        for b in baixos:
            try:
                out.add(bytes([a, b]).decode(codec))
            except UnicodeDecodeError:
                pass
    return out


CONJUNTOS = {
    "NotoSansSC": _de_codec("gb2312", range(0xA1, 0xF8), range(0xA1, 0xFF)),
    "NotoSansJP": _de_codec("euc_jp", range(0xA1, 0xFF), range(0xA1, 0xFF)),
    "NotoSansKR": _de_codec("euc_kr", range(0xA1, 0xFF), range(0xA1, 0xFF)),
}


def gerar(origem: Path, destino: Path) -> None:
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for nome, chars in CONJUNTOS.items():
        f = origem / f"{nome}.ttf"
        fonte = TTFont(f)
        fonte = instancer.instantiateVariableFont(fonte, {"wght": 400})
        op = subset.Options()
        op.layout_features = ["kern", "locl"]
        op.hinting = False
        op.desubroutinize = True
        op.notdef_outline = True
        op.name_IDs = [1, 2, 3, 4, 6]
        s = subset.Subsetter(op)
        s.populate(text="".join(sorted(chars | ASCII | PONTUACAO)))
        s.subset(fonte)
        familia = {"NotoSansSC": "Noto Sans SC", "NotoSansJP": "Noto Sans JP", "NotoSansKR": "Noto Sans KR"}[nome]
        for r in fonte["name"].names:                      # o instanciador deixa os nomes do peso por omissão («Thin»): põem-se os do peso 400
            if r.nameID == 1:
                r.string = familia
            elif r.nameID == 2:
                r.string = "Regular"
            elif r.nameID == 4:
                r.string = familia + " Regular"
            elif r.nameID == 6:
                r.string = nome + "-Regular"
        saida = destino / f"{nome}.ttf"
        fonte.save(saida)
        print(f"{saida.name}: {saida.stat().st_size / 1048576:.2f} MB ({len(chars)} carateres + ASCII)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    gerar(Path(sys.argv[1]), Path(sys.argv[2]))
