"""A API FastAPI (src/web): /health, textos, ficheiros do frontend, entrada `python -m src.web` e a regra de so chamar o `core`."""
import ast
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient

from core import i18n
from web import VERSAO, config
from web.app import criar_app

RAIZ = Path(__file__).resolve().parents[1]
FRONTEND_SRC = RAIZ / "src" / "web" / "frontend" / "src"


@pytest.fixture
def dist(tmp_path):
    """Um frontend «compilado» minimo."""
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><title>Rifas</title><div id=raiz></div>", encoding="utf-8")
    (tmp_path / "assets" / "app-123.js").write_text("console.log(1)", encoding="utf-8")
    (tmp_path / "favicon.svg").write_text("<svg/>", encoding="utf-8")
    return tmp_path


@pytest.fixture
def cliente(dist):
    return TestClient(criar_app(dist))


# ------------------------------------------------------------------ /health
def test_health_devolve_200(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200 and r.json() == {"estado": "ok", "versao": VERSAO}


def test_health_aceita_head_para_os_monitores_externos(cliente):
    r = cliente.head("/health")
    assert r.status_code == 200 and r.content == b""


def test_health_funciona_sem_frontend_compilado(tmp_path):
    assert TestClient(criar_app(tmp_path / "nao_existe")).get("/health").status_code == 200


# ------------------------------------------------------------------ linguas e textos
def test_linguas_sao_as_18_e_por_defeito_vem_do_browser(cliente):
    r = cliente.get("/api/linguas", headers={"Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8"})
    d = r.json()
    assert [x["codigo"] for x in d["linguas"]] == list(i18n.LINGUAS) and len(d["linguas"]) == 22
    assert d["linguas"][0] == {"codigo": "pt", "nome": "Português"}
    assert d["por_defeito"] == "ja"


@pytest.mark.parametrize("cabecalho, esperado", [("pt-PT,pt;q=0.9", "pt"), ("zh-CN", "zh"), ("xx-YY", "en"), (None, "en")])
def test_lingua_por_defeito(cliente, cabecalho, esperado):
    r = cliente.get("/api/linguas", headers={"Accept-Language": cabecalho} if cabecalho else {})
    assert r.json()["por_defeito"] == esperado


def test_textos_de_cada_lingua_tem_as_mesmas_chaves_que_o_portugues(cliente):
    pt = cliente.get("/api/textos/pt").json()
    assert pt["lingua"] == "pt" and len(pt["textos"]) == 348 and pt["textos"]["app_nome"] == "Gerador de Rifas"
    for lg in i18n.LINGUAS:
        d = cliente.get(f"/api/textos/{lg}").json()
        assert d["lingua"] == lg and d["textos"].keys() == pt["textos"].keys(), lg


def test_textos_vem_na_lingua_pedida_e_com_os_parametros_por_substituir(cliente):
    en = cliente.get("/api/textos/en").json()["textos"]
    assert en["err_digitos"] == i18n.TEXTOS["en"]["err_digitos"]
    assert "{max}" in en["err_digitos"]                                # a substituicao e feita no browser
    assert en["app_nome"] == i18n.TEXTOS["en"]["app_nome"]


def test_textos_em_falta_numa_lingua_caem_no_portugues(dist, monkeypatch):
    monkeypatch.delitem(i18n.TEXTOS["en"], "nenhum")
    d = TestClient(criar_app(dist)).get("/api/textos/en").json()["textos"]
    assert d["nenhum"] == i18n.TEXTOS["pt"]["nenhum"]


@pytest.mark.parametrize("lg", ["xx", "PT", "pt-PT", "%2e%2e", "pt%00"])
def test_textos_de_lingua_desconhecida_dao_404(cliente, lg):
    assert cliente.get(f"/api/textos/{lg}").status_code == 404


def test_o_frontend_so_usa_chaves_que_existem_em_todas_as_linguas():
    """Cada t("chave") e cada chave de PASSOS no React tem de existir nas 18 linguas (senao o utilizador ve o nome da chave)."""
    usadas = set()
    for f in FRONTEND_SRC.glob("*.tsx"):
        if f.name.endswith(".test.tsx"):
            continue
        txt = f.read_text(encoding="utf-8")
        usadas |= set(re.findall(r'\bt\("([a-z0-9_]+)"', txt))
        usadas |= set(re.findall(r'"([a-z0-9]+_[a-z0-9_]+)"', re.search(r"PASSOS = \[(.*?)\]", txt, re.S).group(1))) if "PASSOS" in txt else set()
    assert {"app_nome", "m_idioma", "c1_titulo", "c4_titulo", "previa", "gerar"} <= usadas
    for lg, textos in i18n.TEXTOS.items():
        assert not usadas - textos.keys(), (lg, usadas - textos.keys())


# ------------------------------------------------------------------ API desconhecida
@pytest.mark.parametrize("caminho", ["/api", "/api/", "/api/nao_existe", "/api/textos/pt/extra", "/api/textos/.."])
def test_api_desconhecida_da_404_em_json_e_nao_o_index(cliente, caminho):
    r = cliente.get(caminho)
    assert r.status_code == 404 and r.json() == {"detail": "Rota inexistente"}


def test_um_caminho_que_so_comeca_por_api_continua_a_ser_do_frontend(cliente):
    assert "<div id=raiz>" in cliente.get("/apice").text


def test_a_documentacao_openapi_existe_em_api(cliente):
    assert cliente.get("/api/openapi.json").json()["info"]["version"] == VERSAO
    assert cliente.get("/api/docs").status_code == 200


# ------------------------------------------------------------------ ficheiros do frontend
def test_raiz_e_rotas_do_react_devolvem_o_index(cliente):
    for caminho in ("/", "/tutorial", "/video", "/sobre"):
        r = cliente.get(caminho)
        assert r.status_code == 200 and "<div id=raiz>" in r.text and r.headers["cache-control"] == "no-cache", caminho
    r = cliente.get("/sobre/qualquer/coisa")            # rota que nao existe: 404 a serio (sem «soft 404»), mas a SPA arranca na mesma
    assert r.status_code == 404 and "<div id=raiz>" in r.text and r.headers["cache-control"] == "no-cache"


def test_ficheiros_com_hash_sao_cacheados_para_sempre(cliente):
    r = cliente.get("/assets/app-123.js")
    assert r.status_code == 200 and "console.log" in r.text
    assert "immutable" in r.headers["cache-control"]
    assert "immutable" not in cliente.get("/favicon.svg").headers.get("cache-control", "")


def test_ficheiro_inexistente_dentro_de_assets_cai_no_index(cliente):
    assert "<div id=raiz>" in cliente.get("/assets/nao_existe.js").text


@pytest.mark.parametrize("caminho", ["/../segredo.txt", "/%2e%2e/segredo.txt", "/..%2fsegredo.txt", "/assets/../../segredo.txt",
                                     "/%2e%2e%2f%2e%2e%2fsegredo.txt"])
def test_nao_sai_da_pasta_do_frontend(dist, caminho):
    (dist.parent / "segredo.txt").write_text("SEGREDO", encoding="utf-8")
    r = TestClient(criar_app(dist)).get(caminho)
    assert "SEGREDO" not in r.text


def test_sem_frontend_compilado_diz_como_o_compilar(tmp_path):
    r = TestClient(criar_app(tmp_path)).get("/")
    assert r.status_code == 503 and "pnpm build" in r.json()["detail"]


def test_frontend_por_variavel_de_ambiente(monkeypatch, dist):
    monkeypatch.setenv("RIFAS_FRONTEND", str(dist))
    assert config.pasta_frontend() == dist
    assert "<div id=raiz>" in TestClient(criar_app()).get("/").text
    monkeypatch.delenv("RIFAS_FRONTEND")
    assert config.pasta_frontend() == RAIZ / "src" / "web" / "frontend" / "dist"


# ------------------------------------------------------------------ configuracao
def test_config_por_defeito(monkeypatch):
    for v in ("PORT", "HOST"):
        monkeypatch.delenv(v, raising=False)
    assert (config.porta(), config.host()) == (8080, "127.0.0.1")


def test_config_le_o_ambiente(monkeypatch):
    monkeypatch.setenv("PORT", "9123")
    monkeypatch.setenv("HOST", "0.0.0.0")
    assert (config.porta(), config.host()) == (9123, "0.0.0.0")


@pytest.mark.parametrize("valor", ["", "abc", "0", "-5", "80.5"])
def test_porta_invalida_volta_ao_defeito(monkeypatch, valor):
    monkeypatch.setenv("PORT", valor)
    assert config.porta() == 8080


# ------------------------------------------------------------------ `python -m src.web` (ponto de entrada real)
def _porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_python_m_src_web_ouve_na_porta_PORT_e_responde_a_health(dist):
    porta = _porta_livre()
    ambiente = {k: v for k, v in __import__("os").environ.items() if not k.startswith(("PYTEST", "PORT", "HOST", "RIFAS_"))}
    ambiente.update(PORT=str(porta), RIFAS_FRONTEND=str(dist), PYTHONIOENCODING="utf-8")
    proc = subprocess.Popen([sys.executable, "-m", "src.web"], cwd=RAIZ, env=ambiente, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        fim = time.time() + 30
        while True:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{porta}/health", timeout=2) as r:
                    assert r.status == 200 and b'"ok"' in r.read()
                with urllib.request.urlopen(f"http://127.0.0.1:{porta}/", timeout=2) as r:
                    assert b"<div id=raiz>" in r.read()
                break
            except OSError:
                assert proc.poll() is None, proc.stdout.read()
                assert time.time() < fim, "o servidor nao arrancou em 30 s"
                time.sleep(0.2)
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()


# ------------------------------------------------------------------ arquitetura
def test_a_api_so_chama_o_core():
    """Nenhum ficheiro de src/web importa as bibliotecas de PDF/imagens (isso e do core) nem Tkinter/Windows."""
    proibidos = {"pypdf", "pypdfium2", "PIL", "reportlab", "fitz", "tkinter", "customtkinter", "winreg", "ctypes", "msvcrt"}
    ficheiros = sorted((RAIZ / "src" / "web").glob("*.py"))
    assert len(ficheiros) >= 4
    for f in ficheiros:
        for no in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            nomes = [a.name for a in no.names] if isinstance(no, ast.Import) else ([no.module] if isinstance(no, ast.ImportFrom) and no.level == 0 and no.module else [])
            assert not [n for n in nomes if n.split(".")[0] in proibidos], (f.name, nomes)
