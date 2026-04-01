# Reviewer Quickstart

Fast validation path for this repository. Total time: ~5 minutes.

---

## 1. Verify detection counts are real

```powershell
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
```

This counts every Sigma, Wazuh, and Splunk rule file on disk and compares against published numbers. Zero tolerance for drift.

## 2. Check the source of truth

Open [`PROOF_PACK/VERIFIED_COUNTS.md`](PROOF_PACK/VERIFIED_COUNTS.md). Every number in the README traces back to this script-generated file.

## 3. Inspect sample artifacts

Browse [`PROOF_PACK/SAMPLES/`](PROOF_PACK/SAMPLES/) for representative detection rules, triage outputs, and redacted evidence packs.

## 4. Spot-check detection content

Pick any file from:
- `content/detection-rules/sigma/` — Sigma YAML rules by MITRE tactic
- `content/detection-rules/wazuh/rules/` — Wazuh XML rules
- `content/incident-response/playbooks/` — IR playbooks (7-step format)

## 5. Review pipeline architecture

[`docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md`](docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md) covers the live SignalFoundry engine: how alerts flow, how triage decisions are made, and how proof artifacts are generated.

---

## What to look for

- **Counts match.** README, VERIFIED_COUNTS.md, and `verify-counts.ps1` output should agree.
- **Rules are real.** Each Sigma/Wazuh/Splunk file contains actual detection logic, not stubs.
- **Playbooks are actionable.** Each IR playbook includes copy-paste commands and time estimates.
- **Sanitization is clean.** No real IPs, credentials, or PII in committed files. See [`PROOF_PACK/REDACTION_RULES.md`](PROOF_PACK/REDACTION_RULES.md).

---

## Questions?

Open an issue or contact [raylee@hawkinsops.com](mailto:raylee@hawkinsops.com).
