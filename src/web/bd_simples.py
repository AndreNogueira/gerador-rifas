"""Uma tabelinha no Postgres (`DATABASE_URL`, Neon) ou, sem ela, num SQLite local: o mesmo SQL para os dois (`%s` vira `?`).

Uma ligação nova por operação (o Neon suspende a computação e corta as ligações inativas) e o esquema cria-se na primeira (`CREATE TABLE IF NOT EXISTS`).
Usado pelas chaves da API (`chaves_api.py`) e pelos textos de SEO editáveis (`seo_bd.py`).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


class BaseSql:
    ESQUEMA: tuple = ()

    def __init__(self, url_bd: str = "", caminho: Path | None = None):
        if not url_bd and caminho is None:
            raise ValueError("precisa de url_bd ou de um caminho SQLite")
        self._url, self._caminho = url_bd, caminho
        self._pronto = False

    @property
    def persistente(self) -> bool:
        return bool(self._url)

    def _executar(self, sql: str, args: tuple = ()) -> list[tuple]:
        if self._url:
            import psycopg                                   # so com DATABASE_URL: sem ela a app nem precisa do driver

            with psycopg.connect(self._url, connect_timeout=10) as lig:
                if not self._pronto:
                    for s in self.ESQUEMA:
                        lig.execute(s)
                    self._pronto = True
                cur = lig.execute(sql, args)
                return cur.fetchall() if cur.description else []
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        lig = sqlite3.connect(self._caminho, timeout=10)
        try:
            if not self._pronto:
                for s in self.ESQUEMA:
                    lig.execute(s)
                self._pronto = True
            cur = lig.execute(sql.replace("%s", "?"), args)
            linhas = cur.fetchall() if cur.description else []
            lig.commit()
            return linhas
        finally:
            lig.close()
