#!/usr/bin/env python3
"""
Wave I, Lane G — Gate honesty (parser + read-only assertion + dead code).

Plan: docs/superpowers/plans/2026-11-18-wave-i-audit-response.md (Lane IG §3).

Three lock groups:

1. T-G1 (§6.4, honest parser): ``parse_boundaries()`` treats a bullet line as
   a COMMAND LINE only when its body starts with a known CLI verb; every
   other bullet line is a path-candidate line. The historical substring
   blacklist ("assert", "expect", "python ", ...) silently DROPPED real path
   patterns (a Green-zone ``docs/expected_behavior.md`` bullet vanished
   because the candidate contains the substring "expect"), and a backticked
   comma-multi-pattern (``docs/**, *.md``) parsed as ONE never-matching glob
   instead of two separate patterns. Command lines are still skipped.
   Regression bar (plan §1): the live framework boundaries.md must classify
   every path IDENTICALLY before/after the change (verified by the dispatcher
   captures /tmp/iw_map_before.json vs /tmp/iw_map_after.json plus
   audit-tree 100%); this file additionally locks representative patterns and
   sentinel classifications of the live file.

2. T-G2 (§6.1): ``--read-only`` becomes a verifiable assertion — a stdlib
   audit hook (``sys.addaudithook``) raises on write/move/delete operations
   targeting the audited repository during the inspection call; the CLI
   emits the Wave-E envelope READ_ONLY_VIOLATION (rc != 0, clean, no
   traceback). Pure reads never fire; normal runs (no flag) are byte-
   identical to before.

3. T-G3 (§6.8): dead code removed — scoped grep-locks per module+symbol
   actually removed (other scripts may legitimately reuse the same names).

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import check_boundaries, inspect_meta_project

LIVE_BOUNDARIES = REPO_ROOT / ".agents" / "project_knowledge" / "boundaries.md"

INSPECT_SCRIPT = REPO_ROOT / "scripts" / "inspect_meta_project.py"


# ---------------------------------------------------------------------------
# T-G1 §6.4 — honest parser
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
            "tests/test_iwave_g.py": "green",
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
# T-G2 §6.1 — --read-only as a verifiable assertion
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
# T-G3 §6.8 — dead code grep-locks (scoped per module+symbol)
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
