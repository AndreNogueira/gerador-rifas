# syntax=docker/dockerfile:1
# Substitui o build do .exe (Nuitka + assinatura) da app Windows: aqui o resultado e uma imagem Linux.
#   docker build --target testes -t gerador-rifas-testes .     corre pytest e o auto-teste durante o build (falha se algo falhar)
# O alvo «web» (API FastAPI + frontend) junta-se na Fase 1, quando existir src/web.
ARG PYTHON=3.12

FROM python:${PYTHON}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 \
    UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=never
RUN pip install --no-cache-dir uv
WORKDIR /repo
COPY pyproject.toml uv.lock ./

FROM base AS testes
RUN uv sync --frozen
COPY pytest.ini ./
COPY src ./src
COPY tests ./tests
COPY app/exemplos ./app/exemplos
COPY app/assets ./app/assets
COPY app/ambiente.py ./app/ambiente.py
RUN uv run --no-sync python -m pytest -q -p no:cacheprovider \
 && cd src && /opt/venv/bin/python -m core ../app/exemplos /tmp/autoteste
