# Wazuh → Splunk Alert Ingestion Pipeline (Verified Data Path)

Date: 2026-03-20
Status: CLOSED — pipeline proven end-to-end

## Claim

Centralized Wazuh alert ingestion into Splunk with verified file-based pipeline and indexed event visibility.

## Context

Wazuh generates alerts on the manager host. The Splunk VM (`[REDACTED_INTERNAL_VM_SPLUNK]`, VM 104) mounts the Operations share over CIFS, which exposes the Wazuh alert files directly at `/mnt/operations/wazuh/alerts/`. Splunk monitors that path and indexes arriving events into `idx=wazuh`.

---

## Evidence

### 1. Persistent mount — fstab entry

```
//[REDACTED_INTERNAL_SHARE_HOST]/Operations  /mnt/operations  cifs  credentials=/etc/samba/[REDACTED_CREDENTIAL_FILE],uid=splunk,gid=splunk,iocharset=utf8,_netdev,x-systemd.automount  0  0
```

Mount type: `cifs`
Mount point: `/mnt/operations`
Source: `//[REDACTED_INTERNAL_SHARE_HOST]/Operations`
Persistence: `_netdev,x-systemd.automount` — survives reboot, auto-remounts

Active mount confirmed:
```
//[REDACTED_INTERNAL_SHARE_HOST]/Operations on /mnt/operations type cifs ... x-systemd.automount
```

### 2. Alert file visibility from mounted share

Files visible on Splunk host at time of verification:

```
/mnt/operations/wazuh/alerts/alerts.json
/mnt/operations/wazuh/alerts/alerts.log
```

These are live Wazuh alert files written by the Wazuh manager and readable by the Splunk VM through the mount — no manual file transfer, no agent required on the alerts path.

### 3. Splunk inputs.conf — monitor configuration

```ini
[splunktcp://9997]

[monitor:///mnt/operations]
index = wazuh
```

Splunk is configured to watch the full mounted share path. Any file written under `/mnt/operations/wazuh/alerts/` is picked up automatically.

### 4. Index confirmation — idx=wazuh bucket created

From `splunkd.log` post-restart:

```
idx=wazuh  hot bucket creation confirmed after ingest activity
```

The `wazuh` index is present in `indexes.conf` and hot bucket creation confirms Splunk received and stored events, not just configured for it.

### 5. Per-source throughput — metrics.log

```
series=/mnt/operations/wazuh/alerts/alerts.json   ev=3241
series=/mnt/operations/wazuh/alerts/alerts.log    ev=155264
```

`ev` = events ingested from each source file. Both paths show real throughput. This is not a configuration test — events moved.

---

## Pipeline summary

```
Wazuh Manager
    │
    │  writes alerts
    ▼
//[REDACTED_INTERNAL_SHARE_HOST]/Operations   (Windows share)
    │
    │  CIFS mount (credentialed, persistent)
    ▼
/mnt/operations/wazuh/alerts/   (on [REDACTED_INTERNAL_VM_SPLUNK])
    │
    │  Splunk monitor input
    ▼
index=wazuh   (hot bucket confirmed, ev=158505 total)
```

---

## What this proves

| Claim | Evidence |
|---|---|
| Mount is persistent | fstab entry + active mount output |
| Alert files are reachable | direct file paths visible on Splunk host |
| Splunk is configured to ingest | inputs.conf monitor stanza |
| Events were actually indexed | metrics.log per-source ev counts |
| Index exists and received data | splunkd.log hot bucket creation |

## What this does not claim

- SPL query output is not included here (blocked in shell context at time of verification)
- Alerting or detection rules on the wazuh index are not scoped to this artifact
- This covers the ingestion path only — investigation pivots are documented separately

---

## Related artifacts

- `SPLUNK_LIVE_WINDOWS_INGEST_VALIDATION_2026-03-17.md` — Windows UF ingest proof
- `SPLUNK_EVENTID_4688_VALIDATED_PIVOTS_2026-03-17.md` — SPL investigation pivots
- `Reports/STACK_STATUS_SPLUNK_WAZUH_HONEYPOT_GRAFANA_2026-03-20.md` — full stack status
