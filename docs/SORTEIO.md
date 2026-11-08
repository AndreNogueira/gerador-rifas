# Sorteio verificável

A página **Sorteio** (`/sorteio`) sorteia números de forma que **qualquer pessoa possa repetir o sorteio e obter o mesmo resultado**. Faz-se tudo no browser (nada vai ao servidor) e a ligação que se copia repete o mesmo sorteio.

## O que decide o resultado

Só quatro coisas: o intervalo de números (e os que se saltam), **quantos** se sorteiam e a **semente pública**. Não há acaso escondido: com os mesmos quatro dados sai sempre o mesmo resultado.

## O algoritmo (a referência é `src/core/sorteio.py`; o browser faz o mesmo em `sorteador.ts`)

1. Os números possíveis são os inteiros de `de` a `ate` (inclusive) menos os que se saltam, por ordem crescente (`N` números).
2. Um inteiro em `[0, m)` com o contador `c` sai de `SHA-256(semente + ":" + c + ":" + j)`, para `j = 0, 1, 2…`: tomam-se os 8 primeiros bytes (big-endian) como `x`; se `x < 2⁶⁴ − (2⁶⁴ mod m)` devolve-se `x mod m`; senão tenta-se o `j` seguinte (a rejeição evita enviesar o resultado).
3. Baralha-se parcialmente: para `i = 0 … quantos−1`, `r` é um inteiro em `[0, N−i)` com o contador `i`, e trocam-se as posições `i` e `i+r`.
4. Os sorteados são as primeiras `quantos` posições, pela ordem em que saem (1.º, 2.º…).

A semente é o texto escrito, sem espaços nas pontas, em UTF-8 (até 200 caracteres). Limites: até 1 000 000 de números e 100 sorteados.

## Verificar sem o site

```python
from core import sorteio          # com src/ no caminho
sorteio.sortear(1, 100, 3, "semente-um")        # [29, 38, 74]
sorteio.sortear(1, 500, 4, "Lotaria 2026-12-24 12 34 45", ((13, 13), (100, 110)))   # [495, 382, 7, 329]
```

Os mesmos vetores estão em `tests/test_sorteio.py` (Python) e `src/web/frontend/src/sorteador.test.ts` (TypeScript): se um mudar, o outro tem de mudar; é assim que se garante que o site e a referência dão o mesmo.

## A semente é o que torna o sorteio honesto

O algoritmo é público, por isso **quem escolhe a semente controla o resultado**. Para ninguém poder escolher uma semente que lhe dê um número favorável, a semente tem de ser algo que:

- **ninguém controla** (nem quem organiza a rifa); e
- **só se conhece depois de fechadas as vendas** (e de se saber que números foram vendidos).

Boas fontes: o resultado de uma lotaria pública (os números do Euromilhões, da Lotaria Nacional…) ou a aleatoriedade pública do [drand](https://drand.love) (o botão «Usar a semente do drand» põe `drand:<ronda>:<aleatoriedade>`; para ser verificável anuncie **antes** a ronda ou a hora). **Combine a fonte da semente com os participantes antes de abrir as vendas.**

## O que isto não é

É uma ferramenta de transparência, **não** um sorteio com valor legal: as regras de uma rifa (licença da câmara municipal, regras para associações) são da responsabilidade de quem a organiza (ver os Termos do site e `docs/PLANO_PRODUTO.md` §5).
