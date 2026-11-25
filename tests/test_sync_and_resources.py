#!/usr/bin/env python3
"""Canonical domain tests for template synchronization and skill resources.
Consolidated from test_sync_templates.py, test_ewave_p.py, and test_gwave_s.py.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT_DIR
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

CHANGELOG_PATH = ROOT_DIR / "CHANGELOG.md"
RESOURCES_DIR = ROOT_DIR / "skills" / "init-meta-project" / "resources"
MIRROR_RESOURCES_DIR = ROOT_DIR / ".agents" / "skills" / "init-meta-project" / "resources"
INIT_SKILL_PATH = ROOT_DIR / "skills" / "init-meta-project" / "SKILL.md"

MANAGE_SKILL_PATH = ROOT_DIR / "skills" / "manage-meta-project" / "SKILL.md"
MANAGE_MIRROR_SKILL_PATH = ROOT_DIR / ".agents" / "skills" / "manage-meta-project" / "SKILL.md"
MANAGE_RESOURCES_DIR = ROOT_DIR / "skills" / "manage-meta-project" / "resources"
MANAGE_MIRROR_RESOURCES_DIR = ROOT_DIR / ".agents" / "skills" / "manage-meta-project" / "resources"
MANAGE_SKILL_RELPATH = "skills/manage-meta-project/SKILL.md"

MANIFEST_PATH = ROOT_DIR / "templates" / "release_manifest.json"
SYNC_SCRIPT = ROOT_DIR / "scripts" / "sync_templates.py"
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import sync_templates
except ImportError:
    sync_templates = None

try:
    from scripts.update_meta_project import _resolve_target
except ImportError:
    _resolve_target = None

CANONICAL_SOURCES = {
    "observations.md": "templates/project_knowledge/observations.md",
    "boundaries.md": "templates/project_knowledge/boundaries.md",
    "weak_spots.md": "templates/project_knowledge/weak_spots.md",
    "architecture.md": "templates/project_knowledge/architecture.md",
    "tasks.md": "templates/project_knowledge/tasks.md",
    "AGENTS.md": "templates/AGENTS.md",
    "record-observation-SKILL.md": "skills/record-observation/SKILL.md",
    "sync-architecture-SKILL.md": "skills/sync-architecture/SKILL.md",
    "ground-meta-project-SKILL.md": "skills/ground-meta-project/SKILL.md",
}

MANAGE_CANONICAL_SOURCES = {
    "profile.md": "templates/team/profile.md",
    "notes.md": "templates/team/notes.md",
    "system_prompt.md": "templates/team/system_prompt.md",
}

MISSING_RESOURCE_GUIDANCE = (
    "missing mandatory resource 'resources/<name>' — reinstall the skill "
    "from the pinned source (update-meta-project) or restore the file; "
    "do not improvise the template from memory"
)

MANAGE_SKILL_MAX_LINES = 240


def _latest_changelog_version() -> str:
    """Latest release version heading from CHANGELOG.md, skipping [Unreleased]."""
    for line in CHANGELOG_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## [") and "]" in stripped:
            version = stripped[4:stripped.index("]")].strip()
            if version and version.lower() != "unreleased":
                return version
    raise AssertionError("no release version heading found in CHANGELOG.md")


class TestSkillResourceSync(unittest.TestCase):
    """Per-skill resource byte-copy semantics: drift = recoverable,
    missing canonical = fatal."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not implemented yet")

    def _write_init_canonical_sources(self, root: Path) -> None:
        """Canonical sources for the init resource set (Wave E Lane P2)."""
        tmpl_dir = root / "templates" / "project_knowledge"
        tmpl_dir.mkdir(parents=True, exist_ok=True)
        for name in ("boundaries.md", "observations.md", "weak_spots.md", "architecture.md", "tasks.md"):
            (tmpl_dir / name).write_text(f"canonical {name}\n", encoding="utf-8")
        (root / "templates" / "AGENTS.md").write_text("canonical AGENTS.md\n", encoding="utf-8")
        for skill in ("record-observation", "sync-architecture", "ground-meta-project"):
            sdir = root / "skills" / skill
            sdir.mkdir(parents=True, exist_ok=True)
            (sdir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

    def _write_manage_canonical_sources(self, root: Path) -> None:
        """Canonical sources for the manage resource set (Wave G Lane S)."""
        team_dir = root / "templates" / "team"
        team_dir.mkdir(parents=True, exist_ok=True)
        for name in ("profile.md", "notes.md", "system_prompt.md"):
            (team_dir / name).write_text(f"canonical {name}\n", encoding="utf-8")

    def test_missing_template_sentinel_raises_drift_error(self):
        """Superseded per plan §6a (init embedded blocks -> resources/): when a
        required sync-managed resource file is missing, drift is detected
        (recoverable — --write repairs it by byte copy)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "init-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Init Skill\nRouting only.\n", encoding="utf-8")

            # All canonical sources present, resources/ intentionally absent.
            self._write_init_canonical_sources(root)
            self._write_manage_canonical_sources(root)

            in_sync, drift_msgs = sync_templates.sync_skill_resources(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(
                any("Missing resource file" in msg for msg in drift_msgs),
                f"missing resource file must be reported as drift: {drift_msgs}",
            )

    def test_missing_canonical_template_reports_drift(self):
        """Superseded per plan §6a (init embedded blocks -> resources/): a missing
        canonical source file is reported as drift rather than silently ignored
        (fatal — unrecoverable by --write)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "init-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Init Skill\nRouting only.\n", encoding="utf-8")
            (skill_dir / "resources").mkdir(parents=True, exist_ok=True)
            (skill_dir / "resources" / "boundaries.md").write_text("stale copy\n", encoding="utf-8")

            # Note: canonical sources under templates/ and skills/ are intentionally NOT created
            in_sync, drift_msgs = sync_templates.sync_skill_resources(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(
                any("Missing canonical source file" in msg for msg in drift_msgs),
                f"missing canonical source must be reported as drift: {drift_msgs}",
            )

    def test_missing_manage_resources_reports_drift(self):
        """Superseded per Wave G Lane S (plan §4; was test_missing_target_skill_reports_drift,
        which relied on the removed module-level EMBEDDED_TARGETS manage entry):
        missing sync-managed MANAGE resource files are reported as (recoverable)
        drift when their canonical sources exist — resource-equivalence of the
        old 'missing target' drift intent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "manage-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Manage Skill\nRouting only.\n", encoding="utf-8")

            # Both canonical source sets present; resources/ intentionally absent.
            self._write_init_canonical_sources(root)
            self._write_manage_canonical_sources(root)
            init_dir = root / "skills" / "init-meta-project"
            init_dir.mkdir(parents=True, exist_ok=True)
            (init_dir / "SKILL.md").write_text("# Init Skill\nRouting only.\n", encoding="utf-8")

            in_sync, drift_msgs = sync_templates.sync_skill_resources(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(
                any(
                    "Missing resource file skills/manage-meta-project/resources/" in msg
                    for msg in drift_msgs
                ),
                f"missing manage resource files must be reported as drift: {drift_msgs}",
            )
            # The canonical sources exist, so nothing may be flagged fatal here.
            self.assertFalse(
                any(msg.startswith("Missing canonical") for msg in drift_msgs),
                f"present canonical sources must not be flagged fatal: {drift_msgs}",
            )

    def test_manage_resource_targets_declare_canonical_team_templates(self):
        """Wave G Lane S: MANAGE_RESOURCE_TARGETS maps the 3 team resources to
        their canonical templates/team/ sources; RESOURCE_SYNC_SETS registers
        both skill resource sets."""
        self.assertEqual(
            sync_templates.MANAGE_RESOURCE_TARGETS,
            {
                "profile.md": "templates/team/profile.md",
                "notes.md": "templates/team/notes.md",
                "system_prompt.md": "templates/team/system_prompt.md",
            },
        )
        self.assertEqual(
            sync_templates.RESOURCE_SYNC_SETS,
            {
                sync_templates.INIT_RESOURCES_DIR: sync_templates.RESOURCE_TARGETS,
                sync_templates.MANAGE_RESOURCES_DIR: sync_templates.MANAGE_RESOURCE_TARGETS,
            },
        )

    def test_no_embedded_sync_machinery_remains(self):
        """Wave G Lane S grep-lock: the embedded TEMPLATE-block injection
        machinery is removed — its last consumer (manage) moved to resource
        byte-copy semantics, so no skill ships embedded sections anymore."""
        for symbol in ("EMBEDDED_TARGETS", "replace_embedded_template", "sync_embedded_templates"):
            self.assertFalse(
                hasattr(sync_templates, symbol),
                f"removed embedded-sync symbol reappeared: {symbol}",
            )


class TestSyncTemplatesCLI(unittest.TestCase):
    """Test CLI --check and --write operations."""

    def setUp(self):
        self.script_path = SCRIPTS_DIR / "sync_templates.py"
        if not self.script_path.is_file():
            self.skipTest("scripts/sync_templates.py does not exist yet")

    def test_cli_help(self):
        res = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("usage:", res.stdout.lower())

    def test_cli_check_drift_detected_exit_1(self):
        """Wave G Lane S fixture refresh (supersession disclosed in module
        docstring): both skills are routing-only; drift is the absent sync-managed
        resource files (init set + manage set) and their missing mirrors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create all canonical templates
            (tmppath / "templates" / "project_knowledge").mkdir(parents=True)
            (tmppath / "templates" / "team").mkdir(parents=True)
            (tmppath / "templates" / "project_knowledge" / "boundaries.md").write_text(
                "CANONICAL BOUNDARIES V2", encoding="utf-8"
            )
            (tmppath / "templates" / "project_knowledge" / "observations.md").write_text(
                "CANONICAL OBS", encoding="utf-8"
            )
            (tmppath / "templates" / "project_knowledge" / "weak_spots.md").write_text(
                "CANONICAL WEAK", encoding="utf-8"
            )
            (tmppath / "templates" / "project_knowledge" / "architecture.md").write_text(
                "CANONICAL ARCH", encoding="utf-8"
            )
            (tmppath / "templates" / "project_knowledge" / "tasks.md").write_text(
                "CANONICAL TASKS", encoding="utf-8"
            )
            (tmppath / "templates" / "AGENTS.md").write_text(
                "CANONICAL AGENTS", encoding="utf-8"
            )
            (tmppath / "templates" / "team" / "profile.md").write_text(
                "CANONICAL PROFILE", encoding="utf-8"
            )
            (tmppath / "templates" / "team" / "notes.md").write_text(
                "CANONICAL NOTES", encoding="utf-8"
            )
            (tmppath / "templates" / "team" / "system_prompt.md").write_text(
                "CANONICAL PROMPT", encoding="utf-8"
            )
            # Canonical shell-skill sources for the init resources (Wave E Lane P2)
            for skill_name, body in (
                ("record-observation", "CANONICAL RECORD-OBSERVATION SKILL"),
                ("sync-architecture", "CANONICAL SYNC-ARCHITECTURE SKILL"),
                ("ground-meta-project", "CANONICAL GROUND SKILL"),
            ):
                skill_dir = tmppath / "skills" / skill_name
                skill_dir.mkdir(parents=True, exist_ok=True)
                (skill_dir / "SKILL.md").write_text(f"# {body}\n", encoding="utf-8")

            # Routing-only skills (Wave E Lane P2 for init; Wave G Lane S for
            # manage — both ship sync-managed resources/, not embedded blocks);
            # resources/ intentionally absent so --check detects drift.
            init_skill = (
                "# Init Skill\n"
                "## Resource Loading Contract\n"
                "Clean init reads each resource exactly when its step needs it.\n"
            )
            (tmppath / "skills" / "init-meta-project").mkdir(parents=True)
            (tmppath / "skills" / "init-meta-project" / "SKILL.md").write_text(
                init_skill, encoding="utf-8"
            )
            manage_skill = (
                "# Manage Skill\n"
                "## Resource Loading Contract\n"
                "Phase 5 reads each resource exactly when its step needs it.\n"
            )
            (tmppath / "skills" / "manage-meta-project").mkdir(parents=True)
            (tmppath / "skills" / "manage-meta-project" / "SKILL.md").write_text(
                manage_skill, encoding="utf-8"
            )

            # Create .agents/skills/ matching skills/
            (tmppath / ".agents" / "skills" / "init-meta-project").mkdir(parents=True)
            (tmppath / ".agents" / "skills" / "init-meta-project" / "SKILL.md").write_text(
                init_skill, encoding="utf-8"
            )
            (tmppath / ".agents" / "skills" / "manage-meta-project").mkdir(parents=True)
            (tmppath / ".agents" / "skills" / "manage-meta-project" / "SKILL.md").write_text(
                manage_skill, encoding="utf-8"
            )

            # Run --check -> should detect drift and exit 1
            cmd = [
                sys.executable,
                str(self.script_path),
                "--check",
                "--repo-root",
                str(tmppath),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 1)
            self.assertIn("drift", res.stderr.lower() + res.stdout.lower())

            # Run --write -> should update files and exit 0
            cmd_write = [
                sys.executable,
                str(self.script_path),
                "--write",
                "--repo-root",
                str(tmppath),
            ]
            res_write = subprocess.run(cmd_write, capture_output=True, text=True)
            self.assertEqual(res_write.returncode, 0)

            # Check that the resource copies (canonical + mirrored) received the canonical templates
            updated_resource = (tmppath / "skills" / "init-meta-project" / "resources" / "boundaries.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL BOUNDARIES V2", updated_resource)
            mirrored_resource = (tmppath / ".agents" / "skills" / "init-meta-project" / "resources" / "boundaries.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL BOUNDARIES V2", mirrored_resource)
            updated_manage_resource = (tmppath / "skills" / "manage-meta-project" / "resources" / "profile.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL PROFILE", updated_manage_resource)
            mirrored_manage_resource = (tmppath / ".agents" / "skills" / "manage-meta-project" / "resources" / "profile.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL PROFILE", mirrored_manage_resource)

            # Now --check must pass with 0 exit code
            res_check2 = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res_check2.returncode, 0)

    def test_sync_global_skills_option(self):
        """Verify that sync_global_skills checks and synchronizes external global skills directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            skills_dir = tmppath / "skills" / "test-skill"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Test Skill\nCanonical content\n", encoding="utf-8")

            global_dir = tmppath / "global_skills"
            global_skill = global_dir / "test-skill"
            global_skill.mkdir(parents=True)
            (global_skill / "SKILL.md").write_text("# Test Skill\nOutdated content\n", encoding="utf-8")

            # Check without write -> detects drift
            in_sync, drifts = sync_templates.sync_global_skills(tmppath, global_dir, write=False)
            self.assertFalse(in_sync)
            self.assertEqual(len(drifts), 1)
            self.assertIn("Global skill 'test-skill' diverges", drifts[0])

            # Write -> synchronizes global skill
            in_sync_w, drifts_w = sync_templates.sync_global_skills(tmppath, global_dir, write=True)
            self.assertFalse(in_sync_w)
            self.assertEqual(
                (global_skill / "SKILL.md").read_text(encoding="utf-8"),
                "# Test Skill\nCanonical content\n",
            )

            # Check again -> passes with 0 drift
            in_sync_after, drifts_after = sync_templates.sync_global_skills(tmppath, global_dir, write=False)
            self.assertTrue(in_sync_after)
            self.assertEqual(len(drifts_after), 0)

    def test_sync_global_skills_resources(self):
        """Verify that sync_global_skills detects and synchronizes resources/* for skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Canonical skills with resources
            init_skill = tmppath / "skills" / "init-meta-project"
            init_res = init_skill / "resources"
            init_res.mkdir(parents=True)
            (init_skill / "SKILL.md").write_bytes(b"# Init Skill\n")
            (init_res / "AGENTS.md").write_bytes(b"# Canonical AGENTS\n")
            (init_res / "observations.md").write_bytes(b"# Canonical OBS\n")

            manage_skill = tmppath / "skills" / "manage-meta-project"
            manage_res = manage_skill / "resources"
            manage_res.mkdir(parents=True)
            (manage_skill / "SKILL.md").write_bytes(b"# Manage Skill\n")
            (manage_res / "profile.md").write_bytes(b"# Canonical PROFILE\n")

            # Global directory
            global_dir = tmppath / "global_skills"
            g_init = global_dir / "init-meta-project"
            g_init.mkdir(parents=True)
            (g_init / "SKILL.md").write_bytes(b"# Init Skill\n")
            # Missing resources in g_init

            g_manage = global_dir / "manage-meta-project"
            g_manage_res = g_manage / "resources"
            g_manage_res.mkdir(parents=True)
            (g_manage / "SKILL.md").write_bytes(b"# Manage Skill\n")
            # Diverged resource in g_manage
            (g_manage_res / "profile.md").write_bytes(b"# Diverged PROFILE\n")

            # 1. Check without write -> detects drift
            in_sync, drifts = sync_templates.sync_global_skills(tmppath, global_dir, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(
                any("init-meta-project" in d and "AGENTS.md" in d for d in drifts),
                f"Missing global resource AGENTS.md must be detected: {drifts}",
            )
            self.assertTrue(
                any("init-meta-project" in d and "observations.md" in d for d in drifts),
                f"Missing global resource observations.md must be detected: {drifts}",
            )
            self.assertTrue(
                any("manage-meta-project" in d and "profile.md" in d for d in drifts),
                f"Diverging global resource profile.md must be detected: {drifts}",
            )

            # 2. Write -> byte-copies missing and diverged resources
            in_sync_w, drifts_w = sync_templates.sync_global_skills(tmppath, global_dir, write=True)
            self.assertFalse(in_sync_w)

            self.assertEqual(
                (g_init / "resources" / "AGENTS.md").read_bytes(),
                b"# Canonical AGENTS\n",
            )
            self.assertEqual(
                (g_init / "resources" / "observations.md").read_bytes(),
                b"# Canonical OBS\n",
            )
            self.assertEqual(
                (g_manage / "resources" / "profile.md").read_bytes(),
                b"# Canonical PROFILE\n",
            )

            # 3. Check again -> in_sync=True, drifts=[]
            in_sync_after, drifts_after = sync_templates.sync_global_skills(tmppath, global_dir, write=False)
            self.assertTrue(in_sync_after)
            self.assertEqual(drifts_after, [])


class TestAbsentMirrorContract(unittest.TestCase):
    """Wave G follow-up (distribution contract): mirror parity applies only
    when a self-installation mirror exists. A distribution checkout (the
    framework branch carries no .agents/) is a valid tree without mirrors -
    the sync must stay green over canonical sources and per-skill resources."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not implemented yet")

    def test_dist_tree_without_agents_mirror_is_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tmpl_k = root / "templates" / "project_knowledge"
            tmpl_k.mkdir(parents=True)
            for name in ("boundaries.md", "observations.md", "weak_spots.md", "architecture.md", "tasks.md"):
                (tmpl_k / name).write_text(f"canonical {name}\n", encoding="utf-8")
            (root / "templates" / "AGENTS.md").write_text("canonical AGENTS.md\n", encoding="utf-8")
            team = root / "templates" / "team"
            team.mkdir(parents=True)
            for name in ("profile.md", "notes.md", "system_prompt.md"):
                (team / name).write_text(f"canonical {name}\n", encoding="utf-8")
            for skill in ("init-meta-project", "manage-meta-project", "record-observation", "sync-architecture", "ground-meta-project"):
                sdir = root / "skills" / skill
                sdir.mkdir(parents=True)
                (sdir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
            in_sync, _ = sync_templates.run_sync(root, write=True)  # repair pass
            in_sync_after, drifts_after = sync_templates.run_sync(root, write=False)
            self.assertTrue(
                in_sync_after,
                f"dist tree must be valid without .agents after repair: {drifts_after}",
            )
            self.assertEqual([], drifts_after)

    def test_mirror_present_keeps_parity_enforced(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill = root / "skills" / "init-meta-project"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# init v2\n", encoding="utf-8")
            mirror = root / ".agents" / "skills" / "init-meta-project"
            mirror.mkdir(parents=True)
            (mirror / "SKILL.md").write_text("# init v1 diverged\n", encoding="utf-8")
            in_sync, drifts = sync_templates.run_sync(root, write=False)
            self.assertFalse(in_sync, "a diverged mirror must still report drift")
            self.assertTrue(drifts)

class TestEngineResourceRuntimeLayout(unittest.TestCase):
    """(a) Engine maps resource components into the .agents/skills runtime layout."""

    def setUp(self):
        if _resolve_target is None:
            self.skipTest("update_meta_project engine module not importable")

    def _repo_with_runtime_layout(self, root: Path) -> Path:
        (root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
        return root

    def test_resource_component_maps_to_agents_skills_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_runtime_layout(Path(tmp))
            for res_name in ("AGENTS.md", "record-observation-SKILL.md"):
                self.assertEqual(
                    _resolve_target(
                        f"skills/init-meta-project/resources/{res_name}", repo, None
                    ),
                    f".agents/skills/init-meta-project/resources/{res_name}",
                    "resource component must install at the runtime layout path",
                )

    def test_recorded_target_stays_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_runtime_layout(Path(tmp))
            self.assertEqual(
                _resolve_target(
                    "skills/init-meta-project/resources/AGENTS.md",
                    repo,
                    {"target": "skills/init-meta-project/resources/AGENTS.md"},
                ),
                "skills/init-meta-project/resources/AGENTS.md",
                "a recorded lock target must win over the fresh layout rule",
            )

    def test_without_agents_skills_distribution_path_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)  # no .agents/skills/
            self.assertEqual(
                _resolve_target(
                    "skills/init-meta-project/resources/AGENTS.md", repo, None
                ),
                "skills/init-meta-project/resources/AGENTS.md",
            )

    def test_plain_skill_mapping_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_runtime_layout(Path(tmp))
            self.assertEqual(
                _resolve_target("skills/w/SKILL.md", repo, None),
                ".agents/skills/w/SKILL.md",
            )


class TestManifestResourceComponents(unittest.TestCase):
    """(b) Manifest gains the 9 resource components and bumps to alpha.4."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.components = cls.manifest.get("components") or []

    def test_framework_version_matches_changelog_latest(self):
        """Wave F T-D6 lock: manifest framework_version must equal the latest
        release version heading in CHANGELOG.md (the two are bumped together
        at release time). Supersedes the frozen '1.0.0-alpha.4' hardcode,
        which went stale at every release bump while still asserting exact
        equality."""
        self.assertEqual(
            self.manifest.get("framework_version"),
            _latest_changelog_version(),
            "manifest framework_version must equal the latest CHANGELOG "
            "release heading (bump both together at release time)",
        )

    def test_init_resource_components_declared(self):
        """Wave G Lane S supersession (plan
        docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md §4 —
        mandated manifest change): the manifest resource set grew from 9 to 12
        (3 manage resources riding the same init-P2 pattern), so the former
        exact-set equality over ALL resource components is superseded to a
        subset lock: the 9 init resources are declared with their init-SKILL.md
        requires edge. The 3 manage components are locked by
        tests/test_gwave_s.py (TestManifestManageResourceComponents)."""
        resources = {
            str(c.get("path", "")): c
            for c in self.components
            if c.get("kind") == "resource"
        }
        expected = {
            f"skills/init-meta-project/resources/{name}" for name in CANONICAL_SOURCES
        }
        self.assertTrue(
            expected.issubset(resources),
            f"manifest resource components must cover the 9 init resources; "
            f"missing: {sorted(expected - set(resources))}",
        )
        for path, comp in resources.items():
            if not path.startswith("skills/init-meta-project/resources/"):
                continue
            self.assertEqual(
                comp.get("requires"),
                ["skills/init-meta-project/SKILL.md"],
                f"resource {path} must depend on the init SKILL.md",
            )
            self.assertTrue(
                (ROOT_DIR / path).is_file(),
                f"resource component path absent from repo tree: {path}",
            )


class TestInitSkillLoadingContract(unittest.TestCase):
    """(c) SKILL.md carries the Resource Loading Contract + per-step pointers."""

    @classmethod
    def setUpClass(cls):
        cls.text = INIT_SKILL_PATH.read_text(encoding="utf-8")

    def test_loading_contract_block_present(self):
        self.assertIn("Resource Loading Contract", self.text)

    def test_scenario_read_policy_clauses(self):
        self.assertIn(
            "reads NO resources",
            self.text,
            "contract must state that the healthy repeat-run reads no resources",
        )
        self.assertIn(
            "exactly when its step needs it",
            self.text,
            "contract must state on-demand reads for clean init (Scenario 1)",
        )
        self.assertIn(
            "only its procedure",
            self.text,
            "contract must state Scenario 4 reads only its procedure",
        )

    def test_missing_resource_envelope_and_guidance(self):
        self.assertIn(
            "MISSING_RESOURCE",
            self.text,
            "missing-resource envelope code absent from SKILL.md",
        )
        self.assertIn(MISSING_RESOURCE_GUIDANCE, self.text)

    def test_per_step_resource_pointers(self):
        for name in CANONICAL_SOURCES:
            self.assertIn(
                f"resources/{name}",
                self.text,
                f"SKILL.md must name the resource file per step: resources/{name}",
            )

    def test_no_embedded_template_blocks_remain(self):
        self.assertNotIn(
            "<!-- TEMPLATE:BEGIN",
            self.text,
            "embedded template blocks must be extracted to resources/",
        )


class TestSyncResourcesZeroDrift(unittest.TestCase):
    """(d) The repo tree is at 0 template drift: a full temp CLONE of the
    repository reaches 0 drift after ``sync_templates --write`` then
    ``--check``.

    Wave F T-D6: a test must never run ``sync --write`` against the LIVE
    repo tree — the fixture clones the tree (minus ``.git``/bytecode caches)
    and writes only inside the clone. A drifted live tree is still detected,
    because the clone inherits the drifted bytes byte-for-byte.
    """

    def test_write_then_check_zero_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            clone_root = Path(tmp) / "repo-clone"
            shutil.copytree(
                ROOT_DIR,
                clone_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            write_res = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--write", "--repo-root", str(clone_root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                write_res.returncode,
                0,
                f"sync_templates --write failed on the repo clone: "
                f"{write_res.stdout}\n{write_res.stderr}",
            )
            check_res = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--check", "--repo-root", str(clone_root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                check_res.returncode,
                0,
                f"sync_templates --check detected drift in the repo clone: "
                f"{check_res.stdout}\n{check_res.stderr}",
            )


class TestResourcesByteCanonical(unittest.TestCase):
    """(e) Every resources/ file is byte-equal to its canonical source (and mirror)."""

    def setUp(self):
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )
        super().setUp()


    def test_resources_match_canonical_bytes(self):
        for name, canon_rel in CANONICAL_SOURCES.items():
            res_path = RESOURCES_DIR / name
            canon_path = ROOT_DIR / canon_rel
            self.assertTrue(
                res_path.is_file(), f"missing resource file: {res_path}"
            )
            self.assertEqual(
                res_path.read_bytes(),
                canon_path.read_bytes(),
                f"resource {name} diverges from canonical {canon_rel} "
                f"(run sync_templates --write)",
            )

    def test_mirror_resources_match_canonical_bytes(self):
        for name, canon_rel in CANONICAL_SOURCES.items():
            mirror_path = MIRROR_RESOURCES_DIR / name
            self.assertTrue(
                mirror_path.is_file(),
                f"missing mirrored resource file: {mirror_path}",
            )
            self.assertEqual(
                mirror_path.read_bytes(),
                (ROOT_DIR / canon_rel).read_bytes(),
                f"mirrored resource {name} diverges from canonical {canon_rel}",
            )


class TestResourceTargetsDeclared(unittest.TestCase):
    """RESOURCE_TARGETS declares the canonical -> resource mapping in sync_templates."""

    def test_resource_targets_cover_all_nine(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not importable")
        targets = getattr(sync_templates, "RESOURCE_TARGETS", None)
        self.assertIsNotNone(targets, "RESOURCE_TARGETS missing from sync_templates")
        self.assertEqual(
            dict(targets), CANONICAL_SOURCES, "RESOURCE_TARGETS mapping mismatch"
        )

class TestEngineManageResourceRuntimeLayout(unittest.TestCase):
    """(a) Engine plan maps manage resources into the .agents/skills runtime layout."""

    def setUp(self):
        if _resolve_target is None:
            self.skipTest("update_meta_project engine module not importable")

    def _runtime_layout_consumer_repo(self, root: Path) -> Path:
        """Consumer fixture with the init-deployed runtime layout (.agents/skills/)."""
        (root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
        return root

    def test_manage_resource_component_maps_to_agents_skills_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._runtime_layout_consumer_repo(Path(tmp))
            for res_name in MANAGE_CANONICAL_SOURCES:
                self.assertEqual(
                    _resolve_target(
                        f"skills/manage-meta-project/resources/{res_name}", repo, None
                    ),
                    f".agents/skills/manage-meta-project/resources/{res_name}",
                    "manage resource component must install at the runtime layout path",
                )

    def test_manage_recorded_target_stays_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._runtime_layout_consumer_repo(Path(tmp))
            self.assertEqual(
                _resolve_target(
                    "skills/manage-meta-project/resources/profile.md",
                    repo,
                    {"target": "skills/manage-meta-project/resources/profile.md"},
                ),
                "skills/manage-meta-project/resources/profile.md",
                "a recorded lock target must win over the fresh layout rule",
            )

    def test_manage_without_agents_skills_distribution_path_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)  # no .agents/skills/ — distribution layout consumer
            self.assertEqual(
                _resolve_target(
                    "skills/manage-meta-project/resources/profile.md", repo, None
                ),
                "skills/manage-meta-project/resources/profile.md",
            )


class TestManifestManageResourceComponents(unittest.TestCase):
    """(b) Manifest gains the 3 manage resource components; edges intact."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.components = cls.manifest.get("components") or []

    def _resource_components(self):
        return {
            str(c.get("path", "")): c for c in self.components if c.get("kind") == "resource"
        }

    def test_three_manage_resource_components_declared(self):
        resources = self._resource_components()
        expected = {
            f"skills/manage-meta-project/resources/{name}" for name in MANAGE_CANONICAL_SOURCES
        }
        self.assertTrue(
            expected.issubset(resources),
            f"manifest must declare the 3 manage resource components; missing: "
            f"{sorted(expected - set(resources))}",
        )
        for path, comp in resources.items():
            if not path.startswith("skills/manage-meta-project/resources/"):
                continue
            self.assertEqual(
                comp.get("requires"),
                [MANAGE_SKILL_RELPATH],
                f"resource {path} must depend on the manage SKILL.md",
            )
            self.assertTrue(
                (ROOT_DIR / path).is_file(),
                f"manage resource component path absent from repo tree: {path}",
            )

    def test_resource_component_count_is_fifteen(self):
        """Edge: 9 init resources (Wave E P2) + 3 manage resources (Wave G) + 3 references (Wave Z2-B)."""
        resources = self._resource_components()
        self.assertEqual(
            len(resources), 15,
            f"resource components must be exactly the 9 init + 3 manage + 3 references set; got {sorted(resources)}",
        )

    def test_references_resource_components_declared(self):
        resources = self._resource_components()
        expected = {
            "skills/manage-meta-project/references/competencies.md": "skills/manage-meta-project/SKILL.md",
            "skills/init-meta-project/references/scenarios.md": "skills/init-meta-project/SKILL.md",
            "skills/update-meta-project/references/troubleshooting.md": "skills/update-meta-project/SKILL.md",
        }
        for path, req_skill in expected.items():
            self.assertIn(path, resources, f"Missing {path} in manifest resources")
            self.assertEqual(
                resources[path].get("requires"),
                [req_skill],
                f"resource {path} must depend on {req_skill}",
            )
            self.assertTrue(
                (ROOT_DIR / path).is_file(),
                f"resource component path absent from repo tree: {path}",
            )

    def test_manage_skill_component_edge_intact(self):
        by_path = {str(c.get("path", "")): c for c in self.components}
        self.assertIn(MANAGE_SKILL_RELPATH, by_path)
        self.assertEqual(
            by_path[MANAGE_SKILL_RELPATH].get("kind"), "skill",
            "manage SKILL.md must remain a skill component",
        )
        self.assertEqual(
            by_path[MANAGE_SKILL_RELPATH].get("requires"), ["scripts/manage_reports.py"],
            "manage SKILL.md must keep its script dependency edge",
        )

    def test_resources_are_leaf_components(self):
        """Edge: no component may require a manage resource (resources are leaves)."""
        manage_res_prefix = "skills/manage-meta-project/resources/"
        for c in self.components:
            for req in c.get("requires") or []:
                self.assertFalse(
                    str(req).startswith(manage_res_prefix),
                    f"component {c.get('path')} must not depend on a manage resource: {req}",
                )


class TestManageSkillLoadingContract(unittest.TestCase):
    """(c) manage SKILL.md carries the Resource Loading Contract; slim shape;
    no embedded TEMPLATE blocks."""

    @classmethod
    def setUpClass(cls):
        cls.text = MANAGE_SKILL_PATH.read_text(encoding="utf-8")

    def test_loading_contract_block_present(self):
        self.assertIn("Resource Loading Contract", self.text)

    def test_phase_read_policy_clauses(self):
        self.assertIn(
            "reads NO resources",
            self.text,
            "contract must state that the non-materializing phases read no resources",
        )
        self.assertIn(
            "exactly when its step needs it",
            self.text,
            "contract must state on-demand reads for the materializing phases",
        )

    def test_missing_resource_envelope_and_guidance(self):
        self.assertIn(
            "MISSING_RESOURCE",
            self.text,
            "missing-resource envelope code absent from SKILL.md",
        )
        self.assertIn(MISSING_RESOURCE_GUIDANCE, self.text)

    def test_per_step_resource_pointers(self):
        for name in MANAGE_CANONICAL_SOURCES:
            self.assertIn(
                f"resources/{name}",
                self.text,
                f"SKILL.md must name the resource file per step: resources/{name}",
            )

    def test_no_embedded_template_blocks_remain(self):
        self.assertNotIn(
            "<!-- TEMPLATE:BEGIN",
            self.text,
            "embedded template blocks must be extracted to resources/",
        )
        self.assertNotIn(
            "Embedded Reference Templates",
            self.text,
            "the embedded-templates section must be gone from the slim skill",
        )

    def test_duplicate_phase2_headers_fixed(self):
        """The old skill had two `#### 2.` headings in Phase 2; the slim skill
        numbers its Phase 2 subsections 1..4 exactly once each."""
        numbered = re.findall(r"^#### (\d+)\.", self.text, flags=re.MULTILINE)
        self.assertEqual(
            numbered, ["1", "2", "3", "4"],
            f"Phase 2 subsection numbering must be 1..4 without duplicates: {numbered}",
        )

    def test_slim_shape_locked(self):
        lines = self.text.splitlines()
        self.assertLessEqual(
            len(lines), MANAGE_SKILL_MAX_LINES,
            f"manage SKILL.md must stay within the wave-G slim bound "
            f"({MANAGE_SKILL_MAX_LINES} lines); got {len(lines)}",
        )

    def test_behavioral_contracts_retained(self):
        """Slimming must not lose the phase-mandated contracts."""
        for marker in (
            "Fail-Closed Block",
            "Machine-Enforced Intake",
            "evaluate_manage_intake",
            "Staleness Protocol",
            "Topology Precedence Invariants",
            "Action Differentiation (The 5 Operations)",
            "Polyglot Stack Isolation Rule",
            "Mandatory Dispatcher Rule",
            "Open Competency Catalog",
            "task CERTAINTY beats task size",
            "acceptance criterion",
            "model tier",
            "verifier",
            "Prohibition on autonomous deletion",
            "Profile Created ≠ Loaded by Harness",
            "Execution Role Invariance",
            "Handoff Chain Limit",
            "dispatching-parallel-agents",
            "Circuit Breaker & Flow Tracing",
            "Toolchain Handoff Tripwire",
            "- [>]",
            "changes[]",
            "add_role",
        ):
            self.assertIn(marker, self.text, f"behavioral contract lost while slimming: {marker}")

    def test_handoff_packet_format_retained(self):
        self.assertIn("### Task Handoff Package: [agent-A -> agent-B]", self.text)
        for field in (
            "- Original goal:",
            "- Completed work:",
            "- Handoff boundary:",
            "- Recommended prompt for agent-B:",
        ):
            self.assertIn(field, self.text, f"handoff packet field lost: {field}")

    def test_skill_format_sections_present(self):
        self.assertRegex(self.text, r"^---\s*\n", "frontmatter missing")
        self.assertIn("name: manage-meta-project", self.text)
        self.assertIn("description:", self.text)
        self.assertIn("## When to invoke skill", self.text)
        self.assertIn("## Execution steps", self.text)


class TestManageResourcesByteCanonical(unittest.TestCase):
    """(e) Every manage resources/ file is byte-equal to its canonical source (and mirror)."""

    def setUp(self):
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )
        super().setUp()


    def test_resources_match_canonical_bytes(self):
        for name, canon_rel in MANAGE_CANONICAL_SOURCES.items():
            res_path = MANAGE_RESOURCES_DIR / name
            canon_path = ROOT_DIR / canon_rel
            self.assertTrue(
                res_path.is_file(), f"missing resource file: {res_path}"
            )
            self.assertEqual(
                res_path.read_bytes(),
                canon_path.read_bytes(),
                f"resource {name} diverges from canonical {canon_rel} "
                f"(run sync_templates --write)",
            )

    def test_mirror_resources_match_canonical_bytes(self):
        for name, canon_rel in MANAGE_CANONICAL_SOURCES.items():
            mirror_path = MANAGE_MIRROR_RESOURCES_DIR / name
            self.assertTrue(
                mirror_path.is_file(),
                f"missing mirrored resource file: {mirror_path}",
            )
            self.assertEqual(
                mirror_path.read_bytes(),
                (ROOT_DIR / canon_rel).read_bytes(),
                f"mirrored resource {name} diverges from canonical {canon_rel}",
            )

    def test_mirror_skill_matches_canonical_bytes(self):
        self.assertEqual(
            MANAGE_MIRROR_SKILL_PATH.read_bytes(),
            MANAGE_SKILL_PATH.read_bytes(),
            "manage SKILL.md mirror diverges from the canonical skill",
        )


class TestManageResourceTargetsDeclared(unittest.TestCase):
    """(d) sync_templates declares manage's canonical pairs; embedded machinery gone."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not importable")

    def test_manage_resource_targets_mapping(self):
        self.assertEqual(
            dict(sync_templates.MANAGE_RESOURCE_TARGETS), MANAGE_CANONICAL_SOURCES,
            "MANAGE_RESOURCE_TARGETS mapping mismatch",
        )

    def test_init_resource_targets_unchanged(self):
        """Cross-lock with tests/test_ewave_p.py: the init mapping stays the 9 entries."""
        self.assertEqual(
            dict(sync_templates.RESOURCE_TARGETS),
            {
                "observations.md": "templates/project_knowledge/observations.md",
                "boundaries.md": "templates/project_knowledge/boundaries.md",
                "weak_spots.md": "templates/project_knowledge/weak_spots.md",
                "architecture.md": "templates/project_knowledge/architecture.md",
                "tasks.md": "templates/project_knowledge/tasks.md",
                "AGENTS.md": "templates/AGENTS.md",
                "record-observation-SKILL.md": "skills/record-observation/SKILL.md",
                "sync-architecture-SKILL.md": "skills/sync-architecture/SKILL.md",
                "ground-meta-project-SKILL.md": "skills/ground-meta-project/SKILL.md",
            },
        )

    def test_resource_sync_sets_register_both_skills(self):
        self.assertEqual(
            dict(sync_templates.RESOURCE_SYNC_SETS),
            {
                sync_templates.INIT_RESOURCES_DIR: sync_templates.RESOURCE_TARGETS,
                sync_templates.MANAGE_RESOURCES_DIR: sync_templates.MANAGE_RESOURCE_TARGETS,
            },
        )

    def test_embedded_machinery_removed(self):
        for symbol in ("EMBEDDED_TARGETS", "replace_embedded_template", "sync_embedded_templates"):
            self.assertFalse(
                hasattr(sync_templates, symbol),
                f"removed embedded-sync symbol reappeared: {symbol}",
            )


class TestSkillReferencesSync(unittest.TestCase):
    """Wave Z2-B: references/ mirroring in sync_skill_mirroring and sync_global_skills."""

    def test_sync_skill_mirroring_handles_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "sample-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
            ref_dir = skill_dir / "references"
            ref_dir.mkdir(parents=True)
            (ref_dir / "guide.md").write_text("# Reference Guide\n", encoding="utf-8")

            agents_dir = root / ".agents" / "skills" / "sample-skill"
            agents_dir.mkdir(parents=True)
            (agents_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            # Check: drift detected for missing reference in .agents
            in_sync, drifts = sync_templates.sync_skill_mirroring(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(any("references/guide.md" in d for d in drifts))

            # Write: repair drift
            in_sync_w, _ = sync_templates.sync_skill_mirroring(root, write=True)
            mirrored_ref = agents_dir / "references" / "guide.md"
            self.assertTrue(mirrored_ref.is_file())
            self.assertEqual(mirrored_ref.read_bytes(), (ref_dir / "guide.md").read_bytes())

            # Check again: in_sync=True
            in_sync_after, drifts_after = sync_templates.sync_skill_mirroring(root, write=False)
            self.assertTrue(in_sync_after)
            self.assertEqual(drifts_after, [])

    def test_sync_global_skills_handles_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "sample-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
            ref_dir = skill_dir / "references"
            ref_dir.mkdir(parents=True)
            (ref_dir / "guide.md").write_text("# Reference Guide\n", encoding="utf-8")

            global_dir = root / "global_cache"
            global_dir.mkdir(parents=True)
            global_skill = global_dir / "sample-skill"
            global_skill.mkdir(parents=True)
            (global_skill / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            # Check: drift detected for missing reference in global
            in_sync, drifts = sync_templates.sync_global_skills(root, global_dir=global_dir, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(any("references" in d or "guide.md" in d for d in drifts))

            # Write: repair drift
            sync_templates.sync_global_skills(root, global_dir=global_dir, write=True)
            target_ref = global_skill / "references" / "guide.md"
            self.assertTrue(target_ref.is_file())
            self.assertEqual(target_ref.read_bytes(), (ref_dir / "guide.md").read_bytes())

            # Check again: in_sync=True
            in_sync_after, drifts_after = sync_templates.sync_global_skills(root, global_dir=global_dir, write=False)
            self.assertTrue(in_sync_after)
            self.assertEqual(drifts_after, [])


if __name__ == '__main__':
    unittest.main()
