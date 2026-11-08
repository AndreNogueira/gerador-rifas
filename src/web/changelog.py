"""O changelog do site: le `CHANGELOG.md` (a unica fonte) e devolve-o estruturado.

Formato: `## <versao> — <data>`, depois `### <seccao>` e itens `- texto`. So portugues (como o painel). O texto nunca e HTML:
quem o mostra escapa-o. Um teste garante que a primeira versao e a `VERSAO` do servico.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

FICHEIRO = Path(__file__).with_name("CHANGELOG.md")
_VERSAO = re.compile(r"^##\s+(\d+\.\d+\.\d+)\s*[—-]\s*(\d{4}-\d{2}-\d{2})\s*$")
_SECCAO = re.compile(r"^###\s+(.+?)\s*$")


@dataclass
class Seccao:
    titulo: str
    itens: list[str] = field(default_factory=list)


@dataclass
class Entrada:
    versao: str
    data: str
    seccoes: list[Seccao] = field(default_factory=list)


def ler(texto: str) -> list[Entrada]:
    """As entradas por ordem do ficheiro (a mais recente primeiro). Linhas fora do formato ignoram-se; itens que continuam na
    linha seguinte (recuados) juntam-se ao anterior."""
    entradas: list[Entrada] = []
    for linha in texto.splitlines():
        if m := _VERSAO.match(linha):
            entradas.append(Entrada(m.group(1), m.group(2)))
        elif entradas and (m := _SECCAO.match(linha)):
            entradas[-1].seccoes.append(Seccao(m.group(1)))
        elif entradas and entradas[-1].seccoes and linha.startswith("- "):
            entradas[-1].seccoes[-1].itens.append(linha[2:].strip())
        elif entradas and entradas[-1].seccoes and entradas[-1].seccoes[-1].itens and linha.startswith("  ") and linha.strip():
            entradas[-1].seccoes[-1].itens[-1] += " " + linha.strip()
    return entradas


@lru_cache(maxsize=1)
def entradas() -> tuple[Entrada, ...]:
    return tuple(ler(FICHEIRO.read_text(encoding="utf-8")))
