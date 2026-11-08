"""Metricas (src/web/metricas.py): agregacao, histogramas, retencao, privacidade e o proxy."""
import json
import sqlite3
import time

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from web import metricas
from web.metricas import INTERVALOS, Metricas, dispositivo, percentil


class Relogio:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def relogio():
    return Relogio()


@pytest.fixture
def m(tmp_path, relogio):
    obj = Metricas(tmp_path / "m.sqlite3", relogio=relogio)
    yield obj
    obj.fechar()


def test_percentil_por_baldes():
    hist = [0] * (len(metricas.LIMITES_MS) + 1)
    assert percentil(hist, 0.5) is None
    hist[2], hist[5] = 90, 10                          # 90 pedidos ate 25 ms e 10 ate 250 ms
    assert percentil(hist, 0.5) == 25.0 and percentil(hist, 0.95) == 250.0
    hist[-1] = 1000                                    # o que passa do ultimo limite conta como o ultimo limite
    assert percentil(hist, 0.99) == float(metricas.LIMITES_MS[-1])


@pytest.mark.parametrize("ua,esperado", [
    ("Mozilla/5.0 (Windows NT 10.0) AppleWebKit Chrome/150", "computador"),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 19) Mobile Safari", "movel"),
    ("Mozilla/5.0 (Linux; Android 16) Mobile", "movel"),
    ("Googlebot/2.1 (+http://www.google.com/bot.html)", "robo"),
    ("facebookexternalhit/1.1", "robo"),
    ("curl/9.0", "robo"),
    ("", "computador"),
])
def test_dispositivo(ua, esperado):
    assert dispositivo(ua) == esperado


def test_pedidos_agregam_por_minuto_e_calculam_erros_e_latencia(m, relogio):
    for ms in (3, 4, 8, 20, 400):
        m.pedido("POST /api/sessoes/{id_}/previa", 200, ms)
    m.pedido("POST /api/sessoes/{id_}/previa", 422, 30)
    m.pedido("POST /api/sessoes/{id_}/previa", 500, 900)
    m.pedido("GET /api/sessoes/{id_}/trabalho", 200, 2)             # sondagem: fora da serie, dentro da tabela
    relogio.t += 120
    tabela = {d["pedido"]: d for d in m.tabela_pedidos(int(relogio.t) - 600)}
    p = tabela["POST /api/sessoes/{id_}/previa"]
    assert (p["n"], p["e4"], p["e5"]) == (7, 1, 1) and p["max_ms"] == 900 and p["p50"] == 25.0
    assert tabela["GET /api/sessoes/{id_}/trabalho"]["sondagem"] is True
    serie = m.serie_pedidos(int(relogio.t) - 600, 60)
    assert sum(d["n"] for d in serie) == 7                          # as sondagens nao entram
    assert serie[0]["p95"] == 1000.0


def test_os_pedidos_do_mesmo_minuto_que_ja_foi_para_o_disco_somam(m, relogio):
    m.pedido("GET /x", 200, 5)
    m.descarregar(tudo=True)
    m.pedido("GET /x", 200, 7)
    m.descarregar(tudo=True)
    assert m.tabela_pedidos(0)[0]["n"] == 2


def test_eventos_e_resumo(m, relogio):
    for lg, visual, disp in (("pt", "matrix", "computador"), ("pt", "premiado", "movel"), ("en", "matrix", "computador")):
        m.evento("sessao", lg, visual, disp)
    m.evento("previa", "ok", v1=120)
    m.evento("previa", "erro")
    m.evento("template", "ok")
    m.evento("algarismos", "tipo_invalido")
    m.evento("geracao", "ok", "", "varios", v1=12.0, v2=500, v3=100)
    m.evento("geracao", "ok", "", "unico", v1=70.0, v2=1000, v3=200)
    m.evento("geracao", "cancelado", v1=2.0, v2=900, v3=0)
    m.evento("geracao", "falhou", "err_digitos", v1=1.0, v2=10)
    m.evento("descarga", "zip")
    m.evento("pagina", "/", c="computador")
    m.evento("pagina", "/", c="robo")
    m.evento("erro_http", "429", "aviso")
    m.evento("erro_http", "429", "aviso")
    m.evento("motor_reiniciado")
    r = m.resumo(0)
    assert r["sessoes"] == 3 and r["previas"] == {"ok": 1, "erro": 1}
    assert r["templates"] == {"ok": 1, "erro": 0} and r["algarismos"] == {"ok": 0, "erro": 1}
    assert r["geracoes"] == {"ok": 2, "cancelado": 1, "falhou": 1}
    assert r["numeros"] == 1500 and r["paginas"] == 300                  # so as geracoes que acabaram bem
    assert r["duracao"]["mediana_s"] == 70.0 and r["duracao"]["max_s"] == 70.0
    assert {d["chave"]: d["n"] for d in r["linguas"]} == {"pt": 2, "en": 1}
    assert {d["chave"]: d["n"] for d in r["temas"]} == {"matrix": 2, "premiado": 1}
    assert {d["chave"]: d["n"] for d in r["dispositivos"]} == {"computador": 2, "movel": 1}
    assert r["paginas_vistas"] == [{"chave": "/", "n": 1}] and r["robos"] == 1       # os robos nao contam como visitas
    assert r["erros_http"] == [{"chave": "429", "n": 2}] and r["falhas"] == [{"chave": "err_digitos", "n": 1}]
    assert r["reinicios_motor"] == 1 and r["descargas"] == [{"chave": "zip", "n": 1}]
    assert sum(d["n"] for d in r["duracao"]["histograma"]) == 2


def test_series_agrupam_por_ponto(m, relogio):
    for i in range(3):
        m.evento("sessao", "pt", "x", "computador")
        relogio.t += 30
    m.evento("geracao", "ok", v2=40)
    serie = m.serie_eventos(int(relogio.t) - 3600, 60)
    assert sum(d["sessoes"] for d in serie) == 3 and sum(d["numeros"] for d in serie) == 40


def test_sistema_serie_e_dados_desde(m, relogio):
    inicio = int(relogio.t)
    for i in range(4):
        m.amostrar(cpu=10.0 + i, mem_srv=100.0, mem_motor=50.0 + i, mem_cont=160.0, disco=5.0, sessoes=i, geracoes=0)
        relogio.t += 30
    serie = m.serie_sistema(inicio - 10, 60)
    assert [d["sessoes"] for d in serie] == [1, 3]                      # o maximo de cada minuto
    assert serie[0]["cpu"] == 10.5 and serie[1]["mem_motor"] == 53.0
    assert m.dados_desde() == inicio                                    # o evento `arranque`


def test_retencao_apaga_o_antigo(m, relogio):
    m.evento("sessao", "pt", "x", "computador")
    m.amostrar(1, 1, 1, 1, 1, 0, 0)
    m.descarregar(tudo=True)
    relogio.t += metricas.RETENCAO_EVENTOS_S + 10
    m.descarregar(tudo=True)
    ligacao = sqlite3.connect(str(m.caminho))
    assert ligacao.execute("SELECT COUNT(*) FROM eventos").fetchone()[0] == 0
    assert ligacao.execute("SELECT COUNT(*) FROM sistema").fetchone()[0] == 0


def test_o_texto_longo_e_cortado_e_nao_parte_o_sql(m):
    m.evento("sessao", "x" * 500, "'; DROP TABLE eventos; --", "computador")
    assert m.resumo(0)["sessoes"] == 1
    assert max(len(d["chave"]) for d in m.resumo(0)["linguas"]) <= 40


def test_privacidade_nenhum_ip_fica_no_disco(m, relogio):
    for ip in ("203.0.113.7", "198.51.100.23", "2001:db8::1"):
        for _ in range(3):
            m.cliente(ip, tem_xff=True)
            m.pedido("GET /api/linguas", 200, 3)
    m.evento("sessao", "pt", "matrix", "computador")
    m.descarregar(tudo=True)
    m.fechar()
    bruto = m.caminho.read_bytes() + (m.caminho.parent / (m.caminho.name + "-wal")).read_bytes() if (m.caminho.parent / (m.caminho.name + "-wal")).exists() else m.caminho.read_bytes()
    for ip in (b"203.0.113.7", b"198.51.100.23", b"2001:db8"):
        assert ip not in bruto
    assert b"CREATE TABLE" in bruto                                      # a leitura do ficheiro serviu para alguma coisa


def test_proxy_sem_dados_poucos_pedidos_ok_e_problema(m, relogio):
    assert m.proxy()["veredicto"] == "sem_dados"
    for i in range(5):
        m.cliente(f"93.184.216.{i}", True)
    assert m.proxy()["veredicto"] == "poucos_pedidos"
    for i in range(40):
        m.cliente(f"93.184.216.{i % 15}", True)
    p = m.proxy()
    assert p["veredicto"] == "ok" and p["ips_distintos"] == 15 and p["privados_pct"] == 0
    m2 = Metricas(None, relogio=relogio)
    for _ in range(50):
        m2.cliente("10.20.30.40", True)                                  # todos com o IP do proxy, mas com X-Forwarded-For: mal configurado
    assert m2.proxy()["veredicto"] == "problema"
    m3 = Metricas(None, relogio=relogio)
    for _ in range(50):
        m3.cliente("127.0.0.1", False)                                   # local, sem proxy
    assert m3.proxy()["veredicto"] == "sem_proxy"


def test_o_proxy_so_olha_para_a_ultima_hora(m, relogio):
    for _ in range(30):
        m.cliente("10.0.0.1", True)
    relogio.t += 3700
    assert m.proxy()["veredicto"] == "sem_dados"


def test_intervalos_validos():
    for chave, (janela, passo) in INTERVALOS.items():
        assert janela // passo <= 720, chave                             # nunca mais de 720 pontos por grafico
    assert time.time() > 0
    assert json.dumps(list(INTERVALOS))
