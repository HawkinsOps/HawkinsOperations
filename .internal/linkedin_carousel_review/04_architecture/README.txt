SLIDE 4 — ARCHITECTURE / PIPELINE FLOW
========================================

PURPOSE: Show the automated SOC pipeline is real, not theoretical.
         Key message: "I built and operated a live detection pipeline."
         Recruiter takeaway: ops discipline + automation + system design.

CANDIDATE A (RECOMMENDED PRIMARY)
  File: ARCHITECTURE.md
  Section: "## Deployment Architecture (Wazuh Example)" — the 4-step flow
  Use:  Recreated cleanly in PowerPoint/Canva as a 4-box pipeline diagram
  Why:  Shows the exact repo→build→deploy→verify pipeline in clean prose.
        Each step has a labeled code block:
          1. Development (content/detection-rules/wazuh/rules/*.xml)
          2. Build Phase (scripts/build-wazuh-bundle.ps1)
          3. Deployment (dist/wazuh/local_rules.xml → scp → /var/ossec)
          4. Verification (tail ossec.log → validate rule counts)
        This is the pipeline flow diagram. Recreate as 4 connected boxes.
  Risk:  Raw markdown has code blocks — needs visual translation, not screenshot.

CANDIDATE B
  File: AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md
  Section: "## Pipeline Components" (6 numbered components)
  Use:  Copy source — extract component list as slide bullets
  Why:  Names all 6 pipeline scripts (poll-alerts.py, triage.py, redact.py,
        assemble-pack.py, create-pr.py, run-pipeline.py) with clear roles.
        Shows the full ingest→triage→redact→pack→publish flow.
        Demonstrates automated security operations architecture.
  Risk:  6 components is a lot for one slide. Consolidate to 3-4 stages visually.

CANDIDATE C
  File: ARCHITECTURE.md
  Section: "## Quick Validation (90-Second Recruiter Path)"
  Use:  Backup only — this is more of a proof path than architecture
  Why:  Good for a reviewer CTA but not a pipeline flow diagram.

REFERENCE SCREENSHOTS
  autosoc-desktop.png — rendered AutoSOC page from Playwright
  proof-desktop-final.png — rendered proof page from Playwright
  These show the live public site. Use as background or inset visual only.

CAPTURE INSTRUCTION
  Open ARCHITECTURE.md. Find "## Deployment Architecture (Wazuh Example)".
  Extract the 4-step flow (Development → Build Phase → Deployment → Verification).
  Re-create in Canva as horizontal 4-box pipeline with arrows between each box.
  Label each box with the step name. Add the key tool/file reference beneath each.
  Keep technical text minimal — one line per box is enough for LinkedIn.
