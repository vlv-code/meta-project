"""
Unit tests for scripts/sync_templates.py (Template Injection & Skill Parity Synchronizer).
Verifies marker-based embedded template replacement, skill parity validation, and CLI exit codes.
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
        """Verify that when a required template block is missing, drift is detected with exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "init-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Corrupted Skill\nNo templates here.\n", encoding="utf-8")

            tmpl_dir = root / "templates" / "project_knowledge"
            tmpl_dir.mkdir(parents=True, exist_ok=True)
            (tmpl_dir / "boundaries.md").write_text("# Canonical Boundaries\n", encoding="utf-8")

            in_sync, drift_msgs = sync_templates.sync_embedded_templates(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(any("Missing template block" in msg for msg in drift_msgs))

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
            # Create templates/
            (tmppath / "templates" / "project_knowledge").mkdir(parents=True)
            (tmppath / "templates" / "project_knowledge" / "boundaries.md").write_text(
                "CANONICAL BOUNDARIES V2", encoding="utf-8"
            )

            # Create skills/
            (tmppath / "skills" / "init-meta-project").mkdir(parents=True)
            skill_text = """# Init Skill\n### Template: `boundaries.md`\n<!-- TEMPLATE:BEGIN boundaries.md -->\n```markdown\nOLD BOUNDARIES V1\n```\n<!-- TEMPLATE:END boundaries.md -->\n"""
            (tmppath / "skills" / "init-meta-project" / "SKILL.md").write_text(
                skill_text, encoding="utf-8"
            )

            # Create .agents/skills/ with matching old content
            (tmppath / ".agents" / "skills" / "init-meta-project").mkdir(parents=True)
            (tmppath / ".agents" / "skills" / "init-meta-project" / "SKILL.md").write_text(
                skill_text, encoding="utf-8"
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

            # Check that skills/ and .agents/skills/ both received the canonical template
            updated_skill = (tmppath / "skills" / "init-meta-project" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL BOUNDARIES V2", updated_skill)
            mirrored_skill = (tmppath / ".agents" / "skills" / "init-meta-project" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("CANONICAL BOUNDARIES V2", mirrored_skill)

            # Now --check must pass with 0 exit code
            res_check2 = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res_check2.returncode, 0)


if __name__ == "__main__":
    unittest.main()
