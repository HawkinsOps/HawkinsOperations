param(
    [string]$RunPath = "",
    [string]$RunsRoot = "C:\RH\OPS\50_System\Runs\AutoSOC",
    [string]$GlobalIndexRoot = "C:\RH\OPS\50_System\Runs\indexes\global",
    [string]$MonthIndexRoot = "C:\RH\OPS\50_System\Runs\indexes\months",
    [string]$ReportRoot = "C:\RH\OPS\50_System\Runs\Reports",
    [string]$OperatorOutputPath = "C:\RH\OPS\30_Projects\Active\AutoSOC\Output",
    [int]$Year = 0,
    [int]$Month = 0,
    [int]$OperatorWarnFiles = 150,
    [int]$OperatorMaxFiles = 200,
    [switch]$Execute,
    [switch]$ForceEmpty
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$sw = [System.Diagnostics.Stopwatch]::StartNew()

$scriptRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$buildManifestScript = Join-Path $scriptRoot "build_run_manifest.ps1"
$buildIndexScript = Join-Path $scriptRoot "build_runs_index.ps1"
$buildTruthScript = Join-Path $scriptRoot "build_march_truth_index.ps1"
$validateScript = Join-Path $scriptRoot "validate_runs_contract.ps1"
$logRoot = "C:\RH\OPS\50_System\Runs\Logs"
$dateTag = Get-Date -Format "MM-dd-yyyy"
$runLog = Join-Path $logRoot ("autosoc-runs-contract-{0}.log" -f $dateTag)

New-Item -ItemType Directory -Path $logRoot -Force | Out-Null

function Write-RunLog {
    param([string]$Message)
    $line = "{0} {1}" -f ((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")), $Message
    Write-Host $line
    Add-Content -LiteralPath $runLog -Value $line
}

function Resolve-LatestRunPath {
    param([string]$Root)
    if (-not (Test-Path -LiteralPath $Root)) {
        throw "Runs root not found: $Root"
    }
    $latest = Get-ChildItem -LiteralPath $Root -Recurse -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "^run_\d{2}-\d{2}-\d{4}_\d{6}$" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) {
        throw "No run folders found under $Root"
    }
    return $latest.FullName
}

function Resolve-YearMonth {
    param([string]$PathValue, [int]$InYear, [int]$InMonth)
    if ($InYear -gt 0 -and $InMonth -gt 0) {
        return [pscustomobject]@{ Year = $InYear; Month = $InMonth }
    }
    if ($PathValue -match "\\Runs\\AutoSOC\\(\d{4})\\(\d{2})\\run_\d{2}-\d{2}-\d{4}_\d{6}$") {
        return [pscustomobject]@{ Year = [int]$Matches[1]; Month = [int]$Matches[2] }
    }
    $now = Get-Date
    return [pscustomobject]@{ Year = $now.Year; Month = $now.Month }
}

function Write-OperatorCardLatest {
    param(
        [string]$Path,
        [int]$YearValue,
        [int]$MonthValue,
        [string]$RunsRootValue,
        [string]$GlobalIndexRootValue,
        [string]$MonthIndexRootValue,
        [string]$ReportRootValue
    )
    $globalMd = Join-Path $GlobalIndexRootValue "runs_index_global_LATEST.md"
    $globalJsonl = Join-Path $GlobalIndexRootValue "output_catalog_global_LATEST.jsonl"
    $monthMd = Join-Path (Join-Path $MonthIndexRootValue (Join-Path $YearValue ("{0:d2}" -f $MonthValue))) "runs_index_LATEST.md"
    $monthTruth = Join-Path $ReportRootValue "MARCH_TRUTH_INDEX_LATEST.md"
    $lines = @(
        "# AutoSOC Operator Card (LATEST)",
        "",
        "- Generated UTC: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))",
        "- Read this file first for current run truth surfaces.",
        "",
        "## Primary Truth Surfaces",
        "",
        "- MARCH_TRUTH_INDEX_LATEST.md: $monthTruth",
        "- runs_index_global_LATEST.md: $globalMd",
        "- output_catalog_global_LATEST.jsonl: $globalJsonl",
        "- runs_index_month_LATEST.md: $monthMd",
        "",
        "## Run Stream Root",
        "",
        "- $RunsRootValue"
    )
    $lines | Set-Content -LiteralPath $Path -Encoding utf8
}

if ([string]::IsNullOrWhiteSpace($RunPath)) {
    $RunPath = Resolve-LatestRunPath -Root $RunsRoot
}
if (-not (Test-Path -LiteralPath $RunPath)) {
    throw "Run path not found: $RunPath"
}

$ym = Resolve-YearMonth -PathValue $RunPath -InYear $Year -InMonth $Month
$Year = $ym.Year
$Month = $ym.Month

Write-RunLog "START mode=$(if ($Execute) { 'EXECUTE' } else { 'DRY-RUN' }) run_path=$RunPath year=$Year month=$Month force_empty=$($ForceEmpty.IsPresent)"

$steps = @(
    [pscustomobject]@{
        Name = "build_run_manifest"
        Script = $buildManifestScript
        Args = @{
            RunPath = $RunPath
            IncludeSha256 = $true
            Execute = [bool]$Execute
        }
    },
    [pscustomobject]@{
        Name = "validate_runs_contract_pre"
        Script = $validateScript
        Args = @{
            RunsRoot = $RunsRoot
            OperatorOutputPath = $OperatorOutputPath
            OperatorWarnFiles = $OperatorWarnFiles
            OperatorMaxFiles = $OperatorMaxFiles
            Execute = [bool]$Execute
        }
    },
    [pscustomobject]@{
        Name = "build_runs_index"
        Script = $buildIndexScript
        Args = @{
            RunsRoot = $RunsRoot
            GlobalIndexRoot = $GlobalIndexRoot
            MonthIndexRoot = $MonthIndexRoot
            Execute = [bool]$Execute
            ForceEmpty = [bool]$ForceEmpty
        }
    },
    [pscustomobject]@{
        Name = "build_march_truth_index"
        Script = $buildTruthScript
        Args = @{
            Year = $Year
            Month = $Month
            RunsRoot = $RunsRoot
            MonthIndexRoot = $MonthIndexRoot
            ReportRoot = $ReportRoot
            Execute = [bool]$Execute
            ForceEmpty = [bool]$ForceEmpty
        }
    },
    [pscustomobject]@{
        Name = "validate_runs_contract_post"
        Script = $validateScript
        Args = @{
            RunsRoot = $RunsRoot
            OperatorOutputPath = $OperatorOutputPath
            OperatorWarnFiles = $OperatorWarnFiles
            OperatorMaxFiles = $OperatorMaxFiles
            Execute = [bool]$Execute
        }
    }
)

foreach ($step in $steps) {
    Write-RunLog ("STEP_START name={0} script={1}" -f $step.Name, $step.Script)
    try {
        $stepArgs = $step.Args
        & $step.Script @stepArgs
        Write-RunLog ("STEP_OK name={0}" -f $step.Name)
    } catch {
        Write-RunLog ("STEP_FAIL name={0} error={1}" -f $step.Name, $_.Exception.Message)
        throw
    }
}

if ($Execute) {
    New-Item -ItemType Directory -Path $OperatorOutputPath -Force | Out-Null
    $operatorCard = Join-Path $OperatorOutputPath "operator_card_LATEST.md"
    Write-OperatorCardLatest -Path $operatorCard -YearValue $Year -MonthValue $Month -RunsRootValue $RunsRoot -GlobalIndexRootValue $GlobalIndexRoot -MonthIndexRootValue $MonthIndexRoot -ReportRootValue $ReportRoot
    Write-RunLog ("OPERATOR_CARD path={0}" -f $operatorCard)
}

$globalLatestCsv = Join-Path $GlobalIndexRoot "runs_index_global_LATEST.csv"
$monthLatestCsv = Join-Path (Join-Path $MonthIndexRoot (Join-Path $Year ("{0:d2}" -f $Month))) "runs_index_LATEST.csv"
$globalLatestJsonl = Join-Path $GlobalIndexRoot "output_catalog_global_LATEST.jsonl"

$globalRunsCount = if (Test-Path -LiteralPath $globalLatestCsv) { @(Import-Csv -LiteralPath $globalLatestCsv).Count } else { 0 }
$monthRunsCount = if (Test-Path -LiteralPath $monthLatestCsv) { @(Import-Csv -LiteralPath $monthLatestCsv).Count } else { 0 }
$operatorLaneFileCount = if (Test-Path -LiteralPath $OperatorOutputPath) { @(Get-ChildItem -LiteralPath $OperatorOutputPath -Recurse -File -ErrorAction SilentlyContinue).Count } else { 0 }
$catalogEntriesThisRun = if (Test-Path -LiteralPath $globalLatestJsonl) { @(Get-Content -LiteralPath $globalLatestJsonl -ErrorAction SilentlyContinue).Count } else { 0 }
$durationSeconds = [math]::Round($sw.Elapsed.TotalSeconds, 2)

Write-RunLog ("METRIC global_runs_count={0}" -f $globalRunsCount)
Write-RunLog ("METRIC month_runs_count={0}" -f $monthRunsCount)
Write-RunLog ("METRIC operator_lane_file_count={0}" -f $operatorLaneFileCount)
Write-RunLog ("METRIC catalog_entries_written_this_run={0}" -f $catalogEntriesThisRun)
Write-RunLog ("METRIC duration_seconds={0}" -f $durationSeconds)

Write-RunLog ("DONE run_path={0}" -f $RunPath)
Write-Host ("[OK] Contract pipeline complete. Log: {0}" -f $runLog) -ForegroundColor Green
