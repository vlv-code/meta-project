"""
Unit tests for scripts/check_boundaries.py (Boundary Gate CLI).
Verifies zone parsing, Default Deny evaluation, glob matching, and exit codes.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

# Import target module from scripts
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import check_boundaries
    from check_boundaries import main
except ImportError:
    check_boundaries = None
    main = None


SAMPLE_BOUNDARIES_MD = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- Creating new tests (`tests/test_unit_*.py`) for auxiliary utilities.
- `docs/**`, `*.md` — technical documentation.
- `src/utils/**` — helper functions.

---

## Yellow Zone (Modification with Mandatory Verification)
- `skills/**` — procedural skills.
- `templates/**` — meta-project templates.
- `src/core/**` — business logic.

---

## Red Zone (Prohibited Without Direct User Confirmation)
- `scripts/check_boundaries.py` — core boundary enforcement CLI.
- `*boundaries.md` — responsibility boundaries policy files.
- `tests/test_integrity.py` — specification tests.
- `.github/workflows/**` — CI/CD pipelines.
- `.gitignore` — ignore rules.
- `LICENSE` — license file.

---

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any directory or file path not explicitly listed in Green, Yellow, or Red zones above is strictly classified as Red Zone by Default.
"""


class TestBoundaryGateParser(unittest.TestCase):
    """Checks extraction of globs from boundaries.md markdown content."""

    def setUp(self):
        if check_boundaries is None:
            self.skipTest("check_boundaries module not implemented yet")

    def test_parse_zones(self):
        zones = check_boundaries.parse_boundaries(SAMPLE_BOUNDARIES_MD)
        self.assertIn("green", zones)
        self.assertIn("yellow", zones)
        self.assertIn("red", zones)

        self.assertIn("docs/**", zones["green"])
        self.assertIn("*.md", zones["green"])
        self.assertIn("skills/**", zones["yellow"])
        self.assertIn("tests/test_integrity.py", zones["red"])
        self.assertIn(".github/workflows/**", zones["red"])

    def test_parenthesis_exceptions_not_extracted_as_globs(self):
        content = """# Boundaries
## Green Zone
- `docs/**`, `*.md` (except the root `AGENTS.md`) — documentation
- Creating new tests (`tests/test_unit_*.py`) for auxiliary utilities.
"""
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("docs/**", zones["green"])
        self.assertIn("*.md", zones["green"])
        self.assertIn("tests/test_unit_*.py", zones["green"])
        self.assertNotIn("AGENTS.md", zones["green"])

    def test_zero_depth_double_star_matching(self):
        regex = check_boundaries.glob_to_regex("src/**/test.py")
        self.assertTrue(bool(regex.match("src/test.py")))
        self.assertTrue(bool(regex.match("src/sub/test.py")))
        self.assertTrue(bool(regex.match("src/sub/nested/test.py")))
        self.assertFalse(bool(regex.match("src/other.py")))



class TestBoundaryGateClassification(unittest.TestCase):
    """Checks zone classification and Default Deny invariant."""

    def setUp(self):
        if check_boundaries is None:
            self.skipTest("check_boundaries module not implemented yet")
        self.zones = check_boundaries.parse_boundaries(SAMPLE_BOUNDARIES_MD)

    def test_green_zone_classification(self):
        zone, reason = check_boundaries.classify_path("docs/decisions.md", self.zones)
        self.assertEqual(zone, "green")

        zone, reason = check_boundaries.classify_path("src/utils/math.py", self.zones)
        self.assertEqual(zone, "green")

    def test_yellow_zone_classification(self):
        zone, reason = check_boundaries.classify_path("skills/init-meta-project/SKILL.md", self.zones)
        self.assertEqual(zone, "yellow")

        zone, reason = check_boundaries.classify_path("templates/AGENTS.md", self.zones)
        self.assertEqual(zone, "yellow")

    def test_red_zone_classification(self):
        zone, reason = check_boundaries.classify_path(".github/workflows/ci.yml", self.zones)
        self.assertEqual(zone, "red")

        zone, reason = check_boundaries.classify_path("tests/test_integrity.py", self.zones)
        self.assertEqual(zone, "red")

        zone, reason = check_boundaries.classify_path("scripts/check_boundaries.py", self.zones)
        self.assertEqual(zone, "red")

        zone, reason = check_boundaries.classify_path(".agents/project_knowledge/boundaries.md", self.zones)
        self.assertEqual(zone, "red")

        zone, reason = check_boundaries.classify_path("templates/project_knowledge/boundaries.md", self.zones)
        self.assertEqual(zone, "red")

    def test_default_deny_black_zone(self):
        # Unmapped file should fall under Default Deny (black/red)
        zone, reason = check_boundaries.classify_path("client/native/main.cpp", self.zones)
        self.assertEqual(zone, "black")
        self.assertIn("Default Deny", reason)

        zone, reason = check_boundaries.classify_path("random_unmapped.sh", self.zones)
        self.assertEqual(zone, "black")

    def test_agents_md_is_not_classified_as_green(self):
        # Even if *.md is in green, root AGENTS.md must NEVER be green
        zone, reason = check_boundaries.classify_path("AGENTS.md", self.zones)
        self.assertIn(zone, ["yellow", "red"])
        self.assertNotEqual(zone, "green")

    def test_specific_test_mask_precedence_over_broad_yellow(self):
        custom_zones = {
            "green": ["tests/test_*.py"],
            "yellow": ["tests/**"],
            "red": ["tests/test_integrity.py"],
        }
        # tests/test_foo.py should be green (specific test file mask beats broad tests/**)
        zone, _ = check_boundaries.classify_path("tests/test_foo.py", custom_zones)
        self.assertEqual(zone, "green")

        # But tests/test_integrity.py must still be strictly red
        zone_red, _ = check_boundaries.classify_path("tests/test_integrity.py", custom_zones)
        self.assertEqual(zone_red, "red")

    def test_non_ascii_and_spaces_path_classification(self):
        # Paths with spaces and Cyrillic/Unicode characters should match correctly
        zone, _ = check_boundaries.classify_path("docs/НЕ ОБРАБОТАННЫЙ meta-project.md", self.zones)
        self.assertEqual(zone, "green")
        zone_nested, _ = check_boundaries.classify_path("docs/some folder with spaces/note.md", self.zones)
        self.assertEqual(zone_nested, "green")



class TestBoundaryGateEvaluation(unittest.TestCase):
    """Checks evaluate_files batch evaluation and policy enforcement."""

    def setUp(self):
        if check_boundaries is None:
            self.skipTest("check_boundaries module not implemented yet")
        self.zones = check_boundaries.parse_boundaries(SAMPLE_BOUNDARIES_MD)

    def test_clean_green_yellow_files_pass(self):
        files = ["docs/readme.md", "skills/sync/SKILL.md", "src/utils/string.py"]
        passed, violations = check_boundaries.evaluate_files(files, self.zones, allow_red_zone=False)
        self.assertTrue(passed)
        self.assertEqual(len(violations), 0)

    def test_red_zone_fails_without_override(self):
        files = ["docs/readme.md", ".github/workflows/ci.yml"]
        passed, violations = check_boundaries.evaluate_files(files, self.zones, allow_red_zone=False)
        self.assertFalse(passed)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["file"], ".github/workflows/ci.yml")
        self.assertEqual(violations[0]["zone"], "red")

    def test_red_zone_passes_with_override(self):
        files = ["docs/readme.md", ".github/workflows/ci.yml"]
        passed, violations = check_boundaries.evaluate_files(files, self.zones, allow_red_zone=True)
        self.assertTrue(passed)
        self.assertEqual(len(violations), 0)

    def test_unmapped_files_always_fail(self):
        files = ["unmapped_folder/some_code.py"]
        passed, violations = check_boundaries.evaluate_files(files, self.zones, allow_red_zone=False)
        self.assertFalse(passed)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["zone"], "black")

    def test_audit_tree_detects_unmapped_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "docs").mkdir()
            (tmppath / "docs" / "readme.md").write_text("# Readme", encoding="utf-8")
            (tmppath / "src" / "utils").mkdir(parents=True)
            (tmppath / "src" / "utils" / "app.py").write_text("print(1)", encoding="utf-8")

            # All mapped
            passed, unmapped, counts = check_boundaries.audit_tree(tmppath, self.zones)
            self.assertTrue(passed)
            self.assertEqual(len(unmapped), 0)
            self.assertGreaterEqual(counts["green"] + counts["yellow"], 2)

            # Introduce unmapped file
            (tmppath / "unmapped_dir").mkdir()
            (tmppath / "unmapped_dir" / "rogue.py").write_text("x = 1", encoding="utf-8")

            passed2, unmapped2, counts2 = check_boundaries.audit_tree(tmppath, self.zones)
            self.assertFalse(passed2)
            self.assertIn("unmapped_dir/rogue.py", [p.replace("\\", "/") for p in unmapped2])



class TestBoundaryGateCLI(unittest.TestCase):
    """Checks CLI execution with subprocess and flags."""

    def setUp(self):
        self.script_path = SCRIPTS_DIR / "check_boundaries.py"
        if not self.script_path.is_file():
            self.skipTest("scripts/check_boundaries.py does not exist yet")

    def test_cli_help(self):
        res = subprocess.run([sys.executable, str(self.script_path), "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("usage:", res.stdout.lower())

    def test_cli_clean_files_exit_0(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as f:
            f.write(SAMPLE_BOUNDARIES_MD)
            boundaries_file = f.name

        try:
            cmd = [
                sys.executable,
                str(self.script_path),
                "--boundaries",
                boundaries_file,
                "--files",
                "docs/test.md",
                "src/utils/test.py",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
        finally:
            Path(boundaries_file).unlink(missing_ok=True)

    def test_cli_red_zone_violation_exit_1(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as f:
            f.write(SAMPLE_BOUNDARIES_MD)
            boundaries_file = f.name

        try:
            cmd = [
                sys.executable,
                str(self.script_path),
                "--boundaries",
                boundaries_file,
                "--files",
                ".github/workflows/ci.yml",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 1)
            self.assertIn("RED ZONE VIOLATION", res.stderr)
        finally:
            Path(boundaries_file).unlink(missing_ok=True)

    def test_cli_audit_tree_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            boundaries_file = tmppath / "boundaries.md"
            boundaries_file.write_text(SAMPLE_BOUNDARIES_MD, encoding="utf-8")

            (tmppath / "docs").mkdir()
            (tmppath / "docs" / "doc.md").write_text("# Doc", encoding="utf-8")

            # Clean audit -> exit 0
            cmd = [
                sys.executable,
                str(self.script_path),
                "--boundaries",
                str(boundaries_file),
                "--audit-tree",
                "--repo-root",
                str(tmppath),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            self.assertIn("100%", res.stdout)

            # Unmapped file -> exit 1
            (tmppath / "unmapped.xyz").write_text("mystery", encoding="utf-8")
            res2 = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res2.returncode, 1)
            self.assertIn("UNMAPPED", res2.stderr + res2.stdout)

    def test_install_hook_creates_pre_commit_script(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / ".git").mkdir()

            # Direct function call test
            ok, msg = check_boundaries.install_git_hook(tmppath)
            self.assertTrue(ok)
            hook_file = tmppath / ".git" / "hooks" / "pre-commit"
            self.assertTrue(hook_file.is_file())
            content = hook_file.read_text(encoding="utf-8")
            self.assertIn("check_boundaries.py --staged", content)

            # CLI execution test
            cmd = [
                sys.executable,
                str(self.script_path),
                "--install-hook",
                "--repo-root",
                str(tmppath),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            self.assertIn("installed successfully", res.stdout.lower())

    def test_install_hook_chains_with_existing_pre_commit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            hooks_dir = tmppath / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            existing_hook = hooks_dir / "pre-commit"
            original_content = "#!/bin/sh\npytest tests/\n"
            existing_hook.write_text(original_content, encoding="utf-8")

            # First run: should chain without erasing existing content
            ok, msg = check_boundaries.install_git_hook(tmppath)
            self.assertTrue(ok)
            content = existing_hook.read_text(encoding="utf-8")
            self.assertIn("pytest tests/", content)
            self.assertIn("check_boundaries.py --staged", content)

            # Second run: idempotent, should not duplicate
            ok2, msg2 = check_boundaries.install_git_hook(tmppath)
            self.assertTrue(ok2)
            content_after = existing_hook.read_text(encoding="utf-8")
            self.assertEqual(content, content_after)
            self.assertEqual(content_after.count("# Meta-Project Boundary Gate Pre-Commit Hook"), 1)

    def test_cli_diff_against_head_exits_clean(self):
        ret = main(["--boundaries", ".agents/project_knowledge/boundaries.md", "--diff", "HEAD"])
        self.assertIn(ret, (0, 1))


class TestArchitectureDrift(unittest.TestCase):
    """Tests for check_architecture_drift function."""

    def test_drift_detected_when_code_modified_without_architecture(self):
        files = ["src/api/routes.py", "src/services/billing.py"]
        has_drift, drift_files = check_boundaries.check_architecture_drift(files)
        self.assertTrue(has_drift)
        self.assertEqual(len(drift_files), 2)
        self.assertIn("src/api/routes.py", drift_files)

    def test_drift_suppressed_when_architecture_included(self):
        files = ["src/api/routes.py", ".agents/project_knowledge/architecture.md"]
        has_drift, drift_files = check_boundaries.check_architecture_drift(files)
        self.assertFalse(has_drift)
        self.assertEqual(len(drift_files), 0)

    def test_drift_suppressed_for_non_code_files(self):
        files = ["docs/readme.md", "tests/test_unit.py", ".agents/project_knowledge/tasks.md"]
        has_drift, drift_files = check_boundaries.check_architecture_drift(files)
        self.assertFalse(has_drift)
        self.assertEqual(len(drift_files), 0)

    def test_drift_detected_for_skills_framework_code(self):
        files = ["skills/my-new-skill/SKILL.md"]
        has_drift, drift_files = check_boundaries.check_architecture_drift(files)
        self.assertTrue(has_drift)
        self.assertIn("skills/my-new-skill/SKILL.md", drift_files)


if __name__ == "__main__":
    unittest.main()
