"""As etiquetas (senhas) de levantamento (`core/etiquetas.py`): uma por cópia de cada artigo, com a zona onde se levanta, agrupadas por zona; os combos dão uma senha por artigo."""
import io

import pytest
from core import etiquetas, i18n, moeda, precario_catalogo as cat
from core.etiquetas import Etiquetas
from core.motor import ErroRifas
from core.precario import Linha, Precario
from pypdf import PdfReader

LINGUAS = list(i18n.LINGUAS)


def texto_do_pdf(pdf: bytes) -> str:
    return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf)).pages)


def base(**campos) -> Etiquetas:
    p = Precario(linhas=(Linha(artigo="agua", preco=1000), Linha(artigo="bifana", preco=2500), Linha(artigo="cerveja", preco=1500)), titulo="Festa da escola", lingua="pt")
    return Etiquetas(**{"precario": p, "zonas": {"bebidas": "Bar", "alcool": "Bar", "comida": "Cozinha"}, "copias": 5, **campos})


def test_cada_artigo_da_tantas_senhas_como_copias_agrupadas_por_zona_e_por_artigo():
    ss = etiquetas.senhas(base())
    assert len(ss) == 15 and [s.nome for s in ss[:5]] == ["Água"] * 5
    assert [s.zona for s in ss] == ["Bar"] * 10 + ["Cozinha"] * 5                        # a zona do bar primeiro (a ordem das secções), depois a cozinha
    assert [s.nome for s in ss if s.zona == "Bar"][5:] == ["Cerveja"] * 5
    assert etiquetas.zonas_em_uso(base()) == ["Bar", "Cozinha"]
    assert all(s.preco is not None for s in ss) and all(s.preco is None for s in etiquetas.senhas(base(preco=False)))


def test_um_combo_da_uma_senha_por_artigo_cada_uma_com_a_zona_da_sua_seccao_e_o_nome_do_menu():
    p = Precario(linhas=(Linha(combo=("bifana", "cerveja"), nome="Menu da festa", preco=3500),), lingua="pt")
    ss = etiquetas.senhas(Etiquetas(p, {"comida": "Cozinha", "alcool": "Bar"}, copias=3))
    assert len(ss) == 6 and {(s.nome, s.zona, s.menu, s.preco) for s in ss} == {("Bifana", "Cozinha", "Menu da festa", None), ("Cerveja", "Bar", "Menu da festa", None)}
    pdf = etiquetas.criar_pdf(Etiquetas(p, {"comida": "Cozinha", "alcool": "Bar"}, copias=3))
    texto = texto_do_pdf(pdf)
    assert "Menu: Menu da festa" in texto and "Levantar em: Cozinha" in texto and "Levantar em: Bar" in texto


def test_o_pdf_tem_24_senhas_por_folha_o_titulo_o_preco_e_a_zona():
    pdf = etiquetas.criar_pdf(base(copias=10))                                           # 30 senhas: 2 folhas
    assert len(PdfReader(io.BytesIO(pdf)).pages) == 2
    texto = texto_do_pdf(pdf)
    assert texto.count("Festa da escola") == 30 and texto.count("Levantar em: Bar") == 20 and texto.count("Levantar em: Cozinha") == 10
    assert "1,00 €" in texto and "2,50 €" in texto
    assert "€" not in texto_do_pdf(etiquetas.criar_pdf(base(preco=False)))
    assert len(PdfReader(io.BytesIO(etiquetas.criar_pdf(base(copias=8)))).pages) == 1    # 24 senhas cabem numa folha


def test_sem_zona_a_senha_nao_leva_a_faixa_de_levantamento_e_sem_imagens_tambem_serve():
    texto = texto_do_pdf(etiquetas.criar_pdf(base(zonas={})))
    assert "Levantar" not in texto
    p = Precario(linhas=(Linha(artigo="agua"), Linha(nome="Bolo da avó", categoria="doces", preco=2000)), imagens=False, lingua="pt")
    assert "Bolo da avó" in texto_do_pdf(etiquetas.criar_pdf(Etiquetas(p, {"doces": "Mesa dos bolos"}, copias=2)))


@pytest.mark.parametrize("lg", LINGUAS)
def test_sai_em_todas_as_linguas_e_moedas(lg):
    p = Precario(linhas=(Linha(artigo="agua", preco=1000), Linha(artigo="bolo", preco=2000), Linha(combo=("agua", "bolo"))), titulo="Festa", lingua=lg, moeda=moeda.moeda_por_omissao(lg))
    pdf = etiquetas.criar_pdf(Etiquetas(p, {"bebidas": "Bar", "doces": "Doces"}, copias=2))
    assert pdf.startswith(b"%PDF") and len(PdfReader(io.BytesIO(pdf)).pages) == 1


def test_nomes_compridos_quebram_em_duas_linhas_ou_cortam_com_reticencias():
    longo = "Sandes mista de queijo e fiambre"
    assert len(etiquetas._linhas_do_nome(longo, True, 100, 2, 17, 8)[0]) <= 2
    assert etiquetas.criar_pdf(Etiquetas(Precario(linhas=(Linha(nome="X" * 40, categoria="extras"), Linha(nome=longo, categoria="extras")), lingua="pt"), {"extras": "Y" * 20}, copias=1)).startswith(b"%PDF")


def test_o_limite_de_senhas_e_de_copias_e_as_zonas_validam_se():
    with pytest.raises(ErroRifas) as e:
        etiquetas.criar_pdf(base(copias=0))
    assert e.value.chave == "err_etiquetas"
    with pytest.raises(ErroRifas):
        etiquetas.criar_pdf(base(copias=100))
    muitos = Precario(linhas=tuple(Linha(nome=f"Artigo {i}", categoria="extras") for i in range(30)), lingua="pt")
    with pytest.raises(ErroRifas) as e:
        etiquetas.criar_pdf(Etiquetas(muitos, {}, copias=50))                            # 1500 senhas
    assert e.value.chave == "err_etiquetas_limite"
    assert etiquetas.criar_pdf(Etiquetas(muitos, {}, copias=40)).startswith(b"%PDF")      # 1200 senhas: no limite
    for zonas in ({"nao_existe": "Bar"}, {"bebidas": "नमस्ते"}, {"bebidas": "Y" * 21}):
        with pytest.raises(ErroRifas):
            etiquetas.criar_pdf(base(zonas=zonas))


def test_de_dict_valida_tipos_ignora_o_formato_do_precario_e_tira_zonas_vazias():
    d = {"precario": {"linhas": [{"artigo": "agua", "preco": "1"}], "formato": "A6x4"}, "zonas": {"bebidas": " Bar ", "comida": "  "}, "copias": 4, "preco": False}
    e = etiquetas.de_dict(d, "pt")
    assert e.precario.formato == "A4" and e.zonas == {"bebidas": " Bar "} and e.copias == 4 and e.preco is False
    assert etiquetas.zonas_em_uso(e) == ["Bar"]
    for mau in (None, {}, {"precario": 3}, {"precario": {"linhas": []}, "copias": "5"}, {"precario": {"linhas": []}, "zonas": {"bebidas": 3}}, {"precario": {"linhas": []}, "copias": True}):
        with pytest.raises(ErroRifas):
            etiquetas.criar_pdf(etiquetas.de_dict(mau, "pt"))


def test_as_etiquetas_creditam_uma_biblioteca_so_quando_a_usa_de_verdade():
    com_credito = next(i for i in cat.ARTIGOS["agua"].icones if i.startswith("twemoji:"))
    sem = base(precario=Precario(linhas=(Linha(artigo="agua", preco=1000),), lingua="pt"))
    com = base(precario=Precario(linhas=(Linha(artigo="agua", preco=1000, emoji=com_credito),), lingua="pt"))
    assert "Twemoji" not in texto_do_pdf(etiquetas.criar_pdf(sem))
    t = texto_do_pdf(etiquetas.criar_pdf(com))
    assert "Twemoji" in t and "CC BY 4.0" in t
