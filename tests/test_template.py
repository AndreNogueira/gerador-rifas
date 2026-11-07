"""Caracterizacao: leitura do template (analisar_template), criar_fundo, preparar e os erros de ficheiros."""
import io

import pytest

import core
from core import pdftexto
from conftest import erro_de, pdf_sintetico


# ------------------------------------------------------------------ analisar_template (exemplos da app)
def test_template_5_por_pagina(fx):
    i = core.analisar_template(fx("template_exemplo.pdf"))
    assert (i.n_campos, i.n_paginas, i.primeiro, i.ultimo) == (5, 1, "0001", "0005")
    assert i.fontes == ["BitstreamVeraSans-Bold"]
    assert (i.largura, i.altura, i.caixa) == (595.0, 842.0, (0.0, 0.0, 595.0, 842.0))
    assert i.n_numeros == {1: 2, 2: 2, 3: 2, 4: 2, 5: 2}               # talao + parte principal
    assert i.celula is None and i.celula_origem == "pagina"            # so se calcula com 1 rifa
    assert len(i.slots) == 10
    assert [s.campo for s in i.slots] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]    # ordenados por campo, depois y, depois x


def test_slots_do_primeiro_bilhete(fx):
    s1 = core.analisar_template(fx("template_exemplo.pdf")).slots[:2]
    assert [(s.rot, s.tamanho, s.texto) for s in s1] == [(0, 20.0, "0001"), (90, 19.0, "0001")]
    assert s1[0].origem == pytest.approx((453.168, 69.0))
    assert s1[1].origem == pytest.approx((67.0, 126.0))
    assert s1[0].cor == pytest.approx((0.93, 0.47, 0.08))
    assert s1[0].avanco == pytest.approx(55.664, abs=1e-3)
    assert s1[0].fonte == "BitstreamVeraSans-Bold" and not s1[0].vertical and s1[1].vertical


def test_template_de_uma_rifa_pagina_inteira(fx):
    i = core.analisar_template(fx("template_exemplo_1_rifa.pdf"))
    assert (i.n_campos, i.largura, i.altura, i.n_numeros) == (1, 539.0, 156.0, {1: 2})
    assert i.celula == core.Ret(0.0, 0.0, 539.0, 156.0) and i.celula_origem == "pagina"


def test_template_de_uma_rifa_numa_pagina_a4_usa_a_zona_desenhada(fx):
    i = core.analisar_template(fx("template_exemplo_1_rifa_a4.pdf"))
    assert (i.largura, i.altura) == (595.0, 842.0)
    assert i.celula_origem == "conteudo"
    assert (i.celula.x0, i.celula.y0, i.celula.x1, i.celula.y1) == pytest.approx((27.5, 192.5, 567.5, 349.5), abs=1e-6)


@pytest.mark.parametrize("semente, n_campos, fonte, ultimo, rotacoes", [
    (1, 2, "SegoeUI", "0002", [0, 90]),
    (3, 8, "SegoeUI", "0008", [0]),
    (5, 24, "Tahoma", "0024", [0, 270]),
    (9, 12, "Tahoma", "00000012", [0, 270]),          # 8 algarismos
    (10, 1, "Candara", "0001", [0, 90]),
])
def test_templates_aleatorios(fx, semente, n_campos, fonte, ultimo, rotacoes):
    i = core.analisar_template(fx(f"aleatorio_s{semente}.pdf"))
    assert (i.n_campos, i.fontes, i.ultimo) == (n_campos, [fonte], ultimo)
    assert len(i.slots) == 2 * n_campos
    assert sorted({s.rot for s in i.slots}) == rotacoes
    assert (i.celula is not None) == (n_campos == 1)


# ------------------------------------------------------------------ analisar_template: erros e casos limite
def test_erros_ao_abrir_template(tmp_path, fx):
    (tmp_path / "x.pdf").write_text("isto nao e um PDF")
    assert erro_de(core.analisar_template, tmp_path / "x.pdf")[:2] == ("ErroRifas", "err_abrir_template")
    assert erro_de(core.analisar_template, tmp_path / "nao_existe.pdf")[:2] == ("ErroRifas", "err_abrir_template")
    assert erro_de(core.analisar_template, fx("digitos_exemplo.png"))[:2] == ("ErroRifas", "err_abrir_template")


def test_template_sem_numeros_de_exemplo(tmp_path, fx):
    # o ficheiro dos algarismos usado por engano como template: nenhum numero a comecar por 0
    assert erro_de(core.analisar_template, fx("digitos_exemplo.pdf")) == ("ErroRifas", "err_sem_exemplos", {"achados": "0123456789"})
    p = pdf_sintetico(tmp_path / "d.pdf", [(20, 200, "hello", 0)])
    assert erro_de(core.analisar_template, p) == ("ErroRifas", "err_sem_exemplos", {"achados": "nenhum"})


def test_numeros_so_contam_se_a_sequencia_e_2x_cada(tmp_path):
    # 0001 duas vezes e 0002 so uma: a sequencia parte-se -> erro
    p = pdf_sintetico(tmp_path / "c.pdf", [(20, 200, "0001", 0), (20, 100, "0001", 0), (200, 200, "0002", 0)])
    assert erro_de(core.analisar_template, p) == ("ErroRifas", "err_sequencia", {"numero": "0002", "vezes": 1})
    # 0001 tres vezes: nao e nem 1x nem 2x
    p = pdf_sintetico(tmp_path / "h.pdf", [(20, 200, "0001", 0), (20, 100, "0001", 0), (20, 50, "0001", 0)])
    assert erro_de(core.analisar_template, p) == ("ErroRifas", "err_sem_exemplos", {"achados": "0001"})


def test_uma_rifa_com_o_numero_escrito_uma_so_vez(tmp_path):
    p = pdf_sintetico(tmp_path / "b.pdf", [(20, 200, "0001", 0)])
    i = core.analisar_template(p)
    assert (i.n_campos, i.n_numeros) == (1, {1: 1})
    assert i.celula_origem == "conteudo"                # a pagina quase toda em branco: mede-se a tinta
    assert i.celula.x0 == pytest.approx(19.0) and i.celula.y0 == pytest.approx(84.0, abs=1.0)


def test_numeros_fixos_do_template_sao_ignorados(tmp_path):
    # um telefone (0912345678) e outro numero que nao e da sequencia 1..N nao sao tocados
    p = pdf_sintetico(tmp_path / "e.pdf", [(20, 250, "0912345678", 0), (20, 100, "0001", 0), (20, 50, "0001", 0)])
    i = core.analisar_template(p)
    assert (i.n_campos, i.primeiro, i.ultimo) == (1, "0001", "0001")
    assert all(s.texto == "0001" for s in i.slots)
    p = pdf_sintetico(tmp_path / "f.pdf", [(20, 200, "0001", 0), (20, 100, "0001", 0), (200, 200, "0003", 0), (200, 100, "0003", 0)])
    assert core.analisar_template(p).n_campos == 1       # o 0003 (sem o 0002) fica de fora


def test_mais_algarismos_e_menos_algarismos(tmp_path):
    p = pdf_sintetico(tmp_path / "g.pdf", [(20, 200, "00001", 0), (20, 100, "00001", 0), (200, 200, "00002", 0), (200, 100, "00002", 0)])
    i = core.analisar_template(p)
    assert (i.n_campos, i.primeiro, i.ultimo) == (2, "00001", "00002")
    p = pdf_sintetico(tmp_path / "i.pdf", [(20, 200, "001", 0), (20, 100, "001", 0), (20, 50, "123", 0)])
    assert core.analisar_template(p).primeiro == "001"       # 3 algarismos ja contam como exemplo


def test_rotacao_do_talao_lida_do_texto(tmp_path):
    p = pdf_sintetico(tmp_path / "a.pdf", [(20, 200, "0001", 0), (20, 100, "0001", 90), (200, 200, "0002", 0), (200, 100, "0002", 90)])
    i = core.analisar_template(p)
    assert [(s.campo, s.rot) for s in i.slots] == [(1, 0), (1, 90), (2, 0), (2, 90)]


# ------------------------------------------------------------------ criar_fundo
def _tokens_de_exemplo(pdf_bytes_ou_caminho):
    rd = core._abrir_leitor(io.BytesIO(pdf_bytes_ou_caminho) if isinstance(pdf_bytes_ou_caminho, bytes) else pdf_bytes_ou_caminho)
    return pdftexto.Extrator(rd, rd.pages[0]).tokens(core.PADRAO_EXEMPLO)


def test_criar_fundo_apaga_so_os_numeros_de_exemplo(fx):
    tpl = fx("template_exemplo.pdf")
    info = core.analisar_template(tpl)
    assert len(_tokens_de_exemplo(tpl)) == 10
    fundo = core.criar_fundo(tpl, info)
    assert fundo[:5] == b"%PDF-"
    assert len(_tokens_de_exemplo(fundo)) == 0
    rd = core._abrir_leitor(io.BytesIO(fundo))
    assert len(rd.pages) == 1 and [float(v) for v in rd.pages[0].mediabox] == [0.0, 0.0, 595.0, 842.0]
    # o texto fixo continua la
    from conftest import textos_pdf
    import tempfile
    import pathlib
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "fundo.pdf"
        f.write_bytes(fundo)
        txt = textos_pdf(f)[0]
    assert "RIFA DE EXEMPLO" in txt and "31/12/2099" in txt and "0001" not in txt


# ------------------------------------------------------------------ preparar
def test_preparar_com_pdf_e_com_imagem(fx):
    pdf = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    img = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.png"))
    assert pdf.por_pagina == img.por_pagina == 5 and pdf.disp is None
    assert type(pdf.escritores["BitstreamVeraSans-Bold"]).__name__ == "LetraPDF" and pdf.escritores["BitstreamVeraSans-Bold"].vetorial
    assert type(img.escritores["BitstreamVeraSans-Bold"]).__name__ == "GlifosImagem" and not img.escritores["BitstreamVeraSans-Bold"].vetorial
    assert pdf.descricoes == ["letra «BitstreamVeraSans-Bold» extraída de digitos_exemplo.pdf"]
    assert img.descricoes == ["imagem digitos_exemplo.png"]
    assert pdf.fundo[:5] == b"%PDF-" and pdf.template == fx("template_exemplo.pdf")


def test_preparar_regista_o_que_encontrou(fx):
    logs = []
    core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"), log=logs.append)
    assert logs[0] == "Template: 5 bilhetes por página; números de exemplo 0001–0005."


@pytest.mark.parametrize("semente", [1, 3, 5, 9, 10])
def test_preparar_templates_aleatorios_pdf_e_png(fx, semente):
    pdf = core.preparar(fx(f"aleatorio_s{semente}.pdf"), fx(f"aleatorio_s{semente}_algarismos.pdf"))
    png = core.preparar(fx(f"aleatorio_s{semente}.pdf"), fx(f"aleatorio_s{semente}_algarismos.png"))
    assert pdf.por_pagina == png.por_pagina == pdf.info.n_campos
    assert pdf.info.slots == png.info.slots
    assert pdf.escritores[pdf.info.fontes[0]].vetorial and not png.escritores[png.info.fontes[0]].vetorial


@pytest.mark.parametrize("preparar_args, chave", [
    (("template_exemplo.pdf", None), "err_sem_ficheiro_algarismos"),
    (("template_exemplo.pdf", "digitos_exemplo.txt"), "err_formato"),
    (("template_exemplo.pdf", "nao_existe.pdf"), "err_ficheiro_inexistente"),
    (("template_exemplo.pdf", "template_exemplo.pdf"), "err_img_simbolos"),      # um PDF sem letra com 0-9 e tratado como imagem
])
def test_preparar_erros_de_algarismos_levam_a_info_do_template(fx, tmp_path, preparar_args, chave):
    tpl, alg = preparar_args
    if alg is None:
        alg_path = None
    elif alg == "digitos_exemplo.txt":
        alg_path = tmp_path / alg
        alg_path.write_text("x")
    elif alg == "nao_existe.pdf":
        alg_path = tmp_path / alg
    else:
        alg_path = fx(alg)
    with pytest.raises(core.ErroAlgarismos) as e:
        core.preparar(fx(tpl), alg_path)
    assert e.value.chave == chave
    assert e.value.info.n_campos == 5 and isinstance(e.value, core.ErroRifas)


def test_preparar_ficheiro_de_algarismos_corrompido(fx, tmp_path):
    (tmp_path / "x.pdf").write_text("isto nao e um PDF")
    with pytest.raises(core.ErroAlgarismos) as e:
        core.preparar(fx("template_exemplo.pdf"), tmp_path / "x.pdf")
    assert e.value.chave == "err_usar_ficheiro" and e.value.params["nome"] == "x.pdf"


def test_preparar_template_invalido_nao_e_erro_de_algarismos(tmp_path, fx):
    (tmp_path / "x.pdf").write_text("isto nao e um PDF")
    with pytest.raises(core.ErroRifas) as e:
        core.preparar(tmp_path / "x.pdf", fx("digitos_exemplo.pdf"))
    assert not isinstance(e.value, core.ErroAlgarismos) and e.value.chave == "err_abrir_template"


def test_com_folha_copia_sem_alterar_o_original(fx):
    p1 = core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf"))
    assert p1.disp is None and p1.por_pagina == 1
    p5 = p1.com_folha("A4", 5)
    assert p5 is not p1 and p1.disp is None and p5.por_pagina == 5
    assert p5.fundo is p1.fundo and p5.escritores is p1.escritores        # partilha o que e pesado
    assert p1.com_folha("A4", 5, 3).por_pagina == 3
    p_varias = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    assert erro_de(p_varias.com_folha, "A4", 5) == ("ErroRifas", "err_folha_varias", {})
