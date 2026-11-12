"""X1: o editor de templates. O desenho vem do browser em JSON (elementos com posição, cor e texto, ver `core/editor.py`); aqui só se valida,
se desenha uma pré-visualização em PNG (no processo do motor: o PDFium só lá) e «usar este template» cria o template e os algarismos na sessão,
como a galeria. Nada do que se desenha fica guardado fora do template da sessão; os eventos das métricas levam só códigos e números.
"""
from __future__ import annotations

import asyncio
from concurrent.futures.process import BrokenProcessPool

from core import ErroRifas, editor, galeria, i18n
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field

from . import trabalhos
from .modelos import ErroApi, Sessao
from .rotas import (Geracao, Ocupado, Servico, _analisar, _guardar, _levantar, _limpar_previa, _motivo, _ocupado, _sessao, leve, lingua,
                    pesado, servico)
from .sessoes import vista

router = APIRouter(prefix="/api", tags=["editor"])


class ElementoEditor(BaseModel):
    tipo: str = Field(max_length=10)
    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0
    cor: str = Field("", max_length=7)
    contorno: str = Field("", max_length=7)
    espessura: float = 1
    raio: float = 0
    tracejado: bool = False
    texto: str = Field("", max_length=editor.MAX_TEXTO + 20)     # o limite a sério (e a mensagem) é o de `core.editor`
    tamanho: float = 12
    negrito: bool = False
    alinhamento: str = Field("e", max_length=1)
    rot: int = 0


class PedidoEditor(BaseModel):
    largura: float = 535
    altura: float = 152
    fundo: str = Field("#ffffff", max_length=7)
    elementos: list[ElementoEditor] = Field(default_factory=list, max_length=editor.MAX_ELEMENTOS + 10)

    def desenho(self) -> dict:
        return self.model_dump(exclude_unset=True)       # so o que veio: os valores por omissao sao os de `core.editor` (varia com o tipo)


@router.post("/editor/previa.png", dependencies=[Depends(leve)])
async def previa(pedido: PedidoEditor, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Response:
    """O PNG do desenho (só se desenha, nada se guarda). Um desenho que não presta dá um aviso traduzido em vez de uma imagem."""
    try:
        r = await serv.motor.curto(trabalhos.editor_png, pedido.desenho(), 110)
    except Ocupado:
        raise _ocupado(lg) from None
    except (asyncio.TimeoutError, BrokenProcessPool) as e:
        raise ErroApi(500, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if r[0] != "ok":
        _levantar(r, lg)
    return Response(r[1], media_type="image/png", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.post("/sessoes/{id_}/editor", response_model=Sessao, dependencies=[Depends(pesado)])
async def usar(id_: str, pedido: PedidoEditor, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Sessao:
    """«Usar este template»: o desenho e os algarismos passam a ser os da sessão (como se tivessem sido carregados)."""
    s, pasta = _sessao(serv, id_)
    if s.a_correr:
        raise _ocupado(lg)
    try:
        with i18n.com_lingua(lg):
            template = editor.criar_template(editor.de_dict(pedido.desenho()))
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
    s.tpl_nome, s.alg_nome, s.alg_erro = "editor.pdf", "editor-algarismos.pdf", None
    await _analisar(s, serv, pasta, lg)
    serv.metricas.evento("editor", "usar", v1=float(len(pedido.elementos)))
    return vista(s, lg, pasta)
