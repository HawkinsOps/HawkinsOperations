param(
  [string]$PackRoot = "content/wazuh/pack"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
  param([string]$RelativePath)
  $full = Join-Path -Path (Get-Location) -ChildPath $RelativePath
  return [System.IO.Path]::GetFullPath($full)
}

$packPath = Resolve-RepoPath -RelativePath $PackRoot
$rulesPath = Join-Path $packPath "rules"
$decodersPath = Join-Path $packPath "decoders"
$listsPath = Join-Path $packPath "lists"

$errors = New-Object System.Collections.Generic.List[string]
$validatedXml = New-Object System.Collections.Generic.List[string]

if (-not (Test-Path -LiteralPath $packPath)) { $errors.Add("Missing pack root: $PackRoot") | Out-Null }
if (-not (Test-Path -LiteralPath $rulesPath)) { $errors.Add("Missing rules directory: $rulesPath") | Out-Null }
if (-not (Test-Path -LiteralPath $listsPath)) { $errors.Add("Missing lists directory: $listsPath") | Out-Null }

$ruleXml = @()
if (Test-Path -LiteralPath $rulesPath) {
  $ruleXml = Get-ChildItem -LiteralPath $rulesPath -Filter *.xml -File
  if ($ruleXml.Count -eq 0) { $errors.Add("No XML files found in rules directory: $rulesPath") | Out-Null }
}

function Test-WazuhXml {
  param([string]$Path)
  $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
  # Wazuh rule/decoder files frequently contain multiple top-level <group>
  # blocks plus leading/trailing comments. Wrap in a synthetic root so the
  # XML parser can validate well-formedness without requiring content edits.
  $stripped = $raw -replace '^\s*<\?xml[^?]*\?>\s*', ''
  [xml]$null = "<__root__>$stripped</__root__>"
}

foreach ($file in $ruleXml) {
  try {
    Test-WazuhXml -Path $file.FullName
    $validatedXml.Add($file.FullName) | Out-Null
  } catch {
    $errors.Add("XML parse failure in rule file '$($file.FullName)': $($_.Exception.Message)") | Out-Null
  }
}

if (Test-Path -LiteralPath $decodersPath) {
  $decoderXml = Get-ChildItem -LiteralPath $decodersPath -Filter *.xml -File
  foreach ($file in $decoderXml) {
    try {
      Test-WazuhXml -Path $file.FullName
      $validatedXml.Add($file.FullName) | Out-Null
    } catch {
      $errors.Add("XML parse failure in decoder file '$($file.FullName)': $($_.Exception.Message)") | Out-Null
    }
  }
}

Write-Host "Wazuh pack validation summary"
Write-Host "- Pack root: $packPath"
Write-Host "- Rules XML validated: $($ruleXml.Count)"
Write-Host "- Total XML validated: $($validatedXml.Count)"

if ($errors.Count -gt 0) {
  Write-Host "- Status: FAIL" -ForegroundColor Red
  $errors | ForEach-Object { Write-Host "  * $_" -ForegroundColor Red }
  exit 1
}

Write-Host "- Status: PASS" -ForegroundColor Green
exit 0

