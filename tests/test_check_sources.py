import importlib.util
import hashlib
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock
from zipfile import ZipFile

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "skills"
    / "calmhsa-medi-cal-documentation"
    / "scripts"
    / "check_sources.py"
)
PART_2_SCRIPT_PATH = (
    REPO_ROOT
    / "skills"
    / "42-cfr-part-2"
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
    def write_skill(self, sources, meta=None):
        tmp = tempfile.TemporaryDirectory()
        skill_dir = Path(tmp.name) / "skill"
        refs = skill_dir / "references"
        refs.mkdir(parents=True)
        (refs / "sources.yml").write_text(
            yaml.safe_dump(
                {"schema_version": 1, "meta": meta or {}, "sources": sources},
                sort_keys=False,
            )
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

    def test_report_distinguishes_listed_automated_and_manual_sources(self):
        checker = load_checker()
        body = b"stable source body"
        skill_dir = self.write_skill(
            [
                {
                    "id": "automated-source",
                    "type": "guidance",
                    "url": "https://example.test/source",
                    "expected_sha256": hashlib.sha256(body).hexdigest(),
                },
                {
                    "id": "manual-source",
                    "type": "manual",
                    "url": "https://example.test/manual",
                },
            ]
        )

        with mock.patch.object(
            checker,
            "urlopen",
            return_value=FakeResponse(body, {"Content-Type": "text/plain"}, 200),
        ):
            report = checker.check_skill(skill_dir)

        self.assertEqual(report["listed"], 2)
        self.assertEqual(report["automated_checked"], 1)
        self.assertEqual(report["manual_review"], 1)
        self.assertEqual(report["changes"], [])
        rendered = checker.render_markdown([report])
        self.assertIn("- sources listed: 2", rendered)
        self.assertIn("- automated checks run: 1", rendered)
        self.assertIn("- manual-review sources: 1", rendered)
        self.assertIn("- status: **automated sources unchanged**", rendered)
        self.assertIn(
            "  status: automated sources unchanged",
            checker.render_text([report]),
        )

        automated_only_report = {
            **report,
            "listed": 1,
            "manual_review": 0,
        }
        automated_only_rendered = checker.render_markdown([automated_only_report])
        self.assertIn("- status: **unchanged**", automated_only_rendered)
        self.assertNotIn("automated sources unchanged", automated_only_rendered)

    def test_expected_spreadsheet_rejects_incapsula_html(self):
        checker = load_checker()
        challenge = b"""<html><iframe src=\"/_Incapsula_Resource\">\n+        Request unsuccessful. Incapsula incident ID: test
        </iframe></html>"""

        with mock.patch.object(
            checker,
            "urlopen",
            return_value=FakeResponse(
                challenge,
                {"Content-Type": "text/html"},
                200,
            ),
        ):
            result = checker.fetch(
                "https://www.dhcs.ca.gov/file/current-service-table/",
                expected_type="xlsx",
            )

        self.assertTrue(result["bot_protected"])

    def test_expected_pdf_rejects_generic_html_without_challenge_marker(self):
        checker = load_checker()

        with mock.patch.object(
            checker,
            "urlopen",
            return_value=FakeResponse(
                b"<html><body>unexpected response</body></html>",
                {"Content-Type": "text/html"},
                200,
            ),
        ):
            result = checker.fetch(
                "https://example.test/guide.pdf",
                expected_type="pdf",
            )

        self.assertTrue(result["bot_protected"])

    def test_xlsx_validation_requires_workbook_zip_structure(self):
        checker = load_checker()

        valid_workbook = BytesIO()
        with ZipFile(valid_workbook, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types />")
            archive.writestr("xl/workbook.xml", "<workbook />")

        self.assertFalse(checker.is_xlsx_payload(b"PK not a ZIP archive"))

        docx_like = BytesIO()
        with ZipFile(docx_like, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types />")
            archive.writestr("word/document.xml", "<document />")

        self.assertFalse(checker.is_xlsx_payload(docx_like.getvalue()))
        self.assertTrue(checker.is_xlsx_payload(valid_workbook.getvalue()))

    def test_expected_document_rejects_non_document_payload(self):
        checker = load_checker()
        body = b"not actually a PDF"
        skill_dir = self.write_skill(
            [
                {
                    "id": "mislabeled-pdf",
                    "type": "direct",
                    "artifact_type": "pdf",
                    "url": "https://example.test/source.pdf",
                    "expected_sha256": hashlib.sha256(body).hexdigest(),
                }
            ]
        )

        with mock.patch.object(
            checker,
            "urlopen",
            return_value=FakeResponse(
                body,
                {"Content-Type": "application/pdf"},
                200,
            ),
        ):
            report = checker.check_skill(skill_dir)

        self.assertEqual(report["changes"][0]["id"], "mislabeled-pdf")
        self.assertEqual(report["changes"][0]["status"], "unexpected_artifact")

    def test_review_due_date_and_draft_status_are_enforced(self):
        checker = load_checker()
        body = b"draft guidance"
        skill_dir = self.write_skill(
            [
                {
                    "id": "overdue-manual-source",
                    "type": "manual",
                    "review_due_date": "2000-01-01",
                },
                {
                    "id": "due-today-manual-source",
                    "type": "manual",
                    "review_due_date": checker.date.today().isoformat(),
                },
                {
                    "id": "draft-source",
                    "type": "guidance",
                    "url": "https://example.test/draft",
                    "status": "draft",
                    "normative": True,
                    "expected_sha256": hashlib.sha256(body).hexdigest(),
                },
            ]
        )

        with mock.patch.object(
            checker,
            "urlopen",
            return_value=FakeResponse(body, {"Content-Type": "text/plain"}, 200),
        ):
            report = checker.check_skill(skill_dir)

        changes = {(item["id"], item["status"]) for item in report["changes"]}
        self.assertIn(("overdue-manual-source", "review_overdue"), changes)
        self.assertIn(("due-today-manual-source", "review_overdue"), changes)
        self.assertIn(("draft-source", "draft_marked_normative"), changes)

    def test_default_manual_review_interval_flags_stale_sources(self):
        checker = load_checker()
        skill_dir = self.write_skill(
            [
                {
                    "id": "stale-manual-source",
                    "type": "manual",
                    "last_verified_date": "2000-01-01",
                }
            ],
            meta={"manual_review_interval_days": 90},
        )

        report = checker.check_skill(skill_dir)

        self.assertEqual(
            report["changes"],
            [
                {
                    "id": "stale-manual-source",
                    "status": "review_overdue",
                    "review_due_date": "2000-03-31",
                }
            ],
        )

    def test_default_manual_review_interval_requires_a_review_date(self):
        checker = load_checker()
        skill_dir = self.write_skill(
            [{"id": "undated-manual-source", "type": "manual"}],
            meta={"manual_review_interval_days": 90},
        )

        report = checker.check_skill(skill_dir)

        self.assertEqual(
            report["changes"],
            [
                {
                    "id": "undated-manual-source",
                    "status": "missing_manual_review_date",
                    "note": "Set review_due_date or last_verified_date.",
                }
            ],
        )

    def test_skill_checker_copies_are_byte_identical(self):
        self.assertEqual(SCRIPT_PATH.read_bytes(), PART_2_SCRIPT_PATH.read_bytes())


class CaliforniaSourceCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_root = REPO_ROOT / "skills" / "calmhsa-medi-cal-documentation"
        cls.sources = yaml.safe_load(
            (cls.skill_root / "references" / "sources.yml").read_text()
        )["sources"]
        cls.sources_by_id = {source["id"]: source for source in cls.sources}

    def test_current_fiscal_year_claiming_sources_are_cataloged(self):
        expected_ids = {
            "dhcs-medccc-claims-library",
            "dhcs-smhs-billing-manual-2026-27",
            "dhcs-dmc-ods-billing-manual-2026-27",
            "dhcs-dmc-state-plan-billing-manual-2026-27",
            "dhcs-smhs-service-table-2026-27",
            "dhcs-dmc-ods-service-table-2026-27",
            "dhcs-dmc-state-plan-service-table-2026-27",
        }
        self.assertTrue(expected_ids.issubset(self.sources_by_id))

        for source_id in expected_ids - {"dhcs-medccc-claims-library"}:
            with self.subTest(source=source_id):
                source = self.sources_by_id[source_id]
                self.assertEqual(source["fiscal_year"], "2026-27")
                self.assertEqual(source["status"], "final")
                self.assertTrue(source["normative"])

        dmc_table = self.sources_by_id[
            "dhcs-dmc-state-plan-service-table-2026-27"
        ]
        self.assertEqual(dmc_table["type"], "direct")
        self.assertEqual(dmc_table["artifact_type"], "xlsx")
        self.assertIn("DMC-Service-Table-26-27-2.xlsx", dmc_table["url"])
        self.assertEqual(
            dmc_table["expected_sha256"],
            "4e09a5c50caca73c74446969d60dd41048868d351094c31b519cef5f3054645e",
        )

    def test_current_bhins_replace_superseded_and_isolate_draft_rules(self):
        self.assertNotIn("bhin-21-073", self.sources_by_id)

        access = self.sources_by_id["bhin-26-002"]
        self.assertEqual(access["supersedes"], ["bhin-21-073"])
        self.assertEqual(access["status"], "final")
        self.assertTrue(access["normative"])

        ntp = self.sources_by_id["bhin-26-022"]
        self.assertEqual(ntp["status"], "final")
        self.assertEqual(ntp["effective_date"], "2026-09-20")

        draft = self.sources_by_id["draft-bhin-26-0xx-ebp-fsp-bhss-claiming"]
        self.assertEqual(draft["status"], "draft")
        self.assertFalse(draft["normative"])

        index = self.sources_by_id["dhcs-bhin-2026-index"]
        self.assertFalse(index["normative"])
        self.assertEqual(index["review_due_date"], "2026-07-13")

    def test_all_fetchable_pdf_sources_declare_their_artifact_type(self):
        for source in self.sources:
            url = source.get("url", "")
            if source.get("type") not in {"manual", "wayback"} and url.endswith(
                ".pdf"
            ):
                with self.subTest(source=source["id"]):
                    self.assertEqual(source.get("artifact_type"), "pdf")

    def test_skill_uses_current_access_and_claiming_sources(self):
        skill_text = (self.skill_root / "SKILL.md").read_text()
        self.assertNotIn("- DHCS BHIN 21-073 —", skill_text)
        self.assertIn("BHIN 26-002", skill_text)
        self.assertIn("SFY 2026-27", skill_text)


if __name__ == "__main__":
    unittest.main()
