---
name: 42-cfr-part-2
description: Apply current 42 CFR Part 2 (SAMHSA Confidentiality of Substance Use Disorder Patient Records) rules — use whenever building, reviewing, or modifying any feature that touches SUD records, consent, redisclosure, breach response, patient notice, accounting of disclosures, restriction requests, audit logs, role-based access to SUD data, court-order workflows, subpoena response, or law-enforcement queries. Trigger even when the request only mentions HIPAA, "consent," "release of information," "behavioral health records," or a clinician role in an SUD program, because Part 2 is stricter than HIPAA in specific places that get implemented wrong by default. The 2024 final rule (effective 2024-04-16, compliance deadline 2026-02-16, OCR enforcing) aligned Part 2 with HIPAA in important ways but kept distinct rules for proceedings against the patient — surface those differences explicitly.
license: MIT
metadata:
  last_verified: 2026-05-27
  sources_file: references/sources.yml
---

> **Guidance, not legal or clinical advice.** This skill synthesizes publicly available authorities for use by software development agents. The cited authorities — not this skill body — are the source of truth. Verify they remain current before relying on any specific rule. See [DISCLAIMER.md](../../DISCLAIMER.md).

# 42 CFR Part 2 — Confidentiality of SUD Patient Records

This skill is for engineering, product, QA, and clinical work on any system that creates, receives, stores, or transmits substance use disorder records held by a federally assisted SUD program — anywhere in the United States. Part 2 is **stricter than HIPAA** in a few specific places, and the 2024 final rule aligned many but not all of those places. The remaining differences are exactly where audits and complaints will land.

The rules are grounded in three current authorities — read them in this conflict order:

1. **42 CFR Part 2** as amended by the 2024 final rule — the regulation itself, as in eCFR. Authority: 42 U.S.C. § 290dd-2; PHS Act § 543. This is the regulatory floor.
2. **HHS Final Rule, *Confidentiality of Substance Use Disorder (SUD) Patient Records*** — 89 FR 12472, document 2024-02544, RIN 0945-AA16. Published Feb 16, 2024; effective April 16, 2024; compliance required Feb 16, 2026. The preamble is the canonical explanation of intent.
3. **HHS / SAMHSA / OCR guidance** — fact sheets, FAQs, and the OCR Civil Enforcement Program (announced Feb 13, 2026, complaints accepted from Feb 16, 2026).

Where Part 2 and HIPAA conflict, the **stricter rule controls** — almost always Part 2. The 2024 alignment narrowed the conflict zones (consent, NPP, breach notification, accounting, restriction requests) but kept the **proceedings prohibition** as a Part 2-only protection.

## When to apply this skill

Apply when the task involves any of the following on a record that could plausibly be a Part 2 record (or a feature that produces/validates one):

- Identifying or flagging programs, units, or personnel as "Part 2 programs" (§ 2.11–2.12).
- Designing or changing the consent capture/storage UI, schema, or workflow — especially single TPO consent and proceeding-specific consent.
- Disclosure of SUD records to another provider, payer, family member, court, law enforcement, public health agency, researcher, or auditor.
- Generating or attaching the "notice to accompany disclosure" / Patient Notice / Notice of Privacy Practices.
- Anything to do with **redisclosure** by a downstream recipient, including HIPAA covered entities and business associates.
- **Subpoena, court order, warrant, or law-enforcement query** response paths.
- Breach detection, breach incident response, and breach notification to patients / HHS / media.
- Patient rights workflows: accounting of disclosures, right to restrict, right to NPP, right to file a complaint with the Secretary.
- Anti-discrimination logic — what data can and cannot be used to deny employment, housing, benefits, or court access.
- Audit logs, role-based access, data export, data segmentation/segregation, and de-identification.
- Any integration that pipes SUD records out of the Part 2 program — HIE, FHIR API, claims pipeline, analytics warehouse, BAA partner.

Skip only if the work demonstrably touches no SUD record and no metadata that could indirectly identify a person as having received SUD services from a Part 2 program.

## How to act on it

When you propose code, schema, validation, or copy:

1. **Cite the specific section** (e.g., "§ 2.31(a)(4)", "§ 2.12(c)(5)", "§ 2.16(b)") inline. A reviewer needs to verify against authority, not your memory.
2. **State the minimum required** by the regulation. Don't add stricter rules unless the customer's state law or organizational policy explicitly imposes them. (State law that is stricter than Part 2 still applies — § 2.20.)
3. **Default to person-first, plain-language UX copy.** Patients can read records and consents. Avoid jargon and unexplained acronyms.
4. **When the data is ambiguous, assume it's Part 2.** The cost of treating non-Part 2 data as Part 2 is small (extra consent). The cost of treating Part 2 data as non-Part 2 is enforcement action.
5. **Default to "ask before you allow."** New disclosure flows, new data exports, new integrations involving SUD data — open a question, don't ship a default-on path.

---

## The core rules

### 1. Applicability — is this a Part 2 record?

A Part 2 record is one that (§ 2.12(a)):

- Identifies an individual (directly or indirectly) as having a current or past **substance use disorder**, AND
- Was created or maintained by a **Part 2 program**, AND
- The program is **federally assisted** (§ 2.12(b)).

A **Part 2 program** is (§ 2.11):

- An individual or entity that **holds itself out as providing**, AND provides, SUD diagnosis, treatment, or referral for treatment; OR
- An **identified unit** within a general medical facility that holds itself out as providing SUD services and provides them; OR
- **Medical personnel or other staff** in a general medical facility whose **primary function** is the provision of SUD diagnosis, treatment, or referral and who are identified as such.

"**Federally assisted**" is intentionally broad (§ 2.12(b)) — it includes Medicare/Medicaid participation, federal tax-exempt status, DEA registration for controlled-substance prescribing, federal funding (direct or indirect), federal licensure, and several other hooks. **Assume most US SUD programs are federally assisted** unless legal counsel has confirmed otherwise.

**Practical implication for software:** every encounter, problem, medication, lab, and note record needs an unambiguous answer to "is this a Part 2 record?" Encode this as a record-level flag derived from the program of origin, not a UI toggle.

### 2. Single TPO consent (the 2024 change)

A single written patient consent now covers all future uses and disclosures for **treatment, payment, and health care operations (TPO)** — replacing the old per-disclosure consent model. (§ 2.31, § 2.33.)

**Required elements of a written consent** (§ 2.31(a)):

- Patient name (or other unique identifier).
- Specific name(s) of the Part 2 program(s) — or a general designation of the disclosing program when authorized.
- How much and what kind of information may be disclosed.
- Name(s) or general designation of recipient(s). For TPO consent, a general designation of "covered entities and business associates" is permitted.
- Purpose of the disclosure.
- A statement that the consent is subject to **written revocation** at any time except to the extent already acted upon.
- Date, event, or condition on which the consent expires if not previously revoked.
- Signature of the patient (or other person legally authorized).
- Date of signature.

**A TPO consent does NOT cover** (§ 2.31(d), § 2.12(d)): any use or disclosure in **civil, criminal, administrative, or legislative proceedings against the patient**. That requires either a separate written consent that specifically references such proceedings, or a court order under § 2.61–2.67. This is the central Part 2-only protection that survived alignment.

**Revocation** (§ 2.31(b)): a patient may revoke any consent at any time, in writing or orally. Already-acted-on disclosures are not affected. Build a revocation workflow that propagates to consent records, future-disclosure gates, and the disclosure log.

**Non-TPO consents** (e.g., to a family member, to an attorney, to a researcher under § 2.52): still require purpose-specific information.

### 3. Redisclosure by recipients

**HIPAA covered entities and business associates that receive Part 2 records under a TPO consent** may redisclose those records consistent with HIPAA — **EXCEPT** they may not use or disclose them in proceedings against the patient without separate written consent or a court order (§ 2.12(d), § 2.33(c)).

**Part 2 programs** that receive records continue to be bound by Part 2 in full.

**Other non-HIPAA recipients** (e.g., schools, employers, government benefits agencies) may redisclose only as permitted by the consent that authorized the original disclosure.

**The accompanying notice** (§ 2.32) — every disclosure of Part 2 records must include either:

- The traditional Part 2 notice: roughly *"This information has been disclosed to you from records protected by federal confidentiality rules (42 CFR Part 2). The federal rules prohibit you from making any further disclosure of this information unless further disclosure is expressly permitted by the written consent of the individual whose information is being disclosed or as otherwise permitted by 42 CFR Part 2. A general authorization for the release of medical or other information is NOT sufficient for this purpose (see § 2.32). The federal rules restrict any use of this information to investigate or prosecute with regard to a crime any patient with a substance use disorder, except as provided at §§ 2.12(c)(5) and 2.65."*; OR
- An abbreviated notice referencing § 2.32, OR
- The recipient's HIPAA Notice of Privacy Practices when the recipient is a HIPAA covered entity (post-2024).

Build the notice as part of every export/disclosure pipeline — it must travel with the record.

### 4. Segregation / segmentation — explicitly NOT required after TPO consent

§ 2.12(e) and § 2.24 (as amended) now state expressly that a Part 2 program, covered entity, or business associate that receives records under TPO consent is **NOT required to segregate or segment** those records from the rest of the patient's PHI.

**However**, the recipient still owes the **proceedings prohibition** on those records, which means downstream systems must be able to **identify Part 2-origin records** when responding to subpoenas, court orders, law-enforcement queries, or legal-discovery exports — even when records are commingled. Practical approach: store a per-record "Part 2 origin" provenance flag and apply the proceedings prohibition based on the flag, not on storage location.

### 5. Court orders, subpoenas, and law enforcement

**A subpoena alone is not enough.** Disclosure under legal compulsion requires a court order issued under § 2.61–2.67, which has specific procedural requirements (notice to the patient, opportunity to be heard, good-cause finding, narrow scope, judicial protective measures).

- **§ 2.61** — General rules for court orders.
- **§ 2.62** — Order authorizing disclosure of confidential communications.
- **§ 2.63** — Confidential communications.
- **§ 2.64** — Procedures and criteria for orders authorizing disclosures for noncriminal purposes.
- **§ 2.65** — Procedures and criteria for orders authorizing disclosures and use of records to investigate or prosecute a patient.
- **§ 2.66** — Procedures and criteria for orders authorizing disclosures and use of records to investigate or prosecute a Part 2 program or person holding records.
- **§ 2.67** — Orders authorizing the use of undercover agents and informants to investigate Part 2 programs.

**Law-enforcement queries** — including bench warrants, administrative summonses, agency requests, and informal asks — get the same answer: produce nothing without either a § 2.31 consent that specifically authorizes proceedings against the patient, or a § 2.61–2.67 court order. Treat "law enforcement is asking" as an escalation event, not a workflow.

**Safe harbor for investigative agencies** (2024 final rule) — an investigative agency seeking records receives Part 2 protection from sanctions if it took **reasonable diligence steps** to determine the provider was a Part 2 program before requesting records. Reasonable diligence includes checking SAMHSA's online treatment facility locator and reviewing the provider's Patient Notice or HIPAA NPP. EHRs do not need to implement the safe-harbor side, but should make Part 2 status visible in any provider-facing API so investigative agencies' diligence is possible.

### 6. Medical emergencies

§ 2.51 permits disclosure to medical personnel **to the extent necessary to meet a bona fide medical emergency** in which the patient's prior informed consent cannot be obtained.

Required logging (§ 2.51(c)):

- The name of the medical personnel to whom disclosure was made and their affiliation.
- The name of the person making the disclosure.
- Date and time of the disclosure.
- Nature of the emergency.

Build an emergency-disclosure path that captures these fields and routes the entry to the disclosure log; do not bypass logging to ship faster.

### 7. Public health, research, audit/evaluation

- **Public health** (§ 2.12(c)(6), as amended): disclosure to a public health authority is permitted **without consent** if the records are **de-identified under the HIPAA Privacy Rule standards** (45 CFR § 164.514(b)).
- **Research** (§ 2.52): disclosure for research is permitted under HIPAA-aligned conditions (IRB approval, privacy board waiver, data-use agreement, etc.). Disclosure of identifiable Part 2 data for research without a § 2.31 consent requires the recipient to follow HIPAA's research protections.
- **Audit and evaluation** (§ 2.53): permitted to specified persons performing audit/evaluation of the Part 2 program, with written agreement that the records will not be redisclosed except back to the program or as otherwise permitted by Part 2.

### 8. Patient Notice (§ 2.22)

The 2024 rule aligns Part 2 Patient Notice content with HIPAA Notice of Privacy Practices content. A Part 2 program must provide a written notice that includes:

- A description of the program's uses and disclosures of records.
- Patient rights (access, accounting, restriction, complaint).
- The program's duties.
- How to file a complaint with the program and with the Secretary.
- Effective date of the notice.

A HIPAA covered entity may use a single combined notice that satisfies both HIPAA NPP requirements and Part 2 Patient Notice requirements.

### 9. Breach notification

§ 2.16 (as amended) extends the **HIPAA Breach Notification Rule** (45 CFR §§ 164.400–414) to Part 2 records.

**Trigger**: any acquisition, access, use, or disclosure of unsecured Part 2 records not permitted by Part 2 that compromises the security or privacy of the record. Three Part 2 / HIPAA-aligned exceptions: unintentional access by workforce in good faith, inadvertent disclosure within the same organization, and good-faith belief that the recipient could not retain the information.

**Notifications**:

- **Patient**: written notification without unreasonable delay and within **60 calendar days** of discovery (45 CFR § 164.404).
- **HHS Secretary**: contemporaneously with patient notice if 500+ individuals affected; annually within 60 days of the end of the calendar year for breaches affecting <500 individuals (45 CFR § 164.408).
- **Media**: prominent media outlet in any state/jurisdiction where 500+ individuals are affected (45 CFR § 164.406).

**Risk assessment**: a four-factor risk assessment determines whether an impermissible use/disclosure is a "breach" under the rule (nature/extent of records, who accessed, whether records were actually acquired/viewed, mitigation). Build the four factors into your breach-triage workflow.

### 10. Patient rights — accounting, restriction, complaint

The 2024 rule aligns these with HIPAA:

- **Accounting of disclosures** (§ 2.25, aligned with 45 CFR § 164.528): patient may request a list of disclosures of their records over the prior six years, excluding TPO disclosures. Build a disclosure log that supports this query.
- **Right to request restriction** (§ 2.26, aligned with 45 CFR § 164.522): including the right to **restrict disclosure to a health plan** when the patient pays out-of-pocket in full for an item or service. This restriction is **mandatory** when properly requested — do not ship a workflow that lets the billing system claim against a plan in that case.
- **Right to file a complaint** (§ 2.4, 2024 addition): directly with the Secretary of HHS, and with the program. The patient cannot be retaliated against for filing.

### 11. Anti-discrimination (§ 2.12(c)(5))

Part 2 records, and the existence of a patient's SUD, **may not be used** to:

- Initiate or substantiate any criminal charges against the patient or conduct any investigation of the patient (subject to § 2.65 court orders);
- Deny or revoke employment, hiring, or promotion;
- Deny or revoke the sale, rental, or lease of housing;
- Deny access to courts, government-funded SUD treatment, or eligibility for government benefits;
- Or discriminate in education and educational benefits.

Build this into any product feature that exports SUD data to non-clinical contexts (employer wellness programs, school nurse modules, court-involved-youth reports).

### 12. Penalties (the 2024 change)

The 2024 rule applies **HIPAA's enforcement structure** to Part 2 violations:

- **Civil monetary penalties** under § 2.4(c) and 45 CFR § 160.404, applying HITECH tiers (adjusted annually for inflation; ranges below reflect amounts effective for violations after 2024-02-16, before subsequent inflation adjustments):
  - **Tier 1** (did not know, exercising reasonable diligence): minimum ~$137/violation, annual cap ~$2.1M/provision.
  - **Tier 2** (reasonable cause, not willful neglect): minimum ~$1,379, annual cap ~$2.1M.
  - **Tier 3** (willful neglect, corrected within 30 days): minimum ~$13,785.
  - **Tier 4** (willful neglect, not timely corrected): minimum ~$68,928.
- **Criminal penalties** under Social Security Act § 1177 (42 U.S.C. § 1320d-6): up to **$250,000 + 10 years** for knowingly obtaining/disclosing protected information under false pretenses or for personal gain or malicious harm.

OCR began accepting complaints alleging Part 2 violations on **February 16, 2026**, the compliance deadline. Use the current penalty figures from the most recent OCR enforcement notice — they shift annually.

---

## Cross-cutting design rules

### Part 2 vs. HIPAA — what still differs after 2024

| Topic | HIPAA | Part 2 (post-2024) |
|---|---|---|
| Consent model | Authorization required only for non-TPO; TPO does not require authorization | Written consent **required for all disclosures**, but a single TPO consent covers all future TPO |
| Proceedings against the patient | Allowed with HIPAA-permitted disclosure | **Prohibited** absent specific written consent or § 2.61–2.67 court order |
| Subpoena | Generally honored under § 164.512(e) | **Not sufficient** — court order required |
| Law-enforcement disclosure | Multiple permitted scenarios under § 164.512(f) | **Court order required** (§ 2.65 for patient investigation) |
| Anti-discrimination | None in HIPAA | § 2.12(c)(5) prohibits use for employment, housing, benefits, court |
| Breach notification | HIPAA Breach Notification Rule | **Same** rule applies (post-2024) |
| Patient notice | HIPAA NPP | Aligned content; combined notice permitted |
| Patient right to restrict | § 164.522 | Aligned |
| Accounting of disclosures | § 164.528 | Aligned |

**Rule of thumb for code:** if a record is Part 2-origin, the system must (a) honor every HIPAA rule AND (b) additionally prohibit use/disclosure in proceedings against the patient absent a § 2.31 proceeding-specific consent or a § 2.61–2.67 court order. The proceedings prohibition is the most commonly missed.

### State law (§ 2.20)

Part 2 does not preempt state laws that are **stricter**. If a state requires additional patient protections (e.g., minor consent rules, mental health record confidentiality), the system needs a per-state overlay. Most states have at least some additional protection.

### Telehealth and remote SUD services

Telehealth visits with a Part 2 program produce Part 2 records. The platform's data — chat transcripts, recordings, screen captures — are Part 2 records when associated with the encounter. Same rules apply.

### AI features touching SUD data

If an AI feature (drafting, summarization, scheduling, clinical-decision support, agentic workflows) reads or writes Part 2 records:

- The AI vendor is a **business associate** if it processes PHI (and Part 2 records held by a HIPAA-covered Part 2 program are PHI). Sign a BAA before sending Part 2 data to the vendor.
- Training data: do not include Part 2 records in training corpora absent de-identification per HIPAA standards.
- Logs and prompt caches: treat as Part 2 records — apply retention, access, audit, and breach-notification rules accordingly.

### De-identification

The 2024 rule lets you disclose Part 2 records to public health authorities **without consent** if de-identified per HIPAA standards (45 CFR § 164.514(b) — Safe Harbor or Expert Determination). Don't roll your own de-identifier. Use a vetted implementation.

---

## Common audit findings to design out

- **Treating Part 2 records as merely HIPAA-protected**. Most common failure mode. Build a record-level Part 2 provenance flag and check it on disclosure paths.
- **Missing or wrong "notice to accompany disclosure"** on outbound transmissions. Embed it in every export pipeline; don't leave it to humans to attach.
- **Subpoena response without court order**. Build the legal-process intake to recognize that a subpoena ≠ a § 2.61–2.67 court order.
- **Law-enforcement portals** or "verify patient" endpoints that respond without a court order.
- **TPO consent text that omits revocation language, expiration date, or signature/date fields.**
- **No way to revoke consent**, or revocation that doesn't propagate to active disclosures and the disclosure log.
- **No accounting-of-disclosures support** — TPO disclosures need not be on the accounting, but every other disclosure does.
- **Health plan claim submitted after a § 164.522(a) restriction request** when the patient paid out-of-pocket. This is a hard "must not" with no exception.
- **Analytics warehouse pulls** that include Part 2 records without consent or proper de-identification.
- **Breach risk assessment** that lacks the four-factor analysis or doesn't run inside the 60-day clock.
- **AI feature** that sends Part 2 records to a third-party LLM without a BAA, or that retains them in logs/caches without retention controls.
- **Combined notice** that satisfies HIPAA NPP requirements but not Part 2 Patient Notice (or vice versa).

---

## Schema and data-model implications (illustrative)

These are common implementation patterns that make the regulatory requirements easier to enforce — not regulatory requirements themselves.

- **Record-level Part 2 flag.** Every encounter, problem, medication, note, lab, attachment carries a `part2_record` boolean derived from the program/unit of origin, **never a UI toggle**. Application-layer authorization decisions key off this flag.
- **Programs registry.** A `program` model identifies each clinical program with `is_part2: bool`, `federally_assisted: bool`, `general_designation_allowed: bool`, and the legal-entity contact for breach response.
- **Consent model.** A polymorphic `consent` table with `consent_type` (`tpo_general`, `non_tpo_specific`, `proceeding_specific`, `emergency_documented`), required elements as columns (patient_id, programs_designation, info_scope, recipient, purpose, revocation_terms, expiration_event_or_date, signature_at, signed_by). Active vs. revoked vs. expired computed at query time.
- **Disclosure log.** Every outbound transmission of Part 2 records logs: record_ids, recipient, purpose, basis (`consent_id` | `court_order_id` | `emergency` | `audit` | `public_health_deid` | `research`), accompanying-notice variant, date, the user/system that authorized. Supports accounting-of-disclosures queries and breach-incident scoping.
- **Restriction log.** Patient-initiated restrictions (§ 2.26 / § 164.522), each with the restricted recipient (e.g., specific health plan), service scope, effective-from date, and an enforcement check that runs at claim-submission time.
- **Breach incident model.** Incident, affected-patient set, four-factor risk assessment, notification due-dates (patient, HHS, media), notification-sent timestamps. CI alert if any due-date is approaching.
- **Court-order intake.** Distinct from generic legal-process intake. Captures which § 2.6x section the order issues under, judicial findings, scope, and protective measures.
- **Disclosure pipelines** (claims, HIE, FHIR API, analytics export) gate on `part2_record == true` and check the consent / order / exception path before allowing the record out.
- **AI integration**: every prompt sent to an LLM with Part 2 data is logged as a disclosure; vendor inclusion gated by an active BAA flag on the vendor record.

---

## When to escalate to a human

You **must not**:

- Decide whether a particular record is "Part 2" based on heuristics alone. The program-of-origin determination is a compliance decision.
- Generate consent text for production use without legal review. Sample consents in the SAMHSA guidance are starting points, not drop-ins.
- Respond to a subpoena, law-enforcement request, or court order on the system's behalf. Always route to the program's privacy officer / legal counsel.
- Treat an LLM-generated breach-risk assessment as final. The four factors require human judgment.

Escalate to a human (privacy officer, compliance, legal counsel) when:

- A new disclosure path is proposed (new payer, new HIE, new vendor, new state, new AI feature).
- A consent's required fields are missing or ambiguous and the patient is no longer reachable.
- A subpoena, warrant, summons, or court order arrives.
- A potential breach is detected.
- A patient files a complaint or requests an accounting / restriction / amendment.
- State law appears to add requirements the system does not currently honor.

---

## Source documents (verify against these — they win over this skill)

**Authoritative (regulatory):**

- 42 CFR Part 2 (current eCFR) — https://www.ecfr.gov/current/title-42/chapter-I/subchapter-A/part-2
- HHS Final Rule, *Confidentiality of Substance Use Disorder (SUD) Patient Records*, 89 FR 12472, Document 2024-02544, RIN 0945-AA16 — published 2024-02-16, effective 2024-04-16, compliance 2026-02-16.
  - Federal Register page: https://www.federalregister.gov/documents/2024/02/16/2024-02544/confidentiality-of-substance-use-disorder-sud-patient-records
  - govinfo.gov PDF: https://www.govinfo.gov/content/pkg/FR-2024-02-16/pdf/2024-02544.pdf
- 42 U.S.C. § 290dd-2 — statutory authority.
- HIPAA Privacy Rule (45 CFR Part 164 Subpart E), Breach Notification Rule (45 CFR §§ 164.400–414), Enforcement Rule (45 CFR Part 160 Subpart D) — cross-referenced by the 2024 final rule.

**Practical guidance:**

- HHS Fact Sheet — 42 CFR Part 2 Final Rule: https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html
- HHS Understanding Confidentiality of SUD Patient Records ("Part 2"): https://www.hhs.gov/hipaa/for-professionals/special-topics/hipaa-part-2/index.html
- SAMHSA SUD Treatment Facility Locator (used for investigative-agency safe harbor): https://findtreatment.samhsa.gov/
- OCR Civil Enforcement Program announcements (current OCR site).

**State law overlays:** consult the state board of behavioral health / health department for the jurisdiction(s) the program serves. State protections that are stricter than Part 2 still apply (§ 2.20).

If this skill conflicts with the linked authorities, the authorities win. Open an issue or PR when the authorities change.
