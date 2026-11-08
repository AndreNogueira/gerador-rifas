"""O painel de administracao: so existe com ADMIN_TOKEN, so se entra com a palavra-passe, e mostra o que de facto aconteceu."""
import re
import time
import urllib.parse
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import admin, config
from web.app import criar_app
from web.sistema import Observador
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
TOKEN = "palavra-passe-muito-longa-123"
INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("PUBLIC_URL", "RENDER_EXTERNAL_URL", "ADMIN_TOKEN", "RENDER", "RIFAS_METRICAS"):
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setenv("MAX_NUMEROS", "1000000")


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


def _app(tmp_path, motor=None, base="http://testserver"):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor), base_url=base)


@pytest.fixture
def sem_token(tmp_path):
    return _app(tmp_path)


@pytest.fixture
def com_token(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    return _app(tmp_path)


def _entrar(c, token=TOKEN):
    return c.post("/api/admin/entrar", json={"token": token})


# ---------------------------------------------------------------- existencia
@pytest.mark.parametrize("valor", [None, "", "curta", "x" * 11])
def test_sem_token_valido_o_painel_nao_existe(tmp_path, monkeypatch, valor):
    if valor is not None:
        monkeypatch.setenv("ADMIN_TOKEN", valor)
    c = _app(tmp_path)
    assert not admin.ativo()
    assert c.get("/admin").status_code == 404
    for caminho in ("/api/admin/estado", "/api/admin/dados"):
        assert c.get(caminho).status_code == 404
    assert c.post("/api/admin/entrar", json={"token": valor or "x"}).status_code == 404
    assert c.post("/api/admin/sair").status_code == 204                          # nao ha nada para fechar: inofensivo


def test_a_api_do_painel_nao_aparece_na_documentacao(com_token):
    assert "/api/admin" not in str(com_token.get("/api/openapi.json").json()["paths"])


# ---------------------------------------------------------------- a pagina
def test_a_pagina_do_painel_nao_se_indexa_nem_fica_em_cache(com_token):
    r = com_token.get("/admin")
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store" and r.headers["x-robots-tag"] == "noindex, nofollow"
    assert 'content="noindex,nofollow"' in r.text and 'rel="canonical"' not in r.text and "application/ld+json" not in r.text
    assert "/admin" not in com_token.get("/sitemap.xml").text
    assert "Disallow: /admin" in com_token.get("/robots.txt").text


# ---------------------------------------------------------------- acesso
def test_sem_cookie_toda_a_api_do_painel_e_404(com_token):
    for caminho in ("/api/admin/estado", "/api/admin/dados", "/api/admin/dados?intervalo=24h"):
        r = com_token.get(caminho)
        assert r.status_code == 404 and "Cache-Control" in r.headers and "no-store" in r.headers["cache-control"]


def test_palavra_passe_errada_e_401_e_nao_da_cookie(com_token):
    r = _entrar(com_token, "errada-errada-errada")
    assert r.status_code == 401 and "set-cookie" not in r.headers and TOKEN not in r.text
    assert com_token.get("/api/admin/estado").status_code == 404


def test_cinco_tentativas_por_minuto_e_depois_nem_a_certa_entra(com_token):
    for _ in range(admin.MAX_TENTATIVAS_IP):
        assert _entrar(com_token, "errada-errada-errada").status_code == 401
    assert _entrar(com_token, "errada-errada-errada").status_code == 429
    assert _entrar(com_token).status_code == 429                                   # travado: a certa tambem espera
    assert com_token.get("/api/admin/estado").status_code == 404


def test_o_cookie_e_httponly_strict_e_so_para_a_api_do_painel(com_token):
    r = _entrar(com_token)
    assert r.status_code == 200 and r.json()["ok"] is True
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie and "path=/api/admin" in cookie and f"max-age={admin.DURACAO_S}" in cookie
    assert "secure" not in cookie                                                  # em http local nao pode ser «secure»
    assert TOKEN not in r.headers["set-cookie"] and TOKEN not in r.text            # a palavra-passe nunca volta ao browser


def test_em_https_o_cookie_e_secure(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    c = _app(tmp_path, base="https://testserver")
    assert "secure" in _entrar(c).headers["set-cookie"].lower()


def test_com_cookie_o_estado_e_os_dados_funcionam_e_sem_segredos(com_token):
    _entrar(com_token)
    e = com_token.get("/api/admin/estado")
    assert e.status_code == 200 and "no-store" in e.headers["cache-control"]
    d = e.json()
    assert d["versao"] and d["sistema"]["mem_servidor_mb"] > 10 and d["sistema"]["python"] and d["intervalos"] == ["1h", "6h", "24h", "7d", "30d"]
    assert d["limites"]["max_numeros"] == 1_000_000 and d["proxy"]["veredicto"] in ("sem_dados", "poucos_pedidos", "sem_proxy")
    assert TOKEN not in e.text and "ADMIN_TOKEN" not in e.text and "/tmp" not in e.text.replace("\\", "/").lower()
    r = com_token.get("/api/admin/dados?intervalo=24h").json()
    assert r["intervalo"] == "24h" and r["passo_s"] == 300 and set(r) >= {"sistema", "pedidos", "eventos", "tabela_pedidos", "resumo"}
    assert com_token.get("/api/admin/dados?intervalo=1ano").status_code == 422


def test_cookie_adulterado_expirado_ou_de_outro_token_e_404(com_token, monkeypatch):
    _entrar(com_token)
    bom = com_token.cookies.get("rifas_admin")
    expira = bom.split(".")[0]
    for mau in (bom[:-1] + ("0" if bom[-1] != "0" else "1"), f"{int(expira) + 999}.{bom.split('.')[1]}", "lixo", "x.y", f"{int(time.time()) - 5}.abc"):
        com_token.cookies.clear()
        com_token.cookies.set("rifas_admin", mau)
        assert com_token.get("/api/admin/estado").status_code == 404, mau
    com_token.cookies.clear()
    com_token.cookies.set("rifas_admin", bom)
    assert com_token.get("/api/admin/estado").status_code == 200
    assert admin.cookie_valido(bom, agora=int(expira) + 1) is False                # passou o prazo
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN + "-novo")                             # mudar a palavra-passe fecha todas as sessoes
    assert com_token.get("/api/admin/estado").status_code == 404


def test_sair_apaga_o_cookie(com_token):
    _entrar(com_token)
    r = com_token.post("/api/admin/sair")
    assert r.status_code == 204 and "max-age=0" in r.headers["set-cookie"].lower()
    assert com_token.get("/api/admin/estado").status_code == 404


# ---------------------------------------------------------------- o que o painel mostra
def _gerar_uma_vez(c, visual="matrix", agente="Mozilla/5.0 (iPhone) Mobile"):
    h = {"X-Lingua": "pt", "X-Visual": visual, "User-Agent": agente}
    s = c.post("/api/sessoes", headers=h).json()["sessao"]
    cab = {"X-Nome": urllib.parse.quote("Rifa de Teste.pdf"), "Content-Type": "application/octet-stream", "X-Lingua": "pt"}
    assert c.put(f"/api/sessoes/{s}/template", content=(FX / "template_exemplo.pdf").read_bytes(), headers=cab).status_code == 200
    assert c.put(f"/api/sessoes/{s}/algarismos", content=(FX / "digitos_exemplo.png").read_bytes(), headers=cab).json()["pronto"]
    campos = dict(nome="Rifa", inicio="1", fim="20", digitos="4", modo="varios", max_ficheiro="10", papel="A4", margem="5", porfolha="")
    assert c.post(f"/api/sessoes/{s}/previa", json=campos, headers=h).status_code == 200
    assert c.post(f"/api/sessoes/{s}/gerar", json=campos, headers=h).status_code == 202
    for _ in range(300):
        if c.get(f"/api/sessoes/{s}/trabalho").json()["estado"] in ("ok", "erros", "falhou", "cancelado"):
            break
        time.sleep(0.2)
    assert c.get(f"/api/sessoes/{s}/descarregar").status_code == 200
    return s


def test_o_painel_mostra_o_que_aconteceu_sem_dados_pessoais(tmp_path, monkeypatch, motor):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    with _app(tmp_path, motor=motor) as c:
        _gerar_uma_vez(c)
        c.get("/", headers={"User-Agent": "Mozilla/5.0 Chrome"})
        c.get("/", headers={"User-Agent": "Googlebot/2.1"})
        c.post("/api/sessoes", headers={"X-Visual": "<script>alert(1)</script>"})            # o que o cliente diz nao entra sem filtro
        _entrar(c)
        d = c.get("/api/admin/dados?intervalo=1h").json()
        r = d["resumo"]
        assert r["sessoes"] == 2 and {x["chave"] for x in r["temas"]} == {"matrix", "outro"}
        assert {x["chave"]: x["n"] for x in r["dispositivos"]}["movel"] == 1
        assert r["previas"]["ok"] == 1 and r["templates"]["ok"] == 1 and r["algarismos"]["ok"] == 1
        assert r["geracoes"] == {"ok": 1} and r["numeros"] == 20 and r["paginas"] > 0
        assert r["descargas"] == [{"chave": "zip", "n": 1}] and r["duracao"]["mediana_s"] is not None and r["duracao"]["mediana_s"] >= 0   # 0.0 num runner rapido (arredonda a 0,1 s)
        assert r["paginas_vistas"] == [{"chave": "/", "n": 1}] and r["robos"] == 1
        # o funil conta eventos por etapa (nao pessoas): 2 sessoes, 1 template, 1 algarismos, 1 pre-visualizacao, 1 geracao, 1 descarga
        assert [(f["chave"], f["n"]) for f in r["funil"]] == [("Sessões abertas", 2), ("Template carregado", 1), ("Algarismos prontos", 1),
                                                                 ("Pré-visualização", 1), ("Geração concluída", 1), ("Descarga", 1)]
        pedidos = {t["pedido"]: t for t in d["tabela_pedidos"]}
        assert pedidos["POST /api/sessoes"]["n"] == 2 and pedidos["POST /api/sessoes/{id_}/gerar"]["n"] == 1
        assert pedidos["GET /api/sessoes/{id_}/trabalho"]["sondagem"] is True
        assert all("sessoes/" + "{id_}" in k or k.startswith(("GET /api/", "POST /api/", "PUT /api/", "DELETE /api/")) for k in pedidos)
        assert sum(x["n"] for x in d["pedidos"]) > 0 and sum(x["geracoes"] for x in d["eventos"]) == 1
        estado = c.get("/api/admin/estado").json()
        assert estado["sistema"]["sessoes_ativas"] == 2 and estado["sistema"]["motor_vivo"] is True
        bruto = str(d) + str(estado)
        assert "Rifa de Teste" not in bruto and "Rifa São" not in bruto and TOKEN not in bruto


def test_uma_geracao_cancelada_ou_falhada_conta_com_motivo(tmp_path, monkeypatch, motor):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    with _app(tmp_path, motor=motor) as c:
        h = {"X-Lingua": "pt"}
        s = c.post("/api/sessoes", headers=h).json()["sessao"]
        cab = {"X-Nome": "t.pdf", "Content-Type": "application/octet-stream"}
        c.put(f"/api/sessoes/{s}/template", content=(FX / "template_exemplo.pdf").read_bytes(), headers=cab)
        c.put(f"/api/sessoes/{s}/algarismos", content=(FX / "digitos_exemplo.png").read_bytes(), headers=cab)
        invalido = dict(nome="", inicio="1", fim="20", digitos="4", modo="varios", max_ficheiro="10", papel="A4", margem="5", porfolha="")
        assert c.post(f"/api/sessoes/{s}/gerar", json=invalido, headers=h).status_code == 422          # sem nome: recusado antes de comecar
        _entrar(c)
        r = c.get("/api/admin/dados?intervalo=1h").json()["resumo"]
        assert r["erros_http"] == [{"chave": "422", "n": 1}] and r["geracoes"] == {}


# ---------------------------------------------------------------- coerencia
def test_os_temas_aceites_nas_metricas_sao_os_do_frontend():
    from web import rotas
    fonte = (Path(__file__).resolve().parents[1] / "src" / "web" / "frontend" / "src" / "temas.ts").read_text(encoding="utf-8")
    assert set(re.findall(r'id: "([a-z0-9]+)"', fonte)) == set(rotas._VISUAIS)


def test_o_observador_le_o_sistema(tmp_path):
    (tmp_path / "x.bin").write_bytes(b"0" * 3 * 1024 * 1024)
    o = Observador(tmp_path)
    d = o.ler(sessoes=3, geracao_em_curso=False, reinicios_motor=2)
    assert d["mem_servidor_mb"] > 10 and d["disco_usado_mb"] >= 3 and d["disco_livre_mb"] > 0
    assert d["sessoes_ativas"] == 3 and d["motor_reinicios"] == 2 and d["cpu_nucleos"] >= 1 and d["cpu"] >= 0


def test_um_filho_que_desaparece_a_meio_da_leitura_nao_derruba_o_observador(tmp_path):
    import psutil

    class Fantasma:                       # o processo do motor acabou entre `children()` e a 1.a leitura de CPU
        pid = 999_999

        def cpu_percent(self, _=None):
            raise psutil.NoSuchProcess(self.pid)

    o = Observador(tmp_path)
    o._eu = type("Eu", (), {"children": lambda self, recursive: [Fantasma()], "cpu_percent": lambda self, _=None: 0.0,
                            "memory_info": psutil.Process().memory_info})()
    d = o.ler(sessoes=0, geracao_em_curso=False, reinicios_motor=0)
    assert d["motor_vivo"] is False and d["mem_motor_mb"] == 0.0


def test_config_metricas_efemeras(monkeypatch):
    assert config.metricas_efemeras() is False
    monkeypatch.setenv("RENDER", "true")
    assert config.metricas_efemeras() is True
    monkeypatch.setenv("RIFAS_METRICAS", "/data/m.sqlite3")
    assert config.metricas_efemeras() is False
