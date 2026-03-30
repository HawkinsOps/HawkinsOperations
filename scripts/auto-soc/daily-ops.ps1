param(
    [switch]$Refresh,
    [switch]$SkipTests,
    [switch]$ExecutePromotion,
    [int]$RealtimeWindowMinutes = 60,
    [int]$FreshnessP95MaxSeconds = 3600,
    [int]$FreshnessOldestMaxSeconds = 7200,
    [int]$CoverageWindowHours = 168,
    [int]$PolicyMaxFiles = 1000,
    [int]$PolicyMinRecommendCount = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$opsRoot = "C:\RH\OPS"
$scriptRoot = Join-Path $opsRoot "50_System\Scripts\Automation\auto-soc"
$outputRoot = Join-Path $opsRoot "30_Projects\Active\AutoSOC\Output"

$heartbeatPath = Join-Path $outputRoot "heartbeat.json"
$coveragePath = Join-Path $outputRoot "coverage_latest.json"
$reconPath = Join-Path $outputRoot "reconciliation_latest.json"
$promotionPath = Join-Path $outputRoot "promotion_latest.json"

function Read-JsonOrNull {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 100
    } catch {
        return $null
    }
}

function Run-Step {
    param(
        [string]$Name,
        [scriptblock]$Block
    )
    Write-Host "`n[$Name]" -ForegroundColor Cyan
    & $Block
}

if ($Refresh) {
    Run-Step -Name "Pipeline Live Run" -Block {
        $args = @(
            "$scriptRoot\run-pipeline.py",
            "--mode", "realtime",
            "--realtime-window-minutes", "$RealtimeWindowMinutes",
            "--freshness-p95-max-seconds", "$FreshnessP95MaxSeconds",
            "--freshness-oldest-max-seconds", "$FreshnessOldestMaxSeconds"
        )
        if ($SkipTests) { $args += "--skip-tests" }
        & python @args
    }
} else {
    Run-Step -Name "Pipeline Reconcile-Only Refresh" -Block {
        $args = @(
            "$scriptRoot\run-pipeline.py",
            "--reconcile-only",
            "--freshness-p95-max-seconds", "$FreshnessP95MaxSeconds",
            "--freshness-oldest-max-seconds", "$FreshnessOldestMaxSeconds"
        )
        if ($SkipTests) { $args += "--skip-tests" }
        & python @args
    }
}

Run-Step -Name "Coverage Snapshot" -Block {
    & python "$scriptRoot\coverage-check.py" --window-hours $CoverageWindowHours
}

Run-Step -Name "Escalation Quality" -Block {
    & python "$scriptRoot\escalation-quality.py"
}

Run-Step -Name "Policy Audit + Weekly Delta" -Block {
    & python "$scriptRoot\policy-audit.py" --max-files $PolicyMaxFiles --min-recommend-count $PolicyMinRecommendCount
    & python "$scriptRoot\policy-audit-delta.py"
}

Run-Step -Name "Heartbeat Trend" -Block {
    & python "$scriptRoot\heartbeat-trend.py"
}

Run-Step -Name "Incident Taxonomy" -Block {
    & python "$scriptRoot\incident-taxonomy.py" --max-files 5000
}

Run-Step -Name "Passfile ACL Evidence" -Block {
    & pwsh -NoProfile -File "$scriptRoot\capture-passfile-acl.ps1"
}

Run-Step -Name "Export Publish Bundle" -Block {
    & python "$scriptRoot\export-publish-bundle.py"
}

Run-Step -Name "Promotion Plan" -Block {
    if ($ExecutePromotion) {
        & python "$scriptRoot\promote-publish-bundle.py" --execute
    } else {
        & python "$scriptRoot\promote-publish-bundle.py"
    }
}

$heartbeat = Read-JsonOrNull -Path $heartbeatPath
$coverage = Read-JsonOrNull -Path $coveragePath
$recon = Read-JsonOrNull -Path $reconPath
$promotion = Read-JsonOrNull -Path $promotionPath

$status = if ($heartbeat) { [string]$heartbeat.status } else { "UNKNOWN" }
$reconStatus = if ($recon) { if ([int]$recon.mismatch_count -eq 0) { "PASS" } else { "FAIL" } } else { "UNKNOWN" }
$coverageStatus = if ($coverage) { if ([int]$coverage.missing_hosts -eq 0) { "PASS" } else { "FAIL" } } else { "UNKNOWN" }
$freshnessStatus = if ($heartbeat -and $heartbeat.freshness) { [string]$heartbeat.freshness.status } else { "UNKNOWN" }
$promotionPlanned = if ($promotion) { [int]$promotion.planned_count } else { 0 }
$promotionCopied = if ($promotion) { [int]$promotion.copied_count } else { 0 }

$overall = "PASS"
if ($status -ne "SUCCESS") { $overall = "FAIL" }
if ($reconStatus -ne "PASS") { $overall = "FAIL" }
if ($coverageStatus -ne "PASS") { $overall = "WARN" }
if ($freshnessStatus -eq "FAIL") { $overall = "WARN" }

Write-Host "`n================ AutoSOC Daily Ops Board ================" -ForegroundColor Green
Write-Host ("Run status:           {0}" -f $status)
Write-Host ("Reconciliation:       {0}" -f $reconStatus)
Write-Host ("Coverage:             {0}" -f $coverageStatus)
Write-Host ("Freshness:            {0}" -f $freshnessStatus)
if ($coverage) {
    Write-Host ("Coverage hosts:       present={0} missing={1}" -f $coverage.present_hosts, $coverage.missing_hosts)
}
if ($heartbeat -and $heartbeat.poller) {
    Write-Host ("Poller source/mode:   {0} / {1}" -f $heartbeat.poller.secret_source, $heartbeat.poller.mode)
    Write-Host ("Poller delays (p95):  {0}s" -f $heartbeat.poller.p95_delay_seconds)
}
Write-Host ("Promotion planned:    {0}" -f $promotionPlanned)
Write-Host ("Promotion copied:     {0}" -f $promotionCopied)
Write-Host ("OVERALL:              {0}" -f $overall)
Write-Host "=========================================================" -ForegroundColor Green
