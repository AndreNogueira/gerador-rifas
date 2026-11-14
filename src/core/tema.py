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
NOMES_VISUAIS = {"premiado": "Premiado", "quermesse": "Quermesse", "arcade": "Arcade", "brutalista": "Brutalista", "risografia": "Risografia",
                 "janela98": "Janela 98", "gala": "Gala", "matrix": "Matrix Gamer", "natal": "Natal", "halloween": "Halloween", "praia": "Praia",
                 "jornal": "Jornal antigo", "terminal": "Terminal verde", "circo": "Cartaz de circo"}      # nomes proprios: nao se traduzem (os mesmos de temas.ts)
VISUAIS = tuple(NOMES_VISUAIS)           # os mesmos 14 da webapp (src/web/frontend/src/temas.ts); aqui so as cores (a faixa, as letras e os fundos nao passam para o Tk)
VISUAL_POR_OMISSAO = "premiado"


def visual_por_epoca(hoje=None) -> str:
    """O visual automatico: o Natal em dezembro, o Premiado nos outros meses (a mesma regra de `visualPorEpoca` no site)."""
    import datetime
    return "natal" if (hoje or datetime.date.today()).month == 12 else VISUAL_POR_OMISSAO


# {visual: (cores fixas, cores extras)}; cada cor e (claro, escuro). Os valores do Premiado e do Natal sao os de
# src/web/frontend/src/estilos (_tokens.scss e temas/_natal.scss). Os outros 12 sairam de `temas/_<id>.scss` (as cores de `light-dark(claro, escuro)`), com o
# que o Tk precisa a mais derivado delas e o texto e os estados (ok, erro, aviso) aproximados da cor do tema ate terem contraste WCAG AA sobre o cartao e o fundo
# (no site medem-se contra os pixeis do fundo, aqui contra uma cor lisa).
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
    "quermesse": (
        dict(fundo=("#FFF1CF", "#17122E"), cartao=("#FFFDF6", "#261B46"), barra=("#FFF6E1", "#1E1639"), borda=("#ECD7A4", "#43346E"),
             texto=("#3A1420", "#FDF1DC"), suave=("#7A5A50", "#C5B6DA"), campo=("#FFF8E4", "#1A1237"), acento=("#C4122F", "#FF7587"),
             acento_h=("#990E25", "#FF93A1"), link=("#C4122F", "#FF7587"), acento_suave=("#F7DCDA", "#512D53"),
             sel_menu=("#F9E6E2", "#492950"), ok=("#0B7A5F", "#3FE0B5"), erro=("#C9183A", "#FF7A90"), aviso=("#A05A00", "#FFB454"),
             visor=("#F0E3C3", "#0F0C1E")),
        dict(acento2=("#197F70", "#3DDBC2"), acento2_h=("#136358", "#68E3CF"), passo1=("#C4122F", "#FF7587"), passo2=("#976500", "#FFC93C"),
             passo3=("#2556A8", "#84ACFF"), passo4=("#197F70", "#3DDBC2"), banda_a=("#7A0B1D", "#803A44"), banda_b=("#167063", "#248273")),
    ),
    "arcade": (
        dict(fundo=("#E9E6FF", "#0B0A1F"), cartao=("#FFFFFF", "#15133D"), barra=("#F3F1FF", "#100E2C"), borda=("#B9B3FF", "#34318A"),
             texto=("#1A1650", "#E8F4FF"), suave=("#575392", "#9A97D6"), campo=("#F4F2FF", "#0D0C2B"), acento=("#3B2BFF", "#00E5FF"),
             acento_h=("#2E22C7", "#38EBFF"), link=("#3B2BFF", "#00E5FF"), acento_suave=("#E4E1FF", "#113D64"),
             sel_menu=("#EBEAFF", "#12355C"), ok=("#007A3F", "#39FF88"), erro=("#D1103A", "#FF5C7A"), aviso=("#8A5A00", "#FFE600"),
             visor=("#DBD8F0", "#070614")),
        dict(acento2=("#D71197", "#FF2BD6"), acento2_h=("#A80D76", "#FF5ADF"), passo1=("#3B2BFF", "#00E5FF"), passo2=("#D71197", "#FF2BD6"),
             passo3=("#C47600", "#FFE600"), passo4=("#008141", "#39FF88"), banda_a=("#251B9E", "#007280"), banda_b=("#BD0F85", "#B21E96")),
    ),
    "brutalista": (
        dict(fundo=("#FFE14D", "#121212"), cartao=("#FFFFFF", "#1E1E1E"), barra=("#FFEE9D", "#171717"), borda=("#0A0A0A", "#F5F5F5"),
             texto=("#0A0A0A", "#F5F5F5"), suave=("#4A4A4A", "#B8B8B8"), campo=("#FFFFFF", "#151515"), acento=("#2433E6", "#8EA2FF"),
             acento_h=("#1C28B3", "#A7B6FF"), link=("#2433E6", "#8EA2FF"), acento_suave=("#E0E2FC", "#34384B"),
             sel_menu=("#E9EBFC", "#303342"), ok=("#087A4A", "#4AE39B"), erro=("#D10F3A", "#FF6A86"), aviso=("#8A5200", "#FFB84A"),
             visor=("#F0D448", "#0C0C0C")),
        dict(acento2=("#FF3D81", "#FF6AA0"), acento2_h=("#C73065", "#FF8BB5"), passo1=("#2433E6", "#8EA2FF"), passo2=("#E50050", "#FF6AA0"),
             passo3=("#FF8A00", "#FFA940"), passo4=("#00A86B", "#4AE39B"), banda_a=("#16208F", "#475180"), banda_b=("#D5336C", "#B24A70")),
    ),
    "risografia": (
        dict(fundo=("#F3EFE6", "#17171D"), cartao=("#FFFDF8", "#1F1F27"), barra=("#F8F5EE", "#1B1B22"), borda=("#C9D4E6", "#3A3A4C"),
             texto=("#1B2A52", "#F1EFE8"), suave=("#4D5A7D", "#AAA8C0"), campo=("#F8F5EC", "#16161C"), acento=("#0068A8", "#5DB4FF"),
             acento_h=("#005183", "#81C4FF"), link=("#0068A8", "#5DB4FF"), acento_suave=("#DBE8ED", "#2B3D52"),
             sel_menu=("#E6EEF0", "#29374A"), ok=("#00774A", "#4BE0A0"), erro=("#C4143A", "#FF6A86"), aviso=("#8A5000", "#FFC24A"),
             visor=("#E4E1D8", "#0F0F13")),
        dict(acento2=("#D71F89", "#FF5CBC"), acento2_h=("#A8186B", "#FF80CB"), passo1=("#0068A8", "#5DB4FF"), passo2=("#D61E88", "#FF5CBC"),
             passo3=("#E65100", "#FF9A52"), passo4=("#00814C", "#4BE0A0"), banda_a=("#004068", "#2E5A80"), banda_b=("#BD1B79", "#B24084")),
    ),
    "janela98": (
        dict(fundo=("#0A8585", "#0D2B2B"), cartao=("#C0C0C0", "#3B3B40"), barra=("#5CA0A0", "#223234"), borda=("#808080", "#1C1C20"),
             texto=("#000000", "#F0F0F0"), suave=("#000000", "#C4C4CC"), campo=("#FFFFFF", "#1B1B20"), acento=("#000080", "#9DB8FF"),
             acento_h=("#000064", "#B3C8FF"), link=("#000080", "#9DB8FF"), acento_suave=("#A5A5B7", "#4F5466"),
             sel_menu=("#ADADBA", "#4B4F5F"), ok=("#005500", "#6EE06E"), erro=("#960000", "#FF8888"), aviso=("#683F00", "#FFCB5C"),
             visor=("#0A7D7D", "#081C1C")),
        dict(acento2=("#C00000", "#FF8A8A"), acento2_h=("#960000", "#FFA4A4"), passo1=("#000080", "#8FA9FF"), passo2=("#800080", "#E09CFF"),
             passo3=("#804000", "#FFB066"), passo4=("#006060", "#66E0D0"), banda_a=("#00004F", "#4E5C80"), banda_b=("#A90000", "#AA5C5C")),
    ),
    "gala": (
        dict(fundo=("#ECEFF5", "#0A101F"), cartao=("#FBFCFF", "#121A30"), barra=("#F3F5FA", "#0E1427"), borda=("#CDD3E0", "#2A3454"),
             texto=("#0D1B34", "#F6EEDB"), suave=("#56627D", "#AEB4C8"), campo=("#F2F4FA", "#0C1326"), acento=("#8A6516", "#E6C56E"),
             acento_h=("#6C4F11", "#ECD28E"), link=("#8A6516", "#E6C56E"), acento_suave=("#EBE7DE", "#3C3C3C"),
             sel_menu=("#F0EDE8", "#34353A"), ok=("#0B7A56", "#46E0AC"), erro=("#B0102E", "#FF7D94"), aviso=("#8A5A00", "#FFC861"),
             visor=("#DEE1E6", "#060A14")),
        dict(acento2=("#0F7A5C", "#35D6A4"), acento2_h=("#0C5F48", "#61DFB8"), passo1=("#8A6516", "#E6C56E"), passo2=("#0F7A5C", "#35D6A4"),
             passo3=("#A3112F", "#FF7D94"), passo4=("#1D4EA8", "#7BA6FF"), banda_a=("#563F0E", "#736237"), banda_b=("#0D6B51", "#207F62")),
    ),
    "matrix": (
        dict(fundo=("#E3F9E8", "#020A04"), cartao=("#FBFFFC", "#06150A"), barra=("#EEFCF1", "#040F07"), borda=("#B5DCC0", "#0F4D22"),
             texto=("#052E12", "#C8FFD4"), suave=("#3D6B4B", "#62C57E"), campo=("#F0FCF3", "#031007"), acento=("#007A2E", "#00FF66"),
             acento_h=("#005F24", "#38FF88"), link=("#007A2E", "#00FF66"), acento_suave=("#D8ECDF", "#05441C"),
             sel_menu=("#E2F2E7", "#053A19"), ok=("#007A2E", "#00FF66"), erro=("#C4143A", "#FF4D6D"), aviso=("#8A6500", "#FFD400"),
             visor=("#D5EADA", "#010603")),
        dict(acento2=("#C4109E", "#FF2BD6"), acento2_h=("#990C7B", "#FF5ADF"), passo1=("#007A2E", "#00FF66"), passo2=("#007A99", "#00E5FF"),
             passo3=("#C4109E", "#FF2BD6"), passo4=("#A87A00", "#FFD400"), banda_a=("#004C1D", "#008033"), banda_b=("#AC0E8B", "#B21E96")),
    ),
    "halloween": (
        dict(fundo=("#FFF1E0", "#130A1D"), cartao=("#FFFAF3", "#1F1230"), barra=("#FFF5E9", "#180E26"), borda=("#F0CFA6", "#3D2659"),
             texto=("#2A1238", "#FBEEDD"), suave=("#6A4A63", "#C4AAD8"), campo=("#FFF6EA", "#170C26"), acento=("#B8480A", "#FF9A3D"),
             acento_h=("#903808", "#FFB068"), link=("#B8480A", "#FF9A3D"), acento_suave=("#F5E1D2", "#4C2D33"),
             sel_menu=("#F8E8DC", "#432832"), ok=("#13734A", "#55E3A0"), erro=("#B50F2D", "#FF7A92"), aviso=("#8F5000", "#FFC15C"),
             visor=("#F0E3D3", "#0C0613")),
        dict(acento2=("#6A1FB0", "#C892FF"), acento2_h=("#531889", "#D4AAFF"), passo1=("#B8480A", "#FF9A3D"), passo2=("#6A1FB0", "#C892FF"),
             passo3=("#2F7D12", "#8FE35A"), passo4=("#A3174F", "#FF7AB0"), banda_a=("#722D06", "#804D1E"), banda_b=("#5D1B9B", "#8561AA")),
    ),
    "praia": (
        dict(fundo=("#FFF6E0", "#07222B"), cartao=("#FFFDF6", "#0D3441"), barra=("#FFF9EA", "#0A2A35"), borda=("#F0DCAA", "#1D5565"),
             texto=("#0B3140", "#FDF3DC"), suave=("#4F6D74", "#A9D2D8"), campo=("#FFFAEB", "#082A35"), acento=("#00718A", "#4FD8EF"),
             acento_h=("#00586C", "#76E1F3"), link=("#00718A", "#4FD8EF"), acento_suave=("#DBE9E7", "#1A5564"),
             sel_menu=("#E6EFEB", "#184E5D"), ok=("#0B7A5A", "#4EE3B0"), erro=("#B8132F", "#FF7F93"), aviso=("#8F5400", "#FFC65C"),
             visor=("#F0E7D3", "#05161C")),
        dict(acento2=("#C8374A", "#FF8190"), acento2_h=("#9C2B3A", "#FF9DA8"), passo1=("#00718A", "#4FD8EF"), passo2=("#C8374A", "#FF8190"),
             passo3=("#A35B00", "#FFC65C"), passo4=("#17803D", "#6EE79A"), banda_a=("#004656", "#286C78"), banda_b=("#B03041", "#B25A65")),
    ),
    "jornal": (
        dict(fundo=("#EBE4D1", "#14120E"), cartao=("#F8F3E4", "#201D16"), barra=("#F1EBDA", "#191712"), borda=("#CBBF9F", "#3A352A"),
             texto=("#1B1913", "#EFE7D2"), suave=("#5B5546", "#B9B09A"), campo=("#F2ECDA", "#181510"), acento=("#8E1B14", "#FF8A7D"),
             acento_h=("#6F1510", "#FFA49A"), link=("#8E1B14", "#FF8A7D"), acento_suave=("#E9D5C7", "#4D332B"),
             sel_menu=("#EDDDCF", "#442E26"), ok=("#2F6B2A", "#8FD68A"), erro=("#A3140F", "#FF8A80"), aviso=("#7A5200", "#F0C060"),
             visor=("#DDD6C4", "#0D0C09")),
        dict(acento2=("#2D4A6B", "#8FB6E0"), acento2_h=("#233A53", "#A8C6E7"), passo1=("#8E1B14", "#FF8A7D"), passo2=("#2D4A6B", "#8FB6E0"),
             passo3=("#6B5200", "#F0C060"), passo4=("#2F6B2A", "#8FD68A"), banda_a=("#58110C", "#80453E"), banda_b=("#28415E", "#5A738D")),
    ),
    "terminal": (
        dict(fundo=("#E9F1E4", "#040A05"), cartao=("#F7FBF4", "#09140B"), barra=("#EFF6EB", "#060E08"), borda=("#B9D0B4", "#14451D"),
             texto=("#0A2A0F", "#B8FFC7"), suave=("#3F6347", "#6FCF88"), campo=("#EEF6EA", "#060E07"), acento=("#0B6B1F", "#3DFF6E"),
             acento_h=("#095318", "#68FF8E"), link=("#0B6B1F", "#3DFF6E"), acento_suave=("#D6E7D6", "#13431F"),
             sel_menu=("#DFEDDF", "#113A1B"), ok=("#0B6B1F", "#3DFF6E"), erro=("#B0102A", "#FF6B7E"), aviso=("#8A5A00", "#FFC400"),
             visor=("#DBE3D6", "#030603")),
        dict(acento2=("#8A5A00", "#FFC400"), acento2_h=("#6C4600", "#FFD138"), passo1=("#0B6B1F", "#3DFF6E"), passo2=("#8A5A00", "#FFC400"),
             passo3=("#0A6B78", "#4FE3F0"), passo4=("#A3126B", "#FF7AD0"), banda_a=("#074213", "#1E8037"), banda_b=("#794F00", "#8F6E00")),
    ),
    "circo": (
        dict(fundo=("#FBECCB", "#1B0F1F"), cartao=("#FFFAF0", "#2B1830"), barra=("#FDF2DC", "#221327"), borda=("#E9CF94", "#4B2F55"),
             texto=("#2F1020", "#FBECCB"), suave=("#715048", "#CDB1C9"), campo=("#FFF4DD", "#20122A"), acento=("#B50F2A", "#FF6B80"),
             acento_h=("#8D0C21", "#FF8C9C"), link=("#B50F2A", "#FF6B80"), acento_suave=("#F5D9D4", "#552940"),
             sel_menu=("#F8E2DC", "#4D253D"), ok=("#1B7A45", "#5FE39A"), erro=("#B50F2A", "#FF7B8C"), aviso=("#8A5A00", "#FFC94D"),
             visor=("#ECDEBF", "#120A14")),
        dict(acento2=("#1F3F8F", "#8AAEFF"), acento2_h=("#183170", "#A4C0FF"), passo1=("#B50F2A", "#FF6B80"), passo2=("#1F3F8F", "#8AAEFF"),
             passo3=("#8A5A00", "#FFC94D"), passo4=("#1B7A45", "#5FE39A"), banda_a=("#70091A", "#803640"), banda_b=("#1B377E", "#5C74AA")),
    ),
}


def pares_de_contraste(paleta: dict) -> list:
    """[(descricao, cor do texto, cor do fundo, minimo)] que a paleta de um visual tem de cumprir (WCAG AA), nos dois modos (indice 0 claro, 1 escuro).
    O que se vai medir: o texto e o texto suave sobre o cartao e o fundo, os estados (ok, erro, aviso) e a ligacao sobre o cartao, e o
    texto dos botoes sobre o destaque e o magenta. Os cinzentos desativados e o que e so decoracao ficam de fora (como no WCAG)."""
    return [("texto/cartao", "texto", "cartao", 4.5), ("texto/fundo", "texto", "fundo", 4.5), ("suave/cartao", "suave", "cartao", 4.5),
            ("suave/fundo", "suave", "fundo", 4.5), ("ok/cartao", "ok", "cartao", 4.5), ("erro/cartao", "erro", "cartao", 4.5),
            ("aviso/cartao", "aviso", "cartao", 4.5), ("link/cartao", "link", "cartao", 4.5), ("texto/campo", "texto", "campo", 4.5)]
