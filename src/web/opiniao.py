"""Comentários dos visitantes (página «Comentários») e a ligação ao GitHub para reportar problemas.

PRIVACIDADE (a Política de privacidade das 22 línguas diz exatamente isto, `legal_opiniao.py`):
 - o comentário guarda-se com o texto, o nome que a pessoa quiser mostrar (ou nenhum) e o **endereço IP**, que só o dono vê no painel (para travar abusos) e
   que se APAGA do comentário passados `DIAS_IP` dias; o comentário em si continua;
 - a página pública nunca devolve o IP nem o id interno do visitante: só o texto, o nome a mostrar e o dia;
 - quem escolhe ficar anónimo não tem nome; quem escolhe mostrar nome e não escreve nenhum aparece como «Visitante n.º ####» (um número tirado do id do comentário).
O texto de um comentário nunca vai para os registos nem para as métricas (só «houve um comentário», anónimo ou com nome).
"""
from __future__ import annotations

import hashlib
import re
import secrets
import time
from collections import deque
from pathlib import Path

from .bd_simples import BaseSql

DIAS_IP = 90
TEXTO_MIN, TEXTO_MAX = 5, 1000
NOME_MAX = 40
POR_PAGINA = 20
POR_IP_E_HORA = 3                                  # comentários por IP numa hora
TOTAL_POR_HORA = 100                               # e no site inteiro (trava um enxame de robôs)

_ESQUEMA = (
    "CREATE TABLE IF NOT EXISTS comentarios(id TEXT PRIMARY KEY, criado BIGINT NOT NULL, anonimo INTEGER NOT NULL, nome TEXT NOT NULL, "
    "texto TEXT NOT NULL, ip TEXT NOT NULL)",
    "CREATE INDEX IF NOT EXISTS ix_comentarios_criado ON comentarios(criado)",
)
_CONTROLO = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‏‪-‮⁦-⁩]")      # controlo e marcas que invertem/escondem texto


def limpar_texto(t: str, maximo: int, uma_linha: bool = False) -> str:
    """Tira controlo e marcas invisíveis, junta espaços e limita as linhas em branco; corta em `maximo`."""
    t = _CONTROLO.sub("", t.replace("\r\n", "\n").replace("\r", "\n"))
    if uma_linha:
        return re.sub(r"\s+", " ", t).strip()[:maximo]
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t[:maximo]


def numero_de_visitante(id_: str) -> int:
    """O «Visitante n.º ####» de um comentário sem nome: 4 dígitos tirados do id (sempre o mesmo para o mesmo comentário, sem ligar comentários entre si)."""
    return 1000 + int(hashlib.sha256(id_.encode()).hexdigest()[:8], 16) % 9000


class LimiteHorario:
    """N ocorrências por chave na última hora, em memória (reinicia com o servidor: serve para travar excessos, não para contar)."""

    def __init__(self, maximo: int, janela_s: float = 3600.0):
        self.maximo, self.janela = maximo, janela_s
        self._filas: dict[str, deque] = {}

    def permitir(self, chave: str, agora: float | None = None) -> bool:
        agora = time.monotonic() if agora is None else agora
        fila = self._filas.setdefault(chave, deque())
        while fila and agora - fila[0] > self.janela:
            fila.popleft()
        if len(fila) >= self.maximo:
            return False
        fila.append(agora)
        if len(self._filas) > 5000:                # não crescer sem limite
            for k in [k for k, v in self._filas.items() if not v or agora - v[-1] > self.janela][:2500]:
                del self._filas[k]
        return True


class Comentarios(BaseSql):
    ESQUEMA = _ESQUEMA

    def __init__(self, url_bd: str = "", caminho: Path | None = None, relogio=time.time):
        super().__init__(url_bd, caminho)
        self._relogio = relogio

    def criar(self, texto: str, anonimo: bool, nome: str, ip: str) -> str:
        """Guarda um comentário (já limpo e validado) e devolve o id. Aproveita para apagar os IPs que passaram do prazo."""
        agora = int(self._relogio())
        self._executar("UPDATE comentarios SET ip = '' WHERE ip <> '' AND criado < %s", (agora - DIAS_IP * 86400,))
        id_ = secrets.token_urlsafe(8)
        self._executar("INSERT INTO comentarios(id, criado, anonimo, nome, texto, ip) VALUES (%s, %s, %s, %s, %s, %s)",
                       (id_, agora, 1 if anonimo else 0, "" if anonimo else nome, texto, ip))
        return id_

    def recentes_do_ip(self, ip: str) -> int:
        return int(self._executar("SELECT COUNT(*) FROM comentarios WHERE ip = %s AND criado >= %s", (ip, int(self._relogio()) - 3600))[0][0])

    def na_ultima_hora(self) -> int:
        return int(self._executar("SELECT COUNT(*) FROM comentarios WHERE criado >= %s", (int(self._relogio()) - 3600,))[0][0])

    def publicos(self, antes: str = "", limite: int = POR_PAGINA) -> list[dict]:
        """Os mais recentes primeiro, SÓ o que a página pública pode mostrar: o texto, o nome (ou nenhum / o número de visitante) e a data. `antes`: o cursor
        `«criado»~«id»` do último já mostrado (paginação estável mesmo com vários comentários no mesmo segundo)."""
        criado_antes, _, id_antes = antes.partition("~")
        if antes and criado_antes.isdigit() and id_antes:
            linhas = self._executar(
                "SELECT id, criado, anonimo, nome, texto FROM comentarios WHERE criado < %s OR (criado = %s AND id < %s) "
                "ORDER BY criado DESC, id DESC LIMIT %s", (int(criado_antes), int(criado_antes), id_antes, limite))
        else:
            linhas = self._executar("SELECT id, criado, anonimo, nome, texto FROM comentarios ORDER BY criado DESC, id DESC LIMIT %s", (limite,))
        saida = []
        for id_, criado, anonimo, nome, texto in linhas:
            visitante = 0 if anonimo or nome else numero_de_visitante(id_)
            saida.append({"id": id_, "criado": int(criado), "anonimo": bool(anonimo), "nome": nome, "visitante": visitante, "texto": texto})
        return saida

    def total(self) -> int:
        return int(self._executar("SELECT COUNT(*) FROM comentarios")[0][0])

    def para_admin(self, limite: int = 500) -> list[dict]:
        """O que o dono vê: o id (para apagar), o IP e o texto. Mais nada (não interessa quem escreveu)."""
        return [{"id": i, "ip": ip, "texto": t} for i, ip, t in
                self._executar("SELECT id, ip, texto FROM comentarios ORDER BY criado DESC, id DESC LIMIT %s", (limite,))]

    def apagar(self, id_: str) -> bool:
        existia = bool(self._executar("SELECT 1 FROM comentarios WHERE id = %s", (id_,)))
        if existia:
            self._executar("DELETE FROM comentarios WHERE id = %s", (id_,))
        return existia
