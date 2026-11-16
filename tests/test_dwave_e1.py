#!/usr/bin/env python3
"""
Wave D, Lane E1 — Engine State Integrity (RED phase contract tests).

Plan source: docs/superpowers/plans/2026-11-15-wave-d-state-integrity-and-perimeter.md (§3).

Closes auditor items п.1 + D6 (lock v2: base vs installed, marker-preserving
fast-forward), п.2 (restore rolls back files AND lock), п.4 (plan pins what
apply may do: pin + expected_before_sha256, CLI --plan-file).

RED contract: the six named tests
(test_second_update_preserves_markers, test_lock_records_base_and_installed,
test_same_pin_base_available, test_restore_returns_coherent_state,
test_apply_refuses_when_upstream_moved, test_apply_refuses_when_target_moved)
MUST fail against the pre-lane engine, then go GREEN after implementation.
Never edited to pass; a contradiction is reported, not patched.

Fixture conventions reuse tests/test_update_meta_project.py builders
(origin repo with commit history, integral cache, target with v1 lock).

Zero-dependency: Python 3.10+ stdlib only.
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

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_update_meta_project import (  # fixture reuse (same package)
    ACTOR_ID,
    INSTALLATION_ID,
    MARKER_BODY,
    MARKER_CLOSE,
    MARKER_OPEN,
    ORIGIN_X_V1,
    ORIGIN_X_V2,
    ORIGIN_Y_V1,
    ORIGIN_Y_V2,
    _git_ok,
    _make_cache_dir,
    _make_origin_repo,
    _make_target,
    _manifest_v2,
    _origin_files_v2,
    _sha,
    _write_lock,
    _write_tree,
)

try:
    from scripts.update_meta_project import (
        ApplyError,
        apply_updates,
        check_updates,
        load_bundle,
        main,
        plan_updates,
        read_lock,
        resolve_source,
        restore_updates,
    )
except ImportError:  # pragma: no cover - engine module always present in repo
    ApplyError = None
    apply_updates = None
    check_updates = None
    load_bundle = None
    main = None
    plan_updates = None
    read_lock = None
    resolve_source = None
    restore_updates = None

# ---------------------------------------------------------------------------
# Extended fixture: a THIRD upstream revision (v3) for the two-step
# update-with-adaptations chain (п.1 scenario).
# ---------------------------------------------------------------------------

ORIGIN_Y_V3 = b"# Skill Y v3\n\nPhase 1: do v3 things (Y-V3-UPSTREAM).\n"


def _manifest_v3() -> dict:
    manifest = _manifest_v2()
    manifest["framework_version"] = "1.0.0-fix.3"
    return manifest


def _origin_files_v3() -> dict:
    files = _origin_files_v2()
    files["skills/y/SKILL.md"] = ORIGIN_Y_V3
    return files


def _marked_y(base: bytes) -> bytes:
    """Installed content of skills/y/SKILL.md carrying one local adaptation
    wrapped in local_repo_data markers (HTML form)."""
    return base + b"\n" + MARKER_OPEN + b"\n" + MARKER_BODY + b"\n" + MARKER_CLOSE + b"\n"


LOCK_RELPATH = ".agents/framework-lock.json"


# ---------------------------------------------------------------------------
# Base test case
# ---------------------------------------------------------------------------


class WaveE1TestCase(unittest.TestCase):
    """Temp-dir fixture with automatic cleanup + RED guards."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_e1_")
        self.tmp = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def require_engine(self, *symbols):
        for symbol in symbols:
            if symbol is None:
                self.fail("engine not implemented (RED)")

    def apply_or_fail(self, repo_root, plan, **kwargs):
        """apply_updates on a conflict-free plan must succeed loudly."""
        try:
            return apply_updates(repo_root, plan, ACTOR_ID, INSTALLATION_ID, **kwargs)
        except Exception as exc:  # noqa: BLE001 - surfacing engine failures verbatim
            self.fail(f"apply_updates must succeed on this clean fixture: {exc!r}")
            return None

    def _lock_bytes(self, target: Path) -> bytes:
        return (target / LOCK_RELPATH).read_bytes()

    def _merge_actions(self, plan) -> dict:
        actions = plan.get("actions") if isinstance(plan, dict) else None
        return {
            a.get("path"): a
            for a in (actions or [])
            if isinstance(a, dict) and a.get("op") == "merge"
        }


# ---------------------------------------------------------------------------
# T1.1 — Lock v2: base vs installed (п.1 + D6, CRITICAL)
# ---------------------------------------------------------------------------


class TestLockV2BaseAndInstalled(WaveE1TestCase):
    def test_second_update_preserves_markers(self):
        """п.1: TWO sequential updates over a marked adaptation.

        install v1 -> local marked block -> apply v2 (markers preserved)
        -> apply v3 (different bytes) -> markers MUST still be present.
        Currently FAILS: the fast-forward branch plain-overwrites the file
        and silently drops the local adaptation.
        """
        self.require_engine(
            resolve_source, load_bundle, read_lock, plan_updates, apply_updates
        )
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        # Step 1: install the v1 set at the pinned first revision.
        pin1 = resolve_source(str(origin), first_sha)
        plan1 = plan_updates(target, load_bundle(pin1, cache), read_lock(target))
        self.apply_or_fail(target, plan1)
        self.assertEqual(
            (target / "skills" / "y" / "SKILL.md").read_bytes(),
            ORIGIN_Y_V1,
            "fixture sanity: v1 installed verbatim",
        )

        # Step 2: local adaptation wrapped in markers.
        (target / "skills" / "y" / "SKILL.md").write_bytes(_marked_y(ORIGIN_Y_V1))

        # Step 3: apply upstream v2 (main) — markers preserved via merge.
        pin2 = resolve_source(str(origin), "main")
        plan2 = plan_updates(target, load_bundle(pin2, cache), read_lock(target))
        self.apply_or_fail(target, plan2)
        merged_v2 = (target / "skills" / "y" / "SKILL.md").read_bytes()
        self.assertIn(b"Y-V2-UPSTREAM", merged_v2, "upstream v2 must be applied")
        self.assertIn(MARKER_OPEN, merged_v2, "markers must survive the first update")

        # Step 4: upstream publishes v3 (different bytes) AFTER step 3.
        _write_tree(origin, _manifest_v3(), _origin_files_v3())
        _git_ok(origin, "add", "-A")
        _git_ok(origin, "commit", "-qm", "c3: upstream drift v3")
        pin3 = resolve_source(str(origin), "main")
        self.assertNotEqual(_get_sha(pin2), _get_sha(pin3), "fixture sanity: upstream moved")
        plan3 = plan_updates(target, load_bundle(pin3, cache), read_lock(target))
        self.apply_or_fail(target, plan3)
        merged_v3 = (target / "skills" / "y" / "SKILL.md").read_bytes()
        self.assertIn(
            b"Y-V3-UPSTREAM",
            merged_v3,
            "upstream v3 content must be applied on the second update",
        )
        self.assertIn(
            MARKER_OPEN,
            merged_v3,
            "local_repo_data opener must survive the SECOND update (fast-forward)",
        )
        self.assertIn(
            MARKER_BODY,
            merged_v3,
            "marked local adaptation must survive the SECOND update",
        )
        self.assertIn(
            MARKER_CLOSE,
            merged_v3,
            "local_repo_data closer must survive the SECOND update",
        )
        # Lock v2 coherence for the marker-carrying fast-forward write.
        entry = self._lock_entry(target, "skills/y/SKILL.md")
        self.assertEqual(
            entry.get("base_sha256"),
            _sha(ORIGIN_Y_V3),
            "lock v2 must record the pinned upstream bytes as base even on a "
            "marker-preserving fast-forward",
        )
        self.assertEqual(
            entry.get("installed_sha256"),
            _sha(merged_v3),
            "lock v2 must record the on-disk installed bytes",
        )

    def _lock_entry(self, target: Path, rel: str) -> dict:
        lock = read_lock(target)
        self.assertIsNotNone(lock, "apply must maintain the framework lock")
        for comp in lock.get("components") or []:
            if comp.get("path") == rel:
                return comp
        self.fail(f"lock carries no entry for {rel}")
        return {}

    def test_lock_records_base_and_installed(self):
        """After a MERGE apply the lock entry carries BOTH base_sha256 (the
        pinned upstream bytes) and installed_sha256 (the on-disk bytes)."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        (target / "skills" / "y" / "SKILL.md").write_bytes(_marked_y(ORIGIN_Y_V1))

        pin = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(pin, cache), read_lock(target))
        self.apply_or_fail(target, plan)

        on_disk = (target / "skills" / "y" / "SKILL.md").read_bytes()
        entry = self._lock_entry(target, "skills/y/SKILL.md")
        self.assertEqual(
            entry.get("base_sha256"),
            _sha(ORIGIN_Y_V2),
            "lock v2 entry must record base_sha256 = pinned upstream bytes",
        )
        self.assertEqual(
            entry.get("installed_sha256"),
            _sha(on_disk),
            "lock v2 entry must record installed_sha256 = on-disk bytes",
        )

    def test_same_pin_base_available(self):
        """D6: local drift against the SAME pin resolves without needs_base —
        the pinned bundle itself is a valid base candidate when
        pin.sha == lock base sha (hash-verified acceptance)."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        # Install the full v1 set at the pinned revision.
        pin1 = resolve_source(str(origin), first_sha)
        self.apply_or_fail(
            target, plan_updates(target, load_bundle(pin1, cache), read_lock(target))
        )

        # Local drift: marked adaptation on top of the SAME pinned revision.
        (target / "skills" / "y" / "SKILL.md").write_bytes(_marked_y(ORIGIN_Y_V1))

        # Re-plan at the SAME pin: the pinned (cached) bundle holds the exact
        # lock-recorded base bytes, so no needs_base may appear.
        plan = plan_updates(target, load_bundle(pin1, cache), read_lock(target))
        needs = plan.get("needs_base") or []
        self.assertNotIn(
            "skills/y/SKILL.md",
            json.dumps(needs),
            f"D6: same-pin drift must resolve via the pinned bundle as merge "
            f"base, got needs_base: {json.dumps(needs)}",
        )
        merge_actions = self._merge_actions(plan)
        self.assertIn(
            "skills/y/SKILL.md",
            merge_actions,
            f"same-pin drift must plan a marker-preserving merge, plan: "
            f"{json.dumps(plan, default=str)[:600]}",
        )
        self.apply_or_fail(target, plan)
        merged = (target / "skills" / "y" / "SKILL.md").read_bytes()
        self.assertIn(b"Y-V1-UPSTREAM", merged, "same-pin content stays")
        self.assertIn(MARKER_BODY, merged, "adaptation preserved on same-pin re-apply")

    def test_v1_lock_entries_read_as_base_and_installed(self):
        """Backward compat lock-in: v1 entries (single sha256) are read as
        base=installed by plan/merge-base acceptance — never dropped."""
        self.require_engine(read_lock, plan_updates)
        target = _make_target(self.tmp)  # fixture writes a v1-format lock
        (target / "skills" / "y" / "SKILL.md").write_bytes(_marked_y(ORIGIN_Y_V1))
        bundle = {
            "manifest": _manifest_v2(),
            "files": _origin_files_v2(),
            "base": {"skills/y/SKILL.md": ORIGIN_Y_V1, "scripts/x.py": ORIGIN_X_V1},
        }
        plan = plan_updates(target, bundle, read_lock(target))
        merge_actions = self._merge_actions(plan)
        self.assertIn(
            "skills/y/SKILL.md",
            merge_actions,
            "v1 lock sha256 must be accepted as the merge base record",
        )


def _get_sha(pin) -> str:
    """Tolerant commit_sha accessor for dict-like SourcePin."""
    if isinstance(pin, dict):
        return str(pin.get("commit_sha") or "")
    return str(getattr(pin, "commit_sha", "") or "")


# ---------------------------------------------------------------------------
# T1.2 — Restore rolls back files AND lock (п.2)
# ---------------------------------------------------------------------------


class TestRestoreCoherence(WaveE1TestCase):
    def test_restore_returns_coherent_state(self):
        """п.2: successful apply -> restore -> files AND framework-lock.json
        revert to the pre-apply state; a subsequent check against the
        pre-apply pin reports up_to_date with zero drift."""
        self.require_engine(
            resolve_source, load_bundle, read_lock, plan_updates,
            apply_updates, restore_updates, check_updates,
        )
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        lock_before = self._lock_bytes(target)
        x_before = (target / "scripts" / "x.py").read_bytes()
        y_before = (target / "skills" / "y" / "SKILL.md").read_bytes()

        pin = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(pin, cache), read_lock(target))
        self.apply_or_fail(target, plan)
        self.assertNotEqual(
            self._lock_bytes(target),
            lock_before,
            "fixture sanity: apply rewrote the lock",
        )

        result = restore_updates(target)
        self.assertIn(
            LOCK_RELPATH,
            json.dumps(result),
            f"restore must roll the lock back too, got: {json.dumps(result)[:600]}",
        )
        self.assertEqual(
            self._lock_bytes(target),
            lock_before,
            "framework-lock.json must revert byte-identically to pre-apply",
        )
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), x_before)
        self.assertEqual((target / "skills" / "y" / "SKILL.md").read_bytes(), y_before)

        check = check_updates(target, str(origin), first_sha, cache)
        self.assertEqual(
            check.get("status"),
            "up_to_date",
            f"check after restore must report up_to_date, got: "
            f"{json.dumps(check, default=str)[:600]}",
        )
        self.assertEqual(
            check.get("drifted"),
            [],
            "no component may be diagnosed as drifted after a coherent restore",
        )


# ---------------------------------------------------------------------------
# T1.3 — Plan pins what apply may do (п.4, TOCTOU)
# ---------------------------------------------------------------------------


class TestPlanPinsApply(WaveE1TestCase):
    def test_plan_carries_pin_and_expected_shas(self):
        """Plan result carries pin (source + commit_sha) and per-action
        expected_before_sha256 (None for creates)."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        pinned = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(pinned, cache), read_lock(target))

        pin = plan.get("pin") or {}
        self.assertEqual(
            str(pin.get("commit_sha") or ""),
            _get_sha(pinned),
            "plan must pin the exact source commit sha",
        )
        self.assertTrue(
            str(pin.get("source") or ""),
            "plan pin must carry the source repository",
        )

        actions = plan.get("actions") or []
        self.assertTrue(actions, "fixture sanity: plan must carry actions")
        by_path = {a.get("path"): a for a in actions}
        for rel, action in by_path.items():
            self.assertIn(
                "expected_before_sha256",
                action,
                f"action for {rel} must pin the target state at plan time",
            )
        self.assertEqual(
            by_path["scripts/x.py"].get("expected_before_sha256"),
            _sha(ORIGIN_X_V1),
            "update action must pin the on-disk sha observed at plan time",
        )
        self.assertIsNone(
            by_path["scripts/z.py"].get("expected_before_sha256"),
            "create action pins 'absent' (None)",
        )

    def test_apply_refuses_when_upstream_moved(self):
        """п.4: apply with a re-resolved pin that differs from the plan pin
        must REFUSE ('plan/source revision changed: re-plan required') and
        perform ZERO writes — never silently apply a different SHA."""
        self.require_engine(ApplyError, resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        plan_pin = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(plan_pin, cache), read_lock(target))

        # Upstream branch moves AFTER the plan was approved.
        _write_tree(origin, _manifest_v3(), _origin_files_v3())
        _git_ok(origin, "add", "-A")
        _git_ok(origin, "commit", "-qm", "c3: upstream moves after plan")
        moved_pin = resolve_source(str(origin), "main")
        self.assertNotEqual(_get_sha(plan_pin), _get_sha(moved_pin))

        x_before = (target / "scripts" / "x.py").read_bytes()
        lock_before = self._lock_bytes(target)

        with self.assertRaises(ApplyError) as ctx:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID, resolved_pin=moved_pin)
        message = str(ctx.exception)
        self.assertIn(
            "plan/source revision changed",
            message,
            f"refusal must diagnose the moved source revision, got: {message}",
        )
        self.assertIn(
            "re-plan required",
            message,
            f"refusal must demand a re-plan, got: {message}",
        )
        # ZERO writes anywhere.
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), x_before)
        self.assertEqual(self._lock_bytes(target), lock_before, "lock must stay untouched")
        self.assertFalse((target / "scripts" / "z.py").exists())

    def test_apply_refuses_when_target_moved(self):
        """п.4: a target file edited between plan and apply_updates must
        trigger 'target state changed since plan: <path>' refusal with ZERO
        writes (all-or-nothing preserved)."""
        self.require_engine(ApplyError, resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        pin = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(pin, cache), read_lock(target))

        # A user edits an action target between plan and apply.
        surprise = ORIGIN_X_V1 + b"# surprise user edit after plan\n"
        (target / "scripts" / "x.py").write_bytes(surprise)
        y_before = (target / "skills" / "y" / "SKILL.md").read_bytes()
        lock_before = self._lock_bytes(target)

        with self.assertRaises(ApplyError) as ctx:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        message = str(ctx.exception)
        self.assertIn(
            "target state changed since plan: scripts/x.py",
            message,
            f"refusal must name the moved target path, got: {message}",
        )
        # ZERO writes: no other action target may be written either.
        self.assertEqual((target / "skills" / "y" / "SKILL.md").read_bytes(), y_before)
        self.assertEqual(self._lock_bytes(target), lock_before)
        self.assertFalse((target / "scripts" / "z.py").exists(), "creates must not run either")
        self.assertFalse((target / "skills" / "w" / "SKILL.md").exists())


# ---------------------------------------------------------------------------
# T1.3 CLI surface — --plan-file, [RE-PLANNED] notice, report record
# ---------------------------------------------------------------------------


class TestCliPlanFile(WaveE1TestCase):
    def _run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_cli_apply_accepts_plan_file_refuses_stale_and_records(self):
        """--plan-file: apply executes the approved plan, refuses a stale
        plan when upstream moved, and records the approved plan file in the
        update report."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        plan_args = [
            "plan", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
        ]

        # 1) Approve a plan, upstream then moves.
        rc, out, _err = self._run_main(plan_args)
        self.assertEqual(rc, 0, f"plan must succeed, stderr: {_err}")
        stale_plan_file = self.tmp / "approved-plan-stale.json"
        stale_plan_file.write_text(out, encoding="utf-8")

        _write_tree(origin, _manifest_v3(), _origin_files_v3())
        _git_ok(origin, "add", "-A")
        _git_ok(origin, "commit", "-qm", "c3: upstream moves after approval")

        # 2) apply with the stale approved plan must REFUSE.
        apply_stale = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main",
            "--plan-file", str(stale_plan_file),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        try:
            rc, _out, err = self._run_main(apply_stale)
        except SystemExit as exc:  # argparse refusing --plan-file = RED
            self.fail(f"apply must accept --plan-file (argparse refused: rc={exc.code})")
        self.assertEqual(
            rc, 1,
            f"stale approved plan must be refused with rc=1, stderr: {err}",
        )
        self.assertIn("plan/source revision changed", err)
        self.assertFalse((target / "scripts" / "z.py").exists(), "zero writes on refusal")

        # 3) Fresh plan file applies cleanly and is recorded in the report.
        rc, out, _err = self._run_main(plan_args)
        self.assertEqual(rc, 0)
        fresh_plan_file = self.tmp / "approved-plan-fresh.json"
        fresh_plan_file.write_text(out, encoding="utf-8")
        apply_fresh = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main",
            "--plan-file", str(fresh_plan_file),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        try:
            rc, _out, err = self._run_main(apply_fresh)
        except SystemExit as exc:
            self.fail(f"apply must accept --plan-file (argparse refused: rc={exc.code})")
        self.assertEqual(
            rc, 0, f"apply with a fresh approved plan must succeed, stderr: {err}"
        )
        self.assertNotIn("[RE-PLANNED]", err, "plan-file apply is NOT a re-plan")
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            ORIGIN_X_V2,
            "the approved plan's content must be applied verbatim",
        )

        report_dir = target / ".agents" / "reports" / INSTALLATION_ID / "update"
        self.assertTrue(report_dir.is_dir(), f"update report directory missing: {report_dir}")
        reports = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(report_dir.glob("*.json"))
            if p.name != "latest.json"
        ]
        self.assertTrue(
            any(r.get("approved_plan_file") == str(fresh_plan_file) for r in reports),
            "the update report must record the approved plan file path in "
            "'approved_plan_file', reports: " + json.dumps(reports)[:400],
        )

    def test_cli_apply_without_plan_file_prints_replanned_notice(self):
        """When apply builds its own plan (no --plan-file) it must print the
        [RE-PLANNED] notice — the freshly computed plan is treated as
        approved, but the deviation from an approved plan file is visible."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        try:
            rc, _out, err = self._run_main(
                [
                    "apply", "--repo-root", str(target),
                    "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
                    "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
                ],
            )
        except SystemExit as exc:
            self.fail(f"apply must run (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 0, f"apply must succeed, stderr: {err}")
        self.assertIn(
            "[RE-PLANNED]",
            err,
            "apply without --plan-file must print the [RE-PLANNED] notice on stderr",
        )


if __name__ == "__main__":
    unittest.main()
