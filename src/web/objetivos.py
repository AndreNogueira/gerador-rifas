"""Objetivos diários: o dono define uma meta por dia para os números que acompanha (sessões, gerações, números gerados…) e o painel e o relatório diário dizem se
foi atingida, a média dos últimos 7 dias face à meta e em quantos desses dias se cumpriu.

Só há metas «de pelo menos» para contagens (não para erros). Guardam-se na tabela `objetivos` (no Neon com `DATABASE_URL`, senão SQLite local); só o dono as muda
(`PUT /api/admin/objetivos`); a leitura vê. As metas são números do dono, sem dados de visitantes.
"""
from __future__ import annotations

from datetime import date

from .bd_simples import BaseSql

# chave -> (painel da «Evolução», série ou None = soma das séries, rótulo): os números de contagem que se podem pôr como objetivo
KPIS: dict[str, tuple[str, str | None, str]] = {
    "sessoes": ("sessoes", None, "Sessões"),
    "geracoes": ("geracoes", None, "Gerações pedidas"),
    "numeros": ("numeros", None, "Números gerados"),
    "descargas": ("descargas", None, "Descargas"),
    "paginas_vistas": ("paginas_vistas", "Pessoas", "Páginas vistas (pessoas)"),
    "comentarios": ("comentarios", None, "Comentários"),
}
META_MAX = 1_000_000_000
JANELA = 7


class Objetivos(BaseSql):
    ESQUEMA = ("CREATE TABLE IF NOT EXISTS objetivos(chave TEXT PRIMARY KEY, meta DOUBLE PRECISION NOT NULL)",)

    def todos(self) -> dict[str, float]:
        return {c: float(m) for c, m in self._executar("SELECT chave, meta FROM objetivos") if c in KPIS}

    def definir(self, chave: str, meta: float) -> None:
        if chave not in KPIS or not 0 < meta <= META_MAX:
            raise ValueError("objetivo invalido")
        self._executar("INSERT INTO objetivos(chave, meta) VALUES (%s, %s) ON CONFLICT (chave) DO UPDATE SET meta = excluded.meta", (chave, float(meta)))

    def apagar(self, chave: str) -> None:
        self._executar("DELETE FROM objetivos WHERE chave = %s", (chave,))


def diarios(paineis: dict[str, dict], chave: str, dias: int) -> list[float]:
    """O valor de cada um dos `dias` dias do número `chave` (a soma das séries escolhidas do painel); zeros se o painel não tem séries (nunca houve esse evento)."""
    painel, serie, _ = KPIS[chave]
    p = paineis.get(painel)
    escolhidas = [s for s in (p["series"] if p else []) if serie is None or s["nome"] == serie]
    return [float(sum((s["valores"][i] or 0) for s in escolhidas)) for i in range(dias)]


def avaliar(ev: dict, metas: dict[str, float]) -> list[dict]:
    """Para cada número com meta: a meta, o valor do último dia (`ontem`), a média e os dias cumpridos dos últimos 7 (o último incluído) e se o último dia a cumpriu.
    `ev` é uma `Metricas.evolucao` cujo último dia é o que se avalia."""
    paineis = {p["id"]: p for p in ev["paineis"]}
    saida = []
    for chave, (_, _, rotulo) in KPIS.items():
        meta = metas.get(chave)
        v = diarios(paineis, chave, len(ev["dias_lista"]))
        ultimos = v[-JANELA:]
        ontem = v[-1] if v else 0.0
        saida.append({"chave": chave, "rotulo": rotulo, "meta": meta, "ontem": ontem, "media7": sum(ultimos) / len(ultimos) if ultimos else 0.0,
                      "dias_cumpridos": sum(1 for x in ultimos if meta is not None and x >= meta), "dias": len(ultimos),
                      "atingido": None if meta is None else ontem >= meta,
                      "pct": None if meta is None else round(ontem / meta * 100)})
    return saida


def estado(metricas, extras, objetivos, fuso, agora: float | None = None) -> dict:
    """O que o painel mostra: cada número com a meta (ou sem), os valores de ontem e dos últimos 7 dias."""
    import time
    from datetime import datetime, timedelta

    from .relatorio import janela_do_dia

    agora = time.time() if agora is None else agora
    ontem: date = datetime.fromtimestamp(agora, fuso).date() - timedelta(days=1)
    desvio, _, fim = janela_do_dia(ontem, fuso)
    ev = metricas.evolucao(JANELA + 1, desvio, extras, fim)
    return {"dia": ontem.isoformat(), "kpis": avaliar(ev, objetivos.todos() if objetivos is not None else {})}
