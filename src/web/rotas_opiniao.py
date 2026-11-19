"""Comentários (`/api/comentarios`) e problemas reportados (`/api/problemas`), a API das páginas «Comentários», «Deixar um comentário» e «Reportar problema».

Tudo o que o visitante lê sai já traduzido (cabeçalho `X-Lingua`). Defesas: limites de tamanho, um campo-isco (`site`) que os robôs preenchem, no máximo
`POR_IP_E_HORA` envios por IP e hora (e um teto para o site todo) e, para os problemas, um teto diário. Ver `opiniao.py` (privacidade) e `github_issues.py`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from core import i18n

from . import VERSAO, config, github_issues
from .modelos import ErroApi
from .opiniao import NOME_MAX, POR_IP_E_HORA, POR_PAGINA, TEXTO_MAX, TEXTO_MIN, TOTAL_POR_HORA, limpar_texto
from .rotas import Servico, lingua, servico

router = APIRouter(prefix="/api", tags=["opiniao"])


def _ip(request: Request) -> str:
    return request.client.host if request.client else "?"


def _letras(t: str) -> int:
    return sum(1 for c in t if c.isalnum())


class NovoComentario(BaseModel):
    texto: str = Field(max_length=TEXTO_MAX * 3)         # o corte a sério é feito depois de limpar; isto só trava corpos enormes
    anonimo: bool = True
    nome: str = Field("", max_length=NOME_MAX * 3)
    site: str = Field("", max_length=200)                # campo-isco: escondido no formulário; um robô preenche-o


class ComentarioPublico(BaseModel):
    id: str
    criado: int
    anonimo: bool
    nome: str                                            # vazio: anónimo, ou «Visitante n.º {visitante}»
    visitante: int
    texto: str


class ListaComentarios(BaseModel):
    total: int
    itens: list[ComentarioPublico]
    seguinte: str = ""                                   # passa-se em `antes` para a página seguinte (vazio = não há mais)


class Registado(BaseModel):
    ok: bool = True


@router.get("/comentarios", response_model=ListaComentarios)
def listar(antes: str = "", serv: Servico = Depends(servico)) -> ListaComentarios:
    """Os comentários, mais recentes primeiro. Nunca devolve IPs."""
    itens = serv.comentarios.publicos(antes[:40], POR_PAGINA + 1)
    tem_mais = len(itens) > POR_PAGINA
    itens = itens[:POR_PAGINA]
    return ListaComentarios(total=serv.comentarios.total(), itens=[ComentarioPublico(**i) for i in itens],
                            seguinte=f'{itens[-1]["criado"]}~{itens[-1]["id"]}' if tem_mais and itens else "")


@router.post("/comentarios", response_model=Registado, status_code=201)
def comentar(c: NovoComentario, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Registado:
    if c.site.strip():                                    # um robô: finge-se que correu bem e não se guarda nada
        serv.metricas.evento("limite", "isco")
        return Registado()
    texto = limpar_texto(c.texto, TEXTO_MAX)
    if _letras(texto) < TEXTO_MIN:
        raise ErroApi(422, i18n.traduzir("web_op_curto", lg), "aviso")
    ip = _ip(request)
    if (serv.comentarios.recentes_do_ip(ip) >= POR_IP_E_HORA or serv.comentarios.na_ultima_hora() >= TOTAL_POR_HORA
            or not serv.limitador.permitir(ip, "comentario", 5)):
        serv.metricas.evento("limite", "comentario")
        raise ErroApi(429, i18n.traduzir("web_erro_envios", lg), "aviso")
    nome = limpar_texto(c.nome, NOME_MAX, uma_linha=True)
    serv.comentarios.criar(texto, c.anonimo, nome, ip)
    serv.metricas.evento("comentario", "anonimo" if c.anonimo else ("nome" if nome else "visitante"))     # só o tipo, nunca o texto
    return Registado()


class NovoProblema(BaseModel):
    resumo: str = Field(max_length=300)
    descricao: str = Field(max_length=github_issues.CAMPO_MAX * 2)
    passos: str = Field("", max_length=github_issues.CAMPO_MAX * 2)
    tecnica: str = Field("", max_length=github_issues.TECNICA_MAX * 2)
    pagina: str = Field("", max_length=100)
    site: str = Field("", max_length=200)


class ProblemaRegistado(BaseModel):
    numero: int


@router.post("/problemas", response_model=ProblemaRegistado, status_code=201)
def reportar(p: NovoProblema, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> ProblemaRegistado:
    """Cria um issue no GitHub do projeto (precisa de `GITHUB_ISSUES_TOKEN` e `GITHUB_REPO`: sem eles, 503)."""
    token, repo = config.github_token(), config.github_repo()
    if not (token and repo):
        raise ErroApi(503, i18n.traduzir("web_bug_indisponivel", lg), "aviso")
    if p.site.strip():
        serv.metricas.evento("limite", "isco")
        return ProblemaRegistado(numero=0)
    resumo, descricao = limpar_texto(p.resumo, github_issues.TITULO_MAX, uma_linha=True), limpar_texto(p.descricao, github_issues.CAMPO_MAX)
    if _letras(resumo) < 10 or _letras(descricao) < 10:
        raise ErroApi(422, i18n.traduzir("web_bug_curto", lg), "aviso")
    ip = _ip(request)
    if (not serv.limite_problemas_ip.permitir(ip) or not serv.limite_problemas_total.permitir("*")
            or not serv.limitador.permitir(ip, "problema", 3)):
        serv.metricas.evento("limite", "problema")
        raise ErroApi(429, i18n.traduzir("web_erro_envios", lg), "aviso")
    pagina = limpar_texto(p.pagina, 100, uma_linha=True) or "/"
    corpo = github_issues.corpo_do_issue(descricao, p.passos, p.tecnica, VERSAO, lg, pagina)
    try:
        numero = serv.criar_issue(token, repo, github_issues.neutralizar_titulo(resumo), corpo)
    except github_issues.ErroGithub as e:
        serv.metricas.evento("problema", "falhou", str(e)[:40])
        raise ErroApi(502, i18n.traduzir("web_bug_falhou", lg), "erro") from None
    serv.metricas.evento("problema", "ok")
    return ProblemaRegistado(numero=numero)

