Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath "."
$hookDir = Join-Path -Path $repoRoot -ChildPath ".git/hooks"
$hookPath = Join-Path -Path $hookDir -ChildPath "pre-commit"

if (-not (Test-Path -LiteralPath $hookDir)) {
  throw ".git/hooks was not found. Run this from repository root."
}

$hookBody = @"
#!/bin/sh
pwsh -NoProfile -File "./scripts/verify/staged-scope-check.ps1"
if [ `$? -ne 0 ]; then
  echo "Commit blocked by staged scope check."
  exit 1
fi
pwsh -NoProfile -File "./scripts/verify/public-safety-scan.ps1"
if [ `$? -ne 0 ]; then
  echo "Commit blocked by public safety scan."
  exit 1
fi
pwsh -NoProfile -File "./scripts/verify/autosoc-publish-contract-scan.ps1"
if [ `$? -ne 0 ]; then
  echo "Commit blocked by AutoSOC publish contract scan."
  exit 1
fi
"@

Set-Content -LiteralPath $hookPath -Value $hookBody -NoNewline -Encoding UTF8
Write-Host "Installed pre-commit hook: $hookPath"
