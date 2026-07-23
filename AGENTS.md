# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

## Validation policy

Choose the validation lane from the change surface:

- **Routine:** documentation, tests, content, CI/configuration, and small bounded fixes that do not cross a higher-risk boundary use repository-native checks plus hosted CI. Never invoke no-mistakes.
- **Medium risk:** skill-behavior changes that do not cross a high-risk boundary use review-only `no-mistakes axi run --skip=test,document,lint,push,pr,ci`, then targeted tests and a direct PR.
- **High risk:** PHI/privacy, clinical or regulatory compliance scope, security, destructive operations, or broad/high-blast-radius changes use the full no-mistakes pipeline. Root `.no-mistakes.yaml` governs this lane.

Honor an explicit `/no-mistakes` request. Routine requests to commit, push, ship, validate, or open a PR do not imply no-mistakes.

The captain approves every merge; agents must not merge. [CONTRIBUTING.md](CONTRIBUTING.md) remains authoritative for clinical and regulatory content boundaries, citations, source metadata, domain review, and contributor requirements. The authoritative native commands are in [.github/workflows/ci.yml](.github/workflows/ci.yml); keep `.no-mistakes.yaml` aligned with that workflow and do not add independent quality gates there.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
