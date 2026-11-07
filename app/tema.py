"""Cores da aplicacao: seguem o Windows (cor de destaque e modo claro/escuro).

- A cor de destaque vem da paleta de personalizacao do Windows (Definicoes > Personalizacao > Cores).
- O modo escuro/claro por defeito acompanha o Windows; o utilizador pode forcar um dos dois.
`C` e um dicionario {nome: (claro, escuro)} atualizado no proprio objeto por `atualizar()`.
"""
from __future__ import annotations

import sys

try:                                    # so existe no Windows
    import winreg
except ImportError:                     # pragma: no cover
    winreg = None

import customtkinter as ctk

FONTE = "Segoe UI"
PADRAO = [(0x99, 0xEB, 0xFF), (0x4C, 0xC2, 0xFF), (0x00, 0x91, 0xF8), (0x00, 0x78, 0xD4),
          (0x00, 0x5A, 0x9E), (0x00, 0x3E, 0x92), (0x00, 0x1A, 0x68)]      # azul predefinido do Windows

C: dict = {}


# ------------------------------------------------------------------ utilitarios de cor
def _hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(int(round(max(0, min(255, c)))) for c in rgb)


def _rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def misturar(a, b, t: float) -> tuple:
    """a*(1-t) + b*t, com a e b em RGB."""
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


def _lum(rgb) -> float:
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def texto_sobre(fundo) -> str:
    """Branco ou quase preto, o que tiver mais contraste com a cor de fundo."""
    return "#FFFFFF" if contraste(fundo, (255, 255, 255)) >= contraste(fundo, (17, 17, 17)) else "#111111"


def _legivel(cor, fundo, minimo: float = 4.5, para=(0, 0, 0)) -> tuple:
    """Escurece (ou clareia) a cor ate ter contraste suficiente com o fundo."""
    for i in range(21):
        c = misturar(cor, para, i / 20)
        if contraste(c, fundo) >= minimo:
            return c
    return c


# ------------------------------------------------------------------ Windows
def paleta_windows() -> list:
    """7 tons da cor de destaque (do mais claro ao mais escuro). Sem registo usa o azul predefinido."""
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent") as k:
                v, _ = winreg.QueryValueEx(k, "AccentPalette")
            if len(v) >= 28:
                return [tuple(v[i:i + 3]) for i in range(0, 28, 4)]
        except OSError:
            pass
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\DWM") as k:
                v, _ = winreg.QueryValueEx(k, "AccentColor")        # 0xAABBGGRR
            base = (v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF)
            return [misturar(base, (255, 255, 255), 0.6), misturar(base, (255, 255, 255), 0.4),
                    misturar(base, (255, 255, 255), 0.2), base, misturar(base, (0, 0, 0), 0.2),
                    misturar(base, (0, 0, 0), 0.4), misturar(base, (0, 0, 0), 0.6)]
        except OSError:
            pass
    return list(PADRAO)


def windows_escuro() -> bool:
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
                return winreg.QueryValueEx(k, "AppsUseLightTheme")[0] == 0
        except OSError:
            pass
    return False


# ------------------------------------------------------------------ paleta
def _par(claro, escuro) -> tuple:
    return (_hex(claro) if not isinstance(claro, str) else claro,
            _hex(escuro) if not isinstance(escuro, str) else escuro)


def construir(p: list) -> dict:
    """Paleta da app a partir dos 7 tons de destaque do Windows."""
    base_c, hover_c = p[3], p[4]                       # modo claro: o destaque tal como o Windows o usa
    base_e, hover_e = p[1], p[0]                       # modo escuro: tons claros (Windows 11 faz o mesmo)
    papel_c, papel_e = (255, 255, 255), (43, 43, 43)
    bg_c, bg_e = (243, 243, 243), (28, 28, 28)
    link_c = _legivel(p[4], papel_c)
    link_e = _legivel(p[1], papel_e, para=(255, 255, 255))
    sup = lambda a, b, t: _hex(misturar(a, b, t))
    return dict(
        fundo=(_hex(bg_c), _hex(bg_e)),
        cartao=(_hex(papel_c), _hex(papel_e)),
        barra=(_hex((249, 249, 249)), _hex((32, 32, 32))),
        borda=("#E0E0E0", "#3F3F3F"),
        texto=("#1B1B1B", "#F5F5F5"),
        suave=("#605E5C", "#A8A8A8"),
        campo=("#F7F7F7", "#242424"),
        acento=(_hex(base_c), _hex(base_e)),
        acento_h=(_hex(hover_c), _hex(hover_e)),
        sobre_acento=(texto_sobre(base_c), texto_sobre(base_e)),
        link=(_hex(link_c), _hex(link_e)),
        acento_suave=(sup(papel_c, base_c, 0.16), sup(papel_e, base_e, 0.28)),
        sel_menu=(sup(papel_c, base_c, 0.14), sup(papel_e, base_e, 0.30)),
        ok=("#0F7B0F", "#6CCB5F"), erro=("#C42B1C", "#FF99A4"), aviso=("#9D5D00", "#FCE100"),
        visor=("#E4E4E4", "#171717"), papel=("#FFFFFF", "#FFFFFF"),
    )


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
