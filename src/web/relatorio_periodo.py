"""Os resumos SEMANAL e MENSAL por e-mail: a mesma coisa do relatório diário, somada por semana (segunda a domingo) ou por mês, face ao período anterior.

Lêem do histórico permanente (`historico.py`, um resumo por dia), por isso funcionam depois dos 90 dias da base e precisam de o dia em que o período acaba já
estar gravado. Enviam-se na segunda-feira (a semana que acabou) e no dia 1 (o mês que acabou), depois das 00:05; se o serviço dormia, saem quando acordar (a semana até
à segunda seguinte; o mês nos primeiros 7 dias). A reserva está na mesma tabela `relatorios` (chaves `semana:2026-11-09`, `mes:2026-10`): nunca duplicam. `RELATORIOS_PERIODICOS=0` desliga-os.
Um período só sai se tiver pelo menos metade dos dias gravados (o histórico só existe desde que foi ligado). Cada série soma (contagens), faz a média ou o pico
conforme o seu `agregado`, tal como o resumo do painel.
"""
from __future__ import annotations

import os
import time
import urllib.request
from calendar import monthrange
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import config, email_envio
from .relatorio import (DEPOIS_DAS, DESTAQUES, ESPERA_APOS_FALHA_S, MESES, EstadoRelatorio, ErroRelatorio, _num, _variacao, assunto, ativo, em_html,
                        em_texto, log, miniatura)

TIPOS = ("dia", "semana", "mes")


def periodicos_ativos() -> bool:
    return ativo() and os.environ.get("RELATORIOS_PERIODICOS", "").strip().lower() not in ("0", "nao", "não", "false", "off")


def semana_de(dia: date) -> tuple[date, date]:
    """Segunda e domingo da semana que contém `dia`."""
    ini = dia - timedelta(days=dia.weekday())
    return ini, ini + timedelta(days=6)


def mes_de(dia: date) -> tuple[date, date]:
    return dia.replace(day=1), dia.replace(day=monthrange(dia.year, dia.month)[1])


def periodo_de(tipo: str, dia: date) -> tuple[date, date]:
    return semana_de(dia) if tipo == "semana" else mes_de(dia)


def anterior(tipo: str, ini: date) -> tuple[date, date]:
    """O período imediatamente antes (a semana anterior, ou o mês anterior inteiro)."""
    return periodo_de(tipo, ini - timedelta(days=1))


def ultimo_completo(tipo: str, hoje: date) -> tuple[date, date]:
    """O último período que já acabou à data `hoje`."""
    return periodo_de(tipo, hoje - timedelta(days=hoje.weekday() + 1)) if tipo == "semana" else mes_de(hoje.replace(day=1) - timedelta(days=1))


def chave_de(tipo: str, ini: date) -> str:
    return f"semana:{ini.isoformat()}" if tipo == "semana" else f"mes:{ini.strftime('%Y-%m')}"


def _dias(ini: date, fim: date) -> list[str]:
    return [(ini + timedelta(days=i)).isoformat() for i in range((fim - ini).days + 1)]


def _agregar(valores: list[float | None], como: str) -> float | None:
    reais = [v for v in valores if v is not None]
    if not reais:
        return None
    return max(reais) if como == "max" else sum(reais) / len(reais) if como == "media" else sum(reais)


def titulos(tipo: str, ini: date, fim: date) -> tuple[str, str]:
    """`(titulo, curto)` do período."""
    if tipo == "mes":
        t = f"{MESES[ini.month - 1]} de {ini.year}"
        return t, f"{MESES[ini.month - 1]} de {ini.year}"
    de, ate = f"{ini.day} {MESES[ini.month - 1][:3]}", f"{fim.day} {MESES[fim.month - 1][:3]} {fim.year}"
    return f"Semana de {de} a {ate}", f"semana {de} – {ate}"


def montar_periodo(historico, metricas, extras, tipo: str, ini: date, fim: date, fuso: ZoneInfo) -> dict:
    """Os dados do resumo do período `ini`..`fim` (inclusive), com o mesmo formato do relatório diário (`relatorio.montar`)."""
    ant_ini, ant_fim = anterior(tipo, ini)
    linhas = dict(historico.ler(ant_ini.isoformat(), fim.isoformat()))
    dias, dias_ant = _dias(ini, fim), _dias(ant_ini, ant_fim)
    com_dados = sum(1 for d in dias if d in linhas)
    if com_dados == 0:
        raise ErroRelatorio("sem_dados")
    meta = metricas.evolucao(1, 0, extras)["paineis"]

    def valores(painel: str, serie: str, lista: list[str]) -> list[float | None]:
        return [linhas[d].get(painel, {}).get(serie, 0) if d in linhas else None for d in lista]

    grupos: dict[str, list[dict]] = {}
    inativos: list[str] = []
    totais: dict[tuple[str, str], tuple[float | None, float | None]] = {}
    for p in meta:
        nomes = {n for d in dias + dias_ant for n in linhas.get(d, {}).get(p["id"], {})}
        como_de = {s["nome"]: s["agregado"] for s in p["series"]}
        series = []
        for nome in sorted(nomes, key=lambda n: -sum(v or 0 for v in valores(p["id"], n, dias))):
            como = como_de.get(nome, p["agregado"])
            v, a = valores(p["id"], nome, dias), valores(p["id"], nome, dias_ant)
            valor, antes = _agregar(v, como), _agregar(a, como)
            totais[(p["id"], nome)] = (valor, antes)
            if valor or antes:
                series.append({"nome": nome, "valor": valor, "media": antes, "variacao": _variacao(valor, antes), "miniatura": miniatura(v), "ativa": True})
        if series:
            grupos.setdefault(p["grupo"], []).append({"titulo": p["titulo"], "unidade": p["unidade"], "series": series})
        else:
            inativos.append(p["titulo"])
    destaques = []
    unidades = {p["id"]: p["unidade"] for p in meta}
    for painel, serie, rotulo in DESTAQUES:
        escolhidas = [k for k in totais if k[0] == painel and (serie is None or k[1] == serie)]
        valor = sum(totais[k][0] or 0 for k in escolhidas)
        antes = sum(totais[k][1] or 0 for k in escolhidas)
        destaques.append({"rotulo": rotulo, "valor": valor, "media": antes, "variacao": _variacao(valor, antes), "unidade": unidades.get(painel, "")})
    avisos: list[tuple[str, str]] = []
    if com_dados < len(dias):
        avisos.append(("aviso", f"Só há {com_dados} de {len(dias)} dias gravados neste período: os totais podem ficar abaixo do real (o histórico só existe desde que foi ligado)."))
    cinco = next((x for x in destaques if x["rotulo"] == "Erros 5xx"), None)
    if cinco and cinco["valor"]:
        avisos.append(("aviso", f"{_num(cinco['valor'])} pedidos com erro do servidor (5xx) neste período."))
    falhas = totais.get(("geracoes", "Falhou"), (0, 0))[0]
    if falhas:
        avisos.append(("aviso", f"{_num(falhas)} gerações falharam neste período."))
    titulo, curto = titulos(tipo, ini, fim)
    nome_ant = "semana anterior" if tipo == "semana" else "mês anterior"
    return {"dia": fim, "dias_lista": dias, "grupos": grupos, "inativos": inativos, "destaques": destaques, "alertas": avisos, "fuso": fuso.key,
            "nome": "resumo semanal" if tipo == "semana" else "resumo mensal", "titulo": titulo, "curto": curto,
            "colunas": ("Período", "Anterior", "Variação", f"{len(dias)} dias"),
            "legenda": f"Contagens somadas no período; «Anterior» é a {nome_ant}. Médias e picos (CPU, memória, tempos) são a média e o pico dos dias. A miniatura mostra cada dia do período."}


def construir_periodo(historico, metricas, extras, tipo: str, ini: date, fim: date, fuso: ZoneInfo) -> dict:
    d = montar_periodo(historico, metricas, extras, tipo, ini, fim, fuso)
    link = config.url_publica()
    return {"assunto": assunto(d), "html": em_html(d, link), "texto": em_texto(d, link), "dia": fim.isoformat(), "inicio": ini.isoformat(), "tipo": tipo,
            "alertas": len(d["alertas"])}


def enviar_periodo(historico, metricas, extras, tipo: str, ini: date, fim: date, fuso: ZoneInfo, abrir=urllib.request.urlopen, teste: bool = False) -> str:
    r = construir_periodo(historico, metricas, extras, tipo, ini, fim, fuso)
    return email_envio.enviar(config.email_chave(), config.relatorio_remetente(), config.relatorio_destinos(),
                              ("[Teste] " if teste else "") + r["assunto"], r["html"], r["texto"], abrir)


def enviar_periodicos_se_devido(relatorios, historico, metricas, extras, estado: EstadoRelatorio, agora: float | None = None, abrir=urllib.request.urlopen) -> list[str]:
    """Chamado de poucos em poucos minutos: envia o resumo da semana e/ou do mês que acabaram, se ainda não saíram. Devolve as chaves enviadas."""
    if not periodicos_ativos() or relatorios is None or historico is None:
        return []
    agora = time.time() if agora is None else agora
    fuso = ZoneInfo(config.relatorio_fuso())
    local = datetime.fromtimestamp(agora, fuso)
    if local.time() < DEPOIS_DAS or agora < estado.proxima_tentativa:
        return []
    enviados: list[str] = []
    for tipo in ("semana", "mes"):
        if tipo == "mes" and local.day > 7:
            continue                                               # um mês que acabou há mais de uma semana já não vale a pena enviar
        ini, fim = ultimo_completo(tipo, local.date())
        chave = chave_de(tipo, ini)
        if chave in estado.periodicos_tratados:
            continue                                               # já decidido: nenhuma consulta à base (o Neon pode adormecer)
        try:
            gravados = {d for d, _ in historico.ler(ini.isoformat(), fim.isoformat())}
            if fim.isoformat() not in gravados or len(gravados) * 2 < len(_dias(ini, fim)):
                if historico.feito_ate == (local.date() - timedelta(days=1)).isoformat():
                    estado.periodicos_tratados.add(chave)          # o histórico de ontem já está feito e não chega: a decisão é definitiva
                continue                                           # o último dia ainda não foi gravado, ou há menos de metade dos dias: não vale a pena
            if not relatorios.reservar(chave, agora):
                estado.periodicos_tratados.add(chave)
                continue
        except Exception:  # noqa: BLE001 - a base em baixo: tenta-se daqui a pouco
            estado.proxima_tentativa = agora + 300
            return enviados
        try:
            enviar_periodo(historico, metricas, extras, tipo, ini, fim, fuso, abrir)
        except (email_envio.ErroEmail, ErroRelatorio) as e:
            motivo = str(e) or type(e).__name__
        except Exception as e:  # noqa: BLE001
            motivo = type(e).__name__
        else:
            log.info("resumo %s enviado: %s", tipo, chave)
            enviados.append(chave)
            estado.periodicos_tratados.add(chave)
            continue
        try:
            relatorios.libertar(chave)
        except Exception:  # noqa: BLE001
            log.warning("resumo: nao consegui desfazer a reserva de %s", chave)
        estado.ultimo_erro, estado.ultimo_erro_em = motivo, agora
        estado.proxima_tentativa = agora + ESPERA_APOS_FALHA_S
        log.warning("resumo %s falhou (%s)", tipo, motivo)
        return enviados
    return enviados
