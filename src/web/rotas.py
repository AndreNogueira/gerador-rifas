"""A API das sessoes: carregar o template e os algarismos, calcular o formulario, pre-visualizar, gerar, cancelar, descarregar, limpar.

O servico e publico (sem palavra-passe): cada rota pesada passa pelos limites (tamanho, pedidos por IP, uma geracao de cada vez).
Os textos que o utilizador le saem na lingua do pedido (cabecalho `X-Lingua`, senao o `Accept-Language` do browser).
"""
from __future__ import annotations

import asyncio
import shutil
import time
import urllib.parse
from concurrent.futures.process import BrokenProcessPool
from dataclasses import dataclass, field
from pathlib import Path

import core
from core import entradas, i18n, pedido, saida
from core.armazenamento import ArmazenamentoCheio
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import FileResponse, StreamingResponse

from . import VERSAO, config, seo, trabalhos
from .limites import Limitador, ler_corpo
from .manter_acordado import EstadoAcordado
from .metricas import Metricas, classe_do_ecra, dispositivo, familia, modelo_limpo, pais_do_cabecalho
from . import github_issues
from .observabilidade import Observabilidade
from .opiniao import LimiteHorario
from .modelos import Calculo, Campos, Ecra, ErroApi, Sessao, TrabalhoEstado
from .sessoes import (Geracao, SessaoEstado, Sessoes, calcular, folha_dos_campos, ler_progresso, texto_de_erro,
                      trabalho_dos_campos, vista, _trabalho)
from .sistema import Observador
from .trabalhos import CANCELAR, PROGRESSO, Motor, Ocupado


@dataclass
class Servico:
    sessoes: Sessoes
    motor: Motor
    limitador: Limitador
    metricas: Metricas = field(default_factory=Metricas)           # contagens para o painel de administracao (sem dados pessoais)
    observador: Observador | None = None
    acordado: EstadoAcordado = field(default_factory=EstadoAcordado)       # o anti-sono (ver manter_acordado.py)
    partilhas: object | None = None                                         # `partilhas.Partilhas` (desenhos do editor partilhados por ligacao): so com DATABASE_URL
    chaves: object | None = None                                            # `chaves_api.Chaves`: as chaves da API publica v1 (Postgres, ou SQLite local)
    seo: object | None = None                                               # `seo_bd.SeoBd`: os textos de SEO editados no painel (Postgres, ou SQLite local)
    obs: Observabilidade = field(default_factory=lambda: Observabilidade(versao=VERSAO))   # registo estruturado e livro de erros (observabilidade.py)
    comentarios: object | None = None                                       # `opiniao.Comentarios`: os comentarios dos visitantes (Postgres, ou SQLite local)
    limite_problemas_ip: LimiteHorario = field(default_factory=lambda: LimiteHorario(3))        # problemas reportados por IP e hora
    limite_problemas_total: LimiteHorario = field(default_factory=lambda: LimiteHorario(20))    # e no site todo
    criar_issue: object = github_issues.criar_issue                         # troca-se nos testes: nunca se chama o GitHub a sério

    def __post_init__(self) -> None:
        if self.observador is None:
            self.observador = Observador(self.sessoes.armazem.raiz)
        self.metricas.observar = self.obs.evento


router = APIRouter(prefix="/api/sessoes", tags=["sessoes"])
# os ids de `temas.ts`: o que o cliente diz (X-Visual) so entra nas metricas se estiver aqui
_VISUAIS = frozenset({"premiado", "quermesse", "arcade", "brutalista", "risografia", "janela98", "gala", "natal", "matrix", "halloween", "praia", "jornal", "terminal", "circo"})


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
            serv.metricas.evento("limite", categoria)
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
def criar(request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s = serv.sessoes.criar()
    if s is None:
        serv.metricas.evento("limite", "sessoes")
        raise _ocupado(lg)
    visual = request.headers.get("x-visual", "")
    serv.metricas.evento("sessao", lg, visual if visual in _VISUAIS else "outro", dispositivo(request.headers.get("user-agent", "")))
    serv.metricas.evento("pais", pais_do_cabecalho(request.headers.get("cf-ipcountry")))       # so o codigo do pais (a rede do alojamento deduz-o do IP; o IP nao se guarda)
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
        serv.metricas.evento("template", "tipo_invalido")
        return vista(s, lg, pasta)
    _guardar(serv, s, "template.pdf", dados, lg)
    await _analisar(s, serv, pasta, lg)
    serv.metricas.evento("template", "ok" if s.analise and s.analise[0] in ("ok", "alg") else (s.analise[0] if s.analise else "erro"), v2=len(dados) / 1024)   # «alg»: o template esta bem, faltam os algarismos
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
        serv.metricas.evento("algarismos", "tipo_invalido")
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
    serv.metricas.evento("algarismos", "ok" if s.analise is None or s.analise[0] == "ok" else s.analise[0], v2=len(dados) / 1024)
    return vista(s, lg, pasta)


@router.put("/{id_}/logotipo", response_model=Sessao, dependencies=[Depends(pesado)])
async def carregar_logotipo(id_: str, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    """O logotipo da marca propria (PNG ou JPG, ate 2 MB): valida-se (tipo real, tamanho, imagem inteira) antes de se guardar."""
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    aviso = i18n.traduzir("err_logotipo", lg, mb=core.marca.MAX_MB)
    dados = await ler_corpo(request, core.marca.MAX_MB * 1024 * 1024, aviso)
    try:
        core.marca.ler_logotipo(dados)
    except core.ErroRifas as e:
        serv.metricas.evento("logotipo", "invalido")
        raise ErroApi(422, e.em(lg), "aviso") from None
    for antigo in pasta.glob("logotipo.*"):
        antigo.unlink(missing_ok=True)
    _guardar(serv, s, f"logotipo.{entradas.detetar_tipo(dados)}", dados, lg)
    s.logo_nome = _nome_do_ficheiro(request) or "logotipo"
    _limpar_previa(s, pasta)
    serv.metricas.evento("logotipo", "ok", v2=len(dados) / 1024)
    return vista(s, lg, pasta)


@router.delete("/{id_}/logotipo", response_model=Sessao, dependencies=[Depends(leve)])
def remover_logotipo(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    for antigo in pasta.glob("logotipo.*"):
        antigo.unlink(missing_ok=True)
    s.logo_nome = ""
    _limpar_previa(s, pasta)
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


async def _png(serv: Servico, pdf: Path, lg: str) -> FileResponse:
    """O PNG da 1.a pagina de `pdf` (cache ao lado do PDF: so se refaz se o PDF mudou)."""
    cache = pdf.with_suffix(".png")
    if not (cache.is_file() and cache.stat().st_mtime >= pdf.stat().st_mtime):
        try:
            r = await serv.motor.curto(trabalhos.png, str(pdf), 150)
        except Ocupado:
            raise _ocupado(lg) from None
        except (asyncio.TimeoutError, BrokenProcessPool) as e:
            raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
        if r[0] != "ok":
            _levantar(r, lg)
        cache.write_bytes(r[1])
    return FileResponse(cache, media_type="image/png", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/{id_}/modelo.png")
async def modelo_png(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> FileResponse:
    s, pasta = _sessao(serv, id_)
    if not (pasta / "template.pdf").is_file():
        raise ErroApi(404, "Sem template", "erro")
    return await _png(serv, pasta / "template.pdf", lg)


@router.get("/{id_}/previa.png")
async def previa_png(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> FileResponse:
    s, pasta = _sessao(serv, id_)
    if not (pasta / "previa.pdf").is_file():
        raise ErroApi(404, "Sem pré-visualização", "erro")
    return await _png(serv, pasta / "previa.pdf", lg)


# ------------------------------------------------------------------ formulario
@router.post("/{id_}/calcular", response_model=Calculo, dependencies=[Depends(leve)])
def calcular_formulario(id_: str, campos: Campos, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Calculo:
    """O painel da folha e o resumo do pedido (o que a app Windows recalculava a cada tecla)."""
    s, _ = _sessao(serv, id_)
    return calcular(s.info, campos, lg)


def _qr_dos_campos(c: Campos, request: Request, lg: str) -> tuple | None:
    """Os dados do QR de verificacao (base do site, chave, evento, canto, tamanho) ou None. Sem `VERIFICACAO_CHAVE` pedir QR e um aviso."""
    if c.qr != "1":
        return None
    chave = config.verificacao_chave()
    if not chave:
        raise ErroApi(422, i18n.traduzir("err_qr_indisponivel", lg), "aviso")
    posicao = c.qr_posicao if c.qr_posicao in core.qr.POSICOES else "ie"
    tamanho = min(max(int(c.qr_tamanho), core.qr.TAMANHO_MIN), core.qr.TAMANHO_MAX) if c.qr_tamanho.isdigit() else core.qr.TAMANHO_PADRAO
    return (seo.url_publica(request), chave, core.qr.evento_limpo(c.nome), posicao, tamanho)


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
                if core.series.contar(tr) > config.max_numeros():          # numeros do intervalo (sem os saltados) x series
                    raise core.ErroRifas("web_demasiados", max=config.max_numeros())
                if c.qr == "1" and disp is not None and core.series.contar(tr) > config.max_numeros_qr():
                    raise core.ErroRifas("web_demasiados", max=config.max_numeros_qr())      # o QR custa CPU: teto proprio
                tr.saida = pasta / "saida"
                core.planear(tr, pedido.rifas_por_pagina(disp, s.info))        # valida tudo antes de comecar
            return tr
    except core.ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None


# ------------------------------------------------------------------ pre-visualizar
@router.post("/{id_}/previa", response_model=Sessao, dependencies=[Depends(pesado)])
async def previa(id_: str, campos: Campos, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    tr = _validar(s, campos, lg, pasta, geracao=False)
    qr = _qr_dos_campos(campos, request, lg)
    t0 = time.perf_counter()
    try:
        r = await serv.motor.curto(trabalhos.previa, str(pasta), s.tpl_nome, s.alg_nome, campos.papel, campos.margem, campos.porfolha,
                                   tr.inicio, tr.fim, tr.digitos, tr.prefixos[0] if tr.prefixos else "", core.series.cor_da_serie(tr, 0) or tr.cor_numeros, tr.saltar, campos.marcas == "1",
                                   campos.logo_posicao, campos.logo_tamanho, qr)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if r[0] != "ok":
        serv.metricas.evento("previa", r[0], v1=(time.perf_counter() - t0) * 1000)
        _levantar(r, lg)
    serv.metricas.evento("previa", "ok", v1=(time.perf_counter() - t0) * 1000)
    _guardar(serv, s, "previa.pdf", r[1], lg)
    s.previa_n += 1
    s.previa_titulo = ("previa_titulo_n", {"de": tr.inicio, "ate": min(tr.fim, tr.inicio + r[2] - 1)})
    return vista(s, lg, pasta)


# ------------------------------------------------------------------ gerar, acompanhar, cancelar, descarregar
def _motivo_da_falha(g: Geracao) -> str:
    """Uma etiqueta CURTA e sem dados do utilizador para a falha de uma geracao (a chave da regra do motor, ou a categoria)."""
    if g.erro is None:
        return ""
    if g.erro[0] in ("erro", "alg"):
        return str(g.erro[1])
    texto = str(g.erro[1])
    if texto.startswith("tempo excedido"):
        return "tempo"
    if "motor foi interrompido" in texto:
        return "motor"
    return texto.split(":", 1)[0][:30]


async def _geracao(serv: Servico, s: SessaoEstado, pasta: Path, args: tuple) -> None:
    """Corre a geracao e regista nas metricas como acabou (sem nomes de ficheiros nem conteudo: so estado, numeros e duracao)."""
    t0 = time.perf_counter()
    try:
        await _geracao_interna(serv, s, pasta, args)
    finally:
        g = s.gerar
        numeros = max(0, args[5] - args[4] + 1)
        serv.metricas.evento("geracao", g.estado, _motivo_da_falha(g), "unico" if args[6] >= numeros else "varios",
                             v1=time.perf_counter() - t0, v2=numeros, v3=g.total or 0)


async def _geracao_interna(serv: Servico, s: SessaoEstado, pasta: Path, args: tuple) -> None:
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


def argumentos_de_geracao(pasta: Path, s: SessaoEstado, campos: Campos, tr: core.Trabalho, qr: tuple | None) -> tuple:
    """Os argumentos de `trabalhos.gerar` (partilhado com a API publica em lote)."""
    return (str(pasta), s.tpl_nome, s.alg_nome, tr.nome, tr.inicio, tr.fim, tr.por_ficheiro, tr.digitos, campos.papel, campos.margem,
            campos.porfolha, tr.prefixos, tr.saltar, tr.cor_por_serie, campos.marcas == "1", campos.logo_posicao, campos.logo_tamanho,
            tr.cor_numeros, qr)


@router.post("/{id_}/gerar", response_model=Sessao, status_code=202, dependencies=[Depends(pesado)])
async def gerar(id_: str, campos: Campos, request: Request, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    tr = _validar(s, campos, lg, pasta, geracao=True)
    qr = _qr_dos_campos(campos, request, lg)
    if not serv.motor.reservar(s.id):                        # so uma geracao de cada vez em todo o servidor
        raise _ocupado(lg)
    try:
        saida_dir = pasta / "saida"
        if saida_dir.is_dir():
            shutil.rmtree(saida_dir, ignore_errors=True)     # nao se misturam PDFs de geracoes diferentes
        for f in (PROGRESSO, CANCELAR):
            (pasta / f).unlink(missing_ok=True)
        s.gerar = Geracao(estado="a_gerar", nome=tr.nome)
        s.tarefa = asyncio.create_task(_geracao(serv, s, pasta, argumentos_de_geracao(pasta, s, campos, tr, qr)))
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


def pedir_cancelamento(serv: Servico, s: SessaoEstado, pasta: Path) -> None:
    """Pede ao motor que pare a geracao da sessao (e mata-o passado `CANCELAR_ESPERA_S` se nao parar). Nao faz nada se nao ha geracao a correr."""
    if s.gerar.estado == "a_gerar":
        (pasta / CANCELAR).touch()                           # o motor consulta-a a cada pagina (trabalhos.Bandeira)
        s.gerar.estado = "a_cancelar"
        tarefa = asyncio.create_task(_cancelar_a_forca(serv, s))
        _TAREFAS.add(tarefa)                                 # sem uma referencia o asyncio pode descartar a tarefa a meio
        tarefa.add_done_callback(_TAREFAS.discard)


@router.post("/{id_}/cancelar", response_model=TrabalhoEstado, dependencies=[Depends(leve)])
async def cancelar(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> TrabalhoEstado:
    s, pasta = _sessao(serv, id_)
    pedir_cancelamento(serv, s, pasta)
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
    serv.metricas.evento("descarga", e.tipo, v2=len(e.ficheiros))
    cabecalhos = {"Content-Disposition": _cabecalho_download(e.nome), "Cache-Control": "no-store"}
    if e.tipo == "pdf":
        cabecalhos["Content-Length"] = str(e.ficheiros[0].stat().st_size)
    return StreamingResponse(saida.conteudo_da_entrega(e), media_type=e.media_type, headers=cabecalhos)


# ------------------------------------------------------------------ o tipo de ecra (so para as metricas: nunca muda nada)
router_ecra = APIRouter(prefix="/api/ecra", tags=["metricas"])


@router_ecra.post("", status_code=204, dependencies=[Depends(leve)])
def registar_ecra(e: Ecra, request: Request, serv: Servico = Depends(servico)) -> Response:
    """O browser diz, uma vez por separador, o tamanho do ecra e da janela e o modelo (se o souber). Guardam-se so a classe, o
    tamanho do ecra, a familia/modelo do dispositivo e a largura da janela: sem IP, sem User-Agent. Os robos nao contam."""
    ua = request.headers.get("user-agent", "")
    if dispositivo(ua) != "robo":
        classe = classe_do_ecra(e.ecra_l, e.ecra_a, e.toque)
        # a notacao do ecra: tamanho em px CSS e a densidade (os telemoveis recentes sao 2x ou 3x)
        dens = f"{round(e.dpr * 4) / 4:g}x"
        modelo = modelo_limpo(e.modelo)
        serv.metricas.evento("ecra", classe, f"{e.ecra_l}×{e.ecra_a} @{dens}", modelo or familia(ua, e.toque, e.ecra_l),
                             v1=e.janela_l, v2=e.janela_a, v3=1 if e.toque else 0)
    return Response(status_code=204)
