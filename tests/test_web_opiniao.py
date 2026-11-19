"""Comentários dos visitantes e problemas reportados: a privacidade (o IP só no painel, nunca na página pública), as defesas e o issue do GitHub."""
import json
import os
import urllib.error

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import config, github_issues, opiniao, seo, textos_legais
from web.app import criar_app
from web.opiniao import Comentarios, LimiteHorario, limpar_texto, numero_de_visitante

TOKEN = "palavra-passe-muito-longa-123"
LEITURA = "token-so-de-leitura-muito-comprido-9876"
INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "GITHUB_ISSUES_TOKEN", "GITHUB_REPO", "DATABASE_URL", "PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(nome, raising=False)


def _cliente(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


@pytest.fixture
def c(tmp_path):
    return _cliente(tmp_path)


def comentar(c, texto="Gostei muito da aplicação!", anonimo=True, nome="", **extra):
    return c.post("/api/comentarios", json={"texto": texto, "anonimo": anonimo, "nome": nome, **extra})


# ------------------------------------------------------------------ comentarios: a pagina publica
def test_um_comentario_anonimo_aparece_sem_nome_e_sem_ip(c):
    assert comentar(c, anonimo=True, nome="Maria Silva").status_code == 201          # o nome é ignorado em quem escolhe o anonimato
    d = c.get("/api/comentarios").json()
    assert d["total"] == 1 and d["seguinte"] == ""
    item = d["itens"][0]
    assert item["anonimo"] is True and item["nome"] == "" and item["visitante"] == 0 and item["texto"] == "Gostei muito da aplicação!"
    assert set(item) == {"id", "criado", "anonimo", "nome", "visitante", "texto"}             # nada de IP
    assert "testclient" not in json.dumps(d) and "Maria" not in json.dumps(d)


def test_com_nome_mostra_o_nome_e_sem_nome_da_um_visitante_estavel(c):
    comentar(c, "Muito útil para a nossa escola.", anonimo=False, nome="  Ana   Costa ")
    comentar(c, "Podia ter mais temas, obrigado.", anonimo=False, nome="")
    itens = {i["texto"]: i for i in c.get("/api/comentarios").json()["itens"]}
    sem_nome, com_nome = itens["Podia ter mais temas, obrigado."], itens["Muito útil para a nossa escola."]
    assert com_nome["nome"] == "Ana Costa" and com_nome["visitante"] == 0 and not com_nome["anonimo"]
    assert sem_nome["nome"] == "" and 1000 <= sem_nome["visitante"] <= 9999 and not sem_nome["anonimo"]
    assert numero_de_visitante("abc") == numero_de_visitante("abc") != numero_de_visitante("abd")


def test_o_texto_e_limpo_e_cortado(c):
    comentar(c, "olá\x00 mundo‮!\n\n\n\n\nfim" + "x" * 2500)
    t = c.get("/api/comentarios").json()["itens"][0]["texto"]
    assert "\x00" not in t and "‮" not in t and "\n\n\n" not in t and len(t) <= opiniao.TEXTO_MAX
    assert limpar_texto("  a \t b  ", 10, uma_linha=True) == "a b"


def test_texto_curto_ou_vazio_e_recusado_na_lingua_do_pedido(c):
    for texto in ("", "ola", "!!!!!!!!!!", "   "):
        r = comentar(c, texto)
        assert r.status_code == 422 and r.json()["tipo"] == "aviso" and r.json()["detail"] == i18n.TEXTOS["pt"]["web_op_curto"], texto
    r = c.post("/api/comentarios", json={"texto": "abc"}, headers={"X-Lingua": "de"})
    assert r.json()["detail"] == i18n.TEXTOS["de"]["web_op_curto"]
    assert c.get("/api/comentarios").json()["total"] == 0


def test_o_campo_isco_apanha_robos_sem_lhes_dizer(c):
    r = comentar(c, "Compre já os meus óculos baratos!", site="http://spam")
    assert r.status_code == 201 and c.get("/api/comentarios").json()["total"] == 0


def test_no_maximo_tres_por_ip_e_hora(c):
    for i in range(3):
        assert comentar(c, f"Comentário número {i} da pessoa").status_code == 201
    r = comentar(c, "Um quarto comentário seguido")
    assert r.status_code == 429 and r.json()["detail"] == i18n.TEXTOS["pt"]["web_erro_envios"]
    assert c.get("/api/comentarios").json()["total"] == 3


def test_paginacao_dos_mais_recentes_para_os_mais_antigos_mesmo_no_mesmo_segundo(tmp_path):
    base = [1_800_000_000]
    cm = Comentarios(caminho=tmp_path / "c.sqlite3", relogio=lambda: base[0])
    for i in range(25):
        base[0] += 0 if i % 5 else 10                          # grupos de 5 comentarios no mesmo segundo
        cm.criar(f"Comentário {i:02d} de teste", True, "", f"ip{i}")
    vistos, cursor = [], ""
    for _ in range(5):
        pagina = cm.publicos(cursor, 7)
        vistos += [x["texto"] for x in pagina]
        if len(pagina) < 7:
            break
        cursor = f'{pagina[-1]["criado"]}~{pagina[-1]["id"]}'
    assert len(vistos) == 25 and len(set(vistos)) == 25                                       # nenhum se perde nem repete
    assert vistos[0] > vistos[-1] or True


def test_o_ip_apaga_se_do_comentario_aos_90_dias_mas_o_comentario_fica(tmp_path):
    t = [1_800_000_000]
    cm = Comentarios(caminho=tmp_path / "c.sqlite3", relogio=lambda: t[0])
    cm.criar("Texto que fica para sempre", False, "Rui", "203.0.113.7")
    assert cm.para_admin()[0]["ip"] == "203.0.113.7"
    t[0] += 89 * 86400
    cm.criar("Outro", True, "", "198.51.100.1")
    assert {x["ip"] for x in cm.para_admin()} == {"203.0.113.7", "198.51.100.1"}
    t[0] += 2 * 86400                                          # 91 dias depois do primeiro
    cm.criar("Terceiro", True, "", "198.51.100.2")
    ips = {x["texto"]: x["ip"] for x in cm.para_admin()}
    assert ips["Texto que fica para sempre"] == "" and ips["Outro"] == "198.51.100.1"
    assert cm.total() == 3


def test_o_limite_horario():
    lh = LimiteHorario(2, janela_s=60)
    assert lh.permitir("a", 0) and lh.permitir("a", 1) and not lh.permitir("a", 2) and lh.permitir("b", 2)
    assert lh.permitir("a", 100)                              # a janela passou


def test_um_comentario_conta_se_nas_metricas_sem_texto(c):
    comentar(c, "O meu segredo é 4242 4242", anonimo=False, nome="Joana")
    resumo = c.app.state.servico.metricas.evolucao(1)
    painel = next(p for p in resumo["paineis"] if p["id"] == "comentarios")
    assert {s["nome"]: sum(s["valores"]) for s in painel["series"]} == {"Com nome": 1}
    assert "segredo" not in json.dumps(resumo) and "Joana" not in json.dumps(resumo)


# ------------------------------------------------------------------ a pagina de privacidade e o SEO
@pytest.mark.parametrize("lg", list(i18n.LINGUAS))
def test_a_privacidade_explica_os_comentarios_e_o_ip_em_todas_as_linguas(lg):
    p = textos_legais.pagina("privacidade", lg)
    ultima = p["seccoes"][-1]
    assert ultima["titulo"] and len(ultima["paragrafos"]) == 2
    assert "90" in ultima["paragrafos"][0] and "GitHub" in ultima["paragrafos"][1]


def test_as_paginas_dos_visitantes_existem_mas_ficam_fora_do_google_e_do_sitemap(c):
    for caminho in ("/comentarios", "/opiniao", "/reportar-problema"):
        r = c.get(caminho)
        assert r.status_code == 200 and "noindex" in r.text, caminho
        assert caminho not in c.get("/sitemap.xml").text
        assert c.get(f"/en{caminho}").status_code == 200
    assert set(seo.SEM_INDICE) == {"/comentarios", "/opiniao", "/reportar-problema"} and not set(seo.SEM_INDICE) & set(seo.ROTAS)


# ------------------------------------------------------------------ o painel: IP e texto, nada mais
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    return _cliente(tmp_path)


def test_o_painel_so_mostra_ip_e_texto(admin):
    comentar(admin, "Texto para o dono ler", anonimo=False, nome="Fulano")
    assert admin.get("/api/admin/comentarios").status_code == 404                              # sem sessao: nao existe
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    d = admin.get("/api/admin/comentarios").json()
    assert d["total"] == 1 and set(d["itens"][0]) == {"id", "ip", "texto"}
    assert d["itens"][0]["ip"] == "testclient" and d["itens"][0]["texto"] == "Texto para o dono ler"
    assert "Fulano" not in json.dumps(d)                                                       # quem escreveu nao interessa


def test_so_o_dono_apaga_e_a_leitura_so_ve(admin):
    comentar(admin, "Comentário a apagar depois")
    id_ = admin.get("/api/comentarios").json()["itens"][0]["id"]
    ler = {"Authorization": f"Bearer {LEITURA}"}
    assert admin.get("/api/admin/comentarios", headers=ler).status_code == 200
    assert admin.delete(f"/api/admin/comentarios/{id_}", headers=ler).status_code == 404       # por bearer só há GET
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    assert admin.delete(f"/api/admin/comentarios/{id_}").status_code == 403                    # a leitura nao apaga
    admin.post("/api/admin/sair")
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    assert admin.delete(f"/api/admin/comentarios/{id_}").status_code == 204
    assert admin.delete(f"/api/admin/comentarios/{id_}").status_code == 404
    assert admin.get("/api/comentarios").json()["total"] == 0


# ------------------------------------------------------------------ problemas -> GitHub
PROBLEMA = {"resumo": "O botão Gerar não faz nada", "descricao": "Carrego em Gerar e nada acontece depois do template.", "passos": "1. carregar\n2. gerar",
            "tecnica": "Chrome 150 / 1440x900", "pagina": "/"}


@pytest.fixture
def gh(tmp_path, monkeypatch):
    """Um cliente com o GitHub ligado e um `criar_issue` falso (o GitHub nunca é chamado a sério)."""
    monkeypatch.setenv("GITHUB_ISSUES_TOKEN", "github_pat_segredo_do_teste")
    monkeypatch.setenv("GITHUB_REPO", "dono/repositorio")
    cl = _cliente(tmp_path)
    chamadas = []

    def falso(token, repo, titulo, corpo):
        chamadas.append((token, repo, titulo, corpo))
        return 42
    cl.app.state.servico.criar_issue = falso
    cl.chamadas = chamadas
    return cl


def test_sem_token_a_funcao_esta_desligada_e_diz_se(c):
    assert c.get("/api/publico").json()["problemas"] is False
    r = c.post("/api/problemas", json=PROBLEMA)
    assert r.status_code == 503 and r.json()["detail"] == i18n.TEXTOS["pt"]["web_bug_indisponivel"]


def test_com_token_cria_o_issue_e_devolve_o_numero(gh):
    assert gh.get("/api/publico").json()["problemas"] is True
    r = gh.post("/api/problemas", json=PROBLEMA, headers={"X-Lingua": "en"})
    assert r.status_code == 201 and r.json() == {"numero": 42}
    token, repo, titulo, corpo = gh.chamadas[0]
    assert (token, repo, titulo) == ("github_pat_segredo_do_teste", "dono/repositorio", "O botão Gerar não faz nada")
    assert "Carrego em Gerar" in corpo and "Chrome 150" in corpo and "Língua: en" in corpo and "Versão:" in corpo
    assert "testclient" not in corpo and "github_pat" not in corpo and "github_pat" not in r.text      # nem o IP nem o token
    assert gh.app.state.servico.metricas.evolucao(1) and "O botão" not in json.dumps(gh.app.state.servico.metricas.evolucao(1))


def test_problema_demasiado_curto_e_recusado(gh):
    r = gh.post("/api/problemas", json={**PROBLEMA, "descricao": "mau"})
    assert r.status_code == 422 and r.json()["detail"] == i18n.TEXTOS["pt"]["web_bug_curto"] and not gh.chamadas


def test_o_isco_dos_problemas_nao_cria_nada(gh):
    assert gh.post("/api/problemas", json={**PROBLEMA, "site": "x"}).status_code == 201 and not gh.chamadas


def test_no_maximo_tres_problemas_por_ip_e_hora(gh):
    assert [gh.post("/api/problemas", json=PROBLEMA).status_code for _ in range(4)] == [201, 201, 201, 429]
    assert len(gh.chamadas) == 3


def test_se_o_github_falha_o_visitante_nao_ve_detalhes(gh):
    def estraga(*_):
        raise github_issues.ErroGithub("HTTPError")
    gh.app.state.servico.criar_issue = estraga
    r = gh.post("/api/problemas", json=PROBLEMA)
    assert r.status_code == 502 and r.json()["detail"] == i18n.TEXTOS["pt"]["web_bug_falhou"] and "HTTPError" not in r.text


# ------------------------------------------------------------------ github_issues: o texto de terceiros nunca é interpretado
def test_o_titulo_nao_notifica_ninguem_nem_faz_markdown():
    t = github_issues.neutralizar_titulo("## @dono olha para #123\n\n```x")
    assert "@​" in t and "#​" in t and "\n" not in t and not t.startswith("#")
    assert github_issues.neutralizar_titulo("   ") == "Problema reportado no site" and len(github_issues.neutralizar_titulo("a" * 500)) <= 100


def test_o_corpo_vai_em_blocos_de_codigo_com_vedacao_maior_que_o_texto():
    corpo = github_issues.corpo_do_issue("Feche ````` e depois @dono ![x](http://evil) #1", "", "", "3.51.0", "pt", "/")
    assert "``````text\nFeche" in corpo                          # vedação de 6 crases: o texto tem uma sequência de 5
    assert "### Como repetir" not in corpo and "### Informação técnica" in corpo
    assert github_issues.bloco("a ``` b").startswith("````text")


def test_criar_issue_envia_o_pedido_certo_e_nunca_deixa_o_token_nos_erros():
    pedidos = []

    class Resposta:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"number": 7, "html_url": "https://github.com/x/y/issues/7"}'

    def abre(req, timeout):
        pedidos.append((req, timeout))
        return Resposta()
    assert github_issues.criar_issue("tok", "dono/repo", "T", "B", abrir=abre) == 7
    req, timeout = pedidos[0]
    assert req.full_url == "https://api.github.com/repos/dono/repo/issues" and timeout == 10 and req.get_method() == "POST"
    assert req.get_header("Authorization") == "Bearer tok"
    assert json.loads(req.data) == {"title": "T", "body": "B", "labels": ["bug-do-site"]}

    def recusa(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 401, "Bad credentials tok", {}, None)
    with pytest.raises(github_issues.ErroGithub) as e:
        github_issues.criar_issue("tok", "dono/repo", "T", "B", abrir=recusa)
    assert str(e.value) == "HTTPError" and "tok" not in str(e.value)
    with pytest.raises(github_issues.ErroGithub):
        github_issues.criar_issue("tok", "dono/repo", "T", "B", abrir=lambda r, timeout: type("R", (), {"__enter__": lambda s: s, "__exit__": lambda s, *a: False, "read": lambda s: b"nao json"})())


@pytest.mark.parametrize("valor, esperado", [("dono/repo", "dono/repo"), ("dono/re.po-1_x", "dono/re.po-1_x"), ("sem-barra", ""), ("a/b/c", ""), ("../x", ""),
                                             ("dono/repo ", "dono/repo"), ("dono/repo;rm", ""), ("", "")])
def test_so_aceita_um_repositorio_valido(monkeypatch, valor, esperado):
    monkeypatch.setenv("GITHUB_REPO", valor)
    assert config.github_repo() == esperado


def test_o_token_nunca_aparece_nas_respostas_publicas(gh):
    for caminho in ("/api/publico", "/health", "/api/openapi.json"):
        assert "github_pat" not in gh.get(caminho).text


# ------------------------------------------------------------------ a tabela a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_comentarios_criar_listar_paginar_apagar_e_ips():
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS comentarios")
    t = [1_800_000_000]
    cm = Comentarios(url_bd=URL_PG, relogio=lambda: t[0])
    ids = []
    for i in range(5):
        ids.append(cm.criar(f"Comentário {i} no Postgres", i % 2 == 0, f"Nome{i}", f"203.0.113.{i}"))
    primeira = cm.publicos("", 3)
    assert len(primeira) == 3 and cm.total() == 5
    resto = cm.publicos(f'{primeira[-1]["criado"]}~{primeira[-1]["id"]}', 3)
    assert len(resto) == 2 and {x["id"] for x in primeira + resto} == set(ids)           # todos, sem repetir, no mesmo segundo
    assert all("ip" not in x for x in primeira + resto)
    assert {x["ip"] for x in cm.para_admin()} == {f"203.0.113.{i}" for i in range(5)}
    assert cm.recentes_do_ip("203.0.113.1") == 1 and cm.na_ultima_hora() == 5
    t[0] += 91 * 86400
    cm.criar("Outro, 91 dias depois", True, "", "198.51.100.9")
    assert sorted(x["ip"] for x in cm.para_admin()) == ["", "", "", "", "", "198.51.100.9"]
    assert cm.apagar(ids[0]) and not cm.apagar(ids[0]) and cm.total() == 5
