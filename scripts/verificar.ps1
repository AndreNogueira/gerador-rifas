# Corre em local o mesmo que o CI: ruff, pytest, e no frontend Biome, tsc, Vitest e build. Uso (a partir da raiz):
#   powershell -File scripts/verificar.ps1            # tudo, menos o Docker
#   powershell -File scripts/verificar.ps1 -Docker    # junta a construcao das imagens (precisa do Docker a correr)
#   powershell -File scripts/verificar.ps1 -E2e       # junta os testes e2e (Playwright; uma vez: pnpm exec playwright install chromium)
# Este ficheiro e so ASCII de proposito: o PowerShell 5.1 le UTF-8 sem BOM como ANSI.
param([switch]$Docker, [switch]$E2e)

$raiz = Split-Path -Parent $PSScriptRoot
$falhas = @()

function Passo([string]$nome, [string]$pasta, [scriptblock]$comando) {
    Write-Host ""
    Write-Host "==> $nome" -ForegroundColor Cyan
    Push-Location $pasta
    try {
        & $comando
        if ($LASTEXITCODE -ne 0) { $script:falhas += $nome; Write-Host "FALHOU: $nome" -ForegroundColor Red }
    } finally { Pop-Location }
}

$front = Join-Path $raiz "src\web\frontend"

Passo "ruff"            $raiz  { uv run ruff check . }
Passo "pytest"          $raiz  { uv run pytest -q }
Passo "frontend: Biome" $front { pnpm run lint }
Passo "frontend: tsc"   $front { pnpm run tipos }
Passo "frontend: Vitest" $front { pnpm run teste }
Passo "frontend: build" $front { pnpm run build }

if ($E2e) {
    Passo "frontend: e2e (Playwright)" $front { pnpm run e2e }
}

if ($Docker) {
    Passo "docker: testes" $raiz { docker build --target testes -t gerador-rifas-testes . }
    Passo "docker: web"    $raiz { docker build --target web -t gerador-rifas . }
}

Write-Host ""
if ($falhas.Count -eq 0) {
    Write-Host "Tudo verde. Podes abrir o PR." -ForegroundColor Green
    exit 0
}
Write-Host ("Falhou: " + ($falhas -join ", ")) -ForegroundColor Red
exit 1
