"""Anti-sono: o servico chama-se a si proprio para o Render gratuito nao o adormecer (src/web/manter_acordado.py)."""
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from web import config
from web.manter_acordado import EstadoAcordado, chamar, ciclo


class _Servidor:
    """Um servidor HTTP local que conta os pedidos (faz de «proxy publico do Render»)."""

    def __init__(self, estado=200):
        self.pedidos = []
        outer = self

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                outer.pedidos.append((self.path, self.headers.get("User-Agent")))
                self.send_response(estado)
                self.end_headers()
                self.wfile.write(b"{}")

            def log_message(self, *a):
                pass

        self.http = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.http.server_port}"
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def parar(self):
        self.http.shutdown()
        self.http.server_close()


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for n in ("KEEPALIVE", "KEEPALIVE_URL", "KEEPALIVE_MIN", "RENDER_EXTERNAL_URL"):
        monkeypatch.delenv(n, raising=False)


def test_fora_do_render_nao_faz_nada():
    assert config.manter_acordado() == ("", 0.0)


def test_no_render_chama_o_url_publico_de_10_em_10_minutos(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://gerador-rifas.onrender.com/")
    assert config.manter_acordado() == ("https://gerador-rifas.onrender.com", 600.0)


@pytest.mark.parametrize("valor,esperado", [("5", 300.0), ("0.2", 60.0), ("99", 840.0), ("abc", 600.0), ("14", 840.0)])
def test_o_intervalo_fica_sempre_abaixo_dos_15_min_do_render(monkeypatch, valor, esperado):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://x.onrender.com")
    monkeypatch.setenv("KEEPALIVE_MIN", valor)
    assert config.manter_acordado()[1] == esperado and config.manter_acordado()[1] < 15 * 60


@pytest.mark.parametrize("valor", ["0", "nao", "false", "OFF"])
def test_keepalive_zero_desliga(monkeypatch, valor):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://x.onrender.com")
    monkeypatch.setenv("KEEPALIVE", valor)
    assert config.manter_acordado() == ("", 0.0)


def test_keepalive_url_manda_e_so_aceita_http(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://render.onrender.com")
    monkeypatch.setenv("KEEPALIVE_URL", "https://meu-dominio.pt")
    assert config.manter_acordado()[0] == "https://meu-dominio.pt"
    for mau in ("file:///etc/passwd", "javascript:1", "ftp://x", "https://a b"):
        monkeypatch.setenv("KEEPALIVE_URL", mau)
        monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)
        assert config.manter_acordado() == ("", 0.0), mau


def test_chamar_diz_se_deu_200_e_nunca_levanta():
    s = _Servidor(200)
    try:
        ok, ms = chamar(f"{s.url}/health")
        assert ok is True and ms >= 0 and s.pedidos == [("/health", "gerador-rifas-manter-acordado")]
    finally:
        s.parar()
    s = _Servidor(503)
    try:
        assert chamar(f"{s.url}/health")[0] is False                        # 503 conta como falha
    finally:
        s.parar()
    assert chamar("http://127.0.0.1:1/health", tempo_s=1)[0] is False        # ninguem a ouvir


def test_o_ciclo_chama_o_health_e_regista_o_resultado():
    s = _Servidor(200)

    async def correr():
        estado = EstadoAcordado(ativo=True, url=s.url, cada_s=0.05)
        tarefa = asyncio.create_task(ciclo(estado, primeira_espera_s=0.01))
        await asyncio.sleep(0.4)
        tarefa.cancel()
        return estado

    try:
        e = asyncio.run(correr())
    finally:
        s.parar()
    assert e.chamadas >= 3 and e.falhas == 0 and e.ultima_ok is True and e.ultima_em > 0
    assert {p for p, _ in s.pedidos} == {"/health"}


def test_o_ciclo_conta_as_falhas(monkeypatch):
    monkeypatch.setattr("web.manter_acordado.chamar", lambda url, tempo_s=20.0: (False, 3.0))      # (recusar a ligacao demora ~2 s no Windows)

    async def correr():
        estado = EstadoAcordado(ativo=True, url="http://127.0.0.1:1", cada_s=0.05)
        tarefa = asyncio.create_task(ciclo(estado, primeira_espera_s=0.01))
        await asyncio.sleep(0.3)
        tarefa.cancel()
        return estado

    e = asyncio.run(correr())
    assert e.falhas >= 1 and e.falhas == e.chamadas and e.ultima_ok is False


def test_o_health_do_proprio_servico_nao_conta_nas_metricas(tmp_path):
    from fastapi.testclient import TestClient
    from web.app import criar_app
    from web.metricas import Metricas
    m = Metricas(None)
    c = TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "d", metricas=m))
    for _ in range(5):
        c.get("/health", headers={"User-Agent": "gerador-rifas-manter-acordado"})
    assert m.tabela_pedidos(0) == [] and m.resumo(0)["paginas_vistas"] == [] and m.proxy()["pedidos"] == 0


def test_o_painel_diz_se_o_anti_sono_esta_ativo(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from web.app import criar_app
    monkeypatch.setenv("ADMIN_TOKEN", "palavra-passe-longa-123")
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:1")
    with TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "d")) as c:                 # com o ciclo de vida (arranca o anti-sono)
        assert c.post("/api/admin/entrar", json={"token": "palavra-passe-longa-123"}).status_code == 200
        a = c.get("/api/admin/estado").json()["acordado"]
    assert a["ativo"] is True and a["cada_min"] == 10.0 and a["chamadas"] == 0 and a["ultima_ok"] is None
