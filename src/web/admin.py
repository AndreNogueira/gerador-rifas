"""O painel de administracao (`/admin`): so para o dono do servico.

ACESSO: uma palavra-passe longa na variavel de ambiente `ADMIN_TOKEN` (no Render, em Environment: NAO e um *secret* do GitHub e nunca
vai para o repositorio). Sem ela (ou com menos de 12 caracteres) o painel NAO EXISTE: a pagina e a API devolvem 404.
 - `POST /api/admin/entrar` troca a palavra-passe por um cookie assinado (HttpOnly, SameSite=Strict, so enviado a `/api/admin`, 8 h);
   a palavra-passe nunca fica no browser nem no JS. Comparacao em tempo constante; 5 tentativas por minuto por IP e 40 no total.
 - Sem cookie valido, TODA a API do painel responde 404 (nao confirma que existe). Respostas `no-store`; `noindex`.
 - Mudar o `ADMIN_TOKEN` (ou o `CLAUDE_TOKEN`) invalida todos os cookies (a chave de assinatura deriva dos dois).
 - Um SEGUNDO acesso, so de LEITURA, para um assistente: `CLAUDE_TOKEN` (24+ caracteres, diferente do `ADMIN_TOKEN`). Entra-se do mesmo modo
   (papel `leitura` no cookie) ou, sem cookie, com `Authorization: Bearer <CLAUDE_TOKEN>` nos pedidos GET. Le tudo o que o painel mostra (estado,
   graficos, erros), mas as rotas que MUDAM alguma coisa (chaves da API, textos de SEO) respondem 403. Com so o `CLAUDE_TOKEN` (sem `ADMIN_TOKEN`)
   o painel existe so em leitura.
"""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import hmac
import time
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field

from . import VERSAO, alertas, auditoria, config, email_envio, historico, objetivos, opiniao, quotas, relatorio, relatorio_periodo
from . import seo_bd
from .chaves_api import QUOTA_PADRAO
from .metricas import DIAS_MAXIMOS, INTERVALOS, novo_painel
from .rotas import Servico, servico

COOKIE = "rifas_admin"
DURACAO_S = 8 * 3600
MAX_TENTATIVAS_IP = 5
MAX_TENTATIVAS_TOTAL = 40

_SEM_CACHE = {"Cache-Control": "no-store"}
router = APIRouter(prefix="/api/admin", tags=["admin"], include_in_schema=False)


PAPEL_ADMIN, PAPEL_LEITURA = "admin", "leitura"
MAX_TENTATIVAS_BEARER = 10


def ativo() -> bool:
    return bool(config.admin_token() or config.claude_token())


def _chave() -> bytes:
    return hashlib.sha256(b"rifas-admin|" + config.admin_token().encode() + b"|" + config.claude_token().encode()).digest()


def _assinar(expira: int, papel: str = PAPEL_ADMIN) -> str:
    return f"{expira}.{papel}.{hmac.new(_chave(), f'{expira}|{papel}'.encode(), hashlib.sha256).hexdigest()}"


def cookie_papel(valor: str | None, agora: float | None = None) -> str | None:
    """O papel («admin» ou «leitura») de um cookie valido; None se nao presta, expirou, ou o papel ja nao tem token."""
    if not valor or not ativo():
        return None
    expira, _, resto = valor.partition(".")
    papel = resto.partition(".")[0]
    if not expira.isdigit() or papel not in (PAPEL_ADMIN, PAPEL_LEITURA) or not hmac.compare_digest(valor.encode(), _assinar(int(expira), papel).encode()):
        return None
    if int(expira) <= (time.time() if agora is None else agora):
        return None
    if (papel == PAPEL_ADMIN and not config.admin_token()) or (papel == PAPEL_LEITURA and not config.claude_token()):
        return None
    return papel


def cookie_valido(valor: str | None, agora: float | None = None) -> bool:
    return cookie_papel(valor, agora) is not None


def _bearer(request: Request) -> str:
    h = request.headers.get("authorization", "")
    return h[7:].strip() if h[:7].lower() == "bearer " else ""


def papel_do_pedido(request: Request, serv: Servico | None = None) -> str | None:
    """O papel de quem pede: pelo cookie, ou (so leitura, so em GET) pelo cabecalho `Authorization: Bearer <CLAUDE_TOKEN>`."""
    papel = cookie_papel(request.cookies.get(COOKIE))
    if papel or request.method not in ("GET", "HEAD"):
        return papel
    dado = _bearer(request)
    if not dado or not config.claude_token():
        return None
    ip = request.client.host if request.client else "?"
    if serv is not None and serv.limitador.esgotado(ip, "admin-bearer", MAX_TENTATIVAS_BEARER):
        return None                                           # demasiadas tentativas falhadas: trava ate o certo (anti-adivinhacao)
    if hmac.compare_digest(dado.encode(), config.claude_token().encode()):
        return PAPEL_LEITURA                                   # as certas nao contam: o assistente pode consultar o painel a vontade
    if serv is not None:
        serv.limitador.permitir(ip, "admin-bearer", MAX_TENTATIVAS_BEARER)
    return None


def exigir(request: Request, resposta: Response, serv: Servico = Depends(servico)) -> str:
    """Dependencia de toda a API do painel: sem papel valido (ou sem painel ativo) e 404, como se nao existisse. Devolve o papel."""
    resposta.headers["Cache-Control"] = "no-store"
    papel = papel_do_pedido(request, serv)
    if papel is None:
        raise HTTPException(404, "Rota inexistente", headers=_SEM_CACHE)
    return papel


def exigir_admin(request: Request, resposta: Response, serv: Servico = Depends(servico)) -> str:
    """Como `exigir`, mas so o dono: quem entrou so com leitura (o Claude) recebe 403 nas rotas que mudam alguma coisa."""
    papel = exigir(request, resposta, serv)
    if papel != PAPEL_ADMIN:
        raise HTTPException(403, "Acesso so de leitura.", headers=_SEM_CACHE)
    return papel


def _registar(serv: Servico, acao: str, papel: str = PAPEL_ADMIN, detalhe: str = "") -> None:
    """Conta a acao nas metricas («Acessos ao painel») e guarda-a no registo permanente (`auditoria.py`): nunca parte o pedido se a base falhar."""
    serv.metricas.evento("admin", acao)
    with contextlib.suppress(Exception):
        serv.auditoria.registar(acao, papel, detalhe)


class Credencial(BaseModel):
    token: str


@router.post("/entrar")
async def entrar(c: Credencial, request: Request, resposta: Response, serv: Servico = Depends(servico)) -> dict:
    resposta.headers["Cache-Control"] = "no-store"
    if not ativo():
        raise HTTPException(404, "Rota inexistente", headers=_SEM_CACHE)
    ip = request.client.host if request.client else "?"
    if not serv.limitador.permitir(ip, "admin-entrar", MAX_TENTATIVAS_IP) or not serv.limitador.permitir("*", "admin-entrar-total", MAX_TENTATIVAS_TOTAL):
        serv.metricas.evento("admin", "bloqueado")
        raise HTTPException(429, "Demasiadas tentativas: espere um minuto.", headers=_SEM_CACHE)
    dado = c.token.encode()
    e_admin = bool(config.admin_token()) and hmac.compare_digest(dado, config.admin_token().encode())
    e_leitura = bool(config.claude_token()) and hmac.compare_digest(dado, config.claude_token().encode())
    if not (e_admin or e_leitura):
        serv.metricas.evento("admin", "falhou")
        await asyncio.sleep(0.4)                           # trava ainda mais quem adivinha
        raise HTTPException(401, "Palavra-passe errada.", headers=_SEM_CACHE)
    papel = PAPEL_ADMIN if e_admin else PAPEL_LEITURA
    expira = int(time.time()) + DURACAO_S
    resposta.set_cookie(COOKIE, _assinar(expira, papel), max_age=DURACAO_S, path="/api/admin", httponly=True, samesite="strict",
                        secure=request.url.scheme == "https")
    _registar(serv, "entrou" if e_admin else "entrou_leitura", papel)
    return {"ok": True, "expira": expira, "papel": papel}


@router.post("/sair", status_code=204)
def sair() -> Response:
    resposta = Response(status_code=204, headers=_SEM_CACHE)
    resposta.delete_cookie(COOKIE, path="/api/admin")
    return resposta


@router.get("/estado", dependencies=[Depends(exigir)])
def estado(request: Request, serv: Servico = Depends(servico), papel: str = Depends(exigir)) -> dict:
    """O que se passa AGORA: sistema, limites, proxy e desde quando ha dados."""
    agora = int(time.time())
    atual = serv.observador.ler(len(serv.sessoes), serv.motor.geracao is not None, serv.motor.reinicios)
    return {
        "papel": papel,
        "versao": VERSAO,
        "agora": agora,
        "arranque": serv.metricas.arranque,
        "dados_desde": serv.metricas.dados_desde(),
        "dados_efemeros": config.metricas_efemeras() and not serv.metricas.persistente,
        "base_de_dados": serv.metricas.estado_bd(),
        "sistema": atual,
        "limites": {"max_sessoes": serv.sessoes.maximo, "max_numeros": config.max_numeros(), "max_upload_mb": config.limite_upload_mb(),
                    "validade_min": config.validade_min(), "tempo_maximo_geracao_min": config.tempo_maximo_geracao_min(),
                    "pedidos_pesados_por_min": config.pedidos_pesados_por_min(), "pedidos_leves_por_min": config.pedidos_leves_por_min(),
                    "forwarded_allow_ips": config.proxies_de_confianca()},
        "proxy": serv.metricas.proxy(),
        "acordado": {"ativo": serv.acordado.ativo, "cada_min": round(serv.acordado.cada_s / 60, 1), "chamadas": serv.acordado.chamadas,
                     "falhas": serv.acordado.falhas, "ultima_em": int(serv.acordado.ultima_em) or None, "ultima_ok": serv.acordado.ultima_ok,
                     "ultimo_ms": serv.acordado.ultimo_ms},
        "intervalos": list(INTERVALOS),
    }


@router.get("/dados", dependencies=[Depends(exigir)])
def dados(intervalo: str = "6h", serv: Servico = Depends(servico)) -> dict:
    """As series (para os graficos), os totais e as distribuicoes do intervalo pedido."""
    if intervalo not in INTERVALOS:
        raise HTTPException(422, f"intervalo deve ser um de {', '.join(INTERVALOS)}", headers=_SEM_CACHE)
    janela, passo = INTERVALOS[intervalo]
    desde = int(time.time()) - janela
    m = serv.metricas
    return {
        "intervalo": intervalo,
        "desde": desde,
        "passo_s": passo,
        "sistema": m.serie_sistema(desde, passo),
        "pedidos": m.serie_pedidos(desde, passo),
        "eventos": m.serie_eventos(desde, passo),
        "tabela_pedidos": m.tabela_pedidos(desde),
        "resumo": m.resumo(desde),
    }


def paineis_de_outras_tabelas(serv: Servico):
    """Os paineis que vem de fora das metricas: o gasto da API publica (por dia UTC, como a quota) e as partilhas do editor (so com Postgres)."""
    def extras(primeiro: int, dias: int, desvio: int, desde: int) -> list[dict]:
        saida: list[dict] = []
        try:
            numeros, lotes, chaves = ([0.0] * dias for _ in range(3))
            for d, n, lo, c in serv.chaves.uso_por_dia(primeiro):
                if 0 <= d - primeiro < dias:
                    numeros[d - primeiro], lotes[d - primeiro], chaves[d - primeiro] = n, lo, c
            saida.append(novo_painel("API e partilhas", "api_numeros", "API pública: números gastos", {"Números": numeros},
                                     "Quantos números de rifa a API pública v1 gastou da quota, somando todas as chaves (dias UTC, como a quota)."))
            saida.append(novo_painel("API e partilhas", "api_lotes", "API pública: lotes e chaves", {"Lotes": lotes, "Chaves usadas": chaves},
                                     "Quantos lotes se pediram à API pública e quantas chaves distintas foram usadas em cada dia (dias UTC).", "linhas", "", "max"))
        except Exception:  # noqa: BLE001 - uma tabela em baixo nao pode estragar o resto da vista
            pass
        if serv.partilhas is not None:
            try:
                criadas = [0.0] * dias
                for d, n in serv.partilhas.criadas_por_dia(desde, desvio):
                    if 0 <= d - primeiro < dias:
                        criadas[d - primeiro] = n
                saida.append(novo_painel("API e partilhas", "partilhas", "Desenhos partilhados (editor)", {"Criados": criadas},
                                         "Quantos desenhos do editor se partilharam por ligação em cada dia (só contam os que ainda não passaram do prazo de 90 dias sem acessos)."))
            except Exception:  # noqa: BLE001
                pass
        return saida
    return extras


@router.get("/evolucao", dependencies=[Depends(exigir)])
def evolucao(dias: int = Query(30, ge=1, le=historico.DIAS_HISTORICO_MAX), fuso: int = Query(0, ge=-840, le=840), serv: Servico = Depends(servico)) -> dict:
    """TUDO o que se grava na base, dia a dia (ate `DIAS_MAXIMOS`): uma lista de paineis com as series diarias. `fuso` = minutos de diferenca do browser para UTC
    (local - UTC), para os dias serem os do dono e nao os de Greenwich."""
    if dias > DIAS_MAXIMOS:                                  # mais do que a retencao dos eventos: vem do historico permanente (um resumo por dia)
        try:
            return historico.evolucao_historica(serv.historico, serv.metricas, paineis_de_outras_tabelas(serv), ZoneInfo(config.relatorio_fuso()), dias)
        except Exception:  # noqa: BLE001 - a base em baixo: o painel mostra o aviso de sempre
            raise HTTPException(503, "O historico nao respondeu: tente outra vez daqui a pouco.", headers=_SEM_CACHE) from None
    return serv.metricas.evolucao(dias, fuso, paineis_de_outras_tabelas(serv))


@router.get("/objetivos", dependencies=[Depends(exigir)])
def objetivos_do_dono(serv: Servico = Depends(servico)) -> dict:
    """As metas diarias do dono e como foi o ultimo dia completo face a elas (so contagens)."""
    fuso = ZoneInfo(config.relatorio_fuso())
    try:
        return objetivos.estado(serv.metricas, paineis_de_outras_tabelas(serv), serv.objetivos, fuso)
    except Exception:  # noqa: BLE001 - a base em baixo: o painel mostra o aviso
        raise HTTPException(503, "A base de dados nao respondeu: tente outra vez daqui a pouco.", headers=_SEM_CACHE) from None


class NovoObjetivo(BaseModel):
    chave: str
    meta: float | None = Field(None, description="Meta por dia; vazio apaga o objetivo")


@router.put("/objetivos", dependencies=[Depends(exigir_admin)])
def definir_objetivo(o: NovoObjetivo, serv: Servico = Depends(servico)) -> dict:
    """Define (ou, sem `meta`, apaga) o objetivo diario de um numero. So o dono."""
    if o.chave not in objetivos.KPIS:
        raise HTTPException(422, "Numero desconhecido", headers=_SEM_CACHE)
    if o.meta is None:
        serv.objetivos.apagar(o.chave)
    elif not 0 < o.meta <= objetivos.META_MAX:
        raise HTTPException(422, "A meta tem de ser maior que zero", headers=_SEM_CACHE)
    else:
        serv.objetivos.definir(o.chave, o.meta)
    _registar(serv, "objetivo", detalhe=f"{o.chave}: {'apagado' if o.meta is None else o.meta}")
    return {"chave": o.chave, "meta": o.meta}


@router.get("/auditoria", dependencies=[Depends(exigir)])
def registo_de_acoes(limite: int = Query(200, ge=1, le=1000), serv: Servico = Depends(servico)) -> dict:
    """O registo das acoes do painel (quem, o que, quando; sem dados de visitantes): as mais recentes primeiro. A leitura tambem o ve."""
    try:
        return {"total": serv.auditoria.total(), "retencao_dias": auditoria.RETENCAO_S // 86400, "persistente": bool(config.database_url()),
                "itens": serv.auditoria.recentes(limite)}
    except Exception:  # noqa: BLE001 - a base em baixo: o painel mostra o aviso
        raise HTTPException(503, "O registo nao respondeu: tente outra vez daqui a pouco.", headers=_SEM_CACHE) from None


@router.get("/quotas", dependencies=[Depends(exigir)])
def quotas_do_alojamento(serv: Servico = Depends(servico)) -> dict:
    """As horas do Render no mes e o espaco da base no Neon (estimativas deste servico), com a projecao e os avisos. Ver `quotas.py`."""
    return quotas.estado(serv.metricas)


@router.get("/comentarios", dependencies=[Depends(exigir)])
def comentarios_admin(estado: str = "", serv: Servico = Depends(servico)) -> dict:
    """Os comentarios dos visitantes como o dono os ve: SO o pais, o texto e o estado (mais o id, para agir). Nao interessa quem escreveu.
    `estado` filtra (novo, lido, favorito, escondido); `por_ler` conta os novos, `escondidos` os que a pagina publica nao mostra."""
    c = serv.comentarios
    return {"total": c.total(), "por_ler": c.por_ler(), "escondidos": c.total() - c.total_publico(), "itens": c.para_admin(estado=estado)}


class EstadoComentario(BaseModel):
    estado: str


@router.post("/comentarios/lidos", dependencies=[Depends(exigir_admin)])
def comentarios_lidos(serv: Servico = Depends(servico)) -> dict:
    """Marca todos os comentarios novos como lidos."""
    n = serv.comentarios.marcar_lidos()
    if n:
        _registar(serv, "comentarios_lidos", detalhe=f"{n} comentário(s)")
    return {"marcados": n}


@router.patch("/comentarios/{id_}", dependencies=[Depends(exigir_admin)])
def estado_do_comentario(id_: str, e: EstadoComentario, serv: Servico = Depends(servico)) -> dict:
    """Muda o estado de um comentario: lido, favorito, escondido (deixa de aparecer na pagina publica, sem se apagar) ou novo. So o dono."""
    if e.estado not in opiniao.ESTADOS:
        raise HTTPException(422, "Estado invalido", headers=_SEM_CACHE)
    if not serv.comentarios.definir_estado(id_, e.estado):
        raise HTTPException(404, "Comentário inexistente", headers=_SEM_CACHE)
    _registar(serv, f"comentario_{e.estado}", detalhe=id_)
    return {"estado": e.estado}


@router.delete("/comentarios/{id_}", status_code=204, dependencies=[Depends(exigir_admin)])
def apagar_comentario(id_: str, serv: Servico = Depends(servico)) -> Response:
    """Apaga um comentario (spam, abuso, nome de outra pessoa...). So o dono: a leitura recebe 403."""
    if not serv.comentarios.apagar(id_):
        raise HTTPException(404, "Comentário inexistente", headers=_SEM_CACHE)
    _registar(serv, "comentario_apagado", detalhe=id_)
    return Response(status_code=204, headers=_SEM_CACHE)


@router.get("/relatorio", dependencies=[Depends(exigir)])
def relatorio_estado(serv: Servico = Depends(servico)) -> dict:
    """O relatorio diario por e-mail: se esta ligado, para onde vai (mascarado), o ultimo dia enviado e o ultimo erro."""
    try:
        ultimo = serv.relatorios.ultimo() if serv.relatorios is not None else None
    except Exception:  # noqa: BLE001 - a base em baixo nao estraga o painel
        ultimo = None
    e = serv.estado_relatorio
    return {"ativo": relatorio.ativo(), "tem_chave": bool(config.email_chave()), "destinos": [relatorio.mascarar(x) for x in config.relatorio_destinos()],
            "fuso": config.relatorio_fuso(), "persistente": bool(config.database_url()), "ultimo": ultimo,
            "periodicos": relatorio_periodo.periodicos_ativos(), "ultimo_semana": _ultimo(serv, "semana"), "ultimo_mes": _ultimo(serv, "mes"),
            "erro": e.ultimo_erro, "erro_em": int(e.ultimo_erro_em) or None, "alertas": _estado_alertas(serv)}


def _ultimo(serv: Servico, tipo: str) -> dict | None:
    try:
        return serv.relatorios.ultimo(tipo) if serv.relatorios is not None else None
    except Exception:  # noqa: BLE001
        return None


def _estado_alertas(serv: Servico) -> dict:
    """Os alertas imediatos: se estao ligados, as regras, quando se avisou de cada uma (desde sempre) e o ultimo erro de envio."""
    try:
        ultimos = serv.alertas.ultimos() if serv.alertas is not None else {}
    except Exception:  # noqa: BLE001
        ultimos = {}
    regras = [{"chave": "erros5xx", "texto": f"{alertas.LIMITE_5XX} ou mais erros do servidor (5xx) em {alertas.JANELA_S // 60} minutos"},
              {"chave": "reinicios", "texto": f"{alertas.LIMITE_REINICIOS} ou mais reinícios do motor em {alertas.JANELA_S // 60} minutos"},
              {"chave": "memoria", "texto": f"memória do contentor acima de {alertas.LIMITE_MEMORIA_MB} MB (limite do Render: 512)"},
              {"chave": "base_de_dados", "texto": f"a base de dados sem resposta há {alertas.VERIFICACOES_BD} verificações seguidas"}]
    return {"ativo": alertas.ativos(), "espera_h": alertas.ESPERA_ENTRE_REPETICOES_S // 3600, "regras": regras,
            "ultimos": {r["chave"]: ultimos.get(r["chave"]) for r in regras}, "erro": serv.estado_alertas.ultimo_erro}


def _dia_pedido(dia: str, fuso: ZoneInfo, tipo: str = "dia") -> date:
    ontem = relatorio.dia_de_ontem(time.time(), fuso)
    if not dia:
        return ontem
    try:
        d = date.fromisoformat(dia)
    except ValueError:
        raise HTTPException(422, "Dia invalido (AAAA-MM-DD)", headers=_SEM_CACHE) from None
    limite = 80 if tipo == "dia" else historico.DIAS_HISTORICO_MAX                      # os resumos leem do historico permanente
    if not ontem - timedelta(days=limite) <= d <= ontem:
        raise HTTPException(422, "So ha dados dos ultimos dias (ate ontem)", headers=_SEM_CACHE)
    return d


def _tipo_pedido(tipo: str) -> str:
    if tipo not in relatorio_periodo.TIPOS:
        raise HTTPException(422, "Tipo invalido (dia, semana ou mes)", headers=_SEM_CACHE)
    return tipo


def _periodo_pedido(tipo: str, dia: str, fuso: ZoneInfo) -> tuple[date, date]:
    """O periodo pedido: o que contem `dia` (por omissao, o ultimo completo); o que ainda nao acabou corta-se em ontem."""
    if not dia:
        return relatorio_periodo.ultimo_completo(tipo, relatorio.dia_de_ontem(time.time(), fuso) + timedelta(days=1))
    ini, fim = relatorio_periodo.periodo_de(tipo, _dia_pedido(dia, fuso, tipo))
    return ini, min(fim, relatorio.dia_de_ontem(time.time(), fuso))


@router.get("/relatorio/previa", dependencies=[Depends(exigir)])
def relatorio_previa(dia: str = "", tipo: str = "dia", serv: Servico = Depends(servico)) -> dict:
    """O relatorio tal como seria enviado: assunto, HTML e texto. `tipo`: `dia` (por omissao ontem), `semana` ou `mes` (por omissao o ultimo completo; `dia` = um
    dia desse periodo). Nao envia nada."""
    fuso = ZoneInfo(config.relatorio_fuso())
    tipo = _tipo_pedido(tipo)
    try:
        if tipo == "dia":
            return relatorio.construir(serv.metricas, paineis_de_outras_tabelas(serv), _dia_pedido(dia, fuso), fuso, relatorio._metas(serv.objetivos))
        ini, fim = _periodo_pedido(tipo, dia, fuso)
        return relatorio_periodo.construir_periodo(serv.historico, serv.metricas, paineis_de_outras_tabelas(serv), tipo, ini, fim, fuso)
    except relatorio.ErroRelatorio as e:
        if str(e) == "sem_dados":
            raise HTTPException(404, "Ainda nao ha dias gravados no historico para esse periodo.", headers=_SEM_CACHE) from None
        raise HTTPException(503, "A base de dados nao respondeu: tente outra vez daqui a pouco.", headers=_SEM_CACHE) from None


@router.post("/relatorio/enviar", dependencies=[Depends(exigir_admin)])
def relatorio_enviar(dia: str = "", tipo: str = "dia", serv: Servico = Depends(servico)) -> dict:
    """Envia JA uma copia de teste do relatorio (assunto «[Teste]»). Nao conta como o envio do dia: o da meia-noite sai na mesma."""
    if not relatorio.ativo():
        raise HTTPException(409, "O relatorio por e-mail esta desligado: faltam RESEND_API_KEY e RELATORIO_EMAIL_PARA no Render.", headers=_SEM_CACHE)
    fuso = ZoneInfo(config.relatorio_fuso())
    tipo = _tipo_pedido(tipo)
    try:
        if tipo == "dia":
            relatorio.enviar_relatorio(serv.metricas, paineis_de_outras_tabelas(serv), _dia_pedido(dia, fuso), fuso, teste=True, objetivos=relatorio._metas(serv.objetivos))
        else:
            ini, fim = _periodo_pedido(tipo, dia, fuso)
            relatorio_periodo.enviar_periodo(serv.historico, serv.metricas, paineis_de_outras_tabelas(serv), tipo, ini, fim, fuso, teste=True)
    except (email_envio.ErroEmail, relatorio.ErroRelatorio) as e:
        serv.metricas.evento("admin", "relatorio_teste_falhou")
        raise HTTPException(502, f"Nao foi possivel enviar ({e}).", headers=_SEM_CACHE) from None
    _registar(serv, "relatorio_teste", detalhe=f"{tipo} {dia}".strip())
    return {"enviado": True}


@router.post("/relatorio/alerta-teste", dependencies=[Depends(exigir_admin)])
def alerta_teste(serv: Servico = Depends(servico)) -> dict:
    """Envia JA um alerta de exemplo (assunto «[Teste]») para ver como chega. Nao conta para a espera entre repeticoes."""
    if not alertas.ativos():
        raise HTTPException(409, "Os alertas estao desligados: faltam RESEND_API_KEY e RELATORIO_EMAIL_PARA no Render (ou ALERTAS_EMAIL=0).", headers=_SEM_CACHE)
    assunto, corpo, texto = alertas.montar({"teste": "Isto é um alerta de teste: se o recebeu, os alertas imediatos estão a funcionar."}, time.time(), config.url_publica())
    try:
        email_envio.enviar(config.email_chave(), config.relatorio_remetente(), config.relatorio_destinos(), "[Teste] " + assunto, corpo, texto)
    except email_envio.ErroEmail as e:
        raise HTTPException(502, f"Nao foi possivel enviar ({e}).", headers=_SEM_CACHE) from None
    _registar(serv, "alerta_teste")
    return {"enviado": True}


@router.get("/erros", dependencies=[Depends(exigir)])
def erros(intervalo: str = "24h", serv: Servico = Depends(servico)) -> dict:
    """O livro de erros (observabilidade.py): o que falhou desde o ultimo arranque, agrupado por assinatura (tipo, rota, estado, classe da excecao, sitio)."""
    if intervalo not in INTERVALOS:
        raise HTTPException(422, f"intervalo deve ser um de {', '.join(INTERVALOS)}", headers=_SEM_CACHE)
    return {"intervalo": intervalo, **serv.obs.livro(int(time.time()) - INTERVALOS[intervalo][0])}


# ------------------------------------------------------------------ chaves da API publica v1 (/api/v1): criam-se e revogam-se aqui, nunca no repositorio
class NovaChave(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    quota_dia: int = Field(QUOTA_PADRAO, ge=1, le=100_000_000)             # numeros por dia


@router.get("/chaves", dependencies=[Depends(exigir)])
def chaves(serv: Servico = Depends(servico)) -> list[dict]:
    """As chaves (sem o segredo: so o prefixo) e o que gastaram hoje."""
    saida = []
    for c in serv.chaves.listar():
        usados, lotes = serv.chaves.uso_hoje(c)
        saida.append({"id": c.id, "nome": c.nome, "prefixo": c.prefixo, "criada": c.criada, "ativa": c.ativa, "quota_dia": c.quota,
                      "usados_hoje": usados, "lotes_hoje": lotes})
    return saida


@router.post("/chaves", status_code=201, dependencies=[Depends(exigir_admin)])
def criar_chave(n: NovaChave, serv: Servico = Depends(servico)) -> dict:
    """Cria uma chave. A chave em claro **so aparece nesta resposta** (guarda-se o SHA-256); nao fica em nenhum log."""
    info, chave = serv.chaves.criar(n.nome.strip(), n.quota_dia)
    _registar(serv, "chave_criada", detalhe=f"{info.nome} ({info.id})")
    return {"id": info.id, "nome": info.nome, "prefixo": info.prefixo, "quota_dia": info.quota, "chave": chave}


@router.delete("/chaves/{id_}", status_code=204, dependencies=[Depends(exigir_admin)])
def revogar_chave(id_: str, serv: Servico = Depends(servico)) -> Response:
    if not serv.chaves.revogar(id_):
        raise HTTPException(404, "Chave inexistente", headers=_SEM_CACHE)
    _registar(serv, "chave_revogada", detalhe=id_)
    return Response(status_code=204, headers=_SEM_CACHE)


# ------------------------------------------------------------------ SEO por lingua (titulos, descricoes e guias) editado na base de dados
class TextoSeo(BaseModel):
    chave: str = Field(max_length=120)
    lingua: str = Field(max_length=5)
    valor: str = Field(max_length=2000)


@router.get("/seo", dependencies=[Depends(exigir)])
def seo_ver(lingua: str = "pt", serv: Servico = Depends(servico)) -> dict:
    """Os textos de SEO editaveis numa lingua: o do codigo e o editado. `persistente`: false = a base e local e some quando o Render adormece."""
    from core import i18n
    if lingua not in i18n.LINGUAS:
        raise HTTPException(422, "Língua desconhecida", headers=_SEM_CACHE)
    return {"lingua": lingua, "linguas": list(i18n.LINGUAS), "persistente": serv.seo.persistente, "erro": serv.seo.erro,
            "limites": {"titulo": seo_bd.LARGURA_TITULO, "descricao": list(seo_bd.LARGURA_DESCRICAO), "max": seo_bd.VALOR_MAX},
            "itens": serv.seo.vista(lingua)}


@router.put("/seo", dependencies=[Depends(exigir_admin)])
def seo_guardar(t: TextoSeo, serv: Servico = Depends(servico)) -> dict:
    try:
        valor = serv.seo.definir(t.chave, t.lingua, t.valor)
    except ValueError as e:
        raise HTTPException(422, str(e), headers=_SEM_CACHE) from None
    _registar(serv, "seo_editado", detalhe=f"{t.chave} · {t.lingua}")
    return {"chave": t.chave, "lingua": t.lingua, "valor": valor}


@router.delete("/seo", status_code=204, dependencies=[Depends(exigir_admin)])
def seo_repor(chave: str, lingua: str, serv: Servico = Depends(servico)) -> Response:
    serv.seo.repor(chave, lingua)
    _registar(serv, "seo_reposto", detalhe=f"{chave} · {lingua}")
    return Response(status_code=204, headers=_SEM_CACHE)
