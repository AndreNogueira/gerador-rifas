"""`core/moeda.py`: valores em inteiros (milésimos), a moeda do país, a escrita de cada língua, a leitura tolerante e a moeda inventada."""
import pytest
from core import i18n, letras, moeda
from core.moeda import ErroMoeda, MoedaInventada, formatar, valor_de_texto


@pytest.mark.parametrize("texto, lingua, esperado", [
    ("1,5", "pt", 1500), ("1.5", "en", 1500), ("1,50", "pt", 1500), ("0,10", "pt", 100), ("0.1", "en", 100), (".5", "en", 500), (",5", "pt", 500),
    ("€ 1 234,50", "pt", 1_234_500), ("1.234,50", "pt", 1_234_500), ("1,234.50", "en", 1_234_500), ("R$ 12,90", "pt-br", 12_900),
    ("1.500", "pt", 1_500_000), ("1.500", "id", 1_500_000), ("1,500", "en", 1_500_000), ("1.500", "en", 1500), ("1,500", "pt", 1500),
    ("1.234.567", "pt", 1_234_567_000), ("3", "pt", 3000), ("0", "pt", 0), ("  2 ", "en", 2000), ("2 fichas", "pt", 2000), ("1,5 €", "fr", 1500),
    ("0,005", "pt", 5), ("0,0004", "pt", 0), ("1,2345", "pt", 1235),            # meio para cima nos milésimos
])
def test_valor_de_texto(texto, lingua, esperado):
    assert valor_de_texto(texto, lingua) == esperado


@pytest.mark.parametrize("texto", ["", "   ", "abc", "-1", "€", ".", ",", "1,2,3x?-", "99999999999", None])
def test_o_que_nao_e_preco_da_none(texto):
    assert valor_de_texto(texto or "", "pt") is None


def test_nunca_se_usa_float_nos_valores():
    assert valor_de_texto("0,10", "pt") + valor_de_texto("0,20", "pt") == valor_de_texto("0,30", "pt") == 300     # 0,1 + 0,2 em float dava 0,30000000000000004
    assert isinstance(valor_de_texto("1,5", "pt"), int) and isinstance(moeda.numero(1500, 2, "pt"), str)


@pytest.mark.parametrize("valor, cod, lingua, esperado", [
    (1500, "EUR", "pt", "1,50 €"), (1500, "EUR", "en", "€1.50"), (1500, "EUR", "de", "1,50 €"), (1500, "EUR", "fr", "1,50 €"), (1500, "EUR", "nl", "€ 1,50"),
    (1500, "BRL", "pt-br", "R$ 1,50"), (12_900, "BRL", "pt-br", "R$ 12,90"), (1_234_500, "BRL", "pt-br", "R$ 1.234,50"), (1_234_500, "EUR", "pt", "1234,50 €"), (12_345_500, "EUR", "pt", "12 345,50 €"),
    (1500, "USD", "en", "$1.50"), (1500, "GBP", "en", "£1.50"), (1500, "CHF", "de", "1,50 CHF"), (1500, "CHF", "en", "CHF 1.50"),
    (1500, "PLN", "pl", "1,50 zł"), (1500, "CZK", "cs", "1,50 Kč"), (1500, "SEK", "sv", "1,50 kr"), (1500, "RON", "ro", "1,50 lei"),
    (1500, "RUB", "ru", "1,50 ₽"), (1500, "TRY", "tr", "₺1,50"), (1500, "UAH", "uk", "1,50 ₴"),
    (1500, "JPY", "ja", "¥2"), (150_000, "JPY", "ja", "¥150"), (1_500_000, "KRW", "ko", "₩1,500"), (1500, "INR", "hi", "₹1.50"), (1500, "CNY", "zh", "¥1.50"),
    (1_500_000, "IDR", "id", "Rp1.500"), (1_500_000, "VND", "vi", "1.500 ₫"), (1500, "EUR", "xx", "€1.50"),
    (0, "EUR", "pt", "0,00 €"), (5, "EUR", "pt", "0,01 €"), (4, "EUR", "pt", "0,00 €"), (995, "EUR", "pt", "1,00 €"), (999, "EUR", "pt", "1,00 €"), (1000, "EUR", "en", "€1.00"),
])
def test_formatar(valor, cod, lingua, esperado):
    assert formatar(valor, moeda.MOEDAS[cod], lingua) == esperado


def test_a_moeda_inventada_escreve_se_antes_ou_depois_com_as_casas_que_se_escolhem():
    fichas = moeda.validar_inventada(MoedaInventada("fichas"))
    assert formatar(3000, fichas, "pt") == "3 fichas" and formatar(1500, MoedaInventada("fichas", False, 1), "pt") == "1,5 fichas"
    assert formatar(2000, MoedaInventada("Tostões", True, 0), "pt") == "Tostões 2" and formatar(2500, MoedaInventada("tokens", False, 2), "en") == "2.50 tokens"
    assert formatar(1_234_000, MoedaInventada("bolotas"), "pt-br") == "1.234 bolotas"


@pytest.mark.parametrize("m", [MoedaInventada(""), MoedaInventada("   "), MoedaInventada("x" * 15), MoedaInventada("fichas2"), MoedaInventada("a\x01b"), MoedaInventada("fichas", False, 3),
                               MoedaInventada("चिप")])
def test_a_moeda_inventada_invalida_recusa_se(m):
    with pytest.raises(ErroMoeda):
        moeda.validar_inventada(m)


def test_a_moeda_inventada_valida_arruma_os_espacos_e_aceita_letras_de_varias_linguas():
    assert moeda.validar_inventada(MoedaInventada("  fichas   verdes ")).nome == "fichas verdes"
    for nome in ("жетони", "φύλλα", "筹码", "チップ", "칩", "żetony", "fişe", "tokens"):
        assert moeda.validar_inventada(MoedaInventada(nome)).nome == nome


def test_cada_pais_tem_uma_moeda_conhecida_e_cada_lingua_um_pais_com_moeda():
    assert all(c in moeda.MOEDAS for c in moeda.PAIS_MOEDA.values())
    for lg in i18n.LINGUAS:
        pais = moeda.pais_por_omissao(lg)
        assert moeda.moeda_do_pais(pais) is not None and pais == moeda.PAIS_DA_LINGUA[lg], lg
        assert lg in moeda.CONVENCOES, lg
    assert moeda.moeda_por_omissao("pt").codigo == "EUR" and moeda.moeda_por_omissao("pt-br").codigo == "BRL" and moeda.moeda_por_omissao("en").codigo == "USD"
    assert moeda.moeda_por_omissao("pl").codigo == "PLN" and moeda.moeda_por_omissao("ja").codigo == "JPY" and moeda.moeda_por_omissao("xx").codigo == "USD"


def test_moeda_por_pais_e_nao_so_por_lingua():
    assert moeda.moeda_do_pais("br").codigo == "BRL" and moeda.moeda_do_pais("MX").codigo == "MXN" and moeda.moeda_do_pais("gb").codigo == "GBP"
    assert moeda.moeda_do_pais("AO").codigo == "AOA" and moeda.moeda_do_pais("MZ").codigo == "MZN" and moeda.moeda_do_pais("CV").codigo == "CVE"
    assert moeda.moeda_do_pais("CH").codigo == "CHF" and moeda.moeda_do_pais("XX") is None and moeda.moeda_do_pais("") is None
    assert moeda.moeda_de_codigo("eur").simbolo == "€"
    with pytest.raises(ErroMoeda):
        moeda.moeda_de_codigo("XYZ")


def test_todos_os_simbolos_tem_letra_no_pdf():
    for m in moeda.MOEDAS.values():
        assert not letras.em_falta(m.simbolo), (m.codigo, m.simbolo)
    for lg in i18n.LINGUAS:                                         # e os números formatados em todas as línguas (separadores incluídos)
        for m in moeda.MOEDAS.values():
            assert not letras.em_falta(formatar(1_234_560, m, lg)), (lg, m.codigo)


def test_fora_dos_limites_levanta_erro():
    with pytest.raises(ErroMoeda):
        formatar(-1, moeda.MOEDAS["EUR"], "pt")
    with pytest.raises(ErroMoeda):
        formatar(moeda.MAX_VALOR + 1, moeda.MOEDAS["EUR"], "pt")
