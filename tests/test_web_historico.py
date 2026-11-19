"""O histórico permanente por dia (`web/historico.py`): grava o que acabou, preenche o passado que ainda há, e serve a vista de mais de 90 dias."""
import os
from datetime import date

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import INDEX, LISBOA, TOKEN, metricas_com_dados, ts
from web import historico
from web.app import criar_app
from web.historico import HistoricoDiario


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RELATORIO_FUSO", "DATABASE_URL", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA"):
        monkeypatch.delenv(nome, raising=False)


def preparar(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    return m, HistoricoDiario(caminho=tmp_path / "h.sqlite3")


def test_grava_o_que_ha_na_base_e_so_depois_dos_dados_existirem(tmp_path):
    m, h = preparar(tmp_path)
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 1)) == 9        # de 10 a 18 de novembro (o dia 9 é parcial: o 1.º registo é às 8h)
    dias = sorted(h.dias("2026-01-01", "2026-12-31"))
    assert dias[0] == "2026-11-10" and dias[-1] == "2026-11-18" and "2026-11-19" not in dias and "2026-11-09" not in dias
    ler = dict(h.ler("2026-11-18", "2026-11-18"))["2026-11-18"]
    assert ler["sessoes"] == {"Sessões": 5} and ler["numeros"] == {"Números": 6000.0}
    assert "comentarios" not in ler                                  # só o que não é zero


def test_nao_grava_antes_das_zero_e_cinco_nem_duas_vezes(tmp_path):
    m, h = preparar(tmp_path)
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 0, 2)) == 0
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 0, 6)) == 9
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 9)) == 0          # ontem já está: nem consulta a base
    assert historico.gravar_pendentes(None, m, None, LISBOA, ts(2026, 11, 19, 9)) == 0


def test_a_base_em_baixo_nao_grava_zeros_falsos(tmp_path):
    m, h = preparar(tmp_path)
    m._consultar = lambda *a, **k: (setattr(m, "erro_bd", True), [])[1]
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 1)) == 0 and h.total() == 0


def test_regravar_um_dia_substitui_o_resumo(tmp_path):
    _, h = preparar(tmp_path)
    h.gravar("2026-11-18", {"sessoes": {"Sessões": 1}}, 1)
    h.gravar("2026-11-18", {"sessoes": {"Sessões": 9}}, 2)
    assert h.total() == 1 and h.ler("2026-11-18", "2026-11-18") == [("2026-11-18", {"sessoes": {"Sessões": 9}})]


def test_a_vista_historica_tem_a_mesma_forma_e_marca_os_dias_sem_registo(tmp_path):
    m, h = preparar(tmp_path)
    historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 1))
    ev = historico.evolucao_historica(h, m, None, LISBOA, 200, ts(2026, 11, 19, 12))
    assert ev["origem"] == "historico" and ev["dias"] == 200 and len(ev["dias_lista"]) == 200 and ev["dias_lista"][-1] == "2026-11-18"
    sessoes = next(p for p in ev["paineis"] if p["id"] == "sessoes")["series"][0]["valores"]
    assert sessoes[-1] == 5 and sessoes[-2] == 2 and sessoes[0] is None and ev["dias_com_dados"] == 9      # o passado sem registo é «sem dados», não zero
    assert all({"id", "grupo", "titulo", "series", "tipo", "unidade", "agregado", "rotulos", "explica"} <= set(p) for p in ev["paineis"])
    assert date.fromisoformat(ev["dias_lista"][0]) < date(2026, 5, 4)


@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    c = TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})
    c.post("/api/admin/entrar", json={"token": TOKEN})
    return c


def test_o_painel_serve_mais_de_90_dias_a_partir_do_historico(admin):
    admin.app.state.servico.historico.gravar("2026-01-05", {"sessoes": {"Sessões": 12}}, 1)
    assert admin.get("/api/admin/evolucao", params={"dias": 90}).json().get("origem") is None             # até 90 dias: a vista de sempre
    r = admin.get("/api/admin/evolucao", params={"dias": 730})
    assert r.status_code == 200 and r.json()["origem"] == "historico" and r.json()["dias"] == 730
    assert admin.get("/api/admin/evolucao", params={"dias": 731}).status_code == 422


# ------------------------------------------------------------------ o upsert a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_grava_le_e_substitui():
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS historico_diario")
    h = HistoricoDiario(url_bd=URL_PG)
    h.gravar("2026-11-18", {"sessoes": {"Sessões": 1}}, 1)
    h.gravar("2026-11-18", {"sessoes": {"Sessões": 9}}, 2)
    h.gravar("2026-11-17", {"sessoes": {"Sessões": 3}}, 2)
    assert h.total() == 2 and h.primeiro() == "2026-11-17"
    assert h.ler("2026-11-17", "2026-11-18") == [("2026-11-17", {"sessoes": {"Sessões": 3}}), ("2026-11-18", {"sessoes": {"Sessões": 9}})]
