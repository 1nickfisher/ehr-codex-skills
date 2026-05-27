---
name: <kebab-case-skill-name>
description: <One paragraph — when this skill should trigger and what it does. Include both what the skill covers AND specific contexts for use. Lean slightly "pushy" so the skill triggers when it could help, not only when explicitly invoked. Example phrasing: "Apply current X rules for Y — use whenever building, reviewing, or modifying Z, including when the request only mentions ...". Keep under ~120 words; the description is loaded into the agent's context up-front.>
license: MIT
metadata:
  last_verified: 2026-MM-DD
  owner: <github-handle-or-team>
  sources_file: references/sources.yml
---

> **Guidance, not legal or clinical advice.** This skill synthesizes publicly available authorities for use by software development agents. The cited authorities — not this skill body — are the source of truth. Verify they remain current before relying on any specific rule. See [DISCLAIMER.md](../../DISCLAIMER.md).

# <Skill Title>

One-paragraph framing. What the skill is about, who issued the rules it covers, the version/date that defines "current," and the conflict-of-authority order (e.g., "If a county contract conflicts with the BHIN, the BHIN wins").

The two or three primary authorities, named explicitly:

1. **<Authority 1>** (effective date, issuer) — <link>. <One-line description of what it controls.>
2. **<Authority 2>** — <link>.

## When to apply this skill

Bulleted, concrete trigger list. Be specific about which workflows pull this skill in: feature builds, reviews, validations, copy/UX, schema changes, billing logic, etc. The reader should be able to look at their current task and decide in seconds whether this skill is in scope.

Skip only if: <when the skill genuinely does not apply>.

## How to act on it

Numbered, short rules for the agent's behavior when the skill is active:

1. **Cite the source** — name the section number every time. Reviewers need to verify against authority, not memory.
2. **State the minimum** — don't add stricter rules than the regulation imposes; surface stricter county/local rules as configuration, not hard-coded defaults.
3. **Default to person-first, plain-language copy** in any user-visible text.
4. **Escalate ambiguity** — name the human or team to ask when the regulation is unclear for the specific context.

---

## The core rules

Use a top-level section per artifact, workflow, or topic. Inside each, state:

- The **required elements** with citations.
- The **timeliness** rules.
- The **scope of practice / authority** constraints.
- The **exceptions** that commonly trip people up.

Use small tables for code-vs-discipline matrices, timeliness summaries, allowable-vs-prohibited combinations. Tables are easier to scan than prose.

### Example: <Artifact Name>

Body. Include a short "common audit findings" list at the end of each major section if relevant — the agent should design against the failure modes auditors actually find.

---

## Cross-cutting rules

Topics that affect multiple artifacts: access criteria, telehealth, signatures, supervision, etc. Keep each subsection tight.

---

## Common audit findings to design out

A flat list of the things real auditors cite. Each item references the rule it violates. This is one of the most useful sections of any compliance skill.

---

## Schema / data-model implications (illustrative)

If the skill is likely to inform software design, include a short, illustrative section on schema patterns that support the rules. Mark clearly as illustrative — these are not requirements.

---

## When to escalate to a human

Bulleted list of situations where the agent should stop and ask for clinician / counsel / compliance review instead of generating output.

---

## Source documents

List authorities in two groups:

**Authoritative (regulatory):**

- <Citation> — <URL>
- ...

**Practical guidance:**

- <Citation> — <URL>
- ...

If this skill conflicts with the linked authorities, the authorities win. Open an issue or PR when the authorities change.
