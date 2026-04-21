# HawkinsOperations

**Detection engineering, SOC automation, and proof-backed security operations.**

The public record of the HawkinsOps system: detections, case studies, proof
pack, verification infrastructure, and reviewer paths. This is the current
live portfolio, and it is tied directly to the operational system published
at [hawkinsops.com](https://hawkinsops.com).

A successor architecture is being built in the open at the
[HawkinsOperations organization](https://github.com/HawkinsOperations).
Until that migration lands, this repository and hawkinsops.com remain the
canonical public surfaces.

[![Portfolio](https://img.shields.io/badge/Portfolio-hawkinsops.com-00D4FF)](https://hawkinsops.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](/LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-raylee--hawkins-0A66C2)](https://linkedin.com/in/raylee-hawkins)
[![Successor org](https://img.shields.io/badge/Successor_org-HawkinsOperations-181717?logo=github)](https://github.com/HawkinsOperations)

---

## For reviewers in a hurry

Start at [`START_HERE.md`](/START_HERE.md) if you are a recruiter or hiring
manager. Go to [`PROOF_PACK/VERIFIED_COUNTS.md`](/PROOF_PACK/VERIFIED_COUNTS.md)
if you are a technical reviewer verifying numbers. Everything else in this
README exists to give context to those two destinations.

---

## The thesis

The default pattern for AI in security operations is either hand-waving
about reliability or treating large language models as opaque copilots
attached to a human analyst. Both patterns fail at production scale. The
first produces brittle pipelines that silently drift. The second
underuses the model while still inheriting its unreliability.

This system starts from a different premise. Large language models are
unreliable labor, and unreliable labor is a problem the manufacturing
world solved decades ago through management systems. Intake controls.
Standard work. Verification gates. Escalation paths. Evidence capture.
Regression harnesses. Post-incident review. The IATF 16949 and ISO 9001
frameworks that govern Tier 1 automotive production are, at their core,
systems for extracting reliable output from unreliable inputs. Applied
to an AI triage workforce running against a live SOC pipeline, the same
discipline produces a system that closes the high-confidence cases,
escalates the genuinely suspicious, and leaves an audit trail for every
decision.

That thesis is the reason this portfolio exists and the reason the
metrics below are achievable from a single-operator homelab rather than
a staffed SOC.

---

## System at a glance

| Metric | Value |
|---|---|
| Verified cases triaged | **324,074** |
| Auto-close rate | **88%** |
| Detection coverage | **210** rules across Sigma, Wazuh XML, Splunk SPL |
| Escalation packs produced | **8,574** |
| Agent fleet | **10** Wazuh agents, 8/8 host coverage |
| Infrastructure | **15**-server Proxmox homelab, V100 local inference |

Canonical values are maintained at [hawkinsops.com](https://hawkinsops.com)
and updated on a truth-lock cadence. If a number in this repository
disagrees with the site, the site wins.

Every number above is traceable. The case count comes from the AutoSOC
pipeline's verified ledger. The auto-close rate is computed against that
ledger. The rule count is enumerable across the `content/` and
`wazuh/rules/` directories. The escalation pack count comes from the
generated output tree. None of these figures are estimates.

---

## Reviewer paths

**Recruiters and hiring managers** should start with
[`START_HERE.md`](/START_HERE.md). It is the shortest possible path from
"who is this person" to "here is the work."

**Technical reviewers verifying numbers** should go to
[`PROOF_PACK/VERIFIED_COUNTS.md`](/PROOF_PACK/VERIFIED_COUNTS.md). That
document walks the audit trail behind the metrics table above, with
paths to the raw evidence for each figure.

**Detection engineers** should browse `content/` for the authored rules
and `wazuh/rules/` for the production Wazuh pack. The most recent
detection work lives in both directories and is versioned through the
tagged releases. The tuning work behind the rule pack is documented in
the case studies rather than inline, because the tuning story is usually
more instructive than the final rule.

**Case study readers** should start with the most recent entries under
`content/`. The Wazuh process-telemetry tuning sprint and the AutoSOC
race-condition writeup are the two case studies that best illustrate how
the management-system thesis plays out in practice. Each case study pairs
the written analysis with the underlying rule, log, and evidence bundle.

**Architecture reviewers** should examine `scripts/`, `tools/`, and
`source_of_truth/`. The first two hold the pipeline control logic and
the integrity tooling. The third holds the contracts that keep public
claims traceable back to source data, which is the mechanism that makes
the truth-lock cadence possible rather than aspirational.

---

## What this repository contains

The detection content, case studies, and proof artifacts here are the
product of eight months of focused work on a single-operator homelab
while holding mandatory twelve-hour production supervision shifts. The
system runs on a fifteen-server Proxmox cluster with a V100 handling
local inference for the agentic triage layer. The detection surface
spans Sigma, Wazuh XML, and Splunk SPL, with regression harnesses
verifying that rule edits do not break previously captured true
positives. The SignalFoundry AutoSOC engine consumes alerts, applies the verification
gates, generates escalation packs for the cases that warrant analyst
attention, and writes evidence to a bundle tree that is indexed for
audit.

The case studies in `content/` document specific operational moments,
including a race condition that required detection logic to enforce
ordering guarantees the source data did not provide, and a tuning sprint
that cut process-telemetry noise by roughly ninety percent without
degrading true-positive capture. The case studies are written to be
readable as standalone engineering narratives, not as marketing.

---

## Background

Raylee Hawkins. Self-taught detection engineer. Built this system in
eight months from a manufacturing supervision background running
IATF 16949, ISO 9001, and TISAX quality frameworks on Tier 1 automotive
production floors at Fehrer Automotive and Unipres Alabama, supervising
thirty-plus operators on twelve-hour shifts.

The manufacturing background is the foundation of the thesis rather
than an unrelated prior career. Running a production floor is, in
practice, running a management system against an unreliable workforce.
The workforce in a SOC is now partly synthetic, but the management
discipline transfers directly, and this system is what the transfer
produces.

---

## Where this repository is going

Active work is being migrated into the
[HawkinsOperations organization](https://github.com/HawkinsOperations),
which splits the system into dedicated repositories for detections,
validation, platform, proof, and the successor website. That
organization is under construction and is not yet the right surface
for evaluation. Until the migration completes, this repository stays
live, stays maintained at the level required to keep the public proof
surface honest, and remains the canonical public record.

When the successor system is ready to host operational evidence, this
repository will be archived with a forward pointer, and
hawkinsoperations.com will replace the current site. Nothing about
this repository is retired today.

---

## Contact

- Site: [hawkinsops.com](https://hawkinsops.com)
- Email: raylee@hawkinsops.com
- LinkedIn: [linkedin.com/in/raylee-hawkins](https://linkedin.com/in/raylee-hawkins)
- Location: Gadsden, AL, relocating to Huntsville, AL
