[CmdletBinding()]
param(
    [string]$TaskName = 'OPS_AutoSOC_Live_5Min',
    [string]$ScriptPath = 'C:\RH\OPS\50_System\Scripts\Automation\auto-soc\daily-ops.ps1',
    [string]$LogsRoot = 'C:\RH\OPS\50_System\Runs\Logs',
    [int]$IntervalMinutes = 5,
    [int]$FreshnessP95MaxSeconds = 3600,
    [int]$FreshnessOldestMaxSeconds = 7200,
    [switch]$RunNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    throw "AutoSOC live runner not found at $ScriptPath"
}
if (-not (Test-Path -LiteralPath $LogsRoot)) {
    New-Item -ItemType Directory -Path $LogsRoot -Force | Out-Null
}
if ($IntervalMinutes -lt 1) {
    throw "IntervalMinutes must be at least 1"
}

$pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
$engine = if ($pwshCmd) { $pwshCmd.Source } else { "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" }

$taskLog = Join-Path $LogsRoot 'autosoc-live-task.log'
$taskLogPrev = Join-Path $LogsRoot 'autosoc-live-task.log.1'
$runnerScript = Join-Path (Split-Path -Path $ScriptPath -Parent) 'run-autosoc-live-task.ps1'
$runnerCmd = Join-Path (Split-Path -Path $ScriptPath -Parent) 'run-autosoc-live-task.cmd'
$maxBytes = 262144

$runnerContent = @"
`$ErrorActionPreference = 'Continue'
`$log = '$taskLog'
`$prev = '$taskLogPrev'
`$max = $maxBytes
if (Test-Path -LiteralPath `$log) {
    try {
        if ((Get-Item -LiteralPath `$log).Length -gt `$max) {
            if (Test-Path -LiteralPath `$prev) { Remove-Item -LiteralPath `$prev -Force -ErrorAction SilentlyContinue }
            Move-Item -LiteralPath `$log -Destination `$prev -Force
        }
    } catch {}
}
& '$engine' -NoProfile -ExecutionPolicy Bypass -File '$ScriptPath' -Refresh -SkipTests -FreshnessP95MaxSeconds $FreshnessP95MaxSeconds -FreshnessOldestMaxSeconds $FreshnessOldestMaxSeconds *>> '$taskLog'
"@
Set-Content -LiteralPath $runnerScript -Value $runnerContent -Encoding UTF8

$cmdContent = '@echo off' + "`r`n" +
    '"' + $engine + '" -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $runnerScript + '"' + "`r`n"
Set-Content -LiteralPath $runnerCmd -Value $cmdContent -Encoding ASCII

$taskCommand = '"' + $runnerCmd + '"'
schtasks /Create /SC MINUTE /MO $IntervalMinutes /TN $TaskName /TR $taskCommand /F | Out-Null

if ($RunNow) {
    schtasks /Run /TN $TaskName | Out-Null
}

Write-Output "Scheduled task installed: $TaskName"
Write-Output "Engine: $engine"
Write-Output "Runner script: $runnerScript"
Write-Output "Runner cmd: $runnerCmd"
Write-Output "Task log: $taskLog"
Write-Output "IntervalMinutes: $IntervalMinutes"
Write-Output "FreshnessP95MaxSeconds: $FreshnessP95MaxSeconds"
Write-Output "FreshnessOldestMaxSeconds: $FreshnessOldestMaxSeconds"
Write-Output "TaskCommand: $taskCommand"
