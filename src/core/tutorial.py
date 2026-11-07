"""Conteudo do tutorial (topicos, textos e imagens a mostrar), sem interface.

Extraido de ajuda.py (lista_de_topicos e _caixas). A janela do tutorial (CustomTkinter) fica em ajuda.py; a webapp usa
esta mesma lista. As imagens estao em assets/ajuda/: `modelo.jpg`, `modelo1.jpg`, `digitos.png`, `folha.png` (iguais em todas
as linguas) e, por lingua, `<lingua>_a.png` / `_b.png` / `_c.png` (capturas da janela) + `ajuda.json` com as zonas a recortar.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .i18n import t

TOPICO_ALGARISMOS = 3          # posicao do topico «2 Algarismos» na lista
IMAGENS_FIXAS = ("modelo.jpg", "modelo1.jpg", "digitos.png", "folha.png")
LINGUAS_COM_VIDEO = ("pt", "en")
VIDEO_MIN_BYTES = 100_000
ESTADOS_DE_CAPTURA = ("a", "b", "c")


def caixas(pasta_ajuda: Path) -> dict:
    """Zonas a recortar das capturas (ajuda.json); {} se o ficheiro nao existe ou esta estragado."""
    try:
        return json.loads((Path(pasta_ajuda) / "ajuda.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def lista_de_topicos() -> list:
    """[(titulo no menu, titulo da pagina, texto, [imagens])]; imagem = ('fixa', ficheiro) | ('rec', estado, zona)."""
    ps = dict(previa=t("previa"), gerar=t("gerar"), ajustar=t("zoom_ajustar"), pasta=t("abrir_pasta"),
              de=t("de"), ate=t("ate"), algarismos=t("algarismos"), varios=t("modo_varios"), unico=t("modo_unico"),
              papel=t("lay_papel"), margem=t("lay_margem"), porfolha=t("lay_por_folha"),
              ajuda=t("m_ajuda"), video=t("mi_video"), limpar=t("limpar"), ficheiro=t("m_ficheiro"))

    def curto(s: str) -> str:               # "Algarismos 0-9 (obrigatorio)" -> "Algarismos 0-9"
        return re.sub(r"\s*[（(][^)）]*[)）]\s*$", "", s)
    return [
        (t("tut_t0"), t("tut_t0"), t("tut_b0", **ps) + "\n\n" + t("tut_video", **ps), [("rec", "a", "janela")]),
        ("1   " + curto(t("c1_titulo")), t("c1_titulo"), t("tut_b1"), [("fixa", "modelo.jpg"), ("rec", "a", "c1")]),
        ("      " + t("tut_t_uma"), t("tut_t_uma"), t("tut_b_uma", **ps),
         [("fixa", "modelo1.jpg"), ("rec", "c", "c1"), ("fixa", "folha.png")]),
        ("2   " + curto(t("c2_titulo")), t("ajuda_titulo"), t("ajuda_texto"), [("fixa", "digitos.png"), ("rec", "a", "c2")]),
        ("3   " + curto(t("c3_titulo")), t("c3_titulo"), t("tut_b3", **ps), [("rec", "a", "c3")]),
        ("4   " + curto(t("c4_titulo")), t("c4_titulo"), t("tut_b4"), [("rec", "a", "c4")]),
        ("5   " + t("tut_t5"), t("tut_t5"), t("tut_b5", **ps) + "\n\n" + t("tut_limpar", **ps),
         [("rec", "a", "barra"), ("rec", "b", "acoes")]),
        (t("tut_t6"), t("tut_t6"), t("tut_b6"), []),
    ]


def verificar_ajuda(pasta_ajuda: Path, pasta_video: Path, linguas) -> list:
    """As imagens e os videos do tutorial existem (para todas as `linguas`). Devolve os problemas (lista vazia = tudo ok)."""
    pasta_ajuda, pasta_video = Path(pasta_ajuda), Path(pasta_video)
    problemas = []
    for nome in IMAGENS_FIXAS:
        if not (pasta_ajuda / nome).exists():
            problemas.append(f"falta {nome}")
    for lg in LINGUAS_COM_VIDEO:
        f = pasta_video / f"tutorial_{lg}.mp4"
        if not f.exists() or f.stat().st_size < VIDEO_MIN_BYTES:
            problemas.append(f"falta o video {f.name}")
    zonas = caixas(pasta_ajuda)
    for lg in linguas:
        for estado in ESTADOS_DE_CAPTURA:
            if not (pasta_ajuda / f"{lg}_{estado}.png").exists() or estado not in zonas.get(lg, {}):
                problemas.append(f"falta a captura {lg}_{estado}")
    return problemas


def ficheiro_video(pasta_video: Path, lingua: str) -> Path | None:
    """O video tutorial na `lingua` (ou em ingles / portugues, se nao houver nessa lingua); None se nao ha nenhum.
    Na webapp serve-se como ficheiro estatico (<video>) em vez de abrir o leitor do sistema."""
    for lg in (lingua, "en", "pt"):
        f = Path(pasta_video) / f"tutorial_{lg}.mp4"
        if f.exists():
            return f
    return None
