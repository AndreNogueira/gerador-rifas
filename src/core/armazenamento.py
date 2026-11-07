"""Onde ficam os ficheiros do utilizador num servidor (uploads, PDFs gerados): uma pasta por sessao, configuravel, que se apaga sozinha.

Substitui «ficheiros locais escolhidos nos dialogos» da app Windows: o utilizador faz upload (core.entradas) e descarrega o resultado
(core.saida); entre os dois, tudo vive aqui, em `RIFAS_ARMAZENAMENTO` (por defeito, a pasta temporaria do sistema).
`Armazenamento` e o contrato; `ArmazenamentoLocal` usa uma pasta. Mais tarde pode haver um S3/Blob com a mesma interface - o motor
(PDFium) precisa de ficheiros locais, por isso `ficheiro_local` devolve sempre um Path (um S3 descarregava para uma cache).
"""
from __future__ import annotations

import os
import re
import secrets
import shutil
import tempfile
import time
from pathlib import Path
from typing import Protocol, runtime_checkable

ENV_ARMAZENAMENTO = "RIFAS_ARMAZENAMENTO"
ENV_LIMITE_MB = "RIFAS_LIMITE_SESSAO_MB"
_SESSAO = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
_NOME = re.compile(r"^[^\x00-\x1f<>:\"/\\|?*]{1,200}$")


class ArmazenamentoCheio(Exception):
    """A sessao ultrapassaria o limite de espaco."""


@runtime_checkable
class Armazenamento(Protocol):
    def nova_sessao(self) -> str: ...
    def guardar(self, sessao: str, nome: str, dados: bytes, sub: str = "") -> Path: ...
    def ler(self, sessao: str, nome: str, sub: str = "") -> bytes: ...
    def existe(self, sessao: str, nome: str, sub: str = "") -> bool: ...
    def listar(self, sessao: str, sub: str = "") -> list: ...
    def ficheiro_local(self, sessao: str, nome: str, sub: str = "") -> Path: ...
    def pasta(self, sessao: str, sub: str = "") -> Path: ...
    def tamanho(self, sessao: str) -> int: ...
    def apagar_sessao(self, sessao: str) -> None: ...
    def limpar_antigas(self, max_idade_s: float, agora: float | None = None) -> int: ...


def raiz_por_defeito() -> Path:
    env = os.environ.get(ENV_ARMAZENAMENTO, "").strip()
    return Path(env) if env else Path(tempfile.gettempdir()) / "gerador-rifas"


def limite_por_defeito() -> int | None:
    """Limite de bytes por sessao a partir de RIFAS_LIMITE_SESSAO_MB (vazio ou invalido = sem limite)."""
    try:
        mb = float(os.environ.get(ENV_LIMITE_MB, ""))
        return int(mb * 1024 * 1024) if mb > 0 else None
    except ValueError:
        return None


class ArmazenamentoLocal:
    """Uma pasta por sessao dentro de `raiz`. Os ids de sessao e os nomes sao validados (nada de «..», barras ou unidades)."""

    def __init__(self, raiz: Path | None = None, limite_bytes: int | None = None):
        self.raiz = Path(raiz) if raiz is not None else raiz_por_defeito()
        self.limite = limite_bytes if limite_bytes is not None else limite_por_defeito()
        self.raiz.mkdir(parents=True, exist_ok=True)

    # -- validacao
    @staticmethod
    def _validar_sessao(sessao: str) -> str:
        if not isinstance(sessao, str) or not _SESSAO.match(sessao):
            raise ValueError("identificador de sessao invalido")
        return sessao

    @staticmethod
    def _validar_nome(nome: str) -> str:
        if not isinstance(nome, str) or not _NOME.match(nome) or nome in (".", "..") or nome != nome.strip(" ."):
            raise ValueError("nome de ficheiro invalido")
        return nome

    def _dir(self, sessao: str, sub: str = "") -> Path:
        d = self.raiz / self._validar_sessao(sessao)
        return d / self._validar_nome(sub) if sub else d

    # -- sessoes
    def nova_sessao(self) -> str:
        sessao = secrets.token_urlsafe(18)
        self._dir(sessao).mkdir(parents=True)
        return sessao

    def pasta(self, sessao: str, sub: str = "") -> Path:
        """A pasta da sessao (ou de uma subpasta, p.ex. «saida»), criada se nao existir."""
        d = self._dir(sessao, sub)
        d.mkdir(parents=True, exist_ok=True)
        return d

    def apagar_sessao(self, sessao: str) -> None:
        shutil.rmtree(self._dir(sessao), ignore_errors=True)

    # -- ficheiros
    def guardar(self, sessao: str, nome: str, dados: bytes, sub: str = "") -> Path:
        destino = self.pasta(sessao, sub) / self._validar_nome(nome)
        if self.limite is not None:
            antigo = destino.stat().st_size if destino.exists() else 0
            if self.tamanho(sessao) - antigo + len(dados) > self.limite:
                raise ArmazenamentoCheio(f"limite de {self.limite} bytes por sessao")
        destino.write_bytes(dados)
        return destino

    def ficheiro_local(self, sessao: str, nome: str, sub: str = "") -> Path:
        f = self._dir(sessao, sub) / self._validar_nome(nome)
        if not f.is_file():
            raise FileNotFoundError(nome)
        return f

    def ler(self, sessao: str, nome: str, sub: str = "") -> bytes:
        return self.ficheiro_local(sessao, nome, sub).read_bytes()

    def existe(self, sessao: str, nome: str, sub: str = "") -> bool:
        return (self._dir(sessao, sub) / self._validar_nome(nome)).is_file()

    def listar(self, sessao: str, sub: str = "") -> list:
        d = self._dir(sessao, sub)
        return sorted(p.name for p in d.iterdir() if p.is_file()) if d.is_dir() else []

    def tamanho(self, sessao: str) -> int:
        d = self._dir(sessao)
        return sum(p.stat().st_size for p in d.rglob("*") if p.is_file()) if d.is_dir() else 0

    # -- limpeza
    def limpar_antigas(self, max_idade_s: float, agora: float | None = None) -> int:
        """Apaga as sessoes sem alteracoes ha mais de `max_idade_s` segundos. Devolve quantas apagou."""
        agora = time.time() if agora is None else agora
        apagadas = 0
        for d in self.raiz.iterdir():
            if not (d.is_dir() and _SESSAO.match(d.name)):
                continue                                  # so mexe nas pastas que sao sessoes
            ultimo = max([d.stat().st_mtime] + [p.stat().st_mtime for p in d.rglob("*")])
            if agora - ultimo > max_idade_s:
                shutil.rmtree(d, ignore_errors=True)
                apagadas += 1
        return apagadas
