"""O Changelog e as páginas legais (Termos, Privacidade, Contacto) existem nas 18 línguas, com a mesma estrutura do português.

Regra do projeto (CLAUDE.md): o texto novo de uma funcionalidade e a sua entrada no Changelog traduzem-se para todas as línguas; sem estes testes a regra
apodrecia na versão seguinte. Os testes não avaliam a qualidade da tradução (não houve revisão nativa), só que nada falta nem sobra."""
import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import changelog, config, textos_legais
from web.app import criar_app

LINGUAS = list(i18n.LINGUAS)
OUTRAS = [lg for lg in LINGUAS if lg != "pt"]
MARCADOR = re.compile(r"\{(\w+)\}")


def _estrutura(entradas):
    return [(e.versao, e.data, [len(s.itens) for s in e.seccoes]) for e in entradas]


# ------------------------------------------------------------------ Changelog
def test_ha_um_changelog_por_lingua_e_nenhum_a_mais():
    ficheiros = {f.stem for f in changelog.PASTA.glob("*.md")}
    assert ficheiros == set(OUTRAS), f"faltam {set(OUTRAS) - ficheiros}; a mais {ficheiros - set(OUTRAS)}"


@pytest.mark.parametrize("lg", OUTRAS)
def test_o_changelog_traduzido_tem_as_mesmas_versoes_seccoes_e_itens_que_o_portugues(lg):
    assert _estrutura(changelog.entradas(lg)) == _estrutura(changelog.entradas("pt")), (
        f"changelog/{lg}.md tem de ter as mesmas versões, datas, secções e nº de itens que o CHANGELOG.md (acrescenta a versão nova às 17 línguas)")


@pytest.mark.parametrize("lg", OUTRAS)
def test_o_changelog_traduzido_tem_texto_a_sério(lg):
    pt = changelog.entradas("pt")
    for e, original in zip(changelog.entradas(lg), pt, strict=True):
        for s, so in zip(e.seccoes, original.seccoes, strict=True):
            assert s.titulo.strip() and s.titulo != so.titulo or lg == "pt", (lg, e.versao, "o título da secção está por traduzir")
            for item, item_pt in zip(s.itens, so.itens, strict=True):
                assert item.strip() and item != item_pt, (lg, e.versao, "item por traduzir")
                assert abs(len(item) - len(item_pt)) < len(item_pt) * 1.2 + 80, (lg, e.versao, "tamanho absurdo: erro de colagem?")
                assert item.count("**") % 2 == 0, (lg, e.versao, "negritos por fechar")


def test_a_lingua_desconhecida_ou_maliciosa_do_changelog_cai_no_portugues():
    for lg in ("xx", "../CHANGELOG", "pt/../en", "", "EN"):
        assert changelog.ficheiro(lg) == changelog.FICHEIRO


# ------------------------------------------------------------------ páginas legais
def _milhares_do_limite() -> str:
    return f"{config.max_numeros():,}".replace(",", " ")


def _paginas(lg: str) -> dict:
    mod = textos_legais._modulo(lg)
    return mod.TEXTOS


def test_ha_um_modulo_legal_por_lingua():
    pasta = Path(textos_legais.__file__).with_name("legal")
    assert {f.stem for f in pasta.glob("*.py")} - {"__init__"} == set(LINGUAS)


@pytest.mark.parametrize("lg", OUTRAS)
def test_as_paginas_legais_traduzidas_tem_as_mesmas_seccoes_paragrafos_e_marcadores_que_o_portugues(lg):
    pt, outra = _paginas("pt"), _paginas(lg)
    assert outra.keys() == pt.keys() == set(textos_legais.NOMES)
    for nome in pt:
        assert len(outra[nome]["seccoes"]) == len(pt[nome]["seccoes"]), (lg, nome)
        assert bool(outra[nome]["aviso"]) == bool(pt[nome]["aviso"]) and outra[nome]["titulo"].strip(), (lg, nome)
        for s, sp in zip(outra[nome]["seccoes"], pt[nome]["seccoes"], strict=True):
            assert s["titulo"].strip() and len(s["paragrafos"]) == len(sp["paragrafos"]), (lg, nome, sp["titulo"])
            for p, pp in zip(s["paragrafos"], sp["paragrafos"], strict=True):
                assert set(MARCADOR.findall(p)) == set(MARCADOR.findall(pp)), (lg, nome, "marcadores diferentes", p[:60])
    # o aviso de que é provisório e de que vale o português tem de estar nos Termos e na Privacidade
    for nome in ("termos", "privacidade"):
        assert "provisória" not in outra[nome]["aviso"] or lg == "pt"
        assert len(outra[nome]["aviso"]) > 60


@pytest.mark.parametrize("lg", OUTRAS)
def test_as_frases_de_cada_lingua_tem_os_mesmos_marcadores_que_as_portuguesas(lg):
    pt, outra = textos_legais._modulo("pt").FRASES, textos_legais._modulo(lg).FRASES
    assert outra.keys() == pt.keys()
    for k in pt:
        assert set(MARCADOR.findall(outra[k])) == set(MARCADOR.findall(pt[k])), (lg, k)
        assert outra[k].strip() and (outra[k] != pt[k] or k == "atualizado"), (lg, k)


@pytest.mark.parametrize("lg", LINGUAS)
def test_as_paginas_legais_renderizam_sem_marcadores_por_substituir_e_com_a_configuracao(lg, monkeypatch):
    monkeypatch.setenv("CONTACTO_EMAIL", "ola@exemplo.pt")
    monkeypatch.setenv("RESPONSAVEL", "Ana Silva")
    for nome in textos_legais.NOMES:
        d = textos_legais.pagina(nome, lg)
        texto = " ".join([d["titulo"], d["aviso"]] + [s["titulo"] + " " + " ".join(s["paragrafos"]) for s in d["seccoes"]])
        assert "{" not in texto and "}" not in texto, (lg, nome)
        assert d["titulo"] and d["seccoes"] and all(s["titulo"] and s["paragrafos"] for s in d["seccoes"])
    assert "ola@exemplo.pt" in str(textos_legais.pagina("contacto", lg)) and "Ana Silva" in str(textos_legais.pagina("termos", lg))
    assert _milhares_do_limite() in str(textos_legais.pagina("termos", lg))


@pytest.mark.parametrize("lg", LINGUAS)
def test_sem_configuracao_cada_lingua_diz_que_nao_ha_contacto(lg, monkeypatch):
    for v in ("CONTACTO_EMAIL", "RESPONSAVEL"):
        monkeypatch.delenv(v, raising=False)
    mod = textos_legais._modulo(lg)
    assert mod.FRASES["contacto_pagina_sem"] in textos_legais.pagina("contacto", lg)["seccoes"][0]["paragrafos"][0]
    assert "@" not in str(textos_legais.pagina("termos", lg))


# ------------------------------------------------------------------ a API entrega a língua pedida
@pytest.fixture
def c(tmp_path):
    with TestClient(criar_app(armazenamento=tmp_path)) as cliente:
        yield cliente


@pytest.mark.parametrize("lg", LINGUAS)
def test_a_api_entrega_o_changelog_e_as_paginas_na_lingua_do_pedido(c, lg):
    r = c.get("/api/changelog", headers={"X-Lingua": lg})
    assert r.status_code == 200 and "x-lingua" in r.headers["vary"].lower() and "accept-language" in r.headers["vary"].lower()
    assert _estrutura(changelog.entradas(lg)) == [(e["versao"], e["data"], [len(s["itens"]) for s in e["seccoes"]]) for e in r.json()["entradas"]]
    pt = c.get("/api/pagina/termos", headers={"X-Lingua": "pt"}).json()
    d = c.get("/api/pagina/termos", headers={"X-Lingua": lg}).json()
    assert (d["titulo"] == pt["titulo"]) == (lg == "pt")
    assert "x-lingua" in c.get("/api/pagina/termos", headers={"X-Lingua": lg}).headers["vary"].lower()


def test_sem_cabecalho_de_lingua_vale_a_do_browser_e_uma_desconhecida_cai_no_ingles(c):
    assert c.get("/api/pagina/termos", headers={"Accept-Language": "fr-FR,fr;q=0.9"}).json()["titulo"] == "Conditions d'utilisation"
    assert c.get("/api/pagina/termos", headers={"X-Lingua": "xx"}).json()["titulo"] == "Terms of use"
