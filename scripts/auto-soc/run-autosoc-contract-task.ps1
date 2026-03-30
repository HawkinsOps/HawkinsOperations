$ErrorActionPreference = 'Continue'
$log = 'C:\RH\OPS\50_System\Runs\Logs\autosoc-contract-task.log'
$prev = 'C:\RH\OPS\50_System\Runs\Logs\autosoc-contract-task.log.1'
$max = 262144
if (Test-Path -LiteralPath $log) {
    try {
        if ((Get-Item -LiteralPath $log).Length -gt $max) {
            if (Test-Path -LiteralPath $prev) { Remove-Item -LiteralPath $prev -Force -ErrorAction SilentlyContinue }
            Move-Item -LiteralPath $log -Destination $prev -Force
        }
    } catch {}
}
& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -ExecutionPolicy Bypass -File 'C:\RH\OPS\50_System\Scripts\Automation\auto-soc\run-autosoc-contract.ps1' -Execute -OperatorWarnFiles 150 -OperatorMaxFiles 200 *>> 'C:\RH\OPS\50_System\Runs\Logs\autosoc-contract-task.log'
