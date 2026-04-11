[CmdletBinding()]
param(
    [string]$OutFile = ".\PROOF_PACK\VERIFIED_COUNTS.md"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$sigmaPath = Join-Path $repoRoot "content\detection-rules\sigma"
$splunkPath = Join-Path $repoRoot "content\detection-rules\splunk"
$wazuhPath = Join-Path $repoRoot "content\detection-rules\wazuh\rules"
$playbookPath = Join-Path $repoRoot "content\incident-response\playbooks"
$outPath = if ([System.IO.Path]::IsPathRooted($OutFile)) { $OutFile } else { Join-Path $repoRoot $OutFile }

$sigmaYml = (Get-ChildItem -Recurse -Filter *.yml -Path $sigmaPath -ErrorAction SilentlyContinue).Count
$sigmaYaml = (Get-ChildItem -Recurse -Filter *.yaml -Path $sigmaPath -ErrorAction SilentlyContinue).Count
$sigma = $sigmaYml + $sigmaYaml
$splunkFiles = (Get-ChildItem -Recurse -Filter *.spl -Path $splunkPath -ErrorAction SilentlyContinue).Count
$splunk = (Get-ChildItem -Recurse -Filter *.spl -Path $splunkPath -ErrorAction SilentlyContinue |
    Select-String -Pattern '^# .+ - T\d+|^# MITRE: T\d+' | Measure-Object).Count
$wazuhXmlFiles = (Get-ChildItem -Recurse -Filter *.xml -Path $wazuhPath -ErrorAction SilentlyContinue).Count
$wazuhRuleBlocks = (Get-ChildItem -Recurse -Filter *.xml -Path $wazuhPath -ErrorAction SilentlyContinue |
    Select-String -Pattern "<rule id=" | Measure-Object).Count
$playbooks = (Get-ChildItem -Recurse -Filter IR-*.md -Path $playbookPath -ErrorAction SilentlyContinue).Count

# Read MITRE coverage from PROOF_PACK/VERIFIED_MITRE.csv if present.
# Produced by scripts/verify/verify-mitre.ps1. If the CSV is missing, the MITRE
# row is omitted — run verify-mitre.ps1 first to include it.
$mitreCsvPath = Join-Path $repoRoot "PROOF_PACK\VERIFIED_MITRE.csv"
$mitreRow = ""
if (Test-Path -LiteralPath $mitreCsvPath) {
    $mitreRows = Import-Csv -LiteralPath $mitreCsvPath
    $mitreTechniques = ($mitreRows | Measure-Object).Count
    $mitreFamilies = ($mitreRows | Select-Object -ExpandProperty Family -Unique | Measure-Object).Count
    $mitreRow = "| **MITRE ATT&CK coverage** | **$mitreTechniques** techniques / **$mitreFamilies** families | PROOF_PACK/VERIFIED_MITRE.csv |`r`n"
}

$content = @"
# Verified Detection Counts

This file is generated from live repository file counts.

---

## Detection Rules

| Platform | Count | Location |
|----------|-------|----------|
| **Sigma** (YAML) | **$sigma** rules | content/detection-rules/sigma/ |
| **Splunk** (SPL) | **$splunkFiles** files, **$splunk** detection searches | content/detection-rules/splunk/ |
| **Wazuh** (XML) | **$wazuhXmlFiles** files, **$wazuhRuleBlocks** rule blocks | content/detection-rules/wazuh/rules/ |

## Incident Response

| Type | Count | Location |
|------|-------|----------|
| **IR Playbooks** (IR-*.md) | **$playbooks** playbooks | content/incident-response/playbooks/ |

## MITRE ATT&CK Coverage

| Metric | Count | Source |
|--------|-------|--------|
$mitreRow---

## Verification Commands

    pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
    pwsh -NoProfile -File ".\scripts\verify\verify-mitre.ps1"
    pwsh -NoProfile -File ".\scripts\verify\generate-verified-counts.ps1" -OutFile ".\PROOF_PACK\VERIFIED_COUNTS.md"

## Build Artifact Command

    pwsh -NoProfile -File ".\scripts\build-wazuh-bundle.ps1"

---

_Regenerate this file after detection or playbook content changes._
"@

$outDir = Split-Path -Parent $outPath
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

Set-Content -LiteralPath $outPath -Value $content -Encoding UTF8
Write-Host "Wrote verified counts: $outPath"

