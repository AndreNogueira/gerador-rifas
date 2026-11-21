"""Motor do Gerador de Rifas (sem interface).

Le um template em PDF (exportado do Canva) com os numeros de exemplo 0001, 0002, ... (um por
bilhete, 2x cada: talao + parte principal), apaga esses numeros e volta a escrever, em cada
pagina, os numeros pedidos.

Se o template tiver UMA so rifa (0001), `Preparado.com_folha(papel, margem)` enche a folha com copias dela (o
maximo que couber, com rotacao de 90 graus se compensar): cada copia e o fundo + os numeros dentro de um
`q <matriz> cm ... Q`, por isso a calibracao e as posicoes dos numeros ficam sempre nas coordenadas do template.

Os algarismos 0-9 TEM de ser fornecidos pelo utilizador:
  - um PDF com o texto 0123456789 (a letra e copiada do proprio PDF -> vetorial), ou
  - uma imagem PNG/JPG (ou um PDF sem texto) com os algarismos 0-9 -> imagem.

Bibliotecas (todas com licenca permissiva): pypdf (BSD-3), pypdfium2 (Apache-2.0/BSD-3, PDFium),
Pillow (HPND). Nada aqui imprime ou termina o programa: os erros sao ErroRifas (chave + parametros,
traduzidos so quando se mostram) e os avisos vao para a funcao `log`.
"""
from __future__ import annotations

import io
import logging
import math
import re
import threading
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

import pypdfium2 as pdfium
from PIL import Image, ImageChops
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DecodedStreamObject, DictionaryObject, FloatObject,
                           IndirectObject, NameObject, NumberObject, RectangleObject)

from . import pdftexto
from .i18n import msg, t, traduzir

logging.getLogger("pypdf").setLevel(logging.CRITICAL)

DIGITOS = "0123456789"
# numero de exemplo: comeca por 0, pelo menos 3 algarismos (0001, 0010, 0100, 00001, ...)
PADRAO_EXEMPLO = re.compile(r"(?<!\d)0\d{2,}(?!\d)")
EXT_IMAGEM = {".png", ".jpg", ".jpeg"}
MAX_DIGITOS = 12
LIMITE_ALTURA_GLIFO = 300      # px; acima disto a imagem dos algarismos e reduzida
DPI_MEDIDA = 800               # resolucao a que se mede a tinta dos numeros de exemplo

Log = Callable[[str], None]


def _sem_log(_: str) -> None:
    pass


class ErroRifas(Exception):
    """Erro com mensagem pronta a mostrar ao utilizador (traduzida ao converter para texto)."""

    def __init__(self, chave: str, **params):
        super().__init__(chave)
        self.chave, self.params = chave, params

    def __str__(self) -> str:
        return t(self.chave, **self.params)

    def em(self, lingua: str) -> str:
        """A mensagem do erro numa lingua escolhida (sem mexer na lingua global)."""
        return traduzir(self.chave, lingua, **self.params)


class Cancelado(ErroRifas):
    def __init__(self):
        super().__init__("cancelado")


class ErroAlgarismos(ErroRifas):
    """O template esta bem mas faltam/falham os algarismos. `info` tem os dados do template."""

    def __init__(self, chave: str, info: "InfoTemplate", **params):
        super().__init__(chave, **params)
        self.info = info


# ------------------------------------------------------------------ geometria
# Eixos do texto em coordenadas da pagina com y PARA BAIXO (origem no canto superior esquerdo da
# MediaBox): u = sentido da escrita, v = "para baixo" da letra. rot e o angulo (anti-horario) da escrita.
EIXOS = {0: ((1, 0), (0, 1)), 90: ((0, -1), (1, 0)), 180: ((-1, 0), (0, -1)), 270: ((0, 1), (-1, 0))}


def _uv(p, rot: int) -> tuple:
    eu, ev = EIXOS[rot]
    return p[0] * eu[0] + p[1] * eu[1], p[0] * ev[0] + p[1] * ev[1]


def _xy(u: float, v: float, rot: int) -> tuple:
    eu, ev = EIXOS[rot]
    return u * eu[0] + v * ev[0], u * eu[1] + v * ev[1]


@dataclass
class Ret:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


@dataclass
class Slot:
    campo: int            # 1 = A ... N
    texto: str            # numero de exemplo, ex.: "0001"
    origem: tuple         # inicio da linha de base (pagina, y para baixo)
    rot: int              # 0, 90 (a subir), 180, 270 (a descer)
    tamanho: float
    cor: tuple            # rgb 0..1
    fonte: str            # nome da fonte no PDF, sem o prefixo AAAAAA+
    avanco: float         # comprimento do numero de exemplo (pt)

    @property
    def vertical(self) -> bool:
        return self.rot in (90, 270)

    def caixa(self, margem: float = 3.0) -> Ret:
        """Retangulo que contem com folga a tinta do numero de exemplo."""
        eu, ev = EIXOS[self.rot]
        pts = []
        for u in (0.0, self.avanco):
            for v in (-1.1 * self.tamanho, 0.4 * self.tamanho):
                pts.append((self.origem[0] + eu[0] * u + ev[0] * v, self.origem[1] + eu[1] * u + ev[1] * v))
        return Ret(min(p[0] for p in pts) - margem, min(p[1] for p in pts) - margem,
                   max(p[0] for p in pts) + margem, max(p[1] for p in pts) + margem)


@dataclass
class InfoTemplate:
    caminho: Path
    slots: list
    n_campos: int         # bilhetes por pagina
    fontes: list          # nomes das fontes usadas nos numeros
    largura: float
    altura: float
    n_paginas: int
    primeiro: str         # ex.: "0001"
    ultimo: str           # ex.: "0005"
    caixa: tuple = (0.0, 0.0, 0.0, 0.0)    # MediaBox (x0, y0, x1, y1) em coordenadas do PDF
    celula: "Ret | None" = None            # so com 1 rifa: a zona da pagina que e a rifa (y para baixo)
    celula_origem: str = "pagina"          # "pagina" | "trim" | "conteudo"
    n_numeros: dict = field(default_factory=dict)   # campo -> quantas vezes o numero aparece (talao + principal = 2)


def limpar_nome_fonte(nome: str) -> str:
    return re.sub(r"^[A-Z]{6}\+", "", nome)


def normalizar(nome: str) -> str:
    return re.sub(r"[^a-z0-9]", "", limpar_nome_fonte(nome).lower())


def _mesma_letra(x: str, y: str) -> bool:      # "Comic Sans MS Regular" ~ "ComicSansMS"
    x, y = normalizar(x), normalizar(y)
    return x == y or x.startswith(y) or y.startswith(x)


def _abrir_leitor(origem) -> PdfReader:
    rd = PdfReader(origem if isinstance(origem, (io.BytesIO,)) else str(origem))
    if rd.is_encrypted:
        rd.decrypt("")
    return rd


def _caixa(pagina) -> tuple:
    mb = pagina.mediabox
    return float(mb.left), float(mb.bottom), float(mb.right), float(mb.top)


def _rot_de(direcao: tuple) -> int:
    return round(math.degrees(math.atan2(direcao[1], direcao[0])) / 90) % 4 * 90


def _slots_de_tokens(tokens: list, caixa: tuple, so_validos: bool = True) -> tuple:
    """Converte tokens em Slots; so os numeros 1..N que aparecem exatamente 2x (talao + principal)."""
    x0, y0, x1, y1 = caixa
    contagem = Counter(int(tk.texto) for tk in tokens)
    n = 0
    while contagem.get(n + 1, 0) == 2:
        n += 1
    if n == 0 and contagem.get(1, 0) == 1 and not contagem.get(2, 0):
        n = 1          # uma so rifa com o numero escrito uma unica vez (sem talao)
    elif n and contagem.get(n + 1, 0):
        raise ErroRifas("err_sequencia", numero=f"{n + 1:04d}", vezes=contagem[n + 1])
    slots, escolhidos = [], []
    for tk in tokens:
        v = int(tk.texto)
        if not 1 <= v <= n:
            continue
        c = tk.corrida
        slots.append(Slot(
            campo=v, texto=tk.texto, origem=(tk.origem[0] - x0, y1 - tk.origem[1]), rot=_rot_de(c.direcao),
            tamanho=c.tamanho, cor=tuple(c.cor) if c.cor else (0.0, 0.0, 0.0),
            fonte=limpar_nome_fonte(c.fonte.nome), avanco=tk.avanco))
        escolhidos.append(tk)
    return slots, escolhidos, [tk.texto for tk in tokens]


def analisar_template(caminho: Path) -> InfoTemplate:
    try:
        rd = _abrir_leitor(caminho)
        n_pag = len(rd.pages)
    except Exception as e:  # ficheiro corrompido, nao e PDF, ...
        raise ErroRifas("err_abrir_template", erro=str(e)) from e
    if n_pag == 0:
        raise ErroRifas("err_sem_paginas")
    pagina = rd.pages[0]
    caixa = _caixa(pagina)
    try:
        ex = pdftexto.Extrator(rd, pagina)
        slots, _, achados = _slots_de_tokens(ex.tokens(PADRAO_EXEMPLO), caixa)
    except ErroRifas:
        raise
    except Exception as e:
        raise ErroRifas("err_abrir_template", erro=str(e)) from e
    if not slots:
        raise ErroRifas("err_sem_exemplos", achados=", ".join(sorted(set(achados))) or t("nenhum"))
    slots.sort(key=lambda s: (s.campo, s.origem[1], s.origem[0]))
    n = max(s.campo for s in slots)
    por_campo = {s.campo: s.texto for s in slots}
    info = InfoTemplate(
        caminho=Path(caminho), slots=slots, n_campos=n, fontes=sorted({s.fonte for s in slots}),
        largura=caixa[2] - caixa[0], altura=caixa[3] - caixa[1], n_paginas=n_pag,
        primeiro=por_campo[1], ultimo=por_campo[n], caixa=caixa,
        n_numeros=dict(Counter(s.campo for s in slots)))
    if n == 1:      # uma so rifa: o programa enche a folha com copias, por isso precisa de saber o tamanho dela
        info.celula, info.celula_origem = _celula_da_rifa(pagina, caixa, Path(caminho))
    return info


def _celula_da_rifa(pagina, caixa: tuple, caminho: Path) -> tuple:
    """Zona da pagina que e a rifa (retangulo, y para baixo) e de onde veio:
    TrimBox do PDF (se for menor que a pagina) > tinta desenhada (se ocupar bem menos que a pagina) > pagina."""
    x0, y0, x1, y1 = caixa
    w, h = x1 - x0, y1 - y0
    inteira = Ret(0.0, 0.0, w, h)
    try:
        tb = pagina.trimbox
        l, b, r, c = float(tb.left), float(tb.bottom), float(tb.right), float(tb.top)
        if max(abs(l - x0), abs(b - y0), abs(r - x1), abs(c - y1)) > 1.0 and r - l > 20 and c - b > 20:
            return Ret(max(l - x0, 0.0), max(y1 - c, 0.0), min(r - x0, w), min(y1 - b, h)), "trim"
    except Exception:
        pass
    try:
        doc = _abrir_pdfium(caminho)
        try:
            pg = doc[0]
            pw, ph = pg.get_size()
            if abs(pw - w) > 1.0 or abs(ph - h) > 1.0:        # o PDFium desenha outra caixa: nao medir
                return inteira, "pagina"
            z = min(2.0, 3000 / max(w, h))
            im = pg.render(scale=z).to_pil().convert("RGB")
        finally:
            doc.close()
    except Exception:
        return inteira, "pagina"
    dif = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L")
    bb = dif.point(lambda v: 255 if v > 12 else 0).getbbox()
    if bb is None:
        return inteira, "pagina"
    pad = 1.5
    r = Ret(max(bb[0] / z - pad, 0.0), max(bb[1] / z - pad, 0.0), min(bb[2] / z + pad, w), min(bb[3] / z + pad, h))
    if r.width >= 0.97 * w and r.height >= 0.97 * h:
        return inteira, "pagina"
    return r, "conteudo"


def criar_fundo(caminho: Path, info: InfoTemplate) -> bytes:
    """PDF de 1 pagina com o template SEM os numeros de exemplo (so os numeros; o resto fica igual)."""
    rd = _abrir_leitor(caminho)
    w = PdfWriter()
    w.add_page(rd.pages[0])
    cp = w.pages[0]
    ex = pdftexto.Extrator(w, cp)
    _, escolhidos, _ = _slots_de_tokens(ex.tokens(PADRAO_EXEMPLO), info.caixa)
    ex.apagar(escolhidos)
    # confirmar
    ex2 = pdftexto.Extrator(w, cp)
    if _slots_de_tokens(ex2.tokens(PADRAO_EXEMPLO), info.caixa)[0]:
        raise ErroRifas("err_apagar")
    saida = io.BytesIO()
    w.write(saida)
    return saida.getvalue()


# ------------------------------------------------------------------ renderizacao (pdfium)
def _abrir_pdfium(origem):
    return pdfium.PdfDocument(origem if isinstance(origem, (bytes, bytearray)) else str(origem))


def _render_recorte(doc, caixa: tuple, rect: Ret, escala: float) -> tuple:
    """Renderiza o retangulo `rect` (pagina, y para baixo) da 1.a pagina. Devolve (imagem RGB, escala x, escala y)."""
    w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
    rect = Ret(max(rect.x0, 0.0), max(rect.y0, 0.0), min(rect.x1, w), min(rect.y1, h))
    bmp = doc[0].render(scale=escala, crop=(rect.x0, h - rect.y1, w - rect.x1, rect.y0))
    im = bmp.to_pil().convert("RGB")
    return im, rect, im.width / rect.width, im.height / rect.height


def imagem_de_pdf(caminho: Path) -> Image.Image:
    doc = _abrir_pdfium(caminho)
    try:
        pg = doc[0]
        w, h = pg.get_size()
        z = min(600 / 72, 9000 / max(w, h))
        return pg.render(scale=z).to_pil().convert("RGB")
    finally:
        doc.close()


def png_de_pagina(pdf, dpi: int, indice: int = 0) -> bytes:
    doc = _abrir_pdfium(pdf)
    try:
        buf = io.BytesIO()
        doc[indice].render(scale=dpi / 72).to_pil().convert("RGB").save(buf, "PNG")
        return buf.getvalue()
    finally:
        doc.close()


# ------------------------------------------------------------------ algarismos como letra (vetorial)
def _f(v: float) -> str:
    return f"{v:.4f}".rstrip("0").rstrip(".") if v else "0"


def _matriz_texto(rot: int, x: float, y: float) -> str:
    """Tm para escrever a `rot` graus (anti-horario) com origem (x, y) em coordenadas do PDF."""
    c, s = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}[rot]
    return f"{c} {s} {-s} {c} {_f(x)} {_f(y)} Tm"


def _origem_pdf(slot: Slot, largura_nova: float, caixa: tuple, dv: float = 0.0) -> tuple:
    """Origem (coordenadas do PDF) do texto novo, centrado na caixa de avanco do numero de exemplo
    (dv = deslocamento da linha de base no sentido "para baixo" da letra)."""
    eu, ev = EIXOS[slot.rot]
    d = slot.avanco / 2 - largura_nova / 2
    x, y = slot.origem[0] + eu[0] * d + ev[0] * dv, slot.origem[1] + eu[1] * d + ev[1] * dv
    return x + caixa[0], caixa[3] - y


def fator_ajuste(slot: Slot, texto: str) -> float:
    """Se o numero novo tem mais algarismos do que o de exemplo, reduz o tamanho para ocupar o mesmo espaco
    (igual em todos os bilhetes, pois todos os numeros tem o mesmo comprimento)."""
    return min(1.0, len(slot.texto) / max(len(texto), 1))


class LetraPDF:
    """Escreve os numeros com uma letra copiada de um PDF (vetorial)."""
    vetorial = True

    def __init__(self, leitor, fonte_ref, codigos: dict, n_bytes: int, larguras: dict, desc: tuple):
        self.leitor, self.fonte_ref = leitor, fonte_ref
        self.codigos, self.n_bytes, self.larguras, self._desc = codigos, n_bytes, larguras, desc

    @property
    def descricao(self) -> str:
        return t(self._desc[0], **self._desc[1])

    def contexto(self, doc: "Documento") -> "_CtxLetra":
        obj = self.fonte_ref.get_object() if isinstance(self.fonte_ref, IndirectObject) else self.fonte_ref
        ref = doc.w._add_object(obj.clone(doc.w))
        doc.fontes[NameObject("/FD")] = ref
        return _CtxLetra(self, doc)


class _CtxLetra:
    def __init__(self, letra: LetraPDF, doc: "Documento"):
        self.l, self.doc = letra, doc

    def ops(self, slot: Slot, texto: str, cor: tuple | None = None) -> str:
        l = self.l
        k = fator_ajuste(slot, texto)
        tam = slot.tamanho * k
        larg = sum(l.larguras[d] for d in texto) / 1000 * tam
        x, y = _origem_pdf(slot, larg, self.doc.caixa, -0.35 * slot.tamanho * (1 - k))   # mantem o centro vertical
        hexa = "".join(l.codigos[d].to_bytes(l.n_bytes, "big").hex() for d in texto)
        r, g, b = cor or slot.cor
        return (f"BT /FD {_f(tam)} Tf {_f(r)} {_f(g)} {_f(b)} rg {_matriz_texto(slot.rot, x, y)} "
                f"<{hexa}> Tj ET\n")


def letra_de_pdf(caminho: Path, nome_pedido: str, log: Log) -> LetraPDF | None:
    """Procura no PDF uma letra com os 10 algarismos e guarda o codigo de cada um. O Canva so embute as
    letras usadas, por isso um PDF com «0123456789» traz a letra completa para os numeros."""
    rd = _abrir_leitor(caminho)
    ex = pdftexto.Extrator(rd, rd.pages[0])
    por_fonte: dict = {}
    for c in ex.corridas:
        d = por_fonte.setdefault(id(c.fonte), {"fonte": c.fonte, "mapa": {}})
        for cod, ch in zip(c.codigos, c.chars):
            if ch in DIGITOS:
                d["mapa"][ch] = cod
    candidatos = [d for d in por_fonte.values() if len(d["mapa"]) == 10]
    if not candidatos:      # sem ToUnicode: aceita uma corrida com 10 codigos diferentes, na ordem 0..9
        for c in ex.corridas:
            if len(c.codigos) == 10 and len(set(c.codigos)) == 10:
                candidatos.append({"fonte": c.fonte, "mapa": {str(i): cod for i, cod in enumerate(c.codigos)}})
                break
    if not candidatos:
        return None
    escolhido = next((d for d in candidatos if _mesma_letra(d["fonte"].nome, nome_pedido)), None)
    if escolhido is None:
        escolhido = candidatos[0]
        log(msg("aviso_letra_diferente", usada=escolhido["fonte"].nome, pedida=nome_pedido))
    f = escolhido["fonte"]
    mapa = escolhido["mapa"]
    return LetraPDF(rd, f.ref if f.ref is not None else f.obj, {d: mapa[d] for d in DIGITOS}, f.n_bytes,
                    {d: f.largura(mapa[d]) for d in DIGITOS},
                    ("desc_letra_pdf", {"nome": f.nome, "pdf": Path(caminho).name}))


# ------------------------------------------------------------------ algarismos como imagem
@dataclass
class Glifo:
    mascara: Image.Image   # cobertura de tinta (L), mesma altura para todos (preserva a linha de base)
    w: int                 # largura da tinta (px)
    topo: float            # inicio da tinta na faixa (px)
    base: float            # fim da tinta na faixa (px)


def mascara_de_imagem(img: Image.Image) -> Image.Image:
    """Cobertura da tinta (0 = fundo, 255 = tinta), seja qual for a cor da imagem."""
    img = img.convert("RGBA")
    alfa = img.getchannel("A")
    if alfa.getextrema()[0] < 250:        # tem transparencia: a tinta e o alfa
        return alfa
    rgb = img.convert("RGB")
    w, h = rgb.size
    cantos = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    fundo = tuple(sorted(c[i] for c in cantos)[1] for i in range(3))
    dif = ImageChops.difference(rgb, Image.new("RGB", rgb.size, fundo))
    r, g, b = dif.split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), b)
    hist = m.histogram()
    tinta = sum(hist[32:])
    if tinta == 0:
        raise ErroRifas("err_img_vazia")
    acc, ref = 0, 255
    for v in range(255, 31, -1):          # referencia = intensidade tipica da tinta
        acc += hist[v]
        if acc >= 0.10 * tinta:
            ref = v
            break
    ref = max(ref, 64)
    piso = 20                              # tira o ruido de JPEG
    return m.point(lambda v: 0 if v <= piso else min(255, int((v - piso) * 255 / max(ref - piso, 1))))


def _segmentar(mascara: Image.Image) -> list:
    """Devolve [(x0, x1)] de cada grupo de tinta (separados por colunas vazias)."""
    w, h = mascara.size
    binaria = mascara.point(lambda v: 255 if v >= 40 else 0)
    runs, ini = [], None
    for x in range(w):
        tem = binaria.crop((x, 0, x + 1, h)).getextrema()[1] > 0
        if tem and ini is None:
            ini = x
        elif not tem and ini is not None:
            runs.append((ini, x))
            ini = None
    if ini is not None:
        runs.append((ini, w))
    if not runs:
        return []
    alturas = []
    for x0, x1 in runs:
        bb = binaria.crop((x0, 0, x1, h)).getbbox()
        alturas.append(bb[3] - bb[1])
    maxh = max(alturas)
    return [r for r, a in zip(runs, alturas) if a >= 0.15 * maxh]   # ignora pontinhos / ruido


def extrair_glifos(mascara: Image.Image) -> list:
    runs = _segmentar(mascara)
    if len(runs) != 10:
        raise ErroRifas("err_img_simbolos", n=len(runs))
    w, h = mascara.size
    binaria = mascara.point(lambda v: 255 if v >= 40 else 0)
    caixas = []
    for x0, x1 in runs:
        bb = binaria.crop((x0, 0, x1, h)).getbbox()
        caixas.append((x0, bb[1], x1, bb[3]))
    y0 = min(c[1] for c in caixas)
    y1 = max(c[3] for c in caixas)
    f = min(1.0, LIMITE_ALTURA_GLIFO / (y1 - y0))
    glifos = []
    for (x0, gy0, x1, gy1) in caixas:
        faixa = mascara.crop((x0, y0, x1, y1))     # mesma faixa vertical -> linha de base preservada
        if f < 1.0:
            faixa = faixa.resize((max(1, round(faixa.width * f)), max(1, round(faixa.height * f))), Image.LANCZOS)
        glifos.append(Glifo(faixa, faixa.width, (gy0 - y0) * f, (gy1 - y0) * f))
    return glifos


def _medir_tinta(doc_orig, doc_branco, caixa: tuple, slot: Slot) -> tuple:
    """(retangulo da tinta do numero de exemplo, [(u_ini, u_fim)] de cada algarismo no sentido da escrita),
    em coordenadas da pagina (y para baixo)."""
    z = DPI_MEDIDA / 72
    area = slot.caixa()
    ia, area, sx, sy = _render_recorte(doc_orig, caixa, area, z)
    ib, _, _, _ = _render_recorte(doc_branco, caixa, area, z)
    dif = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v >= 40 else 0)
    bb = dif.getbbox()
    if bb is None:
        raise ErroRifas("err_medir", texto=slot.texto)
    rect = Ret(area.x0 + bb[0] / sx, area.y0 + bb[1] / sy, area.x0 + bb[2] / sx, area.y0 + bb[3] / sy)
    horiz = slot.rot in (0, 180)
    w, h = dif.size
    runs, ini = [], None
    for k in range(w if horiz else h):
        tem = dif.crop((k, 0, k + 1, h) if horiz else (0, k, w, k + 1)).getextrema()[1] > 0
        if tem and ini is None:
            ini = k
        elif not tem and ini is not None:
            runs.append((ini, k))
            ini = None
    if ini is not None:
        runs.append((ini, w if horiz else h))
    us = []
    for ra, rb in runs:
        if horiz:
            pa, pb = _uv((area.x0 + ra / sx, 0), slot.rot)[0], _uv((area.x0 + rb / sx, 0), slot.rot)[0]
        else:
            pa, pb = _uv((0, area.y0 + ra / sy), slot.rot)[0], _uv((0, area.y0 + rb / sy), slot.rot)[0]
        us.append((min(pa, pb), max(pa, pb)))
    return rect, sorted(us)


@dataclass
class _Calib:
    escala: float      # pt por px da imagem dos algarismos
    topo: float        # inicio da faixa no eixo v (altura da letra)
    centro: float      # centro do numero de exemplo no eixo u (sentido da escrita)
    v_centro: float    # centro vertical da tinta do numero de exemplo (eixo v)
    modelo: str        # "A": margens laterais por algarismo; "B": passo constante (algarismos de largura fixa)
    param: float       # B: passo entre centros dos algarismos (pt)
    margens: tuple = ()  # A: margem lateral de cada algarismo 0-9 (pt); intervalo entre a e b = margem[a] + margem[b]


class GlifosImagem:
    """Escreve os numeros colando a imagem de cada algarismo (tingida com a cor do template)."""
    vetorial = False

    def __init__(self, glifos: list, desc: tuple):
        self.glifos, self._desc = glifos, desc
        self.altura_faixa = glifos[0].mascara.height
        self.calib: dict = {}      # id(slot) -> _Calib

    @property
    def descricao(self) -> str:
        return t(self._desc[0], **self._desc[1])

    # -- calibracao: faz o "0001" desenhado coincidir com o "0001" do template
    def calibrar(self, info: InfoTemplate, template: Path, fundo: bytes, log: Log) -> None:
        d1, d2 = _abrir_pdfium(template), _abrir_pdfium(fundo)
        try:
            medidas, v1_ = [], {}
            for s in info.slots:
                r, runs = _medir_tinta(d1, d2, info.caixa, s)
                us, vs = zip(*(_uv(p, s.rot) for p in ((r.x0, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x1, r.y0))))
                u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
                gs = [self.glifos[int(c)] for c in s.texto]
                topo_min = min(g.topo for g in gs)
                hc = max(g.base for g in gs) - topo_min
                escala = (v1 - v0) / hc
                if (u1 - u0) < sum(g.w for g in gs) * escala - 0.15 * (v1 - v0) * (len(gs) - 1):
                    log(msg("aviso_mais_largos", texto=s.texto))
                v1_[id(s)] = v1
                medidas.append((s, u0, u1, v0, escala, topo_min, hc, runs if len(runs) == len(gs) else None))
        finally:
            d1.close()
            d2.close()

        # modelo de espacamento: que melhor explica as posicoes de cada algarismo no template?
        erro = {"A": 0.0, "B": 0.0}
        for s, u0, u1, v0, escala, topo_min, hc, runs in medidas:
            if not runs or len(runs) < 3:
                continue
            larg = [b - a for a, b in runs]
            d = [((runs[i + 1][0] + runs[i + 1][1]) - (runs[i][0] + runs[i][1])) / 2 for i in range(len(runs) - 1)]
            ink = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
            p, g = sum(d) / len(d), sum(ink) / len(ink)
            erro["B"] += sum((x - p) ** 2 for x in d)
            erro["A"] += sum((d[i] - ((larg[i] + larg[i + 1]) / 2 + g)) ** 2 for i in range(len(d)))
        modelo = "B" if erro["B"] < erro["A"] else "A"

        # modelo A: margem lateral de cada algarismo (minimos quadrados com regularizacao), em px da folha
        obs = []
        for s, u0, u1, v0, escala, topo_min, hc, runs in medidas:
            if runs:
                obs += [(int(s.texto[i]), int(s.texto[i + 1]), (runs[i + 1][0] - runs[i][1]) / escala)
                        for i in range(len(runs) - 1)]
        margem_px = self._ajustar_margens(obs)

        pior_dpi = None
        for s, u0, u1, v0, escala, topo_min, hc, runs in medidas:
            gs = [self.glifos[int(c)] for c in s.texto]
            n = len(gs)
            margens: tuple = ()
            param = 0.0
            if modelo == "B":
                if runs:
                    ctr = [(a + b) / 2 for a, b in runs]
                    param = (ctr[-1] - ctr[0]) / (n - 1)
                    centro = (ctr[0] + ctr[-1]) / 2
                else:
                    param = ((u1 - u0) - (gs[0].w + gs[-1].w) * escala / 2) / (n - 1)
                    centro = (u0 + u1) / 2
            else:
                if obs:
                    margens = tuple(x * escala for x in margem_px)
                else:       # sem medidas por algarismo: intervalo uniforme
                    gap = ((u1 - u0) - sum(g.w for g in gs) * escala) / (n - 1)
                    margens = (gap / 2,) * 10
                # centro da caixa de avanco = centro da tinta corrigido pelas margens do 1.o e ultimo algarismo
                centro = (u0 + u1) / 2 - (margens[int(s.texto[-1])] - margens[int(s.texto[0])]) / 2
            self.calib[id(s)] = _Calib(escala, v0 - escala * topo_min, centro, (v0 + v1_[id(s)]) / 2, modelo,
                                       param, margens)
            dpi = 72 / escala
            pior_dpi = dpi if pior_dpi is None else min(pior_dpi, dpi)
        if pior_dpi is not None:
            log(msg("aviso_dpi_baixo" if pior_dpi < 300 else "info_dpi", dpi=f"{pior_dpi:.0f}"))

    @staticmethod
    def _ajustar_margens(obs: list) -> list:
        """obs = [(a, b, intervalo_px)]: intervalo(a, b) ~ m[a] + m[b]. Devolve m[0..9]."""
        if not obs:
            return [0.0] * 10
        medio = sum(g for _, _, g in obs) / len(obs) / 2
        m, lam = [medio] * 10, 0.3
        for _ in range(200):
            for d in range(10):
                num, den = lam * medio, lam
                for a, b, g in obs:
                    if a == d and b == d:
                        num += 2 * g
                        den += 4
                    elif a == d:
                        num += g - m[b]
                        den += 1
                    elif b == d:
                        num += g - m[a]
                        den += 1
                m[d] = num / den
        return m

    def contexto(self, doc: "Documento") -> "_CtxImagem":
        return _CtxImagem(self, doc)


def _img_xobject(w: PdfWriter, mascara: Image.Image, cor: tuple) -> IndirectObject:
    """Imagem RGB de cor constante com a mascara como transparencia (SMask)."""
    larg, alt = mascara.size
    sm = DecodedStreamObject()
    sm.set_data(mascara.tobytes())
    sm.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Image"),
               NameObject("/Width"): NumberObject(larg), NameObject("/Height"): NumberObject(alt),
               NameObject("/ColorSpace"): NameObject("/DeviceGray"), NameObject("/BitsPerComponent"): NumberObject(8)})
    sm_ref = w._add_object(sm.flate_encode())
    rgb = DecodedStreamObject()
    rgb.set_data(bytes(round(c * 255) for c in cor) * (larg * alt))
    rgb.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Image"),
                NameObject("/Width"): NumberObject(larg), NameObject("/Height"): NumberObject(alt),
                NameObject("/ColorSpace"): NameObject("/DeviceRGB"), NameObject("/BitsPerComponent"): NumberObject(8),
                NameObject("/SMask"): sm_ref})
    return w._add_object(rgb.flate_encode())


def _cm(rect: Ret, rot: int, caixa: tuple) -> str:
    """Matriz PDF que coloca a imagem (quadrado unitario) em `rect` (pagina, y para baixo), rodada `rot` graus
    no sentido anti-horario."""
    w, h = rect.width, rect.height
    x0, x1 = rect.x0 + caixa[0], rect.x1 + caixa[0]
    yb, yt = caixa[3] - rect.y1, caixa[3] - rect.y0          # y do PDF (para cima): base e topo do retangulo
    m = {0: (w, 0, 0, h, x0, yb), 90: (0, h, -w, 0, x1, yb), 180: (-w, 0, 0, -h, x1, yt), 270: (0, -h, w, 0, x0, yt)}[rot]
    return " ".join(_f(v) for v in m)


class _CtxImagem:
    """Estado por documento de saida: cada algarismo e criado uma unica vez como imagem do PDF e
    reutilizado por todas as paginas."""

    def __init__(self, g: GlifosImagem, doc: "Documento"):
        self.g, self.doc = g, doc
        self.nomes: dict = {}
        for s in doc.info.slots:
            self._nome(s.cor)

    def _nome(self, cor: tuple) -> int:
        """O indice dos 10 algarismos desta cor (cria-os, uma so vez, quando aparece uma cor nova: a cor por serie)."""
        if cor not in self.nomes:
            k = len(self.nomes)
            self.nomes[cor] = k
            for d, gl in enumerate(self.g.glifos):
                self.doc.xobjetos[NameObject(f"/G{k}_{d}")] = _img_xobject(self.doc.w, gl.mascara, cor)
        return self.nomes[cor]

    def ops(self, slot: Slot, texto: str, cor: tuple | None = None) -> str:
        g, caixa = self.g, self.doc.caixa
        c = g.calib[id(slot)]
        k = fator_ajuste(slot, texto)         # mais algarismos que o exemplo: tudo encolhe em torno do centro
        escala = c.escala * k
        topo = c.v_centro + (c.topo - c.v_centro) * k
        gs = [g.glifos[int(d)] for d in texto]
        larguras = [escala * x.w for x in gs]
        n = len(gs)
        faixa = escala * g.altura_faixa
        if c.modelo == "B":      # passo constante: centro de cada algarismo = centro do bloco + i*passo
            inicios = [c.centro + (i - (n - 1) / 2) * c.param * k - larguras[i] / 2 for i in range(n)]
        else:                    # margens por algarismo; bloco de tinta centrado na caixa de avanco
            ds = [int(d) for d in texto]
            gaps = [(c.margens[ds[i]] + c.margens[ds[i + 1]]) * k for i in range(n - 1)]
            total = sum(larguras) + sum(gaps)
            centro_tinta = c.centro + (c.margens[ds[-1]] - c.margens[ds[0]]) * k / 2
            inicios, u = [], centro_tinta - total / 2
            for i, w in enumerate(larguras):
                inicios.append(u)
                u += w + (gaps[i] if i < n - 1 else 0)
        ci = self._nome(cor or slot.cor)
        partes = []
        for d, w, ua in zip(texto, larguras, inicios):
            x1, y1 = _xy(ua, topo, slot.rot)
            x2, y2 = _xy(ua + w, topo + faixa, slot.rot)
            rect = Ret(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            partes.append(f"q {_cm(rect, slot.rot, caixa)} cm /G{ci}_{d} Do Q\n")
        # texto invisivel (Helvetica, modo 3): a rifa continua pesquisavel e a verificacao automatica funciona
        tam_h = slot.tamanho * k
        larg_h = len(texto) * 0.556 * tam_h
        x, y = _origem_pdf(slot, larg_h, caixa, -0.35 * slot.tamanho * (1 - k))
        partes.append(f"BT /FH {_f(tam_h)} Tf 3 Tr {_matriz_texto(slot.rot, x, y)} ({texto}) Tj 0 Tr ET\n")
        return "".join(partes)


def glifos_de_imagem(caminho: Path, log: Log) -> GlifosImagem:
    try:
        if caminho.suffix.lower() == ".pdf":
            img = imagem_de_pdf(caminho)
        else:
            img = Image.open(caminho)
            img.load()
    except Exception as e:
        raise ErroRifas("err_abrir_ficheiro", nome=caminho.name, erro=str(e)) from e
    glifos = extrair_glifos(mascara_de_imagem(img))
    log(msg("log_imagem_ok", altura=glifos[0].mascara.height))
    return GlifosImagem(glifos, ("desc_imagem", {"nome": caminho.name}))


# ------------------------------------------------------------------ preparar
@dataclass
class Preparado:
    info: InfoTemplate
    escritores: dict           # nome da fonte no template -> escritor
    fundo: bytes               # PDF de 1 pagina: template sem numeros
    template: Path = Path()
    disp: "Disposicao | None" = None     # so com 1 rifa no template: como as copias enchem a folha

    @property
    def descricoes(self) -> list:
        vistos = {id(e): e for e in self.escritores.values()}
        return [e.descricao for e in vistos.values()]

    @property
    def por_pagina(self) -> int:
        """Rifas (numeros) por pagina de saida."""
        return self.disp.n if self.disp is not None else self.info.n_campos

    def com_folha(self, papel: str, margem_mm: float, n: int | None = None) -> "Preparado":
        """Copia deste Preparado (partilha o que e pesado) com a rifa repetida na folha; so para templates de 1 rifa."""
        return replace(self, disp=disposicao_da_folha(self.info, papel, margem_mm, n))


# ------------------------------------------------------------------ folha: uma rifa repetida o maximo de vezes
PAPEIS = {"A4": (595.276, 841.89), "A3": (841.89, 1190.551), "A5": (419.528, 595.276),
          "Letter": (612.0, 792.0), "Legal": (612.0, 1008.0)}
MM = 72 / 25.4
MARGEM_MM = 5                  # margem por defeito (as impressoras nao imprimem junto ao bordo)
AVISO_POR_PAGINA = 24          # acima disto as rifas ficam muito pequenas: avisa-se o utilizador
ESPACO_MAX_MM = 15             # tecto do espaco entre rifas quando ha marcas de corte (o resto da folga fica so na margem)
_EPS = 0.01


@dataclass
class Disposicao:
    papel: str
    largura: float             # pagina de saida (pt)
    altura: float
    margem: float              # pt
    posicoes: list             # [(x, y, rot)] canto superior esquerdo de cada rifa na folha (y para baixo); rot 0 | 90
    maximo: int                # quantas cabem
    celula: Ret                # a rifa, no template (y para baixo)
    origem: str = "pagina"
    marcas: bool = False       # marcas de corte nas margens da folha (ver Documento._ops_marcas)

    @property
    def n(self) -> int:
        return len(self.posicoes)

    @property
    def rodadas(self) -> int:
        return sum(1 for p in self.posicoes if p[2] == 90)


def _arrumar(aw: float, ah: float, cw: float, ch: float) -> list:
    """Maximo de retangulos cw x ch (rodados 90 graus ou nao) numa area aw x ah: dois blocos de grelha separados por
    um corte reto (vertical ou horizontal). Devolve [(x, y, rot)] com a origem no canto superior esquerdo."""
    tam = {0: (cw, ch), 90: (ch, cw)}

    def grelha(x0, y0, larg, alt, rot):
        w, h = tam[rot]
        nc, nl = int((larg + _EPS) // w), int((alt + _EPS) // h)
        return [(x0 + c * w, y0 + r * h, rot) for r in range(nl) for c in range(nc)]
    melhor: list = []
    for a in (0, 90):
        b = 90 - a
        wa, ha = tam[a]
        candidatos = [grelha(0, 0, k * wa, ah, a) + grelha(k * wa, 0, aw - k * wa, ah, b)
                      for k in range(int((aw + _EPS) // wa) + 1)]
        candidatos += [grelha(0, 0, aw, k * ha, a) + grelha(0, k * ha, aw, ah - k * ha, b)
                       for k in range(int((ah + _EPS) // ha) + 1)]
        for c in candidatos:       # mais rifas; a igualdade, menos rodadas
            if (len(c), -sum(1 for p in c if p[2])) > (len(melhor), -sum(1 for p in melhor if p[2])):
                melhor = c
    return melhor


def _espacar(pos: list, aw: float, ah: float, cw: float, ch: float) -> list:
    """Afasta as rifas de `pos` (saida de `_arrumar`, ainda sem margem nem centragem: a area e aw x ah) para a folga
    que sobra deixar de virar so margem extra (centragem) e passar a espaco ENTRE elas. Nunca muda quantas rifas ha
    nem a ordem; com encaixe perfeito (sem folga nenhuma) devolve `pos` sem alteracoes. Um corte entre dois blocos
    de orientacoes diferentes conta como uma so cadeia nesse eixo; no outro eixo cada bloco tem a sua folga."""
    tam = {0: (cw, ch), 90: (ch, cw)}

    def deslocamentos(bloco: list, eixo: int, livre: float) -> dict:
        valores = sorted(set(p[eixo] for p in bloco))
        k = len(valores)
        if k == 0:
            return {}
        fim = max(p[eixo] + tam[p[2]][eixo] for p in bloco)
        folga = max(0.0, livre - (fim - valores[0]))
        if k == 1:
            return {valores[0]: folga / 2}
        gap = min(folga / (k - 1), ESPACO_MAX_MM * MM)
        return {v: i * gap for i, v in enumerate(valores)}

    rots = sorted(set(r for _, _, r in pos))
    if len(rots) < 2:
        dx, dy = deslocamentos(pos, 0, aw), deslocamentos(pos, 1, ah)
        return [(x + dx[x], y + dy[y], r) for x, y, r in pos]
    a = [p for p in pos if p[2] == rots[0]]
    b = [p for p in pos if p[2] == rots[1]]
    fim_a_x = max(p[0] + tam[p[2]][0] for p in a)
    fim_b_x = max(p[0] + tam[p[2]][0] for p in b)
    inicio_a_x, inicio_b_x = min(p[0] for p in a), min(p[0] for p in b)
    divisao_x = fim_a_x <= inicio_b_x + _EPS or fim_b_x <= inicio_a_x + _EPS       # blocos lado a lado (corte vertical)
    if divisao_x:
        dx = deslocamentos(a + b, 0, aw)
        dy_a, dy_b = deslocamentos(a, 1, ah), deslocamentos(b, 1, ah)
        return [(x + dx[x], y + (dy_a if r == rots[0] else dy_b)[y], r) for x, y, r in a + b]
    dy = deslocamentos(a + b, 1, ah)
    dx_a, dx_b = deslocamentos(a, 0, aw), deslocamentos(b, 0, aw)
    return [(x + (dx_a if r == rots[0] else dx_b)[x], y + dy[y], r) for x, y, r in a + b]


def disposicao_da_folha(info: InfoTemplate, papel: str, margem_mm: float, n: int | None = None, espacos: bool = False) -> Disposicao:
    """Como encher uma folha `papel` com a rifa do template (so `info.n_campos == 1`). `n` = quantas por folha
    (None = o maximo que couber). `espacos`: afasta as rifas entre si (ver `_espacar`), para a margem poder ficar
    pequena e as marcas de corte (`Documento._ops_marcas`) terem onde desenhar entre cada rifa."""
    if info.n_campos != 1 or info.celula is None:
        raise ErroRifas("err_folha_varias")
    cel = info.celula
    cw, ch = cel.width, cel.height
    margem = max(0.0, margem_mm) * MM
    W0, H0 = PAPEIS[papel]
    melhor = None
    for W, H in ((W0, H0), (H0, W0)):          # folha em altura e em largura: fica a que levar mais
        aw, ah = W - 2 * margem, H - 2 * margem
        if aw <= 0 or ah <= 0:
            continue
        pos = _arrumar(aw, ah, cw, ch)
        chave = (len(pos), -sum(1 for p in pos if p[2]), W <= H)
        if melhor is None or chave > melhor[0]:
            melhor = (chave, W, H, pos)
    if melhor is None or not melhor[3]:
        raise ErroRifas("err_rifa_grande", w=f"{cw / MM:.0f}", h=f"{ch / MM:.0f}", papel=papel, margem=f"{margem_mm:g}")
    _, W, H, pos = melhor      # ja vem por blocos, cada um em ordem de leitura: os numeros crescem bloco a bloco
    if espacos:
        pos = _espacar(pos, W - 2 * margem, H - 2 * margem, cw, ch)
    tam = {0: (cw, ch), 90: (ch, cw)}
    x0, y0 = min(p[0] for p in pos), min(p[1] for p in pos)
    x1, y1 = max(p[0] + tam[p[2]][0] for p in pos), max(p[1] + tam[p[2]][1] for p in pos)
    dx, dy = (W - (x1 - x0)) / 2 - x0, (H - (y1 - y0)) / 2 - y0     # grelha centrada na folha
    pos = [(x + dx, y + dy, r) for x, y, r in pos]
    maximo = len(pos)
    if n is not None:
        pos = pos[:max(1, min(n, maximo))]
        # recentrar o subconjunto: truncar tira sempre do fim (ordem de leitura), por isso o que fica ficava
        # encostado ao topo/esquerda e toda a folga ia para o lado de baixo/direito (margens desiguais, a
        # guilhotina a direito já não serve para todas as linhas)
        x0, y0 = min(p[0] for p in pos), min(p[1] for p in pos)
        x1, y1 = max(p[0] + tam[p[2]][0] for p in pos), max(p[1] + tam[p[2]][1] for p in pos)
        dx, dy = (W - (x1 - x0)) / 2 - x0, (H - (y1 - y0)) / 2 - y0
        pos = [(x + dx, y + dy, r) for x, y, r in pos]
    return Disposicao(papel, W, H, margem, pos, maximo, cel, info.celula_origem)


def preparar(template: Path, algarismos: Path | None, log: Log = _sem_log) -> Preparado:
    """Le o template e o ficheiro dos algarismos 0-9 (obrigatorio)."""
    info = analisar_template(template)
    log(msg("log_template", n=info.n_campos, primeiro=info.primeiro, ultimo=info.ultimo))
    if info.n_paginas > 1:
        log(msg("aviso_paginas_template", n=info.n_paginas))
    if algarismos is None:
        raise ErroAlgarismos("err_sem_ficheiro_algarismos", info)

    try:
        algarismos = Path(algarismos)
        if not algarismos.exists():
            raise ErroRifas("err_ficheiro_inexistente", caminho=str(algarismos))
        ext = algarismos.suffix.lower()
        if ext == ".pdf":
            esc = letra_de_pdf(algarismos, info.fontes[0], log)
            if esc is None:
                log(msg("log_pdf_imagem"))
                esc = glifos_de_imagem(algarismos, log)
        elif ext in EXT_IMAGEM:
            esc = glifos_de_imagem(algarismos, log)
        else:
            raise ErroRifas("err_formato")
    except ErroAlgarismos:
        raise
    except ErroRifas as e:      # o template esta bem; o problema e o ficheiro dos algarismos
        raise ErroAlgarismos(e.chave, info, **e.params) from e
    except Exception as e:
        raise ErroAlgarismos("err_usar_ficheiro", info, nome=algarismos.name, erro=str(e)) from e
    if len(info.fontes) > 1:
        log(msg("aviso_varias_letras"))

    fundo = criar_fundo(template, info)
    if not esc.vetorial:    # imagem: calibrar contra o template (precisa do original e do "sem numeros")
        esc.calibrar(info, Path(template), fundo, log)
    return Preparado(info, {n: esc for n in info.fontes}, fundo, Path(template))


# ------------------------------------------------------------------ documento de saida
class Documento:
    """Um PDF de saida: o fundo (template sem numeros) e guardado uma so vez como Form XObject e cada
    pagina so tem a referencia a ele + os numeros."""

    def __init__(self, prep: Preparado, marca=None, qr=None):
        self.info = prep.info
        self.caixa = prep.info.caixa
        self.disp = prep.disp
        self.w = PdfWriter()
        rd = PdfReader(io.BytesIO(prep.fundo))
        pg = rd.pages[0]
        form = DecodedStreamObject()
        form.set_data(pg.get_contents().get_data())
        bbox = self.caixa
        if self.disp is not None:      # a rifa e so uma zona da pagina do template
            c = self.disp.celula
            bbox = (self.caixa[0] + c.x0, self.caixa[3] - c.y1, self.caixa[0] + c.x1, self.caixa[3] - c.y0)
        self.bbox = bbox
        form.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Form"),
                     NameObject("/BBox"): ArrayObject([FloatObject(v) for v in bbox]),
                     NameObject("/Resources"): pg["/Resources"]})
        self.xobjetos = DictionaryObject({NameObject("/Bg"): self.w._add_object(form.clone(self.w))})
        helv = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica"),
                                 NameObject("/Encoding"): NameObject("/WinAnsiEncoding")})
        helv_b = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
                                   NameObject("/BaseFont"): NameObject("/Helvetica-Bold"),
                                   NameObject("/Encoding"): NameObject("/WinAnsiEncoding")})
        self.fontes = DictionaryObject({NameObject("/FH"): self.w._add_object(helv), NameObject("/FB"): self.w._add_object(helv_b)})
        self.ctxs = {id(e): e.contexto(self) for e in prep.escritores.values()}
        self.prep = prep
        self.recursos = self.w._add_object(DictionaryObject({NameObject("/XObject"): self.xobjetos,
                                                             NameObject("/Font"): self.fontes}))
        self.largura, self.altura = prep.info.largura, prep.info.altura
        if self.disp is not None:
            self.largura, self.altura = self.disp.largura, self.disp.altura
        self.marcas = self._ops_marcas()
        self.logo = self._logotipo(marca) if self.disp is not None and marca is not None else ""
        self.qr = qr if self.disp is not None else None

    def _matriz_rifa(self, x: float, y: float, rot: int) -> str:
        """Matriz que leva a rifa (zona `bbox` do template) para a posicao (x, y) da folha (canto superior esquerdo,
        y para baixo), rodada `rot` graus no sentido anti-horario."""
        cx0, cy0, cx1, cy1 = self.bbox
        cw, ch, alt = cx1 - cx0, cy1 - cy0, self.altura
        if rot == 0:
            return f"1 0 0 1 {_f(x - cx0)} {_f(alt - y - ch - cy0)}"
        return f"0 1 -1 0 {_f(x + ch + cy0)} {_f(alt - y - cw - cx0)}"

    def _logotipo(self, marca) -> str:
        """Embebe o logotipo (uma so vez neste PDF) e devolve os operadores que o desenham num canto da rifa, em coordenadas do
        template (dentro do q...Q de cada rifa na folha)."""
        w = self.w
        img = DecodedStreamObject()
        img.set_data(marca.rgb)
        img.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Image"),
                    NameObject("/Width"): NumberObject(marca.largura), NameObject("/Height"): NumberObject(marca.altura),
                    NameObject("/ColorSpace"): NameObject("/DeviceRGB"), NameObject("/BitsPerComponent"): NumberObject(8)})
        if marca.alfa is not None:
            sm = DecodedStreamObject()
            sm.set_data(marca.alfa)
            sm.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Image"),
                       NameObject("/Width"): NumberObject(marca.largura), NameObject("/Height"): NumberObject(marca.altura),
                       NameObject("/ColorSpace"): NameObject("/DeviceGray"), NameObject("/BitsPerComponent"): NumberObject(8)})
            img[NameObject("/SMask")] = w._add_object(sm.flate_encode())
        self.xobjetos[NameObject("/Logo")] = w._add_object(img.flate_encode())
        x0, y0, x1, y1 = self.bbox
        alt = (y1 - y0) * marca.tamanho / 100
        lar = alt * marca.largura / marca.altura
        if lar > (x1 - x0) * 0.45:                                         # um logotipo muito largo nunca passa de 45 % da rifa
            lar = (x1 - x0) * 0.45
            alt = lar * marca.altura / marca.largura
        folga = 8.0
        x = x0 + folga if marca.posicao in ("se", "ie") else x1 - folga - lar
        y = y1 - folga - alt if marca.posicao in ("se", "sd") else y0 + folga
        return f"q {_f(lar)} 0 0 {_f(alt)} {_f(x)} {_f(y)} cm /Logo Do Q\n"

    def _ops_qr(self, prefixo: str, num: str) -> str:
        """O QR de verificacao deste bilhete, num canto da rifa (coordenadas do template, dentro do q...Q da rifa)."""
        from . import qr as modulo_qr
        q = self.qr
        x0, y0, x1, y1 = self.bbox
        lado = min((y1 - y0) * q.tamanho / 100, (x1 - x0) * 0.45)
        folga = 5.0
        x = x0 + folga if q.posicao in ("se", "ie") else x1 - folga - lado
        y = y1 - folga - lado if q.posicao in ("se", "sd") else y0 + folga
        return modulo_qr.ops_pdf(modulo_qr.modulos(modulo_qr.url(q, prefixo.strip(), num)), x, y, lado)

    def _ops_marcas(self) -> str:
        """Marcas de corte (tracos curtos pretos) a prolongar cada linha de corte: nas margens da folha (como sempre)
        e tambem ENTRE cada rifa, quando ha espaco para isso (ver `disposicao_da_folha(..., espacos=True)`). Cada
        lado de cada rifa recebe a sua propria marca, a apontar para o espaco livre mais proximo nessa direcao (a
        folha, ou a rifa vizinha): sem espaco (encostadas, como antes de haver `espacos`) nao ha marca nenhuma nesse
        lado, e o resultado fica identico ao de antes. Vazio se não há folha ou as marcas estão desligadas."""
        d = self.disp
        if d is None or not d.marcas or not d.posicoes:
            return ""
        cw, ch = d.celula.width, d.celula.height
        caixas = [(x, y, x + (cw if rot == 0 else ch), y + (ch if rot == 0 else cw)) for x, y, rot in d.posicoes]
        folga = 1.0 * MM                                     # a marca nao toca na zona de corte (nem, havendo vizinha, nela)
        # junto a folha so precisa de 1 folga (do lado da rifa); junto a outra rifa precisa de 2 (uma de cada lado,
        # para a marca nao tocar em nenhuma das duas): comp_pagina/comp_vizinha
        comp_pagina = lambda livre: min(3.5 * MM, livre - folga)          # noqa: E731
        comp_vizinha = lambda livre: min(3.5 * MM, livre - 2 * folga)     # noqa: E731
        sobrepoe = lambda a0, a1, b0, b1: min(a1, b1) - max(a0, b0) > _EPS    # noqa: E731

        tracos: set = set()
        for ax, ay, bx, by in caixas:
            outras = [o for o in caixas if o != (ax, ay, bx, by)]
            acima = [o[3] for o in outras if o[3] <= ay + _EPS and sobrepoe(o[0], o[2], ax, bx)]
            comp = comp_vizinha if acima else comp_pagina
            if (c := comp(ay - (max(acima) if acima else 0.0))) >= 1:
                tracos |= {(round(v, 2), round(ay - folga, 2), round(v, 2), round(ay - folga - c, 2)) for v in (ax, bx)}
            abaixo = [o[1] for o in outras if o[1] >= by - _EPS and sobrepoe(o[0], o[2], ax, bx)]
            comp = comp_vizinha if abaixo else comp_pagina
            if (c := comp((min(abaixo) if abaixo else d.altura) - by)) >= 1:
                tracos |= {(round(v, 2), round(by + folga, 2), round(v, 2), round(by + folga + c, 2)) for v in (ax, bx)}
            esquerda = [o[2] for o in outras if o[2] <= ax + _EPS and sobrepoe(o[1], o[3], ay, by)]
            comp = comp_vizinha if esquerda else comp_pagina
            if (c := comp(ax - (max(esquerda) if esquerda else 0.0))) >= 1:
                tracos |= {(round(ax - folga, 2), round(v, 2), round(ax - folga - c, 2), round(v, 2)) for v in (ay, by)}
            direita = [o[0] for o in outras if o[0] >= bx - _EPS and sobrepoe(o[1], o[3], ay, by)]
            comp = comp_vizinha if direita else comp_pagina
            if (c := comp((min(direita) if direita else d.largura) - bx)) >= 1:
                tracos |= {(round(bx + folga, 2), round(v, 2), round(bx + folga + c, 2), round(v, 2)) for v in (ay, by)}
        linhas = [f"{_f(a)} {_f(d.altura - b)} m {_f(c)} {_f(d.altura - e)} l S" for a, b, c, e in sorted(tracos)]
        return "q 0 G 0.4 w\n" + "\n".join(linhas) + "\nQ\n" if linhas else ""

    def _escrever(self, slot: Slot, num: str, prefixo: str, cor: tuple | None) -> str:
        """Os operadores de um numero (e do prefixo, se houver) no sitio do numero de exemplo `slot`."""
        ops = self.ctxs[id(self.prep.escritores[slot.fonte])].ops(slot, num, cor)
        if prefixo:
            ops += self._ops_prefixo(slot, num, prefixo, cor)
        return ops

    def _ops_prefixo(self, slot: Slot, num: str, prefixo: str, cor: tuple | None) -> str:
        """O prefixo em Helvetica-Bold, com o mesmo tamanho e cor dos algarismos, a terminar um pouco antes do 1.o algarismo
        (os algarismos ficam exatamente onde estariam sem prefixo: o prefixo cresce para a esquerda)."""
        from .series import largura_do_prefixo
        k = fator_ajuste(slot, num)
        tam = slot.tamanho * k
        bloco = slot.avanco * min(1.0, len(num) / max(len(slot.texto), 1))        # largura aproximada do numero, centrado na caixa
        u = slot.avanco / 2 - bloco / 2 - 0.15 * tam - largura_do_prefixo(prefixo, tam)
        eu, ev = EIXOS[slot.rot]
        dv = -0.35 * slot.tamanho * (1 - k)
        x = slot.origem[0] + eu[0] * u + ev[0] * dv + self.caixa[0]
        y = self.caixa[3] - (slot.origem[1] + eu[1] * u + ev[1] * dv)
        r, g, b = cor or slot.cor
        return f"BT /FB {_f(tam)} Tf {_f(r)} {_f(g)} {_f(b)} rg {_matriz_texto(slot.rot, x, y)} ({prefixo}) Tj ET\n"

    def adicionar_linha(self, linha: list, prefixo: str = "", cor: tuple | None = None) -> None:
        if self.disp is not None:
            # todas as rifas da folha sao o mesmo desenho (campo 1): cada uma e o fundo + os numeros, tudo dentro
            # de um q...Q com a matriz da posicao (os numeros e a calibracao ficam nas coordenadas do template)
            slots1 = [s for s in self.info.slots if s.campo == 1]
            partes = []
            for i, num in enumerate(linha):
                x, y, rot = self.disp.posicoes[i]
                ops = "".join(self._escrever(s, num, prefixo, cor) for s in slots1)
                qr = self._ops_qr(prefixo, num) if self.qr is not None else ""
                partes.append(f"q {self._matriz_rifa(x, y, rot)} cm /Bg Do\n{self.logo}{qr}{ops}Q\n")
            conteudo = "".join(partes) + self.marcas
        else:
            ops = []
            for slot in self.info.slots:
                if slot.campo <= len(linha):
                    ops.append(self._escrever(slot, linha[slot.campo - 1], prefixo, cor))
            conteudo = "/Bg Do\n" + "".join(ops)
        w = self.w
        pg = w.add_blank_page(width=self.largura, height=self.altura)
        if self.disp is None:
            pg.mediabox = RectangleObject(self.caixa)
        st = DecodedStreamObject()
        st.set_data(conteudo.encode("latin-1"))
        pg[NameObject("/Contents")] = w._add_object(st.flate_encode())
        pg[NameObject("/Resources")] = self.recursos

    def gravar(self, destino) -> None:
        if isinstance(destino, (io.BytesIO,)):
            self.w.write(destino)
        else:
            with open(destino, "wb") as f:
                self.w.write(f)


# ------------------------------------------------------------------ gerar
@dataclass
class Trabalho:
    saida: Path
    nome: str = ""
    inicio: int = 1
    fim: int = 100
    por_ficheiro: int | None = None     # None = tudo num unico PDF
    digitos: int = 4
    # series e saltos (ver series.py); por omissao nada disto muda o resultado
    prefixos: tuple = ()                # texto antes dos algarismos; com mais de um, cada um e uma serie com os seus ficheiros
    saltar: tuple = ()                  # ((a, b), ...) numeros que nunca se imprimem
    cor_por_serie: bool = False         # com varias series, uma cor para cada
    marca: object | None = None         # core.marca.Marca: o logotipo em cada rifa (so templates de uma rifa, em folha)
    cor_numeros: tuple | None = None    # (r, g, b) 0..1: a cor dos numeros (a da serie, se ha, ganha)
    qr: object | None = None            # core.qr.Qr: um QR de verificacao em cada rifa (so em modo folha)


@dataclass
class Resultado:
    caminho: Path
    paginas: int
    erros: list

    @property
    def ok(self) -> bool:
        return not self.erros


def nome_seguro(nome: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nome).strip(" .")


def validar(tr: Trabalho, por_pagina: int) -> None:
    if not nome_seguro(tr.nome):
        raise ErroRifas("err_nome")
    if tr.inicio < 0 or tr.fim < tr.inicio:
        raise ErroRifas("err_intervalo")
    if not 1 <= tr.digitos <= MAX_DIGITOS:
        raise ErroRifas("err_digitos", max=MAX_DIGITOS)
    if tr.prefixos or tr.saltar:
        from .series import validar_extras
        validar_extras(tr)
    if tr.por_ficheiro is not None:
        if tr.por_ficheiro < 1:
            raise ErroRifas("err_max")
        if tr.por_ficheiro % por_pagina:
            sug = max(tr.por_ficheiro // por_pagina, 1) * por_pagina
            raise ErroRifas("err_max_multiplo", max=tr.por_ficheiro, n=por_pagina, sug=sug)


def planear(tr: Trabalho, por_pagina: int) -> list:
    """[(caminho do PDF, primeiro numero, ultimo numero)]; `por_pagina` = rifas por pagina de saida."""
    validar(tr, por_pagina)
    largura = max(tr.digitos, len(str(tr.fim)))
    if tr.por_ficheiro is None:
        partes = [(tr.inicio, tr.fim)]
    else:
        partes = [(a, min(a + tr.por_ficheiro - 1, tr.fim)) for a in range(tr.inicio, tr.fim + 1, tr.por_ficheiro)]
    base = nome_seguro(tr.nome)
    return [(tr.saida / f"{base} - {a:0{largura}d} - {b:0{largura}d}.pdf", a, b) for a, b in partes]


def linhas_de_numeros(a: int, b: int, n_campos: int, largura: int) -> list:
    nums = [f"{i:0{largura}d}" for i in range(a, b + 1)]
    return [nums[i:i + n_campos] for i in range(0, len(nums), n_campos)]


def _montar(linhas: list, prep: Preparado, progresso: Callable[[], None] | None = None,
            cancelar: threading.Event | None = None, prefixo: str = "", cor: tuple | None = None, marca=None, qr=None) -> Documento:
    doc = Documento(prep, marca, qr)
    for row in linhas:
        if cancelar is not None and cancelar.is_set():
            raise Cancelado()
        doc.adicionar_linha(row, prefixo, cor)
        if progresso:
            progresso()
    return doc


def _texto_pagina(pagina) -> str:
    tp = pagina.get_textpage()
    try:
        return tp.get_text_range()
    finally:
        tp.close()


def verificar(destino: Path, linhas: list, prep: Preparado, largura: int) -> list:
    """Cada pagina tem de ter os numeros da linha, 2x cada (talao + principal),
    alem dos numeros fixos do template (ex.: o ano na data do sorteio; numa folha com varias copias da mesma
    rifa, uma vez por copia)."""
    erros = []
    padrao = re.compile(rf"(?<!\d)\d{{{largura},}}(?!\d)")
    bg = _abrir_pdfium(prep.fundo)
    try:
        fixos = padrao.findall(_texto_pagina(bg[0]))
    finally:
        bg.close()
    mult, repetida = prep.info.n_numeros, prep.disp is not None
    doc = _abrir_pdfium(destino)
    try:
        if len(doc) != len(linhas):
            erros.append(msg("ver_paginas", tem=len(doc), esperado=len(linhas)))
        for i in range(min(len(doc), len(linhas))):
            pg = doc[i]
            achados = sorted(padrao.findall(_texto_pagina(pg)))
            pg.close()
            c_esp = Counter()
            for k, n in enumerate(linhas[i]):
                c_esp[n] += mult.get(1 if repetida else k + 1, 2)
            copias = len(linhas[i]) if repetida else 1
            c_ach, c_fix = Counter(achados), Counter({k: v * copias for k, v in Counter(fixos).items()})
            # todos os numeros dos bilhetes tem de estar la (2x cada); o que sobrar so pode ser numero fixo do
            # template (o PDFium nem sempre extrai o texto de formularios aninhados, por isso tambem pode faltar)
            if (any(c_ach[k] < v for k, v in c_esp.items())
                    or any(c_ach[k] - c_esp.get(k, 0) > c_fix.get(k, 0) for k in c_ach)):
                erros.append(msg("ver_pagina", i=i + 1, esperado=sorted(c_esp.elements()), achado=achados))
    finally:
        doc.close()
    return erros


def gerar(tr: Trabalho, prep: Preparado, log: Log = _sem_log,
          progresso: Callable[[int, int], None] | None = None,
          cancelar: threading.Event | None = None) -> list:
    """Gera os PDFs. progresso(feitas, total) conta paginas. Devolve [Resultado]."""
    from .series import planear_partes
    info = prep.info
    por_pagina = prep.por_pagina
    partes = planear_partes(tr, por_pagina)
    largura = max(tr.digitos, len(str(tr.fim)))
    if prep.disp is not None:
        d = prep.disp
        log(msg("log_folha", papel=d.papel, n=d.n, w=f"{d.celula.width / MM:.0f}", h=f"{d.celula.height / MM:.0f}"))
        if d.n > AVISO_POR_PAGINA:
            log(msg("aviso_muitas", n=d.n))
    if largura > len(info.primeiro):
        log(msg("aviso_algarismos", exemplo=len(info.primeiro), largura=largura,
              pct=round(100 * len(info.primeiro) / largura)))
    qtd_serie = sum(len(p.numeros) for p in partes) // max(1, len(tr.prefixos))
    if qtd_serie % por_pagina:
        log(msg("aviso_multiplo", qtd=qtd_serie, n=por_pagina))
    try:
        tr.saida.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ErroRifas("err_pasta", erro=str(e)) from e

    total = sum(-(-len(p.numeros) // por_pagina) for p in partes)
    feitas = 0

    def passo():
        nonlocal feitas
        feitas += 1
        if progresso:
            progresso(feitas, total)

    resultados = []
    for parte in partes:
        destino = parte.destino
        nums = [f"{i:0{largura}d}" for i in parte.numeros]
        linhas = [nums[i:i + por_pagina] for i in range(0, len(nums), por_pagina)]
        log(msg("log_a_gerar", nome=destino.name, paginas=len(linhas)))
        doc = _montar(linhas, prep, passo, cancelar, parte.prefixo, parte.cor, tr.marca, tr.qr)
        try:
            doc.gravar(destino)
        except Exception as e:
            raise ErroRifas("err_gravar", nome=destino.name, erro=str(e)) from e
        finally:
            del doc
        erros = verificar(destino, linhas, prep, largura)
        r = Resultado(destino, len(linhas), erros)
        resultados.append(r)
        mb = f"{destino.stat().st_size / 1e6:.1f}"
        if r.ok:
            log(msg("log_pronto_ok", nome=destino.name, paginas=len(linhas), mb=mb))
        else:
            log(msg("log_pronto_erro", nome=destino.name, paginas=len(linhas), mb=mb, n=len(erros), primeiro=erros[0]))
    return resultados


def pagina_previa(prep: Preparado, inicio: int, digitos: int, fim: int | None = None, dpi: int = 160, prefixo: str = "",
                  cor: tuple | None = None, saltar: tuple = (), marca=None) -> bytes:
    """PNG da 1.a pagina, com os primeiros numeros do intervalo (e, como `pdf_da_previa`, prefixo, cor, saltos e logotipo)."""
    return png_de_pagina(pdf_da_previa(prep, inicio, digitos, fim, prefixo, cor, saltar, marca), dpi)


def pdf_da_previa(prep: Preparado, inicio: int, digitos: int, fim: int | None = None, prefixo: str = "",
                  cor: tuple | None = None, saltar: tuple = (), marca=None, qr=None) -> bytes:
    """PDF de 1 pagina (bytes) com os primeiros numeros do intervalo: o que `pagina_previa` desenha, mas ainda vetorial
    (a webapp mostra-o no browser com PDF.js). `prefixo`, `cor` e `saltar`: como num pedido com series (ver series.py)."""
    n = prep.por_pagina
    largura = max(digitos, len(str(fim if fim is not None else inicio + n)))
    if saltar:      # os numeros a saltar nao entram: os primeiros `n` que sobram
        from .series import numeros
        teto = fim if fim is not None else inicio + n + sum(b - a + 1 for a, b in saltar)
        linhas = [[f"{i:0{largura}d}" for i in numeros(inicio, teto, saltar)[:n]]]
    else:
        ultimo = inicio + n - 1 if fim is None else min(fim, inicio + n - 1)
        linhas = linhas_de_numeros(inicio, ultimo, n, largura)[:1]
    doc = _montar(linhas, prep, prefixo=prefixo, cor=cor, marca=marca, qr=qr)
    buf = io.BytesIO()
    doc.gravar(buf)
    return buf.getvalue()


def pagina_template(caminho: Path, dpi: int = 90) -> bytes:
    return png_de_pagina(Path(caminho), dpi)
