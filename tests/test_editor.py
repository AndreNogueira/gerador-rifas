"""X1: o editor de templates. O desenho que vem do browser vira um PDF que o motor aceita (preparar -> gerar -> verificar), mesmo com texto
cheio de algarismos à volta; o que o motor confundiria com o número (0123) e os valores fora dos limites são recusados com mensagens traduzíveis."""
import pytest

import core
from conftest import erro_de, numeros_pdf
from core import editor, galeria

CINZA = "#555555"


def _desenho(extra=(), numeros=2, **kw) -> dict:
    """Uma rifa com talão, como a que o editor propõe: moldura, talão, título, data, e o número no talão (rodado) e na parte principal."""
    elementos = [
        dict(tipo="retangulo", x=2, y=2, w=531, h=148, cor="#fffdf5", contorno="#0f6e73", espessura=2, raio=10),
        dict(tipo="linha", x=64, y=8, w=0, h=136, contorno="#0f6e73", espessura=1, tracejado=True),
        dict(tipo="texto", x=78, y=34, texto="Rifa de Natal 2026", tamanho=21, cor="#0f6e73", negrito=True),
        dict(tipo="texto", x=78, y=100, texto="1.º Prémio: 2 noites · Sorteio: 24/12/2026 às 21h30", tamanho=9, cor=CINZA),
        dict(tipo="numero", x=392, y=44, tamanho=20, cor="#e37815", alinhamento="c"),
    ]
    if numeros == 2:
        elementos.append(dict(tipo="numero", x=40, y=96, tamanho=19, cor="#e37815", rot=90))
    elementos += list(extra)
    return dict(largura=535, altura=152, fundo="#ffffff", elementos=elementos) | kw


@pytest.fixture(scope="module")
def algarismos(tmp_path_factory):
    p = tmp_path_factory.mktemp("editor") / "algarismos.pdf"
    p.write_bytes(galeria.criar_algarismos())
    return p


def _pdf(tmp_path, desenho: dict):
    p = tmp_path / "template.pdf"
    p.write_bytes(editor.criar_template(editor.de_dict(desenho)))
    return p


@pytest.mark.parametrize("numeros", [1, 2])
def test_o_desenho_vira_um_template_que_o_motor_aceita_e_enche_a_folha(tmp_path, algarismos, numeros):
    logs = []
    prep = core.preparar(_pdf(tmp_path, _desenho(numeros=numeros)), algarismos, logs.append)
    assert prep.info.n_campos == 1 and prep.info.n_numeros == {1: numeros} and prep.info.primeiro == "0001"
    assert not any("diferente" in str(m) for m in logs)                      # os algarismos estão na mesma letra do número
    folha = prep.com_folha("A4", 5)
    assert folha.por_pagina == 5
    r = core.gerar(core.Trabalho(tmp_path / "out", "R", 1, 10, digitos=4), folha)
    assert [x.ok for x in r] == [True]
    esperado = sorted(f"{n:04d}" for n in range(1, 6) for _ in range(numeros))
    # o texto livre (2026, 24/12/2026, 21h30…) não pode contar como número do bilhete: «2026» tem 4 algarismos mas o ano vem em `fixos`
    assert numeros_pdf(r[0].caminho, 4, fixos=("2026",))[0] == esperado


def test_texto_com_muitos_algarismos_nao_confunde_o_motor(tmp_path, algarismos):
    extra = [dict(tipo="texto", x=78, y=120, texto="Tel. 912345678 · NIF 509999999 · 20/11/2026 · 2.º e 3.º prémios", tamanho=8, cor=CINZA)]
    prep = core.preparar(_pdf(tmp_path, _desenho(extra)), algarismos)
    assert prep.info.n_numeros == {1: 2}


@pytest.mark.parametrize("texto", ["Prémio 0123", "Ref. 0001", "Nº 007", "(0002)", "a 00000 b"])
def test_texto_com_algo_que_parece_o_numero_e_recusado(texto):
    d = _desenho([dict(tipo="texto", x=5, y=5, texto=texto)])
    tipo, chave, params = erro_de(editor.de_dict, d)
    assert (tipo, chave) == ("ErroRifas", "err_editor_digitos") and params["texto"]


def test_zeros_dentro_de_numeros_maiores_nao_sao_o_numero():
    editor.de_dict(_desenho([dict(tipo="texto", x=5, y=5, texto="Tel. 910000000 · 2026 · 10/01 · 100€ · 1000")]))


@pytest.mark.parametrize("numeros", [0, 3])
def test_o_numero_aparece_uma_ou_duas_vezes(numeros):
    d = _desenho(numeros=2)
    d["elementos"] = [e for e in d["elementos"] if e["tipo"] != "numero"] + [dict(tipo="numero", x=5, y=5, tamanho=14)] * numeros
    assert erro_de(editor.de_dict, d)[:2] == ("ErroRifas", "err_editor_numero")


def test_letras_que_a_vera_nao_tem_sao_recusadas():
    d = _desenho([dict(tipo="texto", x=5, y=5, texto="Рифа")])
    assert erro_de(editor.de_dict, d)[:2] == ("ErroRifas", "err_editor_letra")


@pytest.mark.parametrize("alteracao", [
    dict(largura=50), dict(largura=5000), dict(altura=10), dict(fundo="vermelho"), dict(fundo="#fff"),
    dict(elementos=[dict(tipo="numero", x=1, y=1, tamanho=900)]),
    dict(elementos=[dict(tipo="numero", x=float("nan"), y=1)]),
    dict(elementos=[dict(tipo="numero", x=1, y=1, rot=45)]),
    dict(elementos=[dict(tipo="foto", x=1, y=1)]),
    dict(elementos=[dict(tipo="numero", x=1, y=1)] * 41),
    dict(elementos=[dict(tipo="numero", x=1, y=1), dict(tipo="linha", x=0, y=0, w=10, h=0)]),            # linha sem cor
    dict(elementos=[dict(tipo="numero", x=1, y=1), dict(tipo="texto", x=0, y=0, texto="x" * 81)]),
    dict(elementos=[dict(tipo="numero", x=1, y=1), dict(tipo="texto", x=0, y=0, texto="duas\nlinhas")]),
    dict(elementos="muitos"),
])
def test_valores_fora_dos_limites_sao_recusados(alteracao):
    assert erro_de(editor.de_dict, _desenho() | alteracao)[:2] == ("ErroRifas", "err_editor_limite")


def test_o_mesmo_desenho_da_os_mesmos_bytes_e_a_ordem_dos_elementos_importa():
    a = editor.criar_template(editor.de_dict(_desenho()))
    assert a == editor.criar_template(editor.de_dict(_desenho()))
    d = _desenho()
    d["elementos"] = list(reversed(d["elementos"]))
    assert a != editor.criar_template(editor.de_dict(d))


def test_o_texto_e_o_numero_ancoram_na_linha_de_base_e_rodam_a_volta_do_ponto():
    import io

    import pypdfium2 as pdfium
    d = _desenho()
    d["elementos"] = [dict(tipo="numero", x=100, y=50, tamanho=20, alinhamento="d"), dict(tipo="texto", x=10, y=140, texto="base", tamanho=10)]
    doc = pdfium.PdfDocument(io.BytesIO(editor.criar_template(editor.de_dict(d))))
    try:
        tp = doc[0].get_textpage()
        esq, _, _, cima = tp.get_charbox(0)                   # o «0» do número
        _, _, dir_, _ = tp.get_charbox(3)                     # o último «1»: alinhado à direita, termina em x=100
        assert abs(dir_ - 100) < 2 and abs(esq - (100 - editor.largura_do_texto("0001", True, 20))) < 2
        assert abs(cima - (152 - 50 + 20 * 0.7)) < 4          # a linha de base está em y=50 (de cima), ou seja, 102 de baixo; os algarismos sobem ~0,73 × tamanho
        tp.close()
    finally:
        doc.close()


# ------------------------------------------------------------------ imagens (o logótipo dentro do desenho)
def _data_url(formato="PNG", tamanho=(40, 20), cor=(200, 30, 30, 255)) -> str:
    import base64
    import io

    from PIL import Image
    b = io.BytesIO()
    imagem = Image.new("RGBA" if formato == "PNG" else "RGB", tamanho, cor if formato == "PNG" else cor[:3])
    imagem.save(b, formato)
    mime = "png" if formato == "PNG" else "jpeg"
    return f"data:image/{mime};base64," + base64.b64encode(b.getvalue()).decode()


@pytest.mark.parametrize("formato", ["PNG", "JPEG"])
def test_a_imagem_entra_no_template_e_o_motor_continua_a_aceita_lo(tmp_path, algarismos, formato):
    import io

    import pypdfium2 as pdfium
    d = _desenho([dict(tipo="imagem", x=20, y=20, w=80, h=40, dados=_data_url(formato))])
    pdf = editor.criar_template(editor.de_dict(d))
    doc = pdfium.PdfDocument(io.BytesIO(pdf))
    try:
        assert len(list(doc[0].get_objects(filter=[pdfium.raw.FPDF_PAGEOBJ_IMAGE]))) == 1
        pixeis = doc[0].render(scale=2).to_pil().convert("RGB")
        assert pixeis.getpixel((int(60 * 2), int(40 * 2)))[0] > 150 and pixeis.getpixel((int(60 * 2), int(40 * 2)))[1] < 100     # o vermelho da imagem
    finally:
        doc.close()
    p = tmp_path / "t.pdf"
    p.write_bytes(pdf)
    assert core.preparar(p, algarismos).info.n_numeros == {1: 2}


@pytest.mark.parametrize("dados", [
    "", None, 5, "data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=", "data:image/png;base64,nao-e-base64!!", "data:image/png;base64,AAAA",
    "data:text/html;base64,PGgxPg==", "http://exemplo.pt/x.png", "data:image/png;base64," + "A" * 1_400_000,
])
def test_imagens_que_nao_prestam_sao_recusadas(dados):
    d = _desenho([dict(tipo="imagem", x=0, y=0, w=10, h=10, dados=dados)])
    assert erro_de(editor.de_dict, d)[:2] == ("ErroRifas", "err_editor_imagem")


def test_o_tipo_real_conta_nao_o_que_o_texto_diz():
    import base64
    import io

    from PIL import Image
    b = io.BytesIO()
    Image.new("RGB", (4, 4)).save(b, "GIF")
    d = _desenho([dict(tipo="imagem", x=0, y=0, w=10, h=10, dados="data:image/png;base64," + base64.b64encode(b.getvalue()).decode())])
    assert erro_de(editor.de_dict, d)[:2] == ("ErroRifas", "err_editor_imagem")           # um GIF com o nome de PNG


def test_imagem_enorme_em_pixeis_e_mais_de_cinco_imagens_sao_recusadas(monkeypatch):
    grande = _desenho([dict(tipo="imagem", x=0, y=0, w=10, h=10, dados=_data_url(tamanho=(2100, 4)))])
    assert erro_de(editor.de_dict, grande)[:2] == ("ErroRifas", "err_editor_imagem")
    seis = _desenho([dict(tipo="imagem", x=i, y=0, w=5, h=5, dados=_data_url()) for i in range(6)])
    assert erro_de(editor.de_dict, seis)[:2] == ("ErroRifas", "err_editor_limite")
    assert erro_de(editor.de_dict, _desenho([dict(tipo="imagem", x=0, y=0, w=0, h=10, dados=_data_url())]))[:2] == ("ErroRifas", "err_editor_limite")


def test_a_imagem_e_recodificada_sem_metadados():
    import base64
    import io

    from PIL import Image
    b = io.BytesIO()
    im = Image.new("RGB", (8, 8), (1, 2, 3))
    exif = Image.Exif()
    exif[0x010E] = "SEGREDO-EXIF"
    im.save(b, "JPEG", exif=exif)
    assert b"SEGREDO-EXIF" in b.getvalue()
    d = editor.de_dict(_desenho([dict(tipo="imagem", x=0, y=0, w=10, h=10, dados="data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode())]))
    imagem = next(e for e in d.elementos if e.tipo == "imagem")
    assert imagem.imagem[:8] == b"\x89PNG\r\n\x1a\n" and b"SEGREDO-EXIF" not in imagem.imagem
