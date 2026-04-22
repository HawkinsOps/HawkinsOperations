# Wazuh Honeypot Proof Pipeline

The honeypot proof pipeline runs on the private Wazuh manager and publishes only sanitized artifacts.

## Pipeline flow

1. `/opt/hawkinsops/bin/export_honeypot_proof.sh`
- Reads `/var/ossec/logs/alerts/alerts.json`
- Filters `agent.name == "[REDACTED_HOST]"`
- Exports only: `ts`, `agent`, `rule.id`, `rule.level`, `rule.desc`, `has_srcip`
- Writes metadata artifact: `latest.meta.json` (`generated_utc`, `exported_count`, `agent_name`, `last_rule_id`)
- Writes:
  - `proof/wazuh/honeypot/latest.json`
  - `proof/wazuh/honeypot/latest.md`

2. `/opt/hawkinsops/bin/publish_proof_to_github.sh`
- Syncs sanitized artifacts to:
  - `proof/wazuh/honeypot/`
  - `site/proof/wazuh/honeypot/`
- Commits only when changes exist
- Pushes with deploy key (`/root/.ssh/hawkinsops_proof_deploy`)

3. `/opt/hawkinsops/bin/install_proof_cron.sh`
- Installs root cron every 15 minutes:
  `*/15 * * * * /opt/hawkinsops/bin/export_honeypot_proof.sh && /opt/hawkinsops/bin/publish_proof_to_github.sh >> /var/log/hawkinsops_proof_pipeline.log 2>&1`

## Verification

1. Check timestamp and count in `proof/wazuh/honeypot/latest.md`.
2. Review commit history for updates:
`https://github.com/raylee-hawkins/HawkinsOperations/commits/main/proof/wazuh/honeypot`
3. Reproduce on the Wazuh manager:

```bash
/opt/hawkinsops/bin/export_honeypot_proof.sh
/opt/hawkinsops/bin/publish_proof_to_github.sh
```

