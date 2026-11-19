"""O registo permanente das ações do painel (`web/auditoria.py`): o quê, quem e quando; só o que importa; sem dados de visitantes."""
import json
import os

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import INDEX, LEITURA, TOKEN
from web import auditoria
from web.app import criar_app
from web.auditoria import Auditoria


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)


# ------------------------------------------------------------------ a tabela
def test_regista_e_lista_as_mais_recentes_primeiro(tmp_path):
    a = Auditoria(caminho=tmp_path / "a.sqlite3")
    a.registar("entrou", "admin", "", 1_800_000_000)
    a.registar("comentario_apagado", "admin", "abc123", 1_800_000_100)
    a.registar("coisa_nova", "admin", "x", 1_800_000_200)
    r = a.recentes()
    assert [x["acao"] for x in r] == ["coisa_nova", "comentario_apagado", "entrou"]
    assert r[1] == {"ts": 1_800_000_100, "acao": "comentario_apagado", "texto": "Apagou um comentário", "papel": "admin", "detalhe": "abc123"}
    assert r[0]["texto"] == "coisa_nova"                                              # uma ação sem tradução mostra o código
    assert len(a.recentes(2)) == 2 and a.total() == 3


def test_o_detalhe_e_cortado_e_o_registo_antigo_apaga_se(tmp_path):
    a = Auditoria(caminho=tmp_path / "a.sqlite3")
    a.registar("seo_editado", "admin", "x" * 500, 1_800_000_000)
    assert len(a.recentes()[0]["detalhe"]) == auditoria.DETALHE_MAX
    a.registar("entrou", "admin", "", 1_800_000_000 + auditoria.RETENCAO_S + 10)       # passou a retenção: a linha antiga sai
    assert [x["acao"] for x in a.recentes()] == ["entrou"]


def test_toda_a_acao_do_painel_tem_texto_em_portugues():
    import re
    from pathlib import Path

    codigo = (Path(__file__).parent.parent / "src" / "web" / "admin.py").read_text(encoding="utf-8")
    usadas = set(re.findall(r'_registar\(serv, "([a-z_]+)"', codigo)) | {"entrou", "entrou_leitura"} | {f"comentario_{e}" for e in ("novo", "lido", "favorito", "escondido")}
    assert usadas <= set(auditoria.ACOES), usadas - set(auditoria.ACOES)


# ------------------------------------------------------------------ o painel
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def entrar_como_dono(c):
    c.post("/api/admin/entrar", json={"token": TOKEN})


def comentar(c, texto):
    return c.post("/api/comentarios", json={"texto": texto, "anonimo": True, "nome": "", "site": ""})


def test_regista_a_entrada_e_as_acoes_do_dono_com_o_detalhe_certo(admin):
    comentar(admin, "Texto privado do visitante que nunca vai para o registo")
    entrar_como_dono(admin)
    id_ = admin.get("/api/admin/comentarios").json()["itens"][0]["id"]
    admin.patch(f"/api/admin/comentarios/{id_}", json={"estado": "escondido"})
    admin.delete(f"/api/admin/comentarios/{id_}")
    admin.put("/api/admin/objetivos", json={"chave": "sessoes", "meta": 25})
    chave = admin.post("/api/admin/chaves", json={"nome": "Escola de Teste", "quota_dia": 100}).json()
    admin.delete(f"/api/admin/chaves/{chave['id']}")
    d = admin.get("/api/admin/auditoria").json()
    assert d["retencao_dias"] == 400 and d["persistente"] is False and d["total"] == 6
    por_acao = {i["acao"]: i for i in d["itens"]}
    assert [i["acao"] for i in d["itens"]] == ["chave_revogada", "chave_criada", "objetivo", "comentario_apagado", "comentario_escondido", "entrou"]
    assert por_acao["comentario_escondido"]["detalhe"] == id_ and por_acao["comentario_apagado"]["detalhe"] == id_ and por_acao["comentario_apagado"]["papel"] == "admin"
    assert por_acao["objetivo"]["detalhe"] == "sessoes: 25.0" and por_acao["chave_criada"]["detalhe"] == f"Escola de Teste ({chave['id']})"
    assert por_acao["entrou"]["texto"] == "Entrou no painel" and por_acao["chave_revogada"]["detalhe"] == chave["id"]
    texto = json.dumps(d)
    assert "Texto privado" not in texto and chave["chave"] not in texto and TOKEN not in texto and "testclient" not in texto      # nem texto de visitantes, nem a chave, nem a palavra-passe, nem IPs


def test_uma_palavra_passe_errada_ou_um_bloqueio_nao_enchem_o_registo(admin):
    for _ in range(4):                                                              # o limite é de 5 tentativas por minuto: as falhadas e o bloqueio contam-se nas métricas, não aqui
        assert admin.post("/api/admin/entrar", json={"token": "errada-errada-errada"}).status_code == 401
    entrar_como_dono(admin)
    assert [i["acao"] for i in admin.get("/api/admin/auditoria").json()["itens"]] == ["entrou"]


def test_a_leitura_aparece_como_leitura_e_pode_consultar_o_registo(admin):
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    d = admin.get("/api/admin/auditoria").json()
    assert [(i["acao"], i["papel"]) for i in d["itens"]] == [("entrou_leitura", "leitura")] and d["itens"][0]["texto"] == "Entrou no painel (só leitura)"


def test_o_registo_so_existe_com_sessao_e_valida_o_limite(admin):
    assert admin.get("/api/admin/auditoria").status_code == 404
    entrar_como_dono(admin)
    assert admin.get("/api/admin/auditoria", params={"limite": 0}).status_code == 422
    assert admin.get("/api/admin/auditoria", params={"limite": 1001}).status_code == 422
    assert len(admin.get("/api/admin/auditoria", params={"limite": 1}).json()["itens"]) == 1


def test_uma_base_do_registo_em_baixo_nao_estraga_a_acao(admin):
    entrar_como_dono(admin)
    comentar(admin, "Comentário para apagar com o registo avariado")
    id_ = admin.get("/api/admin/comentarios").json()["itens"][0]["id"]

    def avariada(*a, **k):
        raise RuntimeError("sem base")
    admin.app.state.servico.auditoria.registar = avariada
    assert admin.delete(f"/api/admin/comentarios/{id_}").status_code == 204                 # a ação faz-se na mesma
    admin.app.state.servico.auditoria.recentes = avariada
    admin.app.state.servico.auditoria.total = avariada
    assert admin.get("/api/admin/auditoria").status_code == 503


# ------------------------------------------------------------------ o registo a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_registar_listar_e_limpar():
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS auditoria")
    a = Auditoria(url_bd=URL_PG)
    a.registar("entrou", "admin", "", 1_800_000_000)
    a.registar("chave_criada", "admin", "Escola (k1)", 1_800_000_050)
    assert [x["acao"] for x in a.recentes()] == ["chave_criada", "entrou"] and a.total() == 2
    a.registar("entrou", "admin", "", 1_800_000_000 + auditoria.RETENCAO_S + 100)
    assert a.total() == 1
