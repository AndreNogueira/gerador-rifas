"""O catálogo do preçário: categorias, artigos (com o emoji que é a sua imagem) e ocasiões ligadas aos desenhos da galeria e às épocas do ano.

Os dados estão em `precario_dados.py` (uma linha por entrada, nas 22 línguas; o pt-br deriva-se do pt: `core/ptbr.py`). Aqui lê-se, valida-se e consulta-se:
- **Região:** um artigo ou uma ocasião pode ser só de Portugal (`pt`: bifana, caldo verde, Santos Populares) ou só do Brasil (`br`: coxinha, quentão, Festa Junina): só aparecem com a língua
  respetiva; os outros aparecem em todas. O texto livre que a pessoa escreve nunca precisa de tradução.
- **Nome para o PDF:** o do site pode ter letras que o PDF não tem (hindi); `nome_imprimivel` cai para o inglês e depois o português (`core/letras.py`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import precario_dados as dados
from . import ptbr

LINGUAS = dados.LINGUAS + ("pt-br",)
MAX_NOME = 48
_EMOJI = re.compile(r"[0-9a-f]{4,6}")


@dataclass(frozen=True)
class Categoria:
    id: str
    nomes: dict


@dataclass(frozen=True)
class Artigo:
    id: str
    emoji: str                      # código hexadecimal do emoji (a imagem: `core/icones_precario/<emoji>.png`)
    categoria: str
    regiao: str                     # "" | "pt" | "br"
    nomes: dict


@dataclass(frozen=True)
class Ocasiao:
    id: str
    desenho: str                    # o id do desenho da galeria (`core.galeria.POR_ID`)
    regiao: str
    meses: tuple
    artigos: tuple
    nomes: dict


def _nomes(campos: list[str], onde: str) -> dict:
    """Os nomes por língua: `=Nome` (igual em todas), ou as 22 línguas por ordem (e, opcionalmente, o nome pt-br)."""
    if len(campos) == 1 and campos[0].startswith("="):
        n = campos[0][1:]
        return dict.fromkeys(LINGUAS, n)
    if len(campos) not in (len(dados.LINGUAS), len(dados.LINGUAS) + 1) or not all(c.strip() for c in campos):
        raise ValueError(f"{onde}: {len(campos)} nomes (esperava {len(dados.LINGUAS)} ou {len(dados.LINGUAS) + 1}, nenhum vazio)")
    nomes = dict(zip(dados.LINGUAS, (c.strip() for c in campos), strict=False))
    nomes["pt-br"] = campos[len(dados.LINGUAS)].strip() if len(campos) > len(dados.LINGUAS) else ptbr.derivar(nomes["pt"])
    return nomes


def _linhas(texto: str):
    for linha in texto.strip().splitlines():
        if linha.strip():
            yield [c for c in linha.rstrip("\n").split("|")]


CATEGORIAS: dict[str, Categoria] = {}
for _l in _linhas(dados.CATEGORIAS):
    CATEGORIAS[_l[0]] = Categoria(_l[0], _nomes(_l[1:], f"categoria {_l[0]}"))

ARTIGOS: dict[str, Artigo] = {}
for _l in _linhas(dados.ARTIGOS):
    _id, _emoji, _cat, _reg = _l[:4]
    if _id in ARTIGOS or _cat not in CATEGORIAS or _reg not in ("", "pt", "br") or not _EMOJI.fullmatch(_emoji):
        raise ValueError(f"artigo inválido: {_id}")
    ARTIGOS[_id] = Artigo(_id, _emoji, _cat, _reg, _nomes(_l[4:], f"artigo {_id}"))

OCASIOES: dict[str, Ocasiao] = {}
for _l in _linhas(dados.OCASIOES):
    _id, _desenho, _reg, _meses, _arts = _l[:5]
    _ids = tuple(a for a in _arts.split(",") if a)
    if _id in OCASIOES or _reg not in ("", "pt", "br") or any(a not in ARTIGOS for a in _ids):
        raise ValueError(f"ocasião inválida: {_id}")
    OCASIOES[_id] = Ocasiao(_id, _desenho, _reg, tuple(int(m) for m in _meses.split(",")), _ids, _nomes(_l[5:], f"ocasião {_id}"))


# ------------------------------------------------------------------ consulta
def visivel(regiao: str, lingua: str) -> bool:
    """Um item de Portugal só com `pt`, um do Brasil só com `pt-br`, os outros sempre."""
    return not regiao or (regiao == "pt" and lingua == "pt") or (regiao == "br" and lingua == "pt-br")


def nome(item, lingua: str) -> str:
    """O nome na língua do site (inglês e depois português se faltar)."""
    return item.nomes.get(lingua) or item.nomes["en"]


def nome_imprimivel(item, lingua: str) -> str:
    """O nome que o PDF consegue escrever: o da língua se houver letra para ele, senão o inglês, senão o português."""
    from . import letras
    for lg in (lingua, "en", "pt"):
        n = item.nomes.get(lg)
        if n and not letras.em_falta(n):
            return n
    return item.nomes["pt"]


def artigos_da_lingua(lingua: str) -> list[Artigo]:
    """Os artigos que a língua vê, pela ordem das categorias e do ficheiro de dados."""
    return [a for c in CATEGORIAS for a in ARTIGOS.values() if a.categoria == c and visivel(a.regiao, lingua)]


def ocasioes_da_lingua(lingua: str) -> list[Ocasiao]:
    return [o for o in OCASIOES.values() if visivel(o.regiao, lingua)]


def ocasiao_da_epoca(mes: int, lingua: str) -> Ocasiao | None:
    """A ocasião sugerida num mês (1-12): a da região da língua (Santos Populares, Festa Junina) antes das gerais; `None` se nenhuma cai nesse mês."""
    candidatas = [o for o in ocasioes_da_lingua(lingua) if mes in o.meses]
    return min(candidatas, key=lambda o: 0 if o.regiao else 1) if candidatas else None


def catalogo(lingua: str, mes: int | None = None) -> dict:
    """O catálogo para a interface (a API devolve-o): categorias com artigos, ocasiões (com os artigos que a língua vê) e a ocasião sugerida para `mes`."""
    ids = {a.id for a in artigos_da_lingua(lingua)}
    sugerida = ocasiao_da_epoca(mes, lingua) if mes else None
    return {
        "categorias": [{"id": c.id, "nome": nome(c, lingua),
                        "artigos": [{"id": a.id, "nome": nome(a, lingua), "emoji": a.emoji} for a in artigos_da_lingua(lingua) if a.categoria == c.id]} for c in CATEGORIAS.values()],
        "ocasioes": [{"id": o.id, "nome": nome(o, lingua), "desenho": o.desenho, "artigos": [a for a in o.artigos if a in ids], "meses": list(o.meses)} for o in ocasioes_da_lingua(lingua)],
        "sugerida": sugerida.id if sugerida else "",
    }
