"""A aplicacao FastAPI: API em /api, `/health` e o frontend compilado (ficheiros estaticos, com *fallback* para o index.html).

So chama `core` (um teste proibe aqui imports de pypdf/PIL/Tk). O motor sera chamado nas rotas da Fase 1 seguinte
(sessoes, upload, previa, gerar), sempre num processo de trabalho: ver `webapp/PLANO.md`.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from core import i18n

from . import VERSAO, config


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


def criar_app(frontend: Path | None = None) -> FastAPI:
    """`frontend`: pasta do frontend compilado (por omissao `config.pasta_frontend()`)."""
    pasta = (frontend or config.pasta_frontend()).resolve()
    app = FastAPI(title="Gerador de Rifas", version=VERSAO, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")

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
        pt = i18n.TEXTOS["pt"]
        resposta.headers["Cache-Control"] = "public, max-age=300"
        return Textos(lingua=lingua, textos={**pt, **i18n.TEXTOS[lingua]})      # o que faltar numa lingua cai no portugues

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
