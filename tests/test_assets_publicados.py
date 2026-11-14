"""Os vídeos e as capturas do site vão num .zip no armazenamento de objetos (docs/ASSETS.md). Se alguém regravar um vídeo ou mudar uma captura sem
voltar a publicar o .zip, o site em produção ficava com os ficheiros velhos: este teste falha enquanto o SHA-256 do Dockerfile não for o dos ficheiros do repositório."""
import hashlib
import importlib.util
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DOCKERFILE = RAIZ / "Dockerfile"
SCRIPT = RAIZ / "scripts" / "publicar_assets.py"

pytestmark = pytest.mark.skipif(not (DOCKERFILE.exists() and SCRIPT.exists()), reason="a imagem de testes não leva o Dockerfile nem os scripts")


def _script():
    spec = importlib.util.spec_from_file_location("publicar_assets", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _arg(nome: str) -> str:
    m = re.search(rf"^ARG {nome}=(\S+)$", DOCKERFILE.read_text(encoding="utf-8"), re.M)
    assert m, f"falta `ARG {nome}=` no Dockerfile (estágio web)"
    return m.group(1)


def test_o_zip_publicado_e_o_dos_ficheiros_do_repositorio():
    sha = hashlib.sha256(_script().zip_bytes()).hexdigest()
    assert _arg("ASSETS_SHA256") == sha, (
        "os vídeos/capturas do site mudaram: `uv run python scripts/publicar_assets.py`, enviar o .zip para o bucket site-assets e pôr "
        f"o URL e o SHA-256 novos nos ARG do Dockerfile (docs/ASSETS.md). SHA-256 atual: {sha}")


def test_o_url_do_dockerfile_aponta_para_esse_zip():
    url, sha = _arg("ASSETS_URL"), _arg("ASSETS_SHA256")
    assert url.startswith("https://") and url.endswith(f"/assets-web-{sha[:12]}.zip") and "/site-assets/" in url


def test_o_zip_so_leva_o_que_o_site_usa():
    nomes = [n for n, _ in _script().do_site()]
    assert all(re.fullmatch(r"(ajuda|video)/[A-Za-z0-9._-]+", n) for n in nomes)
    assert not any(n.startswith("video/windows_") or re.fullmatch(r"ajuda/[a-z]{2}_[abc]\.png", n) for n in nomes)      # o que é só da app Windows
    assert "video/tutorial_pt.mp4" in nomes and "ajuda/ajuda.json" in nomes and "ajuda/pt_wa.png" in nomes


def test_o_zip_e_o_mesmo_em_duas_construcoes():
    s = _script()
    assert s.zip_bytes() == s.zip_bytes()
