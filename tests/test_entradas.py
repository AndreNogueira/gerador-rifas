"""Entradas por bytes (upload): validacao do tipo real, ficheiros temporarios, preparar_de_bytes e pdf_da_previa."""
import io
from pathlib import Path

import pytest
from pypdf import PdfReader

import core
from core import entradas
from conftest import erro_de, textos_pdf


def _bytes(fx, nome):
    return fx(nome).read_bytes()


# ------------------------------------------------------------------ detetar_tipo / nome_de_upload
def test_detetar_tipo_pelos_bytes(fx):
    assert entradas.detetar_tipo(_bytes(fx, "template_exemplo.pdf")) == "pdf"
    assert entradas.detetar_tipo(_bytes(fx, "digitos_exemplo.png")) == "png"
    assert entradas.detetar_tipo(b"\xff\xd8\xff\xe0\x00\x10JFIF") == "jpg"
    for mau in (b"", b"hello", b" %PDF-1.4", b"MZ\x90\x00", b"<html>", b"GIF89a", b"%PD"):
        assert entradas.detetar_tipo(mau) is None, mau


@pytest.mark.parametrize("nome, tipo, esperado", [
    ("Rifa Natal.pdf", "pdf", "Rifa Natal.pdf"),
    ("../../etc/passwd", "pdf", "passwd.pdf"),
    ("..\\..\\Windows\\x.exe", "png", "x.png"),                  # a extensao e a do tipo REAL, nao a do cliente
    ("C:\\x\\y.pdf", "pdf", "y.pdf"),
    ("a<b>c:d|e?.pdf", "pdf", "abcde.pdf"),
    ("", "pdf", "ficheiro.pdf"),
    ("...", "jpg", "ficheiro.jpg"),
    ("nome.tar.gz", "pdf", "nome.tar.pdf"),
])
def test_nome_de_upload(nome, tipo, esperado):
    assert entradas.nome_de_upload(nome, tipo) == esperado


def test_nome_de_upload_por_defeito():
    assert entradas.nome_de_upload("", "png", "algarismos") == "algarismos.png"


# ------------------------------------------------------------------ ficheiro_temporario
def test_ficheiro_temporario_cria_e_apaga(tmp_path):
    with entradas.ficheiro_temporario(b"abc", "x.pdf", pasta=tmp_path) as f:
        assert f.read_bytes() == b"abc" and f.name == "x.pdf" and f.parent.parent == tmp_path
        pasta = f.parent
    assert not pasta.exists() and list(tmp_path.iterdir()) == []


def test_ficheiro_temporario_apaga_mesmo_com_erro(tmp_path):
    with pytest.raises(RuntimeError):
        with entradas.ficheiro_temporario(b"abc", "x.pdf", pasta=tmp_path):
            raise RuntimeError
    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------------------------ preparar_de_bytes
@pytest.mark.parametrize("alg", ["digitos_exemplo.pdf", "digitos_exemplo.png"])
def test_preparar_de_bytes_igual_a_preparar(tmp_path, fx, alg):
    por_bytes = entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), _bytes(fx, alg), "Meu template.pdf", "digitos")
    por_caminho = core.preparar(fx("template_exemplo.pdf"), fx(alg))
    assert por_bytes.info.slots == por_caminho.info.slots and por_bytes.por_pagina == 5
    assert por_bytes.template == Path("Meu template.pdf") and por_bytes.info.caminho == Path("Meu template.pdf")   # sem caminhos temporarios
    r1 = core.gerar(core.Trabalho(tmp_path / "a", "T", 1, 12), por_bytes)
    r2 = core.gerar(core.Trabalho(tmp_path / "b", "T", 1, 12), por_caminho)
    assert r1[0].ok and (r1[0].paginas, r1[0].erros) == (r2[0].paginas, r2[0].erros)
    from conftest import numeros_pdf
    assert numeros_pdf(r1[0].caminho, 4) == numeros_pdf(r2[0].caminho, 4)


def test_preparar_de_bytes_o_nome_da_descricao_e_o_seguro(fx):
    prep = entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), _bytes(fx, "digitos_exemplo.pdf"), "t.pdf", "../../algs.exe")
    assert prep.descricoes == ["letra «BitstreamVeraSans-Bold» extraída de algs.pdf"]


def test_preparar_de_bytes_uma_rifa_e_folha(fx):
    prep = entradas.preparar_de_bytes(_bytes(fx, "template_exemplo_1_rifa.pdf"), _bytes(fx, "digitos_exemplo.pdf"))
    assert prep.info.n_campos == 1 and prep.com_folha("A4", 5).por_pagina == 5


def test_preparar_de_bytes_log_estruturado(fx):
    logs = []
    entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), _bytes(fx, "digitos_exemplo.png"), log=logs.append)
    assert [m.chave for m in logs] == ["log_template", "log_imagem_ok", "info_dpi"]


def test_preparar_de_bytes_nomes_iguais_nao_se_sobrepoem(fx):
    prep = entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), _bytes(fx, "digitos_exemplo.pdf"), "x.pdf", "x")
    assert prep.por_pagina == 5 and prep.descricoes == ["letra «BitstreamVeraSans-Bold» extraída de alg_x.pdf"]


@pytest.mark.parametrize("template", [b"", b"nao e pdf", b"\x89PNG\r\n\x1a\nxxxx", b"MZ\x90\x00"])
def test_preparar_de_bytes_template_que_nao_e_pdf(fx, template):
    e = erro_de(entradas.preparar_de_bytes, template, _bytes(fx, "digitos_exemplo.pdf"))
    assert e[:2] == ("ErroRifas", "err_abrir_template")


def test_preparar_de_bytes_template_pdf_estragado(fx):
    e = erro_de(entradas.preparar_de_bytes, b"%PDF-1.4 lixo lixo", _bytes(fx, "digitos_exemplo.pdf"))
    assert e[:2] == ("ErroRifas", "err_abrir_template")


def test_preparar_de_bytes_algarismos_de_tipo_errado(fx):
    with pytest.raises(core.ErroAlgarismos) as e:
        entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), b"isto e texto", "t.pdf", "alg.png")      # o nome mente: conta o conteudo
    assert e.value.chave == "err_formato" and e.value.info.n_campos == 5 and e.value.info.caminho == Path("t.pdf")


def test_preparar_de_bytes_sem_algarismos(fx):
    with pytest.raises(core.ErroAlgarismos) as e:
        entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), None)
    assert e.value.chave == "err_sem_ficheiro_algarismos" and e.value.info.caminho == Path("template.pdf")


def test_preparar_de_bytes_png_estragado(fx):
    with pytest.raises(core.ErroAlgarismos) as e:
        entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), b"\x89PNG\r\n\x1a\n" + b"x" * 20, "t.pdf", "a.png")
    assert e.value.chave == "err_abrir_ficheiro"


def test_preparar_de_bytes_nao_deixa_temporarios(fx, monkeypatch, tmp_path):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.setenv("TMP", str(tmp_path))
    import tempfile
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    entradas.preparar_de_bytes(_bytes(fx, "template_exemplo.pdf"), _bytes(fx, "digitos_exemplo.pdf"))
    with pytest.raises(core.ErroRifas):
        entradas.preparar_de_bytes(b"lixo", _bytes(fx, "digitos_exemplo.pdf"))
    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------------------------ pdf_da_previa
def test_pdf_da_previa_e_um_pdf_de_1_pagina_com_os_primeiros_numeros(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    pdf = core.pdf_da_previa(prep, 7, 4)
    assert pdf[:5] == b"%PDF-"
    rd = PdfReader(io.BytesIO(pdf))
    assert len(rd.pages) == 1 and [float(v) for v in rd.pages[0].mediabox] == [0.0, 0.0, 595.0, 842.0]
    f = tmp_path / "previa.pdf"
    f.write_bytes(pdf)
    texto = textos_pdf(f)[0]
    for n in range(7, 12):
        assert texto.count(f"{n:04d}") == 2


def test_pdf_da_previa_com_fim_e_folha(tmp_path, fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.png"))
    f = tmp_path / "p.pdf"
    f.write_bytes(core.pdf_da_previa(prep, 1, 3, fim=2))                  # so 2 numeros: os outros bilhetes ficam sem numero
    assert "003" not in textos_pdf(f)[0]
    p1 = core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf")).com_folha("A4", 5)
    rd = PdfReader(io.BytesIO(core.pdf_da_previa(p1, 1, 4)))
    assert [round(float(v), 1) for v in rd.pages[0].mediabox] == [0.0, 0.0, 595.3, 841.9]


def test_pagina_previa_continua_igual_a_renderizar_o_pdf(fx):
    prep = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    assert core.pagina_previa(prep, 1, 4, dpi=50) == core.png_de_pagina(core.pdf_da_previa(prep, 1, 4), 50)


# ------------------------------------------------------------------ analisar_template_de_bytes (a webapp mostra o que leu antes dos algarismos)
def test_analisar_template_de_bytes_devolve_a_info(fx):
    info = entradas.analisar_template_de_bytes(_bytes(fx, "template_exemplo.pdf"), "Rifa Natal.pdf")
    assert info.caminho == Path("Rifa Natal.pdf")                 # nome seguro, nunca um caminho do cliente
    esperado = core.analisar_template(fx("template_exemplo.pdf"))
    assert info.n_campos > 0                                      # leu os numeros de exemplo
    campos = ("n_campos", "n_paginas", "primeiro", "ultimo", "largura", "altura", "slots")
    assert [getattr(info, c) for c in campos] == [getattr(esperado, c) for c in campos]


def test_analisar_template_de_bytes_nome_perigoso(fx):
    info = entradas.analisar_template_de_bytes(_bytes(fx, "template_exemplo.pdf"), "../../etc/passwd")
    assert info.caminho == Path("passwd.pdf")


@pytest.mark.parametrize("mau", [b"", b"hello", b"\x89PNG\r\n\x1a\n", b" %PDF-1.4"])
def test_analisar_template_de_bytes_so_aceita_pdf(mau):
    with pytest.raises(core.ErroRifas) as e:
        entradas.analisar_template_de_bytes(mau, "x.pdf")
    assert e.value.chave == "err_abrir_template"
    assert "«x.pdf»" in e.value.em("pt")                           # o erro nomeia o ficheiro (sem texto em ingles misturado)
    assert "not a PDF" not in e.value.em("pt")
