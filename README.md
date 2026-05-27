# ehr-codex-skills

Private Agent Skills for EHR and behavioral-health software — focused on regulatory, clinical-documentation, release, and operational gaps that general public skill collections do not cover well.

Each skill is a single `SKILL.md` (YAML frontmatter + markdown body) loadable by [Claude Code](https://github.com/anthropics/claude-code), Codex, Gemini CLI, Cursor, and any other [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)-compatible runtime.

## What's here

| Skill | Covers | Status | Last verified |
|---|---|---|---|
| [calmhsa-medi-cal-documentation](skills/calmhsa-medi-cal-documentation/SKILL.md) | California Medi-Cal behavioral health documentation (SMHS / DMC / DMC-ODS) per DHCS BHIN 23-068 and the CalMHSA clinical documentation guides | stable | 2026-05-26 |

Planned (in order of next-up):

- `42-cfr-part-2` — SAMHSA confidentiality of SUD patient records (2024 final rule). No mature public skill exists.
- `onc-information-blocking` — ONC Cures Act final rule, the eight exceptions, actor obligations.
- `bh-screening-instruments` — PHQ-9, GAD-7, AUDIT, DAST-10, C-SSRS, CANS, ACEs, PSC-35: scoring, reuse cadences, scope of administration.
- `zero-suicide` — SAMHSA Zero Suicide framework.
- `ccbhc` — Federal CCBHC certification standards.
- `ncpdp-script-epcs-pdmp` — e-prescribing, EPCS, and PDMP integration.
- Additional state-Medicaid BH documentation skills (NY, TX, MA, OH, WA, …) using `calmhsa-medi-cal-documentation` as the template.

## What's deliberately not here

Skills for FHIR, generic ICD-10 lookup, NPI registry, and similar commodity healthcare tooling are well covered upstream. Install those alongside this collection rather than expecting duplicates here:

- [anthropics/healthcare](https://github.com/anthropics/healthcare) — official FHIR Developer skill, prior authorization review, ICD-10 codes, NPI registry, CMS coverage, PubMed.
- [Sushegaad/Claude-Skills-Governance-Risk-and-Compliance](https://github.com/Sushegaad/Claude-Skills-Governance-Risk-and-Compliance) — community GRC collection (HIPAA, SOC 2, NIST, GDPR, Section 508, WCAG, …). PRs to add behavioral-health context are a better fit upstream than a fork here.

## Installing a skill

Two patterns work; both treat this repo as the source of truth and avoid the stale-copy problem.

**Symlink** — recommended when you control your development environment and want updates on `git pull`:

```sh
# Claude Code
ln -s "$(pwd)/skills/calmhsa-medi-cal-documentation" \
  ~/.claude/skills/calmhsa-medi-cal-documentation

# Codex
ln -s "$(pwd)/skills/calmhsa-medi-cal-documentation" \
  ~/.codex/skills/calmhsa-medi-cal-documentation
```

Restart your agent afterwards so it re-reads skill metadata.

**Vendor** — recommended inside a product repo where you want to pin a specific version and review updates before they reach your codebase:

```sh
# Pin to a commit and copy the skill directory in.
git submodule add -b main git@github.com:1nickfisher/ehr-codex-skills.git vendor/ehr-codex-skills
# or simply: cp -r <ehr-codex-skills>/skills/calmhsa-medi-cal-documentation docs/skills/
```

## Freshness model

Compliance content rots silently — a regulation changes, the prose stays the same, and the rule quietly stops being right. This repo's defence:

1. Every skill carries a `last_verified` date in its frontmatter metadata.
2. Every skill has a companion `references/sources.yml` enumerating the regulatory authorities it depends on, with the SHA-256 hash and HTTP `ETag` / `Last-Modified` for each fetchable source.
3. `skills/<name>/scripts/check_sources.py` fetches each authority, compares hashes, and reports changes.
4. A weekly GitHub Action runs the check and **opens an issue** when an authority changes — it never auto-edits a skill. A human reads the new authority and decides what (if anything) needs updating.

Run locally:

```sh
python3 skills/calmhsa-medi-cal-documentation/scripts/check_sources.py skills/calmhsa-medi-cal-documentation
```

After a human review confirms the skill is still accurate (or has been updated), bump the baseline:

```sh
python3 skills/calmhsa-medi-cal-documentation/scripts/check_sources.py skills/calmhsa-medi-cal-documentation --write
```

## License

[MIT](LICENSE). Both the scripts and the skill content are MIT-licensed.

## Disclaimer

**This is guidance, not legal or clinical advice.** Read [DISCLAIMER.md](DISCLAIMER.md) before using any skill in a clinical or compliance context. Cited authorities are the source of truth — verify them current before relying on any rule.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The bar for new skills is: cited primary authority for every regulatory claim, populated `references/sources.yml`, current `last_verified` date, and review by someone with domain expertise.
