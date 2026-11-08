"""O tipo de ecra e de dispositivo nas metricas: classificacao, POST /api/ecra e o que fica (e nao fica) guardado."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.metricas import Metricas, classe_do_ecra, familia, modelo_limpo

UA_IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"
UA_ANDROID = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36"
UA_ANDROID_TABLET = "Mozilla/5.0 (Linux; Android 14; SM-X900) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36"
UA_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"
UA_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36"


@pytest.mark.parametrize("ua,toque,larg,esperado", [
    (UA_IPHONE, True, 393, "iPhone"), (UA_ANDROID, True, 412, "Android (telemóvel)"), (UA_ANDROID_TABLET, True, 800, "Android (tablet)"),
    (UA_MAC, True, 1024, "iPad"), (UA_MAC, False, 1440, "Mac"), (UA_WIN, False, 1920, "Windows"),
    ("Mozilla/5.0 (X11; Linux x86_64)", False, 1920, "Linux"), ("Mozilla/5.0 (X11; CrOS x86_64)", False, 1366, "ChromeOS"), ("", False, 0, "Outro"),
])
def test_familia(ua, toque, larg, esperado):
    assert familia(ua, toque, larg) == esperado


@pytest.mark.parametrize("l,a,toque,esperado", [
    (393, 852, True, "telemóvel"), (440, 956, True, "telemóvel"), (360, 780, True, "telemóvel"), (412, 915, True, "telemóvel"),
    (820, 1180, True, "tablet"), (1024, 1366, True, "tablet"),
    (1366, 768, False, "computador pequeno (< 1400 px)"), (1536, 864, False, "computador médio (1400–1799 px)"),
    (1920, 1080, False, "computador Full HD (1800–2399 px)"), (2560, 1440, False, "computador QHD/2K (2400–3199 px)"),
    (3840, 2160, False, "computador 4K ou maior (≥ 3200 px)"), (3440, 1440, False, "computador ultra-wide (3440×1440)"),
    (2560, 1080, False, "computador ultra-wide (2560×1080)"),
    (393, 852, False, "computador pequeno (< 1400 px)"), (852, 393, False, "computador pequeno (< 1400 px)"),   # sem toque e pequeno: uma janela, nao um ultra-wide
])
def test_classe_do_ecra(l, a, toque, esperado):
    assert classe_do_ecra(l, a, toque) == esperado


def test_a_orientacao_do_ecra_nao_muda_a_classe():
    assert classe_do_ecra(852, 393, True) == classe_do_ecra(393, 852, True) == "telemóvel"


@pytest.mark.parametrize("bruto,esperado", [("Pixel 9", "Pixel 9"), ("K", ""), ("", ""), ("  SM-S928B  ", "SM-S928B"), ("a\x00b\nc", "abc"),
                                            ("x" * 100, "x" * 40), ("Android", ""), ("unknown", "")])
def test_modelo_limpo(bruto, esperado):
    assert modelo_limpo(bruto) == esperado


@pytest.fixture
def cliente(tmp_path):
    m = Metricas(None)
    return TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "dados", metricas=m)), m


def _ecra(**kw):
    base = dict(ecra_l=393, ecra_a=852, janela_l=393, janela_a=700, dpr=3, toque=True, modelo="")
    base.update(kw)
    return base


def test_o_ecra_fica_nas_metricas_sem_ip_nem_user_agent(cliente):
    c, m = cliente
    r = c.post("/api/ecra", json=_ecra(), headers={"User-Agent": UA_IPHONE})
    assert r.status_code == 204 and not r.content
    c.post("/api/ecra", json=_ecra(ecra_l=412, ecra_a=915, janela_l=412, dpr=2.625, modelo="Pixel 9"), headers={"User-Agent": UA_ANDROID})
    c.post("/api/ecra", json=_ecra(ecra_l=2560, ecra_a=1440, janela_l=1500, janela_a=1300, dpr=1, toque=False), headers={"User-Agent": UA_WIN})
    r = m.resumo(0)
    assert {d["chave"]: d["n"] for d in r["classes_de_ecra"]} == {"telemóvel": 2, "computador QHD/2K (2400–3199 px)": 1}
    assert {d["chave"] for d in r["ecras"]} == {"393×852 @3x", "412×915 @2.5x", "2560×1440 @1x"}
    assert {d["chave"]: d["n"] for d in r["dispositivos_detalhe"]} == {"iPhone": 1, "Pixel 9": 1, "Windows": 1}
    assert {d["chave"]: d["n"] for d in r["toque"]} == {"com toque": 2, "sem toque": 1}
    assert {d["chave"] for d in r["janelas"]} == {"360–413 px (telemóvel)", "1440–1919 px"}


def test_robos_nao_contam(cliente):
    c, m = cliente
    for ua in ("Googlebot/2.1", "facebookexternalhit/1.1", "curl/9"):
        assert c.post("/api/ecra", json=_ecra(), headers={"User-Agent": ua}).status_code == 204
    assert m.resumo(0)["ecras"] == []


@pytest.mark.parametrize("campo,valor", [("ecra_l", 5), ("ecra_a", 99999), ("janela_l", 0), ("dpr", 0), ("dpr", 99), ("dpr", "x"), ("modelo", "m" * 200)])
def test_valores_absurdos_sao_recusados(cliente, campo, valor):
    c, m = cliente
    assert c.post("/api/ecra", json=_ecra(**{campo: valor}), headers={"User-Agent": UA_WIN}).status_code == 422
    assert m.resumo(0)["ecras"] == []


def test_o_ecra_nao_guarda_o_user_agent_nem_o_ip(tmp_path):
    m = Metricas(tmp_path / "m.sqlite3")
    c = TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "dados", metricas=m))
    ua = UA_ANDROID.replace("Chrome/150", "Chrome/150 SegredoNoUA123")
    c.post("/api/ecra", json=_ecra(modelo="Pixel 9"), headers={"User-Agent": ua, "X-Forwarded-For": "203.0.113.9"})
    m.fechar()
    bruto = (tmp_path / "m.sqlite3").read_bytes()
    assert b"SegredoNoUA123" not in bruto and b"203.0.113.9" not in bruto and b"testclient" not in bruto
    assert "Pixel 9".encode() in bruto                                                  # o modelo (agregado) e o unico dado do aparelho


def test_o_ecra_respeita_o_limite_de_pedidos(cliente):
    c, _ = cliente
    codigos = [c.post("/api/ecra", json=_ecra(), headers={"User-Agent": UA_WIN}).status_code for _ in range(310)]
    assert codigos.count(204) == 300 and codigos[-1] == 429
