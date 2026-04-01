<#
.SYNOPSIS
    Verification script for Sigma Detection Library case study.
.PARAMETER Snapshot
    Snapshot tag (default: "2026-03-25")
#>

[CmdletBinding()]
param([string]$Snapshot = "2026-03-25")

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$ExitCode = 0
$Results = @()

function Write-Check {
    param([string]$Name, [bool]$Pass, [string]$Detail)
    $status = if ($Pass) { "PASS" } else { "FAIL" }
    Write-Host "[$status] $Name" -ForegroundColor $(if ($Pass) { "Green" } else { "Red" })
    if ($Detail) { Write-Host "       $Detail" -ForegroundColor Gray }
    $script:Results += [PSCustomObject]@{ Check = $Name; Status = $status }
    if (-not $Pass) { $script:ExitCode = 1 }
}

# ── JSON counts ──
$vcJsonPath = Join-Path $RepoRoot "PROOF_PACK" "verified_counts.json"
$vc = Get-Content $vcJsonPath -Raw | ConvertFrom-Json
Write-Check "Sigma count = 103 (JSON)" ($vc.counts.sigma -eq 103) "Actual: $($vc.counts.sigma)"

# ── Physical file count ──
$sigmaDir = Join-Path $RepoRoot "content" "detection-rules" "sigma"
$sigmaFiles = (Get-ChildItem -Recurse $sigmaDir -Filter *.yml).Count
Write-Check "Physical Sigma files = 103" ($sigmaFiles -eq 103) "Found: $sigmaFiles"

# ── Tactic directories ──
$expectedTactics = @("collection","credential-access","defense-evasion","discovery","execution","exfiltration","impact","lateral-movement","persistence","privilege-escalation")
$actualTactics = (Get-ChildItem $sigmaDir -Directory).Name | Sort-Object
$tacticMatch = ($expectedTactics | Sort-Object) -join "," -eq ($actualTactics -join ",")
Write-Check "All 10 tactic directories present" $tacticMatch "Expected: $($expectedTactics -join ', ')"

# ── Per-tactic counts ──
$expectedCounts = @{
    "collection" = 10; "credential-access" = 10; "defense-evasion" = 10
    "discovery" = 10; "execution" = 9; "exfiltration" = 10
    "impact" = 13; "lateral-movement" = 10; "persistence" = 11
    "privilege-escalation" = 10
}
foreach ($tactic in $expectedCounts.Keys) {
    $tacticDir = Join-Path $sigmaDir $tactic
    if (Test-Path $tacticDir) {
        $count = (Get-ChildItem $tacticDir -Filter *.yml).Count
        Write-Check "Tactic '$tactic' = $($expectedCounts[$tactic])" ($count -eq $expectedCounts[$tactic]) "Found: $count"
    } else {
        Write-Check "Tactic '$tactic' directory exists" $false "NOT FOUND"
    }
}

# ── HTML data-verified ──
$htmlPath = Join-Path $RepoRoot "site" "case-study-sigma-library.html"
if (Test-Path $htmlPath) {
    $html = Get-Content $htmlPath -Raw
    $hasVerified = $html -match 'data-verified="sigma">103<'
    Write-Check "HTML data-verified='sigma' = 103" $hasVerified ""
} else {
    Write-Check "HTML case-study-sigma-library.html exists" $false "NOT FOUND"
}

# ── Sitemap ──
$sitemapPath = Join-Path $RepoRoot "site" "sitemap.xml"
if (Test-Path $sitemapPath) {
    $sitemap = Get-Content $sitemapPath -Raw
    Write-Check "Sitemap includes case-study-sigma-library" ($sitemap -match "case-study-sigma-library") ""
}

# ── Summary ──
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
$pass = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$fail = ($Results | Where-Object { $_.Status -eq "FAIL" }).Count
Write-Host "PASS: $pass / $($Results.Count)   FAIL: $fail" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Red" })
Write-Host "Snapshot: $Snapshot" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

exit $ExitCode
