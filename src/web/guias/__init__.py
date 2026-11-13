"""As páginas de «como fazer» (SEO e leitura): `/rifas-para-escolas` e `/rifas-para-associacoes`, nas línguas (as 18 primeiras em `escolas.py`/`associacoes.py`, as de um ficheiro só em `novas.py`).

Cada guia é um texto com título, introdução, 5 passos (título e texto), 3 dicas e uma frase final (`escolas.py`, `associacoes.py`; uma língua por entrada,
as traduções sem revisão nativa). A API entrega-o na língua do pedido (`/api/guia/{nome}`), o React desenha-o (`Guia.tsx`) e o `seo.py` põe o mesmo texto
no HTML estático. As regras de licença de uma rifa variam por país e por tipo: por isso o 1.º passo de ambos manda confirmar na câmara municipal.
"""
from __future__ import annotations

from ..seo_textos import sobreposto
from . import associacoes, escolas, novas

DADOS = {"escolas": escolas.DADOS, "associacoes": associacoes.DADOS}
DADOS["escolas"].update(novas.ESCOLAS)               # as linguas de um ficheiro so (docs/LINGUAS.md)
DADOS["associacoes"].update(novas.ASSOCIACOES)
CAMINHOS = {"escolas": "/rifas-para-escolas", "associacoes": "/rifas-para-associacoes"}
NOMES = tuple(DADOS)
N_PASSOS, N_DICAS = 5, 3


def padrao(nome: str, lingua: str = "pt") -> dict:
    """O guia como esta no codigo (sem o editado no painel)."""
    d = DADOS[nome].get(lingua) or DADOS[nome]["pt"]
    return {"titulo": d["titulo"], "intro": d["intro"], "passos": [{"titulo": t, "texto": x} for t, x in d["passos"]],
            "dicas": list(d["dicas"]), "fim": d["fim"]}


def chaves_editaveis(nome: str) -> list[str]:
    """As chaves que o painel pode editar neste guia (`guia.<nome>.titulo`, `.intro`, `.passo1.titulo`, `.passo1.texto`, `.dica1`, `.fim`...)."""
    return ([f"guia.{nome}.titulo", f"guia.{nome}.intro"] + [f"guia.{nome}.passo{i}.{c}" for i in range(1, N_PASSOS + 1) for c in ("titulo", "texto")]
            + [f"guia.{nome}.dica{i}" for i in range(1, N_DICAS + 1)] + [f"guia.{nome}.fim"])


def guia(nome: str, lingua: str = "pt") -> dict:
    """O guia `nome` na `lingua` (portugues se nao houver), com o que o painel editou por cima: {titulo, intro, passos: [{titulo, texto}], dicas: [..], fim}."""
    g = padrao(nome, lingua)
    ed = lambda chave, valor: sobreposto(f"guia.{nome}.{chave}", lingua) or valor  # noqa: E731
    return {"titulo": ed("titulo", g["titulo"]), "intro": ed("intro", g["intro"]),
            "passos": [{"titulo": ed(f"passo{i}.titulo", p["titulo"]), "texto": ed(f"passo{i}.texto", p["texto"])} for i, p in enumerate(g["passos"], 1)],
            "dicas": [ed(f"dica{i}", d) for i, d in enumerate(g["dicas"], 1)], "fim": ed("fim", g["fim"])}
