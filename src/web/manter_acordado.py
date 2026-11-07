"""Manter o servico acordado no Render gratuito: o proprio servico chama o seu `/health` pelo URL publico.

O plano gratuito do Render adormece o servico passados 15 minutos sem pedidos vindos de fora (o primeiro pedido seguinte espera cerca
de 1 minuto). Um pedido a `<URL publico>/health` atravessa o proxy do Render, por isso conta como trafego: enquanto o servico esta
acordado, este ciclo mantem-no acordado (e o `/health` nao conta nas metricas nem como pagina vista).

LIMITES (ver docs/ONLINE.md): nao acorda um servico que ja adormeceu (so um pedido de fora o faz: uma visita, um monitor externo, um
deploy); e as horas gratuitas do Render (750 por mes e por conta) so chegam para UM servico acordado sempre.
"""
from __future__ import annotations

import asyncio
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class EstadoAcordado:
    ativo: bool = False
    url: str = ""
    cada_s: float = 0.0
    chamadas: int = 0
    falhas: int = 0
    ultima_em: float = 0.0          # quando foi a ultima chamada (epoch)
    ultima_ok: bool | None = None
    ultimo_ms: float = 0.0


def chamar(url: str, tempo_s: float = 20.0) -> tuple[bool, float]:
    """Um GET a `url`: (deu 200, milissegundos). Nunca levanta excecoes."""
    t0 = time.perf_counter()
    try:
        pedido = urllib.request.Request(url, headers={"User-Agent": "gerador-rifas-manter-acordado"})
        with urllib.request.urlopen(pedido, timeout=tempo_s) as r:  # noqa: S310 - o URL vem da configuracao (http/https validado)
            ok = r.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        ok = False
    return ok, (time.perf_counter() - t0) * 1000


async def ciclo(estado: EstadoAcordado, primeira_espera_s: float | None = None) -> None:
    """Chama `<url>/health` de `cada_s` em `cada_s` segundos, para sempre (cancela-se ao parar o servidor)."""
    await asyncio.sleep(estado.cada_s if primeira_espera_s is None else primeira_espera_s)
    while True:
        ok, ms = await asyncio.to_thread(chamar, f"{estado.url}/health")
        estado.chamadas += 1
        estado.falhas += 0 if ok else 1
        estado.ultima_em, estado.ultima_ok, estado.ultimo_ms = time.time(), ok, round(ms, 1)
        await asyncio.sleep(estado.cada_s)
