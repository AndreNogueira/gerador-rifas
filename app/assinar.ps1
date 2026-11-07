<#
  Assina digitalmente o executavel (Authenticode).

  Sem argumentos extra: usa (ou cria) um certificado AUTOASSINADO de assinatura de codigo no repositorio
  pessoal do utilizador (Cert:\CurrentUser\My). Isto da ao .exe uma identidade verificavel e protege contra
  alteracoes, mas o Windows SmartScreen so deixa de avisar nos PCs onde esse certificado for instalado
  (ver instalar_certificado.ps1). Para o aviso desaparecer em QUALQUER PC e preciso um certificado emitido por
  uma autoridade reconhecida (OV/EV ou Azure Trusted Signing): quando o tiver, basta
      .\assinar.ps1 -Exe dist\GeradorRifas.exe -Pfx meu_certificado.pfx -Senha "..." -Timestamp

  Parametros:
    -Exe        ficheiro a assinar (por defeito dist\GeradorRifas.exe)
    -Pfx/-Senha certificado em ficheiro .pfx (opcional)
    -Timestamp  carimba a assinatura com a hora (envia o hash do ficheiro a um servidor de tempo, ex. DigiCert)
#>
param(
    [string]$Exe = "dist\GeradorRifas.exe",
    [string]$Pfx = "",
    [string]$Senha = "",
    [switch]$Timestamp
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path $Exe)) { Write-Host "Nao encontro $Exe"; exit 1 }

if ($Pfx) {
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($Pfx, $Senha)
} else {
    $assunto = "CN=Gerador de Rifas (autoassinado)"
    $cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -eq $assunto -and $_.NotAfter -gt (Get-Date) } | Select-Object -First 1
    if (-not $cert) {
        Write-Host "A criar certificado de assinatura autoassinado (valido 5 anos)..."
        $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $assunto -KeyAlgorithm RSA -KeyLength 3072 `
            -HashAlgorithm SHA256 -CertStoreLocation Cert:\CurrentUser\My -NotAfter (Get-Date).AddYears(5)
    }
    New-Item -ItemType Directory -Force assinatura | Out-Null
    Export-Certificate -Cert $cert -FilePath "assinatura\GeradorRifas.cer" | Out-Null   # so a parte publica
}

$args2 = @{ FilePath = $Exe; Certificate = $cert; HashAlgorithm = "SHA256" }
if ($Timestamp) { $args2.TimestampServer = "http://timestamp.digicert.com" }
$r = Set-AuthenticodeSignature @args2
Write-Host ("Assinado: {0}  (estado: {1})" -f $Exe, $r.Status)
Write-Host ("Certificado: {0}  impressao digital {1}" -f $cert.Subject, $cert.Thumbprint)
if (-not $Pfx) {
    Write-Host "Certificado publico (para instalar noutros PCs): assinatura\GeradorRifas.cer"
}
