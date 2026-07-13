#!/usr/bin/env python3
"""Check that the authorities a skill cites haven't changed since last review.

Each skill directory contains a `references/sources.yml` enumerating the regulatory
authorities the skill is grounded in. This script fetches each automatable
authority, computes a SHA-256 hash plus HTTP ETag / Last-Modified, and reports
whether anything has changed since the last recorded baseline. Sources marked
`type: manual` remain part of the report but require human review.

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
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlencode
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
WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"
WAYBACK_WEB_URL = "https://web.archive.org/web"
WAYBACK_SAVE_URL = "https://web.archive.org/save"
ECFR_VERSIONS_URL = "https://www.ecfr.gov/api/versioner/v1/versions"
ECFR_FULL_URL = "https://www.ecfr.gov/api/versioner/v1/full"


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


def fetch_wayback_latest(url: str, from_timestamp: str | None = None) -> dict:
    params = {
        "url": url,
        "output": "json",
        "limit": "-5",
        "fl": "timestamp,original,mimetype,statuscode,digest,length",
        "filter": ["statuscode:200", "mimetype:application/pdf"],
    }
    if from_timestamp:
        params["from"] = from_timestamp

    endpoint = f"{WAYBACK_CDX_URL}?{urlencode(params, doseq=True)}"
    req = Request(endpoint, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")

    rows = json.loads(body) if body.strip() else []
    if not rows or len(rows) == 1:
        return {"status": "wayback_no_snapshot", "cdx_url": endpoint}

    latest = rows[-1]
    return {
        "status": "ok",
        "cdx_url": endpoint,
        "timestamp": latest[0],
        "original": latest[1],
        "mimetype": latest[2],
        "statuscode": latest[3],
        "digest": latest[4],
        "length": latest[5],
    }


def fetch_wayback_archived_hash(url: str, timestamp: str) -> dict:
    archived_url = f"{WAYBACK_WEB_URL}/{timestamp}id_/{quote(url, safe=':/?&=%')}"
    req = Request(archived_url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        body = resp.read()
        return {
            "url": archived_url,
            "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
            "content_type": (resp.headers.get("Content-Type") or "").lower(),
        }


def request_wayback_save(url: str) -> None:
    save_url = f"{WAYBACK_SAVE_URL}/{quote(url, safe=':/?&=%')}"
    req = Request(save_url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        resp.read()


def check_wayback_source(
    src: dict,
    sid: str,
    today: str,
    write: bool,
    should_request_save: bool = False,
) -> dict | None:
    url = src.get("url")
    if not url:
        return {"id": sid, "status": "no_url"}

    current = fetch_wayback_latest(url, src.get("wayback_timestamp"))
    if current["status"] != "ok":
        return {"id": sid, "status": current["status"], "url": url}

    if should_request_save:
        request_wayback_save(url)

    expected_digest = src.get("wayback_digest")
    expected_timestamp = src.get("wayback_timestamp")
    if expected_digest and current["digest"] != expected_digest:
        change = {
            "id": sid,
            "status": "wayback_candidate_changed",
            "url": url,
            "old_digest": expected_digest,
            "new_digest": current["digest"],
            "old_timestamp": expected_timestamp,
            "new_timestamp": current["timestamp"],
            "mimetype": current["mimetype"],
            "length": current["length"],
            "note": "Wayback observed a new archived payload. Human review required.",
        }
    elif not expected_digest:
        change = {
            "id": sid,
            "status": "missing_wayback_baseline",
            "url": url,
            "new_digest": current["digest"],
            "new_timestamp": current["timestamp"],
            "mimetype": current["mimetype"],
            "length": current["length"],
        }
    else:
        change = None

    if write:
        archived = fetch_wayback_archived_hash(url, current["timestamp"])
        src["wayback_digest"] = current["digest"]
        src["wayback_timestamp"] = current["timestamp"]
        src["wayback_mimetype"] = current["mimetype"]
        src["wayback_length"] = current["length"]
        src["wayback_archived_sha256"] = archived["sha256"]
        src["wayback_archived_url"] = archived["url"]
        src["last_verified_date"] = today

    return change


def fetch_ecfr_section(title: str, part: str, section: str) -> dict:
    versions_url = f"{ECFR_VERSIONS_URL}/title-{title}"
    req = Request(versions_url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        versions = json.loads(resp.read().decode("utf-8"))

    latest_date = versions.get("meta", {}).get("latest_issue_date")
    if not latest_date:
        raise ValueError(f"eCFR title {title} did not return latest_issue_date")

    full_url = f"{ECFR_FULL_URL}/{latest_date}/title-{title}.xml?part={part}"
    req = Request(full_url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        xml = resp.read().decode("utf-8")

    match = re.search(
        rf'(<DIV\d+\s+N="{re.escape(section)}"\s+TYPE="SECTION"[\s\S]*?</DIV\d+>)',
        xml,
    )
    if not match:
        raise ValueError(f"eCFR section {title} CFR {section} not found in part {part}")

    section_xml = match.group(1).encode("utf-8")
    return {
        "date": latest_date,
        "url": full_url,
        "sha256": hashlib.sha256(section_xml).hexdigest(),
        "bytes": len(section_xml),
    }


def check_ecfr_source(src: dict, sid: str, today: str, write: bool) -> dict | None:
    title = str(src.get("ecfr_title") or "")
    part = str(src.get("ecfr_part") or "")
    section = str(src.get("ecfr_section") or "")
    if not title or not part or not section:
        return {"id": sid, "status": "missing_ecfr_fields"}

    current = fetch_ecfr_section(title, part, section)
    expected = src.get("ecfr_sha256")
    if expected and current["sha256"] != expected:
        change = {
            "id": sid,
            "status": "changed",
            "old_hash": expected,
            "new_hash": current["sha256"],
            "ecfr_date": current["date"],
            "url": current["url"],
        }
    elif not expected:
        change = {
            "id": sid,
            "status": "missing_ecfr_baseline",
            "new_hash": current["sha256"],
            "ecfr_date": current["date"],
            "url": current["url"],
        }
    else:
        change = None

    if write:
        src["ecfr_sha256"] = current["sha256"]
        src["ecfr_date"] = current["date"]
        src["ecfr_bytes"] = current["bytes"]
        src["last_verified_date"] = today

    return change


def check_skill(
    skill_dir: Path,
    write: bool = False,
    request_wayback_save: bool = False,
) -> dict:
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
    automated_checked = 0
    manual_review = 0

    for src in sources:
        url = src.get("url")
        sid = src.get("id") or url or "<unknown>"

        if src.get("type") == "manual":
            # Some authorities are not fetchable (paywalled, login-gated,
            # bot-protected, statute in an aspx viewer). Track these separately:
            # the source-of-truth is the cited human-review process, not an
            # automated hash.
            manual_review += 1
            continue

        automated_checked += 1

        if src.get("type") == "wayback":
            try:
                change = check_wayback_source(
                    src,
                    sid,
                    today,
                    write,
                    should_request_save=request_wayback_save,
                )
            except (URLError, HTTPError, TimeoutError, json.JSONDecodeError) as e:
                changes.append(
                    {"id": sid, "status": "wayback_unreachable", "error": str(e)}
                )
                continue
            if change:
                changes.append(change)
            continue

        if src.get("type") == "ecfr":
            try:
                change = check_ecfr_source(src, sid, today, write)
            except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, ValueError) as e:
                changes.append({"id": sid, "status": "ecfr_unreachable", "error": str(e)})
                continue
            if change:
                changes.append(change)
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
        "listed": len(sources),
        "automated_checked": automated_checked,
        "manual_review": manual_review,
        "changes": changes,
    }


def render_markdown(reports: list[dict]) -> str:
    lines: list[str] = []
    for r in reports:
        lines.append(f"## `{r['skill']}`")
        if "error" in r:
            lines.append(f"- **error**: {r['error']}")
            continue
        lines.append(f"- sources listed: {r['listed']}")
        lines.append(f"- automated checks run: {r['automated_checked']}")
        lines.append(f"- manual-review sources: {r['manual_review']}")
        if not r["changes"]:
            if r["manual_review"]:
                lines.append("- status: **automated sources unchanged**")
            else:
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
        lines.append(f"  sources listed: {r['listed']}")
        lines.append(f"  automated checks run: {r['automated_checked']}")
        lines.append(f"  manual-review sources: {r['manual_review']}")
        if not r["changes"]:
            if r["manual_review"]:
                lines.append("  status: automated sources unchanged")
            else:
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
    p.add_argument(
        "--request-wayback-save",
        action="store_true",
        help="For wayback sources, ask Internet Archive Save Page Now to capture the canonical URL.",
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
        reports.append(
            check_skill(
                path,
                write=args.write,
                request_wayback_save=args.request_wayback_save,
            )
        )

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
