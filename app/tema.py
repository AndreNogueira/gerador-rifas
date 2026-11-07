"""Cores da aplicacao: seguem o Windows (cor de destaque e modo claro/escuro).

O registo do Windows le-se em ambiente.py e a paleta calcula-se em core/tema.py (sem Windows, serve tambem a webapp).

- A cor de destaque vem da paleta de personalizacao do Windows (Definicoes > Personalizacao > Cores).
- O modo escuro/claro por defeito acompanha o Windows; o utilizador pode forcar um dos dois.
`C` e um dicionario {nome: (claro, escuro)} atualizado no proprio objeto por `atualizar()`.
"""
from __future__ import annotations

import ambiente          # noqa: F401  (poe ..\src no sys.path; o registo do Windows esta la)
import customtkinter as ctk
from core.tema import PADRAO, construir, contraste, legivel as _legivel, misturar, texto_sobre   # noqa: F401
from core.tema import hex_para_rgb as _rgb, rgb_para_hex as _hex                                   # noqa: F401

FONTE = "Segoe UI"

C: dict = {}


# ------------------------------------------------------------------ Windows
def paleta_windows() -> list:
    """7 tons da cor de destaque (do mais claro ao mais escuro). Sem registo usa o azul predefinido."""
    return ambiente.paleta_do_windows() or list(PADRAO)


def windows_escuro() -> bool:
    return bool(ambiente.windows_escuro())


# ------------------------------------------------------------------ paleta (construir esta em core/tema.py)
def atualizar() -> bool:
    """Le o destaque do Windows e refaz C no proprio objeto. Devolve True se as cores mudaram."""
    novo = construir(paleta_windows())
    mudou = novo != dict(C)
    C.clear()
    C.update(novo)
    return mudou


def assinatura() -> tuple:
    """Muda quando o utilizador troca a cor de destaque do Windows."""
    return tuple(paleta_windows())


def cor_tk(par: tuple) -> str:
    """Cor para widgets tk simples (que nao aceitam pares claro/escuro)."""
    return par[1] if ctk.get_appearance_mode() == "Dark" else par[0]


def aplicar_modo(modo: str) -> None:
    """modo: 'system' (como o Windows), 'light' ou 'dark'."""
    if modo == "system":
        ctk.set_appearance_mode("dark" if windows_escuro() else "light")
    else:
        ctk.set_appearance_mode(modo)


atualizar()
