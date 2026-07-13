# ehr-codex-skills

A public Codex plugin and portable Agent Skills collection for EHR and behavioral-health software — focused on regulatory and clinical-documentation gaps that general public skill collections do not cover well.

Each packaged skill has a `SKILL.md` plus supporting source metadata, checks, and host manifests. The skills are loadable by [Claude Code](https://github.com/anthropics/claude-code), Codex, Gemini CLI, Cursor, and other [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)-compatible runtimes.

## What's here

| Skill | Covers | Status | Last verified |
|---|---|---|---|
| [42-cfr-part-2](skills/42-cfr-part-2/SKILL.md) | SAMHSA Confidentiality of SUD Patient Records — 2024 final rule (89 FR 12472), single TPO consent, redisclosure, court orders, breach notification, anti-discrimination, HITECH-tier penalties (OCR enforcement active since 2026-02-16) | stable | 2026-05-27 |
| [calmhsa-medi-cal-documentation](skills/calmhsa-medi-cal-documentation/SKILL.md) | California Medi-Cal behavioral health documentation (SMHS / DMC / DMC-ODS) per DHCS BHIN 23-068 and the CalMHSA clinical documentation guides | stable | 2026-05-26 |

Planned (in order of next-up):

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

## Installing

Use the native plugin installer where the host supports it. Symlinking or vendoring individual skills remains available for other runtimes.

A symlink avoids duplicate local copies, but it does not update the Git checkout. Pull updates explicitly, then restart the host so it reloads the skill catalog:

```sh
git -C /path/to/ehr-codex-skills pull --ff-only
```

### Codex — install as a plugin (recommended)

The repository includes a Codex manifest and marketplace catalog, so the complete collection can be installed as one versioned plugin:

```sh
codex plugin marketplace add 1nickfisher/ehr-codex-skills --ref main
codex plugin add ehr-codex-skills@ehr-codex-skills
```

Start a new Codex task after installation so the bundled skills are discovered.

Codex installs a cached plugin snapshot. Pushing new repository content does not replace that snapshot automatically: every change that must reach installed plugin snapshots must bump the version in both plugin manifests. Then refresh the marketplace installation:

```sh
codex plugin marketplace upgrade ehr-codex-skills
```

Start another new task after updating.

### Claude Code — manifest compatibility

A `.claude-plugin/plugin.json` ships at the repo root and validates the collection as a Claude Code plugin. This repository does not yet publish a Claude marketplace catalog, so it does not claim a direct `/plugin install` command. Until that catalog is added and tested, use the single-skill symlink flow below.

```sh
claude plugin validate .
```

### Codex — symlink individual skills (alternative)

The `agents/openai.yaml` per skill provides Codex's interface manifest (display name, default prompt, implicit-invocation policy). If plugin installation is unavailable, symlink each skill directory instead:

```sh
ln -s "$(pwd)/skills/calmhsa-medi-cal-documentation" \
  ~/.codex/skills/calmhsa-medi-cal-documentation
ln -s "$(pwd)/skills/42-cfr-part-2" \
  ~/.codex/skills/42-cfr-part-2
```

Restart Codex afterwards.

### Symlink for any Agent Skills-compatible runtime

For Gemini CLI, Cursor, or other hosts, the SKILL.md is the universal interface. Symlink the skill directory into whatever path the host expects:

```sh
# Claude Code (single-skill alternative to plugin install)
ln -s "$(pwd)/skills/42-cfr-part-2" ~/.claude/skills/42-cfr-part-2
```

### Vendor — inside a product repo (pin and review)

When the skill collection is consumed by a product codebase that needs to pin a specific version and review updates before they reach production:

```sh
# Git submodule pinned to a commit
git submodule add -b main git@github.com:1nickfisher/ehr-codex-skills.git vendor/ehr-codex-skills

# Or copy a skill directly
cp -r <ehr-codex-skills>/skills/42-cfr-part-2 docs/skills/
```

## Freshness model

Compliance content rots silently — a regulation changes, the prose stays the same, and the rule quietly stops being right. This repo's defence:

1. Every skill carries a `last_verified` date in its frontmatter metadata.
2. Every skill has a companion `references/sources.yml` enumerating the regulatory authorities it depends on, with a baseline for each automatable source.
3. `skills/<name>/scripts/check_sources.py` checks each automatable authority, compares baselines, and reports changes. Sources marked `type: manual` remain on the human-review list.
4. A weekly GitHub Action runs the monitoring check and **opens or updates an issue** when an automatable authority changes. It never auto-edits a skill or pulls updates into installed clones; a human reads the new authority and decides what (if anything) needs updating.

Current coverage is 19 automated and 5 manual-review sources for `42-cfr-part-2`, and 6 automated and 12 manual-review sources for `calmhsa-medi-cal-documentation`.

Supported source types:

- Direct fetchable sources use `expected_sha256` plus HTTP `ETag` / `Last-Modified` when available.
- DHCS PDFs that are bot-protected at the origin can use `type: wayback`; the checker reads the Internet Archive CDX API and treats a new archive digest as a human-review signal.
- eCFR sections can use `type: ecfr`; the checker reads the eCFR API's latest issue date and hashes the cited section XML.
- Sources that cannot be checked safely remain `type: manual`.

Run locally:

```sh
python3 skills/calmhsa-medi-cal-documentation/scripts/check_sources.py skills/calmhsa-medi-cal-documentation
```

After a human review confirms the skill is still accurate (or has been updated), bump the baseline:

```sh
python3 skills/calmhsa-medi-cal-documentation/scripts/check_sources.py skills/calmhsa-medi-cal-documentation --write
```

To ask Internet Archive to refresh Wayback coverage during a manual run:

```sh
python3 skills/calmhsa-medi-cal-documentation/scripts/check_sources.py skills/calmhsa-medi-cal-documentation --request-wayback-save
```

### Email alerts

When the weekly source check detects a changed, missing, or unreachable source, the GitHub Action opens an issue. It can also send an SMTP email if these repository secrets are configured:

| Secret | Purpose |
|---|---|
| `SOURCE_ALERT_SMTP_HOST` | SMTP server hostname. |
| `SOURCE_ALERT_SMTP_PORT` | SMTP port; defaults to `587` when unset. Use `465` for implicit TLS. |
| `SOURCE_ALERT_SMTP_USERNAME` | SMTP username. |
| `SOURCE_ALERT_SMTP_PASSWORD` | SMTP password or provider API key. |
| `SOURCE_ALERT_EMAIL_TO` | Alert recipient email address. |
| `SOURCE_ALERT_EMAIL_FROM` | Sender address accepted by the SMTP provider. |

If any required email secret is missing, the workflow still opens the GitHub issue and logs that email delivery was skipped.

## License

[MIT](LICENSE). Both the scripts and the skill content are MIT-licensed.

## Disclaimer

**This is guidance, not legal or clinical advice.** Read [DISCLAIMER.md](DISCLAIMER.md) before using any skill in a clinical or compliance context. Cited authorities are the source of truth — verify them current before relying on any rule.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The bar for new skills is: cited primary authority for every regulatory claim, populated `references/sources.yml`, current `last_verified` date, and review by someone with domain expertise.
