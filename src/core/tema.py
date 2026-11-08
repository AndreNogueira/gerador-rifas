"""Cores da aplicacao a partir de uma cor de destaque - sem Windows e sem interface.

Na app Windows a cor de destaque e o modo claro/escuro vem do registo (app/ambiente.py); na web vem do CSS do browser
(`prefers-color-scheme`, `accent-color`) ou, se o dono quiser, de variaveis de ambiente (ver core.sistema). Daqui sai sempre
a mesma paleta: `construir(7 tons)` -> {nome: (claro, escuro)}, e `variaveis_css(paleta)` para a levar para a pagina.
Extraido de app/tema.py sem alterar os calculos.
"""
from __future__ import annotations

PADRAO = [(0x99, 0xEB, 0xFF), (0x4C, 0xC2, 0xFF), (0x00, 0x91, 0xF8), (0x00, 0x78, 0xD4),
          (0x00, 0x5A, 0x9E), (0x00, 0x3E, 0x92), (0x00, 0x1A, 0x68)]      # azul predefinido do Windows


def rgb_para_hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(int(round(max(0, min(255, c)))) for c in rgb)


def hex_para_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def cor_valida(txt: str | None) -> tuple | None:
    """'#0078D4' | '0078d4' -> (0, 120, 212); qualquer outra coisa -> None."""
    if not txt:
        return None
    h = txt.strip().lstrip("#")
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        return None
    return hex_para_rgb(h)


def misturar(a, b, t: float) -> tuple:
    """a*(1-t) + b*t, com a e b em RGB."""
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


def luminancia(rgb) -> float:
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def texto_sobre(fundo) -> str:
    """Branco ou quase preto, o que tiver mais contraste com a cor de fundo."""
    return "#FFFFFF" if contraste(fundo, (255, 255, 255)) >= contraste(fundo, (17, 17, 17)) else "#111111"


def legivel(cor, fundo, minimo: float = 4.5, para=(0, 0, 0)) -> tuple:
    """Escurece (ou clareia) a cor ate ter contraste suficiente com o fundo."""
    for i in range(21):
        c = misturar(cor, para, i / 20)
        if contraste(c, fundo) >= minimo:
            return c
    return c


def paleta_de_cor(base) -> list:
    """7 tons (do mais claro ao mais escuro) a partir de UMA cor de destaque RGB - como o Windows faz quando so conhece essa cor."""
    return [misturar(base, (255, 255, 255), 0.6), misturar(base, (255, 255, 255), 0.4),
            misturar(base, (255, 255, 255), 0.2), base, misturar(base, (0, 0, 0), 0.2),
            misturar(base, (0, 0, 0), 0.4), misturar(base, (0, 0, 0), 0.6)]


def _par(claro, escuro) -> tuple:
    return (rgb_para_hex(claro) if not isinstance(claro, str) else claro,
            rgb_para_hex(escuro) if not isinstance(escuro, str) else escuro)


def construir(p: list) -> dict:
    """Paleta da app a partir dos 7 tons de destaque: {nome: (cor no modo claro, cor no modo escuro)}."""
    base_c, hover_c = p[3], p[4]                       # modo claro: o destaque tal como o Windows o usa
    base_e, hover_e = p[1], p[0]                       # modo escuro: tons claros (Windows 11 faz o mesmo)
    papel_c, papel_e = (255, 255, 255), (43, 43, 43)
    bg_c, bg_e = (243, 243, 243), (28, 28, 28)
    link_c = legivel(p[4], papel_c)
    link_e = legivel(p[1], papel_e, para=(255, 255, 255))
    sup = lambda a, b, t: rgb_para_hex(misturar(a, b, t))
    return dict(
        fundo=(rgb_para_hex(bg_c), rgb_para_hex(bg_e)),
        cartao=(rgb_para_hex(papel_c), rgb_para_hex(papel_e)),
        barra=(rgb_para_hex((249, 249, 249)), rgb_para_hex((32, 32, 32))),
        borda=("#E0E0E0", "#3F3F3F"),
        texto=("#1B1B1B", "#F5F5F5"),
        suave=("#605E5C", "#A8A8A8"),
        campo=("#F7F7F7", "#242424"),
        acento=(rgb_para_hex(base_c), rgb_para_hex(base_e)),
        acento_h=(rgb_para_hex(hover_c), rgb_para_hex(hover_e)),
        sobre_acento=(texto_sobre(base_c), texto_sobre(base_e)),
        link=(rgb_para_hex(link_c), rgb_para_hex(link_e)),
        acento_suave=(sup(papel_c, base_c, 0.16), sup(papel_e, base_e, 0.28)),
        sel_menu=(sup(papel_c, base_c, 0.14), sup(papel_e, base_e, 0.30)),
        ok=("#0F7B0F", "#6CCB5F"), erro=("#C42B1C", "#FF99A4"), aviso=("#9D5D00", "#FCE100"),
        visor=("#E4E4E4", "#171717"), papel=("#FFFFFF", "#FFFFFF"),
    )


def variaveis_css(paleta: dict) -> dict:
    """{'claro': {'--rifas-fundo': '#F3F3F3', ...}, 'escuro': {...}} para a pagina (os nomes tem «_» trocado por «-»)."""
    return {modo: {"--rifas-" + nome.replace("_", "-"): par[i] for nome, par in paleta.items()}
            for i, modo in enumerate(("claro", "escuro"))}


# ------------------------------------------------------------------ visuais (a app Windows e a webapp tem os mesmos nomes)
VISUAIS = ("premiado", "natal")           # os da app Windows; a webapp tem mais (ver src/web/frontend/src/temas.ts)
VISUAL_POR_OMISSAO = "premiado"


def visual_por_epoca(hoje=None) -> str:
    """O visual automatico: o Natal em dezembro, o Premiado nos outros meses (a mesma regra de `visualPorEpoca` no site)."""
    import datetime
    return "natal" if (hoje or datetime.date.today()).month == 12 else VISUAL_POR_OMISSAO


# {visual: (cores fixas, cores extras)}; cada cor e (claro, escuro). Os valores do Premiado e do Natal sao os de
# src/web/frontend/src/estilos (_tokens.scss e temas/_natal.scss); aqui servem a janela do Windows, que so conhece estes dois.
PALETAS_VISUAIS = {
    "premiado": (
        dict(fundo=("#F3EFFE", "#0F0A22"), cartao=("#FFFFFF", "#1B1236"), barra=("#FBF9FF", "#150E2C"), borda=("#DDD5F5", "#35295A"),
             texto=("#1D1240", "#F1ECFF"), suave=("#62597F", "#AA9FCF"), campo=("#F8F6FF", "#130C2A"),
             acento=("#6A35F5", "#A68BFF"), acento_h=("#5628D8", "#C2AEFF"), link=("#5528D4", "#B9A5FF"),
             acento_suave=("#E5DCFE", "#2F2160"), sel_menu=("#E9E2FD", "#2A1D52"),
             ok=("#0B7A5F", "#3FE0B5"), erro=("#C9183A", "#FF7A90"), aviso=("#A05A00", "#FFB454"),
             visor=("#E8E2F8", "#0D0820")),
        dict(acento2=("#D62B8F", "#FF6FB5"), acento2_h=("#B81E78", "#FF9AC9"),
             passo1=("#6A35F5", "#A68BFF"), passo2=("#D62B8F", "#FF6FB5"), passo3=("#EC6A08", "#FFA14D"), passo4=("#0E9F84", "#3FE0B5"),
             banda_a=("#4A1FD6", "#3A1AC0"), banda_b=("#D62B8F", "#C42A92")),
    ),
    "natal": (
        dict(fundo=("#EEF5EF", "#08150F"), cartao=("#FFFFFF", "#10281C"), barra=("#F7FBF8", "#0B1F15"), borda=("#CFE0D4", "#234A35"),
             texto=("#12301F", "#F1FBF4"), suave=("#4C6A58", "#A6C7B2"), campo=("#F5FAF6", "#0B1F15"),
             acento=("#0F6B3F", "#6FE3A0"), acento_h=("#0B5230", "#9BF0BE"), link=("#0B5A35", "#8EE8B3"),
             acento_suave=("#D6ECDC", "#1A3D2B"), sel_menu=("#E2F0E6", "#16382A"),
             ok=("#0B7A46", "#5FE39B"), erro=("#B50F1C", "#FF7B86"), aviso=("#8A5A00", "#FFCB5C"),
             visor=("#E1ECE4", "#06120C")),
        dict(acento2=("#C1121F", "#FF6B78"), acento2_h=("#9E0E19", "#FF909A"),
             passo1=("#C1121F", "#FF6B78"), passo2=("#0F6B3F", "#6FE3A0"), passo3=("#B27700", "#FFCB5C"), passo4=("#1F6FB2", "#7CC0FF"),
             banda_a=("#0A4A2B", "#06281A"), banda_b=("#14783F", "#0D4A2C")),
    ),
}


def pares_de_contraste(paleta: dict) -> list:
    """[(descricao, cor do texto, cor do fundo, minimo)] que a paleta de um visual tem de cumprir (WCAG AA), nos dois modos (indice 0 claro, 1 escuro).
    O que se vai medir: o texto e o texto suave sobre o cartao e o fundo, os estados (ok, erro, aviso) e a ligacao sobre o cartao, e o
    texto dos botoes sobre o destaque e o magenta. Os cinzentos desativados e o que e so decoracao ficam de fora (como no WCAG)."""
    return [("texto/cartao", "texto", "cartao", 4.5), ("texto/fundo", "texto", "fundo", 4.5), ("suave/cartao", "suave", "cartao", 4.5),
            ("suave/fundo", "suave", "fundo", 4.5), ("ok/cartao", "ok", "cartao", 4.5), ("erro/cartao", "erro", "cartao", 4.5),
            ("aviso/cartao", "aviso", "cartao", 4.5), ("link/cartao", "link", "cartao", 4.5), ("texto/campo", "texto", "campo", 4.5)]
