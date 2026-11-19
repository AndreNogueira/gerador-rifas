"""Termos, Privacidade e Contacto: o texto das três páginas, numa só fonte (a API entrega-o ao React; o SEO usa o português no HTML estático).

O texto vive em `legal/<língua>.py` (um módulo por língua: `legal/pt.py` é o original, as outras 17 são traduções dos mesmos parágrafos, com os
mesmos marcadores) e é **provisório**: foi redigido sem apoio jurídico e tem de ser revisto por um advogado e por um contabilista antes de o serviço
cobrar (ver docs/PLANO_PRODUTO.md §5); as traduções não tiveram revisão nativa e, em caso de divergência, vale a versão portuguesa (diz-se no aviso).
Nenhum dado pessoal está aqui: o nome do responsável e o e-mail vêm das variáveis de ambiente `RESPONSAVEL` e `CONTACTO_EMAIL` (ver config.py).
Cada página é um dict {titulo, aviso, seccoes: [{titulo, paragrafos}]}; os parágrafos são texto simples (quem os mostra escapa-os).
"""
from __future__ import annotations

import copy
import importlib
from collections.abc import Callable
from functools import lru_cache

from . import config, legal_anuncios, legal_medicoes, legal_opiniao, legal_partilhas

NOMES = ("termos", "privacidade", "contacto")


def _milhares(n: int) -> str:
    return f"{n:,}".replace(",", " ")


@lru_cache(maxsize=32)
def _modulo(lingua: str):
    """O módulo `legal.<língua>`; o português se a língua não tiver tradução (ou não existir)."""
    for lg in (lingua, "pt"):
        try:
            return importlib.import_module(f"{__package__}.legal.{lg.replace('-', '_')}")
        except ImportError:
            continue
    raise ImportError("legal.pt em falta")


def _valores(frases: dict) -> dict:
    """Os valores dos marcadores, na língua das `frases` (a configuração do serviço entra aqui, nunca no texto)."""
    nome, mail = config.responsavel(), config.contacto_email()
    return {
        "responsavel": frases["responsavel_com"].format(nome=nome) if nome else frases["responsavel_sem"],
        "contacto": frases["contacto_com"].format(email=mail) if mail else frases["contacto_sem"],
        "contacto_pagina": frases["contacto_pagina_com"].format(email=mail) if mail else frases["contacto_pagina_sem"],
        "max_numeros": _milhares(config.max_numeros()),
        "validade": config.validade_min(),
        "atualizado": frases["atualizado"],
    }


def pagina(nome: str, lingua: str = "pt") -> dict:
    """A página `nome` ({titulo, aviso, seccoes}) em `lingua` (português se não houver), com a configuração do serviço preenchida."""
    mod = _modulo(lingua)
    valores = _valores(mod.FRASES)
    saida = copy.deepcopy(mod.TEXTOS[nome])
    for s in saida["seccoes"]:
        s["paragrafos"] = [p.format_map(valores) for p in s["paragrafos"]]
    if nome == "privacidade" and config.adsense_cliente():           # com anuncios o texto «sem anuncios» deixava de ser verdade
        legal_anuncios.aplicar(saida, lingua if lingua in legal_anuncios.TEXTOS else "pt")
    if nome == "privacidade":                                           # a origem das visitas (so categorias; metricas.categoria_de_origem): sempre
        legal_medicoes.aplicar(saida, lingua if lingua in legal_medicoes.TEXTOS else "pt")
    if nome == "privacidade":                                           # os comentarios e os problemas reportados (opiniao.py, github_issues.py): sempre
        legal_opiniao.aplicar(saida, lingua if lingua in legal_opiniao.TEXTOS else "pt")
    if nome == "privacidade" and config.database_url():              # com base de dados o editor partilha desenhos por ligação (partilhas.py)
        legal_partilhas.aplicar(saida, lingua if lingua in legal_partilhas.TEXTOS else "pt")
    return saida


def termos(lingua: str = "pt") -> dict:
    return pagina("termos", lingua)


def privacidade(lingua: str = "pt") -> dict:
    return pagina("privacidade", lingua)


def contacto(lingua: str = "pt") -> dict:
    return pagina("contacto", lingua)


PAGINAS: dict[str, Callable[[], dict]] = {"termos": termos, "privacidade": privacidade, "contacto": contacto}
