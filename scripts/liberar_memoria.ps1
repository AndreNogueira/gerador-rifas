# Liberta a memoria antes de trabalho pesado (build do .exe com o Nuitka, pytest completo, e2e).
# O Rancher Desktop deixa a maquina virtual do WSL (`vmmem`) a segurar ~15 GB durante dias, mesmo sem contentores do utilizador, e foi isso que fez o
# Claude Code matar a compilacao do .exe 2.6.0 por falta de memoria. Fecha o Rancher e o WSL; volta a abrir-se quando for preciso (testes no Docker).
# Uso: powershell -File scripts\liberar_memoria.ps1 [-ManterRancher]    (nao toca em Chrome, VS Code nem em processos python)
param([switch]$ManterRancher)

function Livre { "{0:N1} GB livres de {1:N1}" -f ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB), ((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize / 1MB) }
function VmMem { [math]::Round(((Get-Process vmmem* -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum) / 1GB, 1) }

"Antes:  $(Livre); vmmem = $(VmMem) GB"
if (-not $ManterRancher) {
    $rdctl = "C:\Program Files\Rancher Desktop\resources\resources\win32\bin\rdctl.exe"
    if (Test-Path $rdctl) { & $rdctl shutdown 2>&1 | Out-Null }
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 10
}
"Depois: $(Livre); vmmem = $(VmMem) GB"
