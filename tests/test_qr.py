"""M6: QR de verificacao por bilhete: o codigo assinado (sem base de dados) e o desenho vetorial no PDF."""
import importlib.util
import io
import re

import pytest
from pypdf import PdfReader

import core
from core import qr
from conftest import numeros_pdf

# o segno so e preciso no servidor (grupo `web`): o venv 3.13 da app Windows nao o tem e salta o que o usa
requer_segno = pytest.mark.skipif(importlib.util.find_spec("segno") is None, reason="precisa do `segno` (uv sync)")
CHAVE = b"uma-chave-so-do-servidor-1234567890"
BASE = "https://rifas.exemplo.pt"


# ------------------------------------------------------------------ o codigo
def test_codigo_ida_e_volta_so_com_a_mesma_chave():
    c = qr.codigo(CHAVE, "Rifa Natal", "A-", "0042")
    assert re.fullmatch(r"[A-Z2-7]+\.[A-Z2-7]+", c)                                       # so A-Z, 2-7 e o ponto: cabe no modo alfanumerico
    assert qr.verificar(CHAVE, c) == ("Rifa Natal", "A-", "0042")
    assert qr.verificar(CHAVE, c.lower()) == ("Rifa Natal", "A-", "0042")                  # o endereco pode vir em minusculas
    assert qr.verificar(b"outra-chave-completamente-diferente", c) is None
    assert qr.codigo(CHAVE, "Rifa Natal", "A-", "0042") == c                               # determinista


def test_um_codigo_alterado_ou_lixo_nunca_valida_nem_levanta():
    c = qr.codigo(CHAVE, "Rifa", "", "0001")
    parte, assinatura = c.split(".")
    maus = [c[:-1] + ("A" if c[-1] != "A" else "B"),                                       # assinatura mexida
            qr.codigo(CHAVE, "Rifa", "", "0002").split(".")[0] + "." + assinatura,         # outro numero com a assinatura do 1
            parte, "." + assinatura, parte + ".", "", ".", "!!!.???", "A" * 500, "\x00\x01.\x02", parte + "." + assinatura + "." + assinatura,
            "MFRGG===.AAAA"]
    for m in maus:
        assert qr.verificar(CHAVE, m) is None, m


def test_so_se_aceita_o_que_o_servico_emitiu_mesmo_com_a_chave_certa():
    # um payload mal formado, mesmo assinado, nao e um bilhete (o formato e estrito)
    for evento, serie, numero in (("x", "9", "0001"), ("x", "A", "abc"), ("x" * 40, "A", "1"), ("", "A|B", "1")):
        payload = "|".join((evento, serie, numero)).encode()
        codigo = f"{qr._b32(payload)}.{qr._assinar(CHAVE, payload)}"
        assert qr.verificar(CHAVE, codigo) is None, (evento, serie, numero)


def test_evento_limpo_deixa_so_ascii_seguro_ate_16():
    assert qr.evento_limpo("Rifa de Natal 2026!") == "Rifa de Natal 20"
    assert qr.evento_limpo("Ação Ñandú <b>x</b>") == "Ao and bxb"
    assert qr.evento_limpo("  a   b  ") == "a b" and qr.evento_limpo("日本語") == ""


@requer_segno
def test_o_url_vai_em_maiusculas_e_o_qr_e_pequeno():
    q = qr.Qr(BASE, CHAVE, "Rifa Natal")
    u = qr.url(q, "A-", "0001")
    assert u == u.upper() and u.startswith("HTTPS://RIFAS.EXEMPLO.PT/V/") and len(u) < 100
    m = qr.modulos(u)
    assert len(m) == len(m[0]) and len(m) <= 37                                          # versao <= 5 no modo alfanumerico
    assert qr.modulos(u) == m                                                            # determinista (mascara fixa)
    assert qr.modulos(qr.url(q, "A-", "0002")) != m


# ------------------------------------------------------------------ o desenho
@pytest.fixture(scope="module")
def prep1(fx):
    return core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf")).com_folha("A4", 5)


@pytest.fixture(scope="module")
def prep5(fx):
    return core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))


def _gerar(tmp_path, prep, **kw):
    r = core.gerar(core.Trabalho(tmp_path, "R", 1, 5, **kw), prep)
    assert r[0].ok, r[0].erros
    return r[0].caminho


def _conteudo(caminho) -> str:
    return PdfReader(str(caminho)).pages[0].get_contents().get_data().decode("latin-1")


@requer_segno
@pytest.mark.parametrize("posicao", qr.POSICOES)
def test_cada_modulo_do_qr_esta_onde_a_matriz_diz(tmp_path, prep1, posicao):
    """Renderiza a pagina com o PDFium e confirma, modulo a modulo, que o que se ve e a matriz do QR do 1.o bilhete."""
    import pypdfium2 as pdfium
    q = qr.Qr(BASE, CHAVE, "Rifa", posicao, 30)
    pdf = _gerar(tmp_path / posicao, prep1, qr=q)
    d = prep1.disp
    x, y, _ = d.posicoes[0]                                                              # canto superior esquerdo da 1.a rifa (y para baixo)
    ch, cw = d.celula.height, d.celula.width
    lado = min(ch * q.tamanho / 100, cw * 0.45)
    esquerda = x + 5 if posicao in ("se", "ie") else x + cw - 5 - lado
    topo = y + 5 if posicao in ("se", "sd") else y + ch - 5 - lado
    matriz = qr.modulos(qr.url(q, "", "0001"))
    n, silencio = len(matriz), 3
    m = lado / (n + 2 * silencio)
    escala = 8.0
    doc = pdfium.PdfDocument(str(pdf))
    try:
        im = doc[0].render(scale=escala).to_pil().convert("L")
    finally:
        doc.close()
    erradas = 0
    for r in range(n):
        for c in range(n):
            px = (esquerda + (silencio + c + 0.5) * m) * escala
            py = (topo + (silencio + r + 0.5) * m) * escala
            escuro = im.getpixel((round(px), round(py))) < 128
            erradas += escuro != matriz[r][c]
    assert erradas == 0, f"{erradas} modulos fora do sitio"


@requer_segno
def test_cada_bilhete_tem_o_seu_qr_e_a_verificacao_dos_pdfs_continua_a_passar(tmp_path, prep1):
    q = qr.Qr(BASE, CHAVE, "Rifa")
    pdf = _gerar(tmp_path, prep1, qr=q, prefixos=("A-",))
    assert numeros_pdf(pdf, 4)[0] == sorted(f"{n:04d}" for n in range(1, 6) for _ in range(2))       # o QR nao mete algarismos no texto da pagina
    conteudo = _conteudo(pdf)
    assert conteudo.count("1 g ") >= 5                                                  # uma zona de silencio branca por bilhete
    sem = _conteudo(_gerar(tmp_path / "sem", prep1, prefixos=("A-",)))
    assert len(conteudo) > len(sem) + 5 * 2000                                          # e cinco QR a mais no desenho


def test_sem_qr_ou_em_template_de_varias_rifas_nada_muda(tmp_path, prep1, prep5):
    a, b = _gerar(tmp_path / "a", prep1), _gerar(tmp_path / "b", prep1, qr=None)
    assert _conteudo(a) == _conteudo(b)
    c = _gerar(tmp_path / "c", prep5, qr=qr.Qr(BASE, CHAVE, "Rifa"))
    assert _conteudo(c) == _conteudo(_gerar(tmp_path / "d", prep5))                     # templates de varias rifas ignoram o QR


@requer_segno
def test_previa_com_qr(prep1):
    pdf = core.pdf_da_previa(prep1, 1, 4, qr=qr.Qr(BASE, CHAVE, "Rifa"))
    assert PdfReader(io.BytesIO(pdf)).pages[0].get_contents().get_data().count(b"1 g ") >= 5
