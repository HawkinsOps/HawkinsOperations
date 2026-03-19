# Design Stack

## Current state assumption

The current public site is a static HTML/CSS/JS site under `site/` with no framework runtime.

That assumption must be verified by audit before any package changes.

## Design goals

- increase clarity
- improve hierarchy
- preserve seriousness
- avoid template look
- keep implementation risk controlled

## Constrained upgrade shortlist

If the audit supports a tooling upgrade, the only approved shortlist is:
- Tailwind CSS
- shadcn/ui
- lucide-react
- clsx
- tailwind-merge
- class-variance-authority

## Rules

- do not add multiple UI kits
- do not install packages before the audit recommends them
- do not rebuild the site architecture just to chase styling convenience
- preserve deployability to Cloudflare Pages

## Low-risk preference

Prefer:
- tokens
- spacing rules
- typography cleanup
- component consistency
- navigation clarity

Before:
- architecture migration
- framework swap
- broad dependency expansion
