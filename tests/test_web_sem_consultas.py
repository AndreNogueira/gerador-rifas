"""Depois de tratado o dia, as rondas de 5 minutos (e as de 1 minuto dos alertas) já não tocam na base: o Neon gratuito pode adormecer entre meias-noites."""
from datetime import date

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from test_web_alertas import T0, erros, preparar as preparar_alertas
from test_web_relatorio import CHAVE, DESTINO, LISBOA, Rede, metricas_com_dados, ts
from web import alertas, historico, relatorio, relatorio_periodo as rp
from web.historico import HistoricoDiario
from web.relatorio import EstadoRelatorio, RelatoriosEnviados


class Contador:
    """Conta as consultas à base de uma tabela (`_executar` de um `BaseSql`)."""
    def __init__(self, tabela):
        self.n = 0
        original = tabela._executar

        def contado(*a, **k):
            self.n += 1
            return original(*a, **k)
        tabela._executar = contado


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "RELATORIOS_PERIODICOS", "ALERTAS_EMAIL", "DATABASE_URL", "PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)


def test_o_historico_depois_de_gravado_nao_volta_a_consultar_a_base(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    h = HistoricoDiario(caminho=tmp_path / "h.sqlite3")
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 0, 6)) == 9
    c = Contador(h)
    for minuto in range(11, 600, 5):                                   # as rondas das 00:11 às 10:00
        assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 0, 0) + minuto * 60) == 0
    assert c.n == 0
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 20, 0, 6)) >= 0 and c.n >= 1      # no dia seguinte volta a ver


def test_o_historico_que_ja_estava_completo_tambem_se_lembra(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    h = HistoricoDiario(caminho=tmp_path / "h.sqlite3")
    h.gravar("2026-11-18", {}, 1)
    assert historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 1)) == 0
    c = Contador(h)
    historico.gravar_pendentes(h, m, None, LISBOA, ts(2026, 11, 19, 2))
    assert c.n == 0


def test_o_relatorio_diario_enviado_ou_ja_enviado_nao_consulta_mais(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    r = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3")
    est = EstadoRelatorio()
    assert relatorio.enviar_se_devido(r, m, None, est, ts(2026, 11, 19, 1), Rede()) == "enviado"
    c = Contador(r)
    for h in range(2, 20):
        assert relatorio.enviar_se_devido(r, m, None, est, ts(2026, 11, 19, h), Rede()) == "ja_enviado"
    assert c.n == 0
    outro = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3")                 # um arranque novo: pergunta UMA vez e depois lembra-se
    est2 = EstadoRelatorio()
    c2 = Contador(outro)
    for h in range(2, 20):
        assert relatorio.enviar_se_devido(outro, m, None, est2, ts(2026, 11, 19, h), Rede()) == "ja_enviado"
    assert c2.n == 1


def test_os_resumos_decididos_nao_consultam_mais(tmp_path):
    from test_web_relatorio_periodo import historico_com

    h, m = historico_com(tmp_path, date(2026, 10, 1), date(2026, 11, 15))
    r, est = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoRelatorio()
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), Rede()) == ["semana:2026-11-09"]
    ch, cr = Contador(h), Contador(r)
    for hora in range(2, 20):
        assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, hora), Rede()) == []
    assert ch.n == 0 and cr.n == 0


def test_um_resumo_sem_dias_suficientes_com_o_historico_feito_e_definitivo(tmp_path):
    from test_web_relatorio_periodo import historico_com

    h, m = historico_com(tmp_path, date(2026, 11, 15), date(2026, 11, 15))            # 1 dia em 7
    r, est = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoRelatorio()
    h.feito_ate = "2026-11-15"
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), Rede()) == []
    ch = Contador(h)
    rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 2), Rede())
    assert ch.n == 0 and "semana:2026-11-09" in est.periodicos_tratados


def test_sem_o_historico_feito_a_decisao_nao_e_definitiva(tmp_path):
    from test_web_relatorio_periodo import historico_com

    h, m = historico_com(tmp_path, date(2026, 11, 9), date(2026, 11, 14))             # falta o domingo: o histórico ainda não gravou
    r, est = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoRelatorio()
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1), Rede()) == []
    h.gravar("2026-11-15", {"sessoes": {"Sessões": 1}}, 1)                             # entretanto grava-se
    assert rp.enviar_periodicos_se_devido(r, h, m, None, est, ts(2026, 11, 16, 1, 6), Rede()) == ["semana:2026-11-09"]


def test_um_alerta_que_continua_mau_so_consulta_a_base_uma_vez_por_espera(tmp_path):
    m, rel, a, est = preparar_alertas(tmp_path)
    erros(m, rel, 6)
    assert alertas.verificar_e_enviar(a, m, est, T0, Rede()) == "enviado"
    c = Contador(a)
    for minuto in range(1, 120):                                                          # duas horas a 1 verificação por minuto, sempre mau
        m._recentes["5xx"].extend([T0 + minuto * 60] * 6)
        assert alertas.verificar_e_enviar(a, m, est, T0 + minuto * 60, Rede()) == "nada"
    assert c.n == 0


def test_se_outro_arranque_ja_avisou_volta_a_ver_so_daqui_a_uma_hora(tmp_path):
    m, rel, a, est = preparar_alertas(tmp_path)
    a.reservar("erros5xx", T0, alertas.ESPERA_ENTRE_REPETICOES_S)                         # um arranque anterior já avisou
    erros(m, rel, 6)
    c = Contador(a)
    assert alertas.verificar_e_enviar(a, m, est, T0 + 60, Rede()) == "nada" and c.n == 1
    for minuto in range(2, 50):
        m._recentes["5xx"].extend([T0 + minuto * 60] * 6)
        alertas.verificar_e_enviar(a, m, est, T0 + minuto * 60, Rede())
    assert c.n == 1                                                                         # durante a hora seguinte não pergunta mais
