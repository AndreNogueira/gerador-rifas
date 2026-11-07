"""Configuracao da webapp: tudo por variaveis de ambiente (nada de caminhos nem segredos no codigo)."""
from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]            # raiz do repositorio (ou /repo no contentor)


def _inteiro(nome: str, por_defeito: int) -> int:
    try:
        v = int(os.environ.get(nome, "").strip())
        return v if v > 0 else por_defeito
    except ValueError:
        return por_defeito


def porta() -> int:
    """Porta onde ouvir: variavel PORT (por omissao 8080)."""
    return _inteiro("PORT", 8080)


def host() -> str:
    """127.0.0.1 por omissao (so este computador); num contentor define-se HOST=0.0.0.0."""
    return os.environ.get("HOST", "").strip() or "127.0.0.1"


def pasta_frontend() -> Path:
    """Onde esta o frontend compilado (`pnpm build` -> src/web/frontend/dist). RIFAS_FRONTEND troca-o."""
    env = os.environ.get("RIFAS_FRONTEND", "").strip()
    return Path(env) if env else Path(__file__).resolve().parent / "frontend" / "dist"
