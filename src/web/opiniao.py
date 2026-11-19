"""Comentários dos visitantes (página «Comentários») e a ligação ao GitHub para reportar problemas.

PRIVACIDADE (a Política de privacidade das 22 línguas diz exatamente isto, `legal_opiniao.py`):
 - o comentário guarda-se com o texto, a data, o nome que a pessoa quiser mostrar (ou nenhum) e o **país** de onde veio (`CF-IPCountry`, o mesmo código de duas letras
   das estatísticas; `??` se não vier). **Nunca o endereço IP**: o limite de comentários por hora conta-se em memória e esquece-se (`LimiteHorario`);
 - a página pública nunca devolve o país nem o id interno do visitante: só o texto, o nome a mostrar e o dia; o país só o dono vê, no painel;
 - quem escolhe ficar anónimo não tem nome; quem escolhe mostrar nome e não escreve nenhum aparece como «Visitante n.º ####» (um número tirado do id do comentário).
O texto de um comentário nunca vai para os registos nem para as métricas (só «houve um comentário», anónimo ou com nome).
"""
from __future__ import annotations

import contextlib
import hashlib
import re
import secrets
import time
from collections import deque
from pathlib import Path

from .bd_simples import BaseSql

TEXTO_MIN, TEXTO_MAX = 5, 1000
NOME_MAX = 40
POR_PAGINA = 20
POR_IP_E_HORA = 3                                  # comentários por endereço numa hora (contados em memória: o endereço não se guarda)
TOTAL_POR_HORA = 100                               # e no site inteiro (trava um enxame de robôs)

_ESQUEMA = (
    "CREATE TABLE IF NOT EXISTS comentarios(id TEXT PRIMARY KEY, criado BIGINT NOT NULL, anonimo INTEGER NOT NULL, nome TEXT NOT NULL, "
    "texto TEXT NOT NULL, pais TEXT NOT NULL DEFAULT '', estado TEXT NOT NULL DEFAULT 'novo')",
    "CREATE INDEX IF NOT EXISTS ix_comentarios_criado ON comentarios(criado)",
)
# a 1.ª versao guardava o endereco IP: numa tabela que ja exista acrescenta-se o pais e APAGA-SE a coluna do IP (e tudo o que tinha)
_MIGRACOES = ("ALTER TABLE comentarios ADD COLUMN pais TEXT NOT NULL DEFAULT ''", "ALTER TABLE comentarios DROP COLUMN ip",
              "ALTER TABLE comentarios ADD COLUMN estado TEXT NOT NULL DEFAULT 'novo'")
ESTADOS = ("novo", "lido", "favorito", "escondido")   # o que o dono faz com cada comentário; «escondido» deixa de aparecer na página pública (sem o apagar)
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
        self._migrado = False

    def _executar(self, sql: str, args: tuple = ()) -> list[tuple]:
        if not self._migrado:
            super()._executar("SELECT 1")                       # cria a tabela (ou falha: a base esta em baixo e nada se marca como feito)
            for m in _MIGRACOES:
                with contextlib.suppress(Exception):            # «a coluna ja existe» / «nao existe»: o que se queria ja esta feito
                    super()._executar(m)
            super()._executar("SELECT pais, estado FROM comentarios LIMIT 1")      # falha se a migracao nao chegou ao fim: tenta-se outra vez no pedido seguinte
            self._migrado = True
        return super()._executar(sql, args)

    def criar(self, texto: str, anonimo: bool, nome: str, pais: str) -> str:
        """Guarda um comentário (já limpo e validado) e devolve o id. `pais`: o código de duas letras (ou `??`); nunca o endereço IP."""
        id_ = secrets.token_urlsafe(8)
        self._executar("INSERT INTO comentarios(id, criado, anonimo, nome, texto, pais) VALUES (%s, %s, %s, %s, %s, %s)",
                       (id_, int(self._relogio()), 1 if anonimo else 0, "" if anonimo else nome, texto, pais[:2] if pais else "??"))
        return id_

    def na_ultima_hora(self) -> int:
        return int(self._executar("SELECT COUNT(*) FROM comentarios WHERE criado >= %s", (int(self._relogio()) - 3600,))[0][0])

    def publicos(self, antes: str = "", limite: int = POR_PAGINA) -> list[dict]:
        """Os mais recentes primeiro, SÓ o que a página pública pode mostrar: o texto, o nome (ou nenhum / o número de visitante) e a data. `antes`: o cursor
        `«criado»~«id»` do último já mostrado (paginação estável mesmo com vários comentários no mesmo segundo)."""
        criado_antes, _, id_antes = antes.partition("~")
        if antes and criado_antes.isdigit() and id_antes:
            linhas = self._executar(
                "SELECT id, criado, anonimo, nome, texto FROM comentarios WHERE estado <> 'escondido' AND (criado < %s OR (criado = %s AND id < %s)) "
                "ORDER BY criado DESC, id DESC LIMIT %s", (int(criado_antes), int(criado_antes), id_antes, limite))
        else:
            linhas = self._executar("SELECT id, criado, anonimo, nome, texto FROM comentarios WHERE estado <> 'escondido' ORDER BY criado DESC, id DESC LIMIT %s", (limite,))
        saida = []
        for id_, criado, anonimo, nome, texto in linhas:
            visitante = 0 if anonimo or nome else numero_de_visitante(id_)
            saida.append({"id": id_, "criado": int(criado), "anonimo": bool(anonimo), "nome": nome, "visitante": visitante, "texto": texto})
        return saida

    def total(self) -> int:
        """Todos os comentários (o que o dono vê)."""
        return int(self._executar("SELECT COUNT(*) FROM comentarios")[0][0])

    def total_publico(self) -> int:
        """Os que aparecem na página pública (sem os escondidos)."""
        return int(self._executar("SELECT COUNT(*) FROM comentarios WHERE estado <> 'escondido'")[0][0])

    def por_ler(self) -> int:
        return int(self._executar("SELECT COUNT(*) FROM comentarios WHERE estado = 'novo'")[0][0])

    def para_admin(self, limite: int = 500, estado: str = "") -> list[dict]:
        """O que o dono vê: o id (para agir), o país de onde veio, o texto e o estado (novo, lido, favorito, escondido). Mais nada (não interessa quem escreveu).
        `estado` filtra por um deles."""
        onde, args = ("WHERE estado = %s", (estado, limite)) if estado in ESTADOS else ("", (limite,))
        return [{"id": i, "pais": p or "??", "texto": t, "estado": e} for i, p, t, e in
                self._executar(f"SELECT id, pais, texto, estado FROM comentarios {onde} ORDER BY criado DESC, id DESC LIMIT %s", args)]    # noqa: S608 - `onde` e constante

    def definir_estado(self, id_: str, estado: str) -> bool:
        """Muda o estado de um comentário; False se não existe ou o estado é inválido."""
        if estado not in ESTADOS or not self._executar("SELECT 1 FROM comentarios WHERE id = %s", (id_,)):
            return False
        self._executar("UPDATE comentarios SET estado = %s WHERE id = %s", (estado, id_))
        return True

    def marcar_lidos(self) -> int:
        """Todos os «novo» passam a «lido»; devolve quantos."""
        n = self.por_ler()
        if n:
            self._executar("UPDATE comentarios SET estado = 'lido' WHERE estado = 'novo'")
        return n

    def apagar(self, id_: str) -> bool:
        existia = bool(self._executar("SELECT 1 FROM comentarios WHERE id = %s", (id_,)))
        if existia:
            self._executar("DELETE FROM comentarios WHERE id = %s", (id_,))
        return existia
