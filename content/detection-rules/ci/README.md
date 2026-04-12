# Detection-rules CI

CI lane for Sigma rules under `content/detection-rules/sigma/`.

## What the gate enforces

1. **Schema + syntax** — every rule in `sigma/` passes `sigma check`.
2. **Convertibility** — every rule compiles to Splunk SPL via `sigma convert` with the pipeline in `ci/splunk-pipeline.yml`.
3. **Behavioral tests** — `pytest` runs the suites in `../tests/`, including positive-fixture matching for selected rules.

Workflow: `.github/workflows/sigma-ci.yml`.

## Run locally

```bash
cd content/detection-rules
python -m venv .venv && . .venv/bin/activate
pip install -r ci/requirements.txt

sigma check sigma/
sigma convert -t splunk -p ci/splunk-pipeline.yml -o build/rules.spl sigma/
pytest tests/ -q
```

## Pipeline scope

`ci/splunk-pipeline.yml` maps Sigma logsources to HawkinsOps Splunk conventions:

- `windows/security` → `index=wineventlog sourcetype=WinEventLog:Security`
- `linux/auth` → `sourcetype=linux_secure`
- `EventID` → `EventCode` (Splunk field name)

Extend the pipeline when a new logsource appears in `sigma/`; do not hand-edit generated SPL.
