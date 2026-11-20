"""O gerador de preçários na webapp (`docs/PLANO_PRECARIO.md`, fase 5): o catálogo, a pré-visualização em PNG e o descarregar (PDF e imagem). **Sem sessão**: tudo sai do corpo do pedido,
como a folha de controlo (`rotas_listas.py`); os textos, os artigos e os preços só entram no ficheiro que se desenha e nunca se guardam. A pré-visualização desenha-se no processo do motor
(o PDFium só vive lá); o PDF faz-se no próprio servidor (só o reportlab). Métricas só agregadas: o desenho, o formato, o tamanho da lista e a moeda (nunca o texto nem os preços).
"""
from __future__ import annotations

import asyncio
import json
import urllib.parse
from concurrent.futures.process import BrokenProcessPool
from typing import Annotated

from core import ErroRifas, i18n, moeda, precario, precario_catalogo
from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field, StringConstraints

from . import partilhas, trabalhos
from .modelos import ErroApi
from .rotas import Ocupado, _levantar, _motivo, _ocupado, leve, lingua, pesado, servico, Servico

router = APIRouter(prefix="/api/precario", tags=["precario"])


class LinhaEntrada(BaseModel):
    artigo: str = Field("", max_length=40)
    nome: str = Field("", max_length=precario.MAX_NOME)
    preco: str = Field("", max_length=24)                    # o que a pessoa escreveu: lê-se na língua do pedido («1,5», «1.50»)
    preco2: str = Field("", max_length=24)                   # o segundo preço (só com `tamanhos`)
    categoria: str = Field("", max_length=20)
    emoji: str = Field("", max_length=8)


class MoedaEntrada(BaseModel):
    codigo: str = Field("", max_length=3)                    # «EUR»; vazio = a do país da língua
    nome: str = Field("", max_length=moeda.MAX_NOME_INVENTADA)   # com nome = moeda inventada («fichas»)
    antes: bool = False
    decimais: int = Field(0, ge=0, le=2)


class PedidoPrecario(BaseModel):
    linhas: list[LinhaEntrada] = Field(default_factory=list, max_length=precario.MAX_LINHAS)
    titulo: str = Field("", max_length=precario.MAX_TITULO)
    subtitulo: str = Field("", max_length=precario.MAX_SUBTITULO)
    rodape: str = Field("", max_length=precario.MAX_RODAPE)
    desenho: str = Field("quermesse", max_length=20)
    formato: str = Field("A4", max_length=4)
    orientacao: str = Field("vertical", max_length=12)
    colunas: int = Field(0, ge=0, le=3)
    imagens: bool = True
    tamanhos: bool = False
    rotulos: list[Annotated[str, StringConstraints(max_length=32)]] = Field(default_factory=lambda: ["P", "G"], min_length=2, max_length=2)
    moeda: MoedaEntrada = Field(default_factory=MoedaEntrada)


def _classe_de_linhas(n: int) -> str:
    return "1-5" if n <= 5 else "6-15" if n <= 15 else "16-40" if n <= 40 else "41+"


def _evento(serv: Servico, p: PedidoPrecario) -> None:
    serv.metricas.evento("precario", p.desenho, p.formato, _classe_de_linhas(len(p.linhas)))
    serv.metricas.evento("precario_moeda", "inventada" if p.moeda.nome.strip() else (p.moeda.codigo.upper() or "pais"))


def _anexo(dados: bytes, tipo: str, nome: str) -> Response:
    return Response(dados, media_type=tipo, headers={"Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(nome)}",
                                                      "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/catalogo")
def catalogo(resposta: Response, mes: int | None = Query(None, ge=1, le=12), lg: str = Depends(lingua)) -> dict:
    """O catálogo na língua do pedido (categorias com artigos e imagens, ocasiões, a sugerida para `mes`), os desenhos, as moedas e o país de omissão. Muda só com a língua: cache curta."""
    resposta.headers["Cache-Control"] = "public, max-age=300"
    resposta.headers["Vary"] = "X-Lingua, Accept-Language"
    pais = moeda.pais_por_omissao(lg)
    return {
        **precario_catalogo.catalogo(lg, mes),
        "desenhos": [{"id": d.id, "nome": d.nome} for d in precario.DESENHOS],
        "moedas": [{"codigo": m.codigo, "simbolo": m.simbolo, "decimais": m.decimais} for m in moeda.MOEDAS.values()],
        "paises": moeda.PAIS_MOEDA,
        "pais": pais, "moeda": moeda.moeda_por_omissao(lg).codigo,
        "limites": {"linhas": precario.MAX_LINHAS, "titulo": precario.MAX_TITULO, "subtitulo": precario.MAX_SUBTITULO, "rodape": precario.MAX_RODAPE, "nome": precario.MAX_NOME,
                    "moeda_inventada": moeda.MAX_NOME_INVENTADA},
        "formatos": list(precario.FORMATOS),
    }


async def _png(pedido: PedidoPrecario, serv: Servico, lg: str, dpi: int) -> bytes:
    try:
        r = await serv.motor.curto(trabalhos.precario_png, pedido.model_dump(), lg, dpi)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if r[0] != "ok":
        _levantar(r, lg)
    return r[1]


@router.post("/previa.png", dependencies=[Depends(leve)])
async def previa(pedido: PedidoPrecario, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Response:
    """O PNG do preçário (a 1.ª página) para a pré-visualização: desenha-se, não se guarda nada."""
    return Response(await _png(pedido, serv, lg, 110), media_type="image/png", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.post("/imagem.png", dependencies=[Depends(pesado)])
async def imagem(pedido: PedidoPrecario, dpi: int = Query(150, ge=72, le=200), serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Response:
    """O PNG do preçário (1.ª página, para partilhar no WhatsApp ou nas redes), descarregado."""
    dados = await _png(pedido, serv, lg, dpi)
    _evento(serv, pedido)
    return _anexo(dados, "image/png", "precario.png")


def _criar_pdf(d: dict, lg: str) -> bytes:
    with i18n.com_lingua(lg):
        return precario.criar_pdf(precario.de_dict(d, lg))


@router.post("/pdf", dependencies=[Depends(pesado)])
async def pdf(pedido: PedidoPrecario, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Response:
    """O PDF do preçário (1 a 5 páginas, pronto a imprimir), descarregado."""
    try:
        dados = await asyncio.to_thread(_criar_pdf, pedido.model_dump(), lg)
    except ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None
    _evento(serv, pedido)
    return _anexo(dados, "application/pdf", "precario.pdf")


# ------------------------------------------------------------------ partilhar por ligação (`/precario?p=<id>`), com o mesmo armazenamento do editor (`partilhas.py`: só com DATABASE_URL)
class Partilhado(BaseModel):
    id: str


class PrecarioPartilhado(BaseModel):
    precario: dict                              # o formato de `core.precario.para_dict` (preços em milésimos: não dependem da língua de quem abre)


@router.post("/partilhar", response_model=Partilhado, dependencies=[Depends(pesado)])
async def partilhar(pedido: PedidoPrecario, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Partilhado:
    """Guarda o preçário (só os campos: textos, artigos, preços e aspeto) e devolve o id da ligação. Só existe com `DATABASE_URL`; 90 dias depois do último acesso apaga-se."""
    if serv.partilhas is None:
        raise ErroApi(404, "Partilha indisponível", "erro")
    try:
        with i18n.com_lingua(lg):
            p = precario.de_dict(pedido.model_dump(), lg)
            precario.validar(p)                                # só se guarda o que o gerador aceita
    except ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None
    dados = json.dumps(precario.para_dict(p), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    try:
        id_ = await asyncio.to_thread(serv.partilhas.guardar, dados)
    except ValueError:
        raise ErroApi(413, i18n.traduzir("err_precario_linhas", lg, max=precario.MAX_LINHAS), "aviso") from None
    except Exception as e:  # noqa: BLE001 - a base de dados em baixo nao derruba o servidor
        raise ErroApi(503, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    serv.metricas.evento("precario_partilha", "criar")
    return Partilhado(id=id_)


@router.get("/partilha/{id_}", response_model=PrecarioPartilhado, dependencies=[Depends(leve)])
async def ver_partilha(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> PrecarioPartilhado:
    """O preçário partilhado (validado outra vez). 404 se o id não existe, o prazo acabou ou a partilha é de outra coisa (um desenho do editor)."""
    invalido = ErroApi(404, i18n.traduzir("web_precario_ligacao_invalida", lg), "aviso")
    if serv.partilhas is None or not partilhas.ID.fullmatch(id_):
        raise invalido
    try:
        dados = await asyncio.to_thread(serv.partilhas.obter, id_)
    except Exception as e:  # noqa: BLE001
        raise ErroApi(503, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if dados is None:
        raise invalido
    try:
        d = json.loads(dados)
        with i18n.com_lingua(lg):
            precario.validar(precario.de_dict(d, lg))
    except (ValueError, ErroRifas):
        raise invalido from None
    return PrecarioPartilhado(precario=d)
