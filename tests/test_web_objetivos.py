"""Os objetivos diários (`web/objetivos.py`): as metas do dono, a avaliação do último dia e a secção do relatório por e-mail."""
import json
import os
from datetime import date

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import CHAVE, DESTINO, INDEX, LEITURA, LISBOA, TOKEN, Rede, metricas_com_dados, ts
from web import objetivos, relatorio
from web.app import criar_app
from web.objetivos import Objetivos
from web.relatorio import EstadoRelatorio, RelatoriosEnviados


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "DATABASE_URL", "PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)


# ------------------------------------------------------------------ as metas
def test_definir_ler_substituir_e_apagar(tmp_path):
    o = Objetivos(caminho=tmp_path / "o.sqlite3")
    assert o.todos() == {}
    o.definir("sessoes", 30)
    o.definir("numeros", 5000.5)
    o.definir("sessoes", 40)                                              # substitui
    assert o.todos() == {"sessoes": 40.0, "numeros": 5000.5}
    o.apagar("sessoes")
    assert o.todos() == {"numeros": 5000.5}


@pytest.mark.parametrize(("chave", "meta"), [("erros5xx", 5), ("sessoes", 0), ("sessoes", -3), ("sessoes", objetivos.META_MAX + 1)])
def test_recusa_chaves_e_metas_invalidas(tmp_path, chave, meta):
    with pytest.raises(ValueError):
        Objetivos(caminho=tmp_path / "o.sqlite3").definir(chave, meta)


# ------------------------------------------------------------------ a avaliação
def test_ontem_a_media_e_os_dias_cumpridos(tmp_path):
    m, _ = metricas_com_dados(tmp_path)                                  # 18 de nov: 5 sessões, 3 gerações; 12 a 17: 2 sessões por dia
    o = Objetivos(caminho=tmp_path / "o.sqlite3")
    o.definir("sessoes", 4)
    o.definir("geracoes", 10)
    e = objetivos.estado(m, None, o, LISBOA, ts(2026, 11, 19, 12))
    assert e["dia"] == "2026-11-18"
    k = {x["chave"]: x for x in e["kpis"]}
    assert k["sessoes"] | {"rotulo": "Sessões"} == {"chave": "sessoes", "rotulo": "Sessões", "meta": 4.0, "ontem": 5.0, "media7": pytest.approx(17 / 7), "dias_cumpridos": 1,
                                                   "dias": 7, "atingido": True, "pct": 125}
    assert k["geracoes"]["atingido"] is False and k["geracoes"]["ontem"] == 3 and k["geracoes"]["dias_cumpridos"] == 0
    assert k["descargas"]["meta"] is None and k["descargas"]["atingido"] is None and k["descargas"]["pct"] is None          # sem meta
    assert set(k) == set(objetivos.KPIS)


def test_sem_objetivos_nao_ha_seccao_no_relatorio(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    d = relatorio.montar(m, None, date(2026, 11, 18), LISBOA)
    assert d["objetivos"] == [] and "Objetivos do dia" not in relatorio.em_html(d) and "OBJETIVOS" not in relatorio.em_texto(d)


def test_o_relatorio_mostra_os_objetivos_cumpridos_e_falhados(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    r = relatorio.construir(m, None, date(2026, 11, 18), LISBOA, {"sessoes": 4.0, "geracoes": 10.0})
    assert "Objetivos do dia" in r["html"] and "✔" in r["html"] and "✘" in r["html"] and "125 %" in r["html"]
    assert "OBJETIVOS DO DIA" in r["texto"] and "✔ Sessões: 5 de 4 (125 %)" in r["texto"] and "✘ Gerações pedidas: 3 de 10 (30 %)" in r["texto"]
    d = relatorio.montar(m, None, date(2026, 11, 18), LISBOA, {"sessoes": 4.0, "geracoes": 10.0})
    assert any("Abaixo do objetivo" in t and "Gerações pedidas 3 de 10" in t and "Sessões" not in t for _, t in d["alertas"])


def test_o_envio_diario_leva_as_metas_do_dono(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)
    m, _ = metricas_com_dados(tmp_path)
    o = Objetivos(caminho=tmp_path / "o.sqlite3")
    o.definir("sessoes", 4)
    rede = Rede()
    assert relatorio.enviar_se_devido(RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), m, None, EstadoRelatorio(), ts(2026, 11, 19, 1), rede, objetivos=o) == "enviado"
    assert "Objetivos do dia" in json.loads(rede.pedidos[0].data)["html"]


def test_uma_base_de_objetivos_em_baixo_nao_impede_o_relatorio(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)
    m, _ = metricas_com_dados(tmp_path)

    class Avariada:
        def todos(self):
            raise RuntimeError("sem base")
    rede = Rede()
    assert relatorio.enviar_se_devido(RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), m, None, EstadoRelatorio(), ts(2026, 11, 19, 1), rede, objetivos=Avariada()) == "enviado"
    assert "Objetivos do dia" not in json.loads(rede.pedidos[0].data)["html"]


# ------------------------------------------------------------------ o painel
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def test_so_o_dono_define_metas_e_a_leitura_so_ve(admin):
    assert admin.get("/api/admin/objetivos").status_code == 404 and admin.put("/api/admin/objetivos", json={"chave": "sessoes", "meta": 5}).status_code == 404
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    assert admin.get("/api/admin/objetivos").status_code == 200
    assert admin.put("/api/admin/objetivos", json={"chave": "sessoes", "meta": 5}).status_code == 403
    admin.post("/api/admin/sair")
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    assert admin.put("/api/admin/objetivos", json={"chave": "sessoes", "meta": 5}).json() == {"chave": "sessoes", "meta": 5}
    kpis = {k["chave"]: k for k in admin.get("/api/admin/objetivos").json()["kpis"]}
    assert kpis["sessoes"]["meta"] == 5 and kpis["numeros"]["meta"] is None
    assert admin.put("/api/admin/objetivos", json={"chave": "sessoes", "meta": None}).status_code == 200            # sem meta: apaga
    assert {k["chave"]: k for k in admin.get("/api/admin/objetivos").json()["kpis"]}["sessoes"]["meta"] is None


def test_o_painel_recusa_chaves_e_metas_invalidas(admin):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    for corpo in ({"chave": "erros5xx", "meta": 5}, {"chave": "sessoes", "meta": 0}, {"chave": "sessoes", "meta": -1}, {"chave": "sessoes", "meta": 1e12}):
        assert admin.put("/api/admin/objetivos", json=corpo).status_code == 422, corpo


def test_a_previa_do_relatorio_inclui_os_objetivos(admin):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    admin.put("/api/admin/objetivos", json={"chave": "sessoes", "meta": 1})
    assert "Objetivos do dia" in admin.get("/api/admin/relatorio/previa").json()["html"]


# ------------------------------------------------------------------ o upsert a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_metas():
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS objetivos")
    o = Objetivos(url_bd=URL_PG)
    o.definir("sessoes", 30)
    o.definir("sessoes", 45.5)
    o.definir("numeros", 1000)
    assert o.todos() == {"sessoes": 45.5, "numeros": 1000.0}
    o.apagar("numeros")
    assert o.todos() == {"sessoes": 45.5}
