"""Metricas (src/web/metricas.py): agregacao, histogramas, retencao, privacidade e o proxy."""
import json
import os
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


URL_PG = os.environ.get("TEST_DATABASE_URL", "")                   # um Postgres descartavel (no CI: o contentor do servico); sem ele os testes de Postgres saltam


def limpar_postgres() -> None:
    import psycopg

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        lig.execute("DROP TABLE IF EXISTS sistema, pedidos, eventos")


@pytest.fixture(params=["sqlite", pytest.param("postgres", marks=pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL"))])
def m(request, tmp_path, relogio):
    """As mesmas consultas e agregacoes correm no SQLite e no Postgres: o painel nao pode depender da base."""
    if request.param == "postgres":
        limpar_postgres()
        obj = Metricas(None, relogio=relogio, url_bd=URL_PG)
    else:
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
    assert m._armazem.executar("SELECT COUNT(*) FROM eventos")[0][0] == 0
    assert m._armazem.executar("SELECT COUNT(*) FROM sistema")[0][0] == 0


def test_o_texto_longo_e_cortado_e_nao_parte_o_sql(m):
    m.evento("sessao", "x" * 500, "'; DROP TABLE eventos; --", "computador")
    assert m.resumo(0)["sessoes"] == 1
    assert max(len(d["chave"]) for d in m.resumo(0)["linguas"]) <= 40


def test_privacidade_nenhum_ip_fica_no_disco(m, relogio):
    if m.persistente:
        pytest.skip("o ficheiro bruto so existe no SQLite; o teste abaixo olha para as linhas do Postgres")
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


def test_privacidade_nenhum_ip_fica_na_base_postgres(m, relogio):
    """O mesmo teste de privacidade, lendo todas as linhas de todas as tabelas (no Postgres nao ha ficheiro para ler)."""
    if not m.persistente:
        pytest.skip("o SQLite tem o teste do ficheiro bruto")
    for ip in ("203.0.113.7", "198.51.100.23", "2001:db8::1"):
        m.cliente(ip, tem_xff=True)
        m.pedido("GET /api/linguas", 200, 3)
    m.evento("sessao", "pt", "matrix", "computador")
    m.amostrar(1, 1, 1, 1, 1, 0, 0)
    m.descarregar(tudo=True)
    tudo = repr([m._armazem.executar(f"SELECT * FROM {t}") for t in ("eventos", "sistema", "pedidos")])   # noqa: S608
    for ip in ("203.0.113.7", "198.51.100.23", "2001:db8"):
        assert ip not in tudo
    assert "matrix" in tudo


# ---------------------------------------------------------------- evolucao dia a dia
DIA = 86400


def _painel(d: dict, id_: str) -> dict:
    return next(p for p in d["paineis"] if p["id"] == id_)


def _serie(d: dict, id_: str, nome: str | None = None) -> list:
    p = _painel(d, id_)
    return next(s for s in p["series"] if nome is None or s["nome"] == nome)["valores"]


def test_a_evolucao_poe_cada_evento_no_seu_dia(m, relogio):
    base = relogio.t                                                        # 2027-01-15 08:00 UTC
    for dias_atras, n in ((2, 1), (1, 3), (0, 2)):
        relogio.t = base - dias_atras * DIA
        for _ in range(n):
            m.evento("sessao", "pt", "premiado", "computador")
    relogio.t = base - DIA
    m.evento("geracao", "ok", "", "unico", v1=10.0, v2=500, v3=100)
    m.evento("geracao", "ok", "", "unico", v1=30.0, v2=700, v3=140)
    m.evento("geracao", "falhou", "err_digitos", v1=1.0)
    m.evento("descarga", "pdf")
    relogio.t = base
    d = m.evolucao(4)
    assert d["dias"] == 4 and d["dias_lista"][-1] == "2027-01-15" and d["dias_lista"][0] == "2027-01-12" and len(d["dias_lista"]) == 4
    assert _serie(d, "sessoes") == [0, 1, 3, 2]
    assert _serie(d, "numeros") == [0, 0, 1200, 0] and _serie(d, "paginas_geradas") == [0, 0, 240, 0]
    assert _serie(d, "geracoes", "Concluída") == [0, 0, 2, 0] and _serie(d, "geracoes", "Falhou") == [0, 0, 1, 0]
    assert _serie(d, "falhas", "err_digitos") == [0, 0, 1, 0]
    assert _serie(d, "duracao", "Mediana")[2] == 30.0 and _serie(d, "duracao", "Mediana")[0] is None            # sem gerações = sem valor, não zero
    assert _serie(d, "funil", "Gerações descarregadas")[2] == 50.0 and _serie(d, "funil", "Sessões que geraram")[3] == 0.0
    assert _serie(d, "linguas", "pt") == [0, 1, 3, 2] and _serie(d, "temas", "premiado") == [0, 1, 3, 2]


def test_a_evolucao_segue_o_fuso_do_browser(m, relogio):
    relogio.t = 1_800_000_000.0 + 15 * 3600 + 1800                           # 2027-01-15 23:30 UTC
    m.evento("sessao", "pt", "x", "computador")
    utc = m.evolucao(2, 0)
    mais_uma_hora = m.evolucao(2, 60)                                        # 00:30 de dia 16
    assert utc["dias_lista"] == ["2027-01-14", "2027-01-15"] and _serie(utc, "sessoes") == [0, 1]
    assert mais_uma_hora["dias_lista"] == ["2027-01-15", "2027-01-16"] and _serie(mais_uma_hora, "sessoes") == [0, 1]
    assert m.evolucao(2, -300)["dias_lista"][-1] == "2027-01-15"            # a oeste de Greenwich o dia ainda e o 15
    assert m.evolucao(2, 99999)["fuso_min"] == 840                           # o fuso e limitado


def test_a_evolucao_junta_o_resto_em_outros_e_separa_os_robos(m, relogio):
    for i in range(12):
        m.evento("sessao", f"l{i:02d}", "x", "computador")
    m.evento("sessao", "l00", "x", "computador")
    m.evento("pagina", "/", c="computador")
    m.evento("pagina", "/", c="robo")
    m.evento("pagina", "/sobre", c="robo")
    d = m.evolucao(1)
    nomes = [s["nome"] for s in _painel(d, "linguas")["series"]]
    assert len(nomes) == 9 and nomes[0] == "l00" and nomes[-1] == "Outros" and _serie(d, "linguas", "Outros") == [4]
    assert _serie(d, "paginas_vistas", "Pessoas") == [1] and _serie(d, "paginas_vistas", "Robôs") == [2]
    assert [s["nome"] for s in _painel(d, "rotas")["series"]] == ["/"]        # as rotas so contam pessoas


def test_a_evolucao_inclui_pedidos_latencia_e_sistema_sem_as_sondagens(m, relogio):
    for _ in range(3):
        m.pedido("POST /api/sessoes/{id_}/previa", 200, 20)
    m.pedido("POST /api/sessoes/{id_}/previa", 429, 5)
    m.pedido("GET /x", 500, 40)
    m.pedido("GET /api/sessoes/{id_}/trabalho", 200, 3)                      # a sondagem do progresso nao conta
    m.amostrar(cpu=10.0, mem_srv=100.0, mem_motor=50.0, mem_cont=160.0, disco=5.0, sessoes=2, geracoes=1)
    relogio.t += 30
    m.amostrar(cpu=30.0, mem_srv=120.0, mem_motor=70.0, mem_cont=200.0, disco=6.0, sessoes=4, geracoes=0)
    d = m.evolucao(2)
    assert _serie(d, "pedidos", "Certos") == [0, 3] and _serie(d, "pedidos", "Erros do cliente (4xx)") == [0, 1]
    assert _serie(d, "pedidos", "Erros do servidor (5xx)") == [0, 1]
    assert _serie(d, "latencia", "Mediana")[0] is None and _serie(d, "latencia", "Mediana")[1] is not None
    assert _serie(d, "cpu", "Média") == [None, 20.0] and _serie(d, "cpu", "Máxima") == [None, 30.0]
    assert _serie(d, "memoria", "Motor") == [None, 70.0] and _serie(d, "simultaneos", "Sessões") == [None, 4]


def test_a_evolucao_cobre_todos_os_tipos_de_evento_que_se_gravam(m, relogio):
    for tipo, a in (("galeria", "natal"), ("precario", "natal"), ("precario_moeda", "EUR"), ("editor", "usar"), ("logotipo", "ok"), ("verificacao", "ok"), ("api_geracao", "ok"), ("limite", "sessoes"),
                    ("erro_http", "404"), ("admin", "entrou"), ("pais", "PT"), ("ecra", "telemovel"), ("comentario", "anonimo"), ("problema", "ok")):
        m.evento(tipo, a, v1=390)
    m.evento("motor_reiniciado")
    d = m.evolucao(1)
    for id_, nome in (("galeria", "natal"), ("precario", "natal"), ("precario_moeda", "EUR"), ("editor", "Usado"), ("logotipo", "Certo"), ("verificacao", "ok"), ("api_geracao", "ok"), ("limites", "sessoes"),
                      ("erros_http", "404"), ("admin", "entrou"), ("paises", "PT"), ("classes_ecra", "telemovel"), ("comentarios", "Anónimos"), ("problemas", "Registados no GitHub")):
        assert _serie(d, id_, nome) == [1], id_
    assert _serie(d, "motor", "Reinícios do motor") == [1] and _serie(d, "motor", "Arranques do serviço") == [1]
    assert _serie(d, "janelas", "Telemóvel (< 414 px)") == [1]


def test_a_evolucao_sem_dados_nao_parte_e_os_dias_sao_limitados(m):
    d = m.evolucao(500)
    assert d["dias"] == metricas.DIAS_MAXIMOS == len(d["dias_lista"])
    assert sum(_serie(d, "sessoes")) == 0 and sum(_serie(d, "numeros")) == 0           # o `arranque` do servico nao e uma sessao
    assert m.evolucao(0)["dias"] == 1


def test_a_evolucao_nao_traz_nada_pessoal(m):
    m.cliente("203.0.113.9", True, True)
    m.evento("sessao", "pt", "x", "computador")
    assert "203.0.113.9" not in json.dumps(m.evolucao(7))
