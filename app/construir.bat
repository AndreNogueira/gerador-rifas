@echo off
rem Cria o ambiente (se faltar), compila a app para codigo nativo com o Nuitka e assina o .exe.
rem Resultado: dist\GeradorRifas.exe
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
  echo Precisa do "uv" ^(https://docs.astral.sh/uv/^) ou de um Python 3.13 com venv. Veja o README.
  exit /b 1
)
if not exist .venv\Scripts\python.exe uv venv .venv --python 3.13 || exit /b 1
uv pip install --python .venv\Scripts\python.exe -r requirements.txt || exit /b 1
.venv\Scripts\python.exe make_icon.py

rem Nuitka traduz o Python para C e compila (a 1.a vez descarrega sozinho o compilador "zig", cerca de 10-20 min).
rem O resultado nao contem codigo Python nem bytecode (.pyc), so codigo maquina: muito mais dificil de reverter.
rem --python-flag=no_docstrings/no_asserts: tira docstrings e assert do binario.
rem --onefile-tempdir-spec: o .exe descompacta-se uma so vez para %%LOCALAPPDATA%% (arranques seguintes rapidos).
rem O motor (pacote `core`) esta em ..\src: o Nuitka tem de o encontrar e incluir no executavel.
set "PYTHONPATH=%~dp0..\src"
.venv\Scripts\python.exe -m nuitka --onefile --assume-yes-for-downloads --remove-output ^
  --output-dir=dist --output-filename=GeradorRifas.exe ^
  --windows-console-mode=disable --windows-icon-from-ico=assets\icon.ico ^
  --enable-plugin=tk-inter ^
  --include-package=core --include-package-data=customtkinter --include-package-data=pypdfium2 --include-package-data=pypdfium2_raw ^
  --include-data-dir=assets=assets --include-data-dir=exemplos=exemplos ^
  --python-flag=no_docstrings --python-flag=no_asserts --python-flag=no_warnings ^
  --nofollow-import-to=reportlab --nofollow-import-to=fontTools --nofollow-import-to=psutil --nofollow-import-to=numpy ^
  --onefile-tempdir-spec="{CACHE_DIR}/GeradorRifas/{VERSION}" ^
  --company-name="Gerador de Rifas" --product-name="Gerador de Rifas" ^
  --file-description="Gerador de rifas a partir de templates PDF" ^
  --file-version=2.2.0.0 --product-version=2.2.0.0 --copyright="Gerador de Rifas" ^
  app.py || exit /b 1

rem Assinatura digital (autoassinada por defeito; com um certificado comprado: assinar.ps1 -Pfx ficheiro.pfx)
powershell -NoProfile -ExecutionPolicy Bypass -File assinar.ps1 -Exe dist\GeradorRifas.exe
echo.
echo Pronto: %~dp0dist\GeradorRifas.exe
