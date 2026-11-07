"""A API das sessoes: carregar o template e os algarismos, calcular o formulario, pre-visualizar, gerar, cancelar, descarregar, limpar.

O servico e publico (sem palavra-passe): cada rota pesada passa pelos limites (tamanho, pedidos por IP, uma geracao de cada vez).
Os textos que o utilizador le saem na lingua do pedido (cabecalho `X-Lingua`, senao o `Accept-Language` do browser).
"""
from __future__ import annotations

import asyncio
import shutil
import urllib.parse
from concurrent.futures.process import BrokenProcessPool
from dataclasses import dataclass
from pathlib import Path

import core
from core import entradas, i18n, pedido, saida
from core.armazenamento import ArmazenamentoCheio
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import FileResponse, StreamingResponse

from . import config, trabalhos
from .limites import Limitador, ler_corpo
from .modelos import Calculo, Campos, ErroApi, Sessao, TrabalhoEstado
from .sessoes import (Geracao, SessaoEstado, Sessoes, calcular, folha_dos_campos, ler_progresso, texto_de_erro,
                      trabalho_dos_campos, vista, _trabalho)
from .trabalhos import CANCELAR, PROGRESSO, Motor, Ocupado


@dataclass
class Servico:
    sessoes: Sessoes
    motor: Motor
    limitador: Limitador


router = APIRouter(prefix="/api/sessoes", tags=["sessoes"])


# ------------------------------------------------------------------ dependencias
def servico(request: Request) -> Servico:
    return request.app.state.servico


def lingua(request: Request) -> str:
    """A lingua do pedido: `X-Lingua` (a que o utilizador escolheu), senao a do browser, senao ingles."""
    escolhida = request.headers.get("x-lingua", "")
    return escolhida if escolhida in i18n.LINGUAS else i18n.lingua_de_accept_language(request.headers.get("accept-language"))


def _ip(request: Request) -> str:
    return request.client.host if request.client else "?"


def _limite(categoria: str, maximo):
    def verificar(request: Request, serv: Servico = Depends(servico)) -> None:
        if not serv.limitador.permitir(_ip(request), categoria, maximo()):
            raise ErroApi(429, i18n.traduzir("web_ocupado", lingua(request)), "aviso")
    return verificar


pesado = _limite("pesado", config.pedidos_pesados_por_min)       # uploads, pre-visualizar, gerar
leve = _limite("leve", config.pedidos_leves_por_min)             # calculos do formulario, cancelar...


def _ocupado(lg: str) -> ErroApi:
    return ErroApi(503, i18n.traduzir("web_ocupado", lg), "aviso")


def _sessao(serv: Servico, id_: str) -> tuple:
    """(SessaoEstado, pasta). 404 se nao existe (o frontend cria outra: um reinicio do servidor apaga as sessoes)."""
    try:
        s = serv.sessoes.obter(id_)
    except ValueError:
        s = None
    if s is None:
        raise ErroApi(404, "Sessão expirada", "erro")
    return s, serv.sessoes.pasta(s)


def _levantar(r: tuple, lg: str) -> None:
    """Um erro do worker -> ErroApi (as regras do motor sao «aviso»: o utilizador pode corrigir; o resto e «erro»)."""
    tipo = "aviso" if r[0] in ("erro", "alg") else "erro"
    raise ErroApi(422 if tipo == "aviso" else 500, texto_de_erro(r, lg), tipo)


def _nome_do_ficheiro(request: Request) -> str:
    """O nome que o browser diz (cabecalho X-Nome, codificado). So serve para mostrar: nunca se usa como caminho."""
    nome = urllib.parse.unquote(request.headers.get("x-nome", ""))[:200]
    return "".join(c for c in nome if c.isprintable()).strip()


def _limpar_previa(s: SessaoEstado, pasta: Path) -> None:
    s.previa_titulo = None
    (pasta / "previa.pdf").unlink(missing_ok=True)


async def _analisar(s: SessaoEstado, serv: Servico, pasta: Path, lg: str) -> None:
    """Le o template (e os algarismos) no processo do motor e guarda o resultado na sessao."""
    try:
        s.analise = await serv.motor.curto(trabalhos.analisar, str(pasta), s.tpl_nome, s.alg_nome)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None


def _motivo(e: BaseException) -> str:
    return "tempo excedido" if isinstance(e, asyncio.TimeoutError) else "o motor foi interrompido (memória insuficiente?)"


def _guardar(serv: Servico, s: SessaoEstado, nome: str, dados: bytes, lg: str) -> None:
    try:
        serv.sessoes.armazem.guardar(s.id, nome, dados)
    except ArmazenamentoCheio:
        raise ErroApi(413, i18n.traduzir("web_demasiado_grande", lg, mb=config.limite_sessao_mb()), "aviso") from None


# ------------------------------------------------------------------ sessao
@router.post("", response_model=Sessao, status_code=201, dependencies=[Depends(leve)])
def criar(serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s = serv.sessoes.criar()
    if s is None:
        raise _ocupado(lg)
    return vista(s, lg, serv.sessoes.pasta(s))


@router.get("/{id_}", response_model=Sessao)
def ver(id_: str, desde: int = 0, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    return vista(s, lg, pasta, max(0, desde))


@router.delete("/{id_}", status_code=204, dependencies=[Depends(leve)])
def apagar(id_: str, serv: Servico = Depends(servico)) -> Response:
    """«Limpar tudo»: apaga os ficheiros e o estado (e para a geracao, se ha uma a correr)."""
    try:
        s = serv.sessoes.obter(id_)
    except ValueError:
        s = None
    if s is not None:
        if s.a_correr and serv.motor.geracao == s.id:
            serv.motor.reiniciar()                          # o processo esta a gerar para esta sessao: matar e recriar
        serv.sessoes.apagar(id_)
    return Response(status_code=204)


# ------------------------------------------------------------------ uploads (corpo em bruto, sem multipart: o teto aplica-se ao fluxo)
@router.put("/{id_}/template", response_model=Sessao, dependencies=[Depends(pesado)])
async def carregar_template(id_: str, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    dados = await ler_corpo(request, config.limite_upload_mb() * 1024 * 1024, i18n.traduzir("web_demasiado_grande", lg, mb=config.limite_upload_mb()))
    nome = _nome_do_ficheiro(request) or "template.pdf"
    _limpar_previa(s, pasta)
    s.gerar = Geracao()
    s.tpl_nome = nome
    if entradas.detetar_tipo(dados) != "pdf":                # o tipo REAL, pelos bytes (o nome do cliente nao conta)
        (pasta / "template.pdf").unlink(missing_ok=True)
        s.analise = ("erro", "err_abrir_template", {"erro": f"«{nome}»"}, [])
        return vista(s, lg, pasta)
    _guardar(serv, s, "template.pdf", dados, lg)
    await _analisar(s, serv, pasta, lg)
    return vista(s, lg, pasta)


@router.put("/{id_}/algarismos", response_model=Sessao, dependencies=[Depends(pesado)])
async def carregar_algarismos(id_: str, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    dados = await ler_corpo(request, config.limite_upload_mb() * 1024 * 1024, i18n.traduzir("web_demasiado_grande", lg, mb=config.limite_upload_mb()))
    nome = _nome_do_ficheiro(request) or "algarismos"
    tipo = entradas.detetar_tipo(dados)
    if tipo is None:
        s.alg_erro, s.alg_nome = ("erro", "err_formato", {}), nome
        return vista(s, lg, pasta)
    for antigo in serv.sessoes.armazem.listar(s.id):
        if antigo.startswith("algarismos."):
            (pasta / antigo).unlink(missing_ok=True)
    _guardar(serv, s, f"algarismos.{tipo}", dados, lg)
    s.alg_nome, s.alg_erro = nome, None
    _limpar_previa(s, pasta)
    s.gerar = Geracao()
    if (pasta / "template.pdf").is_file():
        await _analisar(s, serv, pasta, lg)
    return vista(s, lg, pasta)


def _pdf_inline(caminho: Path) -> FileResponse:
    """Para o visor do browser: inline, sem cache, sem adivinhar o tipo."""
    return FileResponse(caminho, media_type=saida.MEDIA_PDF,
                        headers={"Content-Disposition": "inline", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/{id_}/modelo.pdf")
def modelo(id_: str, serv: Servico = Depends(servico)) -> FileResponse:
    s, pasta = _sessao(serv, id_)
    if not (pasta / "template.pdf").is_file():
        raise ErroApi(404, "Sem template", "erro")
    return _pdf_inline(pasta / "template.pdf")


@router.get("/{id_}/previa.pdf")
def previa_pdf(id_: str, serv: Servico = Depends(servico)) -> FileResponse:
    s, pasta = _sessao(serv, id_)
    if not (pasta / "previa.pdf").is_file():
        raise ErroApi(404, "Sem pré-visualização", "erro")
    return _pdf_inline(pasta / "previa.pdf")


# ------------------------------------------------------------------ formulario
@router.post("/{id_}/calcular", response_model=Calculo, dependencies=[Depends(leve)])
def calcular_formulario(id_: str, campos: Campos, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Calculo:
    """O painel da folha e o resumo do pedido (o que a app Windows recalculava a cada tecla)."""
    s, _ = _sessao(serv, id_)
    return calcular(s.info, campos, lg)


def _validar(s: SessaoEstado, c: Campos, lg: str, pasta: Path, geracao: bool) -> core.Trabalho:
    """As mesmas verificacoes da app antes de pre-visualizar/gerar; os erros do motor saem como aviso (ErroApi 422)."""
    if s.analise is None or s.analise[0] != "ok":
        raise ErroApi(409, i18n.traduzir("c1_vazio" if s.analise is None else "c2_precisa", lg), "aviso")
    try:
        with i18n.com_lingua(lg):
            tr = trabalho_dos_campos(c)
            if not geracao and (not 1 <= tr.digitos <= core.MAX_DIGITOS or tr.fim < tr.inicio):
                raise core.ErroRifas("conf_numeros")             # a pre-visualizacao pede numeros validos; ao gerar, quem fala e o motor
            disp, _ = folha_dos_campos(s.info, c)
            if geracao:
                if not tr.nome:
                    raise core.ErroRifas("err_nome")
                if tr.fim - tr.inicio + 1 > config.max_numeros():
                    raise core.ErroRifas("web_demasiados", max=config.max_numeros())
                tr.saida = pasta / "saida"
                core.planear(tr, pedido.rifas_por_pagina(disp, s.info))        # valida tudo antes de comecar
            return tr
    except core.ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None


# ------------------------------------------------------------------ pre-visualizar
@router.post("/{id_}/previa", response_model=Sessao, dependencies=[Depends(pesado)])
async def previa(id_: str, campos: Campos, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    tr = _validar(s, campos, lg, pasta, geracao=False)
    try:
        r = await serv.motor.curto(trabalhos.previa, str(pasta), s.tpl_nome, s.alg_nome, campos.papel, campos.margem, campos.porfolha,
                                   tr.inicio, tr.fim, tr.digitos)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if r[0] != "ok":
        _levantar(r, lg)
    _guardar(serv, s, "previa.pdf", r[1], lg)
    s.previa_n += 1
    s.previa_titulo = ("previa_titulo_n", {"de": tr.inicio, "ate": min(tr.fim, tr.inicio + r[2] - 1)})
    return vista(s, lg, pasta)


# ------------------------------------------------------------------ gerar, acompanhar, cancelar, descarregar
async def _geracao(serv: Servico, s: SessaoEstado, pasta: Path, args: tuple) -> None:
    """A tarefa que espera pelo processo do motor e passa o resultado para o estado da sessao."""
    g = s.gerar
    try:
        r = await serv.motor.gerar(s.id, *args)
        ler_progresso(g, pasta)
        if r[0] == "ok":
            g.resultados = r[1]
            try:
                g.entrega = saida.entrega(r[1], g.nome)
            except ValueError:
                g.entrega = None                              # nenhum PDF passou a verificacao
            g.estado = "erros" if any(not x.ok for x in r[1]) else "ok"
        elif r[0] == "cancelado":
            g.estado = "cancelado"
        else:
            g.estado, g.erro = "falhou", (r[0], r[1], r[2]) if r[0] in ("erro", "alg") else ("exc", r[1])
    except asyncio.CancelledError:
        g.estado = "cancelado"
        raise
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        ler_progresso(g, pasta)
        if g.estado == "a_cancelar":                         # o processo foi morto de proposito para cancelar (`_cancelar_a_forca`)
            g.estado = "cancelado"
        else:
            g.estado, g.erro = "falhou", ("exc", _motivo(e) + f" ({config.tempo_maximo_geracao_min()} min)" if isinstance(e, asyncio.TimeoutError) else _motivo(e))
    except Exception as e:  # noqa: BLE001 - nunca um traceback para o utilizador
        g.estado, g.erro = "falhou", ("exc", f"{type(e).__name__}: {e}")


@router.post("/{id_}/gerar", response_model=Sessao, status_code=202, dependencies=[Depends(pesado)])
async def gerar(id_: str, campos: Campos, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    tr = _validar(s, campos, lg, pasta, geracao=True)
    if not serv.motor.reservar(s.id):                        # so uma geracao de cada vez em todo o servidor
        raise _ocupado(lg)
    try:
        saida_dir = pasta / "saida"
        if saida_dir.is_dir():
            shutil.rmtree(saida_dir, ignore_errors=True)     # nao se misturam PDFs de geracoes diferentes
        for f in (PROGRESSO, CANCELAR):
            (pasta / f).unlink(missing_ok=True)
        s.gerar = Geracao(estado="a_gerar", nome=tr.nome)
        args = (str(pasta), s.tpl_nome, s.alg_nome, tr.nome, tr.inicio, tr.fim, tr.por_ficheiro, tr.digitos, campos.papel, campos.margem,
                campos.porfolha)
        s.tarefa = asyncio.create_task(_geracao(serv, s, pasta, args))
    except BaseException:
        serv.motor.geracao = None
        raise
    return vista(s, lg, pasta)


@router.get("/{id_}/trabalho", response_model=TrabalhoEstado)
def trabalho(id_: str, desde: int = 0, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> TrabalhoEstado:
    s, pasta = _sessao(serv, id_)
    return _trabalho(s, lg, max(0, desde), pasta)


_TAREFAS: set = set()


async def _cancelar_a_forca(serv: Servico, s: SessaoEstado) -> None:
    """Se passado o tempo o motor ainda nao parou (esta a gravar/verificar o PDF), mata o processo: o cancelamento tem de ser eficaz."""
    await asyncio.sleep(config.espera_cancelar_s())
    if s.gerar.estado == "a_cancelar" and serv.motor.geracao == s.id:
        serv.motor.reiniciar()                               # `_geracao` ve o processo morrer e passa a «cancelado»


@router.post("/{id_}/cancelar", response_model=TrabalhoEstado, dependencies=[Depends(leve)])
async def cancelar(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> TrabalhoEstado:
    s, pasta = _sessao(serv, id_)
    if s.gerar.estado == "a_gerar":
        (pasta / CANCELAR).touch()                           # o motor consulta-a a cada pagina (trabalhos.Bandeira)
        s.gerar.estado = "a_cancelar"
        tarefa = asyncio.create_task(_cancelar_a_forca(serv, s))
        _TAREFAS.add(tarefa)                                 # sem uma referencia o asyncio pode descartar a tarefa a meio
        tarefa.add_done_callback(_TAREFAS.discard)
    return _trabalho(s, lg, 0, pasta)


def _cabecalho_download(nome: str) -> str:
    ascii_ = "".join(c if 32 <= ord(c) < 127 and c not in '"\\' else "_" for c in nome) or "rifas"
    return f"attachment; filename=\"{ascii_}\"; filename*=UTF-8''{urllib.parse.quote(nome, safe='')}"


@router.get("/{id_}/descarregar")
def descarregar(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> StreamingResponse:
    s, _ = _sessao(serv, id_)
    e = s.gerar.entrega
    if e is None or s.gerar.estado not in ("ok", "erros"):
        raise ErroApi(404, "Nada para descarregar", "erro")
    cabecalhos = {"Content-Disposition": _cabecalho_download(e.nome), "Cache-Control": "no-store"}
    if e.tipo == "pdf":
        cabecalhos["Content-Length"] = str(e.ficheiros[0].stat().st_size)
    return StreamingResponse(saida.conteudo_da_entrega(e), media_type=e.media_type, headers=cabecalhos)
