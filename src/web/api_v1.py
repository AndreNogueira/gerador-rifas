"""A API pública v1 (`/api/v1`, Swagger em `/api/v1/docs`): gerar **vários pedidos de rifas de uma vez** (lote) a partir de um só template.

Para quem quer automatizar (uma associação com vários eventos, uma gráfica, um sistema de bilheteira): em vez de usar o site, pede-se um lote com N itens
(cada um com o seu nome, intervalo, prefixos...), carrega-se o template e os algarismos **uma vez**, arranca-se e descarrega-se um ZIP com tudo.

 - **Chave** no cabeçalho `X-API-Key` (`chaves_api.py`: criam-se no painel de administração; guarda-se só o SHA-256). Sem chave válida: 401.
 - **Limites**: pedidos por minuto por chave, quota de **números por dia** por chave, itens e números por lote, lotes ativos por chave e os mesmos tetos do
   site por item (`MAX_NUMEROS`, `JOB_MAX_MIN`). **Uma só geração de cada vez no servidor**: os itens de um lote esperam a sua vez atrás de quem usa o site.
 - **Por baixo é o mesmo motor e a mesma sessão em disco** do site (`rotas.py`): um lote é uma sessão com N pedidos em fila. Ficheiros e resultados
   desaparecem ao fim de `JOB_TTL_MIN` min sem acessos ou com `DELETE`. Nada do conteúdo (template, números, nomes) vai para logs ou métricas.
 - Os nomes e as descrições da API são em inglês (contrato público); as mensagens das regras do motor saem na língua do `X-Lingua`/`Accept-Language`.
"""
from __future__ import annotations

import asyncio
import secrets
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Literal

import core
from core import entradas, i18n, saida
from fastapi import Depends, FastAPI, Request, Response, Security
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from . import VERSAO, config, rotas
from .chaves_api import InfoChave
from .limites import ler_corpo
from .modelos import Campos, ErroApi
from .sessoes import _ficheiros, ler_progresso, texto_de_erro, trabalho_dos_campos
from .trabalhos import CANCELAR, PROGRESSO

DESCRICAO = """
Generate **several raffle-ticket jobs at once** from a single template (a *batch*).

1. `POST /batches` with the list of jobs (name, number range, prefixes...).
2. `PUT /batches/{id}/template` (the PDF from Canva) and `PUT /batches/{id}/digits` (the digits image/PDF) — once for the whole batch.
3. `POST /batches/{id}/start`, then poll `GET /batches/{id}` until `state` is `done`.
4. `GET /batches/{id}/download` (a ZIP with every PDF) or `GET /batches/{id}/items/{n}/download`.
5. `DELETE /batches/{id}` when you are done (otherwise everything is deleted after 30 minutes without activity).

Authenticate with the `X-API-Key` header. Keys are issued by the service owner. Limits (per key): requests per minute, numbers per day,
items and numbers per batch, active batches. The server generates **one job at a time**: your items wait their turn behind the website's users
(`queued` state). Messages about the template or the numbers are returned in the language of the `X-Lingua` (or `Accept-Language`) header.
"""

_cabecalho_chave = APIKeyHeader(name="X-API-Key", auto_error=False, description="API key issued by the service owner (`rk_...`).")


# ====================================================================== modelos (contrato publico, em ingles)
class Item(BaseModel):
    """One job of the batch: one range of numbers, written on the template."""
    name: str = Field(min_length=1, max_length=200, description="Base name of the PDF files (and of the ZIP).")
    first: int = Field(1, ge=0, le=999_999_999, description="First number.")
    last: int = Field(ge=0, le=999_999_999, description="Last number (inclusive).")
    digits: int = Field(4, ge=1, le=12, description="Digits of each number (zero-padded): 4 -> 0001.")
    per_file: int | None = Field(None, ge=1, le=1_000_000, description="Numbers per PDF file. Omit for a single PDF.")
    prefixes: list[str] = Field(default_factory=list, max_length=10, description='Series prefixes, e.g. `["A-", "B-"]` (letters, `.`, `-`, `/` only).')
    skip: str = Field("", max_length=300, description='Numbers that are never printed, e.g. `"13, 100-110"`.')
    color_per_series: bool = Field(False, description="One colour for each series.")
    number_color: str = Field("", pattern=r"^(#[0-9a-fA-F]{6})?$", description="Colour of the numbers as `#RRGGBB` (empty = the template's own).")
    paper: str = Field("A4", max_length=20, description="Paper for templates with a single ticket (e.g. A4, A3, Letter).")
    margin_mm: float = Field(5, ge=0, le=100, description="Sheet margin in mm (single-ticket templates).")
    per_sheet: int | None = Field(None, ge=1, le=200, description="Tickets per sheet (default: as many as fit).")
    cut_marks: bool = Field(False, description="Cut marks in the sheet margins (single-ticket templates).")


class BatchIn(BaseModel):
    items: list[Item] = Field(min_length=1, max_length=100, description="The jobs. The server limits how many (default 20).")


class FileState(BaseModel):
    state: Literal["missing", "ok", "error"]
    message: str = ""


class ItemOut(BaseModel):
    index: int
    name: str
    state: Literal["pending", "queued", "running", "done", "errors", "failed", "cancelled"] = Field(
        description="`errors`: finished but some PDFs failed verification. `failed`: nothing was produced (see `error`).")
    numbers: int
    done: int = 0
    total: int = 0
    files: list[str] = []
    error: str = ""
    download_url: str = ""


class BatchOut(BaseModel):
    id: str
    state: Literal["waiting_files", "ready", "running", "cancelling", "done", "done_with_errors", "failed", "cancelled"]
    template: FileState
    digits: FileState
    items: list[ItemOut]
    download_url: str = ""
    numbers_total: int


class Usage(BaseModel):
    key_id: str
    name: str
    daily_quota_numbers: int
    used_today_numbers: int
    remaining_today_numbers: int
    active_batches: int


# ====================================================================== estado em memoria dos lotes
@dataclass
class ItemEstado:
    item: Item
    campos: Campos
    numeros: int = 0
    estado: str = "pending"
    args: tuple | None = None
    entrega: saida.Entrega | None = None
    erro: tuple | None = None
    feitas: int = 0
    total: int = 0


@dataclass
class Lote:
    id: str
    chave: str
    sessao: str
    itens: list[ItemEstado]
    fase: str = "preparing"                          # preparing | running | finished
    cancelar: bool = False
    consumido: int = 0
    tarefa: asyncio.Task | None = None
    criado: float = field(default_factory=time.time)


class Lotes:
    def __init__(self):
        self._todos: dict = {}

    def limpar(self, serv: rotas.Servico) -> None:
        """Esquece os lotes cuja sessao ja foi apagada (inatividade, reinicio do servidor)."""
        for i in [i for i, l in self._todos.items() if serv.sessoes.obter(l.sessao) is None]:
            del self._todos[i]

    def ativos_da_chave(self, chave: str) -> int:
        return sum(1 for l in self._todos.values() if l.chave == chave)

    def criar(self, lote: Lote) -> None:
        self._todos[lote.id] = lote

    def obter(self, id_: str, chave: str) -> Lote | None:
        l = self._todos.get(id_)
        return l if l is not None and l.chave == chave else None       # o lote de outra chave nao existe

    def remover(self, id_: str) -> None:
        self._todos.pop(id_, None)


# ====================================================================== dependencias
def servico(request: Request) -> rotas.Servico:
    return request.app.state.servico


def lotes(request: Request) -> Lotes:
    return request.app.state.lotes


def lingua(request: Request) -> str:
    return rotas.lingua(request)


def chave_atual(request: Request, valor: str | None = Security(_cabecalho_chave), serv: rotas.Servico = Depends(servico)) -> InfoChave:
    """Autentica o pedido. Chave em falta/invalida: 401 (e, depois de 20 falhas por minuto do mesmo IP, 429)."""
    info = serv.chaves.autenticar(valor.strip()) if valor else None
    if info is None:
        serv.metricas.evento("api_v1", "sem_chave")
        if not serv.limitador.permitir(rotas._ip(request), "v1-falha", 20):
            raise ErroApi(429, "Too many failed attempts: wait a minute.", "aviso")
        raise ErroApi(401, "Missing or invalid API key (header X-API-Key).", "erro")
    if not serv.limitador.permitir(info.id, "v1", config.api_pedidos_por_min()):
        serv.metricas.evento("api_v1", "limite_pedidos")
        raise ErroApi(429, f"Too many requests: at most {config.api_pedidos_por_min()} per minute per key.", "aviso")
    return info


def _lote(id_: str, info: InfoChave, serv: rotas.Servico, todos: Lotes) -> tuple:
    """(Lote, SessaoEstado, pasta) ou 404 (id desconhecido, de outra chave, ou ja expirado)."""
    lote = todos.obter(id_, info.id)
    s = serv.sessoes.obter(lote.sessao) if lote is not None else None
    if lote is None or s is None:
        if lote is not None:
            todos.remover(id_)
        raise ErroApi(404, "Batch not found (it may have expired).", "erro")
    return lote, s, serv.sessoes.pasta(s)


# ====================================================================== conversao e vista
def _campos(it: Item) -> Campos:
    return Campos(nome=it.name, inicio=str(it.first), fim=str(it.last), digitos=str(it.digits), modo="varios" if it.per_file else "unico",
                  max_ficheiro=str(it.per_file or 300), papel=it.paper, margem=f"{it.margin_mm:g}", porfolha=str(it.per_sheet or ""),
                  prefixos=", ".join(it.prefixes), saltar=it.skip, cor_serie="1" if it.color_per_series else "", marcas="1" if it.cut_marks else "",
                  cor_numeros=it.number_color)


def _contar(it: ItemEstado, lg: str, indice: int) -> int:
    """Quantos numeros tem o item (valida os campos: nome, intervalo, prefixos, saltos) ou 422 «[indice] mensagem»."""
    try:
        with i18n.com_lingua(lg):
            tr = trabalho_dos_campos(it.campos)
            if not tr.nome:
                raise core.ErroRifas("err_nome")
            if not 1 <= tr.digitos <= core.MAX_DIGITOS or tr.fim < tr.inicio:
                raise core.ErroRifas("conf_numeros")
            n = core.series.contar(tr)
            if n > config.max_numeros():
                raise core.ErroRifas("web_demasiados", max=config.max_numeros())
            return n
    except core.ErroRifas as e:
        raise ErroApi(422, f"[items/{indice}] {e.em(lg)}", "aviso") from None


def _estado_ficheiro(f) -> FileState:
    return FileState(state={"ok": "ok", "erro": "error"}.get(f.estado, "missing"), message=(f.detalhe or f.texto) if f.estado == "erro" else "")


def _vista(lote: Lote, s, pasta: Path, lg: str) -> BatchOut:
    tpl, alg, _ = _ficheiros(s, lg)
    itens = []
    for i, it in enumerate(lote.itens):
        feitas, total, ficheiros, erro = it.feitas, it.total, [], ""
        if it.estado == "running":
            ler_progresso(s.gerar, pasta)
            feitas, total = s.gerar.feitas, s.gerar.total
        if it.entrega is not None:
            ficheiros = [f.name for f in it.entrega.ficheiros]
        if it.estado == "failed" and it.erro is not None:
            erro = texto_de_erro(it.erro, lg)
        itens.append(ItemOut(index=i, name=it.item.name, state=it.estado, numbers=it.numeros, done=feitas, total=total, files=ficheiros, error=erro,
                             download_url=f"/api/v1/batches/{lote.id}/items/{i}/download" if it.entrega is not None else ""))
    pronto = s.analise is not None and s.analise[0] == "ok"
    if lote.fase == "preparing":
        estado = "ready" if pronto else "waiting_files"
    elif lote.fase == "running":
        estado = "cancelling" if lote.cancelar else "running"
    else:
        estados = {it.estado for it in lote.itens}
        estado = "cancelled" if lote.cancelar else "done" if estados == {"done"} else "failed" if estados == {"failed"} else "done_with_errors"
    tem_resultado = any(it.entrega is not None for it in lote.itens)
    return BatchOut(id=lote.id, state=estado, template=_estado_ficheiro(tpl), digits=_estado_ficheiro(alg), items=itens,
                    download_url=f"/api/v1/batches/{lote.id}/download" if tem_resultado and lote.fase == "finished" else "",
                    numbers_total=sum(it.numeros for it in lote.itens))


# ====================================================================== a execucao do lote
async def _correr_item(serv: rotas.Servico, lote: Lote, s, pasta: Path, i: int, it: ItemEstado) -> None:
    it.estado = "queued"
    limite = time.monotonic() + config.api_espera_motor_min() * 60
    while not serv.motor.reservar(s.id):                           # a vez do motor: quem usa o site passa primeiro (nao se fura a fila)
        if lote.cancelar:
            it.estado = "cancelled"
            return
        if time.monotonic() > limite:
            it.estado, it.erro = "failed", ("exc", "the server stayed busy for too long: try again later")
            return
        serv.sessoes.obter(s.id)                                   # mantem a sessao viva enquanto espera
        await asyncio.sleep(2)
    saida_dir = pasta / "saida"
    if saida_dir.is_dir():
        shutil.rmtree(saida_dir, ignore_errors=True)
    for f in (PROGRESSO, CANCELAR):
        (pasta / f).unlink(missing_ok=True)
    s.gerar = rotas.Geracao(estado="a_gerar", nome=it.item.name)
    it.estado = "running"
    t0 = time.perf_counter()
    await rotas._geracao_interna(serv, s, pasta, it.args)         # liberta a vez do motor no fim (Motor.gerar)
    g = s.gerar
    it.feitas, it.total = g.feitas, g.total
    if g.estado in ("ok", "erros") and (pasta / "saida").is_dir():
        destino = pasta / "itens" / f"{i:02d}"
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pasta / "saida"), str(destino))
        bons = [SimpleNamespace(caminho=destino / r.caminho.name, ok=True) for r in g.resultados if r.ok]
        try:
            it.entrega = saida.entrega(bons, it.item.name)
            it.estado = "done" if g.estado == "ok" else "errors"
        except ValueError:
            it.estado, it.erro = "failed", ("exc", "no PDF passed verification")
    elif g.estado == "cancelado":
        it.estado = "cancelled"
    else:
        it.estado, it.erro = "failed", g.erro or ("exc", "unknown error")
    serv.metricas.evento("api_geracao", it.estado, v1=time.perf_counter() - t0, v2=it.numeros)


async def _correr_lote(serv: rotas.Servico, lote: Lote, s, pasta: Path) -> None:
    try:
        for i, it in enumerate(lote.itens):
            if lote.cancelar:
                it.estado = "cancelled"
                continue
            await _correr_item(serv, lote, s, pasta, i, it)
            await asyncio.sleep(1)                                 # um intervalo para o site passar a frente entre dois itens
    except asyncio.CancelledError:
        raise
    except Exception:  # noqa: BLE001 - um item nunca derruba o servidor; os que faltam ficam por fazer
        for it in lote.itens:
            if it.estado in ("pending", "queued", "running"):
                it.estado, it.erro = "failed", ("exc", "internal error")
    finally:
        for it in lote.itens:
            if it.estado in ("pending", "queued", "running"):
                it.estado = "cancelled"
        lote.fase = "finished"


# ====================================================================== a aplicacao
def criar_api_v1(serv: rotas.Servico) -> FastAPI:
    api = FastAPI(title="Gerador de Rifas — public API", version=VERSAO, description=DESCRICAO, docs_url="/docs", redoc_url=None, openapi_url="/openapi.json")
    api.state.servico = serv
    api.state.lotes = Lotes()

    @api.exception_handler(ErroApi)
    async def _erro_api(_: Request, e: ErroApi) -> JSONResponse:
        serv.metricas.evento("erro_http", str(e.estado), e.tipo)
        return JSONResponse({"detail": e.texto, "tipo": e.tipo}, status_code=e.estado)

    seguro = [Depends(chave_atual)]

    @api.post("/batches", response_model=BatchOut, status_code=201, dependencies=seguro, tags=["batches"], summary="Create a batch")
    def criar(corpo: BatchIn, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes), lg: str = Depends(lingua)) -> BatchOut:
        """Declares the jobs. Nothing is generated yet: upload the template and the digits, then start."""
        if len(corpo.items) > config.max_itens_lote():
            raise ErroApi(422, f"At most {config.max_itens_lote()} items per batch.", "aviso")
        todos.limpar(serv)
        if todos.ativos_da_chave(info.id) >= config.api_lotes_ativos():
            raise ErroApi(429, f"At most {config.api_lotes_ativos()} active batches per key: delete one first.", "aviso")
        itens = [ItemEstado(item=x, campos=_campos(x)) for x in corpo.items]
        for i, it in enumerate(itens):
            it.numeros = _contar(it, lg, i)
        if sum(it.numeros for it in itens) > config.max_numeros_lote():
            raise ErroApi(422, f"At most {config.max_numeros_lote()} numbers per batch.", "aviso")
        s = serv.sessoes.criar()
        if s is None:
            raise rotas._ocupado(lg)
        lote = Lote(id=secrets.token_urlsafe(12), chave=info.id, sessao=s.id, itens=itens)
        todos.criar(lote)
        serv.metricas.evento("api_v1", "lote_criado", v2=len(itens))
        return _vista(lote, s, serv.sessoes.pasta(s), lg)

    @api.get("/batches/{id_}", response_model=BatchOut, tags=["batches"], summary="Batch status and progress")
    def ver(id_: str, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes), lg: str = Depends(lingua)) -> BatchOut:
        lote, s, pasta = _lote(id_, info, serv, todos)
        return _vista(lote, s, pasta, lg)

    async def _carregar(id_: str, request: Request, info: InfoChave, todos: Lotes, lg: str, template: bool) -> BatchOut:
        lote, s, pasta = _lote(id_, info, serv, todos)
        if lote.fase != "preparing":
            raise ErroApi(409, "The batch already started.", "aviso")
        limite = config.limite_upload_mb() * 1024 * 1024
        dados = await ler_corpo(request, limite, i18n.traduzir("web_demasiado_grande", lg, mb=config.limite_upload_mb()))
        tipo = entradas.detetar_tipo(dados)
        if template:
            if tipo != "pdf":
                raise ErroApi(422, i18n.traduzir("err_abrir_template", lg, erro="«template»"), "aviso")
            (pasta / "template.pdf").unlink(missing_ok=True)
            rotas._guardar(serv, s, "template.pdf", dados, lg)
            s.tpl_nome = "template.pdf"
        else:
            if tipo is None:
                raise ErroApi(422, i18n.traduzir("err_formato", lg), "aviso")
            for antigo in serv.sessoes.armazem.listar(s.id):
                if antigo.startswith("algarismos."):
                    (pasta / antigo).unlink(missing_ok=True)
            rotas._guardar(serv, s, f"algarismos.{tipo}", dados, lg)
            s.alg_nome = "digits"
        if (pasta / "template.pdf").is_file():
            await rotas._analisar(s, serv, pasta, lg)
        serv.metricas.evento("api_v1", "template" if template else "algarismos", v2=len(dados) / 1024)
        return _vista(lote, s, pasta, lg)

    @api.put("/batches/{id_}/template", response_model=BatchOut, dependencies=seguro, tags=["batches"], summary="Upload the template PDF (raw body)")
    async def carregar_template(id_: str, request: Request, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes), lg: str = Depends(lingua)) -> BatchOut:
        """The raw PDF as the request body (`Content-Type: application/pdf`). The type is checked from the bytes."""
        return await _carregar(id_, request, info, todos, lg, True)

    @api.put("/batches/{id_}/digits", response_model=BatchOut, dependencies=seguro, tags=["batches"], summary="Upload the digits image (raw body)")
    async def carregar_algarismos(id_: str, request: Request, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes), lg: str = Depends(lingua)) -> BatchOut:
        """The image (PNG/JPG) or PDF with the digits 0-9, as the raw request body."""
        return await _carregar(id_, request, info, todos, lg, False)

    @api.post("/batches/{id_}/start", response_model=BatchOut, status_code=202, tags=["batches"], summary="Start generating")
    async def arrancar(id_: str, request: Request, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes), lg: str = Depends(lingua)) -> BatchOut:
        """Validates every item against the template, spends the daily quota and queues the batch. Poll `GET /batches/{id}`."""
        lote, s, pasta = _lote(id_, info, serv, todos)
        if lote.fase != "preparing":
            raise ErroApi(409, "The batch already started.", "aviso")
        if s.analise is None or s.analise[0] != "ok":
            raise ErroApi(409, i18n.traduzir("c1_vazio" if s.analise is None else "c2_precisa", lg), "aviso")
        for i, it in enumerate(lote.itens):
            try:
                tr = rotas._validar(s, it.campos, lg, pasta, geracao=True)
            except ErroApi as e:
                raise ErroApi(e.estado, f"[items/{i}] {e.texto}", e.tipo) from None
            it.args = rotas.argumentos_de_geracao(pasta, s, it.campos, tr, None)
        total = sum(it.numeros for it in lote.itens)
        if not serv.chaves.consumir(info, total):
            usados, _ = serv.chaves.uso_hoje(info)
            serv.metricas.evento("api_v1", "quota")
            raise ErroApi(429, f"Daily quota exceeded: {usados} of {info.quota} numbers used today, this batch needs {total}.", "aviso")
        lote.consumido, lote.fase = total, "running"
        lote.tarefa = s.tarefa = asyncio.create_task(_correr_lote(serv, lote, s, pasta))
        serv.metricas.evento("api_v1", "lote_arrancado", v2=total)
        return _vista(lote, s, pasta, lg)

    @api.post("/batches/{id_}/cancel", response_model=BatchOut, tags=["batches"], summary="Cancel the batch")
    async def cancelar(id_: str, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes), lg: str = Depends(lingua)) -> BatchOut:
        """Stops the running item and skips the rest. What was already generated stays available until you delete the batch."""
        lote, s, pasta = _lote(id_, info, serv, todos)
        if lote.fase == "running":
            lote.cancelar = True
            rotas.pedir_cancelamento(serv, s, pasta)
        return _vista(lote, s, pasta, lg)

    @api.delete("/batches/{id_}", status_code=204, tags=["batches"], summary="Delete the batch and its files")
    def apagar(id_: str, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes)) -> Response:
        lote = todos.obter(id_, info.id)
        if lote is not None:
            s = serv.sessoes.obter(lote.sessao)
            if s is not None and s.a_correr and serv.motor.geracao == s.id:
                serv.motor.reiniciar()                              # o processo esta a gerar para este lote: matar e recriar
            lote.cancelar = True
            serv.sessoes.apagar(lote.sessao)
            todos.remover(id_)
        return Response(status_code=204)

    def _transferir(e: saida.Entrega, nome: str | None = None) -> StreamingResponse:
        cab = {"Content-Disposition": rotas._cabecalho_download(nome or e.nome), "Cache-Control": "no-store"}
        if e.tipo == "pdf":
            cab["Content-Length"] = str(e.ficheiros[0].stat().st_size)
        return StreamingResponse(saida.conteudo_da_entrega(e), media_type=e.media_type, headers=cab)

    @api.get("/batches/{id_}/items/{n}/download", tags=["batches"], summary="Download one item (PDF, or ZIP if it has several files)",
             responses={200: {"content": {"application/pdf": {}, "application/zip": {}}}})
    def descarregar_item(id_: str, n: int, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes)) -> StreamingResponse:
        lote, _, _ = _lote(id_, info, serv, todos)
        if not 0 <= n < len(lote.itens) or lote.itens[n].entrega is None:
            raise ErroApi(404, "Nothing to download for this item.", "erro")
        serv.metricas.evento("api_v1", "descarga_item")
        return _transferir(lote.itens[n].entrega)

    @api.get("/batches/{id_}/download", tags=["batches"], summary="Download everything as one ZIP",
             responses={200: {"content": {"application/zip": {}}}})
    def descarregar_tudo(id_: str, info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes)) -> StreamingResponse:
        lote, _, _ = _lote(id_, info, serv, todos)
        ficheiros = [f for it in lote.itens if it.entrega is not None for f in it.entrega.ficheiros]
        if lote.fase != "finished" or not ficheiros:
            raise ErroApi(404, "Nothing to download yet.", "erro")
        serv.metricas.evento("api_v1", "descarga_lote", v2=len(ficheiros))
        return _transferir(saida.Entrega("zip", f"batch-{lote.id}.zip", saida.MEDIA_ZIP, ficheiros))

    @api.get("/usage", response_model=Usage, tags=["account"], summary="Quota and usage of the key")
    def uso(info: InfoChave = Depends(chave_atual), todos: Lotes = Depends(lotes)) -> Usage:
        usados, _ = serv.chaves.uso_hoje(info)
        return Usage(key_id=info.id, name=info.nome, daily_quota_numbers=info.quota, used_today_numbers=usados,
                     remaining_today_numbers=max(0, info.quota - usados), active_batches=todos.ativos_da_chave(info.id))

    return api
