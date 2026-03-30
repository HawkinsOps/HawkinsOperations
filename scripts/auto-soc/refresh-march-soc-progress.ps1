param(
    [int]$Year = 2026,
    [int]$Month = 3,
    [switch]$Execute,
    [switch]$InstallTask,
    [string]$TaskName = "AutoSOC-March-Progress-12h"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$opsRoot = "C:\RH\OPS"
$autoSocRoot = Join-Path $opsRoot "30_Projects\Active\AutoSOC"
$outputRoot = Join-Path $autoSocRoot "Output"
$casesRoot = Join-Path $autoSocRoot "Build\Cases"
$logsRoot = Join-Path $opsRoot "50_System\Runs\Logs"
$reportsRoot = Join-Path $opsRoot "50_System\Runs\Reports"
$scriptsRoot = Join-Path $opsRoot "50_System\Scripts\Automation\auto-soc"
$repoRoot = Join-Path $opsRoot "10_Portfolio\HawkinsOperations"
$reportPath = Join-Path $reportsRoot "AutoSOC_MARCH_SOC_PROGRESS_LOG_LATEST.md"
$stableSummaryPath = Join-Path $reportsRoot "AutoSOC_MARCH_AGENT_SUMMARY.md"

$start = Get-Date -Year $Year -Month $Month -Day 1 -Hour 0 -Minute 0 -Second 0
$end = $start.AddMonths(1)

function Sum-Ints {
    param([int[]]$Values)
    if (-not $Values -or $Values.Count -eq 0) { return 0 }
    return [int](($Values | Measure-Object -Sum).Sum)
}

function Parse-RunRecords {
    param([string[]]$LogPaths)
    $records = New-Object System.Collections.Generic.List[object]
    foreach ($lp in $LogPaths) {
        if (-not (Test-Path -LiteralPath $lp)) { continue }
        $logName = Split-Path -Leaf $lp
        $cur = $null
        foreach ($line in Get-Content -LiteralPath $lp) {
            if ($line -match '^RUN_UTC=(.+)$') {
                if ($cur) { [void]$records.Add([pscustomobject]$cur) }
                $cur = [ordered]@{
                    log = $logName
                    run_utc = $Matches[1]
                    polled = 0
                    triaged = 0
                    mismatch_count = -1
                    fail = ""
                }
                continue
            }
            if ($null -eq $cur) { continue }
            if ($line -match '^POLLED=(\d+)$') { $cur.polled = [int]$Matches[1]; continue }
            if ($line -match '^TRIAGED=(\d+)$') { $cur.triaged = [int]$Matches[1]; continue }
            if ($line -match '^MISMATCH_COUNT=(\d+)$') { $cur.mismatch_count = [int]$Matches[1]; continue }
            if ($line -match '^FAIL=(.+)$') { $cur.fail = $Matches[1]; continue }
        }
        if ($cur) { [void]$records.Add([pscustomobject]$cur) }
    }
    return @($records.ToArray())
}

function Get-LogSummary {
    param([System.IO.FileInfo[]]$Logs)
    $rows = @()
    foreach ($l in $Logs) {
        $text = Get-Content -LiteralPath $l.FullName
        $polledVals = $text | Select-String '^POLLED=' | ForEach-Object { [int](($_.Line -split '=')[1]) }
        $triagedVals = $text | Select-String '^TRIAGED=' | ForEach-Object { [int](($_.Line -split '=')[1]) }
        $mismatchVals = $text | Select-String '^MISMATCH_COUNT=' | ForEach-Object { [int](($_.Line -split '=')[1]) }
        $rows += [pscustomobject]@{
            Log = $l.Name
            SizeBytes = $l.Length
            Runs = ($text | Select-String '^RUN_UTC=').Count
            PolledSum = Sum-Ints -Values $polledVals
            TriagedSum = Sum-Ints -Values $triagedVals
            MismatchSum = Sum-Ints -Values $mismatchVals
        }
    }
    return $rows
}

if (-not (Test-Path -LiteralPath $reportsRoot)) {
    throw "Reports root not found: $reportsRoot"
}

$logs = Get-ChildItem -LiteralPath $logsRoot -Filter ("auto-soc-{0}-*.log" -f $start.ToString("MM")) -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $start -and $_.LastWriteTime -lt $end } |
    Sort-Object Name
$logPaths = @($logs | ForEach-Object { $_.FullName })
$runRecords = Parse-RunRecords -LogPaths $logPaths

$monthRuns = @($runRecords | Where-Object {
    try {
        $dt = [datetime]$_.run_utc
        $dt -ge $start.ToUniversalTime() -and $dt -lt $end.ToUniversalTime()
    } catch {
        $false
    }
})

$bins = @()
for ($t = $start.ToUniversalTime(); $t -lt $end.ToUniversalTime(); $t = $t.AddHours(12)) {
    $bEnd = $t.AddHours(12)
    $slice = @($monthRuns | Where-Object {
        $rt = [datetime]$_.run_utc
        $rt -ge $t -and $rt -lt $bEnd
    })
    $bins += [pscustomobject]@{
        WindowUtc = ("{0} -> {1}" -f $t.ToString("MM-dd HH:mm"), $bEnd.ToString("MM-dd HH:mm"))
        Runs = $slice.Count
        PolledSum = Sum-Ints -Values @($slice | ForEach-Object { [int]$_.polled })
        TriagedSum = Sum-Ints -Values @($slice | ForEach-Object { [int]$_.triaged })
        Fails = @($slice | Where-Object { $_.fail }).Count
        MismatchNonzero = @($slice | Where-Object { $_.mismatch_count -gt 0 }).Count
    }
}

$heartbeatPath = Join-Path $outputRoot "heartbeat_history.jsonl"
$hbRows = @()
if (Test-Path -LiteralPath $heartbeatPath) {
    $hbRows = Get-Content -LiteralPath $heartbeatPath | Where-Object { $_.Trim() } | ForEach-Object {
        try { $_ | ConvertFrom-Json } catch { $null }
    } | Where-Object { $_ }
}
$hbMonth = @($hbRows | Where-Object {
    try {
        $dt = [datetime]$_.start_utc
        $dt -ge $start.ToUniversalTime() -and $dt -lt $end.ToUniversalTime()
    } catch {
        $false
    }
})
$hbSuccess = @($hbMonth | Where-Object { $_.status -eq "SUCCESS" }).Count
$hbFailed = @($hbMonth | Where-Object { $_.status -ne "SUCCESS" }).Count
$hbTotal = $hbMonth.Count
$hbPassRate = if ($hbTotal -gt 0) { [math]::Round(($hbSuccess * 100.0) / $hbTotal, 2) } else { 0.0 }
$firstRunUtc = if ($monthRuns.Count -gt 0) { ([datetime]($monthRuns | Sort-Object run_utc | Select-Object -First 1 -ExpandProperty run_utc)).ToString("yyyy-MM-ddTHH:mm:ssZ") } else { "" }
$lastRunUtc = if ($monthRuns.Count -gt 0) { ([datetime]($monthRuns | Sort-Object run_utc | Select-Object -Last 1 -ExpandProperty run_utc)).ToString("yyyy-MM-ddTHH:mm:ssZ") } else { "" }

$ledgerPath = Join-Path $outputRoot "ledger.json"
$coveragePath = Join-Path $outputRoot "coverage_latest.md"
$coverageDiagPath = Join-Path $outputRoot "coverage_diagnose_latest.md"

$ledger = $null
if (Test-Path -LiteralPath $ledgerPath) {
    $ledger = Get-Content -LiteralPath $ledgerPath -Raw | ConvertFrom-Json
}

$caseCount = if (Test-Path -LiteralPath $casesRoot) { (Get-ChildItem -LiteralPath $casesRoot -Directory | Measure-Object).Count } else { 0 }
$monthCaseCount = if (Test-Path -LiteralPath $casesRoot) {
    (Get-ChildItem -LiteralPath $casesRoot -Directory | Where-Object { $_.Name -like ("{0}-*" -f $start.ToString("yyyy-MM")) } | Measure-Object).Count
} else { 0 }

$outFiles = Get-ChildItem -LiteralPath $outputRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $start -and $_.LastWriteTime -lt $end }
$outCount = ($outFiles | Measure-Object).Count
$outBytes = [int64](($outFiles | Measure-Object Length -Sum).Sum)

$reports = Get-ChildItem -LiteralPath $reportsRoot -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $start -and $_.LastWriteTime -lt $end -and $_.Name -match 'AutoSOC|autosoc|SOC' }
$reportCount = ($reports | Measure-Object).Count

$repoCommitCount = 0
$repoModified = 0
$repoUntracked = 0
$repoIncidentUntracked = 0
if (Test-Path -LiteralPath $repoRoot) {
    $sinceArg = "--since=$($start.ToString('yyyy-MM-dd'))"
    $repoCommitCount = [int](git -C $repoRoot log $sinceArg --oneline 2>$null | Measure-Object | Select-Object -ExpandProperty Count)
    $status = @(git -C $repoRoot status --short)
    $repoModified = @($status | Where-Object { $_ -match '^ M ' }).Count
    $repoUntracked = @($status | Where-Object { $_ -match '^\?\? ' }).Count
    $repoIncidentUntracked = @($status | Where-Object { $_ -match '^\?\? incident-response/incidents/2026/' }).Count
}

$logSummary = Get-LogSummary -Logs $logs

$covJsonPath = Join-Path $outputRoot "coverage_latest.json"
$cov = $null
if (Test-Path -LiteralPath $covJsonPath) {
    $cov = Get-Content -LiteralPath $covJsonPath -Raw | ConvertFrom-Json
}
$covRequired = if ($cov) { [int]$cov.required_hosts } else { 0 }
$covPresent = if ($cov) { [int]$cov.present_hosts } else { 0 }
$covMissing = if ($cov) { [int]$cov.missing_hosts } else { 0 }
$covPct = if ($cov) { [double]$cov.required_coverage_percent } else { 0.0 }
$covMissingList = if ($cov -and $cov.missing) { (@($cov.missing | ForEach-Object { $_.hostname }) -join ", ") } else { "" }
$reconLatestPath = Join-Path $outputRoot "reconciliation_latest.json"
$reconMismatchLatest = "n/a"
if (Test-Path -LiteralPath $reconLatestPath) {
    try {
        $reconMismatchLatest = [string]((Get-Content -LiteralPath $reconLatestPath -Raw | ConvertFrom-Json).mismatch_count)
    } catch {
        $reconMismatchLatest = "parse_error"
    }
}

$lines = @()
$lines += "# AutoSOC Agent Summary (March 2026)"
$lines += ""
$lines += ("Generated: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
$lines += ("Scope: {0} SOC build + run + repo progress" -f $start.ToString("yyyy-MM"))
$lines += ""
$lines += "## Mission Status"
$lines += "- Objective: design and stand up an unattended AutoSOC loop with auditable outputs."
$lines += "- Build stood up: 2026-03-02 (first March run observed)."
$lines += ("- Active run window observed: {0} -> {1}" -f $firstRunUtc, $lastRunUtc)
$lines += "- Current state: running and producing artifacts; coverage closure remains the main blocker."
$lines += ""
$lines += "## Architecture Executed"
$lines += "- Ingest: Wazuh alert polling with cursor/realtime modes."
$lines += "- Triage: AUTO_CLOSE_BENIGN / AUTO_CLOSE_KNOWN_FP / ESCALATE policy decisions."
$lines += "- Hard gates: redaction + reconciliation strict."
$lines += "- Output: heartbeat, run metrics, coverage, reconciliation, quality/tuning artifacts."
$lines += "- Promotion model: allowlisted publish bundle flow."
$lines += ""
$lines += "## Runtime Scoreboard"
if ($ledger) {
    $lines += ("- Cases generated total: {0}" -f [int]$ledger.metrics.total_cases)
    $lines += ("- Auto-closed benign: {0}" -f [int]$ledger.metrics.auto_closed_benign)
    $lines += ("- Auto-closed known FP: {0}" -f [int]$ledger.metrics.auto_closed_known_fp)
    $lines += ("- Escalated: {0}" -f [int]$ledger.metrics.escalated)
}
$lines += ("- March run records parsed from logs: {0}" -f $monthRuns.Count)
$lines += ("- March polled sum: {0}" -f (Sum-Ints -Values @($monthRuns | ForEach-Object { [int]$_.polled })))
$lines += ("- March triaged sum: {0}" -f (Sum-Ints -Values @($monthRuns | ForEach-Object { [int]$_.triaged })))
$lines += ("- Instrumented pass rate (heartbeat status): {0}% ({1}/{2} success)" -f $hbPassRate, $hbSuccess, $hbTotal)
$lines += ("- Reconciliation strict mismatch (latest): {0}" -f $reconMismatchLatest)
$lines += ("- Required coverage (latest): {0}% ({1}/{2})" -f $covPct, $covPresent, $covRequired)
if ($covMissingList) {
    $lines += ("- Required hosts missing now: {0}" -f $covMissingList)
}
$lines += ""
$lines += "## Files Generated"
$lines += ("- Case directories total: {0}" -f $caseCount)
$lines += ("- March case directories: {0}" -f $monthCaseCount)
$lines += ("- Output files in March: {0}" -f $outCount)
$lines += ("- Output bytes in March: {0}" -f $outBytes)
$lines += ("- SOC report files in March (Runs\\Reports): {0}" -f $reportCount)
$lines += ""
$lines += "## 12-Hour Markers (UTC)"
foreach ($b in ($bins | Where-Object { $_.Runs -gt 0 })) {
    $lines += ("- {0}: runs={1}, polled={2}, triaged={3}, fails={4}, mismatch_nonzero={5}" -f $b.WindowUtc, $b.Runs, $b.PolledSum, $b.TriagedSum, $b.Fails, $b.MismatchNonzero)
}
$lines += ""
$lines += "## Repo Signal"
$lines += ("- March commits (portfolio repo): {0}" -f $repoCommitCount)
$lines += ("- Working tree modified: {0}" -f $repoModified)
$lines += ("- Working tree untracked: {0}" -f $repoUntracked)
$lines += ("- Untracked incident dirs: {0}" -f $repoIncidentUntracked)
$lines += ""
$lines += "## Source Paths"
$lines += ("- AutoSOC: {0}" -f $autoSocRoot)
$lines += ("- Output: {0}" -f $outputRoot)
$lines += ("- Scripts: {0}" -f $scriptsRoot)
$lines += ("- Logs: {0}" -f $logsRoot)
$lines += ("- Reports: {0}" -f $reportsRoot)
$lines += ("- Portfolio repo: {0}" -f $repoRoot)
$lines += ""
$lines += "## Log Summary"
foreach ($r in $logSummary) {
    $lines += ("- {0} size={1} runs={2} polled_sum={3} triaged_sum={4} mismatch_sum={5}" -f $r.Log, $r.SizeBytes, $r.Runs, $r.PolledSum, $r.TriagedSum, $r.MismatchSum)
}
$lines += ""
$lines += "## Current Coverage Artifacts"
$lines += ("- {0}" -f $coveragePath)
$lines += ("- {0}" -f $coverageDiagPath)

if (-not $Execute) {
    Write-Host ("DRY_RUN=TRUE")
    Write-Host ("REPORT_TARGET={0}" -f $reportPath)
    Write-Host ("TASK_INSTALL_REQUESTED={0}" -f [bool]$InstallTask)
    if ($InstallTask) {
        Write-Host "TASK_NOTE=Run again with -Execute -InstallTask to register scheduler."
    }
    exit 0
}

$content = $lines -join "`n"
$stamp = Get-Date -Format "yyyyMMddTHHmmss"
$historyPath = Join-Path $reportsRoot ("AutoSOC_MARCH_AGENT_SUMMARY_{0}.md" -f $stamp)
Set-Content -LiteralPath $historyPath -Value $content -Encoding UTF8
Write-Host ("HISTORY_WRITTEN={0}" -f $historyPath)

foreach ($target in @($reportPath, $stableSummaryPath)) {
    $written = $false
    for ($i = 1; $i -le 8; $i++) {
        try {
            Set-Content -LiteralPath $target -Value $content -Encoding UTF8
            $written = $true
            break
        } catch {
            Start-Sleep -Milliseconds (250 * $i)
        }
    }
    if ($written) {
        Write-Host ("STABLE_WRITTEN={0}" -f $target)
    } else {
        Write-Host ("STABLE_WRITE_SKIPPED_LOCKED={0}" -f $target)
    }
}

if ($InstallTask) {
    $scriptPath = $MyInvocation.MyCommand.Path
    $taskCmd = "pwsh -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -Year $Year -Month $Month -Execute"
    schtasks /Create /SC HOURLY /MO 12 /TN $TaskName /TR $taskCmd /F | Out-Null
    Write-Host ("TASK_REGISTERED={0}" -f $TaskName)
    Write-Host ("TASK_COMMAND={0}" -f $taskCmd)
}
