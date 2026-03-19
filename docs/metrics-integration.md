# Metrics Integration

## Purpose

Define how public numbers should be governed, generated, and consumed.

## Current reality

The repo already has multiple metrics surfaces:
- `PROOF_PACK/VERIFIED_COUNTS.md`
- `PROOF_PACK/verified_counts.json`
- `site/assets/verified-counts.json`
- `site/data/ops-metrics.js`
- `site/data/counts.js`
- `data/metrics.json`
- `proof/autosoc/latest/*.json`

This is useful coverage, but it also creates drift risk.

## Current numeric authority

Until normalization is complete:
- detection inventory truth comes from `PROOF_PACK/VERIFIED_COUNTS.md`
- live operational-state truth comes from `proof/autosoc/latest/*.json`
- any aggregated public metrics must reconcile to those sources

## Target state

Create one canonical public metrics artifact:
- `data/metrics.json`

Then document the full derivation chain in:
- `docs/METRICS_PROVENANCE.md`

## Required properties of the canonical artifact

- every field has a definition
- every field has a provenance source
- generated timestamp is included
- intended public-use status is explicit
- static snapshot vs live-derived values are distinguished

## Integration rules

- Do not hardcode numbers directly into HTML when a generated artifact should provide them.
- Keep site-consumed data derivative, not editorial.
- Add drift checks between canonical metrics and rendered site surfaces.

## Audit questions

The audit must answer:
- which scripts currently generate metrics
- which pages read which metric files
- which files are stale or contradictory
- whether `data/metrics.json` is generated, hand-edited, or abandoned
- what minimum contract is needed before the site can trust it
