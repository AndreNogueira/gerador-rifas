"""As páginas de «como fazer» (SEO e leitura): `/rifas-para-escolas`, `/rifas-para-associacoes`, `/rifas-para-clubes`, `/rifas-para-bombeiros`, `/rifas-para-festas` e `/rifas-para-igrejas`, nas línguas
(as 18 primeiras em `<guia>.py`, as de um ficheiro só em `novas.py`).

Cada guia é um texto com título, introdução, 5 passos (título e texto), 3 dicas e uma frase final (um módulo por guia; uma língua por entrada,
as traduções sem revisão nativa). A API entrega-o na língua do pedido (`/api/guia/{nome}`), o React desenha-o (`Guia.tsx`) e o `seo.py` põe o mesmo texto
no HTML estático. As regras de licença de uma rifa variam por país e por tipo: por isso o 1.º passo dos guias por público manda confirmar na câmara municipal. Há ainda três guias por TEMA (`numerar`, `sorteio`, `quantos`: `/como-numerar-bilhetes-de-rifa`, `/sorteio-de-rifa-verificavel`, `/quantos-bilhetes-de-rifa-fazer`), com as 22 línguas no próprio módulo.
"""
from __future__ import annotations

from core import ptbr as _ptbr

from ..seo_textos import sobreposto
from . import associacoes, bombeiros, clubes, escolas, festas, igrejas, novas, numerar, quantos, sorteio

DADOS = {"escolas": escolas.DADOS, "associacoes": associacoes.DADOS, "clubes": clubes.DADOS, "bombeiros": bombeiros.DADOS, "festas": festas.DADOS, "igrejas": igrejas.DADOS}
for _nome, _novas in (("escolas", novas.ESCOLAS), ("associacoes", novas.ASSOCIACOES), ("clubes", novas.CLUBES), ("bombeiros", novas.BOMBEIROS), ("festas", novas.FESTAS), ("igrejas", novas.IGREJAS)):
    DADOS[_nome].update(_novas)                       # as linguas de um ficheiro so (docs/LINGUAS.md)
PARA_PUBLICOS = tuple(DADOS)                         # os guias por PUBLICO (`/rifas-para-<nome>`): o 1.o passo manda confirmar a licenca na camara municipal
DADOS.update({"numerar": numerar.DADOS, "sorteio": sorteio.DADOS, "quantos": quantos.DADOS})   # os guias por TEMA (as 22 linguas no proprio modulo)
CAMINHOS = {nome: f"/rifas-para-{nome}" for nome in PARA_PUBLICOS}
CAMINHOS.update({"numerar": "/como-numerar-bilhetes-de-rifa", "sorteio": "/sorteio-de-rifa-verificavel", "quantos": "/quantos-bilhetes-de-rifa-fazer"})
NOMES = tuple(DADOS)
for _nome in DADOS:
    DADOS[_nome]["pt-br"] = _ptbr.derivar_tudo(DADOS[_nome]["pt"])      # o portugues do Brasil deriva-se do de Portugal (core/ptbr.py)
N_PASSOS, N_DICAS = 5, 3
INDICE = "/como-fazer"                                # a pagina que lista todos os guias e liga a cada um (e cada guia liga de volta)


def resumo(intro: str, maximo: int = 170) -> str:
    """A primeira frase da introducao (ate ao primeiro ponto final), cortada em `maximo` letras: o que se mostra ao lado de cada guia no indice."""
    for fim in (". ", "。", "! ", "? "):
        i = intro.find(fim)
        if 0 < i < maximo:
            return intro[: i + len(fim.strip())]
    return intro[:maximo].rsplit(" ", 1)[0] + "…" if len(intro) > maximo else intro


def lista(lingua: str = "pt") -> list[dict]:
    """Os guias na `lingua`, para o indice e para as ligacoes entre guias: `{nome, caminho, titulo, resumo}`."""
    saida = []
    for nome in NOMES:
        g = guia(nome, lingua)
        saida.append({"nome": nome, "caminho": CAMINHOS[nome], "titulo": g["titulo"], "resumo": resumo(g["intro"])})
    return saida


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
