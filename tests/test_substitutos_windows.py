"""Testes dos substitutos das dependencias do Windows (docs/MIGRATION_PLAN.md §2):
  registo (tema/cor)  -> core.tema + core.sistema (variaveis de ambiente / CSS)     os.startfile -> core.saida (descarregar)
  kernel32 (lingua)   -> i18n.lingua_de_accept_language                              %APPDATA%    -> config.pasta_de_dados
  ficheiros locais    -> core.armazenamento + core.entradas                          --selftest   -> python -m core
O codigo do Windows (app/ambiente.py) tambem se testa aqui, com um «registo» falso, por isso corre em qualquer sistema."""
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

from core import config, galeria, i18n, sistema, tema, tutorial

RAIZ = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------ core.tema (a paleta que antes dependia do registo)
def test_cor_valida():
    assert tema.cor_valida("#0078D4") == (0, 120, 212) and tema.cor_valida("0078d4") == (0, 120, 212)
    assert tema.cor_valida("  #FFFFFF ") == (255, 255, 255)
    for mau in (None, "", "#123", "#GGGGGG", "azul", "#12345678", "12 456"):
        assert tema.cor_valida(mau) is None, mau


def test_hex_rgb_ida_e_volta():
    assert tema.rgb_para_hex((0, 120, 212)) == "#0078D4" and tema.hex_para_rgb("#0078D4") == (0, 120, 212)
    assert tema.rgb_para_hex((300, -5, 12.6)) == "#FF000D"          # limita a 0..255 e arredonda


def test_misturar_contraste_e_texto_sobre():
    assert tema.misturar((0, 0, 0), (255, 255, 255), 0.5) == (127.5, 127.5, 127.5)
    assert tema.contraste((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0)
    assert tema.texto_sobre((0, 0, 0)) == "#FFFFFF" and tema.texto_sobre((255, 255, 255)) == "#111111"
    c = tema.legivel((200, 200, 200), (255, 255, 255))
    assert tema.contraste(c, (255, 255, 255)) >= 4.5


def test_paleta_de_cor_tem_7_tons_e_o_quarto_e_a_base():
    p = tema.paleta_de_cor((0, 120, 212))
    assert len(p) == 7 and p[3] == (0, 120, 212)
    assert tema.luminancia(p[0]) > tema.luminancia(p[3]) > tema.luminancia(p[6])       # do mais claro ao mais escuro


def test_construir_paleta_do_windows_por_defeito():
    c = tema.construir(tema.PADRAO)
    assert c["acento"] == ("#0078D4", "#4CC2FF") and c["fundo"] == ("#F3F3F3", "#1C1C1C")
    assert c["sobre_acento"] == ("#FFFFFF", "#111111") and c["ok"] == ("#0F7B0F", "#6CCB5F")
    assert len(c) == 18 and all(len(par) == 2 for par in c.values())


def test_variaveis_css():
    css = tema.variaveis_css(tema.construir(tema.PADRAO))
    assert set(css) == {"claro", "escuro"} and set(css["claro"]) == set(css["escuro"])
    assert css["claro"]["--rifas-acento"] == "#0078D4" and css["escuro"]["--rifas-acento"] == "#4CC2FF"
    assert css["claro"]["--rifas-acento-h"] == "#005A9E" and "--rifas-sel-menu" in css["claro"]


# ------------------------------------------------------------------ core.sistema (contrato + implementacao neutra)
def test_sistema_neutro_so_usa_variaveis_de_ambiente(tmp_path):
    s = sistema.SistemaNeutro({})
    assert s.codigo_de_lingua() == "" and s.modo_escuro() is None and s.cor_destaque() is None
    assert s.pasta_de_dados() == Path.home() / ".gerador-rifas" and s.abrir(tmp_path) is False
    s = sistema.SistemaNeutro({"RIFAS_LINGUA": " ja ", "RIFAS_TEMA": "Escuro", "RIFAS_COR_DESTAQUE": "#0078d4",
                               "RIFAS_DADOS": str(tmp_path)})
    assert (s.codigo_de_lingua(), s.modo_escuro(), s.cor_destaque(), s.pasta_de_dados()) == ("ja", True, (0, 120, 212), tmp_path)
    assert sistema.SistemaNeutro({"RIFAS_TEMA": "claro"}).modo_escuro() is False
    assert sistema.SistemaNeutro({"RIFAS_TEMA": "sistema", "RIFAS_COR_DESTAQUE": "azul"}).modo_escuro() is None
    assert sistema.SistemaNeutro({"RIFAS_COR_DESTAQUE": "azul"}).cor_destaque() is None


def test_sistema_neutro_le_o_ambiente_real_por_defeito(monkeypatch):
    monkeypatch.setenv("RIFAS_TEMA", "escuro")
    assert sistema.SistemaNeutro().modo_escuro() is True


def test_sistema_neutro_cumpre_o_contrato():
    assert isinstance(sistema.SistemaNeutro({}), sistema.Sistema)
    assert not isinstance(object(), sistema.Sistema)


def test_sistema_neutro_nao_abre_nada():
    assert sistema.SistemaNeutro({}).abrir(Path("/")) is False         # num servidor «abrir a pasta» nao existe: ver core.saida


# ------------------------------------------------------------------ app/ambiente.py (Windows) com um registo falso
@pytest.fixture
def ambiente(monkeypatch):
    monkeypatch.syspath_prepend(str(RAIZ / "app"))
    import importlib
    import ambiente as amb
    importlib.reload(amb)
    return amb


class RegistoFalso:
    """Imita o winreg: valores por (chave, nome). Chave em falta -> OSError, como no registo real."""
    HKEY_CURRENT_USER = "HKCU"

    def __init__(self, valores):
        self.valores = valores

    def OpenKey(self, raiz, chave):
        if not any(k == chave for k, _ in self.valores):
            raise FileNotFoundError(chave)
        return types.SimpleNamespace(chave=chave, __enter__=None)

    def QueryValueEx(self, k, nome):
        try:
            return self.valores[(k.chave, nome)], 3
        except KeyError:
            raise FileNotFoundError(nome)


class _Ctx:      # OpenKey devolve um gestor de contexto
    def __init__(self, chave):
        self.chave = chave

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _registo(valores):
    r = RegistoFalso(valores)
    r.OpenKey = lambda raiz, chave: (_ for _ in ()).throw(FileNotFoundError(chave)) if not any(k == chave for k, _ in valores) else _Ctx(chave)
    return r


def test_ambiente_importa_se_sem_windows(ambiente):
    assert ambiente.SRC.name == "src" and isinstance(ambiente.SistemaWindows(), sistema.Sistema)


def test_ambiente_sem_registo_devolve_nao_sei(ambiente, monkeypatch):
    monkeypatch.setattr(ambiente, "winreg", None)
    assert ambiente.paleta_do_windows() is None and ambiente.windows_escuro() is None
    assert ambiente.SistemaWindows().cor_destaque() is None and ambiente.SistemaWindows().modo_escuro() is None


def test_ambiente_paleta_do_registo(ambiente, monkeypatch):
    paleta = bytes(sum(([i, 2 * i, 3 * i, 255] for i in range(1, 8)), []))        # 7 x (R, G, B, A)
    monkeypatch.setattr(ambiente, "winreg", _registo({(ambiente.CHAVE_ACENTO, "AccentPalette"): paleta}))
    assert ambiente.paleta_do_windows() == [(i, 2 * i, 3 * i) for i in range(1, 8)]
    assert ambiente.SistemaWindows().cor_destaque() == (4, 8, 12)                   # o 4.o tom


def test_ambiente_paleta_alternativa_dwm(ambiente, monkeypatch):
    abgr = 0xFF_D4_78_00                                                            # 0xAABBGGRR: R=0x00 G=0x78 B=0xD4
    monkeypatch.setattr(ambiente, "winreg", _registo({(ambiente.CHAVE_DWM, "AccentColor"): abgr}))
    p = ambiente.paleta_do_windows()
    assert len(p) == 7 and p[3] == (0, 120, 212)


def test_ambiente_modo_escuro_do_registo(ambiente, monkeypatch):
    for valor, escuro in ((0, True), (1, False)):
        monkeypatch.setattr(ambiente, "winreg", _registo({(ambiente.CHAVE_TEMA, "AppsUseLightTheme"): valor}))
        assert ambiente.windows_escuro() is escuro and ambiente.SistemaWindows().modo_escuro() is escuro
    monkeypatch.setattr(ambiente, "winreg", _registo({}))
    assert ambiente.windows_escuro() is None and ambiente.paleta_do_windows() is None


def test_ambiente_dados_e_abrir(ambiente, monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.delenv("RIFAS_DADOS", raising=False)
    assert ambiente.dados_por_defeito() == tmp_path / "GeradorRifas"
    assert ambiente.SistemaWindows().pasta_de_dados() == tmp_path / "GeradorRifas"
    monkeypatch.setenv("RIFAS_DADOS", str(tmp_path / "outra"))
    assert ambiente.SistemaWindows().pasta_de_dados() == tmp_path / "outra"
    aberto = []
    monkeypatch.setattr(ambiente.os, "startfile", lambda p: aberto.append(p), raising=False)
    assert ambiente.abrir(tmp_path) is True and aberto == [str(tmp_path)]
    monkeypatch.setattr(ambiente.os, "startfile", lambda p: (_ for _ in ()).throw(OSError()), raising=False)
    assert ambiente.abrir(tmp_path) is False


def test_ambiente_lingua_do_windows_fora_do_windows(ambiente, monkeypatch):
    monkeypatch.setattr(ambiente.sys, "platform", "linux")
    assert ambiente.codigo_de_lingua_do_windows() == ""


@pytest.mark.skipif(sys.platform != "win32", reason="so no Windows a sério")
def test_ambiente_no_windows_real(ambiente):
    s = ambiente.SistemaWindows()
    assert isinstance(s.codigo_de_lingua(), str) and s.modo_escuro() in (True, False, None)
    cor = s.cor_destaque()
    assert cor is None or (len(cor) == 3 and all(0 <= c <= 255 for c in cor))


# ------------------------------------------------------------------ lingua do browser (substitui o kernel32)
@pytest.mark.parametrize("cabecalho, lingua", [
    ("pt-PT,pt;q=0.9,en;q=0.8", "pt"),
    ("en-US,en;q=0.9", "en"),
    ("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", "fr"),
    ("xx,yy;q=0.9,de;q=0.5", "de"),                               # a primeira suportada pela ordem de q
    ("de;q=0.5,es;q=0.9", "es"),                                  # q manda, nao a posicao
    ("zh-CN", "zh"), ("hi", "hi"), ("PT_br", "pt-br"),
    ("*", "en"), ("", "en"), (None, "en"), ("klingon", "en"), (";;;,", "en"),
    ("de;q=0", "en"),                                             # q=0 = «nao aceito»
    ("de;q=abc,es;q=0.1", "es"),                                  # q invalido: ignora essa entrada
])
def test_lingua_de_accept_language(cabecalho, lingua):
    assert i18n.lingua_de_accept_language(cabecalho) == lingua


def test_lingua_de_accept_language_por_defeito():
    assert i18n.lingua_de_accept_language("klingon", por_defeito="pt") == "pt"
    assert i18n.lingua_de_accept_language(None, por_defeito="pt") == "pt"


# ------------------------------------------------------------------ preferencias que vem do browser (substitui %APPDATA%)
def test_preferencias_sem_caminhos(tmp_path):
    alg = tmp_path / "a.pdf"
    alg.write_bytes(b"x")
    cfg = {"algarismos": str(alg), "saida": "C:/out", "fim": 99, "papel": "A3"}
    assert config.preferencias(cfg) == {"algarismos": str(alg), "saida": "C:/out", "fim": "99", "papel": "A3"}
    assert config.preferencias(cfg, caminhos=False) == {"fim": "99", "papel": "A3"}


# ------------------------------------------------------------------ video do tutorial (substitui abrir no leitor do Windows)
def test_ficheiro_video(tmp_path):
    assert tutorial.ficheiro_video(tmp_path, "pt") is None
    (tmp_path / "tutorial_pt.mp4").write_bytes(b"x")
    assert tutorial.ficheiro_video(tmp_path, "ja").name == "tutorial_pt.mp4"
    (tmp_path / "tutorial_en.mp4").write_bytes(b"x")
    assert tutorial.ficheiro_video(tmp_path, "ja").name == "tutorial_en.mp4"          # en antes de pt
    assert tutorial.ficheiro_video(tmp_path, "pt").name == "tutorial_pt.mp4"
    assert tutorial.ficheiro_video(RAIZ / "app" / "assets" / "video", "pt").name == "tutorial_pt.mp4"


# ------------------------------------------------------------------ auto-teste fora do Windows (substitui o --selftest do .exe)
def test_python_m_core_corre_o_autoteste(tmp_path):
    r = subprocess.run([sys.executable, "-m", "core", str(RAIZ / "tests" / "fixtures"), str(tmp_path)],
                       capture_output=True, text=True, timeout=300, cwd=RAIZ / "src",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": ""})
    assert r.returncode == 0, r.stderr
    linhas = r.stdout.strip().splitlines()
    assert linhas[0] == f"traducoes ({len(i18n.LINGUAS)} linguas): ok" and linhas[-1] == "RESULTADO: OK"
    assert len(linhas) == 10 + 25         # traducoes + RESULTADO + 8 exemplos + os 25 desenhos da galeria
    assert [l.split(":")[0] for l in linhas[-26:-22]] == ["galeria bosque", "galeria quermesse", "galeria natal", "galeria gala"]
    assert [l.split(":")[0] for l in linhas[-26:-1]] == [f"galeria {d.id}" for d in galeria.DESENHOS]


def test_python_m_core_sem_argumentos():
    r = subprocess.run([sys.executable, "-m", "core"], capture_output=True, text=True, timeout=60, cwd=RAIZ / "src",
                       env={**os.environ, "PYTHONPATH": ""})
    assert r.returncode == 2 and "uso:" in r.stderr
