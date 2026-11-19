"""O registo de ações do painel: quem (o dono ou o acesso só de leitura) fez o quê e quando, para sempre (400 dias), mesmo depois de os eventos brutos se apagarem.

Cada linha tem a hora, o papel (`admin` ou `leitura`), um código de ação e um detalhe curto: o id (aleatório) do comentário, o nome da chave da API, a chave do texto de SEO e a
língua, o número com objetivo… Nunca dados de visitantes (o texto dos comentários não entra) nem a palavra-passe nem a chave da API em claro. As **tentativas falhadas e os bloqueios
de entrada não se guardam aqui** (um ataque encheria a tabela): contam-se nas métricas, em «Acessos ao painel». Só o dono altera coisas; a leitura só entra e consulta.
"""
from __future__ import annotations

import time

from .bd_simples import BaseSql

RETENCAO_S = 400 * 86400
DETALHE_MAX = 120

ACOES = {
    "entrou": "Entrou no painel",
    "entrou_leitura": "Entrou no painel (só leitura)",
    "comentario_apagado": "Apagou um comentário",
    "comentario_novo": "Marcou um comentário como novo",
    "comentario_lido": "Marcou um comentário como lido",
    "comentario_favorito": "Marcou um comentário como favorito",
    "comentario_escondido": "Escondeu um comentário da página pública",
    "comentarios_lidos": "Marcou todos os comentários como lidos",
    "chave_criada": "Criou uma chave da API",
    "chave_revogada": "Revogou uma chave da API",
    "seo_editado": "Editou um texto de SEO",
    "seo_reposto": "Repôs um texto de SEO",
    "objetivo": "Mudou um objetivo diário",
    "relatorio_teste": "Enviou um relatório de teste por e-mail",
    "alerta_teste": "Enviou um alerta de teste por e-mail",
    "copia_manual": "Fez uma cópia de segurança dos dados",
}


class Auditoria(BaseSql):
    ESQUEMA = (
        "CREATE TABLE IF NOT EXISTS auditoria(ts BIGINT NOT NULL, acao TEXT NOT NULL, papel TEXT NOT NULL, detalhe TEXT NOT NULL)",
        "CREATE INDEX IF NOT EXISTS ix_auditoria_ts ON auditoria(ts)",
    )

    def registar(self, acao: str, papel: str, detalhe: str = "", agora: float | None = None) -> None:
        agora = time.time() if agora is None else agora
        self._executar("INSERT INTO auditoria(ts, acao, papel, detalhe) VALUES (%s, %s, %s, %s)", (int(agora), acao[:60], papel[:20], detalhe[:DETALHE_MAX]))
        self._executar("DELETE FROM auditoria WHERE ts < %s", (int(agora - RETENCAO_S),))              # o registo nao cresce para sempre

    def recentes(self, limite: int = 200) -> list[dict]:
        return [{"ts": int(t), "acao": a, "texto": ACOES.get(a, a), "papel": p, "detalhe": d}
                for t, a, p, d in self._executar("SELECT ts, acao, papel, detalhe FROM auditoria ORDER BY ts DESC LIMIT %s", (max(1, min(limite, 1000)),))]

    def total(self) -> int:
        return int(self._executar("SELECT COUNT(*) FROM auditoria")[0][0])
