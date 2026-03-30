param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [string]$OutputPath = "C:\RH\OPS\30_Projects\Active\AutoSOC\Output\manager_agents_latest.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "Input file not found: $InputPath"
}

$agents = @()
$lineNo = 0
foreach ($line in Get-Content -LiteralPath $InputPath) {
    $lineNo++
    $trim = $line.Trim()
    if (-not $trim) { continue }
    if ($trim -notmatch '^ID:\s*([^,]+),\s*Name:\s*([^,]+),\s*IP:\s*([^,]+),\s*(.+)$') { continue }
    $id = $Matches[1].Trim()
    $name = $Matches[2].Trim()
    $ip = $Matches[3].Trim()
    $status = $Matches[4].Trim()
    $agents += [pscustomobject]@{
        id = $id
        name = $name
        ip = $ip
        status = $status
        active = [bool]($status.ToLower().Contains("active"))
        source_line = $lineNo
    }
}

$out = [ordered]@{
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    source_path = $InputPath
    agent_count = $agents.Count
    agents = $agents
}

$outDir = Split-Path -Parent $OutputPath
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$out | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host ("MANAGER_AGENTS_JSON={0}" -f $OutputPath)
Write-Host ("AGENTS_PARSED={0}" -f $agents.Count)
