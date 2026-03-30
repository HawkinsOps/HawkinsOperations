# SOC Stack Integration: Wazuh → Splunk + Grafana

**Project:** HawkinsOps Home Lab
**Date:** 2026-03-29
**Environment:** Self-hosted on Proxmox, Ubuntu VMs, LAN + Tailscale overlay
**Status:** Production-ready for lab / portfolio demonstration

---

## Overview

End-to-end integration of a three-tier SOC visibility stack built without managed services, external data lakes, or vendor tooling. Wazuh serves as the detection engine. Splunk ingests alerts as a secondary SIEM with 4.8M events indexed. Grafana visualizes live alert data directly from the OpenSearch backend with four community dashboards active and returning data.

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│  Wazuh Manager  (ho-sr-wm-01 / 192.168.8.231)      │
│  v4.14.4 · 9 agents · OpenSearch 2.x backend       │
│                                                      │
│  /var/ossec/logs/alerts/                            │
│  ├── alerts.json          (live, updated ~30s)      │
│  ├── alerts.log           (live)                    │
│  └── YYYY/Mon/ossec-alerts-DD.{log,json}.gz         │
│                  │                                  │
│       rsync every 5 min (root cron)                 │
│                  │                                  │
│  /mnt/operations/wazuh/alerts/  ──── CIFS ──────────┼──┐
└────────────────────────────────────────────────────┘  │
                                                         │  //192.168.8.254/Operations
┌────────────────────────────────────────────────────┐  │  (SMBv3, rw from Wazuh, ro from Splunk)
│  Splunk Enterprise  (ho-splunk-01 / 192.168.8.248) │  │
│  v10.0.2                                           │  │
│                                                     │  │
│  /mnt/operations/  ◄────────────── CIFS ───────────┼──┘
│       monitor input → index:wazuh                  │
│       4,822,012 events  (Jan–Mar 2026)             │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  Wazuh Indexer  (OpenSearch)  :9200                │
│  Cluster: wazuh-cluster · status: green            │
│  Index pattern: wazuh-alerts-4.x-*                 │
│  38,090 alerts last 7 days                         │
│                  │                                  │
│        Elasticsearch datasource (TLS, basicAuth)   │
│                  │                                  │
│  Grafana  (HO-GRAFANA-01 / 192.168.8.134:3000)     │
│  v12.3.3 · 4 Wazuh dashboards active               │
│  WAZUH SUMMARY · MITRE ATT&CK ·                    │
│  SYSTEM VULNERABILITIES · FIM                      │
└────────────────────────────────────────────────────┘
```

---

## What Was Built / Fixed

### Discovery (Phase 1)

Full environment audit performed via REST APIs and paramiko-based SSH. Key findings:

| Component | Pre-work State | Finding |
|-----------|---------------|---------|
| Wazuh Manager API | Unknown | Working — v4.14.4, 9 agents, JWT auth |
| OpenSearch :9200 | Unknown | Running — but admin password stale in secrets file |
| Splunk wazuh index | Unknown | 4.6M events — data stale 9 days |
| Grafana datasources | Unknown | 4 configured, 0 healthy — all 401 |
| Grafana dashboards | Unknown | 0 Wazuh dashboards imported |
| Splunk → Wazuh path | Unknown | NFS/CIFS mount, not syslog forwarding |
| SSH from workstation | Unknown | Blocked — keys not in authorized_keys on VMs |

### Decision (Phase 2)

**Architecture chosen: no new infrastructure.** Every component was already in place. The work was configuration repair and pipeline restoration.

Rejected paths:
- **Syslog forwarding** — the CIFS mount already provides richer, structured ingestion including JSON archives. Syslog would be unstructured and lose historical data.
- **Universal Forwarder** — unnecessary when a shared filesystem gives the same data with zero agent overhead.
- **Hadoop / virtual indexes / HEC** — out of scope, added complexity with no benefit.

### Implementation (Phase 3–4)

**OpenSearch credential reset:**
Used `wazuh-passwords-tool.sh --change-all` to rotate all indexer credentials. Backed up internal_users to `/etc/wazuh-indexer/internalusers-backup/`. Restarted wazuh-dashboard, wazuh-manager, and filebeat. Confirmed cluster health green via REST.

**Grafana datasource repair:**
Patched datasource ID 2 (`Wazuh-OpenSearch`, elasticsearch plugin) via Grafana REST API with the new admin credential. Confirmed health: `Elasticsearch data source is healthy`. Used `PUT /api/datasources/2` with `secureJsonData.basicAuthPassword`.

**Dashboard import:**
Fetched current community dashboards from grafana.com (IDs 22448, 22449, 22451, 23072). Mapped `DS_WAZUH` input to the working datasource UID. All four imported successfully.

**Splunk pipeline restoration:**
Root-caused stale data: `rsync` from `/var/ossec/logs/alerts/` to the CIFS share stopped running on 2026-03-19. The mount itself was healthy (SMBv3, 96G share, 64G free). Ran catch-up rsync (48 missing files synced), then installed a root crontab entry on the Wazuh VM:

```
*/5 * * * * /usr/bin/rsync -a /var/ossec/logs/alerts/ /mnt/operations/wazuh/alerts/ \
    >> /var/log/wazuh_alert_sync.log 2>&1 # wazuh-splunk-sync
```

**SSH access:**
Installed `id_ed25519.pub` from HO-WE-01 into `authorized_keys` on both Wazuh VM and Splunk host via paramiko (password auth bootstrap). Both hosts are now accessible via key.

---

## Validation

### Grafana

- Datasource health: `OK — Elasticsearch data source is healthy`
- Live query result: **38,090 alerts in last 7 days**
- Daily breakdown:

| Date | Alert Count |
|------|-------------|
| 2026-03-23 | 3,470 |
| 2026-03-24 | 3,351 |
| 2026-03-25 | 5,704 |
| 2026-03-26 | 11,587 |
| 2026-03-27 | 8,102 |
| 2026-03-28 | 2,520 |
| 2026-03-29 | 3,319 |
| 2026-03-30 | 37 (partial day) |

- Active dashboards: WAZUH SUMMARY, WAZUH - MITRE ATT&CK, WAZUH - SYSTEM VULNERABILITIES, WAZUH - FIM

### Splunk

- Index event count: **4,822,012** (up from 4,610,226 before restoration)
- Latest ingested source: `/mnt/operations/wazuh/alerts/2026/Mar/ossec-alerts-30.log`
- Data covers: January 2026 – present

**Useful SPL queries:**

```splunk
# Alert volume by severity level (last 24h)
index=wazuh | spath rule.level | where isnum(rule.level)
| eval severity=case(rule.level>=12,"critical", rule.level>=8,"high",
                     rule.level>=4,"medium", true(),"low")
| timechart span=1h count by severity

# Top alerting agents
index=wazuh | spath agent.name
| stats count by agent.name
| sort -count | head 10

# Rule description lookup for recent alerts
index=wazuh | spath rule.description | spath rule.level
| where rule.level >= 8
| table _time, agent.name, rule.description, rule.level
| sort -_time | head 20
```

### OpenSearch / Wazuh Indexer

```bash
# Cluster health
curl -sk -u admin:<password> https://192.168.8.231:9200/_cluster/health | python3 -m json.tool

# Alert count in current index
curl -sk -u admin:<password> \
  "https://192.168.8.231:9200/wazuh-alerts-4.x-$(date +%Y.%m.%d)/_count"

# Most active rule IDs today
curl -sk -u admin:<password> \
  -H 'Content-Type: application/json' \
  -d '{"size":0,"aggs":{"rules":{"terms":{"field":"rule.id","size":10}}}}' \
  "https://192.168.8.231:9200/wazuh-alerts-4.x-$(date +%Y.%m.%d)/_search"
```

---

## Rollback

| Change | Rollback |
|--------|----------|
| OpenSearch password rotation | Restore from `/etc/wazuh-indexer/internalusers-backup/` on Wazuh VM; re-run `wazuh-passwords-tool.sh` with old hash |
| Grafana datasource password | `PUT /api/datasources/2` with previous password |
| Dashboard imports | `DELETE /api/dashboards/uid/<uid>` for each imported dashboard |
| rsync cron | `sudo crontab -e` on Wazuh VM; remove the `# wazuh-splunk-sync` line |
| SSH authorized_keys | Remove the `raylee@HO-WE-01` line from `~/.ssh/authorized_keys` on Wazuh and Splunk hosts |

---

## Technical Environment

| Host | Role | OS | IP |
|------|------|----|----|
| ho-sr-wm-01 | Wazuh Manager + Indexer + Dashboard | Ubuntu 22.04 | 192.168.8.231 (LAN) / 100.x.x.x (Tailscale) |
| ho-splunk-01 | Splunk Enterprise 10.0.2 | Ubuntu 22.04 | 192.168.8.248 |
| HO-GRAFANA-01 | Grafana 12.3.3 | Ubuntu | 192.168.8.134 |
| HO-WE-01 | Windows 11 workstation | Windows 11 Enterprise | 100.x.x.x (Tailscale) |
| 192.168.8.254 | NAS / file server | — | SMBv3 share host |

---

## Notes

- The `grafana-opensearch-datasource` (native) plugin health check returns "Index not found" despite the index pattern being correctly set. The `elasticsearch` compatibility plugin works without issue. Both target the same OpenSearch backend — use datasource ID 2 (`Wazuh-OpenSearch`) for queries.
- Wazuh API passwords (`wazuh-wui`) were not rotated by `--change-all` (requires `--api` flag with admin credentials). These remain unchanged.
- Prometheus datasource (ID 3) targets localhost:9090 on the Grafana VM — no Prometheus is deployed. Not a dependency for Wazuh/Splunk visibility.
- The rsync cron runs as root to read `wazuh`-owned alert files. Log at `/var/log/wazuh_alert_sync.log` on the Wazuh VM.
