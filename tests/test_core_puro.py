"""O pacote src/core nao pode depender de interface desktop, do Windows nem de frameworks web (regra do CLAUDE.md)."""
import ast
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
CORE = SRC / "core"
PROIBIDOS = {"tkinter", "_tkinter", "customtkinter", "win32api", "win32con", "win32gui", "win32com", "pywintypes",
             "pythoncom", "winreg", "_winreg", "ctypes", "msvcrt", "winsound", "fastapi", "starlette", "uvicorn", "flask",
             "django", "nicegui", "darkdetect"}


def _importados(ficheiro: Path):
    arvore = ast.parse(ficheiro.read_text(encoding="utf-8"), filename=str(ficheiro))
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for a in no.names:
                yield a.name, no.lineno
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            yield no.module, no.lineno


def _ficheiros():
    return sorted(CORE.rglob("*.py"))


def test_ha_ficheiros_para_verificar():
    assert len(_ficheiros()) >= 15 and (CORE / "__init__.py").exists()


@pytest.mark.parametrize("ficheiro", _ficheiros(), ids=lambda p: str(p.relative_to(CORE)))
def test_sem_imports_de_ui_nem_windows(ficheiro):
    maus = [(m, linha) for m, linha in _importados(ficheiro)
            if m.split(".")[0] in PROIBIDOS or m.split(".")[0].startswith("win32")]
    assert maus == [], f"{ficheiro.name}: {maus}"


def test_sem_referencias_ao_windows_no_codigo():
    # nada de os.startfile, windll, APPDATA nem caminhos com letra de unidade (so comentarios/docstrings a explicar a regra)
    for f in _ficheiros():
        arvore = ast.parse(f.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Attribute):
                assert no.attr not in {"startfile", "windll", "WinDLL"}, (f.name, no.lineno)
            if isinstance(no, ast.Constant) and isinstance(no.value, str) and len(no.value) < 200 and "\n" not in no.value:
                assert "APPDATA" not in no.value, (f.name, no.lineno)
                assert not (len(no.value) > 2 and no.value[1:3] == ":\\" and no.value[0].isalpha()), (f.name, no.lineno, no.value)


def test_import_core_nao_carrega_tkinter_nem_windows():
    codigo = (
        "import sys; sys.path.insert(0, %r); import core\n"
        # (ctypes e winreg nao entram aqui: as bibliotecas de terceiros - pypdfium2, PIL - usam-nos; o AST acima cobre o nosso codigo)
        "mal = [m for m in ('tkinter','customtkinter','win32api','fastapi','starlette') if m in sys.modules]\n"
        "assert not mal, mal\n"
        "assert core.preparar and core.pedido and core.config and core.escolha_folha and core.tutorial and core.autoteste\n"
        "print('ok')\n" % str(SRC))
    r = subprocess.run([sys.executable, "-I", "-c", codigo], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and r.stdout.strip() == "ok", r.stderr
