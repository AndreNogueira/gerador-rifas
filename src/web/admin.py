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
import hashlib
import hmac
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from . import VERSAO, config
from . import seo_bd
from .chaves_api import QUOTA_PADRAO
from .metricas import INTERVALOS
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
    serv.metricas.evento("admin", "entrou" if e_admin else "entrou_leitura")
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
    serv.metricas.evento("admin", "chave_criada")
    return {"id": info.id, "nome": info.nome, "prefixo": info.prefixo, "quota_dia": info.quota, "chave": chave}


@router.delete("/chaves/{id_}", status_code=204, dependencies=[Depends(exigir_admin)])
def revogar_chave(id_: str, serv: Servico = Depends(servico)) -> Response:
    if not serv.chaves.revogar(id_):
        raise HTTPException(404, "Chave inexistente", headers=_SEM_CACHE)
    serv.metricas.evento("admin", "chave_revogada")
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
    serv.metricas.evento("admin", "seo_editado")
    return {"chave": t.chave, "lingua": t.lingua, "valor": valor}


@router.delete("/seo", status_code=204, dependencies=[Depends(exigir_admin)])
def seo_repor(chave: str, lingua: str, serv: Servico = Depends(servico)) -> Response:
    serv.seo.repor(chave, lingua)
    serv.metricas.evento("admin", "seo_reposto")
    return Response(status_code=204, headers=_SEM_CACHE)
