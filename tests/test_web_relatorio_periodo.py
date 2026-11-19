"""Os resumos semanal e mensal por e-mail (`web/relatorio_periodo.py`): os períodos, as somas face ao anterior, o envio único e o painel."""
import json
import urllib.error
from datetime import date, timedelta

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import CHAVE, DESTINO, INDEX, LEITURA, LISBOA, TOKEN, Rede, ts
from web import email_envio, relatorio_periodo as rp
from web.app import criar_app
from web.historico import HistoricoDiario
from web.metricas import Metricas
from web.relatorio import ErroRelatorio, EstadoRelatorio, RelatoriosEnviados


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "RELATORIOS_PERIODICOS", "DATABASE_URL", "PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def ligado(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)


def historico_com(tmp_path, de: date, ate: date, sessoes=lambda d: 10, extra=None):
    h = HistoricoDiario(caminho=tmp_path / "h.sqlite3")
    d = de
    while d <= ate:
        dados = {"sessoes": {"Sessões": sessoes(d)}, "numeros": {"Números": 1000}, "memoria": {"Contentor": 300 + d.day}}
        if extra:
            dados.update(extra(d))
        h.gravar(d.isoformat(), dados, 1)
        d += timedelta(days=1)
    return h, Metricas(tmp_path / "m.sqlite3")


# ------------------------------------------------------------------ os períodos
def test_semana_mes_e_o_ultimo_periodo_completo():
    assert rp.semana_de(date(2026, 11, 18)) == (date(2026, 11, 16), date(2026, 11, 22))
    assert rp.semana_de(date(2026, 11, 22)) == (date(2026, 11, 16), date(2026, 11, 22))                 # o domingo é da semana que acaba
    assert rp.mes_de(date(2026, 2, 10)) == (date(2026, 2, 1), date(2026, 2, 28))
    assert rp.anterior("semana", date(2026, 11, 16)) == (date(2026, 11, 9), date(2026, 11, 15))
    assert rp.anterior("mes", date(2026, 3, 1)) == (date(2026, 2, 1), date(2026, 2, 28))
    assert rp.ultimo_completo("semana", date(2026, 11, 16)) == (date(2026, 11, 9), date(2026, 11, 15))   # na segunda
    assert rp.ultimo_completo("semana", date(2026, 11, 22)) == (date(2026, 11, 9), date(2026, 11, 15))   # o domingo ainda não acabou
    assert rp.ultimo_completo("mes", date(2026, 12, 1)) == (date(2026, 11, 1), date(2026, 11, 30))
    assert rp.ultimo_completo("mes", date(2026, 1, 15)) == (date(2025, 12, 1), date(2025, 12, 31))
    assert rp.chave_de("semana", date(2026, 11, 9)) == "semana:2026-11-09" and rp.chave_de("mes", date(2026, 11, 1)) == "mes:2026-11"


# ------------------------------------------------------------------ os números
def test_a_semana_soma_os_dias_e_compara_com_a_anterior(tmp_path):
    h, m = historico_com(tmp_path, date(2026, 11, 2), date(2026, 11, 15), sessoes=lambda d: 10 if d < date(2026, 11, 9) else 15,
                         extra=lambda d: {"pedidos": {"Erros do servidor (5xx)": 2}} if d == date(2026, 11, 12) else {})
    d = rp.montar_periodo(h, m, None, "semana", date(2026, 11, 9), date(2026, 11, 15), LISBOA)
    x = {e["rotulo"]: e for e in d["destaques"]}
    assert x["Sessões"]["valor"] == 105 and x["Sessões"]["media"] == 70 and x["Sessões"]["variacao"] == ("▲", "50 %")
    assert x["Números gerados"]["valor"] == 7000 and x["Erros 5xx"]["valor"] == 2
    assert any("5xx" in t for _, t in d["alertas"]) and not any("Só há" in t for _, t in d["alertas"])
    assert d["titulo"] == "Semana de 9 nov a 15 nov 2026" and d["nome"] == "resumo semanal" and d["colunas"][0] == "Período"
    memoria = next(s for g in d["grupos"].values() for p in g if p["titulo"].startswith("Memória") for s in p["series"])
    assert memoria["valor"] == 315                                              # um painel «max»: o pico do período (dia 15), não a soma
    assert len(memoria["miniatura"]) == 7


def test_dias_em_falta_avisam_e_sem_nenhum_nao_ha_resumo(tmp_path):
    h, m = historico_com(tmp_path, date(2026, 11, 12), date(2026, 11, 15))
    d = rp.montar_periodo(h, m, None, "semana", date(2026, 11, 9), date(2026, 11, 15), LISBOA)
    assert any("Só há 4 de 7 dias" in t for _, t in d["alertas"])
    with pytest.raises(ErroRelatorio):
        rp.montar_periodo(h, m, None, "semana", date(2026, 10, 12), date(2026, 10, 18), LISBOA)


def test_o_email_do_resumo_tem_o_titulo_e_as_colunas_do_periodo(tmp_path):
    h, m = historico_com(tmp_path, date(2026, 10, 1), date(2026, 11, 30))
    r = rp.construir_periodo(h, m, None, "mes", date(2026, 11, 1), date(2026, 11, 30), LISBOA)
    assert r["assunto"].startswith("Gerador de Rifas · novembro de 2026: 300 sessões") and "resumo mensal" in r["html"] and "Anterior" in r["html"]
    assert "<script" not in r["html"].lower() and CHAVE not in r["html"] + r["texto"] and DESTINO not in r["html"] + r["texto"]


# ------------------------------------------------------------------ o envio
def preparar(tmp_path, de=date(2026, 10, 1), ate=date(2026, 11, 30)):
    h, m = historico_com(tmp_path, de, ate)
    return h, m, RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoRelatorio()


def test_na_segunda_sai_a_semana_uma_so_vez(tmp_path, ligado):
    h, m, r, est = preparar(tmp_path, ate=date(2026, 11, 15))
    rede = Rede()
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 0, 2), rede) == []              # antes das 00:05
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 0, 10), rede) == ["semana:2026-11-09"]
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 9), rede) == [] and len(rede.pedidos) == 1
    outro = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3")
    assert rp.enviar_periodicos_se_devido(outro, h, m, None, EstadoRelatorio(), ts(2026, 11, 17, 9), rede) == [] and len(rede.pedidos) == 1
    assert "resumo semanal" in json.loads(rede.pedidos[0].data)["html"] and r.ultimo("semana")["dia"] == "semana:2026-11-09" and r.ultimo("dia") is None


def test_no_dia_1_sai_o_mes_e_na_quarta_ainda_se_apanha_a_semana_que_dormiu(tmp_path, ligado):
    h, m, r, est = preparar(tmp_path)
    rede = Rede()
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 12, 2, 8), rede) == ["semana:2026-11-23", "mes:2026-11"]           # o serviço dormia na segunda e no dia 1
    assert "novembro de 2026" in json.loads(rede.pedidos[1].data)["subject"]


def test_so_se_o_ultimo_dia_ja_esta_gravado_e_ha_metade_dos_dias(tmp_path, ligado):
    h, m, r, est = preparar(tmp_path, ate=date(2026, 11, 14))                       # falta o domingo 15
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), Rede()) == []
    (tmp_path / "b").mkdir()
    h2, m2, r2, est2 = preparar(tmp_path / "b", de=date(2026, 11, 15), ate=date(2026, 11, 15))
    assert rp.enviar_periodicos_se_devido(r2, h2, m2, None, est2, ts(2026, 11, 16, 1), Rede()) == []               # 1 dia em 7: pouco


def test_o_mes_so_se_apanha_nos_primeiros_sete_dias(tmp_path, ligado):
    h, m, r, est = preparar(tmp_path)
    assert "mes:2026-11" not in rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 12, 9, 1), Rede())


def test_falha_desfaz_a_reserva_espera_e_repete(tmp_path, ligado):
    h, m, r, est = preparar(tmp_path, ate=date(2026, 11, 15))
    rede = Rede(falhas=1, erro=urllib.error.URLError(f"x {DESTINO} {CHAVE}"))
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), rede) == [] and r.ultimo("semana") is None
    assert est.ultimo_erro == "URLError" and DESTINO not in est.ultimo_erro and CHAVE not in est.ultimo_erro
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1, 30), rede) == []                    # à espera
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 2, 10), rede) == ["semana:2026-11-09"]


def test_desligados_sem_email_ou_com_relatorios_periodicos_zero(tmp_path, monkeypatch, ligado):
    h, m, r, est = preparar(tmp_path, ate=date(2026, 11, 15))
    monkeypatch.setenv("RELATORIOS_PERIODICOS", "0")
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), Rede()) == []
    monkeypatch.delenv("RELATORIOS_PERIODICOS")
    monkeypatch.delenv("RESEND_API_KEY")
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), Rede()) == [] and rp.enviar_periodicos_se_devido(None, h, m, None, est) == []


# ------------------------------------------------------------------ o painel
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    c = TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})
    c.post("/api/admin/entrar", json={"token": TOKEN})
    return c


def test_a_previa_da_semana_e_do_mes_e_os_erros_de_pedido(admin):
    h = admin.app.state.servico.historico
    d = date.today() - timedelta(days=40)
    while d < date.today():
        h.gravar(d.isoformat(), {"sessoes": {"Sessões": 3}}, 1)
        d += timedelta(days=1)
    for tipo, nome in (("semana", "resumo semanal"), ("mes", "resumo mensal")):
        r = admin.get("/api/admin/relatorio/previa", params={"tipo": tipo})
        assert r.status_code == 200 and nome in r.json()["html"] and r.json()["tipo"] == tipo
    assert admin.get("/api/admin/relatorio/previa", params={"tipo": "ano"}).status_code == 422
    assert admin.get("/api/admin/relatorio/previa", params={"tipo": "semana", "dia": (date.today() - timedelta(days=400)).isoformat()}).status_code == 404   # sem dias gravados
    assert admin.get("/api/admin/relatorio/previa", params={"tipo": "semana", "dia": (date.today() - timedelta(days=5)).isoformat()}).status_code == 200
    e = admin.get("/api/admin/relatorio").json()
    assert e["periodicos"] is False and e["ultimo_semana"] is None and e["ultimo_mes"] is None


def test_o_teste_do_resumo_so_o_dono_e_so_ligado(admin, monkeypatch):
    enviados = []
    monkeypatch.setattr(email_envio, "enviar", lambda *a, **k: enviados.append(a) or "id")
    assert admin.post("/api/admin/relatorio/enviar", params={"tipo": "semana"}).status_code == 409
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)
    h = admin.app.state.servico.historico
    for i in range(1, 20):
        h.gravar((date.today() - timedelta(days=i)).isoformat(), {"sessoes": {"Sessões": 3}}, 1)
    assert admin.post("/api/admin/relatorio/enviar", params={"tipo": "semana"}).status_code == 200 and enviados[0][3].startswith("[Teste] ")
    assert admin.get("/api/admin/relatorio").json()["periodicos"] is True
