# Content Architecture

## Purpose

This file defines the intended information architecture for reviewer-facing content.

## Primary reviewer path

Recommended sequence:
1. homepage
2. flagship case study
3. proof lane
4. resume
5. deeper lab and detection surfaces

## Core page roles

- `site/index.html`
  - first-impression page
  - establish identity, flagship system, and proof path

- `site/case-study-autosoc.html`
  - flagship system narrative
  - may evolve toward SignalFoundry naming, but must stay the primary technical story surface

- `site/proof.html`
  - public proof lane
  - numbers, artifacts, and reviewer-safe verification path

- `site/resume.html`
  - fast ATS and recruiter conversion surface

- `site/detections.html`
  - detection inventory and structured technical depth

- `site/soc-lab.html`
  - lab environment and bounded Splunk / infrastructure proof

- `site/start-here.html`
  - guided reviewer entry point

## Architecture rules

- Do not duplicate the flagship narrative across too many pages.
- Keep one obvious flagship proof object.
- Avoid multiple competing landing pages that all try to explain the same thing.
- Preserve the proof lane as a first-class path, not a buried appendix.

## Splunk placement rule

Splunk should live as supporting investigation proof inside the lab or case-study ecosystem, not as an isolated vanity page unless evidence volume later justifies it.

## Resume relationship

The resume should inherit the same identity model as the site:
- cyber-first
- SignalFoundry as flagship system
- manufacturing as operational credibility layer
