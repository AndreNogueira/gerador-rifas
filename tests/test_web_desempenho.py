"""O desempenho real nos browsers (LCP, CLS, INP): o que se guarda (três números e a classe do aparelho), o percentil 75 por dia e a privacidade."""
import json

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import legal_medicoes, textos_legais
from web.app import criar_app

INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'
PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36"
TELEMOVEL = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150 Mobile Safari/537.36"


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "DATABASE_URL", "ADSENSE_CLIENTE", "ADSENSE_SLOT"):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def c(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def enviar(c, lcp=2000, cls=50, inp=120, ua=PC):
    return c.post("/api/desempenho", json={"lcp": lcp, "cls": cls, "inp": inp}, headers={"User-Agent": ua})


def eventos(c):
    m = c.app.state.servico.metricas
    m.descarregar(tudo=True)
    return m._consultar("SELECT a, v1, v2, v3 FROM eventos WHERE tipo = 'desempenho' ORDER BY ts, v1", atualizar=False)


def test_guarda_so_tres_numeros_e_a_classe_do_aparelho(c):
    assert enviar(c, 2100, 30, 180).status_code == 204
    assert enviar(c, 3500, 120, 0, ua=TELEMOVEL).status_code == 204
    assert eventos(c) == [("computador", 2100.0, 30.0, 180.0), ("movel", 3500.0, 120.0, 0.0)]


def test_os_robos_nao_contam_e_os_valores_absurdos_sao_recusados(c):
    assert enviar(c, ua="Googlebot/2.1 (+http://www.google.com/bot.html)").status_code == 204
    assert eventos(c) == []
    for corpo in ({"lcp": -1, "cls": 0, "inp": 0}, {"lcp": 60001, "cls": 0, "inp": 0}, {"lcp": 1, "cls": 10001, "inp": 0}, {"lcp": 1, "cls": 0, "inp": 10001},
                  {"lcp": "lento", "cls": 0, "inp": 0}, {"lcp": 1, "cls": 0}):
        assert c.post("/api/desempenho", json=corpo, headers={"User-Agent": PC}).status_code == 422, corpo
    assert eventos(c) == []


def test_o_painel_mostra_o_percentil_75_por_dia_e_classe(c):
    for lcp in (1000, 2000, 3000, 4000):                                              # p75 de 4 valores = o 4.º (índice int(0.75*4) = 3)
        enviar(c, lcp, cls=lcp // 10, inp=lcp // 10)
    enviar(c, 5000, cls=500, inp=0, ua=TELEMOVEL)
    d = c.app.state.servico.metricas.evolucao(1)
    por = {p["id"]: {s["nome"]: s["valores"] for s in p["series"]} for p in d["paineis"]}
    assert por["medicoes"] == {"Telemóvel": [1.0], "Computador": [4.0]}
    assert por["lcp"] == {"Telemóvel": [5000], "Computador": [4000]} and por["cls"] == {"Telemóvel": [0.5], "Computador": [0.4]}
    assert por["inp"]["Computador"] == [400] and por["inp"]["Telemóvel"] == [None]               # sem interação (INP 0) não há INP: não é zero
    assert next(p for p in d["paineis"] if p["id"] == "lcp")["grupo"] == "Desempenho real"


def test_sem_medicoes_os_paineis_ficam_vazios_sem_partir(c):
    d = c.app.state.servico.metricas.evolucao(3)
    por = {p["id"]: {s["nome"]: s["valores"] for s in p["series"]} for p in d["paineis"]}
    assert por["lcp"] == {"Telemóvel": [None, None, None], "Computador": [None, None, None]} and por["medicoes"]["Computador"] == [0.0, 0.0, 0.0]


def test_nada_que_identifique_fica_guardado(c):
    enviar(c, 2222, 33, 144)
    tudo = json.dumps(eventos(c)) + json.dumps(c.app.state.servico.metricas.evolucao(1))
    for segredo in ("testclient", "Windows", "Chrome", "Mozilla"):
        assert segredo not in tudo
    m = c.app.state.servico.metricas
    assert m._consultar("SELECT b, c FROM eventos WHERE tipo = 'desempenho'", atualizar=False) == [("", "")]


def test_o_limite_de_pedidos_protege_a_rota(c, monkeypatch):
    monkeypatch.setenv("RATE_LEVES_POR_MIN", "3")
    c2 = TestClient(criar_app(frontend=c.app.state.servico.sessoes.armazem.raiz.parent / "dist", armazenamento=c.app.state.servico.sessoes.armazem.raiz.parent / "dados2"))
    estados = [enviar(c2).status_code for _ in range(6)]
    assert 429 in estados


# ------------------------------------------------------------------ a política de privacidade
def test_a_privacidade_explica_o_desempenho_em_todas_as_linguas():
    for lg in i18n.LINGUAS:
        seccao = textos_legais.privacidade(lg)["seccoes"][-2]
        assert seccao["titulo"] == legal_medicoes.TEXTOS[lg]["titulo"] and len(seccao["paragrafos"]) == 2, lg
        assert "IP" in seccao["paragrafos"][1], lg                                                      # diz que nunca guarda o IP
    assert "desempenho" in textos_legais.privacidade("pt")["seccoes"][-2]["titulo"]
