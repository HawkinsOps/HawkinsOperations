# RENAMELOG

## Phase 1 Staging Artifacts

This branch prepares the Phase 1 staging contract for the SignalFoundry rebrand without changing the production deployment.

### Planned rename direction

- Umbrella brand remains `HawkinsOps`
- Flagship system name is `SignalFoundry`
- Internal engine references remain `AutoSOC` where technical precision matters

### Files changed in this phase

- `data/metrics.json`
- `data/metrics.json.sha256`
- `scripts/sign_metrics.sh`
- `scripts/validate_metrics.py`
- `scripts/check-md-links.sh`
- `AGENTS.md`
- `agents_activity.log`

### Human gate

Do not proceed to Phase 2 until Raylee reviews the Phase 1 PR and approves the contract, checks, and naming direction.
