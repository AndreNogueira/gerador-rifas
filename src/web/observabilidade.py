"""Observabilidade: o que se passa no servidor, sem guardar nada de ninguém.

DUAS COISAS:
 1. **Registo estruturado**: uma linha JSON por pedido da API e por evento (`{"t": ..., "n": "info", "ev": "pedido", "id": "a1b2c3d4", "m": "POST", "r": "/api/sessoes/{id}/gerar",
    "s": 200, "ms": 41.2, "v": "3.36.0"}`), no stdout (o Render guarda-o e deixa pesquisar). O mesmo `id` volta ao cliente no cabeçalho `X-Request-ID` e, num erro 500, no texto
    do erro, para ligar «o que o utilizador viu» a «o que o servidor registou».
 2. **Livro de erros**: as falhas agrupadas por «assinatura» (tipo, rota, estado, classe da exceção, sítio no código), com contagem e primeira/última vez, para o painel
    (`/api/admin/erros`) responder «o que está a falhar, quanto e desde quando» sem abrir os logs. Vive em memória (desde o último arranque); o que persiste são os eventos das métricas.

PRIVACIDADE (a regra do painel): **nunca** um IP, nome de ficheiro, conteúdo, User-Agent, texto de erro nem a rota com os seus valores (usa-se o modelo, `/api/sessoes/{id}/…`).
De uma exceção só se guarda a **classe** e o **sítio** (`ficheiro.py:linha:função`), nunca a mensagem (que pode trazer um nome de ficheiro ou um texto do utilizador).
Os eventos já são só códigos e números (`Metricas.evento`) e entram tal e qual. Desliga-se o registo de pedidos com `LOG_PEDIDOS=0`.
"""
from __future__ import annotations

import json
import logging
import secrets
import sys
import threading
import time
import traceback
from collections import deque
from pathlib import Path

LOGGER = logging.getLogger("rifas")
MAX_ASSINATURAS = 200
MAX_RECENTES = 50
# eventos das métricas que contam como «erro» no livro: (tipo, estados que NÃO são erro)
_EVENTOS_ERRO = {"erro_http": (), "motor_reiniciado": (), "geracao": ("ok", "livre", "a_gerar", "a_cancelar", "cancelado", "")}


def configurar(ativo: bool = True) -> None:
    """Liga o registo estruturado (uma linha JSON por registo, no stdout). Idempotente: chamar duas vezes não duplica as linhas."""
    LOGGER.setLevel(logging.INFO if ativo else logging.CRITICAL + 1)
    LOGGER.propagate = False
    if not any(getattr(h, "_rifas", False) for h in LOGGER.handlers):
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(message)s"))
        h._rifas = True                                                          # type: ignore[attr-defined]
        LOGGER.addHandler(h)


def novo_id() -> str:
    return secrets.token_hex(4)


def onde(exc: BaseException) -> str:
    """O sítio onde a exceção rebentou (`ficheiro.py:linha:função`, o último quadro): código nosso ou de uma biblioteca, nunca dados do utilizador."""
    try:
        q = traceback.extract_tb(exc.__traceback__)[-1]
        return f"{Path(q.filename).name}:{q.lineno}:{q.name}"[:90]
    except Exception:
        return "?"


class Observabilidade:
    def __init__(self, agora=time.time, versao: str = ""):
        self._agora = agora
        self.versao = versao
        self._trava = threading.Lock()
        self._assinaturas: dict[tuple, dict] = {}
        self._recentes: deque = deque(maxlen=MAX_RECENTES)
        self.inicio = int(agora())

    # ------------------------------------------------------------------ registo estruturado
    def linha(self, nivel: str, ev: str, **campos) -> None:
        """Uma linha JSON no registo. Os campos são da responsabilidade de quem chama: só códigos, números e modelos de rota."""
        if not LOGGER.isEnabledFor(logging.INFO):
            return
        d = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self._agora())), "n": nivel, "ev": ev, **campos}
        LOGGER.log(logging.ERROR if nivel == "error" else logging.WARNING if nivel == "warn" else logging.INFO, json.dumps(d, ensure_ascii=False, separators=(",", ":")))

    def pedido(self, rid: str, metodo: str, rota: str, estado: int, ms: float) -> None:
        nivel = "error" if estado >= 500 else "warn" if estado >= 400 else "info"
        self.linha(nivel, "pedido", id=rid, m=metodo, r=rota[:80], s=estado, ms=round(ms, 1), v=self.versao)

    def evento(self, tipo: str, a: str, b: str, c: str, v1: float, v2: float, v3: float) -> None:
        """O gancho de `Metricas.evento`: regista o evento (que já são só códigos) e, se é uma falha, no livro de erros."""
        campos = {"tipo": tipo}
        for nome, valor in (("a", a), ("b", b), ("c", c)):
            if valor != "":
                campos[nome] = valor
        for nome, valor in (("v1", v1), ("v2", v2), ("v3", v3)):
            if valor:
                campos[nome] = round(valor, 2)
        erro = tipo in _EVENTOS_ERRO and a not in _EVENTOS_ERRO[tipo]
        if tipo == "erro_http" and a[:1] != "5":
            erro = False                                                          # um 4xx é o utilizador a enganar-se, não uma falha do servidor
        self.linha("warn" if erro else "info", "evento", **campos)
        if erro and tipo == "erro_http":
            self.erro("http", estado=_int(a), excecao=b)
        elif erro and tipo == "geracao":
            self.erro("geracao", excecao=a, onde=b)
        elif erro:
            self.erro(tipo)

    # ------------------------------------------------------------------ livro de erros
    def erro(self, tipo: str, rota: str = "", estado: int = 0, excecao: str = "", onde: str = "") -> None:
        chave = (tipo, rota[:80], estado, excecao[:60], onde[:90])
        agora = int(self._agora())
        with self._trava:
            e = self._assinaturas.get(chave)
            if e is None:
                if len(self._assinaturas) >= MAX_ASSINATURAS:                    # cheio: sai a assinatura mais antiga
                    del self._assinaturas[min(self._assinaturas, key=lambda k: self._assinaturas[k]["ultima"])]
                e = self._assinaturas[chave] = {"tipo": tipo, "rota": chave[1], "estado": estado, "excecao": chave[3], "onde": chave[4], "n": 0, "primeira": agora, "ultima": agora}
            e["n"] += 1
            e["ultima"] = agora
            self._recentes.append((agora, tipo, chave[1], estado, chave[3]))

    def excecao(self, rid: str, metodo: str, rota: str, exc: BaseException) -> None:
        """Uma exceção que ninguém tratou (um 500): regista a classe e o sítio (NUNCA a mensagem) no registo e no livro."""
        classe, sitio = type(exc).__name__, onde(exc)
        self.erro("excecao", rota=f"{metodo} {rota}", estado=500, excecao=classe, onde=sitio)
        self.linha("error", "excecao", id=rid, m=metodo, r=rota[:80], exc=classe, onde=sitio, v=self.versao)

    def livro(self, desde: int = 0) -> dict:
        """Para o painel: as assinaturas (a mais recente primeiro) e o total, só do que aconteceu desde `desde`."""
        with self._trava:
            itens = [dict(e) for e in self._assinaturas.values() if e["ultima"] >= desde]
            recentes = [{"t": t, "tipo": tipo, "rota": rota, "estado": estado, "excecao": exc} for t, tipo, rota, estado, exc in self._recentes if t >= desde]
        itens.sort(key=lambda e: e["ultima"], reverse=True)
        return {"desde_arranque": self.inicio, "total": sum(e["n"] for e in itens), "erros": itens, "recentes": recentes[-20:][::-1]}


def _int(texto: str) -> int:
    try:
        return int(texto)
    except (TypeError, ValueError):
        return 0
