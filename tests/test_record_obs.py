#!/usr/bin/env python3
"""Canonical domain test suite for record_obs (scripts/record_obs.py).

Consolidated in Wave T (Lane T2) from:
- tests/test_record_obs.py
- tests/test_dwave_r.py

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import datetime
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.record_obs import (
    CANONICAL_CATEGORIES,
    file_lock,
    main,
)

UNIFIED_CATEGORIES = {
    "build", "runtime", "deps", "db", "api", "test", "env", "ci",
    "boundaries", "orchestration", "decommission", "incident",
    "init", "testing", "git", "architecture",
}

LEGACY_ENGINE_TAGS = {
    "boundaries", "ci", "decommission", "incident", "orchestration",
    "runtime", "git", "init", "testing", "architecture",
}

SKILL_DOC = REPO_ROOT / "skills" / "record-observation" / "SKILL.md"


def _seed_obs(path: Path) -> None:
    path.write_text(
        "# Agent Observations Base\n\n"
        "| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# TestRecordObs (from tests/test_record_obs.py)
# ---------------------------------------------------------------------------
class TestRecordObs(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.obs_file = Path(self.temp_dir.name) / "observations.md"
        # Seed standard header
        self.obs_file.write_text(
            "# Agent Observations Base\n\n"
            "| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_observation_appends_row(self):
        """Verify that a valid observation appends a row with current ISO date and proper columns."""
        today_str = datetime.date.today().isoformat()
        ret = main([
            "--category", "runtime",
            "--path", "scripts/runner.py",
            "--issue", "Recursion limit exceeded on deep AST traversal",
            "--solution", "Increase sys.setrecursionlimit or convert to iterative stack",
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 0)

        content = self.obs_file.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        last_line = lines[-1]

        expected_prefix = f"| {today_str} | [runtime] | scripts/runner.py |"
        self.assertTrue(last_line.startswith(expected_prefix), f"Expected prefix '{expected_prefix}', got '{last_line}'")
        self.assertIn("Recursion limit exceeded", last_line)
        self.assertIn("Increase sys.setrecursionlimit", last_line)

    def test_invalid_category_fails_exit_1(self):
        """Adversarial check: verify that an unapproved category is rejected with exit code 1 and file unmodified."""
        initial_content = self.obs_file.read_text(encoding="utf-8")
        ret = main([
            "--category", "unauthorized_arbitrary_category",
            "--path", "scripts/test.py",
            "--issue", "Any issue",
            "--solution", "Any solution",
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 1)

        final_content = self.obs_file.read_text(encoding="utf-8")
        self.assertEqual(initial_content, final_content, "Observations file must not be modified on category validation failure")

    def test_pipe_escaping_in_issue_and_solution(self):
        r"""Verify that raw pipes '|' in issue and solution are properly escaped to '\|' without breaking table columns."""
        ret = main([
            "--category", "boundaries",
            "--path", "scripts/check_boundaries.py",
            "--issue", "Path contains | pipe separator | and another",
            "--solution", r"Use \| escaped pipe or regex | alternative",
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 0)

        content = self.obs_file.read_text(encoding="utf-8")
        last_line = content.splitlines()[-1]

        # Verify raw unescaped pipes do not exist inside issue/solution
        self.assertIn(r"Path contains \| pipe separator \| and another", last_line)
        self.assertIn(r"Use \| escaped pipe or regex \| alternative", last_line)

        # Splitting by unescaped pipe should result in exactly 5 table columns (plus 2 empty outer edges)
        unescaped_pipe_parts = re.split(r"(?<!\\)\|", last_line)
        self.assertEqual(len(unescaped_pipe_parts), 7)

    def test_path_pipe_escaping(self):
        r"""Verify that raw pipes '|' in path argument are properly escaped to '\|'."""
        ret = main([
            "--category", "boundaries",
            "--path", "src/module | helper.py",
            "--issue", "Issue text",
            "--solution", "Solution text",
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 0)

        content = self.obs_file.read_text(encoding="utf-8")
        last_line = content.splitlines()[-1]
        self.assertIn(r"src/module \| helper.py", last_line)
        unescaped_pipe_parts = re.split(r"(?<!\\)\|", last_line)
        self.assertEqual(len(unescaped_pipe_parts), 7)

    def test_invalid_date_format_fails_exit_1(self):
        """Adversarial check: verify that a malformed date string fails validation with exit code 1."""
        ret = main([
            "--category", "runtime",
            "--path", "src/app.py",
            "--issue", "Issue text",
            "--solution", "Solution text",
            "--date", "2026/11/14",  # Malformed date (slash instead of hyphen)
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 1)

        ret_junk = main([
            "--category", "runtime",
            "--path", "src/app.py",
            "--issue", "Issue text",
            "--solution", "Solution text",
            "--date", "not-a-date",
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret_junk, 1)

    def test_pinned_observation_flag(self):
        """Verify that --pin appends the [pin] invariant tag to the category tag."""
        ret = main([
            "--category", "ci",
            "--path", ".github/workflows/ci.yml",
            "--issue", "Always fetch unshallow git history for base diffs",
            "--solution", "Set fetch-depth: 0 in actions/checkout",
            "--pin",
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 0)

        content = self.obs_file.read_text(encoding="utf-8")
        last_line = content.splitlines()[-1]
        self.assertIn("| [ci][pin] |", last_line)

    def test_observation_with_actor_id(self):
        """Verify that --actor-id inserts [actor=<actor_id>] into the issue column while preserving 5-column table structure."""
        actor = "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"
        ret = main([
            "--category", "runtime",
            "--path", "scripts/verify_identity.py",
            "--issue", "Missing schema causes unhandled exit",
            "--solution", "Enforce jsonschema structure validation",
            "--actor-id", actor,
            "--obs-file", str(self.obs_file),
        ])
        self.assertEqual(ret, 0)

        content = self.obs_file.read_text(encoding="utf-8")
        last_line = content.splitlines()[-1]

        # Verify actor tag is at start of issue field
        self.assertIn(f"| [actor={actor}] Missing schema causes unhandled exit |", last_line)

        # Splitting by unescaped pipe must still yield exactly 7 parts (5 table columns + 2 outer empty parts)
        unescaped_pipe_parts = re.split(r"(?<!\\)\|", last_line)
        self.assertEqual(len(unescaped_pipe_parts), 7)

    def test_file_lock_concurrent_access(self):
        """Verify that cross-platform file locking prevents concurrent write access."""
        lock_file_path = Path(self.temp_dir.name) / "lock_test.txt"
        lock_file_path.write_text("lock test data\n", encoding="utf-8")

        with open(lock_file_path, "r+b") as f1:
            with file_lock(f1, blocking=False):
                # Attempting a second non-blocking lock on the same file from a separate handle must fail with OSError
                with open(lock_file_path, "r+b") as f2:
                    with self.assertRaises(OSError):
                        with file_lock(f2, blocking=False):
                            pass


# ---------------------------------------------------------------------------
# TestCategoryVocabularyD8 (from tests/test_dwave_r.py)
# ---------------------------------------------------------------------------
class TestCategoryVocabularyD8(unittest.TestCase):
    """T4.1: --category must accept the unified vocabulary (D8)."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.obs_file = Path(self.temp_dir.name) / "observations.md"
        _seed_obs(self.obs_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _record(self, category: str) -> int:
        return main([
            "--category", category,
            "--path", "src/app.py",
            "--issue", f"Issue for {category}",
            "--solution", f"Solution for {category}",
            "--obs-file", str(self.obs_file),
        ])

    def test_category_test_accepted(self):
        """D8 headline: `--category test` (already used in the live
        observations.md) must be accepted, exit 0, and land in the table."""
        self.assertEqual(self._record("test"), 0)
        self.assertIn("[test]", self.obs_file.read_text(encoding="utf-8"))

    def test_d8_unified_vocabulary_accepted(self):
        """`--category deps|db|api|build|env|git|architecture|testing` all succeed."""
        for cat in ("deps", "db", "api", "build", "env", "git", "architecture", "testing"):
            with self.subTest(category=cat):
                self.assertEqual(self._record(cat), 0, f"category '{cat}' rejected")
                self.assertIn(f"[{cat}]", self.obs_file.read_text(encoding="utf-8"))

    def test_engine_set_equals_unified_vocabulary(self):
        """The accepted set must be exactly the unified vocabulary — the full
        union, no missing doc-listed domains."""
        self.assertEqual(CANONICAL_CATEGORIES, UNIFIED_CATEGORIES)

    def test_legacy_engine_tags_stay_accepted(self):
        """Union semantics: explicit domain tags already in the engine stay."""
        self.assertTrue(
            LEGACY_ENGINE_TAGS.issubset(CANONICAL_CATEGORIES),
            f"legacy engine tags dropped: {LEGACY_ENGINE_TAGS - CANONICAL_CATEGORIES}",
        )

    def test_skill_doc_canonical_list_matches_engine(self):
        """D8 root-cause lock-in: the skill doc's canonical category list must
        equal the engine's accepted set exactly (no doc/engine drift)."""
        line = next(
            (
                ln
                for ln in SKILL_DOC.read_text(encoding="utf-8").splitlines()
                if "One of the canonical categories" in ln
            ),
            None,
        )
        self.assertIsNotNone(line, "canonical category list line missing from SKILL.md")
        doc_set = set(re.findall(r"`([a-z_]+)`", line))
        self.assertEqual(
            doc_set,
            CANONICAL_CATEGORIES,
            f"skill doc categories {sorted(doc_set)} != engine categories "
            f"{sorted(CANONICAL_CATEGORIES)}",
        )


# ---------------------------------------------------------------------------
# TestLockCleanupT42 (from tests/test_dwave_r.py)
# ---------------------------------------------------------------------------
class TestLockCleanupT42(unittest.TestCase):
    """T4.2: `<target>.lock` must not survive a completed record run."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.obs_file = Path(self.temp_dir.name) / "observations.md"
        _seed_obs(self.obs_file)
        self.lock_path = Path(str(self.obs_file) + ".lock")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _record(self, category: str = "runtime", extra=()) -> int:
        return main([
            "--category", category,
            "--path", "src/app.py",
            "--issue", "lock cleanup probe",
            "--solution", "released and unlinked",
            "--obs-file", str(self.obs_file),
            *extra,
        ])

    def test_no_lock_file_left_after_successful_record(self):
        """After record_obs.py completes, <target>.lock does NOT exist."""
        self.assertEqual(self._record(), 0)
        self.assertTrue(self.obs_file.exists(), "observation row not recorded")
        self.assertFalse(self.lock_path.exists(), "<target>.lock persisted after run")

    def test_no_lock_file_left_after_duplicate_suppression(self):
        """The duplicate-suppression early-return exits inside the lock —
        cleanup must still run on that path."""
        pinned = ["--date", "2026-01-15"]
        self.assertEqual(self._record(extra=pinned), 0)
        self.assertEqual(self._record(extra=pinned), 0)
        content = self.obs_file.read_text(encoding="utf-8")
        self.assertEqual(
            content.count("| 2026-01-15 | [runtime] | src/app.py | lock cleanup probe |"),
            1,
            "exact duplicate event not suppressed",
        )
        self.assertFalse(
            self.lock_path.exists(),
            "lock left behind on the duplicate-suppression path",
        )

    def test_no_lock_file_left_after_invalid_category(self):
        """Validation failure must never leave a lock file behind."""
        self.assertEqual(self._record(category="unauthorized_arbitrary_category"), 1)
        self.assertFalse(self.lock_path.exists())

    def test_file_lock_path_cleanup_preserves_exclusivity(self):
        """Cleanup must not break concurrent-write protection: while the path
        lock is held a second acquisition fails; after release the lock file
        is unlinked."""
        probe = Path(self.temp_dir.name) / "probe.lock"
        with file_lock(probe, blocking=False, cleanup=True):
            self.assertTrue(probe.exists(), "lock file absent while held")
            with open(probe, "r+b") as second:
                with self.assertRaises(OSError):
                    with file_lock(second, blocking=False):
                        pass
        self.assertFalse(probe.exists(), "path-based lock not unlinked after release")


if __name__ == "__main__":
    unittest.main()
