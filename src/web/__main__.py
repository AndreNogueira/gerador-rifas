"""`python -m src.web`: arranca a webapp (porta em PORT, por omissao 8080)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))     # src/ no caminho: `import core`

import uvicorn  # noqa: E402

from . import config  # noqa: E402
from .app import criar_app  # noqa: E402


def iniciar() -> None:
    uvicorn.run(criar_app(), host=config.host(), port=config.porta(), log_level="info")


if __name__ == "__main__":
    iniciar()
