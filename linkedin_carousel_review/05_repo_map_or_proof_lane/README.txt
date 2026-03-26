SLIDE 5 — PROOF LANE (chosen over repo map)
============================================

DECISION: Proof lane wins over repo map.
REASON:   A repo map (directory tree) is noise to most recruiters.
          A proof lane says: "I designed this so you can validate it in 5 minutes."
          That is a much higher-trust signal. Repo map is backup reference only.

PURPOSE: Close the carousel. Give the recruiter a clear next action.
         Key message: "Here is exactly how to verify everything I just showed you."

CANDIDATE A (RECOMMENDED PRIMARY)
  File: START_HERE.md
  Section: "## 5-Minute Proof Path" (numbered list of 5 steps)
  Use:  Recreated cleanly in PowerPoint/Canva as a numbered-step slide
  Why:  Five clear steps. Recruiter-optimized language.
        Steps include:
          1. PROOF_PACK/PROOF_INDEX.md
          2. PROOF_PACK/VERIFIED_COUNTS.md
          3. content/detection-rules/INDEX.md
          4. content/incident-response/INDEX.md
          5. docs/execution/AUTOSOC_OPERATIONS_RUNBOOK_03-02-2026.md
        Ends with a CTA to reproduce counts via PowerShell.
        This is the most recruiter-actionable closing slide possible.
  Risk:  File paths on screen look technical — use plain-English step descriptions
         in the slide, cite file paths in presenter notes only.

CANDIDATE B
  File: PROOF_INDEX.md
  Section: "## Suggested Review Path" (5-step numbered list)
  Use:  Backup / copy source
  Why:  Almost identical to START_HERE.md but shorter.
        Works as a secondary source if START_HERE needs trimming.
  Risk:  Very sparse. Better as a supplement than a standalone.

CANDIDATE C
  File: README_full.md (repo root — not copied here, see 02_choose_your_path/)
  Section: "## Quick Validation (90-Second Recruiter Path)" (in ARCHITECTURE.md)
  Use:  Backup — 90-second validation framing is strong recruiter language
  Risk:  Content is in ARCHITECTURE.md not README. Slight disconnect.

REFERENCE SCREENSHOT
  01_wazuh_overview_dashboard.png — live Wazuh dashboard with 7 agents visible
  Use this as a background or inset to add visual credibility.
  This is a real production screenshot with real alert data (redacted).

CAPTURE INSTRUCTION
  Open START_HERE.md. Extract "## 5-Minute Proof Path" section (5 numbered items).
  Re-create in Canva as a vertical numbered list:
    1. Check the evidence layout → PROOF_PACK/PROOF_INDEX.md
    2. See verified rule counts → PROOF_PACK/VERIFIED_COUNTS.md
    3. Inspect detection coverage → detection-rules/INDEX.md
    4. Review IR catalog → incident-response/INDEX.md
    5. Explore live pipeline → AutoSOC Operations Runbook
  Add CTA at bottom: "Run verify-counts.ps1 to reproduce any count."
  Keep file paths as secondary text, not headline.
