#!/usr/bin/env python3
"""Canonical domain test suite for check_boundaries (scripts/check_boundaries.py).

Consolidated in Wave T (Lane T2) from:
- tests/test_check_boundaries.py
- tests/test_red_zone_sanction.py
- tests/test_dwave_b.py
- tests/test_iwave_g.py

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import check_boundaries
from check_boundaries import (
    DISPATCHER_TEMPLATE,
    SANCTION_AUTHORIZED_ACTORS,
    check_architecture_drift,
    install_git_hook,
    main,
)
gate_main = main
from scripts import inspect_meta_project

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

SANCTION_SAMPLE_BOUNDARIES_MD = """# Responsibility Zones and Change Boundaries

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
- Root project passport `AGENTS.md` (except the root AGENTS.md of this framework repository).
- Database files (`*.db`, `*.sqlite`).
- `secrets/**` — credentials and keys.
- `.github/workflows/ci.yml`.
"""

BASE_SHA = "a" * 40
AUTHORIZED_ACTOR = "vlv-code"
UNAUTHORIZED_ACTOR = "drive-by-contributor"


def _sanction(paths, base_sha=BASE_SHA, actor=AUTHORIZED_ACTOR, kind="red_zone_sanction"):
    return {
        "schema_version": "1.0.0",
        "kind": kind,
        "base_sha": base_sha,
        "authorized_by": actor,
        "paths": paths,
        "reason": "test",
    }


CHECK_BOUNDARIES_SCRIPT = SCRIPTS_DIR / "check_boundaries.py"
INIT_SKILL = REPO_ROOT / "skills" / "init-meta-project" / "SKILL.md"


def _find_posix_shell() -> str | None:
    candidates: list[str] = []
    for name in ("bash", "sh"):
        p = shutil.which(name)
        if p:
            candidates.append(p)
    git_path = shutil.which("git")
    if git_path:
        git_dir = Path(git_path).resolve().parent
        for rel in (
            Path("../bin/bash.exe"),
            Path("../bin/sh.exe"),
            Path("../usr/bin/bash.exe"),
            Path("../usr/bin/sh.exe"),
        ):
            cand = (git_dir / rel).resolve()
            if cand.is_file():
                candidates.append(str(cand))
    for cand in candidates:
        try:
            res = subprocess.run(
                [cand, "-c", "exit 0"], capture_output=True, timeout=5
            )
            if res.returncode == 0:
                return cand
        except Exception:
            continue
    return None


POSIX_SHELL = _find_posix_shell()
ENV_VAR = "META_PROJECT_ALLOW_RED_ZONE"

MINIMAL_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- `docs/**` and `*.md` documentation.

## Yellow Zone (Modification with Mandatory Verification)
- `AGENTS.md` root passport.

## Red Zone (Prohibited Without Direct User Confirmation)
- `*boundaries.md` policy files.
- `LICENSE` root license.

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any path not explicitly listed in Green, Yellow, or Red zones above is strictly classified as Red Zone by Default.
"""

PYCACHE_GREEN_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- `docs/**`
- `tests/**`
- `**/__pycache__/**`
- `**/*.pyc`

## Yellow Zone (Modification with Mandatory Verification)
- `scripts/**`

## Red Zone (Prohibited Without Direct User Confirmation)
- `*boundaries.md`
- `LICENSE`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any path not explicitly listed in Green, Yellow, or Red zones above is strictly classified as Red Zone by Default.
"""


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )


def _init_repo(path: Path, boundaries: str = MINIMAL_BOUNDARIES) -> Path:
    """Create a tiny committed git repository with a boundaries fixture."""
    path.mkdir(parents=True, exist_ok=True)
    res = _git(path, "init", "-q")
    assert res.returncode == 0, res.stderr
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    pk = path / ".agents" / "project_knowledge"
    pk.mkdir(parents=True, exist_ok=True)
    (pk / "boundaries.md").write_text(boundaries, encoding="utf-8")
    (path / "README.md").write_text("# fixture\n", encoding="utf-8")
    _git(path, "add", "-A")
    res = _git(path, "commit", "-qm", "init")
    assert res.returncode == 0, res.stderr
    return path


def _run_gate(
    cwd: Path, *args: str, env_overrides: dict | None = None
) -> subprocess.CompletedProcess:
    """Run the real gate CLI against cwd with an optional env overlay."""
    env = dict(os.environ)
    env.pop(ENV_VAR, None)  # baseline: env var absent unless overridden
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(CHECK_BOUNDARIES_SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
    )


LIVE_BOUNDARIES = REPO_ROOT / ".agents" / "project_knowledge" / "boundaries.md"
INSPECT_SCRIPT = REPO_ROOT / "scripts" / "inspect_meta_project.py"


# ---------------------------------------------------------------------------
# TestBoundaryGateParser (from tests/test_check_boundaries.py)
# ---------------------------------------------------------------------------
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

    def test_russian_zone_headers_parsing(self):
        """Verify that Russian zone headers (Зеленая зона, Желтая зона, Красная зона) are parsed correctly."""
        content = """# Зоны ответственности
## Зеленая зона (Автономные изменения)
- `docs/**`, `*.md`
- `src/utils/**`

## Желтая зона (С обязательной верификацией)
- `skills/**`
- `templates/**`

## Красная зона (Запрещено без подтверждения)
- `scripts/check_boundaries.py`
- `*boundaries.md`
- `tests/test_integrity.py`
"""
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("docs/**", zones["green"])
        self.assertIn("src/utils/**", zones["green"])
        self.assertIn("skills/**", zones["yellow"])
        self.assertIn("templates/**", zones["yellow"])
        self.assertIn("scripts/check_boundaries.py", zones["red"])
        self.assertIn("*boundaries.md", zones["red"])

    def test_zero_depth_double_star_matching(self):
        regex = check_boundaries.glob_to_regex("src/**/test.py")
        self.assertTrue(bool(regex.match("src/test.py")))
        self.assertTrue(bool(regex.match("src/sub/test.py")))
        self.assertTrue(bool(regex.match("src/sub/nested/test.py")))
        self.assertFalse(bool(regex.match("src/other.py")))


# ---------------------------------------------------------------------------
# TestBoundaryGateClassification (from tests/test_check_boundaries.py)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# TestBoundaryGateEvaluation (from tests/test_check_boundaries.py)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# TestBoundaryGateCLI (from tests/test_check_boundaries.py)
# ---------------------------------------------------------------------------
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

            # First run: dispatcher installed; existing hook preserved
            # byte-for-byte as a legacy companion executed as a separate
            # process (audit §8: no append-chaining).
            ok, msg = check_boundaries.install_git_hook(tmppath)
            self.assertTrue(ok, msg)
            legacy_hook = hooks_dir / "pre-commit.legacy-meta"
            self.assertTrue(legacy_hook.is_file())
            self.assertEqual(
                legacy_hook.read_text(encoding="utf-8"),
                original_content,
                "legacy hook content must be preserved byte-for-byte",
            )
            dispatcher_content = existing_hook.read_text(encoding="utf-8")
            self.assertIn("# Meta-Project Boundary Gate Pre-Commit Hook", dispatcher_content)
            self.assertIn("pre-commit.legacy-meta", dispatcher_content)
            self.assertIn("check_boundaries.py --staged", dispatcher_content)

            # Second run: idempotent, should not duplicate
            ok2, msg2 = check_boundaries.install_git_hook(tmppath)
            self.assertTrue(ok2)
            content_after = existing_hook.read_text(encoding="utf-8")
            self.assertEqual(dispatcher_content, content_after)
            self.assertEqual(content_after.count("# Meta-Project Boundary Gate Pre-Commit Hook"), 1)

    def test_cli_diff_against_head_exits_clean(self):
        b_path = Path(".agents/project_knowledge/boundaries.md")
        if not b_path.is_file():
            self.skipTest("live .agents/project_knowledge/boundaries.md absent (main branch)")
        ret = main(["--boundaries", str(b_path), "--diff", "HEAD"])
        self.assertIn(ret, (0, 1))


# ---------------------------------------------------------------------------
# TestArchitectureDrift (from tests/test_check_boundaries.py)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# TestSanctionFlagPairing (from tests/test_check_boundaries.py)
# ---------------------------------------------------------------------------
class TestSanctionFlagPairing(unittest.TestCase):
    """Wave P acceptance D7: --sanction-base-sha / --sanction-file /
    --sanction-actor are a mutual trio. Supplying a subset crashed with a
    raw TypeError (open(NoneType)); the CLI must fail with a clean usage
    error instead (fail-closed preserved, crash-form removed)."""

    def _run(self, *flags):
        import subprocess

        return subprocess.run(
            [sys.executable, "-B", str(REPO_ROOT / "scripts" / "check_boundaries.py"), *flags],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

    def test_base_sha_without_file_is_clean_usage_error(self):
        proc = self._run("--diff", "HEAD", "--sanction-base-sha", "abc")
        self.assertEqual(proc.returncode, 2, "argparse usage error must exit rc=2")
        self.assertIn("usage:", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertNotIn("TypeError", proc.stderr)

    def test_file_without_base_sha_is_clean_usage_error(self):
        proc = self._run("--diff", "HEAD", "--sanction-file", "x.json")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_actor_alone_is_clean_usage_error(self):
        proc = self._run("--diff", "HEAD", "--sanction-actor", "someone")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_full_trio_still_parses(self):
        proc = self._run("--diff", "HEAD", "--sanction-file", "x.json",
                         "--sanction-base-sha", "abc", "--sanction-actor", "op")
        self.assertNotIn("Traceback", proc.stderr)


# ---------------------------------------------------------------------------
# TestRedZoneSanctionContract (from tests/test_red_zone_sanction.py)
# ---------------------------------------------------------------------------
class TestRedZoneSanctionContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.boundaries = self.root / "boundaries.md"
        self.boundaries.write_text(SANCTION_SAMPLE_BOUNDARIES_MD, encoding="utf-8")
        self.sanction_file = self.root / "red-zone-sanction.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, files, sanction=None, base_sha=BASE_SHA, actor=AUTHORIZED_ACTOR):
        if sanction is not None:
            self.sanction_file.write_text(
                json.dumps(sanction, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        argv = [
            "--boundaries", str(self.boundaries),
            "--files", *files,
            "--sanction-file", str(self.sanction_file),
            "--sanction-base-sha", base_sha,
            "--sanction-actor", actor,
        ]
        return main(argv)

    def _run_no_sanction(self, files):
        return main(
            ["--boundaries", str(self.boundaries), "--files", *files]
        )

    # -- requirement: green path needs no sanction ------------------------

    def test_green_zone_change_still_needs_no_sanction(self):
        self.assertEqual(0, self._run_no_sanction(["docs/readme.md"]))
        self.assertEqual(0, self._run(["docs/readme.md"], _sanction(["docs/readme.md"])))

    # -- historical fail-closed behavior preserved ------------------------

    def test_red_zone_without_sanction_flags_refused(self):
        self.assertEqual(1, self._run_no_sanction([".github/workflows/ci.yml"]))

    # -- happy path: all three requirements satisfied ----------------------

    def test_valid_sanction_admits_red_zone_change(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"]),
        )
        self.assertEqual(0, rc)

    def test_sanction_is_path_explicit_no_wildcards(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/**"]),
        )
        self.assertNotEqual(0, rc)

    # -- requirement 1: WHO ------------------------------------------------

    def test_unauthorized_actor_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], actor=UNAUTHORIZED_ACTOR),
            actor=UNAUTHORIZED_ACTOR,
        )
        self.assertNotEqual(0, rc)

    def test_authorized_set_contains_single_owner(self):
        self.assertIn(AUTHORIZED_ACTOR, SANCTION_AUTHORIZED_ACTORS)
        self.assertNotIn(UNAUTHORIZED_ACTOR, SANCTION_AUTHORIZED_ACTORS)

    def test_actor_mismatch_with_sanction_author_refused(self):
        # Sanction issued by the maintainer, but the push actor differs.
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], actor=AUTHORIZED_ACTOR),
            actor=UNAUTHORIZED_ACTOR,
        )
        self.assertNotEqual(0, rc)

    # -- requirement 2: WHICH REVISION -------------------------------------

    def test_stale_base_sha_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], base_sha="b" * 40),
        )
        self.assertNotEqual(0, rc)

    # -- requirement 3: INVALIDATION / coverage ------------------------------

    def test_uncovered_red_path_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction(["secrets/key.pem"]),
        )
        self.assertNotEqual(0, rc)

    def test_partial_coverage_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml", "secrets/key.pem"],
            _sanction([".github/workflows/ci.yml"]),
        )
        self.assertNotEqual(0, rc)

    # -- tamper resistance ---------------------------------------------------

    def test_malformed_json_refused(self):
        self.sanction_file.write_text("{ not json", encoding="utf-8")
        rc = self._run([".github/workflows/ci.yml"], sanction=None)
        self.assertNotEqual(0, rc)

    def test_wrong_kind_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], kind="post_factum_approval"),
        )
        self.assertNotEqual(0, rc)

    def test_missing_sanction_file_refused(self):
        (self.sanction_file).unlink(missing_ok=True)
        rc = self._run([".github/workflows/ci.yml"], sanction=None)
        self.assertNotEqual(0, rc)


# ---------------------------------------------------------------------------
# TempRootTestCase (from tests/test_dwave_b.py)
# ---------------------------------------------------------------------------
class TempRootTestCase(unittest.TestCase):
    """Base fixture with automatic temp directory cleanup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_b_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def sub(self, name: str) -> Path:
        p = self.root / name
        p.mkdir(parents=True, exist_ok=True)
        return p


# ---------------------------------------------------------------------------
# TestStagedEnvOverrideContract (from tests/test_dwave_b.py)
# ---------------------------------------------------------------------------
class TestStagedEnvOverrideContract(TempRootTestCase):
    """Gate contract: staged mode honors the env var, fail-closed default."""

    def setUp(self):
        super().setUp()
        self.repo = _init_repo(self.sub("repo"))

    def _gate(self, *args: str, env_overrides: dict | None = None):
        return _run_gate(self.repo, *args, env_overrides=env_overrides)

    # RED: pre-fix the env var is ignored -> staged Red Zone file refused.
    def test_env_one_allows_staged_red_zone_with_allowed_notice(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._gate("--staged", env_overrides={ENV_VAR: "1"})

        self.assertEqual(
            res.returncode,
            0,
            f"env override must admit staged Red Zone file "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        self.assertIn(
            "[ALLOWED]",
            res.stdout,
            f"admitted Red Zone file must carry an [ALLOWED] notice "
            f"(stdout={res.stdout!r})",
        )

    # RED: pre-fix no notice exists at all.
    def test_allowed_notice_names_each_red_file(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")
        boundaries = (
            self.repo / ".agents" / "project_knowledge" / "boundaries.md"
        )
        boundaries.write_text(
            MINIMAL_BOUNDARIES + "\n- appended line\n", encoding="utf-8"
        )
        _git(self.repo, "add", ".agents/project_knowledge/boundaries.md")

        res = self._gate("--staged", env_overrides={ENV_VAR: "1"})

        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn(
            "[ALLOWED] LICENSE",
            res.stdout,
            f"[ALLOWED] notice must name LICENSE (stdout={res.stdout!r})",
        )
        self.assertIn(
            "[ALLOWED] .agents/project_knowledge/boundaries.md",
            res.stdout,
            f"[ALLOWED] notice must name each red file "
            f"(stdout={res.stdout!r})",
        )

    # Lock-in: refusal without the env var is identical to current behavior.
    def test_default_refusal_identical_without_env(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._gate("--staged")

        self.assertNotEqual(
            res.returncode,
            0,
            f"Red Zone staged file must be refused without the env var "
            f"(stdout={res.stdout!r})",
        )
        self.assertIn("RED ZONE VIOLATION", res.stderr)
        self.assertIn("LICENSE", res.stderr)
        self.assertNotIn("[ALLOWED]", res.stdout)

    # Lock-in: only the explicit affirmative value "1" enables the override
    # (fail-closed contract; anything else must keep the refusal).
    def test_non_one_values_fail_closed(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        for value in ("0", "true", "yes", "on", ""):
            res = self._gate("--staged", env_overrides={ENV_VAR: value})
            self.assertNotEqual(
                res.returncode,
                0,
                f"{ENV_VAR}={value!r} must NOT admit a Red Zone staged file "
                f"(stdout={res.stdout!r})",
            )

    # Adversarial boundary case: the override is scoped to RED-zone files;
    # Default Deny (unmapped) paths must stay refused even under the env var.
    def test_unmapped_default_deny_stays_refused_under_override(self):
        (self.repo / "external_tool.cfg").write_text("k=v\n", encoding="utf-8")
        _git(self.repo, "add", "external_tool.cfg")

        res = self._gate("--staged", env_overrides={ENV_VAR: "1"})

        self.assertNotEqual(
            res.returncode,
            0,
            f"env override must not admit unmapped Default Deny files "
            f"(stdout={res.stdout!r})",
        )
        self.assertIn("DEFAULT DENY", res.stderr)

    # Scope lock-in: the env var is read in STAGED mode only; the default
    # working-tree mode keeps refusing regardless of the env var.
    def test_env_ignored_outside_staged_mode(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._gate(env_overrides={ENV_VAR: "1"})  # no --staged flag

        self.assertNotEqual(
            res.returncode,
            0,
            f"env override must stay scoped to --staged mode "
            f"(stdout={res.stdout!r})",
        )

    # In-process fast-path: same contract through main() (library entry).
    def test_main_honors_env_one_in_staged_mode(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {ENV_VAR: "1"}):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = gate_main(["--staged", "--repo-root", str(self.repo)])

        self.assertEqual(
            rc, 0, f"main() must honor the env override (err={err.getvalue()!r})"
        )
        self.assertIn("[ALLOWED] LICENSE", out.getvalue())

    def test_main_refuses_without_env_in_staged_mode(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        out, err = io.StringIO(), io.StringIO()
        env = dict(os.environ)
        env.pop(ENV_VAR, None)
        with mock.patch.dict(os.environ, env, clear=True):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = gate_main(["--staged", "--repo-root", str(self.repo)])

        self.assertNotEqual(rc, 0, "refusal must be preserved without env var")
        self.assertNotIn("[ALLOWED]", out.getvalue())


# ---------------------------------------------------------------------------
# TestHookDispatcherEnvPassthrough (from tests/test_dwave_b.py)
# ---------------------------------------------------------------------------
class TestHookDispatcherEnvPassthrough(TempRootTestCase):
    """The installed pre-commit dispatcher must pass the env through."""

    def setUp(self):
        super().setUp()
        self.repo = _init_repo(self.sub("repo"))

    def test_installed_dispatcher_passes_env_through(self):
        # RED: dispatcher template does not mention the env var pre-fix.
        ok, msg = install_git_hook(self.repo)
        assert ok, msg
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        content = hook.read_text(encoding="utf-8")
        self.assertIn(
            ENV_VAR,
            content,
            "installed dispatcher must explicitly pass "
            "META_PROJECT_ALLOW_RED_ZONE through to the gate",
        )
        self.assertIn(
            ENV_VAR,
            DISPATCHER_TEMPLATE,
            "DISPATCHER_TEMPLATE must carry the env pass-through",
        )


# ---------------------------------------------------------------------------
# TestHookEndToEndEnvOverride (from tests/test_dwave_b.py)
# ---------------------------------------------------------------------------
class TestHookEndToEndEnvOverride(TempRootTestCase):
    """Full dispatcher path: hook script -> gate, with and without env."""

    def setUp(self):
        super().setUp()
        self.repo = _init_repo(self.sub("repo"))
        # Deploy a working gate script so installed hooks are executable.
        # Wave F FC (ADR #22): the gate imports its shared-helper requires
        # companion — the subset deployment ships scripts/_common.py too.
        scripts_dir = self.repo / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        shutil.copyfile(CHECK_BOUNDARIES_SCRIPT, scripts_dir / "check_boundaries.py")
        shutil.copyfile(
            REPO_ROOT / "scripts" / "_common.py", scripts_dir / "_common.py"
        )
        ok, msg = install_git_hook(self.repo)
        assert ok, msg

    def _run_hook(self, env_overrides: dict | None = None):
        env = dict(os.environ)
        env.pop(ENV_VAR, None)
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            [POSIX_SHELL, str(self.repo / ".git" / "hooks" / "pre-commit")],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
            env=env,
        )

    @unittest.skipIf(POSIX_SHELL is None, "no POSIX shell available")
    def test_hook_with_env_one_passes_staged_red_zone(self):
        # RED: pre-fix the hook refuses despite the env var.
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._run_hook(env_overrides={ENV_VAR: "1"})

        self.assertEqual(
            res.returncode,
            0,
            f"hook must admit the staged Red Zone file under "
            f"{ENV_VAR}=1 (stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        self.assertIn(
            "[ALLOWED] LICENSE",
            res.stdout,
            f"hook output must carry the [ALLOWED] notice naming the file "
            f"(stdout={res.stdout!r})",
        )

    @unittest.skipIf(POSIX_SHELL is None, "no POSIX shell available")
    def test_hook_without_env_preserves_refusal(self):
        # Lock-in: without the env var the hook still blocks Red Zone files.
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._run_hook()

        self.assertNotEqual(
            res.returncode,
            0,
            f"hook must refuse the staged Red Zone file by default "
            f"(stdout={res.stdout!r})",
        )


# ---------------------------------------------------------------------------
# TestDriftDetectorExcludesBytecode (from tests/test_dwave_b.py)
# ---------------------------------------------------------------------------
class TestDriftDetectorExcludesBytecode(TempRootTestCase):
    """Architecture-drift classifier must treat bytecode caches as noise."""

    # RED: pre-fix scripts/__pycache__/*.pyc is framework code (scripts/
    # prefix) and triggers the drift warning.
    def test_pycache_pyc_not_flagged_as_functional_code(self):
        has_drift, drift_files = check_architecture_drift(
            [
                "scripts/__pycache__/mod.cpython-312.pyc",
                "skills/pkg/__pycache__/util.pyc",
            ]
        )
        self.assertFalse(
            has_drift,
            f"bytecode caches must not trigger architecture drift: {drift_files!r}",
        )
        self.assertEqual(drift_files, [])

    # RED: the whole __pycache__ directory is noise, whatever it contains.
    def test_pycache_dir_contents_not_flagged(self):
        has_drift, drift_files = check_architecture_drift(
            ["scripts/__pycache__/notes.txt"]
        )
        self.assertFalse(
            has_drift,
            f"__pycache__ directory contents must be skipped: {drift_files!r}",
        )

    # RED: *.pyc bytecode is skipped even outside a __pycache__ directory.
    def test_pyc_outside_pycache_not_flagged(self):
        has_drift, drift_files = check_architecture_drift(
            ["scripts/build/output.pyc"]
        )
        self.assertFalse(
            has_drift,
            f"*.pyc bytecode must be skipped: {drift_files!r}",
        )

    # Lock-in: real functional code still flags the drift.
    def test_functional_code_still_flagged(self):
        has_drift, drift_files = check_architecture_drift(
            ["scripts/new_util.py", "skills/new-skill/SKILL.md"]
        )
        self.assertTrue(has_drift, "functional code changes must still flag drift")
        self.assertIn("scripts/new_util.py", drift_files)

    # Lock-in: an architecture.md update still suppresses the warning.
    def test_arch_update_still_suppresses(self):
        has_drift, _ = check_architecture_drift(
            ["scripts/new_util.py", ".agents/project_knowledge/architecture.md"]
        )
        self.assertFalse(has_drift, "architecture update must suppress drift")

    # RED (CLI): staged __pycache__/*.pyc produces no drift warning on the
    # real gate output.
    def test_cli_staged_pycache_no_drift_warning(self):
        repo = _init_repo(self.sub("repo"), boundaries=PYCACHE_GREEN_BOUNDARIES)
        pyc_dir = repo / "scripts" / "__pycache__"
        pyc_dir.mkdir(parents=True, exist_ok=True)
        (pyc_dir / "mod.cpython-312.pyc").write_bytes(b"\x00fake bytecode")
        _git(repo, "add", "scripts/__pycache__/mod.cpython-312.pyc")

        res = _run_gate(repo, "--staged")

        self.assertNotIn(
            "ARCHITECTURE DRIFT",
            res.stdout + res.stderr,
            f"staged __pycache__/*.pyc must not produce a drift warning "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        self.assertEqual(
            res.returncode,
            0,
            f"green-mapped bytecode cache must pass the gate "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )


# ---------------------------------------------------------------------------
# TestInitSkillGitignoreScaffold (from tests/test_dwave_b.py)
# ---------------------------------------------------------------------------
class TestInitSkillGitignoreScaffold(unittest.TestCase):
    """Canon lock-in: init skill scaffold steps document the .gitignore."""

    def _scaffold_region(self) -> str:
        text = INIT_SKILL.read_text(encoding="utf-8")
        start_marker = "5. **Create initial knowledge slice drafts and registry:**"
        end_marker = "##### Pass 2:"
        start = text.find(start_marker)
        self.assertGreaterEqual(
            start, 0, "init skill Pass 1 step 5 (scaffold writes) not found"
        )
        end = text.find(end_marker, start)
        self.assertGreater(end, start, "Pass 2 header not found after step 5")
        return text[start:end]

    def test_scaffold_steps_lock_in_gitignore_block(self):
        # RED: pre-fix none of the append-if-absent semantics are documented.
        region = self._scaffold_region().lower()
        for needle in (
            ".gitignore",
            "append-if-absent",
            "never overwrite",
            "__pycache__/",
            "*.pyc",
            "*.lock",
            "green",
            "hygiene",
        ):
            self.assertIn(
                needle,
                region,
                f"init skill scaffold steps must document the baseline "
                f".gitignore semantics: missing {needle!r}",
            )


# ---------------------------------------------------------------------------
# TestWaveIParserHonesty (from tests/test_iwave_g.py)
# ---------------------------------------------------------------------------
class TestWaveIParserHonesty(unittest.TestCase):
    """parse_boundaries: verb-anchored command detection + comma splitting."""

    def setUp(self):
        if not LIVE_BOUNDARIES.is_file():
            self.skipTest("live .agents/project_knowledge/boundaries.md absent (main branch)")

    def test_expect_substring_path_is_not_dropped(self):
        """RED probe (a): a path whose name contains 'expect' must be mapped,
        never silently dropped by a substring blacklist (audit §6.4)."""
        content = (
            "# Zones\n"
            "## Green Zone\n"
            "- `docs/expected_behavior.md` — expected behavior specification.\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn(
            "docs/expected_behavior.md",
            zones["green"],
            "path pattern containing 'expect' was silently dropped by the "
            "substring blacklist (Wave I audit §6.4)",
        )

    def test_assert_substring_path_is_not_dropped(self):
        """The 'assert' substring blacklist must not drop paths either."""
        content = (
            "# Zones\n"
            "## Green Zone\n"
            "- `docs/assert_reference.md` — assertion helper docs.\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("docs/assert_reference.md", zones["green"])

    def test_backticked_comma_multi_pattern_splits(self):
        """RED probe (b): `` `docs/**, *.md` `` is TWO patterns, not one."""
        content = (
            "# Zones\n"
            "## Green Zone\n"
            "- `docs/**, *.md` — documentation.\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("docs/**", zones["green"])
        self.assertIn("*.md", zones["green"])
        self.assertNotIn(
            "docs/**, *.md",
            zones["green"],
            "comma-multi-pattern parsed as a single never-matching glob",
        )

    def test_comma_split_trims_whitespace(self):
        """Each comma-separated piece is whitespace-trimmed."""
        content = (
            "# Zones\n"
            "## Yellow Zone\n"
            "- `skills/** , templates/**` — framework components.\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("skills/**", zones["yellow"])
        self.assertIn("templates/**", zones["yellow"])
        self.assertNotIn("skills/** , templates/**", zones["yellow"])

    def test_comma_split_respects_except_clause(self):
        """The (except ...) strip still applies before comma splitting."""
        content = (
            "# Zones\n"
            "## Green Zone\n"
            "- `docs/**, *.md` (except the root `AGENTS.md`) — documentation.\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("docs/**", zones["green"])
        self.assertIn("*.md", zones["green"])
        self.assertNotIn("AGENTS.md", zones["green"])

    def test_command_bullet_lines_are_skipped(self):
        """Bullets whose body starts with a CLI verb are command lines: no
        pattern is extracted from them (guard: rule must not over-capture)."""
        content = (
            "# Zones\n"
            "## Yellow Zone\n"
            "- `python scripts/check_boundaries.py --staged` — run the gate.\n"
            "- `pytest tests/ -v` — run the suite.\n"
            "- `git push --force` — prohibited.\n"
            "- `pip install nothing` — never.\n"
            "- python scripts/tool.py --flag (unquoted invocation)\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertEqual(
            zones["yellow"],
            [],
            "command documentation bullets must not yield path patterns",
        )

    def test_path_bullet_with_inline_path_still_maps(self):
        """A path bullet whose body does NOT start with a CLI verb keeps
        mapping its backticked paths (guard: rule must not over-drop)."""
        content = (
            "# Zones\n"
            "## Green Zone\n"
            "- Enforcement runs via `python scripts/gate.py` on `scripts/gate.py`.\n"
        )
        zones = check_boundaries.parse_boundaries(content)
        self.assertIn("scripts/gate.py", zones["green"])

    def test_live_boundaries_representative_patterns(self):
        """Regression bar (plan §1): representative patterns of the live
        framework boundaries.md keep their exact zones under the new parser."""
        zones = check_boundaries.parse_boundaries(
            LIVE_BOUNDARIES.read_text(encoding="utf-8")
        )
        for pattern in (
            "tests/test_*.py",
            "tests/test_unit_*.py",
            "docs/**",
            "*.md",
            ".agents/team/*/notes.md",
            ".gitattributes",
        ):
            self.assertIn(pattern, zones["green"], f"live Green pattern lost: {pattern}")
        for pattern in (
            "AGENTS.md",
            "tests/**",
            "skills/**",
            "templates/**",
            "project_knowledge/**",
            "team/**",
            "scripts/**",
            ".agents/skills/**",
            ".agents/project_knowledge/**",
            ".agents/team/**",
            ".agents/*.json",
            ".agents/reports/**",
            ".github/*.yml",
            ".github/*.yaml",
            "FUNDING.yml",
            ".claude-plugin/**",
            "plugin.json",
        ):
            self.assertIn(pattern, zones["yellow"], f"live Yellow pattern lost: {pattern}")
        for pattern in (
            "scripts/check_boundaries.py",
            "*boundaries.md",
            "tests/test_integrity.py",
            ".github/workflows/**",
            "ci.yml",
            ".github/CODEOWNERS",
            "LICENSE",
            ".gitignore",
            ".github/red-zone-sanction.json",
        ):
            self.assertIn(pattern, zones["red"], f"live Red pattern lost: {pattern}")
        self.assertNotIn("docs/**, *.md", zones["green"])

    def test_live_boundaries_sentinel_classification(self):
        """Sentinel paths classify identically under the new parser (the
        full path->zone map proof lives in the dispatcher captures)."""
        zones = check_boundaries.parse_boundaries(
            LIVE_BOUNDARIES.read_text(encoding="utf-8")
        )
        expectations = {
            "scripts/check_boundaries.py": "red",
            "scripts/some_new_tool.py": "yellow",
            "docs/expected_behavior.md": "green",
            "README.md": "green",
            "CHANGELOG.md": "green",
            "AGENTS.md": "yellow",
            "tests/test_check_boundaries.py": "green",
            "tests/test_integrity.py": "red",
            "templates/AGENTS.md": "yellow",
            "templates/project_knowledge/boundaries.md": "red",
            ".agents/project_knowledge/boundaries.md": "red",
            ".agents/team/agent-dev-lead/profile.md": "yellow",
            ".github/workflows/ci.yml": "red",
            ".github/CODEOWNERS": "red",
            "LICENSE": "red",
            ".gitignore": "red",
            ".gitattributes": "green",
            "unknown_dir/file.bin": "black",
            "FUNDING.yml": "yellow",
        }
        for path, expected_zone in expectations.items():
            zone, _ = check_boundaries.classify_path(path, zones)
            self.assertEqual(
                zone,
                expected_zone,
                f"sentinel classification drifted for {path}: "
                f"{expected_zone} -> {zone}",
            )


# ---------------------------------------------------------------------------
# TestWaveIReadOnlyAssertion (from tests/test_iwave_g.py)
# ---------------------------------------------------------------------------
class TestWaveIReadOnlyAssertion(unittest.TestCase):
    """enforce_read_only(): audit-hook-backed write refusal scoped to the
    inspection window; CLI emits the READ_ONLY_VIOLATION envelope."""

    def setUp(self):
        for attr in ("enforce_read_only", "ReadOnlyViolation"):
            if not hasattr(inspect_meta_project, attr):
                self.fail(
                    f"scripts.inspect_meta_project.{attr} missing — the "
                    "--read-only assertion (Wave I §6.1) is not implemented"
                )

    def test_write_inside_repo_fires_and_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "planted.txt"
            with inspect_meta_project.enforce_read_only(repo):
                with self.assertRaises(inspect_meta_project.ReadOnlyViolation):
                    target.write_text("must never land", encoding="utf-8")
            self.assertFalse(
                target.exists(),
                "the read-only assertion must block the write before it lands",
            )

    def test_append_and_delete_and_rename_inside_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            existing = repo / "existing.txt"
            existing.write_text("data", encoding="utf-8")
            with inspect_meta_project.enforce_read_only(repo):
                with self.assertRaises(inspect_meta_project.ReadOnlyViolation):
                    with open(existing, "a", encoding="utf-8") as fh:
                        fh.write("more")
                with self.assertRaises(inspect_meta_project.ReadOnlyViolation):
                    existing.unlink()
                with self.assertRaises(inspect_meta_project.ReadOnlyViolation):
                    existing.rename(repo / "moved.txt")
                with self.assertRaises(inspect_meta_project.ReadOnlyViolation):
                    existing.replace(repo / "replaced.txt")
            self.assertTrue(existing.exists(), "delete/rename must be blocked")
            self.assertEqual(existing.read_text(encoding="utf-8"), "data")

    def test_pure_reads_do_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            f = repo / "slice.md"
            f.write_text("content", encoding="utf-8")
            with inspect_meta_project.enforce_read_only(repo):
                self.assertEqual(f.read_text(encoding="utf-8"), "content")
                self.assertTrue(f.is_file())
                _ = sorted(p.name for p in repo.rglob("*"))

    def test_writes_outside_repo_do_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            repo = Path(tmp_a)
            outside = Path(tmp_b) / "outside.txt"
            with inspect_meta_project.enforce_read_only(repo):
                outside.write_text("allowed", encoding="utf-8")
            self.assertEqual(outside.read_text(encoding="utf-8"), "allowed")

    def test_assertion_is_scoped_to_the_window(self):
        """After the guarded block the hook is dormant: writes pass again."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "later.txt"
            with inspect_meta_project.enforce_read_only(repo):
                pass
            target.write_text("after window", encoding="utf-8")
            self.assertTrue(target.exists())

    def test_cli_read_only_pure_run_is_byte_identical(self):
        """CLI-level: --read-only on this repo -> rc=0 and byte-identical
        stdout/stderr versus the same run without the flag."""
        base_cmd = [sys.executable, "-B", str(INSPECT_SCRIPT), "--repo-root", str(REPO_ROOT)]
        without = subprocess.run(
            base_cmd + ["--json"], capture_output=True, check=False
        )
        with_flag = subprocess.run(
            base_cmd + ["--json", "--read-only"], capture_output=True, check=False
        )
        self.assertEqual(without.returncode, 0)
        self.assertEqual(with_flag.returncode, 0)
        self.assertEqual(without.stdout, with_flag.stdout, "stdout must be byte-identical")
        self.assertEqual(without.stderr, with_flag.stderr, "stderr must be byte-identical")

    def test_cli_violation_emits_envelope_without_traceback(self):
        """CLI-level mechanism probe: a write planted inside the guarded
        inspection call -> READ_ONLY_VIOLATION envelope, rc != 0, clean
        stderr (no traceback), nothing written to disk."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            planted = repo / "planted.txt"

            def _writer(*, repo_root, target_harness=None, target_installation=None):
                planted.write_text("violation", encoding="utf-8")
                return {"state": "NONE", "capabilities": {}}

            argv = [
                INSPECT_SCRIPT.name,
                "--repo-root", str(repo),
                "--read-only",
                "--json",
            ]
            captured_stderr = io.StringIO()
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(sys, "stderr", captured_stderr), \
                    mock.patch.object(
                        inspect_meta_project, "inspect_repository", _writer
                    ):
                rc = inspect_meta_project.main()
            self.assertNotEqual(rc, 0)
            self.assertFalse(planted.exists(), "planted write must be blocked")
            stderr = captured_stderr.getvalue()
            self.assertIn("[READ_ONLY_VIOLATION]", stderr)
            self.assertNotIn("Traceback", stderr)


# ---------------------------------------------------------------------------
# TestWaveIDeadCodeRemoved (from tests/test_iwave_g.py)
# ---------------------------------------------------------------------------
class TestWaveIDeadCodeRemoved(unittest.TestCase):
    """Scoped grep-locks: the removed symbols/local names must not reappear
    in the exact module they were removed from."""

    @staticmethod
    def _lines(path: Path):
        return path.read_text(encoding="utf-8").splitlines()

    def test_black_violations_removed_from_check_boundaries(self):
        for line in self._lines(REPO_ROOT / "scripts" / "check_boundaries.py"):
            self.assertNotIn("black_violations", line)

    def test_compacted_any_removed_from_compact_memory(self):
        for line in self._lines(REPO_ROOT / "scripts" / "compact_memory.py"):
            self.assertNotIn("compacted_any", line)

    def test_tasks_and_obs_file_locals_removed_from_inspector(self):
        for line in self._lines(REPO_ROOT / "scripts" / "inspect_meta_project.py"):
            self.assertNotIn("tasks_file", line)
            self.assertNotIn("obs_file", line)

    def test_unused_re_import_removed_from_inspector(self):
        for line in self._lines(REPO_ROOT / "scripts" / "inspect_meta_project.py"):
            self.assertNotEqual(line.strip(), "import re")

    def test_dead_journal_path_assignment_removed_from_updater(self):
        """Only the LEGITIMATE journal_path assignment (the lock reader at
        the end of the module) may remain — the dead twin inside the apply
        flow must be gone (scoped lock: exact-count, not repo-wide grep)."""
        occurrences = [
            line
            for line in self._lines(REPO_ROOT / "scripts" / "update_meta_project.py")
            if "journal_path = repo_root / UPDATE_JOURNAL_RELPATH" in line
        ]
        self.assertEqual(
            len(occurrences),
            1,
            "expected exactly the legitimate journal_path assignment; the "
            "dead one inside _apply_plan must be removed",
        )


if __name__ == "__main__":
    unittest.main()
