"""Apoio comum aos testes de caracterizacao do motor.

Estes testes fixam o comportamento ATUAL (mesmo o que parece estranho); se um falhar depois de uma alteracao,
ou a alteracao e uma regressao, ou o comportamento mudou de proposito e o teste deve ser atualizado conscientemente.
Nunca importam app.py / ajuda.py / tema.py / widgets.py (puxam o Tkinter e o Windows).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from core import i18n

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(autouse=True)
def _lingua_pt():
    """A lingua do i18n e global: cada teste comeca em portugues e repoe a anterior no fim."""
    antes = i18n.atual()
    i18n.definir("pt")
    yield
    i18n.definir(antes)


@pytest.fixture(scope="session")
def fx():
    """fx("template_exemplo.pdf") -> caminho de um ficheiro de tests/fixtures (existe sempre)."""
    def _fx(nome: str) -> Path:
        p = FIXTURES / nome
        assert p.exists(), p
        return p
    return _fx


def textos_pdf(caminho) -> list:
    """Texto de cada pagina, tal como o PDFium o extrai (fecha tudo: no Windows um PDF aberto nao se apaga)."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(caminho))
    try:
        saida = []
        for i in range(len(doc)):
            pg = doc[i]
            tp = pg.get_textpage()
            saida.append(tp.get_text_range())
            tp.close()
            pg.close()
        return saida
    finally:
        doc.close()


def numeros_pdf(caminho, largura: int, fixos=("2099",)) -> list:
    """Por pagina, os numeros (>= `largura` algarismos) ordenados. `fixos` = numeros do proprio template que nao sao
    bilhetes (nos templates de exemplo, o ano 2099 da data do sorteio) e por isso se ignoram."""
    import re
    padrao = re.compile(rf"(?<!\d)\d{{{largura},}}(?!\d)")
    return [sorted(n for n in padrao.findall(t) if n not in fixos) for t in textos_pdf(caminho)]


def pdf_sintetico(destino: Path, linhas: list, tamanho=(400, 300)) -> Path:
    """PDF de 1 pagina com texto Helvetica-Bold 20 pt; linhas = [(x, y, texto, rotacao_graus)] (y para cima)."""
    from reportlab.pdfgen import canvas
    cv = canvas.Canvas(str(destino), pagesize=tamanho)
    for x, y, texto, rot in linhas:
        cv.saveState()
        cv.translate(x, y)
        cv.rotate(rot)
        cv.setFont("Helvetica-Bold", 20)
        cv.drawString(0, 0, texto)
        cv.restoreState()
    cv.showPage()
    cv.save()
    return destino


def erro_de(funcao, *args, **kw):
    """Chama `funcao` e devolve (tipo, chave, params) do ErroRifas levantado; falha se nao levantar nada."""
    try:
        funcao(*args, **kw)
    except Exception as e:  # noqa: BLE001 - queremos ver qualquer tipo
        return type(e).__name__, getattr(e, "chave", None), getattr(e, "params", None)
    raise AssertionError("nao levantou nenhum erro")
