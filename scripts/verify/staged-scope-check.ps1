param(
  [switch]$AllowMixedArtifacts,
  [switch]$AllowRestrictedPaths
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-StagedPaths {
  $raw = git diff --cached --name-only
  if (-not $raw) { return @() }
  return @($raw | Where-Object { $_ -and $_.Trim() -ne "" } | ForEach-Object { $_.Trim().Replace("\", "/") })
}

function Is-ArtifactFile {
  param([string]$Path)

  $artifactSet = @(
    "proof/autosoc/latest/reconciliation_latest.json",
    "proof/autosoc/latest/reconciliation_latest.md",
    "site/assets/data/ops-metrics.json",
    "site/data/ops-metrics.js",
    "data/metrics.json",
    "data/metrics.json.sha256"
  )

  return $artifactSet -contains $Path
}

function Is-RestrictedPath {
  param([string]$Path)

  if ($Path -match '(^|/)deploy_[^/]+(/|$)') { return $true }
  if ($Path -match '(^|/)phase0_discovery_log_.*\.md$') { return $true }
  if ($Path -match '(^|/)AutoSOC/Output(/|$)') { return $true }
  if ($Path -match '(^|/)auto-soc/Output(/|$)') { return $true }
  return $false
}

$staged = @(Get-StagedPaths)
if ($staged.Count -eq 0) {
  Write-Host "Staged scope check: no staged files."
  exit 0
}

$restricted = @($staged | Where-Object { Is-RestrictedPath -Path $_ })
if ($restricted.Count -gt 0 -and -not $AllowRestrictedPaths) {
  Write-Host "Commit blocked: restricted path(s) staged." -ForegroundColor Red
  $restricted | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
  Write-Host "If intentional, re-run with -AllowRestrictedPaths." -ForegroundColor Yellow
  exit 1
}

$artifactFiles = @($staged | Where-Object { Is-ArtifactFile -Path $_ })
if ($artifactFiles.Count -gt 0 -and -not $AllowMixedArtifacts) {
  $nonArtifact = @($staged | Where-Object { -not (Is-ArtifactFile -Path $_) })
  if ($nonArtifact.Count -gt 0) {
    Write-Host "Commit blocked: artifact refresh files are mixed with non-artifact files." -ForegroundColor Red
    Write-Host "Artifact files detected:" -ForegroundColor Yellow
    $artifactFiles | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
    Write-Host "Non-artifact files detected:" -ForegroundColor Yellow
    $nonArtifact | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
    Write-Host "Use a separate commit or re-run with -AllowMixedArtifacts if this is intentional." -ForegroundColor Yellow
    exit 1
  }
}

Write-Host "Staged scope check passed." -ForegroundColor Green
exit 0
