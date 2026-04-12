# HawkinsOps — Codex Agent Rules

**Scope:** any Codex session in this repo or its subfolders.
**Most specific** — overrides all parent `AGENTS.md` files.

---

## First: read `CLAUDE.md`

`CLAUDE.md` is the canonical AI-assistant guide for this repo. It covers
repository identity, directory map, data flow, tech stack, verification,
CI/CD, commit conventions, sanitization, hosting guardrails, the protected
files list, and the standard AI workflow.

**Everything in `CLAUDE.md` applies to Codex sessions.** This file only adds
the Codex-specific rules that aren't in `CLAUDE.md`.

---

## Codex discovery contract

- Repo-local Codex skills must live in `.agents/skills/`.
- For planning, audits, and redesign work, read these files in order before
  proposing changes:
  1. `AGENTS.md` (this file)
  2. `CLAUDE.md`
  3. `.internal/PLANS.md` (if present locally — gitignored)
  4. `docs/PRECEDENCE_CONTRACT.md`
  5. `docs/source-of-truth.md`
  6. `docs/mission-today.md`
  7. `docs/content-architecture.md`
  8. `docs/metrics-integration.md`
  9. `docs/design-stack.md`
- Treat repo docs as authority, not session memory.
- Numeric claims are not trustworthy unless they resolve to the active
  public-metrics authority defined in `docs/PRECEDENCE_CONTRACT.md`.

---

## Phase 1 preflight checks (Codex-specific)

Before opening or updating a rebrand staging PR, run **all** of the following
in addition to the standard verification in `CLAUDE.md`:

1. `python -m unittest`
2. `python3 scripts/validate_metrics.py`
3. `scripts/check-md-links.sh`

If any preflight fails, stop and document the failure in a GitHub issue
before asking for Phase 2 approval.

---

## Approval and push rules

- **Required approver** for rebrand and public proof changes: `raylee`
- **Never push without confirmation from Raylee**, even if local verification
  and pre-commit hooks pass.
- The standard verification steps in `CLAUDE.md` (PR Process section) must
  pass before any commit lands.
