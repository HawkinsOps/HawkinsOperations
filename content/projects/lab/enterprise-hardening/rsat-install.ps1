$OutputFile = "C:\OPS\enterprise-security\rsat-output.txt"
$ErrorFile  = "C:\OPS\enterprise-security\rsat-errors.txt"

try {
    "=== RSAT CAPABILITY SCAN - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $OutputFile

    "`n--- All RSAT Capabilities ---" | Out-File $OutputFile -Append
    $allRsat = Get-WindowsCapability -Name RSAT* -Online
    $allRsat | Select-Object Name, State | Format-Table -AutoSize | Out-String | Out-File $OutputFile -Append

    $total     = ($allRsat | Measure-Object).Count
    $installed = ($allRsat | Where-Object State -eq Installed | Measure-Object).Count
    $notInst   = ($allRsat | Where-Object State -ne Installed | Measure-Object).Count
    "Total RSAT capabilities: $total | Already installed: $installed | To install: $notInst" | Out-File $OutputFile -Append

    "`n--- Installing missing RSAT capabilities ---" | Out-File $OutputFile -Append
    $toInstall = $allRsat | Where-Object State -ne Installed
    if ($toInstall.Count -eq 0) {
        "All RSAT capabilities already installed." | Out-File $OutputFile -Append
    } else {
        foreach ($cap in $toInstall) {
            "Installing: $($cap.Name)..." | Out-File $OutputFile -Append
            try {
                $result = Add-WindowsCapability -Online -Name $cap.Name
                "  -> Done. RestartNeeded: $($result.RestartNeeded)" | Out-File $OutputFile -Append
            } catch {
                "  -> ERROR: $_" | Out-File $OutputFile -Append
            }
        }
    }

    "`n--- Post-Install Verification ---" | Out-File $OutputFile -Append
    Get-WindowsCapability -Name RSAT* -Online | Where-Object State -eq Installed | Select-Object Name, State | Format-Table -AutoSize | Out-String | Out-File $OutputFile -Append

    "`n--- Key Tool Availability Check ---" | Out-File $OutputFile -Append
    $checks = @(
        @{ Name="gpmc.msc";    Path="$env:SystemRoot\System32\gpmc.msc" },
        @{ Name="dsa.msc";     Path="$env:SystemRoot\System32\dsa.msc" },
        @{ Name="dnsmgmt.msc"; Path="$env:SystemRoot\System32\dnsmgmt.msc" },
        @{ Name="AD PS Module";Path="$env:SystemRoot\System32\WindowsPowerShell\v1.0\Modules\ActiveDirectory" }
    )
    foreach ($c in $checks) {
        "$($c.Name): $(if (Test-Path $c.Path) { 'PRESENT' } else { 'NOT FOUND' })" | Out-File $OutputFile -Append
    }

    "=== COMPLETE ===" | Out-File $OutputFile -Append
} catch {
    "FATAL ERROR: $_" | Out-File $ErrorFile
}