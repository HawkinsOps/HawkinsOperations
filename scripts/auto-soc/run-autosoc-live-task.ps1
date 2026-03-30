$ErrorActionPreference = 'Continue'
$log = 'C:\RH\OPS\50_System\Runs\Logs\autosoc-live-task.log'
$prev = 'C:\RH\OPS\50_System\Runs\Logs\autosoc-live-task.log.1'
$max = 262144
if (Test-Path -LiteralPath $log) {
    try {
        if ((Get-Item -LiteralPath $log).Length -gt $max) {
            if (Test-Path -LiteralPath $prev) { Remove-Item -LiteralPath $prev -Force -ErrorAction SilentlyContinue }
            Move-Item -LiteralPath $log -Destination $prev -Force
        }
    } catch {}
}
& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -ExecutionPolicy Bypass -File 'C:\RH\OPS\50_System\Scripts\Automation\auto-soc\daily-ops.ps1' -Refresh -SkipTests -FreshnessP95MaxSeconds 3600 -FreshnessOldestMaxSeconds 7200 *>> 'C:\RH\OPS\50_System\Runs\Logs\autosoc-live-task.log'
