"""Cabeçalhos de segurança em toda a resposta, o `nosniff` sem quebrar nenhum ficheiro (cada um com o seu tipo) e HEAD nas páginas, no sitemap e nos ficheiros."""
import gzip
import mimetypes
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import app as modulo_app
from web.app import CABECALHOS_SEGURANCA, HSTS, criar_app

INDEX = '<!doctype html><html lang="pt"><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>'
FICHEIROS = {                                    # nome -> tipo esperado (o que o browser tem de ver para executar/mostrar o ficheiro)
    "assets/index-abc123.js": "text/javascript", "assets/index-abc123.css": "text/css", "assets/pdf.worker.min-xyz.mjs": "text/javascript",
    "assets/fonte-latin-400.woff2": "font/woff2", "assets/fonte-latin-400.woff": "font/woff", "galeria/bosque.webp": "image/webp",
    "icone.svg": "image/svg+xml", "icone-192.png": "image/png", "manifest.webmanifest": "application/manifest+json", "sw.js": "text/javascript",
    "fontes/Vera.ttf": "font/ttf",
}


@pytest.fixture
def c(tmp_path, monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    for nome in FICHEIROS:
        f = dist / nome
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"x" * 600)
        if nome.endswith((".js", ".css", ".mjs", ".svg")):
            Path(str(f) + ".gz").write_bytes(gzip.compress(f.read_bytes()))          # a versão pré-comprimida tem de levar o tipo do original
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def test_toda_a_resposta_leva_os_cabecalhos_de_seguranca(c):
    for caminho in ("/", "/tutorial", "/en/tutorial", "/api/publico", "/health", "/sitemap.xml", "/robots.txt", "/nao-existe", "/assets/index-abc123.js", "/icone.svg", "/api/inexistente"):
        r = c.get(caminho)
        for nome, valor in CABECALHOS_SEGURANCA.items():
            assert r.headers.get(nome) == valor, (caminho, nome)
    assert CABECALHOS_SEGURANCA["X-Frame-Options"] == "SAMEORIGIN" and "geolocation=()" in CABECALHOS_SEGURANCA["Permissions-Policy"]
    assert "autoplay" not in CABECALHOS_SEGURANCA["Permissions-Policy"] and "ads" not in CABECALHOS_SEGURANCA["Permissions-Policy"]          # não se fecha nada que os anúncios usem


def test_o_hsts_so_vai_com_https_e_sem_subdominios_nem_preload(c):
    assert "strict-transport-security" not in c.get("/").headers                            # http (desenvolvimento): nada
    r = c.get("/", headers={"X-Forwarded-Proto": "https"})                                  # atrás do proxy do Render
    assert r.headers["strict-transport-security"] == HSTS == "max-age=31536000"
    assert "includeSubDomains" not in HSTS and "preload" not in HSTS                        # o domínio onrender.com não é nosso
    assert c.get("/api/publico", headers={"X-Forwarded-Proto": "https"}).headers["strict-transport-security"] == HSTS


@pytest.mark.parametrize("nome", sorted(FICHEIROS))
def test_cada_ficheiro_sai_com_o_tipo_certo_com_e_sem_compressao(c, nome):
    esperado = FICHEIROS[nome]
    for ae in ("identity", "gzip"):
        r = c.get("/" + nome, headers={"Accept-Encoding": ae})
        tipo = r.headers["content-type"].split(";")[0]
        assert r.status_code == 200 and tipo == esperado, (nome, ae, tipo)                  # com `nosniff` um tipo errado impede o browser de usar o ficheiro
        assert r.headers["x-content-type-options"] == "nosniff"


def test_o_python_conhece_os_tipos_que_o_site_serve():
    assert mimetypes.guess_type("pdf.worker.min.mjs")[0] == "text/javascript" and mimetypes.guess_type("a.webmanifest")[0] in ("application/manifest+json", "application/x-web-app-manifest+json")


# ------------------------------------------------------------------ HEAD
@pytest.mark.parametrize("caminho", ["/", "/tutorial", "/en/tutorial", "/rifas-para-escolas", "/sitemap.xml", "/robots.txt", "/assets/index-abc123.js", "/icone.svg", "/health"])
def test_head_responde_como_get_sem_corpo(c, caminho):
    g, h = c.get(caminho, headers={"Accept-Encoding": "identity"}), c.head(caminho, headers={"Accept-Encoding": "identity"})
    assert h.status_code == g.status_code == 200 and h.content == b""
    assert h.headers["content-type"] == g.headers["content-type"] and h.headers.get("content-length") == g.headers.get("content-length")
    assert h.headers["x-content-type-options"] == "nosniff"


def test_head_de_um_caminho_que_nao_existe_e_um_404_a_serio(c):
    assert c.head("/nao-existe").status_code == 404 and c.head("/en/nao-existe").status_code == 404 and c.head("/assets/nao-existe.js").status_code == 404


def test_head_nao_conta_como_pagina_vista_e_get_sim(c):
    m = c.app.state.servico.metricas

    def paginas():
        m.descarregar(tudo=True)
        return m._consultar("SELECT COUNT(*) FROM eventos WHERE tipo = 'pagina'", atualizar=False)[0][0]
    antes = paginas()
    c.head("/tutorial")
    c.head("/")
    assert paginas() == antes
    c.get("/tutorial")
    assert paginas() == antes + 1


def test_a_api_continua_a_recusar_head_menos_o_health(c):
    assert c.head("/api/publico").status_code == 405 and c.head("/health").status_code == 200


def test_os_cabecalhos_nao_estragam_a_pagina_de_administracao(c, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "palavra-passe-muito-longa-123")
    r = c.get("/admin")
    assert r.headers["cache-control"] == "no-store" and r.headers["x-robots-tag"] == "noindex, nofollow" and r.headers["x-frame-options"] == "SAMEORIGIN"
    assert modulo_app.CABECALHOS_SEGURANCA                                                      # (a política de frames não impede o próprio site de se enquadrar)
