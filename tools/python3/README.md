# Python 3 Utility Samples

This folder contains Python 3 automation tools built for real SOC and detection engineering workflows.

## Tools

### `normalize_sigma_titles.py`
Normalizes Sigma rule title lines (`title:`) into consistent sentence case.
Standard library only.

```bash
python tools/python3/normalize_sigma_titles.py \
  --in tools/python3/samples/sigma_input.yml \
  --out tools/python3/samples/sigma_output.yml
```

```bash
python -m unittest tools.python3.tests.test_normalize_sigma_titles
```

Sample files: `tools/python3/samples/`

---

### `wazuh_proof_pack.py`
Collects high-severity Wazuh alerts (level >= 10 by default) and builds a timestamped proof pack.

Outputs per run:
- `alerts/high_severity_alerts.jsonl` — raw alert records
- `alerts/high_severity_summary.csv` — analyst-friendly summary with MITRE category
- `incident_action_log.md` — action checklist mapped to response playbooks per rule ID
- `evidence/host_context.txt` — host and wazuh manager status snapshot
- Append-only `high_severity_alerts.log` and `incident_tracker.csv` across runs

State file tracks last-seen alert so repeated runs process only new events.

```bash
# Run on Wazuh manager (Linux)
python3 tools/python3/wazuh_proof_pack.py
python3 tools/python3/wazuh_proof_pack.py --severity 12 --lookback-lines 100000 --outdir /tmp/sprint_pack
```

Response playbook mappings live in `~/wazuh_response_map.json` (auto-created from defaults on first run). Rule IDs covered by default: 60204, 100053, 100055, 100062, 100075.

---

### `generate_detection_report.py`
Validates expected detections against `alerts.json` and produces a Markdown report.

Reads an `expected_detections.yaml` spec (same format as `content/projects/lab/wazuh-detection-harness/`) and checks each test for a matching alert in the lookback window. Outputs a pass/fail table with alert ID, timestamp, and agent.

```bash
# Run on Wazuh manager (Linux)
python3 tools/python3/generate_detection_report.py \
  --expected /home/raylee/soc/expected_detections.yaml \
  --out /home/raylee/soc/report.md
```

---

### `xml4688_parser.py`
Parses raw Windows Security XML event text and extracts:

- `EventID`
- `NewProcessName`
- `ParentProcessName`
- `CommandLine`

Outputs JSON payload with event list and top process-launch summary.

```bash
python tools/python3/xml4688_parser.py \
  --in tools/python3/samples/windows_security_4688_sample.xml \
  --out-json output/windows_security_4688_parsed_03-19-2026.json \
  --top 10
```

```bash
python -m unittest tools.python3.tests.test_xml4688_parser
```


