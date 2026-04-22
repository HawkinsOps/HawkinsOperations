# Cross-Surface Consistency Matrix — 2026-04-21

Site consistency pass — Task 6. Generated
2026-04-22 on branch `site-consistency-2026-04-21`
after commits C1–C4 + Task 3 + Task 5 landed (through `f2415bc`).

Retitled "2026-04-21" per the sprint prompt's task name; generation
clock read 2026-04-22.

## Scope

Four reviewer-primary pages, per sprint prompt §6.1:

- `site/index.html` → **home**
- `site/proof.html` → **proof**
- `site/case-studies.html` → **case-studies**
- `site/resume.html` → **resume**

Values extracted by regex over hardcoded strings and
`data-verified="…"` / `data-ops="…"` attribute fallbacks. Runtime
JS may overwrite these at render time with the live values from
`site/data/counts.js`, but the fallbacks are what the integrity
script gates against, and what a reviewer sees if JS is delayed
or disabled.

## Matrix

| Field | home | proof | case-studies | resume |
|---|---|---|---|---|
| total_cases | **324,074** | **324,074** | **324,074** | **324,074** |
| auto_close_rate | **~88%** | **~88%** | **~88%** | **~88%** |
| escalated | **8,574** | **8,574** | **8,574** | **8,574** |
| host_coverage | **8/8** | **8/8** | — not rendered | **8/8** |
| reconciliation | **0 mismatches** | **PASS (0 mismatches)** | — not rendered | **0 mismatches** |
| heartbeat | **SUCCESS** | **SUCCESS** | — not rendered | **SUCCESS** |
| sigma | **103** | **103** | **103** | **103** |
| wazuh (rule blocks) | **29** | **29** | — not rendered | **29** |
| wazuh_xml_files | — not rendered | — not rendered | — not rendered | **25** |
| splunk (searches) | **79** | **79** | — not rendered | **79** |
| ir (playbooks) | **10** | **10** | **10** | **10** |
| detections (total) | **211** | **211** | **211** | **211** |
| github link | raylee-hawkins | raylee-hawkins | raylee-hawkins | raylee-hawkins |
| linkedin link | linkedin.com | linkedin.com | linkedin.com | linkedin.com |
| availability | Open to relocation | Open to relocation | Open to relocation | Open to relocation |

## Disagreements across pages

**None.** Every row where a value is rendered on more than one
page shows the same value across all pages that render it.

The dashes above (`— not rendered`) mark absence, not
disagreement — the case-studies index page is a card grid, not a
metrics dashboard; it reasonably doesn't carry host coverage /
reconciliation / heartbeat / per-platform detection counts.
Similarly `wazuh_xml_files` is a resume-page-only data-verified
key, because the integrity script only requires that key on
`resume.html` per its `$resumeKeys` contract at line 90.

## Disagreements vs. canonical facts (sprint prompt §"CANONICAL FACTS")

| Canonical fact | Canonical value | Matrix value | Match? |
|---|---|---|---|
| Total cases | 324,074 | 324,074 | ✓ |
| Auto-close rate | ~88% | ~88% | ✓ |
| Escalations | 8,574 | 8,574 | ✓ |
| Host coverage | 8/8 | 8/8 | ✓ |
| Reconciliation | PASS (0 mismatches) | PASS (0 mismatches) | ✓ |
| Heartbeat | SUCCESS | SUCCESS | ✓ |
| IR playbooks | 10 | 10 | ✓ |

**Zero disagreements.** The sprint prompt's canonical-facts block
did not enumerate detection-inventory values (Fact 3 explicitly
marked those as contested and requiring Raylee's call). After
commit C2 (`truth: promote 2026-04-21 snapshot …`) those values
are canonically **103 / 79 / 29 / 25 / 10 / 211** and the matrix
reflects them uniformly.

## Verification: `verify-site-count-integrity.ps1`

Re-run after all commits in this pass:

```
SITE COUNT INTEGRITY: PASS
 - source: PROOF_PACK/verified_counts.json
 - generated: site/data/counts.js
 - homepage and resume count fallbacks match source-of-truth
EXIT=0
```

Was FAIL before C3; now PASS. No further integrity action needed
for this pass.

## Residual findings worth flagging (report-only)

These were identified during this pass but are out of the pass's
edit scope. Not fixed.

### R1. schema.org `addressLocality` still reads "Huntsville"

- `site/index.html:46` and `site/resume.html:34` — both `Person`
  JSON-LD blocks list `"addressLocality": "Huntsville"`,
  `"addressRegion": "AL"`.
- Semantic argument for leaving it: `PostalAddress` is a
  *physical residence* address, not availability. Changing it to
  one of four relocation targets (Tampa / Jersey City / Dallas /
  LA) would be factually wrong.
- Semantic argument for changing it: search-engine "jobs near
  me" / geo-targeted recruiter queries read `addressLocality`.
  Reviewer impact: a recruiter's LinkedIn-integrated search index
  may still surface this profile as a Huntsville-local match.
- **Recommendation** (post-pass, Raylee's call): drop the
  `PostalAddress` block entirely on both pages, or reduce to just
  `"addressCountry": "US"`. Don't pick a single city — commits
  to one relocation target the resume copy explicitly disclaims.

### R2. `site/wildcard.html:114` career target reads "Defense-adjacent Huntsville ecosystem"

- Timeline item titled **Target** with subtitle "MSFC contractor
  environment. Documentation-first workflow aligns with
  clearance-track role requirements."
- Left alone in Task 3 because the prompt's narrative-prose rule
  was conservative. But this IS an active availability claim
  ("Target:") — it describes intent, not history. With relocation
  expanded to 4 cities, a single MSFC-anchored "Target" item is
  stale.
- **Recommendation**: either retitle to a non-Huntsville-anchored
  target ("Clearance-track detection engineering role, any of
  the relocation targets") or demote from "Target" to
  "Background" and move the timeline forward with a new Target.
  Post-pass editorial decision.

### R3. `site/proof.html:509` evidence-path reference

Reads `data/truth/current-authority.json`; actual path is
`site/data/truth/current-authority.json`. Leading `site/` missing.
Was flagged in ground-truth report §7c (2026-04-21) as out of
scope (Proof page body). Still not fixed; Proof content remains
untouchable in this pass. Post-pass 5-character fix.

### R4. LinkedIn domain canonicalization (from Task 5)

31 references read `linkedin.com/in/raylee-hawkins`; LinkedIn 301s
to `www.linkedin.com/...`. Follows correctly. Optional
post-pass swap to eliminate the redirect hop.

### R5. Minor `reconciliation` phrasing variance

Not a disagreement on value, but a phrasing variance worth a
single sentence: home + resume render the reconciliation claim as
"0 mismatches" without the "PASS" prefix (inside a wrapper
sentence); proof renders the full "PASS (0 mismatches)" per the
authority JSON. Both accurate. Not a consistency defect — the
surrounding sentence context makes each read correctly. No
action.

---

## Summary

- **Every canonical metric is uniform across home / proof /
  case-studies / resume**, to the extent each page renders it.
- **Every rendered value matches the sprint-prompt canonical
  facts block**, zero disagreements.
- **The integrity script passes**, was FAIL at session start.
- **Five residual findings** (schema.org, wildcard target, proof
  path typo, LinkedIn redirect, reconciliation phrasing) are
  documented for post-pass review. None are material to
  this pass.

---

*Generated 2026-04-22. Report covers state through commit
`f2415bc` (link integrity report). Branch still unpushed.*
