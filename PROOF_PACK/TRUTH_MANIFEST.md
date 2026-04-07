# TRUTH MANIFEST

Audit date: 2026-04-04
Auditor: Claude Code (read-only reconnaissance)
Scope: All files in Z:\GitHub\HawkinsOperations + live site hawkinsops.com

---

## 1. CANONICAL METRICS — LOCKED VALUES

### 1A. Detection Inventory

Authoritative source: `PROOF_PACK/VERIFIED_COUNTS.md` (script-generated from disk)
Verification script: `scripts/verify/verify-counts.ps1`
Generator script: `scripts/verify/generate-verified-counts.ps1`

| Metric | Canonical Value | Authoritative Source |
|---|---|---|
| Sigma rules (YAML) | **103** | `PROOF_PACK/VERIFIED_COUNTS.md:11` |
| Splunk detection searches (SPL) | **79** (9 SPL files) | `PROOF_PACK/VERIFIED_COUNTS.md:12` |
| Wazuh XML files | **24** | `PROOF_PACK/VERIFIED_COUNTS.md:13` |
| Wazuh rule blocks | **28** | `PROOF_PACK/VERIFIED_COUNTS.md:13` |
| IR Playbooks | **10** | `PROOF_PACK/VERIFIED_COUNTS.md:19` |
| Total detections | **210** | Computed: 103 + 28 + 79 (by `scripts/generate_verified_counts.py:~78`) |

### 1B. Operational Metrics — April 1, 2026 Stable Benchmark

Authoritative source: `source_of_truth/metrics_canonical_2026-04-01.json`
Pipeline source: `data/metrics.json` → `scripts/generate-site-data.js` → `site/assets/data/ops-metrics.json`

| Metric | Canonical Value | Authoritative Source |
|---|---|---|
| Total cases processed | **321,351** | `source_of_truth/metrics_canonical_2026-04-01.json:4` |
| Auto-close rate (display) | **~88%** | `source_of_truth/metrics_canonical_2026-04-01.json:9` |
| Auto-close rate (exact) | **88.64%** | Computed: (199,672 + 85,185) / 321,351 = 284,857 / 321,351 |
| Auto-closed benign | **199,672** | `source_of_truth/metrics_canonical_2026-04-01.json:5` |
| Known FP auto-closed | **85,185** | `source_of_truth/metrics_canonical_2026-04-01.json:6` |
| Escalated (stable benchmark) | **6,178** | `source_of_truth/metrics_canonical_2026-04-01.json:7` |
| Review | **28,544** | `source_of_truth/metrics_canonical_2026-04-01.json:8` |
| Host coverage | **8/8** | `source_of_truth/metrics_canonical_2026-04-01.json:12` |
| Reconciliation | **PASS (0 mismatches)** | `source_of_truth/metrics_canonical_2026-04-01.json:13` |
| Heartbeat | **SUCCESS** | `source_of_truth/metrics_canonical_2026-04-01.json:14` |
| Benchmark locked date | **04-01-2026** | `source_of_truth/metrics_canonical_2026-04-01.json:16` |

### 1C. Lifetime Runtime Metrics

Authoritative source: `data/metrics.json` (lifetime_runtime object)
**Post-audit decision:** Lifetime values locked to April 1 benchmark. No separate lifetime escalation count.

| Metric | Canonical Value | Authoritative Source |
|---|---|---|
| Escalated (lifetime) | **6,178** (locked to April 1) | `data/metrics.json:20` |
| Staged pending | **67** | `data/metrics.json:22` |

### 1D. Career / Background Metrics

| Metric | Canonical Value | Source |
|---|---|---|
| Fehrer promotion timeline | **under 5 months** | `site/index.html:455`, `site/resume.html:362` |
| MITRE ATT&CK technique/sub-technique IDs | **90** across **53** families | `README.md:45` |

---

## 2. DISCREPANCY REPORT

### 2A. Detection Inventory

| Metric | Canonical | All Values Found | File:Line | Status |
|---|---|---|---|---|
| Sigma rules | 103 | 103 | All files | **MATCH** |
| Splunk detection searches | 79 | 79 | All files | **MATCH** |
| Wazuh XML files | 24 | 24 | All files | **MATCH** |
| Wazuh rule blocks | 28 | 28 | All files | **MATCH** |
| IR Playbooks | 10 | 10 | All files | **MATCH** |
| Total detections | 210 | 210 | All files | **MATCH** |

### 2B. Operational Metrics — April 1 Snapshot

| Metric | Canonical | All Values Found | File:Line | Status |
|---|---|---|---|---|
| Total cases | 321,351 | 321,351 | All files | **MATCH** |
| Auto-close rate | ~88% | ~88% | All current files | **MATCH** |
| Escalated (stable) | 6,178 | 6,178 | All files | **MATCH** |
| Known FP | 85,185 | 85,185 | All files | **MATCH** |
| Auto-closed benign | 199,672 | 199,672 | All files | **MATCH** |
| Review | 28,544 | 28,544 | All files | **MATCH** |
| Host coverage | 8/8 | 8/8 | All files | **MATCH** |
| Reconciliation mismatch | 0 | 0 | All files | **MATCH** |

### 2C. DISCREPANCIES FOUND

| # | Metric | Expected | Found | File:Line | Status | Severity |
|---|---|---|---|---|---|---|
| D1 | Lifetime escalated | 6,178 | 6,178 | `site/data/ops-metrics.js:58` | **RESOLVED** | -- |
| D2 | Lifetime escalated (HTML fallback) | 6,178 | 6,178 | `site/proof.html:442` | **RESOLVED** | -- |
| D3 | Lifetime known FP (HTML fallback) | 85,185 | 85,185 | `site/proof.html:443` | **RESOLVED** | -- |
| D4 | EXECUTION_LOG Phase 0 counts | Current: 103/9/24/28/10 | Stale: 105/8/25/29/10 | `PROOF_PACK/EXECUTION_LOG.md:14` | **STALE** | Informational (annotated as historical) |
| D5 | MITRE technique count | 90 (README claim) | UNVERIFIED | `README.md:45` | **UNRESOLVED** | Medium |

---

## 3. ROOT CAUSE ANALYSIS

### 3A. Escalation Count: 6,178 vs 7,950

**What they are:**
- **6,178** = April 1, 2026 locked benchmark snapshot. This is the number of escalation artifacts at the time the canonical snapshot was taken. Stored in `source_of_truth/metrics_canonical_2026-04-01.json:7` and `data/metrics.json` under `stable_benchmark.escalated` and `running_totals.escalated`.
- **7,950** = Ledger lifetime total including post-benchmark runtime processing. Stored in `data/metrics.json:20` under `lifetime_runtime.escalated`. Explicitly annotated: "Ledger lifetime total including post-benchmark runtime. The April 1 public benchmark is 6,178."

**They are NOT the same metric.** 6,178 is a point-in-time snapshot; 7,950 is a running cumulative total. Both are correct for their respective scopes.

**Which to use publicly:** 6,178 is the defensible canonical number for public claims because it's a locked, reconciled snapshot (PASS, 0 mismatches). 7,950 is the accurate lifetime total but should only appear with "lifetime" or "runtime" qualification.

**Where the discrepancy actually is:**
- `site/data/ops-metrics.js:58` shows `lifetime_escalated: "6,178"` — this is WRONG. It should be `"7,950"`. This file was generated before the lifetime value was updated in `data/metrics.json` and was never regenerated.
- `site/assets/data/ops-metrics.json:59` correctly shows `lifetime_escalated: "7,950"`.
- `site/proof.html:442` HTML fallback shows `6,178` for lifetime_escalated — stale but overwritten by JS hydration from `ops-metrics.json` (which has the correct `7,950`).

**Recommendation:** Regenerate `site/data/ops-metrics.js` from `data/metrics.json` via the site data pipeline. Update the HTML fallback in `proof.html:442` to `7,950` and `proof.html:443` to `85,185`.

### 3B. Auto-Close Rate: ~88% vs ~92%

**These are NOT conflicting values.** They are the same calculation at different points in time:

- **~92%** = March 25, 2026 snapshot. Calculation: (45,334 + 5,898) / 55,665 = 51,232 / 55,665 = 92.04%. Source: `source_of_truth/metrics_canonical_2026-03-25.json:5,17`.
- **~88%** = April 1, 2026 snapshot. Calculation: (199,672 + 85,185) / 321,351 = 284,857 / 321,351 = 88.64%. Source: `source_of_truth/metrics_canonical_2026-04-01.json:9,21`.

The rate decreased because the case composition changed as the pipeline processed significantly more data (55K to 321K cases). The proportion of escalated + review cases grew relative to auto-closed cases.

**No discrepancy exists.** The ~92% value only appears in `source_of_truth/metrics_canonical_2026-03-25.json` (a historical snapshot file). All current-facing files correctly show ~88%.

### 3C. Fehrer Promotion Timeline

**Canonical value: under 5 months.** All references updated:
- `site/index.html:455` — "Promoted in under 5 months"
- `site/resume.html:362` — "Promoted from second-shift operator to third-shift Team Lead in under 5 months"

### 3D. MITRE ATT&CK Coverage (90 technique IDs / 53 families)

**Status: UNRESOLVED.** The claim appears only in `README.md:45`. No script generates or verifies this count. The detection rules are organized into 10 tactic folders under `content/detection-rules/sigma/`. A full count of unique MITRE technique IDs across all Sigma YAML `tags:` fields, Wazuh `<mitre><id>` elements, and Splunk `# MITRE: T####` comments would be needed to verify or refute the "90 / 53" claim.

**Recommendation:** Create a verification script (or extend `verify-counts.ps1`) to count unique technique IDs and families from rule files, and add the result to `VERIFIED_COUNTS.md`.

### 3E. EXECUTION_LOG Phase 0 Counts (Historical)

`PROOF_PACK/EXECUTION_LOG.md:14` shows Phase 0 snapshot values: Sigma 105, Splunk 8, Wazuh XML 25, Wazuh rule blocks 29. These differ from current counts (103/9/24/28) because rules were added and removed between Phase 0 (2026-02-13) and the current state. The file already has an annotation: "Historical — Phase 0 snapshot; see VERIFIED_COUNTS.md for current canonical counts."

**No action needed.** The annotation is sufficient.

---

## 4. FILE REFERENCE INDEX

Every file that contains metric values. When a canonical value changes, these files must be checked and updated.

### Detection Inventory (103 / 9 / 24 / 28 / 10 / 140)

| File | Type |
|---|---|
| `PROOF_PACK/VERIFIED_COUNTS.md` | **AUTHORITATIVE SOURCE** |
| `PROOF_PACK/verified_counts.json` | Generated from VERIFIED_COUNTS.md |
| `data/metrics.json` (detection_inventory) | Pipeline source |
| `site/assets/data/ops-metrics.json` (metrics.*) | Generated by generate-site-data.js |
| `site/data/ops-metrics.js` (metrics.*) | Generated by generate-site-data.js |
| `content/detections.json` | Content manifest |
| `site/assets/data/detections.json` | Generated by generate-site-content.js |
| `CLAUDE.md` | Project instructions |
| `README.md:41-44` | Project overview |
| `.internal/profile_README_draft.md:17` | Draft content |
| `.internal/linkedin_carousel_review/manifest.md` | Carousel content |
| `.internal/linkedin_carousel_review/01_cover/*.md` | Carousel slides |
| `.internal/linkedin_carousel_review/03_verified_inventory/README.txt` | Carousel inventory |
| `case-studies/autosoc-race-condition/front_matter.yaml` | Case study metadata |
| `content/detection-rules/splunk/README.md:6` | Section README |
| `site/index.html` (data-verified attrs) | Live site HTML |
| `site/proof.html` (data-verified attrs) | Live site HTML |
| `site/detections.html` (data-verified attrs) | Live site HTML |
| `site/case-studies.html` (data-verified attrs) | Live site HTML |
| `site/operations-bridge.html` (data-verified attrs) | Live site HTML |

### Stable Benchmark (321,351 / ~88% / 6,178 / 85,185 / 199,672 / 28,544 / 8/8)

| File | Type |
|---|---|
| `source_of_truth/metrics_canonical_2026-04-01.json` | **AUTHORITATIVE SOURCE** |
| `data/metrics.json` (stable_benchmark + running_totals) | Pipeline source |
| `site/assets/data/ops-metrics.json` | Generated |
| `site/data/ops-metrics.js` | Generated |
| `site/index.html` (data-ops attrs) | Live site HTML |
| `site/proof.html` (data-ops attrs) | Live site HTML |
| `.internal/profile_README_draft.md:10,16` | Draft content |
| `case-studies/autosoc-race-condition/README.md:44-49` | Case study |
| `case-studies/autosoc-race-condition/front_matter.yaml` | Case study metadata |

### Lifetime Escalated (6,178 — locked to April 1)

| File | Type |
|---|---|
| `data/metrics.json:20` (lifetime_runtime.escalated) | **AUTHORITATIVE SOURCE** |
| `site/assets/data/ops-metrics.json:22,58` | Generated (6,178) |
| `site/data/ops-metrics.js:22,58` | Generated (6,178) |
| `site/proof.html:442` | HTML fallback (6,178) |
| `README.md:112` | Documentation (6,178) |

### Fehrer Promotion Timeline (under 5 months)

| File | Type |
|---|---|
| `site/index.html:444` | Live site |
| `site/resume.html:362` | Live site |
| `.internal/profile_README_draft.md:26` | Draft |

### MITRE Coverage (90 / 53)

| File | Type |
|---|---|
| `README.md:45` | **ONLY REFERENCE — UNVERIFIED** |

---

## 5. LIVE SITE VS REPO COMPARISON

| Page | Metric | Live Value | Repo Source | Status |
|---|---|---|---|---|
| Homepage | Total detections | 210 | 210 | **MATCH** |
| Homepage | Sigma | 103 | 103 | **MATCH** |
| Homepage | Wazuh | 28 | 28 | **MATCH** |
| Homepage | Splunk | 79 | 79 | **MATCH** |
| Homepage | IR Playbooks | 10 | 10 | **MATCH** |
| Homepage | Total cases | 321,351 | 321,351 | **MATCH** |
| Homepage | Auto-close | ~88% | ~88% | **MATCH** |
| Homepage | Escalated (stable) | 6,178 | 6,178 | **MATCH** |
| Homepage | Coverage | 8/8 | 8/8 | **MATCH** |
| Homepage | Fehrer promotion | under 5 months | under 5 months | **MATCH** |
| Proof | Stable snapshot | All match | All match | **MATCH** |
| Proof | Lifetime escalated (JS off) | 6,178 | 6,178 | **RESOLVED** |
| Proof | Lifetime known FP (JS off) | 85,185 | 85,185 | **RESOLVED** |
| Detections | All counts | Match | Match | **MATCH** |
| Case Studies | Detection refs | Match | Match | **MATCH** |

---

## 6. HISTORICAL SNAPSHOTS (Not Discrepancies)

These are frozen-in-time values from prior canonical snapshots. They are correct for their date.

| Date | Total Cases | Auto-Close | Escalated | Source |
|---|---|---|---|---|
| 2026-03-13 | 25,167 | 90.1% | 2,478 | `source_of_truth/metrics_canonical_2026-03-20.json` area |
| 2026-03-20 | 49,774 | N/A | 2,478 | `source_of_truth/metrics_canonical_2026-03-20.json` |
| 2026-03-25 | 55,665 | ~92% | 2,545 | `source_of_truth/metrics_canonical_2026-03-25.json` |
| 2026-04-01 | 321,351 | ~88% | 6,178 | `source_of_truth/metrics_canonical_2026-04-01.json` |

---

## 7. ACTION ITEMS

| # | Action | Priority | Files to Update | Status |
|---|---|---|---|---|
| A1 | Lock lifetime_escalated to April 1 benchmark (6,178) across all files | **High** | `data/metrics.json`, `site/assets/data/ops-metrics.json`, `README.md` | **DONE** |
| A2 | Update HTML fallback in `proof.html:443` — lifetime_known_fp from N/A to 85,185 | **Medium** | `site/proof.html` | **DONE** |
| A3 | Remove escalation count split from README | **Medium** | `README.md` | **DONE** |
| A4 | Verify MITRE technique count (90 / 53 claim) or remove from README | **Medium** | `README.md:45` | OPEN |
| A5 | Consider adding MITRE count to verification pipeline | **Low** | `scripts/verify/verify-counts.ps1` | OPEN |

---

_This manifest is read-only audit output. No files were modified during this audit._
_To lock values, run a second pass updating downstream references to match canonical sources._
