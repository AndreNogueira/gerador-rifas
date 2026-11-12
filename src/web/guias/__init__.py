"""As páginas de «como fazer» (SEO e leitura): `/rifas-para-escolas` e `/rifas-para-associacoes`, nas 18 línguas.

Cada guia é um texto com título, introdução, 5 passos (título e texto), 3 dicas e uma frase final (`escolas.py`, `associacoes.py`; uma língua por entrada,
as traduções sem revisão nativa). A API entrega-o na língua do pedido (`/api/guia/{nome}`), o React desenha-o (`Guia.tsx`) e o `seo.py` põe o mesmo texto
no HTML estático. As regras de licença de uma rifa variam por país e por tipo: por isso o 1.º passo de ambos manda confirmar na câmara municipal.
"""
from __future__ import annotations

from . import associacoes, escolas

DADOS = {"escolas": escolas.DADOS, "associacoes": associacoes.DADOS}
CAMINHOS = {"escolas": "/rifas-para-escolas", "associacoes": "/rifas-para-associacoes"}
NOMES = tuple(DADOS)
N_PASSOS, N_DICAS = 5, 3


def guia(nome: str, lingua: str = "pt") -> dict:
    """O guia `nome` na `lingua` (português se não houver): {titulo, intro, passos: [{titulo, texto}], dicas: [..], fim}."""
    d = DADOS[nome].get(lingua) or DADOS[nome]["pt"]
    return {"titulo": d["titulo"], "intro": d["intro"], "passos": [{"titulo": t, "texto": x} for t, x in d["passos"]],
            "dicas": list(d["dicas"]), "fim": d["fim"]}
