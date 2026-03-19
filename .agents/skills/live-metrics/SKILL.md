---
name: live-metrics
description: Reconcile public-facing metrics and provenance. Use when tracing metric sources, resolving contradictions, updating metric generators, or adding drift checks.
---

# Live Metrics

## Use when

- reconciling public numbers
- tracing metric provenance
- updating metric generators
- adding drift checks

## Workflow

1. Read `docs/PRECEDENCE_CONTRACT.md` and `docs/metrics-integration.md`.
2. Identify all metric artifacts, generators, and site consumers.
3. Treat `PROOF_PACK/VERIFIED_COUNTS.md` and committed proof artifacts as upstream truth until normalization is complete.
4. Do not publish a number that cannot be traced to a committed source.
5. Prefer generated artifacts over hand-edited snapshots.

## Output expectations

- source map
- contradiction list
- canonical schema proposal
- implementation plan
