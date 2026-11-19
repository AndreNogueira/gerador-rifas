"""Alertas imediatos por e-mail: o serviço avisa assim que algo corre mal, sem esperar pelo relatório diário.

REGRAS (avaliadas de minuto a minuto sobre o que o servidor viu nos últimos 15 minutos, em memória: não dependem da base):
 - `erros5xx`: 5 ou mais pedidos com erro do servidor (5xx);
 - `reinicios`: o motor reiniciou 2 ou mais vezes (memória, tempo ou cancelamento);
 - `memoria`: o contentor passou de 460 MB (o Render gratuito tem 512 MB);
 - `base_de_dados`: a base das métricas não responde há 2 verificações seguidas.
Cada alerta só se repete passadas 6 horas (a reserva está na tabela `alertas`, na base: um arranque novo não o repete) e as condições que aparecem juntas vão num
só e-mail. Usa o mesmo Resend e o mesmo destinatário do relatório (`RESEND_API_KEY` + `RELATORIO_EMAIL_PARA`); `ALERTAS_EMAIL=0` desliga-os.

PRIVACIDADE: só contagens e a hora; nunca IPs, rotas com valores nem textos de erro.
"""
from __future__ import annotations

import html
import time
import urllib.request
from dataclasses import dataclass, field

from . import config, email_envio
from .bd_simples import BaseSql

JANELA_S = 900
LIMITE_5XX = 5
LIMITE_REINICIOS = 2
LIMITE_MEMORIA_MB = 460
ESPERA_ENTRE_REPETICOES_S = 6 * 3600
ESPERA_APOS_FALHA_S = 900
VERIFICACOES_BD = 2

TITULOS = {"teste": "Teste de alerta", "erros5xx": "Erros do servidor (5xx)", "reinicios": "Reinícios do motor", "memoria": "Memória quase no limite", "base_de_dados": "Base de dados sem resposta"}


class AlertasEnviados(BaseSql):
    """Quando se avisou de cada condição pela última vez: impede a repetição durante `ESPERA_ENTRE_REPETICOES_S` (mesmo com arranques novos)."""
    ESQUEMA = ("CREATE TABLE IF NOT EXISTS alertas(chave TEXT PRIMARY KEY, ultimo BIGINT NOT NULL)",)

    def reservar(self, chave: str, agora: float, espera_s: float = ESPERA_ENTRE_REPETICOES_S) -> bool:
        """True só se ainda não se avisou desta condição nas últimas `espera_s` (e fica registado agora)."""
        return bool(self._executar("INSERT INTO alertas(chave, ultimo) VALUES (%s, %s) ON CONFLICT (chave) DO UPDATE SET ultimo = excluded.ultimo "
                                   "WHERE alertas.ultimo <= %s RETURNING chave", (chave, int(agora), int(agora - espera_s))))

    def libertar(self, chave: str) -> None:
        self._executar("DELETE FROM alertas WHERE chave = %s", (chave,))

    def ultimos(self) -> dict[str, int]:
        return {c: int(t) for c, t in self._executar("SELECT chave, ultimo FROM alertas")}


@dataclass
class EstadoAlertas:
    bd_falhas_seguidas: int = 0
    proxima_tentativa: float = 0.0
    ultimo_erro: str = ""
    avisados: dict[str, float] = field(default_factory=dict)              # quando se avisou (ou se soube que se avisou) de cada condição: sem consultas à base durante a espera
    enviados: list[tuple[float, str]] = field(default_factory=list)       # (quando, chave) desde o arranque, para o painel


def ativos() -> bool:
    import os

    desligado = os.environ.get("ALERTAS_EMAIL", "").strip().lower() in ("0", "nao", "não", "false", "off")
    return bool(config.email_chave() and config.relatorio_destinos()) and not desligado


def condicoes(metricas, estado: EstadoAlertas, agora: float) -> dict[str, str]:
    """As condições de alerta verdadeiras AGORA: `{chave: detalhe}`."""
    saida: dict[str, str] = {}
    n = metricas.recentes("5xx", JANELA_S, agora)
    if n >= LIMITE_5XX:
        saida["erros5xx"] = f"{n} pedidos acabaram em erro do servidor (5xx) nos últimos {JANELA_S // 60} minutos."
    n = metricas.recentes("reinicio", JANELA_S, agora)
    if n >= LIMITE_REINICIOS:
        saida["reinicios"] = f"O motor reiniciou {n} vezes nos últimos {JANELA_S // 60} minutos (memória, tempo ou cancelamento)."
    mem = metricas.memoria_recente(JANELA_S, agora)
    if mem is not None and mem >= LIMITE_MEMORIA_MB:
        saida["memoria"] = f"O contentor está a usar {mem:.0f} MB (o Render gratuito tem 512 MB): perto do limite, o motor pode ser morto."
    estado.bd_falhas_seguidas = estado.bd_falhas_seguidas + 1 if getattr(metricas, "erro_bd", False) else 0
    if estado.bd_falhas_seguidas >= VERIFICACOES_BD:
        saida["base_de_dados"] = "A base de dados das métricas não responde (o painel pode mostrar dados antigos; as gravações ficam à espera no buffer)."
    return saida


def montar(novos: dict[str, str], agora: float, link: str = "") -> tuple[str, str, str]:
    """`(assunto, html, texto)` do e-mail com os alertas novos."""
    quando = time.strftime("%d/%m/%Y %H:%M UTC", time.gmtime(agora))
    nomes = [TITULOS.get(c, c) for c in novos]
    assunto = f"⚠ Gerador de Rifas: {', '.join(nomes)}"
    painel = f"{link}/admin" if link else ""
    linhas = [f"Gerador de Rifas — alerta ({quando})", ""] + [f"! {TITULOS.get(c, c)}: {t}" for c, t in novos.items()]
    linhas += ["", "Só se repete passadas 6 horas se a condição continuar."] + ([f"Painel: {painel}"] if painel else [])
    itens = "".join(f"<div style='background:#fff4e0;color:#8a5300;padding:10px 12px;border-radius:6px;margin-bottom:8px;font-size:14px'>"
                    f"<b>{html.escape(TITULOS.get(c, c))}</b><br>{html.escape(t)}</div>" for c, t in novos.items())
    corpo = (f"<!doctype html><html lang='pt'><head><meta charset='utf-8'><title>{html.escape(assunto)}</title></head>"
             f"<body style=\"margin:0;padding:16px;background:#f3f4f7;font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1d2430\">"
             f"<div style='max-width:560px;margin:auto;background:#fff;border-radius:8px;padding:20px 24px'>"
             f"<div style='font-size:18px;font-weight:700;margin-bottom:4px'>⚠ Alerta do Gerador de Rifas</div>"
             f"<div style='font-size:12px;color:#5b6472;margin-bottom:14px'>{quando}</div>{itens}"
             f"<div style='font-size:12px;color:#5b6472'>Só se repete passadas 6 horas se a condição continuar.")
    if painel:
        corpo += f" <a href='{html.escape(painel, quote=True)}' style='color:#7a1fa2'>Abrir o painel</a>."
    return assunto, corpo + "</div></div></body></html>", "\n".join(linhas) + "\n"


def verificar_e_enviar(alertas, metricas, estado: EstadoAlertas, agora: float | None = None, abrir=urllib.request.urlopen) -> str:
    """Chamado de minuto a minuto. Devolve `desligado`, `espera` (falhou há pouco), `nada`, `enviado` ou `falhou`."""
    if alertas is None or not ativos():
        return "desligado"
    agora = time.time() if agora is None else agora
    if agora < estado.proxima_tentativa:
        return "espera"
    ativas = condicoes(metricas, estado, agora)
    if not ativas:
        return "nada"
    novos: dict[str, str] = {}
    try:
        for chave, detalhe in ativas.items():
            if agora - estado.avisados.get(chave, -1e18) < ESPERA_ENTRE_REPETICOES_S:
                continue                                           # uma condição que continua má não faz uma consulta por minuto (o Neon pode adormecer)
            if alertas.reservar(chave, agora):
                novos[chave] = detalhe
            else:
                estado.avisados[chave] = agora - ESPERA_ENTRE_REPETICOES_S + 3600          # outro arranque já avisou: volta-se a ver daqui a 1 hora
    except Exception:  # noqa: BLE001 - a base em baixo: tenta-se no minuto seguinte (o alerta de «base de dados» sai na mesma, se for o caso)
        estado.proxima_tentativa = agora + 60
        return "falhou"
    if not novos:
        return "nada"
    assunto, corpo, texto = montar(novos, agora, config.url_publica())
    try:
        email_envio.enviar(config.email_chave(), config.relatorio_remetente(), config.relatorio_destinos(), assunto, corpo, texto, abrir)
    except Exception as e:  # noqa: BLE001 - nada derruba o ciclo; só a classe fica
        for chave in novos:
            estado.avisados.pop(chave, None)
            try:
                alertas.libertar(chave)                         # a próxima tentativa volta a avisar
            except Exception:  # noqa: BLE001
                pass
        estado.ultimo_erro = str(e) if isinstance(e, email_envio.ErroEmail) else type(e).__name__
        estado.proxima_tentativa = agora + ESPERA_APOS_FALHA_S
        return "falhou"
    estado.ultimo_erro = ""
    estado.avisados.update({c: agora for c in novos})
    estado.enviados += [(agora, c) for c in novos]
    del estado.enviados[:-20]
    return "enviado"
