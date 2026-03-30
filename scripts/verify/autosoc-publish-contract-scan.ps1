param(
  [int]$MaxStagedFiles = 250,
  [int]$MaxFileSizeMB = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-StagedPaths {
  $raw = git diff --cached --name-only -z
  if (-not $raw) { return @() }
  $items = $raw -split "`0" | Where-Object { $_ -and $_.Trim().Length -gt 0 }
  return $items
}

function To-NormalizedPath {
  param([string]$PathText)
  return ($PathText -replace '\\', '/').ToLowerInvariant()
}

$repoRoot = Resolve-Path -LiteralPath "."
$staged = @(Get-StagedPaths)
if ($staged.Count -eq 0) {
  Write-Host "AutoSOC publish contract scan passed: no staged files."
  exit 0
}

$findings = New-Object System.Collections.Generic.List[string]

if ($staged.Count -gt $MaxStagedFiles) {
  $findings.Add("Staged file count $($staged.Count) exceeds cap $MaxStagedFiles.")
}

$blockedPathPatterns = @(
  '/autosoc/output/',
  '/auto-soc/output/',
  '/output/cases/',
  '/build/cases/',
  '/build/queue/',
  '/projects/autosoc/build/cases/',
  '/projects/autosoc/build/queue/',
  '/projects/autosoc/output/cases/'
)

foreach ($rel in $staged) {
  $norm = To-NormalizedPath -PathText $rel

  foreach ($p in $blockedPathPatterns) {
    if ($norm.Contains($p)) {
      $findings.Add("Blocked path pattern '$p' matched staged file '$rel'.")
      break
    }
  }

  $abs = Join-Path -Path $repoRoot -ChildPath $rel
  if (Test-Path -LiteralPath $abs -PathType Leaf) {
    $size = try { (Get-Item -LiteralPath $abs).Length } catch { 0 }
    if ($size -gt ($MaxFileSizeMB * 1MB)) {
      $mb = [math]::Round($size / 1MB, 2)
      $findings.Add("File '$rel' size ${mb}MB exceeds ${MaxFileSizeMB}MB cap.")
    }
  }
}

if ($findings.Count -gt 0) {
  Write-Host "AutoSOC publish contract scan failed:" -ForegroundColor Red
  foreach ($f in $findings) { Write-Host "- $f" -ForegroundColor Red }
  Write-Host "Allowed lane: proof/autosoc/** only." -ForegroundColor Yellow
  exit 1
}

Write-Host "AutoSOC publish contract scan passed."
exit 0

