"""Gera as imagens dos artigos do preçário: o Noto Emoji (Google, curado em `precario_dados.ICONES`) e, para quem já tem Noto, mais alternativas de outras
bibliotecas (Fluent Emoji 3D, Twemoji, OpenMoji — `precario_catalogo.FONTES_EXTRA`), sem trocar nenhuma imagem: `core.precario_catalogo._alternativas_extra`
acrescenta-as sozinho a quem tiver o ficheiro gerado aqui.

Para cada emoji do catálogo (`core/precario_catalogo.py`): descarrega o PNG de 512 px do repositório `googlefonts/noto-emoji`, e grava
- `src/core/icones_precario/<codigo>.png` (256 px, paleta de 256 cores: o que se desenha no PDF; ~10 KB) e
- `src/web/frontend/public/precario/<codigo>.webp` (96 px: as miniaturas da página).

Depois, para os mesmos códigos, tenta cada biblioteca extra (nem todos os códigos têm em todas: fica sem essa alternativa, sem erro), gravando em
`src/core/icones_precario/<fonte>/<codigo>.png` e `.../public/precario/<fonte>/<codigo>.webp`:
- **Fluent Emoji 3D** (`microsoft/fluentui-emoji`, MIT): como a pasta não tem um `emoji_u<codigo>.png` previsível, clona-se só os `metadata.json` (um por
  emoji, ~7 MB) para descobrir que pasta tem cada código Unicode (campo `unicode`) e o caminho exato do PNG 3D (`git ls-tree`, sem descarregar as imagens todas).
- **Twemoji** (`jdecked/twemoji`, gráficos CC BY 4.0): os ficheiros já são nomeados pelo código Unicode (como o Noto), mas só há SVG (ou PNG de 72 px,
  pequeno de mais para o PDF): rasteriza-se a 256/96 px com `resvg_py`.
- **OpenMoji** (`hfg-gmuend/openmoji`, CC BY-SA 4.0): nomeados pelo código Unicode em MAIÚSCULAS, já em PNG de 618 px (não precisa de rasterizar).

Corre-se à mão quando se acrescenta um artigo com um emoji novo: `uv run --with pillow --with resvg-py python scripts/gerar_icones_precario.py [pasta_de_cache]`
(precisa de rede e `git`; as imagens ficam no repositório).
"""
from __future__ import annotations

import io
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

TWEMOJI_SVG = "https://raw.githubusercontent.com/jdecked/twemoji/main/assets/svg/{codigo}.svg"
TWEMOJI_LICENCA = "https://raw.githubusercontent.com/jdecked/twemoji/main/LICENSE-GRAPHICS"
TWEMOJI_COPYRIGHT = "https://raw.githubusercontent.com/jdecked/twemoji/main/LICENSE"      # so tem os nomes dos autores (o LICENSE-GRAPHICS e so o texto legal da CC BY, sem nomes)

OPENMOJI_PNG = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/618x618/{codigo}.png"
OPENMOJI_LICENCA = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/LICENSE.txt"


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


def _rasterizar_centrado(svg: str, lado: int):
    """resvg_py mantém a proporção do SVG dentro de `lado` x `lado` (não estica): algumas emoji do Twemoji não são
    quadradas (ex. a fatia de melancia), por isso centra-se o resultado num quadrado transparente desse tamanho."""
    import resvg_py
    im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=lado, height=lado)))).convert("RGBA")
    if im.size == (lado, lado):
        return im
    quadro = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    quadro.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2), im)
    return quadro


def gerar_twemoji(cache: Path, codigos: set) -> int:
    """Twemoji (`jdecked/twemoji`, fork mantido do antigo `twitter/twemoji`): ficheiros nomeados pelo código Unicode
    (minúsculas, como o Noto), mas só em SVG (ou PNG de 72 px, pequeno de mais para o PDF): rasteriza-se com `resvg_py`
    a 256 px. Gráficos sob CC BY 4.0 (o código do repositório é MIT; o `LICENSE-GRAPHICS` à parte é que vale aqui)."""
    pasta_pdf, pasta_web = PASTA_PDF / "twemoji", PASTA_WEB / "twemoji"
    pasta_pdf.mkdir(parents=True, exist_ok=True)
    pasta_web.mkdir(parents=True, exist_ok=True)
    feitos, faltam = 0, []
    for codigo in sorted(codigos):
        bruto = cache / "twemoji-svg" / f"{codigo}.svg"
        bruto.parent.mkdir(parents=True, exist_ok=True)
        try:
            descarregar(TWEMOJI_SVG.format(codigo=codigo), bruto)
        except urllib.error.URLError as e:
            faltam.append((codigo, str(e)))
            continue
        svg = bruto.read_text(encoding="utf-8")
        grande = _rasterizar_centrado(svg, 256)
        grande.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(pasta_pdf / f"{codigo}.png", optimize=True)
        pequena = _rasterizar_centrado(svg, 96)
        pequena.save(pasta_web / f"{codigo}.webp", quality=82, method=6)
        feitos += 1
    descarregar(TWEMOJI_LICENCA, cache / "LICENSE-GRAPHICS")
    descarregar(TWEMOJI_COPYRIGHT, cache / "LICENSE")
    autores = "\n".join(li for li in (cache / "LICENSE").read_text(encoding="utf-8").splitlines() if li.startswith("Copyright"))
    (pasta_pdf / "LICENSE.txt").write_text(
        "As imagens desta pasta são do projeto Twemoji (https://github.com/jdecked/twemoji), rasterizadas a partir do SVG e com paleta reduzida.\n"
        f"{autores}\n"
        "Os gráficos estão sob a licença CC BY 4.0 (copiada abaixo; o ficheiro LICENSE-GRAPHICS do repositório não tem os nomes dos autores, só o texto "
        "legal — vêm do ficheiro LICENSE, que é do código, mas é onde o projeto os regista): exige atribuição, que o site e o PDF dão (ver "
        "`core.precario_catalogo.texto_creditos`).\n\n" + (cache / "LICENSE-GRAPHICS").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{feitos} de {len(codigos)} códigos têm Twemoji (os outros ficam só com o Noto)")
    for c, e in faltam:
        print("FALTA (twemoji)", c, e)
    return 0


def gerar_openmoji(cache: Path, codigos: set) -> int:
    """OpenMoji (`hfg-gmuend/openmoji`): ficheiros nomeados pelo código Unicode em MAIÚSCULAS (ao contrário do Noto/
    Twemoji), já em PNG de 618 px (não precisa de rasterizar). Licença CC BY-SA 4.0: exige atribuição e partilha-igual
    (as imagens adaptadas aqui — redimensionadas — continuam disponíveis nos mesmos termos)."""
    pasta_pdf, pasta_web = PASTA_PDF / "openmoji", PASTA_WEB / "openmoji"
    pasta_pdf.mkdir(parents=True, exist_ok=True)
    pasta_web.mkdir(parents=True, exist_ok=True)
    feitos, faltam = 0, []
    for codigo in sorted(codigos):
        bruto = cache / "openmoji-618" / f"{codigo}.png"
        bruto.parent.mkdir(parents=True, exist_ok=True)
        try:
            descarregar(OPENMOJI_PNG.format(codigo=codigo.upper()), bruto)
        except urllib.error.URLError as e:
            faltam.append((codigo, str(e)))
            continue
        with Image.open(bruto) as im:
            im = im.convert("RGBA")
            im.resize((256, 256), Image.LANCZOS).quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(pasta_pdf / f"{codigo}.png", optimize=True)
            im.resize((96, 96), Image.LANCZOS).save(pasta_web / f"{codigo}.webp", quality=82, method=6)
        feitos += 1
    descarregar(OPENMOJI_LICENCA, cache / "LICENSE.txt")
    (pasta_pdf / "LICENSE.txt").write_text(
        "As imagens desta pasta são do projeto OpenMoji (https://openmoji.org, https://github.com/hfg-gmuend/openmoji), redimensionadas e com paleta "
        "reduzida.\nA licença é CC BY-SA 4.0 (copiada abaixo): exige atribuição, que o site e o PDF dão (ver `core.precario._creditos`), e partilha-igual "
        "(as imagens adaptadas aqui continuam disponíveis sob a mesma licença).\n\n"
        + (cache / "LICENSE.txt").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{feitos} de {len(codigos)} códigos têm OpenMoji (os outros ficam só com o Noto)")
    for c, e in faltam:
        print("FALTA (openmoji)", c, e)
    return 0


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
    erro_twemoji = gerar_twemoji(cache.parent / "twemoji", set(codigos))
    erro_openmoji = gerar_openmoji(cache.parent / "openmoji", set(codigos))
    return (1 if faltam else 0) or erro_fluent or erro_twemoji or erro_openmoji


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / "noto_emoji_512"))
