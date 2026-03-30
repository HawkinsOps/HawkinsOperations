# AutoSOC File Decision Log

**Date:** 2026-03-30
**Consolidation agent:** Claude (automated)

---

## Scripts

| File | Source A (from_OPS) | Source B (from_RH_OPS) | Decision | Rationale |
|------|-------------------|----------------------|----------|-----------|
| `assemble-pack.py` | SHA256: 620D7BC9... / 6,541 B / 2026-03-04 | SHA256: 620D7BC9... / 6,541 B / 2026-03-04 | **IDENTICAL** - used Source B copy | Byte-identical |
| `build_march_truth_index.ps1` | SHA256: 0977C714... / 5,523 B / 2026-03-23 | SHA256: 23CBBBD3... / 5,088 B / 2026-03-04 | **CANONICAL_A** | Source A is 435 bytes larger, 19 days newer, contains Assert-CanonicalPath function |
| `build_runs_index.ps1` | SHA256: B7AB4B40... / 7,377 B / 2026-03-23 | SHA256: 1874829A... / 6,938 B / 2026-03-04 | **CANONICAL_A** | Source A is 439 bytes larger, 19 days newer, more evolved version |
| `build_run_manifest.ps1` | SHA256: 45429046... / 2,780 B / 2026-03-04 | SHA256: 45429046... / 2,780 B / 2026-03-04 | **IDENTICAL** - used Source B copy | Byte-identical |
| `common.py` | N/A | 3,281 B / 2026-03-04 | **ONLY_IN_B** | Core path constants module |
| `run-pipeline.py` | N/A | 18,999 B / 2026-03-22 | **ONLY_IN_B** | Main pipeline orchestrator |
| `triage.py` | N/A | 22,534 B / 2026-03-15 | **ONLY_IN_B** | Core triage engine |
| `poll-alerts.py` | N/A | 10,351 B / 2026-03-04 | **ONLY_IN_B** | Wazuh alert poller |
| `reconcile-state.py` | N/A | 7,646 B / 2026-03-25 | **ONLY_IN_B** | Ledger reconciliation |
| `coverage-check.py` | N/A | 8,625 B / 2026-03-13 | **ONLY_IN_B** | Host coverage validation |
| `daily-ops.ps1` | N/A | 5,136 B / 2026-03-25 | **ONLY_IN_B** | Daily operations coordinator |
| `policy-audit.py` | N/A | 8,496 B / 2026-03-15 | **ONLY_IN_B** | Policy tuning audit |
| (remaining 23 files) | N/A | Source B only | **ONLY_IN_B** | Complete pipeline scripts |

## Configs

| File | Source A | Source B | Decision | Rationale |
|------|---------|---------|----------|-----------|
| `policy.yaml` | 5,800 B / 2026-03-15 | Not present | **CANONICAL_A** | Only copy exists in Source A |
| `known_fps.yaml` | 436 B / 2026-03-02 | Not present | **CANONICAL_A** | Only copy exists in Source A |
| `agent_inventory.json` | 2,611 B / 2026-03-24 | Not present | **CANONICAL_A** | Only copy exists in Source A |
| `canonical_baseline.json` | 309 B / 2026-03-24 | Not present | **CANONICAL_A** | Locked metrics baseline |
| `secrets/wazuh_indexer_pass.txt` | 32 B / 2026-03-04 | 32 B (in Build/Config/secrets) | **TEMPLATED** | Copied as .TEMPLATE to prevent credential leakage |

## Proof Artifacts

| File | Source A | Source B (HawkinsOps-audit) | Decision | Rationale |
|------|---------|---------------------------|----------|-----------|
| `heartbeat.json` | SHA256: 8F6220D5... / 1,618 B | SHA256: 8F6220D5... / 1,618 B | **IDENTICAL** | Byte-identical content |
| `coverage_latest.json` | SHA256: 3C795762... / 2,529 B | SHA256: 3C795762... / 2,529 B | **IDENTICAL** | Byte-identical content |
| `run_metrics_latest.json` | SHA256: F219AFEC... / 440 B | SHA256: F219AFEC... / 440 B | **IDENTICAL** | Byte-identical content |
| `policy_audit_latest.json` | 6,521 B | 6,370 B | **CANONICAL_A** | Source A larger/more complete |
| `reconciliation_latest.json` | 7,900 B | 780 B | **Repo version kept** | Repo already has 2026-03-30 version |

## Reports (Source A canonical for all)

| File | Source A Size | Source B Size | Decision | Rationale |
|------|-------------|-------------|----------|-----------|
| `autosoc-triage-quality-history.csv` | 43,669 B | 16,289 B | **CANONICAL_A** | A is 2.7x larger - strict superset |
| `AutoSOC_MARCH_AGENT_SUMMARY.md` | 2,913 B (2026-03-25) | 2,413 B (2026-03-23) | **CANONICAL_A** | A is 2 days newer, more complete |
| `System_Journal_03-2026.md` | 15,600 B (2026-03-24) | N/A | **CANONICAL_A** | Only complete copy |
| `MARCH_TRUTH_INDEX_LATEST.md` | 685 B (2026-03-25) | 678 B (2026-03-23) | **CANONICAL_A** | A is newer |

## Run Manifests

| File | Source A | Source B | Decision | Rationale |
|------|---------|---------|----------|-----------|
| `run_manifest_run_03-04-2026_162827.json` | SHA256: D03BA8C8... / 935 B / 2026-03-20 | SHA256: F704E86E... / 935 B / 2026-03-23 | **CANONICAL_B** | B is later regeneration, internally consistent with C:\RH\OPS path |
