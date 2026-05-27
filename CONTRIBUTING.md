# Contributing

Thanks for considering a contribution. Compliance content has higher stakes than typical code, so the bar is a little higher than usual — and a little more boring. Read this once before opening a PR.

## What we accept

- **New skills in domains the public ecosystem doesn't already cover well**: regulatory programs (42 CFR Part 2, ONC Information Blocking, CCBHC), behavioral-health-specific clinical documentation, state Medicaid behavioral health rules, accreditation-driven documentation (Joint Commission BH, CARF).
- **Updates to existing skills** when an underlying authority changes. Cite the new authority and the effective date.
- **Improvements to the source-checking infrastructure**, issue templates, contribution flow, or documentation.

## What we don't accept

- **Forks of skills that are already well maintained elsewhere.** FHIR, generic ICD-10 lookup, NPI registry, and generic HIPAA are out of scope — send those PRs to [anthropics/healthcare](https://github.com/anthropics/healthcare) or the canonical maintainer and we'll link from the README.
- **Skills without primary-authority citations.** Every regulatory claim must reference the source (CFR section, BHIN number, ONC paragraph, state code) inline. A reviewer needs to be able to verify the claim, not your memory of it.
- **Skills without a populated `references/sources.yml`.** Source-checking is non-negotiable for published compliance content.
- **Skills that have not been read by someone with domain expertise.** If you're not that person, open a draft PR with the label `needs-domain-review` and we'll find one before merging.

## Skill submission requirements

1. **Directory shape.**

   ```
   skills/<name>/
   ├── SKILL.md
   ├── agents/openai.yaml
   ├── references/
   │   └── sources.yml
   └── scripts/
   ```

2. **YAML frontmatter** at the top of `SKILL.md`:

   ```yaml
   ---
   name: <kebab-case-skill-name>
   description: <one paragraph — when to trigger, what it does>
   license: MIT
   metadata:
     last_verified: 2026-MM-DD
     owner: <github-handle or team>
     sources_file: references/sources.yml
   ---
   ```

3. **Disclaimer header** as the first line of the body — copy verbatim from `SKILL_TEMPLATE.md`.

4. **Citation for every regulatory claim.** Inline format: `(BHIN 23-068 § (d)(2))`, `(42 CFR § 2.31(a))`, `(45 CFR § 164.524)`. Future reviewers must be able to verify against the cited authority without reading your mind.

5. **`references/sources.yml` populated** with every authority the skill cites. Run

   ```sh
   python3 skills/<name>/scripts/check_sources.py skills/<name> --write
   ```

   on a clean checkout to capture initial hashes. Commit the result.

## Maintenance commitment

By submitting a skill you commit to a **quarterly review** — or to designating a maintainer who will. Skills that go six months past their `last_verified` date without a refresh are marked stale; skills twelve months past are moved to `skills/archive/`.

If your circumstances change and you can't maintain a skill anymore, open an issue requesting a co-maintainer. Don't ghost.

## PR checklist

Copy this into your PR description:

```
- [ ] Every regulatory claim in the skill body cites the primary authority inline.
- [ ] `references/sources.yml` includes every cited authority with `expected_sha256` populated for fetchable sources, or `type: manual` with a review note for non-fetchable authorities.
- [ ] `metadata.last_verified` date in frontmatter matches today's review.
- [ ] `python3 skills/<name>/scripts/check_sources.py skills/<name>` passes.
- [ ] A reviewer with domain expertise has read the skill end-to-end.
- [ ] Disclaimer header is present at the top of the body.
```

## Tone of skill content

- Imperative, concise, person-first.
- Cite first, explain second.
- Don't invent best practices — stick to what the cited authority or canonical guide says, and label clearly when something is a "common implementation pattern" rather than a regulatory requirement.
- Plain language. Members and patients may read records produced by software the skill influences.

## Reviewer responsibilities

If you're reviewing a PR:

- Verify two random citations against the linked authority. If either is wrong, the contributor needs to recheck everything.
- Confirm `references/sources.yml` includes every authority the skill body cites.
- Confirm `metadata.last_verified` matches the PR date.
- Look for "soft" claims that should be harder ("providers must…" without a citation) or harder claims that should be softer ("organizations typically…" presented as regulation).

Thanks for keeping compliance content honest.
