"""O relatório diário por e-mail: tudo o que se gravou no dia que acabou, para acompanhar a app sem abrir o painel (`docs/ADMIN.md`).

COMO FUNCIONA
 - O serviço acorda de poucos em poucos minutos (`app._relatorio_diario`). Depois das 00:05 (hora do `RELATORIO_FUSO`) vê se o relatório de ONTEM já foi enviado;
   se não, **reserva o dia na base** (`RelatoriosEnviados.reservar`: um `INSERT … ON CONFLICT DO NOTHING`, só quem o consegue envia) e manda o e-mail.
   Por isso um arranque ou uma atualização a meio da noite não o duplica, e se o serviço estava a dormir à meia-noite o relatório sai assim que acorda.
   Se o envio falha, a reserva desfaz-se e tenta-se outra vez daí a uma hora.
 - O relatório usa a mesma vista da «Evolução diária» (`Metricas.evolucao`, com uma janela que acaba no fim desse dia): o dia, a média dos 7 dias anteriores, a
   variação e uma miniatura dos 8 dias de cada série. O e-mail é só HTML em tabelas com estilos «inline» (o Gmail ignora `<style>`, SVG e scripts) e traz também
   a versão em texto simples.
 - Dias de mudança de hora (março e outubro): a janela fica uma hora desfasada nesse dia. Aceita-se.

PRIVACIDADE: só os agregados do painel (contagens e códigos de país de duas letras). Nunca IPs, nomes, ficheiros, o texto dos comentários nem textos de erro.
O fornecedor de e-mail (Resend) vê o relatório e o endereço do dono; é o único terceiro a quem isto chega (a Política de privacidade fala só dos visitantes).
"""
from __future__ import annotations

import html
import logging
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from datetime import time as hora_do_dia
from zoneinfo import ZoneInfo

from . import config, email_envio
from .bd_simples import BaseSql

log = logging.getLogger("rifas.relatorio")

JANELA_DIAS = 8                      # o dia do relatório + os 7 anteriores (a média de comparação)
DEPOIS_DAS = hora_do_dia(0, 5)       # um pouco depois da meia-noite: o buffer da base já foi descarregado (`evolucao` descarrega-o na mesma)
ESPERA_APOS_FALHA_S = 3600.0
MEMORIA_AVISO_MB = 400               # o Render gratuito tem 512 MB
LATENCIA_AVISO_MS = 1500
BARRAS = "▁▂▃▄▅▆▇█"
MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")
SEMANA = ("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo")

# (painel, série ou None = a soma das séries, rótulo): os números grandes do topo
DESTAQUES = (
    ("sessoes", None, "Sessões"), ("geracoes", None, "Gerações pedidas"), ("numeros", None, "Números gerados"), ("descargas", None, "Descargas"),
    ("paginas_vistas", "Pessoas", "Páginas vistas (pessoas)"), ("comentarios", None, "Comentários"), ("problemas", None, "Problemas reportados"),
    ("pedidos", "Erros do servidor (5xx)", "Erros 5xx"),
)


class ErroRelatorio(Exception):
    """Não foi possível montar o relatório (a base está em baixo, ou o dia pedido não está na janela)."""


class RelatoriosEnviados(BaseSql):
    """Os dias cujo relatório já foi reservado/enviado: é o que impede dois envios do mesmo dia (dois arranques sobrepostos, uma atualização a meio da noite)."""
    ESQUEMA = ("CREATE TABLE IF NOT EXISTS relatorios(dia TEXT PRIMARY KEY, enviado BIGINT NOT NULL)",)

    def reservar(self, dia: str, agora: float) -> bool:
        """True só para quem consegue a reserva (a primeira): esse é quem envia."""
        return bool(self._executar("INSERT INTO relatorios(dia, enviado) VALUES (%s, %s) ON CONFLICT (dia) DO NOTHING RETURNING dia", (dia, int(agora))))

    def libertar(self, dia: str) -> None:
        self._executar("DELETE FROM relatorios WHERE dia = %s", (dia,))

    def ultimo(self, tipo: str = "dia") -> dict | None:
        """O último envio: `dia` (as chaves são datas) ou um resumo `semana` / `mes` (chaves `semana:2026-11-09`, `mes:2026-10`)."""
        if tipo == "dia":
            linhas = self._executar("SELECT dia, enviado FROM relatorios WHERE dia NOT LIKE %s ORDER BY dia DESC LIMIT 1", ("%:%",))
        else:
            linhas = self._executar("SELECT dia, enviado FROM relatorios WHERE dia LIKE %s ORDER BY dia DESC LIMIT 1", (f"{tipo}:%",))
        return {"dia": linhas[0][0], "enviado": int(linhas[0][1])} if linhas else None


@dataclass
class EstadoRelatorio:
    """O que o painel mostra do envio (em memória: o `ultimo` verdadeiro está na base)."""
    proxima_tentativa: float = 0.0
    ultimo_erro: str = ""
    ultimo_erro_em: float = 0.0
    dia_tratado: str = ""                                    # o último relatório diário já enviado (ou visto como enviado): sem consultas até à meia-noite seguinte
    periodicos_tratados: set[str] = field(default_factory=set)       # chaves dos resumos semanal/mensal já decididos (`relatorio_periodo.py`)


# ------------------------------------------------------------------ o dia e o fuso
def dia_de_ontem(agora: float, fuso: ZoneInfo) -> date:
    return datetime.fromtimestamp(agora, fuso).date() - timedelta(days=1)


def _meia_noite(dia: date, fuso: ZoneInfo) -> datetime:
    return datetime.combine(dia, hora_do_dia(0), tzinfo=fuso)


def janela_do_dia(dia: date, fuso: ZoneInfo) -> tuple[int, int, float]:
    """`(desvio_min, inicio_ts, fim_ts)`: o desvio do fuso nesse dia (ao meio-dia), o instante em que começa e o último segundo."""
    desvio = int(datetime.combine(dia, hora_do_dia(12), tzinfo=fuso).utcoffset().total_seconds() // 60)
    return desvio, int(_meia_noite(dia, fuso).timestamp()), _meia_noite(dia + timedelta(days=1), fuso).timestamp() - 1


def mascarar(email: str) -> str:
    """`ana@exemplo.pt` -> `a**@exemplo.pt`: o painel mostra para onde vai sem expor o endereço inteiro."""
    nome, _, resto = email.partition("@")
    return f"{nome[:1]}{'*' * max(2, len(nome) - 1)}@{resto}"


# ------------------------------------------------------------------ os números
def _num(v: float | None, unidade: str = "") -> str:
    if v is None:
        return "—"
    texto = f"{round(v):,}".replace(",", " ") if abs(v - round(v)) < 0.05 or abs(v) >= 1000 else f"{v:,.1f}".replace(",", " ").replace(".", ",")
    return f"{texto}{unidade}"


def _variacao(valor: float | None, media: float | None) -> tuple[str, str]:
    """`(seta, texto)` face à média dos dias anteriores."""
    if valor is None or media is None:
        return "", "—"
    if media == 0:
        return ("▲", "novo") if valor > 0 else ("", "—")
    p = round((valor - media) / media * 100)
    if p == 0:
        return "", "igual"
    return ("▲" if p > 0 else "▼"), f"{abs(p)} %"


def _pl(n: float, um: str, varios: str) -> str:
    return f"{_num(n)} {um if round(n) == 1 else varios}"


def _junta(v: tuple[str, str]) -> str:
    return f"{v[0]} {v[1]}".strip()


def miniatura(valores: list[float | None]) -> str:
    reais = [v for v in valores if v is not None]
    topo = max(reais, default=0)
    if topo <= 0:
        return "".join("▁" if v is not None else "·" for v in valores)
    return "".join("·" if v is None else BARRAS[min(len(BARRAS) - 1, round(v / topo * (len(BARRAS) - 1)))] for v in valores)


PAISES = {"PT": "Portugal", "BR": "Brasil", "ES": "Espanha", "FR": "França", "US": "EUA", "GB": "Reino Unido", "DE": "Alemanha", "AO": "Angola",
          "MZ": "Moçambique", "CV": "Cabo Verde", "CH": "Suíça", "LU": "Luxemburgo", "IT": "Itália", "NL": "Países Baixos", "BE": "Bélgica", "IE": "Irlanda",
          "CA": "Canadá", "IN": "Índia", "CN": "China", "JP": "Japão", "RU": "Rússia", "UA": "Ucrânia", "PL": "Polónia", "TR": "Turquia", "??": "Desconhecido"}


def _serie(s: dict, pais: bool = False) -> dict:
    valores = s["valores"]
    ontem = valores[-1]
    antes = [v for v in valores[:-1] if v is not None]
    media = sum(antes) / len(antes) if antes else None
    nome = s["nome"]
    if pais and nome in PAISES:
        nome = PAISES[nome] if nome == "??" else f"{PAISES[nome]} ({nome})"
    return {"nome": nome, "valor": ontem, "media": media, "variacao": _variacao(ontem, media), "miniatura": miniatura(valores),
            "ativa": bool(ontem) or bool(media)}


def _destaque(paineis: dict[str, dict], painel: str, serie: str | None) -> tuple[float | None, float | None]:
    p = paineis.get(painel)
    if p is None:
        return None, None
    escolhidas = [s for s in p["series"] if serie is None or s["nome"] == serie]
    if not escolhidas:
        return (0.0, 0.0) if serie is None else (None, None)           # um painel sem nenhuma série (nunca houve um evento desse tipo) é «zero», não «sem dados»
    dias = len(escolhidas[0]["valores"])
    total = [sum((s["valores"][i] or 0) for s in escolhidas) for i in range(dias)]
    antes = total[:-1]
    return total[-1], (sum(antes) / len(antes) if antes else None)


def alertas(ev: dict, paineis: dict[str, dict], dia: date, inicio_ts: int) -> list[tuple[str, str]]:
    """O que merece atenção: `(nivel, texto)`, nivel «aviso» ou «info»."""
    def hoje(painel: str, serie: str | None = None) -> float:
        return _destaque(paineis, painel, serie)[0] or 0

    saida: list[tuple[str, str]] = []
    if ev["dados_desde"] > inicio_ts:
        desde = datetime.fromtimestamp(ev["dados_desde"], ZoneInfo(config.relatorio_fuso())).strftime("%d/%m às %H:%M")
        saida.append(("aviso", f"Só há registos desde {desde}: os números deste dia podem estar incompletos (serviço reiniciado ou base de dados temporária)."))
    if (n := hoje("pedidos", "Erros do servidor (5xx)")):
        saida.append(("aviso", f"{_pl(n, 'pedido acabou', 'pedidos acabaram')} em erro do servidor (5xx). Ver a secção «Erros» do painel."))
    if (n := hoje("geracoes", "Falhou")):
        saida.append(("aviso", f"{_pl(n, 'geração falhou', 'gerações falharam')}."))
    if (n := hoje("motor", "Reinícios do motor")):
        saida.append(("aviso", f"O motor reiniciou {_pl(n, 'vez', 'vezes')} (memória, tempo ou cancelamento)."))
    if (n := hoje("problemas", "Falharam")):
        saida.append(("aviso", f"{_pl(n, 'problema reportado não chegou', 'problemas reportados não chegaram')} ao GitHub."))
    if (n := hoje("problemas", "Registados no GitHub")):
        saida.append(("info", f"{_pl(n, 'problema novo reportado', 'problemas novos reportados')} por visitantes: ver os issues do GitHub."))
    memoria = max(((s["valores"][-1] or 0) for s in paineis.get("memoria", {"series": []})["series"]), default=0)
    if memoria >= MEMORIA_AVISO_MB:
        saida.append(("aviso", f"A memória chegou a {_num(memoria)} MB (o Render gratuito tem 512 MB)."))
    p95 = next((s["valores"][-1] for s in paineis.get("latencia", {"series": []})["series"] if s["nome"] == "95 % até"), None)
    if p95 and p95 >= LATENCIA_AVISO_MS:
        saida.append(("aviso", f"Em 5 % dos pedidos a resposta demorou {_num(p95)} ms ou mais."))
    if (n := hoje("motor", "Arranques do serviço")) > 1:
        saida.append(("info", f"O serviço arrancou {_pl(n, 'vez', 'vezes')} (atualizações ou adormecer/acordar)."))
    if (n := hoje("limites")):
        saida.append(("info", f"{_pl(n, 'pedido foi recusado', 'pedidos foram recusados')} por limites (pedidos por minuto, geração em curso…)."))
    novas = [v["versao"] for v in ev.get("versoes", []) if v["dia"] == dia.isoformat()]
    if novas:
        saida.append(("info", f"{'Chegou a versão' if len(novas) == 1 else 'Chegaram as versões'} {', '.join(novas)} neste dia."))
    if hoje("sessoes") == 0:
        saida.append(("info", "Ninguém abriu o gerador neste dia."))
    return saida


# ------------------------------------------------------------------ montar o relatório
def _avisos_de_quotas(metricas) -> list[tuple[str, str]]:
    """Os avisos das quotas do alojamento (horas do Render, espaço do Neon): ver `quotas.py`. Nunca estragam o relatório."""
    try:
        from . import quotas

        return [("aviso", t) for t in quotas.estado(metricas)["avisos"]]
    except Exception:  # noqa: BLE001
        return []


def montar(metricas, extras, dia: date, fuso: ZoneInfo) -> dict:
    """Os dados do relatório do `dia` (já calculados: as séries, os destaques e os alertas)."""
    desvio, inicio, fim = janela_do_dia(dia, fuso)
    ev = metricas.evolucao(JANELA_DIAS, desvio, extras, fim)
    if getattr(metricas, "erro_bd", False):
        raise ErroRelatorio("base_de_dados")                    # números a zero por a base estar em baixo seriam mentira: tenta-se mais tarde
    if ev["dias_lista"][-1] != dia.isoformat():
        raise ErroRelatorio("janela")
    paineis = {p["id"]: p for p in ev["paineis"]}
    grupos: dict[str, list[dict]] = {}
    inativos: list[str] = []
    for p in ev["paineis"]:
        series = [_serie(s, p.get("rotulos") == "pais") for s in p["series"]]
        if not any(s["ativa"] for s in series):
            inativos.append(p["titulo"])
            continue
        grupos.setdefault(p["grupo"], []).append({"titulo": p["titulo"], "unidade": p["unidade"], "series": [s for s in series if s["ativa"]]})
    destaques = []
    for painel, serie, rotulo in DESTAQUES:
        valor, media = _destaque(paineis, painel, serie)
        unidade = paineis.get(painel, {}).get("unidade", "")
        destaques.append({"rotulo": rotulo, "valor": valor, "media": media, "variacao": _variacao(valor, media), "unidade": unidade})
    return {"dia": dia, "dias_lista": ev["dias_lista"], "grupos": grupos, "inativos": inativos, "destaques": destaques,
            "alertas": alertas(ev, paineis, dia, inicio) + _avisos_de_quotas(metricas), "fuso": fuso.key, "nome": "relatório diário", "titulo": titulo_do_dia(dia), "curto": titulo_do_dia(dia, True),
            "colunas": ("Dia", "Média 7 d", "Variação", "8 dias"),
            "legenda": "«Média 7 d» é a média dos 7 dias anteriores; a miniatura mostra os 8 dias, o último é este."}


def titulo_do_dia(dia: date, curto: bool = False) -> str:
    if curto:
        return f"{dia.day} de {MESES[dia.month - 1][:3]}"
    return f"{SEMANA[dia.weekday()]}, {dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def assunto(d: dict) -> str:
    sessoes = next((x["valor"] for x in d["destaques"] if x["rotulo"] == "Sessões"), 0) or 0
    geracoes = next((x["valor"] for x in d["destaques"] if x["rotulo"] == "Gerações pedidas"), 0) or 0
    avisos = sum(1 for n, _ in d["alertas"] if n == "aviso")
    return f"Gerador de Rifas · {d['curto']}: {_num(sessoes)} sessões, {_num(geracoes)} gerações" + (f" · ⚠ {avisos} aviso(s)" if avisos else "")


def em_texto(d: dict, link: str = "") -> str:
    linhas = [f"GERADOR DE RIFAS — {d['titulo']}", ""]
    if d["alertas"]:
        linhas += ["ATENÇÃO", *[f"  {'!' if n == 'aviso' else '-'} {t}" for n, t in d["alertas"]], ""]
    linhas += [f"EM RESUMO ({d['colunas'][0].lower()} · {d['colunas'][1].lower()})"]
    for x in d["destaques"]:
        linhas.append(f"  {x['rotulo']}: {_num(x['valor'], x['unidade'])} · média {_num(x['media'], x['unidade'])} · {_junta(x['variacao'])}")
    for grupo, paineis in d["grupos"].items():
        linhas += ["", grupo.upper()]
        for p in paineis:
            linhas.append(f"  {p['titulo']}")
            for s in p["series"]:
                linhas.append(f"    {s['nome']}: {_num(s['valor'], p['unidade'])} (média {_num(s['media'], p['unidade'])}, {_junta(s['variacao'])}) {s['miniatura']}")
    if d["inativos"]:
        linhas += ["", "Sem atividade: " + ", ".join(d["inativos"]) + "."]
    linhas += ["", f"Dias do fuso {d['fuso']}. Só contagens: nunca IPs, nomes, ficheiros nem textos."]
    if link:
        linhas.append(f"Painel: {link}/admin")
    return "\n".join(linhas) + "\n"


_E = html.escape
_FONTE = "font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
_CINZA, _TINTA, _LINHA, _MARCA = "#5b6472", "#1d2430", "#e3e6ec", "#7a1fa2"


def _cor_aviso(nivel: str) -> tuple[str, str]:
    return ("#fff4e0", "#8a5300") if nivel == "aviso" else ("#eaf2ff", "#1d4f91")


def em_html(d: dict, link: str = "") -> str:
    def variacao(v: tuple[str, str]) -> str:
        return _E(_junta(v))

    p: list[str] = [
        f"<!doctype html><html lang='pt'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{_E(assunto(d))}</title></head>"
        f"<body style=\"margin:0;padding:0;background:#f3f4f7;{_FONTE};color:{_TINTA}\">"
        f"<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='background:#f3f4f7'><tr><td align='center' style='padding:16px 8px'>"
        f"<table role='presentation' width='640' cellpadding='0' cellspacing='0' style='width:100%;max-width:640px;background:#ffffff;border-radius:8px'>"
        f"<tr><td style='padding:20px 24px;background:{_MARCA};color:#ffffff;border-radius:8px 8px 0 0'>"
        f"<div style='font-size:13px;letter-spacing:.04em;text-transform:uppercase;opacity:.9'>Gerador de Rifas · {_E(d['nome'])}</div>"
        f"<div style='font-size:22px;font-weight:700;margin-top:4px'>{_E(d['titulo'])}</div></td></tr>"]
    if d["alertas"]:
        p.append("<tr><td style='padding:16px 24px 0'>")
        for nivel, texto in d["alertas"]:
            fundo, cor = _cor_aviso(nivel)
            p.append(f"<div style='background:{fundo};color:{cor};padding:8px 12px;border-radius:6px;margin-bottom:6px;font-size:14px'>"
                     f"{'⚠ ' if nivel == 'aviso' else 'ℹ '}{_E(texto)}</div>")
        p.append("</td></tr>")
    p.append("<tr><td style='padding:16px 24px 0'><table role='presentation' width='100%' cellpadding='0' cellspacing='6'>")
    for i, x in enumerate(d["destaques"]):
        if i % 4 == 0:
            p.append("<tr>")
        p.append(f"<td width='25%' valign='top' style='background:#f6f1fa;border-radius:6px;padding:10px'>"
                 f"<div style='font-size:12px;color:{_CINZA}'>{_E(x['rotulo'])}</div>"
                 f"<div style='font-size:24px;font-weight:700'>{_E(_num(x['valor'], x['unidade']))}</div>"
                 f"<div style='font-size:12px;color:{_CINZA}'>média {_E(_num(x['media'], x['unidade']))} · {variacao(x['variacao'])}</div></td>")
        if i % 4 == 3:
            p.append("</tr>")
    p.append("</table></td></tr>")
    cab = f"font-size:12px;color:{_CINZA};text-align:right;padding:4px 6px;border-bottom:1px solid {_LINHA}"
    for grupo, paineis in d["grupos"].items():
        p.append(f"<tr><td style='padding:18px 24px 0'><div style='font-size:16px;font-weight:700;color:{_MARCA};margin-bottom:6px'>{_E(grupo)}</div>"
                 f"<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='font-size:13px'>"
                 f"<tr><td style='{cab};text-align:left'></td><td width='70' style='{cab}'>{_E(d['colunas'][0])}</td><td width='84' style='{cab}'>{_E(d['colunas'][1])}</td>"
                 f"<td width='84' style='{cab}'>{_E(d['colunas'][2])}</td><td width='96' style='{cab}'>{_E(d['colunas'][3])}</td></tr>")
        for painel in paineis:
            varias = len(painel["series"]) > 1
            if varias:
                p.append(f"<tr><td colspan='5' style='padding:8px 6px 2px;font-weight:600'>{_E(painel['titulo'])}</td></tr>")
            for s in painel["series"]:
                nome = s["nome"] if varias else painel["titulo"]
                recuo = "padding:4px 6px 4px 18px" if varias else "padding:4px 6px"
                p.append(f"<tr><td style='{recuo};border-bottom:1px solid {_LINHA}'>{_E(nome)}</td>"
                         f"<td style='text-align:right;padding:4px 6px;border-bottom:1px solid {_LINHA};font-weight:600'>{_E(_num(s['valor'], painel['unidade']))}</td>"
                         f"<td style='text-align:right;padding:4px 6px;border-bottom:1px solid {_LINHA};color:{_CINZA}'>{_E(_num(s['media'], painel['unidade']))}</td>"
                         f"<td style='text-align:right;padding:4px 6px;border-bottom:1px solid {_LINHA};color:{_CINZA}'>{variacao(s['variacao'])}</td>"
                         f"<td style='text-align:right;padding:4px 6px;border-bottom:1px solid {_LINHA};color:{_MARCA};letter-spacing:1px;font-family:monospace'>{s['miniatura']}</td></tr>")
        p.append("</table></td></tr>")
    if d["inativos"]:
        p.append(f"<tr><td style='padding:16px 24px 0;font-size:13px;color:{_CINZA}'>Sem atividade neste período: {_E(', '.join(d['inativos']))}.</td></tr>")
    p.append(f"<tr><td style='padding:18px 24px 22px;font-size:12px;color:{_CINZA}'>Os dias são os do fuso {_E(d['fuso'])}. {_E(d['legenda'])} "
             f"Só contagens: nunca IPs, nomes, ficheiros nem textos de visitantes.")
    if link:
        p.append(f" <a href='{_E(link, quote=True)}/admin' style='color:{_MARCA}'>Abrir o painel</a>.")
    p.append("</td></tr></table></td></tr></table></body></html>")
    return "".join(p)


def construir(metricas, extras, dia: date, fuso: ZoneInfo) -> dict:
    """`{assunto, html, texto}` do relatório do `dia`."""
    d = montar(metricas, extras, dia, fuso)
    link = config.url_publica()
    return {"assunto": assunto(d), "html": em_html(d, link), "texto": em_texto(d, link), "dia": dia.isoformat(), "alertas": len(d["alertas"])}


# ------------------------------------------------------------------ enviar
def ativo() -> bool:
    return bool(config.email_chave() and config.relatorio_destinos())


def enviar_relatorio(metricas, extras, dia: date, fuso: ZoneInfo, abrir=urllib.request.urlopen, teste: bool = False) -> str:
    """Monta e envia o relatório de `dia`; devolve o id do e-mail. `teste` põe «[Teste]» no assunto."""
    r = construir(metricas, extras, dia, fuso)
    return email_envio.enviar(config.email_chave(), config.relatorio_remetente(), config.relatorio_destinos(),
                              ("[Teste] " if teste else "") + r["assunto"], r["html"], r["texto"], abrir)


def enviar_se_devido(relatorios, metricas, extras, estado: EstadoRelatorio, agora: float | None = None, abrir=urllib.request.urlopen) -> str:
    """Chamado de poucos em poucos minutos. Devolve o que fez: `desligado`, `cedo` (ainda antes das 00:05), `espera` (falhou há pouco), `ja_enviado`, `enviado` ou `falhou`."""
    if not ativo() or relatorios is None:
        return "desligado"
    agora = time.time() if agora is None else agora
    fuso = ZoneInfo(config.relatorio_fuso())
    local = datetime.fromtimestamp(agora, fuso)
    if local.time() < DEPOIS_DAS:
        return "cedo"
    if agora < estado.proxima_tentativa:
        return "espera"
    dia = local.date() - timedelta(days=1)
    chave = dia.isoformat()
    if estado.dia_tratado == chave:
        return "ja_enviado"                                  # já tratado: nem consulta a base (o Neon pode adormecer entre uma meia-noite e a seguinte)
    try:
        if not relatorios.reservar(chave, agora):
            estado.dia_tratado = chave
            return "ja_enviado"
    except Exception:  # noqa: BLE001 - a base de dados em baixo: tenta-se daqui a pouco
        estado.proxima_tentativa = agora + 300
        return "falhou"
    try:
        enviar_relatorio(metricas, extras, dia, fuso, abrir)
    except (email_envio.ErroEmail, ErroRelatorio) as e:
        motivo = str(e) or type(e).__name__
    except Exception as e:  # noqa: BLE001 - nada pode derrubar o ciclo do serviço
        motivo = type(e).__name__
    else:
        estado.ultimo_erro = ""
        estado.dia_tratado = chave
        log.info("relatorio diario enviado: %s", chave)
        return "enviado"
    try:
        relatorios.libertar(chave)                             # desfaz a reserva: a próxima tentativa volta a enviar
    except Exception:  # noqa: BLE001
        log.warning("relatorio: nao consegui desfazer a reserva de %s", chave)
    estado.ultimo_erro, estado.ultimo_erro_em = motivo, agora
    estado.proxima_tentativa = agora + ESPERA_APOS_FALHA_S
    log.warning("relatorio diario falhou (%s)", motivo)
    return "falhou"
