"""O pedido do utilizador (campos de texto -> core.Trabalho) e o resumo que se mostra antes de gerar.

Extraido de app.py (App._trabalho e App._resumo) sem alterar o comportamento: a interface le os campos e mostra o
resultado; as regras ficam aqui, sem Tkinter. Os erros sao ErroRifas (chave + parametros), traduzidos so ao mostrar.
"""
from __future__ import annotations

import math
from pathlib import Path

from .i18n import t
from .motor import ErroRifas, InfoTemplate, Trabalho


def ler_inteiro(txt: str, campo: str) -> int:
    """int(txt.strip()), com o erro `int_invalido` (e o nome traduzido do campo) se nao for um inteiro.
    Aceita o que o int() do Python aceita: «+5», « 12 », «1_000»; recusa «1.0» e «»."""
    try:
        return int(txt.strip())
    except ValueError:
        raise ErroRifas("int_invalido", campo=campo)


def trabalho_de_campos(saida: str, nome: str, inicio: str, fim: str, max_ficheiro: str, digitos: str, modo: str) -> Trabalho:
    """Os 6 campos de texto + o modo («varios» | «unico») -> Trabalho. A ordem em que os campos se leem (e portanto qual
    o erro que aparece primeiro) e: De, Ate, Maximo por ficheiro (so no modo «varios»), Algarismos."""
    saida = saida.strip()
    return Trabalho(
        saida=Path(saida) if saida else Path(""),
        nome=nome.strip(),
        inicio=ler_inteiro(inicio, t("de")), fim=ler_inteiro(fim, t("ate")),
        por_ficheiro=ler_inteiro(max_ficheiro, t("max_ficheiro")) if modo == "varios" else None,
        digitos=ler_inteiro(digitos, t("algarismos")))


def rifas_por_pagina(disp, info: InfoTemplate | None) -> int:
    """Numeros por pagina de saida para o resumo: a folha escolhida, senao os bilhetes do template, senao 1."""
    return disp.n if disp is not None else (info.n_campos if info else 1)


def resumo_do_pedido(tr: Trabalho, n: int, tem_template: bool) -> tuple:
    """(texto, aviso) do resumo. `aviso` = True se o texto e um aviso (a interface pinta-o de outra cor).
    Levanta ErroRifas (err_intervalo, err_max) - a interface mostra o erro como aviso.
    Nao chama core.validar (por isso, p.ex., inicio < 0 nao e recusado aqui)."""
    if tr.fim < tr.inicio:
        raise ErroRifas("err_intervalo")
    qtd = tr.fim - tr.inicio + 1
    paginas = math.ceil(qtd / n)
    if tr.por_ficheiro is None:
        return t("resumo_unico", qtd=qtd, paginas=paginas), False
    if tr.por_ficheiro < 1:
        raise ErroRifas("err_max")
    txt = t("resumo_varios", qtd=qtd, ficheiros=math.ceil(qtd / tr.por_ficheiro), paginas=paginas)
    if tem_template and tr.por_ficheiro % n:
        return t("resumo_multiplo", n=n), True
    return txt, False
