# Splunk Event ID 4688 Validated Pivots

Date: 2026-03-17
Scope: reviewer-safe SPL examples validated against live Windows telemetry

## Validated dataset

- index: `windows`
- sourcetype: `XmlWinEventLog:Security`
- event family: Windows Security process creation (`EventID=4688`)

## Pivot 1: confirm event family is present

```spl
index=windows sourcetype=XmlWinEventLog:Security
| search EventID=4688
| stats count by EventID
| sort - count
```

Use:
- confirm live process-creation data is present
- verify that the target event family is actively searchable

## Pivot 2: extract process, command line, and parent process

```spl
index=windows sourcetype=XmlWinEventLog:Security
| rex field=_raw "<EventID>(?<EventID>\d+)</EventID>"
| rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
| rex field=_raw "<Data Name='CommandLine'>(?<CommandLine>[^<]*)</Data>"
| rex field=_raw "<Data Name='ParentProcessName'>(?<ParentProcessName>[^<]+)</Data>"
| search EventID=4688
| stats count by NewProcessName CommandLine ParentProcessName
| sort - count
```

Use:
- generate investigation-ready process-parent summaries
- compare expected versus unexpected parent-child relationships

## Pivot 3: narrow to PowerShell execution paths

```spl
index=windows sourcetype=XmlWinEventLog:Security
| rex field=_raw "<EventID>(?<EventID>\d+)</EventID>"
| rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
| rex field=_raw "<Data Name='ParentProcessName'>(?<ParentProcessName>[^<]+)</Data>"
| search EventID=4688 NewProcessName="*pwsh.exe"
| where NOT like(ParentProcessName, "%explorer.exe%")
  AND NOT like(ParentProcessName, "%cmd.exe%")
  AND NOT like(ParentProcessName, "%services.exe%")
| stats count by NewProcessName ParentProcessName
```

Use:
- isolate scripted or automated PowerShell launches
- separate interactive launches from automation-driven execution

## Validated observations

- Live results included `pwsh.exe` launched from automation-linked parents such as `python.exe` and `codex.exe`.
- Live results also included Splunk Universal Forwarder process activity associated with `splunkd.exe`.
- The successful pivot path depended on raw XML extraction with `rex`, not the earlier `spath` attempt used during exploration.

## Boundaries

These SPL examples are validated as live investigation pivots.
They are not represented here as production detections, notable-event content, or a full analyst-case workflow.
