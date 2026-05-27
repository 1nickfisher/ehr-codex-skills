#!/usr/bin/env python3
"""Check that the authorities a skill cites haven't changed since last review.

Each skill directory contains a `references/sources.yml` enumerating the regulatory
authorities the skill is grounded in. This script fetches each authority,
computes a SHA-256 hash plus HTTP ETag / Last-Modified, and reports whether
anything has changed since the last recorded baseline.

By design, the script never edits the SKILL.md body — only `references/sources.yml`,
and only with `--write`. Compliance content needs a human to read a changed
authority and decide what (if anything) the skill should say differently.

Exit codes:
  0  All sources unchanged.
  2  At least one source changed, missing a baseline, or was unreachable.
  1  Usage or fatal error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "PyYAML is required. Install with: pip install -r scripts/requirements.txt\n"
    )
    sys.exit(1)


USER_AGENT = (
    "Mozilla/5.0 (compatible; ehr-codex-skills source-checker; "
    "+https://github.com/) Safari/605"
)


def fetch(url: str, expected_type: str | None = None, timeout: int = 60) -> dict:
    """Fetch a URL and report content + headers.

    Detects bot-protection wrappers: sites behind Imperva/Incapsula/Cloudflare
    challenge pages return a small HTML JS challenge in place of the real
    document, but with HTTP 200. If the URL is supposed to be a PDF and the
    response is small HTML, surface that as `bot_protected` instead of
    silently hashing the challenge page.
    """
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        content_type = (resp.headers.get("Content-Type") or "").lower()

        bot_protected = (
            url.lower().endswith(".pdf")
            and "text/html" in content_type
            and len(body) < 2048
        )

        return {
            "status": resp.status,
            "etag": resp.headers.get("ETag"),
            "last_modified": resp.headers.get("Last-Modified"),
            "content_type": content_type,
            "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
            "bot_protected": bot_protected,
        }


def check_skill(skill_dir: Path, write: bool = False) -> dict:
    sources_path = skill_dir / "references" / "sources.yml"
    if not sources_path.exists():
        sources_path = skill_dir / "sources.yml"
    if not sources_path.exists():
        return {
            "skill": skill_dir.name,
            "path": str(skill_dir),
            "error": "references/sources.yml missing",
        }

    data = yaml.safe_load(sources_path.read_text()) or {}
    sources = data.get("sources") or []
    today = date.today().isoformat()
    changes: list[dict] = []

    for src in sources:
        url = src.get("url")
        sid = src.get("id") or url or "<unknown>"

        if src.get("type") == "manual":
            # Some authorities are not fetchable (paywalled, login-gated,
            # bot-protected, statute in an aspx viewer). Skip but count as
            # checked — the source-of-truth is the cited human-review
            # process, not an automated hash.
            continue

        if not url:
            changes.append({"id": sid, "status": "no_url"})
            continue

        try:
            current = fetch(url)
        except (URLError, HTTPError, TimeoutError) as e:
            changes.append({"id": sid, "status": "unreachable", "error": str(e)})
            continue

        if current["bot_protected"]:
            changes.append(
                {
                    "id": sid,
                    "status": "bot_protected",
                    "url": url,
                    "content_type": current["content_type"],
                    "bytes": current["bytes"],
                    "note": "Server returned a JS-challenge page instead of the document. "
                    "Set type: manual and verify by hand, or point url at a stable mirror.",
                }
            )
            continue

        expected = src.get("expected_sha256")
        if expected and current["sha256"] != expected:
            changes.append(
                {
                    "id": sid,
                    "status": "changed",
                    "url": url,
                    "old_hash": expected,
                    "new_hash": current["sha256"],
                    "etag": current.get("etag"),
                    "last_modified": current.get("last_modified"),
                }
            )
        elif not expected:
            changes.append(
                {
                    "id": sid,
                    "status": "missing_baseline",
                    "url": url,
                    "new_hash": current["sha256"],
                }
            )

        if write:
            src["expected_sha256"] = current["sha256"]
            if current.get("etag"):
                src["etag"] = current["etag"]
            if current.get("last_modified"):
                src["last_modified"] = current["last_modified"]
            src["last_verified_date"] = today

    if write:
        data["sources"] = sources
        data.setdefault("meta", {})["last_write"] = today
        sources_path.write_text(
            yaml.safe_dump(data, sort_keys=False, width=100, allow_unicode=True)
        )

    return {
        "skill": skill_dir.name,
        "path": str(skill_dir),
        "checked": len(sources),
        "changes": changes,
    }


def render_markdown(reports: list[dict]) -> str:
    lines: list[str] = []
    for r in reports:
        lines.append(f"## `{r['skill']}`")
        if "error" in r:
            lines.append(f"- **error**: {r['error']}")
            continue
        lines.append(f"- sources checked: {r['checked']}")
        if not r["changes"]:
            lines.append("- status: **unchanged**")
            continue
        lines.append("- status: **changes detected**")
        for c in r["changes"]:
            lines.append(f"  - `{c['id']}`: **{c['status']}**")
            for k, v in c.items():
                if k in {"id", "status"} or v is None:
                    continue
                lines.append(f"    - {k}: `{v}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_text(reports: list[dict]) -> str:
    lines: list[str] = []
    for r in reports:
        lines.append(f"=== {r['skill']} ===")
        if "error" in r:
            lines.append(f"  error: {r['error']}")
            continue
        lines.append(f"  sources checked: {r['checked']}")
        if not r["changes"]:
            lines.append("  status: unchanged")
            continue
        lines.append("  status: changes detected")
        for c in r["changes"]:
            lines.append(f"  - {c['id']}: {c['status']}")
            for k, v in c.items():
                if k in {"id", "status"} or v is None:
                    continue
                lines.append(f"      {k}: {v}")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Check skill source manifests against live URLs.",
    )
    p.add_argument(
        "paths",
        nargs="+",
        help="Skill directories to check (each must contain references/sources.yml).",
    )
    p.add_argument(
        "--write",
        action="store_true",
        help="Update references/sources.yml with current hashes/etags. "
        "Use only after a human has reviewed each change.",
    )
    fmt = p.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="Emit JSON.")
    fmt.add_argument("--markdown", action="store_true", help="Emit Markdown.")
    args = p.parse_args()

    reports: list[dict] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            reports.append({"skill": path.name or str(path), "error": "not found"})
            continue
        if not path.is_dir():
            reports.append({"skill": path.name, "error": "not a directory"})
            continue
        reports.append(check_skill(path, write=args.write))

    if args.json:
        print(json.dumps(reports, indent=2))
    elif args.markdown:
        sys.stdout.write(render_markdown(reports))
    else:
        sys.stdout.write(render_text(reports))

    any_problem = any(r.get("changes") or r.get("error") for r in reports)
    return 2 if any_problem else 0


if __name__ == "__main__":
    sys.exit(main())
