"""Fase 7 do preçário: os vales de fichas numerados. Uma pré-visualização em PNG (desenhada no processo do motor: o PDFium só lá) e «criar vales numerados»,
que cria o template do vale e os algarismos na sessão e continua como se tivessem sido carregados: a partir daí é o motor das rifas que numera (séries,
QR de verificação, folhas). Os textos só entram no PDF que se desenha; as métricas levam só o desenho e a quantidade (nunca títulos nem nomes).
"""
from __future__ import annotations

import asyncio
from concurrent.futures.process import BrokenProcessPool

from core import ErroRifas, i18n, vales
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field

from . import trabalhos
from .modelos import ErroApi, Sessao
from .rotas import (Geracao, Ocupado, Servico, _analisar, _guardar, _levantar, _limpar_previa, _motivo, _ocupado, _sessao, leve, lingua,
                    pesado, servico)
from .sessoes import vista

router = APIRouter(prefix="/api", tags=["vales"])


class PedidoVale(BaseModel):
    desenho: str = Field("arraial", max_length=20)
    titulo: str = Field("", max_length=vales.MAX_TITULO + 10)         # o limite a sério (e a mensagem) é o de `core.vales`
    organizacao: str = Field("", max_length=vales.MAX_ORGANIZACAO + 10)
    moeda: str = Field("", max_length=vales.MAX_MOEDA + 10)
    moeda_plural: str = Field("", max_length=vales.MAX_MOEDA + 10)
    quantidade: int = Field(1, ge=-1000, le=1000)
    nota: str = Field("", max_length=vales.MAX_NOTA + 10)

    def vale(self) -> dict:
        return self.model_dump()


@router.post("/vales/previa.png", dependencies=[Depends(leve)])
async def previa(pedido: PedidoVale, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Response:
    """O PNG do vale com estes textos (só se desenha, nada se guarda). Um vale que não presta dá um aviso traduzido em vez de uma imagem."""
    try:
        r = await serv.motor.curto(trabalhos.vale_png, pedido.vale(), lg, 110)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if r[0] != "ok":
        _levantar(r, lg)
    return Response(r[1], media_type="image/png", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.post("/sessoes/{id_}/vales", response_model=Sessao, dependencies=[Depends(pesado)])
async def usar(id_: str, pedido: PedidoVale, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    """«Criar vales numerados»: o template do vale e os algarismos passam a ser os da sessão (como se tivessem sido carregados)."""
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    try:
        with i18n.com_lingua(lg):
            vale = vales.de_dict(pedido.vale())
            template = vales.criar_template(vale)
            algarismos = vales.criar_algarismos()
    except ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None
    for antigo in serv.sessoes.armazem.listar(s.id):
        if antigo.startswith("algarismos."):
            (pasta / antigo).unlink(missing_ok=True)
    _limpar_previa(s, pasta)
    s.gerar = Geracao()
    _guardar(serv, s, "template.pdf", template, lg)
    _guardar(serv, s, "algarismos.pdf", algarismos, lg)
    s.tpl_nome, s.alg_nome, s.alg_erro = f"vales-{vale.desenho}.pdf", f"vales-{vale.desenho}-algarismos.pdf", None
    await _analisar(s, serv, pasta, lg)
    serv.metricas.evento("vales", vale.desenho, v1=float(vale.quantidade))
    return vista(s, lg, pasta)
