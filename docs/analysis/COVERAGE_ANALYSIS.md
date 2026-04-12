# MITRE ATT&CK Coverage Analysis — HawkinsOperations

**Date:** 2026-04-04
**Context:** Detection rule coverage analysis for SOC portfolio review

---

## Kill Chain Heatmap

### Coverage by ATT&CK Tactic (Enterprise)

```
TACTIC                    SIGMA  WAZUH  SPLUNK  TOTAL  DEPTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reconnaissance              0      0      0       0    ⬛ GAP
Resource Development        0      0      0       0    ⬛ GAP
Initial Access              0      1      0       1    🟨 MINIMAL
Execution                   9      2      8      19    🟩 DEEP
Persistence                11      3      7      21    🟩 DEEP
Privilege Escalation       10      1      6      17    🟩 DEEP
Defense Evasion            10      1      9      20    🟩 DEEP
Credential Access          10      3      8      21    🟩 DEEP
Discovery                  10      1      9      20    🟩 DEEP
Lateral Movement           10      2      8      20    🟩 DEEP
Collection                 10      0      5      15    🟩 COVERED
Exfiltration               10      1      5      16    🟩 COVERED
Command and Control         1      2      1       4    🟨 LIGHT
Impact                     13      1      9      23    🟩 DEEP
```

### Depth Assessment

**DEEP coverage (multi-platform, multi-variant detections):**
- Credential Access: 21 detections across 13 technique IDs. Covers LSASS dumping (3 methods), Kerberoasting, DCSync, NTDS.dit, SAM dump, browser creds, SSH keys, Linux passwd/shadow. This is the strongest area.
- Defense Evasion: 20 detections across 13 technique IDs. AMSI bypass, log clearing, Defender disable, masquerading, process injection, DLL side-loading, timestomping, rootkit detection.
- Lateral Movement: 20 detections covering all major Windows lateral movement vectors (RDP, SMB, WMI, DCOM, WinRM, PsExec, SSH, Pass-the-Hash). Complete T1021 sub-technique coverage.
- Impact: 23 detections covering ransomware, data destruction, service stop, shadow copy deletion, boot config modification, disk wipe, cryptomining, DoS, defacement.

**COVERED but could be deeper:**
- Collection: 15 detections. Strong on clipboard/screen/audio/video/keylogging. Gap: no T1119 (Automated Collection) or T1074.002 (Remote Data Staging).
- Exfiltration: 16 detections. Covers DNS tunneling, FTP, email, cloud, removable media, SMB. Gap: no T1537 (Transfer Data to Cloud Account) or T1567.001 (Exfiltration to Code Repository).

**LIGHT coverage (single-detection or minimal):**
- Command and Control: Only 4 detections (DNS tunneling mapped to both exfil and C2). Missing T1071.001 (Web Protocols), T1105 (Ingress Tool Transfer), T1573 (Encrypted Channel), T1090 (Proxy/Tor).
- Initial Access: Single Wazuh rule for T1190 (web application attacks). Missing T1566 (Phishing), T1133 (External Remote Services), T1078 as initial access vector.

**ZERO coverage (expected gaps):**
- Reconnaissance (TA0043): Pre-intrusion activity. Cannot be detected with endpoint/log telemetry. Expected gap.
- Resource Development (TA0042): Adversary infrastructure setup. Cannot be detected from defender telemetry. Expected gap.

---

## Financial Services Relevance Scoring

Techniques rated by relevance to banking/financial sector SOC operations.

### HIGH RELEVANCE — Highlight on the call

These are the techniques most commonly seen in financial sector attacks (APT groups targeting banks, insider threats, fraud-adjacent TTPs):

| Technique | Why It Matters for FinServ | Detections |
|-----------|---------------------------|------------|
| T1003.001 LSASS Dumping | Core credential theft for lateral movement in bank networks | 5 (Sigma x2, Wazuh, Splunk x2) |
| T1003.006 DCSync | Domain compromise leads to full AD control — catastrophic in banking | 2 (Sigma, Splunk) |
| T1558.003 Kerberoasting | Service account compromise enables access to financial databases | 3 (Sigma, Wazuh, Splunk) |
| T1021.002 SMB/Admin Shares | Primary lateral movement path in Windows-heavy bank environments | 6 (Sigma x3, Wazuh, Splunk x2) |
| T1550.002 Pass-the-Hash | Credential reuse attack — common in financial sector intrusions | 2 (Sigma, Splunk) |
| T1486 Ransomware | Existential threat to financial institutions | 3 (Sigma, Wazuh, Splunk) |
| T1078 Valid Accounts | Compromised credentials — #1 initial access vector in financial attacks | 3 (Wazuh x2, Splunk) |
| T1078.002 Domain Accounts | Privileged domain account misuse — audit requirement | 1 (Wazuh) |
| T1059.001 PowerShell | Primary attack tool in post-exploitation against Windows environments | 3 (Sigma, Wazuh, Splunk) |
| T1562.001 Disable Defenses | Attackers disable EDR/AV before deploying ransomware or tools | 4 (Sigma x2, Wazuh, Splunk) |
| T1070.001 Log Clearing | Anti-forensics — critical for incident response and compliance | 2 (Sigma, Splunk) |
| T1190 Exploit Public-Facing | Web application attacks against banking portals | 1 (Wazuh) |
| T1046 Port Scanning | Reconnaissance inside bank network — compliance-relevant | 1 (Wazuh) |
| T1053.005 Scheduled Tasks | Used for persistence after initial compromise | 4 (Sigma x2, Wazuh x2) |
| T1547.001 Registry Run Keys | Most common Windows persistence mechanism | 5 (Sigma x2, Wazuh x2, Splunk x2) |
| T1543.003 Windows Service | Service persistence — common in advanced intrusions | 4 (Sigma, Wazuh x2, Splunk) |
| T1041 Exfiltration Over C2 | Data theft — existential risk for financial data | 2 (Sigma, Wazuh) |
| T1489 Service Stop | Disabling security services before ransomware deployment | 2 (Sigma, Splunk) |
| T1490 Inhibit Recovery | Shadow copy deletion — ransomware precursor | 3 (Sigma x2, Splunk) |
| T1555.003 Browser Creds | Internal user credential theft from browser stores | 2 (Sigma, Splunk) |
| T1555.004 Credential Manager | Windows Credential Manager access — direct credential theft | 1 (Splunk) |
| T1087.002 AD Enumeration | Attacker mapping AD environment — precursor to privilege escalation | 2 (Sigma, Splunk) |
| T1482 Domain Trust | Trust relationship abuse for cross-domain compromise | 2 (Sigma, Splunk) |
| T1531 Account Access Removal | Locking out accounts as impact/disruption in financial ops | 2 (Sigma, Splunk) |

### MEDIUM RELEVANCE — Mention if asked

| Technique | Note | Detections |
|-----------|------|------------|
| T1047 WMI Execution | Common but not FinServ-specific | 3 |
| T1055 Process Injection | Advanced TTPs, relevant for all verticals | 2 |
| T1036 Masquerading | General evasion, not sector-specific | 2 |
| T1574.002 DLL Side-Loading | Supply chain risk, relevant but not FinServ-focused | 2 |
| T1048.003 Exfil Over Alt Protocol | Data theft vector, DNS tunneling in particular | 4 |
| T1218.005/010/011 Signed Binary Proxy | LOLBins abuse, relevant everywhere | 4 |
| T1204.002 Malicious File | User execution of malware — universal | 2 |
| T1134.001 Token Manipulation | Windows privilege abuse | 2 |
| T1548.002 UAC Bypass | Windows privesc, relevant for all Windows environments | 5 |
| T1197 BITS Jobs | Increasingly common persistence mechanism | 2 |
| T1611 Container Escape | If the bank uses containers (increasingly common) | 1 |
| T1071.004 DNS C2 | C2 channel — always relevant | 1 |

### LOW RELEVANCE — Don't highlight

| Technique | Why Lower Priority |
|-----------|-------------------|
| T1123 Audio Capture | Espionage-specific, not typical in FinServ attacks |
| T1125 Video Capture | Espionage-specific |
| T1113 Screen Capture | More relevant to espionage than financial theft |
| T1491.001 Web Defacement | Reputational, but not a primary FinServ threat |
| T1498 Network DoS | DDoS is typically handled by network team, not SOC detections |
| T1495 Firmware Corruption | Very rare, ICS/OT-focused |
| T1496 Cryptomining | Nuisance, not targeted financial attack |
| T1580 Cloud Discovery | Relevant if cloud-heavy, but generic |
| T1029 Scheduled Transfer | Uncommon exfil method |
| T1052.001 Removable Media | Insider threat vector, less relevant for external attacks |

---

## Depth vs Breadth Assessment

### Where You Have DEPTH (highlight these)

These techniques have 3+ independent detections across multiple platforms — this is what mature detection programs do:

| Technique | Detection Count | Platforms | Why This Matters |
|-----------|----------------|-----------|-----------------|
| T1021.002 SMB/Admin Shares | 6 | Sigma, Wazuh, Splunk | Multiple detection angles: service install, share access, PsExec |
| T1003.001 LSASS Dumping | 5 | Sigma, Wazuh, Splunk | Process access + comsvcs.dll variant + EDR-aware exclusions |
| T1547.001 Registry Run Keys | 5 | Sigma, Wazuh, Splunk | Registry monitoring + startup folder + suspicious path chaining |
| T1548.002 UAC Bypass | 5 | Sigma, Splunk | Three distinct bypass methods (Fodhelper, Eventvwr, AlwaysInstallElevated) |
| T1485 Data Destruction | 5 | Sigma, Splunk | Windows + Linux + database destruction variants |
| T1562.001 Disable Defenses | 4 | Sigma, Wazuh, Splunk | AMSI bypass + Defender disable via registry + two platform views |
| T1543.003 Windows Service | 4 | Sigma, Wazuh, Splunk | Service creation + suspicious path chaining |
| T1053.005 Scheduled Tasks | 4 | Sigma, Wazuh, Splunk | Task creation + XML import + suspicious path filtering |
| T1558.003 Kerberoasting | 3 | Sigma, Wazuh, Splunk | TGS request + RC4 encryption + threshold detection |
| T1486 Ransomware | 3 | Sigma, Wazuh, Splunk | File extension monitoring + mass encryption frequency |
| T1490 Inhibit Recovery | 3 | Sigma, Splunk | vssadmin + wmic + bcdedit variants |
| T1059.001 PowerShell | 3 | Sigma, Wazuh, Splunk | Suspicious cmdlets + download behavior + ScriptBlock logging |
| T1047 WMI | 3 | Sigma, Wazuh, Splunk | wmiprvse.exe child process monitoring |

### Where You Have BREADTH Only (know the limits)

These techniques have a single basic detection — checkbox coverage, not defense-in-depth:

| Technique | Single Detection | Gap |
|-----------|-----------------|-----|
| T1190 Exploit Public-Facing | Wazuh SQL injection/XSS pattern match | No WAF integration, no web shell detection |
| T1014 Rootkit | Sigma unsigned driver load | No kernel-level integrity monitoring |
| T1068 Exploitation for PrivEsc | Sigma PrintSpooler EID 808 | Only one exploit class covered |
| T1611 Container Escape | Wazuh docker --privileged pattern | No container runtime security integration |
| T1046 Port Scanning | Wazuh frequency correlation | No network flow analysis |
| T1098 Account Manipulation | Wazuh sudo passwd | No Windows account modification events |
| T1071.004 DNS C2 | Wazuh query length analysis | No DNS response analysis, no DGA detection |
| T1078.002 Domain Accounts | Wazuh off-hours RDP | No cross-correlating with HR data or baseline |

### Depth/Breadth Ratio

- **Techniques with 3+ detections:** 13 (13.5% of 96 verified)
- **Techniques with 2 detections:** ~50 (52% — most are Sigma + Splunk pairs)
- **Techniques with 1 detection:** ~33 (34.5%)

**Assessment:** The portfolio shows BOTH depth and breadth. The 2-detection pattern (Sigma rule + Splunk implementation of the same logic) is common and demonstrates cross-platform detection engineering capability. The 13 techniques with 3+ detections show genuine defense-in-depth thinking. The 33 single-detection techniques are mostly in the Collection, Exfiltration, and Impact categories where one well-crafted rule is often sufficient.

For a director-level reviewer: this ratio is credible for a junior/mid-level detection engineer. The depth in credential access and lateral movement (the areas that matter most for financial sector defense) is particularly strong.

---

## Coverage Gaps — What a Reviewer Might Ask About

### "Why don't you detect phishing?" (T1566)
Phishing detection typically requires email gateway integration (Proofpoint, Mimecast) or O365 audit logs. Endpoint detection for phishing-delivered payloads IS covered via T1204.002 (macro execution) and T1059 sub-techniques. Worth mentioning: "I detect phishing at the execution stage, not the delivery stage — email security is a different tool boundary."

### "Where's your C2 detection?" (TA0011)
Weakest tactic. Only DNS tunneling is detected. Missing: HTTP/S beaconing patterns, Cobalt Strike/Sliver C2 signatures, JA3/JA4 fingerprinting, unusual certificate patterns. Response: "C2 detection at the network level requires NIDS/NDR integration — my detections focus on endpoint telemetry where I can identify the execution and post-exploitation behavior."

### "How do you handle cloud?" 
Limited: 1 AWS S3 rule (Wazuh), 1 cloud discovery rule (Sigma). If the bank is cloud-heavy, this is a gap. Response: "Cloud detection is a growth area — my current lab environment is on-prem focused. I've structured the detection framework to extend to cloud sources."

### "What about insider threat?"
Partially covered: after-hours execution (Splunk), credential manager access (Splunk), data staging (Sigma), exfiltration rules (multiple). Missing: behavioral analytics for data access patterns, print activity monitoring, USB device tracking beyond basic copy commands.

---

## Top 5 Detections to Walk Through on the Call

If asked "walk me through a detection," lead with these — they show the most sophistication:

1. **DCSync Attack Detection** (Sigma + Splunk) — Shows understanding of Active Directory replication abuse, specific GUID-based detection, proper exclusion of legitimate DCs and sync accounts.

2. **Kerberoasting Detection** (Sigma + Wazuh + Splunk) — Three-platform coverage. RC4 encryption type as indicator. Threshold-based correlation in Wazuh to detect mass TGS requests. Demonstrates understanding of Kerberos authentication internals.

3. **LSASS Memory Dump via Comsvcs.dll** (Sigma + Wazuh + Splunk) — Detects a specific credential dumping technique using a living-off-the-land binary. Shows knowledge of alternative dumping methods beyond just Mimikatz.

4. **Registry Autorun Persistence with Suspicious Path Chaining** (Wazuh 100070 + 100170) — Demonstrates rule chaining: base rule detects any autorun modification, child rule elevates severity when the target is a suspicious path. This is how Wazuh rules should be written.

5. **Impossible Travel Detection** (Wazuh 100064) — Shows awareness of identity-based detection beyond simple log monitoring. Requires geoIP enrichment — demonstrates understanding of data pipeline requirements for advanced detections.

---

*Coverage analysis based on verified detection inventory as of 2026-04-04. Gap analysis reflects inherent limitations of endpoint/log-based detection — network and cloud detection gaps are expected for this telemetry scope.*
