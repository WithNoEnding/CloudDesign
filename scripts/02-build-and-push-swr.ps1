param(
    [Parameter(Mandatory=$true)][string]$Region,
    [Parameter(Mandatory=$true)][string]$Org,
    [Parameter(Mandatory=$true)][string]$Ak,
    [Parameter(Mandatory=$true)][string]$Token
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SWR = "swr.$Region.myhuaweicloud.com/$Org"
$Registry = "swr.$Region.myhuaweicloud.com"

Write-Host "[1/6] Login to SWR: $Registry"
docker login -u "$Region@$Ak" -p "$Token" $Registry

Write-Host "[2/6] Build backend image"
docker buildx build --provenance=false --load -t backend:v1 ./backend

Write-Host "[3/6] Build frontend image"
docker buildx build --provenance=false --load -t frontend:v1 ./frontend

Write-Host "[4/6] Tag images"
docker tag backend:v1 "$SWR/backend:v1"
docker tag frontend:v1 "$SWR/frontend:v1"

Write-Host "[5/6] Push backend"
docker push "$SWR/backend:v1"

Write-Host "[6/6] Push frontend"
docker push "$SWR/frontend:v1"

Write-Host "Done. SWR=$SWR"
Write-Host "Next: take a screenshot of SWR image list containing backend:v1 and frontend:v1."
