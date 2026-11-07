"""A aplicacao FastAPI: a API (`/api`), `/health` e o frontend compilado (ficheiros estaticos, com *fallback* para o index.html).

So chama `core` (um teste proibe aqui imports de pypdf/PIL/Tk). O motor corre noutro processo (`trabalhos.Motor`).
O servico e PUBLICO e sem palavra-passe: ver `limites.py` e `config.py` para as defesas.
"""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

from core import i18n
from core.armazenamento import ArmazenamentoLocal
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import VERSAO, config, rotas, rotas_ajuda
from .limites import Limitador
from .modelos import ErroApi
from .rotas import Servico
from .sessoes import Sessoes
from .trabalhos import Motor


class Lingua(BaseModel):
    codigo: str
    nome: str


class Linguas(BaseModel):
    por_defeito: str          # a lingua do browser (Accept-Language), ou ingles
    linguas: list[Lingua]


class Textos(BaseModel):
    lingua: str
    textos: dict[str, str]    # chave -> texto, com {parametros} por substituir no browser


class Saude(BaseModel):
    estado: str
    versao: str


async def _limpeza_periodica(servico: Servico, cada_s: float) -> None:
    """Apaga as sessoes inativas (e os seus ficheiros) de tempos a tempos."""
    while True:
        await asyncio.sleep(cada_s)
        with contextlib.suppress(Exception):
            servico.sessoes.limpar()


def criar_app(frontend: Path | None = None, armazenamento: Path | None = None, motor: Motor | None = None) -> FastAPI:
    """`frontend`: pasta do frontend compilado; `armazenamento`: onde ficam as sessoes (RIFAS_ARMAZENAMENTO); `motor`: para os testes."""
    pasta = (frontend or config.pasta_frontend()).resolve()
    armazem = ArmazenamentoLocal(armazenamento, limite_bytes=config.limite_sessao_mb() * 1024 * 1024)
    servico = Servico(Sessoes(armazem), motor or Motor(tempo_maximo_s=config.tempo_maximo_geracao_min() * 60), Limitador())

    @contextlib.asynccontextmanager
    async def ciclo_de_vida(app: FastAPI):
        armazem.limpar_antigas(0)                            # pastas de um arranque anterior (nao ha sessoes em memoria para elas)
        limpeza = asyncio.create_task(_limpeza_periodica(servico, 60))
        try:
            await servico.motor.aquecer()                    # o 1.o pedido nao paga o arranque do processo do motor
        except Exception:  # noqa: BLE001 - o servidor arranca na mesma; o motor recria-se no 1.o pedido
            servico.motor.reiniciar()
        try:
            yield
        finally:
            limpeza.cancel()
            servico.motor.parar()

    app = FastAPI(title="Gerador de Rifas", version=VERSAO, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json",
                  lifespan=ciclo_de_vida)
    app.state.servico = servico

    @app.exception_handler(ErroApi)
    async def _erro_api(_: Request, e: ErroApi) -> JSONResponse:
        return JSONResponse({"detail": e.texto, "tipo": e.tipo}, status_code=e.estado)

    @app.get("/health", response_model=Saude, tags=["sistema"])
    def saude() -> Saude:
        """Para o Render e para o Docker (HEALTHCHECK): 200 enquanto o servidor responde."""
        return Saude(estado="ok", versao=VERSAO)

    @app.get("/api/linguas", response_model=Linguas, tags=["textos"])
    def linguas(accept_language: str | None = Header(default=None)) -> Linguas:
        """As 18 linguas e a que corresponde ao browser (cabecalho Accept-Language)."""
        return Linguas(por_defeito=i18n.lingua_de_accept_language(accept_language),
                       linguas=[Lingua(codigo=c, nome=n) for c, n in i18n.LINGUAS.items()])

    @app.get("/api/textos/{lingua}", response_model=Textos, tags=["textos"])
    def textos(lingua: str, resposta: Response) -> Textos:
        """Todos os textos da interface numa lingua (os mesmos de `src/core/idiomas`, partilhados com a app Windows)."""
        if lingua not in i18n.LINGUAS:
            raise HTTPException(404, f"Língua desconhecida: {lingua}")
        resposta.headers["Cache-Control"] = "public, max-age=300"
        return Textos(lingua=lingua, textos={**i18n.TEXTOS["pt"], **i18n.TEXTOS[lingua]})      # o que faltar cai no portugues

    app.include_router(rotas.router)
    app.include_router(rotas_ajuda.router)

    # imagens do tutorial e videos (os mesmos ficheiros da app Windows); tem de vir antes do «fallback» do frontend
    assets = config.pasta_assets()
    for rota, sub in (("/ajuda", "ajuda"), ("/videos", "video")):
        if (assets / sub).is_dir():
            app.mount(rota, StaticFiles(directory=assets / sub), name=sub)

    @app.get("/{caminho:path}", include_in_schema=False)
    def frontend_estatico(caminho: str):
        """Ficheiros do frontend; qualquer outra rota devolve o index.html (o React trata das paginas). `/api...` nunca cai aqui."""
        if caminho == "api" or caminho.startswith("api/"):
            return JSONResponse({"detail": "Rota inexistente"}, status_code=404)
        index = pasta / "index.html"
        if not index.is_file():
            return JSONResponse({"detail": "Frontend por compilar: cd src/web/frontend && pnpm install && pnpm build"}, status_code=503)
        alvo = (pasta / caminho).resolve()
        if caminho and alvo.is_relative_to(pasta) and alvo.is_file():
            cabecalhos = {"Cache-Control": "public, max-age=31536000, immutable"} if alvo.parent.name == "assets" else {}
            return FileResponse(alvo, headers=cabecalhos)
        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app
