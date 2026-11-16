"""
Unit tests for scripts/sync_templates.py (Template Injection & Skill Parity Synchronizer).
Verifies marker-based embedded template replacement, resource byte-copy parity,
skill parity validation, and CLI exit codes.

Wave E Lane P2 supersession (plan §6a owner decision ADJUST AND PROCEED,
fixture scope authorized by the dispatcher 2026-11-16): init's embedded
TEMPLATE-block entries moved to RESOURCE_TARGETS byte-copy semantics —
test_missing_template_sentinel_raises_drift_error,
test_missing_canonical_template_reports_drift, and
test_cli_check_drift_detected_exit_1 were retargeted to the resources design
(same intents: missing sync-managed file -> drift; missing canonical -> fatal
drift; CLI write/check roundtrip).
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


SAMPLE_SKILL_WITH_EMBEDDED = """# Sample Skill

## Embedded Reference Templates

### Template: `sample.md`
<!-- TEMPLATE:BEGIN sample.md -->
```markdown
Old outdated content
```
<!-- TEMPLATE:END sample.md -->

### Template: other.md
<!-- TEMPLATE:BEGIN other.md -->
```markdown
Other content
```
<!-- TEMPLATE:END other.md -->
"""


class TestTemplateInjection(unittest.TestCase):
    """Test marker-based embedded template replacement in markdown files."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not implemented yet")

    def test_replace_embedded_template_with_backticks(self):
        new_content = "# Fresh Canonical Template\nNew content here."
        updated, modified, err = sync_templates.replace_embedded_template(
            SAMPLE_SKILL_WITH_EMBEDDED, "sample.md", new_content
        )
        self.assertIsNone(err)
        self.assertTrue(modified)
        self.assertIn("# Fresh Canonical Template", updated)
        self.assertNotIn("Old outdated content", updated)
        # Verify second template was untouched
        self.assertIn("Other content", updated)

    def test_replace_embedded_template_without_backticks(self):
        new_content = "Replacement for other"
        updated, modified, err = sync_templates.replace_embedded_template(
            SAMPLE_SKILL_WITH_EMBEDDED, "other.md", new_content
        )
        self.assertIsNone(err)
        self.assertTrue(modified)
        self.assertIn("Replacement for other", updated)
        self.assertIn("Old outdated content", updated)

    def test_missing_template_sentinel_raises_drift_error(self):
        """Superseded per plan §6a (init embedded blocks -> resources/): when a
        required sync-managed init resource file is missing, drift is detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "init-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Init Skill\nRouting only.\n", encoding="utf-8")

            # All canonical sources present, resources/ intentionally absent.
            tmpl_dir = root / "templates" / "project_knowledge"
            tmpl_dir.mkdir(parents=True, exist_ok=True)
            for name in ("boundaries.md", "observations.md", "weak_spots.md", "architecture.md", "tasks.md"):
                (tmpl_dir / name).write_text(f"canonical {name}\n", encoding="utf-8")
            (root / "templates" / "AGENTS.md").write_text("canonical AGENTS.md\n", encoding="utf-8")
            for skill in ("record-observation", "sync-architecture", "ground-meta-project"):
                sdir = root / "skills" / skill
                sdir.mkdir(parents=True, exist_ok=True)
                (sdir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

            in_sync, drift_msgs = sync_templates.sync_skill_resources(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(
                any("Missing resource file" in msg for msg in drift_msgs),
                f"missing resource file must be reported as drift: {drift_msgs}",
            )

    def test_missing_canonical_template_reports_drift(self):
        """Superseded per plan §6a (init embedded blocks -> resources/): a missing
        canonical source file is reported as drift rather than silently ignored."""
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

    def test_missing_target_skill_reports_drift(self):
        """Verify that missing target skill file is reported as drift rather than silently ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create template but not skill file
            tmpl_dir = root / "templates" / "project_knowledge"
            tmpl_dir.mkdir(parents=True, exist_ok=True)
            (tmpl_dir / "boundaries.md").write_text("# Canonical Boundaries\n", encoding="utf-8")

            in_sync, drift_msgs = sync_templates.sync_embedded_templates(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(any("Missing target skill file" in msg for msg in drift_msgs))

    def test_nested_fenced_backticks_replacement(self):
        """Verify template replacement handles inner triple backtick code blocks properly."""
        tmpl_content = "# Title\n\n```python\nprint('hello')\n```\n"
        skill_text = (
            "Header\n\n"
            "<!-- TEMPLATE:BEGIN test.md -->\n"
            "```markdown\nOld content\n```\n"
            "<!-- TEMPLATE:END test.md -->\n\nFooter\n"
        )
        updated, modified, err = sync_templates.replace_embedded_template(skill_text, "test.md", tmpl_content)
        self.assertIsNone(err)
        self.assertTrue(modified)
        self.assertIn("print('hello')", updated)
        self.assertIn("<!-- TEMPLATE:END test.md -->", updated)

    def test_replace_no_op_when_identical(self):
        updated, modified, err = sync_templates.replace_embedded_template(
            SAMPLE_SKILL_WITH_EMBEDDED, "other.md", "Other content\n"
        )
        self.assertIsNone(err)
        self.assertFalse(modified)
        self.assertEqual(updated, SAMPLE_SKILL_WITH_EMBEDDED)


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

            # Create skills/init-meta-project (routing-only skill; resources/
            # intentionally absent — superseded per plan §6a: init ships its
            # templates as sync-managed resource files, not embedded blocks)
            (tmppath / "skills" / "init-meta-project").mkdir(parents=True)
            init_skill = (
                "# Init Skill\n"
                "## Resource Loading Contract\n"
                "Clean init reads each resource exactly when its step needs it.\n"
            )
            (tmppath / "skills" / "init-meta-project" / "SKILL.md").write_text(
                init_skill, encoding="utf-8"
            )

            # Create skills/manage-meta-project (in sync)
            (tmppath / "skills" / "manage-meta-project").mkdir(parents=True)
            manage_skill = (
                "# Manage Skill\n"
                "### Template: `profile.md`\n<!-- TEMPLATE:BEGIN profile.md -->\n```markdown\nCANONICAL PROFILE\n```\n<!-- TEMPLATE:END profile.md -->\n"
                "### Template: `notes.md`\n<!-- TEMPLATE:BEGIN notes.md -->\n```markdown\nCANONICAL NOTES\n```\n<!-- TEMPLATE:END notes.md -->\n"
                "### Template: `system_prompt.md`\n<!-- TEMPLATE:BEGIN system_prompt.md -->\n```markdown\nCANONICAL PROMPT\n```\n<!-- TEMPLATE:END system_prompt.md -->\n"
            )
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

            # Check that the resource copies (canonical + mirrored) received the canonical template
            updated_resource = (tmppath / "skills" / "init-meta-project" / "resources" / "boundaries.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL BOUNDARIES V2", updated_resource)
            mirrored_resource = (tmppath / ".agents" / "skills" / "init-meta-project" / "resources" / "boundaries.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL BOUNDARIES V2", mirrored_resource)

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
