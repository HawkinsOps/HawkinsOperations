# Build Steps

Record the actual install and first-ingest steps here as Phase 3 progresses.

Guardrails:
- Keep commands sanitized for public-repo safety.
- Do not store credentials, tokens, or private host details.

## Post-install baseline

After first boot and login as `raylee`:

```bash
hostnamectl --static
whoami
ip -brief address
```

Expected:
- hostname should resolve to `HO-SPLUNK-01`
- logged-in user should be `raylee`

## SSH key import

If the installer did not import an SSH key, add it from the VM console:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys
```

Paste the public key, then press Enter and `Ctrl+D`, then run:

```bash
chmod 600 ~/.ssh/authorized_keys
```

## Reachability checks

From the VM:

```bash
systemctl status ssh --no-pager
ss -ltn
```

Expected:
- SSH service active
- port `22` listening

## Splunk verification

If Splunk is already installed:

```bash
test -x /opt/splunk/bin/splunk && /opt/splunk/bin/splunk version
systemctl status splunk --no-pager
ss -ltn | grep -E ':(8000|8088|8089|9997) '
```

Expected minimum evidence:
- Splunk binary present
- Splunk service state visible
- at least the management or web ports listening if the service is active

## First-ingest direction

Preferred first source for Phase 3:
- primary Windows endpoint telemetry

Minimum honest first-ingest proof:
- one live source reaches Splunk
- events are indexed
- events are searchable
- one or two investigation pivots work against real data

Current public-safe proof artifacts:
- `content/lab/proxmox/vms/104/splunk/exports/SPLUNK_LIVE_WINDOWS_INGEST_VALIDATION_2026-03-17.md`
- `content/lab/proxmox/vms/104/splunk/exports/SPLUNK_EVENTID_4688_VALIDATED_PIVOTS_2026-03-17.md`
