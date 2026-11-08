"""Cores da aplicacao: a identidade «Premiado» (violeta e magenta, a mesma da webapp), ou as do Windows se se pedir.

O registo do Windows le-se em ambiente.py e a paleta neutra calcula-se em core/tema.py (sem Windows, serve tambem a webapp).

- POR DEFEITO a app usa as cores da marca (violeta #6A35F5 e magenta #D62B8F), claras e escuras, como a webapp.
- RIFAS_COR_DESTAQUE=windows segue a cor de destaque do Windows (Definicoes > Personalizacao > Cores);
  RIFAS_COR_DESTAQUE=#RRGGBB usa essa cor de destaque, ambas com os cinzentos neutros do Windows.
- O modo escuro/claro por defeito acompanha o Windows; o utilizador pode forcar um dos dois.
`C` e um dicionario {nome: (claro, escuro)} atualizado no proprio objeto por `atualizar()`.
"""
from __future__ import annotations

import os

import ambiente          # noqa: F401  (poe ..\src no sys.path; o registo do Windows esta la)
import customtkinter as ctk
from core import tema as core_tema
from core.tema import PADRAO, construir, contraste, cor_valida, legivel as _legivel, misturar, paleta_de_cor, texto_sobre   # noqa: F401
from core.tema import hex_para_rgb as _rgb, rgb_para_hex as _hex                                                           # noqa: F401

FONTE = "Segoe UI"

C: dict = {}

MARCA = (0x6A, 0x35, 0xF5)          # o violeta da marca (o mesmo de src/web/frontend: --destaque)

# As cores dos visuais «Premiado» e «Natal» (as mesmas de src/web/frontend; a paleta vive em core/tema.py, sem Tk, para ter testes)
VISUAL = "auto"          # «auto» (o Natal em dezembro, o Premiado nos outros meses), «premiado» ou «natal»


def definir_visual(valor: str) -> None:
    global VISUAL
    VISUAL = valor if valor == "auto" or valor in core_tema.VISUAIS else "auto"


def visual_efetivo() -> str:
    return core_tema.visual_por_epoca() if VISUAL == "auto" else VISUAL


# ------------------------------------------------------------------ Windows
def paleta_windows() -> list:
    """7 tons da cor de destaque (do mais claro ao mais escuro). Sem registo usa o azul predefinido."""
    return ambiente.paleta_do_windows() or list(PADRAO)


def windows_escuro() -> bool:
    return bool(ambiente.windows_escuro())


def _escolha() -> str:
    return os.environ.get("RIFAS_COR_DESTAQUE", "").strip().lower()


def marca_ativa() -> bool:
    """True com as cores da marca (por defeito); False se RIFAS_COR_DESTAQUE pede as do Windows ou uma cor propria."""
    e = _escolha()
    return not (e == "windows" or cor_valida(e))


def _paleta_pedida() -> list:
    e = _escolha()
    if e == "windows":
        return paleta_windows()
    rgb = cor_valida(e)
    return paleta_de_cor(rgb) if rgb else paleta_de_cor(MARCA)


def _par_rgb(par: tuple) -> tuple:
    return _rgb(par[0]), _rgb(par[1])


def _paleta_completa() -> dict:
    p = construir(_paleta_pedida())
    if marca_ativa():
        fixas, extras = core_tema.PALETAS_VISUAIS[visual_efetivo()]
        p.update(fixas)
        p["sobre_acento"] = tuple(texto_sobre(c) for c in _par_rgb(p["acento"]))
        p.update(extras)
    else:                                   # cor do Windows: o magenta e os passos reutilizam o destaque
        p.update(acento2=p["acento"], acento2_h=p["acento_h"], banda_a=p["acento_h"], banda_b=p["acento"])
        for i in range(1, 5):
            p[f"passo{i}"] = p["acento"]
    p["sobre_acento2"] = tuple(texto_sobre(c) for c in _par_rgb(p["acento2"]))
    for i in range(1, 5):
        p[f"sobre_passo{i}"] = tuple(texto_sobre(c) for c in _par_rgb(p[f"passo{i}"]))
    return p


# ------------------------------------------------------------------ paleta
def atualizar() -> bool:
    """Refaz C no proprio objeto (cor da marca, ou do Windows se se pediu). Devolve True se as cores mudaram."""
    novo = _paleta_completa()
    mudou = novo != dict(C)
    C.clear()
    C.update(novo)
    return mudou


def assinatura() -> tuple:
    """Muda quando o utilizador troca a cor de destaque do Windows (so conta se a app a segue)."""
    return (tuple(paleta_windows()) if _escolha() == "windows" else tuple(_paleta_pedida())) + (visual_efetivo(),)


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
