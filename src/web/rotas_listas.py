"""M2: exportar a lista de bilhetes (CSV) e a folha de controlo de vendas (PDF) do pedido que esta no formulario.

Nao precisam de template nem de sessao: saem so dos campos (de, ate, algarismos, prefixos, saltos), como a pre-visualizacao do
resumo. Os mesmos limites do resto (teto de numeros, pedidos por minuto) valem aqui, e nada fica guardado no servidor.
"""
from __future__ import annotations

import urllib.parse

import core
from core import controlo, i18n, series
from fastapi import APIRouter, Depends, Response

from . import config
from .modelos import Campos, ErroApi
from .rotas import leve, lingua
from .sessoes import trabalho_dos_campos

router = APIRouter(prefix="/api/exportar", tags=["exportar"])


def _bilhetes(c: Campos, lg: str) -> tuple:
    """(Trabalho, [(serie, numero)]). Os erros do motor saem como aviso (422), como ao gerar."""
    try:
        with i18n.com_lingua(lg):
            tr = trabalho_dos_campos(c)
            if not 1 <= tr.digitos <= core.MAX_DIGITOS or tr.inicio < 0 or tr.fim < tr.inicio:
                raise core.ErroRifas("conf_numeros")
            series.validar_extras(tr)
            if series.contar(tr) > config.max_numeros():
                raise core.ErroRifas("web_demasiados", max=config.max_numeros())
            return tr, series.bilhetes(tr)
    except core.ErroRifas as e:
        raise ErroApi(422, e.em(lg), "aviso") from None


def _anexo(dados: bytes, tipo: str, nome: str) -> Response:
    quoted = urllib.parse.quote(nome)
    return Response(dados, media_type=tipo, headers={
        "Content-Disposition": f"attachment; filename*=UTF-8''{quoted}",
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.post("/lista.csv", dependencies=[Depends(leve)])
def lista_csv(campos: Campos, lg: str = Depends(lingua)) -> Response:
    """Um CSV (UTF-8, separado por «;») com um bilhete por linha e as colunas Nome, Contacto e Pago em branco."""
    tr, bilhetes = _bilhetes(campos, lg)
    nome, dados = controlo.exportar_csv(tr, bilhetes, lg)
    return _anexo(dados, "text/csv; charset=utf-8", nome)


@router.post("/controlo.pdf", dependencies=[Depends(leve)])
def controlo_pdf(campos: Campos, lg: str = Depends(lingua)) -> Response:
    """A folha de controlo de vendas (PDF A4, 36 bilhetes por pagina) para imprimir e preencher."""
    tr, bilhetes = _bilhetes(campos, lg)
    nome, dados = controlo.exportar_folha(tr, bilhetes, lg)
    return _anexo(dados, "application/pdf", nome)
