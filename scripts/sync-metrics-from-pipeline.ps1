param(
    [string]$OpsRoot = "C:\RH\OPS"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$dateStamp = Get-Date -Format "MM-dd-yyyy"
$logPath = Join-Path $OpsRoot ("50_System\Runs\Logs\sync-metrics-from-pipeline-{0}.log" -f $dateStamp)

function Write-RunLog {
    param([string]$Message)
    $line = "{0} {1}" -f (Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mm:ssZ"), $Message
    New-Item -ItemType Directory -Path (Split-Path -Parent $logPath) -Force | Out-Null
    Add-Content -LiteralPath $logPath -Value $line
    Write-Host $Message
}

Push-Location $repoRoot
try {
    & node ".\scripts\generate-metrics.js"
    if ($LASTEXITCODE -ne 0) {
        throw "generate-metrics.js failed"
    }
} finally {
    Pop-Location
}

Write-RunLog "SYNC_DONE generated data/metrics.json from active pipeline output"
