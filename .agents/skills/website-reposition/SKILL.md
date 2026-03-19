---
name: website-reposition
description: Reposition site messaging and page roles without overclaiming proof. Use when auditing homepage narrative, reviewer paths, and information architecture.
---

# Website Reposition

## Use when

- auditing homepage messaging
- rewriting reviewer paths
- clarifying flagship system positioning
- improving information architecture without reducing proof density

## Workflow

1. Read the repo control docs in the order defined by `AGENTS.md`.
2. Confirm the flagship identity and naming boundaries from `docs/source-of-truth.md` and `docs/PRECEDENCE_CONTRACT.md`.
3. Audit current page roles before rewriting copy.
4. Prefer route clarity, narrative compression, and reviewer trust over brand flourish.
5. Do not overclaim beyond committed proof.

## Execution guidance for web-design passes

- pair copy rewrites with design-system primitives (cards, metric tiles, section headers, tabs, dialogs) so new messaging lands in consistent components
- when the stack supports it, migrate proof-heavy narratives to MDX-backed pages for easier structured updates
- keep reviewer-path navigation explicit and low-friction with smooth section transitions and direct role-based routes
- use motion and charting (`framer-motion`, `recharts`) only when they improve comprehension of proof timelines or metric deltas
- use `fuse.js` for searchable inventories when page density or detection counts make manual scanning slow

## Output expectations

- audit summary
- page-role recommendation
- copy risks
- phased rewrite plan
