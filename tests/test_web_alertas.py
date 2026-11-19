"""Os alertas imediatos por e-mail (`web/alertas.py`): quando disparam, que não se repetem, que não vazam nada e o painel."""
import json
import os
import urllib.error

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import CHAVE, DESTINO, INDEX, TOKEN, LEITURA, Rede, Relogio
from web import alertas, email_envio
from web.alertas import AlertasEnviados, EstadoAlertas
from web.app import criar_app
from web.metricas import Metricas

T0 = 1_800_000_000.0


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "ALERTAS_EMAIL", "DATABASE_URL", "PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def ligado(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)


def preparar(tmp_path):
    rel = Relogio(T0)
    return Metricas(tmp_path / "m.sqlite3", relogio=rel), rel, AlertasEnviados(caminho=tmp_path / "a.sqlite3"), EstadoAlertas()


def erros(m, rel, n, grupo="POST /api/sessoes"):
    for _ in range(n):
        m.pedido(grupo, 500, 10.0)


def test_cinco_erros_5xx_em_quinze_minutos_disparam_e_menos_nao(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    erros(m, rel, 4)
    assert alertas.verificar_e_enviar(a, m, est, T0, Rede()) == "nada"
    erros(m, rel, 1)
    rede = Rede()
    assert alertas.verificar_e_enviar(a, m, est, T0 + 60, rede) == "enviado"
    corpo = json.loads(rede.pedidos[0].data)
    assert "5xx" in corpo["subject"] and corpo["to"] == [DESTINO] and "5 pedidos" in corpo["text"]


def test_a_sondagem_do_progresso_nao_conta_como_erro(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    erros(m, rel, 9, "GET /api/sessoes/{id_}/trabalho")
    assert alertas.verificar_e_enviar(a, m, est, T0, Rede()) == "nada"


def test_erros_antigos_saem_da_janela(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    erros(m, rel, 6)
    assert alertas.verificar_e_enviar(a, m, est, T0 + 16 * 60, Rede()) == "nada"


def test_nao_se_repete_durante_seis_horas_e_repete_depois(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    rede = Rede()
    erros(m, rel, 6)
    assert alertas.verificar_e_enviar(a, m, est, T0, rede) == "enviado"
    assert alertas.verificar_e_enviar(a, m, est, T0 + 120, rede) == "nada"                      # continua mau, mas já se avisou
    outro = AlertasEnviados(caminho=tmp_path / "a.sqlite3")                                     # um arranque novo, a mesma base
    assert alertas.verificar_e_enviar(outro, m, EstadoAlertas(), T0 + 300, rede) == "nada"
    rel.t = T0 + 6 * 3600 + 10
    erros(m, rel, 6)                                                                            # as regras olham para os últimos 15 minutos
    m._recentes["5xx"].extend([T0 + 6 * 3600] * 6)
    assert alertas.verificar_e_enviar(a, m, est, T0 + 6 * 3600 + 20, rede) == "enviado" and len(rede.pedidos) == 2


def test_as_condicoes_que_aparecem_juntas_vao_num_so_email(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    erros(m, rel, 5)
    m.evento("motor_reiniciado")
    m.evento("motor_reiniciado")
    m.amostrar(10.0, 200.0, 100.0, 480.0, 40.0, 1, 0)
    rede = Rede()
    assert alertas.verificar_e_enviar(a, m, est, T0 + 5, rede) == "enviado" and len(rede.pedidos) == 1
    texto = json.loads(rede.pedidos[0].data)["text"]
    assert "5xx" in texto and "reiniciou 2" in texto and "480 MB" in texto


def test_a_base_em_baixo_so_avisa_depois_de_duas_verificacoes(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    m.erro_bd = True
    rede = Rede()
    assert alertas.verificar_e_enviar(a, m, est, T0, rede) == "nada"
    assert alertas.verificar_e_enviar(a, m, est, T0 + 60, rede) == "enviado" and "Base de dados" in json.loads(rede.pedidos[0].data)["subject"]
    m.erro_bd = False
    alertas.verificar_e_enviar(a, m, est, T0 + 120, rede)
    assert est.bd_falhas_seguidas == 0


def test_uma_falha_de_envio_desfaz_a_reserva_espera_e_tenta_outra_vez(tmp_path, ligado):
    m, rel, a, est = preparar(tmp_path)
    erros(m, rel, 6)
    rede = Rede(falhas=1, erro=urllib.error.URLError(f"falhou {DESTINO} {CHAVE}"))
    assert alertas.verificar_e_enviar(a, m, est, T0, rede) == "falhou" and a.ultimos() == {}
    assert est.ultimo_erro == "URLError" and CHAVE not in est.ultimo_erro and DESTINO not in est.ultimo_erro
    assert alertas.verificar_e_enviar(a, m, est, T0 + 60, rede) == "espera"
    rel.t = T0 + alertas.ESPERA_APOS_FALHA_S + 1
    erros(m, rel, 6)                                                                            # o problema continua: as regras só olham para os últimos 15 minutos
    assert alertas.verificar_e_enviar(a, m, est, rel.t, rede) == "enviado" and est.ultimo_erro == ""


def test_desligado_sem_chave_ou_com_alertas_email_zero(tmp_path, monkeypatch, ligado):
    m, rel, a, est = preparar(tmp_path)
    erros(m, rel, 6)
    monkeypatch.setenv("ALERTAS_EMAIL", "0")
    assert alertas.verificar_e_enviar(a, m, est, T0, Rede()) == "desligado"
    monkeypatch.delenv("ALERTAS_EMAIL")
    monkeypatch.delenv("RESEND_API_KEY")
    assert alertas.verificar_e_enviar(a, m, est, T0, Rede()) == "desligado" and alertas.verificar_e_enviar(None, m, est, T0, Rede()) == "desligado"


def test_o_email_escapa_o_texto_e_nao_leva_dados_pessoais(ligado):
    assunto, corpo, texto = alertas.montar({"erros5xx": "<script>alert(1)</script>"}, T0, "https://rifas.exemplo.pt")
    assert "<script>" not in corpo and "https://rifas.exemplo.pt/admin" in corpo and "https://rifas.exemplo.pt/admin" in texto
    assert CHAVE not in corpo + texto and DESTINO not in corpo + texto


# ------------------------------------------------------------------ o painel
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def test_o_estado_do_relatorio_traz_as_regras_dos_alertas(admin, ligado):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    a = admin.get("/api/admin/relatorio").json()["alertas"]
    assert a["ativo"] is True and a["espera_h"] == 6 and [r["chave"] for r in a["regras"]] == ["erros5xx", "reinicios", "memoria", "base_de_dados"]
    assert set(a["ultimos"]) == {"erros5xx", "reinicios", "memoria", "base_de_dados"}


def test_o_alerta_de_teste_so_o_dono_e_so_ligado(admin, ligado, monkeypatch):
    enviados = []
    monkeypatch.setattr(email_envio, "enviar", lambda *a, **k: enviados.append(a) or "id")
    assert admin.post("/api/admin/relatorio/alerta-teste").status_code == 404
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    assert admin.post("/api/admin/relatorio/alerta-teste").status_code == 403 and enviados == []
    admin.post("/api/admin/sair")
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    assert admin.post("/api/admin/relatorio/alerta-teste").status_code == 200 and enviados[0][3].startswith("[Teste] ")


def test_alerta_de_teste_desligado_da_409(admin):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    assert admin.post("/api/admin/relatorio/alerta-teste").status_code == 409


# ------------------------------------------------------------------ a reserva com espera, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_reserva_com_espera():
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS alertas")
    a, b = AlertasEnviados(url_bd=URL_PG), AlertasEnviados(url_bd=URL_PG)
    assert a.reservar("erros5xx", 1000, 100) is True
    assert b.reservar("erros5xx", 1050, 100) is False                                           # dentro da espera
    assert b.reservar("erros5xx", 1101, 100) is True and a.ultimos() == {"erros5xx": 1101}
    b.libertar("erros5xx")
    assert a.ultimos() == {}
