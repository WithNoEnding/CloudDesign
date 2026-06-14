Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[1/2] Building and starting local compose services..."
docker compose up --build
