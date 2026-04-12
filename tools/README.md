# `tools/` — Operator Utilities

Standalone Python utilities and one-off generators that operators run **by hand**, typically on the Wazuh manager or a workstation. Distinct from `scripts/`, which holds the CI/build/verification pipeline that runs in GitHub Actions.

| Folder | Folder runs in | Purpose |
|---|---|---|
| `tools/` (this folder) | Operator shell, Wazuh manager | Hand-run utilities, parsers, one-off generators |
| `scripts/` | CI / build pipeline | Verification gates, site generation, AutoSOC pipeline, deployment |

## Contents

- **`python3/`** — Python 3 utilities for Wazuh proof packs, Sigma title normalization, detection-report generation, and Windows Security 4688 XML parsing. Each utility is documented with usage examples in [`python3/README.md`](python3/README.md).
- **`og-generator.html`** — Static HTML page used to generate Open Graph preview images for the portfolio site. Open in a browser, capture, save under `site/assets/og/`.
- **`__init__.py`** — Empty marker so `tools.python3.tests.*` can be invoked via `python -m unittest`.

## Where to look for related code

- Detection / portfolio verification automation: [`scripts/verify/`](../scripts/verify/)
- Site generation and proof aggregation: [`scripts/`](../scripts/) root
- AutoSOC pipeline: [`scripts/auto-soc/`](../scripts/auto-soc/)
- Detection rule mappings (content, not tooling): [`content/detection-rules/mappings/`](../content/detection-rules/mappings/)
