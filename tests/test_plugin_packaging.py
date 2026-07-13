import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_MANIFEST_PATH = REPO_ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST_PATH = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
STRICT_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class PluginPackagingTests(unittest.TestCase):
    def setUp(self):
        self.codex_manifest = load_json(CODEX_MANIFEST_PATH)
        self.claude_manifest = load_json(CLAUDE_MANIFEST_PATH)
        self.marketplace = load_json(MARKETPLACE_PATH)

    def test_codex_manifest_has_publishable_metadata(self):
        manifest = self.codex_manifest
        self.assertEqual(manifest["name"], "ehr-codex-skills")
        self.assertRegex(manifest["version"], STRICT_SEMVER)
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue((REPO_ROOT / manifest["skills"]).is_dir())
        self.assertEqual(manifest["author"]["name"], "Nick Fisher")
        self.assertNotIn("apps", manifest)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)

        interface = manifest["interface"]
        required_fields = {
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "defaultPrompt",
        }
        self.assertTrue(required_fields.issubset(interface))
        self.assertTrue(interface["capabilities"])
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        for prompt in interface["defaultPrompt"]:
            self.assertTrue(prompt.strip())
            self.assertLessEqual(len(prompt), 128)

    def test_codex_and_claude_package_metadata_match(self):
        for field in (
            "name",
            "version",
            "description",
            "author",
            "homepage",
            "repository",
            "license",
            "keywords",
        ):
            with self.subTest(field=field):
                self.assertEqual(self.codex_manifest[field], self.claude_manifest[field])

    def test_marketplace_publishes_root_plugin_from_main(self):
        self.assertEqual(self.marketplace["name"], "ehr-codex-skills")
        self.assertEqual(
            self.marketplace["interface"]["displayName"],
            self.codex_manifest["interface"]["displayName"],
        )
        self.assertEqual(len(self.marketplace["plugins"]), 1)

        entry = self.marketplace["plugins"][0]
        self.assertEqual(entry["name"], self.codex_manifest["name"])
        self.assertEqual(entry["category"], self.codex_manifest["interface"]["category"])
        self.assertEqual(
            entry["policy"],
            {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
        )
        self.assertEqual(entry["source"]["source"], "url")
        self.assertEqual(entry["source"]["ref"], "main")
        parsed_url = urlparse(entry["source"]["url"])
        self.assertEqual(parsed_url.scheme, "https")
        self.assertEqual(parsed_url.netloc, "github.com")
        self.assertEqual(parsed_url.path, "/1nickfisher/ehr-codex-skills.git")

    def test_every_packaged_skill_has_codex_metadata(self):
        for skill_root in sorted((REPO_ROOT / "skills").iterdir()):
            if not skill_root.is_dir() or skill_root.name.startswith("."):
                continue
            with self.subTest(skill=skill_root.name):
                self.assertTrue((skill_root / "SKILL.md").is_file())
                self.assertTrue((skill_root / "agents" / "openai.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
