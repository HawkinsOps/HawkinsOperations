# Precedence Contract

## Purpose

This file defines which artifacts win when repo content, site copy, metrics, resumes, or planning notes disagree.

If two files conflict, use this contract first and then follow the listed authority order for that topic.

## General rule

- Memory is convenience.
- Repo docs are authority.
- Canonical metrics artifacts are numeric truth.
- Public wording must never outrun proof.

## Narrative authority

Primary authority:
- `docs/source-of-truth.md`

Secondary authority:
- `AGENTS.md`
- `PLANS.md`

Lower-precedence supporting material:
- `README.md`
- `START_HERE.md`
- historical execution reports

Rule:
- If public copy conflicts with `docs/source-of-truth.md`, `docs/source-of-truth.md` wins.

## Public metrics authority

Current authority for detection and playbook inventory:
1. `PROOF_PACK/VERIFIED_COUNTS.md`
2. `PROOF_PACK/verified_counts.json`
3. `site/assets/verified-counts.json`

Current authority for live operational-state and pipeline-status claims:
1. `proof/autosoc/latest/heartbeat.json`
2. `proof/autosoc/latest/coverage_latest.json`
3. `proof/autosoc/latest/reconciliation_latest.json`
4. `proof/autosoc/latest/run_metrics_latest.json`
5. explicitly cited public-safe execution docs under `docs/execution/`

Transitional artifact:
- `data/metrics.json` exists, but it is not yet authoritative unless its values are regenerated from the active proof chain and documented in `docs/METRICS_PROVENANCE.md`.

Rule:
- Do not publish or repeat a number from `data/metrics.json` unless it reconciles with the active upstream proof artifacts.

## Resume metrics authority

Primary authority:
- the same numeric sources as public metrics authority above

Rule:
- Resume metrics must be a subset of public-safe, repo-verifiable numbers.
- If a resume number cannot be traced to the public metrics authority or a documented public-safe proof artifact, remove or generalize it.

## Website naming authority

Primary naming model:
- `SignalFoundry` = flagship system / public-facing proof object
- `HawkinsOperations` or `HawkinsOps` = portfolio / site / umbrella identity
- `AutoSOC` = internal engine and historical implementation term until explicitly retired from the repo

Rule:
- Do not perform blind mass-replace operations across these names.
- If a page needs one label, prefer `SignalFoundry` for the flagship public system.
- Use `AutoSOC` only where implementation history or internal engine naming is materially relevant.

## Splunk claim authority

Primary authority:
- `content/lab/proxmox/vms/104/splunk/exports/SPLUNK_LIVE_WINDOWS_INGEST_VALIDATION_2026-03-17.md`
- `content/lab/proxmox/vms/104/splunk/exports/SPLUNK_EVENTID_4688_VALIDATED_PIVOTS_2026-03-17.md`
- `content/lab/proxmox/vms/104/splunk/exports/README.md`

Allowed public claim ceiling:
- Splunk operates in the lab as an investigation layer with live Windows telemetry ingest and validated SPL pivots against real Event ID 4688 process-creation data.

Rule:
- Do not claim alert-to-investigation maturity, broad telemetry coverage, or analyst-workflow completeness unless newer committed artifacts prove it.

## Sensitive and personal background handling

Primary authority:
- `AGENTS.md`
- `SECURITY.md`

Rule:
- The public repo may include only recruiter-safe, portfolio-relevant personal details.
- Do not include criminal-history details, abuse history, sealed-record discussion, treatment history, internal host data, credentials, or other sensitive background material.
- The only clearance-related public line that is pre-approved is:
  - "Eligible to obtain clearance; willing to pursue sponsorship."

## Audit reading order

For repo audit and planning sessions, read in this order:
1. `AGENTS.md`
2. `PLANS.md`
3. `docs/PRECEDENCE_CONTRACT.md`
4. `docs/source-of-truth.md`
5. `docs/mission-today.md`
6. `docs/content-architecture.md`
7. `docs/metrics-integration.md`
8. `docs/design-stack.md`

## Change-control rule

If a planned edit would change any authority listed above, update the controlling file first before changing downstream content.
