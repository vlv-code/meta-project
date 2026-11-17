"""
Unit tests for scripts/sync_templates.py (Template Injection & Skill Parity Synchronizer).
Verifies per-skill resource byte-copy parity, skill parity validation, and CLI exit codes.

Wave E Lane P2 supersession (plan §6a owner decision ADJUST AND PROCEED,
fixture scope authorized by the dispatcher 2026-11-16): init's embedded
TEMPLATE-block entries moved to RESOURCE_TARGETS byte-copy semantics —
test_missing_template_sentinel_raises_drift_error,
test_missing_canonical_template_reports_drift, and
test_cli_check_drift_detected_exit_1 were retargeted to the resources design
(same intents: missing sync-managed file -> drift; missing canonical -> fatal
drift; CLI write/check roundtrip).

Wave G Lane S supersession (plan docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md
§4, lane file ownership: tests/test_sync_templates.py manage-embedded assertions):
manage-meta-project moved from EMBEDDED_TARGETS to resource byte-copy semantics
too, which made the embedded injection machinery dead code — it was removed.
Superseded here:
  - test_replace_embedded_template_with_backticks / _without_backticks /
    test_nested_fenced_backticks_replacement / test_replace_no_op_when_identical
    (pure-function tests of the removed replace_embedded_template helper) —
    dropped; the byte-copy contract they indirectly guarded is now asserted
    directly by the resource-equivalence tests below (drift = recoverable,
    missing canonical = fatal — semantics preserved).
  - test_missing_target_skill_reports_drift (relied on the module-level
    EMBEDDED_TARGETS manage entry) — retargeted to resource equivalence as
    test_missing_manage_resources_reports_drift: missing sync-managed resource
    files are reported as (recoverable) drift, for BOTH skill resource sets.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import sync_templates
except ImportError:
    sync_templates = None


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


if __name__ == "__main__":
    unittest.main()
