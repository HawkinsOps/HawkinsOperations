# EXECUTION PLAN — Minimum Safe Cleanup Before April 9

**Generated:** 2026-04-04  
**Deadline:** Wednesday April 8 EOD  
**Constraint:** Zero CI, site, or script breakage. Every item verified.

---

## P0 — REMOVE FROM PUBLIC VIEW (Reviewer Risk)

These items are visible to anyone browsing the GitHub repo and create professional risk.

### P0-1: TRUTH_MANIFEST.md

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\TRUTH_MANIFEST.md` |
| **Target path** | `Z:\GitHub\HawkinsOperations\PROOF_PACK\TRUTH_MANIFEST.md` |
| **What it exposes** | Internal audit manifest with operational benchmarks, canonical metric derivations, pipeline architecture details. Reads like internal engineering notes, not a public artifact. |
| **Git tracked?** | Yes |
| **Dependency risk** | NONE from CI or scripts. File has zero inbound references from any workflow, script, or build file. It references `source_of_truth/` paths internally but nothing references it. |
| **Breakage risk** | NONE. No workflow, script, or site page loads this file. |
| **Required ref updates** | None. No file in the repo links to `TRUTH_MANIFEST.md`. |
| **Verification after move** | `pwsh -File scripts/verify/verify-counts.ps1` (confirm CI gate still passes) |

### P0-2: og-generator.html

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\og-generator.html` |
| **Target path** | `Z:\GitHub\HawkinsOperations\tools\og-generator.html` |
| **What it exposes** | Standalone OG image generator. Not harmful, but an HTML file in repo root looks like project debris. |
| **Git tracked?** | Yes |
| **Dependency risk** | NONE. Zero references in any file in the entire repo. |
| **Breakage risk** | NONE. |
| **Required ref updates** | None. |
| **Verification after move** | Visual check — file still opens in browser from new path. |

### P0-3: RELEASE_NOTES_2026-04-01.md

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\RELEASE_NOTES_2026-04-01.md` |
| **Target path** | `Z:\GitHub\HawkinsOperations\docs\release-notes\2026-04-01.md` |
| **What it exposes** | Single release notes file at root. Not harmful content, but clutters root and will accumulate over time. Looks like it was dropped here and never organized. |
| **Git tracked?** | Yes |
| **Dependency risk** | NONE from CI/scripts. Contains one internal link to `REVIEWER_QUICKSTART.md` (update if that file also moves — see P0-7). |
| **Breakage risk** | NONE. |
| **Required ref updates** | Update internal link to REVIEWER_QUICKSTART.md if it gets merged into START_HERE.md (P0-7). |
| **Verification after move** | None required. |

### P0-4: REPO_ABOUT_BLURB.txt

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\REPO_ABOUT_BLURB.txt` |
| **Target path** | DELETE from repo (`git rm`). Save copy to `Z:\Career\drafts\` if wanted. |
| **What it exposes** | One-paragraph GitHub "About" blurb. Harmless but pointless as a committed file — this text goes in GitHub repo settings, not a tracked file. |
| **Git tracked?** | Yes |
| **Dependency risk** | NONE. Zero references anywhere. |
| **Breakage risk** | NONE. |
| **Required ref updates** | None. |
| **Verification after move** | None required. |

### P0-5: Root carousel PNGs (x5)

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\carousel_*.png` (5 files) |
| **Target path** | No action needed — already gitignored, not tracked. |
| **What it exposes** | Nothing to remote viewers. Local-only. |
| **Git tracked?** | No (`.gitignore` line 32: `carousel_*.png`) |
| **Action** | SKIP. These are invisible on GitHub. Optionally delete locally or move to `.internal/`. |

### P0-6: analysis/ directory

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\analysis\backlog-fp-patterns.md` |
| **Target path** | `Z:\GitHub\HawkinsOperations\docs\analysis\backlog-fp-patterns.md` then delete empty `analysis/` |
| **What it exposes** | A single-file top-level directory. Looks like an abandoned folder. |
| **Git tracked?** | Yes (1 file) |
| **Dependency risk** | NONE from CI/scripts. Referenced only in `README.md:172` (directory table row). |
| **Breakage risk** | NONE. |
| **Required ref updates** | `README.md:172` — remove or update the `analysis/` row in the directory table. |
| **Verification after move** | None required. |

### P0-7: REVIEWER_QUICKSTART.md (merge into START_HERE.md)

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\REVIEWER_QUICKSTART.md` |
| **Target path** | Merge content into `START_HERE.md`, then `git rm REVIEWER_QUICKSTART.md` |
| **What it exposes** | Two competing "start here for reviewers" documents at root. Confusing — which one does Kosednar read? |
| **Git tracked?** | Yes |
| **Dependency risk** | Referenced in `RELEASE_NOTES_2026-04-01.md:38` (one link). |
| **Breakage risk** | NONE. No CI, script, or site reference. |
| **Required ref updates** | `RELEASE_NOTES_2026-04-01.md:38` — update link to point to `START_HERE.md` (or skip since we're moving that file to docs/ in P0-3). |
| **Verification after move** | Confirm `START_HERE.md` contains all checklist items from both files. |

### P0-8: README.md directory table update

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\README.md` |
| **Target path** | Edit in place |
| **What it exposes** | Directory table references `analysis/`, `source_of_truth/`, `case-studies/` (root), `tokens/` — all of which are being moved or are misleading. |
| **Dependency risk** | README.md is NOT read by any CI script. It's documentation only. |
| **Breakage risk** | NONE. |
| **Required ref updates** | Update directory table to match post-move reality. Remove rows for moved/deleted dirs. |
| **Verification after move** | Visual review. |

---

## P0 — SAFE MOVES (No CI/Script/Site Dependencies)

These are structural clutter that a reviewer will see in the top-level directory listing.

### P0-9: case-studies/ (root) → content/case-studies/

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\case-studies\` (22 tracked files, 3 case studies) |
| **Target path** | Merge into `Z:\GitHub\HawkinsOperations\content\case-studies\` |
| **What it exposes** | Two `case-studies/` directories (root + content/) — looks like duplication or disorganization. |
| **Git tracked?** | Yes (22 files) |
| **Dependency risk** | NONE from CI/scripts. Referenced only in `README.md:173`. The evidence.yaml files inside use `source_of_truth` as a type label (string value, not a path import). |
| **Breakage risk** | LOW. Verify no name collisions with existing `content/case-studies/` subdirectories before merge. |
| **Required ref updates** | `README.md:173` — remove root `case-studies/` row. |
| **Pre-move check** | Diff `case-studies/` vs `content/case-studies/` to confirm no overlapping subdirectory names. |
| **Verification after move** | `pwsh -File scripts/verify/verify-counts.ps1` |

---

## P0 — DO NOT MOVE THIS WEEK (Confirmed Dangerous)

These items have CI, script, or site path dependencies. Documented here so you don't touch them.

### source_of_truth/ — HAS LIVE DEPENDENCIES

| Ref | File | Line | Type |
|---|---|---|---|
| 1 | `scripts/generate-metrics.js` | `:85` | `path.join(root, "source_of_truth")` — **code reads this dir** |
| 2 | `data/metrics.json` | `:60` | `"canonical_source": "source_of_truth/metrics_canonical_2026-04-01.json"` |
| 3 | `site/index.html` | `:649` | Inline text references the path in a `<p>` tag |
| 4 | `site/proof.html` | `:506` | Evidence reference in HTML |
| 5 | `README.md` | `:176` | Directory table row |
| 6 | `TRUTH_MANIFEST.md` | 15+ lines | Extensive path references throughout |

**Verdict:** Moving `source_of_truth/` requires updating a build script AND two published HTML pages. Too risky for this week. Leave it.

### tokens/ — HAS DOC DEPENDENCIES

| Ref | File | Line | Type |
|---|---|---|---|
| 1 | `docs/design/TASKS_MODERNIZE.md` | — | Task references `tokens/modernize-tokens.json` |
| 2 | `docs/visual-upgrade-package.md` | `:542, :675, :681` | 3 path references including a validation command |

**Verdict:** Moving requires updating 4 references in design docs. Low risk but zero reviewer-facing value. Leave it.

---

## P1 — AFTER THE CALL (April 10+)

These are valuable but either risky or not reviewer-facing.

### P1-1: Move source_of_truth/ → PROOF_PACK/metrics-history/

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\source_of_truth\` (4 JSON files) |
| **Target path** | `Z:\GitHub\HawkinsOperations\PROOF_PACK\metrics-history\` |
| **Required ref updates** | `scripts/generate-metrics.js:85`, `data/metrics.json:60`, `site/index.html:649`, `site/proof.html:506`, `README.md:176`, entire `TRUTH_MANIFEST.md` |
| **Verification** | `node scripts/generate-metrics.js` + `python scripts/drift_scan.py` + site visual check |

### P1-2: Move tokens/ → docs/design/

| Field | Value |
|---|---|
| **Current path** | `Z:\GitHub\HawkinsOperations\tokens\modernize-tokens.json` |
| **Target path** | `Z:\GitHub\HawkinsOperations\docs\design\modernize-tokens.json` |
| **Required ref updates** | `docs/design/TASKS_MODERNIZE.md`, `docs/visual-upgrade-package.md` (lines 542, 675, 681) |
| **Verification** | Grep for `tokens/` to confirm zero remaining refs. |

### P1-3: Add README.md stubs

Create READMEs for: `proof/`, `data/`, `docs/`, `scripts/`, `tools/`. Under 20 lines each. Engineer-to-engineer, no marketing.

### P1-4: Clean up tracked __pycache__ in tools/

| Field | Value |
|---|---|
| **Current path** | `tools/python3/__pycache__/` and `tools/python3/tests/__pycache__/` (6 .pyc files tracked) |
| **Target path** | `git rm -r --cached` + add `**/__pycache__/` to `.gitignore` |
| **Verification** | `git status` confirms files untracked, `.gitignore` updated. |

### P1-5: Consolidate duplicate scripts in scripts/runs/ vs scripts/auto-soc/

Diff and deduplicate: `build_march_truth_index.ps1`, `build_run_manifest.ps1`, `build_runs_index.ps1`, `validate_runs_contract.ps1`.

### P1-6: Gitignore .internal/

Currently not tracked (0 files in git). Add `.internal/` to `.gitignore` as a safety net so it's never accidentally committed.

### P1-7: Git history scrub (BFG)

Interview prep files (`CALL_PREP_*`, `PRACTICE_SCRIPTS*`) are already gitignored and never committed — no history scrub needed. But `TRUTH_MANIFEST.md` will remain in history after `git rm`. Consider BFG if the content is sensitive enough to warrant a force push.

---

## THIS WEEK ONLY — Smallest Safe Cleanup

**8 operations. ~90 minutes with Claude Code. Zero CI risk.**

```
STEP  OPERATION                                       GIT COMMAND
────  ────────────────────────────────────────────────  ─────────────────────────────────────────────
 1    Move TRUTH_MANIFEST.md → PROOF_PACK/             git mv TRUTH_MANIFEST.md PROOF_PACK/
 2    Move og-generator.html → tools/                  git mv og-generator.html tools/
 3    Move RELEASE_NOTES → docs/release-notes/         mkdir -p docs/release-notes
                                                       git mv RELEASE_NOTES_2026-04-01.md docs/release-notes/2026-04-01.md
 4    Delete REPO_ABOUT_BLURB.txt                      git rm REPO_ABOUT_BLURB.txt
 5    Move analysis/ → docs/analysis/                  mkdir -p docs/analysis
                                                       git mv analysis/backlog-fp-patterns.md docs/analysis/
                                                       git rm -r analysis/  (if not auto-removed)
 6    Merge REVIEWER_QUICKSTART into START_HERE         [edit START_HERE.md to include checklist]
                                                       git rm REVIEWER_QUICKSTART.md
 7    Move case-studies/ → content/case-studies/        [verify no name collisions first]
                                                       git mv case-studies/* content/case-studies/
                                                       git rm -r case-studies/  (if not auto-removed)
 8    Update README.md directory table                  [edit: remove analysis/, update case-studies/ 
                                                        path, remove REPO_ABOUT_BLURB reference]
```

**After all 8 steps — run verification:**

```powershell
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
python scripts/drift_scan.py
node scripts/diagnose-site.js --fail-on-issues
```

**Commit message:**
```
chore: clean up repo root — move support files to proper directories
```

**What changes in the top-level view:**

| BEFORE (visible at root) | AFTER |
|---|---|
| `TRUTH_MANIFEST.md` | gone (in PROOF_PACK/) |
| `og-generator.html` | gone (in tools/) |
| `RELEASE_NOTES_2026-04-01.md` | gone (in docs/release-notes/) |
| `REPO_ABOUT_BLURB.txt` | gone (deleted) |
| `REVIEWER_QUICKSTART.md` | gone (merged into START_HERE.md) |
| `analysis/` | gone (in docs/analysis/) |
| `case-studies/` | gone (in content/case-studies/) |

**Net result:** Root drops from 24 directories / 20 files → **17 directories / 13 files**. The remaining clutter (`source_of_truth/`, `tokens/`) stays because it has live dependencies — address in P1 after the call.

**Do NOT touch this week:** `content/`, `PROOF_PACK/`, `scripts/`, `site/`, `proof/`, `data/`, `dist/`, `source_of_truth/`, `tokens/`, `.github/`, any script file, any workflow file.
