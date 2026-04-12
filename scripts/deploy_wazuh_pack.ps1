param(
  [string]$PackRoot = "content/wazuh/pack",
  [switch]$AllowRuleIdLoss
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-Stamp {
  return Get-Date -Format "MM-dd-yyyy_HHmmss"
}

function Get-RuleIdsFromFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return @() }
  $content = Get-Content -LiteralPath $Path -Raw
  $ids = [System.Collections.Generic.HashSet[string]]::new()
  foreach ($m in [regex]::Matches($content, '<rule\s+id="(\d+)"')) {
    [void]$ids.Add($m.Groups[1].Value)
  }
  return $ids
}

function Get-RemoteRuleIds {
  param(
    [string]$RemotePath,
    [string]$RemoteHost,
    [string]$User,
    [int]$Port,
    [string]$KeyPath
  )
  $check = "[ -f '$RemotePath' ] && grep -oE 'id=`"[0-9]+`"' '$RemotePath' || true"
  $raw = Invoke-Ssh -RemoteHost $RemoteHost -User $User -Port $Port -KeyPath $KeyPath -Command $check
  $ids = [System.Collections.Generic.HashSet[string]]::new()
  foreach ($line in ($raw -split "`n")) {
    if ($line -match 'id="(\d+)"') { [void]$ids.Add($matches[1]) }
  }
  return $ids
}

function Assert-SafeOverwrite {
  param(
    [string]$LocalFile,
    [string]$RemotePath,
    [string]$RemoteHost,
    [string]$User,
    [int]$Port,
    [string]$KeyPath,
    [bool]$Allow
  )
  $localIds  = Get-RuleIdsFromFile -Path $LocalFile
  $remoteIds = Get-RemoteRuleIds -RemotePath $RemotePath -RemoteHost $RemoteHost -User $User -Port $Port -KeyPath $KeyPath
  if ($remoteIds.Count -eq 0) { return }
  $lost = @($remoteIds | Where-Object { -not $localIds.Contains($_) })
  if ($lost.Count -gt 0) {
    $msg = "DESTRUCTIVE OVERWRITE REFUSED for $RemotePath. Live file has " +
           "$($lost.Count) rule ID(s) that the repo file does not: " +
           "$($lost -join ', '). Reconcile the repo from live first, " +
           "or pass -AllowRuleIdLoss to override."
    if ($Allow) {
      Write-Warning ("OVERRIDE: " + $msg)
    } else {
      throw $msg
    }
  }
}

function New-EvidenceDir {
  $stamp = Get-Stamp
  $runDir = Join-Path (Get-Location) "evidence/wazuh/run_$stamp"
  New-Item -ItemType Directory -Path $runDir -Force | Out-Null
  return $runDir
}

function Get-SshOptions {
  param([int]$Port, [string]$KeyPath)
  $opts = @("-p", "$Port")
  if ($KeyPath) { $opts += @("-i", $KeyPath) }
  return $opts
}

function Invoke-Ssh {
  param(
    [string]$RemoteHost,
    [string]$User,
    [int]$Port,
    [string]$KeyPath,
    [string]$Command
  )
  $opts = Get-SshOptions -Port $Port -KeyPath $KeyPath
  & ssh @opts "$User@$RemoteHost" $Command 2>&1
}

function Copy-WithScp {
  param(
    [string]$SourceGlob,
    [string]$RemoteHost,
    [string]$User,
    [int]$Port,
    [string]$KeyPath,
    [string]$DestinationDir
  )
  $opts = Get-SshOptions -Port $Port -KeyPath $KeyPath
  & scp @opts $SourceGlob "$User@$RemoteHost`:$DestinationDir" 2>&1
}

function Resolve-SshKey {
  param([string]$Raw)
  if (-not $Raw) { return @{ Path = ""; Temp = $null } }
  $looksLikeContent = ($Raw -match '-----BEGIN ') -or ($Raw -match "`n")
  if (-not $looksLikeContent) {
    if (Test-Path -LiteralPath $Raw) { return @{ Path = $Raw; Temp = $null } }
    return @{ Path = $Raw; Temp = $null }
  }
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("wazuh_deploy_key_" + [guid]::NewGuid().ToString("N"))
  $normalized = $Raw -replace "`r`n", "`n"
  if (-not $normalized.EndsWith("`n")) { $normalized += "`n" }
  [System.IO.File]::WriteAllText($tmp, $normalized, [System.Text.UTF8Encoding]::new($false))
  if ($IsLinux -or $IsMacOS) {
    & chmod 600 $tmp 2>&1 | Out-Null
  } else {
    try {
      $acl = Get-Acl -LiteralPath $tmp
      $acl.SetAccessRuleProtection($true, $false)
      foreach ($rule in @($acl.Access)) { [void]$acl.RemoveAccessRule($rule) }
      $me = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
      $ar = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $me, "FullControl", "Allow")
      $acl.SetAccessRule($ar)
      Set-Acl -LiteralPath $tmp -AclObject $acl
    } catch {
      Write-Warning "Could not tighten ACL on temp SSH key $tmp`: $($_.Exception.Message)"
    }
  }
  return @{ Path = $tmp; Temp = $tmp }
}

$hostName = if ($env:WAZUH_HOST) { $env:WAZUH_HOST } else { "[REDACTED_IP]" }
$sshUser = if ($env:WAZUH_SSH_USER) { $env:WAZUH_SSH_USER } else { "root" }
$sshPort = if ($env:WAZUH_SSH_PORT) { [int]$env:WAZUH_SSH_PORT } else { 22 }
$sshKeyRaw = if ($env:WAZUH_SSH_KEY) { $env:WAZUH_SSH_KEY } else { "" }
$sshKeyResolved = Resolve-SshKey -Raw $sshKeyRaw
$sshKey = $sshKeyResolved.Path
$sshKeyTemp = $sshKeyResolved.Temp

$rulesDest = "/var/ossec/etc/rules/"
$decodersDest = "/var/ossec/etc/decoders/"
$listsDest = "/var/ossec/etc/lists/"
$backupRoot = "/var/ossec/backup"
$managerService = "wazuh-manager"

$packPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $PackRoot))
$runDir = New-EvidenceDir
$validationOut = Join-Path $runDir "validation_output.txt"
$deployReport = Join-Path $runDir "deploy_report.md"
$remoteStamp = Get-Date -Format "MM-dd-yyyy_HHmmss"
$remoteBackupDir = "$backupRoot/wazuh_pack_$remoteStamp"

$summary = New-Object System.Collections.Generic.List[string]
$summary.Add("# Wazuh Pack Deployment Report") | Out-Null
$summary.Add("") | Out-Null
$summary.Add("- Date: $(Get-Date -Format 'MM-dd-yyyy HH:mm:ss')") | Out-Null
$summary.Add("- Host: $hostName") | Out-Null
$summary.Add("- SSH user: $sshUser") | Out-Null
$summary.Add("- Pack root: $PackRoot") | Out-Null
$summary.Add("- Remote backup dir: $remoteBackupDir") | Out-Null
$summary.Add("") | Out-Null

try {
  $validateOutput = & pwsh -NoProfile -File ".\scripts\validate_wazuh_pack.ps1" -PackRoot $PackRoot 2>&1
  $validateOutput | Out-File -LiteralPath $validationOut -Encoding UTF8
  if ($LASTEXITCODE -ne 0) { throw "validate_wazuh_pack.ps1 failed. See validation_output.txt" }

  $summary.Add("## Validation") | Out-Null
  $summary.Add("- Status: PASS") | Out-Null
  $summary.Add("") | Out-Null

  $mkdirCmd = "mkdir -p $backupRoot '$remoteBackupDir' $rulesDest $decodersDest $listsDest"
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $mkdirCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  $backupCmd = "cp -a $rulesDest '$remoteBackupDir/rules_backup' && cp -a $decodersDest '$remoteBackupDir/decoders_backup' && cp -a $listsDest '$remoteBackupDir/lists_backup'"
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $backupCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  "## Pre-deploy rule-ID diff guard" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  $rulesLocalDir = Join-Path $packPath "rules"
  if (Test-Path -LiteralPath $rulesLocalDir) {
    foreach ($f in Get-ChildItem -LiteralPath $rulesLocalDir -Filter *.xml) {
      $remote = ($rulesDest.TrimEnd('/')) + "/" + $f.Name
      Assert-SafeOverwrite -LocalFile $f.FullName -RemotePath $remote `
        -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey `
        -Allow ([bool]$AllowRuleIdLoss)
      "- $($f.Name): rule-ID diff guard PASS" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
    }
  }
  $decodersLocalDir = Join-Path $packPath "decoders"
  if (Test-Path -LiteralPath $decodersLocalDir) {
    foreach ($f in Get-ChildItem -LiteralPath $decodersLocalDir -Filter *.xml) {
      $remote = ($decodersDest.TrimEnd('/')) + "/" + $f.Name
      Assert-SafeOverwrite -LocalFile $f.FullName -RemotePath $remote `
        -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey `
        -Allow ([bool]$AllowRuleIdLoss)
      "- $($f.Name): rule-ID diff guard PASS" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
    }
  }

  if (Test-Path -LiteralPath (Join-Path $packPath "rules")) {
    Copy-WithScp -SourceGlob "$packPath/rules/*.xml" -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir $rulesDest | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  if (Test-Path -LiteralPath (Join-Path $packPath "decoders")) {
    Copy-WithScp -SourceGlob "$packPath/decoders/*.xml" -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir $decodersDest | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  if (Test-Path -LiteralPath (Join-Path $packPath "lists")) {
    Copy-WithScp -SourceGlob "$packPath/lists/*" -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir $listsDest | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  $xmllintCmd = "if command -v xmllint >/dev/null 2>&1; then xmllint --noout $rulesDest/*.xml; [ -d $decodersDest ] && ls $decodersDest/*.xml >/dev/null 2>&1 && xmllint --noout $decodersDest/*.xml || true; else echo 'xmllint not available; skipping'; fi"
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $xmllintCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  "## wazuh-analysisd -t (hard gate: fails loudly on any Wazuh semantic error)" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  $analysisdOutput = Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "/var/ossec/bin/wazuh-analysisd -t; echo EXIT=`$?"
  $analysisdOutput | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  $analysisdExit = $null
  foreach ($line in ($analysisdOutput -split "`n")) {
    if ($line -match '^EXIT=(\d+)') { $analysisdExit = [int]$matches[1] }
  }
  $analysisdBad = ($null -eq $analysisdExit) -or ($analysisdExit -ne 0) -or ($analysisdOutput -match 'ERROR|CRITICAL')
  if ($analysisdBad) {
    "## AUTO-ROLLBACK: analysisd gate failed, restoring from $remoteBackupDir" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
    $rollbackCmd = "cp -a '$remoteBackupDir/rules_backup/.' $rulesDest && cp -a '$remoteBackupDir/decoders_backup/.' $decodersDest && cp -a '$remoteBackupDir/lists_backup/.' $listsDest && chown -R root:wazuh $rulesDest $decodersDest $listsDest"
    Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $rollbackCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
    throw "wazuh-analysisd -t failed (exit=$analysisdExit). Ruleset has a semantic error. Files rolled back from $remoteBackupDir. Manager was NOT restarted. Inspect validation_output.txt."
  }

  $sampleLocal = Join-Path $packPath "tests/log_samples/powershell_encodedcommand.json"
  if (Test-Path -LiteralPath $sampleLocal) {
    $tmpSample = "/tmp/wazuh_logtest_sample.json"
    Copy-WithScp -SourceGlob $sampleLocal -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir $tmpSample | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
    $logtestCmd = "if [ -x /var/ossec/bin/wazuh-logtest ]; then cat $tmpSample | /var/ossec/bin/wazuh-logtest; else echo 'wazuh-logtest not available; skipping'; fi"
    Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $logtestCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  } else {
    "No local log sample found at $sampleLocal; skipping wazuh-logtest." | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "systemctl restart $managerService" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "systemctl is-active $managerService" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "tail -n 80 /var/ossec/logs/ossec.log" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  $summary.Add("## Deployment") | Out-Null
  $summary.Add("- Status: SUCCESS") | Out-Null
  $summary.Add("- Manager service restart attempted: yes") | Out-Null
  $summary.Add("- Post-checks captured in validation_output.txt") | Out-Null
  $summary.Add("") | Out-Null
  $summary.Add("## Rollback") | Out-Null
  $summary.Add("```bash") | Out-Null
  $summary.Add("cp -a '$remoteBackupDir/rules_backup/.' $rulesDest") | Out-Null
  $summary.Add("cp -a '$remoteBackupDir/decoders_backup/.' $decodersDest") | Out-Null
  $summary.Add("cp -a '$remoteBackupDir/lists_backup/.' $listsDest") | Out-Null
  $summary.Add("systemctl restart $managerService") | Out-Null
  $summary.Add("```") | Out-Null
}
catch {
  $summary.Add("## Deployment") | Out-Null
  $summary.Add("- Status: FAILED") | Out-Null
  $summary.Add("- Error: $($_.Exception.Message)") | Out-Null
  $summary.Add("") | Out-Null
  throw
}
finally {
  $summary | Out-File -LiteralPath $deployReport -Encoding UTF8
  if ($sshKeyTemp -and (Test-Path -LiteralPath $sshKeyTemp)) {
    try { Remove-Item -LiteralPath $sshKeyTemp -Force -ErrorAction Stop }
    catch { Write-Warning "Failed to remove temp SSH key $sshKeyTemp`: $($_.Exception.Message)" }
  }
}


