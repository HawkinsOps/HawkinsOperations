# Splunk Live Windows Ingest Validation

Date: 2026-03-17
Scope: Phase 3 minimum-evidence checkpoint
System: `HO-SPLUNK-01`
Evidence type: sanitized validation summary

## Claim supported by this artifact

Splunk operates in the lab as an investigation layer with live Windows telemetry ingest and validated SPL pivots against real Event ID `4688` process-creation data.

## What was validated

- A dedicated Splunk Enterprise `10.0.2` instance is running on the lab Splunk VM.
- Live Windows Security telemetry is searchable in Splunk.
- Searches against `index=windows sourcetype=XmlWinEventLog:Security` return current events.
- Real `EventID=4688` process-creation events are present.
- Investigation pivots using extracted `NewProcessName`, `CommandLine`, and `ParentProcessName` fields return usable results against live data.

## Sanitized evidence summary

Reviewed screenshot set:
- `Screenshot 2026-03-17 193413.png`
- `Screenshot 2026-03-17 193428.png`
- `Screenshot 2026-03-17 193445.png`
- `Screenshot 2026-03-17 190701.png`
- `Screenshot 2026-03-17 212611.png`
- `Screenshot 2026-03-17 212918.png`
- `Screenshot 2026-03-17 212939.png`
- `Screenshot 2026-03-17 212946.png`

Observed progression:
- Initial `spath` testing confirmed live Windows Security events were present.
- A `spath` attempt to count by `NewProcessName`, `CommandLine`, and `ParentProcessName` returned zero results, indicating those fields were not usable in that form for this sourcetype.
- Follow-up searches switched to `rex` extraction from raw XML and produced stable process-parent pivot output.
- Narrowed searches for `NewProcessName="*pwsh.exe"` returned live results with parent-child relationships suitable for investigation pivots.

## Minimum live-ingest proof points

- Search scope used live data, not static samples.
- Results showed Windows Security `EventID=4688`.
- Results exposed host, source, and sourcetype metadata in the search UI.
- Result sets included analyst-usable process and parent-process relationships.

## Boundaries

This artifact proves:
- live Windows telemetry ingest exists in Splunk
- the data is searchable
- Event ID `4688` pivots are validated against real data

This artifact does not prove:
- a full alert-to-investigation workflow package
- multi-source ingest maturity
- a completed dashboard or saved-search library
- end-to-end SOC case handling in Splunk

## Public-safe notes

- Internal addresses are intentionally omitted.
- Raw screenshots are not committed here because the originals contain private UI details.
- This file is the reviewer-safe summary artifact for the underlying validation session.
