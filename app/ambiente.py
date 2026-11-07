"""Poe a pasta src/ (onde esta o pacote `core`, a logica sem interface) no sys.path e guarda o que e do Windows.

`import ambiente` tem de ser a primeira importacao do projeto em app.py e nos scripts de testes/. No .exe compilado
(Nuitka) nao existe pasta src/: o pacote `core` vai dentro do executavel e este ficheiro nao faz nada.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE.parent / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def dados_por_defeito() -> Path:
    """Pasta de dados da app Windows: %APPDATA%\\GeradorRifas (a variavel RIFAS_DADOS, se existir, tem prioridade
    - ver core.config.pasta_de_dados)."""
    return Path(os.environ.get("APPDATA", Path.home())) / "GeradorRifas"


def codigo_de_lingua_do_windows() -> str:
    """Codigo da lingua do Windows (p.ex. «pt-PT»), ou «» se nao se conseguir (outro sistema ou erro)."""
    try:
        if sys.platform == "win32":
            import ctypes
            buf = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85):
                return buf.value
    except Exception:
        pass
    return ""
