# Manutencao do Rancher Desktop: impede o disco do WSL (ext4.vhdx) de crescer sem limite e garante as imagens do projeto.
# (ASCII de proposito: o PowerShell 5.1 le .ps1 sem BOM como ANSI.)
#
#   powershell -File scripts\manter_rancher.ps1                 # poda + imagens do projeto + compacta se o disco passou o limite
#   powershell -File scripts\manter_rancher.ps1 -Instalar       # regista a tarefa semanal (pede administrador: UAC)
#   powershell -File scripts\manter_rancher.ps1 -ForcarCompactar
#
# A regra:
#  1. Cache de build (BuildKit): guarda so os ultimos $CacheGB GB (foi ela que chegou aos 88 GB).
#  2. Imagens: NUNCA apaga imagens com etiqueta, so as orfas (<none>); as que o projeto precisa (FROM do Dockerfile) sao puxadas se faltarem.
#  3. Volumes: NUNCA toca (nenhum `prune --volumes`).
#  4. O ficheiro .vhdx do WSL nunca encolhe sozinho (o modo "sparse" esta desativado no WSL 2.6 por risco de corromper dados), por isso,
#     se passar de $LimiteVhdxGB, fecha o Rancher, compacta os .vhdx com o diskpart e volta a abri-lo (precisa de administrador).
param([switch]$Instalar, [switch]$ForcarCompactar, [int]$CacheGB = 10, [int]$LimiteVhdxGB = 60)

$ErrorActionPreference = 'Continue'
$raiz = Split-Path -Parent $PSScriptRoot
$rd = 'C:\Program Files\Rancher Desktop\resources\resources\win32\bin'
$dados = Join-Path $env:LOCALAPPDATA 'rancher-desktop'
$vhdx = @('distro-data\ext4.vhdx', 'distro\ext4.vhdx') | ForEach-Object { Join-Path $dados $_ } | Where-Object { Test-Path $_ }
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# alem dos FROM do Dockerfile: o Postgres que o CI e os testes usam
$ImagensExtra = @('postgres:17.11')
function Garantir-Imagem($img) {
    & docker image inspect $img 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "a puxar $img"; & docker pull $img | Select-Object -Last 1 }
}
function Tamanho-Vhdx { ($vhdx | ForEach-Object { (Get-Item $_).Length } | Measure-Object -Sum).Sum / 1GB }

if ($Instalar) {
    if (-not $admin) {
        Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-Instalar'
        exit
    }
    $acao = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`""
    $gatilhos = @((New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 4am), (New-ScheduledTaskTrigger -AtLogOn))
    $defs = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2)
    $quem = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    Register-ScheduledTask -TaskName 'Rancher-Manutencao' -Action $acao -Trigger $gatilhos -Settings $defs -Principal $quem -Force | Out-Null
    Write-Host 'Tarefa "Rancher-Manutencao" registada (domingo as 4h e ao iniciar sessao; so compacta se o disco passar de' $LimiteVhdxGB 'GB).'
    exit
}

$env:Path += ";$rd"
$docker = Get-Command docker -ErrorAction SilentlyContinue
$ativo = $docker -and (& docker info 2>$null | Select-String 'Server Version')
if ($ativo) {
    Write-Host '== poda'
    & docker builder prune -f --keep-storage "${CacheGB}GB" | Select-Object -Last 1
    & docker image prune -f | Select-Object -Last 1
    # as imagens de que o projeto precisa (FROM do Dockerfile, com os ARG resolvidos): so se faltarem
    $df = Get-Content (Join-Path $raiz 'Dockerfile') -Raw
    $args_ = @{}; [regex]::Matches($df, '(?m)^ARG\s+(\w+)=(\S+)') | ForEach-Object { $args_[$_.Groups[1].Value] = $_.Groups[2].Value }
    [regex]::Matches($df, '(?m)^FROM\s+(\S+)') | ForEach-Object {
        $img = $_.Groups[1].Value
        $img = [regex]::Replace($img, '\$\{(\w+)\}', { param($m) $args_[$m.Groups[1].Value] })
        if ($img -match '^\$|^(base|frontend|uv|testes)$') { return }
        Garantir-Imagem $img
    }
    foreach ($img in $ImagensExtra) { Garantir-Imagem $img }
    & docker system df
} else { Write-Host 'Docker/Rancher nao esta ativo: so verifico o tamanho do disco.' }

$gb = Tamanho-Vhdx
Write-Host ('discos do WSL: {0:N1} GB (limite {1})' -f $gb, $LimiteVhdxGB)
if ($gb -gt $LimiteVhdxGB -or $ForcarCompactar) {
    if (-not $admin) { Write-Host 'Compactar precisa de administrador: corre -Instalar (a tarefa ja corre com os privilegios maximos).'; exit 1 }
    Write-Host '== a compactar (o Rancher fecha e volta a abrir)'
    & "$rd\rdctl.exe" shutdown 2>$null | Out-Null
    Start-Sleep 10; wsl --shutdown; Start-Sleep 5
    foreach ($v in $vhdx) {
        $antes = (Get-Item $v).Length / 1GB
        $s = New-TemporaryFile
        @("select vdisk file=`"$v`"", 'attach vdisk readonly', 'compact vdisk', 'detach vdisk', 'exit') | Set-Content $s -Encoding ascii
        diskpart /s $s | Out-Null; Remove-Item $s -Force
        Write-Host ('{0}: {1:N1} GB -> {2:N1} GB' -f $v, $antes, ((Get-Item $v).Length / 1GB))
    }
    # reabre-o SEM direitos de administrador (pelo Explorer): aberto daqui, o Docker ficava so acessivel a administradores ("permission denied")
    Start-Process explorer.exe '"C:\Program Files\Rancher Desktop\Rancher Desktop.exe"'
}
