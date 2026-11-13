@echo off
rem Cria o ambiente (se faltar), compila a app para codigo nativo com o Nuitka e assina o .exe.
rem Resultado: dist\GeradorRifas.exe
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
  echo Precisa do "uv" ^(https://docs.astral.sh/uv/^) ou de um Python 3.15 com venv. Veja o README.
  exit /b 1
)
rem Python 3.15 (desde a 2.5). Uma .venv antiga de outra versao (a 3.13 da 2.4) e recriada em vez de reutilizada em silencio.
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 15) else 1)" || (
    echo A .venv e de outra versao do Python: a recriar com a 3.15.
    rmdir /s /q .venv
  )
)
if not exist .venv\Scripts\python.exe uv venv .venv --python 3.15 || exit /b 1
uv pip install --python .venv\Scripts\python.exe -r requirements.txt || exit /b 1
rem O zstandard (compressao do .exe) nao tem roda para a 3.15 no Windows: compila-se se houver o Visual C++ (como nos servidores do GitHub); senao o
rem Nuitka faz o .exe sem compressao, que fica maior mas funciona igual.
uv pip install --python .venv\Scripts\python.exe zstandard || echo AVISO: sem zstandard, o .exe fica sem compressao ^(maior^).
.venv\Scripts\python.exe make_icon.py

rem Nuitka traduz o Python para C e compila (a 1.a vez descarrega sozinho o compilador "zig", cerca de 10-20 min).
rem O resultado nao contem codigo Python nem bytecode (.pyc), so codigo maquina: muito mais dificil de reverter.
rem --python-flag=no_docstrings/no_asserts: tira docstrings e assert do binario.
rem --onefile-tempdir-spec: o .exe descompacta-se uma so vez para %%LOCALAPPDATA%% (arranques seguintes rapidos).
rem O motor (pacote `core`) esta em ..\src: o Nuitka tem de o encontrar e incluir no executavel.
rem Os videos do SITE (assets\video\web_*) nao vao no .exe: o tutorial da app so usa os `windows_*`.
set "PYTHONPATH=%~dp0..\src"
rem Python 3.15 traz o Tcl/Tk 9 (bibliotecas dentro da DLL): o Nuitka precisa de duas pastas «de fachada» (ver tcl_dirs.py); com o Tcl 8.6 isto fica vazio.
set "TCLTK="
for /f "tokens=1,2 delims=;" %%a in ('.venv\Scripts\python.exe tcl_dirs.py') do set "TCLTK=--tcl-library-dir=%%a --tk-library-dir=%%b"
.venv\Scripts\python.exe -m nuitka --onefile --assume-yes-for-downloads --remove-output ^
  --output-dir=dist --output-filename=GeradorRifas.exe ^
  --windows-console-mode=disable --windows-icon-from-ico=assets\icon.ico ^
  --enable-plugin=tk-inter %TCLTK% ^
  --include-package=core --include-package-data=customtkinter --include-package-data=pypdfium2 --include-package-data=pypdfium2_raw --include-package-data=reportlab ^
  --include-data-dir=assets=assets --include-data-dir=exemplos=exemplos ^
  --noinclude-data-files=assets/video/web_* ^
  --noinclude-data-files=assets/ajuda/*_w?.png ^
  --python-flag=no_docstrings --python-flag=no_asserts --python-flag=no_warnings ^
  --nofollow-import-to=segno --nofollow-import-to=fontTools --nofollow-import-to=psutil --nofollow-import-to=numpy ^
  --onefile-tempdir-spec="{CACHE_DIR}/GeradorRifas/{VERSION}" ^
  --company-name="Gerador de Rifas" --product-name="Gerador de Rifas" ^
  --file-description="Gerador de rifas a partir de templates PDF" ^
  --file-version=2.5.0.0 --product-version=2.5.0.0 --copyright="Gerador de Rifas" ^
  app.py || exit /b 1

rem Assinatura digital (autoassinada por defeito; com um certificado comprado: assinar.ps1 -Pfx ficheiro.pfx)
rem (SEM_ASSINATURA=1, como no GitHub Actions, salta este passo: um certificado autoassinado criado no servidor nao vale nada)
if defined SEM_ASSINATURA (
  echo SEM_ASSINATURA definido: o .exe fica sem assinatura digital.
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File assinar.ps1 -Exe dist\GeradorRifas.exe
)
echo.
echo Pronto: %~dp0dist\GeradorRifas.exe
