---
name: Source change
about: An authority cited by a skill has changed and needs human review.
title: "Source change detected — <skill> — <YYYY-MM-DD>"
labels: source-change
---

A check detected that one or more authorities cited by a skill have changed.

**Do not auto-edit the skill.** Read the new source against the current `SKILL.md` and decide what (if anything) needs to update.

## Skill(s) affected

<filled by CI, or describe manually>

## Changes

<paste the output of `python scripts/check_sources.py skills/<name> --markdown`>

## Review checklist

- [ ] Read the changed authority in full (not just the diff).
- [ ] Compare against the affected `SKILL.md` sections paragraph by paragraph.
- [ ] If the skill needs to change: open a separate PR with the edit; do not bundle the edit with the baseline update.
- [ ] If the skill is still accurate: bump `last_verified` in the skill's frontmatter and run `python scripts/check_sources.py <skill> --write` to refresh the baseline.
- [ ] Close this issue with a one-line note recording the decision (kept skill / amended skill / superseded by PR #).
