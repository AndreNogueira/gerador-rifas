"""Conteudo do tutorial (topicos, textos e imagens a mostrar), sem interface.

Extraido de ajuda.py (lista_de_topicos e _caixas). A janela do tutorial (CustomTkinter) fica em ajuda.py; a webapp usa
esta mesma lista. As imagens estao em assets/ajuda/: `modelo.jpg`, `modelo1.jpg`, `digitos.png`, `folha.png` (iguais em todas
as linguas) e, por lingua, `<lingua>_a.png` / `_b.png` / `_c.png` (capturas da janela) + `ajuda.json` com as zonas a recortar.
"""
from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .i18n import t

TOPICO_ALGARISMOS = 3          # posicao do topico «2 Algarismos» na lista
IMAGENS_FIXAS = ("modelo.jpg", "modelo1.jpg", "digitos.png", "folha.png")
LINGUAS_COM_VIDEO = ("pt", "en")
SEM_CAPTURAS_PROPRIAS = ("pt-br",)         # o portugues do Brasil usa as capturas e os videos do portugues (os textos da interface sao quase iguais)


def ordem_de_recurso(lingua: str) -> tuple:
    """Onde procurar uma captura ou um video: a propria lingua, depois a lingua de recurso (o portugues para o do Brasil; o ingles para as outras) e a outra."""
    return (lingua, "pt", "en") if lingua in SEM_CAPTURAS_PROPRIAS else (lingua, "en", "pt")
VIDEO_MIN_BYTES = 100_000
ESTADOS_DE_CAPTURA = ("a", "b", "c")          # capturas da app Windows (<lg>_a.png ...)
ESTADOS_WEB = ("wa", "wb", "wc")               # capturas do site (<lg>_wa.png ...; e2e/capturas.spec.ts): os mesmos 3 estados, com o prefixo «w»
PLATAFORMAS = ("web", "windows")
VIDEO_FUNC_MIN_BYTES = 20_000     # os videos das funcionalidades sao curtos (gravados da propria interface)


@dataclass(frozen=True)
class Funcionalidade:
    """Uma funcionalidade de utilizador, com o seu topico no tutorial e o seu video. REGRA (CLAUDE.md): uma funcionalidade de utilizador so esta
    feita quando esta na lista FUNCIONALIDADES, com texto nas 18 linguas (`tut_f_<id>_t` e `_b`, em idiomas/tutoriais.py) e um video por plataforma
    (`<plataforma>_<id>_pt.mp4` e `_en.mp4` em assets/video/). `web`/`windows` dizem onde ela esta (chave do texto «Onde»)."""
    id: str
    plataformas: tuple
    web: str = ""                     # chave do rotulo, na pagina inicial do site
    windows: tuple = ()               # (chave do menu, chave do item) na app Windows
    onde: bool = True                 # False: o texto nao diz «Onde» (nao ha um sitio unico)


FUNCIONALIDADES = (
    Funcionalidade("series", PLATAFORMAS, "web_prefixos", ("win_m_extras", "win_opcoes")),
    Funcionalidade("lista", PLATAFORMAS, "web_exportar_csv", ("win_m_extras", "web_exportar_csv")),
    Funcionalidade("marcas", PLATAFORMAS, "web_marcas", ("win_m_extras", "win_opcoes")),
    Funcionalidade("galeria", PLATAFORMAS, "web_galeria", ("win_m_extras", "win_galeria")),
    Funcionalidade("precario", PLATAFORMAS, "web_precario", ("win_m_extras", "web_precario")),
    Funcionalidade("vales", PLATAFORMAS, "web_precario", ("win_m_extras", "web_precario")),          # o cartão «Vales numerados» do preçário (moeda inventada)
    Funcionalidade("etiquetas", PLATAFORMAS, "web_precario", ("win_m_extras", "web_precario")),      # as etiquetas de levantamento do preçário (paga-se num sítio, levanta-se noutro)
    Funcionalidade("marca", PLATAFORMAS, "web_logotipo", ("win_m_extras", "win_opcoes")),
    Funcionalidade("qr", ("web",), "web_qr"),
    Funcionalidade("editor", PLATAFORMAS, "web_editor", ("win_m_extras", "web_editor")),
    Funcionalidade("sorteio", PLATAFORMAS, "web_sorteio", ("win_m_extras", "web_sorteio")),
    Funcionalidade("guardar", ("web",), onde=False),
    Funcionalidade("instalar", ("web",), onde=False),
    Funcionalidade("visual", PLATAFORMAS, "web_visual", ("m_ver", "web_visual")),
    Funcionalidade("partilhar", ("web",), "web_partilhar"),
    Funcionalidade("comentarios", ("web",), "web_comentarios"),
    Funcionalidade("problema", ("web",), "web_reportar"),
    Funcionalidade("pedido", ("windows",), "", ("win_m_extras", "win_guardar_pedido")),         # o site tem «guardar» (copiar ligação)
)


def caixas(pasta_ajuda: Path) -> dict:
    """Zonas a recortar das capturas (ajuda.json); {} se o ficheiro nao existe ou esta estragado."""
    try:
        return json.loads((Path(pasta_ajuda) / "ajuda.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def funcionalidades(plataforma: str) -> list:
    """As funcionalidades que existem nesta plataforma («web» ou «windows»), pela ordem do tutorial."""
    return [f for f in FUNCIONALIDADES if plataforma in f.plataformas]


def _onde(f: Funcionalidade, plataforma: str) -> str:
    if not f.onde:
        return ""
    if plataforma == "windows":
        menu, item = f.windows
        return t("tut_onde_menu", menu=t(menu).rstrip("…"), item=t(item).rstrip("…"))
    return t("tut_onde_web", item=t(f.web).rstrip("…"))


def topico_da_funcionalidade(f: Funcionalidade, plataforma: str) -> tuple:
    """O topico (menu, titulo, texto, imagens) de uma funcionalidade: sem imagens (o video mostra-a), com o «Onde» desta plataforma."""
    titulo = t(f"tut_f_{f.id}_t")
    return (titulo, titulo, t(f"tut_f_{f.id}_b", onde=_onde(f, plataforma)).strip(), [])


def video_ids(plataforma: str = "windows") -> list:
    """Em paralelo com `lista_de_topicos(plataforma)`: o id da funcionalidade de cada topico (None nos 8 topicos de base, que tem o video geral)."""
    return [None] * N_BASE + [f.id for f in funcionalidades(plataforma)]


def lista_de_topicos(plataforma: str = "windows") -> list:
    """[(titulo no menu, titulo da pagina, texto, [imagens])]; imagem = ('fixa', ficheiro) | ('rec', estado, zona). Os 8 primeiros sao os de
    base (iguais nas duas plataformas, com as capturas da app Windows); seguem-se os das funcionalidades (`FUNCIONALIDADES`) que a `plataforma` tem."""
    return _base(plataforma) + [topico_da_funcionalidade(f, plataforma) for f in funcionalidades(plataforma)]


N_BASE = 8


def _base(plataforma: str = "windows") -> list:
    """Os 8 topicos de base; as imagens `('rec', estado, zona)` sao as capturas da `plataforma` (no site, estado «a» -> «wa»)."""
    ps = dict(previa=t("previa"), gerar=t("gerar"), ajustar=t("zoom_ajustar"), pasta=t("abrir_pasta"),
              de=t("de"), ate=t("ate"), algarismos=t("algarismos"), varios=t("modo_varios"), unico=t("modo_unico"),
              papel=t("lay_papel"), margem=t("lay_margem"), porfolha=t("lay_por_folha"),
              ajuda=t("m_ajuda"), video=t("mi_video"), limpar=t("limpar"), ficheiro=t("m_ficheiro"))

    def curto(s: str) -> str:               # "Algarismos 0-9 (obrigatorio)" -> "Algarismos 0-9"
        return re.sub(r"\s*[（(][^)）]*[)）]\s*$", "", s)
    topicos = [
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
    if plataforma == "web":
        topicos = [(m, ti, tx, [("rec", "w" + im[1], im[2]) if im[0] == "rec" else im for im in imgs]) for m, ti, tx, imgs in topicos]
    return topicos


def verificar_ajuda(pasta_ajuda: Path, pasta_video: Path, linguas, plataformas=PLATAFORMAS) -> list:
    """As imagens e os videos do tutorial existem (para todas as `linguas`; os das funcionalidades, para as `plataformas` dadas: a app Windows so leva os seus).
    Devolve os problemas (lista vazia = tudo ok)."""
    pasta_ajuda, pasta_video = Path(pasta_ajuda), Path(pasta_video)
    problemas = []
    for nome in IMAGENS_FIXAS:
        if not (pasta_ajuda / nome).exists():
            problemas.append(f"falta {nome}")
    for lg in LINGUAS_COM_VIDEO:
        f = pasta_video / f"tutorial_{lg}.mp4"
        if not f.exists() or f.stat().st_size < VIDEO_MIN_BYTES:
            problemas.append(f"falta o video {f.name}")
    for func in FUNCIONALIDADES:
        for plataforma in (p for p in func.plataformas if p in plataformas):
            for lg in LINGUAS_COM_VIDEO:
                f = pasta_video / f"{plataforma}_{func.id}_{lg}.mp4"
                if not f.exists() or f.stat().st_size < VIDEO_FUNC_MIN_BYTES:
                    problemas.append(f"falta o video {f.name}")
    zonas = caixas(pasta_ajuda)
    for lg in (x for x in linguas if x not in SEM_CAPTURAS_PROPRIAS):
        for estado in [e for p in plataformas for e in (ESTADOS_DE_CAPTURA if p == "windows" else ESTADOS_WEB)]:
            if not (pasta_ajuda / f"{lg}_{estado}.png").exists() or estado not in zonas.get(lg, {}):
                problemas.append(f"falta a captura {lg}_{estado}")
    return problemas


def ficheiro_video(pasta_video: Path, lingua: str) -> Path | None:
    """O video tutorial na `lingua` (ou em ingles / portugues, se nao houver nessa lingua); None se nao ha nenhum.
    Na webapp serve-se como ficheiro estatico (<video>) em vez de abrir o leitor do sistema."""
    for lg in ordem_de_recurso(lingua):
        f = Path(pasta_video) / f"tutorial_{lg}.mp4"
        if f.exists():
            return f
    return None


def video_da_funcionalidade(pasta_video: Path, plataforma: str, id_: str, lingua: str) -> Path | None:
    """O video da funcionalidade `id_` nesta plataforma, na `lingua` (ou em ingles / portugues); None se nao ha nenhum."""
    for lg in ordem_de_recurso(lingua):
        f = Path(pasta_video) / f"{plataforma}_{id_}_{lg}.mp4"
        if f.exists():
            return f
    return None


def recorte(pasta_ajuda: Path, lingua: str, estado: str, zona: str) -> tuple | None:
    """A imagem `('rec', estado, zona)` do tutorial: (bytes PNG, largura natural em unidades logicas), ou None se nao existe.
    Procura na `lingua`, depois em ingles e portugues (como a janela do tutorial). Serve a webapp; a app Windows recorta ela propria."""
    from PIL import Image
    pasta_ajuda = Path(pasta_ajuda)
    zonas = caixas(pasta_ajuda)
    for lg in ordem_de_recurso(lingua):
        info = zonas.get(lg, {}).get(estado)
        ficheiro = pasta_ajuda / f"{lg}_{estado}.png"
        if info and zona in info and ficheiro.exists():
            break
    else:
        return None
    try:
        esc = float(info.get("escala", 1.0)) or 1.0
        with Image.open(ficheiro) as im:
            rec = im.convert("RGB").crop(tuple(info[zona]))
        saida = io.BytesIO()
        rec.save(saida, "PNG")
        return saida.getvalue(), rec.width / esc
    except Exception:
        return None
