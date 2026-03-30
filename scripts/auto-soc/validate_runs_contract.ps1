param(
    [string]$RunsRoot = "C:\RH\OPS\50_System\Runs\AutoSOC",
    [string]$OperatorOutputPath = "C:\RH\OPS\30_Projects\Active\AutoSOC\Output",
    [int]$OperatorMaxFiles = 200,
    [int]$OperatorWarnFiles = 150,
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$violations = New-Object System.Collections.Generic.List[string]
$requiredFolders = @("Logs", "Reports", "Diagnostics", "operator_pack")

if (-not (Test-Path -LiteralPath $RunsRoot)) {
    $violations.Add("Runs root not found: $RunsRoot") | Out-Null
} else {
    $runDirs = Get-ChildItem -LiteralPath $RunsRoot -Recurse -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "^run_\d{2}-\d{2}-\d{4}_\d{6}$" }

    foreach ($run in $runDirs) {
        foreach ($req in $requiredFolders) {
            if (-not (Test-Path -LiteralPath (Join-Path -Path $run.FullName -ChildPath $req))) {
                $violations.Add("Missing required folder '$req' in run: $($run.FullName)") | Out-Null
            }
        }

        $manifestCount = (Get-ChildItem -LiteralPath $run.FullName -File -Filter "run_manifest_run_*.json" -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($manifestCount -lt 1) {
            $violations.Add("Missing run manifest in run: $($run.FullName)") | Out-Null
        }

        $verifyCount = (Get-ChildItem -LiteralPath $run.FullName -File -Filter "verify_*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($verifyCount -lt 1) {
            $violations.Add("Missing verify markdown in run: $($run.FullName)") | Out-Null
        }

        $latestHits = Get-ChildItem -LiteralPath $run.FullName -Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match "LATEST" }
        if (($latestHits | Measure-Object).Count -gt 0) {
            $violations.Add("LATEST marker found inside immutable archive run: $($run.FullName)") | Out-Null
        }
    }
}

if (Test-Path -LiteralPath $OperatorOutputPath) {
    $operatorFileCount = (Get-ChildItem -LiteralPath $OperatorOutputPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($operatorFileCount -gt $OperatorMaxFiles) {
        $violations.Add("Operator lane file cap exceeded: $operatorFileCount > $OperatorMaxFiles at $OperatorOutputPath") | Out-Null
    } elseif ($operatorFileCount -gt $OperatorWarnFiles) {
        Write-Warning ("Operator lane approaching cap: {0} > warn threshold {1} at {2}" -f $operatorFileCount, $OperatorWarnFiles, $OperatorOutputPath)
    }
    Write-Host ("[INFO] Operator lane file count: {0}" -f $operatorFileCount)
} else {
    $violations.Add("Operator output path not found: $OperatorOutputPath") | Out-Null
}

Write-Host ("[INFO] Contract violations: {0}" -f $violations.Count)
if ($violations.Count -gt 0) {
    foreach ($v in $violations) {
        Write-Host ("[VIOLATION] {0}" -f $v) -ForegroundColor Red
    }
}

if ($violations.Count -gt 0 -and $Execute) {
    Write-Error "Run contract validation failed."
    exit 1
}

if ($violations.Count -gt 0 -and -not $Execute) {
    Write-Host "[DRY-RUN] Violations detected. Re-run with -Execute to fail fast in automation." -ForegroundColor Yellow
    exit 0
}

Write-Host "[OK] Contract validation passed." -ForegroundColor Green
