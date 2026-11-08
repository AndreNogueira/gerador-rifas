"""Series, prefixos e numeros a saltar (M1): a logica pura, sem PDF.

Um pedido pode ter:
 - **prefixos**: texto desenhado ANTES dos algarismos (p.ex. «A-» -> A-0001). Com mais de um («A-, B-, C-») cada um e uma **serie**: o
   intervalo repete-se para cada serie, com o seu prefixo, e cada serie tem os seus ficheiros;
 - **saltar**: numeros ou intervalos que nunca se imprimem («13, 100-110»);
 - **cor por serie**: com varias series, cada uma tem a sua cor (a do prefixo e a dos algarismos).

O prefixo desenha-se em Helvetica-Bold (os algarismos vem do ficheiro do utilizador e so tem 0-9), por isso so aceita letras,
espaco, ponto, hifen e barra, ate 6 caracteres, **sem algarismos** (a verificacao dos PDFs procura sequencias de algarismos e o
prefixo nao pode confundi-la). Tudo o que e invalido levanta `ErroRifas` (err_prefixo, err_saltar), traduzido so ao mostrar.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .motor import ErroRifas, Trabalho, nome_seguro, validar

MAX_PREFIXO = 6
MAX_SERIES = 12
MAX_SALTAR = 50
_PREFIXO_OK = re.compile(r"[A-Za-z .\-/]{1,%d}" % MAX_PREFIXO)
_SEPARADORES = " .-/"

# uma cor por serie (RGB 0..1): distintas entre si e legiveis sobre branco
PALETA = [(0.78, 0.16, 0.16), (0.08, 0.40, 0.75), (0.18, 0.49, 0.20), (0.93, 0.42, 0.00), (0.42, 0.11, 0.60), (0.00, 0.51, 0.56)]

# larguras (milesimos de em) da Helvetica-Bold nos caracteres que o prefixo aceita
_LARGURAS = {
    " ": 278, ".": 278, "-": 333, "/": 278,
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278, "J": 556, "K": 722, "L": 611,
    "M": 833, "N": 722, "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667,
    "Y": 667, "Z": 611,
    "a": 556, "b": 611, "c": 556, "d": 611, "e": 556, "f": 333, "g": 611, "h": 611, "i": 278, "j": 278, "k": 556, "l": 278,
    "m": 889, "n": 611, "o": 611, "p": 611, "q": 611, "r": 389, "s": 556, "t": 333, "u": 611, "v": 556, "w": 778, "x": 556,
    "y": 556, "z": 500,
}


def largura_do_prefixo(texto: str, tamanho: float) -> float:
    """Largura (pt) do prefixo em Helvetica-Bold ao `tamanho` dado."""
    return sum(_LARGURAS.get(c, 556) for c in texto) / 1000 * tamanho


def ler_prefixos(txt: str) -> tuple[str, ...]:
    """«A-» -> ("A-",); «A-, B-, C-» -> ("A-", "B-", "C-"); vazio -> (). Levanta err_prefixo."""
    itens = [p.strip() for p in txt.split(",")]
    itens = [p for p in itens if p]
    if len(itens) > MAX_SERIES:
        raise ErroRifas("err_prefixo", max=MAX_PREFIXO, series=MAX_SERIES)
    for p in itens:
        if not _PREFIXO_OK.fullmatch(p):
            raise ErroRifas("err_prefixo", max=MAX_PREFIXO, series=MAX_SERIES)
    if len({etiqueta(p, 0) for p in itens}) != len(itens):          # «A-» e «A.» dariam o mesmo nome de ficheiro
        raise ErroRifas("err_prefixo", max=MAX_PREFIXO, series=MAX_SERIES)
    return tuple(itens)


def ler_saltar(txt: str) -> tuple[tuple[int, int], ...]:
    """«13, 100-110, 666» -> ((13, 13), (100, 110), (666, 666)). Levanta err_saltar."""
    saida = []
    for parte in (p.strip() for p in txt.split(",")):
        if not parte:
            continue
        m = re.fullmatch(r"(\d{1,9})(?:\s*-\s*(\d{1,9}))?", parte)
        if not m:
            raise ErroRifas("err_saltar")
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if b < a:
            raise ErroRifas("err_saltar")
        saida.append((a, b))
    if len(saida) > MAX_SALTAR:
        raise ErroRifas("err_saltar")
    return tuple(saida)


def etiqueta(prefixo: str, indice: int) -> str:
    """O que identifica a serie no nome dos ficheiros: o prefixo sem os separadores nas pontas («A-» -> «A»)."""
    return prefixo.strip(_SEPARADORES) or f"serie{indice + 1}"


def numeros(inicio: int, fim: int, saltar: tuple[tuple[int, int], ...] = ()) -> list[int]:
    """Os numeros a imprimir, por ordem, sem os que se saltam."""
    if not saltar:
        return list(range(inicio, fim + 1))
    return [n for n in range(inicio, fim + 1) if not any(a <= n <= b for a, b in saltar)]


def contar(tr: Trabalho) -> int:
    """Quantos numeros (bilhetes) o pedido gera no total: os do intervalo sem os saltados, vezes o numero de series."""
    return len(numeros(tr.inicio, tr.fim, tr.saltar)) * max(1, len(tr.prefixos))


def bilhetes(tr: Trabalho) -> list[tuple[str, str]]:
    """Todos os bilhetes do pedido, por serie e por ordem: [(serie, numero formatado)] com a serie vazia se nao ha prefixos
    e o numero ja com o prefixo («A-0001»). E o que as listas (CSV, folha de controlo) mostram."""
    largura = max(tr.digitos, len(str(tr.fim)))
    nums = numeros(tr.inicio, tr.fim, tr.saltar)
    return [(etiqueta(p, i) if tr.prefixos else "", f"{p}{n:0{largura}d}") for i, p in enumerate(tr.prefixos or ("",)) for n in nums]


def cor_da_serie(tr: Trabalho, indice: int) -> tuple | None:
    """A cor da serie `indice`, ou None (a do template) se nao ha varias series ou a cor por serie esta desligada."""
    if tr.cor_por_serie and len(tr.prefixos) > 1:
        return PALETA[indice % len(PALETA)]
    return None


def validar_extras(tr: Trabalho) -> None:
    """Prefixos, saltos e serie: o que `motor.validar` nao conhece. Levanta ErroRifas."""
    if len(tr.prefixos) > MAX_SERIES or any(not _PREFIXO_OK.fullmatch(p) for p in tr.prefixos):
        raise ErroRifas("err_prefixo", max=MAX_PREFIXO, series=MAX_SERIES)
    if len({etiqueta(p, 0) for p in tr.prefixos}) != len(tr.prefixos):
        raise ErroRifas("err_prefixo", max=MAX_PREFIXO, series=MAX_SERIES)
    if len(tr.saltar) > MAX_SALTAR or any(b < a for a, b in tr.saltar):
        raise ErroRifas("err_saltar")
    if tr.saltar and not numeros(tr.inicio, tr.fim, tr.saltar):
        raise ErroRifas("err_intervalo")                               # os saltos comem o intervalo todo


@dataclass
class Parte:
    """Um PDF a gerar: os numeros que leva, o prefixo e a cor (None = a do template)."""
    destino: Path
    numeros: list
    prefixo: str
    cor: tuple | None


def planear_partes(tr: Trabalho, por_pagina: int) -> list[Parte]:
    """O plano de ficheiros com series e saltos. Sem extras sai igual ao de `motor.planear` (mesmos nomes e intervalos)."""
    validar(tr, por_pagina)
    validar_extras(tr)
    largura = max(tr.digitos, len(str(tr.fim)))
    nums = numeros(tr.inicio, tr.fim, tr.saltar)
    base = nome_seguro(tr.nome)
    series = tr.prefixos or ("",)
    com_serie = len(tr.prefixos) > 1
    partes: list[Parte] = []
    for i, prefixo in enumerate(series):
        cor = cor_da_serie(tr, i)
        blocos = [nums] if tr.por_ficheiro is None else [nums[k:k + tr.por_ficheiro] for k in range(0, len(nums), tr.por_ficheiro)]
        nome = f"{base} - {etiqueta(prefixo, i)}" if com_serie else base
        for bloco in blocos:
            partes.append(Parte(tr.saida / f"{nome} - {bloco[0]:0{largura}d} - {bloco[-1]:0{largura}d}.pdf", bloco, prefixo, cor))
    return partes
