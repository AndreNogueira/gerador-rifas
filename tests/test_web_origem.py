"""A origem das visitas nas métricas: só categorias (nunca o endereço de origem), a campanha (utm_source) e o texto da privacidade nas 22 línguas."""
import json

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import legal_medicoes, textos_legais
from web.app import criar_app
from web.metricas import campanha_limpa, categoria_de_origem

INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36"
ECRA = {"ecra_l": 1920, "ecra_a": 1080, "janela_l": 1500, "janela_a": 900, "dpr": 1, "toque": False, "modelo": ""}


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "DATABASE_URL", "ADSENSE_CLIENTE", "ADSENSE_SLOT"):
        monkeypatch.delenv(nome, raising=False)


@pytest.mark.parametrize(("host", "categoria"), [
    ("", "direta"), (None, "direta"), ("gerador-rifas.onrender.com", "direta"),
    ("www.google.com", "pesquisa"), ("google.pt", "pesquisa"), ("www.bing.com", "pesquisa"), ("duckduckgo.com", "pesquisa"), ("search.brave.com", "pesquisa"),
    ("l.facebook.com", "rede_social"), ("m.facebook.com", "rede_social"), ("t.co", "rede_social"), ("www.instagram.com", "rede_social"),
    ("x.com", "rede_social"), ("lnkd.in", "rede_social"), ("com.google.android.youtube", "outro_site"), ("youtu.be", "rede_social"), ("wa.me", "rede_social"),
    ("mail.google.com", "email"), ("outlook.live.com", "email"), ("webmail.sapo.pt", "email"),
    ("escola-do-bairro.pt", "outro_site"), ("evil.example.com/path?x=1", "outro_site"),
])
def test_categoria_de_origem(host, categoria):
    assert categoria_de_origem(host, "gerador-rifas.onrender.com") == categoria


def test_o_proprio_site_conta_como_direta_com_ou_sem_www_e_porta():
    assert categoria_de_origem("www.rifas.exemplo.pt", "rifas.exemplo.pt") == "direta"
    assert categoria_de_origem("rifas.exemplo.pt:8080", "RIFAS.exemplo.pt") == "direta"
    assert categoria_de_origem("google.com.evil.pt", "") == "outro_site"                      # não basta conter «google.com» no nome


@pytest.mark.parametrize(("entrada", "saida"), [("escola-2026", "escola-2026"), ("Escola_A", "escola_a"), ("", ""), (None, ""), ("a b", ""), ("<script>", ""), ("x" * 31, ""),
                                                ("-comeca-mal", ""), ("café", "")])
def test_campanha_limpa(entrada, saida):
    assert campanha_limpa(entrada) == saida


@pytest.fixture
def c(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def eventos_de_origem(c):
    m = c.app.state.servico.metricas
    m.descarregar(tudo=True)
    return m._consultar("SELECT a, b FROM eventos WHERE tipo = 'origem' ORDER BY ts, a, b", atualizar=False)


def test_o_ecra_regista_so_a_categoria_e_a_campanha(c):
    c.post("/api/ecra", json={**ECRA, "origem": "www.google.com", "campanha": ""}, headers={"User-Agent": UA})
    c.post("/api/ecra", json={**ECRA, "origem": "l.facebook.com", "campanha": "Escola_Sol"}, headers={"User-Agent": UA})
    c.post("/api/ecra", json={**ECRA, "origem": "escola-do-bairro.pt", "campanha": "<script>"}, headers={"User-Agent": UA})
    c.post("/api/ecra", json={**ECRA}, headers={"User-Agent": UA})                                           # um cliente antigo: sem origem
    assert sorted(eventos_de_origem(c)) == [("direta", ""), ("outro_site", ""), ("pesquisa", ""), ("rede_social", "escola_sol")]
    d = c.app.state.servico.metricas.evolucao(1)
    por = {p["id"]: p for p in d["paineis"]}
    assert {s["nome"]: s["valores"] for s in por["origens"]["series"]} == {"Pesquisa (Google, Bing…)": [1], "Redes sociais": [1], "Outros sites": [1], "Direta": [1]}
    assert {s["nome"]: s["valores"] for s in por["campanhas"]["series"]} == {"escola_sol": [1]}
    tudo = json.dumps(eventos_de_origem(c)) + json.dumps(d)
    for segredo in ("www.google.com", "l.facebook.com", "escola-do-bairro.pt", "script"):
        assert segredo not in tudo                                                                            # o nome do servidor de origem nunca se guarda


def test_o_proprio_site_e_os_robos_nao_contam_como_origem(c):
    c.post("/api/ecra", json={**ECRA, "origem": "testserver"}, headers={"User-Agent": UA})                    # o Host do cliente de teste é «testserver»
    c.post("/api/ecra", json={**ECRA, "origem": "www.google.com"}, headers={"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"})
    assert eventos_de_origem(c) == [("direta", "")]


def test_um_nome_de_origem_enorme_ou_invalido_e_recusado_sem_guardar_nada(c):
    assert c.post("/api/ecra", json={**ECRA, "origem": "a" * 300}, headers={"User-Agent": UA}).status_code == 422
    assert c.post("/api/ecra", json={**ECRA, "campanha": "b" * 41}, headers={"User-Agent": UA}).status_code == 422
    assert eventos_de_origem(c) == []


# ------------------------------------------------------------------ a política de privacidade
def test_a_privacidade_explica_a_origem_em_todas_as_linguas():
    assert set(legal_medicoes.TEXTOS) == set(i18n.LINGUAS)                                                   # uma língua nova obriga a escrever esta frase
    base = [s["titulo"] for s in textos_legais.privacidade("pt")["seccoes"]]
    assert "Origem das visitas e desempenho" in base and base[-1] == "Comentários e problemas reportados"                  # a secção dos comentários continua a ser a última
    for lg in i18n.LINGUAS:
        pagina = textos_legais.privacidade(lg)
        titulos = [s["titulo"] for s in pagina["seccoes"]]
        assert len(titulos) == len(base), lg
        seccao = pagina["seccoes"][-2]
        assert seccao["titulo"] == legal_medicoes.TEXTOS[lg]["titulo"] and "utm_source" in seccao["paragrafos"][0], lg
        assert "IP" in seccao["paragrafos"][0], lg                                                           # diz que nunca guarda o IP
