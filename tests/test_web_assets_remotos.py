"""Os videos e as capturas do site no armazenamento de objetos: o .zip descarrega-se e extrai-se com seguranca, o SHA-256 confere, o site arranca e responde
sem esperar e serve os ficheiros extraidos como se fossem locais; sem ASSETS_URL tudo fica como estava."""
import hashlib
import io
import tempfile
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web import assets_remotos, config
from web.app import criar_app
from web.assets_remotos import AssetsRemotos, extrair
from web.trabalhos import Motor

URL = "https://exemplo.storage.neon.tech/site-assets/assets-web-abc.zip"


def zip_de(ficheiros: dict) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for nome, dados in ficheiros.items():
            z.writestr(nome, dados)
    return b.getvalue()


BOM = zip_de({"video/web_series_pt.mp4": b"MP4" * 100, "ajuda/modelo.jpg": b"JPG" * 10, "ajuda/pt_wa.png": b"PNG", "ajuda/ajuda.json": b"{}"})


def servidor_falso(dados: bytes):
    def baixar(url, destino, **_):
        assert url == URL
        destino.write_bytes(dados)
        return hashlib.sha256(dados).hexdigest()
    return baixar


# ------------------------------------------------------------------ config
@pytest.mark.parametrize("valor", ["http://x.pt/a.zip", "https://x.pt/a.tar", "https://x.pt/a.zip<script>", "ftp://x/a.zip", "", "https://a.zip"])
def test_urls_invalidos_sao_ignorados(monkeypatch, valor):
    monkeypatch.setenv("ASSETS_URL", valor)
    assert config.assets_zip_url() == ""


def test_url_valido_e_sha(monkeypatch):
    monkeypatch.setenv("ASSETS_URL", URL)
    monkeypatch.setenv("ASSETS_SHA256", "A" * 64)
    assert config.assets_zip_url() == URL and config.assets_sha256() == "a" * 64
    monkeypatch.setenv("ASSETS_SHA256", "curto")
    assert config.assets_sha256() == ""


def test_sem_url_os_assets_sao_os_locais_e_com_url_uma_pasta_temporaria(monkeypatch):
    monkeypatch.delenv("ASSETS_URL", raising=False)
    monkeypatch.delenv("RIFAS_ASSETS", raising=False)
    assert config.pasta_assets() == config.RAIZ / "app" / "assets"
    monkeypatch.setenv("ASSETS_URL", URL)
    assert config.pasta_assets() == Path(tempfile.gettempdir()) / "rifas-assets"
    monkeypatch.setenv("RIFAS_ASSETS", "/outra")
    assert config.pasta_assets() == Path("/outra")


# ------------------------------------------------------------------ extrair
def test_extrai_so_ajuda_e_video(tmp_path):
    z = tmp_path / "a.zip"
    z.write_bytes(BOM)
    assert extrair(z, tmp_path / "p") == 4
    assert (tmp_path / "p" / "video" / "web_series_pt.mp4").read_bytes() == b"MP4" * 100
    assert not list((tmp_path / "p").rglob("*.parcial"))


@pytest.mark.parametrize("nome", ["../fora.txt", "ajuda/../../fora.txt", "/abs.png", "ajuda/sub/x.png", "outra/x.png", "ajuda/.oculto", "ajuda/x y.png"])
def test_nomes_perigosos_recusam_o_zip_inteiro(tmp_path, nome):
    z = tmp_path / "a.zip"
    z.write_bytes(zip_de({"video/ok.mp4": b"x", nome: b"x"}))
    with pytest.raises(ValueError):
        extrair(z, tmp_path / "p")
    assert not (tmp_path / "p" / "video" / "ok.mp4").exists() and not (tmp_path / "fora.txt").exists()      # nao extraiu nada


def test_ficheiros_gigantes_sao_recusados(tmp_path, monkeypatch):
    monkeypatch.setattr(assets_remotos, "MAX_FICHEIRO", 10)
    z = tmp_path / "a.zip"
    z.write_bytes(zip_de({"video/a.mp4": b"x" * 11}))
    with pytest.raises(ValueError):
        extrair(z, tmp_path / "p")


# ------------------------------------------------------------------ AssetsRemotos
def test_descarrega_confere_o_sha_e_nao_repete_quando_ja_esta_pronto(tmp_path):
    chamadas = []
    baixar = servidor_falso(BOM)

    def contado(url, destino):
        chamadas.append(1)
        return baixar(url, destino)
    sha = hashlib.sha256(BOM).hexdigest()
    ar = AssetsRemotos(URL, sha, tmp_path / "p", contado)
    assert not ar.pronto
    assert ar.garantir(esperar=True) and ar.pronto and ar.erro == "" and len(chamadas) == 1
    ar.garantir(esperar=True)
    assert len(chamadas) == 1
    outro = AssetsRemotos(URL, sha, tmp_path / "p", baixar)                       # um arranque seguinte com a mesma pasta e o mesmo .zip
    assert outro.pronto
    novo = AssetsRemotos(URL.replace("abc", "def"), "", tmp_path / "p", baixar)    # outra versao: volta a descarregar
    assert not novo.pronto


def test_sha_errado_nao_extrai_nada_e_fica_com_o_erro(tmp_path):
    ar = AssetsRemotos(URL, "0" * 64, tmp_path / "p", servidor_falso(BOM))
    assert not ar.garantir(esperar=True)
    assert "SHA-256" in ar.erro and not list((tmp_path / "p" / "video").iterdir())


def test_falha_da_rede_nao_derruba_e_so_repete_passado_um_minuto(tmp_path, monkeypatch):
    tentativas = []

    def falha(url, destino):
        tentativas.append(1)
        raise OSError("sem rede")
    ar = AssetsRemotos(URL, "", tmp_path / "p", falha)
    assert not ar.garantir(esperar=True) and "OSError" in ar.erro and len(tentativas) == 1
    ar.garantir(esperar=True)
    assert len(tentativas) == 1                                    # ainda nao passou REPETIR_S
    monkeypatch.setattr(assets_remotos, "REPETIR_S", 0.0)
    ar.garantir(esperar=True)
    assert len(tentativas) == 2


# ------------------------------------------------------------------ a app
@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


def _app(tmp_path, motor):
    dist = tmp_path / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor))


def test_com_assets_remotos_o_site_serve_os_ficheiros_extraidos(tmp_path, motor, monkeypatch):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.delenv("RIFAS_ASSETS", raising=False)
    monkeypatch.setenv("ASSETS_URL", URL)
    monkeypatch.setenv("ASSETS_SHA256", hashlib.sha256(BOM).hexdigest())
    monkeypatch.setattr(assets_remotos, "baixar", servidor_falso(BOM))
    with _app(tmp_path, motor) as c:
        assert c.get("/health").status_code == 200                 # nao espera pelo descarregamento
        assert c.app.state.assets.garantir(esperar=True)
        r = c.get("/videos/web_series_pt.mp4")
        assert r.status_code == 200 and r.content == b"MP4" * 100
        assert c.get("/ajuda/modelo.jpg").content == b"JPG" * 10
        assert c.get("/videos/nao-existe.mp4").status_code == 404
        t = c.get("/api/tutorial").json()
        assert any(x["video"] == "/videos/web_series_pt.mp4" for x in t["topicos"])


def test_sem_assets_remotos_nao_ha_estado_e_usa_os_locais(tmp_path, motor, monkeypatch):
    monkeypatch.delenv("ASSETS_URL", raising=False)
    monkeypatch.delenv("RIFAS_ASSETS", raising=False)
    with _app(tmp_path, motor) as c:
        assert c.app.state.assets is None
        assert c.get("/videos/tutorial_pt.mp4").status_code == 200
