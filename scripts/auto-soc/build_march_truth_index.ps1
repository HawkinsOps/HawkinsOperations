param(
    [int]$Year = 2026,
    [int]$Month = 3,
    [string]$RunsRoot = "C:\OPS\Control\Logs\AutoSOC\Runs",
    [string]$MonthIndexRoot = "C:\OPS\Control\Logs\AutoSOC\Indexes\Months",
    [string]$ReportRoot = "C:\OPS\Control\Logs\AutoSOC\Reports",
    [switch]$Execute,
    [switch]$ForceEmpty
)

$ErrorActionPreference = "Stop"
function Assert-CanonicalPath {
    param([string]$PathValue, [string]$Label)
    if ($PathValue -match '^[A-Za-z]:\\(RH\\OPS|Operations)(\\|$)') {
        throw "$Label points to legacy root: $PathValue"
    }
}
$today = Get-Date -Format "MM-dd-yyyy"
Assert-CanonicalPath -PathValue $RunsRoot -Label "RunsRoot"
Assert-CanonicalPath -PathValue $MonthIndexRoot -Label "MonthIndexRoot"
Assert-CanonicalPath -PathValue $ReportRoot -Label "ReportRoot"
$monthName = (Get-Culture).DateTimeFormat.GetMonthName($Month).ToUpperInvariant()
$reportPath = Join-Path -Path $ReportRoot -ChildPath ("{0}_TRUTH_INDEX_{1}.md" -f $monthName, $today)
$latestReportPath = Join-Path -Path $ReportRoot -ChildPath ("{0}_TRUTH_INDEX_LATEST.md" -f $monthName)

$runMonthPath = Join-Path -Path $RunsRoot -ChildPath (Join-Path -Path $Year -ChildPath ("{0:d2}" -f $Month))
$monthIndexPath = Join-Path -Path $MonthIndexRoot -ChildPath (Join-Path -Path $Year -ChildPath ("{0:d2}" -f $Month))

$manifestFiles = @()
if (Test-Path -LiteralPath $runMonthPath) {
    $manifestFiles = @(
        Get-ChildItem -LiteralPath $runMonthPath -Recurse -File -Filter "run_manifest_run_*.json" -ErrorAction SilentlyContinue
    )
}

if ($manifestFiles.Count -eq 0 -and -not $ForceEmpty) {
    $msg = "No run manifests found for month path: $runMonthPath"
    Write-Error ("FAILED: {0}" -f $msg)
    if ($Execute) { throw $msg }
    Write-Warning $msg
    return
}

$runs = @()
$totalFiles = [int64]0
$totalBytes = [int64]0

foreach ($mf in $manifestFiles) {
    $json = Get-Content -LiteralPath $mf.FullName -Raw | ConvertFrom-Json
    $runId = if ($json.run_id) { [string]$json.run_id } else { (Split-Path -Path $mf.DirectoryName -Leaf) }
    $runPath = if ($json.run_path) { [string]$json.run_path } else { $mf.DirectoryName }
    $files = if ($json.file_count) { [int64]$json.file_count } else { 0 }
    $bytes = if ($json.total_size_bytes) { [int64]$json.total_size_bytes } else { 0 }
    $totalFiles += $files
    $totalBytes += $bytes
    $runs += [pscustomobject]@{
        run_id = $runId
        run_path = $runPath
        file_count = $files
        total_size_bytes = $bytes
    }
}

$runs = @($runs | Sort-Object run_id -Descending)
$latestMonthIndex = $null
$latestMonthCsv = $null
if (Test-Path -LiteralPath $monthIndexPath) {
    $latestMonthIndex = @(Get-ChildItem -LiteralPath $monthIndexPath -File -Filter "runs_index_*.md" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1)[0]
    $latestMonthCsv = @(Get-ChildItem -LiteralPath $monthIndexPath -File -Filter "runs_index_*.csv" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1)[0]
}

if ((-not $latestMonthIndex -or -not $latestMonthCsv) -and -not $ForceEmpty) {
    $msg = "Month index missing for $Year-$('{0:d2}' -f $Month); run build_runs_index first."
    Write-Error ("FAILED: {0}" -f $msg)
    if ($Execute) { throw $msg }
    Write-Warning $msg
    return
}

$monthIndexRows = 0
if ($latestMonthCsv) {
    $monthIndexRows = @(
        Import-Csv -LiteralPath $latestMonthCsv.FullName -ErrorAction SilentlyContinue
    ).Count
}
if ($monthIndexRows -eq 0 -and -not $ForceEmpty) {
    $msg = "Month index is empty: $($latestMonthCsv.FullName)"
    Write-Error ("FAILED: {0}" -f $msg)
    if ($Execute) { throw $msg }
    Write-Warning $msg
    return
}

$lines = @()
$lines += ("# {0} Truth Index ({1}-{2:d2})" -f $monthName, $Year, $Month)
$lines += ""
$lines += ("> Derived view only. Immutable source-of-truth is the run stream under Control\\Logs\\AutoSOC\\Runs\\{0}\\{1:d2}\\run_MM-DD-YYYY_HHMMSS." -f $Year, $Month)
$lines += ""
$lines += "- Generated UTC: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$lines += ("- Month run path: {0}" -f $runMonthPath)
$lines += "- Runs found: $($runs.Count)"
$lines += "- Total files (from manifests): $totalFiles"
$lines += "- Total bytes (from manifests): $totalBytes"
$lines += "- Latest month index: $(if ($latestMonthIndex) { $latestMonthIndex.FullName } else { 'not found' })"
$lines += "- Latest month CSV rows: $monthIndexRows"
$lines += ""
$lines += "## Latest Runs"
$lines += ""
$lines += "| run_id | file_count | total_size_bytes | run_path |"
$lines += "|---|---:|---:|---|"
foreach ($r in ($runs | Select-Object -First 20)) {
    $lines += ("| {0} | {1} | {2} | {3} |" -f $r.run_id, $r.file_count, $r.total_size_bytes, $r.run_path)
}

Write-Host ("[INFO] Runs in month: {0}" -f $runs.Count)
Write-Host ("[INFO] Report target: {0}" -f $reportPath)
Write-Host ("[INFO] Latest report pointer: {0}" -f $latestReportPath)

if (-not $Execute) {
    Write-Host "[DRY-RUN] Truth index not written. Re-run with -Execute to write file." -ForegroundColor Yellow
    return
}

New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
$lines | Set-Content -LiteralPath $reportPath -Encoding utf8
Copy-Item -LiteralPath $reportPath -Destination $latestReportPath -Force
Write-Host ("[OK] Wrote truth index: {0}" -f $reportPath) -ForegroundColor Green
Write-Host ("[OK] Updated truth latest pointer: {0}" -f $latestReportPath) -ForegroundColor Green







