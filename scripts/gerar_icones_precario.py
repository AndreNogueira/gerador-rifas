"""Gera as imagens dos artigos do preçário: o Noto Emoji (Google, curado em `precario_dados.ICONES`) e, para quem já tem Noto, também o Fluent Emoji 3D da
Microsoft (MIT, sem troca nenhuma: só mais alternativas — `core.precario_catalogo._alternativas_extra` acrescenta-as sozinho a quem tiver o ficheiro).

Para cada emoji do catálogo (`core/precario_catalogo.py`): descarrega o PNG de 512 px do repositório `googlefonts/noto-emoji`, e grava
- `src/core/icones_precario/<codigo>.png` (256 px, paleta de 256 cores: o que se desenha no PDF; ~10 KB) e
- `src/web/frontend/public/precario/<codigo>.webp` (96 px: as miniaturas da página).

Depois, para os mesmos códigos, tenta o Fluent Emoji 3D (`microsoft/fluentui-emoji`, licença MIT): como a pasta não tem um `emoji_u<codigo>.png` previsível,
clona-se só os `metadata.json` (um por emoji, ~7 MB) para descobrir que pasta tem cada código Unicode (campo `unicode`) e o caminho exato do PNG 3D (`git ls-tree`,
sem descarregar as imagens todas). Grava em `src/core/icones_precario/fluent/<codigo>.png` e `.../public/precario/fluent/<codigo>.webp`; nem todos os códigos
têm Fluent (fica sem alternativa extra, sem erro).

Corre-se à mão quando se acrescenta um artigo com um emoji novo: `uv run --with pillow python scripts/gerar_icones_precario.py [pasta_de_cache]` (precisa de rede
e `git`; as imagens ficam no repositório).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
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

FLUENT_REPO = "https://github.com/microsoft/fluentui-emoji.git"
FLUENT_BRUTO = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/{caminho}"
FLUENT_LICENCA = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/LICENSE"


def descarregar(url: str, destino: Path) -> None:
    if destino.exists() and destino.stat().st_size > 100:
        return
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "gerador-rifas-icones"}), timeout=60) as r:
        destino.write_bytes(r.read())


def _mapa_fluent(cache: Path) -> dict:
    """{código Unicode: caminho do PNG 3D no repositório}, construído a partir dos metadata.json (um clone raso e
    esparso, só esses ficheiros: ~7 MB, sem as imagens). Ignora emoji de várias sequências (famílias, bandeiras…):
    o catálogo só usa códigos de um só carácter."""
    pasta = cache / "fluentui-emoji"
    if not pasta.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", FLUENT_REPO, str(pasta)], check=True)
        subprocess.run(["git", "-C", str(pasta), "sparse-checkout", "set", "--no-cone", "/assets/*/metadata.json"], check=True)
    else:
        subprocess.run(["git", "-C", str(pasta), "fetch", "--depth", "1", "origin", "main"], check=True)
        subprocess.run(["git", "-C", str(pasta), "reset", "--hard", "origin/main"], check=True)
    arvore = subprocess.run(["git", "-C", str(pasta), "ls-tree", "-r", "HEAD", "--name-only"],
                            check=True, capture_output=True, text=True).stdout.splitlines()
    pasta_do_3d = {}       # nome da pasta (ex.: "Birthday cake") -> caminho do PNG 3D
    for linha in arvore:
        m = re.match(r"assets/([^/]+)/3D/(.+\.png)$", linha)
        if m:
            pasta_do_3d[m.group(1)] = linha
    mapa = {}
    for md in (pasta / "assets").glob("*/metadata.json"):
        uni = json.loads(md.read_text(encoding="utf-8")).get("unicode", "").strip().lower()
        if 4 <= len(uni) <= 6 and uni not in mapa and md.parent.name in pasta_do_3d:
            mapa[uni] = pasta_do_3d[md.parent.name]
    return mapa


def gerar_fluent(cache: Path, codigos: set) -> int:
    pasta_pdf, pasta_web = PASTA_PDF / "fluent", PASTA_WEB / "fluent"
    pasta_pdf.mkdir(parents=True, exist_ok=True)
    pasta_web.mkdir(parents=True, exist_ok=True)
    mapa = _mapa_fluent(cache)
    feitos, faltam = 0, []
    for codigo in sorted(codigos):
        caminho = mapa.get(codigo)
        if caminho is None:
            continue
        bruto = cache / "fluentui-emoji-3d" / f"{codigo}.png"
        bruto.parent.mkdir(parents=True, exist_ok=True)
        try:
            descarregar(FLUENT_BRUTO.format(caminho=urllib.parse.quote(caminho)), bruto)
        except urllib.error.URLError as e:
            faltam.append((codigo, str(e)))
            continue
        with Image.open(bruto) as im:
            im = im.convert("RGBA")
            im.resize((256, 256), Image.LANCZOS).quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(pasta_pdf / f"{codigo}.png", optimize=True)
            im.resize((96, 96), Image.LANCZOS).save(pasta_web / f"{codigo}.webp", quality=82, method=6)
        feitos += 1
    descarregar(FLUENT_LICENCA, cache / "LICENSE")
    (pasta_pdf / "LICENSE.txt").write_text(
        "As imagens desta pasta são do projeto Fluent Emoji (https://github.com/microsoft/fluentui-emoji), estilo 3D, Copyright Microsoft Corporation, "
        "redimensionadas e com paleta reduzida.\nO repositório inteiro (incluindo os assets) está sob a licença MIT (copiada abaixo): permite usar, copiar "
        "e redistribuir sem exigir atribuição (dá-se o crédito à mesma, por cortesia).\n\n" + (cache / "LICENSE").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{feitos} de {len(codigos)} códigos têm Fluent Emoji 3D (os outros ficam só com o Noto)")
    for c, e in faltam:
        print("FALTA (fluent)", c, e)
    return 0        # nem todos os codigos tem fluent: isso nao e erro, so os que falharam a descarregar (raro) o seriam


def main(cache: Path) -> int:
    PASTA_PDF.mkdir(parents=True, exist_ok=True)
    PASTA_WEB.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    # a de omissão e as alternativas de cada artigo; sem as que o próprio catálogo já derivou de outra biblioteca
    # (teriam ":" — ver precario_catalogo._alternativas_extra), senão uma 2.ª corrida misturava-as aqui
    codigos = sorted({e for a in precario_catalogo.ARTIGOS.values() for e in a.icones if ":" not in e})
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
    erro_fluent = gerar_fluent(cache.parent / "fluent_emoji_3d", set(codigos))
    return (1 if faltam else 0) or erro_fluent


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / "noto_emoji_512"))
