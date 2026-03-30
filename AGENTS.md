# HawkinsOps — Repo-Level Codex Rules
# Location: C:\GitHub\HawkinsOperations\AGENTS.md
# Scope: any Codex session in the repo or its subfolders
# Most specific — overrides all parent AGENTS.md files


---

## THIS REPO IS PUBLIC

Everything committed here is visible to recruiters and the world.
Treat every file as if a hiring manager will read it.

## Project identity

- Purpose: evidence-first SOC portfolio for job hunting
- Target roles: Primary SOC Analyst (T1/T2); Secondary junior detection + automation
- Clearance line (use verbatim everywhere): "Eligible to obtain clearance; willing to pursue sponsorship."

## Codex discovery contract

- Repo-local skills must live in `.agents/skills/`.
- For planning, audits, and redesign work, read these files in order before proposing changes:
  1. `AGENTS.md`
  2. `.internal/PLANS.md`
  3. `docs/PRECEDENCE_CONTRACT.md`
  4. `docs/source-of-truth.md`
  5. `docs/mission-today.md`
  6. `docs/content-architecture.md`
  7. `docs/metrics-integration.md`
  8. `docs/design-stack.md`
- Treat repo docs as authority, not session memory.
- Numeric claims are not trustworthy unless they resolve to the active public-metrics authority defined in `docs/PRECEDENCE_CONTRACT.md`.

## MANDATORY BEFORE EVERY COMMIT

1. Run: .\scripts\verify-counts.ps1
2. Run: python .\scripts\drift_scan.py
3. Confirm no real IPs, credentials, or hostnames in the diff
4. Confirm .gitignore covers Evidence-Raw/ and .obsidian/
5. Get Raylee approval — never push without confirmation

## PHASE 1 PREFLIGHT CHECKS

Before opening or updating a rebrand staging PR, run all of the following:

1. `python -m unittest`
2. `python3 scripts/validate_metrics.py`
3. `scripts/check-md-links.sh`

If any preflight fails, stop and document the failure in a GitHub issue before asking for Phase 2 approval.

## PUBLIC REPO SAFETY

- Do not edit binary files unless the task explicitly requires it.
- Never add secrets, tokens, credentials, raw internal identifiers, or private host data.
- Required approver for rebrand and public proof changes: `raylee`

## COMMIT FORMAT

Add: what you added
Update: what changed and why
Fix: what was broken, what you did
Docs: documentation-only changes
Refactor: structural change, no behavior change

## NUMBERS

Source of truth: PROOF_PACK/VERIFIED_COUNTS.md
Never hardcode counts in site/ or content/ — always reference VERIFIED_COUNTS.md.
Run verify-counts.ps1 any time a detection rule or playbook is added or removed.

## Environment constraints

- Windows 11 + Linux Mint dual-boot
- When giving commands:
  - Prefer PowerShell (`pwsh`) for verification scripts and Windows workflows
  - Use fish-compatible syntax on Linux (avoid bashisms)
- Always use `MM-DD-YYYY` date format in filenames, logs, and documentation.
- Deployment primary: Cloudflare Pages (production)
- Site publish directory is `site/` (static HTML/CSS/JS, no framework)

## Files you must not break

- `PROOF_PACK/VERIFIED_COUNTS.md`
- `START_HERE.md`
- `README.md`
- `site/index.html`
- `scripts/verify/verify-counts.ps1`

## Hosting guardrails

- Cloudflare Pages is the production host.
- Cloudflare project must publish from `site/` and track `main` for production.
- `site/_redirects` supports pretty URLs (`/security -> /security.html`, etc.)
- `site/_headers` exists (security headers)
- `site/404.html` exists (custom 404)
- Resume PDF must exist at: `site/assets/Raylee_Hawkins_Resume.pdf`
- Resume link must be: `/assets/Raylee_Hawkins_Resume.pdf` (absolute path)

## Standard workflow (no vibes)

1. Check repo state first (`git status`, recent commits/PR context if relevant)
2. Make smallest change that satisfies the requested phase
3. Run verification + local test before calling it "done"
4. Keep diffs small; do not add dependencies unless explicitly requested
5. Never print or commit secrets/tokens

## Verification / local test

- Verify counts: `pwsh -File scripts/verify/verify-counts.ps1`
- Serve site locally: `python -m http.server --directory site 8000`
- Minimum click-test paths: `/`, `/security`, `/projects`, `/resume` (PDF download), `/proof`, `/lab`, `/triage`

## WHAT LIVES IN THIS REPO

content/detection-rules/     sigma, splunk, wazuh rules + INDEX.md
content/incident-response/   playbooks, checklists, templates
content/threat-hunting/      windows and linux hunt queries
content/wazuh/       pack, sigma, playbooks, suppression
content/lab/                 proxmox, wazuh configs, runbooks
evidence/            sanitized curated evidence per machine
content/projects/            project deliverables and write-ups
content/             projects.json, detections.json (site data)
site/                hawkinsops.com static HTML
scripts/             verify-counts, drift_scan, generate-site-data
docs/                execution docs, decisions, Progress.log, Wins.md
PROOF_PACK/          verified counts, diagrams, architecture

## WHAT NEVER GOES IN THIS REPO

Evidence-Raw/ content of any kind
Real IPs, hostnames, credentials, or internal identifiers
Machine config files
.obsidian/ folder
