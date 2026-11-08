"""O painel de administracao (`/admin`): so para o dono do servico.

ACESSO: uma palavra-passe longa na variavel de ambiente `ADMIN_TOKEN` (no Render, em Environment: NAO e um *secret* do GitHub e nunca
vai para o repositorio). Sem ela (ou com menos de 12 caracteres) o painel NAO EXISTE: a pagina e a API devolvem 404.
 - `POST /api/admin/entrar` troca a palavra-passe por um cookie assinado (HttpOnly, SameSite=Strict, so enviado a `/api/admin`, 8 h);
   a palavra-passe nunca fica no browser nem no JS. Comparacao em tempo constante; 5 tentativas por minuto por IP e 40 no total.
 - Sem cookie valido, TODA a API do painel responde 404 (nao confirma que existe). Respostas `no-store`; `noindex`.
 - Mudar o `ADMIN_TOKEN` invalida todos os cookies (a chave de assinatura deriva dele).
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from . import VERSAO, config
from .metricas import INTERVALOS
from .rotas import Servico, servico

COOKIE = "rifas_admin"
DURACAO_S = 8 * 3600
MAX_TENTATIVAS_IP = 5
MAX_TENTATIVAS_TOTAL = 40

_SEM_CACHE = {"Cache-Control": "no-store"}
router = APIRouter(prefix="/api/admin", tags=["admin"], include_in_schema=False)


def ativo() -> bool:
    return bool(config.admin_token())


def _chave() -> bytes:
    return hashlib.sha256(b"rifas-admin|" + config.admin_token().encode()).digest()


def _assinar(expira: int) -> str:
    return f"{expira}.{hmac.new(_chave(), str(expira).encode(), hashlib.sha256).hexdigest()}"


def cookie_valido(valor: str | None, agora: float | None = None) -> bool:
    if not valor or not ativo():
        return False
    expira, _, assinatura = valor.partition(".")
    if not expira.isdigit() or not hmac.compare_digest(valor.encode(), _assinar(int(expira)).encode()):
        return False
    return int(expira) > (time.time() if agora is None else agora)


def exigir(request: Request, resposta: Response) -> None:
    """Dependencia de toda a API do painel: sem cookie valido (ou sem painel ativo) e 404, como se nao existisse."""
    resposta.headers["Cache-Control"] = "no-store"
    if not cookie_valido(request.cookies.get(COOKIE)):
        raise HTTPException(404, "Rota inexistente", headers=_SEM_CACHE)


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
    if not hmac.compare_digest(c.token.encode(), config.admin_token().encode()):
        serv.metricas.evento("admin", "falhou")
        await asyncio.sleep(0.4)                           # trava ainda mais quem adivinha
        raise HTTPException(401, "Palavra-passe errada.", headers=_SEM_CACHE)
    expira = int(time.time()) + DURACAO_S
    resposta.set_cookie(COOKIE, _assinar(expira), max_age=DURACAO_S, path="/api/admin", httponly=True, samesite="strict",
                        secure=request.url.scheme == "https")
    serv.metricas.evento("admin", "entrou")
    return {"ok": True, "expira": expira}


@router.post("/sair", status_code=204)
def sair() -> Response:
    resposta = Response(status_code=204, headers=_SEM_CACHE)
    resposta.delete_cookie(COOKIE, path="/api/admin")
    return resposta


@router.get("/estado", dependencies=[Depends(exigir)])
def estado(request: Request, serv: Servico = Depends(servico)) -> dict:
    """O que se passa AGORA: sistema, limites, proxy e desde quando ha dados."""
    agora = int(time.time())
    atual = serv.observador.ler(len(serv.sessoes), serv.motor.geracao is not None, serv.motor.reinicios)
    return {
        "versao": VERSAO,
        "agora": agora,
        "arranque": serv.metricas.arranque,
        "dados_desde": serv.metricas.dados_desde(),
        "dados_efemeros": config.metricas_efemeras(),
        "sistema": atual,
        "limites": {"max_sessoes": serv.sessoes.maximo, "max_numeros": config.max_numeros(), "max_upload_mb": config.limite_upload_mb(),
                    "validade_min": config.validade_min(), "tempo_maximo_geracao_min": config.tempo_maximo_geracao_min(),
                    "pedidos_pesados_por_min": config.pedidos_pesados_por_min(), "pedidos_leves_por_min": config.pedidos_leves_por_min(),
                    "forwarded_allow_ips": config.proxies_de_confianca()},
        "proxy": serv.metricas.proxy(),
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
