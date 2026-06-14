param(
    [Parameter(Mandatory=$true)][string]$Region,
    [Parameter(Mandatory=$true)][string]$Org
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SWR = "swr.$Region.myhuaweicloud.com/$Org"
$Out = "k8s-rendered"
if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
New-Item -ItemType Directory -Path $Out | Out-Null

Get-ChildItem k8s -Filter *.yaml | ForEach-Object {
    $text = Get-Content $_.FullName -Raw
    $text = $text.Replace("__SWR__", $SWR)
    Set-Content -Path (Join-Path $Out $_.Name) -Value $text -Encoding UTF8
}

Write-Host "Rendered Kubernetes YAML files to $Out with SWR=$SWR"
Write-Host "Apply later with: kubectl apply -f $Out"
