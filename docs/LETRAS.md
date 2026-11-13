# Letras da galeria e do editor de templates

O que se vê num PDF feito pela **galeria** ou pelo **editor de templates** (o texto, nunca os números do bilhete) usa as famílias de `src/core/letras.py`. Um texto escolhe a **primeira** que tem todas as suas letras, por esta ordem:

| # | Família | Letras | Onde está |
|---|---|---|---|
| 1 | **Vera** (Bitstream Vera) | latim básico e pontuação corrente (a que sempre houve; o que já saía em Vera continua igual, byte a byte) | vem com o reportlab |
| 2 | **DejaVu Sans** (Vera alargada, mesmo desenho) | latim estendido (polaco, checo, romeno, turco, catalão…), **vietnamita**, **grego**, **cirílico** (russo, ucraniano…) | `src/core/fontes/DejaVuSans*.ttf` (licença livre, `LICENCA-DejaVu.txt`) |
| 3 | **Noto Sans SC / JP / KR** | **chinês simplificado** (GB 2312), **japonês** (JIS X 0208), **coreano** (KS X 1001), mais latim estendido, grego e cirílico | `src/core/fontes/NotoSans*.ttf` (SIL OFL, `LICENCA-NotoSans.txt`) |

## Regras
- **Uma família por texto:** não se misturam famílias na mesma linha. As Noto têm também latim, grego e cirílico, por isso «日本語 Рифа» serve; «日本語 हिन्दी» não.
- **Os números do bilhete** (`0001`) são sempre os algarismos Vera/VeraBd: o motor reconhece-os pelo ficheiro dos algarismos 0-9 que acompanha o template.
- **As Noto só têm o peso normal:** o «negrito» usa o mesmo desenho. O chinês simplificado só cobre os 6 763 carateres do GB 2312 (o tradicional cai no japonês, que tem muitas formas tradicionais; o que faltar dá aviso).
- **Não há** hindi/devanágari, árabe nem hebraico: precisam de «shaping» (letras que mudam de forma e de ordem conforme as vizinhas) e de escrita da direita para a esquerda, que o reportlab não faz. Um texto com essas letras dá `err_galeria_texto`/`err_editor_letra` («a letra X não existe nas letras disponíveis») em vez de uma imagem estragada. (O DejaVu *tem* as letras árabes e hebraicas, mas só se aceitam os blocos latinos, grego e cirílico.)
- **No browser** (SVG do editor) a Vera e o DejaVu vêm de `/fontes/` e o chinês/japonês/coreano usam as letras do sistema: a pré-visualização pode diferir um pouco do PDF na forma e na largura. O PDF é sempre o que vale.
- **Tamanho:** as quatro letras extra juntam ≈ 8 MB ao repositório (e ao `.exe` da app Windows, que as inclui com `--include-data-dir`).

## Como se regeneram as Noto
Cortadas a partir das Noto Sans variáveis da Google (10–18 MB cada), peso 400, aos carateres de uso corrente:
`uv run --with fonttools python scripts/gerar_fontes.py <pasta com NotoSansSC/JP/KR.ttf> src/core/fontes` (instruções no topo do script).

## Para quem mexe no código
- `letras.familia(texto)` → o nome da família ou `None`; `letras.fonte(texto, negrito)` → o nome registado no reportlab; `letras.em_falta(texto)` → a primeira letra sem família (ou `""`); `letras.largura(...)`.
- Para acrescentar uma família: ficheiro em `src/core/fontes/`, entrada em `FAMILIAS` (a ordem é a prioridade) e o teste em `tests/test_letras.py`. Se a escrita precisar de «shaping», **não** serve (ver acima).
- Texto novo no PDF = escolher a letra com `letras.fonte(...)`, nunca fixar `"Vera"`.
