"""Traducoes: t("chave", nome=valor) devolve o texto na lingua atual (definir("en")).

Os textos estao em idiomas/<codigo>.py. Se faltar uma chave numa lingua usa o portugues. Os erros do motor
guardam a chave e os parametros e so sao traduzidos quando se mostram, por isso mudam de lingua em tempo real.
"""
from __future__ import annotations

import locale
import sys

from idiomas import NOMES as LINGUAS, TEXTOS

_atual = "pt"


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


def detetar() -> str:
    """Lingua do Windows (pt-PT -> pt, zh-CN -> zh); se nao for suportada, ingles."""
    codigo = ""
    try:
        if sys.platform == "win32":
            import ctypes
            buf = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85):
                codigo = buf.value
    except Exception:
        pass
    if not codigo:
        try:
            codigo = locale.getlocale()[0] or ""
        except Exception:
            codigo = ""
    base = codigo.replace("_", "-").split("-")[0].lower()
    return base if base in LINGUAS else "en"
