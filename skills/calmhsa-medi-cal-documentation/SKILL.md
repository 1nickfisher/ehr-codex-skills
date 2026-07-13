---
name: calmhsa-medi-cal-documentation
description: Apply current DHCS + CalMHSA documentation rules for California Medi-Cal behavioral health (SMHS, DMC, DMC-ODS) — use whenever building, reviewing, or modifying assessments, problem lists, progress notes, treatment/care plans, claim/code logic, telehealth records, signatures/co-signatures, scope-of-practice gates, timeliness checks, or audit-readiness features in any clinical workflow that touches an MHP, DMC, or DMC-ODS member record. Trigger even when the request only names "EHR," "note," "assessment," "treatment plan," "billing," or a clinician role, because that work almost always carries Medi-Cal documentation rules.
license: MIT
metadata:
  last_verified: 2026-07-12
  sources_file: references/sources.yml
---

> **Guidance, not legal or clinical advice.** This skill synthesizes publicly available authorities for use by software development agents. The cited authorities — not this skill body — are the source of truth. Verify they remain current before relying on any specific rule. See [DISCLAIMER.md](../../DISCLAIMER.md).

# CalMHSA / Medi-Cal Behavioral Health Documentation

This skill is for engineering, product, QA, and clinical work on any California Medi-Cal behavioral health system where the artifact under review or being built is a clinical document, a piece of UI that captures one, a rule that validates one, or a process that claims for one.

The rules are grounded in current authorities. Use these source layers for the question they actually govern:

1. **DHCS Behavioral Health Information Notice (BHIN) 23-068** — *Updates to Documentation Requirements for all SMH, DMC, and DMC-ODS Services* (Nov 20, 2023; effective Jan 1, 2024). Supersedes BHIN 22-019. Authority: W&I § 14184.402(h)(3). This is the regulatory floor.
2. **The current DHCS billing manual and service table for the delivery system and state fiscal year** — the claim specification for codes, units, time thresholds, modifiers, taxonomy, place of service, dependent-code edits, and lockouts. For dates of service in SFY 2026-27, use the July 2026 version 4.0 SMHS, DMC, or DMC-ODS manual and its 2026-27 service table.
3. **CalMHSA Outpatient SMHS Clinical Documentation Guide (2026)** and the **CalMHSA Outpatient DMC/DMC-ODS Clinical Documentation Guide (2025)** — practical guidance built on top of the DHCS authorities. Use these for examples and workflow detail only when consistent with the current DHCS specification.

For clinical-documentation requirements, if a county Mental Health Plan (MHP), DMC, or DMC-ODS contract conflicts with BHIN 23-068, **the BHIN wins**, except where Enclosure 1a (care planning requirements that remain in effect — TCM, ICC, TBS, Peer Support, CCRP, CTF, MHRC, SRP, STRTP, DMC-ODS Residential, FSP ISSP, SABG) imposes a stricter rule. For claim construction and adjudication, use the current manual and service table as well. When no conflict exists, comply with all applicable sources.

The core BHIN 23-068 documentation rules summarized here **do not** apply to: Narcotic Treatment Programs; psychiatric inpatient services in hospitals, PHFs, or PRTFs; DMC-ODS inpatient in CDRHs and acute psychiatric hospitals. A narrow NTP claiming exception from BHIN 26-022 is tracked below because it changes claim review behavior. These rules **do not** apply to Fee-for-Service Medi-Cal or Medi-Cal Managed Care Plan (MCP) behavioral health — those are separate documentation regimes.

## When to apply this skill

Apply when the task involves any of the following on a Medi-Cal member record (or a feature that produces/validates one):

- Designing or changing an Assessment screen, template, validation rule, or PDF.
- Designing or changing a Problem List entity, ICD-10/Z-code/SDOH code logic, or "active problems" UI.
- Anything to do with a Progress Note: schema, required fields, narrative editor, signature/lock, late-note workflow, group-note variant.
- Care/Treatment plan templates and the rules that govern when they are required vs. not.
- Claiming, billing edits, CPT/HCPCS selection, ICD-10 association, allowable-discipline gates.
- Signature, co-signature, supervision, scope-of-practice enforcement (LPHA review, MHRS, AOD counselor, registered/waivered staff).
- Timeliness alerts: 3-business-day note rule, 1-calendar-day crisis rule, assessment timeliness.
- Telehealth consent and place-of-service.
- Care coordination, Transition of Care Tool, discharge planning.
- Audit-readiness, compliance reports, recoupment risk.

Skip only if the work is purely cosmetic with no clinical or claim impact (typography on a non-clinical screen, a marketing page, a non-PHI admin tool).

## How to act on it

When you propose code, schema, validations, or copy:

1. **Cite the source** — name the BHIN section (e.g. "BHIN 23-068 § (d)(2)"), current DHCS manual/table and fiscal year, or CalMHSA guide section. Future reviewers need to verify against the authority, not your memory.
2. **State the minimum**, not your preferences. DHCS deliberately left a lot to clinical discretion. Don't add required fields or stricter timelines the regulation does not impose — that creates audit liability and burns clinician time. If a county contract adds a stricter rule, surface that as a county-configurable layer, not a hard-coded default.
3. **Default to person-first, plain-language UX copy.** Members can request and read their records. Avoid jargon, internal codes, and acronyms in user-visible text. Members are not "cases."
4. **When in doubt, ask which delivery system** (MHP / DMC / DMC-ODS / mixed) the feature targets. The rules diverge in important places (e.g., ASAM is required for DMC/DMC-ODS only; CANS/PSC-35 are SMHS youth-only).

---

## The seven artifacts and their hard rules

### 1. Assessment (initial and ongoing)

**Timeliness.** DHCS does **not** prescribe a fixed initial-assessment deadline. Providers use clinical discretion in accordance with generally accepted standards of practice, and assessments are updated as clinically appropriate (e.g., when the member's condition changes). MHPs and DMC-ODS plans must monitor timeliness through their QAPI, but cannot enforce a clock that prevents adequate time when clinical needs require more. (BHIN 23-068 § (a)(1))

**Crisis exception.** A crisis assessment completed during crisis intervention, crisis stabilization, or Mobile Crisis encounters does **not** have to meet comprehensive assessment requirements. It is **not** a substitute for a comprehensive assessment if the member subsequently receives further SMH/DMC/DMC-ODS services. (BHIN 23-068 § (a)(2))

**Pre-diagnosis services are billable.** Clinically appropriate, medically necessary services delivered prior to determination of a diagnosis, during assessment, or before access criteria are confirmed are covered and reimbursable, even if the assessment ultimately determines the member does not meet access criteria for the delivery system in which they sought care. (BHIN 23-068 § (a)(1)(iv); W&I § 14184.402(f); also "No Wrong Door" — BHIN 22-011.) A claim still requires an ICD-10-CM code; permitted "pre-diagnosis" codes include `Z03.89` (encounter for observation for other suspected diseases ruled out — LPHA only) and `Z55–Z65` SDOH/psychosocial codes (any provider in scope). See BHIN 22-013.

**SMHS assessment domains (seven, required).** The format is free, but all seven domains must be captured to the extent information is available. (BHIN 23-068 § (b))

| # | Domain |
|---|---|
| 1 | Presenting Problem(s), Current Mental Status, History of Presenting Problem(s), Member-Identified Impairment(s) |
| 2 | Trauma (exposures, reactions, screening, systems involvement) |
| 3 | Behavioral Health History, Co-occurring Substance Use |
| 4 | Medical History, Current Medications, Co-occurring Conditions other than substance use |
| 5 | Social and Life Circumstances, Culture/Religion/Spirituality |
| 6 | Strengths, Risk Behaviors, and Protective Factors (incl. safety planning) |
| 7 | Clinical Summary, Diagnostic Impression, Treatment Recommendations, Medical Necessity Determination / LOC / Access Criteria |

For SMHS members **under 21**, the CANS is required (ages 6–20) and the PSC-35 is required (ages 3–18). The initial CANS must be completed or an existing CANS updated by a **CANS-certified provider**. (BHIN 23-068 § (a)(4)(vii); MHSUDS IN 17-052, 18-007.)

**DMC / DMC-ODS assessment.** Must use an **ASAM Criteria** assessment. As of Jan 1, 2025, providers shall use either the free ASAM Criteria® Assessment Interview Guide or ASAM CONTINUUM®, or a tool subsequently approved by DHCS. The assessment must include the licensed provider's recommendation for ASAM Level of Care and medically necessary services. (BHIN 23-068 § (a)(3); BHIN 24-001.)

**Scope of practice for the assessment.** Both licensed and non-licensed providers may contribute to the assessment within their scope. **However**, the diagnosis, current mental status, medication history, and assessment of relevant conditions and psychosocial factors must be completed by a provider operating within their scope under California law — licensed, registered, waivered, and/or under the direction of a licensed mental health professional as defined in the State Plan. (BHIN 23-068 § (a)(4)(iv–v))

For DMC/DMC-ODS, if a registered/certified counselor completes the assessment, an **LPHA must review it with the counselor and make the initial diagnosis** — review may be in person, by video, or by phone. (BHIN 23-068 § (a)(3)(ix))

**Assessment signature.** Every assessment must include a typed or legibly printed name, signature of the service provider, provider title (or credentials), and date of signature. (BHIN 23-068 § (a)(3)(x), (a)(4)(vi))

### 2. Problem List

The provider(s) responsible for the member's care **create and maintain** the problem list. The problem list — not a static treatment plan — is the primary mechanism for tracking care over time.

**Required contents** (BHIN 23-068 § (c)(2)):

- Diagnosis/es identified by a provider within their scope, including DSM specifiers when applicable.
- Current ICD-10-CM codes (including Z-codes and SDOH codes).
- Problems identified by a provider within their scope.
- Problems identified by the member and/or significant support person.
- For each problem: name and title (or credentials) of the provider who identified / added / resolved it, plus the date.

A problem identified during a service encounter may be addressed in that encounter and added to the list afterward.

**Updates.** Ongoing; no fixed cadence. Update when there is a relevant change to the member's condition, within a reasonable time consistent with generally accepted standards.

**Cross-discipline entries.** Providers may add items to the problem list that are outside their scope (e.g., a physical-health diagnosis reported by a PCP), and should record who reported the item. The mental health provider is not diagnosing — they are recording reported information.

**Retroactivity.** For members already receiving services on July 1, 2022, no retroactive problem list is required. Start one when they next receive an SMH/DMC/DMC-ODS service. (BHIN 23-068 § (c)(5))

**SDOH codes.** DHCS has a Priority SDOH Code list. Common ones include `Z59.00–Z59.819` (homelessness / housing instability), `Z59.41` (food insecurity), `Z63.x` (family/relationship), `Z65.x` (psychosocial). Encourage rather than require capture — these are policy-priority but not all of them are on the DHCS priority list.

### 3. Progress Notes

**Required elements for non-group notes** (BHIN 23-068 § (d)(2)):

1. Type of service rendered.
2. Date of service.
3. Duration of **direct patient care** for the service (defined in the current SMHS, DMC, or DMC-ODS billing manual and service table).
4. Location / place of service.
5. Typed or legibly printed name and signature of the service provider, with date of signature.
6. Brief description of how the service addressed the member's behavioral health needs (symptom, condition, diagnosis, and/or risk factors).
7. Brief summary of **next steps** (planned action steps by the provider or member, collaboration, referrals, discharge/continuing care planning).

**Group notes** also require: a participants list maintained by the provider; an individual note in each participant's record (containing items 1–5 above); and a brief description of the member's response to the service. If multiple providers render the service, **at least one progress note per member** must be completed and signed by at least one provider; the note must clearly document each provider's specific involvement and duration of direct patient care. (BHIN 23-068 § (d)(1)(i), (d)(3))

**Timeliness** (BHIN 23-068 § (d)(5)):

- All services: progress note within **three (3) business days** of the service.
- Crisis services: within **one (1) calendar day**.
- The day of service is **day zero**.
- Day of service for daily-rate / bundled services (Crisis Residential, Adult Residential, DMC/DMC-ODS Residential, Day Treatment Intensive, Day Rehabilitation, Therapeutic Foster Care): at minimum a **daily note**. Weekly summaries are no longer required.
- Late notes are **still billable** and should not be withheld from claiming. Document the reason for the delay. Recoupment is focused on fraud/waste/abuse, not lateness alone.

**Travel and documentation time** are no longer separately reimbursable — they are accounted for inside provider reimbursement rates. **Continue to record them on the note** so rate-setting reflects real workload.

**No duplication.** If information lives elsewhere in the clinical record (a treatment plan template, the assessment, the problem list), it does **not** need to be repeated in the progress note. (BHIN 23-068 § (d)(4))

**No SOAP/DAP/BIRP mandate.** DHCS does not require any particular note structure. Narrative is fine. Don't ship a UI that forces a structure the regulation does not require — but **do** make the seven required elements unambiguous.

**Avoid jargon and unexplained abbreviations.** Members can access their notes. Notes can be used in legal proceedings.

### 4. Care / Treatment Plans

**The headline rule:** DHCS no longer requires prospectively completed, standalone client plans for SMHS, or standalone treatment plans for DMC/DMC-ODS. Care planning is treated as an ongoing, interactive process documented across the assessment, problem list, and progress notes. (BHIN 23-068 § (e))

Title 9 § 1810.205.2 (Client Plan) and § 1810.232 (Plan Development) are **superseded entirely**. Title 22 § 51341.1 DMC treatment-planning subdivisions (d)(2)–(5), (g), (h)(1)(A)(iv)(c), (h)(1)(A)(v)(b), (h)(2)–(5), (k)(3) are superseded. (BHIN 23-068 Enclosure 2.) Do not ship validations that enforce those superseded rules.

**Plans still required (Enclosure 1a — non-exhaustive).** Care plans / specific care-planning activities remain mandatory for:

- Targeted Case Management (TCM) — 42 CFR § 440.169(d)(2): specifies goals and actions to address medical/social/educational/other services needed; activities including the member's active participation; a course of action responding to assessed needs.
- Intensive Care Coordination (ICC) — Medi-Cal Manual for ICC, IHBS, TFC; documented through assessment + problem list + notes or a dedicated plan.
- Therapeutic Behavioral Services (TBS) — DMH IN 08-38; *Emily Q. v. Bonta*. Plan must include targeted behaviors, observable/quantifiable goals, benchmarks, interventions with measurable change criteria, transition plan, transitional-age-youth plan, signature (co-signature required if the developer/server is unlicensed/unwaivered — co-signer must be physician, licensed/waivered psychologist, licensed/registered social worker, or licensed/registered MFT), evidence of child/youth or legal guardian participation and agreement (or explanation if signature not obtainable).
- Medi-Cal Peer Support Services — must be based on an approved plan of care, approved by a treating provider who can render reimbursable Medi-Cal services.
- Mental Health Rehabilitation Centers, Community Treatment Facilities, Social Rehabilitation Programs, Short-Term Residential Therapeutic Programs, DMC-ODS Residential / Withdrawal Management LOC-designated facilities, Children's Crisis Residential Programs, MHSA Full Service Partnership ISSPs, SABG-funded services.

**Where to store plan elements.** When a plan **is** required, providers choose the location — a dedicated plan template, the assessment, the problem list, the progress notes, or a combination. MHPs/DMCs cannot enforce location, format, or other specifications beyond BHIN 23-068 and its Enclosures. Make the EHR flexible.

**Producibility.** Whatever the storage choice, the provider must be able to **produce and share the plan content** with other providers, the member, and Medi-Cal delivery systems consistent with privacy law. Build export/share affordances accordingly.

### 5. Claiming

Each progress note must provide enough detail to support the **service code(s)** selected. (BHIN 23-068 § (d)(1))

**Start with the current claim specification.** For SFY 2026-27 dates of service, use the July 2026 version 4.0 billing manual and 2026-27 service table for SMHS, DMC State Plan, or DMC-ODS. Do not carry forward a prior-year code, unit, modifier, discipline, place-of-service, dependent-code, or lockout rule. Do not infer a billable duration from an appointment label or a generic example; verify the exact code row and time-selection rule.

**Code sets:**

- **CPT** + **HCPCS** for the procedure (the service activity).
- **ICD-10-CM** for the diagnosis, including Z-codes during assessment when no diagnosis is yet established.
- DSM specifiers ride with the diagnosis on the problem list, not in the claim form.

Current ICD-10-CM and HCPCS/CPT codes are **not required inside the progress note narrative**, but they must appear on the claim and be clearly associated with each encounter and consistent with the note description. (BHIN 23-068 § (d)(1) fn.)

**Allowable disciplines vary by code.** Build a per-code allowable-discipline check, not a global "is licensed?" gate. The current DHCS service table and billing manual control claim validation. The CalMHSA SMHS Clinical Documentation Guide discipline matrix is practical workflow guidance and must not override the current DHCS specification. A few high-traffic examples:

| Code | Description | Allowable disciplines (abbreviated) |
|---|---|---|
| 90791 | Psychiatric Diagnostic Evaluation | LCSW, LMFT, LPCC, PhD/PsyD, MD/DO, NP, PA, CNS (and their CT/waivered counterparts) |
| 90792 | Psychiatric Diagnostic Eval w/ Medical Assessment | MD/DO, NP, PA, CNS (and CTs) — **prescribers only** |
| 90832 / 90834 / 90837 | Individual Psychotherapy 30 / 45 / 60 min | All LPHA disciplines (LCSW, LMFT, LPCC, PhD/PsyD, MD/DO, NP, PA, CNS, and CTs) |
| 90847 | Family Psychotherapy w/ Patient Present | All LPHA disciplines |
| 90853 | Group Psychotherapy | All LPHA disciplines |
| H0031 | Mental Health Assessment by Non-Physician | Broad non-physician set — AOD, CNS, LCSW, LMFT, LOT, LPCC, LPT, LVN, MHRS, NP, PA, PhD/PsyD, Pharm, RN, "Other," and permitted registered/waivered/CT variants; excludes MD/DO |
| H2011 | Crisis Intervention | Broad including MHRS, AOD, RN, LVN, LPT, LOT, Pharm, MD/DO, NPs |
| H2017 | Psychosocial Rehabilitation | Broad including MHRS, MA, RN, LVN, LPT, LOT, Pharm |
| T1017 | Targeted Case Management | Broad including MHRS, MA, AOD, RN, LVN, LPT, LOT, Pharm |
| H2019 | Therapeutic Behavioral Services | Broad including MHRS, MA |
| H0032 | MH Service Plan Developed by Non-Physician | Broad including MHRS, AOD, RN, LVN, LPT, LOT, Pharm |
| H0038 | Self-help / Peer Services | **Certified Peer Specialist only** |
| H0025 | BH Prevention Education Services | Certified Peer Specialist only |

CT = trainee, CT/waivered staff under the direct supervision of a Behavioral Health Professional. Use the CalMHSA matrix to orient the workflow, then verify each new validation against the current DHCS service table and manual.

**"Collateral" is no longer a distinct service type.** Document collateral contact by selecting the service code that best describes the activity. (CalMHSA 2026 SMHS Guide § "Service Categories")

**Bundled services.** If a daily-rate / bundled service (e.g., DMC/DMC-ODS Residential, CRT, ART, DTI, DR, TFC) is delivered on the same day as a second, non-bundled service, both notes are required to support both claims. (BHIN 23-068 § (d)(6))

**No sign-in sheets for DMC/DMC-ODS groups.** Title 22 § 51341.1(g)(2)(A–E) is superseded. The provider maintains a participant list per BHIN 23-068, but the old sign-in-sheet regulatory format is gone.

**NTP counseling outlier rule (future-effective).** BHIN 26-022 applies to DMC and DMC-ODS claims for dates of service beginning September 20, 2026. When aggregate NTP counseling for one member on one date reaches **nine or more 15-minute units** across H0004 and H0005, plus T1006 for DMC-ODS only, the county must manually review documentation for all affected units and place modifier **GD** on every affected NTP counseling service line. Do not apply this threshold before its effective date, and verify the service tables at implementation time.

**Draft claiming guidance is non-normative.** DHCS posted draft BHIN 26-0XX on June 25, 2026 for proposed EBP, FSP, and BHSS Early Intervention codes and modifiers beginning January 1, 2027. Track final publication, but do not implement the draft code/modifier table as a current rule.

### 6. Signatures, co-signatures, scope, supervision

Every assessment and progress note must include typed/printed name, signature, title or credentials, and date. EHRs usually capture the signature and date when the provider finalizes the note — surface those fields explicitly so they appear in printed/exported records.

**Co-signature is required** for plans/services where the rendering provider is **not licensed or waivered**, and the program type still requires a plan. The TBS rule is explicit: co-signature must come from a physician, licensed/waivered psychologist, licensed/registered social worker, or licensed/registered MFT. Apply the same logic for other plan-required programs (TCM, ICC, Peer Support plan-of-care): use an LPHA co-signer.

**LPHA review for DMC/DMC-ODS assessment by a counselor.** If a registered/certified counselor completes the assessment, an LPHA must review with the counselor and make the **initial diagnosis** (in person, video, or phone).

**Diagnoses can only be made by providers within their scope.** Z-codes / SDOH codes can be added by qualified non-LPHA staff during the assessment phase before a diagnosis is set; Z03.89 ("encounter for observation, ruled out") is **LPHA-only**. (BHIN 22-013.)

If you build a "diagnose" affordance, restrict it by scope-of-practice using the Appendix III matrix; if you build "add to problem list," allow broader entry and require provider identity and date.

### 7. Telehealth

Refer to BHIN 23-018 (or any subsequent telehealth policy). Documentation must capture **member consent** for telehealth services, the modality (video vs. audio-only), and the place of service as defined by the telehealth modality, not the provider's physical location. The note's "location / place of service" field should reflect the telehealth POS code (typically POS 02 or 10 depending on member location) consistent with the claim.

---

## Cross-cutting rules to design around

### Access ("medical necessity") criteria

**SMHS, age 21+.** Both must be true:

- The person has **significant impairment** (distress, disability, or dysfunction in social, occupational, or other important activities) **or** a reasonable probability of significant deterioration in an important life function; AND
- The condition is due to a diagnosed mental health disorder per current DSM/ICD **or a suspected mental disorder not yet diagnosed**.

**SMHS, under 21.** Either of the following:

- The person has a condition putting them at high risk for a mental health disorder due to trauma (elevated trauma-screening score, child welfare, juvenile justice, or homelessness); OR
- Both: significant impairment / reasonable probability of significant deterioration / reasonable probability of not progressing developmentally / a need for SMHS not included in MCP mental health benefits; AND condition is due to a diagnosed mental health disorder, a suspected mental health disorder, or significant trauma per a licensed mental health professional's assessment.

(Welfare & Institutions Code § 14059.5; 42 U.S.C. § 1396d(r); BHIN 26-002, which supersedes BHIN 21-073.)

**DMC/DMC-ODS.** Driven by ASAM Criteria assessment; LPHA-confirmed.

### No Wrong Door (BHIN 22-011)

Clinically appropriate SMHS are covered and reimbursable regardless of co-occurring SUD; clinically appropriate DMC/DMC-ODS are covered regardless of co-occurring mental health disorder. NSMHS and SMHS can run concurrently if coordinated and non-duplicative. **Don't build mutex flags between the systems.**

### Screening Tools (BHIN 25-020)

MCPs and MHPs must use the DHCS standardized adult / youth screening tool for first-time contacts seeking mental health services (with documented exceptions). Wording and scoring are fixed. **Score override** can only be performed by RN, PA, MD, licensed psychologist, LCSW, LPCC, LMFT, LOT, or their waivered/registered/trainee counterparts — at the time of administration, not retroactively. Override + rationale must be documented and shared with the receiving delivery system, and is auditable. If you build screening, do not block referral on override review.

### Transition of Care Tool (BHIN 25-020)

When transitioning between MHP and MCP (in either direction), an LPHA makes the decision; once made, a non-clinician can complete the form. Field wording is fixed by DHCS; additional info goes in attachments. Build the tool as a fixed form with attachment support, not a freeform document.

### Documentation timelines summary

| Item | Rule | Source |
|---|---|---|
| Progress note (most services) | Within 3 business days; day-zero = day of service | BHIN 23-068 § (d)(5) |
| Progress note (crisis) | Within 1 calendar day | BHIN 23-068 § (d)(5) |
| Bundled / daily-rate services | At least a daily note | BHIN 23-068 § (d)(6) |
| Assessment (initial / update) | Clinical discretion; reasonable time per accepted standards | BHIN 23-068 § (a)(1) |
| ASAM LOC (residential admission) | Within 72 hours | BHIN 21-001 |
| Problem list updates | Reasonable time per accepted standards | BHIN 23-068 § (c)(4) |
| Late note | Still billable; document delay reason | CalMHSA 2026 Guide § "Progress Notes Timeliness" |

### Common audit findings to design out

- Missing required progress-note element (most often: location/POS, duration of direct patient care, signature date).
- Note narrative that does not "support the service code" — e.g., a 90837 note with no description of the intervention.
- Diagnoses or differential listed in the assessment but never reflected on the problem list (or the reverse).
- Group note without a participants list, or with one provider's note used for multiple members.
- Service rendered by a non-LPHA who needs co-signature, but no co-signature on file.
- ASAM LOC recommendation missing from a DMC/DMC-ODS assessment.
- Telehealth note with no documented member consent on file (separate from the note itself is fine).
- Late note recorded as void/non-billable when it should have been claimed.
- Hard-coded "treatment plan due in 60 days" alerts — superseded by BHIN 23-068 § (e) outside Enclosure 1a.

### Schema and data-model implications (illustrative)

These are common implementation patterns that make the regulatory requirements easier to enforce — not regulatory requirements themselves. Adapt to your stack.

When you add fields or rules, prefer:

- A single `problem_list` model joined to a `clinical_record` / `member`, with rows carrying ICD-10-CM code, optional DSM specifier, source (provider / member / collateral), added/resolved provider IDs, and timestamps. Z-codes / SDOH codes live here, not on a separate model.
- A `progress_note` model with required: service code (FK to a `service_code` master keyed by allowable disciplines), service date, duration_direct_minutes (separate from optional duration_travel_minutes and duration_documentation_minutes — kept for rate-setting), place_of_service code (CMS POS), narrative, next_steps. Signature, provider role/title, signed_at populated on finalize.
- Group notes as `progress_note` rows referencing a `group_session` parent that owns the participants list — one note per participant, never one note covering many.
- A `care_plan` model that is **optional** by default and turned on by program/service type (TCM, ICC, TBS, Peer Support, etc.). Don't hard-require it for SMHS in general.
- An allowable-disciplines lookup on `service_code` so claim-time validation matches the Appendix III matrix per code, not a single global LPHA flag.
- Signature/co-signature as a small `signature` table referencing the artifact polymorphically (assessment, plan, note), capturing signer user, role, title/credentials snapshot at time of signing, and timestamp.
- County-overrides as a configuration layer (per MHP) for the small set of legitimate stricter rules; never bake a county's idiosyncratic stricter rule into the core model.

---

## Quick reference — clinician-facing copy guidelines

Use plain, person-centered language. The member may read everything you write into the record.

- "Member" or "individual in care" — not "client," "patient," or "case." (Counties vary; respect existing organizational convention but bias to person-first.)
- "Symptoms" / "concerns" / "needs" — not "complaints" or "deficits."
- Avoid acronyms in narrative ("LPHA," "MHRS," "POS") unless universally recognized.
- Describe what you did and what the member's response was; don't editorialize.
- Document collaboration explicitly: who you talked to, what was discussed, what was agreed.

When you write a progress-note narrative, the regulation's two prompts are:

1. **How did the service address the member's behavioral health needs?** (Symptom, condition, diagnosis, and/or risk factors — what was the link.)
2. **What are the next steps?** (Planned actions by you or the member; collaboration; referrals; discharge / continuing care planning.)

Tightly written notes that answer both, and capture the service code's defining activity, generally pass audit.

---

## Sample progress notes (illustrative — adapt, do not paste)

Drawn from CalMHSA SMHS Clinical Documentation Guide Appendix V. These are *minimum-sufficient* examples. Member identity, dates, vitals shown for shape only.

**90791 — Psychiatric Diagnostic Evaluation:**

> Therapist met with the member today to conduct an assessment based on presenting concerns including heightened anxiety, persistent depression, and difficulty sleeping for the past 6 months. Member's symptoms have impacted his functioning, leading to issues at work and strained social relationships. Based on the clinical assessment, member meets criteria for Generalized Anxiety Disorder (F41.1) and Major Depressive Disorder, Single Episode, Moderate (F32.1). Member will be referred to psychiatry for medication evaluation and individual therapy.

**H2011 — Crisis Intervention Services:**

> Therapist met with member today for crisis intervention due to acute emotional distress triggered by family conflict and job-related stress. Crisis de-escalation techniques, including grounding exercises and guided deep breathing, were used to help stabilize the member's emotional state. A safety plan was collaboratively developed, including identification of supportive contacts and coping strategies. Therapist will follow up later this week to assess the safety plan, review coping strategies, and evaluate whether additional supports are needed.

**90837 — Individual Psychotherapy, 60 min:**

> Therapist met with member for individual therapy to address PTSD symptoms including hypervigilance, intrusive thoughts, and emotional dysregulation. TF-CBT was used to identify and reframe distorted thoughts contributing to distress; grounding exercises were introduced for acute reactions. Therapist will meet with the member next week to continue TF-CBT, introducing further cognitive restructuring and exposure work as appropriate.

**T1017 — Targeted Case Management:**

> Staff contacted the local county community center to inquire about programs that could assist with the member's mental health needs. The center confirmed that its wellness group and social support activities would be appropriate. Staff requested enrollment information. Staff will contact the member to explain the resources, assist with enrollment, and prepare them for participation.

Each example: states the service activity, links it to a behavioral health need, and ends with next steps. All seven required elements are captured when combined with structured fields (date, duration, location, signature).

---

## When to escalate to a human

You **must not**:

- Decide a member meets or fails medical necessity based on policy text alone — that is a licensed clinician's judgment.
- Edit a finalized progress note. Use amendments / addenda per the EHR's audit-trail policy.
- Bypass scope-of-practice checks for code submission, even at user request.
- Generate clinical narratives that go into the record as if written by the clinician. AI-assisted drafting is allowed by some counties; the *clinician* must review, edit, and sign, and the source of drafting may need to be disclosed. Ask the county's policy before turning AI drafting on by default.

Escalate to a clinical reviewer or county QI/QA team when:

- A county contract appears to require something stricter than BHIN 23-068 — verify before coding.
- Enclosure 1a applies and the program-specific rule (TBS, TCM, ICC, FSP, residential, STRTP, MHRC, etc.) controls.
- Telehealth, place-of-service, or modifier rules are ambiguous for a specific service code.
- New BHINs supersede this document (DHCS publishes them at the [BHIN Library](https://www.dhcs.ca.gov/formsandpubs/Pages/Behavioral-Health-Information-Notice-(BHIN)-Library.aspx)).

---

## Source documents (verify against these — they win over this skill)

**Authoritative (regulatory):**

- DHCS BHIN 23-068 — Documentation Requirements for SMH, DMC, and DMC-ODS Services (effective Jan 1, 2024). https://www.dhcs.ca.gov/Documents/BHIN-23-068-Documentation-Requirements-for-SMH-DMC-and-DMC-ODS-Services.pdf
- DHCS BHIN 22-013 — Code Selection Prior to Diagnosis.
- DHCS BHIN 22-011 — No Wrong Door for Mental Health Services.
- DHCS BHIN 26-002 — SMHS Access Criteria (supersedes BHIN 21-073).
- DHCS BHIN 26-022 — NTP Counseling Unit Threshold and Manual Review (effective for dates of service beginning Sept 20, 2026).
- DHCS BHIN 23-018 — Telehealth Policy (or subsequent).
- DHCS BHIN 25-020 — Screening Tools, Transition of Care Tool.
- DHCS BHIN 24-001 — ASAM Criteria for DMC/DMC-ODS.
- DHCS BHIN 21-001 — DHCS LOC Designations for AOD Treatment Facilities (DMC-ODS residential / withdrawal management).
- DHCS BHIN 22-017 — Authorization & documentation for psychiatric inpatient services.
- DHCS BHIN 23-025 — Mobile Crisis Services.
- DHCS BHIN 23-054 — MAT.
- W&I § 14184.402; 42 U.S.C. § 1396d(r); 42 CFR § 438.208; 42 CFR § 440.169.
- DHCS SMHS, DMC State Plan, and DMC-ODS Billing Manuals, version 4.0, SFY 2026-27.
- DHCS SMHS, DMC State Plan, and DMC-ODS Service Tables, SFY 2026-27.
- DHCS County Claims Customer Services Library: https://www.dhcs.ca.gov/services/mental-health-services-division-default/county-claims-customer-services-library/
- BHIN Library (always check for newer): https://www.dhcs.ca.gov/formsandpubs/Pages/Behavioral-Health-Information-Notice-(BHIN)-Library.aspx

**Non-normative watch item:** Draft BHIN 26-0XX — Medi-Cal Claiming for EBPs, FSP Services, and BHSS Early Intervention. Track for final publication; do not encode the draft table.

**Practical guidance:**

- CalMHSA Outpatient SMHS Clinical Documentation Guide (2026). https://www.calmhsa.org/wp-content/uploads/2026/04/SMHS-Clinical-Documentation-Guide-04.2026.pdf
- CalMHSA Outpatient DMC and DMC-ODS Clinical Documentation Guide (2025). https://www.calmhsa.org/wp-content/uploads/2025/04/SUD-Clinical-Documentation-Guide-4.25.2025.pdf
- CalMHSA Clinical Practice training: https://www.calmhsa.org/clinical-practice/
- CalMHSA Policies & Procedures: https://www.calmhsa.org/policies-procedures/
- CalMHSA contact: managedcare@calmhsa.org

If this skill conflicts with the linked authorities, the authorities win. Open a PR to update this file when DHCS issues new guidance.
