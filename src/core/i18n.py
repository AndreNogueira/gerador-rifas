"""Traducoes: t("chave", nome=valor) devolve o texto na lingua atual (definir("en")).

Os textos estao em idiomas/<codigo>.py. Se faltar uma chave numa lingua usa o portugues. Os erros do motor
guardam a chave e os parametros e so sao traduzidos quando se mostram, por isso mudam de lingua em tempo real.

A lingua atual e GLOBAL (uma por processo): serve a app Windows; a webapp tera de a tornar por pedido (Fase 1).
"""
from __future__ import annotations

import contextlib
import contextvars
import locale
import os
import re

from .idiomas import NOMES as LINGUAS, TEXTOS

_atual = "pt"                       # lingua global (a app Windows: uma por processo)
_do_pedido: contextvars.ContextVar = contextvars.ContextVar("lingua_do_pedido", default=None)
ENV_LINGUA = "RIFAS_LINGUA"         # variavel de ambiente: forca a lingua por defeito (ex.: RIFAS_LINGUA=en)


def definir(lingua: str) -> None:
    """Muda a lingua GLOBAL (a app Windows). Numa webapp use `com_lingua` (por pedido)."""
    global _atual
    _atual = lingua if lingua in LINGUAS else "pt"


def atual() -> str:
    """A lingua em uso: a do pedido (se dentro de `com_lingua`), senao a global."""
    return _do_pedido.get() or _atual


@contextlib.contextmanager
def com_lingua(lingua: str):
    """Dentro do `with`, `t()`, `atual()` e a traducao dos erros usam `lingua` - so no contexto atual (thread ou tarefa
    asyncio), por isso pedidos concorrentes nao se atropelam. NAO passa para outras threads/processos: chame-a la dentro.
    Uma lingua desconhecida vale portugues, como em `definir`."""
    token = _do_pedido.set(lingua if lingua in LINGUAS else "pt")
    try:
        yield
    finally:
        _do_pedido.reset(token)


def traduzir(chave: str, lingua: str, **kw) -> str:
    """Funcao pura: o texto de `chave` em `lingua` (portugues se faltar), sem usar a lingua global nem a do pedido."""
    txt = TEXTOS.get(lingua, {}).get(chave)
    if txt is None:
        txt = TEXTOS["pt"][chave]
    return txt.format(**kw) if kw else txt


def t(chave: str, **kw) -> str:
    return traduzir(chave, atual(), **kw)


class Mensagem(str):
    """Texto ja traduzido (na lingua em uso quando foi criado) que guarda a chave e os parametros: o motor emite estas
    mensagens no log e nos erros de verificacao, por isso uma webapp pode traduzi-las outra vez (`.em(lingua)`) sem
    perder nada. E um `str` normal para quem so quer o texto."""
    chave: str
    params: dict

    def __new__(cls, chave: str, **params):
        obj = super().__new__(cls, t(chave, **params))
        obj.chave, obj.params = chave, params
        return obj

    def em(self, lingua: str) -> str:
        return traduzir(self.chave, lingua, **self.params)

    def __reduce__(self):           # copy/pickle (p.ex. do processo de trabalho para o servidor) mantem texto, chave e parametros
        return (_reconstruir, (str(self), self.chave, self.params))


def _reconstruir(texto: str, chave: str, params: dict) -> "Mensagem":
    obj = str.__new__(Mensagem, texto)
    obj.chave, obj.params = chave, params
    return obj


def msg(chave: str, **params) -> Mensagem:
    return Mensagem(chave, **params)


def lingua_de_codigo(codigo: str) -> str:
    """'pt-PT' -> 'pt', 'zh_CN' -> 'zh'; se a lingua nao for suportada, 'en'."""
    base = codigo.replace("_", "-").split("-")[0].lower()
    return base if base in LINGUAS else "en"


def lingua_de_accept_language(cabecalho: str | None, por_defeito: str = "en") -> str:
    """A melhor lingua suportada para um cabecalho HTTP Accept-Language (p.ex. «pt-PT,pt;q=0.9,en;q=0.8»), pela ordem de
    preferencia (q); `por_defeito` se nenhuma for suportada ou o cabecalho for invalido. E o equivalente web da lingua do Windows."""
    if not cabecalho:
        return por_defeito
    candidatas = []
    for pos, parte in enumerate(cabecalho.split(",")):
        etiqueta, _, resto = parte.strip().partition(";")
        etiqueta = etiqueta.strip()
        if not etiqueta or etiqueta == "*":
            continue
        q = 1.0
        resto = resto.strip()
        if resto.lower().startswith("q="):
            try:
                q = float(resto[2:])
            except ValueError:
                continue
        if q <= 0:
            continue
        candidatas.append((-q, pos, etiqueta))
    for _, _, etiqueta in sorted(candidatas):
        base = etiqueta.replace("_", "-").split("-")[0].lower()
        if base in LINGUAS:
            return base
    return por_defeito


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
