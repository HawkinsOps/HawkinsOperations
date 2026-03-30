# HawkinsOperations Release Notes - v1.4.0

Release date: 2026-03-03  
Scope: SignalFoundry (AutoSOC) March 2026 stabilization and release closure

## Summary

Version `v1.4.0` finalized the March 2026 operational hardening lane and aligned public proof links with execution artifacts used for reviewer validation.

## Included Changes

1. AutoSOC operational hardening updates documented and linked for replay.
2. Rootcheck noise-tuning closeout documented with redacted evidence.
3. Sysmon intake and triage-policy controls integrated into the release narrative.
4. Release chain normalized across:
   - Case study surface
   - March release timeline surface
   - Execution docs under `docs/execution`

## Validation Path

Run repository verification commands from repo root:

```powershell
pwsh -NoProfile -File .\scripts\verify\verify-counts.ps1
python .\scripts\drift_scan.py
```

## Primary References

- `C:\RH\OPS\10_Portfolio\HawkinsOperations\docs\execution\AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md`
- `C:\RH\OPS\10_Portfolio\HawkinsOperations\docs\execution\ROOTCHECK_CLOSEOUT_REDACTED_2026-03-02.md`
- `C:\RH\OPS\10_Portfolio\HawkinsOperations\site\march-2026-release.html`
- `C:\RH\OPS\10_Portfolio\HawkinsOperations\site\case-study-autosoc.html`

## Notes

This file exists as the canonical `v1.4.0` release target referenced by the public site links. It prevents GitHub `404` link hits for the release-notes path and keeps proof-lane navigation coherent.
