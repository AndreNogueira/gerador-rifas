"""As quotas do alojamento gratuito (`web/quotas.py`): horas do Render no mês e espaço da base no Neon."""
import os
from datetime import date, datetime, timezone

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import INDEX, LEITURA, LISBOA, TOKEN, Relogio
from web import quotas, relatorio
from web.app import criar_app
from web.metricas import Metricas


def utc(ano, mes, dia, h=0, m=0) -> float:
    return datetime(ano, mes, dia, h, m, tzinfo=timezone.utc).timestamp()


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RENDER_HORAS_LIMITE", "NEON_LIMITE_MB", "DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)


def acordado(tmp_path, horas_por_dia: dict[int, list[int]], agora=None):
    """Um `Metricas` com amostras do sistema nas horas pedidas de cada dia de novembro de 2026 (UTC); `dia: [horas]`."""
    rel = Relogio(utc(2026, 11, 1))
    m = Metricas(tmp_path / "m.sqlite3", relogio=rel)
    for dia, horas in horas_por_dia.items():
        for h in horas:
            for minuto in (0, 30):                                          # duas amostras na mesma hora contam uma hora
                rel.t = utc(2026, 11, dia, h, minuto)
                m.amostrar(10.0, 100.0, 50.0, 200.0, 40.0, 1, 0)
    rel.t = agora or utc(2026, 11, 19, 12)
    return m, rel


def test_conta_horas_distintas_e_nao_amostras(tmp_path):
    m, _ = acordado(tmp_path, {1: [0, 1, 2], 2: [5]})
    assert m.horas_acordado(int(utc(2026, 11, 1))) == 4
    assert m.horas_acordado(int(utc(2026, 11, 2))) == 1                     # só do dia 2 em diante


def test_as_horas_do_mes_a_projecao_e_o_aviso(tmp_path, monkeypatch):
    m, _ = acordado(tmp_path, {d: list(range(24)) for d in range(1, 19)})                      # 18 dias sempre acordado = 432 h
    e = quotas.estado(m, utc(2026, 11, 19, 12))
    r = e["render"]
    assert r["gastas"] == 432 and r["limite"] == 750 and r["pct"] == 58 and r["mes"] == "2026-11" and r["horas_do_mes"] == 720
    assert r["projecao"] == round(432 / 444 * 720) and r["decorridas"] == 444                     # ritmo: 432 h em 444 h decorridas (18 dias e meio)
    assert e["avisos"] == [] and e["neon"] is None                                                # SQLite: sem espaço do Neon
    monkeypatch.setenv("RENDER_HORAS_LIMITE", "450")                                               # 432 de 450 = 96 %
    aviso = quotas.estado(m, utc(2026, 11, 19, 12))["avisos"]
    assert len(aviso) == 1 and "432" in aviso[0] and "450" in aviso[0]


def test_sem_um_dia_inteiro_ainda_nao_ha_projecao(tmp_path):
    m, _ = acordado(tmp_path, {1: [0, 1, 2]}, agora=utc(2026, 11, 1, 5))
    r = quotas.estado(m, utc(2026, 11, 1, 5))["render"]
    assert r["gastas"] == 3 and r["projecao"] is None


def test_diz_desde_quando_ha_dados_se_o_mes_ja_ia_a_meio(tmp_path):
    rel = Relogio(utc(2026, 11, 10))
    m = Metricas(tmp_path / "m.sqlite3", relogio=rel)                                              # a base só existe desde 10 de novembro
    rel.t = utc(2026, 11, 19, 12)
    assert quotas.estado(m, rel.t)["render"]["dados_desde"] == int(utc(2026, 11, 10))
    cedo = Metricas(tmp_path / "n.sqlite3", relogio=Relogio(utc(2026, 10, 20)))
    assert quotas.estado(cedo, utc(2026, 11, 19, 12))["render"]["dados_desde"] is None             # já havia dados antes do mês: nada a avisar


def test_limites_invalidos_voltam_ao_valor_por_omissao(monkeypatch):
    monkeypatch.setenv("RENDER_HORAS_LIMITE", "muitas")
    monkeypatch.setenv("NEON_LIMITE_MB", "0")
    assert quotas.limite_horas() == 750 and quotas.limite_mb() == 1


def test_o_painel_horas_acordado_aparece_na_evolucao(tmp_path):
    m, _ = acordado(tmp_path, {17: list(range(24)), 18: [3, 4]})
    ev = m.evolucao(3, 0, None, utc(2026, 11, 18, 23))
    horas = next(p for p in ev["paineis"] if p["id"] == "horas")
    assert horas["unidade"] == " h" and horas["series"][0]["valores"] == [0.0, 24.0, 2.0]


def test_o_relatorio_diario_leva_o_aviso_de_quotas(tmp_path, monkeypatch):
    m, rel = acordado(tmp_path, {d: list(range(24)) for d in range(1, 19)}, agora=utc(2026, 11, 19, 0, 30))
    monkeypatch.setenv("RENDER_HORAS_LIMITE", "450")
    d = relatorio.montar(m, None, date(2026, 11, 18), LISBOA)
    assert any("horas do mês no Render" in t for _, t in d["alertas"])


# ------------------------------------------------------------------ o painel
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def test_a_rota_das_quotas_so_existe_com_sessao_e_a_leitura_pode_ver(admin):
    assert admin.get("/api/admin/quotas").status_code == 404
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    r = admin.get("/api/admin/quotas")
    assert r.status_code == 200 and set(r.json()) == {"render", "neon", "avisos"} and r.json()["render"]["limite"] == 750 and r.json()["neon"] is None


# ------------------------------------------------------------------ o espaço a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_espaco_da_base_e_tabelas():
    m = Metricas(url_bd=URL_PG)
    m.amostrar(10.0, 100.0, 50.0, 200.0, 40.0, 1, 0)
    m.descarregar(tudo=True)
    e = m.espaco_bd()
    assert e["total_mb"] > 0 and any(t["nome"] == "sistema" for t in e["tabelas"]) and all(t["mb"] >= 0 for t in e["tabelas"])
    assert m.horas_acordado(0) >= 1
    est = quotas.estado(m)
    assert est["neon"]["limite_mb"] == 512 and est["neon"]["pct"] >= 0
