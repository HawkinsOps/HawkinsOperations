# SEO Audit Report — hawkinsops.com

**Date:** 2026-03-30  
**Status:** Audit complete, fixes applied  
**Auditor:** Claude Code (automated)

---

## Executive Summary

hawkinsops.com had **zero visibility** in search engines. Five external search queries confirmed the site is not indexed at all. The root cause is likely that the site was never submitted to Google Search Console with a sitemap, and the original sitemap.xml was minimal (no `lastmod`, `changefreq`, or `priority` fields). Several pages were also missing critical SEO meta tags.

**All technical fixes have been applied.** Manual Google Search Console steps are required to complete the fix.

---

## 1. robots.txt

**File:** `site/robots.txt`  
**Status:** OK — no changes needed

```
User-agent: *
Allow: /

Sitemap: https://hawkinsops.com/sitemap.xml
```

- Not blocking any crawlers
- References sitemap correctly
- Clean and correct

---

## 2. sitemap.xml

**File:** `site/sitemap.xml`  
**Previous state:** Existed but was minimal — 16 URLs with no `lastmod`, `changefreq`, or `priority`  
**Fixed state:** 27 URLs with full metadata

### Pages included (27):
| URL | Priority | Type |
|-----|----------|------|
| `/` | 1.0 | Homepage |
| `/case-study-autosoc` | 0.9 | Case study |
| `/proof` | 0.9 | Proof surface |
| `/case-study-detection-harness` | 0.9 | Case study |
| `/case-study-sigma-library` | 0.9 | Case study |
| `/case-study-honeypot` | 0.9 | Case study |
| `/case-study-ir-howe01` | 0.9 | Case study |
| `/case-study-ir-playbooks` | 0.9 | Case study |
| `/case-study-cve-patch` | 0.9 | Case study |
| `/case-study-soc-integration` | 0.9 | Case study |
| `/case-study-splunk-codex-hunt` | 0.9 | Case study |
| `/case-study` | 0.9 | Case study index |
| `/case-studies` | 0.9 | Case studies listing |
| `/resume` | 0.8 | Resume |
| `/detections` | 0.7 | Detection surface |
| `/enterprise-security` | 0.7 | Enterprise hardening |
| `/operations-bridge` | 0.7 | Ops bridge |
| `/march-2026-deep-dive` | 0.7 | Deep dive |
| `/architecture` | 0.7 | Architecture |
| `/projects` | 0.7 | Projects |
| `/wildcard` | 0.7 | About |
| `/proof/honeypot` | 0.7 | Honeypot proof |
| `/autosoc-cutover` | 0.7 | AutoSOC cutover |
| `/autosoc-hotfix-rca` | 0.7 | Hotfix RCA |
| `/modernize/` | 0.7 | Modernize index |
| `/modernize/autosoc` | 0.7 | Modernize AutoSOC |
| `/modernize/demo` | 0.7 | Modernize demo |

### Pages excluded (correct):
| File | Reason |
|------|--------|
| `soc-lab.html` | Redirect stub (meta refresh to `/enterprise-security`) |
| `security.html` | Redirect stub (meta refresh to `/detections`, has `noindex`) |
| `lab.html` | Redirect stub (meta refresh to `/enterprise-security`, has `noindex`) |
| `triage.html` | Redirect stub (meta refresh to `/enterprise-security`, has `noindex`) |
| `start-here.html` | Redirect stub (meta refresh to `/`) |
| `march-2026-release.html` | Redirect stub (meta refresh to GitHub Releases) |
| `career-intelligence.html` | Redirect stub (meta refresh to `/operations-bridge`) |
| `blog-python2-to-python3.html` | Redirected to 404 via `_redirects` |
| `404.html` | Error page |
| `partials/footer.html` | HTML fragment, not a page |

---

## 3. Cloudflare `_headers`

**File:** `site/_headers`  
**Status:** OK — no SEO-blocking headers

Security headers are properly configured:
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options: DENY`
- `Permissions-Policy` (camera, microphone, geolocation denied)
- `Content-Security-Policy` (properly scoped)

**No `X-Robots-Tag` header.** This is correct — not blocking crawlers.

---

## 4. Cloudflare `_redirects`

**File:** `site/_redirects`  
**Status:** OK — no SEO interference

Redirects are clean 301s for canonical URL normalization. Notable:
- `/blog-python2-to-python3` → `/404` (301) — dead page correctly removed
- `/proof/honeypot` → `honeypot-proof.html` (200 rewrite) — correct
- Trailing slash normalization for case studies — correct

---

## 5. noindex Directives

**Only 3 pages have `noindex`** — all are redirect stubs (correct):
| File | Directive |
|------|-----------|
| `security.html` | `<meta name="robots" content="noindex,follow">` |
| `lab.html` | `<meta name="robots" content="noindex,follow">` |
| `triage.html` | `<meta name="robots" content="noindex,follow">` |

No content pages have `noindex`. No `googlebot` directives found.

---

## 6. Meta Tags — Per-Page Audit

### Pages with complete SEO tags (before fixes):
| Page | Title | Description | Canonical | OG | Twitter |
|------|-------|-------------|-----------|-----|---------|
| `index.html` | YES | YES | YES | Full | Full |
| `resume.html` | YES | YES | YES | Full | Full |
| `detections.html` | YES | YES | YES | Full | Full |
| `proof.html` | YES | YES | **MISSING** | Full | Full |
| `wildcard.html` | YES | YES | YES | Full | Full |
| `blog-python2-to-python3.html` | YES | YES | YES | Full | Full |
| All case-study-*.html | YES | YES | YES | Full | Full |

### Pages that needed fixes (now fixed):
| Page | What was missing | Fix applied |
|------|-----------------|-------------|
| `proof.html` | Canonical | Added `<link rel="canonical">` |
| `enterprise-security.html` | og:image, twitter:image | Added OG image + Twitter image |
| `architecture.html` | og:*, twitter:* | Added full OG + Twitter tags |
| `autosoc-cutover.html` | og:image, twitter:* | Added OG image + Twitter tags |
| `autosoc-hotfix-rca.html` | og:image, twitter:* | Added OG image + Twitter tags |
| `case-studies.html` | og:image, twitter:* | Added OG image + Twitter tags |
| `operations-bridge.html` | og:image | Added OG image tags |
| `case-study-splunk-codex-hunt.html` | og:image | Added OG image tags |
| `modernize/index.html` | og:*, twitter:* | Added full OG + Twitter tags |
| `modernize/autosoc.html` | og:*, twitter:* | Added full OG + Twitter tags |

### Redirect stubs (no SEO tags needed):
`soc-lab.html`, `security.html`, `lab.html`, `triage.html`, `start-here.html`, `march-2026-release.html`, `career-intelligence.html`

---

## 7. Structured Data (JSON-LD)

**Added:**
- `index.html`: `@type: WebSite` + `@type: Person` (Raylee Hawkins, Detection Engineer & SOC Analyst)
- `resume.html`: `@type: Person` with `worksFor`, `knowsAbout`, `hasCredential`, `sameAs`

---

## 8. External Visibility Check

| Query | Result |
|-------|--------|
| `site:hawkinsops.com` | **ZERO results** — not indexed |
| `"hawkinsops.com"` | **ZERO results** — only unrelated Hawkins businesses |
| `"raylee hawkins" detection engineer` | **NOT FOUND** — only social media/softball profiles |
| `"raylee hawkins" SOC` | **NOT FOUND** — only softball profiles |
| `SignalFoundry hawkinsops` | **NOT FOUND** — only type foundry results |

**Conclusion:** The site has zero search engine presence. This is a submission/indexing problem, not a blocking problem.

---

## 9. Count Consistency Check

**Authority source:** `site/data/truth/current-authority.json` (2026-03-25)

| Metric | Authority Value | Site Values | Consistent? |
|--------|----------------|-------------|-------------|
| Total cases | 321,351+ | All instances match | YES |
| Escalations | 6,178 | All instances match | YES |
| Auto-close rate | ~88% | All instances match | YES |
| Detection count | 140 | All instances match | YES |
| Sigma rules | 103 | All instances match | YES |
| Splunk queries | 9 | All instances match | YES |
| Wazuh rule blocks | 28 | All instances match | YES |
| IR playbooks | 10 | All instances match | YES |

**Note:** `55130` appears in `case-study-cve-patch.html` and `case-study-soc-integration.html` but refers to CVE-2025-55130 (a CVE ID), not a case count. This is a false positive.

**All metrics are consistent with the authority file.**

---

## 10. Required Manual Steps (Post-Deploy)

After the Cloudflare Pages deploy completes:

1. **Google Search Console** — Submit sitemap at `https://hawkinsops.com/sitemap.xml`
2. **Request indexing** for priority pages: `/`, `/case-study-autosoc`, `/proof`, `/resume`, `/detections`
3. **Verify domain ownership** if not already done (DNS TXT record or HTML file method)
4. **Bing Webmaster Tools** — Submit sitemap there too for Bing/DuckDuckGo coverage
5. **Monitor** — Check GSC coverage report after 1-2 weeks for any crawl errors
