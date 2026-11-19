"""As quotas do alojamento gratuito: as horas do Render no mês e o espaço da base no Neon, para ver quanto falta antes de acabarem.

 - **Horas do Render (750 por mês e por conta, mês civil UTC):** conta-se quantas horas distintas do mês têm pelo menos uma amostra do sistema (de 30 em 30 s, só com o
   serviço acordado: adormecido não há amostras, tal como o Render não conta). É uma estimativa DESTE serviço (o limite é da conta: outros serviços também gastam).
   Com o disco efémero (sem `DATABASE_URL`) só conta desde o último reinício, e a nota diz-o. Avisa quando já gastou 90 % (`RENDER_HORAS_LIMITE` muda os 750).
 - **Espaço do Neon (0,5 GB por projeto no plano grátis):** `pg_database_size` e as tabelas maiores; avisa a 80 % (`NEON_LIMITE_MB` muda os 512). Só com `DATABASE_URL`.
As horas de computação do Neon (191,9 h/mês no plano grátis) não se veem daqui: só no painel do Neon (os ciclos do serviço evitam mantê-la acordada: `docs/ADMIN.md`).
"""
from __future__ import annotations

import os
import time
from calendar import monthrange
from datetime import datetime, timezone

AVISO_HORAS = 0.9
AVISO_ESPACO = 0.8


def limite_horas() -> int:
    try:
        return max(1, int(os.environ.get("RENDER_HORAS_LIMITE", "750")))
    except ValueError:
        return 750


def limite_mb() -> int:
    try:
        return max(1, int(os.environ.get("NEON_LIMITE_MB", "512")))
    except ValueError:
        return 512


def estado(metricas, agora: float | None = None) -> dict:
    """`{render, neon, avisos}`: o gasto do mês e do espaço, a projeção até ao fim do mês e o que merece aviso."""
    agora = time.time() if agora is None else agora
    d = datetime.fromtimestamp(agora, timezone.utc)
    inicio = datetime(d.year, d.month, 1, tzinfo=timezone.utc).timestamp()
    horas_do_mes = monthrange(d.year, d.month)[1] * 24
    decorridas = (agora - inicio) / 3600
    gastas = metricas.horas_acordado(int(inicio))
    limite = limite_horas()
    desde = metricas.dados_desde()
    projecao = round(gastas / decorridas * horas_do_mes) if decorridas >= 24 and gastas else None
    render = {"mes": f"{d.year}-{d.month:02d}", "gastas": gastas, "limite": limite, "pct": round(gastas / limite * 100), "projecao": projecao,
              "horas_do_mes": horas_do_mes, "decorridas": round(decorridas), "persistente": metricas.persistente,
              "dados_desde": int(desde) if desde > inicio else None}                    # só há amostras desde aqui: o que é anterior não se contou
    espaco = metricas.espaco_bd()
    neon = None
    if espaco is not None:
        lim = limite_mb()
        neon = {**espaco, "limite_mb": lim, "pct": round(espaco["total_mb"] / lim * 100)}
    avisos: list[str] = []
    if gastas >= limite * AVISO_HORAS:
        avisos.append(f"Este serviço já gastou {gastas} das {limite} horas do mês no Render ({render['pct']} %): se a conta tiver mais serviços, as horas podem acabar antes do fim do mês.")
    if neon is not None and neon["total_mb"] >= neon["limite_mb"] * AVISO_ESPACO:
        avisos.append(f"A base de dados ocupa {neon['total_mb']:.0f} MB dos {neon['limite_mb']} MB do plano grátis do Neon ({neon['pct']} %).")
    return {"render": render, "neon": neon, "avisos": avisos}
