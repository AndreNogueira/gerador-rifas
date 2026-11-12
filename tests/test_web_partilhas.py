"""Partilhar um desenho do editor por ligação: só com base de dados, sem imagens, com prazo, sem nada sobre quem partilha, e a privacidade a dizê-lo.

As rotas testam-se com uma `Partilhas` em memória (a mesma interface); a tabela a sério, no Postgres, precisa de `TEST_DATABASE_URL`
(o CI tem um contentor; localmente qualquer Postgres descartável)."""
import json
import os
import re

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import partilhas, textos_legais
from web.app import criar_app
from web.trabalhos import Motor

URL_PG = os.environ.get("TEST_DATABASE_URL", "")
precisa_de_pg = pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg=="


class Memoria:
    """A mesma interface de `partilhas.Partilhas`, num dicionário (e um relógio que se pode adiantar)."""

    def __init__(self):
        self.linhas, self.agora, self.chamadas = {}, 1_800_000_000, []

    def guardar(self, dados):
        self.chamadas.append(("guardar", dados))
        if len(dados.encode()) > partilhas.MAX_BYTES:
            raise ValueError("grande")
        id_ = f"id{len(self.linhas):08d}"
        self.linhas[id_] = [dados, self.agora]
        return id_

    def obter(self, id_):
        if not partilhas.ID.fullmatch(id_) or id_ not in self.linhas:
            return None
        dados, usado = self.linhas[id_]
        if usado < self.agora - partilhas.DIAS * 86400:
            return None
        self.linhas[id_][1] = self.agora
        return dados


def desenho(**extra) -> dict:
    elementos = [
        dict(tipo="retangulo", x=2, y=2, w=300, h=100, cor="#fffdf5", contorno="#0f6e73", espessura=2),
        dict(tipo="texto", x=20, y=40, texto="Rifa do Clube 2026", tamanho=16, cor="#0f6e73"),
        dict(tipo="imagem", x=200, y=10, w=40, h=40, dados=PNG),
        dict(tipo="numero", x=60, y=80, tamanho=18, cor="#c2410c"),
    ]
    return dict(largura=535, altura=152, fundo="#ffffff", elementos=elementos) | extra


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


def _cliente(tmp_path, motor, partilhas_=None):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor, partilhas=partilhas_))


@pytest.fixture
def sem_bd(tmp_path, motor, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with _cliente(tmp_path, motor) as c:
        yield c


@pytest.fixture
def com_bd(tmp_path, motor, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    mem = Memoria()
    with _cliente(tmp_path, motor, mem) as c:
        c.mem = mem
        yield c


# ------------------------------------------------------------------ sem base de dados a funcionalidade nao existe
def test_sem_base_de_dados_nao_ha_partilha(sem_bd):
    assert sem_bd.get("/api/publico").json()["partilha_editor"] is False
    assert sem_bd.post("/api/editor/partilhar", json=desenho()).status_code == 404
    assert sem_bd.get("/api/editor/partilha/abcdefghijk").status_code == 404


def test_com_base_de_dados_o_frontend_sabe(com_bd):
    assert com_bd.get("/api/publico").json()["partilha_editor"] is True


# ------------------------------------------------------------------ guardar e abrir
def test_partilhar_guarda_o_desenho_sem_imagens_e_abre_igual(com_bd):
    r = com_bd.post("/api/editor/partilhar", json=desenho())
    assert r.status_code == 200 and partilhas.ID.fullmatch(r.json()["id"])
    guardado = com_bd.mem.linhas[r.json()["id"]][0]
    assert "iVBOR" not in guardado and "imagem" not in guardado and "dados" not in guardado           # nada de imagens no que fica guardado
    d = com_bd.get(f"/api/editor/partilha/{r.json()['id']}").json()
    assert d["sem_imagens"] is True and [e["tipo"] for e in d["desenho"]["elementos"]] == ["retangulo", "texto", "numero"]
    assert d["desenho"]["elementos"][1]["texto"] == "Rifa do Clube 2026"
    # o que se abre ainda se pode usar para criar o template
    s = com_bd.post("/api/sessoes").json()["sessao"]
    assert com_bd.post(f"/api/sessoes/{s}/editor", json=d["desenho"]).status_code == 200


def test_o_desenho_que_o_editor_recusa_nao_se_guarda(com_bd):
    sem_numero = desenho(elementos=[dict(tipo="texto", x=1, y=10, texto="x")])
    r = com_bd.post("/api/editor/partilhar", json=sem_numero, headers={"X-Lingua": "en"})
    assert r.status_code == 422 and "0001" in r.json()["detail"] and com_bd.mem.linhas == {}
    parecido = desenho()
    parecido["elementos"].append(dict(tipo="texto", x=1, y=10, texto="Ref 0123"))
    assert com_bd.post("/api/editor/partilhar", json=parecido).status_code == 422 and com_bd.mem.linhas == {}


def test_desenho_grande_de_mais_e_recusado(com_bd):
    d = desenho(elementos=[dict(tipo="numero", x=1, y=1)] + [dict(tipo="texto", x=1, y=i, texto="x" * 80) for i in range(39)])
    assert len(json.dumps(d)) < 64 * 1024                         # cabe no limite do pedido; o limite da partilha e outro
    com_bd.mem.guardar = lambda dados: (_ for _ in ()).throw(ValueError("grande"))
    assert com_bd.post("/api/editor/partilhar", json=d).status_code == 413


@pytest.mark.parametrize("id_", ["curto", "com espaco aqui", "../../etc/passwd", "a" * 40, "nao-existe-1234", "%00%00%00%00%00%00%00%00", "id!!!!!!!!"])
def test_ids_invalidos_ou_desconhecidos_dao_404_traduzido(com_bd, id_):
    r = com_bd.get(f"/api/editor/partilha/{id_}", headers={"X-Lingua": "en"})
    assert r.status_code == 404
    assert "/" in id_ or "no longer exists" in r.json()["detail"]                  # com barras nem chega a esta rota (o caminho e normalizado)


def test_passado_o_prazo_a_ligacao_deixa_de_existir_e_cada_acesso_renova(com_bd):
    id_ = com_bd.post("/api/editor/partilhar", json=desenho()).json()["id"]
    com_bd.mem.agora += 80 * 86400
    assert com_bd.get(f"/api/editor/partilha/{id_}").status_code == 200          # dentro dos 90 dias; renova
    com_bd.mem.agora += 80 * 86400
    assert com_bd.get(f"/api/editor/partilha/{id_}").status_code == 200          # 160 dias depois da criacao, mas 80 depois do ultimo acesso
    com_bd.mem.agora += 91 * 86400
    assert com_bd.get(f"/api/editor/partilha/{id_}").status_code == 404


def test_o_guardado_que_o_editor_ja_nao_aceita_nunca_sai(com_bd):
    com_bd.mem.linhas["lixo12345678"] = [json.dumps({"largura": 9999, "altura": 152, "fundo": "#fff", "elementos": []}), com_bd.mem.agora]
    with pytest.raises(Exception):                                                  # de.dict recusa: nunca devolve um desenho que o editor recusaria
        com_bd.get("/api/editor/partilha/lixo12345678")


def test_nada_sobre_quem_partilha_fica_guardado_nem_nas_metricas(com_bd):
    com_bd.post("/api/editor/partilhar", json=desenho(), headers={"X-Lingua": "ja", "User-Agent": "Segredo/1.0", "X-Forwarded-For": "203.0.113.9"})
    (dados,) = [d for acao, d in com_bd.mem.chamadas if acao == "guardar"]
    assert not re.search(r"203\.0\.113|Segredo|ja\b", dados)
    serv = com_bd.app.state.servico
    serv.metricas.descarregar(tudo=True)
    linhas = serv.metricas._consultar("SELECT tipo, a, b, c, v1 FROM eventos WHERE tipo='editor'")
    assert linhas == [("editor", "partilhar", "", "", 3.0)]                       # codigo e numero de elementos (sem a imagem)


# ------------------------------------------------------------------ a privacidade
@pytest.mark.parametrize("lg", list(i18n.LINGUAS))
def test_a_privacidade_so_fala_dos_desenhos_partilhados_com_base_de_dados(lg, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    sem = textos_legais.pagina("privacidade", lg)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/x")
    com = textos_legais.pagina("privacidade", lg)
    assert len(com["seccoes"]) == len(sem["seccoes"]) + 1
    nova = com["seccoes"][2]
    assert nova["titulo"] and len(nova["paragrafos"]) == 1 and "90" in nova["paragrafos"][0] and "{" not in nova["paragrafos"][0]
    assert [s["titulo"] for s in com["seccoes"] if s is not nova] == [s["titulo"] for s in sem["seccoes"]]


# ------------------------------------------------------------------ a tabela a sério
@pytest.fixture
def pg():
    class Relogio:
        t = 1_800_000_000
    r = Relogio()
    p = partilhas.Partilhas(URL_PG, relogio=lambda: r.t)
    p.apagar_tudo()
    p.r = r
    yield p
    p.apagar_tudo()


@precisa_de_pg
def test_postgres_guardar_e_obter(pg):
    id_ = pg.guardar('{"a":1}')
    assert partilhas.ID.fullmatch(id_) and pg.obter(id_) == '{"a":1}' and pg.obter("naoexiste123") is None


@precisa_de_pg
def test_postgres_prazo_renovacao_e_limpeza(pg):
    velho = pg.guardar("velho")
    pg.r.t += 80 * 86400
    assert pg.obter(velho) == "velho"                                   # renova
    pg.r.t += 80 * 86400
    assert pg.obter(velho) == "velho"
    pg.r.t += 91 * 86400
    assert pg.obter(velho) is None
    novo = pg.guardar("novo")                                           # guardar limpa o que passou do prazo
    assert pg._executar("SELECT count(*) FROM partilhas")[0][0] == 1 and pg.obter(novo) == "novo"


@precisa_de_pg
def test_postgres_tamanho_maximo_e_ids_unicos(pg):
    with pytest.raises(ValueError):
        pg.guardar("x" * (partilhas.MAX_BYTES + 1))
    ids = {pg.guardar(f"d{i}") for i in range(30)}
    assert len(ids) == 30


@precisa_de_pg
def test_postgres_nao_guarda_nada_alem_do_desenho(pg):
    pg.guardar("{}")
    colunas = {c for (c,) in pg._executar("SELECT column_name FROM information_schema.columns WHERE table_name='partilhas'")}
    assert colunas == {"id", "dados", "criado", "usado"}                # nem IP, nem lingua, nem user-agent
