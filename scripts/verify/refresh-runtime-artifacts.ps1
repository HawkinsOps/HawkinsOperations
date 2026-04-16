param(
  [switch]$SkipDriftScan,
  [switch]$SkipRuntimeContract
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Step {
  param(
    [Parameter(Mandatory)][string]$Label,
    [Parameter(Mandatory)][scriptblock]$Action
  )

  Write-Host "==> $Label" -ForegroundColor Cyan
  & $Action
  if ($LASTEXITCODE -ne 0) {
    throw "Step failed: $Label"
  }
}

Invoke-Step -Label "Generate metrics artifacts" -Action {
  node .\scripts\generate-metrics.js
}

Invoke-Step -Label "Generate site data artifacts" -Action {
  node .\scripts\generate-site-data.js
}

if (-not $SkipRuntimeContract) {
  Invoke-Step -Label "Run runtime contract check" -Action {
    node .\scripts\verify\site-runtime-contract.js
  }
}

if (-not $SkipDriftScan) {
  Invoke-Step -Label "Run drift scan" -Action {
    python .\scripts\drift_scan.py
  }
}

Write-Host "`nArtifact refresh workflow completed successfully." -ForegroundColor Green
Write-Host "Suggested review command:" -ForegroundColor DarkGray
Write-Host "  git status --short" -ForegroundColor DarkGray
