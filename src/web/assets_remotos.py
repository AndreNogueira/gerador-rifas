"""As imagens e os videos do site vivem no armazenamento de objetos (Neon Object Storage), nao na imagem Docker.

`scripts/publicar_assets.py` junta o que o site mostra (`ajuda/` e `video/`, sem o que e so da app Windows) num `.zip` e publica-o num bucket
`public_read`; o servico recebe o URL em `ASSETS_URL` (e o SHA-256 em `ASSETS_SHA256`). No arranque, **em segundo plano** (o `/health` responde logo),
descarrega-o, confere o SHA-256 e extrai-o para uma pasta temporaria (`config.pasta_assets()`), de onde o resto do codigo o serve como sempre fez.
Se o armazenamento falhar, o site funciona sem videos nem capturas e volta a tentar passado um minuto (`garantir()`, chamado pelo tutorial).
Seguranca: so se extraem `ajuda/<nome>` e `video/<nome>` com nomes simples (nada de `..`, caminhos ou subpastas), com tetos de tamanho.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
import threading
import time
import urllib.request
import zipfile
from collections.abc import Callable
from pathlib import Path

MAX_ZIP = 120 * 1024 * 1024              # o .zip (hoje ~15 MB)
MAX_FICHEIRO = 60 * 1024 * 1024
MAX_TOTAL = 250 * 1024 * 1024
NOME = re.compile(r"^(ajuda|video)/[A-Za-z0-9][A-Za-z0-9._-]{0,100}$")
REPETIR_S = 60.0


def baixar(url: str, destino: Path, limite: int = MAX_ZIP, tempo_s: float = 30.0) -> str:
    """Descarrega `url` para `destino` (https, com teto de tamanho) e devolve o SHA-256 do que veio."""
    pedido = urllib.request.Request(url, headers={"User-Agent": "gerador-rifas"})
    h, n = hashlib.sha256(), 0
    with urllib.request.urlopen(pedido, timeout=tempo_s) as r, open(destino, "wb") as f:       # noqa: S310 - https validado em config
        while bloco := r.read(1 << 16):
            n += len(bloco)
            if n > limite:
                raise ValueError("o .zip dos assets e maior do que o teto")
            h.update(bloco)
            f.write(bloco)
    return h.hexdigest()


def extrair(zip_: Path, pasta: Path) -> int:
    """Extrai os ficheiros aceites de `zip_` para `pasta/ajuda` e `pasta/video`; devolve quantos. Nomes ou tamanhos fora do esperado: erro, sem extrair nada."""
    with zipfile.ZipFile(zip_) as z:
        membros = [i for i in z.infolist() if not i.is_dir()]
        for i in membros:
            if not NOME.match(i.filename) or i.file_size > MAX_FICHEIRO:
                raise ValueError(f"ficheiro nao aceite no .zip dos assets: {i.filename[:60]}")
        if sum(i.file_size for i in membros) > MAX_TOTAL:
            raise ValueError("o .zip dos assets descomprime para demasiado")
        for sub in ("ajuda", "video"):
            (pasta / sub).mkdir(parents=True, exist_ok=True)
        for i in membros:
            alvo = pasta / i.filename
            tmp = alvo.with_name(alvo.name + ".parcial")
            with z.open(i) as origem, open(tmp, "wb") as saida:
                shutil.copyfileobj(origem, saida)
            os.replace(tmp, alvo)                        # o StaticFiles nunca ve um ficheiro a meio
    return len(membros)


class AssetsRemotos:
    """Tem os assets prontos em `pasta`? Descarrega-os em segundo plano (uma vez; repete passado `REPETIR_S` se falhou e alguem os pedir)."""

    def __init__(self, url: str, sha256: str, pasta: Path, descarregar: Callable[[str, Path], str] | None = None,
                 ao_ficar_pronto: Callable[[], None] | None = None):
        self.url, self.sha256, self.pasta, self._baixar = url, sha256, Path(pasta), descarregar or baixar
        self._ao_ficar_pronto = ao_ficar_pronto
        self._marca = self.pasta / ".pronto"
        self._trava = threading.Lock()
        self._fio: threading.Thread | None = None
        self._ultima = float("-inf")
        self.erro = ""
        (self.pasta / "ajuda").mkdir(parents=True, exist_ok=True)          # o StaticFiles precisa de que as pastas existam ao montar
        (self.pasta / "video").mkdir(parents=True, exist_ok=True)

    @property
    def identidade(self) -> str:
        return hashlib.sha256(f"{self.url}|{self.sha256}".encode()).hexdigest()

    @property
    def pronto(self) -> bool:
        try:
            return self._marca.read_text(encoding="utf-8") == self.identidade
        except OSError:
            return False

    def _correr(self) -> None:
        try:
            with tempfile.TemporaryDirectory(prefix="assets-") as tmp:
                zip_ = Path(tmp) / "assets.zip"
                obtido = self._baixar(self.url, zip_)
                if self.sha256 and obtido != self.sha256:
                    raise ValueError("o SHA-256 do .zip dos assets nao e o esperado")
                extrair(zip_, self.pasta)
            self._marca.write_text(self.identidade, encoding="utf-8")
            self.erro = ""
            if self._ao_ficar_pronto:
                self._ao_ficar_pronto()
        except Exception as e:  # noqa: BLE001 - nunca derruba o servidor: o site fica sem videos ate voltar a tentar
            self.erro = f"{type(e).__name__}: {e}"[:200]

    def garantir(self, esperar: bool = False) -> bool:
        """Dispara o descarregamento se ainda nao esta pronto (e nao ha um a correr nem tentou ha menos de `REPETIR_S`). Devolve se esta pronto."""
        if self.pronto:
            return True
        with self._trava:
            correndo = self._fio is not None and self._fio.is_alive()
            if not correndo and time.monotonic() - self._ultima >= REPETIR_S:
                self._ultima = time.monotonic()
                self._fio = threading.Thread(target=self._correr, name="assets-remotos", daemon=True)
                self._fio.start()
            fio = self._fio
        if esperar and fio is not None:
            fio.join()
        return self.pronto
