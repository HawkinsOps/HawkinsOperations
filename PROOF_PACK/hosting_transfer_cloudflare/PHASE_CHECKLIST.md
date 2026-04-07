# Phase Checklist (0-2B + Hosting Transfer)
AS_OF: 2026-02-14

## Status key
- `[x]` complete and evidenced
- `[~]` partial (exists, but missing execution evidence)
- `[ ]` not completed

## 1) Phase-order gate from AGENTS.md
- `[~]` Step 1 complete current phase work (Phase 0 through Phase 2B) with verified-lane checks.
- `[~]` Step 2 execute hosting transfer and complete Hosting Transfer Proof Pack.
- `[ ]` Step 3 continue polish phases only after hosting transfer evidence is complete and reviewed.

## 2) Pre-check workflow controls
- `[x]` Repo state checked first (`git status`).
  - Evidence: local run output on branch `ops/hosting-transfer-implementation`.
- `[~]` Working tree clean before phase-close decision.
  - Blocker: local uncommitted changes present under `PROOF_PACK/hosting_transfer_cloudflare/run_02-13-2026_191244/`.

## 3) Verified-lane checks (Phase 0-2B)
- `[x]` Counts verification executed with:
  - `pwsh -NoProfile -File scripts/verify/verify-counts.ps1`
  - Latest observed output:
    - Sigma: `103`
    - Splunk: `79`
    - Wazuh XML files: `24`
    - Wazuh `<rule id=>` blocks: `28`
    - IR playbooks: `10`
- `[x]` Source-of-truth counts file present.
  - Evidence: `PROOF_PACK/VERIFIED_COUNTS.md`
- `[x]` Manual local click-test completed for minimum routes:
  - `/`, `/security`, `/projects`, `/resume`, `/proof`, `/lab`, `/triage`
  - Evidence: `PROOF_PACK/hosting_transfer_cloudflare/run_02-14-2026_031137/evidence/logs/route_clicktest_status_02-14-2026.txt`

## 4) Hosting guardrails (static checks)
- `[x]` Cloudflare Pages publish directory is `site`.
  - Evidence: `docs/hosting/CLOUDFLARE_PAGES.md`
- `[x]` Pretty redirect file exists.
  - Evidence: `site/_redirects`
- `[x]` Security headers file exists.
  - Evidence: `site/_headers`
- `[x]` Custom 404 exists.
  - Evidence: `site/404.html`
- `[x]` Resume PDF exists at required path.
  - Evidence: `site/assets/Raylee_Hawkins_Resume.pdf`
- `[x]` Resume absolute link uses required URL.
  - Evidence: `site/resume.html`
  - Expected: `/assets/Raylee_Hawkins_Resume.pdf`

## 5) Hosting Transfer Proof Pack artifacts
- `[x]` Artifact root exists.
  - Evidence: `PROOF_PACK/hosting_transfer_cloudflare/`
- `[x]` Required artifact file exists: `CF_PAGES_PROJECT_SETTINGS.md`
- `[x]` Required artifact file exists: `DNS_CUTOVER_RECORDS.md`
- `[x]` Required artifact file exists: `ROUTING_AND_HEADERS_VALIDATION.md`
- `[x]` Required artifact file exists: `ROLLBACK_PLAN_AND_TRIGGER.md`
- `[x]` Required artifact file exists: `DEPLOY_LOG_LINKS.md`

## 6) Hosting transfer execution evidence completeness
- `[x]` Route validation checklist content exists with full production evidence.
  - Evidence: `PROOF_PACK/hosting_transfer_cloudflare/ROUTING_AND_HEADERS_VALIDATION.md`
- `[x]` DNS cutover output captured from two resolvers.
  - Expected resolvers: `[REDACTED_IP]`, `[REDACTED_IP]`
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/DNS_CUTOVER_RECORDS.md`
- `[x]` Deploy log rows fully filled with timestamp/SHA/URL/status.
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/DEPLOY_LOG_LINKS.md`
- `[x]` Deterministic deploy test complete for at least 3 consecutive commits.
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/DEPLOY_LOG_LINKS.md`
  - Supporting evidence target: `PROOF_PACK/hosting_transfer_cloudflare/run_02-14-2026_031137/evidence/logs/deterministic_deploy_capture_02-14-2026.txt`
- `[x]` Resume PDF download validated on production route.
  - Expected path: `/assets/Raylee_Hawkins_Resume.pdf`
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/run_02-14-2026_031137/RESULTS.md`
- `[x]` `_headers` and `_redirects` parity verified post-cutover.
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/ROUTING_AND_HEADERS_VALIDATION.md`
- `[x]` Hard refresh stale-cache checks completed on desktop and mobile.
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/run_02-14-2026_031137/evidence/logs/hard_refresh_desktop_mobile_02-14-2026.txt`
- `[x]` Rollback drill evidence captured (DNS-record rollback to previous provider/targets).
  - Evidence target: `PROOF_PACK/hosting_transfer_cloudflare/ROLLBACK_PLAN_AND_TRIGGER.md`
  - Supporting evidence target: `PROOF_PACK/hosting_transfer_cloudflare/run_02-14-2026_031137/evidence/logs/rollback_drill_simulation_02-14-2026.txt`

## 7) Phase gate decision
- `[x]` Gate open for post-hosting polish phases.
  - Criteria: all items in sections 3 and 6 must be `[x]`.

