# Ground Truth Report — 2026-04-21

Site consistency pass — Task 0. Report-only. No surface has been
modified. Branch: `site-consistency-2026-04-21` from
`main@7640cf4`.

---

## 1. Script Output

### 1a. `scripts/verify/verify-counts.ps1` — EXIT 0

```
======================================
HawkinsOps Detection Content Counts
======================================

Sigma (.yml/.yaml files): 103
Splunk (.spl files):      9
Splunk (searches):        79
Wazuh XML files:          25
Wazuh <rule id=> blocks:  29
IR Playbooks (IR-*.md):   10
```

Derived total (Sigma + Splunk searches + Wazuh blocks + IR): **221**.
Using file-level counts (Sigma + Splunk SPL + Wazuh XML + IR): **147**.
Neither matches the authority JSON's `total_detections: 210`.

### 1b. `scripts/verify/verify-site-count-integrity.ps1` — EXIT 1 (FAIL)

```
SITE COUNT INTEGRITY: FAIL
 - resume.html missing data-verified fallback for 'wazuh_xml_files'
```

Single failure, isolated to `site/resume.html`. Separate from the
count-drift issue below.

---

## 2. Authority JSON

File: `site/data/truth/current-authority.json` (commit 3f64ef7,
touched 2026-04-21 in `truth: retitle authority file provenance`).
Schema `truth-authority-v1`, `_layer_rank` 1, authority_date
`2026-04-07`.

### 2a. Detection inventory (authority)

| Field                         | Value |
|-------------------------------|------:|
| sigma_rules                   | 103   |
| splunk_spl_files              | 9     |
| splunk_detection_searches     | 79    |
| wazuh_xml_files               | **24** |
| wazuh_rule_blocks             | **28** |
| ir_playbooks                  | 10    |
| total_detections              | **210** |

`public_claim_formats`:
- `wazuh`: `"24 Wazuh XML files (28 rule blocks)"`
- `total_detections`: `"210 detections"`

### 2b. Metrics (authority)

| Field                   | Value            |
|-------------------------|------------------|
| total_cases             | 324,074          |
| auto_close_rate         | ~88%             |
| escalated               | 8,574            |
| coverage_ratio          | 8/8              |
| reconciliation          | PASS (0 mismatches) |
| heartbeat               | SUCCESS          |
| ir (playbooks label)    | 10               |

### 2c. Provenance

`_provenance_note`: "Detection inventory is script-verified via
scripts/verify/verify-counts.ps1. Case-volume metrics are transcribed
from the AutoSOC pipeline ledger output as of the authority_date; the
case-volume transcription step is not yet automated. See /methodology
for full provenance map."

`_source`: `source_of_truth/metrics_canonical_2026-04-07.json`

---

## 3. Rendered Surfaces — Contested Detection Strings

Strings: `28 Wazuh`, `29 Wazuh`, `28 rule`, `29 rule`, `210 rules`,
`211 rules`, `210 detection`, `211 detection`, and related pairs.

### 3a. "28 / 24 / 210" surfaces (authority-aligned, script-stale)

| File | Line | Excerpt |
|---|---|---|
| site/data/truth/current-authority.json | 33 | `"wazuh": "24 Wazuh XML files (28 rule blocks)"` |
| site/data/truth/current-authority.json | 34 | `"total_detections": "210 detections"` |
| docs/SignalFoundry_Case_Study_March2026.md | 29 | `210 detections across 3 platforms` |
| docs/SignalFoundry_Case_Study_March2026.md | 207 | `24 files / 28 rule blocks` |
| docs/SignalFoundry_Case_Study_March2026.md | 342 | `28 Wazuh rule blocks` |
| docs/VALIDATION_FRAMEWORK.md | 272 | `28 rule blocks` |

### 3b. "29 / 25 / 211" surfaces (script-aligned, authority-stale)

| File | Line | Excerpt |
|---|---|---|
| content/detection-rules/mappings/attack-navigator-layer.json | 9 | `211 detection rules (103 Sigma, 29 Wazuh, 79 Splunk...)` |
| content/case-studies/autosoc-pipeline-recovery/reviewer_lanes.md | 102 | `25 files, 29 rule blocks` |
| main commit 7640cf4 title | — | `detections: reconcile all public counts to verify-counts ground truth (103/79/29/25/10/211)` |

### 3c. Rendered site pages — inspected, no count strings found by raw sweep

The detection-count strings above did not match inside any file under
`site/*.html` at rendered text level. The rendered site pages carry
detection numbers through `data-verified` attributes (e.g.
`<span data-verified="wazuh_xml_files">25</span>` in
`site/case-study.html:118`) — runtime-substituted, not hardcoded.
That `25` is already the script value, not the authority value.
**That is a live disagreement between the HTML fallback and the
authority JSON**, which is exactly what the integrity script is
supposed to catch and why it failed on `resume.html`. Full page-by-
page audit of `data-verified` attributes is Task 6 territory and
was not done here.

Detection-count strings in **resume/site/proof area that were found**:
- site/case-study.html:118 — `<span data-verified="wazuh_xml_files">25</span> XML files` (fallback = 25, authority says 24)

---

## 4. Rendered Surfaces — Canonical Metrics (324,074 / 8,574)

Every occurrence sampled reads **324,074 cases / 8,574 escalations**.
No disagreement with the canonical-facts block at the top of the
sprint prompt.

Notable locations (non-exhaustive, evidence of propagation path):

- `site/data/truth/current-authority.json` — authoritative
- `site/data/truth/current-live.json` — runtime feed; same values
- `site/data/ops-metrics.js`, `site/assets/data/ops-metrics.json` — projections, same values
- `data/metrics.json`, `source_of_truth/metrics_canonical_2026-04-07.json` — upstream snapshot
- `proof/quality/latest.{md,json}`, `site/proof/quality/latest.{md,json}` — runtime quality gate, same values
- Site HTML: `site/index.html` (hero + funnel SVG text + case breakdown), `site/proof.html` (KPIs + evidence pack + modal), `site/resume.html` (PS/OF blocks), `site/signalfoundry.html`, `site/detections.html`, `site/case-studies.html`, `site/architecture.html`, `site/march-2026-deep-dive.html`, `site/case-study-race-condition.html`, `site/case-study-pipeline-recovery.html`
- SVGs: `site/assets/autosoc-decision-flow.svg`, `site/assets/ops-bridge.svg`, `site/assets/signalfoundry-pipeline.svg`, and `pp_soc_integration/` duplicates

One minor note: `site/proof.html:509` cites the evidence path as
`data/truth/current-authority.json` — the leading `site/` is
omitted. The actual path is `site/data/truth/current-authority.json`.
Proof page is out of scope to touch; flagging for Task 6.

---

## 5. Rendered Surfaces — Location ("Huntsville")

Classification:
- **A. Availability / hero / contact** (in scope for Task 3 change)
- **B. Footer "Huntsville-adjacent (North Alabama)"** (in scope — it's
  a brand/location line in the footer, recurring on most site pages)
- **C. Narrative / historical / SEO meta** (judgment call per Task 3.3)

### 5a. Availability / hero / contact (change)

| File | Line | Excerpt | Class |
|---|---|---|---|
| site/index.html | 46 | `"addressLocality": "Huntsville"` (schema.org) | A |
| site/index.html | 153 | `Huntsville, AL<br>` (hero contact block) | A |
| site/resume.html | 34 | `"addressLocality": "Huntsville"` (schema.org) | A |
| site/resume.html | 136 | `<span class="rt rt-soft">North Alabama · Huntsville</span>` | A |
| site/resume.html | 139 | `📍 North Alabama (Huntsville preferred)` | A |
| site/wildcard.html | 95 | `Open to SOC Analyst / Detection Engineer roles - Huntsville, AL | Sept 2026 target` | A |

### 5b. Footer brand-location (change — all instances)

| File | Line | Excerpt |
|---|---|---|
| site/index.html | 576 | `<p><b>HawkinsOps</b> | Huntsville-adjacent (North Alabama)</p>` |
| site/proof.html | 702 | same |
| site/resume.html | 487 | same |
| site/detections.html | 329 | same |
| site/case-studies.html | 636 | same |
| site/signalfoundry.html | 352 | same |
| site/enterprise-security.html | 780 | same |
| site/case-study.html | 170 | same |
| site/projects.html | 170 | same |
| site/march-2026-deep-dive.html | 290 | same |
| site/wildcard.html | 347 | same |
| site/operations-bridge.html | 234 | same |
| site/honeypot-proof.html | 157 | same |
| site/case-study-soc-integration.html | 197 | same |
| site/autosoc-hotfix-rca.html | 263 | same |
| site/autosoc-cutover.html | 271 | same |
| site/case-study-wazuh.html | 304 | same |
| site/case-study-pipeline-recovery.html | 302 | same |
| site/case-study-splunk-detection-audit.html | 251 | same |
| site/case-study-threat-hunt-4688.html | 261 | same |
| site/case-study-splunk-codex-hunt.html | 273 | same |
| site/case-study-sigma-library.html | 253 | same |
| site/case-study-security-hardening.html | 282 | same |
| site/case-study-race-condition.html | 386 | same |
| site/case-study-ir-playbooks.html | 250 | same |
| site/case-study-ir-howe01.html | 304 | same |
| site/case-study-honeypot.html | 225 | same |
| site/case-study-detection-harness.html | 230 | same |
| site/case-study-cve-patch.html | 207 | same |
| site/blog-python2-to-python3.html | 123 | same |

**30 pages carrying the "Huntsville-adjacent (North Alabama)" footer.**

DECISION NEEDED: Task 3 canonical new text is
`"Relocating — Tampa / Jersey City / Dallas / LA"`. Task 3.1/3.2
specify only the **homepage hero** change explicitly. Task 3.3 says
update matches in "hero / contact / availability contexts". The
footer brand-line is a location claim on every page; leaving it
stale contradicts Fact 2. Three options — surfaced in message body.

### 5c. Other / narrative / out-of-scope

| File | Line | Excerpt | Suggested class |
|---|---|---|---|
| README.md | 175 | `Location: Gadsden, AL, relocating to Huntsville, AL` | A (stale; repo README) |
| site/index.html | 5, 13, 21 | `<meta name="description" content="…in Huntsville, AL.">` (+ og:, twitter:) | A (SEO; ships to every share card) |
| site/resume.html | 452 | `<li>Huntsville cyber network</li>` (network context list item) | B/C — judgment |
| site/resume.txt | 4 | `Location: North Alabama (Huntsville-adjacent)` | A (resume text) |
| site/resume-content.md | 2 | `North Alabama (Huntsville-adjacent)` | A (resume source) |
| docs/PORTFOLIO_SIGNAL_AUTOSOC.md | 16 | `## Huntsville Gate Handling Lines` (heading; likely factual history) | C — leave |

---

## 6. Rendered Surfaces — GitHub URL

Every footer and every artifact link in the repo points at
`github.com/HawkinsOps/HawkinsOperations` — the 404 URL per Fact 1.
**Zero occurrences** of `github.com/raylee-hawkins/HawkinsOperations`
in the repo. Every surface is stale.

Counts:
- HTML / JSON / JS / MD files with at least one `HawkinsOps/HawkinsOperations`: **~50 lines across ~30 files** (sample below; full list in Task 2).
- Configuration: `.github/ISSUE_TEMPLATE/config.yml` (2 entries),
  `CONTRIBUTING.md`, `scripts/setup-runner.sh` (4 lines),
  `site/README_DEPLOY.md`.
- Scope-impact (per sprint prompt, Task 2 only touches footers):
  - **Footer GitHub link** occurs on ~30 site/*.html pages —
    same enumeration as §5b footer list, at line numbers 2 greater
    (e.g. site/index.html:578 vs footer at :576).
  - **Non-footer site references** (nav CTAs, artifact deep links)
    exist on: site/index.html:73 (schema.org), site/signalfoundry.html:179
    (Inspect Repository CTA), site/proof.html:394/582/583/614/663/664/665
    (button + evidence), site/case-study.html:118-121 (artifact deep
    links), site/march-2026-deep-dive.html:282 (GitHub Repo button),
    site/resume.html:39 (schema.org array), site/case-study-*.html
    (evidence/artifact links on most case studies),
    site/enterprise-security.html (4 deep links),
    site/honeypot-proof.html:109/110/145 (artifact paths),
    site/march-2026-release.html:4/8 (meta refresh redirect).
  - **Non-site references**: content/projects.json,
    content/detections.json, site/assets/data/{detections,projects}.json
    (duplicate data), site/assets/components/sections/listing-renderer.js,
    docs/*, PROOF_PACK/site_link_inventory.md, content/case-studies/*.

DECISION NEEDED: Task 2 says "Grep every page for footer GitHub
references … Canonicalize every footer GitHub link". Task 2's scope
is worded as footers only. But every non-footer occurrence on the
site is **also** a 404 today. Three options — surfaced in message
body.

---

## 7. Disagreements Summary

### 7a. Hard disagreement — detection inventory

| Signal | Wazuh XML files | Wazuh rule blocks | Total detections |
|---|---:|---:|---:|
| verify-counts.ps1 (script, now) | **25** | **29** | (sum 221 / 147) |
| current-authority.json (04-07 snapshot) | **24** | **28** | **210** |
| main commit 7640cf4 title intent | 25 | 29 | 211 |
| attack-navigator-layer.json (content/) | — | **29** | **211** |
| reviewer_lanes.md (case study) | **25** | **29** | — |
| site HTML data-verified fallback (case-study.html) | **25** | — | — |
| docs/SignalFoundry_Case_Study_March2026.md | **24** | **28** | **210** |
| docs/VALIDATION_FRAMEWORK.md | — | **28** | — |

Two truth eras coexist. Per Fact 3 of the prompt, these are
**contested** and must not be propagated without Raylee's call.

### 7b. Hard failure — integrity script

`resume.html` missing `data-verified` fallback for `wazuh_xml_files`.
Scope: single attribute on a single page. Not a number dispute, a
missing attribute dispute.

### 7c. Soft issue — Proof page evidence path

`site/proof.html:509` cites `data/truth/current-authority.json`,
actual is `site/data/truth/current-authority.json`. Out of scope
(Proof content untouchable). Report-only.

### 7d. No disagreement — canonical metrics

324,074 cases / 8,574 escalations / ~88% auto-close / 8/8 coverage /
PASS / SUCCESS all uniform across the repo and align with the
canonical-facts block in the sprint prompt.

---

## 8. Recommendation (for Raylee)

Neither "28/24/210" nor "29/25/211" is unilaterally fixable by this
agent. Three distinct resolution paths:

- **Path A**: Re-snapshot the authority JSON to today's verify
  output (bump `_authority_date` to 2026-04-21, set wazuh_xml_files
  to 25, wazuh_rule_blocks to 29, total_detections to 211, and
  update `public_claim_formats`). This aligns authority with script
  and with main@7640cf4's stated intent. Audit docs follow.
- **Path B**: Revert the new Wazuh XML file so the disk matches the
  2026-04-07 snapshot. Numbers stay at 28/24/210 everywhere. Simpler
  but destructive of legitimate work.
- **Path C**: Do nothing; site ships inconsistent. Not recommended.

The integrity-script FAIL on `resume.html` is a separate 1-line
data-verified attribute addition, independent of A/B/C.

All three are decisions for Raylee, not the agent. Task 0 stops
here per protocol.

---

*Generated: 2026-04-21 by the site consistency pass, Task 0.*
*Report file is untracked; no commits yet on branch
`site-consistency-2026-04-21`.*
