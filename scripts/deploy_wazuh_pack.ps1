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
  $ids = [System.Collections.Generic.HashSet[string]]::new()
  if (-not (Test-Path -LiteralPath $Path)) { return ,$ids }
  $content = Get-Content -LiteralPath $Path -Raw
  foreach ($m in [regex]::Matches($content, '<rule\s+id="(\d+)"')) {
    [void]$ids.Add($m.Groups[1].Value)
  }
  # Comma prevents PowerShell from unrolling the HashSet into the output
  # stream, which would drop empty collections to $null and downgrade
  # populated ones to string[] — breaking .Count and .Contains under
  # Set-StrictMode -Version Latest.
  return ,$ids
}

function Get-RemoteRuleIds {
  param(
    [string]$RemotePath,
    [string]$RemoteHost,
    [string]$User,
    [int]$Port,
    [string]$KeyPath
  )
  $check = "sudo -n test -f '$RemotePath' && sudo -n grep -oE 'id=`"[0-9]+`"' '$RemotePath' || true"
  $raw = Invoke-Ssh -RemoteHost $RemoteHost -User $User -Port $Port -KeyPath $KeyPath -Command $check
  $ids = [System.Collections.Generic.HashSet[string]]::new()
  if ($raw) {
    foreach ($line in ($raw -split "`n")) {
      if ($line -match 'id="(\d+)"') { [void]$ids.Add($matches[1]) }
    }
  }
  return ,$ids
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
  # ssh uses -p <port>. scp uses -P <port> ('-p' in scp means preserve
  # times/modes, a no-arg flag — passing '-p 22' makes scp try to copy a
  # file literally named '22' and fail). The -ForScp switch returns the
  # right shape.
  #
  # BatchMode=yes: never prompt the user. On a runner with no tty this
  # is the difference between hanging forever and failing fast.
  # StrictHostKeyChecking=accept-new: first contact with a host stores
  # its key automatically; any subsequent mismatch fails loudly. Safer
  # than UserKnownHostsFile=/dev/null (which blindly accepts any key).
  # ConnectTimeout=20: bound the time the TCP handshake can stall.
  param([int]$Port, [string]$KeyPath, [switch]$ForScp)
  $portFlag = if ($ForScp) { "-P" } else { "-p" }
  $opts = @(
    $portFlag, "$Port",
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=20"
  )
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
  # Normalize CRLF → LF so multi-line here-strings authored in PowerShell
  # on Windows don't ship literal \r bytes to the remote bash, which would
  # break with: bash: line N: $'\r': command not found.
  $cmd = $Command -replace "`r`n", "`n"
  & ssh @opts "$User@$RemoteHost" $cmd 2>&1
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
  $opts = Get-SshOptions -Port $Port -KeyPath $KeyPath -ForScp
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
# Staging directory the SSH user can write to. scp uploads here as the
# SSH user; then sudo cp -a moves files into /var/ossec/etc/... with the
# correct ownership. Keeps the SSH user out of privileged write paths.
$remoteStage = "/tmp/wazuh_pack_stage_$remoteStamp"

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

  $mkdirCmd = "sudo -n mkdir -p $backupRoot '$remoteBackupDir' $rulesDest $decodersDest $listsDest && mkdir -p '$remoteStage/rules' '$remoteStage/decoders' '$remoteStage/lists'"
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $mkdirCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  $backupCmd = "sudo -n cp -a $rulesDest '$remoteBackupDir/rules_backup' && sudo -n cp -a $decodersDest '$remoteBackupDir/decoders_backup' && sudo -n cp -a $listsDest '$remoteBackupDir/lists_backup'"
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
    Copy-WithScp -SourceGlob "$packPath/rules/*.xml" -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir "$remoteStage/rules/" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  if (Test-Path -LiteralPath (Join-Path $packPath "decoders")) {
    Copy-WithScp -SourceGlob "$packPath/decoders/*.xml" -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir "$remoteStage/decoders/" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  if (Test-Path -LiteralPath (Join-Path $packPath "lists")) {
    Copy-WithScp -SourceGlob "$packPath/lists/*" -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -DestinationDir "$remoteStage/lists/" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  }

  # Install from staging into /var/ossec/etc/... as root, then fix ownership.
  # Staging keeps the SSH user out of privileged write paths (scp writes to
  # /tmp, sudo cp promotes). chown matches the standard Wazuh layout
  # (root:wazuh, 0640 files / 0750 dirs inherited from parent).
  "## Install staged pack into live /var/ossec/etc paths" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  $installCmd = @"
sudo -n cp -a $remoteStage/rules/. $rulesDest && \
sudo -n cp -a $remoteStage/decoders/. $decodersDest && \
sudo -n cp -a $remoteStage/lists/. $listsDest && \
sudo -n chown -R root:wazuh $rulesDest $decodersDest $listsDest
"@
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $installCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  # xmllint soft check. Wazuh rule files legitimately have multiple top-level
  # <group> blocks; wrap each file in a synthetic root on the fly before
  # piping to xmllint so it can actually validate well-formedness.
  $xmllintCmd = @'
if command -v xmllint >/dev/null 2>&1; then
  for f in /var/ossec/etc/rules/*.xml /var/ossec/etc/decoders/*.xml; do
    [ -f "$f" ] || continue
    ( printf '<__root__>'; sudo -n cat "$f"; printf '</__root__>' ) | xmllint --noout - 2>&1 | sed "s|^|xmllint($(basename "$f")): |" || true
  done
else
  echo 'xmllint not available; skipping'
fi
'@
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command $xmllintCmd | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  "## wazuh-analysisd -t (hard gate: fails loudly on any Wazuh semantic error)" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  $analysisdOutput = Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "sudo -n /var/ossec/bin/wazuh-analysisd -t; echo EXIT=`$?"
  $analysisdOutput | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  $analysisdExit = $null
  foreach ($line in ($analysisdOutput -split "`n")) {
    if ($line -match '^EXIT=(\d+)') { $analysisdExit = [int]$matches[1] }
  }
  $analysisdBad = ($null -eq $analysisdExit) -or ($analysisdExit -ne 0) -or ($analysisdOutput -match 'ERROR|CRITICAL')
  if ($analysisdBad) {
    "## AUTO-ROLLBACK: analysisd gate failed, restoring from $remoteBackupDir" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
    $rollbackCmd = "sudo -n cp -a '$remoteBackupDir/rules_backup/.' $rulesDest && sudo -n cp -a '$remoteBackupDir/decoders_backup/.' $decodersDest && sudo -n cp -a '$remoteBackupDir/lists_backup/.' $listsDest && sudo -n chown -R root:wazuh $rulesDest $decodersDest $listsDest"
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

  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "sudo -n systemctl restart $managerService" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "sudo -n systemctl is-active $managerService" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8
  Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "sudo -n tail -n 80 /var/ossec/logs/ossec.log" | Out-File -LiteralPath $validationOut -Append -Encoding UTF8

  $summary.Add("## Deployment") | Out-Null
  $summary.Add("- Status: SUCCESS") | Out-Null
  $summary.Add("- Manager service restart attempted: yes") | Out-Null
  $summary.Add("- Post-checks captured in validation_output.txt") | Out-Null
  $summary.Add("") | Out-Null
  $summary.Add("## Rollback") | Out-Null
  $summary.Add('```bash') | Out-Null
  $summary.Add("cp -a '$remoteBackupDir/rules_backup/.' $rulesDest") | Out-Null
  $summary.Add("cp -a '$remoteBackupDir/decoders_backup/.' $decodersDest") | Out-Null
  $summary.Add("cp -a '$remoteBackupDir/lists_backup/.' $listsDest") | Out-Null
  $summary.Add("systemctl restart $managerService") | Out-Null
  $summary.Add('```') | Out-Null
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
  if ($hostName -and $sshUser -and $remoteStage) {
    try {
      Invoke-Ssh -RemoteHost $hostName -User $sshUser -Port $sshPort -KeyPath $sshKey -Command "rm -rf '$remoteStage'" | Out-Null
    } catch {
      Write-Warning "Failed to clean up remote staging dir $remoteStage`: $($_.Exception.Message)"
    }
  }
  if ($sshKeyTemp -and (Test-Path -LiteralPath $sshKeyTemp)) {
    try { Remove-Item -LiteralPath $sshKeyTemp -Force -ErrorAction Stop }
    catch { Write-Warning "Failed to remove temp SSH key $sshKeyTemp`: $($_.Exception.Message)" }
  }
}


