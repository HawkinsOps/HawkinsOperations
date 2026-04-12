# Verification Scripts

- `verify-counts.ps1` prints current detection/playbook counts.
- `generate-verified-counts.ps1` updates `PROOF_PACK/VERIFIED_COUNTS.md` from live repository counts.
- `hosting-cloudflare-only.js` enforces Cloudflare-only hosting consistency.
  - Notes: allows archived `PROOF_PACK/hosting_transfer_cloudflare/run_*/` evidence logs while blocking new legacy hosting references in active repo files.
- `public-safety-scan.ps1` blocks merge/publish of public-surface token/path/IP leakage patterns.
- `autosoc-publish-contract-scan.ps1` blocks commits that stage runtime AutoSOC output, incident firehose paths, too many files, or oversized files.
- `repo-state-grade.ps1` prints a simple 0-100 repo hygiene score from current working tree state (modified/untracked/deleted counts).
- `install-precommit-public-safety.ps1` installs an optional local pre-commit hook that runs both `public-safety-scan.ps1` and `autosoc-publish-contract-scan.ps1`.
- `validate_detection_content.py` enforces structural correctness of Sigma and Wazuh rule content (complements `verify-counts.ps1`, which only counts files). Wired into `.github/workflows/verify.yml` and required for merge.
  - Sigma: parses each `.yml`/`.yaml` with PyYAML; requires `title`, `id`, `logsource`, `detection.condition`; validates `id` is UUID-shaped; checks `logsource` has at least one of `product`/`service`/`category`; checks `level` is a valid Sigma severity; enforces cross-tree UUID uniqueness.
  - Wazuh: **strict**. Parses each `.xml` with stdlib `xml.etree.ElementTree`; requires `<group>` root, at least one `<rule id="...">`, integer IDs inside `[100000, 199999]`, non-empty `<description>`, and cross-tree rule-ID uniqueness. No allowlist — all Wazuh rules must pass.
  - Sigma duplicate-ID quarantine: `validation_exceptions.yml` lists 33 placeholder-UUID collisions (69 files) discovered on first validator run. Listed collisions are downgraded to warnings **only** when the live collision set matches the allowlist exactly; any drift (new file reusing a listed ID, or a listed file renamed) fails hard. Remediation is tracked in `Z:\AgentOps\plans\sigma_id_remediation_2026-04.md`. New Sigma rules must use fresh UUIDv4s (`python -c "import uuid; print(uuid.uuid4())"`) and cannot be added to the allowlist.
- `validation_exceptions.yml` is the quarantine file for `validate_detection_content.py`. Do not add new entries to unblock new bugs — it exists only to carry pre-existing Sigma placeholder-ID collisions while remediation proceeds.

Count rules:

- Sigma includes both `*.yml` and `*.yaml` under `content/detection-rules/sigma/`.
- IR playbooks include only `IR-*.md` under `content/incident-response/playbooks/`.

Run from repository root:

```powershell
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
pwsh -NoProfile -File ".\scripts\verify\generate-verified-counts.ps1" -OutFile ".\PROOF_PACK\VERIFIED_COUNTS.md"
node .\scripts\verify\hosting-cloudflare-only.js
pwsh -NoProfile -File ".\scripts\verify\public-safety-scan.ps1"
pwsh -NoProfile -File ".\scripts\verify\autosoc-publish-contract-scan.ps1"
pwsh -NoProfile -File ".\scripts\verify\repo-state-grade.ps1" -WarnBelow 80
pwsh -NoProfile -File ".\scripts\verify\install-precommit-public-safety.ps1"
node .\scripts\generate-media-manifest.js
python3 -m pip install --quiet pyyaml==6.0.2
python3 .\scripts\verify\validate_detection_content.py
```

