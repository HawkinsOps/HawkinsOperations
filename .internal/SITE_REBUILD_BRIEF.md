# SITE_REBUILD_BRIEF

## 1. Project identity

- Operator: Raylee Hawkins
- Site: HawkinsOperations portfolio site
- Canonical local repo root: `C:\GitHub\HawkinsOperations`

## 2. Site objective

- Communicate operator + flagship system + proof + hiring relevance.
- Reduce noise and increase signal.
- Make the operations-to-security bridge legible quickly.
- Preserve trust by enforcing one canonical public metrics source.

## 3. Canonical public metrics source

- Source file: `site/assets/data/ops-metrics.json`
- Stable public surfaces must use only `stable_*` keys.
- No silent fallback for stable pages.
- Runtime/lifetime lanes must be explicitly labeled and visually separated.

## 4. Canonical public benchmark language

Use only values supported by the current stable data model:

- Stable total cases: bind to `stable_total_cases`
- Stable escalated: bind to `stable_escalated`
- Stable coverage ratio: bind to `stable_coverage_ratio`
- Stable heartbeat: bind to `stable_heartbeat`
- Stable locked date: bind to `stable_locked_date`
- Stable statement: bind to `stable_statement`

Constraint:

- Do not invent unavailable stable reconciliation fields.

## 5. Nav target

`Home | SignalFoundry | Proof | Resume | Lab`

Nav decisions:

- `Ops -> Cyber` is not a primary nav item.
- The strongest operations-to-security bridge content should be integrated into `Home` and `Resume`.
- Displayed nav text should use `SignalFoundry` (not `SignalFoundry Case Study`); route/slug changes can be finalized later.

## 6. Page contracts

- Home
  - Mission: establish role fit, show flagship system, present stable proof strip, and route reviewers quickly.
  - Data: stable benchmark on candidate-facing proof surfaces; runtime data only when explicitly labeled.
  - Tone: concise, evidence-first, recruiter-readable.
- SignalFoundry
  - Mission: explain the flagship system architecture, workflow, outputs, and why it matters operationally.
  - Data: stable proof indicators in stable surfaces; deeper implementation context allowed.
  - Tone: technical clarity without excess narrative.
- Proof
  - Mission: provide verification path, artifacts, and benchmark language with clear stable vs runtime separation.
  - Data: stable lane uses only `stable_*`; runtime/lifetime lane explicitly labeled.
  - Tone: auditable and concrete.
- Resume
  - Mission: convert system and proof into hiring relevance with direct role alignment.
  - Data: no conflicting metric claims; align to canonical public metrics language.
  - Tone: concise, outcomes-oriented.
- Lab
  - Mission: show operating environment and practical implementation context.
  - Data: may reference supporting artifacts; do not conflict with canonical benchmark claims.
  - Tone: practical and reproducible.

## 7. Homepage contract

Homepage has 5 jobs:

1. Role fit
2. Flagship summary
3. Stable proof strip
4. Operator bridge teaser
5. Reviewer routing

## 8. Visual direction

- Keep existing dark/teal/blue theme.
- Use controlled motion only where it improves scanability.
- Use amber only for operations-bridge content.
- Use uploaded SVG assets intentionally and avoid decorative overload.

## 9. Known issues / watchouts

- Start Here disposition: decide whether to keep as a dedicated page, merge into homepage routing, or deprecate.
- Detections disposition: clarify whether it remains a primary nav destination or secondary proof artifact.
- Historical artifact handling: preserve historical docs/artifacts as historical context and label clearly.
- Metric consistency rules: stable surfaces must not mix stable and runtime keys.
- No mixed stable/runtime language in a single benchmark card.

## 10. Phase plan

1. Homepage structure
2. Homepage copy
3. Homepage nav cleanup
4. Homepage proof strip
5. Bridge teaser
6. Visual polish
7. QA
