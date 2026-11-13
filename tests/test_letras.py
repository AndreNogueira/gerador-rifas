"""As letras do editor e da galeria (`core.letras`): Vera como sempre, DejaVu para latim estendido/vietnamita/grego/cirílico e Noto para chinês, japonês e coreano."""
import io

import pytest
from pypdf import PdfReader

from core import editor, galeria, letras

AMOSTRAS = {
    "latim basico": ("Rifa de Natal São João 2026", "Vera"),
    "polaco": ("Loteria — zażółć gęślą jaźń", "DejaVu"),
    "checo": ("Tombola — příliš žluťoučký kůň", "DejaVu"),
    "romeno": ("Tombolă pentru școală și țară", "DejaVu"),
    "turco": ("Çekiliş — ığüşöç İĞÜŞÖÇ", "Vera"),                       # a Vera já tem o turco
    "vietnamita": ("Bốc thăm cho trường học ắ ề ộ ữ", "DejaVu"),
    "grego": ("Κλήρωση για την ενορία", "DejaVu"),
    "russo": ("Лотерея для школы", "DejaVu"),
    "ucraniano": ("Лотерея для парафії ґ є і ї", "DejaVu"),
    "chines": ("为学校举办抽奖 São", "NotoSC"),
    "japones": ("学校の抽選会 ひらがな カタカナ", "NotoJP"),
    "coreano": ("학교 추첨 행사", "NotoKR"),
    "japones com cirilico": ("日本語 Рифа", "NotoJP"),                 # as Noto também têm grego e cirílico: misturam-se com o CJK
}


@pytest.mark.parametrize("nome", AMOSTRAS)
def test_cada_texto_escolhe_a_primeira_familia_que_o_tem_todo(nome):
    texto, esperada = AMOSTRAS[nome]
    assert letras.familia(texto) == esperada and letras.em_falta(texto) == ""
    assert letras.fonte(texto, negrito=True) == {"Vera": "VeraBd", "DejaVu": "DejaVuBd"}.get(esperada, esperada)


@pytest.mark.parametrize("texto", ["हिन्दी", "العربية", "שלום", "😀", "日本語 हिन्दी", "a\x00b"])
def test_o_que_nenhuma_familia_tem_fica_em_falta(texto):
    assert letras.em_falta(texto) != "" and (letras.familia(texto) is None or "\x00" in texto)


def test_o_latim_basico_continua_a_sair_em_vera_byte_a_byte():
    d = editor.de_dict({"largura": 300, "altura": 100, "fundo": "#ffffff", "elementos": [
        {"tipo": "texto", "x": 10, "y": 30, "texto": "Rifa de Natal", "tamanho": 20, "cor": "#000000"},
        {"tipo": "numero", "x": 10, "y": 80, "tamanho": 20, "cor": "#000000"}]})
    pdf = editor.criar_template(d)
    fontes = {str(f.get("/BaseFont", "")) for p in PdfReader(io.BytesIO(pdf)).pages for f in (v.get_object() for v in p["/Resources"]["/Font"].values())}
    assert all("Vera" in f for f in fontes if f != "/Helvetica"), fontes             # (o /Helvetica é o que o canvas declara por omissão)


@pytest.mark.parametrize("nome", ["grego", "russo", "vietnamita", "chines", "japones", "coreano", "polaco"])
def test_o_editor_desenha_textos_nessas_letras_com_a_familia_certa(nome):
    texto, esperada = AMOSTRAS[nome]
    d = editor.de_dict({"largura": 400, "altura": 120, "fundo": "#ffffff", "elementos": [
        {"tipo": "texto", "x": 10, "y": 40, "texto": texto, "tamanho": 16, "cor": "#000000", "negrito": True},
        {"tipo": "numero", "x": 10, "y": 100, "tamanho": 20, "cor": "#000000"}]})
    pdf = editor.criar_template(d)
    leitor = PdfReader(io.BytesIO(pdf))
    fontes = " ".join(str(v.get_object().get("/BaseFont", "")) for p in leitor.pages for v in p["/Resources"]["/Font"].values())
    chave = {"DejaVu": "DejaVu", "NotoSC": "NotoSansSC", "NotoJP": "NotoSansJP", "NotoKR": "NotoSansKR"}[esperada]
    assert chave in fontes and "BitstreamVeraSans-Bold" in fontes              # o número continua em Vera negrito
    assert texto.split()[0][:2] in (leitor.pages[0].extract_text() or "") or esperada.startswith("Noto")


def test_largura_do_texto_usa_a_letra_que_o_desenha():
    assert editor.largura_do_texto("Rifa", False, 10) == letras.largura("Rifa", False, 10)
    assert editor.largura_do_texto("Κλήρωση", False, 10) > 20 and editor.largura_do_texto("为学校", False, 10) == pytest.approx(30, abs=1)


def test_a_galeria_aceita_gregos_cirilicos_vietnamitas_e_cjk_e_a_previa_corre():
    for titulo in ("Κλήρωση", "Лотерея", "Bốc thăm", "抽奖", "抽選会", "추첨"):
        pdf = galeria.criar_template("natal", galeria.Textos(titulo=titulo, organizacao=titulo, premios=(titulo,), data=titulo))
        assert pdf.startswith(b"%PDF")
