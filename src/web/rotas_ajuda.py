"""Tutorial e video: a lista de topicos (do `core.tutorial`) na lingua do pedido e as imagens recortadas das capturas."""
from __future__ import annotations

import functools
import re

from core import i18n, tutorial
from fastapi import APIRouter, Depends, Response
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


class Tutorial(BaseModel):
    topicos: list[Topico]
    video: str = ""                   # URL do video nesta lingua (so ha pt e en), vazio se nao existe


@functools.lru_cache(maxsize=48)
def _recorte(pasta: str, lg: str, estado: str, zona: str):
    from pathlib import Path
    return tutorial.recorte(Path(pasta), lg, estado, zona)


@router.get("/tutorial", response_model=Tutorial)
def ver_tutorial(lg: str = Depends(lingua)) -> Tutorial:
    ajuda = config.pasta_assets() / "ajuda"
    with i18n.com_lingua(lg):
        topicos = tutorial.lista_de_topicos()
    saida = []
    for menu, titulo, texto, imagens in topicos:
        lista = []
        for img in imagens:
            if img[0] == "fixa":
                lista.append(Imagem(url=f"/ajuda/{img[1]}"))
            else:
                r = _recorte(str(ajuda), lg, img[1], img[2])
                if r is not None:
                    lista.append(Imagem(url=f"/api/tutorial/recorte/{lg}/{img[1]}/{img[2]}.png", largura=round(r[1])))
        saida.append(Topico(menu=menu, titulo=titulo, texto=texto, imagens=lista))
    video = tutorial.ficheiro_video(config.pasta_assets() / "video", lg)
    return Tutorial(topicos=saida, video=f"/videos/{video.name}" if video else "")


@router.get("/tutorial/recorte/{lg}/{estado}/{zona}.png")
def recorte(lg: str, estado: str, zona: str) -> Response:
    if lg not in i18n.LINGUAS or estado not in tutorial.ESTADOS_DE_CAPTURA or not re.fullmatch(r"[a-z0-9]{1,20}", zona):
        raise ErroApi(404, "Imagem inexistente", "erro")
    r = _recorte(str(config.pasta_assets() / "ajuda"), lg, estado, zona)
    if r is None:
        raise ErroApi(404, "Imagem inexistente", "erro")
    return Response(r[0], media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})
