"""O segundo acesso ao painel, só de leitura (`CLAUDE_TOKEN`): vê tudo o que o painel mostra, não muda nada, e nunca pode ser igual ao `ADMIN_TOKEN`."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import admin, config
from web.app import criar_app

ADMIN = "palavra-passe-do-dono-123"
LEITURA = "token-so-de-leitura-do-claude-0123456789"
INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("PUBLIC_URL", "RENDER_EXTERNAL_URL", "ADMIN_TOKEN", "CLAUDE_TOKEN", "RENDER", "RIFAS_METRICAS", "DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)


def _app(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), base_url="http://testserver")


def _entrar(c, token):
    return c.post("/api/admin/entrar", json={"token": token})


@pytest.fixture
def dois(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    return _app(tmp_path)


def test_claude_token_curto_ou_igual_ao_do_dono_fica_desligado(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN)
    monkeypatch.setenv("CLAUDE_TOKEN", "curto-demais-123")
    assert config.claude_token() == ""
    monkeypatch.setenv("CLAUDE_TOKEN", ADMIN * 2)
    assert config.claude_token() == ADMIN * 2
    monkeypatch.setenv("ADMIN_TOKEN", LEITURA)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    assert config.claude_token() == ""                                           # nunca igual ao do dono


def test_o_painel_existe_so_com_o_token_de_leitura(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    c = _app(tmp_path)
    assert admin.ativo() and _entrar(c, LEITURA).json()["papel"] == "leitura"
    assert c.get("/api/admin/estado").json()["papel"] == "leitura"
    assert _entrar(c, "outra-coisa-qualquer-123").status_code == 401


def test_o_dono_continua_a_entrar_como_admin_e_o_estado_diz_o_papel(dois):
    r = _entrar(dois, ADMIN)
    assert r.status_code == 200 and r.json()["papel"] == "admin"
    assert dois.get("/api/admin/estado").json()["papel"] == "admin"


def test_leitura_por_cookie_ve_mas_nao_muda(dois):
    assert _entrar(dois, LEITURA).json()["papel"] == "leitura"
    assert dois.get("/api/admin/estado").status_code == 200 and dois.get("/api/admin/dados?intervalo=6h").status_code == 200
    assert dois.get("/api/admin/chaves").status_code == 200 and dois.get("/api/admin/seo").status_code == 200
    escrita = [dois.post("/api/admin/chaves", json={"nome": "x"}), dois.delete("/api/admin/chaves/abc"),
               dois.put("/api/admin/seo", json={"chave": "t_inicio", "lingua": "pt", "texto": "x"}),
               dois.delete("/api/admin/seo?chave=t_inicio&lingua=pt")]
    assert [r.status_code for r in escrita] == [403, 403, 403, 403]


def test_leitura_por_cabecalho_bearer_so_em_get(dois):
    h = {"Authorization": f"Bearer {LEITURA}"}
    r = dois.get("/api/admin/estado", headers=h)
    assert r.status_code == 200 and r.json()["papel"] == "leitura" and r.headers["cache-control"] == "no-store"
    assert dois.get("/api/admin/estado", headers={"Authorization": f"Bearer {LEITURA}x"}).status_code == 404
    assert dois.get("/api/admin/estado", headers={"Authorization": f"Bearer {ADMIN}"}).status_code == 404       # o token do dono nunca vale como bearer
    assert dois.post("/api/admin/chaves", headers=h, json={"nome": "x"}).status_code == 404                    # só GET
    assert dois.delete("/api/admin/chaves/abc", headers=h).status_code == 404


def test_sem_credencial_tudo_e_404(dois):
    for rota in ("/api/admin/estado", "/api/admin/dados", "/api/admin/chaves", "/api/admin/seo"):
        assert dois.get(rota).status_code == 404


def test_bearer_certo_nao_gasta_tentativas(dois):
    for _ in range(30):
        assert dois.get("/api/admin/estado", headers={"Authorization": f"Bearer {LEITURA}"}).status_code == 200


def test_bearer_errado_trava_depois_de_10_tentativas_mesmo_com_o_certo(dois):
    for _ in range(10):
        assert dois.get("/api/admin/estado", headers={"Authorization": "Bearer errado-errado-errado-1234"}).status_code == 404
    assert dois.get("/api/admin/estado", headers={"Authorization": f"Bearer {LEITURA}"}).status_code == 404     # travado por um minuto


def test_mudar_um_dos_tokens_invalida_os_cookies(dois, monkeypatch):
    _entrar(dois, LEITURA)
    assert dois.get("/api/admin/estado").status_code == 200
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA + "-novo")
    assert dois.get("/api/admin/estado").status_code == 404


def test_cookie_de_leitura_nao_sobrevive_a_remover_o_claude_token(dois, monkeypatch):
    _entrar(dois, LEITURA)
    monkeypatch.delenv("CLAUDE_TOKEN")
    assert dois.get("/api/admin/estado").status_code == 404


def test_cookie_com_o_papel_trocado_a_mao_nao_vale(dois):
    _entrar(dois, LEITURA)
    cookie = dois.cookies.get("rifas_admin", path="/api/admin")
    expira, _, resto = cookie.partition(".")
    adulterado = f"{expira}.admin.{resto.partition('.')[2]}"                      # a assinatura é a do papel «leitura»
    assert admin.cookie_papel(cookie) == "leitura" and admin.cookie_papel(adulterado) is None
