#!/usr/bin/env python3
"""
Unit and Adversarial Tests for scripts/record_obs.py
Zero-dependency tests using Python stdlib unittest.
"""

import datetime
from pathlib import Path
import re
import sys
import tempfile
import unittest

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.record_obs import (
    CANONICAL_CATEGORIES,
    escape_pipes,
    file_lock,
    format_row,
    main,
    normalize_category,
    record_observation,
)


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


if __name__ == "__main__":
    unittest.main()
