# CodeQL Triage — 2026-04-11

First CodeQL scan on this repo ran 2026-04-11 after enabling default setup. This document records the triage of all 9 initial alerts.

---

## 1. js/xss-through-dom — `site/assets/home.js:134`

**CodeQL's concern:** A value read from a DOM attribute (`data-gh-url`) flows into `node.setAttribute("href", ...)`, which could allow DOM-based XSS if the attribute is attacker-controlled.

**Verdict:** False positive.

**Reasoning:** The `data-gh-url` attributes are hardcoded in my own HTML templates. This is a static site with no user-generated content. There is no path for attacker-controlled data to reach these attributes.

**Dismissal:** false positive

---

## 2. js/xss-through-dom — `site/assets/app.js:291`

**CodeQL's concern:** A value read from a DOM attribute (`data-src`) flows into `img.setAttribute('src', src)`, which could allow DOM-based XSS.

**Verdict:** False positive.

**Reasoning:** The `data-src` attributes are set in author-controlled HTML for screenshot cards. No user input reaches these attributes. The value is used as an image source, not injected as HTML.

**Dismissal:** false positive

---

## 3. js/xss-through-dom — `site/assets/components/sections/media-gallery.js:131`

**CodeQL's concern:** A value read from a DOM attribute (`data-src`) flows into `img.src`, which could allow DOM-based XSS.

**Verdict:** False positive.

**Reasoning:** Identical pattern to alert 2. The lightbox reads `data-src` and `data-caption` from author-controlled markup. `img.src` is set to a known-good image path; `cap.textContent` is used for the caption (textContent, not innerHTML). No injection vector exists.

**Dismissal:** false positive

---

## 4. py/clear-text-logging-sensitive-data — `scripts/auto-soc/poll-alerts.py:251`

**CodeQL's concern:** The expression `fetch_meta.get('password_source', 'UNKNOWN')` is printed to stdout, potentially logging sensitive credential data in cleartext.

**Verdict:** False positive.

**Reasoning:** This logs the password *source label* (e.g., `"ENV_VAR"`, `"DOTENV_LEGACY"`) — a string describing where the credential was loaded from, not the credential itself. CodeQL keyed on the field name `password_source` and assumed the value is a secret.

**Dismissal:** false positive

---

## 5. py/clear-text-logging-sensitive-data — `scripts/auto-soc/poll-alerts.py:252`

**CodeQL's concern:** The expression `fetch_meta.get('mode', args.mode)` is printed to stdout, potentially logging sensitive data.

**Verdict:** False positive.

**Reasoning:** This logs the polling mode string (e.g., `"api"`, `"file"`). It is operational metadata with no sensitive content. Flagged only because it appears in the same `fetch_meta` dictionary as the `password_source` key.

**Dismissal:** false positive

---

## 6. py/clear-text-storage-sensitive-data — `scripts/auto-soc/poll-alerts.py:152`

**CodeQL's concern:** Raw alert data is written to disk as JSON via `path.write_text(json.dumps(alert, ...))`, potentially storing sensitive fields (hostnames, IPs, usernames) in cleartext.

**Verdict:** Architectural accept (won't fix).

**Reasoning:** This is the alert queue ingestion point. Raw Wazuh alerts must be written to disk so the downstream pipeline stages can process, triage, and redact them. Redaction happens in a later stage before any data reaches the public portfolio. The architecture is intentional: ingest raw, redact downstream, publish clean. Moving redaction upstream would break the pipeline's separation of concerns.

**Dismissal:** won't fix

---

## 7. py/clear-text-storage-sensitive-data — `scripts/auto-soc/run-pipeline.py:282`

**CodeQL's concern:** Heartbeat data is appended to a history file via `out.write(json.dumps(heartbeat))`, potentially storing sensitive data in cleartext.

**Verdict:** False positive.

**Reasoning:** The heartbeat object contains operational metadata: timestamps, step durations, run status, polling stats. No credentials, alert content, or PII are included in the heartbeat schema.

**Dismissal:** false positive

---

## 8. py/clear-text-storage-sensitive-data — `scripts/auto-soc/run-pipeline.py:297`

**CodeQL's concern:** Metrics data is appended to a history file via `out.write(json.dumps(metrics))`, potentially storing sensitive data in cleartext.

**Verdict:** False positive.

**Reasoning:** The metrics object contains run timing, case counts, pipeline mode, and status. No sensitive data is present. CodeQL flagged this because it is in the same function scope as the heartbeat write.

**Dismissal:** false positive

---

## 9. py/clear-text-storage-sensitive-data — `scripts/auto-soc/common.py:46`

**CodeQL's concern:** The generic `write_json()` utility writes arbitrary data to disk, potentially storing sensitive data in cleartext.

**Verdict:** False positive.

**Reasoning:** This is a utility function. Whether data is sensitive depends on the caller, not the function. The callers that write alert data (poll-alerts.py:152) are addressed in alert 6 above. The remaining callers write operational metadata only.

**Dismissal:** false positive
