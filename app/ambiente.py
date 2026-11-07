"""Poe a pasta src/ (onde esta o pacote `core`, a logica sem interface) no sys.path e guarda TUDO o que e do Windows.

`import ambiente` tem de ser a primeira importacao do projeto em app.py e nos scripts de testes/. No .exe compilado
(Nuitka) nao existe pasta src/: o pacote `core` vai dentro do executavel e este ficheiro nao faz nada a isso.

O que e do Windows (registo, kernel32, os.startfile) esta so aqui, atras do contrato `core.sistema.Sistema`; o resto do
codigo (core/, tema.py, app.py) nao importa winreg/ctypes. Em Linux estas funcoes devolvem "nao sei" e a app nao arranca
(precisa de Tk), mas o modulo importa-se sem erros.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE.parent / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:                                    # so existe no Windows
    import winreg
except ImportError:
    winreg = None

CHAVE_ACENTO = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent"
CHAVE_DWM = r"SOFTWARE\Microsoft\Windows\DWM"
CHAVE_TEMA = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"


def dados_por_defeito() -> Path:
    """Pasta de dados da app Windows: %APPDATA%\\GeradorRifas (a variavel RIFAS_DADOS, se existir, tem prioridade
    - ver core.config.pasta_de_dados)."""
    return Path(os.environ.get("APPDATA", Path.home())) / "GeradorRifas"


def codigo_de_lingua_do_windows() -> str:
    """Codigo da lingua do Windows (p.ex. «pt-PT»), ou «» se nao se conseguir (outro sistema ou erro)."""
    try:
        if sys.platform == "win32":
            import ctypes
            buf = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85):
                return buf.value
    except Exception:
        pass
    return ""


def paleta_do_windows() -> list | None:
    """7 tons RGB da cor de destaque do Windows (do mais claro ao mais escuro), ou None se nao se consegue ler."""
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_ACENTO) as k:
            v, _ = winreg.QueryValueEx(k, "AccentPalette")
        if len(v) >= 28:
            return [tuple(v[i:i + 3]) for i in range(0, 28, 4)]
    except OSError:
        pass
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_DWM) as k:
            v, _ = winreg.QueryValueEx(k, "AccentColor")        # 0xAABBGGRR
        from core.tema import paleta_de_cor
        return paleta_de_cor((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF))
    except OSError:
        pass
    return None


def windows_escuro() -> bool | None:
    """True se o Windows esta em modo escuro, False se claro, None se nao se consegue ler."""
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_TEMA) as k:
            return winreg.QueryValueEx(k, "AppsUseLightTheme")[0] == 0
    except OSError:
        return None


def abrir(caminho: Path) -> bool:
    """Abre uma pasta ou ficheiro com o programa predefinido do Windows (os.startfile). False se falhar."""
    try:
        os.startfile(str(caminho))  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


class SistemaWindows:
    """Implementacao de core.sistema.Sistema para o Windows."""

    def codigo_de_lingua(self) -> str:
        return codigo_de_lingua_do_windows()

    def pasta_de_dados(self) -> Path:
        from core import config
        return config.pasta_de_dados(dados_por_defeito())

    def modo_escuro(self) -> bool | None:
        return windows_escuro()

    def cor_destaque(self) -> tuple | None:
        p = paleta_do_windows()
        return tuple(p[3]) if p else None

    def abrir(self, caminho: Path) -> bool:
        return abrir(caminho)
