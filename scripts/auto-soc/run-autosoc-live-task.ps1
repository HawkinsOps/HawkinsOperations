$ErrorActionPreference = 'Continue'

# Env var routing — all pipeline paths resolve to R:\ via common.py / daily-ops.ps1.
$env:AUTOSOC_OUTPUT          = 'R:\DailyOps\Data\autosoc\runtime_data\Output'
$env:AUTOSOC_DATA            = 'R:\DailyOps\Data\autosoc\runtime_data'
$env:AUTOSOC_PIPELINE        = 'R:\GitHub\HawkinsOperations\scripts\auto-soc'
$env:AUTOSOC_LOGS            = 'R:\DailyOps\Lab\autosoc\runtime\logs'
$env:AUTOSOC_CONFIG          = 'R:\DailyOps\Lab\autosoc\runtime\config'
$env:AUTOSOC_SECRETS         = 'R:\AgentOps\env\credentials_store\wazuh'
$env:AUTOSOC_REPO            = 'R:\GitHub\HawkinsOperations'
$env:WAZUH_INDEXER_PASS_FILE = 'R:\AgentOps\env\credentials_store\wazuh\all.txt'

$logDir = 'R:\DailyOps\Lab\autosoc\runtime\logs'
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$log  = Join-Path $logDir 'autosoc-live-task.log'
$prev = Join-Path $logDir 'autosoc-live-task.log.1'
$max  = 262144
if (Test-Path -LiteralPath $log) {
    try {
        if ((Get-Item -LiteralPath $log).Length -gt $max) {
            if (Test-Path -LiteralPath $prev) { Remove-Item -LiteralPath $prev -Force -ErrorAction SilentlyContinue }
            Move-Item -LiteralPath $log -Destination $prev -Force
        }
    } catch {}
}
& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -ExecutionPolicy Bypass -File 'R:\GitHub\HawkinsOperations\scripts\auto-soc\daily-ops.ps1' -Refresh -SkipTests -FreshnessP95MaxSeconds 3600 -FreshnessOldestMaxSeconds 7200 *>> $log
