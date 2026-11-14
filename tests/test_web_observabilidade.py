"""Observabilidade: o registo estruturado (uma linha JSON por pedido e por evento), o livro de erros do painel, o `X-Request-ID` e a regra de privacidade
(nunca IP, nomes, mensagens de erro, nem a rota com valores)."""
import io
import json
import logging

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from web import observabilidade
from web.app import criar_app
from web.observabilidade import Observabilidade

TOKEN = "palavra-passe-muito-longa-123"
LEITURA = "token-so-de-leitura-do-claude-0123456789"
INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("PUBLIC_URL", "RENDER_EXTERNAL_URL", "RENDER", "RIFAS_METRICAS", "DATABASE_URL", "LOG_PEDIDOS"):
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)


@pytest.fixture
def registo():
    """Apanha o que o registo estruturado escreve (o logger «rifas»)."""
    fluxo = io.StringIO()
    h = logging.StreamHandler(fluxo)
    h.setFormatter(logging.Formatter("%(message)s"))
    observabilidade.configurar(True)
    logging.getLogger("rifas").addHandler(h)
    yield lambda: [json.loads(x) for x in fluxo.getvalue().splitlines() if x.strip()]
    logging.getLogger("rifas").removeHandler(h)


def _app(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), base_url="http://testserver", raise_server_exceptions=False)


# ------------------------------------------------------------------ o livro, sem servidor
def test_o_livro_agrupa_por_assinatura_e_conta():
    t = [1000.0]
    o = Observabilidade(agora=lambda: t[0])
    for _ in range(3):
        o.erro("excecao", rota="POST /api/x", estado=500, excecao="ValueError", onde="rotas.py:10:f")
        t[0] += 5
    o.erro("excecao", rota="POST /api/x", estado=500, excecao="KeyError", onde="rotas.py:10:f")
    livro = o.livro()
    assert livro["total"] == 4 and len(livro["erros"]) == 2
    mais_recente = livro["erros"][0]
    assert mais_recente["excecao"] == "KeyError" and mais_recente["n"] == 1
    antigo = next(e for e in livro["erros"] if e["excecao"] == "ValueError")
    assert antigo["n"] == 3 and antigo["primeira"] == 1000 and antigo["ultima"] == 1010
    assert o.livro(desde=1011)["total"] == 1                                  # só o que aconteceu desde...


def test_o_livro_tem_um_teto_e_deita_fora_o_mais_antigo():
    t = [0.0]
    o = Observabilidade(agora=lambda: t[0])
    for i in range(observabilidade.MAX_ASSINATURAS + 25):
        t[0] += 1
        o.erro("excecao", rota=f"GET /r{i}", estado=500, excecao="E", onde="a.py:1:f")
    assert len(o.livro()["erros"]) == observabilidade.MAX_ASSINATURAS


def test_so_as_falhas_dos_eventos_entram_no_livro():
    o = Observabilidade()
    o.evento("erro_http", "422", "aviso", "", 0, 0, 0)                          # o utilizador a enganar-se: não é falha
    o.evento("geracao", "ok", "", "varios", 1.0, 10, 10)
    o.evento("geracao", "cancelado", "", "varios", 1.0, 10, 0)
    assert o.livro()["total"] == 0
    o.evento("erro_http", "503", "erro", "", 0, 0, 0)
    o.evento("geracao", "falhou", "tempo", "varios", 9.0, 30000, 0)
    o.evento("geracao", "erros", "err_x", "varios", 1.0, 3, 3)
    o.evento("motor_reiniciado", "", "", "", 0, 0, 0)
    tipos = sorted((e["tipo"], e["excecao"], e["onde"]) for e in o.livro()["erros"])
    assert tipos == [("geracao", "erros", "err_x"), ("geracao", "falhou", "tempo"), ("http", "erro", ""), ("motor_reiniciado", "", "")]


def test_a_mensagem_da_excecao_nunca_e_guardada(registo):
    o = Observabilidade(versao="9.9")
    try:
        raise ValueError("C:/Users/Maria/Rifa da Joana 0001.pdf")
    except ValueError as exc:
        o.excecao("abcd1234", "POST", "/api/sessoes/{id_}/gerar", exc)
    saida = json.dumps(o.livro()) + json.dumps(registo())
    assert "Maria" not in saida and "Joana" not in saida and ".pdf" not in saida
    e = o.livro()["erros"][0]
    assert e["excecao"] == "ValueError" and e["onde"].startswith("test_web_observabilidade.py:") and e["rota"] == "POST /api/sessoes/{id_}/gerar"


# ------------------------------------------------------------------ na aplicacao
def test_cada_pedido_da_api_gera_uma_linha_json_com_a_rota_em_modelo(tmp_path, registo):
    c = _app(tmp_path)
    r = c.post("/api/sessoes")
    sessao = r.json()["sessao"]
    c.get(f"/api/sessoes/{sessao}")
    linhas = [x for x in registo() if x["ev"] == "pedido"]
    assert len(linhas) == 2 and all(set(x) == {"t", "n", "ev", "id", "m", "r", "s", "ms", "v"} for x in linhas)
    assert linhas[1]["r"] == "/api/sessoes/{id_}" and sessao not in json.dumps(linhas)          # o modelo, nunca o valor
    assert linhas[1]["id"] == r.headers["x-request-id"] or len(linhas[1]["id"]) == 8
    assert "testclient" not in json.dumps(linhas) and "127.0.0.1" not in json.dumps(linhas)    # nem IP


def test_o_health_e_a_pagina_inicial_nao_enchem_o_registo(tmp_path, registo):
    c = _app(tmp_path)
    c.get("/health")
    c.get("/")
    assert [x for x in registo() if x["ev"] == "pedido"] == []


def test_os_eventos_das_metricas_vao_para_o_registo_so_com_codigos(tmp_path, registo):
    c = _app(tmp_path)
    c.post("/api/sessoes", headers={"User-Agent": "Mozilla/5.0 (Segredo)"})
    ev = [x for x in registo() if x["ev"] == "evento" and x["tipo"] == "sessao"]
    assert len(ev) == 1 and "Segredo" not in json.dumps(ev) and "Mozilla" not in json.dumps(ev)


def test_um_erro_nao_tratado_da_500_com_o_id_e_fica_no_livro(tmp_path, registo):
    c = _app(tmp_path)

    def _explode():
        raise RuntimeError("segredo do utilizador: Rifa Joana.pdf")

    c.app.router.routes.insert(0, APIRoute("/api/explode", _explode, methods=["GET"]))         # antes do «apanha-tudo» do frontend

    r = c.get("/api/explode")
    assert r.status_code == 500
    corpo = r.json()
    assert corpo["id"] == r.headers["x-request-id"] and corpo["id"] in corpo["detail"] and "Joana" not in r.text
    assert c.post("/api/admin/entrar", json={"token": TOKEN}).status_code == 200
    livro = c.get("/api/admin/erros").json()
    assert livro["total"] == 1 and livro["erros"][0]["excecao"] == "RuntimeError" and livro["erros"][0]["rota"] == "GET /api/explode"
    assert "Joana" not in json.dumps(livro) and "Joana" not in json.dumps(registo())
    linha = next(x for x in registo() if x["ev"] == "excecao")
    assert linha["id"] == corpo["id"] and linha["n"] == "error"


def test_o_livro_de_erros_so_se_ve_com_acesso_ao_painel(tmp_path):
    c = _app(tmp_path)
    assert c.get("/api/admin/erros").status_code == 404
    assert c.get("/api/admin/erros", headers={"Authorization": f"Bearer {LEITURA}"}).status_code == 200      # a leitura (CLAUDE_TOKEN) vê
    assert c.get("/api/admin/erros?intervalo=agora").status_code == 404                                       # sem cookie continua a ser 404
    c.post("/api/admin/entrar", json={"token": TOKEN})
    assert c.get("/api/admin/erros?intervalo=agora").status_code == 422


def test_log_pedidos_0_desliga_o_registo(tmp_path, monkeypatch, registo):
    monkeypatch.setenv("LOG_PEDIDOS", "0")
    c = _app(tmp_path)
    c.post("/api/sessoes")
    assert registo() == []
    monkeypatch.delenv("LOG_PEDIDOS")
    _app(tmp_path)                                                              # volta a ligar-se ao criar outra app
