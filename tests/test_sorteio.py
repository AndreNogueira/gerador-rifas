"""M7: o sorteio verificavel (referencia em Python; o do browser tem os mesmos vetores em src/sorteio.test.ts)."""
import hashlib
from collections import Counter

import pytest

from core import sorteio

# os mesmos vetores estao em src/web/frontend/src/sorteador.test.ts: se um mudar, o outro tem de mudar
VETORES = [
    ((1, 100, 3, "semente-um", ()), [29, 38, 74]),
    ((1, 1000, 5, "drand:5000000:abcdef", ()), [401, 161, 907, 932, 644]),
    ((0, 9, 10, "todos", ()), [5, 3, 9, 6, 1, 8, 2, 4, 0, 7]),
    ((1, 500, 4, "Lotaria 2026-12-24 12 34 45", ((13, 13), (100, 110))), [495, 382, 7, 329]),
    ((100, 199, 2, "açúcar ∑ 日本", ()), [109, 170]),
    ((1, 7, 1, "x", ((1, 6),)), [7]),
]


@pytest.mark.parametrize("args,esperado", VETORES)
def test_vetores_de_referencia(args, esperado):
    assert sorteio.sortear(*args) == esperado


def test_determinista_e_a_semente_sem_espacos_nas_pontas_e_a_mesma():
    a = sorteio.sortear(1, 1000, 5, "abc")
    assert a == sorteio.sortear(1, 1000, 5, "  abc \n") and a != sorteio.sortear(1, 1000, 5, "abd")


def test_sem_repeticoes_dentro_do_intervalo_e_sem_os_excluidos():
    for semente in ("a", "b", "c", "d"):
        r = sorteio.sortear(1, 50, 20, semente, ((10, 20),))
        assert len(set(r)) == 20 and all(1 <= n <= 50 and not 10 <= n <= 20 for n in r)
    assert sorted(sorteio.sortear(5, 14, 10, "todos")) == list(range(5, 15))         # sortear todos = uma permutacao


def test_mais_numeros_nao_mudam_os_primeiros_sorteados():
    # o i-esimo numero so depende dos anteriores: pedir mais premios nao muda os que ja saiam
    assert sorteio.sortear(1, 1000, 10, "s")[:3] == sorteio.sortear(1, 1000, 3, "s")


def test_sem_enviesamento_visivel():
    """O 1.o sorteado de 10 numeros, com 5 000 sementes diferentes: cada numero sai ~10 % das vezes."""
    contagem = Counter(sorteio.sortear(0, 9, 1, f"semente-{i}")[0] for i in range(5000))
    assert set(contagem) == set(range(10))
    assert all(400 <= v <= 600 for v in contagem.values()), contagem                  # +-20 % de 500: de sobra para um acaso honesto


def test_a_rejeicao_evita_o_enviesamento_com_intervalos_grandes():
    m = (1 << 63) + 12345                                                              # perto de 2^64/2: a rejeicao dispara muitas vezes
    for c in range(50):
        assert 0 <= sorteio._abaixo_de(m, b"s", c) < m
    # a mesma conta feita a mao, para o contador 0
    base = b"s"
    j = 0
    while True:
        x = int.from_bytes(hashlib.sha256(base + b":0:" + str(j).encode()).digest()[:8], "big")
        if x < (1 << 64) - ((1 << 64) % m):
            break
        j += 1
    assert sorteio._abaixo_de(m, base, 0) == x % m


@pytest.mark.parametrize("args", [
    (5, 1, 1, "s", ()), (1, 10, 0, "s", ()), (1, 10, 11, "s", ()), (1, 10, 1, "", ()), (1, 10, 1, "  ", ()), (1, 10, 1, "x" * 201, ()),
    (1, 10, 1, "s", ((1, 10),)), (1, sorteio.MAX_NUMEROS + 1, 1, "s", ()), (1, 500, sorteio.MAX_QUANTOS + 1, "s", ()),
])
def test_dados_que_nao_servem_sao_um_erro(args):
    with pytest.raises(ValueError):
        sorteio.sortear(*args)
