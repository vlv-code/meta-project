#!/usr/bin/env python3
"""
Wave D — Lane R: record_obs hygiene tests (plan §6, tasks T4.1 + T4.2).

T4.1 — Category vocabulary unification (D8): the accepted set must be the
UNION of the skill-doc list and the engine list; explicit domain tags already
recorded in the live knowledge base stay accepted; the skill doc's canonical
list must match the engine exactly (no doc/engine drift).

T4.2 — Lock file cleanup: `<target>.lock` must NOT exist after the script
completes (release + unlink in finally, Windows-safe), without breaking
concurrent-write protection.

Zero-dependency tests using Python stdlib unittest.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.record_obs import CANONICAL_CATEGORIES, file_lock, main

# Plan T4.1: unified vocabulary (union of skill-doc list and engine list).
UNIFIED_CATEGORIES = {
    "build", "runtime", "deps", "db", "api", "test", "env", "ci",
    "boundaries", "orchestration", "decommission", "incident",
    "init", "testing", "git", "architecture",
}

# Explicit domain tags the engine already accepted — must stay accepted.
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
