"""M4: a galeria de templates. Uma pre-visualizacao em PNG (desenhada no processo do motor: o PDFium so la) e «usar este template»,
que cria o template e os algarismos da galeria na sessao e continua como se tivessem sido carregados.

Os textos que a pessoa escreve (titulo, organizacao, premios, data) so entram no PDF que se desenha; nao se guardam em mais lado nenhum.
"""
from __future__ import annotations

import asyncio
from concurrent.futures.process import BrokenProcessPool
from typing import Annotated

from core import ErroRifas, galeria, i18n
from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field, StringConstraints

from . import trabalhos
from .modelos import ErroApi, Sessao
from .rotas import (Geracao, Ocupado, _analisar, _guardar, _levantar, _limpar_previa, _motivo, _ocupado, _sessao, leve, lingua,
                    pesado, servico, Servico)
from .sessoes import vista

router = APIRouter(prefix="/api", tags=["galeria"])


class PedidoGaleria(BaseModel):
    desenho: str = Field(max_length=20)
    titulo: str = Field("", max_length=galeria.MAX_TITULO)
    organizacao: str = Field("", max_length=galeria.MAX_ORGANIZACAO)
    premios: list[str] = Field(default_factory=list, max_length=galeria.MAX_PREMIOS)
    data: str = Field("", max_length=galeria.MAX_DATA)

    def textos(self) -> galeria.Textos:
        return galeria.Textos(self.titulo, self.organizacao, tuple(p[:galeria.MAX_PREMIO] for p in self.premios), self.data)


@router.get("/galeria/previa.png", dependencies=[Depends(leve)])
async def previa(desenho: str = Query(max_length=20), t: str = Query("", max_length=galeria.MAX_TITULO),
                 o: str = Query("", max_length=galeria.MAX_ORGANIZACAO),
                 p: Annotated[list[Annotated[str, StringConstraints(max_length=galeria.MAX_PREMIO)]], Query(max_length=galeria.MAX_PREMIOS)] = [],  # noqa: B006
                 d: str = Query("", max_length=galeria.MAX_DATA), serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Response:
    """O PNG do desenho com estes textos (so se desenha, nada se guarda)."""
    try:
        r = await serv.motor.curto(trabalhos.galeria_png, desenho, t, o, tuple(p), d, 110)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if r[0] != "ok":
        _levantar(r, lg)
    return Response(r[1], media_type="image/png", headers={"Cache-Control": "private, max-age=120", "X-Content-Type-Options": "nosniff"})


@router.post("/sessoes/{id_}/galeria", response_model=Sessao, dependencies=[Depends(pesado)])
async def usar(id_: str, pedido: PedidoGaleria, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    """«Usar este template»: o template e os algarismos da galeria passam a ser os da sessao (como se tivessem sido carregados)."""
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    try:
        with i18n.com_lingua(lg):
            template = galeria.criar_template(pedido.desenho, pedido.textos())
            algarismos = galeria.criar_algarismos()
    except ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None
    for antigo in serv.sessoes.armazem.listar(s.id):
        if antigo.startswith("algarismos."):
            (pasta / antigo).unlink(missing_ok=True)
    _limpar_previa(s, pasta)
    s.gerar = Geracao()
    _guardar(serv, s, "template.pdf", template, lg)
    _guardar(serv, s, "algarismos.pdf", algarismos, lg)
    s.tpl_nome, s.alg_nome, s.alg_erro = f"galeria-{pedido.desenho}.pdf", f"galeria-{pedido.desenho}-algarismos.pdf", None
    await _analisar(s, serv, pasta, lg)
    serv.metricas.evento("galeria", pedido.desenho)
    return vista(s, lg, pasta)
