<#
.SYNOPSIS
    Verification script for AutoSOC Pipeline Recovery case study.
    Validates detection counts against VERIFIED_COUNTS.md and checks artifact integrity.

.PARAMETER Snapshot
    Snapshot tag (default: "2026-03-25")

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File .\evidence\verify.ps1 --snapshot=2026-03-25
#>

[CmdletBinding()]
param(
    [string]$Snapshot = "2026-03-25"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$ExitCode = 0
$Results = @()

function Write-Check {
    param([string]$Name, [bool]$Pass, [string]$Detail)
    $status = if ($Pass) { "PASS" } else { "FAIL" }
    $color = if ($Pass) { "Green" } else { "Red" }
    Write-Host "[$status] $Name" -ForegroundColor $color
    if ($Detail) { Write-Host "       $Detail" -ForegroundColor Gray }
    $script:Results += [PSCustomObject]@{ Check = $Name; Status = $status; Detail = $Detail }
    if (-not $Pass) { $script:ExitCode = 1 }
}

# ── Check 1: VERIFIED_COUNTS.md exists ──
$vcPath = Join-Path $RepoRoot "PROOF_PACK" "VERIFIED_COUNTS.md"
Write-Check -Name "VERIFIED_COUNTS.md exists" -Pass (Test-Path $vcPath) -Detail $vcPath

# ── Check 2: verified_counts.json exists and parses ──
$vcJsonPath = Join-Path $RepoRoot "PROOF_PACK" "verified_counts.json"
$jsonExists = Test-Path $vcJsonPath
Write-Check -Name "verified_counts.json exists" -Pass $jsonExists -Detail $vcJsonPath

if ($jsonExists) {
    $vc = Get-Content $vcJsonPath -Raw | ConvertFrom-Json

    # ── Check 3: Sigma count ──
    $sigmaExpected = 103
    $sigmaActual = $vc.counts.sigma
    Write-Check -Name "Sigma count = $sigmaExpected" -Pass ($sigmaActual -eq $sigmaExpected) -Detail "Actual: $sigmaActual"

    # ── Check 4: Splunk count ──
    $splunkExpected = 9
    $splunkActual = $vc.counts.splunk
    Write-Check -Name "Splunk count = $splunkExpected" -Pass ($splunkActual -eq $splunkExpected) -Detail "Actual: $splunkActual"

    # ── Check 5: Wazuh XML file count ──
    $wazuhFilesExpected = 24
    $wazuhFilesActual = $vc.counts.wazuh_xml_files
    Write-Check -Name "Wazuh XML files = $wazuhFilesExpected" -Pass ($wazuhFilesActual -eq $wazuhFilesExpected) -Detail "Actual: $wazuhFilesActual"

    # ── Check 6: Wazuh rule block count ──
    $wazuhBlocksExpected = 28
    $wazuhBlocksActual = $vc.counts.wazuh
    Write-Check -Name "Wazuh rule blocks = $wazuhBlocksExpected" -Pass ($wazuhBlocksActual -eq $wazuhBlocksExpected) -Detail "Actual: $wazuhBlocksActual"

    # ── Check 7: IR playbook count ──
    $irExpected = 10
    $irActual = $vc.counts.ir
    Write-Check -Name "IR playbooks = $irExpected" -Pass ($irActual -eq $irExpected) -Detail "Actual: $irActual"

    # ── Check 8: Total detections ──
    $totalExpected = 140
    $totalActual = $vc.counts.detections
    Write-Check -Name "Total detections = $totalExpected" -Pass ($totalActual -eq $totalExpected) -Detail "Actual: $totalActual"
}

# ── Check 9: Physical file count verification (Sigma) ──
$sigmaDir = Join-Path $RepoRoot "content" "detection-rules" "sigma"
if (Test-Path $sigmaDir) {
    $sigmaFiles = (Get-ChildItem -Recurse $sigmaDir -Filter *.yml).Count
    Write-Check -Name "Physical Sigma YAML files = 103" -Pass ($sigmaFiles -eq 103) -Detail "Found: $sigmaFiles"
} else {
    Write-Check -Name "Physical Sigma YAML files = 103" -Pass $false -Detail "Directory not found: $sigmaDir"
}

# ── Check 10: Physical file count verification (Splunk) ──
$splunkDir = Join-Path $RepoRoot "content" "detection-rules" "splunk"
if (Test-Path $splunkDir) {
    $splunkFiles = (Get-ChildItem -Recurse $splunkDir -Filter *.spl).Count
    Write-Check -Name "Physical Splunk SPL files = 9" -Pass ($splunkFiles -eq 9) -Detail "Found: $splunkFiles"
} else {
    Write-Check -Name "Physical Splunk SPL files = 9" -Pass $false -Detail "Directory not found: $splunkDir"
}

# ── Check 11: Physical file count verification (Wazuh) ──
$wazuhDir = Join-Path $RepoRoot "content" "detection-rules" "wazuh" "rules"
if (Test-Path $wazuhDir) {
    $wazuhFiles = (Get-ChildItem -Recurse $wazuhDir -Filter *.xml).Count
    Write-Check -Name "Physical Wazuh XML files = 24" -Pass ($wazuhFiles -eq 24) -Detail "Found: $wazuhFiles"
} else {
    Write-Check -Name "Physical Wazuh XML files = 24" -Pass $false -Detail "Directory not found: $wazuhDir"
}

# ── Check 12: Physical file count verification (IR Playbooks) ──
$irDir = Join-Path $RepoRoot "content" "incident-response" "playbooks"
if (Test-Path $irDir) {
    $irFiles = (Get-ChildItem $irDir -Filter "IR-*.md").Count
    Write-Check -Name "Physical IR playbook files = 10" -Pass ($irFiles -eq 10) -Detail "Found: $irFiles"
} else {
    Write-Check -Name "Physical IR playbook files = 10" -Pass $false -Detail "Directory not found: $irDir"
}

# ── Check 13: Key artifacts exist ──
$requiredFiles = @(
    "PROOF_PACK/VERIFIED_COUNTS.md",
    "PROOF_PACK/ARCHITECTURE.md",
    "PROOF_PACK/PROOF_INDEX.md",
    "docs/SignalFoundry_Case_Study_March2026.md",
    "site/case-study-autosoc.html",
    "site/proof.html",
    "site/resume.html",
    "site/detections.html",
    "site/sitemap.xml",
    "site/robots.txt",
    "site/assets/Raylee_Hawkins_Resume.pdf",
    "site/resume.txt",
    "START_HERE.md"
)

foreach ($f in $requiredFiles) {
    $fp = Join-Path $RepoRoot $f
    Write-Check -Name "Artifact exists: $f" -Pass (Test-Path $fp) -Detail $fp
}

# ── Check 14: robots.txt references sitemap ──
$robotsPath = Join-Path $RepoRoot "site" "robots.txt"
if (Test-Path $robotsPath) {
    $robotsContent = Get-Content $robotsPath -Raw
    $hasSitemap = $robotsContent -match "Sitemap:\s*https://hawkinsops\.com/sitemap\.xml"
    Write-Check -Name "robots.txt references sitemap" -Pass $hasSitemap -Detail "Pattern: Sitemap: https://hawkinsops.com/sitemap.xml"
} else {
    Write-Check -Name "robots.txt references sitemap" -Pass $false -Detail "File not found"
}

# ── Check 15: sitemap includes case-study-autosoc ──
$sitemapPath = Join-Path $RepoRoot "site" "sitemap.xml"
if (Test-Path $sitemapPath) {
    $sitemapContent = Get-Content $sitemapPath -Raw
    $hasAutosoc = $sitemapContent -match "hawkinsops\.com/case-study-autosoc"
    Write-Check -Name "sitemap includes case-study-autosoc" -Pass $hasAutosoc -Detail "URL in sitemap.xml"
} else {
    Write-Check -Name "sitemap includes case-study-autosoc" -Pass $false -Detail "File not found"
}

# ── Summary ──
Write-Host ""
Write-Host "═══════════════════════════════════" -ForegroundColor Cyan
$passCount = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($Results | Where-Object { $_.Status -eq "FAIL" }).Count
Write-Host "PASS: $passCount / $($Results.Count)   FAIL: $failCount" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
Write-Host "Snapshot: $Snapshot" -ForegroundColor Gray
Write-Host "═══════════════════════════════════" -ForegroundColor Cyan

exit $ExitCode
