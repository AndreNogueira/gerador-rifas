"""O seletor de desenhos da galeria (web): as 24 miniaturas estáticas e a lista do frontend têm de acompanhar `core/galeria.py`."""
import re
from pathlib import Path

import pytest
from core import galeria

RAIZ = Path(__file__).resolve().parent.parent
MINIATURAS = RAIZ / "src" / "web" / "frontend" / "public" / "galeria"
GALERIA_TSX = RAIZ / "src" / "web" / "frontend" / "src" / "Galeria.tsx"


def test_cada_desenho_tem_a_sua_miniatura_e_nao_sobram_ficheiros():
    esperados = {f"{d.id}.webp" for d in galeria.DESENHOS}
    existentes = {p.name for p in MINIATURAS.glob("*")}
    assert existentes == esperados, "voltar a correr `uv run python scripts/gerar_miniaturas_galeria.py`"


@pytest.mark.parametrize("desenho", [d.id for d in galeria.DESENHOS])
def test_a_miniatura_e_uma_imagem_pequena(desenho):
    Image = pytest.importorskip("PIL.Image")
    ficheiro = MINIATURAS / f"{desenho}.webp"
    assert ficheiro.stat().st_size < 12_000                     # 24 de uma vez no seletor: têm de ser leves
    with Image.open(ficheiro) as im:
        assert im.format == "WEBP" and im.width == 288 and 70 <= im.height <= 90


def test_a_lista_do_frontend_e_a_do_core_na_mesma_ordem_e_com_os_mesmos_nomes():
    texto = GALERIA_TSX.read_text(encoding="utf-8")
    bloco = texto[texto.index("export const DESENHOS = ["):texto.index("] as const;")]
    do_frontend = re.findall(r'\{ id: "([a-z]+)", nome: "([^"]+)" \}', bloco)
    assert do_frontend == [(d.id, d.nome) for d in galeria.DESENHOS]
