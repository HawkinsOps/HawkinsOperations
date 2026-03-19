# START_HERE

Use this file for a fast technical validation path.

## 5-Minute Proof Path

1. Open [PROOF_PACK/PROOF_INDEX.md](PROOF_PACK/PROOF_INDEX.md) to see the evidence layout.
2. Open [PROOF_PACK/VERIFIED_COUNTS.md](PROOF_PACK/VERIFIED_COUNTS.md) for current rule/playbook counts.
3. Open [content/detection-rules/INDEX.md](content/detection-rules/INDEX.md) to inspect detection coverage and platform layout.
4. Open [content/incident-response/INDEX.md](content/incident-response/INDEX.md) to review the IR catalog.
5. Open [docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md](docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md) for the live AutoSOC pipeline — architecture, scheduler config, and operational proof.

## Reproduce Locally

Run from repository root:

```powershell
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
pwsh -NoProfile -File ".\scripts\verify\generate-verified-counts.ps1" -OutFile ".\PROOF_PACK\VERIFIED_COUNTS.md"
node .\scripts\generate-metrics.js
python .\scripts\drift_scan.py --refresh
pwsh -NoProfile -File ".\scripts\build-wazuh-bundle.ps1"
```

Expected:

- `PROOF_PACK/VERIFIED_COUNTS.md` updates with current counts.
- `site/assets/verified-counts.json` updates from verified counts (and `PROOF_PACK/verified_counts.json` updates when `--with-proof-pack` is used for release/proof packaging).
- `dist/wazuh/local_rules.xml` is generated.

## Reviewer Notes

- This repository is evidence-first: claims are backed by reproducible commands.
- `PROOF_PACK/` is the curated review lane; raw imports and legacy material are not part of the front-door proof path.
- Sanitization and redaction standards: `PROOF_PACK/REDACTION_RULES.md`, `PROOF_PACK/EVIDENCE_CHECKLIST.md`
- Lab infrastructure context: `content/projects/lab/README.md`


