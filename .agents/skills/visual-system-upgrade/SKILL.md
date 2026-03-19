---
name: visual-system-upgrade
description: Plan constrained UI modernization for the static site. Use when auditing styling consistency, selecting a design-system path, or phasing visual upgrades.
---

# Visual System Upgrade

## Use when

- auditing styling consistency
- recommending a safe design-system path
- planning a constrained UI modernization

## Workflow

1. Read `docs/design-stack.md` and `docs/content-architecture.md`.
2. Audit the current implementation before recommending dependencies.
3. Prefer typography, spacing, tokens, and component consistency before framework-level migration.
4. Do not introduce multiple UI kits.
5. Preserve static-site deployability unless an explicit architecture change is approved.

## High-value implementation tasks

- add a small design system first: cards, metric tiles, section headers, tabs, and dialog primitives
- convert case-study and proof surfaces to MDX-backed content where a framework pipeline exists
- add animated benchmark cards with `recharts` and `framer-motion` only on pages that benefit from visual trend context
- add detection inventory filtering and search with `fuse.js`
- add reviewer-path navigation with smooth section/page transitions

## Tailwind initialization note

- if `npx tailwindcss init -p` fails with "could not determine executable to run", call the local binary directly:
  - `.\node_modules\.bin\tailwindcss init -p`
- if no local binary exists, install the Tailwind CLI package first, then retry:
  - `npm i -D tailwindcss @tailwindcss/cli`
  - `npx tailwindcss init -p`

## Output expectations

- styling audit
- risk classification
- package recommendation
- phased upgrade plan
