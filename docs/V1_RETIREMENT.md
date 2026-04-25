# V1 Retirement Notice

**Date:** 2026-04-23
**Status:** Archival reference. No further V1 feature development after this
date; maintenance commits are limited to CI health, governance alignment,
truth-boundary corrections, and public-safety fixes.
**Successor:** [github.com/HawkinsOperations](https://github.com/HawkinsOperations)

---

## What V1 is

This repository (`raylee-hawkins/HawkinsOperations`) is the V1 home of the HawkinsOps system — a single-operator detection-engineering and SOC-automation project run from a Proxmox homelab. It carried the project from inception through approximately seven months of operational evidence. The system it produced, as of the most recent truth-lock:

- 324,074 cases triaged through the AutoSOC pipeline
- ~88% auto-close rate across benign and known-false-positive classes
- 8,574 escalation packs produced for analyst review
- 210+ CI-verified detections spanning Sigma, Wazuh XML, and Splunk SPL
- 10 Wazuh agents, 8 of 8 host coverage
- 15-server Proxmox homelab with V100 local inference

V1 was a working portfolio repo. The pipeline shipped, the rules fired, the reconciliation gate held at zero mismatches, and the proof-pack CI produced verified counts. It did the job it was built to do.

## Why the repository is being retired

Two independent audit passes against the tree on 2026-04-19 and 2026-04-20 reached the same structural conclusion from different angles: the repository's boundaries failed before its code did. Four failure modes carried the diagnosis.

**1. Mixed-plane contamination.** One git tree simultaneously served detection-content library, AutoSOC pipeline runtime, runtime-output archive, multi-surface evidence, and the public portfolio site. One trust class protected all five. One CI pipeline gated all five. One public visibility class exposed all five. The audit counted five `wazuh*` paths at five different roots (`wazuh/`, `content/wazuh/`, `dist/wazuh/`, `evidence/wazuh/`, `proof/wazuh/`) and 14,897 runtime-generated incident files under `content/incident-response/incidents/` — committed before the gitignore rule was added. Gitignore added later cannot un-publish history.

**2. Advisory-only governance.** The repo carried `docs/PRECEDENCE_CONTRACT.md`, `PROOF_PACK/REDACTION_RULES.md`, `docs/source-of-truth.md`, and `docs/VALIDATION_FRAMEWORK.md` as prose contracts. No CI job validated conformance. The `public-safety-gate` workflow scoped only to `site/**` and a narrow list of project paths — it did not scan `content/incident-response/incidents/**`, which is the directory where the 2026-04-18 redaction nested-output bug actually shipped (commit `3af6a1e fix(redact): move default output outside case_dir to prevent nested accumulation`, regression test at `e3f996f`). The gate was real. It was misaimed.

**3. Contradictory truth surfaces.** The tree carried four candidate "current truth" endpoints for operational metrics: `PROOF_PACK/verified_counts.json`, `proof/autosoc/latest/`, five dated files under `source_of_truth/metrics_canonical_*.json` with no current-pointer, and `data/metrics.json` with its sibling `.sha256`. Downstream, the published headline numbers on the portfolio site, the `docs/SignalFoundry_Case_Study_March2026.md` counts, and the README could disagree without any executable check raising a flag. A reader could not determine which surface was canonical without reading commit history.

**4. No mechanical promotion gates.** Operator vigilance was the load-bearing safety mechanism. Present-tense "live pipeline" claims shipped and were retracted reactively in PRs #180 and #182. The March 2026 ledger silent-reseed bug — a `load_ledger()` path that silently recreated a missing ledger file with blank state instead of halting — produced silent loss of pipeline memory for an unknown window, discovered only after a downstream reconciliation anomaly. The April 18 AutoSOC subprocess-nesting bug was caught after the redaction pipeline had already produced nested output in a directory the gate did not scan. In both cases, the system was held together by the operator noticing before the drift compounded. That is not a control. That is a heroic pattern.

## What V1 proved

Donor-quality content and working controls that migrate forward:

- **Detection rules.** Sigma, Wazuh XML rule blocks, Splunk SPL, and their MITRE ATT&CK mappings are CI-verifiable and script-counted. They are the strongest artifacts in the tree.
- **IR playbooks.** Ten hand-authored playbooks on a 7-section analyst template, MITRE-mapped. Durable.
- **AutoSOC pipeline.** Multi-stage Python pipeline with poll, cap, triage, generate, escalate, reconcile, and heartbeat stages. Actively maintained, regression-tested, and migrated to env-var-aware path resolution.
- **Verified-counts and drift-scan gates.** Real enforcement, CI-blocking, preserved into the successor architecture.
- **Case studies and site copy.** The Race Condition Recovery and companion write-ups are engineering narrative at operational depth, not marketing.

## What V1 failed to prove

That a single repository mixing five trust classes, three proof surfaces, and four metrics endpoints could carry the work at the scale the work grew to without operator vigilance as the load-bearing safety mechanism.

## What happens next

Active development moves to the [HawkinsOperations organization](https://github.com/HawkinsOperations), which splits the system into five repositories with single-responsibility, single-audience, and single-change-velocity scope:

| Repository | Responsibility |
|---|---|
| `hawkinsoperations-detections` | Sigma / Wazuh / Splunk rule sources |
| `hawkinsoperations-validation` | Regression harnesses, rule-firing tests, FP/TP tracking |
| `hawkinsoperations-platform` | Pipeline control, AutoSOC orchestration, MCP servers |
| `hawkinsoperations-proof` | Verified counts, case studies, evidence bundles |
| `hawkinsoperations-website` | Source for the successor public site |

The split replaces markdown-as-contract with CI-enforced schemas and path-allowlist gates. Runtime never writes into a content repo. Detection content imports nothing from runtime. Every public-safe artifact carries provenance metadata. The publish bundle is immutable between builds.

## Forward pointers

- Successor organization: [github.com/HawkinsOperations](https://github.com/HawkinsOperations)
- Organization opening commit: [`OPENING.md`](https://github.com/HawkinsOperations) in the org profile repo
- Live operational metrics: [hawkinsops.com](https://hawkinsops.com)
- Methodology paper: [`rayleeops/methodology.md`](https://github.com/raylee-hawkins/rayleeops/blob/main/methodology.md)
- Public review layer: [rayleeops.com](https://rayleeops.com) (The Ledger)

## Archival metadata

```
archival_mode:      read-only
archival_date:      2026-04-23
successor_org:      HawkinsOperations
canonical_system:   hawkinsops.com
legacy_status:      donor history, not active foundation
retraction_policy:  broken links are preserved as forensic evidence, not repaired
```

---

This document closes V1 as an active foundation. The site at hawkinsops.com is
the current public proof surface. The V1 repository remains publicly accessible
as donor history and reference material.
