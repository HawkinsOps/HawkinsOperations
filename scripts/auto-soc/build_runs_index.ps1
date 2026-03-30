param(
    [string]$RunsRoot = "C:\OPS\Control\Logs\AutoSOC\Runs",
    [string]$GlobalIndexRoot = "C:\OPS\Control\Logs\AutoSOC\Indexes\Global",
    [string]$MonthIndexRoot = "C:\OPS\Control\Logs\AutoSOC\Indexes\Months",
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
Assert-CanonicalPath -PathValue $GlobalIndexRoot -Label "GlobalIndexRoot"
Assert-CanonicalPath -PathValue $MonthIndexRoot -Label "MonthIndexRoot"
function Parse-RunId {
    param([string]$RunId)
    if ($RunId -match "^run_(\d{2})-(\d{2})-(\d{4})_(\d{6})$") {
        $mm = $Matches[1]
        $dd = $Matches[2]
        $yyyy = $Matches[3]
        $hhmmss = $Matches[4]
        $dt = [datetime]::ParseExact("$yyyy-$mm-$dd $hhmmss", "yyyy-MM-dd HHmmss", $null)
        return [pscustomobject]@{
            Year  = $yyyy
            Month = $mm
            Date  = "$mm-$dd-$yyyy"
            Utc   = $dt.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
    }
    return $null
}

if (-not (Test-Path -LiteralPath $RunsRoot)) {
    Write-Warning "Runs root not found: $RunsRoot"
    return
}

$manifestFiles = @(
    Get-ChildItem -LiteralPath $RunsRoot -Recurse -File -Filter "run_manifest_run_*.json" -ErrorAction SilentlyContinue
)
$rows = @()

if ($manifestFiles.Count -eq 0 -and -not $ForceEmpty) {
    $msg = "0 manifests found under $RunsRoot; refusing to write indexes."
    Write-Error ("FAILED: {0}" -f $msg)
    if ($Execute) { throw $msg }
    Write-Warning $msg
    return
}

foreach ($mf in $manifestFiles) {
    $json = Get-Content -LiteralPath $mf.FullName -Raw | ConvertFrom-Json
    $runId = if ($json.run_id) { [string]$json.run_id } else { (Split-Path -Path $mf.DirectoryName -Leaf) }
    $parsed = Parse-RunId -RunId $runId
    $runPath = if ($json.run_path) { [string]$json.run_path } else { $mf.DirectoryName }
    $fileCount = if ($json.file_count) { [int64]$json.file_count } else { 0 }
    $bytes = if ($json.total_size_bytes) { [int64]$json.total_size_bytes } else { 0 }

    $rows += [pscustomobject]@{
        run_id           = $runId
        run_utc          = if ($parsed) { $parsed.Utc } else { "" }
        run_date         = if ($parsed) { $parsed.Date } else { "" }
        year             = if ($parsed) { $parsed.Year } else { "" }
        month            = if ($parsed) { $parsed.Month } else { "" }
        run_path         = $runPath
        manifest_path    = $mf.FullName
        file_count       = $fileCount
        total_size_bytes = $bytes
    }
}

$rows = @($rows | Sort-Object run_utc, run_id -Descending)

if ($rows.Count -eq 0 -and -not $ForceEmpty) {
    $msg = "0 index rows resolved from discovered manifests; refusing to write indexes."
    Write-Error ("FAILED: {0}" -f $msg)
    if ($Execute) { throw $msg }
    Write-Warning $msg
    return
}

$globalCsv = Join-Path -Path $GlobalIndexRoot -ChildPath ("runs_index_global_{0}.csv" -f $today)
$globalMd = Join-Path -Path $GlobalIndexRoot -ChildPath ("runs_index_global_{0}.md" -f $today)
$globalJsonl = Join-Path -Path $GlobalIndexRoot -ChildPath ("output_catalog_global_{0}.jsonl" -f $today)
$globalCsvLatest = Join-Path -Path $GlobalIndexRoot -ChildPath "runs_index_global_LATEST.csv"
$globalMdLatest = Join-Path -Path $GlobalIndexRoot -ChildPath "runs_index_global_LATEST.md"
$globalJsonlLatest = Join-Path -Path $GlobalIndexRoot -ChildPath "output_catalog_global_LATEST.jsonl"
$globalJsonlCompat = Join-Path -Path $GlobalIndexRoot -ChildPath "output_catalog_global_latest.jsonl"

Write-Host ("[INFO] Manifests discovered: {0}" -f $manifestFiles.Count)
Write-Host ("[INFO] Global CSV: {0}" -f $globalCsv)
Write-Host ("[INFO] Global MD: {0}" -f $globalMd)
Write-Host ("[INFO] Global JSONL: {0}" -f $globalJsonl)
Write-Host ("[INFO] Global CSV latest pointer: {0}" -f $globalCsvLatest)
Write-Host ("[INFO] Global MD latest pointer: {0}" -f $globalMdLatest)
Write-Host ("[INFO] Global JSONL latest pointer: {0}" -f $globalJsonlLatest)

if (-not $Execute) {
    Write-Host "[DRY-RUN] No index files written. Re-run with -Execute to write outputs." -ForegroundColor Yellow
    return
}

New-Item -ItemType Directory -Path $GlobalIndexRoot -Force | Out-Null
New-Item -ItemType Directory -Path $MonthIndexRoot -Force | Out-Null

$rows | Export-Csv -LiteralPath $globalCsv -NoTypeInformation -Encoding utf8

$mdLines = @()
$mdLines += "# Global Runs Index ($today)"
$mdLines += ""
$mdLines += "- Generated UTC: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
$mdLines += "- Runs indexed: $($rows.Count)"
$mdLines += ""
$mdLines += "| run_id | run_utc | file_count | total_size_bytes | run_path |"
$mdLines += "|---|---|---:|---:|---|"
foreach ($r in $rows) {
    $mdLines += ("| {0} | {1} | {2} | {3} | {4} |" -f $r.run_id, $r.run_utc, $r.file_count, $r.total_size_bytes, $r.run_path)
}
$mdLines | Set-Content -LiteralPath $globalMd -Encoding utf8

$jsonlLines = foreach ($r in $rows) { $r | ConvertTo-Json -Compress }
$jsonlLines | Set-Content -LiteralPath $globalJsonl -Encoding utf8
$jsonlLines | Set-Content -LiteralPath $globalJsonlLatest -Encoding utf8
$jsonlLines | Set-Content -LiteralPath $globalJsonlCompat -Encoding utf8

Copy-Item -LiteralPath $globalCsv -Destination $globalCsvLatest -Force
Copy-Item -LiteralPath $globalMd -Destination $globalMdLatest -Force

$monthGroups = $rows | Group-Object { "{0}-{1}" -f $_.year, $_.month }
foreach ($g in $monthGroups) {
    if ([string]::IsNullOrWhiteSpace($g.Name) -or $g.Name -eq "-") { continue }

    $parts = $g.Name.Split("-")
    $yyyy = $parts[0]
    $mm = $parts[1]
    $monthDir = Join-Path -Path $MonthIndexRoot -ChildPath (Join-Path -Path $yyyy -ChildPath $mm)
    New-Item -ItemType Directory -Path $monthDir -Force | Out-Null

    $monthCsv = Join-Path -Path $monthDir -ChildPath ("runs_index_{0}.csv" -f $today)
    $monthMd = Join-Path -Path $monthDir -ChildPath ("runs_index_{0}.md" -f $today)
    $monthCsvLatest = Join-Path -Path $monthDir -ChildPath "runs_index_LATEST.csv"
    $monthMdLatest = Join-Path -Path $monthDir -ChildPath "runs_index_LATEST.md"

    $g.Group | Export-Csv -LiteralPath $monthCsv -NoTypeInformation -Encoding utf8

    $monthMdLines = @()
    $monthMdLines += "# Month Runs Index ($yyyy-$mm)"
    $monthMdLines += ""
    $monthMdLines += "- Generated UTC: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    $monthMdLines += "- Runs indexed: $($g.Count)"
    $monthMdLines += ""
    $monthMdLines += "| run_id | run_utc | file_count | total_size_bytes | run_path |"
    $monthMdLines += "|---|---|---:|---:|---|"
    foreach ($r in ($g.Group | Sort-Object run_utc -Descending)) {
        $monthMdLines += ("| {0} | {1} | {2} | {3} | {4} |" -f $r.run_id, $r.run_utc, $r.file_count, $r.total_size_bytes, $r.run_path)
    }
    $monthMdLines | Set-Content -LiteralPath $monthMd -Encoding utf8
    Copy-Item -LiteralPath $monthCsv -Destination $monthCsvLatest -Force
    Copy-Item -LiteralPath $monthMd -Destination $monthMdLatest -Force
}

Write-Host "[OK] Index files written." -ForegroundColor Green






