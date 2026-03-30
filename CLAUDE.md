# CLAUDE.md — HawkinsOperations

This file guides AI assistants (Claude, Codex, etc.) working in this repository.
Read the full file before making any changes.

---

## Repository Identity

**HawkinsOperations** is an evidence-first SOC portfolio built for job hunting.

- **Owner:** Raylee Hawkins (`raylee@hawkinsops.com`)
- **Site:** https://hawkinsops.com (Cloudflare Pages, static)
- **Target roles:** SOC Analyst T1/T2, junior detection engineering, SOC automation
- **Clearance line (use verbatim):** "Eligible to obtain clearance; willing to pursue sponsorship."

The repository contains reproducible, verifiable security artifacts — detection rules,
incident response playbooks, and a static portfolio site — all with automated count
verification baked into CI.

---

## Directory Map

```
HawkinsOperations/
├── .github/                    # CI/CD workflows, issue templates, PR template
│   └── workflows/
│       ├── verify.yml          # Main verification pipeline (Windows runner)
│       ├── drift-scan.yml      # Markdown/JSON/HTML consistency (Ubuntu runner)
│       └── public-safety-gate.yml  # PII/credential scan on site/* PRs
├── .codex/                     # Claude Codex runtime context
├── components/                 # Reusable HTML/CSS design system sections
├── content/                    # Structured JSON content
│   ├── projects.json           # Project metadata and evidence links
│   ├── detections.json         # Detection platform summary with counts
│   └── media.json              # Media manifest
├── content/detection-rules/            # Multi-platform detection content
│   ├── sigma/                  # 103 Sigma YAML rules, organized by MITRE tactic
│   ├── splunk/                 # 9 SPL queries
│   ├── content/detection-rules/wazuh/rules/  # 24 Wazuh XML files (28 rule blocks)
│   └── mappings/               # MITRE ATT&CK mapping files
├── docs/                       # Execution notes, architecture docs, hosting runbooks
├── evidence/                   # Wazuh deployment evidence logs
├── content/incident-response/
│   ├── playbooks/              # 10 IR playbooks (IR-001 through IR-022)
│   └── templates/              # IR-Template.md baseline
├── content/lab/                        # Lab infrastructure docs (Proxmox, Wazuh, Grafana)
├── content/projects/                   # Reference/legacy projects
│   ├── lab/enterprise-hardening/  # Enterprise security Phase 2 artifacts
│   └── migration-rh/           # Migration project reference artifacts
├── proof/                      # Wazuh honeypot proof artifacts (auto-updated)
├── PROOF_PACK/                 # Curated review artifacts — source of truth for counts
│   ├── VERIFIED_COUNTS.md      # *** THE source of truth for all public numbers ***
│   ├── verified_counts.json    # Machine-readable version of above
│   ├── PROOF_INDEX.md          # Entry points for technical reviewers
│   ├── ARCHITECTURE.md         # Detection and response architecture overview
│   ├── EVIDENCE_CHECKLIST.md   # Sanitization requirements
│   └── REDACTION_RULES.md      # Redaction patterns in use
├── scripts/                    # Build, verification, and deployment scripts
│   ├── verify/
│   │   ├── verify-counts.ps1       # PowerShell count checker
│   │   ├── generate-verified-counts.ps1  # Generates VERIFIED_COUNTS.md
│   │   └── hosting-cloudflare-only.js    # Hosting consistency check
│   ├── drift_scan.py               # Detects markdown/JSON/HTML count drift
│   ├── generate_verified_counts.py # Python count artifact generator
│   ├── generate-site-data.js       # Publishes verified-counts.json to site/
│   ├── generate-site-content.js    # Publishes content/* to site/
│   ├── generate-media-manifest.js  # Media manifest generation
│   ├── diagnose-site.js            # Site health checker (1348 LOC)
│   ├── build-wazuh-bundle.ps1      # Bundles Wazuh XML → dist/wazuh/local_rules.xml
│   └── smoke-production.js         # Production smoke tests
├── site/                       # Static portfolio site (Cloudflare Pages publish dir)
│   ├── index.html              # Homepage
│   ├── _redirects              # Cloudflare Pages redirect rules
│   ├── _headers                # Cloudflare security headers
│   ├── 404.html                # Custom 404 page
│   └── assets/
│       ├── design-system.css   # Fluid layout primitives and tokens
│       ├── styles.css          # Global styles and theme
│       ├── app.js              # Client-side UX enhancements
│       ├── home.js             # Homepage-specific logic
│       ├── portfolio-data.js   # Content-driven data rendering
│       ├── data/               # Generated JSON (verified-counts.json, etc.)
│       └── Raylee_Hawkins_Resume.pdf  # Resume — must exist at this exact path
├── content/threat-hunting/             # Threat hunting matrices and hypothesis notes
├── tools/python3/              # Python utilities (wazuh_proof_pack.py, etc.)
├── content/wazuh/                      # Wazuh pack source (rules, decoders, playbooks)
├── AGENTS.md                   # Codex/AI environment constraints (read this too)
├── CONTRIBUTING.md             # Full contribution guidelines
├── README.md                   # Main project overview with verification commands
├── SECURITY.md                 # Security policy and sanitization standard
└── START_HERE.md               # 5-minute proof path for technical reviewers
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Detection rules | Sigma (YAML), Splunk (SPL), Wazuh (XML) |
| IR playbooks | Markdown (structured 7-step format) |
| Site | Static HTML/CSS/JS — no framework |
| Build/verify scripts | PowerShell (`pwsh`), Python 3, Node.js 20.18.1 |
| CI/CD | GitHub Actions |
| Hosting | Cloudflare Pages (publish dir: `site/`) |
| Lab infra | Proxmox VMs, Wazuh Manager, Grafana |
| Version control | Git / GitHub (`raylee-hawkins/HawkinsOperations`) |

**No `package.json`, no `requirements.txt`** — Node scripts and Python scripts are
standalone with no external dependencies.

**Node version:** `.node-version` pins Node.js `20.18.1`.

---

## Source of Truth — Counts

> **CRITICAL:** All public-facing numbers must match `PROOF_PACK/VERIFIED_COUNTS.md`.

Current verified inventory (as of last CI run):

| Platform | Count | Location |
|---|---|---|
| Sigma (YAML) | 103 rules | `content/detection-rules/sigma/` |
| Splunk (SPL) | 9 queries | `content/detection-rules/splunk/` |
| Wazuh (XML) | 24 files / 28 rule blocks | `content/detection-rules/wazuh/rules/` |
| IR Playbooks | 10 playbooks | `content/incident-response/playbooks/` |
| Total detections | 140 | (Sigma + Wazuh + Splunk) |

**Never hardcode counts. Never inflate claims ("200+ detections").**
If counts change, run verification scripts to update `VERIFIED_COUNTS.md` first, then
update any downstream references.

---

## Files You Must Not Break

These files are critical. Do not modify them unless explicitly asked and verified:

- `PROOF_PACK/VERIFIED_COUNTS.md` — source-of-truth count file
- `START_HERE.md` — primary recruiter/reviewer entry point
- `README.md` — main project documentation
- `site/index.html` — homepage (production)
- `scripts/verify/verify-counts.ps1` — CI verification gate
- `site/assets/Raylee_Hawkins_Resume.pdf` — resume PDF (must exist at this path)
- `site/_redirects` — Cloudflare routing rules
- `site/_headers` — Cloudflare security headers
- `site/404.html` — custom 404 page

---

## Verification & Local Testing

### Count verification (PowerShell — primary)
```powershell
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
```

### Generate verified counts markdown
```powershell
pwsh -NoProfile -File ".\scripts\verify\generate-verified-counts.ps1" -OutFile ".\PROOF_PACK\VERIFIED_COUNTS.md"
```

### Count generation (Python — CI Ubuntu runner alternative)
```bash
python scripts/generate_verified_counts.py
```

### Drift scan (detects markdown/JSON/HTML mismatches)
```bash
python scripts/drift_scan.py
python scripts/drift_scan.py --refresh   # regenerate then scan
```

### Serve site locally
```bash
python -m http.server --directory site 8000
```
Then verify these routes manually: `/`, `/security`, `/projects`, `/resume` (PDF download),
`/proof`, `/lab`, `/triage`.

### Build Wazuh bundle
```powershell
pwsh -NoProfile -File ".\scripts\build-wazuh-bundle.ps1"
# Output: dist/wazuh/local_rules.xml
```

### Site data pipeline (Node.js)
```bash
node scripts/generate-site-data.js       # verified-counts.json → site/assets/data/
node scripts/generate-site-content.js    # content/* → site/
node scripts/generate-media-manifest.js  # media manifest
node scripts/diagnose-site.js            # health check
node scripts/diagnose-site.js --fail-on-issues  # CI gate mode
```

### Sanitization check (scan for real IPs)
```powershell
Get-ChildItem -Recurse -Include *.md,*.yml,*.xml |
  Select-String -Pattern "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b" |
  Where-Object { $_.Line -notmatch "10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\." }
```

### Python tools (run on Wazuh manager, not in repo)
```bash
python3 tools/python3/wazuh_proof_pack.py
python3 tools/python3/wazuh_proof_pack.py --severity 12 --lookback-lines 100000

python3 tools/python3/generate_detection_report.py \
  --expected content/projects/lab/wazuh-detection-harness/expected_detections.yaml \
  --out report.md
```

---

## CI/CD Pipeline

### `verify.yml` (Windows runner — primary gate)

Triggered on every push and pull request.

1. Checkout repository
2. Setup Node.js 20.18.1
3. Generate verified counts (PowerShell)
4. Run `verify-counts.ps1`
5. `generate-site-data.js` → `generate-site-content.js` → `generate-media-manifest.js`
6. `hosting-cloudflare-only.js` — hosting consistency check
7. `diagnose-site.js --fail-on-issues` — static site gate
8. Build Wazuh bundle, verify output file exists
9. Upload artifacts: verified counts, Wazuh bundle XML

### `drift-scan.yml` (Ubuntu runner)

Triggered on push to `main` and all pull requests.

1. Checkout repository
2. Setup Python 3.11
3. `generate_verified_counts.py`
4. `drift_scan.py` — fails if markdown/JSON/HTML counts diverge

### `public-safety-gate.yml` (Windows runner)

Triggered on PRs/pushes touching `site/*`, `content/projects/lab/PP_SOC_Integration/*`, or README files.
Runs a PowerShell public safety scan for PII, credentials, and real identifiers.

**Both workflows have `permissions: contents:read` only.** They never commit back.

---

## Development Workflow

```
1. git status + recent git log   (understand current state)
2. Make the smallest change that satisfies the request
3. pwsh -File scripts/verify/verify-counts.ps1   (verify counts if content changed)
4. python scripts/drift_scan.py                   (check drift if site/content changed)
5. node scripts/diagnose-site.js                  (check site health if site/* changed)
6. Commit with descriptive message (see conventions below)
7. Push to feature branch
```

**Environment:** Windows 11 (primary) + Linux Mint dual-boot.
- Prefer `pwsh` for verification and Windows workflows.
- Use fish-compatible syntax on Linux (avoid bashisms like `source`, `[[ ]]`).

---

## Commit Message Conventions

```
<Type>: <description>

[optional body]
```

| Prefix | Use for |
|---|---|
| `Add:` | New detection rule, playbook, or feature |
| `Update:` | Modify existing content |
| `Fix:` | Bug fix or correction |
| `Docs:` | Documentation only |
| `Refactor:` | Reorganization, no behavior change |
| `site:` | Site/UI/UX changes |
| `fix(scope):` | Scoped bug fix (e.g., `fix(home):`) |
| `proof(scope):` | Proof artifact updates (e.g., `proof(wazuh):`) |

Skip CI on docs-only commits:
```bash
git commit -m "Docs: Update README [skip ci]"
```

---

## Code Conventions

### Sigma Rules (`content/detection-rules/sigma/<tactic>/`)

File naming: `lowercase_with_underscores.yml`

```yaml
title: Descriptive Rule Title
id: <uuid>
status: stable
description: What this rule detects
references:
  - https://attack.mitre.org/techniques/T####/
author: HawkinsOps SOC
date: YYYY/MM/DD
modified: YYYY/MM/DD
tags:
  - attack.<tactic>
  - attack.t####
logsource:
  product: windows
  service: sysmon
detection:
  selection:
    # detection logic
  condition: selection
falsepositives:
  - Known legitimate scenario
level: high
```

Rules are organized by MITRE ATT&CK tactic folder:
`collection`, `credential-access`, `defense-evasion`, `discovery`, `execution`,
`exfiltration`, `impact`, `lateral-movement`, `persistence`, `privilege-escalation`

### Wazuh Rules (`content/detection-rules/wazuh/rules/`)

File naming: `wazuh-NNN-descriptive-name.xml` (NNN = sequential number)

```xml
<!--
  Wazuh Rule: Rule Name
  ID: 1000XX
  Level: 10
  Description: What this rule detects
  Author: HawkinsOps SOC
  Date: YYYY-MM-DD
-->
<group name="category,">
  <rule id="1000XX" level="10">
    <description>Alert description</description>
    <mitre>
      <id>T####</id>
    </mitre>
  </rule>
</group>
```

- Custom rule IDs use the 100000+ range
- Bundled for deployment via `scripts/build-wazuh-bundle.ps1` → `dist/wazuh/local_rules.xml`

### Splunk Rules (`content/detection-rules/splunk/`)

```spl
# ========================================
# Rule Name
# MITRE: T####
# ========================================

index=windows EventCode=1
| where condition
| stats count by field1, field2
| where count > threshold
```

### IR Playbooks (`content/incident-response/playbooks/`)

File naming: `IR-NNN-Incident-Type.md`

Required 7-step structure:
1. **DETECTION** — Alert trigger and indicators
2. **TRIAGE (5 min)** — Quick validation and escalation criteria
3. **INVESTIGATION (30 min)** — Deep-dive commands and analysis
4. **CONTAINMENT (15 min)** — Immediate response actions
5. **ERADICATION** — Threat removal steps
6. **RECOVERY** — Service restoration
7. **DOCUMENTATION** — Timeline and lessons learned

Each step must include copy-paste PowerShell or Bash commands, time estimates, and MITRE mapping.

### PowerShell Scripts

- `$ErrorActionPreference = "Stop"` at top of all scripts
- Use `Join-Path` / `Split-Path` for path construction
- Output: `Write-Host` for progress, `Write-Error` for failures
- Parameters: typed with `[CmdletBinding()]`

### Python Scripts

- Module-level docstring at top
- Full type annotations on functions
- Compiled regex patterns for performance
- Explicit `try/except` with `sys.exit(1)` on failure

### JavaScript / Node.js

- CommonJS module style (`require`, `module.exports`)
- `fs` module with explicit `'utf-8'` encoding
- Clear section comment separators

### Date Format

Always use `MM-DD-YYYY` in filenames, logs, and documentation.

---

## Content Verification Pipeline

```
content/detection-rules/*  +  content/incident-response/*
          │
          ▼
  verify-counts.ps1  /  generate_verified_counts.py
          │
          ▼
  PROOF_PACK/VERIFIED_COUNTS.md   ← single source of truth
  PROOF_PACK/verified_counts.json
          │
          ▼
  generate-site-data.js → site/assets/data/verified-counts.json
  generate-site-content.js → site/assets/data/{projects,detections}.json
          │
          ▼
  drift_scan.py   ← validates HTML data-verified attrs match JSON counts
          │
          ▼
  build-wazuh-bundle.ps1 → dist/wazuh/local_rules.xml
```

The `data-verified="key">value<` pattern in HTML tags is validated by `drift_scan.py`.
Never change these values manually — regenerate from the verification pipeline.

---

## Sanitization Requirements

This is a public portfolio. All content must be sanitized before commit.

**Never commit:**
- Real IP addresses (public or internal)
- Real hostnames or domain names from production environments
- Credentials, tokens, API keys, passwords
- Real email addresses (other than the owner's public contact)
- PII (names, phone numbers, locations of real people)
- Real alert/log data that contains identifying information

**Use instead:**
- `192.168.x.x` / `10.0.x.x` for internal IPs
- `attacker.example.com` / `malicious.example.com` for external domains
- `[REDACTED]` for sensitive strings
- Synthetic/generated values for any proof artifacts

See `PROOF_PACK/EVIDENCE_CHECKLIST.md` and `PROOF_PACK/REDACTION_RULES.md` for full rules.

---

## Hosting Guardrails

- **Production host:** Cloudflare Pages only
- **Publish directory:** `site/` (static HTML/CSS/JS, no build step)
- **Branch → production:** `main`
- **Resume PDF path:** `site/assets/Raylee_Hawkins_Resume.pdf` (must exist)
- **Resume link in HTML:** `/assets/Raylee_Hawkins_Resume.pdf` (absolute)
- **Routing:** `site/_redirects` handles pretty URLs (e.g., `/security → /security.html`)
- **Security headers:** `site/_headers`
- **Custom 404:** `site/404.html`

Do not introduce any server-side dependencies, build frameworks, or runtime requirements.
The site must be deployable as a plain static directory.

---

## PR Process

Before opening a PR:

- [ ] Verification scripts pass: `pwsh -File scripts/verify/verify-counts.ps1`
- [ ] Drift scan passes: `python scripts/drift_scan.py`
- [ ] Site diagnosis passes: `node scripts/diagnose-site.js`
- [ ] No sanitization issues (no real IPs, credentials, PII)
- [ ] MITRE ATT&CK tags added for new detection content
- [ ] Commit messages follow conventions above
- [ ] One logical change per PR

Fill out `.github/PULL_REQUEST_TEMPLATE.md` fully when submitting.

---

---

## Standard AI Workflow (no vibes)

1. Run `git status` and review recent `git log` before any changes
2. Read the relevant files before editing them
3. Make the smallest change that satisfies the request
4. Run the appropriate verification script before declaring done
5. Keep diffs small; do not add dependencies unless explicitly requested
6. Never print, log, or commit secrets or tokens
7. Never change a public count without running the verification pipeline first
8. If unsure whether a change is safe, ask before proceeding




