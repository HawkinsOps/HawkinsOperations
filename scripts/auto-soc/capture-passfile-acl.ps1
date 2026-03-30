param(
    [string]$PassFile = "C:\RH\OPS\30_Projects\Active\AutoSOC\Build\Config\secrets\wazuh_indexer_pass.txt",
    [string]$OutJson = "C:\RH\OPS\30_Projects\Active\AutoSOC\Output\passfile_acl_latest.json"
)

$acl = Get-Acl -LiteralPath $PassFile
$rows = @()
foreach ($a in $acl.Access) {
    $rows += [pscustomobject]@{
        identity = [string]$a.IdentityReference
        rights = [string]$a.FileSystemRights
        type = [string]$a.AccessControlType
        inherited = [bool]$a.IsInherited
    }
}

$out = [pscustomobject]@{
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    pass_file = $PassFile
    owner = [string]$acl.Owner
    access = $rows
}
$out | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutJson -Encoding utf8
Write-Output "ACL_JSON=$OutJson"
