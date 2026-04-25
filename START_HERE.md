# Start Here

For recruiters and hiring managers. No tools required. Total time: ~5 minutes.

---

## What this repository is

The V1 legacy/reference repository for HawkinsOps detection engineering,
SOC automation, and proof-control work. It preserves the source, case
studies, verification scripts, and archived proof artifacts from the V1
system. It is not the current primary live proof surface.

Use [hawkinsops.com](https://hawkinsops.com) for the current public proof
surface. Use [rayleeops.com](https://rayleeops.com) / The Ledger for public
contested review and methodology framing. The successor architecture is the
[HawkinsOperations organization](https://github.com/HawkinsOperations), which
is architecture-in-progress and should not be treated as primary live proof
until promoted.

---

## 1. Check the numbers

Open [`PROOF_PACK/VERIFIED_COUNTS.md`](PROOF_PACK/VERIFIED_COUNTS.md). The
counts in this repo are source/repo evidence generated from files in the V1
tree. Repo evidence does not, by itself, prove current runtime state or public
deployment.

Key numbers:
- **103** Sigma detection rules
- **28** Wazuh rule blocks across 24 files
- **79** Splunk detection searches across 9 files
- **10** incident response playbooks
- **123** MITRE ATT&CK technique/sub-technique IDs across 69 families
- **8,574** escalation packs from 324,074 total cases (~88% auto-close rate)

## 2. See the detection content

Browse [`content/detection-rules/INDEX.md`](content/detection-rules/INDEX.md)
for the V1 detection catalog organized by MITRE ATT&CK tactic. Each rule is a
source artifact; current runtime/public proof belongs on the promoted public
surfaces.

## 3. See the incident response playbooks

Browse [`content/incident-response/INDEX.md`](content/incident-response/INDEX.md) for 10 structured playbooks. Each includes time estimates, copy-paste commands, and MITRE technique mapping.

## 4. Read a case study

[`content/case-studies/wazuh-telemetry-remediation.md`](content/case-studies/wazuh-telemetry-remediation.md) documents diagnosing three independent failures that left a 10-agent deployment blind to Windows process creation, and restoring full telemetry visibility.

## 5. See the pipeline architecture

[`docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md`](docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md) documents how alerts flow from Wazuh through automated triage to escalation packs.

---

## What the CI checks verify

Maintenance changes keep automated guardrails active:

| Check | What it does |
| --- | --- |
| **verify** | Counts all detection rules, generates site data, builds Wazuh bundle, validates hosting |
| **drift-scan** | Compares published counts against actual files — fails if any number drifts |
| **contract-scan** | Blocks accidental commits of runtime data or oversized files |

These checks preserve the V1 reference boundary. They do not convert this
repository into the current live runtime proof surface.

---

## Quick links

- **Current public proof surface:** [hawkinsops.com](https://hawkinsops.com)
- **Public contested review:** [rayleeops.com](https://rayleeops.com) / The Ledger
- **Proof pack:** [`PROOF_PACK/`](PROOF_PACK/)
- **Full README:** [`README.md`](README.md)
- **Technical reviewer path:** [`REVIEWER_QUICKSTART.md`](REVIEWER_QUICKSTART.md)
