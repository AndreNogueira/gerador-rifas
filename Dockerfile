# syntax=docker/dockerfile:1
# Substitui o build do .exe (Nuitka + assinatura) da app Windows: aqui o resultado e uma imagem Linux.
#   docker build --target testes -t gerador-rifas-testes .     corre pytest, o auto-teste e os testes/build do frontend (falha se algo falhar)
#   docker build --target web -t gerador-rifas .              a webapp (FastAPI + React): docker run -p 8080:8080 gerador-rifas
# Versoes exatas (as ultimas em 2026-11-07): Python 3.15.2 (a app Windows usa a mesma desde a 2.5), Node 26.13.0 (LTS desde 2026-10-28),
# uv 0.13.7, pnpm 12.18.0 (o do package.json). Para atualizar: confirmar a tag com `docker manifest inspect` e voltar a correr os testes.
ARG PYTHON=3.15.2
ARG NODE=26.13.0
ARG UV=0.13.7

# --- frontend: React + Vite + TypeScript. `pnpm build` faz tsc --noEmit e vite build; `pnpm teste` corre o Vitest.
FROM node:${NODE}-slim AS frontend
ENV CI=1
RUN npm install -g pnpm@12.18.0
WORKDIR /frontend
COPY src/web/frontend/package.json src/web/frontend/pnpm-lock.yaml src/web/frontend/pnpm-workspace.yaml* ./
RUN pnpm install --frozen-lockfile
COPY src/web/frontend/ ./
RUN pnpm run teste && pnpm run build

FROM ghcr.io/astral-sh/uv:${UV} AS uv

FROM python:${PYTHON}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 \
    UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=never
COPY --from=uv /uv /bin/uv
WORKDIR /repo
COPY pyproject.toml uv.lock ./

FROM base AS testes
RUN uv sync --frozen
COPY pytest.ini ./
COPY src ./src
COPY --from=frontend /frontend/dist ./src/web/frontend/dist
COPY tests ./tests
COPY app/exemplos ./app/exemplos
COPY app/assets ./app/assets
COPY app/ambiente.py ./app/ambiente.py
RUN uv run --no-sync python -m pytest -q -p no:cacheprovider \
 && cd src && /opt/venv/bin/python -m core ../app/exemplos /tmp/autoteste

# --- a webapp (python -m src.web), sem root. O frontend compilado vem do estagio `frontend` (nao ha Node na imagem final).
FROM base AS web
ENV HOST=0.0.0.0 PORT=8080 RIFAS_ARMAZENAMENTO=/data
RUN uv sync --frozen --no-dev && useradd --create-home rifas && mkdir /data && chown rifas /data
COPY src ./src
COPY --from=frontend /frontend/dist ./src/web/frontend/dist
# Sem `app/assets` (~20 MB de videos e capturas): o servidor descarrega-os no arranque do .zip em ASSETS_URL (armazenamento de objetos; docs/ASSETS.md).
# Sem essa variavel o tutorial funciona na mesma, so que sem videos nem capturas.
# Os valores por omissao sao os do .zip publicado (um teste confere o SHA-256 com o dos ficheiros do repositorio); o Render pode sobrepo-los.
ARG ASSETS_URL=https://br-bitter-base-b9pz4epj.storage.c-7.eu-central-1.aws.neon.tech/site-assets/assets-web-7dd2a785de65.zip
ARG ASSETS_SHA256=7dd2a785de653aec35c6781ecb512e2c177cddb95f713139a86ff4f68d8795c6
ENV ASSETS_URL=$ASSETS_URL ASSETS_SHA256=$ASSETS_SHA256
USER rifas
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD ["/opt/venv/bin/python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ['PORT'], timeout=4)"]
CMD ["/opt/venv/bin/python", "-m", "src.web"]
