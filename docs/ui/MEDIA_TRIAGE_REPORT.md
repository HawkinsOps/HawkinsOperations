# MEDIA TRIAGE REPORT

Generated: `2026-03-30`

- Total discovered assets: **123**
- Safe to publish: **11**
- Needs privacy review: **112**

## Top 10 safe to publish

| id | source | type | tags | size | suggested placement |
|---|---|---|---|---:|---|
| `site-assets-og-84f412f582` | `site/assets/og.png` | screenshot | proof | 63868 | home proof strip |
| `site-assets-icon-192-2dd33d303d` | `site/assets/icon-192.png` | screenshot | proof | 1466 | home proof strip |
| `assets-badges-automation-36aa2147ed` | `site/assets/badges/automation.svg` | logo | proof | 413 | global identity strip |
| `assets-logos-automation-85a1e87692` | `site/assets/logos/automation.svg` | logo | proof | 413 | global identity strip |
| `site-assets-favicon-2641013eae` | `site/assets/favicon.svg` | logo | proof | 289 | global identity strip |
| `assets-badges-wazuh-a9baecedc0` | `site/assets/badges/wazuh.svg` | logo | wazuh, proof | 273 | global identity strip |
| `assets-logos-wazuh-11e7cf3bd9` | `site/assets/logos/wazuh.svg` | logo | wazuh, proof | 273 | global identity strip |
| `assets-badges-splunk-3040c8f48f` | `site/assets/badges/splunk.svg` | logo | splunk, proof | 266 | global identity strip |
| `assets-logos-splunk-1df11b14bf` | `site/assets/logos/splunk.svg` | logo | splunk, proof | 266 | global identity strip |
| `assets-badges-sigma-a00fcaf8d4` | `site/assets/badges/sigma.svg` | logo | sigma, proof | 243 | global identity strip |

## Top 10 needs review

| id | source | reason | tags | size | suggested placement |
|---|---|---|---|---:|---|
| `playwright-cli-page-2026-03-09t20-35-15-236z-ab296a258c` | `.playwright-cli/page-2026-03-09T20-35-15-236Z.png` | privacy_review=required | proof | 802252 | home proof strip |
| `playwright-cli-page-2026-03-09t20-35-55-085z-dfc4b95fa6` | `.playwright-cli/page-2026-03-09T20-35-55-085Z.png` | privacy_review=required | proof | 802252 | home proof strip |
| `playwright-cli-page-2026-03-09t20-34-34-920z-a5c4462038` | `.playwright-cli/page-2026-03-09T20-34-34-920Z.png` | privacy_review=required | proof | 794253 | home proof strip |
| `playwright-cli-page-2026-03-09t20-34-35-296z-7ab84f8792` | `.playwright-cli/page-2026-03-09T20-34-35-296Z.png` | privacy_review=required | proof | 654638 | home proof strip |
| `linkedin-carousel-review-04-architecture-autosoc-desktop-2ee931a6c6` | `.internal/linkedin_carousel_review/04_architecture/autosoc-desktop.png` | privacy_review=required | proof | 570813 | home proof strip |
| `output-playwright-autosoc-desktop-1a38710d1f` | `output/playwright/autosoc-desktop.png` | privacy_review=required | proof | 570813 | home proof strip |
| `2026-01-25-howe01-rule100052-hosts-ics-modified-benign-evidence-06-event-dc85286f46` | `content/incident-response/incidents/2026/2026-01-25__howe01__rule100052__hosts-ics-modified__benign/evidence/06_event_detail_json_full.png` | privacy_review=required | incident, proof | 503893 | home proof strip |
| `evidence-public-images-02-vuln-0critical-31high-redacted-1d70eee371` | `content/projects/lab/PP_SOC_Integration/evidence/public_images/02_vuln_0critical_31high_redacted.png` | privacy_review=required | lab, proof | 486909 | projects page gallery |
| `assets-pp-soc-integration-02-vuln-0critical-31high-redacted-129823dfc5` | `site/assets/pp_soc_integration/02_vuln_0critical_31high_redacted.png` | privacy_review=required | proof | 486909 | home proof strip |
| `evidence-public-images-04-nodejs-patch-terminal-0a8725700a` | `content/projects/lab/PP_SOC_Integration/evidence/public_images/04_nodejs_patch_terminal.png` | privacy_review=required | lab, proof | 448259 | projects page gallery |

## Placement suggestions

- Home: use 3-6 safe assets tagged `proof` / `security`.
- Projects: prefer `lab`, `triage`, `diagram` safe assets.
- Security: prefer `dashboard`, `detection`, `table` safe assets.

## Performance notes

- Prefer `svg` and `webp` where possible.
- Keep gallery image weights small and use `loading="lazy"`.
- Review oversized assets before publishing.
