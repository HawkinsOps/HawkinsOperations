# Draft Post: Auditing and Tightening a Splunk Detection Library

**Status:** Draft — 2026-03-29

---

I ran a full audit of my HawkinsOps Splunk detection library this week. Eight SPL files covering execution, discovery, persistence, credential access, defense evasion, lateral movement, collection/exfiltration, and privilege escalation. What I found was a set of functional-but-noisy queries that would generate real analyst pain in production.

Here is what was loose and what I changed.

---

## The core problem with threshold-based detection

Several queries used a pattern like this:

```spl
| stats count by Computer, User
| where count > 3
```

The issue: no time window. That `count > 3` applies across the entire search timeframe — which in production is often 24 hours. `whoami.exe` running 4 times across 24 hours is baseline noise. `whoami.exe` running 4 times in one hour is recon. The signal is in the rate, not the total.

Fix: add `| bin _time span=1h` before the stats call. Now you get per-hour bucketed counts, and the threshold means something.

This touched Whoami Execution (T1033), Process Discovery (T1057), RDP Logon Activity (T1021.001), Remote File Copy via SMB (T1570), Ransomware File Encryption (T1486), and Kerberoasting (T1558.003).

---

## Process Injection was basically a catch-all

The EventCode=8 (CreateRemoteThread) query had two exclusions:

```spl
| where NOT match(SourceImage, "(?i)^C:\\Program Files")
| where NOT match(TargetImage, "(?i)^C:\\Program Files")
```

In a real environment, EDR agents, AV engines, and the Elastic agent all use cross-process memory operations as part of normal operation. `MsMpEng`, `SentinelOne`, `cbdefense`, `elastic-agent`, `sysmon` — all of these would fire this rule constantly.

The original query's exclusion only covered binaries in `C:\Program Files`. A process running from `C:\Windows\System32` that injects into another process from `C:\Windows\System32` was still firing. That is almost entirely EDR and Windows OS behavior.

Added explicit exclusions for the most common security tool processes and system targets like `svchost`, `RuntimeBroker`, `SearchHost`.

---

## DNS tunneling threshold was too sensitive

```spl
index=dns query_length>50
| stats count by query, src_ip
| where count > 10
```

`query_length>50` fires on any DNS query over 50 characters. CDN providers, cloud services, and Microsoft telemetry routinely generate queries in the 80-120 character range. A corporate endpoint running Microsoft 365 would produce hundreds of these per hour.

Changes:
- Raised threshold to `query_length>100`
- Added exclusions for known CDN/update domains (`microsoft.com`, `akamaiedge.net`, `cloudfront.net`, `amazonaws.com`)
- Changed stats to track `dc(query)` (distinct query count) alongside total count, per 10-minute window
- Threshold now requires both count and unique_queries to be elevated — this pattern is characteristic of tunneling

---

## Encoded PowerShell was missing AI tool exclusions

Coming directly out of the [codex hunt case study](/case-study-splunk-codex-hunt): the OpenAI Codex CLI spawns `pwsh.exe` with encoded command strings as part of its normal operation loop. Any environment running AI coding tools will generate this signal continuously.

Added exclusion for parent processes matching `codex.exe`, `vscode`, `cursor.exe`, and `node.exe` — the runtime environments where AI-assisted coding tools execute.

The exclusion is path-scoped, not behavior-class-scoped. It does not suppress all encoded PowerShell from non-standard parents. It suppresses encoded PowerShell that traces to a known, versioned tool path.

---

## Credential access exclusions were incomplete

The LSASS access query (EventCode=10, T1003.001) had these exclusions:

```
wmiprvse, taskmgr, MsMpEng, procexp
```

Missed: `ATPService`, `SenseIR`, `cbdefense`, `elastic-agent`, `falcon-sensor`, `SentinelOne`. Any endpoint with a real EDR would fire this rule on every boot. Added the full set.

Also added `GrantedAccess=0x1fffff` (PROCESS_ALL_ACCESS) to the LSASS access detection — this is the most permissive access mask and was the one access level missing from the original list.

For Kerberoasting (T1558.003), added `unique_spns > 3` to the threshold condition. A single request for an RC4-encrypted ticket is borderline signal. Multiple distinct SPNs requested in the same hour from the same IP is the actual roasting pattern.

---

## Cleanup: markdown fences in `.spl` files

All eight files had ` ``` ` code fence markers at the top and bottom. These are `.spl` files. They should contain SPL, not markdown. Stripped.

---

## What stayed the same

Detection logic that was already precise:
- **Mimikatz keyword matching** — the command strings are specific enough that no exclusions were needed
- **Volume Shadow Copy deletion** — `vssadmin delete shadows` from any context is worth alerting
- **UAC bypass registry keys** — `ms-settings\shell\open\command` modification is unambiguously suspicious
- **WMI event subscription** (EventCode 19/20/21) — rare enough in production that all events are signal

---

## The pattern

Most of the loose queries shared a structure: correct detection logic wrapped in inadequate noise suppression. The signal was right, the exclusions were minimal.

In a real SOC environment, rules that generate constant false positives get tuned down or disabled. A rule that fires on every Defender scan or every CDN DNS query trains analysts to ignore that rule class. The goal of tightening is not to make rules miss things — it is to make the alerts that do fire actionable by default.

Every exclusion added in this pass is:
1. Scoped to a specific, named process or domain
2. Documented with a reason in the SPL comment
3. Does not suppress the detection class — only the verified-benign variant

---

*Detection library: [github.com/raylee-hawkins/HawkinsOperations/tree/main/content/detection-rules/splunk](https://github.com/raylee-hawkins/HawkinsOperations/tree/main/content/detection-rules/splunk)*
