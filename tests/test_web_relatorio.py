"""O relatório diário por e-mail (`web/relatorio.py`): o dia certo, o envio único, a falha que se repete, a privacidade e o painel."""
import json
import logging
import os
import urllib.error
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import config, email_envio, relatorio
from web.app import criar_app
from web.metricas import Metricas
from web.relatorio import EstadoRelatorio, RelatoriosEnviados

LISBOA = ZoneInfo("Europe/Lisbon")
CHAVE = "re_chave_secreta_de_teste_123456"
DESTINO = "dono.privado@exemplo.pt"
TOKEN = "palavra-passe-muito-longa-123"
LEITURA = "token-so-de-leitura-muito-comprido-9876"
INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'


def ts(ano, mes, dia, h=12, m=0) -> float:
    return datetime(ano, mes, dia, h, m, tzinfo=LISBOA).timestamp()


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "RELATORIO_EMAIL_DE", "RELATORIO_FUSO", "DATABASE_URL", "PUBLIC_URL",
                 "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def ligado(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", DESTINO)
    monkeypatch.setenv("PUBLIC_URL", "https://rifas.exemplo.pt")


class Relogio:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def metricas_com_dados(tmp_path):
    """Dias 10 a 18 de novembro de 2026 (Lisboa): 2 sessões por dia, 5 no dia 18 (o do relatório) e 7 já no dia 19 (que NÃO conta)."""
    rel = Relogio(ts(2026, 11, 9, 8))
    m = Metricas(tmp_path / "m.sqlite3", relogio=rel)
    for dia in range(10, 18):
        for i in range(2):
            rel.t = ts(2026, 11, dia, 10 + i)
            m.evento("sessao", "pt", "premiado", "computador")
    for i in range(5):
        rel.t = ts(2026, 11, 18, 9 + i)
        m.evento("sessao", "en" if i else "pt", "premiado", "telemovel")
    for i in range(2):
        rel.t = ts(2026, 11, 18, 15 + i)
        m.evento("geracao", "ok", "", "", 12.0, 3000.0, 30.0)
    rel.t = ts(2026, 11, 18, 20)
    m.evento("geracao", "falhou", "memoria", "", 4.0)
    rel.t = ts(2026, 11, 18, 21)
    m.evento("pais", "PT")
    for i in range(7):
        rel.t = ts(2026, 11, 19, 0, 10 + i)
        m.evento("sessao", "pt", "premiado", "computador")
    rel.t = ts(2026, 11, 19, 0, 30)
    return m, rel


# ------------------------------------------------------------------ o dia certo
def test_o_relatorio_conta_so_o_dia_que_acabou_e_compara_com_a_media(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    d = relatorio.montar(m, None, date(2026, 11, 18), LISBOA)
    destaques = {x["rotulo"]: x for x in d["destaques"]}
    assert destaques["Sessões"]["valor"] == 5                         # os 7 do dia 19 ficam de fora
    assert destaques["Sessões"]["media"] == pytest.approx(2.0)        # a média dos 7 dias anteriores
    assert destaques["Números gerados"]["valor"] == 6000
    assert destaques["Gerações pedidas"]["valor"] == 3                # 2 certas e 1 falhada
    assert d["dias_lista"][-1] == "2026-11-18" and len(d["dias_lista"]) == relatorio.JANELA_DIAS
    assert any("1 geração falhou" in t for _, t in d["alertas"])              # a geração falhada vira aviso
    assert not any("Ninguém abriu" in t for _, t in d["alertas"])


def test_um_dia_antigo_tambem_se_calcula_e_os_dados_incompletos_avisam(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    d = relatorio.montar(m, None, date(2026, 11, 14), LISBOA)
    assert {x["rotulo"]: x["valor"] for x in d["destaques"]}["Sessões"] == 2
    # o primeiro registo (o arranque) é de 9 de novembro às 8h: esse dia está incompleto, o 14 não
    assert any("Só há registos desde" in t for _, t in relatorio.montar(m, None, date(2026, 11, 9), LISBOA)["alertas"])
    assert not any("Só há registos desde" in t for _, t in d["alertas"])


def test_o_desvio_do_fuso_segue_o_verao_e_o_inverno():
    assert relatorio.janela_do_dia(date(2026, 7, 10), LISBOA)[0] == 60
    assert relatorio.janela_do_dia(date(2026, 11, 18), LISBOA)[0] == 0
    desvio, inicio, fim = relatorio.janela_do_dia(date(2026, 11, 18), LISBOA)
    assert fim - inicio == 86399


def test_se_a_base_estiver_em_baixo_nao_se_manda_um_relatorio_a_zeros(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    m.erro_bd = True
    m._consultar = lambda *a, **k: (setattr(m, "erro_bd", True), [])[1]
    with pytest.raises(relatorio.ErroRelatorio):
        relatorio.montar(m, None, date(2026, 11, 18), LISBOA)


# ------------------------------------------------------------------ o e-mail
def test_o_html_e_inline_pequeno_e_sem_scripts_nem_dados_pessoais(tmp_path, ligado):
    m, _ = metricas_com_dados(tmp_path)
    r = relatorio.construir(m, None, date(2026, 11, 18), LISBOA)
    h = r["html"]
    assert "<script" not in h.lower() and "<style" not in h.lower() and "<svg" not in h.lower()      # o Gmail ignora-os
    assert len(h.encode()) < 100_000                                                                  # acima disto o Gmail corta a mensagem
    assert "quarta-feira, 18 de novembro de 2026" in h and "https://rifas.exemplo.pt/admin" in h
    assert "▁" in h or "█" in h                                                                       # as miniaturas
    assert r["assunto"].startswith("Gerador de Rifas · 18 de nov: 5 sessões, 3 gerações")
    assert "Sessões" in r["texto"] and "<" not in r["texto"]
    for segredo in (CHAVE, DESTINO):
        assert segredo not in h and segredo not in r["texto"]


def test_os_nomes_das_series_escapam_se(tmp_path):
    m, rel = metricas_com_dados(tmp_path)
    rel.t = ts(2026, 11, 18, 22)
    m.evento("erro_http", "404", "<img src=x onerror=alert(1)>")
    h = relatorio.construir(m, None, date(2026, 11, 18), LISBOA)["html"]
    assert "<img" not in h


def test_os_numeros_formatam_se_em_portugues():
    assert relatorio._num(1234567) == "1 234 567" and relatorio._num(12.34) == "12,3" and relatorio._num(None) == "—" and relatorio._num(7, " MB") == "7 MB"
    assert relatorio.miniatura([0, 5, 10, None]) == "▁▅█·" and relatorio.miniatura([0, 0]) == "▁▁"
    assert relatorio._variacao(15, 10) == ("▲", "50 %") and relatorio._variacao(5, 10) == ("▼", "50 %") and relatorio._variacao(3, 0) == ("▲", "novo")
    assert relatorio.mascarar("ana@exemplo.pt") == "a**@exemplo.pt"


def test_os_alertas_apanham_erros_memoria_e_reinicios():
    def painel(id_, **series):
        return {"id": id_, "series": [{"nome": n, "valores": v} for n, v in series.items()]}
    paineis = {p["id"]: p for p in (
        painel("pedidos", **{"Erros do servidor (5xx)": [0, 0, 3]}), painel("memoria", Contentor=[300, 450]), painel("motor", **{"Reinícios do motor": [0, 2], "Arranques do serviço": [1, 4]}),
        painel("latencia", **{"95 % até": [100, 2200]}), painel("sessoes", Sessões=[1, 0]))}
    textos = " | ".join(t for _, t in relatorio.alertas({"dados_desde": 0}, paineis, date(2026, 11, 18), 1))
    assert "5xx" in textos and "450" in textos and "reiniciou 2" in textos and "arrancou 4" in textos and "2 200" in textos and "Ninguém abriu" in textos


# ------------------------------------------------------------------ o agendador
class Resposta:
    def __init__(self, corpo=b'{"id": "email-1"}'):
        self.corpo = corpo

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.corpo


class Rede:
    """Um `urlopen` falso: guarda os pedidos e, se `falhas` > 0, falha essas vezes primeiro."""
    def __init__(self, falhas=0, erro=None):
        self.pedidos, self.falhas, self.erro = [], falhas, erro or urllib.error.HTTPError("https://api.resend.com/emails", 403, "proibido", {}, None)

    def __call__(self, pedido, timeout=0):
        self.pedidos.append(pedido)
        if self.falhas > 0:
            self.falhas -= 1
            raise self.erro
        return Resposta()


def preparar(tmp_path):
    m, _ = metricas_com_dados(tmp_path)
    return m, RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoRelatorio()


def test_sem_chave_ou_destino_nao_faz_nada(tmp_path, monkeypatch):
    m, rel, est = preparar(tmp_path)
    rede = Rede()
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 1), rede) == "desligado"
    monkeypatch.setenv("RESEND_API_KEY", CHAVE)                                    # só a chave: falta o destino
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 1), rede) == "desligado" and rede.pedidos == []


def test_antes_das_zero_e_cinco_ainda_nao_envia(tmp_path, ligado):
    m, rel, est = preparar(tmp_path)
    rede = Rede()
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 0, 3), rede) == "cedo" and rede.pedidos == []


def test_envia_uma_so_vez_por_dia_mesmo_com_varios_arranques(tmp_path, ligado):
    m, rel, est = preparar(tmp_path)
    rede = Rede()
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 0, 6), rede) == "enviado"
    outro = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3")                      # um segundo arranque sobreposto, com a mesma base
    for agora in (ts(2026, 11, 19, 0, 11), ts(2026, 11, 19, 9)):
        assert relatorio.enviar_se_devido(outro, m, None, EstadoRelatorio(), agora, rede) == "ja_enviado"
    assert len(rede.pedidos) == 1
    corpo = json.loads(rede.pedidos[0].data)
    assert corpo["to"] == [DESTINO] and corpo["from"].endswith("<onboarding@resend.dev>") and "5 sessões" in corpo["subject"]
    assert rede.pedidos[0].get_header("Authorization") == f"Bearer {CHAVE}"
    assert rel.ultimo()["dia"] == "2026-11-18"


def test_o_servico_que_dormiu_toda_a_noite_envia_ao_acordar(tmp_path, ligado):
    m, rel, est = preparar(tmp_path)
    rede = Rede()
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 7, 30), rede) == "enviado" and len(rede.pedidos) == 1


def test_o_dia_seguinte_envia_outro(tmp_path, ligado):
    m, rel, est = preparar(tmp_path)
    rede = Rede()
    relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 1), rede)
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 20, 1), rede) == "enviado" and len(rede.pedidos) == 2


def test_uma_falha_desfaz_a_reserva_e_tenta_outra_vez_uma_hora_depois(tmp_path, ligado, caplog):
    m, rel, est = preparar(tmp_path)
    rede = Rede(falhas=1)
    with caplog.at_level(logging.DEBUG):
        assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 1), rede) == "falhou"
        assert rel.ultimo() is None and est.ultimo_erro == "HTTP 403"             # a reserva desfez-se: nada ficou por enviar
        assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 1, 30), rede) == "espera" and len(rede.pedidos) == 1
        assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 2, 10), rede) == "enviado" and len(rede.pedidos) == 2
    assert est.ultimo_erro == ""
    texto = caplog.text + est.ultimo_erro
    assert CHAVE not in texto and DESTINO not in texto and "api.resend.com" not in texto


def test_a_base_em_baixo_ou_o_servidor_de_email_morto_nao_levantam_excecoes(tmp_path, ligado):
    m, rel, est = preparar(tmp_path)
    rede = Rede(falhas=1, erro=urllib.error.URLError(f"https://api.resend.com falhou para {DESTINO} com {CHAVE}"))
    assert relatorio.enviar_se_devido(rel, m, None, est, ts(2026, 11, 19, 1), rede) == "falhou"
    assert est.ultimo_erro == "URLError" and DESTINO not in est.ultimo_erro and CHAVE not in est.ultimo_erro      # só a classe


def test_o_email_envio_recusa_sem_chave_ou_destino():
    with pytest.raises(email_envio.ErroEmail):
        email_envio.enviar("", "a@b.pt", ["c@d.pt"], "x", "<p>x</p>", "x", Rede())
    with pytest.raises(email_envio.ErroEmail):
        email_envio.enviar(CHAVE, "a@b.pt", [], "x", "<p>x</p>", "x", Rede())


def test_a_configuracao_valida_os_enderecos_e_o_fuso(monkeypatch):
    monkeypatch.setenv("RELATORIO_EMAIL_PARA", "a@b.pt, mau, c@d.com;rm, e@f.org, g@h.net, i@j.io")
    assert config.relatorio_destinos() == ["a@b.pt", "e@f.org", "g@h.net"]                  # inválidos fora; no máximo 3
    monkeypatch.setenv("RELATORIO_EMAIL_DE", "Rifas <rifas@exemplo.pt>")
    assert config.relatorio_remetente() == "Rifas <rifas@exemplo.pt>"
    monkeypatch.setenv("RELATORIO_EMAIL_DE", "Rifas <rifas@exemplo.pt>\r\nBcc: x@y.pt")
    assert config.relatorio_remetente().endswith("<onboarding@resend.dev>")                 # sem cabeçalhos injetados
    monkeypatch.setenv("RELATORIO_FUSO", "Marte/Olympus")
    assert config.relatorio_fuso() == "Europe/Lisbon"
    monkeypatch.setenv("RELATORIO_FUSO", "America/Sao_Paulo")
    assert config.relatorio_fuso() == "America/Sao_Paulo"


# ------------------------------------------------------------------ o painel
def _cliente(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    return _cliente(tmp_path)


def test_as_rotas_do_relatorio_so_existem_com_sessao_e_o_envio_so_para_o_dono(admin, ligado, monkeypatch):
    enviados = []
    monkeypatch.setattr(email_envio, "enviar", lambda *a, **k: enviados.append(a) or "id")
    for rota in ("/api/admin/relatorio", "/api/admin/relatorio/previa"):
        assert admin.get(rota).status_code == 404                                           # sem sessão: não existe
    assert admin.post("/api/admin/relatorio/enviar").status_code == 404
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    assert admin.get("/api/admin/relatorio").status_code == 200 and admin.get("/api/admin/relatorio/previa").status_code == 200
    assert admin.post("/api/admin/relatorio/enviar").status_code == 403 and enviados == []   # a leitura não manda e-mails
    admin.post("/api/admin/sair")
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    r = admin.post("/api/admin/relatorio/enviar")
    assert r.status_code == 200 and len(enviados) == 1 and enviados[0][3].startswith("[Teste] ")


def test_o_estado_mostra_o_destino_mascarado_e_nunca_a_chave(admin, ligado):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    d = admin.get("/api/admin/relatorio").json()
    assert d["ativo"] is True and d["destinos"] == ["d" + "*" * 11 + "@exemplo.pt"] and d["fuso"] == "Europe/Lisbon" and d["ultimo"] is None
    assert CHAVE not in json.dumps(d) and DESTINO not in json.dumps(d)


def test_desligado_o_painel_diz_porque_e_o_envio_da_409(admin):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    assert admin.get("/api/admin/relatorio").json()["ativo"] is False
    r = admin.post("/api/admin/relatorio/enviar")
    assert r.status_code == 409 and "RESEND_API_KEY" in r.json()["detail"]


def test_a_previa_traz_o_relatorio_de_ontem_e_valida_o_dia(admin):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    d = admin.get("/api/admin/relatorio/previa").json()
    assert set(d) >= {"assunto", "html", "texto", "dia"} and "Gerador de Rifas" in d["html"]
    assert admin.get("/api/admin/relatorio/previa", params={"dia": "ontem"}).status_code == 422
    assert admin.get("/api/admin/relatorio/previa", params={"dia": "2999-01-01"}).status_code == 422
    assert admin.get("/api/admin/relatorio/previa", params={"dia": "2001-01-01"}).status_code == 422


def test_um_erro_de_envio_no_painel_nao_mostra_enderecos(admin, ligado, monkeypatch):
    def mau(*a, **k):
        raise email_envio.ErroEmail("HTTP 403")
    monkeypatch.setattr(email_envio, "enviar", mau)
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    r = admin.post("/api/admin/relatorio/enviar")
    assert r.status_code == 502 and "HTTP 403" in r.json()["detail"] and CHAVE not in r.text and DESTINO not in r.text


# ------------------------------------------------------------------ a reserva a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_so_uma_reserva_por_dia_e_libertar_volta_a_permitir():
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS relatorios")
    a, b = RelatoriosEnviados(url_bd=URL_PG), RelatoriosEnviados(url_bd=URL_PG)         # dois serviços sobrepostos
    assert a.reservar("2026-11-18", 1_800_000_000) is True
    assert b.reservar("2026-11-18", 1_800_000_001) is False
    assert a.ultimo() == {"dia": "2026-11-18", "enviado": 1_800_000_000}
    b.libertar("2026-11-18")
    assert b.reservar("2026-11-18", 1_800_000_002) is True and a.ultimo()["enviado"] == 1_800_000_002


def test_os_paises_aparecem_por_extenso_e_os_alertas_usam_o_singular():
    assert relatorio._serie({"nome": "PT", "valores": [1, 2]}, True)["nome"] == "Portugal (PT)"
    assert relatorio._serie({"nome": "??", "valores": [1, 2]}, True)["nome"] == "Desconhecido"
    assert relatorio._serie({"nome": "ZZ", "valores": [1, 2]}, True)["nome"] == "ZZ"
    assert relatorio._serie({"nome": "PT", "valores": [1, 2]})["nome"] == "PT"                 # fora dos painéis de países não se mexe
    assert relatorio._pl(1, "pedido acabou", "pedidos acabaram") == "1 pedido acabou" and relatorio._pl(3, "vez", "vezes") == "3 vezes"
