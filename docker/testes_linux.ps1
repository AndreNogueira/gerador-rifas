# Corre os testes do motor num contentor Linux (Rancher Desktop com o motor dockerd/moby ligado).
# Uso (a partir da raiz do repo):  powershell -File docker\testes_linux.ps1 [-Python 3.15]
param([string]$Python = "3.15")
$bin = "C:\Program Files\Rancher Desktop\resources\resources\win32\bin"     # o docker do Rancher nem sempre esta no PATH
if (Test-Path $bin) { $env:PATH = "$bin;$env:PATH" }
$raiz = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
docker run --rm -v "${raiz}:/repo" -e UV_PROJECT_ENVIRONMENT=/opt/venv -e UV_LINK_MODE=copy -e PYTHONDONTWRITEBYTECODE=1 `
    -e UV_PYTHON_DOWNLOADS=never -e UV_PYTHON=$Python "python:${Python}-slim" sh /repo/docker/testes_linux.sh
exit $LASTEXITCODE
