"""Wave P (plugin packaging) — manifest contract and version-lock tests.

Locks FIRST pattern: these tests are the specification for the packaging
manifests and skip (GREEN-but-skipping) while a manifest file does not exist
yet. Once a manifest is created, the corresponding tests stop skipping and
enforce the contract.

Channels covered:
  - Claude Code plugin channel: .claude-plugin/plugin.json
  - Claude Code marketplace channel: .claude-plugin/marketplace.json
  - Agent Plugins 1.0.0 channel: plugin.json (repo root)

Version invariant (single source of truth): the "version" field of BOTH
plugin manifests equals templates/release_manifest.json "framework_version".

Zero-dependency: Python 3.10+ standard library only (json/re/unittest/pathlib);
no network access.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_MANIFEST = REPO_ROOT / "templates" / "release_manifest.json"
CLAUDE_PLUGIN_MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
AGENT_PLUGIN_MANIFEST = REPO_ROOT / "plugin.json"

# Agent Plugins 1.0.0 contract (auditor v2 §4.2): schema URL is pinned.
AGENT_PLUGINS_SCHEMA_URL = (
    "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
)
# Top-level keys CLOSED to exactly this set (10 keys).
AGENT_PLUGINS_ALLOWED_KEYS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
# Agent Plugins 1.0.0 plugin name pattern.
AGENT_PLUGINS_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{0,63}$")
# Claude plugin manifest name pattern (kebab-case).
CLAUDE_PLUGIN_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _load_json(path: Path) -> object:
    """Parse a JSON file, raising so the caller can skip if it is absent."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


class WavePManifestTestBase(unittest.TestCase):
    """Shared skip-guarded manifest loading for Wave P contract tests."""

    def _load(self, path: Path):
        if not path.is_file():
            self.skipTest(f"manifest not created yet: {path.relative_to(REPO_ROOT)}")
        return _load_json(path)


class TestFrameworkVersionLock(WavePManifestTestBase):
    """Version lock: both plugin manifests track framework_version."""

    def _framework_version(self) -> str:
        return _load_json(RELEASE_MANIFEST)["framework_version"]

    def test_claude_plugin_manifest_version_is_locked(self):
        framework_version = self._framework_version()
        manifest = self._load(CLAUDE_PLUGIN_MANIFEST)
        self.assertEqual(
            manifest.get("version"),
            framework_version,
            ".claude-plugin/plugin.json 'version' must equal "
            "templates/release_manifest.json 'framework_version'",
        )

    def test_agent_plugin_manifest_version_is_locked(self):
        framework_version = self._framework_version()
        manifest = self._load(AGENT_PLUGIN_MANIFEST)
        self.assertEqual(
            manifest.get("version"),
            framework_version,
            "root plugin.json 'version' must equal "
            "templates/release_manifest.json 'framework_version'",
        )


class TestAgentPluginsContract(WavePManifestTestBase):
    """Agent Plugins 1.0.0 contract for the root plugin.json."""

    def _manifest(self) -> dict:
        manifest = self._load(AGENT_PLUGIN_MANIFEST)
        self.assertIsInstance(manifest, dict, "root plugin.json must be a JSON object")
        return manifest

    def test_schema_is_pinned_to_100(self):
        manifest = self._manifest()
        self.assertEqual(manifest.get("$schema"), AGENT_PLUGINS_SCHEMA_URL)

    def test_name_required_and_matches_pattern(self):
        manifest = self._manifest()
        name = manifest.get("name")
        self.assertIsInstance(name, str, "'name' is required and must be a string")
        self.assertRegex(name, AGENT_PLUGINS_NAME_RE)

    def test_top_level_keys_are_closed(self):
        manifest = self._manifest()
        unexpected = sorted(set(manifest) - AGENT_PLUGINS_ALLOWED_KEYS)
        self.assertEqual(
            unexpected,
            [],
            f"root plugin.json top-level keys are closed to "
            f"{sorted(AGENT_PLUGINS_ALLOWED_KEYS)}; found extra: {unexpected}",
        )


class TestClaudePluginContract(WavePManifestTestBase):
    """Claude plugin manifest contract for .claude-plugin/plugin.json."""

    def _manifest(self) -> dict:
        manifest = self._load(CLAUDE_PLUGIN_MANIFEST)
        self.assertIsInstance(
            manifest, dict, ".claude-plugin/plugin.json must be a JSON object"
        )
        return manifest

    def test_name_required_kebab_case(self):
        manifest = self._manifest()
        name = manifest.get("name")
        self.assertIsInstance(name, str, "'name' is required and must be a string")
        self.assertRegex(name, CLAUDE_PLUGIN_NAME_RE)

    def test_author_name_required(self):
        manifest = self._manifest()
        author = manifest.get("author")
        self.assertIsInstance(author, dict, "'author' is required and must be an object")
        self.assertIsInstance(
            author.get("name"), str, "'author.name' is required and must be a string"
        )
        self.assertTrue(author["name"].strip(), "'author.name' must be non-empty")

    def test_recommended_fields_present(self):
        manifest = self._manifest()
        for field in ("version", "homepage", "repository", "license"):
            self.assertIn(field, manifest, f"'{field}' must be present")


class TestMarketplaceContract(WavePManifestTestBase):
    """Marketplace manifest contract for .claude-plugin/marketplace.json."""

    def _manifest(self) -> dict:
        manifest = self._load(MARKETPLACE_MANIFEST)
        self.assertIsInstance(
            manifest, dict, ".claude-plugin/marketplace.json must be a JSON object"
        )
        return manifest

    def test_marketplace_name_required(self):
        manifest = self._manifest()
        name = manifest.get("name")
        self.assertIsInstance(name, str, "'name' is required and must be a string")
        self.assertTrue(name.strip(), "'name' must be non-empty")

    def test_owner_name_required(self):
        manifest = self._manifest()
        owner = manifest.get("owner")
        self.assertIsInstance(owner, dict, "'owner' is required and must be an object")
        self.assertIsInstance(
            owner.get("name"), str, "'owner.name' is required and must be a string"
        )
        self.assertTrue(owner["name"].strip(), "'owner.name' must be non-empty")

    def test_plugins_list_entries_have_name_and_source(self):
        manifest = self._manifest()
        plugins = manifest.get("plugins")
        self.assertIsInstance(plugins, list, "'plugins' is required and must be a list")
        self.assertTrue(plugins, "'plugins' must register at least one plugin")
        for index, entry in enumerate(plugins):
            with self.subTest(index=index):
                self.assertIsInstance(entry, dict, "each plugins[] entry must be an object")
                self.assertIsInstance(entry.get("name"), str, "entry 'name' required")
                self.assertIsInstance(entry.get("source"), str, "entry 'source' required")
                self.assertTrue(entry["source"], "entry 'source' must be non-empty")


if __name__ == "__main__":
    unittest.main()
