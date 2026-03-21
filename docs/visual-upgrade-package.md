# Visual Upgrade Package

## 1. Executive Summary

Recommended mode: **MODERNIZE**.

MODERNIZE provides the best balance for HawkinsOperations. It preserves the current proof-first tone and static `site/` deployment model while materially improving accessibility, visual consistency, recruiter scanability, and performance posture. FACELIFT is the fastest route to visible polish and lowest rollout risk, but it leaves structural design debt in place. TRANSFORM offers the strongest visual differentiation and a richer component system, but it carries higher delivery risk, more motion/design complexity, and a longer rollout path that does not match the repo's current static publishing method. For hiring-manager outcomes within a realistic timeline, MODERNIZE is the winning middle path.

## 2. Modes

Each mode below includes Design System, Key Visuals, Component Library, Example Pages, Accessibility and Performance, Assets, Migration and Rollout, Acceptance Criteria, and Estimate.

### FACELIFT

Approach: static-first refresh inside `site/` with typography, spacing, color cleanup, and tighter content hierarchy. No required component system. Good fit for a one-day to two-day polish pass.

#### Design System

| Token | Value | Notes |
|---|---|---|
| Accent CTA | `#F97316` | Use with dark text on light surfaces |
| Text strong | `#111827` | Primary light-mode text |
| Surface | `#FAFAFA` / `#FFFFFF` | Neutral-first UI |
| Fonts | `Inter`, system sans, monospace fallback | Larger base copy |
| Spacing | `4, 8, 12, 16, 24, 32` | Low-risk refresh |

Contrast summary:

| Color | Contrast vs white | 4.5:1 | 3:1 | Contrast vs `#111111` | 4.5:1 | 3:1 | Guidance |
|---|---:|---|---|---:|---|---|---|
| `#F97316` | 2.80 | Fail | Fail | 6.65 | Pass | Pass | Accent background with dark text |
| `#C2410C` | 5.00 | Pass | Pass | 3.72 | Fail | Pass | White text safe |
| `#71717A` | 4.79 | Pass | Pass | 3.89 | Fail | Pass | Secondary text |
| `#111827` | 17.74 | Pass | Pass | 1.00 | Fail | Fail | Primary text only |

Typography:

| Scale | Size | Line-height |
|---|---:|---:|
| `xs` | `0.75rem` | `1.4` |
| `sm` | `0.875rem` | `1.5` |
| `base` | `1.0625rem` | `1.6` |
| `lg` | `1.125rem` | `1.6` |
| `xl` | `1.25rem` | `1.4` |
| `2xl` | `1.5rem` | `1.3` |
| `3xl` | `1.875rem` | `1.2` |
| `4xl` | `2.25rem` | `1.1` |
| `5xl` | `2.75rem` | `1.05` |

Layout specs:

| Breakpoint | Width | Grid | Max width |
|---|---:|---|---:|
| Mobile | `<= 640px` | 1 col | fluid with `16px` side gutters |
| Tablet | `641-1024px` | 6 col | `880px` |
| Desktop | `>= 1025px` | 12 col | `1180px` |

- LCP element: hero text block or lightweight hero image
- FID/INP focus: primary CTAs, nav toggle, featured cards
- Iconography direction: thin outline operational icons

#### Key Visuals

Homepage:

```text
+------------------------------------------------------------+
| nav                                                         |
+------------------------------------------------------------+
| hero title + 2 CTAs + lightweight visual                    |
+------------------------------------------------------------+
| 3 cards: Case Study | Proof | Resume                        |
+------------------------------------------------------------+
| counts strip                                                |
+------------------------------------------------------------+
| footer                                                      |
+------------------------------------------------------------+
```

Project page:

```text
+------------------------------------------------------------+
| title + summary + architecture snapshot                     |
+------------------------------------------------------------+
| overview block                                              |
| decision logic                                              |
| proof links                                                 |
+------------------------------------------------------------+
```

Demo page:

```text
+------------------------------------------------------------+
| demo intro                                                  |
+------------------------------------------------------------+
| command block + screenshots                                 |
+------------------------------------------------------------+
| CTA                                                         |
+------------------------------------------------------------+
```

Mockup files:

- `docs/design/mockups/facelift-home-desktop.svg`
- `docs/design/mockups/facelift-home-tablet.svg`
- `docs/design/mockups/facelift-home-mobile.svg`
- `docs/design/mockups/facelift-project-desktop.svg`
- `docs/design/mockups/facelift-project-tablet.svg`
- `docs/design/mockups/facelift-project-mobile.svg`
- `docs/design/mockups/facelift-demo-desktop.svg`
- `docs/design/mockups/facelift-demo-tablet.svg`
- `docs/design/mockups/facelift-demo-mobile.svg`

#### Component Library

- Minimal reference set: `Hero`, `Card`, `Nav`, `Footer`
- Reuse MODERNIZE reference components with lighter styles
- No production component migration required

#### Example Pages

- Keep static routes `/`, `/case-study-autosoc`, and `/proof`
- Use the reference TSX examples only as implementation guides

#### Accessibility and Performance Checklist

- Performance target: `70-85`
- Accessibility target: `>= 85`
- Add semantic headings and visible focus states
- Ensure body copy and CTA labels meet `4.5:1`
- Compress screenshots to WebP and lazy-load below the fold
- Avoid heavy motion and layout-shift-prone effects

#### Assets Plan

- Hero assets: `1600w`, `960w`, `640w`
- Formats: `AVIF`, `WebP`, fallback `PNG/JPG`
- Keep diagrams as inline SVG where possible

#### Migration and Rollout

1. Add a small token-style CSS layer to static CSS.
2. Update hero, cards, and nav spacing in `site/assets/styles.css`.
3. Test via `site/index.canary.html`.
4. Promote after manual review.

#### Acceptance Criteria

- Pages load in under 2 seconds under simulated slower conditions
- LCP `<= 2.5s`
- Contrast passes `4.5:1` for body copy
- No hosting or content pipeline changes required

#### Estimate

- `6-12 hours`

#### One-Week Sprint Plan

| Priority | Task | Estimate |
|---|---|---:|
| 1 | Static CSS cleanup | 2h |
| 2 | Hero visual replacement | 3h |
| 3 | Card and counts refresh | 2h |
| 4 | Accessibility pass | 2h |
| 5 | Lighthouse canary check | 1h |

### MODERNIZE

Approach: static-first but structured for component extraction. Keep `site/` as the canonical deploy path and deliver tokens, CSS variables, deterministic mockups, and React/Tailwind references that implement the same design. This is the recommended path.

#### Design System

Primary teal scale:

| Scale | Hex | Contrast vs white | 4.5:1 | 3:1 | Contrast vs `#111111` | 4.5:1 | 3:1 | Guidance |
|---|---:|---:|---|---|---:|---|---|---|
| 50 | `#F0FDF9` | 1.05 | Fail | Fail | 17.89 | Pass | Pass | Background only |
| 100 | `#CCFBF1` | 1.15 | Fail | Fail | 16.40 | Pass | Pass | Background only |
| 200 | `#99F6E4` | 1.30 | Fail | Fail | 14.59 | Pass | Pass | Background only |
| 300 | `#5EEAD4` | 1.53 | Fail | Fail | 12.39 | Pass | Pass | Background only |
| 400 | `#2DD4BF` | 1.86 | Fail | Fail | 10.24 | Pass | Pass | Background with dark text |
| 500 | `#14B8A6` | 2.18 | Fail | Fail | 5.45 | Pass | Pass | Background with dark text |
| 600 | `#0D9488` | 3.35 | Fail | Pass | 4.40 | Fail | Pass | Large text only |
| 700 | `#0F766E` | 5.25 | Pass | Pass | 3.06 | Fail | Pass | White text safe |
| 800 | `#115E59` | 7.24 | Pass | Pass | 2.29 | Fail | Fail | Deep surface |
| 900 | `#134E4A` | 9.31 | Pass | Pass | 1.78 | Fail | Fail | Dark accent surface |

Neutral scale:

| Scale | Hex | Contrast vs white | 4.5:1 | 3:1 | Contrast vs `#111111` | 4.5:1 | 3:1 | Guidance |
|---|---:|---:|---|---|---:|---|---|---|
| 50 | `#FAFAFA` | 1.04 | Fail | Fail | 17.96 | Pass | Pass | Page background |
| 100 | `#F4F4F5` | 1.10 | Fail | Fail | 16.96 | Pass | Pass | Secondary surface |
| 200 | `#E4E4E7` | 1.27 | Fail | Fail | 14.64 | Pass | Pass | Dividers |
| 300 | `#D4D4D8` | 1.49 | Fail | Fail | 12.52 | Pass | Pass | Borders |
| 400 | `#A1A1AA` | 2.58 | Fail | Fail | 7.21 | Pass | Pass | Disabled states |
| 500 | `#71717A` | 4.79 | Pass | Pass | 3.89 | Fail | Pass | Secondary text |
| 600 | `#52525B` | 7.81 | Pass | Pass | 2.39 | Fail | Fail | Supporting headings |
| 700 | `#3F3F46` | 10.41 | Pass | Pass | 1.79 | Fail | Fail | Body text |
| 800 | `#27272A` | 14.06 | Pass | Pass | 1.32 | Fail | Fail | Strong text |
| 900 | `#111827` | 17.74 | Pass | Pass | 1.00 | Fail | Fail | Highest emphasis text |

Accent orange scale:

| Scale | Hex | Contrast vs white | 4.5:1 | 3:1 | Contrast vs `#111111` | 4.5:1 | 3:1 | Guidance |
|---|---:|---:|---|---|---:|---|---|---|
| 50 | `#FFF7ED` | 1.12 | Fail | Fail | 16.63 | Pass | Pass | Background only |
| 100 | `#FFEDD5` | 1.19 | Fail | Fail | 15.63 | Pass | Pass | Background only |
| 200 | `#FED7AA` | 1.39 | Fail | Fail | 13.39 | Pass | Pass | Background only |
| 300 | `#FDBA74` | 1.75 | Fail | Fail | 10.64 | Pass | Pass | Highlight background |
| 500 | `#F97316` | 2.80 | Fail | Fail | 6.65 | Pass | Pass | CTA background with dark text |
| 700 | `#C2410C` | 5.00 | Pass | Pass | 3.72 | Fail | Pass | White text safe |
| 900 | `#7C2D12` | 9.57 | Pass | Pass | 1.95 | Fail | Fail | Deep accent surface |

Typography and spacing:

| Token | Value |
|---|---|
| Primary font | `Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial` |
| Mono font | `"Source Code Pro", ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace` |
| Sizes | `xs 0.75rem`, `sm 0.875rem`, `base 1rem`, `lg 1.125rem`, `xl 1.25rem`, `2xl 1.5rem`, `3xl 1.875rem`, `4xl 2.25rem`, `5xl 3rem` |
| Line heights | `1.25`, `1.5`, `1.6` |
| Spacing | `4, 8, 12, 16, 24, 32, 48, 64` |
| Radius | `4, 8, 12, 9999` |
| Shadows | `sm`, `md`, `lg` from token JSON |

Responsive layout specs:

| Page | Mobile | Tablet | Desktop | LCP element | FID/INP focus |
|---|---|---|---|---|---|
| Homepage | 1 col | 8 col, `5/3` hero | 12 col, `7/5` hero | hero visual or H1 | nav toggle, CTAs, project cards |
| AutoSOC Project | 1 col | stacked content + rail | 12 col, `8/4` split | hero architecture frame | copy buttons, drawers, CTA |
| Demo | 1 col | runner above gallery | 12 col, `5/7` split | demo intro panel | command copy, gallery selection |

Breakpoints:

- Mobile: `<= 640px`
- Tablet: `641-1024px`
- Desktop: `>= 1025px`
- Desktop max width: `1200px`
- Iconography direction: thin-line operational glyphs, monochrome or token-tinted

#### Key Visuals

Homepage:

```text
+--------------------------------------------------------------------+
| nav + proof-first CTA                                              |
+--------------------------------------------------------------------+
| strong H1 | subhead | two CTAs | architecture visual               |
+--------------------------------------------------------------------+
| feature strip: AutoSOC | Detections | Proof | Lab                  |
+--------------------------------------------------------------------+
| featured projects grid (3 cards)                                   |
+--------------------------------------------------------------------+
| counts / proof strip                                               |
+--------------------------------------------------------------------+
```

Project page:

```text
+--------------------------------------------------------------------+
| title + summary + architecture snapshot + proof rail               |
+--------------------------------------------------------------------+
| overview and outcome                                               |
| command/code block                                                 |
| demo runner                                                        |
| media gallery                                                      |
+--------------------------------------------------------------------+
```

Demo page:

```text
+--------------------------------------------------------------------+
| intro + status chips                                               |
+--------------------------------------------------------------------+
| demo runner                      | media gallery                    |
+--------------------------------------------------------------------+
| steps + troubleshooting + CTA                                       |
+--------------------------------------------------------------------+
```

Mockup files and alt text:

| File | Alt text |
|---|---|
| `docs/design/mockups/home-desktop.svg` | HawkinsOps MODERNIZE homepage desktop mockup with proof-first hero and featured projects |
| `docs/design/mockups/home-tablet.svg` | HawkinsOps MODERNIZE homepage tablet mockup with stacked hero visual and two-column cards |
| `docs/design/mockups/home-mobile.svg` | HawkinsOps MODERNIZE homepage mobile mockup with compact hero and one-column project list |
| `docs/design/mockups/project-desktop.svg` | HawkinsOps MODERNIZE AutoSOC project desktop mockup with architecture snapshot and evidence rail |
| `docs/design/mockups/project-tablet.svg` | HawkinsOps MODERNIZE AutoSOC project tablet mockup with stacked sections and proof sidebar |
| `docs/design/mockups/project-mobile.svg` | HawkinsOps MODERNIZE AutoSOC project mobile mockup with compact proof cards and demo block |
| `docs/design/mockups/demo-desktop.svg` | HawkinsOps MODERNIZE demo page desktop mockup with demo runner and media gallery |
| `docs/design/mockups/demo-tablet.svg` | HawkinsOps MODERNIZE demo page tablet mockup with runner above gallery |
| `docs/design/mockups/demo-mobile.svg` | HawkinsOps MODERNIZE demo page mobile mockup with one-column walkthrough and CTA |

#### Component Library

Reference stubs:

- `Hero`
- `Card`
- `ProjectLayout`
- `CodeBlock`
- `MediaGallery`
- `CTA`
- `Nav`
- `Footer`
- `DemoRunner`

All reference files live under `docs/design/reference/components/` and include short `// WHY` comments.

#### Example Pages

- Next.js App Router friendly examples live under `docs/design/reference/app/home/page.tsx` and `docs/design/reference/app/project/page.tsx`
- Static HTML equivalents can be derived from the same token and layout rules
- SEO template per page uses title, description, Open Graph image, and `summary_large_image`

#### Accessibility and Performance Checklist

- Lighthouse goals:
  - Performance `>= 90`
  - Accessibility `>= 90`
  - Best Practices `>= 90`
  - SEO `>= 90`
- Use semantic landmarks and visible focus states
- Keep body text contrast `>= 4.5:1`
- Keep actionable control contrast `>= 3:1`
- Inline critical hero CSS
- Lazy-load below-the-fold gallery media
- Keep hero image under a tight byte budget
- Staged image-heavy upgrade:
  1. LQIP + responsive `picture`
  2. AVIF/WebP with fallback
  3. lazy-load all non-critical media

#### Assets Plan

| Asset | Desktop | Tablet | Mobile | Formats |
|---|---:|---:|---:|---|
| Hero visual | `1600x900` | `960x720` | `640x480` | `AVIF`, `WebP`, fallback `PNG/JPG` |
| Project gallery | `1440x900` | `960x640` | `640x480` | `WebP`, fallback `PNG` |
| Open Graph | `1600x900` | n/a | n/a | `PNG` |
| Icons | vector | vector | vector | `SVG` |

- Use inline SVG for diagrams and badge-style UI icons
- Use a sprite only if icon reuse becomes high
- Prefer `srcset` or `picture` for raster screenshots

#### Migration and Rollout

1. Add token JSON and CSS variables.
2. Mirror tokens into a small static CSS layer for `site/`.
3. Build one canary path:
   - `site/modernize/index.html`, or
   - `?variant=modernize`, or
   - alternate stylesheet via query parameter.
4. Test recruiter and proof paths on canary.
5. Promote hero, cards, and project sections in phases.
6. Keep React/Tailwind references in docs as future extraction targets.

A/B test ideas:

- Hero CTA copy: `View AutoSOC` vs `Read the AutoSOC Case Study`
- Card order: AutoSOC first vs Proof first
- Hero visual density: diagram in hero vs moved below fold

Primary metrics:

- AutoSOC case-study clicks
- Proof page clicks
- Resume opens/downloads
- Demo engagement

#### Acceptance Criteria

- Local preview or canary communicates the new design language without hiding proof
- LCP `<= 1.8s` on desktop
- Accessibility, Best Practices, and SEO each `>= 90`
- Core cards are readable at glance in under 5 seconds
- Token JSON parses and TSX stubs are copy/paste runnable with minimal edits

#### Estimate

- Visible-impact sprint: `1 week`
- Full rollout: `2-4 weeks`

#### One-Week Sprint Plan

| Priority | Task | Estimate |
|---|---|---:|
| 1 | Finalize tokens and contrast | 4h |
| 2 | Build canary homepage and AutoSOC prototype | 8h |
| 3 | Produce reference components and mockups | 8h |
| 4 | Optimize hero/media assets | 4h |
| 5 | Accessibility and Lighthouse pass | 4h |
| 6 | PR body and rollout notes | 2h |

### TRANSFORM

Approach: full visual rebrand with motion system, richer narrative layout, deeper component library, and a staged migration path that may eventually justify a framework move or a parallel component package. Best for maximum differentiation, not for the shortest hiring-cycle payoff.

#### Design System

Color summary:

| Family | Key shade | Contrast vs white | 4.5:1 | 3:1 | Contrast vs `#111111` | 4.5:1 | 3:1 | Guidance |
|---|---:|---:|---|---|---:|---|---|---|
| Cyan | `#06B6D4` | 2.43 | Fail | Fail | 6.14 | Pass | Pass | Dark text only |
| Cyan dark | `#0E7490` | 5.18 | Pass | Pass | 3.03 | Fail | Pass | White text safe |
| Slate | `#334155` | 10.03 | Pass | Pass | 1.85 | Fail | Fail | Body text |
| Violet | `#8B5CF6` | 4.23 | Fail | Pass | 2.87 | Fail | Fail | Large accent only |
| Violet dark | `#6D28D9` | 7.73 | Pass | Pass | 2.15 | Fail | Fail | White text safe |

- Primary font: `Inter`
- Display accent: `Sora`
- Mono: `"Source Code Pro"`
- Spacing: `4, 8, 12, 16, 24, 32, 48, 64, 96`
- Motion: staggered reveal, soft panel drift, reduced-motion fallback required

Layout specs:

| Breakpoint | Width | Grid | Max width |
|---|---:|---|---:|
| Mobile | `<= 640px` | 1 col | fluid with `16px` gutters |
| Tablet | `641-1024px` | 8 col | `1024px` |
| Desktop | `>= 1025px` | 12 col | `1280px` |

- LCP element: hero display block or animated architecture frame
- FID/INP focus: reduced-motion-safe transitions, gallery, demo runner controls

#### Key Visuals

Homepage:

```text
+--------------------------------------------------------------------+
| layered nav + brand strip                                          |
+--------------------------------------------------------------------+
| narrative hero + animated architecture ribbon                      |
+--------------------------------------------------------------------+
| chapter cards + proof metrics + timeline                           |
+--------------------------------------------------------------------+
| project stories + CTA                                              |
+--------------------------------------------------------------------+
```

Project page:

```text
+--------------------------------------------------------------------+
| outcome chapter + architecture + evidence + lessons                |
+--------------------------------------------------------------------+
```

Demo page:

```text
+--------------------------------------------------------------------+
| guided runner + motion-aware gallery + CTA                         |
+--------------------------------------------------------------------+
```

Mockup files:

- `docs/design/mockups/transform-home-desktop.svg`
- `docs/design/mockups/transform-home-tablet.svg`
- `docs/design/mockups/transform-home-mobile.svg`
- `docs/design/mockups/transform-project-desktop.svg`
- `docs/design/mockups/transform-project-tablet.svg`
- `docs/design/mockups/transform-project-mobile.svg`
- `docs/design/mockups/transform-demo-desktop.svg`
- `docs/design/mockups/transform-demo-tablet.svg`
- `docs/design/mockups/transform-demo-mobile.svg`

#### Component Library

- Reuse all MODERNIZE stubs as baseline
- Add animation primitives and richer layout framing only if a stronger component system is approved
- Best fit if a future `web/` or separate component package is introduced

#### Example Pages

- Home, project, and demo examples should preserve current IA while allowing narrative treatment
- All motion-heavy sections require reduced-motion fallback

#### Accessibility and Performance Checklist

- WCAG AA still required
- Honor `prefers-reduced-motion`
- No autoplay audio or blocking video hero
- Lighthouse goals:
  - Performance `>= 85`
  - Accessibility `>= 92`
  - Best Practices `>= 90`
  - SEO `>= 90`

#### Assets Plan

- Stage assets carefully:
  1. vector hero layer
  2. responsive screenshots and diagrams
  3. optional muted loop only if budget allows
- Use SVG for decorative framing and AVIF/WebP for screenshots

#### Migration and Rollout

1. Start as a parallel prototype outside production CSS.
2. Validate recruiter response.
3. Promote only approved sections into `site/`.
4. Keep static fallback views for motion-heavy layouts.

#### Acceptance Criteria

- Distinctive visual identity documented and reproducible
- Reduced-motion and no-JS fallback remain usable
- Component system and tokens are documented
- The site feels more differentiated without losing trustworthiness

#### Estimate

- `4-8 weeks`

#### One-Week Sprint Plan

| Priority | Task | Estimate |
|---|---|---:|
| 1 | Finalize visual concept | 1 day |
| 2 | Produce hero, project, and demo mockups | 1 day |
| 3 | Build advanced component references | 1 day |
| 4 | Test motion and performance budget | 1 day |
| 5 | Draft staged migration notes | 0.5 day |

## 3. Figma Tokens JSON

Recommended mode token file: [tokens/modernize-tokens.json](../tokens/modernize-tokens.json)

```json
{
  "global": {
    "color": {
      "primary": {
        "50": "#F0FDF9",
        "100": "#CCFBF1",
        "200": "#99F6E4",
        "300": "#5EEAD4",
        "400": "#2DD4BF",
        "500": "#14B8A6",
        "600": "#0D9488",
        "700": "#0F766E",
        "800": "#115E59",
        "900": "#134E4A"
      },
      "neutral": {
        "50": "#FAFAFA",
        "100": "#F4F4F5",
        "200": "#E4E4E7",
        "300": "#D4D4D8",
        "400": "#A1A1AA",
        "500": "#71717A",
        "600": "#52525B",
        "700": "#3F3F46",
        "800": "#27272A",
        "900": "#111827"
      },
      "accent": {
        "50": "#FFF7ED",
        "100": "#FFEDD5",
        "200": "#FED7AA",
        "300": "#FDBA74",
        "400": "#FB923C",
        "500": "#F97316",
        "600": "#EA580C",
        "700": "#C2410C",
        "800": "#9A3412",
        "900": "#7C2D12"
      }
    },
    "type": {
      "fontPrimary": "Inter, ui-sans-serif, system-ui, -apple-system, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial",
      "fontMono": "\"Source Code Pro\", ui-monospace, SFMono-Regular, Menlo, Monaco, \"Roboto Mono\", monospace",
      "size": {
        "xs": "0.75rem",
        "sm": "0.875rem",
        "base": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem",
        "3xl": "1.875rem",
        "4xl": "2.25rem",
        "5xl": "3rem"
      },
      "lineHeight": {
        "sm": "1.25",
        "base": "1.5",
        "lg": "1.6"
      }
    },
    "space": {
      "1": "4px",
      "2": "8px",
      "3": "12px",
      "4": "16px",
      "5": "24px",
      "6": "32px",
      "7": "48px",
      "8": "64px"
    },
    "radius": {
      "sm": "4px",
      "md": "8px",
      "lg": "12px",
      "pill": "9999px"
    },
    "shadow": {
      "sm": "0 1px 2px rgba(16,24,40,0.05)",
      "md": "0 4px 12px rgba(16,24,40,0.08)",
      "lg": "0 12px 24px rgba(16,24,40,0.12)"
    }
  }
}
```

## 4. Concrete Code Snippets

- Tailwind config: [docs/design/reference/tailwind.config.js](./design/reference/tailwind.config.js)
- Tokens CSS: [docs/design/reference/tokens.css](./design/reference/tokens.css)
- Hero example: [docs/design/reference/components/Hero.tsx](./design/reference/components/Hero.tsx)
- Dark-mode overrides live in `tokens.css`

Inline SVG example from the mockup set:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="430" height="1320" role="img" aria-label="HawkinsOps MODERNIZE demo page mobile mockup with one-column walkthrough and CTA">
  <rect width="430" height="1320" fill="#FAFAFA"/>
  <rect x="16" y="80" width="398" height="150" rx="18" fill="#FFFFFF" stroke="#E4E4E7"/>
  <rect x="16" y="260" width="398" height="220" rx="18" fill="#FFFFFF" stroke="#E4E4E7"/>
  <rect x="16" y="510" width="398" height="180" rx="18" fill="#ECFDF5"/>
  <rect x="16" y="720" width="398" height="180" rx="18" fill="#CCFBF1"/>
  <rect x="16" y="930" width="398" height="180" rx="18" fill="#99F6E4"/>
</svg>
```

PowerShell branch/create/commit snippet:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -Command "
cd 'C:\GitHub\HawkinsOperations';
$b='codex/visual-upgrade-MODERNIZE-$(Get-Date -Format yyyyMMddHHmm)';
git checkout -b $b;
git add docs tokens;
git commit -m 'feat(web-visuals): sketch MODERNIZE design system and components' -m 'Fallback templates used because .codex/COMMIT_TEMPLATE.md and .codex/PR_TEMPLATE.md were not present during repo inspection.';
Write-Host 'Branch:' $b
"
```

## 5. PR Body

Ready-to-paste recommended mode PR body: [docs/design/PR_BODY_MODERNIZE.md](./design/PR_BODY_MODERNIZE.md)

Note: `./.codex/COMMIT_TEMPLATE.md` and `./.codex/PR_TEMPLATE.md` were not present during repo inspection, so this package uses [.github/PULL_REQUEST_TEMPLATE.md](../.github/PULL_REQUEST_TEMPLATE.md) as the structural fallback.

## 6. Tasks Backlog Table

See [docs/design/TASKS_MODERNIZE.md](./design/TASKS_MODERNIZE.md).

## 7. Quick Test Plan

1. Parse `tokens/modernize-tokens.json`.
2. Open SVG fixtures in browser or Figma and export PNGs if needed.
3. Drop reference TSX files into a stock Next.js + Tailwind app and confirm imports resolve with minimal edits.
4. Run:

```powershell
python -c "import json; json.load(open(r'tokens/modernize-tokens.json', 'r', encoding='utf-8')); print('tokens ok')"
pwsh -File .\scripts\verify\verify-counts.ps1
python .\scripts\drift_scan.py
```

## Why I Recommended MODERNIZE

MODERNIZE fixes the site's visual and accessibility weaknesses without forcing a platform migration. It preserves the repo's proof-first tone, gives hiring managers a more current interface to evaluate, and creates durable implementation assets such as tokens, reference components, and deterministic mockups that can be carried into a later componentized site if needed.
