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

docker login -u "$Region@$Ak" -p "$Token" $Registry

docker buildx build --provenance=false --load `
  --build-arg BASE_IMAGE="$SWR/pyspark:v9" `
  -t spark-analysis:v1 ./spark

docker tag spark-analysis:v1 "$SWR/spark-analysis:v1"
docker push "$SWR/spark-analysis:v1"
Write-Host "Done. Spark image: $SWR/spark-analysis:v1"
