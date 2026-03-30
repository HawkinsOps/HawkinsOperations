# HawkinsOps SOC Architecture

This document provides a high-level overview of the detection and response architecture implemented in this repository.

---

## Detection Platform Coverage

This repository provides detection content for **three major security platforms**, organized to demonstrate platform-specific expertise and MITRE ATT&CK coverage:

### Sigma (Universal Detection Format)
- **Location:** `content/detection-rules/sigma/`
- **Format:** YAML-based detection rules following Sigma specification
- **Organization:** Structured by MITRE ATT&CK tactics
- **Strength:** Platform-agnostic rules that can be converted to any SIEM
- **Use Case:** Portable detection logic that works across Splunk, Elastic, QRadar, etc.

**Tactic Coverage:**
```
credential-access/     → T1003, T1110, T1555, T1558
defense-evasion/       → T1027, T1070, T1112, T1562
discovery/             → T1046, T1057, T1083, T1135
execution/             → T1047, T1053, T1059, T1204
exfiltration/          → T1020, T1041, T1048, T1567
impact/                → T1485, T1486, T1490, T1491
lateral-movement/      → T1021, T1550, T1563
persistence/           → T1053, T1098, T1136, T1547
privilege-escalation/  → T1055, T1068, T1078, T1134
```

### Splunk (SPL Queries)
- **Location:** `content/detection-rules/splunk/`
- **Format:** Splunk Search Processing Language (.spl files)
- **Organization:** Grouped by MITRE ATT&CK tactics with multiple queries per file
- **Strength:** Optimized for Splunk Enterprise Security and detection efficiency
- **Use Case:** Production-ready searches for Splunk deployments

**Query Collections:**
- Credential Access (LSASS dumps, Mimikatz, Kerberoasting, DCSync)
- Defense Evasion (Log clearing, AV disabling, process injection)
- Discovery (Network scanning, account enumeration)
- Execution (PowerShell, WMI, scheduled tasks)
- Lateral Movement (RDP, PsExec, WinRM)
- Persistence (Registry run keys, services, scheduled tasks)
- Privilege Escalation (UAC bypass, token manipulation)
- Collection/Exfiltration/Impact (Data staging, ransomware, destruction)

### Wazuh (XML Rules)
- **Location:** `content/detection-rules/wazuh/rules/`
- **Format:** Wazuh XML rule modules (individual files per detection)
- **Organization:** Numbered rule modules (wazuh-051-*.xml format)
- **Strength:** Open-source SIEM deployment with agent-based monitoring
- **Use Case:** Demonstrable production deployment capability

**Key Features:**
- Individual XML modules containing `<rule id="...">` blocks
- Some modules contain multiple related rules
- MITRE ATT&CK tags embedded in rules
- Deployable via `scripts/build-wazuh-bundle.sh`
- Production target: `/var/ossec/etc/rules/local_rules.xml`

---

## Incident Response Architecture

### 7-Step Playbook Framework

Every IR playbook follows a standardized structure for consistency and completeness:

```
1. DETECTION     → What triggered the alert, initial indicators
2. TRIAGE (5m)   → Fast validation, escalation criteria
3. INVESTIGATION → Deep dive commands, artifact collection
4. CONTAINMENT   → Immediate actions to stop the spread
5. ERADICATION   → Remove threat, close attack vectors
6. RECOVERY      → Restore services, validate cleanup
7. DOCUMENTATION → Timeline, evidence, lessons learned
```

**Time-Boxed Approach:**
- Triage: 5 minutes to decide escalate/false positive
- Investigation: 30 minutes of focused analysis
- Containment: 15 minutes to isolate and stabilize
- Recovery/Eradication: Based on threat severity

### Playbook Coverage

**Location:** `content/incident-response/playbooks/`

**Critical Priority Scenarios:**
- IR-001: LSASS Process Access (T1003.001)
- IR-003: Ransomware Detected (T1486)
- IR-007: Active Directory Compromise (T1003.006)
- IR-015: Data Exfiltration (T1041)
- IR-022: Supply Chain Attack (T1195)

**High Priority Scenarios:**
- IR-002: Suspicious PowerShell (T1059.001)
- IR-004: Brute Force Attack (T1110)
- IR-005: Malware Execution (T1204)
- IR-006: Privilege Escalation (T1068)
- IR-008: Lateral Movement (T1021)

---

## Threat Hunting Structure

### Hunt Organization

**Location:** `content/threat-hunting/`

**Platform-Specific Hunts:**
- `windows/` - Windows-focused threat hunting queries
- `linux/` - Linux-focused threat hunting queries
- `00-Hunt-Matrix.md` - Hunt coverage matrix mapped to MITRE

**Hunting Philosophy:**
- Hypothesis-driven investigations
- Baseline normal behavior first
- Look for anomalies and outliers
- Document assumptions and false positive scenarios

---

## Deployment Architecture (Wazuh Example)

### Repository → Production Flow

**1. Development (This Repo):**
```
content/detection-rules/wazuh/rules/*.xml
    ↓
Individual rule modules stored separately
Easy to version control, review, and document
```

**2. Build Phase:**
```
scripts/build-wazuh-bundle.ps1 (PowerShell)
OR scripts/build-wazuh-bundle.sh (Bash/Linux)
    ↓
Concatenates all XML modules
Strips BOMs and XML declarations
Generates: dist/wazuh/local_rules.xml
```

**3. Deployment:**
```
dist/wazuh/local_rules.xml
    ↓
scp to Wazuh manager
    ↓
/var/ossec/etc/rules/local_rules.xml
    ↓
systemctl restart wazuh-manager
```

**4. Verification:**
```
tail /var/ossec/logs/ossec.log
    ↓
Check for rule load errors
Validate rule counts match
Test alert generation
```

### Why This Matters

**Portfolio Benefit:**
- Shows understanding of CI/CD for security content
- Demonstrates production deployment knowledge
- Proves rules aren't just theoretical YAML
- Provides verifiable artifact counts

---

## Verification Architecture

### Count Verification System

**Location:** `docs/VERIFY_COMMANDS_POWERSHELL.md`

**Philosophy:**
- **Never hard-code counts** in documentation
- Always derive counts from actual file system
- Make verification reproducible by anyone
- Provide commands that output can be copy-pasted into resume/interviews

**Verification Points:**
1. Sigma rule count (*.yml files)
2. Splunk query count (*.spl files)
3. Wazuh XML file count
4. Wazuh rule block count (actual `<rule id=>` instances)
5. IR playbook count (*.md files)

**Why Two Wazuh Counts:**
- **XML Files:** Number of rule modules in repo
- **Rule Blocks:** Actual deployable rules (some XML files contain multiple `<rule id=>` blocks)
- Quote both to show attention to detail

---

## Security Hardening in Repository

### Evidence Sanitization

**Location:** `PROOF_PACK/EVIDENCE_CHECKLIST.md`

**Pre-Commit Checks:**
- Scan for real IP addresses
- Scan for Windows paths with usernames
- Scan for passwords/API keys/tokens
- Scan for email addresses

**Philosophy:**
- Security professionals should demonstrate security awareness
- Public portfolio repos must be sanitized
- No internal IPs, hostnames, usernames, or credentials
- Use generic examples (10.x.x.x, analyst01, WORKSTATION-01)

### Safe Documentation Pattern

```
❌ BAD:  "Alert triggered from raylee@company.com at [REDACTED_IP]"
✅ GOOD: "Alert triggered from analyst01@lab.local at [REDACTED_IP]"

❌ BAD:  C:\Users\Raylee\Documents\Tools\mimikatz.exe
✅ GOOD: C:\Users\analyst\Documents\Tools\mimikatz.exe
```

---

## Portfolio Impact

### What This Demonstrates

**Technical Skills:**
1. Multi-platform SIEM expertise (Sigma, Splunk, Wazuh)
2. MITRE ATT&CK framework mapping
3. Structured incident response methodology
4. Threat hunting hypothesis development
5. CI/CD for security content
6. Production deployment knowledge

**Professional Maturity:**
1. Verifiable claims (run commands, get counts)
2. Documented deployment paths (not just theory)
3. Security awareness (sanitized evidence)
4. Portfolio presentation (clear structure, easy to validate)

**Interview Talking Points:**
- "I have 103 Sigma rules covering X tactics"
- "Here's my Wazuh deployment script that bundles rules for production"
- "My IR playbooks follow a 7-step framework with time-boxed phases"
- "Run this PowerShell command to verify my detection counts"

---

## Quick Validation (90-Second Recruiter Path)

For someone validating this portfolio:

1. **Start:** `START_HERE.md` (60 seconds)
2. **Proof:** `PROOF_PACK/VERIFIED_COUNTS.md` (see actual numbers)
3. **Sample:** `PROOF_PACK/SAMPLES/` (review 2-3 detection samples)
4. **Verify:** Run `docs/VERIFY_COMMANDS_POWERSHELL.md` (confirm counts)
5. **Deploy:** Check `docs/wazuh/DEPLOYMENT_REALITY.md` (see it's deployable)

**Result:** Recruiter/hiring manager can validate:
- ✅ Claims are verifiable
- ✅ Content is real and organized
- ✅ Candidate understands production deployment
- ✅ Professional presentation and documentation
