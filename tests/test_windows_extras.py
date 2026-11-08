"""A app Windows 2.4: a lógica das funcionalidades «Extras» (exportar a lista, sorteio, logótipo, pré-visualização com séries, visual por
época) está em `core` e testa-se aqui sem janelas. A ligação à interface (menus, diálogos) tem o seu teste em app/testes/teste_extras.py
(precisa de ecrã). Nunca importar app.py: puxa o Tkinter."""
import io
from datetime import date
from pathlib import Path

import pytest
from PIL import Image

import core
from core import config, controlo, galeria, marca, pedido, series, sorteio, tema
from conftest import erro_de


def _tr(**kw):
    kw.setdefault("saida", Path("out"))
    kw.setdefault("nome", "Rifa de Natal")
    kw.setdefault("inicio", 1)
    kw.setdefault("fim", 4)
    kw.setdefault("digitos", 3)
    return core.Trabalho(**kw)


# ------------------------------------------------------------------ exportar a lista (M2)
def test_exportar_csv_nome_cabecalhos_e_bilhetes():
    tr = _tr(prefixos=("A-", "B-"), saltar=((2, 3),))
    nome, dados = controlo.exportar_csv(tr, series.bilhetes(tr), "pt")
    assert nome == "Rifa de Natal.csv"
    linhas = dados.decode("utf-8-sig").split("\r\n")
    assert linhas[0] == "Série;Número;Nome;Contacto;Pago" and linhas[1:4] == ["A;A-001;;;", "A;A-004;;;", "B;B-001;;;"]
    assert controlo.exportar_csv(_tr(nome=""), [("", "001")], "en")[0] == "rifas.csv"
    assert controlo.exportar_csv(_tr(), [("", "001")], "en")[1].decode("utf-8-sig").startswith("Series;Number;Name;Contact;Paid")


def test_exportar_folha_pdf_e_linguas_sem_as_letras_do_pdf_saem_em_ingles():
    tr = _tr()
    nome, pdf = controlo.exportar_folha(tr, series.bilhetes(tr), "pt")
    assert nome == "Controlo - Rifa de Natal.pdf" and pdf.startswith(b"%PDF")
    import pypdf
    assert "Controlo de vendas" in pypdf.PdfReader(io.BytesIO(pdf)).pages[0].extract_text()
    _, pdf_ru = controlo.exportar_folha(_tr(nome=""), [("", "001")], "ru")             # o russo nao cabe na Helvetica: inglês
    assert "Sales control sheet" in pypdf.PdfReader(io.BytesIO(pdf_ru)).pages[0].extract_text()


# ------------------------------------------------------------------ sorteio (M7)
def test_sorteio_de_campos_igual_a_referencia_e_respeita_os_saltos():
    esperado = sorteio.sortear(1, 100, 3, "lotaria", ((13, 13), (50, 60)))
    assert sorteio.pedido(" 1", "100 ", "3", "  lotaria  ", "13, 50-60") == esperado
    assert not set(esperado) & ({13} | set(range(50, 61)))


@pytest.mark.parametrize("de,ate,q,semente,saltar,chave", [
    ("1", "100", "3", "", "", "web_sorteio_erro_semente"), ("1", "100", "3", "x" * 201, "", "web_sorteio_erro_semente"),
    ("a", "100", "3", "s", "", "web_sorteio_erro_numeros"), ("100", "1", "3", "s", "", "web_sorteio_erro_numeros"),
    ("1", "10", "0", "s", "", "web_sorteio_erro_numeros"), ("1", "10", "11", "s", "", "web_sorteio_erro_numeros"),
    ("1", "2000000", "3", "s", "", "web_sorteio_erro_numeros"), ("1", "10", "101", "s", "", "web_sorteio_erro_numeros"),
])
def test_sorteio_de_campos_erros_traduzidos(de, ate, q, semente, saltar, chave):
    assert erro_de(sorteio.pedido, de, ate, q, semente, saltar)[1] == chave


def test_sorteio_saltar_invalido_e_err_saltar():
    assert erro_de(sorteio.pedido, "1", "10", "1", "s", "a-b")[1] == "err_saltar"


# ------------------------------------------------------------------ logótipo (M5)
def _png(tmp_path, tamanho=(120, 60)) -> Path:
    p = tmp_path / "logo.png"
    Image.new("RGBA", tamanho, (30, 140, 90, 255)).save(p)
    return p


def test_logotipo_a_partir_de_ficheiro(tmp_path):
    m = marca.ler_ficheiro(_png(tmp_path), "ie", 30)
    assert (m.largura, m.altura, m.posicao, m.tamanho) == (120, 60, "ie", 30)


def test_logotipo_inexistente_ou_que_nao_e_imagem_e_err_logotipo(tmp_path):
    assert erro_de(marca.ler_ficheiro, tmp_path / "nao-existe.png")[1] == "err_logotipo"
    falso = tmp_path / "x.png"
    falso.write_bytes(b"isto nao e uma imagem")
    assert erro_de(marca.ler_ficheiro, falso)[1] == "err_logotipo"


def test_logotipo_grande_demais_recusa_se_sem_o_ler(tmp_path):
    grande = tmp_path / "g.png"
    grande.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * (marca.MAX_MB * 1024 * 1024 + 1))
    assert erro_de(marca.ler_ficheiro, grande)[1] == "err_logotipo"


# ------------------------------------------------------------------ pré-visualização com o pedido todo (M1, M3, M5)
@pytest.fixture(scope="module")
def prep_galeria(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("galeria")
    (pasta / "t.pdf").write_bytes(galeria.criar_template("natal", galeria.Textos("Rifa", "Assoc", ("1.º Prémio",), "")))
    (pasta / "a.pdf").write_bytes(galeria.criar_algarismos())
    prep = core.preparar(pasta / "t.pdf", pasta / "a.pdf")
    esc = core.escolha_folha.escolher_folha(prep.info, "A4", "5", "")          # o logotipo so se desenha em modo folha (como na app)
    return core.escolha_folha.preparado_com_folha(prep, esc.disp)


def _png_cor(png: bytes, cor, folga=60) -> int:
    """Quantos pixeis da imagem estao perto de `cor`."""
    b = Image.open(io.BytesIO(png)).convert("RGB").tobytes()
    return sum(1 for i in range(0, len(b), 3) if all(abs(b[i + k] - cor[k]) < folga for k in range(3)))


def test_previa_png_leva_o_prefixo_a_cor_e_os_numeros_saltados(prep_galeria):
    simples = pedido.previa_png(prep_galeria, _tr(fim=30, digitos=4), dpi=80)
    com_tudo = pedido.previa_png(prep_galeria, _tr(fim=30, digitos=4, prefixos=("A-",), saltar=((1, 1),), cor_numeros=(0.0, 0.0, 1.0)), dpi=80)
    assert simples.startswith(b"\x89PNG") and com_tudo.startswith(b"\x89PNG") and simples != com_tudo
    assert _png_cor(com_tudo, (0, 0, 255)) > _png_cor(simples, (0, 0, 255)) + 50          # os numeros ficaram azuis


def test_previa_png_com_logotipo(prep_galeria, tmp_path):
    sem = pedido.previa_png(prep_galeria, _tr(fim=5), dpi=80)
    com = pedido.previa_png(prep_galeria, _tr(fim=5, marca=marca.ler_ficheiro(_png(tmp_path, (200, 100)), "sd", 30)), dpi=80)
    assert _png_cor(com, (30, 140, 90), 20) > _png_cor(sem, (30, 140, 90), 20) + 100         # o logotipo (verde) aparece na rifa


# ------------------------------------------------------------------ visual por época (F1) e contraste das paletas (M10)
def test_visual_por_epoca():
    assert tema.visual_por_epoca(date(2026, 12, 1)) == "natal" and tema.visual_por_epoca(date(2026, 12, 31)) == "natal"
    assert tema.visual_por_epoca(date(2026, 11, 30)) == "premiado" and tema.visual_por_epoca(date(2027, 1, 1)) == "premiado"
    assert tema.visual_por_epoca() in tema.VISUAIS


@pytest.mark.parametrize("visual", tema.VISUAIS)
@pytest.mark.parametrize("modo", (0, 1), ids=("claro", "escuro"))
def test_paleta_cumpre_o_contraste_wcag_aa(visual, modo):
    fixas, extras = tema.PALETAS_VISUAIS[visual]
    p = {**fixas, **extras}
    rgb = lambda nome: tema.hex_para_rgb(p[nome][modo])          # noqa: E731
    for descricao, texto, fundo, minimo in tema.pares_de_contraste(p):
        assert tema.contraste(rgb(texto), rgb(fundo)) >= minimo, f"{visual} {descricao}"
    for botao in ("acento", "acento2", "passo1", "passo2", "passo3", "passo4"):             # o texto escolhido sobre cada cor de botao/passo
        assert tema.contraste(tema.hex_para_rgb(tema.texto_sobre(rgb(botao))), rgb(botao)) >= 4.5, f"{visual} texto sobre {botao}"


def test_as_paletas_dos_visuais_tem_as_mesmas_chaves():
    (f1, e1), (f2, e2) = tema.PALETAS_VISUAIS["premiado"], tema.PALETAS_VISUAIS["natal"]
    assert f1.keys() == f2.keys() and e1.keys() == e2.keys()


def test_visual_no_config():
    assert config.preferencias({"visual": "natal"})["visual"] == "natal"
    assert "visual" not in config.preferencias({"visual": "gala"}) and "visual" not in config.preferencias({})
    base = dict(lingua="pt", tema="system", algarismos="", saida="", inicio="1", fim="9", digitos="4", max_ficheiro="3", modo="varios", papel="A4", margem="5")
    assert "visual" not in config.para_gravar(**base) and config.para_gravar(**base, visual="natal")["visual"] == "natal"
