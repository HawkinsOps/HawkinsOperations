# Case Study: Hotfix RCA — AutoSOC Triage Quality Chart Renderer
**Diagnosing and Fixing a Silent Pipeline Failure Under Production Scheduling**

---

## The Symptom

The AutoSOC pipeline runs on a schedule. One of its steps — rendering a trend chart of triage quality metrics — had been silently failing. The chart artifact wasn't updating. Downstream, the pipeline continued because the chart step isn't a hard dependency, but the failure was real: every scheduled run was hitting an error at that step and moving on without producing output.

The failure wasn't obvious. The pipeline reported overall success because it's designed to be resilient. The chart step was broken in isolation, and the only way to catch it was to look directly at the runtime log.

---

## Diagnosis

I pulled the pipeline log tail and found the error immediately:

```
$ pwsh -NoProfile -File render-triage-quality-chart.ps1

Assert-CanonicalPath: render-triage-quality-chart.ps1:10
  10 | Assert-CanonicalPath -PathValue $CsvPath -Label "CsvPath"
     | ~~~~~~~~~~~~~~~~~~~~
     | The term 'Assert-CanonicalPath' is not recognized as a name of a cmdlet,
     | function, script file, or executable program.
```

The script was calling `Assert-CanonicalPath` on line 10. The function itself was defined later in the same file. PowerShell doesn't pre-scan function declarations the way some languages do — it executes top to bottom, so a function called before its declaration doesn't exist yet at the time of the call.

---

## Root Cause

**Function-order bug.** `Assert-CanonicalPath` was being invoked before it was declared in the script. Every execution — whether triggered by the scheduler or run manually — hit this error at line 10 and terminated before rendering any output.

This is a category of bug that's easy to miss in development because scripts often get written with helper functions at the bottom, which is fine for languages that hoist declarations. PowerShell doesn't. The fix is deterministic and has no edge cases: the function declaration must appear before its first call site.

---

## Fix

I moved the `Assert-CanonicalPath` function definition above line 10, ahead of all invocations. No logic changed. No behavior changed. The fix was purely structural — reordering existing code so the runtime could find the function when it needed it.

Script updated at: `C:\OPS\Control\Automation\AutoSOC\render-triage-quality-chart.ps1`
Last write time post-fix: `2026-03-23 18:53:24 -05:00`

---

## Validation

I ran the script directly after the fix:

```
EXIT=0
QUALITY_CHART_PNG=C:\OPS\Control\Logs\AutoSOC\Reports\autosoc-triage-quality-trend.png
POINTS_RENDERED=30
```

Exit code zero. Thirty data points rendered. The chart artifact was produced at 104,564 bytes — the first successful render since the regression was introduced.

I then triggered the parent pipeline (`\AutoSOC-Pipeline`) manually and confirmed end-to-end success:

- Last Run Time: `3/23/2026 9:50:06 PM`
- Last Result: `0` (success)
- Chart artifact timestamp updated: `2026-03-23 22:09:04 -05:00`
- Downstream steps (reconciliation, coverage check) ran to completion

The fix held through a manual trigger and was documented in the running log and session log before closing.

**Note on the subsequent scheduled run:** The 10:09 PM scheduled run returned exit code `-1073741510`, indicating abnormal termination. This is an open item. It does not invalidate the hotfix — the chart step continued rendering successfully in runtime log evidence after the fix — but the scheduler exit code warrants a separate investigation of what terminated the process at that specific boundary.

---

## Outcome

The triage quality chart is rendering again. The pipeline now has a working visual record of escalation rate trends over time, which is one of the primary health indicators for the AutoSOC system. A regression that had been silently degrading pipeline output is resolved.

Total time from symptom to validated fix: one focused session.

---

## What This Demonstrates

I don't escalate before I diagnose. The error message told me exactly what was wrong — I read it, identified the structural cause, applied the minimum necessary change, and validated against real execution output before calling it done.

The open item on the 10:09 PM run is documented, not papered over. I closed what I could prove was fixed and flagged what still needs investigation. That's the difference between resolving an incident and resolving your discomfort with an incident.

---

*Date: 2026-03-23 | Environment: Windows 11 home lab, PowerShell 7, Windows Task Scheduler | System: AutoSOC (Wazuh-backed SOC pipeline)*
