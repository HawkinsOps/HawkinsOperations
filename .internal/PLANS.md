# PLANS

## Objective

Upgrade the HawkinsOperations site into a clearer, more credible, and more durable evidence-first portfolio without breaking the current public proof lane.

## Planning principles

- Keep the site cyber-first.
- Keep reviewer trust above aesthetics.
- Treat durable repo guidance as the operating system for future Codex sessions.
- Normalize metrics before broad visual redesign.
- Prefer small, reversible phases over uncontrolled rewrites.

## Required phase order

### Phase 0 - control plane

Goal:
- make repo guidance discoverable to Codex
- define precedence explicitly
- establish durable docs for narrative, metrics, structure, and design constraints

Deliverables:
- `PLANS.md`
- `docs/PRECEDENCE_CONTRACT.md`
- `docs/source-of-truth.md`
- `docs/mission-today.md`
- `docs/content-architecture.md`
- `docs/metrics-integration.md`
- `docs/design-stack.md`
- `.agents/skills/*/SKILL.md`

### Phase 1 - repo audit only

Goal:
- understand the current static site, content flow, metrics flow, and risk boundaries before redesign

Required audit outputs:
- audit summary
- conflicts and risks
- package recommendation
- canonical metrics plan
- phased implementation plan

Prohibitions:
- no visual redesign edits yet
- no new UI dependencies yet
- no renaming blast-radius changes yet

### Phase 2 - metrics normalization

Goal:
- resolve numeric contradictions and create one canonical public metrics contract

Target outputs:
- normalized `data/metrics.json`
- `docs/METRICS_PROVENANCE.md`
- generator or validation path that ties metrics to reproducible artifacts
- drift enforcement for public metrics surfaces

### Phase 3 - homepage and IA rewrite

Goal:
- improve first-minute reviewer comprehension without reducing proof density

Scope:
- homepage framing
- reviewer path
- page roles
- safe naming consolidation
- bounded Splunk placement

### Phase 4 - visual system upgrade

Goal:
- improve hierarchy, consistency, and polish with a constrained stack

Allowed dependency shortlist:
- Tailwind CSS
- shadcn/ui
- lucide-react
- clsx
- tailwind-merge
- class-variance-authority

Rules:
- do not mix multiple UI kits
- do not add packages before Phase 1 and Phase 2 are complete
- preserve static-site deployability unless an explicit architecture change is approved

### Phase 5 - Splunk packaging

Goal:
- place Splunk proof in the right location with wording that matches current evidence

Required outcome:
- public wording must not exceed the currently documented live-ingest evidence level

## Parallel workstreams

- Track A: repo audit
- Track B: metrics normalization
- Track C: homepage and IA rewrite
- Track D: visual system upgrade
- Track E: Splunk packaging

These tracks may run in parallel only when they do not conflict on the same files or truth contracts.
