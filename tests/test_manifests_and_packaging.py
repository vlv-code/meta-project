#!/usr/bin/env python3
"""Canonical domain tests for release manifests, plugin manifests, and skill packaging.
Consolidated from test_dwave_k.py, test_pwave_p.py, and test_pwave_f.py.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_DIR = REPO_ROOT
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MANIFEST_PATH = REPO_ROOT / "templates" / "release_manifest.json"
RELEASE_MANIFEST = MANIFEST_PATH
CLAUDE_PLUGIN_MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
AGENT_PLUGIN_MANIFEST = REPO_ROOT / "plugin.json"
CODEX_MARKETPLACE_MANIFEST = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_PLUGIN_MANIFEST = REPO_ROOT / ".cursor-plugin" / "plugin.json"
CURSOR_MARKETPLACE_MANIFEST = REPO_ROOT / ".cursor-plugin" / "marketplace.json"
GEMINI_EXTENSION_MANIFEST = REPO_ROOT / "gemini-extension.json"
UPDATER_PATH = "scripts/update_meta_project.py"
SKILLS_DIR = ROOT_DIR / "skills"
EXPECTED_SKILL_COUNT = 10
WAVE_P_SKILLS = (
    "decommission-meta-project",
    "ground-meta-project",
    "init-meta-project",
    "manage-meta-project",
    "record-observation",
    "scan-meta-project",
    "sync-architecture",
    "tune-meta-project",
    "update-meta-project",
)
EXPECTED_LICENSE = "MIT"
EXPECTED_COMPAT_SUBSTR = "Python 3.10+"

_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

AGENT_PLUGINS_SCHEMA_URL = (
    "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
)
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
AGENT_PLUGINS_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{0,63}$")
CLAUDE_PLUGIN_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _component_paths(components):
    """Paths as the engine sees them."""
    return [str(c.get("path", "")) for c in components if str(c.get("path", ""))]


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


class CanonicalManifestContract(unittest.TestCase):
    """Contract on the CANONICAL templates/release_manifest.json."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.components = cls.manifest.get("components") or []
        cls.paths = _component_paths(cls.components)

    def test_every_component_is_file_kind(self):
        """No directory-kind entries remain (D4): no trailing slash, and
        each path resolves to an actual file in the repo tree."""
        dir_kind = [p for p in self.paths if p.endswith("/")]
        self.assertEqual(
            dir_kind, [], f"directory-kind components remain in manifest: {dir_kind}"
        )

    def test_updater_is_registered_component(self):
        """D5: the update engine ships as a manifest component."""
        self.assertIn(
            UPDATER_PATH,
            self.paths,
            f"{UPDATER_PATH} missing from canonical manifest components",
        )

    def test_framework_version_is_semver(self):
        version = str(self.manifest.get("framework_version", ""))
        self.assertIsNotNone(
            _SEMVER_RE.match(version),
            f"framework_version {version!r} does not parse as semver 2.0.0",
        )

    def test_all_component_paths_exist_in_repo_tree(self):
        missing = [p for p in self.paths if not (REPO_ROOT / p).is_file()]
        self.assertEqual(
            missing, [], f"manifest component paths absent from repo tree: {missing}"
        )

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

def read_frontmatter(text: str):
    """Return the raw frontmatter block (between the opening and closing
    --- delimiter lines), or None if absent/malformed."""
    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", text, re.DOTALL)
    return match.group(1) if match else None


def top_level_scalar(frontmatter: str, key: str):
    """Return the single-line scalar value of a top-level `key: value`
    frontmatter entry (column-0 key only), or None. Surrounding quotes
    are stripped; the raw text form is the caller's concern."""
    match = re.search(
        rf"^{re.escape(key)}:[ \t]*(.+?)[ \t]*$", frontmatter, re.MULTILINE
    )
    if not match:
        return None
    value = match.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def description_block(frontmatter: str) -> str:
    """Extract the raw description entry chunk: the `description:` line plus
    every following continuation line (indented or blank, folded-block style)
    up to the next top-level key or the end of the frontmatter block."""
    captured = []
    in_block = False
    for line in frontmatter.split("\n"):
        if line.startswith("description:"):
            in_block = True
            captured.append(line)
            continue
        if in_block:
            if line == "" or line[0] in " \t":
                captured.append(line)
            else:
                break
    return "\n".join(captured)


def metadata_version_present(frontmatter: str) -> bool:
    """True if the frontmatter declares a version under a `metadata:` block —
    either block-style (indented sub-keys) or inline flow-style."""
    lines = frontmatter.split("\n")
    in_metadata = False
    for line in lines:
        if re.match(r"^metadata:[ \t]*$", line):
            in_metadata = True
            continue
        if re.match(r"^metadata:[ \t]*\{", line):
            # inline flow-style mapping: look for a version key on the line
            if re.search(r"[{,]\s*['\"]?version['\"]?\s*:", line):
                return True
            continue
        if in_metadata:
            if line == "" or line[0] in " \t":
                if re.match(r"^[ \t]+['\"]?version['\"]?[ \t]*:", line):
                    return True
            else:
                break  # next top-level key: metadata block ended
    return False


def head_text(relpath: str) -> str:
    """Return file content at git HEAD via `git show HEAD:<relpath>`."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"],
        cwd=str(ROOT_DIR),
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git show HEAD:{relpath} failed: "
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )
    return result.stdout.decode("utf-8")

class TestSkillInventory(unittest.TestCase):
    def test_skill_glob_is_exactly_nine(self):
        skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
        self.assertEqual(
            len(skill_files),
            EXPECTED_SKILL_COUNT,
            "The packaging frontmatter contract is scoped to exactly "
            f"{EXPECTED_SKILL_COUNT} skills; found {len(skill_files)}: "
            f"{[str(p.relative_to(ROOT_DIR)) for p in skill_files]}",
        )


class TestPackagingFrontmatter(unittest.TestCase):
    def test_every_skill_has_license_and_compatibility(self):
        for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            with self.subTest(skill=skill_file.parent.name):
                frontmatter = read_frontmatter(
                    skill_file.read_text(encoding="utf-8")
                )
                self.assertIsNotNone(
                    frontmatter,
                    f"{skill_file}: missing or malformed frontmatter",
                )
                license_value = top_level_scalar(frontmatter, "license")
                self.assertIsNotNone(
                    license_value,
                    f"{skill_file}: top-level frontmatter key 'license' missing",
                )
                self.assertEqual(
                    license_value,
                    EXPECTED_LICENSE,
                    f"{skill_file}: license must be {EXPECTED_LICENSE!r}",
                )
                compat_value = top_level_scalar(frontmatter, "compatibility")
                self.assertIsNotNone(
                    compat_value,
                    f"{skill_file}: top-level frontmatter key 'compatibility' missing",
                )
                self.assertIn(
                    EXPECTED_COMPAT_SUBSTR,
                    compat_value,
                    f"{skill_file}: compatibility must mention "
                    f"{EXPECTED_COMPAT_SUBSTR!r}",
                )

    def test_no_frontmatter_metadata_version_block(self):
        for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            with self.subTest(skill=skill_file.parent.name):
                frontmatter = read_frontmatter(
                    skill_file.read_text(encoding="utf-8")
                )
                self.assertIsNotNone(frontmatter, f"{skill_file}: no frontmatter")
                self.assertFalse(
                    metadata_version_present(frontmatter),
                    f"{skill_file}: frontmatter carries a version under a "
                    "'metadata:' block — version is single-sourced in "
                    "templates/release_manifest.json; do not duplicate it",
                )

    def test_descriptions_byte_identical_to_head(self):
        for skill_name in WAVE_P_SKILLS:
            skill_file = SKILLS_DIR / skill_name / "SKILL.md"
            relpath = skill_file.relative_to(ROOT_DIR).as_posix()
            with self.subTest(skill=skill_name):
                working = read_frontmatter(
                    skill_file.read_text(encoding="utf-8")
                )
                self.assertIsNotNone(working, f"{skill_file}: no frontmatter")
                head = read_frontmatter(head_text(relpath))
                self.assertIsNotNone(
                    head, f"HEAD:{relpath}: no frontmatter at HEAD"
                )
                self.assertEqual(
                    description_block(working),
                    description_block(head),
                    f"{relpath}: description entry diverged from git HEAD — "
                    "Wave PF must add packaging keys without touching "
                    "descriptions",
                )

class TestVendorMarketplaceManifests(unittest.TestCase):
    """Lane Z2-C: Vendor marketplace manifests for Codex, Cursor, and Gemini."""

    def _framework_version(self) -> str:
        return _load_json(RELEASE_MANIFEST)["framework_version"]

    def test_codex_marketplace_manifest_contract(self):
        self.assertTrue(
            CODEX_MARKETPLACE_MANIFEST.is_file(),
            f"Missing Codex marketplace manifest: {CODEX_MARKETPLACE_MANIFEST}",
        )
        data = _load_json(CODEX_MARKETPLACE_MANIFEST)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("name"), "meta-project")
        self.assertIn("interface", data)
        self.assertIsInstance(data["interface"], dict)
        self.assertTrue(data["interface"].get("displayName"))
        self.assertIn("plugins", data)
        self.assertIsInstance(data["plugins"], list)
        self.assertTrue(len(data["plugins"]) >= 1)
        plugin = data["plugins"][0]
        self.assertEqual(plugin.get("name"), "meta-project")
        self.assertIsInstance(plugin.get("source"), dict)
        self.assertEqual(plugin["source"].get("source"), "local")
        self.assertEqual(plugin["source"].get("path"), "./")
        self.assertIsInstance(plugin.get("policy"), dict)
        self.assertEqual(plugin["policy"].get("installation"), "AVAILABLE")
        self.assertEqual(plugin["policy"].get("authentication"), "ON_INSTALL")
        self.assertEqual(plugin.get("category"), "Developer Tools")

    def test_cursor_plugin_manifest_contract(self):
        self.assertTrue(
            CURSOR_PLUGIN_MANIFEST.is_file(),
            f"Missing Cursor plugin manifest: {CURSOR_PLUGIN_MANIFEST}",
        )
        data = _load_json(CURSOR_PLUGIN_MANIFEST)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("name"), "meta-project")
        self.assertEqual(data.get("version"), self._framework_version())
        for field in ("description", "author", "homepage", "repository", "license", "keywords"):
            self.assertIn(field, data, f"Missing field '{field}' in Cursor plugin manifest")
        self.assertEqual(data.get("license"), "MIT")

    def test_claude_marketplace_manifest_has_homepage(self):
        claude_mkt = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        self.assertTrue(claude_mkt.is_file(), f"Missing {claude_mkt}")
        data = _load_json(claude_mkt)
        self.assertIn("plugins", data)
        self.assertTrue(len(data["plugins"]) >= 1)
        plugin = data["plugins"][0]
        self.assertEqual(plugin.get("homepage"), "https://github.com/vlv-code/meta-project")

    def test_cursor_marketplace_manifest_contract(self):
        self.assertTrue(
            CURSOR_MARKETPLACE_MANIFEST.is_file(),
            f"Missing Cursor marketplace manifest: {CURSOR_MARKETPLACE_MANIFEST}",
        )
        data = _load_json(CURSOR_MARKETPLACE_MANIFEST)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("name"), "meta-project")
        self.assertIsInstance(data.get("owner"), dict)
        self.assertTrue(data["owner"].get("name"))
        self.assertIsInstance(data.get("plugins"), list)
        self.assertTrue(len(data["plugins"]) >= 1)
        self.assertEqual(data["plugins"][0].get("name"), "meta-project")
        self.assertEqual(data["plugins"][0].get("source"), "./")

    def test_gemini_extension_manifest_contract(self):
        self.assertTrue(
            GEMINI_EXTENSION_MANIFEST.is_file(),
            f"Missing Gemini extension manifest: {GEMINI_EXTENSION_MANIFEST}",
        )
        data = _load_json(GEMINI_EXTENSION_MANIFEST)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("name"), "meta-project")
        self.assertEqual(data.get("version"), self._framework_version())
        self.assertTrue(data.get("description"))


class TestSyncDistBranchFiltering(unittest.TestCase):
    """Lane Z2-C: Distribution sync branch path filtering."""

    def test_dist_paths_include_vendor_manifests(self):
        from scripts.sync_dist_branch import DIST_PATHS
        self.assertIn(".agents/plugins", DIST_PATHS)
        self.assertIn(".cursor-plugin", DIST_PATHS)
        self.assertIn("gemini-extension.json", DIST_PATHS)

    def test_dist_filtering_allows_plugins_and_excludes_all_dogfooding(self):
        from scripts.sync_dist_branch import _is_dist_allowed
        # Allowed files
        allowed = [
            ".agents/plugins/marketplace.json",
            ".cursor-plugin/plugin.json",
            ".cursor-plugin/marketplace.json",
            "gemini-extension.json",
            "skills/init-meta-project/SKILL.md",
            "README.md",
            "scripts/inspect_meta_project.py",
        ]
        for path in allowed:
            self.assertTrue(_is_dist_allowed(path), f"Expected {path} to be allowed in dist")

        # Excluded dogfooding files
        excluded = [
            ".agents/project_knowledge/boundaries.md",
            ".agents/project_knowledge/tasks.md",
            ".agents/team/agent-dev-lead/profile.md",
            ".agents/reports/ag-main/init/init-1.json",
            ".agents/skills/init-meta-project/SKILL.md",
            ".agents/meta-project.json",
            ".agents/framework-lock.json",
            ".agents/update-engine.lock",
            ".agents/random-file.txt",
            ".agents/foo/bar.json",
            "docs/superpowers/plan.md",
            "docs/archive/old.md",
            "download/binary.bin",
        ]
        for path in excluded:
            self.assertFalse(_is_dist_allowed(path), f"Expected {path} to be excluded from dist")


class TestWaveZ3HooksManifestAndPackaging(unittest.TestCase):
    """Contracts for Wave Z3: hooks/ distribution and release_manifest.json registration."""

    def test_hooks_registered_in_release_manifest(self):
        manifest_path = REPO_ROOT / "templates" / "release_manifest.json"
        self.assertTrue(manifest_path.is_file(), "templates/release_manifest.json must exist")
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        components = {c["path"]: c for c in data.get("components", [])}

        # 1. hooks/dispatch.py (script)
        self.assertIn("hooks/dispatch.py", components)
        disp = components["hooks/dispatch.py"]
        self.assertEqual(disp.get("kind"), "script")
        self.assertEqual(
            disp.get("requires"),
            [
                "scripts/check_boundaries.py",
                "scripts/inspect_meta_project.py",
                "scripts/compact_memory.py",
                "scripts/triage_incident.py",
                "scripts/_common.py",
            ],
        )

        # 2. hooks/install.py (script)
        self.assertIn("hooks/install.py", components)
        inst = components["hooks/install.py"]
        self.assertEqual(inst.get("kind"), "script")
        self.assertEqual(
            inst.get("requires"),
            [
                "hooks/dispatch.py",
                "scripts/check_boundaries.py",
                "scripts/_common.py",
            ],
        )

        # 3. hooks/hooks.json (resource)
        self.assertIn("hooks/hooks.json", components)
        hjson = components["hooks/hooks.json"]
        self.assertEqual(hjson.get("kind"), "resource")
        self.assertEqual(hjson.get("requires"), ["hooks/dispatch.py"])

        # 4. hooks/README.md (resource)
        self.assertIn("hooks/README.md", components)
        readme = components["hooks/README.md"]
        self.assertEqual(readme.get("kind"), "resource")
        self.assertEqual(readme.get("requires"), ["hooks/install.py"])

    def test_hooks_in_dist_paths_and_allowed(self):
        from scripts.sync_dist_branch import DIST_PATHS, _is_dist_allowed

        self.assertIn("hooks", DIST_PATHS)
        self.assertTrue(_is_dist_allowed("hooks/dispatch.py"))
        self.assertTrue(_is_dist_allowed("hooks/install.py"))
        self.assertTrue(_is_dist_allowed("hooks/hooks.json"))
        self.assertTrue(_is_dist_allowed("hooks/README.md"))


if __name__ == '__main__':
    unittest.main()
