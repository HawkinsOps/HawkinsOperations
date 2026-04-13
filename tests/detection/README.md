# Detection Unit Tests — Layer 1 (rule-firing harness)

This directory encodes the contract **"when this event arrives, this rule must fire."**

It is the ground truth for Wazuh rule logic in this repository. A rule change that breaks a declared fixture fails CI. A rule that has no fixture is an untested rule.

## What this is not

- Not an end-to-end test. This layer does not execute real attacker behavior. It feeds canned log text through `wazuh-logtest` on the manager and asserts the expected rule fires.
- Not a replacement for telemetry integration testing. A rule that passes here can still fail in production if the agent, decoder path, or upstream transport is broken. That is Layer 2's job (Atomic Red Team against a live lab agent, alert asserted in Splunk).
- Not currently hermetic. Phase 1 runs against the deployed Wazuh manager over SSH; Phase 2 will run against an ephemeral docker-based `wazuh-manager` container built from the in-PR bundle.

## Layout

```
tests/detection/
  README.md                  (this file)
  fixtures/
    <ATTACK_ID>/             e.g. T1098, T1190, T1059.001
      <rule_id>_<slug>/
        event.log            raw log text fed to wazuh-logtest via stdin
        expected.yml         assertion contract
```

Example:

```
tests/detection/fixtures/T1098/100066_sudo_password_change/
  event.log
  expected.yml
```

## The `event.log` file

Raw log text, exactly as the Wazuh agent would ship it. Multi-line events are allowed; trailing newline is stripped before piping to `wazuh-logtest`. Use the same format the agent emits — e.g. Apache access log lines for web rules, sudo syslog for sudo rules.

## The `expected.yml` file

```yaml
# Required fields
rule_id: "100066"
level_min: 10                    # the rule must fire at this level OR higher

# Optional assertions (any or all)
mitre_ids:                       # every listed ID must be in rule.mitre.id[]
  - "T1098"
groups_contain:                  # every listed group must appear in rule.groups
  - "account_manipulation"
description_substring: "Privileged account password changed"  # must appear in rule.description

# Optional metadata
note: "sudo passwd root — classic T1098 account manipulation"
```

`rule_id` and `level_min` are required. All other fields are optional and additive — every listed assertion must be satisfied.

## How it runs

1. CI job `verify` checks out the repo.
2. `scripts/verify/run_detection_unit_tests.py` walks `tests/detection/fixtures/**`.
3. For each fixture, the script opens an SSH session to `$WAZUH_HOST` as `$WAZUH_SSH_USER` on port `$WAZUH_SSH_PORT` using key `$WAZUH_SSH_KEY`, pipes `event.log` into `/var/ossec/bin/wazuh-logtest -q`, captures stdout, and parses the Wazuh match output.
4. Each declared assertion in `expected.yml` is checked. Any mismatch fails the test.
5. A machine-readable summary is written to `proof/detection_unit_tests/latest.json` and a human-readable summary to `proof/detection_unit_tests/latest.md`. Both are uploaded as workflow artifacts.
6. The step exits non-zero if any fixture fails.

## Adding a new fixture

1. Decide the ATT&CK technique ID the rule targets (look at the `<mitre>` block in the rule XML).
2. Create `tests/detection/fixtures/<ATTACK_ID>/<rule_id>_<slug>/`.
3. Drop an `event.log` that should trigger the rule. Real test examples are often in the comment block at the bottom of each rule file in `content/detection-rules/wazuh/rules/`.
4. Write `expected.yml` describing what must be true when the rule fires.
5. Run the harness locally if you have SSH to the manager, or open a PR and let CI run it.

## Phase 2 (not in this PR)

- Swap SSH-to-live-manager for ephemeral `wazuh/wazuh-manager` docker container built from the in-PR bundle. Hermetic, pre-deploy, faster.
- Atomic Red Team integration tests on a lab agent, assertions against Splunk.
- DRAPE-style scoring (reliability × precision) emitted as coverage JSON.
- MITRE ATT&CK Navigator heatmap rendered on the site from the coverage JSON.
