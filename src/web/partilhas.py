"""Partilhar um desenho do editor de templates por ligação (`/editor?d=<id>`): a única coisa que o site guarda de quem o usa, por isso é pouco e tem prazo.

Só existe com `DATABASE_URL` (o disco do Render é efémero: uma ligação que desaparecesse ao adormecer seria pior do que não ter a funcionalidade); sem ela o
endpoint responde 404 e o frontend esconde o botão (`/api/publico`). Guarda-se o desenho em JSON **sem imagens** (formas, textos e cores), num endereço
aleatório de 64 bits, e **nada sobre quem o partilha** (nem IP, nem data de pedido, nem língua). Prazo: 90 dias depois do último acesso; limpa-se ao guardar.
A tabela cria-se aqui (`CREATE TABLE IF NOT EXISTS`), como nas métricas. Uma ligação nova por operação: o Neon suspende a computação e corta as ligações inativas.
"""
from __future__ import annotations

import re
import secrets
import time

DIAS = 90
MAX_BYTES = 64 * 1024
ID = re.compile(r"[A-Za-z0-9_-]{8,16}")
_ESQUEMA = "CREATE TABLE IF NOT EXISTS partilhas(id TEXT PRIMARY KEY, dados TEXT NOT NULL, criado BIGINT NOT NULL, usado BIGINT NOT NULL)"


class Partilhas:
    def __init__(self, url_bd: str, relogio=time.time):
        self._url = url_bd
        self._relogio = relogio
        self._pronto = False

    def _executar(self, sql: str, args: tuple = ()) -> list[tuple]:
        import psycopg                                       # so com DATABASE_URL: sem ela a app nem precisa do driver

        with psycopg.connect(self._url, connect_timeout=10) as lig:
            if not self._pronto:
                lig.execute(_ESQUEMA)
                self._pronto = True
            cur = lig.execute(sql, args)
            return cur.fetchall() if cur.description else []

    def guardar(self, dados: str) -> str:
        """Guarda o JSON (já sem imagens e validado) e devolve o id. `ValueError` se for grande de mais."""
        if len(dados.encode("utf-8")) > MAX_BYTES:
            raise ValueError("desenho demasiado grande")
        agora = int(self._relogio())
        self._executar("DELETE FROM partilhas WHERE usado < %s", (agora - DIAS * 86400,))
        for _ in range(5):
            id_ = secrets.token_urlsafe(8)                   # 11 caracteres, 64 bits
            if not self._executar("INSERT INTO partilhas(id, dados, criado, usado) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING id",
                                  (id_, dados, agora, agora)):
                continue
            return id_
        raise RuntimeError("sem id livre")

    def obter(self, id_: str) -> str | None:
        """O JSON guardado (e renova o prazo), ou None se o id não existe ou já passou o prazo."""
        if not ID.fullmatch(id_):
            return None
        agora = int(self._relogio())
        linhas = self._executar("UPDATE partilhas SET usado = %s WHERE id = %s AND usado >= %s RETURNING dados", (agora, id_, agora - DIAS * 86400))
        return linhas[0][0] if linhas else None

    def apagar_tudo(self) -> None:
        """Para os testes."""
        self._executar("DELETE FROM partilhas")
