# SignalFoundry Proof Refresh — 2026-04-01

## What changed

- README rebuilt: cleaner front-door structure, single metrics block, stale update diary removed
- Public naming standardized: SignalFoundry leads, internal engine alias demoted from front-door copy
- Verified inventory date-stamped and consolidated into one table
- Reviewer quickstart added for fast validation path
- Repo About blurb drafted for GitHub settings

## Verified counts (script-generated, not self-reported)

| Category | Count |
|---|---:|
| Sigma rules | 103 |
| Wazuh rules | 24 files / 28 blocks |
| Splunk queries | 9 |
| IR Playbooks | 10 |
| Pipeline cases processed | 55,665 |
| Escalated artifacts | 2,545 |
| Auto-close rate | ~92% |
| Host coverage | 8/8 |
| Reconciliation | 0 mismatches |

Source: `PROOF_PACK/VERIFIED_COUNTS.md`

## New proof artifacts

- Race condition case study: TOCTOU fix at 505K queue depth, verified under live I/O contention
- Scorecard upgraded WATCH -> PASS (auto_close_benign_pct 82.88%)
- Ledger resilience hardened: atomic writes, 7-day dated backups, blank-ledger restore

## Reviewer start path

1. [`START_HERE.md`](START_HERE.md) — 5-minute proof path
2. [`PROOF_PACK/VERIFIED_COUNTS.md`](PROOF_PACK/VERIFIED_COUNTS.md) — script-generated counts
3. [`PROOF_PACK/PROOF_INDEX.md`](PROOF_PACK/PROOF_INDEX.md) — curated sample artifacts
4. [`REVIEWER_QUICKSTART.md`](REVIEWER_QUICKSTART.md) — fast validation checklist

## Known limitations

- Pipeline telemetry (321,351 cases, ~88% auto-close) is from the internal engine and not independently reproducible from this public repo alone. Detection rule and playbook counts are fully reproducible via `verify-counts.ps1`.
- Branch protection not yet enabled on `main`. Tracked for manual setup.
- Enterprise hardening evidence pack references Splunk exports that are redacted snapshots, not live queries.
