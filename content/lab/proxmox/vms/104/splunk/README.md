# Splunk VM

## Purpose
- Dedicated lab VM for Splunk investigation-layer operations and validation.

## VM Identity
- VMID: `104`
- Hostname: `HO-SPLUNK-01`
- Role: Splunk VM

## Snapshot and Reset Policy
- Keep a clean baseline snapshot before major Splunk config changes.
- Reset to baseline after failed ingest experiments or major package/config drift.
- Record snapshot labels and reset triggers using `[REDACTED_INTERNAL]` where needed.

## Evidence to Collect (Redacted)
- Service status and validation notes.
- Sanitized command outputs and screenshots.
- Redacted `qm config 104` text export in `exports/`.

## Redaction Rules
- No secrets, tokens, keys, or credentials.
- No internal IPs.
- Use `[REDACTED_INTERNAL]` for sensitive internal details.
