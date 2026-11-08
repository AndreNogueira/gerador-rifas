"""Escolha da folha pelo utilizador (modo «uma so rifa no template»): papel, margem e rifas por folha em texto.

Extraido de app.py (App._recalcular_folha, _render_folha e _prep_atual) sem alterar o comportamento. As regras que
so existiam na interface (margem inteira entre 0 e 50 mm, «rifas por folha» vazio = maximo, < 1 invalido, aviso quando se
pede mais do que cabe) ficam aqui, sem Tkinter.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .i18n import t
from .motor import (AVISO_POR_PAGINA, MM, Disposicao, ErroRifas, InfoTemplate, Preparado, disposicao_da_folha)

MARGEM_MAX_MM = 50
MARGEM_MIN_MARCAS_MM = 3      # as marcas de corte precisam de espaco na margem (traco de 3,5 mm a 1 mm da rifa)


@dataclass
class EscolhaFolha:
    disp: Disposicao
    acima: bool            # o utilizador pediu mais rifas por folha do que cabem (ficou no maximo)


def tem_folha(info: InfoTemplate | None) -> bool:
    """A escolha da folha so existe quando o template tem uma so rifa (e se conhece o tamanho dela)."""
    return not (info is None or info.n_campos != 1 or info.celula is None)


def ler_margem(txt: str) -> int:
    """Margem em mm: inteiro de 0 a 50, senao `int_invalido` (campo «Margem»)."""
    try:
        m = int(txt.strip())
        if not 0 <= m <= MARGEM_MAX_MM:
            raise ValueError
    except ValueError:
        raise ErroRifas("int_invalido", campo=t("lay_margem"))
    return m


def escolher_folha(info: InfoTemplate, papel: str, margem_txt: str, porfolha_txt: str, marcas: bool = False) -> EscolhaFolha:
    """Disposicao da folha para os valores escritos. `porfolha_txt` vazio = o maximo que couber; um valor acima do maximo
    fica no maximo (e `acima` = True). `marcas`: marcas de corte nas margens (pedem pelo menos 3 mm de margem).
    Levanta ErroRifas (int_invalido, err_rifa_grande, err_folha_varias, err_marcas)."""
    m = ler_margem(margem_txt)
    if marcas and m < MARGEM_MIN_MARCAS_MM:
        raise ErroRifas("err_marcas", min=MARGEM_MIN_MARCAS_MM)
    base = disposicao_da_folha(info, papel, m)
    txt = porfolha_txt.strip()
    try:
        pedido = base.maximo if not txt else int(txt)
        if pedido < 1:
            raise ValueError
    except ValueError:
        raise ErroRifas("int_invalido", campo=t("lay_por_folha"))
    return EscolhaFolha(replace(disposicao_da_folha(info, papel, m, pedido), marcas=marcas), pedido > base.maximo)


def texto_da_folha(disp: Disposicao, acima: bool) -> tuple:
    """(texto, aviso) com a descricao da folha escolhida; `aviso` = True se deve aparecer como aviso."""
    txt = t("lay_resultado", w=f"{disp.celula.width / MM:.0f}", h=f"{disp.celula.height / MM:.0f}", n=disp.n,
            papel=disp.papel, max=disp.maximo)
    if disp.origem != "pagina":
        txt += t("lay_recortada")
    if disp.rodadas:
        txt += t("lay_rodadas", r=disp.rodadas)
    aviso = False
    if acima:
        txt += "\n" + t("lay_acima", max=disp.maximo)
        aviso = True
    if disp.n > AVISO_POR_PAGINA:
        txt += "\n" + t("aviso_muitas", n=disp.n)
        aviso = True
    return txt, aviso


def preparado_com_folha(prep: Preparado | None, disp: Disposicao | None, erro_folha: ErroRifas | None = None) -> Preparado | None:
    """O Preparado a usar para gerar. Template de varias rifas (ou nenhum): o proprio. Uma so rifa: o Preparado com a folha
    escolhida; se nao ha folha valida levanta o erro dessa folha (`erro_folha`) ou `erro_inesperado`."""
    if prep is None or prep.info.n_campos != 1:
        return prep
    if disp is None:
        raise erro_folha if erro_folha is not None else ErroRifas("erro_inesperado", erro="?")
    return replace(prep, disp=disp)
