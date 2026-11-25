"""
Unit tests for scripts/compact_memory.py (Context Rot Shield & Memory Compactor).
Verifies observation table rotation, task completion archiving, dry-run mode, and archive file creation.
"""

import contextlib
from datetime import datetime
import io
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

    def test_compaction_with_duplicate_rows(self):
        """Verify that duplicate rows are handled predictably without id()-based identity corruption."""
        sample_dups = """# Agent Observations Base

| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-01 | [ci] | comp1 | identical issue | identical fix |
| 2026-11-02 | [ci] | comp1 | identical issue | identical fix |
| 2026-11-03 | [ci] | comp1 | identical issue | identical fix |
| 2026-11-04 | [ci] | comp1 | identical issue | identical fix |
| 2026-11-05 | [ci] | comp1 | identical issue | identical fix |
"""
        compacted, primary, archive = compact_memory.compact_observations(
            sample_dups, max_rows=3, keep_rows=2
        )
        self.assertTrue(compacted)
        # Should keep newest 2 rows
        primary_rows = [line for line in primary.splitlines() if line.startswith("| 2026-")]
        self.assertEqual(len(primary_rows), 2)
        archive_rows = [line for line in archive.splitlines() if line.startswith("| 2026-")]
        self.assertEqual(len(archive_rows), 3)



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

    def test_compact_tasks_note_deduplication_and_idempotence(self):
        """Existing tasks archive NOTE (or multiple duplicates) is collapsed to exactly 1 block,
        and repeated compaction is idempotent without accumulating notices."""
        # Case A: Input already has multiple duplicate NOTE blocks, below rotation threshold.
        sample_with_dups = """# Current and Active Project Tasks

## Execution Plan and Checklist
> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

- [x] [agent-meta @ 2026-11-01 10:00] Step 1: Alpha completed
- [ ] [agent-meta @ 2026-11-02 10:00] Step 2: Beta pending
"""
        compacted, primary, archive = compact_memory.compact_tasks(
            sample_with_dups, max_completed=5, keep_completed=2
        )
        self.assertTrue(compacted, "Should return changed=True when collapsing duplicate notes")
        self.assertEqual(archive, "", "No archive rows should be generated when no tasks are rotated")
        self.assertEqual(primary.count("> [!NOTE]"), 1, "Duplicate notes must collapse to exactly 1")
        self.assertEqual(
            primary.count("Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`."),
            1,
        )

        # Case B: Input has 1 NOTE block, rotation triggers.
        # Repeated compaction must keep exactly 1 NOTE block (no duplication).
        content_with_single_note = primary + (
            "- [x] [agent-meta @ 2026-11-03 10:00] Step 3: Gamma completed\n"
            "- [x] [agent-meta @ 2026-11-04 10:00] Step 4: Delta completed\n"
            "- [x] [agent-meta @ 2026-11-05 10:00] Step 5: Epsilon completed\n"
        )
        compacted2, primary2, archive2 = compact_memory.compact_tasks(
            content_with_single_note, max_completed=3, keep_completed=1
        )
        self.assertTrue(compacted2)
        self.assertEqual(primary2.count("> [!NOTE]"), 1, "Rotation must not duplicate existing NOTE block")
        self.assertEqual(
            primary2.count("Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`."),
            1,
        )
        self.assertIn("Step 1: Alpha completed", archive2)

        # Idempotence: running compaction on primary2 without new tasks does not alter it
        compacted3, primary3, archive3 = compact_memory.compact_tasks(
            primary2, max_completed=3, keep_completed=1
        )
        self.assertFalse(compacted3)
        self.assertEqual(primary3, primary2)
        self.assertEqual(archive3, "")

    def test_compact_tasks_preserves_all_rotated_rows(self):
        """All rotated completed tasks must be preserved in archive_chunk without data loss."""
        tasks = ["# Current and Active Project Tasks", "", "## Execution Plan and Checklist"]
        for i in range(1, 11):
            tasks.append(f"- [x] [agent @ 2026-11-{i:02d} 10:00] Step {i}: Task {i} completed")
        tasks.append("- [ ] [agent @ 2026-11-11 10:00] Step 11: Task 11 pending")
        content = "\n".join(tasks) + "\n"

        compacted, primary, archive = compact_memory.compact_tasks(
            content, max_completed=4, keep_completed=2
        )
        self.assertTrue(compacted)
        # 10 completed, keep 2 -> 8 rotated (Steps 1..8)
        archive_lines = [ln for ln in archive.splitlines() if ln.strip()]
        self.assertEqual(len(archive_lines), 8)
        for i in range(1, 9):
            self.assertIn(f"Step {i}: Task {i} completed", archive)
            self.assertNotIn(f"Step {i}: Task {i} completed", primary)
        # Kept steps (9 and 10) in primary, not in archive
        for i in range(9, 11):
            self.assertIn(f"Step {i}: Task {i} completed", primary)
            self.assertNotIn(f"Step {i}: Task {i} completed", archive)
        self.assertIn("Step 11: Task 11 pending", primary)

    def test_compact_tasks_guards_checkpoints_and_probes(self):
        """Active checkpoints `- [>]` and probes `- [?] PROBE` (including nested rows) are guarded from rotation."""
        content = (
            "# Current and Active Project Tasks\n\n"
            "## Execution Plan and Checklist\n"
            "- [x] [agent @ 2026-11-01 10:00] Step 1: Base completed\n"
            "- [x] [agent @ 2026-11-02 10:00] Step 2: Base completed\n"
            "- [x] [agent @ 2026-11-03 10:00] Step 3: Base completed\n"
            "- [>] [agent @ 2026-11-04 10:00] Step 4: Active checkpoint\n"
            "  - goal: refactor\n"
            "  - done:\n"
            "    - [x] checkpoint sub-task 1\n"
            "    - [x] checkpoint sub-task 2\n"
            "  - next: step 5\n"
            "- [?] PROBE [agent @ 2026-11-05 10:00] Investigate cache invalidation\n"
            "  - hypothesis: TTL expired too early\n"
            "  - evidence:\n"
            "    - [x] probe verification in log.txt\n"
            "  - verdict: CONFIRMED\n"
            "- [x] [agent @ 2026-11-06 10:00] Step 6: Base completed\n"
            "- [ ] [agent @ 2026-11-07 10:00] Step 7: Pending\n"
        )
        compacted, primary, archive = compact_memory.compact_tasks(
            content, max_completed=2, keep_completed=1
        )
        self.assertTrue(compacted)
        # Checkpoint block must survive byte-identical in primary
        self.assertIn("- [>] [agent @ 2026-11-04 10:00] Step 4: Active checkpoint", primary)
        self.assertIn("- [x] checkpoint sub-task 1", primary)
        self.assertIn("- [x] checkpoint sub-task 2", primary)
        self.assertNotIn("checkpoint sub-task 1", archive)
        self.assertNotIn("checkpoint sub-task 2", archive)

        # Probe block must survive byte-identical in primary
        self.assertIn("- [?] PROBE [agent @ 2026-11-05 10:00] Investigate cache invalidation", primary)
        self.assertIn("- [x] probe verification in log.txt", primary)
        self.assertNotIn("Investigate cache invalidation", archive)
        self.assertNotIn("probe verification in log.txt", archive)

        # Plain completed tasks (Steps 1, 2, 3) rotated into archive
        self.assertIn("Step 1: Base completed", archive)
        self.assertIn("Step 2: Base completed", archive)
        self.assertIn("Step 3: Base completed", archive)
        self.assertNotIn("Step 1: Base completed", primary)
        # Newest plain completed task (Step 6) retained in primary
        self.assertIn("Step 6: Base completed", primary)
        self.assertNotIn("Step 6: Base completed", archive)


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

    def test_file_lock_lifecycle(self):
        """Verify cross-platform file_lock acquires and releases lock file cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            with compact_memory.file_lock(lock_path):
                self.assertTrue(lock_path.exists())
            # Lock released; file can be reopened/locked again
            with compact_memory.file_lock(lock_path):
                self.assertTrue(lock_path.exists())

    def test_file_lock_cleans_up_lock_file(self):
        """Verify file_lock removes .lock file when cleanup=True (default) and leaves it when cleanup=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            # Default cleanup=True
            with compact_memory.file_lock(lock_path):
                self.assertTrue(lock_path.exists())
            self.assertFalse(lock_path.exists(), "Lock file should be unlinked after exit when cleanup=True")

            # Explicit cleanup=False
            with compact_memory.file_lock(lock_path, cleanup=False):
                self.assertTrue(lock_path.exists())
            self.assertTrue(lock_path.exists(), "Lock file should remain when cleanup=False")


class TestCheckpointNeverCompacted(unittest.TestCase):
    """`- [>]` checkpoint rows are active work: the row AND its indented
    checkpoint block are NEVER re-homed/archived/compacted. Only `- [x]`
    compaction semantics apply (plain completed tasks still rotate)."""

    CHECKPOINT_BLOCK = [
        "- [>] [agent-a @ 2026-11-02 10:00] Step 4: In-flight refactor",
        "  - goal: land the Wave E envelope work",
        "  - decided: envelope format approved by dispatcher",
        "  - done:",
        "    - [x] RED test confirmed (tests/test_ewave_e.py)",
        "    - [x] envelope spec captured",
        "  - open: second acceptance case",
        "  - next: implement remaining case — executor: agent-a",
    ]

    def setUp(self):
        if compact_memory is None:
            self.skipTest("compact_memory module not implemented yet")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _fixture(self) -> str:
        lines = ["# Current and Active Project Tasks", ""]
        lines += [
            f"- [x] [agent-a @ 2026-11-01 10:00] Old completed step {i} done"
            for i in (1, 2, 3)
        ]
        lines += self.CHECKPOINT_BLOCK
        lines.append("- [ ] [agent-a @ 2026-11-03 10:00] Pending step")
        return "\n".join(lines) + "\n"

    def test_checkpoint_block_survives_compaction_untouched(self):
        content = self._fixture()

        compacted, primary, archive = compact_memory.compact_tasks(
            content, max_completed=2, keep_completed=1
        )

        # Plain `- [x]` rotation semantics unchanged: compaction still runs
        # and still archives genuinely completed (non-checkpoint) tasks.
        self.assertTrue(compacted, "`- [x]` compaction must keep working")
        self.assertIn("Old completed step 1", archive)
        self.assertNotIn("Old completed step 1", primary)

        # The checkpoint row and EVERY line of its block stay in the primary
        # file byte-identical and never leak into the archive.
        for block_line in self.CHECKPOINT_BLOCK:
            self.assertIn(
                block_line,
                primary,
                f"checkpoint block line must never be compacted away: {block_line!r}",
            )
            self.assertNotIn(
                block_line,
                archive,
                f"checkpoint block line must never be archived: {block_line!r}",
            )

    def test_checkpoint_survives_dry_run_byte_identical(self):
        tasks_file = self.root / "tasks.md"
        original = self._fixture()
        tasks_file.write_text(original, encoding="utf-8")
        absent_obs = self.root / "absent_observations.md"
        archive_dir = self.root / "archive"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = compact_memory.main(
                [
                    "--tasks", str(tasks_file),
                    "--observations", str(absent_obs),
                    "--archive-dir", str(archive_dir),
                    "--dry-run",
                ]
            )

        self.assertEqual(rc, 0)
        self.assertEqual(
            tasks_file.read_text(encoding="utf-8"),
            original,
            "a `- [>]` checkpoint must survive --dry-run untouched",
        )
        self.assertFalse(archive_dir.exists())


if __name__ == "__main__":
    unittest.main()
