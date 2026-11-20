"""Fase 7 do preçário: **vales de fichas numerados**. Quando a moeda do preçário é inventada («fichas», «senhas»), a festa precisa dos próprios vales: aqui
desenha-se o TEMPLATE de um vale (uma peça com o valor, o título e o campo do número «0001» uma só vez) e os algarismos na mesma letra, e daí em diante é
o motor das rifas que os numera: séries («A-», «B-»), números a saltar, cor por série, QR de verificação, folhas arrumadas, PDF e ZIP. Nada aqui numera nem
verifica: só se desenha o modelo, como a galeria (`galeria.py`) e o editor (`editor.py`).

Geometria (pt, y para cima): o vale mede 300 × 130; o número fica em cima à direita e o canto de baixo à direita fica livre para o QR (em modo folha o QR
ocupa um canto, como o logótipo). O valor vem como «<n> <moeda>» e o motor procura o número pelos algarismos (0 seguido de, pelo menos, 2 algarismos),
por isso nenhum texto do vale pode ter uma sequência assim (`err_editor_digitos`, a mesma regra do editor).
"""
from __future__ import annotations

import io
from dataclasses import dataclass

from . import galeria, letras
from .motor import PADRAO_EXEMPLO, ErroRifas

LARGURA, ALTURA = 300.0, 130.0
MARGEM = 2.0
MAX_TITULO, MAX_ORGANIZACAO, MAX_MOEDA, MAX_NOTA = 24, 50, 14, 60
MIN_QUANTIDADE, MAX_QUANTIDADE = 1, 99            # de 1 a 99: curto, legivel e sem nenhum «0» seguido de 2 algarismos
EXEMPLO = ("VALE", "Associação Imaginária · Festa de Exemplo", "ficha", 1)


@dataclass(frozen=True)
class Vale:
    desenho: str = "arraial"
    titulo: str = ""                       # o que se le em grande em cima («VALE»)
    organizacao: str = ""
    moeda: str = ""                        # o nome da moeda inventada, no singular («ficha»)
    moeda_plural: str = ""                 # no plural («fichas»); vazio = o mesmo
    quantidade: int = 1                    # quantas fichas vale este vale
    nota: str = ""                         # uma linha pequena em baixo («Válido só na festa»)

    def valor_texto(self) -> str:
        nome = self.moeda_plural.strip() if self.quantidade != 1 and self.moeda_plural.strip() else self.moeda.strip()
        return f"{self.quantidade} {nome}".strip()

    def ou_exemplo(self) -> "Vale":
        """Sem nada escrito, o vale de exemplo (a mesma festa inventada dos outros exemplos)."""
        if self.titulo.strip() or self.organizacao.strip() or self.moeda.strip() or self.nota.strip():
            return self
        t, o, m, q = EXEMPLO
        return Vale(self.desenho, t, o, m, m + "s", q, "")


def validar(v: Vale) -> None:
    """`ErroRifas` se o desenho não existe, a quantidade está fora dos limites, um texto é grande demais, tem letras que nenhuma família tem
    ou tem uma sequência de algarismos que o motor confundiria com o número."""
    if v.desenho not in galeria.POR_ID:
        raise ErroRifas("err_galeria_texto", car="?")
    if isinstance(v.quantidade, bool) or not isinstance(v.quantidade, int) or not MIN_QUANTIDADE <= v.quantidade <= MAX_QUANTIDADE:
        raise ErroRifas("err_vale_quantidade", min=MIN_QUANTIDADE, max=MAX_QUANTIDADE)
    letras.registar()
    for texto, maximo in ((v.titulo, MAX_TITULO), (v.organizacao, MAX_ORGANIZACAO), (v.moeda, MAX_MOEDA), (v.moeda_plural, MAX_MOEDA), (v.nota, MAX_NOTA)):
        if len(texto) > maximo or "\n" in texto or "\r" in texto:
            raise ErroRifas("err_galeria_texto", car="?")
        if PADRAO_EXEMPLO.search(texto):
            raise ErroRifas("err_editor_digitos", texto=texto[:30])
        falta = letras.em_falta(texto)
        if falta:
            raise ErroRifas("err_galeria_texto", car=falta)


def _fonte_ajustada(texto: str, negrito: bool, maximo: float, minimo: float, largura: float) -> tuple[str, float]:
    f = letras.fonte(texto, negrito)
    return f, galeria._ajustar(texto, f, maximo, largura, minimo)


def _desenhar(c, d, v: Vale, x: float, yb: float, w: float, h: float, numero: str = "0001") -> None:
    c.saveState()
    c.setLineWidth(2)
    c.setStrokeColorRGB(*d.principal)
    c.setFillColorRGB(*d.papel)
    c.roundRect(x, yb, w, h, 10, stroke=1, fill=1)
    # faixa em cima com o titulo
    c.setFillColorRGB(*d.principal)
    c.roundRect(x + 1, yb + h - 34, w - 2, 33, 9, stroke=0, fill=1)
    c.rect(x + 1, yb + h - 34, w - 2, 14, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    if v.titulo.strip():
        f, tam = _fonte_ajustada(v.titulo, True, 20, 11, w - 132)
        c.setFont(f, tam)
        c.drawString(x + 14, yb + h - 25, v.titulo)
    # o numero (caixa em cima, à direita, sobre a faixa)
    c.setStrokeColorRGB(*d.destaque)
    c.setLineWidth(2)
    c.setFillColorRGB(*d.talao)
    c.roundRect(x + w - 108, yb + h - 30, 96, 26, 7, stroke=1, fill=1)
    c.setFillColorRGB(*d.destaque)
    c.setFont("VeraBd", 19)
    c.drawString(x + w - 108 + (96 - galeria._largura(numero, "VeraBd", 19)) / 2, yb + h - 23, numero)
    # o valor, em grande
    valor = v.valor_texto()
    if valor:
        f, tam = _fonte_ajustada(valor, True, 34, 14, w - 28)
        c.setFillColorRGB(*d.destaque)
        c.setFont(f, tam)
        c.drawCentredString(x + w / 2, yb + 52, valor)
    if v.organizacao.strip():
        f, tam = _fonte_ajustada(v.organizacao, False, 8.5, 5.5, w - 110)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        c.setFont(f, tam)
        c.drawString(x + 14, yb + 30, v.organizacao)
    if v.nota.strip():
        f, tam = _fonte_ajustada(v.nota, False, 8, 5.5, w - 110)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        c.setFont(f, tam)
        c.drawString(x + 14, yb + 15, v.nota)
    # a linha a tracejado (destaca o vale na folha) e o canto livre do QR fica em branco
    c.setStrokeColorRGB(*d.principal)
    c.setLineWidth(0.8)
    c.setDash(2, 3)
    c.line(x + 14, yb + 41, x + w - 96, yb + 41)
    c.setDash()
    c.restoreState()


def criar_template(v: Vale) -> bytes:
    """O PDF do template: a página é o vale com 2 pt de folga, o número 0001 uma vez. `ErroRifas` se algo não é válido."""
    v = v.ou_exemplo()
    validar(v)
    from reportlab.pdfgen import canvas
    galeria._registar()
    d = galeria.POR_ID[v.desenho]
    saida = io.BytesIO()
    c = canvas.Canvas(saida, pagesize=(LARGURA + 2 * MARGEM, ALTURA + 2 * MARGEM), pageCompression=1, invariant=1)
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, LARGURA + 2 * MARGEM, ALTURA + 2 * MARGEM, stroke=0, fill=1)
    _desenhar(c, d, v, MARGEM, MARGEM, LARGURA, ALTURA)
    c.save()
    return saida.getvalue()


def criar_algarismos() -> bytes:
    """Os algarismos 0-9 na letra do número do vale (a mesma da galeria)."""
    return galeria.criar_algarismos()


def de_dict(d: dict) -> Vale:
    """O vale de um dicionário (a API): campos em falta ficam por omissão e o tipo de cada um valida-se."""
    if not isinstance(d, dict):
        raise ErroRifas("err_pedido_ficheiro")

    def texto(k: str) -> str:
        v = d.get(k, "")
        if not isinstance(v, str):
            raise ErroRifas("err_galeria_texto", car="?")
        return v

    q = d.get("quantidade", 1)
    v = Vale(texto("desenho") or "arraial", texto("titulo"), texto("organizacao"), texto("moeda"), texto("moeda_plural"), q, texto("nota"))
    validar(v)
    return v
