# Contributing to HawkinsOps SOC Content Library

Thank you for your interest in contributing! This document provides guidelines for contributing detection rules, incident response playbooks, and documentation to this repository.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Types of Contributions](#types-of-contributions)
- [Before You Contribute](#before-you-contribute)
- [Development Workflow](#development-workflow)
- [Detection Rule Guidelines](#detection-rule-guidelines)
- [Incident Response Playbook Guidelines](#incident-response-playbook-guidelines)
- [Pull Request Process](#pull-request-process)
- [CI/CD Pipeline](#cicd-pipeline)

---

## Quick Start

1. **Fork the repository** and clone your fork
2. **Create a feature branch:** `git checkout -b feature/your-contribution`
3. **Make your changes** following the guidelines below
4. **Test locally** using verification scripts
5. **Submit a pull request** to the `main` branch

---

## Types of Contributions

We welcome the following contributions:

### ✅ Accepted Contributions

- **Detection Rules:** Sigma, Splunk, or Wazuh rules for security threats
- **IR Playbooks:** Structured incident response procedures
- **Documentation:** Improvements to README, guides, or architecture docs
- **Bug Fixes:** Corrections to existing rules or documentation
- **Examples:** Additional sample artifacts for PROOF_PACK

### ❌ Not Accepted

- Hard-coded artifact counts (use verification scripts instead)
- Unsanitized data (real IPs, credentials, PII)
- Malicious or backdoored code
- Content unrelated to security operations

---

## Before You Contribute

### Read These First

1. [.github/CODE_OF_CONDUCT.md](.github/CODE_OF_CONDUCT.md) - Expected behavior
2. [SECURITY.md](SECURITY.md) - Reporting security issues
3. [PROOF_PACK/EVIDENCE_CHECKLIST.md](PROOF_PACK/EVIDENCE_CHECKLIST.md) - Sanitization requirements

### Environment Setup

**Required:**
- Git
- PowerShell (for verification scripts)
- Text editor (VS Code recommended)

**Optional:**
- Python (for future automation scripts)
- Bash/WSL (for Linux-based verification)

---

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/HawkinsOperations.git
cd HawkinsOperations
git remote add upstream https://github.com/raylee-hawkins/HawkinsOperations.git
```

### 2. Create Feature Branch

```bash
git checkout -b feature/add-sigma-rule-lateral-movement
```

**Branch naming:**
- `feature/` - New detection rules or playbooks
- `docs/` - Documentation improvements
- `fix/` - Bug fixes

### 3. Make Changes

Follow the appropriate guidelines:
- [Detection Rule Guidelines](#detection-rule-guidelines)
- [IR Playbook Guidelines](#incident-response-playbook-guidelines)

### 4. Test Locally

**Verify counts:**
```powershell
pwsh -NoProfile -File ".\\scripts\\verify\\verify-counts.ps1"
```

**Build Wazuh bundle (if applicable):**
```powershell
.\scripts\build-wazuh-bundle.ps1
```

**Check for sanitization issues:**
```powershell
# Scan for real IPs
Get-ChildItem -Recurse -Include *.md,*.yml,*.xml | Select-String -Pattern "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b" | Where-Object { $_.Line -notmatch "10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\." }
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add: Sigma rule for detecting lateral movement via WMI"
```

**Commit message format:**
```
<type>: <description>

[optional body]
```

**Types:**
- `Add:` - New detection rule, playbook, or feature
- `Update:` - Modify existing content
- `Fix:` - Bug fix or correction
- `Docs:` - Documentation only
- `Refactor:` - Code reorganization

### 6. Push and Create PR

```bash
git push origin feature/add-sigma-rule-lateral-movement
```

Then create a pull request on GitHub.

---

## Detection Rule Guidelines

### Sigma Rules

**Location:** `content/detection-rules/sigma/<tactic>/`

**Format:**
```yaml
title: Descriptive Rule Title
id: unique-uuid-here
status: stable
description: What this rule detects
references:
    - https://attack.mitre.org/techniques/T####/
author: Your Name
date: YYYY/MM/DD
modified: YYYY/MM/DD
tags:
    - attack.<tactic>
    - attack.t####
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        # Detection logic here
    condition: selection
falsepositives:
    - Known legitimate scenarios
level: high  # or critical, medium, low
```

**Requirements:**
- Must include MITRE ATT&CK technique tags
- Must document false positives
- Must be organized into correct tactic folder
- Must use valid Sigma YAML syntax

### Splunk Rules

**Location:** `content/detection-rules/splunk/`

**Format:**
```spl
# ========================================
# Rule Name
# MITRE: T####
# ========================================

index=windows EventCode=1
| where condition
| stats count by field1, field2
| where count > threshold
```

**Requirements:**
- Include MITRE ATT&CK technique comment
- Use proper SPL syntax
- Include comments explaining logic
- Group by MITRE tactic in files

### Wazuh Rules

**Location:** `content/detection-rules/wazuh/rules/`

**Format:**
```xml
<!--
  Wazuh Rule: Rule Name
  ID: 1000XX
  Level: 10
  Description: What this rule detects
  Author: Your Name
  Date: YYYY-MM-DD
-->

<group name="category,">
  <rule id="1000XX" level="10">
    <!-- Rule logic here -->
    <description>Alert description</description>
    <mitre>
      <id>T####</id>
    </mitre>
  </rule>
</group>
```

**Requirements:**
- Use rule ID in 100000+ range (custom rules)
- Include MITRE ATT&CK tags
- Document false positives in comments
- Follow Wazuh XML schema

---

## Incident Response Playbook Guidelines

**Location:** `content/incident-response/playbooks/`

**Format:** Follow the template in `content/incident-response/templates/IR-Template.md`

**Required Sections:**
1. **DETECTION** - Alert trigger and indicators
2. **TRIAGE (5 min)** - Quick validation and escalation criteria
3. **INVESTIGATION (30 min)** - Deep dive commands and analysis
4. **CONTAINMENT (15 min)** - Immediate response actions
5. **ERADICATION** - Threat removal
6. **RECOVERY** - Service restoration
7. **DOCUMENTATION** - Timeline and lessons learned

**Requirements:**
- Include MITRE ATT&CK technique mapping
- Provide copy-paste commands (PowerShell or Bash)
- Document time estimates for each phase
- List required tools and permissions
- Include false positive scenarios

---

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guidelines
- [ ] All files are sanitized (no real IPs, credentials, PII)
- [ ] Verification scripts pass (`pwsh -NoProfile -File ".\\scripts\\verify\\verify-counts.ps1"`)
- [ ] Commit messages are descriptive
- [ ] Changes are focused (one logical change per PR)

### PR Checklist

When you create a PR, fill out the template:

```markdown
## Description
[Describe what this PR adds/changes]

## Type of Change
- [ ] New detection rule
- [ ] New IR playbook
- [ ] Documentation improvement
- [ ] Bug fix

## MITRE ATT&CK Techniques
[List applicable techniques: T####]

## Testing
- [ ] Ran verification script
- [ ] Built Wazuh bundle (if applicable)
- [ ] Checked for sanitization issues

## Checklist
- [ ] Followed contributing guidelines
- [ ] No sensitive data included
- [ ] MITRE ATT&CK tags added
- [ ] Documentation updated if needed
```

### Review Process

1. **Automated Checks:** CI/CD pipeline runs automatically
   - Counts all detection rules
   - Builds Wazuh bundle
   - Verifies file structure
2. **Manual Review:** Maintainer reviews for:
   - Detection logic quality
   - False positive analysis
   - Documentation completeness
   - Sanitization compliance
3. **Feedback:** Address any requested changes
4. **Merge:** Once approved, PR is merged to `main`

---

## CI/CD Pipeline

### GitHub Actions Workflow

**File:** `.github/workflows/verify.yml`

**On Pull Request:**
- ✅ Counts detection rules across all platforms
- ✅ Generates verification report
- ✅ Builds Wazuh bundle
- ✅ Uploads artifacts
- ❌ Does NOT auto-commit (PR stays clean)

**On Main Branch Push:**
- ✅ Same verification steps as pull requests
- ✅ Generates `PROOF_PACK/VERIFIED_COUNTS.md` in workflow context
- ✅ Uploads verification and bundle artifacts
- ❌ Does NOT commit or push generated files back to the repository

### Skipping CI

If you need to skip CI (e.g., documentation-only changes):

```bash
git commit -m "Docs: Update README [skip ci]"
```

**Note:** Use sparingly - verification is fast and ensures quality.

---

## Getting Help

**Questions about contributing?**
- Open an issue with the `question` label
- Check existing issues and PRs for examples
- Review the [PROOF_PACK/SAMPLES](PROOF_PACK/SAMPLES) directory for examples

**Found a security issue?**
- See [SECURITY.md](SECURITY.md) for responsible disclosure

**Need clarification on guidelines?**
- Open a discussion on GitHub
- Reference specific guidelines in your question

---

## Recognition

Contributors will be:
- Listed in commit history
- Credited in rule/playbook author fields
- Acknowledged in release notes (if applicable)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see [LICENSE](LICENSE)).

---

**Thank you for contributing to HawkinsOps SOC Content Library!** 🛡️

Your contributions help improve security operations practices and demonstrate professional SOC capabilities.

