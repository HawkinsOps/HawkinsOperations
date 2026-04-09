# verify-mitre.ps1
# Enumerate MITRE ATT&CK technique IDs referenced by every detection rule in the repo.
# Parses Sigma YAML tags, Wazuh <mitre><id> blocks, and Splunk "# MITRE: T####" comments,
# with a generic `\bT\d{4}(?:\.\d+)?\b` fallback for any rule file that the platform-specific
# parser does not cover. Emits VERIFIED_MITRE.csv (Technique,Family,FileList,FileCount) and
# VERIFIED_MITRE.md (summary + sample rows).
#
# Usage:
#   pwsh -NoProfile -File ./scripts/verify/verify-mitre.ps1
#   pwsh -NoProfile -File ./scripts/verify/verify-mitre.ps1 -VerboseMode
#
# Exit 0 on success, 2 if zero techniques discovered (indicates pattern mismatch).

[CmdletBinding()]
param(
    [string]$CsvOut = "PROOF_PACK/VERIFIED_MITRE.csv",
    [string]$MdOut  = "PROOF_PACK/VERIFIED_MITRE.md",
    [switch]$VerboseMode
)

$ErrorActionPreference = "Stop"

$repoRoot   = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$sigmaPath  = Join-Path $repoRoot "content\detection-rules\sigma"
$splunkPath = Join-Path $repoRoot "content\detection-rules\splunk"
$wazuhPath  = Join-Path $repoRoot "content\detection-rules\wazuh\rules"

$csvOutPath = if ([System.IO.Path]::IsPathRooted($CsvOut)) { $CsvOut } else { Join-Path $repoRoot $CsvOut }
$mdOutPath  = if ([System.IO.Path]::IsPathRooted($MdOut))  { $MdOut }  else { Join-Path $repoRoot $MdOut }

# techniqueId (e.g. "T1558.003") -> sorted unique list of repo-relative file paths
$techniqueMap = @{}

function Add-Hit {
    param(
        [Parameter(Mandatory)] [string] $Technique,
        [Parameter(Mandatory)] [string] $FilePath
    )
    $normalized = $Technique.ToUpperInvariant().Trim()
    if ($normalized -notmatch '^T\d{4}(\.\d{1,3})?$') { return }
    $rel = $FilePath.Substring($repoRoot.Length).TrimStart('\','/')
    $rel = $rel -replace '\\','/'
    if (-not $techniqueMap.ContainsKey($normalized)) {
        $techniqueMap[$normalized] = [System.Collections.Generic.HashSet[string]]::new()
    }
    [void]$techniqueMap[$normalized].Add($rel)
}

# --- Sigma: parse YAML "tags:" block entries of the form "attack.tNNNN[.NNN]" ---
$sigmaFiles = @()
if (Test-Path -LiteralPath $sigmaPath) {
    $sigmaFiles = Get-ChildItem -Recurse -Path $sigmaPath -Include *.yml,*.yaml -ErrorAction SilentlyContinue
}
foreach ($f in $sigmaFiles) {
    $text = Get-Content -LiteralPath $f.FullName -Raw
    $fileHits = 0
    foreach ($m in [regex]::Matches($text, '(?i)attack\.t(\d{4})(?:\.(\d{1,3}))?')) {
        $tid = "T" + $m.Groups[1].Value
        if ($m.Groups[2].Success) { $tid += "." + $m.Groups[2].Value }
        Add-Hit -Technique $tid -FilePath $f.FullName
        $fileHits++
    }
    # Generic fallback: bare T#### refs in the file (covers `references:` URLs etc.)
    foreach ($m in [regex]::Matches($text, '\bT(\d{4})(?:\.(\d{1,3}))?\b')) {
        $tid = "T" + $m.Groups[1].Value
        if ($m.Groups[2].Success) { $tid += "." + $m.Groups[2].Value }
        Add-Hit -Technique $tid -FilePath $f.FullName
    }
    if ($VerboseMode) { Write-Host ("sigma  {0}: {1} tag hits" -f $f.Name, $fileHits) }
}

# --- Wazuh: parse <mitre><id>TNNNN</id></mitre> and <mitre id="TNNNN"> variants ---
$wazuhFiles = @()
if (Test-Path -LiteralPath $wazuhPath) {
    $wazuhFiles = Get-ChildItem -Recurse -Path $wazuhPath -Filter *.xml -ErrorAction SilentlyContinue
}
foreach ($f in $wazuhFiles) {
    $text = Get-Content -LiteralPath $f.FullName -Raw
    $fileHits = 0
    foreach ($m in [regex]::Matches($text, '(?is)<mitre>(.*?)</mitre>')) {
        foreach ($im in [regex]::Matches($m.Groups[1].Value, '(?i)<id[^>]*>\s*T(\d{4})(?:\.(\d{1,3}))?\s*</id>')) {
            $tid = "T" + $im.Groups[1].Value
            if ($im.Groups[2].Success) { $tid += "." + $im.Groups[2].Value }
            Add-Hit -Technique $tid -FilePath $f.FullName
            $fileHits++
        }
    }
    foreach ($m in [regex]::Matches($text, '(?i)<mitre\s+id="T(\d{4})(?:\.(\d{1,3}))?"')) {
        $tid = "T" + $m.Groups[1].Value
        if ($m.Groups[2].Success) { $tid += "." + $m.Groups[2].Value }
        Add-Hit -Technique $tid -FilePath $f.FullName
        $fileHits++
    }
    # Fallback: bare T#### in rule comments (e.g. "MITRE ATT&CK: T1558.003")
    foreach ($m in [regex]::Matches($text, '\bT(\d{4})(?:\.(\d{1,3}))?\b')) {
        $tid = "T" + $m.Groups[1].Value
        if ($m.Groups[2].Success) { $tid += "." + $m.Groups[2].Value }
        Add-Hit -Technique $tid -FilePath $f.FullName
    }
    if ($VerboseMode) { Write-Host ("wazuh  {0}: {1} <mitre> hits" -f $f.Name, $fileHits) }
}

# --- Splunk: parse "# MITRE: TNNNN" and "/* MITRE: TNNNN */" comments, plus fallback ---
$splunkFiles = @()
if (Test-Path -LiteralPath $splunkPath) {
    $splunkFiles = Get-ChildItem -Recurse -Path $splunkPath -Filter *.spl -ErrorAction SilentlyContinue
}
foreach ($f in $splunkFiles) {
    $text = Get-Content -LiteralPath $f.FullName -Raw
    $fileHits = 0
    foreach ($m in [regex]::Matches($text, '(?im)(?:^\s*#|/\*)\s*MITRE\s*:\s*T(\d{4})(?:\.(\d{1,3}))?')) {
        $tid = "T" + $m.Groups[1].Value
        if ($m.Groups[2].Success) { $tid += "." + $m.Groups[2].Value }
        Add-Hit -Technique $tid -FilePath $f.FullName
        $fileHits++
    }
    # Fallback: bare T#### comment references
    foreach ($m in [regex]::Matches($text, '\bT(\d{4})(?:\.(\d{1,3}))?\b')) {
        $tid = "T" + $m.Groups[1].Value
        if ($m.Groups[2].Success) { $tid += "." + $m.Groups[2].Value }
        Add-Hit -Technique $tid -FilePath $f.FullName
    }
    if ($VerboseMode) { Write-Host ("splunk {0}: {1} # MITRE: hits" -f $f.Name, $fileHits) }
}

$techniqueCount = $techniqueMap.Keys.Count
if ($techniqueCount -eq 0) {
    Write-Error "verify-mitre: zero MITRE techniques discovered. Check parser patterns or rule content."
    exit 2
}

# Family = technique ID without sub-technique (e.g. T1558.003 -> T1558)
$families = [System.Collections.Generic.HashSet[string]]::new()
foreach ($t in $techniqueMap.Keys) {
    $families.Add(($t -split '\.')[0]) | Out-Null
}
$familyCount = $families.Count

# --- Write CSV: Technique,Family,FileList,FileCount ---
$csvDir = Split-Path -Parent $csvOutPath
if ($csvDir -and -not (Test-Path -LiteralPath $csvDir)) {
    New-Item -ItemType Directory -Path $csvDir -Force | Out-Null
}
$csvLines = New-Object System.Collections.Generic.List[string]
$csvLines.Add("Technique,Family,FileList,FileCount") | Out-Null
foreach ($t in ($techniqueMap.Keys | Sort-Object)) {
    $family = ($t -split '\.')[0]
    $files  = ($techniqueMap[$t] | Sort-Object) -join ';'
    $count  = $techniqueMap[$t].Count
    $csvLines.Add(("{0},{1},{2},{3}" -f $t, $family, $files, $count)) | Out-Null
}
Set-Content -LiteralPath $csvOutPath -Value $csvLines -Encoding UTF8

# --- Write MD summary ---
$mdDir = Split-Path -Parent $mdOutPath
if ($mdDir -and -not (Test-Path -LiteralPath $mdDir)) {
    New-Item -ItemType Directory -Path $mdDir -Force | Out-Null
}

$top = $techniqueMap.GetEnumerator() | Sort-Object -Property @{Expression={$_.Value.Count}; Descending=$true}, @{Expression={$_.Key}} | Select-Object -First 10
$mdLines = New-Object System.Collections.Generic.List[string]
$mdLines.Add("# Verified MITRE ATT&CK Coverage") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("This file is generated from live detection rule content by ``scripts/verify/verify-mitre.ps1``.") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("---") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("## Summary") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("| Metric | Value |") | Out-Null
$mdLines.Add("|---|---|") | Out-Null
$mdLines.Add("| Unique techniques (T####[.###]) | **$techniqueCount** |") | Out-Null
$mdLines.Add("| Unique technique families (T####) | **$familyCount** |") | Out-Null
$mdLines.Add("| Sigma YAML files scanned | $($sigmaFiles.Count) |") | Out-Null
$mdLines.Add("| Wazuh XML files scanned | $($wazuhFiles.Count) |") | Out-Null
$mdLines.Add("| Splunk SPL files scanned | $($splunkFiles.Count) |") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("## Top 10 techniques by rule coverage") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("| Technique | Family | # Rule files |") | Out-Null
$mdLines.Add("|---|---|---|") | Out-Null
foreach ($entry in $top) {
    $fam = ($entry.Key -split '\.')[0]
    $mdLines.Add("| $($entry.Key) | $fam | $($entry.Value.Count) |") | Out-Null
}
$mdLines.Add("") | Out-Null
$mdLines.Add("## Verification commands") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("    pwsh -NoProfile -File .\scripts\verify\verify-mitre.ps1") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("Full per-technique provenance is in ``PROOF_PACK/VERIFIED_MITRE.csv`` (columns: Technique, Family, FileList, FileCount).") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("---") | Out-Null
$mdLines.Add("") | Out-Null
$mdLines.Add("_Regenerate after adding or removing detection rules._") | Out-Null
Set-Content -LiteralPath $mdOutPath -Value $mdLines -Encoding UTF8

Write-Host "======================================"
Write-Host "HawkinsOps MITRE ATT&CK Coverage"
Write-Host "======================================"
Write-Host ""
Write-Host "Unique techniques:  $techniqueCount"
Write-Host "Unique families:    $familyCount"
Write-Host "Sigma files:        $($sigmaFiles.Count)"
Write-Host "Wazuh files:        $($wazuhFiles.Count)"
Write-Host "Splunk files:       $($splunkFiles.Count)"
Write-Host ""
Write-Host "Wrote CSV: $csvOutPath"
Write-Host "Wrote MD:  $mdOutPath"
exit 0
