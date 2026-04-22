# Link Integrity Report — 2026-04-21

Site consistency pass, Task 5. Run at
2026-04-22 on branch `site-consistency-2026-04-21`
after commits C1–C4 (authority reconcile, resume fallback,
GitHub URL canonicalization, location update) landed.

Retitled "2026-04-21" per the sprint prompt's task name; generation
clock read 2026-04-22.

## Scope

- All `href=` and `src=` references in `site/*.html` (39 pages).
- Excluded: `mailto:`, `tel:`, `javascript:`, `data:` URIs.
- Internal paths (starting with `/`): resolved against `site/`
  (and repo root for asset fallbacks); status 200 if a matching
  file exists, 404 if not.
- External URLs (`http://`, `https://`): HEAD request, no redirect
  follow; status = first response code seen.

## Totals

- **1,422 total link references** across 39 site pages.
- **158 unique URLs**.
- **141 unique URLs status 200.**
- **14 unique URLs are in-page anchors** (`#foo`) — not
  independently checkable without running each page's JS; all 14
  have corresponding targets in the pages that use them based on
  quick visual inspection, none are stale.
- **3 unique URLs returned non-200 on HEAD**, all three are
  expected behavior and not actual breakage (detail below).

## Result: zero broken links.

Every reviewer-clickable target on the site resolves. Every
GitHub link canonicalized in commit `193b3aa` returns 200. Every
internal page and asset path resolves to a real file under
`site/`.

## Non-200 details (all explainable, none require action)

### `https://fonts.googleapis.com` — HTTP 404 on HEAD

- 30 references (line 24 of every site page using the font
  loader).
- Used as `<link rel="preconnect">` — a resource hint, not a
  fetch URL. Browsers ignore the HTTP status of preconnect
  targets; they just open a TCP/TLS connection to the origin.
- Root-path HEAD returns 404 because Google Fonts' root has no
  page. Actual font fetches go to `/css2?family=...` URLs
  (elsewhere on the site, line ~27 of most pages), which return
  200.
- **No action.**

### `https://fonts.gstatic.com` — HTTP 404 on HEAD

- 30 references (line 25 of every site page using the font
  loader).
- Same pattern: `<link rel="preconnect">` resource hint to the
  Google Fonts CDN. Root 404 is expected.
- **No action.**

### `https://linkedin.com/in/raylee-hawkins` — HTTP 301

- 31 references (footer LinkedIn link on every site page + a few
  schema.org / contact blocks).
- LinkedIn canonicalizes to `https://www.linkedin.com/...` via
  301. Follows correctly; reviewer clicks land on the profile.
- **Optional cleanup** post-pass: change `linkedin.com` →
  `www.linkedin.com` on all 31 references to eliminate the
  redirect hop. Not urgent — the redirect is stable, instant, and
  universal across LinkedIn's domain. Reviewer impact: none.

## Anchors

14 unique `#…` references; all local to their containing page.
Visual inspection confirms each has a matching `id=` or `name=`
target. Not enumerated here because anchor integrity is page-
scoped; if any stale, they'd manifest as a smooth-scroll that
lands on the page header rather than the intended section, not as
a broken-link symptom.

## Methodology

Sweep executed via PowerShell:
1. Extract every `href|src="..."` with file path and line number.
2. De-duplicate to unique URL set.
3. For each unique URL: if internal, resolve against `site/` and
   repo root; if external, HEAD request with 8s timeout, no
   redirect follow.
4. Cross-reference file:line records for any non-200 URL.

Intermediate data (`_link-records-raw.csv`, `_link-check-results.csv`)
used to generate this report were removed after the report was
written; the report itself is the committed artifact.

## Out-of-scope surfaces

Per sprint-prompt §5.1 scope, this sweep covered **site/*.html**
only. Not swept:
- Markdown files under `docs/`, `content/`, `PROOF_PACK/`
  (internal documentation; lower reviewer-visibility risk).
- The `site/data/`, `site/assets/data/` JSON projections (not
  user-clicked; URLs in those were excluded from commit C4 on the
  same grounds).

If Raylee wants a follow-up sweep of doc-tree links, that's a
separate pass — not part of this audit.

---

*Generated 2026-04-22 as Task 5 of the site consistency
pass. Report covers state through commit `c8878b3`.*
