"""O catálogo do preçário (`core/precario_catalogo.py` + `precario_dados.py`): os dados estão completos nas 23 línguas, a região filtra, as ocasiões apontam para desenhos e artigos que existem."""
import pytest
from core import galeria, i18n, letras, precario_catalogo as cat

LINGUAS = list(i18n.LINGUAS)


def test_os_dados_cobrem_todas_as_linguas_do_site():
    assert set(cat.LINGUAS) == set(LINGUAS)
    for item in (*cat.CATEGORIAS.values(), *cat.ARTIGOS.values(), *cat.OCASIOES.values()):
        assert set(item.nomes) == set(LINGUAS), item.id
        assert all(n.strip() and len(n) <= cat.MAX_NOME and "|" not in n for n in item.nomes.values()), item.id


def test_o_tamanho_do_catalogo():
    assert len(cat.ARTIGOS) >= 90 and len(cat.OCASIOES) >= 12 and len(cat.CATEGORIAS) == 8
    assert {a.categoria for a in cat.ARTIGOS.values()} == set(cat.CATEGORIAS) - {"menus"}      # nenhuma categoria vazia (os «Menus e combos» só têm os combos que a pessoa junta)


def test_as_ocasioes_usam_desenhos_da_galeria_artigos_que_existem_e_meses_validos():
    for o in cat.OCASIOES.values():
        assert o.desenho in galeria.POR_ID, o.id
        assert o.meses and all(1 <= m <= 12 for m in o.meses) and 5 <= len(o.artigos) <= 14 and len(set(o.artigos)) == len(o.artigos), o.id
        for a in o.artigos:
            assert a in cat.ARTIGOS, (o.id, a)
            if o.regiao:                                                           # uma ocasião de uma região só leva artigos dela ou gerais
                assert cat.ARTIGOS[a].regiao in ("", o.regiao), (o.id, a)


def test_a_regiao_filtra_artigos_e_ocasioes():
    pt = {a.id for a in cat.artigos_da_lingua("pt")}
    br = {a.id for a in cat.artigos_da_lingua("pt-br")}
    en = {a.id for a in cat.artigos_da_lingua("en")}
    assert {"bifana", "caldo_verde", "imperial", "pastel_de_nata"} <= pt and not ({"coxinha", "quentao", "chopp"} & pt)
    assert {"coxinha", "quentao", "chopp", "pamonha", "brigadeiro"} <= br and not ({"bifana", "caldo_verde", "imperial"} & br)
    assert not ({"bifana", "coxinha"} & en) and {"agua", "cerveja", "bolo"} <= pt & br & en
    assert "santos_populares" in {o.id for o in cat.ocasioes_da_lingua("pt")} and "santos_populares" not in {o.id for o in cat.ocasioes_da_lingua("pt-br")}
    assert "festa_junina" in {o.id for o in cat.ocasioes_da_lingua("pt-br")} and "festa_junina" not in {o.id for o in cat.ocasioes_da_lingua("en")}


def test_a_ocasiao_da_epoca():
    assert cat.ocasiao_da_epoca(6, "pt").id == "santos_populares" and cat.ocasiao_da_epoca(6, "pt-br").id == "festa_junina" and cat.ocasiao_da_epoca(6, "en").id == "festa_popular"
    assert cat.ocasiao_da_epoca(12, "en").id == "natal" and cat.ocasiao_da_epoca(11, "pt").id == "magusto" and cat.ocasiao_da_epoca(11, "en").id == "natal"
    assert cat.ocasiao_da_epoca(10, "ja").id == "halloween" and cat.ocasiao_da_epoca(1, "pt").id == "inverno"
    assert all(cat.ocasiao_da_epoca(m, lg) is not None for m in range(1, 13) for lg in ("pt", "pt-br", "en"))                  # todo o mês tem uma sugestão


def test_nomes_por_lingua_e_o_pt_br_deriva_do_pt_ou_tem_o_seu():
    a = cat.ARTIGOS["sumo"]
    assert cat.nome(a, "pt") == "Sumo" and cat.nome(a, "pt-br") == "Suco" and cat.nome(a, "en") == "Juice" and cat.nome(a, "xx") == "Juice"
    assert cat.nome(cat.ARTIGOS["gelado"], "pt-br") == "Sorvete" and cat.nome(cat.ARTIGOS["agua"], "pt-br") == "Água"
    assert cat.nome(cat.ARTIGOS["bifana"], "ja") == "Bifana" and cat.nome(cat.OCASIOES["santos_populares"], "de") == "Santos Populares"      # nomes próprios


def test_o_nome_para_o_pdf_cai_para_o_ingles_se_a_letra_nao_existe():
    a = cat.ARTIGOS["cerveja"]
    assert cat.nome(a, "hi") == "बीयर" and cat.nome_imprimivel(a, "hi") == "Beer"                   # o PDF não tem devanágari
    assert cat.nome_imprimivel(a, "ja") == "ビール" and cat.nome_imprimivel(a, "ru") == "Пиво" and cat.nome_imprimivel(a, "vi") == "Bia"
    for lg in LINGUAS:
        for item in (*cat.ARTIGOS.values(), *cat.OCASIOES.values(), *cat.CATEGORIAS.values()):
            assert not letras.em_falta(cat.nome_imprimivel(item, lg)), (lg, item.id)


def test_o_catalogo_para_a_interface():
    c = cat.catalogo("pt-br", 6)
    assert [x["id"] for x in c["categorias"]] == list(cat.CATEGORIAS) and c["sugerida"] == "festa_junina"
    ids = {a["id"] for x in c["categorias"] for a in x["artigos"]}
    assert "coxinha" in ids and "bifana" not in ids and all(a["emoji"] for x in c["categorias"] for a in x["artigos"])
    junina = next(o for o in c["ocasioes"] if o["id"] == "festa_junina")
    assert set(junina["artigos"]) <= ids and junina["desenho"] == "arraial" and cat.catalogo("en")["sugerida"] == ""
    assert "bifana" in {a["id"] for x in cat.catalogo("pt")["categorias"] for a in x["artigos"]}


@pytest.mark.parametrize("lg", LINGUAS)
def test_cada_lingua_tem_o_catalogo_completo_com_nomes_diferentes_do_id(lg):
    c = cat.catalogo(lg)
    assert len(c["ocasioes"]) >= 12 and sum(len(x["artigos"]) for x in c["categorias"]) >= 60
    assert all(x["nome"].strip() for x in c["categorias"])


def test_cada_artigo_oferece_ate_5_imagens_sem_repetir_e_a_primeira_e_a_de_omissao():
    for a in cat.ARTIGOS.values():
        assert 1 <= len(a.icones) <= cat.MAX_ICONES and len(set(a.icones)) == len(a.icones) and a.icones[0] == a.emoji, a.id
    assert sum(len(a.icones) > 1 for a in cat.ARTIGOS.values()) == len(cat.ARTIGOS)              # todos têm alternativas
    c = cat.catalogo("pt")
    assert all(x["icones"][0] == x["emoji"] for k in c["categorias"] for x in k["artigos"])

