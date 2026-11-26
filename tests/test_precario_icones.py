"""As imagens dos artigos do preçário (`core/icones_precario/`, `public/precario/`): existem para todos os emojis do catálogo, com o tamanho certo, e a licença vai ao lado.

O Noto Emoji curado (`core/icones_precario/<código>.png`, sempre presente) e, para quem tiver, mais bibliotecas (`core.precario_catalogo.FONTES_EXTRA`, cada uma numa
subpasta própria), acrescentadas sozinhas pelo catálogo como alternativa extra (`core.precario_catalogo._alternativas_extra`). Nenhuma delas troca o Noto nem as outras;
os testes por biblioteca extra (imagens, licença) correm uma vez por cada entrada de FONTES_EXTRA, para que uma biblioteca nova não precise de testes novos.
"""
import re
from pathlib import Path

import pytest
from core import precario_catalogo as cat
from core import precario_icones_linha as linha
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "src" / "core" / "icones_precario"
WEB = RAIZ / "src" / "web" / "frontend" / "public" / "precario"
ICONES_ARTIGO_TSX = RAIZ / "src" / "web" / "frontend" / "src" / "IconesArtigo.tsx"
NOTO = sorted({e for a in cat.ARTIGOS.values() for e in a.icones if ":" not in e})            # a de omissão e as alternativas de cada artigo


def _codigos(fonte: str) -> list:
    return sorted({e.split(":", 1)[1] for a in cat.ARTIGOS.values() for e in a.icones if e.startswith(f"{fonte}:")})


def test_cada_emoji_do_catalogo_tem_a_imagem_do_pdf_e_a_miniatura_da_pagina():
    assert not [c for c in NOTO if not (PDF / f"{c}.png").is_file()], "corre scripts/gerar_icones_precario.py"
    assert not [c for c in NOTO if not (WEB / f"{c}.webp").is_file()]
    assert not [f.name for f in PDF.glob("*.png") if f.stem not in NOTO], "imagem a mais (artigo apagado?)"


def test_tamanho_e_peso_das_imagens():
    for c in NOTO:
        with Image.open(PDF / f"{c}.png") as im:
            assert im.size == (256, 256) and "A" in im.convert("RGBA").getbands(), c          # 256 px: 25 mm a 260 dpi
        assert 1_500 < (PDF / f"{c}.png").stat().st_size < 30_000, c
        with Image.open(WEB / f"{c}.webp") as im:
            assert im.size == (96, 96), c
    assert sum(f.stat().st_size for f in PDF.glob("*.png")) < 2_500_000                         # a imagem Docker e o .exe não engordam


def test_a_licenca_das_imagens_vai_com_elas():
    texto = (PDF / "LICENSE.txt").read_text(encoding="utf-8")
    assert "Noto Emoji" in texto and "Google" in texto and "Open Font License" in texto


def test_nenhuma_biblioteca_extra_troca_a_de_omissao():
    """As alternativas extra juntam-se às do Noto, nunca as tiram: o primeiro ícone (a de omissão) continua sempre Noto."""
    for a in cat.ARTIGOS.values():
        assert ":" not in a.icones[0]
        assert a.emoji == a.icones[0]


# ------------------------------------------------------------------ bibliotecas extra (cada uma numa subpasta; ver FONTES_EXTRA)
@pytest.mark.parametrize("fonte", list(cat.FONTES_EXTRA))
def test_cada_codigo_da_biblioteca_tem_imagem_e_nenhuma_a_mais(fonte):
    codigos = _codigos(fonte)
    assert codigos, f"nenhum artigo ganhou uma alternativa {fonte}: corre scripts/gerar_icones_precario.py"
    assert not [c for c in codigos if not (PDF / fonte / f"{c}.png").is_file()]
    assert not [c for c in codigos if not (WEB / fonte / f"{c}.webp").is_file()]
    # nas de contorno, um código mapeado pode não ser oferecido por nenhum artigo sozinho (dois códigos do mesmo
    # artigo com o mesmo ícone: _alternativas_extra só oferece o 1.º, para não repetir a mesma miniatura — ver
    # test_nenhum_artigo_oferece_duas_imagens_iguais); o que não pode haver é um ficheiro fora do mapa escolhido à mão.
    esperados = set(linha.MAPAS[fonte]) if cat.FONTES_EXTRA[fonte].monocromatica else set(codigos)
    assert not [f.name for f in (PDF / fonte).glob("*.png") if f.stem not in esperados]


@pytest.mark.parametrize("fonte", list(cat.FONTES_EXTRA))
def test_tamanho_e_peso_das_imagens_da_biblioteca(fonte):
    codigos = _codigos(fonte)
    for c in codigos:
        with Image.open(PDF / fonte / f"{c}.png") as im:
            assert im.size == (256, 256) and "A" in im.convert("RGBA").getbands(), c
        with Image.open(WEB / fonte / f"{c}.webp") as im:
            assert im.size == (96, 96), c
    assert sum(f.stat().st_size for f in (PDF / fonte).glob("*.png")) < 2_500_000


@pytest.mark.parametrize("fonte", list(cat.FONTES_EXTRA))
def test_a_licenca_da_biblioteca_vai_com_ela(fonte):
    texto = (PDF / fonte / "LICENSE.txt").read_text(encoding="utf-8")
    assert cat.FONTES_EXTRA[fonte].nome in texto and cat.FONTES_EXTRA[fonte].licenca.split()[0] in texto


def test_o_nome_das_fontes_no_frontend_bate_certo_com_o_catalogo():
    """IconesArtigo.tsx mantém um espelho (NOME_FONTE) dos nomes das bibliotecas, como o Galeria.tsx mantém o dos desenhos."""
    texto = ICONES_ARTIGO_TSX.read_text(encoding="utf-8")
    bloco = texto[texto.index("export const NOME_FONTE"):texto.index("};", texto.index("export const NOME_FONTE"))]
    chaves = {k[0] or k[1]: k[2] for k in re.findall(r'^\s*(?:"([a-z]*)"|([a-z]+)):\s*"([^"]+)",?$', bloco, re.MULTILINE)}
    assert chaves[""] == "Noto Emoji"
    for fonte, info in cat.FONTES_EXTRA.items():
        assert chaves.get(fonte) == info.nome, fonte


def test_as_fontes_monocromaticas_no_frontend_batem_certo_com_o_catalogo():
    """IconesArtigo.tsx mantém um espelho (MONOCROMATICAS) de quais são de contorno, para as pintar com `mask-image`."""
    texto = ICONES_ARTIGO_TSX.read_text(encoding="utf-8")
    bloco = texto[texto.index("MONOCROMATICAS = new Set(["):texto.index("])", texto.index("MONOCROMATICAS = new Set(["))]
    chaves = set(re.findall(r'"([a-z]+)"', bloco))
    assert chaves == {f for f, info in cat.FONTES_EXTRA.items() if info.monocromatica}


@pytest.mark.parametrize("fonte", [f for f, info in cat.FONTES_EXTRA.items() if info.monocromatica])
def test_o_mapeamento_dos_icones_de_linha_bate_certo_com_os_ficheiros(fonte):
    """core/precario_icones_linha.py (a escolha manual) e as imagens geradas (scripts/gerar_icones_precario.py) têm
    de ter exatamente os mesmos códigos: um sem o outro é sinal de o gerador não ter corrido depois de mudar o mapa."""
    mapeados = set(linha.MAPAS[fonte])
    gerados = {f.stem for f in (PDF / fonte).glob("*.png")}
    assert mapeados == gerados


def test_nenhum_artigo_oferece_duas_imagens_iguais():
    """Vários códigos podem resolver para o mesmo ícone de contorno (ex.: os 4 livros de cores diferentes usam o
    mesmo ícone genérico de livro): `_alternativas_extra` tem de filtrar as repetidas, para o mesmo artigo nunca
    mostrar duas miniaturas byte a byte iguais no seletor."""
    for a in cat.ARTIGOS.values():
        vistos = set()
        for codigo in a.icones:
            caminho = (PDF / codigo.replace(":", "/")) if ":" in codigo else (PDF / codigo)
            dados = (caminho.with_suffix(".png")).read_bytes()
            assert dados not in vistos, (a.id, codigo)
            vistos.add(dados)
