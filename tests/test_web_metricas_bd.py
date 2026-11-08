"""Metricas na base Postgres (`DATABASE_URL`): persistencia, quando grava, recuperar de ligacoes cortadas e de a base estar em baixo.

Os testes que falam com um Postgres a sério precisam de `TEST_DATABASE_URL` (o CI tem um contentor; localmente qualquer Postgres descartavel).
"""
import logging
import os

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from web import config, metricas
from web.metricas import BUFFER_MAXIMO, Metricas

URL_PG = os.environ.get("TEST_DATABASE_URL", "")
precisa_de_pg = pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
SEGREDO = "palavra-passe-secreta-123"
URL_EM_BAIXO = f"postgresql://rifas:{SEGREDO}@base.invalido:5432/rifas"


@pytest.fixture(autouse=True)
def base_em_baixo(monkeypatch):
    """Simula a base em baixo sem esperar pelo tempo limite da rede (no Windows uma ligacao a lado nenhum demora 10 s). A mensagem leva a
    palavra-passe de proposito: prova que nada a deixa passar para os logs."""
    import psycopg

    original = metricas._Postgres._ligacao

    def ligacao(self):
        if self._url == URL_EM_BAIXO:
            raise psycopg.OperationalError(f"connection failed: {URL_EM_BAIXO}")
        return original(self)

    monkeypatch.setattr(metricas._Postgres, "_ligacao", ligacao)


class Relogio:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def relogio():
    return Relogio()


@pytest.fixture
def pg(relogio):
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS sistema, pedidos, eventos")
    obj = Metricas(None, relogio=relogio, url_bd=URL_PG)
    yield obj
    obj.fechar()


# ------------------------------------------------------------------ configuracao (sem base)
@pytest.mark.parametrize("valor,esperado", [
    ("postgresql://u:p@ep-x.eu-central-1.aws.neon.tech/db?sslmode=require", True),
    ("postgres://u:p@localhost:5432/db", True),
    ("mysql://u:p@host/db", False),
    ("http://exemplo.pt", False),
    ("postgresql://", False),
    ("postgresql://u:p@host/db com espacos", False),
    ("", False),
])
def test_database_url_so_aceita_postgres(monkeypatch, valor, esperado):
    monkeypatch.setenv("DATABASE_URL", valor)
    assert bool(config.database_url()) is esperado


def test_database_url_ausente_e_sqlite_como_sempre(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    m = Metricas(tmp_path / "m.sqlite3")
    assert m.persistente is False and m.estado_bd() == {"tipo": "sqlite", "erro": False, "intervalo_min": 0}
    m.fechar()


@pytest.mark.parametrize("valor,esperado", [("", 60.0), ("15", 15.0), ("0", 1.0), ("99999", 720.0), ("abc", 60.0)])
def test_intervalo_de_gravacao_na_base(monkeypatch, valor, esperado):
    monkeypatch.setenv("METRICAS_BD_MIN", valor)
    assert config.metricas_bd_min() == esperado


def test_com_base_externa_os_dados_ja_nao_sao_efemeros(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.delenv("RIFAS_METRICAS", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert config.metricas_efemeras() is True
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host/db")
    assert config.metricas_efemeras() is False


def test_a_app_arranca_e_serve_sem_a_base_estar_acessivel(tmp_path, monkeypatch):
    """O Neon em baixo nao pode impedir o gerador de funcionar: so as metricas sofrem."""
    from fastapi.testclient import TestClient
    from web.app import criar_app

    monkeypatch.setenv("DATABASE_URL", URL_EM_BAIXO)
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    with TestClient(criar_app(armazenamento=tmp_path / "dados")) as c:
        assert c.get("/health").status_code == 200
        assert c.get("/api/linguas").status_code == 200


# ------------------------------------------------------------------ quando grava (sem base: a trava e o relogio)
def test_no_postgres_so_grava_de_hora_a_hora_ou_com_muitos_registos(relogio, monkeypatch):
    chamadas = []
    m = Metricas(None, relogio=relogio, url_bd=URL_EM_BAIXO, intervalo_bd_min=60)
    monkeypatch.setattr(m, "descarregar", lambda tudo=False: chamadas.append(tudo))
    m.evento("sessao", "pt", "premiado", "computador")
    m.descarregar_periodico()
    relogio.t += 59 * 60
    m.descarregar_periodico()
    assert chamadas == []                                               # a base tem de poder suspender entre gravacoes
    relogio.t += 120
    m.descarregar_periodico()
    assert chamadas == [False]
    for _ in range(BUFFER_MAXIMO):
        m.evento("pagina", "/", c="computador")
    m.descarregar_periodico()
    assert chamadas == [False, False]                                   # buffer cheio: grava antes do tempo


def test_no_sqlite_grava_sempre(tmp_path, relogio, monkeypatch):
    chamadas = []
    m = Metricas(tmp_path / "m.sqlite3", relogio=relogio)
    monkeypatch.setattr(m, "descarregar", lambda tudo=False: chamadas.append(tudo))
    m.descarregar_periodico()
    m.descarregar_periodico()
    assert len(chamadas) == 2


# ------------------------------------------------------------------ a base em baixo
def test_base_em_baixo_nao_perde_o_buffer_nao_parte_e_nao_mostra_a_palavra_passe(relogio, caplog):
    m = Metricas(None, relogio=relogio, url_bd=URL_EM_BAIXO)
    m.evento("sessao", "pt", "premiado", "computador")
    m.amostrar(1, 1, 1, 1, 1, 0, 0)
    m.pedido("GET /x", 200, 5)
    with caplog.at_level(logging.DEBUG), pytest.raises(Exception, match=r".*"):
        m.descarregar(tudo=True)
    assert m.erro_bd is True and m.estado_bd()["erro"] is True
    assert len(m._eventos) == 2 and len(m._amostras) == 1 and len(m._pedidos) == 1     # o `arranque` e a sessao continuam por gravar
    assert SEGREDO not in caplog.text and SEGREDO not in repr(m.estado_bd())
    assert m.resumo(0)["sessoes"] == 0                                  # o painel recebe vazio em vez de rebentar (e sem esperar por cada consulta)
    assert m._bloqueado_ate == relogio() + metricas.PAUSA_APOS_FALHA_S
    m.fechar()                                                          # terminar o servico nao depende da base


def test_o_buffer_nao_cresce_sem_fim_com_a_base_em_baixo(relogio):
    m = Metricas(None, relogio=relogio, url_bd=URL_EM_BAIXO)
    m._eventos = [(1, "pagina", "", "", "", 0.0, 0.0, 0.0)] * (metricas.BUFFER_LIMITE_FALHAS + 100)
    with pytest.raises(Exception, match=r".*"):
        m.descarregar()
    assert len(m._eventos) == metricas.BUFFER_LIMITE_FALHAS
    m.fechar()


# ------------------------------------------------------------------ Postgres a sério
@precisa_de_pg
def test_os_dados_sobrevivem_a_um_reinicio(pg, relogio):
    pg.evento("sessao", "pt", "premiado", "computador")
    pg.pedido("GET /api/linguas", 200, 4)
    pg.amostrar(12.5, 100, 50, 300, 20, 1, 0)
    pg.fechar()
    novo = Metricas(None, relogio=relogio, url_bd=URL_PG)               # o "servico" voltou a arrancar
    try:
        assert novo.resumo(0)["sessoes"] == 1
        assert novo.resumo(0)["arranques"] == 2                         # o do arranque anterior e o deste
        assert novo.tabela_pedidos(0)[0]["pedido"] == "GET /api/linguas"
        assert novo.serie_sistema(0, 60)[0]["cpu"] == 12.5
        assert novo.dados_desde() == int(relogio())
        assert novo.persistente and novo.estado_bd()["tipo"] == "postgres"
    finally:
        novo.fechar()


@precisa_de_pg
def test_o_mesmo_minuto_gravado_duas_vezes_soma_no_postgres(pg, relogio):
    pg.pedido("GET /api/linguas", 200, 4)
    pg.descarregar(tudo=True)
    pg.pedido("GET /api/linguas", 500, 900)
    pg.descarregar(tudo=True)
    linha = pg.tabela_pedidos(0)[0]
    assert linha["n"] == 2 and linha["e5"] == 1 and linha["max_ms"] == 900.0


@precisa_de_pg
def test_ligacao_cortada_volta_a_ligar_sozinha(pg):
    """O Neon corta as ligacoes quando suspende: a gravacao e a consulta seguintes tem de funcionar na mesma."""
    pg.evento("sessao", "pt", "premiado", "computador")
    pg.descarregar(tudo=True)
    pg._armazem._lig.close()                                            # como se a base tivesse cortado a ligacao
    pg.evento("sessao", "en", "premiado", "movel")
    pg.descarregar(tudo=True)                                           # grava (volta a ligar)
    assert pg.erro_bd is False
    pg._armazem._lig.close()
    assert pg.resumo(0)["sessoes"] == 2                                 # consulta (volta a ligar)
    assert pg.erro_bd is False


@precisa_de_pg
def test_recupera_quando_a_base_volta(pg, relogio):
    boa = pg._armazem
    pg._armazem = metricas._Postgres(URL_EM_BAIXO)
    pg.evento("sessao", "pt", "premiado", "computador")
    with pytest.raises(Exception, match=r".*"):
        pg.descarregar(tudo=True)
    assert pg.erro_bd is True
    pg._armazem = boa                                                   # a base voltou
    pg.descarregar(tudo=True)
    assert pg.erro_bd is True                                           # ainda na pausa depois da falha: nem tenta
    relogio.t += metricas.PAUSA_APOS_FALHA_S + 1
    pg.descarregar(tudo=True)
    assert pg.erro_bd is False and pg.resumo(0)["sessoes"] == 1         # nada se perdeu entretanto
