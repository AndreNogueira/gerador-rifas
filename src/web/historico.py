"""O histórico permanente por dia: uma linha-resumo por dia na base, para ver a evolução de meses e anos.

PORQUÊ: os eventos brutos apagam-se aos 90 dias e os pedidos/sistema aos 35 (`metricas.py`). Depois da meia-noite (00:05, `RELATORIO_FUSO`) grava-se o que a vista
«Evolução diária» mostra para o dia que acabou (cada série do dia, só valores diferentes de zero) na tabela `historico_diario`; na primeira vez grava também os dias
que ainda estão na base (até 90). Cresce ~3 KB por dia (≈ 1 MB por ano). A vista com mais de 90 dias lê daqui (`GET /api/admin/evolucao?dias=365`).

NOTAS: os dias são os do fuso do relatório (não os do browser); o dia em curso não aparece; só há dias desde que o histórico existe; a janela de 90 dias do início usa
o desvio horário de ontem (um dia de mudança de hora fica uma hora desfasado). Só agregados, como o resto do painel. Sem `DATABASE_URL` vive no disco efémero.
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timedelta
from datetime import time as hora_do_dia
from zoneinfo import ZoneInfo

from .bd_simples import BaseSql
from .metricas import DIAS_MAXIMOS, novo_painel
from .relatorio import DEPOIS_DAS, janela_do_dia

DIAS_HISTORICO_MAX = 730                     # dois anos


class HistoricoDiario(BaseSql):
    feito_ate = ""                       # o último dia («aaaa-mm-dd») já tratado, em memória: depois disso as rondas de 5 minutos nem tocam na base (o Neon pode adormecer)
    ESQUEMA = ("CREATE TABLE IF NOT EXISTS historico_diario(dia TEXT PRIMARY KEY, dados TEXT NOT NULL, criado BIGINT NOT NULL)",)

    def gravar(self, dia: str, dados: dict, agora: float) -> None:
        self._executar("INSERT INTO historico_diario(dia, dados, criado) VALUES (%s, %s, %s) "
                       "ON CONFLICT (dia) DO UPDATE SET dados = excluded.dados, criado = excluded.criado",
                       (dia, json.dumps(dados, separators=(",", ":"), ensure_ascii=False), int(agora)))

    def dias(self, desde: str, ate: str) -> set[str]:
        return {r[0] for r in self._executar("SELECT dia FROM historico_diario WHERE dia >= %s AND dia <= %s", (desde, ate))}

    def ler(self, desde: str, ate: str) -> list[tuple[str, dict]]:
        return [(r[0], json.loads(r[1])) for r in self._executar(
            "SELECT dia, dados FROM historico_diario WHERE dia >= %s AND dia <= %s ORDER BY dia", (desde, ate))]

    def total(self) -> int:
        return int(self._executar("SELECT COUNT(*) FROM historico_diario")[0][0])

    def primeiro(self) -> str | None:
        r = self._executar("SELECT MIN(dia) FROM historico_diario")
        return r[0][0] if r and r[0][0] else None


def resumo_do_dia(ev: dict, i: int) -> dict:
    """`{painel: {série: valor}}` do dia de índice `i` de uma `evolucao`: só os valores que não são zero nem «sem dados»."""
    saida: dict[str, dict[str, float]] = {}
    for p in ev["paineis"]:
        valores = {s["nome"]: s["valores"][i] for s in p["series"] if s["valores"][i]}
        if valores:
            saida[p["id"]] = valores
    versoes = [v["versao"] for v in ev.get("versoes", []) if v["dia"] == ev["dias_lista"][i]]
    if versoes:
        saida["_versoes"] = versoes                                # as versoes que chegaram nesse dia (para as marcas nos graficos da vista de meses)
    return saida


def _inicio_do_dia(dia: date, fuso: ZoneInfo) -> int:
    return int(datetime.combine(dia, hora_do_dia(0), tzinfo=fuso).timestamp())


def gravar_pendentes(historico, metricas, extras, fuso: ZoneInfo, agora: float | None = None) -> int:
    """Depois das 00:05 grava o dia de ontem (e, na 1.ª vez, os dias que ainda estão na base). Devolve quantos dias gravou."""
    agora = time.time() if agora is None else agora
    local = datetime.fromtimestamp(agora, fuso)
    if historico is None or local.time() < DEPOIS_DAS:
        return 0
    ontem = local.date() - timedelta(days=1)
    if historico.feito_ate == ontem.isoformat():
        return 0                                                   # já tratado: nenhuma consulta até à meia-noite seguinte
    existentes = historico.dias((ontem - timedelta(days=DIAS_MAXIMOS)).isoformat(), ontem.isoformat())
    if ontem.isoformat() in existentes:
        historico.feito_ate = ontem.isoformat()
        return 0
    desvio, _, fim = janela_do_dia(ontem, fuso)
    ev = metricas.evolucao(DIAS_MAXIMOS, desvio, extras, fim)
    if getattr(metricas, "erro_bd", False):
        return 0                                                   # a base em baixo daria zeros falsos: tenta-se daqui a 5 minutos
    n = 0
    for i, dia in enumerate(ev["dias_lista"]):
        if dia in existentes or _inicio_do_dia(date.fromisoformat(dia), fuso) < ev["dados_desde"]:      # antes do 1.º registo está vazio por não haver dados
            continue
        historico.gravar(dia, resumo_do_dia(ev, i), agora)
        n += 1
    historico.feito_ate = ontem.isoformat()                        # (um dia anterior ao 1.º registo não tem nada para gravar: também é «tratado»)
    return n


def evolucao_historica(historico, metricas, extras, fuso: ZoneInfo, dias: int, agora: float | None = None) -> dict:
    """A mesma estrutura de `Metricas.evolucao`, mas lida do histórico (os últimos `dias` dias até ontem): painéis, séries por dia, `origem: «historico»`."""
    agora = time.time() if agora is None else agora
    dias = max(1, min(int(dias), DIAS_HISTORICO_MAX))
    ontem = datetime.fromtimestamp(agora, fuso).date() - timedelta(days=1)
    primeiro = ontem - timedelta(days=dias - 1)
    linhas = dict(historico.ler(primeiro.isoformat(), ontem.isoformat()))
    lista = [(primeiro + timedelta(days=i)).isoformat() for i in range(dias)]
    meta = metricas.evolucao(1, 0, extras)["paineis"]              # os títulos, as explicações e os tipos de hoje
    paineis = []
    for p in meta:
        total: dict[str, float] = {}
        for d in lista:
            for nome, v in linhas.get(d, {}).get(p["id"], {}).items():
                total[nome] = total.get(nome, 0) + v
        series = {n: [linhas[d][p["id"]].get(n, 0) if d in linhas and p["id"] in linhas[d] else (0 if d in linhas else None) for d in lista]
                  for n in sorted(total, key=lambda n: -total[n])}
        agregados = {s["nome"]: s["agregado"] for s in p["series"]}
        paineis.append(novo_painel(p["grupo"], p["id"], p["titulo"], series, p["explica"], p["tipo"], p["unidade"], p["agregado"], p["rotulos"], agregados))
    primeiro_dia = historico.primeiro()
    versoes = [{"dia": d, "versao": v} for d in lista for v in linhas.get(d, {}).get("_versoes", [])]
    return {"dias": dias, "fuso_min": 0, "dias_lista": lista, "origem": "historico", "dias_com_dados": len(linhas), "versoes": versoes,
            "retencao": {"eventos_dias": DIAS_HISTORICO_MAX, "sistema_dias": DIAS_HISTORICO_MAX},
            "dados_desde": _inicio_do_dia(date.fromisoformat(primeiro_dia), fuso) if primeiro_dia else int(agora), "paineis": paineis}
