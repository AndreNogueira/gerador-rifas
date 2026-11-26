"""As etiquetas (senhas) de levantamento do preçário (`docs/PLANO_PRECARIO.md`): numa festa paga-se num sítio e levanta-se noutro. Cada artigo do preçário vira uma senha com a imagem,
o nome, o preço (opcional) e **onde se levanta** (a zona de cada secção: «Bar», «Cozinha»…); imprimem-se `copias` senhas de cada artigo em folhas A4 (3 × 8) com guias de corte.

- **Combos:** um combo dá uma senha por cada artigo que o compõe, cada uma com a zona da sua secção (a bifana levanta-se na cozinha, a cerveja no bar) e o nome do combo por cima;
  é a ligação entre os combos entre secções e as zonas de levantamento.
- **Zonas:** uma cor por zona (até 8 cores que se distinguem de longe) na faixa de baixo; as senhas saem agrupadas por zona e por artigo para cortar e entregar às equipas.
- **Sem numeração:** as senhas são iguais entre si (fotocopiam-se); para vales numerados e verificáveis, vales de fichas (`core/vales.py`).
Nada se guarda: os textos só entram no PDF. Os mesmos limites de letras do preçário (`core/letras.py`): um texto que o PDF não escreve dá `err_precario_texto`.
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field, replace

from . import i18n, letras, moeda as mod_moeda, precario, precario_catalogo as cat
from .motor import ErroRifas

MAX_COPIAS = 99                   # senhas de cada artigo
MAX_SENHAS = 1200                 # senhas por pedido (50 folhas): cada folha é um PDF mais pesado e mais papel
MAX_ZONA = 20                     # letras do nome de uma zona
COLUNAS, LINHAS = 3, 8            # senhas por folha: 24
MARGEM = 20.0
CORES_ZONA = ((0.12, 0.47, 0.71), (0.84, 0.15, 0.16), (0.17, 0.63, 0.17), (0.58, 0.40, 0.74), (0.89, 0.47, 0.05), (0.09, 0.62, 0.63), (0.55, 0.34, 0.29), (0.35, 0.35, 0.35))
CINZA = (0.45, 0.45, 0.45)


@dataclass(frozen=True)
class Etiquetas:
    precario: precario.Precario
    zonas: dict = field(default_factory=dict)      # id da secção -> nome da zona onde se levanta (vazio = sem zona)
    copias: int = 10                                # senhas de cada artigo (1 a `MAX_COPIAS`)
    preco: bool = True                              # mostrar o preço na senha


@dataclass(frozen=True)
class Senha:
    nome: str
    emoji: str = ""
    foto: bytes = b""
    preco: int | None = None
    zona: str = ""
    menu: str = ""                                  # o nome do combo de que esta senha faz parte (vazio = artigo avulso)


def _zona_de(e: Etiquetas, categoria: str) -> str:
    return " ".join(str(e.zonas.get(categoria, "")).split())


def validar(e: Etiquetas) -> None:
    """Levanta `ErroRifas` (`err_etiquetas`, `err_etiquetas_limite`, e as do preçário) com o que não serve; nada se desenha antes disto."""
    precario.validar(e.precario)
    if not isinstance(e.copias, int) or isinstance(e.copias, bool) or not 1 <= e.copias <= MAX_COPIAS:
        raise ErroRifas("err_etiquetas", max=MAX_COPIAS)
    if not isinstance(e.zonas, dict) or len(e.zonas) > len(cat.CATEGORIAS) or any(k not in cat.CATEGORIAS or not isinstance(v, str) for k, v in e.zonas.items()):
        raise ErroRifas("err_etiquetas", max=MAX_COPIAS)
    for v in e.zonas.values():
        precario._texto_ok(" ".join(v.split()), MAX_ZONA)
    if len(senhas(e)) > MAX_SENHAS:
        raise ErroRifas("err_etiquetas_limite", max=MAX_SENHAS)


def _categoria_de(ln: precario.Linha) -> str:
    return cat.ARTIGOS[ln.artigo].categoria if ln.artigo else (ln.categoria or "extras")


def senhas(e: Etiquetas) -> list[Senha]:
    """As senhas pela ordem em que se imprimem: por zona (a ordem em que aparecem nas secções) e, dentro de cada uma, por artigo, com as `copias` de cada artigo seguidas."""
    p = e.precario
    tipos: list[Senha] = []
    for c, linhas in precario._agrupar(p):
        for ln in linhas:
            nome = precario._nome_da_linha(ln, p.lingua)
            if ln.combo:
                for a in ln.combo:
                    art = cat.ARTIGOS[a]
                    tipos.append(Senha(cat.nome_imprimivel(art, p.lingua), art.emoji, b"", None, _zona_de(e, art.categoria), nome))
            else:
                emoji = ln.emoji or (cat.ARTIGOS[ln.artigo].emoji if ln.artigo else "")
                tipos.append(Senha(nome, emoji, ln.foto, ln.preco if e.preco else None, _zona_de(e, c)))
    ordem_zonas: dict[str, int] = {}
    for s in tipos:
        ordem_zonas.setdefault(s.zona, len(ordem_zonas))
    tipos.sort(key=lambda s: ordem_zonas[s.zona])                  # estável: dentro de cada zona, a ordem do preçário
    return [s for s in tipos for _ in range(e.copias)]


def zonas_em_uso(e: Etiquetas) -> list[str]:
    """Os nomes das zonas que as senhas levam, sem repetir, pela ordem das senhas (a legenda de cores)."""
    vistas: list[str] = []
    for s in senhas(e):
        if s.zona and s.zona not in vistas:
            vistas.append(s.zona)
    return vistas


def _rotulo(chave: str, lingua: str, **par) -> str:
    """Um texto fixo da senha na língua do preçário (ou em inglês se o PDF não tem as letras dela)."""
    t = i18n.traduzir(chave, lingua, **par)
    return t if not letras.em_falta(t) else i18n.traduzir(chave, "en", **par)


def _linhas_do_nome(nome: str, negrito: bool, largura: float, max_linhas: int, grande: float, pequeno: float) -> tuple[list[str], float]:
    """O nome partido em até `max_linhas` linhas com a maior letra (entre `grande` e `pequeno`) em que cabe; o que não cabe corta-se com «…»."""
    tam = grande
    while True:
        palavras, linhas, atual = nome.split(), [], ""
        for w in palavras:
            teste = f"{atual} {w}".strip()
            if letras.largura(teste, negrito, tam) <= largura or not atual:
                atual = teste
            else:
                linhas.append(atual)
                atual = w
        linhas.append(atual)
        if len(linhas) <= max_linhas and all(letras.largura(x, negrito, tam) <= largura for x in linhas):
            return linhas, tam
        if tam <= pequeno:
            break
        tam -= 0.5
    linhas = linhas[:max_linhas]
    linhas[-1] = precario._ajustado(linhas[-1] + "…", negrito, tam, largura, tam)[0]
    return [precario._ajustado(x, negrito, tam, largura, tam)[0] for x in linhas], tam


def _senha(c, e: Etiquetas, d, s: Senha, x: float, y: float, w: float, h: float, cor_zona) -> None:
    """Uma senha com o canto inferior esquerdo em (x, y): faixa do evento em cima, a imagem e o nome ao meio e a zona de levantamento em baixo."""
    p = e.precario
    lg = p.lingua
    c.setFillColorRGB(*d.papel)
    c.rect(x, y, w, h, stroke=0, fill=1)
    alt_cab, alt_zona = h * 0.2, h * 0.26
    # a faixa de cima: o título do preçário (o do evento)
    c.setFillColorRGB(*d.principal)
    c.rect(x, y + h - alt_cab, w, alt_cab, stroke=0, fill=1)
    titulo = p.titulo.strip()
    if titulo:
        texto_cab = (0.12, 0.12, 0.12) if precario._luminancia(d.principal) >= 0.58 else (1.0, 1.0, 1.0)
        t, tam = precario._ajustado(titulo, True, 10, w - 14, 6)
        c.setFillColorRGB(*texto_cab)
        c.setFont(letras.fonte(t, True), tam)
        c.drawCentredString(x + w / 2, y + h - alt_cab / 2 - tam * 0.33, t)
    # a faixa de baixo: onde se levanta
    base = y
    if s.zona:
        c.setFillColorRGB(*cor_zona)
        c.rect(x, y, w, alt_zona, stroke=0, fill=1)
        texto_zona = (0.12, 0.12, 0.12) if precario._luminancia(cor_zona) >= 0.58 else (1.0, 1.0, 1.0)
        rotulo = f"{_rotulo('web_etiquetas_levantar', lg)}: {s.zona}"
        t, tam = precario._ajustado(rotulo, True, 12, w - 14, 6.5)
        c.setFillColorRGB(*texto_zona)
        c.setFont(letras.fonte(t, True), tam)
        c.drawCentredString(x + w / 2, y + alt_zona / 2 - tam * 0.33, t)
        base = y + alt_zona
    corpo_h = (y + h - alt_cab) - base
    # o corpo: imagem à esquerda, nome (até 2 linhas) e, se houver, o preço
    x0 = x + 9
    lado = min(corpo_h - 10, 46)
    centro_y = base + corpo_h / 2
    if p.imagens and s.foto:
        c.drawImage(precario._foto(s.foto), x0, centro_y - lado / 2, lado, lado, preserveAspectRatio=True, anchor="c", mask="auto")
        x0 += lado + 8
    elif p.imagens and s.emoji:
        c.drawImage(precario._imagem(s.emoji, precario._cor_texto(d)), x0, centro_y - lado / 2, lado, lado, mask="auto")
        x0 += lado + 8
    larg_texto = x + w - 9 - x0
    cor_texto = precario._cor_texto(d)
    linhas, tam = _linhas_do_nome(s.nome, True, larg_texto, 2, 17, 8)
    extra_menu = bool(s.menu)
    preco = mod_moeda.formatar(s.preco, p.moeda, lg) if s.preco is not None else ""
    n_blocos = len(linhas) + (1 if preco else 0) + (1 if extra_menu else 0)
    altura_bloco = len(linhas) * tam * 1.12 + (16 if preco else 0) + (9 if extra_menu else 0)
    y_texto = centro_y + altura_bloco / 2 if n_blocos else centro_y
    if extra_menu:
        t, tam_m = precario._ajustado(f"{_rotulo('web_etiquetas_menu', lg)}: {s.menu}", False, 7.5, larg_texto, 5.5)
        c.setFillColorRGB(*(precario._cor_suave(d)))
        c.setFont(letras.fonte(t), tam_m)
        y_texto -= 7
        c.drawString(x0, y_texto, t)
        y_texto -= 2
    c.setFillColorRGB(*cor_texto)
    for ln in linhas:
        y_texto -= tam * 1.0
        c.setFont(letras.fonte(ln, True), tam)
        c.drawString(x0, y_texto, ln)
        y_texto -= tam * 0.12
    if preco:
        c.setFillColorRGB(*precario._cor_realce(d))
        c.setFont(letras.fonte(preco, True), 11.5)
        c.drawString(x0, y_texto - 13.5, preco)


def criar_pdf(e: Etiquetas) -> bytes:
    """O PDF das etiquetas (folhas A4 com 3 × 8 senhas e guias de corte). Levanta `ErroRifas` se algo não serve (ver `validar`)."""
    validar(e)
    from reportlab.pdfgen import canvas
    d = precario._desenho(e.precario)
    todas = senhas(e)
    zonas = zonas_em_uso(e)
    larg, alt = precario.FORMATOS["A4"]
    w, h = (larg - 2 * MARGEM) / COLUNAS, (alt - 2 * MARGEM) / LINHAS
    por_folha = COLUNAS * LINHAS
    creditos = cat.texto_creditos(cat.fontes_usadas(s.emoji for s in todas if s.emoji), e.precario.lingua)
    saida = io.BytesIO()
    c = canvas.Canvas(saida, pagesize=(larg, alt), pageCompression=1, invariant=1)
    c.setTitle((e.precario.titulo.strip() or "Etiquetas") + " (etiquetas)")
    for inicio in range(0, len(todas), por_folha):
        for k, s in enumerate(todas[inicio:inicio + por_folha]):
            col, lin = k % COLUNAS, k // COLUNAS
            cor = CORES_ZONA[zonas.index(s.zona) % len(CORES_ZONA)] if s.zona else CINZA
            _senha(c, e, d, s, MARGEM + col * w, alt - MARGEM - (lin + 1) * h, w, h, cor)
        c.setStrokeColorRGB(0.55, 0.55, 0.55)                                  # as guias de corte, a tracejado, por cima de tudo
        c.setLineWidth(0.5)
        c.setDash(4, 3)
        for i in range(COLUNAS + 1):
            c.line(MARGEM + i * w, MARGEM - 6, MARGEM + i * w, alt - MARGEM + 6)
        for j in range(LINHAS + 1):
            c.line(MARGEM - 6, MARGEM + j * h, larg - MARGEM + 6, MARGEM + j * h)
        c.setDash()
        if creditos:
            c.setFillColorRGB(*CINZA)
            c.setFont("Vera", 5.5)
            c.drawString(MARGEM - 6, 4, creditos)
        c.showPage()
    c.save()
    return saida.getvalue()


# ------------------------------------------------------------------ de dicionários (a API e a app Windows)
def de_dict(d: dict, lingua: str | None = None) -> Etiquetas:
    """As etiquetas de um dicionário (JSON): `precario` (o de `core.precario.de_dict`), `zonas` ({secção: nome}), `copias` e `preco`; tipos errados dão `ErroRifas`."""
    if not isinstance(d, dict) or not isinstance(d.get("precario"), dict):
        raise ErroRifas("err_etiquetas", max=MAX_COPIAS)
    copias = d.get("copias", 10)
    zonas = d.get("zonas") or {}
    if isinstance(copias, bool) or not isinstance(copias, int) or not isinstance(zonas, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in zonas.items()):
        raise ErroRifas("err_etiquetas", max=MAX_COPIAS)
    p = replace(precario.de_dict(d["precario"], lingua), formato="A4", orientacao="vertical")          # as senhas têm folha própria: o formato do preçário não conta
    return Etiquetas(p, {k: v for k, v in zonas.items() if v.strip()}, copias, bool(d.get("preco", True)))
