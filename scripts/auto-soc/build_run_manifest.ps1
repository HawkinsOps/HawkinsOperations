param(
    [Parameter(Mandatory = $true)]
    [string]$RunPath,
    [switch]$Execute,
    [switch]$IncludeSha256
)

$ErrorActionPreference = "Stop"

function Get-RunIdFromPath {
    param([string]$PathValue)
    $leaf = Split-Path -Path $PathValue -Leaf
    if ($leaf -match "^run_\d{2}-\d{2}-\d{4}_\d{6}$") {
        return $leaf
    }
    return $leaf
}

if (-not (Test-Path -LiteralPath $RunPath)) {
    throw "Run path not found: $RunPath"
}

$runItem = Get-Item -LiteralPath $RunPath
if (-not $runItem.PSIsContainer) {
    throw "Run path is not a directory: $RunPath"
}

$runId = Get-RunIdFromPath -PathValue $RunPath
$manifestName = "run_manifest_{0}.json" -f $runId
$manifestPath = Join-Path -Path $RunPath -ChildPath $manifestName

$requiredFolders = @("Logs", "Reports", "Diagnostics", "operator_pack")
$requiredStatus = @{}
foreach ($name in $requiredFolders) {
    $requiredStatus[$name] = Test-Path -LiteralPath (Join-Path -Path $RunPath -ChildPath $name)
}

$verifyFiles = Get-ChildItem -LiteralPath $RunPath -File -Filter "verify_*.md" -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty Name

$allFiles = Get-ChildItem -LiteralPath $RunPath -Recurse -File -Force -ErrorAction SilentlyContinue
$entries = @()
$totalBytes = [int64]0

foreach ($f in $allFiles) {
    $relativePath = $f.FullName.Substring($RunPath.Length).TrimStart("\")
    $totalBytes += [int64]$f.Length

    $entry = [ordered]@{
        relative_path = $relativePath
        size_bytes    = [int64]$f.Length
        last_write_utc = $f.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
    }

    if ($IncludeSha256) {
        $entry.sha256 = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }

    $entries += [pscustomobject]$entry
}

$manifest = [ordered]@{
    schema_version         = "1.0"
    generated_utc          = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    run_id                 = $runId
    run_path               = $RunPath
    file_count             = $allFiles.Count
    total_size_bytes       = $totalBytes
    required_folders       = $requiredStatus
    verify_files           = $verifyFiles
    includes_sha256        = [bool]$IncludeSha256
    artifacts              = $entries
}

Write-Host ("[INFO] Run ID: {0}" -f $runId)
Write-Host ("[INFO] Files: {0}" -f $allFiles.Count)
Write-Host ("[INFO] Bytes: {0}" -f $totalBytes)
Write-Host ("[INFO] Manifest target: {0}" -f $manifestPath)

if (-not $Execute) {
    Write-Host "[DRY-RUN] Manifest not written. Re-run with -Execute to write file." -ForegroundColor Yellow
    return
}

$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8
Write-Host ("[OK] Wrote manifest: {0}" -f $manifestPath) -ForegroundColor Green
