"""A regra «funcionalidade de utilizador = tutorial + vídeo (+ changelog), tudo traduzido» (CLAUDE.md), verificada por máquina.

`core.tutorial.FUNCIONALIDADES` é a lista das funcionalidades de utilizador. Cada uma tem de ter: um tópico no tutorial nas 18 línguas (`tut_f_<id>_t/_b`), um
vídeo por plataforma em pt e en (`app/assets/video/<plataforma>_<id>_<lg>.mp4`) e uma cena no script que o grava (site: `e2e/videos.spec.ts`;
app Windows: `app/testes/fazer_videos_windows.py`). Quem acrescenta uma funcionalidade e se esquece de uma destas coisas faz falhar este ficheiro."""
import re
from pathlib import Path

import pytest

from core import i18n, tutorial

RAIZ = Path(__file__).resolve().parent.parent
VIDEOS = RAIZ / "app" / "assets" / "video"
_SPEC = RAIZ / "src" / "web" / "frontend" / "e2e" / "videos.spec.ts"
_SCRIPT = RAIZ / "app" / "testes" / "fazer_videos_windows.py"          # a imagem Docker de testes não leva app/testes (.dockerignore): aí estes testes saltam
SPEC_WEB = _SPEC.read_text(encoding="utf-8") if _SPEC.exists() else ""
SCRIPT_WINDOWS = _SCRIPT.read_text(encoding="utf-8") if _SCRIPT.exists() else ""
sem_scripts = pytest.mark.skipif(not (SPEC_WEB and SCRIPT_WINDOWS), reason="os scripts de gravação não estão nesta cópia (imagem Docker de testes)")
IDS = [f.id for f in tutorial.FUNCIONALIDADES]


def test_ids_unicos_e_plataformas_validas():
    assert len(set(IDS)) == len(IDS)
    for f in tutorial.FUNCIONALIDADES:
        assert f.plataformas and set(f.plataformas) <= set(tutorial.PLATAFORMAS) and re.fullmatch(r"[a-z]+", f.id)


@pytest.mark.parametrize("f", tutorial.FUNCIONALIDADES, ids=IDS)
def test_cada_funcionalidade_tem_texto_nas_18_linguas_e_o_marcador_onde_certo(f):
    for lg in i18n.LINGUAS:
        for sufixo in ("t", "b"):
            assert i18n.TEXTOS[lg][f"tut_f_{f.id}_{sufixo}"].strip(), (lg, f.id, sufixo)
        corpo = i18n.TEXTOS[lg][f"tut_f_{f.id}_b"]
        assert ("{onde}" in corpo) == f.onde, (lg, f.id)


@pytest.mark.parametrize("f", tutorial.FUNCIONALIDADES, ids=IDS)
def test_cada_funcionalidade_tem_o_seu_video_por_plataforma_em_pt_e_en(f):
    for plataforma in f.plataformas:
        for lg in tutorial.LINGUAS_COM_VIDEO:
            v = VIDEOS / f"{plataforma}_{f.id}_{lg}.mp4"
            assert v.exists() and v.stat().st_size >= tutorial.VIDEO_FUNC_MIN_BYTES, f"falta gravar {v.name}"
            assert v.read_bytes()[4:8] == b"ftyp", f"{v.name} não é um MP4"
        assert tutorial.video_da_funcionalidade(VIDEOS, plataforma, f.id, "pt").name == f"{plataforma}_{f.id}_pt.mp4"
        assert tutorial.video_da_funcionalidade(VIDEOS, plataforma, f.id, "ja").name == f"{plataforma}_{f.id}_en.mp4"      # sem vídeo na língua: inglês


def test_nao_ha_videos_a_mais():
    esperados = {f"{p}_{f.id}_{lg}.mp4" for f in tutorial.FUNCIONALIDADES for p in f.plataformas for lg in tutorial.LINGUAS_COM_VIDEO}
    existentes = {v.name for v in VIDEOS.glob("*_*_??.mp4") if v.name.split("_")[0] in tutorial.PLATAFORMAS}
    assert existentes == esperados, f"a mais: {existentes - esperados}; em falta: {esperados - existentes}"


@sem_scripts
@pytest.mark.parametrize("f", tutorial.FUNCIONALIDADES, ids=IDS)
def test_cada_funcionalidade_tem_a_sua_cena_nos_scripts_que_gravam_os_videos(f):
    if "web" in f.plataformas:
        assert f'id: "{f.id}"' in SPEC_WEB, f"falta a cena «{f.id}» em e2e/videos.spec.ts"
    if "windows" in f.plataformas:
        assert f'"{f.id}": (' in SCRIPT_WINDOWS, f"falta a cena «{f.id}» em app/testes/fazer_videos_windows.py"


@sem_scripts
def test_o_registo_e_as_cenas_nao_tem_funcionalidades_a_mais():
    assert set(re.findall(r'^\s+id: "([a-z]+)",', SPEC_WEB, re.M)) == {f.id for f in tutorial.funcionalidades("web")}
    assert set(re.findall(r'"([a-z]+)": \((?:VARIAS|UMA_RIFA|None)', SCRIPT_WINDOWS)) == {f.id for f in tutorial.funcionalidades("windows")}


# ------------------------------------------------------------------ os tópicos
@pytest.mark.parametrize("plataforma", tutorial.PLATAFORMAS)
def test_topicos_e_ids_de_video_andam_em_paralelo_e_os_de_base_vem_primeiro(plataforma):
    topicos, ids = tutorial.lista_de_topicos(plataforma), tutorial.video_ids(plataforma)
    assert len(topicos) == len(ids) == tutorial.N_BASE + len(tutorial.funcionalidades(plataforma))
    assert ids[: tutorial.N_BASE] == [None] * tutorial.N_BASE and ids[tutorial.N_BASE:] == [f.id for f in tutorial.funcionalidades(plataforma)]
    assert tutorial.TOPICO_ALGARISMOS == 3 and topicos[3][3][0] == ("fixa", "digitos.png")        # os de base não mexem: as capturas dependem deles


def test_o_windows_nao_mostra_o_que_so_existe_no_site():
    windows = {f.id for f in tutorial.funcionalidades("windows")}
    assert {"qr", "guardar", "instalar"}.isdisjoint(windows) and {"series", "galeria", "editor", "sorteio", "visual"} <= windows
    assert "pedido" in windows                                                   # guardar/abrir o pedido em ficheiro: a versão da app para o «guardar» do site
    assert {f.id for f in tutorial.funcionalidades("web")} == set(IDS) - {"pedido"}
    assert "partilhar" not in windows                                            # o botão «Partilhar» é do site (as redes e o «partilhar» do browser)


@pytest.mark.parametrize("lg", list(i18n.LINGUAS))
@pytest.mark.parametrize("plataforma", tutorial.PLATAFORMAS)
def test_os_topicos_das_funcionalidades_renderizam_em_todas_as_linguas(plataforma, lg):
    with i18n.com_lingua(lg):
        topicos = tutorial.lista_de_topicos(plataforma)[tutorial.N_BASE:]
    assert len(topicos) == len(tutorial.funcionalidades(plataforma))
    for menu, titulo, texto, imagens in topicos:
        assert menu.strip() and titulo.strip() and len(texto) > 80 and imagens == []
        assert "{" not in texto and "}" not in texto, (lg, titulo)


def test_o_onde_diz_o_menu_no_windows_e_a_pagina_no_site():
    with i18n.com_lingua("pt"):
        galeria_w = next(t for t in tutorial.lista_de_topicos("windows") if t[1] == "Galeria de templates")
        galeria_s = next(t for t in tutorial.lista_de_topicos("web") if t[1] == "Galeria de templates")
        guardar = next(t for t in tutorial.lista_de_topicos("web") if t[1].startswith("Guardar"))
    assert "menu «Extras» → «Galeria de templates»" in galeria_w[2] and "Onde: «Sem template? Escolha um da galeria»" in galeria_s[2]
    assert "Onde" not in guardar[2]


def test_verificar_ajuda_exige_os_videos_das_funcionalidades(tmp_path):
    problemas = tutorial.verificar_ajuda(RAIZ / "app" / "assets" / "ajuda", tmp_path, ["pt"])
    assert any("web_series_pt.mp4" in p for p in problemas) and any("windows_sorteio_en.mp4" in p for p in problemas)
    so_windows = tutorial.verificar_ajuda(RAIZ / "app" / "assets" / "ajuda", tmp_path, ["pt"], ("windows",))          # a app Windows só leva os seus vídeos
    assert any("windows_series_pt.mp4" in p for p in so_windows) and not any("web_" in p for p in so_windows)
    assert tutorial.verificar_ajuda(RAIZ / "app" / "assets" / "ajuda", VIDEOS, list(i18n.LINGUAS)) == []
