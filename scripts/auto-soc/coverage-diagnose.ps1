param(
    [int]$WindowHours = 168,
    [switch]$QueryIndexer,
    [switch]$InsecureTls
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$opsRoot = "C:\RH\OPS"
$autoRoot = Join-Path $opsRoot "30_Projects\Active\AutoSOC"
$configRoot = Join-Path $autoRoot "Build\Config"
$queueProcessed = Join-Path $autoRoot "Build\Queue\Processed"
$outputRoot = Join-Path $autoRoot "Output"

$inventoryPath = Join-Path $configRoot "agent_inventory.json"
$dotenvPath = Join-Path $configRoot ".env"
$jsonOutPath = Join-Path $outputRoot "coverage_diagnose_latest.json"
$mdOutPath = Join-Path $outputRoot "coverage_diagnose_latest.md"
$managerAgentsPath = Join-Path $outputRoot "manager_agents_latest.json"

function Read-Json {
    param([string]$Path)
    Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 100
}

function Get-ObjValue {
    param(
        [object]$Object,
        [string]$Name,
        [object]$Default = $null
    )
    if ($null -eq $Object) { return $Default }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $Default }
    if ($null -eq $prop.Value) { return $Default }
    return $prop.Value
}

function Normalize-Token {
    param([string]$Value)
    $s = [string]$Value
    $s = $s.Trim().ToLower()
    if ($s.Contains(".")) {
        $s = $s.Split(".", 2)[0]
    }
    return $s.Replace("_", "-")
}

function Build-Aliases {
    param([string]$Hostname, [object[]]$ExplicitAliases)
    $base = Normalize-Token $Hostname
    $aliases = New-Object System.Collections.Generic.HashSet[string]
    if ($base) { [void]$aliases.Add($base) }
    if ($base.EndsWith("-01")) { [void]$aliases.Add($base.Substring(0, $base.Length - 3)) }
    if ($base) { [void]$aliases.Add($base.Replace("-", "_")) }
    foreach ($a in ($ExplicitAliases | ForEach-Object { [string]$_ })) {
        $n = Normalize-Token $a
        if ($n) { [void]$aliases.Add($n) }
    }
    return @($aliases)
}

function Parse-DotEnv {
    param([string]$Path)
    $map = @{}
    if (-not (Test-Path -LiteralPath $Path)) { return $map }
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trim = $line.Trim()
        if (-not $trim -or $trim.StartsWith("#") -or -not $trim.Contains("=")) { continue }
        $parts = $trim.Split("=", 2)
        $k = $parts[0].Trim()
        $v = $parts[1].Trim()
        if ($k) { $map[$k] = $v }
    }
    return $map
}

function Get-Secret {
    param([hashtable]$DotEnv)
    if ($env:WAZUH_INDEXER_PASS) { return [string]$env:WAZUH_INDEXER_PASS }
    if ($env:WAZUH_INDEXER_PASS_FILE -and (Test-Path -LiteralPath $env:WAZUH_INDEXER_PASS_FILE)) {
        return (Get-Content -LiteralPath $env:WAZUH_INDEXER_PASS_FILE -Raw).Trim()
    }
    if ($DotEnv.ContainsKey("WAZUH_INDEXER_PASS_FILE") -and (Test-Path -LiteralPath $DotEnv["WAZUH_INDEXER_PASS_FILE"])) {
        return (Get-Content -LiteralPath $DotEnv["WAZUH_INDEXER_PASS_FILE"] -Raw).Trim()
    }
    if ($DotEnv.ContainsKey("WAZUH_INDEXER_PASS")) { return [string]$DotEnv["WAZUH_INDEXER_PASS"] }
    return ""
}

function Get-IndexerCount {
    param(
        [string]$HostUrl,
        [string]$IndexPattern,
        [string]$User,
        [string]$Password,
        [string[]]$Aliases,
        [int]$WindowHours,
        [bool]$Insecure
    )
    if (-not $HostUrl -or -not $User -or -not $Password) {
        return [pscustomobject]@{
            count = $null
            error = "missing indexer host/user/password"
        }
    }

    $fields = @("agent.name", "agent.hostname", "host.hostname", "manager.name", "location")
    $terms = @($Aliases | ForEach-Object { '"{0}"' -f $_ })
    if ($terms.Count -eq 0) {
        return [pscustomobject]@{
            count = $null
            error = "no alias terms"
        }
    }
    $queryText = $terms -join " OR "

    $body = @{
        size  = 0
        query = @{
            bool = @{
                filter = @(
                    @{
                        range = @{
                            "@timestamp" = @{
                                gte = "now-$($WindowHours)h"
                            }
                        }
                    }
                )
                must = @(
                    @{
                        simple_query_string = @{
                            query            = $queryText
                            fields           = $fields
                            default_operator = "or"
                        }
                    }
                )
            }
        }
    } | ConvertTo-Json -Depth 10

    $url = "{0}/{1}/_search" -f $HostUrl.TrimEnd("/"), $IndexPattern
    $pair = "{0}:{1}" -f $User, $Password
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($pair)
    $basic = [Convert]::ToBase64String($bytes)
    $headers = @{
        Authorization = "Basic $basic"
        "Content-Type" = "application/json"
    }

    $oldCallback = $null
    if ($Insecure) {
        $oldCallback = [System.Net.ServicePointManager]::ServerCertificateValidationCallback
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
    }
    try {
        $irmArgs = @{
            Method = "Post"
            Uri = $url
            Headers = $headers
            Body = $body
            TimeoutSec = 20
        }
        if ($Insecure) {
            $irmArgs["SkipCertificateCheck"] = $true
        }
        $resp = Invoke-RestMethod @irmArgs
        return [pscustomobject]@{
            count = [int]$resp.hits.total.value
            error = ""
        }
    } catch {
        return [pscustomobject]@{
            count = $null
            error = $_.Exception.Message
        }
    } finally {
        if ($Insecure) {
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $oldCallback
        }
    }
}

function Get-ManagerState {
    param(
        [string]$Hostname,
        [string[]]$Aliases,
        [hashtable]$ManagerMap
    )
    $tokens = New-Object System.Collections.Generic.List[string]
    $tokens.Add((Normalize-Token $Hostname)) | Out-Null
    foreach ($a in $Aliases) {
        $n = Normalize-Token ([string]$a)
        if ($n) { $tokens.Add($n) | Out-Null }
    }
    foreach ($t in $tokens) {
        if (-not $t) { continue }
        if ($ManagerMap.ContainsKey($t)) {
            return [string]$ManagerMap[$t]
        }
    }
    return "NOT_ENROLLED_OR_UNKNOWN"
}

if (-not (Test-Path -LiteralPath $inventoryPath)) {
    throw "Missing inventory file: $inventoryPath"
}

$inventory = Read-Json -Path $inventoryPath
$dotenv = Parse-DotEnv -Path $dotenvPath

$managerAgentMap = @{}
$managerSnapshotUtc = ""
$managerSnapshotLoaded = $false
if (Test-Path -LiteralPath $managerAgentsPath) {
    try {
        $mgr = Read-Json -Path $managerAgentsPath
        $managerSnapshotUtc = [string](Get-ObjValue $mgr "generated_utc" "")
        foreach ($a in (Get-ObjValue $mgr "agents" @())) {
            $name = Normalize-Token ([string](Get-ObjValue $a "name" ""))
            if (-not $name) { continue }
            $rawStatus = [string](Get-ObjValue $a "status" "")
            $statusNorm = $rawStatus.ToLower()
            $mapped = "ENROLLED_UNKNOWN"
            if ($statusNorm -match "active") {
                $mapped = "ENROLLED_ACTIVE"
            } elseif ($statusNorm -match "never connected|disconnected|pending|not active") {
                $mapped = "ENROLLED_NOT_ACTIVE"
            }
            $managerAgentMap[$name] = $mapped
            if ($name.EndsWith("-01")) {
                $managerAgentMap[$name.Substring(0, $name.Length - 3)] = $mapped
            }
            $managerAgentMap[$name.Replace("-", "_")] = $mapped
        }
        $managerSnapshotLoaded = $true
    } catch {
        $managerSnapshotLoaded = $false
    }
}

$required = @()
$coveragePolicy = Get-ObjValue $inventory "coverage_policy" @{}
$includeRequired = @()
$excludeRequired = @()
if ($coveragePolicy) {
    $includeRequired = @(
        (Get-ObjValue $coveragePolicy "include_in_required_coverage" @()) |
            ForEach-Object { Normalize-Token ([string]$_) } |
            Where-Object { $_ }
    )
    $excludeRequired = @(
        (Get-ObjValue $coveragePolicy "exclude_from_required_coverage" @()) |
            ForEach-Object { Normalize-Token ([string]$_) } |
            Where-Object { $_ }
    )
}

function Should-IncludeHost {
    param(
        [string]$Hostname,
        [string[]]$IncludeList,
        [string[]]$ExcludeList
    )
    $n = Normalize-Token $Hostname
    if (-not $n) { return $false }
    if ($ExcludeList -contains $n) { return $false }
    if ($IncludeList.Count -gt 0 -and -not ($IncludeList -contains $n)) { return $false }
    return $true
}

function Add-RequiredHost {
    param(
        [object]$Item,
        [string]$SourceType
    )
    $hostname = [string](Get-ObjValue $Item "hostname" "")
    if (-not $hostname) { return }
    if (-not (Should-IncludeHost -Hostname $hostname -IncludeList $includeRequired -ExcludeList $excludeRequired)) { return }
    $aliases = Build-Aliases -Hostname $hostname -ExplicitAliases @((Get-ObjValue $Item "aliases" @()))
    $script:required += [pscustomobject]@{
        vmid = if ($SourceType -eq "vm") { Get-ObjValue $Item "vmid" "" } else { "" }
        hostname = $hostname
        role = [string](Get-ObjValue $Item "role" "")
        source_type = $SourceType
        aliases = $aliases
    }
}

foreach ($vm in (Get-ObjValue $inventory "vms" @())) {
    Add-RequiredHost -Item $vm -SourceType "vm"
}
foreach ($ep in (Get-ObjValue $inventory "endpoints" @())) {
    $coverageRequired = Get-ObjValue $ep "coverage_required" $true
    if (-not [bool]$coverageRequired) { continue }
    Add-RequiredHost -Item $ep -SourceType "endpoint"
}

$cutoff = (Get-Date).ToUniversalTime().AddHours(-1 * $WindowHours)
$hostHits = @{}
$hostLastSeenUtc = @{}
$seenTokenCounts = @{}

foreach ($h in $required) {
    $hostHits[$h.hostname] = 0
    $hostLastSeenUtc[$h.hostname] = $null
}

if (Test-Path -LiteralPath $queueProcessed) {
    $files = Get-ChildItem -LiteralPath $queueProcessed -File -Filter "*.json"
    foreach ($f in $files) {
        $raw = $null
        try {
            $raw = Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json -Depth 100
        } catch {
            continue
        }

        $tsRaw = [string](Get-ObjValue $raw "@timestamp" "")
        $ts = $null
        try { $ts = [datetime]::Parse($tsRaw).ToUniversalTime() } catch { $ts = $null }
        if ($null -eq $ts -or $ts -lt $cutoff) { continue }

        $candidates = @(
            [string](Get-ObjValue (Get-ObjValue $raw "agent" @{}) "name" ""),
            [string](Get-ObjValue (Get-ObjValue $raw "agent" @{}) "hostname" ""),
            [string](Get-ObjValue (Get-ObjValue $raw "host" @{}) "hostname" ""),
            [string](Get-ObjValue (Get-ObjValue $raw "manager" @{}) "name" ""),
            [string](Get-ObjValue $raw "location" "")
        ) | Where-Object { $_ -and $_.Trim() }

        $normalized = @()
        foreach ($c in $candidates) {
            $n = Normalize-Token $c
            if (-not $n) { continue }
            $normalized += $n
            if (-not $seenTokenCounts.ContainsKey($n)) { $seenTokenCounts[$n] = 0 }
            $seenTokenCounts[$n]++
        }

        foreach ($h in $required) {
            $aliasSet = @($h.aliases)
            $match = $false
            foreach ($n in $normalized) {
                if ($aliasSet -contains $n) { $match = $true; break }
            }
            if ($match) {
                $hostHits[$h.hostname]++
                if ($null -eq $hostLastSeenUtc[$h.hostname] -or $ts -gt $hostLastSeenUtc[$h.hostname]) {
                    $hostLastSeenUtc[$h.hostname] = $ts
                }
            }
        }
    }
}

$indexerHost = [string]($dotenv["WAZUH_INDEXER_HOST"])
$indexerUser = [string]($dotenv["WAZUH_INDEXER_USER"])
$indexerIndex = if ($dotenv.ContainsKey("WAZUH_INDEX")) { [string]$dotenv["WAZUH_INDEX"] } else { "wazuh-alerts-*" }
$indexerPass = Get-Secret -DotEnv $dotenv

$hostRows = @()
foreach ($h in $required) {
    $processedHits = [int]$hostHits[$h.hostname]
    $lastSeen = $hostLastSeenUtc[$h.hostname]
    $indexerHits = $null
    $indexerError = ""
    if ($QueryIndexer) {
        $indexerResult = Get-IndexerCount `
            -HostUrl $indexerHost `
            -IndexPattern $indexerIndex `
            -User $indexerUser `
            -Password $indexerPass `
            -Aliases @($h.aliases) `
            -WindowHours $WindowHours `
            -Insecure:($InsecureTls -or ($dotenv["WAZUH_TLS_INSECURE"] -eq "true"))
        $indexerHits = $indexerResult.count
        $indexerError = [string]$indexerResult.error
    }
    $hostRows += [pscustomobject]@{
        vmid = $h.vmid
        hostname = $h.hostname
        role = $h.role
        source_type = $h.source_type
        processed_hits = $processedHits
        last_seen_utc = if ($lastSeen) { $lastSeen.ToString("yyyy-MM-ddTHH:mm:ssZ") } else { "" }
        indexer_hits = if ($null -eq $indexerHits) { "" } else { [int]$indexerHits }
        indexer_error = $indexerError
        manager_state = Get-ManagerState -Hostname $h.hostname -Aliases @($h.aliases) -ManagerMap $managerAgentMap
        status = if ($processedHits -gt 0) { "PRESENT" } else { "MISSING" }
        aliases = ($h.aliases -join ", ")
    }
}

$topTokens = $seenTokenCounts.GetEnumerator() |
    Sort-Object -Property Value -Descending |
    Select-Object -First 20 |
    ForEach-Object {
        [pscustomobject]@{
            token = $_.Key
            hits = [int]$_.Value
        }
    }

$requiredNames = @($required | ForEach-Object { $_.hostname })
$unmappedTokens = @()
foreach ($t in $topTokens) {
    $matched = $false
    foreach ($h in $required) {
        if (@($h.aliases) -contains $t.token) { $matched = $true; break }
    }
    if (-not $matched) { $unmappedTokens += $t }
}

$hostUri = ""
$hostReachable = ""
if ($indexerHost) {
    try {
        $u = [uri]$indexerHost
        $hostUri = $u.Host
        $tnc = Test-NetConnection -ComputerName $u.Host -Port $u.Port -WarningAction SilentlyContinue
        $hostReachable = [string]$tnc.TcpTestSucceeded
    } catch {
        $hostReachable = "unknown"
    }
}

$actionRows = @()
foreach ($row in $hostRows) {
    if ($row.status -eq "PRESENT") {
        $actionRows += [pscustomobject]@{
            hostname = $row.hostname
            status = $row.status
            priority = "Monitor"
            likely_cause = "Telemetry present in processed queue."
            next_action = "No immediate fix. Keep host in coverage trend checks."
            verify_command = "python `"$opsRoot\50_System\Scripts\Automation\auto-soc\coverage-check.py`" --window-hours $WindowHours"
        }
        continue
    }

    $likelyCause = "No matching alert tokens in processed queue within window."
    $nextAction = "Confirm Wazuh agent enrollment + hostname label alignment + generate a test event."
    if ($hostReachable -eq "False") {
        $likelyCause = "No processed hits and runner cannot reach indexer over TCP."
        $nextAction = "Restore indexer connectivity first, then validate host telemetry path."
    } elseif ($row.indexer_error) {
        $likelyCause = "Indexer query failed: $($row.indexer_error)"
        $nextAction = "Fix indexer auth/TLS/query path first, then re-run coverage diagnose."
    } elseif ($row.manager_state -eq "ENROLLED_ACTIVE") {
        $likelyCause = "Host is enrolled/active on manager but still silent in indexer/processed aliases."
        $nextAction = "Generate forced test event on host and verify emitted fields map to inventory aliases (agent.name/agent.hostname/location)."
    } elseif ($row.manager_state -eq "ENROLLED_NOT_ACTIVE") {
        $likelyCause = "Host is enrolled on manager but not active."
        $nextAction = "Restore agent connectivity/keepalive first, then re-run coverage diagnose."
    } elseif ($row.manager_state -eq "NOT_ENROLLED_OR_UNKNOWN") {
        $likelyCause = "Host not found in manager enrollment snapshot."
        $nextAction = "Enroll host on manager (agent-auth/manage_agents), then generate test event."
    }

    $verify = @(
        "1) On manager: /var/ossec/bin/agent_control -l | grep -i $($row.hostname)",
        "2) On host: verify wazuh-agent service running",
        "3) Trigger test event and confirm it lands in index + AutoSOC processed queue"
    ) -join " | "

    $actionRows += [pscustomobject]@{
        hostname = $row.hostname
        status = $row.status
        priority = "High"
        likely_cause = $likelyCause
        next_action = $nextAction
        verify_command = $verify
    }
}

$report = [ordered]@{
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    window_hours = $WindowHours
    processed_root = $queueProcessed
    inventory_hosts = $required.Count
    present_hosts = @($hostRows | Where-Object status -eq "PRESENT").Count
    missing_hosts = @($hostRows | Where-Object status -eq "MISSING").Count
    required_coverage_percent = if ($required.Count -gt 0) { [math]::Round((@($hostRows | Where-Object status -eq "PRESENT").Count * 100.0) / $required.Count, 2) } else { 100.0 }
    indexer = @{
        queried = [bool]$QueryIndexer
        host = $indexerHost
        host_reachable_tcp = $hostReachable
        index = $indexerIndex
        user_present = [bool]($indexerUser)
        password_present = [bool]($indexerPass)
    }
    manager_snapshot = @{
        loaded = [bool]$managerSnapshotLoaded
        source = $managerAgentsPath
        generated_utc = $managerSnapshotUtc
        enrolled_hosts = $managerAgentMap.Count
    }
    hosts = $hostRows
    top_seen_tokens = $topTokens
    unmapped_top_tokens = $unmappedTokens
    action_matrix = $actionRows
}

$report | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $jsonOutPath -Encoding UTF8

$md = @()
$md += "# AutoSOC Coverage Diagnose"
$md += ""
$md += "- Generated UTC: $($report.generated_utc)"
$md += "- Window hours: $WindowHours"
$md += "- Inventory hosts: $($report.inventory_hosts)"
$md += "- Present hosts: $($report.present_hosts)"
$md += "- Missing hosts: $($report.missing_hosts)"
$md += "- Required coverage: $($report.required_coverage_percent)%"
$md += "- Indexer queried: $($report.indexer.queried)"
$md += "- Indexer reachable (TCP): $($report.indexer.host_reachable_tcp)"
$md += "- Manager snapshot loaded: $($report.manager_snapshot.loaded)"
if ($report.manager_snapshot.generated_utc) {
    $md += "- Manager snapshot generated UTC: $($report.manager_snapshot.generated_utc)"
}
$md += ""
$md += "## Host Status"
foreach ($row in $hostRows | Sort-Object status,hostname) {
    $idxErr = if ($row.indexer_error) { $row.indexer_error } else { "none" }
    $md += "- [$($row.status)] $($row.hostname) source=$($row.source_type) manager_state=$($row.manager_state) hits=$($row.processed_hits) last_seen=$($row.last_seen_utc) indexer_hits=$($row.indexer_hits) indexer_error=$idxErr"
}
$md += ""
$md += "## Action Matrix"
foreach ($a in $actionRows | Sort-Object priority,hostname) {
    $md += "- [$($a.priority)] $($a.hostname) ($($a.status))"
    $md += "  - Likely cause: $($a.likely_cause)"
    $md += "  - Next action: $($a.next_action)"
    $md += "  - Verify: $($a.verify_command)"
}
$md += ""
$md += "## Unmapped Top Tokens"
if ($unmappedTokens.Count -eq 0) {
    $md += "- none"
} else {
    foreach ($u in $unmappedTokens) {
        $md += "- $($u.token) ($($u.hits))"
    }
}

$md -join "`n" | Set-Content -LiteralPath $mdOutPath -Encoding UTF8

Write-Host "COVERAGE_DIAGNOSE_JSON=$jsonOutPath"
Write-Host "COVERAGE_DIAGNOSE_MD=$mdOutPath"
Write-Host ("PRESENT_HOSTS={0}" -f $report.present_hosts)
Write-Host ("MISSING_HOSTS={0}" -f $report.missing_hosts)
if ($QueryIndexer) {
    Write-Host ("INDEXER_REACHABLE_TCP={0}" -f $report.indexer.host_reachable_tcp)
}
Write-Host "ACTION_MATRIX:"
foreach ($a in $actionRows | Sort-Object priority,hostname) {
    Write-Host ("- [{0}] {1}: {2}" -f $a.priority, $a.hostname, $a.next_action)
}
