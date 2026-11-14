"""As letras que a galeria e o editor de templates embebem nos PDFs: quais existem, qual serve para cada texto e se alguma falta.

Cada TEXTO escolhe a **primeira** família que tem todas as suas letras, por esta ordem (assim o que já saía em Vera continua igual, byte a byte):
 1. **Vera** (Bitstream Vera, vem com o reportlab): alfabeto latino básico e as pontuações correntes (a que sempre houve);
 2. **DejaVu Sans** (Vera alargada, mesmo desenho): latim estendido (polaco, checo, romeno, turco…), vietnamita, grego e cirílico (russo, ucraniano…);
 3. **Noto Sans SC / JP / KR** (SIL OFL, cortadas aos carateres correntes por `scripts/gerar_fontes.py`): chinês simplificado (GB 2312), japonês (JIS X 0208) e coreano (KS X 1001).
Um texto só usa **uma** família (não se misturam letras de famílias diferentes na mesma linha); as de CJK só têm o peso normal (o «negrito» usa o mesmo).
**Não há** devanágari (hindi), árabe nem hebraico: precisam de «shaping» (letras que mudam de forma e de ordem conforme as vizinhas) que o reportlab não faz; um texto com essas letras
dá o aviso `err_*_letra` em vez de uma imagem estragada. Os números do bilhete são sempre os algarismos Vera (os que o motor reconhece).
"""
from __future__ import annotations

from pathlib import Path

PASTA = Path(__file__).resolve().parent / "fontes"
# (nome, ficheiro normal, nome do negrito, ficheiro do negrito); Vera vem do reportlab, as outras da pasta `fontes/`
FAMILIAS = (
    ("Vera", None, "VeraBd", None),
    ("DejaVu", "DejaVuSans.ttf", "DejaVuBd", "DejaVuSans-Bold.ttf"),
    ("NotoSC", "NotoSansSC.ttf", "NotoSC", "NotoSansSC.ttf"),
    ("NotoJP", "NotoSansJP.ttf", "NotoJP", "NotoSansJP.ttf"),
    ("NotoKR", "NotoSansKR.ttf", "NotoKR", "NotoSansKR.ttf"),
)
_REGISTADAS = False
_COBERTURA: dict[str, frozenset] = {}
# O DejaVu tem muito mais do que o que se sabe desenhar bem (árabe, hebraico, emojis, devanágari…, que pedem «shaping» ou outra direção): só se aceitam os blocos latinos,
# o grego e o cirílico. (A Vera e as Noto já ficam cortadas ao que interessa.)
_BLOCOS_DEJAVU = ((0x20, 0x24F), (0x1E00, 0x1EFF), (0x2000, 0x206F), (0x20A0, 0x20CF), (0x2100, 0x214F), (0x2190, 0x21FF), (0x2200, 0x22FF), (0x25A0, 0x25FF),
                  (0x2600, 0x26FF), (0x2700, 0x27BF), (0x370, 0x3FF), (0x1F00, 0x1FFF), (0x400, 0x52F), (0xA0, 0xFF), (0x2C60, 0x2C7F), (0xA720, 0xA7FF))


def _reportlab_fontes() -> Path:
    import reportlab
    return Path(reportlab.__file__).parent / "fonts"


def registar() -> None:
    """Regista no reportlab todas as famílias (uma vez)."""
    global _REGISTADAS
    if _REGISTADAS:
        return
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    ficheiros = {"Vera": _reportlab_fontes() / "Vera.ttf", "VeraBd": _reportlab_fontes() / "VeraBd.ttf"}
    for nome, normal, negrito, f_negrito in FAMILIAS:
        if normal is not None:
            ficheiros[nome] = PASTA / normal
        if f_negrito is not None and negrito != nome:
            ficheiros[negrito] = PASTA / f_negrito
    for nome, caminho in ficheiros.items():
        if caminho.is_file():
            pdfmetrics.registerFont(TTFont(nome, str(caminho)))
            cobertura = frozenset(pdfmetrics.getFont(nome).face.charToGlyph)
            if nome.startswith("DejaVu"):
                cobertura = frozenset(c for c in cobertura if any(a <= c <= b for a, b in _BLOCOS_DEJAVU))
            _COBERTURA[nome] = cobertura
    _REGISTADAS = True


def _precisa(texto: str) -> set[str]:
    return {c for c in texto if c != " " and c.isprintable()}


def familia(texto: str) -> str | None:
    """O nome (normal) da primeira família que tem todas as letras do texto, ou None se nenhuma tem. Texto sem letras (só espaços): Vera."""
    registar()
    precisa = {ord(c) for c in _precisa(texto)}
    for nome, *_ in FAMILIAS:
        cobertura = _COBERTURA.get(nome)
        if cobertura and precisa <= cobertura:
            return nome
    return None


def fonte(texto: str, negrito: bool = False) -> str:
    """O nome da letra registada com que desenhar `texto` (normal ou negrito). Vera se não houver nenhuma (nunca deve chegar aqui: valida-se antes)."""
    nome = familia(texto) or "Vera"
    for n, _, bold, _ in FAMILIAS:
        if n == nome:
            return bold if negrito else nome
    return "Vera"


def em_falta(texto: str) -> str:
    """A primeira letra do texto que NENHUMA família tem (as que se podem desenhar numa mesma linha), ou «» se o texto serve. Caracteres não imprimíveis contam como em falta."""
    registar()
    if any(c != " " and not c.isprintable() for c in texto):
        return next(c for c in texto if c != " " and not c.isprintable())
    if familia(texto) is not None:
        return ""
    # nenhuma família tem tudo: devolve a letra que mais famílias não têm (a primeira que falha em todas)
    for c in texto:
        if c != " " and not any(ord(c) in cob for cob in _COBERTURA.values()):
            return c
    for c in texto:                                           # cada letra existe nalguma família, mas não juntas (ex.: acentos latinos com chinês)
        if c != " ":
            return c
    return ""


def largura(texto: str, negrito: bool, tamanho: float) -> float:
    """A largura (pt) do texto na letra que o desenha."""
    registar()
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(texto, fonte(texto, negrito), tamanho)
