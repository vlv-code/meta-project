"""
Unit tests for scripts/compact_memory.py (Context Rot Shield & Memory Compactor).
Verifies observation table rotation, task completion archiving, dry-run mode, and archive file creation.
"""

from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import compact_memory
except ImportError:
    compact_memory = None


SAMPLE_OBSERVATIONS = """# Agent Observations Base

Cumulative registry of findings.

---

| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-01 | [init] | comp1 | issue 1 | fix 1 |
| 2026-11-02 | [env] | comp2 | issue 2 | fix 2 |
| 2026-11-03 | [ci] | comp3 | issue 3 | fix 3 |
| 2026-11-04 | [code] | comp4 | issue 4 | fix 4 |
| 2026-11-05 | [theme] | comp5 | issue 5 | fix 5 |
| 2026-11-06 | [boundaries] | comp6 | issue 6 | fix 6 |
"""

SAMPLE_TASKS = """# Current and Active Project Tasks

## Active Objective
- Task: Test task objective

## Execution Plan and Checklist
- [x] [agent-meta @ 2026-11-01 10:00] Step 1: Alpha completed
- [x] [agent-meta @ 2026-11-02 10:00] Step 2: Beta completed
- [x] [agent-meta @ 2026-11-03 10:00] Step 3: Gamma completed
- [x] [agent-meta @ 2026-11-04 10:00] Step 4: Delta completed
- [ ] [agent-meta @ 2026-11-05 10:00] Step 5: Epsilon in progress
- [ ] [agent-meta @ 2026-11-06 10:00] Step 6: Zeta pending

## Delegated Subtasks
- None
"""


class TestCompactObservations(unittest.TestCase):
    """Test observation table compaction logic."""

    def setUp(self):
        if compact_memory is None:
            self.skipTest("compact_memory module not implemented yet")

    def test_no_compaction_below_threshold(self):
        compacted, primary, archive = compact_memory.compact_observations(
            SAMPLE_OBSERVATIONS, max_rows=10, keep_rows=5
        )
        self.assertFalse(compacted)
        self.assertEqual(primary, SAMPLE_OBSERVATIONS)
        self.assertEqual(archive, "")

    def test_compaction_above_threshold(self):
        compacted, primary, archive = compact_memory.compact_observations(
            SAMPLE_OBSERVATIONS, max_rows=4, keep_rows=2
        )
        self.assertTrue(compacted)
        # Should keep table header + 2 newest rows (rows 5 and 6)
        self.assertIn("comp5", primary)
        self.assertIn("comp6", primary)
        self.assertNotIn("comp1", primary)
        self.assertNotIn("comp2", primary)

        # Archive chunk should contain older rows
        self.assertIn("comp1", archive)
        self.assertIn("comp2", archive)
        self.assertIn("comp3", archive)
        self.assertIn("comp4", archive)

    def test_pinned_observations_never_archived(self):
        sample_pinned = """# Agent Observations Base

| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-01 | [env][pin] | comp1 | permanent invariant 1 | fix 1 |
| 2026-11-02 | [pin] | comp2 | permanent invariant 2 | fix 2 |
| 2026-11-03 | [ci] | comp3 | issue 3 | fix 3 |
| 2026-11-04 | [code] | comp4 | issue 4 | fix 4 |
| 2026-11-05 | [theme] | comp5 | issue 5 | fix 5 |
| 2026-11-06 | [boundaries] | comp6 | issue 6 | fix 6 |
"""
        compacted, primary, archive = compact_memory.compact_observations(
            sample_pinned, max_rows=4, keep_rows=2
        )
        self.assertTrue(compacted)
        # Pinned rows (comp1, comp2) MUST remain in primary
        self.assertIn("comp1", primary)
        self.assertIn("comp2", primary)
        self.assertIn("permanent invariant 1", primary)
        self.assertIn("permanent invariant 2", primary)

        # Newest rows (comp5, comp6) must also remain in primary
        self.assertIn("comp5", primary)
        self.assertIn("comp6", primary)

        # Older unpinned rows (comp3, comp4) must be moved to archive
        self.assertNotIn("comp3", primary)
        self.assertNotIn("comp4", primary)
        self.assertIn("comp3", archive)
        self.assertIn("comp4", archive)

        # Pinned rows MUST NOT be in archive
        self.assertNotIn("permanent invariant 1", archive)
        self.assertNotIn("permanent invariant 2", archive)



class TestCompactTasks(unittest.TestCase):
    """Test task checklist compaction logic."""

    def setUp(self):
        if compact_memory is None:
            self.skipTest("compact_memory module not implemented yet")

    def test_no_compaction_below_threshold(self):
        compacted, primary, archive = compact_memory.compact_tasks(
            SAMPLE_TASKS, max_completed=10, keep_completed=2
        )
        self.assertFalse(compacted)
        self.assertEqual(primary, SAMPLE_TASKS)
        self.assertEqual(archive, "")

    def test_compaction_above_threshold(self):
        compacted, primary, archive = compact_memory.compact_tasks(
            SAMPLE_TASKS, max_completed=3, keep_completed=1
        )
        self.assertTrue(compacted)
        # Pending tasks must remain intact
        self.assertIn("Step 5: Epsilon in progress", primary)
        self.assertIn("Step 6: Zeta pending", primary)

        # Only newest completed step (Step 4) should remain in primary
        self.assertIn("Step 4: Delta completed", primary)
        self.assertNotIn("Step 1: Alpha completed", primary)
        self.assertNotIn("Step 2: Beta completed", primary)

        # Archive chunk must contain older completed steps
        self.assertIn("Step 1: Alpha completed", archive)
        self.assertIn("Step 2: Beta completed", archive)
        self.assertIn("Step 3: Gamma completed", archive)


class TestCompactMemoryCLI(unittest.TestCase):
    """Test compact_memory CLI interface and file handling."""

    def setUp(self):
        if compact_memory is None:
            self.skipTest("compact_memory module not implemented yet")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.obs_file = self.root / "observations.md"
        self.obs_file.write_text(SAMPLE_OBSERVATIONS, encoding="utf-8")

        self.tasks_file = self.root / "tasks.md"
        self.tasks_file.write_text(SAMPLE_TASKS, encoding="utf-8")

        self.archive_dir = self.root / "archive"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_dry_run_does_not_modify_files(self):
        code = compact_memory.main([
            "--observations", str(self.obs_file),
            "--tasks", str(self.tasks_file),
            "--archive-dir", str(self.archive_dir),
            "--max-observations", "4",
            "--keep-observations", "2",
            "--dry-run"
        ])
        self.assertEqual(code, 0)
        self.assertEqual(self.obs_file.read_text(encoding="utf-8"), SAMPLE_OBSERVATIONS)
        self.assertFalse(self.archive_dir.exists())

    def test_cli_live_run_modifies_files_and_creates_archive(self):
        code = compact_memory.main([
            "--observations", str(self.obs_file),
            "--tasks", str(self.tasks_file),
            "--archive-dir", str(self.archive_dir),
            "--max-observations", "4",
            "--keep-observations", "2",
            "--max-completed-tasks", "3",
            "--keep-completed-tasks", "1"
        ])
        self.assertEqual(code, 0)
        self.assertTrue(self.archive_dir.is_dir())

        # Check archive files exist
        archive_files = list(self.archive_dir.glob("*.md"))
        self.assertGreaterEqual(len(archive_files), 1)

        # Primary observations file must be updated
        new_obs = self.obs_file.read_text(encoding="utf-8")
        self.assertIn("comp6", new_obs)
        self.assertNotIn("comp1", new_obs)

    def test_compaction_preserves_rows_with_date_and_dash_substrings(self):
        """Verify that rows containing 'Date' or '---' in text are not discarded when appending to existing archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            obs_file = tmp_path / "observations.md"
            archive_dir = tmp_path / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)

            current_month = datetime.now().strftime("%Y%m")
            archive_file = archive_dir / f"observations_{current_month}.md"
            archive_file.write_text(
                f"# Archived Observations ({current_month})\n\n---\n\n"
                "| Date | Category | Component | Issue | Solution |\n"
                "|---|---|---|---|---|\n"
                "| 2026-11-01 | [ci] | ci.yml | Existing item | Old fix |\n",
                encoding="utf-8",
            )

            rows = [
                "| Date | Category | Component | Issue | Solution |",
                "|---|---|---|---|---|",
                "| 2026-11-02 | [runtime] | date_parser.py | Invalid Date format returned | Use ISO Date format |",
                "| 2026-11-03 | [git] | deploy.sh | Missing --- separator in header | Added --- separator |",
            ]
            for i in range(4, 26):
                rows.append(f"| 2026-11-{i:02d} | [general] | module_{i}.py | Issue {i} | Fix {i} |")

            obs_file.write_text("\n".join(rows) + "\n", encoding="utf-8")

            ret = compact_memory.main([
                "--observations", str(obs_file),
                "--archive-dir", str(archive_dir),
                "--max-observations", "20",
                "--keep-observations", "10",
            ])
            self.assertEqual(ret, 0)

            archive_content = archive_file.read_text(encoding="utf-8")
            self.assertIn("Invalid Date format returned", archive_content, "Row with 'Date' in text was lost!")
            self.assertIn("Missing --- separator in header", archive_content, "Row with '---' in text was lost!")


if __name__ == "__main__":
    unittest.main()
