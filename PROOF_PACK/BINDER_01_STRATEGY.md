# HUNTSVILLE T1 SOC EMPLOYMENT BINDER
## Chunk 1 — Strategy Core
**Generated:** 03-01-2026
**Candidate:** Raylee Hawkins | raylee@hawkinsops.com | hawkinsops.com
**Target:** Tier 1 SOC Analyst / Cyber Defense Analyst — Huntsville, Alabama
**Clearance status:** Eligible to obtain; willing to pursue sponsorship
**Relocation:** North Alabama; committing to Huntsville by start date

---

## TABLE OF CONTENTS

- [1. Post-Feb 28 Huntsville SOC Market Assessment](#1-post-feb-28-huntsville-soc-market-assessment)
- [2. Tier 1 SOC Positioning Statement](#2-tier-1-soc-positioning-statement)
- [3. Differentiation Thesis — HawkinsOps and AI-Assisted SOC Workflow](#3-differentiation-thesis)
- [4. Clearance Reality and Targeting Approach](#4-clearance-reality-and-targeting-approach)
- [5. Recruiter 2-Minute Validation Path](#5-recruiter-2-minute-validation-path)
- [6A. Huntsville SOC Hiring Reality — DoD 8140 Context](#6a-huntsville-soc-hiring-reality)
- [6B. Target Employer Universe](#6b-target-employer-universe)
- [6C. Platform Strategy](#6c-platform-strategy)
- [6D. Networking Playbook and Templates](#6d-networking-playbook-and-templates)
- [6E. Tier 1 SOC-First Presentation — Exact Text to Paste](#6e-tier-1-soc-first-presentation)

---

## 1. Post-Feb 28 Huntsville SOC Market Assessment

### What Actually Happened

On February 28, 2026, a joint US-Israel strike killed Iran's Supreme Leader. Iran responded with what reporting characterizes as the largest coordinated cyberattack in history. As of March 1, 2026, the effects on defense contractor hiring in Huntsville are indirect and lagged.

### What This Does and Does Not Mean for Hiring

**What changes near-term (weeks 1–4):**
- Program offices on Redstone Arsenal will conduct cyber posture reviews. This is procedural, not optional.
- Program Managers and CORs on active cyber contracts will field calls from contracting officers asking about staffing coverage and surge capacity.
- SOC-adjacent roles on existing contracts (CSSP support, DCO, monitoring) may be directed to fill vacant billets faster than originally planned.
- Recruiters at prime contractors will flag unfilled cyber requisitions to senior leadership. Approval cycles that were stalled may clear.

**What does not change near-term:**
- New contract awards require a Request for Proposal, competitive bid, and award cycle — minimum 60–180 days.
- New contract modifications require CO coordination, funding authorization, and legal review — minimum 2–6 weeks.
- Clearance adjudication timelines do not accelerate during posture reviews. If anything, investigation queues lengthen.
- Headcount growth driven by the event will produce postings in roughly 4–10 weeks, not days.

**Operational conclusion:** The existing hiring pipeline is active and should be worked immediately. The event creates a secondary wave that may emerge in April–May 2026. Your job search plan does not need to wait for that wave. Execute now against active requisitions.

### Huntsville Cyber Market Fundamentals (March 2026)

Huntsville's defense cyber market has structural depth independent of any single event:

- **Redstone Arsenal** hosts Army Futures Command (AFC), Army Space and Missile Defense Command (USASMDC), and the Missile Defense Agency (MDA). All generate persistent cyber support requirements.
- **Cummings Research Park** is the second-largest research park in the United States with over 300 organizations, many of which support DoD programs requiring CSSP and SOC services.
- **Space Command HQ relocation** to Redstone (ongoing) adds a sustained pipeline of cyber personnel billets as the command staffs up.
- **Volume signal (directional, not guaranteed):** Glassdoor listed 47 SOC analyst positions and 182 cybersecurity positions in Huntsville as of February 2026. This is a healthy active market for a city this size.
- **Active entry-level hirers confirmed:** MAD Security (Huntsville-based SOC, active Tier 1 hiring), PeopleTec (SOC Operations Analyst, Huntsville), Gridiron IT, CGI Group, Systems Planning and Analysis, and the major primes (SAIC, Leidos, Booz Allen, ManTech, CACI).

### What Documentation Discipline Means Post-Feb 28

In a heightened threat posture, defense contractor SOC leads care more about:
- Evidence handling that can survive a debrief
- Escalation paths that are documented, not ad-hoc
- Analysts who can produce a clean IR write-up under time pressure
- Tuning discipline that reduces false-positive alert fatigue on an already-stressed team

This is not a personality preference. In a CSSP environment, sloppy documentation creates compliance exposure. **This is the context in which your documentation-first portfolio is a direct hiring signal, not a differentiator on paper.**

---

## 2. Tier 1 SOC Positioning Statement

### What I Am

A self-trained security analyst with a fully documented, publicly verifiable home lab environment. I operate Wazuh SIEM against instrumented Windows endpoints (Sysmon + Wazuh agent), author and validate detection rules across three platforms (Sigma/Wazuh/Splunk), maintain an AI-assisted investigation workflow, and document findings to a standard that produces reproducible, reviewer-verifiable artifacts.

My work is built around a single operational discipline: **evidence first, claims second.** Every rule count, every investigation, every artifact in the HawkinsOps repository can be verified by running a script from the repo root. This is not a portfolio claim — it is a reproducible proof model.

I am targeting Tier 1 SOC Analyst roles where the primary work is:
- Alert triage with documented reasoning
- Initial investigation using structured pivot sequences
- Escalation with clean hand-off documentation
- Playbook-driven response with human-in-the-loop decision points

### What I Am Not (and will not claim to be)

- I am not a credentialed Security+ holder as of March 1, 2026. Exam is scheduled. I will not represent myself as certified before that date.
- I am not an enterprise SOC operator with production shift experience. My lab is a home environment modeled on SOC architecture, not a production deployment.
- I am not a detection engineer by primary role pitch. Detection capability is background evidence. My hiring message is SOC execution competence.
- I am not cleared. I am eligible and willing to pursue, and I will say exactly that — no more, no less.
- I am not a computer science graduate. I am a self-trained analyst with a verifiable proof record. I will not obscure this.

### The One-Sentence Position

> I am a Tier 1 SOC candidate who can triage alerts, investigate incidents with a structured workflow, and produce documentation that holds up to review — and I can demonstrate all three from a public repository before the interview.

---

## 3. Differentiation Thesis

### The Core Problem HawkinsOps Solves

Most entry-level candidates describe skills. A minority can demonstrate them. Almost none can demonstrate them with automated evidence verification.

The HawkinsOps portfolio is built on three principles that directly map to Tier 1 SOC hiring criteria:

**1. Evidence before claims**
Rule counts are generated by script (`verify-counts.ps1`), not self-reported. A reviewer can clone the repo and reproduce the count in under five minutes. This is the same discipline that makes a SOC analyst's incident write-up trustworthy — you don't report findings you haven't backed with evidence.

**2. Documented investigation workflow**
The FIM alert case study (`site/case-study-ir-howe01.html`) documents a complete SOC investigation: a Level 12 Wazuh FIM alert fires, 9 evidence artifacts are collected, each pivot step is recorded, a verdict (BENIGN) is reached with explicit reasoning, and a tuning recommendation is produced. This is a playbook-executable sequence, not a narrative.

**3. AI-assisted investigation acceleration with human-in-the-loop decision points**
The AI-assisted workflow operates as follows:
1. A detection rule fires on a repeatable trigger condition
2. Relevant telemetry is automatically collected (Wazuh alert data, Sysmon event correlation, endpoint context)
3. Investigation pivots are executed in a documented sequence
4. Triage classification and verdict are produced by the analyst — AI provides structured investigation scaffolding, not autonomous decisions
5. Documentation is generated in a standardized format with evidence, timeline, decision rationale, and next hardening step

This framing — **AI accelerates investigation, analyst decides** — is the correct framing for a defense contractor context. It is not "AI does SOC." It is "AI reduces time-to-investigation-start and ensures no pivot step is missed." This is defensible, accurate, and differentiating.

### What the Proof Stack Looks Like

| Claim | Backing Artifact | How to Verify |
|-------|-----------------|---------------|
| 103 Sigma rules, MITRE-organized | `content/detection-rules/sigma/` (10 tactic folders) | `ls` the directory tree |
| 9 Splunk SPL queries | `content/detection-rules/splunk/` | Count files |
| 28 Wazuh rule blocks | `content/detection-rules/wazuh/rules/` | Inspect XML files |
| 10 IR playbooks | `content/incident-response/playbooks/` | IR-001 through IR-022 |
| 1,191 lines automation code | `scripts/` (.ps1, .py, .sh) | `wc -l` recursive |
| Counts are reproducible | `scripts/verify/verify-counts.ps1` | Run the script |
| Live SOC investigation | `site/case-study-ir-howe01.html` | Read the case study |
| Lab infrastructure | `site/soc-lab.html` + `site/lab.html` | Review architecture |

---

## 4. Clearance Reality and Targeting Approach

### The Reality

Defense contractor cyber roles in Huntsville fall into three clearance tiers:

**Tier A — Requires active clearance (Secret or TS)**
These roles are unreachable until an investigation is initiated and adjudicated. Active Secret adjudication takes 6–12 months under normal conditions; current backlog may extend this. Do not apply and expect to start. Do apply if the posting says "will sponsor" — it puts you in their talent pipeline for future openings.

**Tier B — Clearable / sponsorship positions**
The posting may say "able to obtain Secret" or "clearance sponsorship available." These positions exist and are the primary target tier. The employer is willing to initiate the investigation. Your job is to confirm sponsorship availability before accepting any offer. Standard approach: ask the recruiter directly in the first screen call: "Does this role include clearance sponsorship, or does it require active clearance at start date?"

**Tier C — No clearance required**
Positions explicitly stating no clearance requirement, or commercial SOC roles (like MAD Security's Huntsville SOC). These are open now and should be applied to without hesitation. The work is real SOC work. The credentials and experience transfer directly.

### Targeting Logic

- **Priority 1:** Tier B positions at prime contractors (SAIC, Leidos, Chenega, Amentum, PeopleTec). These are the path to a cleared career and are accessible now.
- **Priority 2:** Tier C positions including commercial SOC (MAD Security) and IT-adjacent cyber roles that don't gate on clearance. These provide income and experience while clearance processes.
- **Do not avoid:** Tier A postings at target companies. Apply and note them as pipeline. If the company extends an offer, you negotiate start dates against adjudication timelines.

### What to Say About Clearance

In every outreach, resume, and interview:

> "Eligible to obtain clearance; willing to pursue sponsorship."

This is factually accurate, legally appropriate, and signals willingness without overclaiming. Do not say "clearance eligible" if it implies you have an active clearance. Do not say "able to obtain clearance" in a way that implies a timeline you cannot guarantee. The phrasing above is calibrated.

---

## 5. Recruiter 2-Minute Validation Path

This is the navigation sequence a recruiter should be able to follow in under 2 minutes to confirm the core claims.

**Entry point:** `hawkinsops.com`

```
Step 1: hawkinsops.com → Homepage
  Confirms: active portfolio, SOC lab environment, detection work exists

Step 2: → Case Studies (site navigation)
  → case-study-ir-howe01.html
  Confirms: documented SOC investigation with evidence artifacts,
            triage workflow, verdict with reasoning, tuning output

Step 3: → Resume (site navigation) → GitHub link
  → github.com/raylee-hawkins
  Confirms: content/detection-rules/ repository with 103 Sigma YAML files
            in MITRE tactic-organized subdirectories

Step 4: → PROOF_PACK/VERIFIED_COUNTS.md (in repo)
  Confirms: reproducible counts via verify-counts.ps1
            103 Sigma | 9 Splunk | 28 Wazuh blocks | 10 IR playbooks

Step 5: → START_HERE.md (repo root)
  Confirms: evidence-first methodology, 5-minute proof path,
            reproducible verification model
```

**What this demonstrates in 2 minutes:**
- Real detection rules (structured, not placeholders)
- Documented investigation (not a blog post, a full evidence trail)
- Reproducible counts (automated verification, not self-report)
- Process discipline (PROOF_PACK methodology)
- AI-assisted workflow integration (described in case study)

**What is NOT in this path:**
- The three case study URLs from the prior binder (credential-dump, lateral-movement, c2-detection) do not exist. They will not be referenced in any outreach or application until they are published.
- No claims beyond what is verifiable at those URLs.

---

## 6A. Huntsville SOC Hiring Reality

### How Defense Contractor Cyber Hiring Works

Defense contractor cyber hiring follows a sequence: **contract award → funded billet → requisition opened → recruiter sourcing → interview → conditional offer → clearance initiation → start.**

The lag between "event that creates cyber need" and "new employee starts" is typically 8–20 weeks when a new contract is involved. For existing contracts with unfilled billets, the cycle compresses to 3–8 weeks. For clearance-required roles, add 6–12 months after offer.

**Implication:** Roles open right now exist because the billet was funded months ago. You are not waiting for the Feb 28 event to generate jobs. Those jobs don't exist yet. You are competing for jobs that already exist in the pipeline.

### DoD 8140 — What It Is and Why It Matters

DoD Directive 8140 (specifically DoDM 8140.03, Cyberspace Workforce Qualification and Management Program) replaced DoD 8570. It defines 72 work roles across seven workforce elements and establishes baseline qualification requirements for each.

**Key facts for this job search:**

- **Compliance deadline was February 15, 2025** for DoD civilian employees and military service members in cybersecurity work roles. Contractors must meet qualifications per their contract statement of work.
- **Qualification Matrix v2.1** (effective September 19, 2025) is the current standard. It maps approved commercial certifications to specific work roles at Basic, Intermediate, and Advanced proficiency levels.
- **Work Role 511 — Cyber Defense Analyst** (DCWF specialty area: Cyber Defense Analysis) is the role that most closely maps to Tier 1 SOC functions. KSATs include: analyzing network traffic and IDS alerts, correlating event data, identifying indicators of compromise, and producing documentation of analysis and findings. This is the role you are performing in your lab.
- **Security+ (CompTIA SY0-701)** is an approved foundational qualification option for multiple DCWF work roles including Cyber Defense Analyst (511) and Incident Responder (531). It is the standard entry-level baseline across most defense contractor SOC job descriptions. It is not optional for DoD-contract SOC roles — it is the floor.
- **CySA+ (CS0-003)** maps at Intermediate proficiency for 511. It is a realistic next certification post-employment.

**What this means for your applications:**
- Until Security+ is passed, use "exam scheduled" language. After it is passed, this gate clears for the majority of open T1 SOC postings.
- On job descriptions that list Security+ as "required," you can still apply and note exam date. Recruiters will often screen you in if the exam is imminent.
- On job descriptions that list Security+ as "desired/preferred," apply immediately with no reservation.
- Roles labeled DCWF 511 are your exact target role code.

### Clearance Gating — What Can Start Uncleared

Roles where you can start and do productive work before clearance adjudication:
- Commercial SOC positions (no government contract requirement for cleared access)
- Program support / documentation / knowledge management roles
- Contractor positions that sponsor clearance and allow 90-day provisional start
- Some IT-adjacent cyber roles (vulnerability management, compliance support) that don't require access to classified systems

Roles that gate on active clearance at start date:
- Positions labeled "Active Secret Required" or "TS/SCI Required"
- Positions on certain Sensitive Compartmented Information (SCI) programs
- Positions requiring polygraph

**Rule of thumb:** If the posting says "must have active clearance," do not count on being able to negotiate around it. If it says "must be able to obtain" or doesn't mention clearance, apply directly.

---

## 6B. Target Employer Universe

### Tier 1 — Apply First, Active Contact

| Employer | Why | Primary SOC Titles | Clearance Stance | Best Platform |
|----------|-----|-------------------|------------------|---------------|
| **Chenega Corporation** | Warm referral path (Jason Garstka). Chenega subsidiaries hold numerous SOC-adjacent contracts on Redstone. Employee-owned, often clearance-sponsoring. | SOC Analyst I, Cyber Defense Analyst, Security Operations Specialist | Varies by contract; sponsorship common | Direct: chenega.com/careers |
| **MAD Security** | Huntsville-based commercial SOC. Active Tier 1 SOC Analyst hiring confirmed. No cleared requirement for commercial SOC work. Entry-level role explicitly posted. | SOC Analyst Tier 1, Security Operations Analyst | None required for commercial SOC | Direct: mad-security-llc.prismhr-hire.com |
| **PeopleTec** | Huntsville HQ, employee-owned, 450+ employees, active SOC Operations Analyst posting confirmed. Cybersecurity, RMF, CND focus. | SOC Operations Analyst, Information Assurance Analyst, Cyber Analyst | Varies; often able-to-obtain for entry | Direct: peopletec.com/careers; Indeed |
| **SAIC** | Major Huntsville presence. Consistent entry-level cyber hiring. Multiple active contracts on Redstone. | SOC Analyst I, Cyber Defense Analyst, Security Analyst | Mix of clearance-required and sponsorship | Direct: saic.com/careers; LinkedIn |
| **Leidos** | Major defense contracts. SOC roles documented across Redstone programs. Acquired Dynetics (Huntsville-based). | Security Analyst, SOC Analyst, Incident Response Analyst | Mix; Leidos sponsors clearances | Direct: leidos.com/careers; Indeed |

### Tier 2 — Apply in Week 1-2

| Employer | Why | Clearance Stance | Best Platform |
|----------|-----|------------------|---------------|
| **Amentum** | Large Huntsville presence, formed from PAE+AECOM merger. Cyber infrastructure, operations support. | Varies; sponsorship on many roles | Direct: amentum.com/careers |
| **Booz Allen Hamilton** | Known Huntsville office, consulting orientation, strong cyber practice. Some non-clearance entry points. | Heavy clearance culture; some open roles | Direct; LinkedIn |
| **ManTech** | SOC operations focus across DoD. Redstone footprint. | Active clearance often required; check postings | Direct: mantech.com/careers |
| **CACI** | Intelligence and cyber focus. Redstone contracts. | Active clearance often required | Direct: caci.com/careers |
| **Parsons** | Cyber infrastructure. Some non-clearance roles. | Varies | Direct: parsons.com/careers; Indeed |
| **Northrop Grumman** | Missile defense focus, clearance-heavy. Apply for pipeline. | Usually active clearance | Direct: northropgrumman.com/careers |
| **BAE Systems** | Space and missile programs. | Usually active clearance | Direct: baesystems.com/careers |
| **Jacobs** | Engineering + IT support, some cyber. | Varies | Direct: jacobs.com/careers |

### Tier 3 — Opportunistic / Pipeline Building

| Employer | Why |
|----------|-----|
| **Torch Technologies** | Huntsville-founded, DoD focus. Cybersecurity engineer roles, higher bar but worth pipeline. |
| **Dynetics (Leidos subsidiary)** | Huntsville origin, now Leidos. Some IT/cyber analyst roles. |
| **Gridiron IT** | Appears on Huntsville cyber job listings. Check current postings. |
| **H2L Solutions** | Huntsville-based cybersecurity and IT firm. RMF, compliance focus. Smaller contract vehicle. |
| **CGI Group** | Huntsville area postings confirmed. Government IT and cyber. |
| **Systems Planning and Analysis (SPA)** | Technical analysis, some cyber roles. Huntsville presence. |
| **ASRC Federal** | Engineering, IT, infrastructure support to defense and civil agencies. |
| **Koniag** | Alaska Native Corporation holding company with cyber and IT subsidiaries; diverse primes. |

**Note on Tier 3:** ANC (Alaska Native Corporation) and small business contractors frequently win set-aside contracts on Redstone. They hire quickly when a contract awards and may have fewer applicants per opening. Track them on SAM.gov new awards if you have capacity.

---

## 6C. Platform Strategy

### LinkedIn — Positioning, Discovery, and Warm Outreach

**Primary use cases:**
1. Recruiter discovery (optimize for inbound)
2. Hiring manager and team lead outreach
3. Connection-building in Huntsville security community
4. Monitoring Tier 1/Tier 2 employer job postings

**Daily cadence:**
- 5 targeted connection requests to Huntsville security professionals
- Monitor saved searches: "SOC Analyst Huntsville," "Cyber Defense Analyst Huntsville," "Cybersecurity Analyst Redstone"
- Review "People Also Viewed" on recruiter profiles to find adjacent contacts

**Who to target for connections:**
- Talent acquisition at SAIC, Leidos, Chenega, Amentum (search "[Company] recruiter Huntsville")
- SOC leads, CSSP program managers, cyber team leads at primes (these are the people who write the job descriptions)
- Huntsville Information Security Association (HISA) members — this is a local group; joining or connecting to members is a direct pipeline signal

**LinkedIn Easy Apply:** Use for Tier 2/Tier 3 employers where tailoring is lower priority. Do not use Easy Apply for Tier 1 targets — apply direct with tailored materials.

---

### Indeed — Volume Pipeline

**Primary use cases:**
1. High-volume daily application loop
2. Finding listings that don't appear on LinkedIn
3. Company discovery (smaller contractors post primarily on Indeed)

**Daily search queries (run in order):**
1. `SOC Analyst` → Huntsville, AL → Date: Last 7 days
2. `Cyber Defense Analyst` → Huntsville, AL → Date: Last 7 days
3. `Security Operations` → Redstone Arsenal, AL → Date: Last 14 days
4. `Cybersecurity Analyst` → Huntsville, AL → Posted: Last 7 days

**Filter discipline:**
- Sort by date, not relevance
- If a posting is older than 21 days, apply anyway but deprioritize follow-up
- Flag postings with "active clearance required" if you cannot meet that requirement — add to pipeline list, not active apply list
- Track salary range when visible; $65k–$90k is the T1 SOC band for non-cleared; $85k–$115k for clearable roles

**Profile optimization:**
- Upload resume as PDF and as `.txt` (Indeed parses both)
- Set job alerts for all four search queries above
- Update "open to work" to show Huntsville, AL as target location — not remote

---

### Direct Company Sites — High-Signal Applications

**Use for:** Tier 1 and Tier 2 targets. Direct applications show intent. Many primes have ATS systems (Workday, Taleo, iCIMS) that recruiters prefer over LinkedIn or Indeed sources.

**Weekly cadence:**
- Monday: Check Chenega, MAD Security, PeopleTec, SAIC
- Wednesday: Check Leidos, Amentum, Booz Allen, ManTech
- Friday: Check remaining Tier 2 employers + any new direct site alerts

**Application practice:** Use the exact job title from the posting in your cover email subject line. Include the requisition ID in the email body. These are ATS routing signals that get your application to the right queue.

---

### ClearanceJobs — Cleared Ecosystem Discovery

**Primary use cases:**
1. Discovering which contractors hold which types of contracts (clearance level signals contract type)
2. Identifying "must sponsor" postings in the database
3. Networking with cleared professionals in the Huntsville ecosystem

**Filter setup:**
- Location: Huntsville, AL
- Clearance required: "None" AND "Eligible (no clearance required)"
- Category: Cyber, IT Security, Information Assurance

**What ClearanceJobs tells you beyond job titles:** When a company posts multiple cleared roles, it's a signal that they have active contracts winning. This is employer targeting intelligence, not just a job board.

---

## 6D. Networking Playbook and Templates

### Weekly Target Counts

| Activity | Weekly Target |
|----------|--------------|
| LinkedIn connection requests sent | 25 (5/day M–F) |
| Direct messages to recruiters | 5 |
| Direct messages to SOC team leads / hiring managers | 3 |
| Follow-up messages on accepted connections (no response after 5 days) | All pending |
| Local community engagement (HISA, BSides Huntsville, local LinkedIn groups) | 1 post or comment/day |

### Who to Connect With

**Category 1 — Recruiters at target employers**
Search: "[Company name] recruiter" filtered to Huntsville, AL area.
These people post roles, review applications, and screen candidates. A connection before applying gets your name visible.

**Category 2 — SOC leads, CSSP program managers, cyber team leads**
Search: "SOC" OR "CSSP" OR "cyber defense" at target companies filtered to Huntsville.
These are the people who write job requirements and influence hiring decisions. A thoughtful message about your portfolio can generate a referral.

**Category 3 — Peers in the Huntsville security community**
Huntsville Information Security Association (HISA) members. Graduates of UAH, AAMU, or Calhoun cybersecurity programs. People who post about Redstone-adjacent security topics. They are the network that feeds word-of-mouth referrals.

---

### Template A — Cold LinkedIn Connection Request

```
Hi [Name],

I'm a SOC analyst candidate relocating to Huntsville in [month]. I noticed you work in security operations at [Company] — I'm targeting the Huntsville defense cyber market and building my local network.

I've been running a home lab SOC environment (Wazuh SIEM, 103 Sigma rules, documented IR workflows) at hawkinsops.com if you're curious about the work.

No pitch — just looking to connect with people doing the work in Huntsville.

Raylee Hawkins
```

*(300 character limit applies to connection notes — shorten to: "SOC candidate relocating to Huntsville. I run a lab SOC with Wazuh/Sigma at hawkinsops.com. Targeting defense cyber roles. Would appreciate the connection.")*

---

### Template B — Recruiter Direct Message (After Connection Accepted)

```
Subject: SOC Analyst candidate — Huntsville relocation

Hi [Name],

Thanks for connecting. I'm targeting Tier 1 SOC Analyst / Cyber Defense Analyst roles at [Company] in Huntsville. A few specifics:

- Home lab SOC: Wazuh SIEM, 103 Sigma rules mapped to MITRE ATT&CK, 10 IR playbooks, full case study at hawkinsops.com
- Security+ exam: [scheduled date / PASSED — update per status]
- Clearance: Eligible to obtain; willing to pursue sponsorship
- Relocation: Committing to Huntsville by start date

Would you be open to a 15-minute call, or is there a current opening I should direct my application to?

hawkinsops.com | github.com/raylee-hawkins
```

---

### Template C — Warm Referral Request (Chenega / Jason Garstka path)

```
Subject: Referral from Jason Garstka — SOC Analyst interest at Chenega

Hi [Name],

Jason Garstka suggested I reach out to you regarding SOC analyst or cybersecurity analyst opportunities at Chenega.

My background:
- Home lab SOC with Wazuh SIEM deployment, 103 Sigma detection rules (MITRE-organized), 9 Splunk queries, 10 IR playbooks — all publicly verifiable at hawkinsops.com
- Security+: [scheduled for [date] / PASSED — update per status]
- Clearance: Eligible to obtain; willing to pursue sponsorship
- Relocating to Huntsville; committed to start date

I'm targeting Tier 1 SOC or Cyber Defense Analyst roles. If there are current openings that fit, I'd welcome the conversation.

Raylee Hawkins
raylee@hawkinsops.com
hawkinsops.com
```

---

### Template D — Follow-Up After Application (7 Days, No Response)

```
Subject: Follow-up — [Position Title], [Req ID if known]

Hi [Name / Hiring Team],

I submitted an application for [Position Title] on [Date]. I wanted to follow up and confirm my continued interest.

My portfolio is at hawkinsops.com — it includes a documented Wazuh SIEM investigation, MITRE-mapped detection rules, and IR playbooks. Security+ [scheduled / passed].

If there's a better way to get my application reviewed, or if the role has moved, I'd appreciate knowing.

Raylee Hawkins
raylee@hawkinsops.com
```

---

### Template E — Thank-You After Screen Call

```
Subject: Thank you — [Position Title] conversation

[Name],

Thank you for the time today. [Specific thing they mentioned about the role or team] reinforced why I'm targeting [Company] specifically.

The triage and documentation discipline you described maps directly to the workflow I've built in my lab — the FIM alert case study at hawkinsops.com/[case-study-ir-howe01] is the closest analog to what you outlined.

I'd welcome the next step whenever you're ready.

Raylee Hawkins
raylee@hawkinsops.com
hawkinsops.com
```

---

### No-Response Escalation Branch

If a connection request is accepted but no response to a follow-up DM after 5 days:
- Send one brief follow-up: "Happy to share the portfolio directly if easier — hawkinsops.com. No pressure either way."
- If no response after that, move to a different contact at the same company. Do not send a third message to the same person.

If an application receives no response after 14 days:
- Send Template D (follow-up email).
- If no response after 7 more days: one final note ("following up one last time"), then close the loop and move on.
- Do not email more than 3 times total for a single application.

If reply rate falls below 5% after 25+ applications (see Chunk 2 escalation logic for full protocol).

---

## 6E. Tier 1 SOC-First Presentation

All text in this section is exact paste text. Copy as written.

### LinkedIn Headline

```
SOC Analyst Candidate | Wazuh SIEM | MITRE ATT&CK Detection | AI-Assisted Investigation Workflows | Relocating to Huntsville
```

*(If Security+ is passed, update to:)*
```
SOC Analyst Candidate | CompTIA Security+ | Wazuh SIEM | MITRE ATT&CK Detection | Relocating to Huntsville
```

---

### LinkedIn About Section

```
I'm a Tier 1 SOC analyst candidate with a documented, verifiable home lab security operations environment. My work is built around three things: triage discipline, evidence-first documentation, and reproducible proof.

What I've built at HawkinsOps (hawkinsops.com):
— Wazuh SIEM deployed against instrumented Windows endpoints (Sysmon + agent). Live alerts, real telemetry.
— 103 Sigma detection rules organized by MITRE ATT&CK tactic. 9 Splunk SPL queries. 28 Wazuh rule blocks.
— 10 incident response playbooks (IR-001 through IR-022 catalog).
— Full SOC investigation documented: Level 12 FIM alert → 9 evidence artifacts → triage → BENIGN verdict with reasoning → tuning recommendation.
— AI-assisted investigation workflow: structured pivot sequences, human-in-the-loop decisions, standardized output.
— 1,191 lines of automation code (PowerShell, Python, shell) for verification, build, and deployment.

All counts are script-generated and reproducible. START_HERE.md in the repo walks a reviewer through the proof in 5 minutes.

Security+: [In progress, exam scheduled / PASSED — update per status]
Clearance: Eligible to obtain; willing to pursue sponsorship.
Relocating to Huntsville, AL — available for in-person interviews.

Portfolio: hawkinsops.com
GitHub: github.com/raylee-hawkins
```

---

### Indeed Profile Summary

```
SOC analyst candidate with hands-on Wazuh SIEM experience, MITRE ATT&CK-mapped detection library, and documented incident investigation workflow. I built and operate a home lab security environment with 103 Sigma rules, 28 Wazuh rule blocks, 10 IR playbooks, and a live alert triage case study. All artifacts are publicly verifiable at hawkinsops.com.

Security+: [scheduled / passed]. Clearance: eligible to obtain, sponsorship welcome. Relocating to Huntsville, AL. Available for Tier 1 SOC Analyst, Cyber Defense Analyst, and Security Operations roles supporting defense programs.
```

---

### Resume Top Summary (Replace Current Headline and Summary)

**Headline:**
```
SOC Analyst | Wazuh SIEM | MITRE ATT&CK Detection | Incident Response Documentation
```

**Summary (3 bullets, ATS-optimized):**
```
• Operate home lab SOC with Wazuh SIEM, Sysmon-instrumented endpoints, and structured alert triage workflow; documented full IR lifecycle from alert to BENIGN verdict with 9 evidence artifacts (hawkinsops.com).
• Maintain and validate detection library: 103 Sigma rules (MITRE ATT&CK-organized), 9 Splunk SPL queries, 28 Wazuh rule blocks, 10 IR playbooks — all counts script-verified and reproducible from public repo.
• Eligible to obtain clearance; willing to pursue sponsorship. Security+ [in progress / PASSED]. Relocating to Huntsville, AL.
```

---

*End of Chunk 1 — BINDER_01_STRATEGY.md*
*Next: Chunk 2 — BINDER_02_EXECUTION.md (targeting system, application cadence, escalation logic, weekly ops)*

