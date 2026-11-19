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
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from . import galeria, letras, moeda as mod_moeda, precario_catalogo as cat
from .motor import ErroRifas

FORMATOS = {"A5": (419.53, 595.28), "A4": (595.28, 841.89), "A3": (841.89, 1190.55)}      # pt, vertical
ORIENTACOES = ("vertical", "horizontal")
MAX_LINHAS, MAX_TITULO, MAX_SUBTITULO, MAX_RODAPE, MAX_NOME = 80, 40, 70, 120, 40
ESCALA_MAX, ESCALA_MIN, PASSO_ESCALA, MAX_PAGINAS = 1.5, 0.55, 0.05, 5
PASTA_ICONES = Path(__file__).resolve().parent / "icones_precario"
CINZA, CINZA_ESCURO = (0.62, 0.62, 0.62), (0.28, 0.28, 0.28)


@dataclass(frozen=True)
class Linha:
    """Um artigo do catálogo (`artigo`) ou um texto livre (`nome`, com a imagem `emoji` opcional); `preco` em milésimos (`None` = em branco, para escrever à mão)."""
    artigo: str = ""
    nome: str = ""                  # texto livre; num artigo do catálogo, se vier preenchido, ganha ao nome do catálogo (a pessoa corrigiu-o)
    preco: int | None = None
    categoria: str = ""             # só nos textos livres (uma categoria do catálogo); vazio = «Outros»
    emoji: str = ""                 # só nos textos livres: a imagem (um código de `core/icones_precario/`)


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
    moeda: object = field(default_factory=lambda: mod_moeda.MOEDAS["EUR"])      # `Moeda` ou `MoedaInventada`
    lingua: str = "pt"


# ------------------------------------------------------------------ validação
def _texto_ok(texto: str, maximo: int) -> None:
    if len(texto) > maximo:
        raise ErroRifas("err_precario_texto", car=texto[:14] + "…")
    falta = letras.em_falta(texto)
    if falta:
        raise ErroRifas("err_precario_texto", car=falta)


def _nome_da_linha(ln: Linha, lingua: str) -> str:
    if ln.nome.strip():
        return " ".join(ln.nome.split())
    return cat.nome_imprimivel(cat.ARTIGOS[ln.artigo], lingua)


def validar(p: Precario) -> None:
    """Levanta `ErroRifas` (`err_precario_texto`, `err_precario_linhas`) com o que não serve; nada se desenha antes disto."""
    if p.desenho not in galeria.POR_ID or p.formato not in FORMATOS or p.orientacao not in ORIENTACOES or not 0 <= p.colunas <= 3 or p.lingua not in cat.LINGUAS:
        raise ErroRifas("err_precario_texto", car="?")
    if not 1 <= len(p.linhas) <= MAX_LINHAS:
        raise ErroRifas("err_precario_linhas", max=MAX_LINHAS)
    letras.registar()
    for t, m in ((p.titulo, MAX_TITULO), (p.subtitulo, MAX_SUBTITULO), (p.rodape, MAX_RODAPE)):
        _texto_ok(t, m)
    for ln in p.linhas:
        if ln.artigo and ln.artigo not in cat.ARTIGOS:
            raise ErroRifas("err_precario_texto", car="?")
        if not ln.artigo and not ln.nome.strip():
            raise ErroRifas("err_precario_linhas", max=MAX_LINHAS)
        _texto_ok(ln.nome, MAX_NOME)
        if ln.categoria and ln.categoria not in cat.CATEGORIAS:
            raise ErroRifas("err_precario_texto", car="?")
        if ln.emoji and not (PASTA_ICONES / f"{ln.emoji}.png").is_file():
            raise ErroRifas("err_precario_texto", car="?")
        if ln.preco is not None and not 0 <= ln.preco <= mod_moeda.MAX_VALOR:
            raise ErroRifas("err_precario_texto", car="?")
    if isinstance(p.moeda, mod_moeda.MoedaInventada):
        try:
            mod_moeda.validar_inventada(p.moeda)
        except mod_moeda.ErroMoeda:
            raise ErroRifas("err_precario_texto", car=p.moeda.nome[:14]) from None


# ------------------------------------------------------------------ medidas
def _luminancia(rgb) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _misturar(rgb, outro, k: float):
    return tuple(a * (1 - k) + b * k for a, b in zip(rgb, outro, strict=True))


@lru_cache(maxsize=128)
def _imagem(emoji: str):
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    with Image.open(PASTA_ICONES / f"{emoji}.png") as im:
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
        c = cat.ARTIGOS[ln.artigo].categoria if ln.artigo else (ln.categoria or "extras")
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
    for cx in (qx + 14 * f + raio, qx + qw - 14 * f - raio):
        cy = topo - altura / 2 + (6 * f if completo else 0)
        c.setFillColorRGB(*d.papel)
        c.setStrokeColorRGB(*d.destaque)
        c.setLineWidth(2 * f)
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
    negro = (0.12, 0.12, 0.12)
    x_texto = x
    emoji = cat.ARTIGOS[ln.artigo].emoji if ln.artigo else ln.emoji
    if p.imagens and emoji:
        lado = linha_h * 0.92
        c.drawImage(_imagem(emoji), x, y_topo - linha_h / 2 - lado / 2, lado, lado, mask="auto")
        x_texto = x + lado + 8 * f * sf
    elif p.imagens:
        x_texto = x + linha_h * 0.92 + 8 * f * sf
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
        c.setFillColorRGB(*d.principal)
        c.setFont(fonte_preco, tam_preco)
        c.drawRightString(x + largura, base - tam_preco * 0.33, preco)
        ini_pontos, fim_pontos = fim_nome + 6 * f * sf, x + largura - larg_preco - 6 * f * sf
    else:                                                                  # em branco: um traço para escrever o preço à mão
        ini_pontos, fim_pontos = fim_nome + 6 * f * sf, x + largura - larg_preco - 4 * f * sf
        c.setStrokeColorRGB(*CINZA)
        c.setLineWidth(0.9 * f)
        c.line(x + largura - larg_preco, y_txt - 1.5 * f, x + largura, y_txt - 1.5 * f)
    if fim_pontos - ini_pontos > 10:
        c.setStrokeColorRGB(*CINZA)
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
    c.setFillColorRGB(*d.principal)
    c.setFont(letras.fonte(t, True), tam)
    c.drawString(x, y_topo - 15.5 * f * s, t)
    c.setStrokeColorRGB(*d.destaque)
    c.setLineWidth(1.8 * f * s)
    c.line(x, y_topo - 20.5 * f * s, x + largura, y_topo - 20.5 * f * s)


def criar_pdf(p: Precario) -> bytes:
    """O PDF do preçário (1 a 5 páginas). Levanta `ErroRifas` se algo não serve (ver `validar`)."""
    validar(p)
    from reportlab.pdfgen import canvas
    d = galeria.POR_ID[p.desenho]
    larg, alt = FORMATOS[p.formato]
    if p.orientacao == "horizontal":
        larg, alt = alt, larg
    f = min(larg, alt) / 595.28                                           # a letra e as margens seguem o lado menor: A4 deitado = A4 de pé
    max_col = 2 if min(larg, alt) < 500 and larg < alt else 3             # num A5 de pé só cabem duas colunas
    margem = 22 * f
    quadro = (margem, margem, larg - 2 * margem, alt - 2 * margem)
    qx, qy, qw, qh = quadro
    pad = 16 * f
    altura_cab1 = min(max(qh * 0.17, 74 * f), 140 * f) if p.orientacao == "vertical" else min(max(qh * 0.2, 64 * f), 110 * f)
    altura_cab2 = 46 * f
    rodape_h = (34 if p.rodape.strip() else 16) * f + 20 * f
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
        escolhido = escolhido or encaixar(ncol, ESCALA_MIN, MAX_PAGINAS)
    else:
        ncol = min(p.colunas, max_col)
        escolhido = encaixar(ncol, ESCALA_MIN, MAX_PAGINAS)
    if escolhido is None:
        raise ErroRifas("err_precario_linhas", max=MAX_LINHAS)
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
            c.setFillColorRGB(*CINZA_ESCURO)
            c.setFont(letras.fonte(t), tam)
            c.drawCentredString(qx + qw / 2, qy + 30 * f, t)
        if len(paginas) > 1:
            c.setFillColorRGB(*CINZA_ESCURO)
            c.setFont("Vera", 9 * f)
            c.drawRightString(qx + qw - 14 * f, qy + 14 * f, f"{n + 1}/{len(paginas)}")
        c.showPage()
    c.save()
    return saida.getvalue()


def de_ocasiao(ocasiao: str, lingua: str, **campos) -> Precario:
    """Um preçário com os artigos sugeridos de uma ocasião (sem preços: em branco), o desenho e o título dela: o ponto de partida da interface e dos testes."""
    o = cat.OCASIOES[ocasiao]
    visiveis = {a.id for a in cat.artigos_da_lingua(lingua)}
    linhas = tuple(Linha(artigo=a) for a in o.artigos if a in visiveis)
    base = dict(linhas=linhas, titulo=cat.nome_imprimivel(o, lingua), desenho=o.desenho, lingua=lingua, moeda=mod_moeda.moeda_por_omissao(lingua))
    base.update(campos)
    return Precario(**base)
