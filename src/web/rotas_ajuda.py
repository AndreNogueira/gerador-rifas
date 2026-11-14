"""Tutorial e video: a lista de topicos (do `core.tutorial`) na lingua do pedido e as imagens recortadas das capturas."""
from __future__ import annotations

import functools
import re

from core import i18n, tutorial
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from . import config
from .modelos import ErroApi
from .rotas import lingua

router = APIRouter(prefix="/api", tags=["ajuda"])


class Imagem(BaseModel):
    url: str
    largura: float | None = None      # largura natural em pixeis CSS (as capturas sao 2x/3x); None: deixar o browser decidir


class Topico(BaseModel):
    menu: str
    titulo: str
    texto: str
    imagens: list[Imagem]
    video: str = ""                   # URL do video desta funcionalidade (so os topicos das funcionalidades o tem), vazio se nao existe


class Tutorial(BaseModel):
    topicos: list[Topico]
    video: str = ""                   # URL do video nesta lingua (so ha pt e en), vazio se nao existe


@functools.lru_cache(maxsize=48)
def _recorte(pasta: str, lg: str, estado: str, zona: str):
    from pathlib import Path
    return tutorial.recorte(Path(pasta), lg, estado, zona)


def esquecer_recortes() -> None:
    """Os recortes que deram `None` por faltarem as capturas (os assets remotos ainda nao tinham chegado) nao ficam em cache."""
    _recorte.cache_clear()


def _assets_prontos(request: Request) -> None:
    """Com os assets no armazenamento de objetos, garante (ou pede, sem esperar) que ja foram descarregados."""
    assets = getattr(request.app.state, "assets", None)
    if assets is not None:
        assets.garantir()


@router.get("/tutorial", response_model=Tutorial)
def ver_tutorial(request: Request, lg: str = Depends(lingua)) -> Tutorial:
    _assets_prontos(request)
    ajuda = config.pasta_assets() / "ajuda"
    with i18n.com_lingua(lg):
        topicos = tutorial.lista_de_topicos("web")
    ids = tutorial.video_ids("web")
    pasta_video = config.pasta_assets() / "video"
    saida = []
    for (menu, titulo, texto, imagens), id_ in zip(topicos, ids, strict=True):
        lista = []
        for img in imagens:
            if img[0] == "fixa":
                lista.append(Imagem(url=f"/ajuda/{img[1]}"))
            else:
                r = _recorte(str(ajuda), lg, img[1], img[2])
                if r is not None:
                    lista.append(Imagem(url=f"/api/tutorial/recorte/{lg}/{img[1]}/{img[2]}.png", largura=round(r[1])))
        v = tutorial.video_da_funcionalidade(pasta_video, "web", id_, lg) if id_ else None
        saida.append(Topico(menu=menu, titulo=titulo, texto=texto, imagens=lista, video=f"/videos/{v.name}" if v else ""))
    video = tutorial.ficheiro_video(config.pasta_assets() / "video", lg)
    return Tutorial(topicos=saida, video=f"/videos/{video.name}" if video else "")


@router.get("/tutorial/recorte/{lg}/{estado}/{zona}.png")
def recorte(request: Request, lg: str, estado: str, zona: str) -> Response:
    _assets_prontos(request)
    if lg not in i18n.LINGUAS or estado not in (*tutorial.ESTADOS_DE_CAPTURA, *tutorial.ESTADOS_WEB) or not re.fullmatch(r"[a-z0-9]{1,20}", zona):
        raise ErroApi(404, "Imagem inexistente", "erro")
    r = _recorte(str(config.pasta_assets() / "ajuda"), lg, estado, zona)
    if r is None:
        raise ErroApi(404, "Imagem inexistente", "erro")
    return Response(r[0], media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})
