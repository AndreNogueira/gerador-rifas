"""Traducoes: t("chave", nome=valor) devolve o texto na lingua atual (definir("en")).

Os textos estao em idiomas/<codigo>.py. Se faltar uma chave numa lingua usa o portugues. Os erros do motor
guardam a chave e os parametros e so sao traduzidos quando se mostram, por isso mudam de lingua em tempo real.

A lingua atual e GLOBAL (uma por processo): serve a app Windows; a webapp tera de a tornar por pedido (Fase 1).
"""
from __future__ import annotations

import locale
import os
import re

from .idiomas import NOMES as LINGUAS, TEXTOS

_atual = "pt"
ENV_LINGUA = "RIFAS_LINGUA"         # variavel de ambiente: forca a lingua por defeito (ex.: RIFAS_LINGUA=en)


def definir(lingua: str) -> None:
    global _atual
    _atual = lingua if lingua in LINGUAS else "pt"


def atual() -> str:
    return _atual


def t(chave: str, **kw) -> str:
    txt = TEXTOS.get(_atual, {}).get(chave)
    if txt is None:
        txt = TEXTOS["pt"][chave]
    return txt.format(**kw) if kw else txt


def lingua_de_codigo(codigo: str) -> str:
    """'pt-PT' -> 'pt', 'zh_CN' -> 'zh'; se a lingua nao for suportada, 'en'."""
    base = codigo.replace("_", "-").split("-")[0].lower()
    return base if base in LINGUAS else "en"


def detetar(codigo_sistema: str = "") -> str:
    """Lingua por defeito. Ordem: variavel de ambiente RIFAS_LINGUA (se for uma lingua suportada) > `codigo_sistema`
    (a app Windows passa aqui o codigo do Windows, p.ex. «pt-PT») > locale do Python > ingles."""
    forcada = os.environ.get(ENV_LINGUA, "").strip().lower()
    if forcada in LINGUAS:
        return forcada
    codigo = codigo_sistema
    if not codigo:
        try:
            codigo = locale.getlocale()[0] or ""
        except Exception:
            codigo = ""
    return lingua_de_codigo(codigo)


def verificar_traducoes() -> list:
    """Todas as linguas tem de ter as mesmas chaves e os mesmos {parametros} que o portugues. Devolve os problemas."""
    problemas = []
    ref = TEXTOS["pt"]
    for lg, textos in TEXTOS.items():
        for k in ref.keys() - textos.keys():
            problemas.append(f"{lg}: falta {k}")
        for k in textos.keys() - ref.keys():
            problemas.append(f"{lg}: chave a mais {k}")
        for k in ref.keys() & textos.keys():
            if set(re.findall(r"\{(\w+)\}", ref[k])) != set(re.findall(r"\{(\w+)\}", textos[k])):
                problemas.append(f"{lg}: parametros diferentes em {k}")
    return problemas
