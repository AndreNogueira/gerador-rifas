"""O preçário: o PDF pronto a imprimir (`docs/PLANO_PRECARIO.md`, fase 4). Um cartaz com o desenho de uma ocasião (as cores e os enfeites dos 24 desenhos da galeria), o título,
os artigos por categoria (imagem, nome, pontinhos e preço) e um rodapé; A5, A4 ou A3, vertical ou horizontal, 1 a 3 colunas.

- **Ajuste automático:** com poucos artigos a letra cresce (até 1,5×) e as linhas ocupam a folha; com muitos encolhe até 0,55× e, só se ainda não couber, passa a 2.ª página (até 5), sem
  nunca deixar uma categoria sozinha no fim de uma coluna.
- **Preço em branco** (`preco=None`): a linha leva um traço para escrever à mão; com preço sai na moeda do país ou inventada (`core/moeda.py`).
- **Letras:** cada texto usa uma só família (`core/letras.py`); um texto que o PDF não consegue escrever dá `err_precario_texto` (nunca um PDF estragado). Os nomes do catálogo caem para o inglês.
- **Enfeites:** reaproveitam os da galeria (`galeria._enfeite`, desenhados para uma rifa de 535 × 152 pt) **recortados**: uma faixa por cima do título, outra no rodapé e o ícone do tema, sem copiar código.
Nada se guarda: os textos só entram no PDF.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path

from . import galeria, letras, marca, moeda as mod_moeda, precario_catalogo as cat
from .motor import ErroRifas

CARTOES = "A6x4"                 # cartões de mesa: o preçário em A6 e 4 por folha A4 (2 x 2), com guias de corte
MAX_FOTOS = 20                   # fotos próprias por preçário (cada uma ocupa bytes no PDF)
FOTO_LADO = 192                  # pixéis do lado maior de uma foto depois de reduzida (chega para a linha do preçário, mesmo em A3)
MAX_FOTO_BYTES = 8_000_000       # o ficheiro que se aceita (a app Windows lê-o do disco; o browser já manda uma foto reduzida)
LOGO_LADO = 480                  # pixéis do lado maior do logótipo depois de reduzido (chega para 4 cm a 300 dpi)
MAX_LOGO_BYTES = 2_000_000       # o ficheiro do logótipo que se aceita (como o das rifas, `core.marca`)
LOGO_LUGARES = ("esquerda", "direita", "rodape")      # onde vai o logótipo: no cabeçalho (no lugar de um dos emblemas) ou no rodapé
MIN_COMBO, MAX_COMBO = 2, 4      # artigos de um combo (um «menu»: bifana + bebida, de secções diferentes)
MAX_ROTULO = 10                 # letras de cada rótulo dos tamanhos
MAX_CARTOES = 12                 # artigos que cabem num cartão A6 com letra legível
FORMATOS = {"A5": (419.53, 595.28), "A4": (595.28, 841.89), "A3": (841.89, 1190.55), "A6x4": (297.64, 419.53)}      # pt, vertical (o A6x4 é o tamanho de UM cartão)
ORIENTACOES = ("vertical", "horizontal")
MAX_LINHAS, MAX_TITULO, MAX_SUBTITULO, MAX_RODAPE, MAX_NOME = 80, 40, 70, 120, 40
ESCALA_MAX, ESCALA_MIN, PASSO_ESCALA, MAX_PAGINAS = 1.5, 0.55, 0.05, 5
PASTA_ICONES = Path(__file__).resolve().parent / "icones_precario"


_FONTES = "|".join(re.escape(f) for f in cat.FONTES_EXTRA)
_ID_ICONE = re.compile(rf"(?:(?:{_FONTES}):)?[0-9a-f]{{4,6}}") if _FONTES else re.compile(r"[0-9a-f]{4,6}")


def caminho_icone(id_icone: str) -> Path:
    """O PNG local de um ícone, pelo seu id: um código Noto Emoji sozinho ('1f382') ou `<fonte>:<código>` de outra
    biblioteca ('fluent:1f382', numa subpasta: o ':' não é válido num nome de ficheiro do Windows). Um id que não
    bata certo com este formato (nunca deveria acontecer: tudo o que chega aqui já passou por `_EMOJI`/`_alternativas_extra`
    ou por `validar`) devolve um caminho que nunca existe, em vez de arriscar escapar de `PASTA_ICONES`."""
    if not _ID_ICONE.fullmatch(id_icone):
        return PASTA_ICONES / "_id_invalido_nao_existe"
    if ":" in id_icone:
        fonte, hexa = id_icone.split(":", 1)
        return PASTA_ICONES / fonte / f"{hexa}.png"
    return PASTA_ICONES / f"{id_icone}.png"
CINZA, CINZA_ESCURO = (0.62, 0.62, 0.62), (0.28, 0.28, 0.28)


@dataclass(frozen=True)
class Linha:
    """Um artigo do catálogo (`artigo`) ou um texto livre (`nome`, com a imagem `emoji` opcional); `preco` em milésimos (`None` = em branco, para escrever à mão)."""
    artigo: str = ""
    nome: str = ""                  # texto livre; num artigo do catálogo, se vier preenchido, ganha ao nome do catálogo (a pessoa corrigiu-o)
    preco: int | None = None
    categoria: str = ""             # só nos textos livres (uma categoria do catálogo); vazio = «Outros»
    emoji: str = ""                 # a imagem (um código de `core/icones_precario/`): num texto livre, qualquer uma; num artigo do catálogo, uma das suas `icones` (vazio = a de omissão)
    preco2: int | None = None       # o segundo preço (o tamanho grande, o «menu»…) quando `Precario.tamanhos` está ligado; em milésimos
    foto: bytes = b""                # a foto própria do artigo (PNG ou JPG já reduzidos por `foto_de_bytes`); nunca vai para o ficheiro `.precario` nem para a ligação partilhada
    combo: tuple = ()               # um combo: 2 a 4 ids de artigos do catálogo (de qualquer secção) com um só preço; o nome é o de `nome` ou os dos artigos unidos por « + »; vai sempre para «Menus e combos»


@dataclass(frozen=True)
class Precario:
    linhas: tuple = ()
    titulo: str = ""
    subtitulo: str = ""
    rodape: str = ""
    desenho: str = "quermesse"      # um id de `core.galeria.POR_ID`
    formato: str = "A4"
    orientacao: str = "vertical"
    colunas: int = 0                # 0 = automático (as menos colunas com que a letra fica legível numa folha), 1, 2 ou 3
    imagens: bool = True
    tamanhos: bool = False          # dois preços por artigo (por omissão «P» e «G»): duas colunas de preços com os rótulos por cima
    rotulos: tuple = ("P", "G")      # os rótulos curtos das duas colunas (até `MAX_ROTULO` letras)
    cores: tuple = ("", "", "")      # `#RRGGBB` que mudam a cor principal, a de destaque e a do papel do desenho; vazio = a do desenho
    logo: bytes = b""                # o logótipo (PNG ou JPG já reduzidos por `logo_de_bytes`); nunca vai para o ficheiro `.precario` nem para a ligação partilhada
    logo_lugar: str = "esquerda"     # um de `LOGO_LUGARES`
    moeda: object = field(default_factory=lambda: mod_moeda.MOEDAS["EUR"])      # `Moeda` ou `MoedaInventada`
    lingua: str = "pt"


# ------------------------------------------------------------------ validação
def _texto_ok(texto: str, maximo: int) -> None:
    if len(texto) > maximo:
        raise ErroRifas("err_precario_texto", car=texto[:14] + "…")
    falta = letras.em_falta(texto)
    if falta:
        raise ErroRifas("err_precario_texto", car=falta)


def nome_do_combo(combo: tuple, lingua: str) -> str:
    """O nome de um combo sem nome próprio: os dos artigos unidos por « + » («Bifana + Cerveja»)."""
    return " + ".join(cat.nome_imprimivel(cat.ARTIGOS[a], lingua) for a in combo)


def _nome_da_linha(ln: Linha, lingua: str) -> str:
    if ln.nome.strip():
        return " ".join(ln.nome.split())
    if ln.combo:
        return nome_do_combo(ln.combo, lingua)
    return cat.nome_imprimivel(cat.ARTIGOS[ln.artigo], lingua)


def validar(p: Precario) -> None:
    """Levanta `ErroRifas` (`err_precario_texto`, `err_precario_linhas`) com o que não serve; nada se desenha antes disto."""
    if p.desenho not in POR_ID or p.formato not in FORMATOS or p.orientacao not in ORIENTACOES or not 0 <= p.colunas <= 3 or p.lingua not in cat.LINGUAS:
        raise ErroRifas("err_precario_texto", car="?")
    if not 1 <= len(p.linhas) <= (MAX_CARTOES if p.formato == CARTOES else MAX_LINHAS):
        raise ErroRifas("err_precario_linhas", max=MAX_CARTOES if p.formato == CARTOES else MAX_LINHAS)
    letras.registar()
    for t, m in ((p.titulo, MAX_TITULO), (p.subtitulo, MAX_SUBTITULO), (p.rodape, MAX_RODAPE)):
        _texto_ok(t, m)
    if len(p.rotulos) != 2 or not all(isinstance(r, str) for r in p.rotulos):
        raise ErroRifas("err_precario_texto", car="?")
    for r in p.rotulos:
        _texto_ok(r, MAX_ROTULO)
    if p.tamanhos and not all(r.strip() for r in p.rotulos):
        raise ErroRifas("err_precario_texto", car="?")
    if len(p.cores) != 3 or not all(isinstance(c, str) for c in p.cores) or p.logo_lugar not in LOGO_LUGARES:
        raise ErroRifas("err_precario_texto", car="?")
    for c in p.cores:
        marca.cor_de_hex(c)                                                                  # `err_cor` se não é #RRGGBB
    if sum(1 for ln in p.linhas if ln.foto) > MAX_FOTOS:
        raise ErroRifas("err_editor_limite", campo="fotos")
    for ln in p.linhas:
        if ln.artigo and ln.artigo not in cat.ARTIGOS:
            raise ErroRifas("err_precario_texto", car="?")
        if ln.combo and (ln.artigo or not isinstance(ln.combo, tuple) or not MIN_COMBO <= len(ln.combo) <= MAX_COMBO or len(set(ln.combo)) != len(ln.combo)
                         or any(a not in cat.ARTIGOS for a in ln.combo)):
            raise ErroRifas("err_precario_combo", min=MIN_COMBO, max=MAX_COMBO)
        if not ln.artigo and not ln.combo and not ln.nome.strip():
            raise ErroRifas("err_precario_linhas", max=MAX_LINHAS)
        _texto_ok(ln.nome, MAX_NOME)
        if ln.categoria and ln.categoria not in cat.CATEGORIAS:
            raise ErroRifas("err_precario_texto", car="?")
        if ln.emoji and not caminho_icone(ln.emoji).is_file():
            raise ErroRifas("err_precario_texto", car="?")
        if ln.artigo and ln.emoji and ln.emoji not in cat.ARTIGOS[ln.artigo].icones:       # um artigo só aceita as imagens que o catálogo lhe oferece
            raise ErroRifas("err_precario_texto", car="?")
        if ln.preco is not None and not 0 <= ln.preco <= mod_moeda.MAX_VALOR:
            raise ErroRifas("err_precario_texto", car="?")
    if isinstance(p.moeda, mod_moeda.MoedaInventada):
        try:
            mod_moeda.validar_inventada(p.moeda)
        except mod_moeda.ErroMoeda:
            raise ErroRifas("err_precario_texto", car=p.moeda.nome[:14]) from None


# ------------------------------------------------------------------ o «quadro negro» (um desenho só do preçário)
# Papel verde-escuro como um quadro de escola, moldura de madeira e giz (branco e amarelo). Não está na galeria de rifas: lá os textos são escuros sobre papel claro.
QUADRO = galeria.Desenho("quadro", "Quadro negro", (0.42, 0.28, 0.15), (0.99, 0.86, 0.38), (0.10, 0.19, 0.16), (0.10, 0.19, 0.16), "escola")
DESENHOS = (*galeria.DESENHOS, QUADRO)
POR_ID = {d.id: d for d in DESENHOS}


def desenho_de(id_: str):
    """O desenho (da galeria ou o quadro negro) ou `KeyError`."""
    return POR_ID[id_]


def hex_de(rgb) -> str:
    """Uma cor (r, g, b em 0..1) como `#rrggbb`: o que a interface mostra nos seletores de cor."""
    return "#" + "".join(f"{round(v * 255):02x}" for v in rgb)


def _desenho(p: "Precario"):
    """O desenho de `p` com as cores que a pessoa mudou (principal, destaque, papel); o resto (talão, enfeite) é o do desenho."""
    d = POR_ID[p.desenho]
    principal, destaque, papel = (marca.cor_de_hex(c) for c in p.cores)
    return replace(d, principal=principal or d.principal, destaque=destaque or d.destaque, papel=papel or d.papel)


def _escuro(d) -> bool:
    """Papel escuro: o texto passa a giz claro e os realces a amarelo (num papel claro o texto é quase preto e os realces a cor principal)."""
    return _luminancia(d.papel) < 0.4


def _cor_texto(d):
    return (0.96, 0.96, 0.92) if _escuro(d) else (0.12, 0.12, 0.12)


def _cor_suave(d):
    return (0.62, 0.66, 0.62) if _escuro(d) else CINZA


def _cor_rodape(d):
    return (0.80, 0.82, 0.78) if _escuro(d) else CINZA_ESCURO


def _contraste(a, b) -> float:
    """A razão de contraste (WCAG) entre duas cores (r, g, b em 0..1)."""
    def lum(rgb):
        r, g, b = (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _cor_realce(d):
    """A cor dos preços e dos títulos das categorias: a principal (papel claro) ou a de destaque (papel escuro); com cores escolhidas pela pessoa podia ficar ilegível
    sobre o papel, e então aproxima-se da cor do texto até haver contraste (3:1, o mínimo do WCAG para texto grande e a negrito)."""
    base = d.destaque if _escuro(d) else d.principal
    cor, k = base, 0.0
    while _contraste(cor, d.papel) < 3.0 and k < 1.0:
        k += 0.1
        cor = _misturar(base, _cor_texto(d), k)
    return cor


# ------------------------------------------------------------------ medidas
def _luminancia(rgb) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _misturar(rgb, outro, k: float):
    return tuple(a * (1 - k) + b * k for a, b in zip(rgb, outro, strict=True))


@lru_cache(maxsize=64)
def _foto(dados: bytes):
    from reportlab.lib.utils import ImageReader
    return ImageReader(io.BytesIO(dados))


def _reduzida(bruto: bytes, lado: int, maximo: int, chave: str, **params) -> bytes:
    """Uma imagem pronta para o PDF: só PNG ou JPG a sério (o tipo real, não o nome), reduzida a `lado` px e recodificada (sem EXIF nem nada que não sejam pixéis):
    JPG se não tem transparência, PNG se tem. `ErroRifas(chave)` se não presta."""
    from PIL import Image, ImageOps, UnidentifiedImageError
    if not isinstance(bruto, (bytes, bytearray)) or not 0 < len(bruto) <= maximo:
        raise ErroRifas(chave, **params)
    try:
        with Image.open(io.BytesIO(bytes(bruto))) as im:
            if im.format not in ("PNG", "JPEG") or min(im.size) < 1 or max(im.size) > 12000:
                raise ErroRifas(chave, **params)
            im.load()
            im = ImageOps.exif_transpose(im)
            im.thumbnail((lado, lado), Image.LANCZOS)
            saida = io.BytesIO()
            if im.mode in ("RGBA", "LA", "P") and (im.mode != "P" or "transparency" in im.info):
                im.convert("RGBA").save(saida, "PNG", optimize=True)
            else:
                im.convert("RGB").save(saida, "JPEG", quality=85, optimize=True)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ErroRifas(chave, **params) from None
    return saida.getvalue()


def foto_de_bytes(bruto: bytes) -> bytes:
    """A foto de um artigo pronta para o PDF (`FOTO_LADO` px). `err_editor_imagem` se não presta."""
    return _reduzida(bruto, FOTO_LADO, MAX_FOTO_BYTES, "err_editor_imagem")


def logo_de_bytes(bruto: bytes) -> bytes:
    """O logótipo pronto para o PDF (`LOGO_LADO` px, até 2 MB de ficheiro). `err_logotipo` se não presta."""
    return _reduzida(bruto, LOGO_LADO, MAX_LOGO_BYTES, "err_logotipo", mb=marca.MAX_MB)


def _de_dados(dados, ler, maximo: int, chave: str, **params) -> bytes:
    import base64
    import binascii
    import re
    m = re.fullmatch(r"data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=\s]+)", dados) if isinstance(dados, str) else None
    if not m or len(m.group(2)) > maximo * 4 // 3 + 8:
        raise ErroRifas(chave, **params)
    try:
        return ler(base64.b64decode(m.group(2), validate=False))
    except binascii.Error:
        raise ErroRifas(chave, **params) from None


def foto_de_dados(dados) -> bytes:
    """A foto de um `data:image/png|jpeg;base64,…` (o que o browser envia, já reduzido): ver `foto_de_bytes`."""
    return _de_dados(dados, foto_de_bytes, MAX_FOTO_BYTES, "err_editor_imagem")


def logo_de_dados(dados) -> bytes:
    """O logótipo de um `data:image/png|jpeg;base64,…`: ver `logo_de_bytes`."""
    return _de_dados(dados, logo_de_bytes, MAX_LOGO_BYTES, "err_logotipo", mb=marca.MAX_MB)


@lru_cache(maxsize=128)
def _imagem(emoji: str):
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    with Image.open(caminho_icone(emoji)) as im:
        return ImageReader(im.convert("RGBA"))


def _ajustado(texto: str, negrito: bool, tamanho: float, maximo: float, minimo: float) -> tuple[str, float]:
    """O texto e o tamanho com que cabe em `maximo` pt: encolhe até `minimo` e, se ainda não cabe, corta com «…»."""
    while tamanho > minimo and letras.largura(texto, negrito, tamanho) > maximo:
        tamanho -= 0.25
    if letras.largura(texto, negrito, tamanho) <= maximo:
        return texto, tamanho
    corte = texto
    while len(corte) > 1 and letras.largura(corte + "…", negrito, tamanho) > maximo:
        corte = corte[:-1]
    return corte.rstrip() + "…", tamanho


@dataclass
class _Bloco:
    tipo: str                       # "cat" | "item"
    altura: float                   # já na escala
    antes: float = 0.0              # o respiro antes do bloco (não conta no topo de uma coluna)
    cat: str = ""
    linha: Linha | None = None


def _altura_col(col: list) -> float:
    return sum(b.altura for b in col) + sum(b.antes for b in col[1:])


def _agrupar(p: Precario) -> list[tuple[str, list[Linha]]]:
    """As linhas por categoria, pela ordem do catálogo (dentro de cada uma, a ordem em que vieram); texto livre sem categoria vai para «Outros»."""
    por_cat: dict[str, list[Linha]] = {c: [] for c in cat.CATEGORIAS}
    for ln in p.linhas:
        c = "menus" if ln.combo else cat.ARTIGOS[ln.artigo].categoria if ln.artigo else (ln.categoria or "extras")
        por_cat[c].append(ln)
    return [(c, ls) for c, ls in por_cat.items() if ls]


def _blocos(p: Precario, s: float, f: float) -> list[_Bloco]:
    linha_h = (31 if p.imagens else 19.5) * f * s
    cat_h = 24 * f * s
    saida = []
    for c, ls in _agrupar(p):
        saida.append(_Bloco("cat", cat_h + 4 * f * s, antes=9 * f * s, cat=c))
        saida += [_Bloco("item", linha_h + 4.5 * f * s, linha=ln) for ln in ls]
    return saida


def _paginar(blocos: list[_Bloco], ncol: int, alturas: list[float]) -> list[list[list[_Bloco]]]:
    """Reparte os blocos por páginas e colunas (`alturas[i]` = altura útil das colunas da página i; a última repete-se). Uma categoria nunca fica sozinha no fim de uma coluna;
    com várias colunas, cada página equilibra-as (não enche a 1.ª e deixa a 2.ª vazia)."""
    paginas: list[list[list[_Bloco]]] = [[[] for _ in range(ncol)]]
    col = 0
    for i, b in enumerate(blocos):
        limite = alturas[min(len(paginas) - 1, len(alturas) - 1)]
        atual = paginas[-1][col]
        seguinte = blocos[i + 1].altura if b.tipo == "cat" and i + 1 < len(blocos) else 0
        precisa = (b.antes if atual else 0) + b.altura + seguinte
        if atual and _altura_col(atual) + precisa > limite:
            col += 1
            if col >= ncol:
                paginas.append([[] for _ in range(ncol)])
                col = 0
        paginas[-1][col].append(b)
    return [_equilibrar(pagina, alturas[min(n, len(alturas) - 1)]) for n, pagina in enumerate(paginas)]


def _equilibrar(colunas: list[list[_Bloco]], limite: float) -> list[list[_Bloco]]:
    """A mesma página com as colunas à altura parecida: a divisão (em 2 ou 3) que dá a coluna mais baixa possível sem passar o limite e sem acabar numa categoria."""
    ncol = len(colunas)
    todos = [b for col in colunas for b in col]
    if ncol == 1 or len(todos) < ncol:
        return colunas

    def valido(partes: list[list[_Bloco]]) -> bool:
        return all(p and p[-1].tipo != "cat" and _altura_col(p) <= limite + 1e-6 for p in partes)

    melhor, melhor_h = colunas, float("inf")
    n = len(todos)
    cortes = ((k,) for k in range(1, n)) if ncol == 2 else ((a, b) for a in range(1, n) for b in range(a + 1, n))
    for corte in cortes:
        pontos = (0, *corte, n)
        partes = [todos[pontos[i]:pontos[i + 1]] for i in range(ncol)]
        if valido(partes):
            h = max(_altura_col(q) for q in partes)
            if h < melhor_h - 1e-6:
                melhor, melhor_h = partes, h
    return melhor


# ------------------------------------------------------------------ enfeites da galeria, recortados
def _recorte(c, x: float, y: float, w: float, h: float) -> None:
    caminho = c.beginPath()
    caminho.rect(x, y, w, h)
    c.clipPath(caminho, stroke=0, fill=0)


def _faixa(c, d, x0: float, x1: float, y: float, topo: bool) -> None:
    """A faixa de enfeite do desenho entre x0 e x1: a de cima (`galeria._enfeite` desenha-a a yb+h−12) ou a de baixo (yb+3), recortada do resto da rifa."""
    c.saveState()
    if topo:
        origem = x0 - 40 - 74                                # o ícone cai à esquerda de x0 (fora do recorte)
        _recorte(c, x0, y - 12, x1 - x0, 26)
        galeria._enfeite(c, d, origem, y - 140, (x1 - origem) + 156, galeria.ALTURA, origem + 76)
    else:
        origem = x0 - 74
        _recorte(c, x0, y - 3, x1 - x0, 14)
        galeria._enfeite(c, d, origem, y - 3, (x1 - x0) + 74 + 12, galeria.ALTURA, origem + 76)
    c.restoreState()


def _icone(c, d, cx: float, cy: float, escala: float) -> None:
    """O ícone do tema (o que a galeria põe junto ao título), centrado em (cx, cy) e `escala` vezes maior."""
    c.saveState()
    c.translate(cx, cy)
    c.scale(escala, escala)
    c.translate(-cx, -cy)
    _recorte(c, cx - 20, cy - 20, 40, 40)
    bx = cx - 18
    galeria._enfeite(c, d, bx - 76, cy - 119, galeria.LARGURA, galeria.ALTURA, bx)
    c.restoreState()


# ------------------------------------------------------------------ o desenho
def _cabecalho(c, p: Precario, d, quadro, altura: float, f: float, completo: bool) -> None:
    qx, qy, qw, qh = quadro
    topo = qy + qh
    claro = _luminancia(d.principal) >= 0.58
    texto = (0.12, 0.12, 0.12) if claro else (1.0, 1.0, 1.0)
    c.saveState()
    c.setFillColorRGB(*d.principal)
    c.roundRect(qx, topo - altura, qw, altura, 12 * f, stroke=0, fill=1)
    c.rect(qx, topo - altura, qw, altura / 2, stroke=0, fill=1)            # cantos de baixo direitos
    # o ícone do tema, dentro de um emblema claro, de cada lado
    raio = min(altura * 0.34, 30 * f)
    for lado, cx in (("esquerda", qx + 14 * f + raio), ("direita", qx + qw - 14 * f - raio)):
        cy = topo - altura / 2 + (6 * f if completo else 0)
        c.setFillColorRGB(*d.papel)
        c.setStrokeColorRGB(*d.destaque)
        c.setLineWidth(2 * f)
        if p.logo and p.logo_lugar == lado:                                  # o logótipo no lugar do emblema, sobre um quadrado de papel (serve com fundo transparente ou branco)
            c.roundRect(cx - raio, cy - raio, 2 * raio, 2 * raio, 6 * f, stroke=1, fill=1)
            c.drawImage(_foto(p.logo), cx - raio + 3 * f, cy - raio + 3 * f, 2 * raio - 6 * f, 2 * raio - 6 * f, preserveAspectRatio=True, anchor="c", mask="auto")
            continue
        c.circle(cx, cy, raio, stroke=1, fill=1)
        _icone(c, d, cx, cy, raio * 1.25 / 34)
    util = qw - 2 * (28 * f + 2 * raio)
    titulo = p.titulo.strip() or ("" if not completo else "")
    if titulo:
        fonte = letras.fonte(titulo, True)
        t, tam = _ajustado(titulo, True, (36 if completo else 20) * f, util, 11 * f)
        c.setFillColorRGB(*texto)
        c.setFont(fonte, tam)
        yb = topo - altura / 2 - (0.0 if p.subtitulo.strip() and completo else tam * 0.25) + (8 * f if p.subtitulo.strip() and completo else 0)
        c.drawCentredString(qx + qw / 2, yb, t)
        if p.subtitulo.strip() and completo:
            sub, tam2 = _ajustado(p.subtitulo.strip(), False, 14 * f, util, 8 * f)
            c.setFillColorRGB(*_misturar(texto, d.principal, 0.18))
            c.setFont(letras.fonte(sub), tam2)
            c.drawCentredString(qx + qw / 2, yb - tam * 0.62 - 4 * f, sub)
    c.restoreState()
    _faixa(c, d, qx + 12 * f, qx + qw - 12 * f, topo - altura - 11, topo=True)


def _item(c, p: Precario, d, ln: Linha, x: float, y_topo: float, largura: float, f: float, s: float) -> None:
    linha_h = (31 if p.imagens else 19.5) * f * s
    sf = min(s, 1.2)                                                       # o texto cresce menos do que as linhas e as imagens: com poucos artigos não fica desproporcionado
    base = y_topo - linha_h / 2
    nome = _nome_da_linha(ln, p.lingua)
    negro = _cor_texto(d)
    x_texto = x
    emoji = ln.emoji or (cat.ARTIGOS[ln.artigo].emoji if ln.artigo else "")
    if p.imagens and ln.foto:                                              # a foto própria ganha ao ícone do catálogo
        lado = linha_h * 0.92
        c.drawImage(_foto(ln.foto), x, y_topo - linha_h / 2 - lado / 2, lado, lado, preserveAspectRatio=True, anchor="c", mask="auto")
        x_texto = x + lado + 8 * f * sf
    elif p.imagens and ln.combo:                                           # as imagens dos artigos do combo, lado a lado e a sobrepor-se um pouco
        lado = linha_h * 0.92 * 0.75
        passo = min(lado * 0.72, (linha_h * 0.92 * 2.1 - lado) / (len(ln.combo) - 1))
        for i, a in enumerate(ln.combo):
            c.drawImage(_imagem(cat.ARTIGOS[a].emoji), x + i * passo, y_topo - linha_h / 2 - lado / 2, lado, lado, mask="auto")
        x_texto = x + lado + (len(ln.combo) - 1) * passo + 8 * f * sf
    elif p.imagens and emoji:
        lado = linha_h * 0.92
        c.drawImage(_imagem(emoji), x, y_topo - linha_h / 2 - lado / 2, lado, lado, mask="auto")
        x_texto = x + lado + 8 * f * sf
    elif p.imagens:
        x_texto = x + linha_h * 0.92 + 8 * f * sf
    if p.tamanhos:
        _precos_em_colunas(c, p, d, x, x_texto, base, largura, f, s, sf, nome, negro, ln)
        return
    preco = mod_moeda.formatar(ln.preco, p.moeda, p.lingua) if ln.preco is not None else ""
    fonte_preco = letras.fonte(preco, True) if preco else "Vera"
    tam_preco = 13.5 * f * sf
    larg_preco = letras.largura(preco, True, tam_preco) if preco else 46 * f * sf
    cabe = largura - (x_texto - x) - larg_preco - 22 * f * sf
    nome_t, tam_nome = _ajustado(nome, False, 13 * f * sf, max(cabe, 20), 7 * f)
    fonte_nome = letras.fonte(nome_t)
    c.setFillColorRGB(*negro)
    c.setFont(fonte_nome, tam_nome)
    y_txt = base - tam_nome * 0.33
    c.drawString(x_texto, y_txt, nome_t)
    fim_nome = x_texto + letras.largura(nome_t, False, tam_nome)
    if preco:
        c.setFillColorRGB(*_cor_realce(d))
        c.setFont(fonte_preco, tam_preco)
        c.drawRightString(x + largura, base - tam_preco * 0.33, preco)
        ini_pontos, fim_pontos = fim_nome + 6 * f * sf, x + largura - larg_preco - 6 * f * sf
    else:                                                                  # em branco: um traço para escrever o preço à mão
        ini_pontos, fim_pontos = fim_nome + 6 * f * sf, x + largura - larg_preco - 4 * f * sf
        c.setStrokeColorRGB(*_cor_suave(d))
        c.setLineWidth(0.9 * f)
        c.line(x + largura - larg_preco, y_txt - 1.5 * f, x + largura, y_txt - 1.5 * f)
    if fim_pontos - ini_pontos > 10:
        c.setStrokeColorRGB(*_cor_suave(d))
        c.setLineWidth(1.1 * f * sf)
        c.setLineCap(1)
        c.setDash(0.1, 3.4 * f * sf)
        c.line(ini_pontos, y_txt + 1.2 * f * s, fim_pontos, y_txt + 1.2 * f * s)
        c.setDash()
        c.setLineCap(0)


def _largura_coluna(p: Precario, f: float, sf: float) -> float:
    """A largura de uma coluna de preços (com os dois tamanhos): a do preço mais largo de todo o preçário, para as colunas ficarem alinhadas em todas as linhas e categorias."""
    tam = 13.5 * f * sf
    mais = 46 * f * sf
    for ln in p.linhas:
        for v in (ln.preco, ln.preco2):
            if v is not None:
                mais = max(mais, letras.largura(mod_moeda.formatar(v, p.moeda, p.lingua), True, tam))
    return mais


def _x_coluna(p: Precario, x: float, largura: float, f: float, sf: float, i: int) -> float:
    """O fim (o lado direito) da coluna `i` (0 = o primeiro tamanho) dos preços."""
    col = _largura_coluna(p, f, sf)
    return x + largura - (1 - i) * (col + 10 * f * sf)


def _precos_em_colunas(c, p: Precario, d, x: float, x_texto: float, base: float, largura: float, f: float, s: float, sf: float, nome: str, negro, ln: Linha) -> None:
    """Uma linha com dois preços (os dois tamanhos): o nome, os pontos e duas colunas de preços alinhadas à direita; um preço em branco é um traço."""
    tam_preco = 13.5 * f * sf
    col = _largura_coluna(p, f, sf)
    ocupado = 2 * col + 10 * f * sf
    cabe = largura - (x_texto - x) - ocupado - 22 * f * sf
    nome_t, tam_nome = _ajustado(nome, False, 13 * f * sf, max(cabe, 20), 7 * f)
    c.setFillColorRGB(*negro)
    c.setFont(letras.fonte(nome_t), tam_nome)
    y_txt = base - tam_nome * 0.33
    c.drawString(x_texto, y_txt, nome_t)
    fim_nome = x_texto + letras.largura(nome_t, False, tam_nome)
    for i, valor in enumerate((ln.preco, ln.preco2)):
        fim = _x_coluna(p, x, largura, f, sf, i)
        if valor is not None:
            txt = mod_moeda.formatar(valor, p.moeda, p.lingua)
            c.setFillColorRGB(*_cor_realce(d))
            c.setFont(letras.fonte(txt, True), tam_preco)
            c.drawRightString(fim, base - tam_preco * 0.33, txt)
        else:
            c.setStrokeColorRGB(*_cor_suave(d))
            c.setLineWidth(0.9 * f)
            c.line(fim - col, y_txt - 1.5 * f, fim, y_txt - 1.5 * f)
    ini_pontos, fim_pontos = fim_nome + 6 * f * sf, x + largura - ocupado - 6 * f * sf
    if fim_pontos - ini_pontos > 10:
        c.setStrokeColorRGB(*_cor_suave(d))
        c.setLineWidth(1.1 * f * sf)
        c.setLineCap(1)
        c.setDash(0.1, 3.4 * f * sf)
        c.line(ini_pontos, y_txt + 1.2 * f * s, fim_pontos, y_txt + 1.2 * f * s)
        c.setDash()
        c.setLineCap(0)


def _categoria(c, p: Precario, d, categoria: str, x: float, y_topo: float, largura: float, f: float, s: float) -> None:
    nome = cat.nome_imprimivel(cat.CATEGORIAS[categoria], p.lingua)
    sf = min(s, 1.2)
    t, tam = _ajustado(nome, True, 14.5 * f * sf, largura - 10 * f, 8 * f)
    c.setFillColorRGB(*_cor_realce(d))
    c.setFont(letras.fonte(t, True), tam)
    c.drawString(x, y_topo - 15.5 * f * s, t)
    if p.tamanhos:                                                          # os rótulos das duas colunas de preços, por cima delas
        c.setFillColorRGB(*_cor_suave(d))
        for i, r in enumerate(p.rotulos):
            rt, tr = _ajustado(r.strip(), True, 10 * f * sf, _largura_coluna(p, f, sf), 6 * f)
            c.setFont(letras.fonte(rt, True), tr)
            c.drawRightString(_x_coluna(p, x, largura, f, sf, i), y_topo - 15.5 * f * s, rt)
    c.setStrokeColorRGB(*d.destaque)
    c.setLineWidth(1.8 * f * s)
    c.line(x, y_topo - 20.5 * f * s, x + largura, y_topo - 20.5 * f * s)


def criar_pdf(p: Precario) -> bytes:
    """O PDF do preçário (1 a 5 páginas). Levanta `ErroRifas` se algo não serve (ver `validar`)."""
    validar(p)
    from reportlab.pdfgen import canvas
    d = _desenho(p)
    cartoes = p.formato == CARTOES
    larg, alt = FORMATOS[p.formato]
    if p.orientacao == "horizontal" and not cartoes:                       # o cartão de mesa é sempre de pé
        larg, alt = alt, larg
    max_paginas = 1 if cartoes else MAX_PAGINAS                            # um cartão tem uma só face
    f = min(larg, alt) / 595.28                                           # a letra e as margens seguem o lado menor: A4 deitado = A4 de pé
    max_col = 2 if min(larg, alt) < 500 and larg < alt else 3             # num A5 de pé só cabem duas colunas
    margem = 22 * f
    quadro = (margem, margem, larg - 2 * margem, alt - 2 * margem)
    qx, qy, qw, qh = quadro
    pad = 16 * f
    altura_cab1 = min(max(qh * 0.17, 74 * f), 140 * f) if p.orientacao == "vertical" else min(max(qh * 0.2, 64 * f), 110 * f)
    altura_cab2 = 46 * f
    logo_rodape = bool(p.logo) and p.logo_lugar == "rodape"
    rodape_h = (34 if p.rodape.strip() else 16) * f + 20 * f + (34 * f if logo_rodape else 0)
    util_larg = qw - 2 * pad
    gap = 20 * f
    espaco_cab = 22 * f                                                      # a faixa de enfeite que pende do cabeçalho

    def util(cab: float) -> float:
        return qh - cab - espaco_cab - rodape_h - 8 * f

    alturas = [util(altura_cab1), util(altura_cab2)]

    def encaixar(n_colunas: int, escala_min: float, max_paginas: int):
        """(escala, páginas) com a maior letra que cabe em menos páginas, ou None."""
        for n_paginas in range(1, max_paginas + 1):
            esc = ESCALA_MAX if n_colunas < 3 else 1.3
            while esc >= escala_min - 1e-9:
                paginas_ = _paginar(_blocos(p, esc, f), n_colunas, alturas)
                if len(paginas_) <= n_paginas:
                    return esc, paginas_
                esc = round(esc - PASSO_ESCALA, 4)
        return None

    if p.colunas == 0:                                                        # automático: as menos colunas com que a letra fica legível numa só folha
        escolhido, ncol = None, max_col
        for n in range(2 if larg > alt else 1, max_col + 1):
            escolhido = encaixar(n, 0.85, 1)
            if escolhido:
                ncol = n
                break
        escolhido = escolhido or encaixar(ncol, ESCALA_MIN, max_paginas)
    else:
        ncol = min(p.colunas, max_col)
        escolhido = encaixar(ncol, ESCALA_MIN, max_paginas)
    if escolhido is None:
        raise ErroRifas("err_precario_linhas", max=MAX_CARTOES if cartoes else MAX_LINHAS)
    s, paginas = escolhido
    col_larg = (util_larg - gap * (ncol - 1)) / ncol

    saida = io.BytesIO()
    c = canvas.Canvas(saida, pagesize=(larg, alt), pageCompression=1, invariant=1)
    c.setTitle(p.titulo.strip() or "Preçário")
    for n, pagina in enumerate(paginas):
        c.setFillColorRGB(*d.papel)
        c.rect(0, 0, larg, alt, stroke=0, fill=1)
        c.setStrokeColorRGB(*d.principal)
        c.setLineWidth(3 * f)
        c.roundRect(qx, qy, qw, qh, 14 * f, stroke=1, fill=0)
        c.setStrokeColorRGB(*d.destaque)
        c.setLineWidth(0.9 * f)
        c.roundRect(qx + 5 * f, qy + 5 * f, qw - 10 * f, qh - 10 * f, 10 * f, stroke=1, fill=0)
        cab = altura_cab1 if n == 0 else altura_cab2
        _cabecalho(c, p, d, quadro, cab, f, completo=n == 0)                  # depois da moldura fina: a faixa do cabeçalho tapa-a
        topo_corpo = qy + qh - cab - espaco_cab
        h_util = util(cab)
        # o conteúdo, centrado na vertical quando sobra espaço (só se cabe numa página)
        maior = max((_altura_col(col) for col in pagina), default=0)
        folga = max(0.0, (h_util - maior) / 2) if len(paginas) == 1 else 0.0
        for k, coluna in enumerate(pagina):
            x = qx + pad + k * (col_larg + gap)
            y = topo_corpo - folga
            for j, b in enumerate(coluna):
                y -= b.antes if j else 0
                if b.tipo == "cat":
                    _categoria(c, p, d, b.cat, x, y, col_larg, f, s)
                else:
                    _item(c, p, d, b.linha, x, y, col_larg, f, s)
                y -= b.altura
        _faixa(c, d, qx + 12 * f, qx + qw - 12 * f, qy + 9 * f, topo=False)
        if p.rodape.strip():
            t, tam = _ajustado(p.rodape.strip(), False, 10.5 * f, qw - 2 * pad - 60 * f, 6.5 * f)
            c.setFillColorRGB(*_cor_rodape(d))
            c.setFont(letras.fonte(t), tam)
            c.drawCentredString(qx + qw / 2, qy + 30 * f, t)
        if logo_rodape:                                                       # o logótipo centrado em cima do texto do rodapé (ou onde ele estaria)
            y_logo = qy + (44 if p.rodape.strip() else 26) * f
            c.drawImage(_foto(p.logo), qx + qw / 2 - 70 * f, y_logo, 140 * f, 30 * f, preserveAspectRatio=True, anchor="c", mask="auto")
        if len(paginas) > 1:
            c.setFillColorRGB(*_cor_rodape(d))
            c.setFont("Vera", 9 * f)
            c.drawRightString(qx + qw - 14 * f, qy + 14 * f, f"{n + 1}/{len(paginas)}")
        c.showPage()
    c.save()
    return _em_folha_a4(saida.getvalue()) if cartoes else saida.getvalue()


def _em_folha_a4(cartao: bytes) -> bytes:
    """Os cartões de mesa: o cartão A6 repetido 4 vezes numa folha A4 (2 x 2), com guias de corte a tracejado no meio e nas pontas. Só se imprime e corta."""
    from pypdf import PageObject, PdfReader, PdfWriter, Transformation
    from reportlab.pdfgen import canvas
    a4l, a4a = FORMATOS["A4"]
    cl, ca = FORMATOS[CARTOES]
    origem = PdfReader(io.BytesIO(cartao)).pages[0]
    folha = PageObject.create_blank_page(width=a4l, height=a4a)
    for linha in range(2):
        for coluna in range(2):
            folha.merge_transformed_page(origem, Transformation().translate(coluna * cl, (1 - linha) * (a4a / 2) + (a4a / 2 - ca) / 2))
    guias = io.BytesIO()
    g = canvas.Canvas(guias, pagesize=(a4l, a4a), pageCompression=1, invariant=1)
    g.setStrokeColorRGB(0.55, 0.55, 0.55)
    g.setLineWidth(0.5)
    g.setDash(4, 4)
    g.line(a4l / 2, 0, a4l / 2, a4a)
    g.line(0, a4a / 2, a4l, a4a / 2)
    g.save()
    folha.merge_page(PdfReader(io.BytesIO(guias.getvalue())).pages[0])
    saida = io.BytesIO()
    w = PdfWriter()
    w.add_page(folha)
    w.add_metadata({"/Title": "Preçário (cartões de mesa)"})
    w.write(saida)
    return saida.getvalue()


def de_ocasiao(ocasiao: str, lingua: str, **campos) -> Precario:
    """Um preçário com os artigos sugeridos de uma ocasião (sem preços: em branco), o desenho e o título dela: o ponto de partida da interface e dos testes."""
    o = cat.OCASIOES[ocasiao]
    visiveis = {a.id for a in cat.artigos_da_lingua(lingua)}
    linhas = tuple(Linha(artigo=a) for a in o.artigos if a in visiveis)
    base = dict(linhas=linhas, titulo=cat.nome_imprimivel(o, lingua), desenho=o.desenho, lingua=lingua, moeda=mod_moeda.moeda_por_omissao(lingua))
    base.update(campos)
    return Precario(**base)


# ------------------------------------------------------------------ de e para dicionários (a API, o ficheiro `.precario` da app Windows e o rascunho do browser usam o mesmo formato)
def _texto(valor, padrao: str = "") -> str:
    if valor is None:
        return padrao
    if not isinstance(valor, str):
        raise ErroRifas("err_precario_texto", car="?")
    return valor


def _preco(valor, lingua: str) -> int | None:
    """O preço de uma linha: `None`/«» = em branco; um inteiro = milésimos (o formato do ficheiro); um texto = o que a pessoa escreveu («1,5»)."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, bool) or not isinstance(valor, (int, str)):
        raise ErroRifas("err_precario_texto", car="?")
    if isinstance(valor, int):
        return valor
    n = mod_moeda.valor_de_texto(valor, lingua)
    if n is None:
        raise ErroRifas("err_precario_texto", car=valor.strip()[:14] or "?")
    return n


def _rotulos(valor) -> tuple:
    """Os dois rótulos dos tamanhos de um dicionário (lista de 2 textos); sem eles, «P» e «G»."""
    if valor is None:
        return ("P", "G")
    if not isinstance(valor, (list, tuple)) or len(valor) != 2 or any(not isinstance(r, str) for r in valor):
        raise ErroRifas("err_precario_texto", car="?")
    return (valor[0], valor[1])


def _combo(valor) -> tuple:
    """Os ids dos artigos de um combo de um dicionário (lista de textos); sem eles, não é um combo."""
    if valor is None or valor == []:
        return ()
    if not isinstance(valor, (list, tuple)) or any(not isinstance(a, str) for a in valor):
        raise ErroRifas("err_precario_combo", min=MIN_COMBO, max=MAX_COMBO)
    return tuple(valor)


def _cores(valor) -> tuple:
    """As três cores de um dicionário (lista de 3 textos `#RRGGBB` ou vazios); sem elas, as do desenho."""
    if valor is None:
        return ("", "", "")
    if not isinstance(valor, (list, tuple)) or len(valor) != 3 or any(not isinstance(c, str) for c in valor):
        raise ErroRifas("err_precario_texto", car="?")
    return tuple(c.strip() for c in valor)


def de_dict(d: dict, lingua: str | None = None) -> Precario:
    """O `Precario` de um dicionário (JSON): `titulo`, `subtitulo`, `rodape`, `desenho`, `formato`, `orientacao`, `colunas`, `imagens`, `lingua`,
    `moeda` (`{"codigo": "EUR"}` ou `{"nome": "fichas", "antes": false, "decimais": 0}`; sem ela, a do país da língua), `cores` (3 `#RRGGBB`), `logotipo` (um `data:image/…`) com `logo_lugar`,
    e `linhas` (`artigo`, `nome`, `preco`, `categoria`, `emoji`, `combo`).
    Tipos errados e valores impossíveis dão `ErroRifas` (a validação completa é a de `validar`, que `criar_pdf` chama)."""
    if not isinstance(d, dict):
        raise ErroRifas("err_precario_texto", car="?")
    lg = lingua or _texto(d.get("lingua"), "pt")
    m = d.get("moeda") or {}
    if not isinstance(m, dict):
        raise ErroRifas("err_precario_texto", car="?")
    if _texto(m.get("nome")).strip():
        decimais = m.get("decimais", 0)
        if isinstance(decimais, bool) or not isinstance(decimais, int):
            raise ErroRifas("err_precario_texto", car="?")
        moeda_ = mod_moeda.MoedaInventada(_texto(m.get("nome")), bool(m.get("antes", False)), decimais)
    elif _texto(m.get("codigo")).strip():
        try:
            moeda_ = mod_moeda.moeda_de_codigo(m["codigo"])
        except mod_moeda.ErroMoeda:
            raise ErroRifas("err_precario_texto", car=_texto(m.get("codigo"))[:14]) from None
    else:
        moeda_ = mod_moeda.moeda_por_omissao(lg)
    linhas = d.get("linhas") or []
    if not isinstance(linhas, (list, tuple)) or any(not isinstance(x, dict) for x in linhas):
        raise ErroRifas("err_precario_linhas", max=MAX_LINHAS)
    colunas = d.get("colunas", 0)
    if isinstance(colunas, bool) or not isinstance(colunas, int):
        raise ErroRifas("err_precario_texto", car="?")
    return Precario(
        linhas=tuple(Linha(_texto(x.get("artigo")), _texto(x.get("nome")), _preco(x.get("preco"), lg), _texto(x.get("categoria")), _texto(x.get("emoji")), _preco(x.get("preco2"), lg), foto_de_dados(x["foto"]) if x.get("foto") else b"", _combo(x.get("combo"))) for x in linhas),
        titulo=_texto(d.get("titulo")), subtitulo=_texto(d.get("subtitulo")), rodape=_texto(d.get("rodape")), desenho=_texto(d.get("desenho"), "quermesse"),
        formato=_texto(d.get("formato"), "A4"), orientacao=_texto(d.get("orientacao"), "vertical"), colunas=colunas, imagens=bool(d.get("imagens", True)), tamanhos=bool(d.get("tamanhos", False)), rotulos=_rotulos(d.get("rotulos")), moeda=moeda_, lingua=lg,
        cores=_cores(d.get("cores")), logo=logo_de_dados(d["logotipo"]) if d.get("logotipo") else b"", logo_lugar=_texto(d.get("logo_lugar"), "esquerda"))


def para_dict(p: Precario) -> dict:
    """O inverso de `de_dict`, com os preços em milésimos (não dependem da língua): o que se guarda num ficheiro `.precario`."""
    m = ({"nome": p.moeda.nome, "antes": p.moeda.antes, "decimais": p.moeda.decimais} if isinstance(p.moeda, mod_moeda.MoedaInventada) else {"codigo": p.moeda.codigo})
    return {"titulo": p.titulo, "subtitulo": p.subtitulo, "rodape": p.rodape, "desenho": p.desenho, "formato": p.formato, "orientacao": p.orientacao, "colunas": p.colunas,
            "imagens": p.imagens, "tamanhos": p.tamanhos, "rotulos": list(p.rotulos), "cores": list(p.cores), "logo_lugar": p.logo_lugar, "lingua": p.lingua, "moeda": m,
            "linhas": [{"artigo": ln.artigo, "nome": ln.nome, "preco": ln.preco, "preco2": ln.preco2, "categoria": ln.categoria, "emoji": ln.emoji, "combo": list(ln.combo)} for ln in p.linhas]}


# ------------------------------------------------------------------ o ficheiro `.precario` (app Windows): só os campos, nunca o logotipo nem nada do computador
FORMATO_FICHEIRO = "gerador-de-rifas-precario"
VERSAO_FICHEIRO = 1
EXTENSAO = ".precario"
MAX_BYTES = 60_000


def para_bytes(p: Precario) -> bytes:
    """O ficheiro (UTF-8) com o preçário: o mesmo dicionário de `para_dict`, com o formato e a versão."""
    import json
    return (json.dumps({"formato": FORMATO_FICHEIRO, "versao": VERSAO_FICHEIRO, "precario": para_dict(p)}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def de_bytes(dados: bytes, lingua: str | None = None) -> Precario:
    """O preçário de um ficheiro `.precario`. `err_pedido_ficheiro` se não é um ficheiro nosso, é grande demais ou está estragado; os campos validam-se como em `de_dict`."""
    import json
    if not isinstance(dados, (bytes, bytearray)) or len(dados) > MAX_BYTES:
        raise ErroRifas("err_pedido_ficheiro")
    try:
        d = json.loads(bytes(dados).decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError):
        raise ErroRifas("err_pedido_ficheiro") from None
    if not isinstance(d, dict) or d.get("formato") != FORMATO_FICHEIRO or not isinstance(d.get("precario"), dict):
        raise ErroRifas("err_pedido_ficheiro")
    p = de_dict(d["precario"], lingua)
    validar(p)
    return p
