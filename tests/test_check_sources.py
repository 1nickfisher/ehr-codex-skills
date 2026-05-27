import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "skills"
    / "calmhsa-medi-cal-documentation"
    / "scripts"
    / "check_sources.py"
)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_sources", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, body, headers=None, status=200):
        self._body = body.encode("utf-8") if isinstance(body, str) else body
        self.headers = headers or {}
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


class WaybackSourceTests(unittest.TestCase):
    def write_skill(self, sources):
        tmp = tempfile.TemporaryDirectory()
        skill_dir = Path(tmp.name) / "skill"
        refs = skill_dir / "references"
        refs.mkdir(parents=True)
        (refs / "sources.yml").write_text(
            yaml.safe_dump({"schema_version": 1, "sources": sources}, sort_keys=False)
        )
        self.addCleanup(tmp.cleanup)
        return skill_dir

    def test_wayback_source_reports_candidate_change_when_latest_digest_differs(self):
        checker = load_checker()
        skill_dir = self.write_skill(
            [
                {
                    "id": "bhin-23-068",
                    "type": "wayback",
                    "url": "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                    "wayback_digest": "OLD_DIGEST",
                    "wayback_timestamp": "20250101000000",
                }
            ]
        )
        cdx = [
            ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            [
                "20250202000000",
                "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                "application/pdf",
                "200",
                "NEW_DIGEST",
                "296600",
            ],
        ]

        with mock.patch.object(
            checker,
            "urlopen",
            return_value=FakeResponse(
                json.dumps(cdx), {"Content-Type": "application/json"}, 200
            ),
        ):
            report = checker.check_skill(skill_dir)

        self.assertEqual(
            report["changes"],
            [
                {
                    "id": "bhin-23-068",
                    "status": "wayback_candidate_changed",
                    "url": "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                    "old_digest": "OLD_DIGEST",
                    "new_digest": "NEW_DIGEST",
                    "old_timestamp": "20250101000000",
                    "new_timestamp": "20250202000000",
                    "mimetype": "application/pdf",
                    "length": "296600",
                    "note": "Wayback observed a new archived payload. Human review required.",
                }
            ],
        )

    def test_wayback_write_persists_digest_metadata_and_archived_sha256(self):
        checker = load_checker()
        skill_dir = self.write_skill(
            [
                {
                    "id": "bhin-23-068",
                    "type": "wayback",
                    "url": "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                }
            ]
        )
        cdx = [
            ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            [
                "20250202000000",
                "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                "application/pdf",
                "200",
                "NEW_DIGEST",
                "296600",
            ],
        ]
        archived_body = b"%PDF archived bytes"

        with mock.patch.object(
            checker,
            "urlopen",
            side_effect=[
                FakeResponse(json.dumps(cdx), {"Content-Type": "application/json"}, 200),
                FakeResponse(
                    archived_body,
                    {"Content-Type": "application/pdf"},
                    200,
                ),
            ],
        ):
            report = checker.check_skill(skill_dir, write=True)

        self.assertEqual(report["changes"][0]["status"], "missing_wayback_baseline")
        data = yaml.safe_load((skill_dir / "references" / "sources.yml").read_text())
        source = data["sources"][0]
        self.assertEqual(source["wayback_digest"], "NEW_DIGEST")
        self.assertEqual(source["wayback_timestamp"], "20250202000000")
        self.assertEqual(source["wayback_mimetype"], "application/pdf")
        self.assertEqual(source["wayback_length"], "296600")
        self.assertEqual(
            source["wayback_archived_sha256"],
            hashlib.sha256(archived_body).hexdigest(),
        )

    def test_request_wayback_save_triggers_save_page_now_for_wayback_source(self):
        checker = load_checker()
        skill_dir = self.write_skill(
            [
                {
                    "id": "bhin-23-068",
                    "type": "wayback",
                    "url": "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                    "wayback_digest": "NEW_DIGEST",
                    "wayback_timestamp": "20250202000000",
                }
            ]
        )
        cdx = [
            ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            [
                "20250202000000",
                "https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
                "application/pdf",
                "200",
                "NEW_DIGEST",
                "296600",
            ],
        ]

        with mock.patch.object(
            checker,
            "urlopen",
            side_effect=[
                FakeResponse(json.dumps(cdx), {"Content-Type": "application/json"}, 200),
                FakeResponse(b"saved", {"Content-Type": "text/plain"}, 200),
            ],
        ) as fake_urlopen:
            report = checker.check_skill(skill_dir, request_wayback_save=True)

        self.assertEqual(report["changes"], [])
        save_request = fake_urlopen.call_args_list[1].args[0]
        self.assertEqual(
            save_request.full_url,
            "https://web.archive.org/save/https://www.dhcs.ca.gov/Documents/BHIN-23-068.pdf",
        )

    def test_ecfr_source_reports_change_when_section_hash_differs(self):
        checker = load_checker()
        skill_dir = self.write_skill(
            [
                {
                    "id": "cfr-42-440-169",
                    "type": "ecfr",
                    "ecfr_title": "42",
                    "ecfr_part": "440",
                    "ecfr_section": "440.169",
                    "ecfr_sha256": "OLD_HASH",
                }
            ]
        )
        versions = {
            "meta": {
                "title": "42",
                "latest_issue_date": "2026-05-20",
            },
            "content_versions": [],
        }
        xml = b"""<?xml version="1.0"?>
<DIV5 N="440" TYPE="PART">
<DIV8 N="440.168" TYPE="SECTION"><HEAD>Other</HEAD></DIV8>
<DIV8 N="440.169" TYPE="SECTION"><HEAD>Case management services.</HEAD><P>Current text.</P></DIV8>
</DIV5>"""

        with mock.patch.object(
            checker,
            "urlopen",
            side_effect=[
                FakeResponse(json.dumps(versions), {"Content-Type": "application/json"}, 200),
                FakeResponse(xml, {"Content-Type": "application/xml"}, 200),
            ],
        ):
            report = checker.check_skill(skill_dir)

        self.assertEqual(report["changes"][0]["id"], "cfr-42-440-169")
        self.assertEqual(report["changes"][0]["status"], "changed")
        self.assertEqual(report["changes"][0]["ecfr_date"], "2026-05-20")
        self.assertIn("new_hash", report["changes"][0])


if __name__ == "__main__":
    unittest.main()
