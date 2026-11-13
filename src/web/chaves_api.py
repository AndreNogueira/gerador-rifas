"""As chaves da API pública (`/api/v1`): criam-se no painel de administração (`/api/admin/chaves`), nunca no repositório.

Da chave só se guarda o **SHA-256** (a chave em claro vê-se uma única vez, ao criá-la; nunca vai para um log, para as métricas ou para o painel) e um
prefixo curto para o dono a reconhecer. Cada chave tem uma quota de **números por dia** (UTC). Postgres com `DATABASE_URL` (Neon: sobrevive ao Render
adormecer), senão SQLite local (efémero no Render, mas a API só existe se o dono criar chaves). Uma ligação nova por operação, como em `partilhas.py`.
Uma chave válida fica 60 s em cache (uma revogação feita neste processo vale logo; noutro, no máximo 60 s depois).
"""
from __future__ import annotations

import hashlib
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

PREFIXO = "rk_"
CACHE_S = 60
QUOTA_PADRAO = 100_000                                   # números por dia, por chave
_ESQUEMA = (
    "CREATE TABLE IF NOT EXISTS api_chaves(id TEXT PRIMARY KEY, hash TEXT UNIQUE NOT NULL, prefixo TEXT NOT NULL, nome TEXT NOT NULL, "
    "criada BIGINT NOT NULL, ativa INTEGER NOT NULL, quota BIGINT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS api_uso(chave_id TEXT NOT NULL, dia BIGINT NOT NULL, numeros BIGINT NOT NULL, lotes INTEGER NOT NULL, PRIMARY KEY(chave_id, dia))",
)


@dataclass(frozen=True)
class InfoChave:
    id: str
    nome: str
    prefixo: str
    criada: int
    ativa: bool
    quota: int


def _hash(chave: str) -> str:
    return hashlib.sha256(chave.encode("utf-8")).hexdigest()


def _dia(agora: float) -> int:
    return int(agora // 86400)


class Chaves:
    def __init__(self, url_bd: str = "", caminho: Path | None = None, relogio=time.time):
        if not url_bd and caminho is None:
            raise ValueError("precisa de url_bd ou de um caminho SQLite")
        self._url, self._caminho, self._relogio = url_bd, caminho, relogio
        self._pronto = False
        self._cache: dict = {}                            # hash -> (InfoChave, expira)

    @property
    def persistente(self) -> bool:
        return bool(self._url)

    # -- base de dados (Postgres ou SQLite: o mesmo SQL, `%s` vira `?`)
    def _executar(self, sql: str, args: tuple = ()) -> list[tuple]:
        if self._url:
            import psycopg                                   # so com DATABASE_URL

            with psycopg.connect(self._url, connect_timeout=10) as lig:
                if not self._pronto:
                    for s in _ESQUEMA:
                        lig.execute(s)
                    self._pronto = True
                cur = lig.execute(sql, args)
                return cur.fetchall() if cur.description else []
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        lig = sqlite3.connect(self._caminho, timeout=10)
        try:
            if not self._pronto:
                for s in _ESQUEMA:
                    lig.execute(s)
                self._pronto = True
            cur = lig.execute(sql.replace("%s", "?"), args)
            linhas = cur.fetchall() if cur.description else []
            lig.commit()
            return linhas
        finally:
            lig.close()

    @staticmethod
    def _info(linha: tuple) -> InfoChave:
        return InfoChave(id=linha[0], nome=linha[1], prefixo=linha[2], criada=int(linha[3]), ativa=bool(linha[4]), quota=int(linha[5]))

    _COLUNAS = "id, nome, prefixo, criada, ativa, quota"

    # -- gestao (painel de administracao)
    def criar(self, nome: str, quota: int = QUOTA_PADRAO) -> tuple[InfoChave, str]:
        """(info, chave em claro). A chave em claro so existe aqui: nao se guarda."""
        chave = PREFIXO + secrets.token_urlsafe(24)
        id_ = _hash(chave)[:10]
        self._executar("INSERT INTO api_chaves(id, hash, prefixo, nome, criada, ativa, quota) VALUES (%s, %s, %s, %s, %s, 1, %s)",
                       (id_, _hash(chave), chave[:7], nome, int(self._relogio()), quota))
        return InfoChave(id_, nome, chave[:7], int(self._relogio()), True, quota), chave

    def listar(self) -> list[InfoChave]:
        return [self._info(x) for x in self._executar(f"SELECT {self._COLUNAS} FROM api_chaves ORDER BY criada DESC")]

    def revogar(self, id_: str) -> bool:
        linhas = self._executar("UPDATE api_chaves SET ativa = 0 WHERE id = %s AND ativa = 1 RETURNING id", (id_,))
        self._cache.clear()
        return bool(linhas)

    # -- uso (API publica)
    def autenticar(self, chave: str) -> InfoChave | None:
        """A chave valida e ativa, ou None. Aceita so o formato `rk_...` (antes de tocar na base de dados)."""
        if not chave.startswith(PREFIXO) or not 20 <= len(chave) <= 80 or not chave.isascii():
            return None
        h, agora = _hash(chave), self._relogio()
        em_cache = self._cache.get(h)
        if em_cache and em_cache[1] > agora:
            return em_cache[0]
        linhas = self._executar(f"SELECT {self._COLUNAS} FROM api_chaves WHERE hash = %s AND ativa = 1", (h,))
        info = self._info(linhas[0]) if linhas else None
        if info is not None:
            if len(self._cache) > 500:
                self._cache.clear()
            self._cache[h] = (info, agora + CACHE_S)
        return info

    def consumir(self, info: InfoChave, numeros: int) -> bool:
        """Gasta `numeros` da quota de hoje de forma atomica. False (e nada se gasta) se passaria da quota."""
        if numeros > info.quota:
            return False
        dia = _dia(self._relogio())
        linhas = self._executar(
            "INSERT INTO api_uso(chave_id, dia, numeros, lotes) VALUES (%s, %s, %s, 1) ON CONFLICT (chave_id, dia) DO UPDATE "
            "SET numeros = api_uso.numeros + EXCLUDED.numeros, lotes = api_uso.lotes + 1 WHERE api_uso.numeros + EXCLUDED.numeros <= %s RETURNING numeros",
            (info.id, dia, numeros, info.quota))
        return bool(linhas)

    def devolver(self, info: InfoChave, numeros: int) -> None:
        """Desfaz um `consumir` (o lote nao chegou a arrancar)."""
        dia = _dia(self._relogio())
        self._executar("UPDATE api_uso SET numeros = CASE WHEN numeros >= %s THEN numeros - %s ELSE 0 END, lotes = CASE WHEN lotes > 0 THEN lotes - 1 ELSE 0 END "
                       "WHERE chave_id = %s AND dia = %s", (numeros, numeros, info.id, dia))

    def uso_hoje(self, info: InfoChave) -> tuple[int, int]:
        """(numeros, lotes) gastos hoje."""
        linhas = self._executar("SELECT numeros, lotes FROM api_uso WHERE chave_id = %s AND dia = %s", (info.id, _dia(self._relogio())))
        return (int(linhas[0][0]), int(linhas[0][1])) if linhas else (0, 0)
