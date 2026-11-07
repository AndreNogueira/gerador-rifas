<#
  Para correr no PC ONDE o programa vai ser usado (nao no PC que o constroi), depois de copiar tambem
  assinatura\GeradorRifas.cer. Faz o Windows confiar nos programas assinados com esse certificado
  (o aviso "Editor desconhecido" do SmartScreen deixa de aparecer nesse PC).

  ATENCAO: instala o certificado como autoridade de confianca SO PARA O UTILIZADOR ATUAL (nao precisa de
  administrador). So o faca se confiar neste ficheiro .cer. Para desfazer: certmgr.msc -> Autoridades de
  Certificacao de Raiz Fidedignas e Editores Fidedignos -> apagar "Gerador de Rifas (autoassinado)".
#>
param([string]$Cer = "$PSScriptRoot\assinatura\GeradorRifas.cer")
if (-not (Test-Path $Cer)) { Write-Host "Nao encontro $Cer"; exit 1 }
$c = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($Cer)
Write-Host "Certificado: $($c.Subject)  impressao digital $($c.Thumbprint)"
$resp = Read-Host "Instalar como confiavel para o utilizador atual? (s/N)"
if ($resp -notmatch '^[sSyY]') { Write-Host "Cancelado."; exit 0 }
Import-Certificate -FilePath $Cer -CertStoreLocation Cert:\CurrentUser\Root | Out-Null
Import-Certificate -FilePath $Cer -CertStoreLocation Cert:\CurrentUser\TrustedPublisher | Out-Null
Write-Host "Feito."
