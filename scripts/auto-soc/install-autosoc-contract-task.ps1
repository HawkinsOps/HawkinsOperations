[CmdletBinding()]
param(
    [string]$TaskName = 'OPS_AutoSOC_Contract_Daily',
    [string]$ScriptPath = 'C:\RH\OPS\50_System\Scripts\Automation\auto-soc\run-autosoc-contract.ps1',
    [string]$LogsRoot = 'C:\RH\OPS\50_System\Runs\Logs',
    [string]$StartTime = '07:20',
    [int]$OperatorWarnFiles = 150,
    [int]$OperatorMaxFiles = 200
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    throw "AutoSOC contract orchestrator not found at $ScriptPath"
}
if (-not (Test-Path -LiteralPath $LogsRoot)) {
    New-Item -ItemType Directory -Path $LogsRoot -Force | Out-Null
}

$pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
$engine = if ($pwshCmd) { $pwshCmd.Source } else { "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" }

$taskLog = Join-Path $LogsRoot 'autosoc-contract-task.log'
$taskLogPrev = Join-Path $LogsRoot 'autosoc-contract-task.log.1'
$runnerScript = Join-Path (Split-Path -Path $ScriptPath -Parent) 'run-autosoc-contract-task.ps1'
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
& '$engine' -NoProfile -ExecutionPolicy Bypass -File '$ScriptPath' -Execute -OperatorWarnFiles $OperatorWarnFiles -OperatorMaxFiles $OperatorMaxFiles *>> '$taskLog'
"@
Set-Content -LiteralPath $runnerScript -Value $runnerContent -Encoding UTF8

$arg = '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $runnerScript + '"'
$triggerTime = [DateTime]::Today.Add([TimeSpan]::Parse($StartTime))
$action = New-ScheduledTaskAction -Execute $engine -Argument $arg
$trigger = New-ScheduledTaskTrigger -Daily -At $triggerTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily AutoSOC run contract pipeline" -Force | Out-Null
} catch {
    throw "Failed to create scheduled task with Register-ScheduledTask: $($_.Exception.Message)"
}

$taskInfo = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
$taskRuntime = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction Stop

Write-Output "Scheduled task installed: $TaskName"
Write-Output "Engine: $engine"
Write-Output "Runner script: $runnerScript"
Write-Output "Task log: $taskLog"
Write-Output "Config: StartTime=$StartTime OperatorWarnFiles=$OperatorWarnFiles OperatorMaxFiles=$OperatorMaxFiles"
Write-Output ""
Write-Output ("TaskPath: {0}" -f $taskInfo.TaskPath)
Write-Output ("State: {0}" -f $taskInfo.State)
Write-Output ("LastRunTime: {0}" -f $taskRuntime.LastRunTime)
Write-Output ("NextRunTime: {0}" -f $taskRuntime.NextRunTime)
