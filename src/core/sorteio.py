"""M7: sorteio verificavel. Qualquer pessoa repete o sorteio com os mesmos dados e obtem os mesmos numeros: nada fica escondido.

O algoritmo (a pagina /sorteio do site faz exatamente isto no browser; este ficheiro e a referencia e os testes garantem que dao o mesmo):
 1. Os numeros possiveis sao os inteiros de `de` a `ate` (inclusive) menos os excluidos, por ordem crescente.
 2. `semente` (texto, sem espacos nas pontas, em UTF-8) e a unica fonte de acaso. Para sortear um inteiro em [0, m) com o contador `c`:
    para j = 0, 1, 2...: x = os 8 primeiros bytes (big-endian) de SHA-256(semente + ":" + c + ":" + j); se x < 2^64 - (2^64 mod m)
    devolve-se x mod m (o resto evita enviesar o resultado); senao tenta-se o j seguinte.
 3. Baralhar parcialmente: para i = 0 .. quantos-1: r = inteiro em [0, N-i) com o contador i; trocam-se as posicoes i e i+r.
 4. Os sorteados sao as primeiras `quantos` posicoes, pela ordem em que saem (1.o, 2.o, ...).
A honestidade do sorteio depende da semente: tem de ser uma coisa que ninguem controla e que so se conhece DEPOIS de fechadas as vendas
(por exemplo o resultado de uma lotaria publica ou a aleatoriedade publica do drand). Ver docs/SORTEIO.md.
"""
from __future__ import annotations

import hashlib

MAX_NUMEROS = 1_000_000
MAX_QUANTOS = 100
MAX_SEMENTE = 200
_DOIS64 = 1 << 64


def _abaixo_de(m: int, semente: bytes, contador: int) -> int:
    """Um inteiro em [0, m) sem enviesamento, determinista a partir da semente e do contador."""
    limite = _DOIS64 - (_DOIS64 % m)
    j = 0
    while True:
        x = int.from_bytes(hashlib.sha256(semente + b":" + str(contador).encode() + b":" + str(j).encode()).digest()[:8], "big")
        if x < limite:
            return x % m
        j += 1


def numeros_possiveis(de: int, ate: int, excluir: tuple = ()) -> list[int]:
    if ate < de:
        raise ValueError("intervalo vazio")
    if ate - de + 1 > MAX_NUMEROS:
        raise ValueError("intervalo demasiado grande")
    return [n for n in range(de, ate + 1) if not any(a <= n <= b for a, b in excluir)]


def sortear(de: int, ate: int, quantos: int, semente: str, excluir: tuple = ()) -> list[int]:
    """Os `quantos` numeros sorteados, pela ordem em que saem. `excluir` = ((a, b), ...). ValueError se os dados nao servem."""
    semente = semente.strip()
    if not semente or len(semente) > MAX_SEMENTE:
        raise ValueError("semente invalida")
    numeros = numeros_possiveis(de, ate, excluir)
    if not 1 <= quantos <= min(MAX_QUANTOS, len(numeros)):
        raise ValueError("quantidade invalida")
    base = semente.encode("utf-8")
    for i in range(quantos):
        r = _abaixo_de(len(numeros) - i, base, i)
        numeros[i], numeros[i + r] = numeros[i + r], numeros[i]
    return numeros[:quantos]
