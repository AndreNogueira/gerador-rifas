"""Defesas de um servico PUBLICO: tamanho dos uploads (antes de os ler) e pedidos por minuto por IP."""
from __future__ import annotations

import time
from collections import deque

from fastapi import Request

from .modelos import ErroApi


class Limitador:
    """Janela deslizante de 60 s por (IP, categoria), em memoria. Sem dependencias; chega para uma so instancia."""

    JANELA = 60.0

    def __init__(self):
        self._pedidos: dict = {}

    def permitir(self, ip: str, categoria: str, maximo: int, agora: float | None = None) -> bool:
        agora = time.monotonic() if agora is None else agora
        fila = self._pedidos.setdefault((ip, categoria), deque())
        while fila and agora - fila[0] > self.JANELA:
            fila.popleft()
        if len(fila) >= maximo:
            return False
        fila.append(agora)
        if len(self._pedidos) > 5000:                      # nao crescer sem limite com muitos IPs
            for k in [k for k, v in self._pedidos.items() if not v or agora - v[-1] > self.JANELA][:2500]:
                del self._pedidos[k]
        return True


async def ler_corpo(request: Request, limite_bytes: int, texto_demasiado_grande: str) -> bytes:
    """O corpo do pedido, com um teto: recusa logo pelo Content-Length e corta o fluxo se mentir ou se nao o indicar
    (um POST de 1 GB nunca chega ao disco nem a memoria)."""
    declarado = request.headers.get("content-length", "")
    if declarado.isdigit() and int(declarado) > limite_bytes:
        raise ErroApi(413, texto_demasiado_grande, "aviso")
    partes, total = [], 0
    async for bloco in request.stream():
        total += len(bloco)
        if total > limite_bytes:
            raise ErroApi(413, texto_demasiado_grande, "aviso")
        partes.append(bloco)
    return b"".join(partes)
