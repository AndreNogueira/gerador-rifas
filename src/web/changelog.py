"""O changelog do site: le `CHANGELOG.md` (o original, em portugues) e as traducoes `changelog/<lingua>.md` e devolve-os estruturados.

Formato (o mesmo em todas as linguas): `## <versao> — <data>`, depois `### <seccao>` e itens `- texto`. O portugues e o completo; as outras 17 linguas
tem um **resumo traduzido** de cada versao (as mesmas versoes, seccoes e itens, mais curtos; a pagina avisa-o). O texto nunca e HTML: quem o mostra
escapa-o. Testes garantem que a primeira versao e a `VERSAO` do servico e que todas as linguas tem a mesma estrutura que o portugues.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from core import ptbr

FICHEIRO = Path(__file__).with_name("CHANGELOG.md")          # o original, em portugues
PASTA = Path(__file__).with_name("changelog")                # as traducoes: <lingua>.md
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


def ficheiro(lingua: str) -> Path:
    """O ficheiro do changelog nesta lingua (o original em portugues; ou o portugues se nao ha traducao)."""
    if lingua != "pt" and re.fullmatch(r"[a-z]{2}", lingua) and (PASTA / f"{lingua}.md").is_file():
        return PASTA / f"{lingua}.md"
    return FICHEIRO


@lru_cache(maxsize=32)
def entradas(lingua: str = "pt") -> tuple[Entrada, ...]:
    if lingua == "pt-br":                                  # o portugues do Brasil deriva-se do original (core/ptbr.py): sem ficheiro proprio, sem resumo a escrever a cada versao
        return tuple(ler(ptbr.derivar(FICHEIRO.read_text(encoding="utf-8"))))
    return tuple(ler(ficheiro(lingua).read_text(encoding="utf-8")))
