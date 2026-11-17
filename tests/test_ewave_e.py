#!/usr/bin/env python3
"""Wave E Lane E — Error envelopes + compact_memory `[>]` checkpoint support
(plan docs/superpowers/plans/2026-11-16-wave-e-context-economy.md §5).

RED-first specification (TDD):

- Uniform error envelope on the canonical failure paths of the 7 Wave E
  scripts (check_boundaries, verify_identity, inspect_meta_project,
  manage_reports, record_obs, update_meta_project, compact_memory), printed
  to stderr as the LEADING line in the canonical format:

      [CODE] <file>: <reason> | expected: <X> | actual: <Y> | next: <step>

  PRESENTATION ONLY: existing exit codes / rc semantics / JSON outputs on
  success MUST NOT change; Wave D structured refusals (intake diff listings,
  APPLY-REFUSED payloads, [ALLOWED] notices) keep their content — the
  envelope wraps them as the leading line.

- compact_memory checkpoint semantics (machine change): `- [>]` checkpoint
  rows and their indented checkpoint blocks are ACTIVE WORK — never
  re-homed/archived/compacted; only `- [x]` compaction semantics apply.

On the pre-fix codebase every test below fails (RED); each documents one
canonical failure path or the checkpoint invariant.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_boundaries import main as gate_main
from scripts.compact_memory import compact_tasks, main as compact_main
from scripts.inspect_meta_project import main as inspect_main
from scripts.manage_reports import main as manage_reports_main
from scripts.record_obs import main as record_obs_main
from scripts.update_meta_project import main as update_main
from scripts.verify_identity import main as identity_main


MINIMAL_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- `docs/**` and `*.md` documentation.

## Yellow Zone (Modification with Mandatory Verification)
- `AGENTS.md` root passport.

## Red Zone (Prohibited Without Direct User Confirmation)
- `LICENSE`
- `*boundaries.md`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""


class TempRootTestCase(unittest.TestCase):
    """Base fixture with automatic temp directory cleanup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ewave_e_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def sub(self, name: str) -> Path:
        p = self.root / name
        p.mkdir(parents=True, exist_ok=True)
        return p


def assert_envelope_leading(testcase, stderr_text, code, file_fragment):
    """The envelope must be the LEADING stderr line in canonical format:
    [CODE] <file>: <reason> | expected: <X> | actual: <Y> | next: <step>"""
    lines = stderr_text.splitlines()
    testcase.assertTrue(lines, "envelope expected on stderr, got nothing")
    leading = lines[0]
    testcase.assertIn(
        f"[{code}]", leading, f"envelope code missing in leading line: {leading!r}"
    )
    testcase.assertIn(
        file_fragment, leading, f"envelope must name the file: {leading!r}"
    )
    testcase.assertIn("expected:", leading, f"'expected:' missing: {leading!r}")
    testcase.assertIn("actual:", leading, f"'actual:' missing: {leading!r}")
    testcase.assertIn("next:", leading, f"'next:' missing: {leading!r}")
    return leading


# ---------------------------------------------------------------------------
# scripts/check_boundaries.py — BOUNDARY_VIOLATION / CONTEXT_UNRESOLVED
# (RED ZONE file: presentation-only envelope; refusal content, rc unchanged)
# ---------------------------------------------------------------------------


class TestBoundaryGateEnvelope(TempRootTestCase):
    """Canonical gate failures carry the envelope as the leading stderr line
    while the full Wave D refusal report and rc semantics stay intact."""

    def test_boundary_violation_envelope_leading_line(self):
        boundaries_path = self.sub("cfg") / "boundaries.md"
        boundaries_path.write_text(MINIMAL_BOUNDARIES, encoding="utf-8")

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = gate_main(["--files", "LICENSE", "--boundaries", str(boundaries_path)])

        self.assertEqual(rc, 1, "Red Zone violation must keep refusal rc=1")
        assert_envelope_leading(self, err.getvalue(), "BOUNDARY_VIOLATION", "LICENSE")
        # Wave D structured refusal content preserved verbatim after the wrap.
        self.assertIn("[FAILURE] BOUNDARY GATE FAILURE", err.getvalue())
        self.assertIn("[!] [RED ZONE VIOLATION] LICENSE", err.getvalue())
        self.assertIn("Total violations: 1", err.getvalue())

    def test_missing_boundaries_file_context_envelope(self):
        absent = self.root / "absent_boundaries.md"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = gate_main(["--files", "LICENSE", "--boundaries", str(absent)])

        self.assertEqual(rc, 1, "missing boundaries.md must keep failure rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "CONTEXT_UNRESOLVED", str(absent)
        )
        # Original diagnostic line preserved after the envelope.
        self.assertIn("boundaries.md file not found", err.getvalue())


# ---------------------------------------------------------------------------
# scripts/verify_identity.py — IDENTITY_UNRESOLVED
# ---------------------------------------------------------------------------


class TestVerifyIdentityEnvelope(TempRootTestCase):
    """Unknown actor resolution refuses with an IDENTITY_UNRESOLVED envelope
    naming the registry, keeping the original [ERROR] line and rc=1."""

    def test_unresolved_actor_envelope(self):
        registry_dir = self.root / ".agents"
        registry_dir.mkdir()
        (registry_dir / "meta-project.json").write_text(
            json.dumps(
                {"schema_version": "1.0", "project_id": "p", "installations": {}}
            ),
            encoding="utf-8",
        )
        unknown_actor = "p::harness-x::inst-x::role-x"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = identity_main(["--repo-root", str(self.root), "--actor", unknown_actor])

        self.assertEqual(rc, 1, "unresolved identity must keep refusal rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "IDENTITY_UNRESOLVED", ".agents/meta-project.json"
        )
        # Wave D structured refusal content preserved.
        self.assertIn("Unresolved identity", err.getvalue())
        self.assertIn(unknown_actor, err.getvalue())


# ---------------------------------------------------------------------------
# scripts/inspect_meta_project.py — CONTEXT_UNRESOLVED (diagnostic notice)
# ---------------------------------------------------------------------------


class TestInspectEnvelope(TempRootTestCase):
    """A healthy installation inspected without runtime context resolves to
    the CONTEXT_UNRESOLVED state: the report (stdout JSON, rc 0) is unchanged
    and the envelope appears on stderr as the leading line."""

    def setUp(self):
        # Dogfood-branch contract: the envelope contract under test is defined
        # against the live meta-project installation schema.
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )
        super().setUp()

    def test_context_unresolved_state_envelope(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch(
                "sys.argv",
                ["inspect_meta_project.py", "--repo-root", str(REPO_ROOT), "--json"],
            ):
                rc = inspect_main()

        self.assertEqual(rc, 0, "inspection rc semantics must not change")
        report = json.loads(out.getvalue())
        self.assertEqual(report["state"], "CONTEXT_UNRESOLVED")
        assert_envelope_leading(
            self, err.getvalue(), "CONTEXT_UNRESOLVED", ".agents/meta-project.json"
        )


# ---------------------------------------------------------------------------
# scripts/manage_reports.py — INVALID_REPORT
# ---------------------------------------------------------------------------


class TestManageReportsEnvelope(TempRootTestCase):
    """Structurally invalid report verification gains an INVALID_REPORT
    envelope on stderr; the stdout [FAIL] verdict and rc=1 are unchanged."""

    def test_invalid_report_envelope(self):
        bad_report = self.root / "bad_report.json"
        bad_report.write_text(
            json.dumps({"schema_version": "1.0.0", "report_type": "init"}),
            encoding="utf-8",
        )

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch(
                "sys.argv",
                ["manage_reports.py", "verify", "--report", str(bad_report)],
            ):
                rc = manage_reports_main()

        self.assertEqual(rc, 1, "invalid report must keep failure rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "INVALID_REPORT", "bad_report.json"
        )
        # Existing stdout verdict (structured refusal content) preserved.
        self.assertIn("[FAIL] Invalid report", out.getvalue())


# ---------------------------------------------------------------------------
# scripts/record_obs.py — INVALID_CATEGORY
# ---------------------------------------------------------------------------


class TestRecordObsEnvelope(TempRootTestCase):
    """A non-canonical observation category is refused with an
    INVALID_CATEGORY envelope naming the observations file; the original
    validation message and rc=1 are preserved (and nothing is written)."""

    def test_invalid_category_envelope(self):
        obs_file = self.root / "observations.md"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = record_obs_main(
                [
                    "--category", "bogus",
                    "--path", "somewhere",
                    "--issue", "issue text",
                    "--solution", "solution text",
                    "--obs-file", str(obs_file),
                ]
            )

        self.assertEqual(rc, 1, "invalid category must keep failure rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "INVALID_CATEGORY", "observations.md"
        )
        # Original validation message preserved after the envelope.
        self.assertIn("Invalid category 'bogus'", err.getvalue())
        self.assertFalse(obs_file.exists(), "refused record must not write files")


# ---------------------------------------------------------------------------
# scripts/update_meta_project.py — APPLY_REFUSED
# ---------------------------------------------------------------------------


class TestUpdateEngineEnvelope(TempRootTestCase):
    """A plan file that is not a serialized plan is refused at apply with an
    APPLY_REFUSED envelope wrapping the [APPLY-REFUSED] payload; rc=1 and the
    payload content are unchanged."""

    def test_apply_refused_envelope(self):
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps({"not": "a plan"}), encoding="utf-8")

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = update_main(
                [
                    "apply",
                    "--repo-root", str(self.root),
                    "--installation", "inst-main",
                    "--actor", "p::h::i::r",
                    "--plan-file", str(plan_file),
                ]
            )

        self.assertEqual(rc, 1, "apply refusal must keep rc=1")
        assert_envelope_leading(self, err.getvalue(), "APPLY_REFUSED", "plan.json")
        # Wave D structured refusal payload preserved verbatim after the wrap.
        self.assertIn("[APPLY-REFUSED]", err.getvalue())
        self.assertIn("not a serialized update plan", err.getvalue())


# ---------------------------------------------------------------------------
# scripts/compact_memory.py — STALE_INPUT (unreadable input) + `[>]` support
# ---------------------------------------------------------------------------


class TestCompactMemoryEnvelope(TempRootTestCase):
    """An unreadable/corrupt compaction input is refused with a STALE_INPUT
    envelope instead of a traceback; rc stays non-zero (crash path today)."""

    def test_unreadable_input_envelope(self):
        corrupt_obs = self.root / "observations.md"
        corrupt_obs.write_bytes(b"\xff\xfe\x00corrupt-not-utf8")
        absent_tasks = self.root / "absent_tasks.md"
        archive_dir = self.root / "archive"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = compact_main(
                [
                    "--observations", str(corrupt_obs),
                    "--tasks", str(absent_tasks),
                    "--archive-dir", str(archive_dir),
                ]
            )

        self.assertNotEqual(rc, 0, "unreadable input must fail, not crash silently")
        assert_envelope_leading(
            self, err.getvalue(), "STALE_INPUT", "observations.md"
        )
        self.assertFalse(archive_dir.exists(), "failed compaction must not archive")


class TestCheckpointNeverCompacted(TempRootTestCase):
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

        compacted, primary, archive = compact_tasks(
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
            rc = compact_main(
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
