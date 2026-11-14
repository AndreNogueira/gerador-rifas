"""X1: o editor de templates. O desenho vem do browser em JSON (elementos com posição, cor e texto, ver `core/editor.py`); aqui só se valida,
se desenha uma pré-visualização em PNG (no processo do motor: o PDFium só lá) e «usar este template» cria o template e os algarismos na sessão,
como a galeria. Nada do que se desenha fica guardado fora do template da sessão; os eventos das métricas levam só códigos e números.
"""
from __future__ import annotations

import asyncio
import json
from concurrent.futures.process import BrokenProcessPool

from core import ErroRifas, editor, galeria, i18n
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field

from . import partilhas, trabalhos
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
    dados: str = Field("", max_length=1_400_000)                 # so a imagem: `data:image/png|jpeg;base64,…` (validada e recodificada em `core.editor`)
    tamanho: float = 12
    negrito: bool = False
    alinhamento: str = Field("e", max_length=1)
    rot: int = 0


class PedidoEditor(BaseModel):
    largura: float = 535
    altura: float = 152
    fundo: str = Field("#ffffff", max_length=7)
    elementos: list[ElementoEditor] = Field(default_factory=list, max_length=editor.MAX_ELEMENTOS + 10)

    def desenho_sem_imagens(self) -> dict:
        """O desenho sem as imagens e sem o que viria delas (o que se partilha por ligação: formas, textos e cores)."""
        d = self.model_dump(exclude_unset=True)
        d["elementos"] = [{k: v for k, v in e.items() if k != "dados"} for e in d.get("elementos", []) if e.get("tipo") != "imagem"]
        return d

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


class Partilhado(BaseModel):
    id: str


class DesenhoPartilhado(BaseModel):
    desenho: dict
    sem_imagens: bool = False


@router.post("/editor/partilhar", response_model=Partilhado, dependencies=[Depends(pesado)])
async def partilhar(pedido: PedidoEditor, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> Partilhado:
    """Guarda o desenho (sem imagens) e devolve o id da ligação `/editor?d=<id>`. Só existe com `DATABASE_URL` (ver `partilhas.py`)."""
    if serv.partilhas is None:
        raise ErroApi(404, "Partilha indisponível", "erro")
    sem = pedido.desenho_sem_imagens()
    try:
        with i18n.com_lingua(lg):
            editor.de_dict(sem)                                    # só se guarda o que o editor aceita
    except ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None
    dados = json.dumps(sem, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    try:
        id_ = await asyncio.to_thread(serv.partilhas.guardar, dados)
    except ValueError:
        raise ErroApi(413, i18n.traduzir("err_editor_limite", lg, campo="tamanho"), "aviso") from None
    except Exception as e:  # noqa: BLE001 - a base de dados em baixo nao derruba o servidor
        raise ErroApi(503, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    serv.metricas.evento("editor", "partilhar", v1=float(len(sem["elementos"])))
    return Partilhado(id=id_)


@router.get("/editor/partilha/{id_}", response_model=DesenhoPartilhado, dependencies=[Depends(leve)])
async def ver_partilha(id_: str, serv: Servico = Depends(servico), lg: str = Depends(lingua)) -> DesenhoPartilhado:
    """O desenho partilhado (já validado outra vez, para só sair o que o editor conhece). 404 se o id não existe ou o prazo acabou."""
    if serv.partilhas is None or not partilhas.ID.fullmatch(id_):
        raise ErroApi(404, i18n.traduzir("web_editor_ligacao_invalida", lg), "aviso")
    try:
        dados = await asyncio.to_thread(serv.partilhas.obter, id_)
    except Exception as e:  # noqa: BLE001
        raise ErroApi(503, i18n.traduzir("erro_inesperado", lg, erro=_motivo(e)), "erro") from None
    if dados is None:
        raise ErroApi(404, i18n.traduzir("web_editor_ligacao_invalida", lg), "aviso")
    desenho = json.loads(dados)
    editor.de_dict(desenho)                                        # nunca devolve algo que o editor recusaria
    return DesenhoPartilhado(desenho=desenho, sem_imagens=True)
