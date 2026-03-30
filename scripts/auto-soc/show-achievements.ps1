param(
    [int]$WindowHours = 168,
    [switch]$Refresh,
    [switch]$SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$opsRoot = "C:\RH\OPS"
$autoRoot = Join-Path $opsRoot "30_Projects\Active\AutoSOC"
$scriptsRoot = Join-Path $opsRoot "50_System\Scripts\Automation\auto-soc"
$outputRoot = Join-Path $autoRoot "Output"
$configRoot = Join-Path $autoRoot "Build\Config"
$queueRoot = Join-Path $autoRoot "Build\Queue"
$processedRoot = Join-Path $queueRoot "Processed"
$logsRoot = Join-Path $opsRoot "50_System\Runs\Logs"

$ledgerPath = Join-Path $outputRoot "ledger.json"
$reconJsonPath = Join-Path $outputRoot "reconciliation_latest.json"
$coverageJsonPath = Join-Path $outputRoot "coverage_latest.json"
$runMetricsPath = Join-Path $outputRoot "run_metrics_latest.json"
$heartbeatPath = Join-Path $outputRoot "heartbeat.json"
$policyPath = Join-Path $configRoot "policy.yaml"
$knownFpPath = Join-Path $configRoot "known_fps.yaml"
$inventoryPath = Join-Path $configRoot "agent_inventory.json"

function Read-JsonOrNull {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 100
    } catch {
        return $null
    }
}

function Get-ObjValue {
    param(
        [object]$Object,
        [string]$Name,
        [object]$Default = $null
    )
    if ($null -eq $Object) { return $Default }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $Default }
    if ($null -eq $prop.Value) { return $Default }
    return $prop.Value
}

function Count-QueueJson {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return 0 }
    return @(
        Get-ChildItem -LiteralPath $Path -File -Filter "*.json" |
        Where-Object { $_.Name -ne ".cursor.json" }
    ).Count
}

if ($Refresh) {
    $lockPath = Join-Path $outputRoot "pipeline.lock.json"
    $waitMaxSeconds = 120
    $waitStepSeconds = 5
    $waited = 0
    while ((Test-Path -LiteralPath $lockPath) -and ($waited -lt $waitMaxSeconds)) {
        Write-Host ("Lock detected, waiting {0}s... ({1}/{2})" -f $waitStepSeconds, $waited, $waitMaxSeconds) -ForegroundColor Yellow
        Start-Sleep -Seconds $waitStepSeconds
        $waited += $waitStepSeconds
    }
    if (Test-Path -LiteralPath $lockPath) {
        Write-Host "Lock still present; running snapshot without refresh run." -ForegroundColor Yellow
    } else {
        $runArgs = @("$scriptsRoot\run-pipeline.py", "--reconcile-only")
        if ($SkipTests) { $runArgs += "--skip-tests" }
        Write-Host "Refreshing state via reconcile-only run..." -ForegroundColor Cyan
        & python @runArgs
    }

    Write-Host "Refreshing coverage snapshot..." -ForegroundColor Cyan
    & python "$scriptsRoot\coverage-check.py" --window-hours $WindowHours | Out-Null
}

$ledger = Read-JsonOrNull -Path $ledgerPath
$recon = Read-JsonOrNull -Path $reconJsonPath
$coverage = Read-JsonOrNull -Path $coverageJsonPath
$runMetrics = Read-JsonOrNull -Path $runMetricsPath
$heartbeat = Read-JsonOrNull -Path $heartbeatPath
$policy = Read-JsonOrNull -Path $policyPath
$knownFp = Read-JsonOrNull -Path $knownFpPath
$inventory = Read-JsonOrNull -Path $inventoryPath

$queueCount = Count-QueueJson -Path $queueRoot
$processedCount = Count-QueueJson -Path $processedRoot

$todayLog = Join-Path $logsRoot ("auto-soc-{0}.log" -f (Get-Date -Format "MM-dd-yyyy"))
$failCount = 0
$retryCount = 0
$doneCount = 0
if (Test-Path -LiteralPath $todayLog) {
    $lines = Get-Content -LiteralPath $todayLog
    $failCount = @($lines | Select-String -SimpleMatch "FAIL=").Count
    $retryCount = @($lines | Select-String -SimpleMatch "RETRY=").Count
    $doneCount = @($lines | Select-String -SimpleMatch "PIPELINE_DONE=TRUE").Count
}

$requiredHosts = 0
$presentHosts = 0
$missingHosts = 0
$presentHostList = @()
$coveragePresent = @()
$coverageMissing = @()
$topSeenTokens = @()
if ($coverage) {
    $requiredHosts = [int](Get-ObjValue $coverage "required_hosts" 0)
    $presentHosts = [int](Get-ObjValue $coverage "present_hosts" 0)
    $missingHosts = [int](Get-ObjValue $coverage "missing_hosts" 0)
    $presentHostList = @(Get-ObjValue $coverage "present_host_list" @())
    $coveragePresent = @(Get-ObjValue $coverage "present" @())
    $coverageMissing = @(Get-ObjValue $coverage "missing" @())
    $topSeenTokens = @(Get-ObjValue $coverage "top_seen_agent_tokens" @())
}

$inventoryCount = 0
if ($inventory -and $inventory.vms) {
    $inventoryCount = @($inventory.vms).Count
}

Write-Host ""
Write-Host "AutoSOC Achievement Snapshot" -ForegroundColor Green
Write-Host "Generated UTC: $(Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mm:ssZ")"
Write-Host ("Window Hours: {0}" -f $WindowHours)
Write-Host ("-" * 72)

Write-Host "Integrity Gates" -ForegroundColor Yellow
$mismatchCount = if ($recon) { [int]$recon.mismatch_count } else { -1 }
Write-Host ("  mismatch_count: {0}" -f $mismatchCount)
Write-Host ("  strict_status:   {0}" -f $(if ($mismatchCount -eq 0) { "PASS" } elseif ($mismatchCount -gt 0) { "FAIL" } else { "UNKNOWN" }))

Write-Host ""
Write-Host "Pipeline Runtime" -ForegroundColor Yellow
if ($runMetrics) {
    Write-Host ("  mode:            {0}" -f (Get-ObjValue $runMetrics "pipeline_mode" "n/a"))
    Write-Host ("  run_seconds:     {0}" -f (Get-ObjValue $runMetrics "run_seconds" "n/a"))
    Write-Host ("  cases_scanned:   {0}" -f (Get-ObjValue $runMetrics "cases_scanned" "n/a"))
    Write-Host ("  cases_processed: {0}" -f (Get-ObjValue $runMetrics "cases_processed" "n/a"))
} else {
    Write-Host "  run_metrics_latest.json not found"
}

Write-Host ""
Write-Host "Case Throughput (Ledger)" -ForegroundColor Yellow
if ($ledger -and $ledger.metrics) {
    Write-Host ("  total_cases:            {0}" -f (Get-ObjValue $ledger.metrics "total_cases" 0))
    Write-Host ("  escalated:              {0}" -f (Get-ObjValue $ledger.metrics "escalated" 0))
    Write-Host ("  auto_closed_benign:     {0}" -f (Get-ObjValue $ledger.metrics "auto_closed_benign" 0))
    Write-Host ("  auto_closed_known_fp:   {0}" -f (Get-ObjValue $ledger.metrics "auto_closed_known_fp" 0))
    Write-Host ("  review:                 {0}" -f (Get-ObjValue $ledger.metrics "review" 0))
} else {
    Write-Host "  ledger.json not found"
}

Write-Host ""
Write-Host "Machine Visibility (Alert Coverage, not VM uptime)" -ForegroundColor Yellow
Write-Host ("  inventory_vms:   {0}" -f $inventoryCount)
Write-Host ("  required_hosts:  {0}" -f $requiredHosts)
Write-Host ("  present_hosts:   {0}" -f $presentHosts)
Write-Host ("  missing_hosts:   {0}" -f $missingHosts)
if ($presentHostList.Count -gt 0) {
    Write-Host ("  present_list:    {0}" -f (($presentHostList -join ", ")))
}

Write-Host ""
Write-Host "Per-Host Recent Hits" -ForegroundColor Yellow
if (($coveragePresent.Count + $coverageMissing.Count) -gt 0) {
    $rows = @()
    foreach ($h in $coveragePresent) {
        $rows += [pscustomobject]@{
            hostname = (Get-ObjValue $h "hostname" "unknown")
            status = "PRESENT"
            recent_hits = [int](Get-ObjValue $h "recent_hits" 0)
            aliases = @((Get-ObjValue $h "aliases" @())) -join ", "
        }
    }
    foreach ($h in $coverageMissing) {
        $rows += [pscustomobject]@{
            hostname = (Get-ObjValue $h "hostname" "unknown")
            status = "MISSING"
            recent_hits = [int](Get-ObjValue $h "recent_hits" 0)
            aliases = @((Get-ObjValue $h "aliases" @())) -join ", "
        }
    }

    $rows |
        Sort-Object @{Expression="status";Descending=$true}, @{Expression="recent_hits";Descending=$true}, hostname |
        Format-Table status, hostname, recent_hits, aliases -AutoSize
} else {
    Write-Host "  no per-host coverage rows found"
}

Write-Host ""
Write-Host "Top Seen Agent Tokens" -ForegroundColor Yellow
if ($topSeenTokens.Count -gt 0) {
    $tokenRows = @()
    foreach ($pair in $topSeenTokens) {
        if ($pair -is [array] -and $pair.Count -ge 2) {
            $tokenRows += [pscustomobject]@{
                token = [string]$pair[0]
                hits = [int]$pair[1]
            }
        }
    }
    $tokenRows | Select-Object -First 12 | Format-Table hits, token -AutoSize
} else {
    Write-Host "  no top_seen_agent_tokens found"
}

Write-Host ""
Write-Host "Policy Controls" -ForegroundColor Yellow
if ($policy) {
    Write-Host ("  always_escalate_rule_ids: {0}" -f @($policy.always_escalate_rule_ids).Count)
    Write-Host ("  always_escalate_groups:   {0}" -f @($policy.always_escalate_groups).Count)
    Write-Host ("  auto_close_rule_ids:      {0}" -f @($policy.auto_close_rule_ids).Count)
    Write-Host ("  review_rule_ids:          {0}" -f @($policy.review_rule_ids).Count)
    Write-Host ("  protected_agents:         {0}" -f @($policy.protected_agents).Count)
    if ($policy.thresholds) {
        Write-Host ("  escalate_min_level:       {0}" -f (Get-ObjValue $policy.thresholds "escalate_min_level" "n/a"))
        Write-Host ("  protected_escalate_level: {0}" -f (Get-ObjValue $policy.thresholds "protected_agent_min_level_escalate" "n/a"))
    }
} else {
    Write-Host "  policy.yaml not readable as JSON-formatted YAML"
}

Write-Host ""
Write-Host "False Positive Controls" -ForegroundColor Yellow
if ($knownFp -and $knownFp.rules) {
    Write-Host ("  known_fp_rules:  {0}" -f @($knownFp.rules).Count)
} else {
    Write-Host "  known_fp_rules:  0"
}

Write-Host ""
Write-Host "Operational Pressure" -ForegroundColor Yellow
Write-Host ("  queue_depth:     {0}" -f $queueCount)
Write-Host ("  processed_total: {0}" -f $processedCount)

Write-Host ""
Write-Host "Pass/Fail Signals (today log)" -ForegroundColor Yellow
Write-Host ("  fail_lines:      {0}" -f $failCount)
Write-Host ("  retry_lines:     {0}" -f $retryCount)
Write-Host ("  done_lines:      {0}" -f $doneCount)
Write-Host ("  log_path:        {0}" -f $todayLog)

Write-Host ""
Write-Host "Key Artifacts" -ForegroundColor Yellow
Write-Host ("  reconciliation:  {0}" -f $reconJsonPath)
Write-Host ("  coverage:        {0}" -f $coverageJsonPath)
Write-Host ("  runtime_metrics: {0}" -f $runMetricsPath)
Write-Host ("  heartbeat:       {0}" -f $heartbeatPath)
Write-Host ("-" * 72)
Write-Host "Tip: use -Refresh to run reconcile-only and update snapshots first." -ForegroundColor Cyan
