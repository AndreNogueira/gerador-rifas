"""O changelog do site: o formato do ficheiro, a API e a regra de que a 1.a versao e a que esta em producao."""
import re

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import VERSAO, changelog
from web.app import criar_app


def test_le_versoes_seccoes_e_itens_com_continuacao():
    texto = ("# T\n\nintro\n\n## 1.2.0 — 2026-01-02\n\n### Novo\n- um\n- dois que continua\n  na linha seguinte\n\n### Corrigido\n- tres\n\n"
             "## 1.1.0 - 2025-12-31\n\n### Melhorado\n- quatro\n")
    e = changelog.ler(texto)
    assert [(x.versao, x.data) for x in e] == [("1.2.0", "2026-01-02"), ("1.1.0", "2025-12-31")]
    assert [(s.titulo, s.itens) for s in e[0].seccoes] == [("Novo", ["um", "dois que continua na linha seguinte"]), ("Corrigido", ["tres"])]
    assert e[1].seccoes[0].itens == ["quatro"]


def test_o_ficheiro_real_esta_bem_formado_e_a_1a_versao_e_a_do_servico():
    todas = changelog.entradas()
    assert todas and todas[0].versao == VERSAO, "acrescenta uma entrada ao src/web/CHANGELOG.md por cada versao nova"
    versoes = [e.versao for e in todas]
    chaves = [tuple(int(p) for p in v.split(".")) for v in versoes]
    assert chaves == sorted(chaves, reverse=True) and len(set(versoes)) == len(versoes)     # da mais recente para a mais antiga, sem repetidas
    for e in todas:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", e.data)
        assert e.seccoes and all(s.itens for s in e.seccoes), e.versao
        assert {s.titulo for s in e.seccoes} <= {"Novo", "Melhorado", "Corrigido"}, e.versao


def test_a_api_devolve_o_changelog_e_nao_se_indexa(tmp_path):
    with TestClient(criar_app(armazenamento=tmp_path)) as c:
        r = c.get("/api/changelog")
        assert r.status_code == 200 and r.headers["x-robots-tag"] == "noindex, nofollow"
        d = r.json()
        assert d["entradas"][0]["versao"] == VERSAO
        assert d["entradas"][0]["seccoes"][0]["itens"]
