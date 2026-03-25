# Mission Today

## Current mission

Run a repo audit before any redesign or dependency changes.

This mission is for understanding and planning only.

## Read order

Read these files in order:
1. `AGENTS.md`
2. `PLANS.md`
3. `docs/PRECEDENCE_CONTRACT.md`
4. `docs/source-of-truth.md`
5. `docs/mission-today.md`
6. `docs/content-architecture.md`
7. `docs/metrics-integration.md`
8. `docs/design-stack.md`

## Required audit scope

Audit:
- framework
- Node version
- package manager
- build and deploy flow
- routing and layout structure
- current component structure
- current styling system
- whether Tailwind already exists
- where metrics are sourced
- which files are low-risk vs high-risk
- where Splunk content should live

## Required output format

Return only:
- audit summary
- conflicts and risks
- package recommendation
- canonical metrics plan
- phased implementation plan

## Explicit prohibitions

- no visual redesign edits
- no package installs
- no broad naming refactor
- no metrics rewrites before the audit resolves current contradictions
