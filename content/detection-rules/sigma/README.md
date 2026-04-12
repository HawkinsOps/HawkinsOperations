# Sigma Rules

Sigma detections (YAML) organized by MITRE ATT&CK tactic:
`credential-access/`, `execution/`, `persistence/`, `privilege-escalation/`,
`defense-evasion/`, `discovery/`, `lateral-movement/`, `collection/`,
`exfiltration/`, `impact/`.

## CI gate

Every change under this folder is validated by `.github/workflows/sigma-ci.yml`:

1. `sigma check` — schema + syntax lint
2. `sigma convert` — compiles all rules to Splunk SPL via `../ci/splunk-pipeline.yml`
3. `pytest` — parse, convert, and positive-fixture tests in `../tests/`

See `../ci/README.md` for local-run instructions.

Rule count and verification are also computed by `docs/VERIFY_COMMANDS_POWERSHELL.md`.
