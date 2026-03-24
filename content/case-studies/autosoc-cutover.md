# Case Study: AutoSOC Infrastructure Cutover
**Migrating a Production SOC Pipeline to a Canonical Root Without Downtime**

---

## The Problem

My home lab SOC pipeline — AutoSOC — had grown across two legacy roots: `C:\RH\OPS\` and `C:\Operations\`. Scripts, configs, scheduled tasks, and log output were split between them. This created real operational risk: any path assumption in one location could silently break something referencing the other. As the system scaled, so did the surface area for that failure. The fix wasn't optional — it was a prerequisite for the system being trustworthy long-term.

The goal: consolidate everything under a single canonical root (`C:\OPS\`) and prove the cutover was clean before declaring it complete.

---

## The Approach

I didn't want to do this as a manual drag-and-drop. The risk of leaving a stale reference behind — one script still pointing at `C:\RH\OPS\`, one scheduled task still running from the wrong path — is exactly the kind of silent failure that's hard to catch until something breaks at 2am.

So I built the cutover around a preflight gate: a validation script that scanned the environment for any remaining legacy path references before the cutover was declared complete. The rule was simple — if the legacy reference file count wasn't zero, the cutover wasn't done.

---

## Execution

I retargeted five Windows Task Scheduler tasks to point at the canonical `C:\OPS\` paths:

| Task | New Target |
|---|---|
| `\AutoSOC-Pipeline` | `C:\OPS\Control\Automation\AutoSOC\run-pipeline.py` |
| `\OPS_AutoSOC_Contract_Daily` | `C:\OPS\Control\Automation\AutoSOC\run-autosoc-contract-task.ps1` |
| `\AutoSOC-March-Progress-12h` | `C:\OPS\Control\Automation\AutoSOC\refresh-march-soc-progress.ps1` |
| `\OPS_DriftHotspots_Daily` | `C:\OPS\Control\Automation\Maintenance\run-drift-hotspots-task.ps1` |
| `\AutoSOC_SystemJournal_March_2026` | `C:\OPS\Control\Automation\SystemJournal\run_system_journal_task.ps1` |

All five tasks run as my user account, with no elevated permission shortcuts — if it doesn't work under normal runtime conditions, I want to know immediately.

Scripts were updated to use `assert_not_legacy_path()` guards inside `common.py`, so any future code that accidentally references a legacy root will fail loudly at startup rather than silently degrading.

---

## Validation

With the retargeting done, I ran the preflight script. The output:

```
CHECK CONFIG_ENV           exists=True
CHECK CONFIG_POLICY        exists=True
CHECK CONFIG_KNOWN_FPS     exists=True
CHECK CONFIG_AGENT_INVENTORY exists=True
CHECK OUTPUT_ROOT          exists=True
CHECK LOGS_ROOT            exists=True
CHECK LEGACY_REFERENCE_FILES count=0
RESULT=PASS
```

Legacy reference file count: **zero**. The preflight gate cleared.

I then ran the contract pipeline manually against the new canonical paths and confirmed it completed successfully end-to-end — build manifest, pre-validation, index build, post-validation — all steps returning `STEP_OK`. Runtime logs and operator card output were writing to `C:\OPS\` roots. The heartbeat snapshot confirmed the latest pipeline run returned `SUCCESS`.

A signed cutover proof document was generated at `C:\OPS\_Canonical\CUTOVER_PROOF_2026-03-23.md` with the full preflight output, task scheduler configuration dump, heartbeat snapshot, and contract log tail. The cutover was declared complete: `CUTOVER_READY=YES`.

---

## Outcome

The AutoSOC pipeline — which processes a live queue of security alerts from a Wazuh SIEM across multiple hosts — now runs entirely from a single canonical root. There are no legacy path dependencies in the scheduler, the scripts, or the runtime output. The system is easier to reason about, easier to back up, and easier to hand off. If something breaks, the path to root cause is shorter.

The cutover took one working session. The proof artifact documents it permanently.

---

## What This Demonstrates

I don't do infrastructure changes on faith. I build the gate first, run the migration through it, and don't declare done until the evidence says so. The preflight validator, the zero-reference scan, the signed proof document — none of that was required. I did it because that's how you know a change actually landed versus how you hope it did.

That distinction matters in any environment where the system is expected to keep working after you walk away from it.

---

*Date: 2026-03-23 | Environment: Windows 11 home lab, Python 3.14, PowerShell 7, Windows Task Scheduler | System: AutoSOC (Wazuh-backed SOC pipeline)*
