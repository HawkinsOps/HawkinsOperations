# Verification script - counts detection and IR content from repo root.
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

$sigmaYml = (Get-ChildItem -Recurse -Filter *.yml -Path (Join-Path $repoRoot "content\detection-rules\sigma") -ErrorAction SilentlyContinue).Count
$sigmaYaml = (Get-ChildItem -Recurse -Filter *.yaml -Path (Join-Path $repoRoot "content\detection-rules\sigma") -ErrorAction SilentlyContinue).Count
$sigma = $sigmaYml + $sigmaYaml
$splunkFiles = (Get-ChildItem -Recurse -Filter *.spl -Path (Join-Path $repoRoot "content\detection-rules\splunk") -ErrorAction SilentlyContinue).Count
$splunk = (Get-ChildItem -Recurse -Filter *.spl -Path (Join-Path $repoRoot "content\detection-rules\splunk") -ErrorAction SilentlyContinue |
    Select-String -Pattern '^# .+ - T\d+|^# MITRE: T\d+' | Measure-Object).Count
$wazuhXmlFiles = (Get-ChildItem -Recurse -Filter *.xml -Path (Join-Path $repoRoot "content\detection-rules\wazuh\rules") -ErrorAction SilentlyContinue).Count
$wazuhRuleBlocks = (Get-ChildItem -Recurse -Filter *.xml -Path (Join-Path $repoRoot "content\detection-rules\wazuh\rules") -ErrorAction SilentlyContinue |
    Select-String -Pattern "<rule id=" | Measure-Object).Count
$playbooks = (Get-ChildItem -Recurse -Filter IR-*.md -Path (Join-Path $repoRoot "content\incident-response\playbooks") -ErrorAction SilentlyContinue).Count

Write-Host "======================================"
Write-Host "HawkinsOps Detection Content Counts"
Write-Host "======================================"
Write-Host ""
Write-Host "Sigma (.yml/.yaml files): $sigma"
Write-Host "Splunk (.spl files):      $splunkFiles"
Write-Host "Splunk (searches):        $splunk"
Write-Host "Wazuh XML files:          $wazuhXmlFiles"
Write-Host "Wazuh <rule id=> blocks:  $wazuhRuleBlocks"
Write-Host "IR Playbooks (IR-*.md):   $playbooks"
Write-Host ""
Write-Host "======================================"
