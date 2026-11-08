"""O pedido do utilizador (campos de texto -> core.Trabalho) e o resumo que se mostra antes de gerar.

Extraido de app.py (App._trabalho e App._resumo) sem alterar o comportamento: a interface le os campos e mostra o
resultado; as regras ficam aqui, sem Tkinter. Os erros sao ErroRifas (chave + parametros), traduzidos so ao mostrar.
"""
from __future__ import annotations

import math
from pathlib import Path

from .i18n import t
from . import marca, series
from .motor import ErroRifas, InfoTemplate, Trabalho


def ler_inteiro(txt: str, campo: str) -> int:
    """int(txt.strip()), com o erro `int_invalido` (e o nome traduzido do campo) se nao for um inteiro.
    Aceita o que o int() do Python aceita: «+5», « 12 », «1_000»; recusa «1.0» e «»."""
    try:
        return int(txt.strip())
    except ValueError:
        raise ErroRifas("int_invalido", campo=campo)


def trabalho_de_campos(saida: str, nome: str, inicio: str, fim: str, max_ficheiro: str, digitos: str, modo: str,
                       prefixos: str = "", saltar: str = "", cor_serie: bool = False, cor_numeros: str = "") -> Trabalho:
    """Os 6 campos de texto + o modo («varios» | «unico») -> Trabalho. A ordem em que os campos se leem (e portanto qual
    o erro que aparece primeiro) e: De, Ate, Maximo por ficheiro (so no modo «varios»), Algarismos e, por fim, os prefixos
    (series) e os numeros a saltar (opcionais: vazios nao mudam nada)."""
    saida = saida.strip()
    tr = Trabalho(
        saida=Path(saida) if saida else Path(""),
        nome=nome.strip(),
        inicio=ler_inteiro(inicio, t("de")), fim=ler_inteiro(fim, t("ate")),
        por_ficheiro=ler_inteiro(max_ficheiro, t("max_ficheiro")) if modo == "varios" else None,
        digitos=ler_inteiro(digitos, t("algarismos")))
    tr.prefixos = series.ler_prefixos(prefixos)
    tr.saltar = series.ler_saltar(saltar)
    tr.cor_por_serie = bool(cor_serie)
    tr.cor_numeros = marca.cor_de_hex(cor_numeros)
    return tr


def rifas_por_pagina(disp, info: InfoTemplate | None) -> int:
    """Numeros por pagina de saida para o resumo: a folha escolhida, senao os bilhetes do template, senao 1."""
    return disp.n if disp is not None else (info.n_campos if info else 1)


def resumo_do_pedido(tr: Trabalho, n: int, tem_template: bool) -> tuple:
    """(texto, aviso) do resumo. `aviso` = True se o texto e um aviso (a interface pinta-o de outra cor).
    Levanta ErroRifas (err_intervalo, err_max) - a interface mostra o erro como aviso.
    Nao chama core.validar (por isso, p.ex., inicio < 0 nao e recusado aqui)."""
    if tr.fim < tr.inicio:
        raise ErroRifas("err_intervalo")
    por_serie = len(series.numeros(tr.inicio, tr.fim, tr.saltar)) if tr.saltar else tr.fim - tr.inicio + 1
    if por_serie < 1:
        raise ErroRifas("err_intervalo")                               # os numeros a saltar comem o intervalo todo
    n_series = max(1, len(tr.prefixos))
    qtd = por_serie * n_series
    paginas = math.ceil(por_serie / n) * n_series
    if tr.por_ficheiro is None:
        if n_series > 1:                                               # um PDF por serie
            return t("resumo_varios", qtd=qtd, ficheiros=n_series, paginas=paginas), False
        return t("resumo_unico", qtd=qtd, paginas=paginas), False
    if tr.por_ficheiro < 1:
        raise ErroRifas("err_max")
    txt = t("resumo_varios", qtd=qtd, ficheiros=math.ceil(por_serie / tr.por_ficheiro) * n_series, paginas=paginas)
    if tem_template and tr.por_ficheiro % n:
        return t("resumo_multiplo", n=n), True
    return txt, False


def previa_png(prep, tr: Trabalho, dpi: int = 200) -> bytes:
    """O PNG da pre-visualizacao do pedido `tr` (1.a pagina): com o prefixo e a cor da 1.a serie, os numeros saltados e o logotipo.
    E o que a app Windows mostra no visor; a webapp faz o mesmo em PDF (trabalhos.previa)."""
    from .motor import pagina_previa
    return pagina_previa(prep, tr.inicio, tr.digitos, tr.fim, dpi, tr.prefixos[0] if tr.prefixos else "",
                         series.cor_da_serie(tr, 0) or tr.cor_numeros, tr.saltar, tr.marca)
