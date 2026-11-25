#!/usr/bin/env python3
"""Canonical domain test suite for the update engine (scripts/update_meta_project.py).

Consolidated in Wave T (Lane T2) from:
- tests/test_update_meta_project.py (core engine lifecycle)
- tests/test_dwave_e1.py (lock v2, restore coherence, plan pins)
- tests/test_dwave_e2.py (perimeter, cache, markers, layouts, adoption)
- tests/test_dwave_d6b.py (cross-pin origin base fetch)
- tests/test_gwave_h.py (CRLF normalization, dead symbols, flag checks)

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.manage_reports import validate_report
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
from tests._git_fixtures import (
    ACTOR_ID,
    INSTALLATION_ID,
    MARKER_BODY,
    MARKER_CLOSE,
    MARKER_OPEN,
    ORIGIN_W_V2,
    ORIGIN_X_V1,
    ORIGIN_X_V2,
    ORIGIN_X_V3,
    ORIGIN_Y_V1,
    ORIGIN_Y_V2,
    ORIGIN_Z_V1,
    X_GHOST_BASE,
    X_GHOST_LOCAL,
    _bundle_files,
    _chdir,
    _content_fingerprint,
    _dump,
    _entry_sha_compat,
    _git_ok,
    _make_cache_dir,
    _make_origin_repo,
    _make_target,
    _manifest_v1,
    _manifest_v2,
    _manifest_v3,
    _origin_files_v1,
    _origin_files_v2,
    _sha,
    _write_fingerprint,
    _write_lock,
    _write_tree,
    _get,
)

# ---------------------------------------------------------------------------
# Extended fixtures and constants
# ---------------------------------------------------------------------------

LOCK_RELPATH = ".agents/framework-lock.json"
STRANGER_ACTOR = "fixture-app/alpha::antigravity::ag-main::agent-intruder"

BOUNDARIES_WITH_X_RED = """# Responsibility Zones and Change Boundaries

## Red Zone (Prohibited Without Direct User Confirmation)
- `scripts/x.py`
- `*boundaries.md`
- `LICENSE`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""

ORIGIN_Y_V3 = b"# Skill Y v3\n\nPhase 1: do v3 things (Y-V3-UPSTREAM).\n"
ORIGIN_W_V3 = b"# Skill W v3\n\nW-V3-UPSTREAM content.\n"

X_HASH_OPEN = b"# local_repo_data:hotfix"
X_HASH_CLOSE = b"# /local_repo_data:hotfix"
X_HASH_BODY = b"HOTFIX_VALUE = 'local-1'"

NOTES_V1 = b"team notes v1\n"
NOTES_V2 = b"team notes v2 (upstream edit)\n"
NOTES_LOCAL = (
    NOTES_V1
    + b"\n<!-- local_repo_data:local-context -->\nLOCALE = eu\n<!-- /local_repo_data:local-context -->\n"
    + b"# local_repo_data:ops-flag\nOPFLAG = on\n# /local_repo_data:ops-flag\n"
)

CODE_MARKER_OPEN = b"# local_repo_data:hotfix"
CODE_MARKER_CLOSE = b"# /local_repo_data:hotfix"
CODE_MARKER_BODY = b"HOTFIX: cross-pin base must come from origin history."


def _origin_files_v3() -> dict:
    files = _origin_files_v2()
    files["skills/y/SKILL.md"] = ORIGIN_Y_V3
    return files


def _origin_files_v3_e2() -> dict:
    files = _origin_files_v2()
    files["skills/w/SKILL.md"] = ORIGIN_W_V3
    files["scripts/x.py"] = ORIGIN_X_V3
    return files


def _get_sha(pin) -> str:
    """Tolerant commit_sha accessor for dict-like SourcePin."""
    if isinstance(pin, dict):
        return str(pin.get("commit_sha") or "")
    return str(getattr(pin, "commit_sha", "") or "")


def _marked_y(base: bytes) -> bytes:
    return base + b"\n" + MARKER_OPEN + b"\n" + MARKER_BODY + b"\n" + MARKER_CLOSE + b"\n"


def _hash_marked_x(base: bytes) -> bytes:
    return base + b"\n" + X_HASH_OPEN + b"\n" + X_HASH_BODY + b"\n" + X_HASH_CLOSE + b"\n"


def _commit_tree(origin: Path, manifest: dict, files: dict, message: str) -> None:
    _write_tree(origin, manifest, files)
    _git_ok(origin, "add", "-A")
    _git_ok(origin, "commit", "-qm", message)


def _git_init(path: Path) -> None:
    _git_ok(path, "init", "-q", "-b", "main")
    _git_ok(path, "commit", "-q", "--allow-empty", "-m", "baseline")


def _crlf(data: bytes) -> bytes:
    return data.replace(b"\n", b"\r\n")


def _entry_installed_sha(entry: dict) -> str:
    from scripts.update_meta_project import _entry_installed_sha as f
    return f(entry)


def _run_cli(args: list[str]):
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(REPO_ROOT / "scripts" / "update_meta_project.py"),
            *args,
        ],
        capture_output=True,
        cwd=str(REPO_ROOT),
    )


# ---------------------------------------------------------------------------
# UpdateEngineTestCase (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class UpdateEngineTestCase(unittest.TestCase):
    """Temp-dir fixture with automatic cleanup + RED guards."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="upd_engine_")
        self.tmp = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def require_engine(self, *symbols):
        for symbol in symbols:
            if symbol is None:
                self.fail("engine not implemented (RED)")

    def apply_or_fail(self, repo_root, plan):
        """apply_updates on a conflict-free plan must succeed loudly."""
        try:
            return apply_updates(repo_root, plan, ACTOR_ID, INSTALLATION_ID)
        except Exception as exc:  # noqa: BLE001 - surfacing engine failures verbatim
            self.fail(f"apply_updates must succeed on this clean fixture: {exc!r}")
            return None

    def full_apply(self, target: Path, origin: Path, cache_dir=None) -> None:
        """Resolve -> load -> plan -> apply pipeline from origin ref 'main'."""
        pin = resolve_source(str(origin), "main")
        bundle = load_bundle(pin, cache_dir)
        plan = plan_updates(target, bundle, read_lock(target))
        self.apply_or_fail(target, plan)


# ---------------------------------------------------------------------------
# TestSourceResolution (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestSourceResolution(UpdateEngineTestCase):
    def test_ref_resolves_to_exact_sha(self):
        self.require_engine(resolve_source)
        origin, _first_sha = _make_origin_repo(self.tmp)
        head_sha = _git_ok(origin, "rev-parse", "HEAD").stdout.strip()
        pin = resolve_source(str(origin), "main")
        sha = _get(pin, "commit_sha")
        self.assertIsInstance(sha, str, f"SourcePin.commit_sha must be a str, got: {sha!r}")
        self.assertRegex(sha, r"^[0-9a-f]{40}$")
        self.assertEqual(sha, head_sha, "ref 'main' must resolve to the exact HEAD sha")

    def test_components_fetched_from_pinned_sha_only(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        pin = resolve_source(str(origin), "main")
        pinned_sha = _get(pin, "commit_sha")

        # Origin receives a NEW commit AFTER resolve: apply must still install
        # the pinned sha's blob content (fetch-by-sha, never refloat).
        (origin / "scripts" / "x.py").write_bytes(ORIGIN_X_V3)
        _git_ok(origin, "add", "-A")
        _git_ok(origin, "commit", "-qm", "c3: post-resolve drift")

        bundle = load_bundle(pin, None)
        self.assertEqual(
            _bundle_files(bundle).get("scripts/x.py"),
            ORIGIN_X_V2,
            "bundle must carry the pinned (commit 2) blob, not the new HEAD",
        )
        plan = plan_updates(target, bundle, read_lock(target))
        self.apply_or_fail(target, plan)
        installed = (target / "scripts" / "x.py").read_bytes()
        self.assertEqual(
            installed,
            ORIGIN_X_V2,
            f"apply must install the pinned sha content (pinned={pinned_sha})",
        )
        self.assertNotEqual(installed, ORIGIN_X_V3)


# ---------------------------------------------------------------------------
# TestCacheFallback (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestCacheFallback(UpdateEngineTestCase):
    def test_unavailable_origin_uses_integral_cache_with_declared_origin(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        pin = resolve_source(str(origin), first_sha)  # explicit-SHA ref, resolved while origin lives
        shutil.move(str(origin), str(self.tmp / "origin-repo-gone"))  # origin becomes unavailable
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        bundle = load_bundle(pin, cache)
        files = _bundle_files(bundle)
        self.assertEqual(files.get("scripts/x.py"), ORIGIN_X_V1)
        self.assertEqual(files.get("scripts/z.py"), ORIGIN_Z_V1)
        self.assertEqual(files.get("skills/y/SKILL.md"), ORIGIN_Y_V1)

        plan = plan_updates(target, bundle, read_lock(target))
        self.apply_or_fail(target, plan)
        self.assertEqual(
            (target / "scripts" / "z.py").read_bytes(),
            ORIGIN_Z_V1,
            "cache bundle must be installable (integral set from one sha)",
        )
        lock = read_lock(target)
        self.assertIsNotNone(lock, "apply must rewrite the lock")
        source = _get(lock, "source")
        self.assertEqual(_get(source, "origin"), "cache", "cache fallback must be DECLARED in the lock")
        self.assertEqual(_get(source, "commit_sha"), first_sha)
        components = {_get(c, "path"): c for c in (_get(lock, "components") or [])}
        # Installed-state sha256 via the v1/v2-tolerant accessor.
        self.assertEqual(_entry_sha_compat(components["scripts/z.py"]), _sha(ORIGIN_Z_V1))
        # NEW (Wave D E1, T1.1): a create records lock schema v2 with
        # base == installed (pinned upstream bytes) and the reserved target.
        z_entry = components["scripts/z.py"]
        self.assertEqual(z_entry.get("base_sha256"), _sha(ORIGIN_Z_V1))
        self.assertEqual(z_entry.get("installed_sha256"), _sha(ORIGIN_Z_V1))
        self.assertEqual(z_entry.get("target"), "scripts/z.py")

    def test_partial_cache_refused_no_mixed_bundle(self):
        self.require_engine(resolve_source, load_bundle)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        before_tree = _content_fingerprint(target)
        before_lock = (target / ".agents" / "framework-lock.json").read_bytes()

        pin = resolve_source(str(origin), first_sha)
        shutil.move(str(origin), str(self.tmp / "origin-repo-gone"))
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        # Punch a hole: remove one manifest component -> cache is partial.
        (cache / first_sha / "skills" / "y" / "SKILL.md").unlink()

        with self.assertRaises(Exception) as ctx:
            load_bundle(pin, cache)
        self.assertTrue(
            str(ctx.exception).strip(),
            "partial-cache refusal must carry an explanatory message",
        )
        # No partial materialization: target tree and lock untouched, nothing installed.
        self.assertEqual(_content_fingerprint(target), before_tree)
        self.assertEqual(
            (target / ".agents" / "framework-lock.json").read_bytes(),
            before_lock,
        )
        self.assertFalse((target / "scripts" / "z.py").exists())


# ---------------------------------------------------------------------------
# TestReadOnlyModes (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestReadOnlyModes(UpdateEngineTestCase):
    def test_check_mode_zero_write(self):
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        before_tree = _write_fingerprint(target)
        before_cache = _content_fingerprint(cache)
        with _chdir(target):
            rc = main(
                [
                    "check",
                    "--repo-root", str(target),
                    "--source", str(origin),
                    "--ref", "main",
                    "--cache-dir", str(cache),
                ]
            )
        self.assertIsInstance(rc, int)
        self.assertIn(
            rc,
            (0, 1),
            f"check must run (rc in 0..1; 2 would be a usage error), got rc={rc}",
        )
        self.assertEqual(
            _write_fingerprint(target),
            before_tree,
            "check mode must be zero-write on the project (size AND mtime_ns)",
        )
        self.assertEqual(_content_fingerprint(cache), before_cache, "check must not write the cache")
        self.assertFalse((target / ".agents" / "update-journal.json").exists())
        self.assertFalse((target / ".agents" / "reports").exists())

    def test_plan_mode_zero_write_and_lists_conflicts(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        # Unmarked local modification of an installed component.
        local_edit = ORIGIN_X_V1 + b"# local unmarked edit\n"
        (target / "scripts" / "x.py").write_bytes(local_edit)

        pin = resolve_source(str(origin), "main")
        bundle = load_bundle(pin, cache)
        before_tree = _write_fingerprint(target)
        plan = plan_updates(target, bundle, read_lock(target))
        self.assertEqual(
            _write_fingerprint(target),
            before_tree,
            "plan mode must be zero-write on the project",
        )
        conflicts = _get(plan, "conflicts") or []
        self.assertIn(
            "scripts/x.py",
            _dump(conflicts),
            f"unmarked local change must surface as a conflict entry, plan: {_dump(plan)[:800]}",
        )


# ---------------------------------------------------------------------------
# TestThreeWayMerge (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestThreeWayMerge(UpdateEngineTestCase):
    def test_local_repo_data_blocks_preserved(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        local_y = (
            ORIGIN_Y_V1 + b"\n" + MARKER_OPEN + b"\n" + MARKER_BODY + b"\n" + MARKER_CLOSE + b"\n"
        )
        (target / "skills" / "y" / "SKILL.md").write_bytes(local_y)

        pin = resolve_source(str(origin), "main")
        bundle = load_bundle(pin, cache)
        plan = plan_updates(target, bundle, read_lock(target))
        self.assertNotIn(
            "skills/y/SKILL.md",
            _dump(_get(plan, "conflicts") or []),
            "marker-wrapped local adaptations are preserved, not conflicts",
        )
        self.apply_or_fail(target, plan)

        merged = (target / "skills" / "y" / "SKILL.md").read_bytes()
        self.assertIn(b"Y-V2-UPSTREAM", merged, "upstream v2 content must be applied")
        self.assertIn(MARKER_OPEN, merged, "local_repo_data block opener must survive")
        self.assertIn(MARKER_BODY, merged, "marked local content must survive")
        self.assertIn(MARKER_CLOSE, merged, "local_repo_data block closer must survive")

    def test_unmarked_local_change_surfaces_conflict(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        local_edit = ORIGIN_X_V1 + b"# local unmarked edit\n"
        (target / "scripts" / "x.py").write_bytes(local_edit)

        pin = resolve_source(str(origin), "main")
        bundle = load_bundle(pin, cache)
        plan = plan_updates(target, bundle, read_lock(target))
        self.assertIn(
            "scripts/x.py",
            _dump(_get(plan, "conflicts") or []),
            "unmarked local change must surface as a conflict entry",
        )
        try:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        except Exception:
            pass  # refusing loudly is acceptable; silently overwriting is not
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            local_edit,
            "conflicting file must NOT be overwritten by apply",
        )

    def test_base_unavailable_no_safe_merge_claim(self):
        self.require_engine(read_lock, plan_updates, apply_updates)
        target = _make_target(self.tmp)
        # Local file edited on top of a base whose bytes exist nowhere
        # (lock sha256 points at ghost content; no cache, no origin).
        (target / "scripts" / "x.py").write_bytes(X_GHOST_LOCAL)
        _write_lock(
            target,
            [
                {"path": "scripts/x.py", "kind": "script", "sha256": _sha(X_GHOST_BASE)},
                {"path": "skills/y/SKILL.md", "kind": "skill", "sha256": _sha(ORIGIN_Y_V1)},
            ],
        )
        bundle = {
            "manifest": _manifest_v1(),
            "files": dict(_origin_files_v1(), **{"scripts/x.py": ORIGIN_X_V2}),
            "base": {},
        }
        plan = plan_updates(target, bundle, read_lock(target))
        needs_base = _get(plan, "needs_base") or []
        self.assertIn(
            "scripts/x.py",
            _dump(needs_base),
            f"missing base must surface as needs_base, plan: {_dump(plan)[:800]}",
        )
        self.assertNotIn(
            "scripts/x.py",
            _dump(_get(plan, "actions") or []),
            "a base-less merge must never be claimed as a safe action",
        )
        try:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        except Exception:
            pass
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            X_GHOST_LOCAL,
            "apply must not overwrite a needs-base component",
        )


# ---------------------------------------------------------------------------
# TestApplyAtomicityAndRecovery (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestApplyAtomicityAndRecovery(UpdateEngineTestCase):
    def test_journal_written_and_restore_reverts_only_engine_changes(self):
        self.require_engine(
            resolve_source, load_bundle, read_lock, plan_updates, apply_updates, restore_updates
        )
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        pin = resolve_source(str(origin), "main")
        bundle = load_bundle(pin, None)
        plan = plan_updates(target, bundle, read_lock(target))
        self.assertIn(
            "skills/w/SKILL.md",
            _dump(_get(plan, "actions") or []),
            "fixture expects at least the new-component action to be plannable",
        )

        # Third-party activity inside the apply window:
        # 1. a user edits an unmanaged file;
        user_notes = target / "docs" / "user-notes.md"
        user_notes.write_bytes(b"USER NOTE v2 (edited while apply runs)\n")
        # 2. a NEW-component target path is poisoned with a directory so the
        #    per-file write fails mid-apply.
        poison = target / "skills" / "w" / "SKILL.md"
        poison.parent.mkdir(parents=True, exist_ok=True)
        poison.mkdir()

        lock_path = target / ".agents" / "framework-lock.json"
        lock_before = lock_path.read_bytes()
        before = _content_fingerprint(target)
        try:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        except Exception:
            pass  # the injected failure may surface as an exception or a failed result

        journal = target / ".agents" / "update-journal.json"
        self.assertTrue(journal.exists(), "operation journal must exist once apply has started")
        full_success = (
            (target / "scripts" / "x.py").read_bytes() == ORIGIN_X_V2
            and (target / "scripts" / "z.py").exists()
            and poison.is_file()
        )
        self.assertFalse(full_success, "injected write failure must abort the apply run")

        restore_updates(target)
        self.assertEqual(
            _content_fingerprint(target),
            before,
            "restore must return the working tree to the pre-apply state "
            "(framework lock included in the comparison since Wave D E1)",
        )
        # NEW (Wave D E1, п.2): the lock is part of the coherent-state
        # contract. This aborted apply never reached the lock write, so the
        # lock must be byte-identical after restore.
        self.assertEqual(
            lock_path.read_bytes(),
            lock_before,
            "framework-lock.json must stay byte-identical across an aborted "
            "apply + restore cycle",
        )
        self.assertEqual(
            user_notes.read_bytes(),
            b"USER NOTE v2 (edited while apply runs)\n",
            "third-party edits outside the managed set must never be clobbered",
        )
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            ORIGIN_X_V1,
            "engine-applied component change must be reverted by restore",
        )
        self.assertFalse((target / "scripts" / "z.py").exists())

    def test_registry_identity_untouched(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        registry = target / ".agents" / "meta-project.json"
        before = registry.read_bytes()

        self.full_apply(target, origin)
        # Sanity: the apply really ran (engine component updated).
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), ORIGIN_X_V2)
        self.assertEqual(
            registry.read_bytes(),
            before,
            ".agents/meta-project.json must stay byte-identical: role assignment and"
            " identity bindings are never engine business",
        )


# ---------------------------------------------------------------------------
# TestLock (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestLock(UpdateEngineTestCase):
    def test_lock_records_installed_subset_and_sha256(self):
        self.require_engine(main, read_lock)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        with _chdir(target):
            rc = main(
                [
                    "apply",
                    "--repo-root", str(target),
                    "--source", str(origin),
                    "--ref", "main",
                    "--components", "scripts/x.py",
                    "--installation", INSTALLATION_ID,
                    "--actor", ACTOR_ID,
                ]
            )
        self.assertEqual(rc, 0, "subset apply on a clean target must succeed with rc=0")

        lock = read_lock(target)
        self.assertIsNotNone(lock)
        self.assertEqual(_get(lock, "schema_version"), "1.0.0")
        components = {_get(c, "path"): c for c in (_get(lock, "components") or [])}
        self.assertEqual(
            set(components),
            {"scripts/x.py", "skills/y/SKILL.md"},
            "lock must record exactly the installed subset",
        )
        # Installed-state sha256, read through the v1/v2-tolerant accessor.
        self.assertEqual(_entry_sha_compat(components["scripts/x.py"]), _sha(ORIGIN_X_V2))
        self.assertEqual(_entry_sha_compat(components["skills/y/SKILL.md"]), _sha(ORIGIN_Y_V1))
        # Recorded hashes match the bytes actually on disk.
        self.assertEqual(
            _entry_sha_compat(components["scripts/x.py"]),
            hashlib.sha256((target / "scripts" / "x.py").read_bytes()).hexdigest(),
        )
        # NEW (Wave D E1, T1.1): lock component schema v2 — the marker-free
        # plain update records base == installed (pinned upstream bytes) and
        # the reserved `target` field defaulting to the manifest path.
        x_entry = components["scripts/x.py"]
        self.assertEqual(x_entry.get("base_sha256"), _sha(ORIGIN_X_V2))
        self.assertEqual(x_entry.get("installed_sha256"), _sha(ORIGIN_X_V2))
        self.assertEqual(x_entry.get("target"), "scripts/x.py")
        # Backward compat (Wave D E1, T1.1): the component NOT touched by
        # this subset apply stays in its v1 shape (single sha256, no v2
        # fields) and keeps being readable.
        y_entry = components["skills/y/SKILL.md"]
        self.assertIn("sha256", y_entry, "untouched v1 entry keeps its v1 shape")
        self.assertNotIn("base_sha256", y_entry)
        self.assertNotIn("installed_sha256", y_entry)
        # Unselected components are neither installed nor recorded.
        self.assertFalse((target / "scripts" / "z.py").exists())
        self.assertFalse((target / "skills" / "w").exists())
        source = _get(lock, "source")
        head_sha = _git_ok(origin, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(_get(source, "commit_sha"), head_sha)
        self.assertEqual(_get(source, "origin"), "upstream")

    def test_drifted_component_diagnosed_as_unknown_origin(self):
        self.require_engine(check_updates)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        # User modified an installed script after installation.
        (target / "scripts" / "x.py").write_bytes(ORIGIN_X_V1 + b"# local drift edit\n")

        result = check_updates(target, str(origin), "main", None)
        blob = _dump(result)
        self.assertIn("scripts/x.py", blob, "drifted component must be named in the check result")
        lowered = blob.lower()
        self.assertTrue(
            any(token in lowered for token in ("unknown", "diverg", "drift")),
            f"diagnosis must classify the drift origin (unknown/diverged/drifted), got: {blob[:600]}",
        )

    def test_user_files_outside_managed_set_untouched(self):
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        user_doc = target / "docs" / "user-notes.md"
        user_obs = target / ".agents" / "project_knowledge" / "observations.md"
        doc_before = user_doc.read_bytes()
        obs_before = user_obs.read_bytes()

        self.full_apply(target, origin)

        self.assertTrue(user_doc.exists())
        self.assertEqual(user_doc.read_bytes(), doc_before)
        self.assertTrue(user_obs.exists())
        self.assertEqual(user_obs.read_bytes(), obs_before)


# ---------------------------------------------------------------------------
# TestProtectedComponents (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestProtectedComponents(UpdateEngineTestCase):
    def test_red_zone_refused_with_open_item_message(self):
        self.require_engine(read_lock, plan_updates, apply_updates)
        target = _make_target(self.tmp)
        protected_path = ".agents/project_knowledge/boundaries.md"
        protected_file = target / ".agents" / "project_knowledge" / "boundaries.md"
        before = protected_file.read_bytes()

        manifest = _manifest_v1()
        manifest["components"].append(
            {"path": protected_path, "kind": "knowledge", "requires": []}
        )
        bundle = {
            "manifest": manifest,
            "files": dict(_origin_files_v1(), **{protected_path: b"# hijacked boundaries\n"}),
            "base": {},
        }

        halt_text = ""
        plan = None
        try:
            plan = plan_updates(target, bundle, read_lock(target))
        except Exception as exc:  # noqa: BLE001 - halt-at-plan is an accepted refusal point
            halt_text = str(exc)
        if plan is not None:
            self.assertIn(
                protected_path,
                _dump(_get(plan, "protected") or []),
                "protected component must be listed in plan['protected']",
            )
            try:
                result = apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
            except Exception as exc:  # noqa: BLE001 - refusal may raise or return a failed result
                halt_text = str(exc)
            else:
                halt_text = _dump(result)

        lowered = halt_text.lower()
        self.assertIn(
            "sanctioned",
            lowered,
            f"refusal must state no sanctioned mechanism exists, got: {halt_text[:600]}",
        )
        self.assertIn(
            "open item",
            lowered,
            f"refusal must reference the explicitly open Red-Zone item, got: {halt_text[:600]}",
        )
        self.assertEqual(
            protected_file.read_bytes(),
            before,
            "protected component must not be modified by plan or apply",
        )


# ---------------------------------------------------------------------------
# TestLegacyTransition (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestLegacyTransition(UpdateEngineTestCase):
    def test_divergent_duplicate_copies_halt_with_report(self):
        self.require_engine(read_lock, plan_updates, apply_updates)
        target = _make_target(self.tmp)
        legacy = target / ".agents" / "scripts" / "x.py"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_bytes(ORIGIN_X_V1 + b"# legacy divergent copy\n")

        bundle = {
            "manifest": _manifest_v2(),
            "files": _origin_files_v2(),
            "base": {"scripts/x.py": ORIGIN_X_V1, "skills/y/SKILL.md": ORIGIN_Y_V1},
        }
        plan_error = None
        plan = None
        try:
            plan = plan_updates(target, bundle, read_lock(target))
        except Exception as exc:  # noqa: BLE001 - halting at plan is the expected semantics
            plan_error = exc
        report_text = str(plan_error) if plan_error is not None else _dump(plan)

        self.assertIn("scripts/x.py", report_text, "halt report must name the canonical copy")
        self.assertIn(".agents/scripts/x.py", report_text, "halt report must name the legacy copy")
        self.assertRegex(
            report_text,
            r"[0-9a-f]{64}",
            "halt report must carry the sha256 hashes of both copies",
        )

        if plan_error is None:
            conflicts = _get(plan, "conflicts") or []
            self.assertTrue(
                any(".agents/scripts/x.py" in _dump(c) for c in conflicts),
                "duplicate must surface as a blocking conflict, never a silent plan",
            )
            canonical_before = (target / "scripts" / "x.py").read_bytes()
            legacy_before = legacy.read_bytes()
            try:
                apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
            except Exception:
                pass
            self.assertEqual(
                (target / "scripts" / "x.py").read_bytes(),
                canonical_before,
                "apply must not proceed over divergent duplicates",
            )
            self.assertEqual(legacy.read_bytes(), legacy_before)


# ---------------------------------------------------------------------------
# TestPerimeterAdmission (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestPerimeterAdmission(UpdateEngineTestCase):
    """Wave D E2 (T6.1, auditor п.5a): apply is a perimeter operation — the
    actor must be ADMITTED by the project identity registry. Library-level
    contract pinned on the shared registry fixture (a registered+active
    binding); the CLI surface and bootstrap semantics live in
    tests/test_dwave_e2.py."""

    STRANGER_ACTOR = "fixture-app/alpha::antigravity::ag-main::agent-intruder"

    def test_apply_refuses_actor_not_admitted(self):
        self.require_engine(
            resolve_source, load_bundle, read_lock, plan_updates, apply_updates
        )
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        pin = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(pin, None), read_lock(target))

        lock_before = (target / ".agents" / "framework-lock.json").read_bytes()
        x_before = (target / "scripts" / "x.py").read_bytes()

        with self.assertRaises(Exception) as ctx:
            apply_updates(target, plan, self.STRANGER_ACTOR, INSTALLATION_ID)
        self.assertIn(
            "actor not admitted",
            str(ctx.exception),
            f"refusal must diagnose the unadmitted actor, got: {ctx.exception!r}",
        )
        # ZERO writes anywhere.
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), x_before)
        self.assertFalse((target / "scripts" / "z.py").exists())
        self.assertEqual(
            (target / ".agents" / "framework-lock.json").read_bytes(),
            lock_before,
        )
        self.assertFalse((target / ".agents" / "update-journal.json").exists())

    def test_registered_active_actor_is_admitted(self):
        self.require_engine(
            resolve_source, load_bundle, read_lock, plan_updates, apply_updates
        )
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        self.full_apply(target, origin)
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            ORIGIN_X_V2,
            "the registered+active fixture actor must pass admission",
        )


# ---------------------------------------------------------------------------
# TestUpdateReport (from tests/test_update_meta_project.py)
# ---------------------------------------------------------------------------
class TestUpdateReport(UpdateEngineTestCase):
    def test_apply_produces_update_report_via_manage_reports(self):
        self.require_engine(main)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        with _chdir(target):
            rc = main(
                [
                    "apply",
                    "--repo-root", str(target),
                    "--source", str(origin),
                    "--ref", "main",
                    "--installation", INSTALLATION_ID,
                    "--actor", ACTOR_ID,
                ]
            )
        self.assertEqual(rc, 0, "full apply on a clean target must succeed with rc=0")

        report_dir = target / ".agents" / "reports" / INSTALLATION_ID / "update"
        self.assertTrue(report_dir.is_dir(), f"update report directory missing: {report_dir}")
        candidates = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(report_dir.glob("*.json"))
            if p.name != "latest.json"
        ]
        reports = [r for r in candidates if r.get("report_type") == "update"]
        self.assertTrue(reports, f"no report_type='update' report found in {report_dir}")
        report = reports[-1]
        self.assertTrue(report.get("run_id"), "update report must carry a run_id")
        self.assertTrue(report.get("affected_components"), "update report must list affected components")
        errors = validate_report(report, expected_type="update")
        self.assertEqual(
            errors,
            [],
            f"update report must pass manage_reports validation (Task C3): {errors}",
        )


# ---------------------------------------------------------------------------
# WaveE1TestCase (from tests/test_dwave_e1.py)
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
# TestLockV2BaseAndInstalled (from tests/test_dwave_e1.py)
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


# ---------------------------------------------------------------------------
# TestRestoreCoherence (from tests/test_dwave_e1.py)
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
# TestPlanPinsApply (from tests/test_dwave_e1.py)
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
# TestCliPlanFile (from tests/test_dwave_e1.py)
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


# ---------------------------------------------------------------------------
# WaveE2TestCase (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class WaveE2TestCase(unittest.TestCase):
    """Temp-dir fixture with automatic cleanup + RED guards."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_e2_")
        self.tmp = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def require_engine(self, *symbols):
        for symbol in symbols:
            if symbol is None:
                self.fail("engine not implemented (RED)")

    def _run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main(argv)
        return rc, out.getvalue(), err.getvalue()

    def _clean_plan(self, target: Path, origin: Path, cache: Path, ref: str = "main"):
        pin = resolve_source(str(origin), ref)
        return plan_updates(target, load_bundle(pin, cache), read_lock(target))

    def _lock_bytes(self, target: Path) -> bytes:
        return (target / LOCK_RELPATH).read_bytes()

    def _lock_entry(self, target: Path, rel: str) -> dict:
        lock = read_lock(target)
        self.assertIsNotNone(lock, "apply must maintain the framework lock")
        for comp in lock.get("components") or []:
            if comp.get("path") == rel:
                return comp
        self.fail(f"lock carries no entry for {rel}")
        return {}

    def _set_binding_status(self, target: Path, status: str) -> None:
        reg_path = target / ".agents" / "meta-project.json"
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
        registry["roles"]["agent-dev-lead"]["bindings"][INSTALLATION_ID]["status"] = status
        reg_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# TestIdentityAdmission (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestIdentityAdmission(WaveE2TestCase):
    def test_apply_refuses_unregistered_actor_zero_writes(self):
        """apply with an actor that is not admitted by the project registry
        must raise ApplyError('actor not admitted ...') with ZERO writes."""
        self.require_engine(ApplyError, resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        # Truthful cache: the helper writes v1 content, so it must be keyed by
        # the v1 pin (a HEAD-pinned v1 cache is a lying cache — SEC-2 refuses).
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        plan = self._clean_plan(target, origin, cache)

        lock_before = self._lock_bytes(target)
        x_before = (target / "scripts" / "x.py").read_bytes()

        with self.assertRaises(ApplyError) as ctx:
            apply_updates(target, plan, STRANGER_ACTOR, INSTALLATION_ID)
        message = str(ctx.exception)
        self.assertIn(
            "actor not admitted",
            message,
            f"refusal must diagnose the unadmitted actor, got: {message}",
        )
        # ZERO writes anywhere (no files, no lock, not even a journal).
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), x_before)
        self.assertFalse((target / "scripts" / "z.py").exists())
        self.assertEqual(self._lock_bytes(target), lock_before)
        self.assertFalse(
            (target / ".agents" / "update-journal.json").exists(),
            "an admission refusal must not even start an operation journal",
        )

    def test_cli_apply_refused_prints_apply_refused(self):
        """CLI apply with an unregistered actor exits rc=1 and prints
        '[APPLY-REFUSED] ... actor not admitted ...'."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--installation", INSTALLATION_ID, "--actor", STRANGER_ACTOR,
        ]
        try:
            rc, _out, err = self._run_main(argv)
        except SystemExit as exc:  # argparse problems are not refusals
            self.fail(f"apply must run (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 1, f"unadmitted actor must be refused with rc=1, stderr: {err}")
        self.assertIn("[APPLY-REFUSED]", err, f"refusal prefix missing, stderr: {err}")
        self.assertIn("actor not admitted", err, f"refusal reason missing, stderr: {err}")
        self.assertFalse((target / "scripts" / "z.py").exists(), "zero writes on refusal")

    def test_registered_active_actor_passes(self):
        """The fixture's registered+active actor is admitted and the same
        apply succeeds."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        rc, _out, err = self._run_main(argv)
        self.assertEqual(rc, 0, f"registered+active actor must be admitted, stderr: {err}")
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            ORIGIN_X_V2,
            "the admitted apply really ran",
        )

    def test_identityless_project_bootstrap_allowed(self):
        """A project WITHOUT .agents/meta-project.json is identity-less
        (bootstrap state, Lane M Phase 0.5): admission is not applicable and
        the apply proceeds."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        (target / ".agents" / "meta-project.json").unlink()
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--installation", INSTALLATION_ID, "--actor", "bootstrap-operator",
        ]
        rc, _out, err = self._run_main(argv)
        self.assertEqual(
            rc, 0,
            f"identity-less (bootstrap) project must not be blocked by "
            f"admission, stderr: {err}",
        )
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), ORIGIN_X_V2)

    def test_non_active_binding_refused(self):
        """A REGISTERED actor whose binding is not 'active' is still not
        admitted (admission control, mirroring verify_identity)."""
        self.require_engine(ApplyError, resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        self._set_binding_status(target, "planned")
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        plan = self._clean_plan(target, origin, cache)
        with self.assertRaises(ApplyError) as ctx:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        self.assertIn(
            "actor not admitted",
            str(ctx.exception),
            f"non-active binding must be refused, got: {ctx.exception}",
        )


# ---------------------------------------------------------------------------
# TestProjectBoundariesAndProtect (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestProjectBoundariesAndProtect(WaveE2TestCase):
    def test_project_red_component_protected_with_boundaries_reason(self):
        """A component whose TARGET path is Red in the project's
        boundaries.md must land in plan['protected'] with a reason naming the
        project boundaries; DEFAULT patterns still apply (union)."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        target = _make_target(self.tmp)
        (target / ".agents" / "project_knowledge" / "boundaries.md").write_text(
            BOUNDARIES_WITH_X_RED, encoding="utf-8"
        )
        manifest = _manifest_v1()
        manifest["components"].append(
            {"path": "tests/test_integrity.py", "kind": "test", "requires": []}
        )
        files = dict(_origin_files_v1())
        files["tests/test_integrity.py"] = b"# integrity spec\n"
        bundle = {"manifest": manifest, "files": files, "base": {}}

        plan = plan_updates(target, bundle, read_lock(target))
        protected = {p.get("path"): p for p in plan.get("protected") or []}
        self.assertIn(
            "scripts/x.py",
            protected,
            f"project-Red component must be protected, plan: {json.dumps(plan, default=str)[:600]}",
        )
        self.assertIn(
            "boundaries",
            str(protected["scripts/x.py"].get("reason", "")).lower(),
            "the refusal reason must name the project boundaries file",
        )
        # Union: DEFAULT patterns still applied.
        self.assertIn(
            "tests/test_integrity.py",
            protected,
            "DEFAULT protect patterns must still be applied alongside the "
            "project boundaries consult",
        )

        # Apply refuses and writes nothing.
        x_before = (target / "scripts" / "x.py").read_bytes()
        lock_before = self._lock_bytes(target)
        try:
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        except Exception:
            pass  # refusing loudly (exception or failed result) is expected
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), x_before)
        self.assertEqual(self._lock_bytes(target), lock_before)
        self.assertFalse((target / "scripts" / "z.py").exists())

    def test_user_protect_pattern_wired_union_with_defaults(self):
        """plan_updates(protect_patterns=...) protects the user pattern AND
        keeps the DEFAULT patterns (union)."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates)
        target = _make_target(self.tmp)
        manifest = _manifest_v1()
        manifest["components"].append(
            {"path": "tests/test_integrity.py", "kind": "test", "requires": []}
        )
        files = dict(_origin_files_v1())
        files["tests/test_integrity.py"] = b"# integrity spec\n"
        bundle = {"manifest": manifest, "files": files, "base": {}}

        plan = plan_updates(
            target, bundle, read_lock(target), protect_patterns=("scripts/x.py",)
        )
        protected = {p.get("path") for p in plan.get("protected") or []}
        self.assertIn(
            "scripts/x.py",
            protected,
            f"--protect pattern must actually protect the component, plan: "
            f"{json.dumps(plan, default=str)[:600]}",
        )
        self.assertIn(
            "tests/test_integrity.py",
            protected,
            "user patterns must ADD to the defaults, not replace them",
        )

    def test_cli_protect_flag_wires_protection(self):
        """CLI plan --protect scripts/x.py actually protects scripts/x.py."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        argv = [
            "plan", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--protect", "scripts/x.py",
        ]
        try:
            rc, out, err = self._run_main(argv)
        except SystemExit as exc:
            self.fail(f"plan must accept --protect (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 0, f"plan must succeed, stderr: {err}")
        plan = json.loads(out)
        protected = [p.get("path") for p in plan.get("protected") or []]
        self.assertIn(
            "scripts/x.py",
            protected,
            f"--protect scripts/x.py must protect it (parsed-but-unused bug), "
            f"protected: {protected}",
        )


# ---------------------------------------------------------------------------
# TestOfflineCache (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestOfflineCache(WaveE2TestCase):
    def test_cli_apply_offline_dead_origin_exact_sha_ref(self):
        """Dead origin + explicit 40-hex --ref + integral cache -> apply
        succeeds and the lock declares origin: cache."""
        self.require_engine(main, read_lock)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        hidden = self.tmp / "origin-repo-hidden"
        shutil.move(str(origin), str(hidden))  # --source now points nowhere

        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", first_sha, "--cache-dir", str(cache),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        try:
            rc, _out, err = self._run_main(argv)
        except SystemExit as exc:
            self.fail(f"offline apply must run (argparse refused: rc={exc.code})")
        self.assertEqual(
            rc, 0,
            f"offline apply with an exact-SHA ref and an integral cache must "
            f"succeed, stderr: {err}",
        )
        lock = read_lock(target)
        self.assertIsNotNone(lock)
        source = lock.get("source") or {}
        self.assertEqual(
            source.get("origin"), "cache", "offline fallback must be DECLARED in the lock"
        )
        self.assertEqual(source.get("commit_sha"), first_sha)
        self.assertEqual(
            (target / "scripts" / "z.py").read_bytes(),
            ORIGIN_Z_V1,
            "the integral cache bundle must be installable offline",
        )

    def test_offline_non_sha_ref_still_requires_origin(self):
        """Refs that are NOT exact SHAs still require a resolvable origin —
        documented limitation, loud refusal."""
        self.require_engine(main)
        origin, _first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", _git_ok(origin, "rev-parse", "HEAD").stdout.strip())
        hidden = self.tmp / "origin-repo-hidden"
        shutil.move(str(origin), str(hidden))
        lock_before = self._lock_bytes(target)

        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        rc, _out, err = self._run_main(argv)
        self.assertEqual(
            rc, 1,
            f"a non-SHA ref against a dead origin must refuse loudly, stderr: {err}",
        )
        self.assertEqual(self._lock_bytes(target), lock_before, "zero writes on refusal")


# ---------------------------------------------------------------------------
# TestCodeFormMarkers (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestCodeFormMarkers(WaveE2TestCase):
    def test_hash_form_markers_survive_merge_in_py(self):
        """A '# local_repo_data:TAG' block in .py survives a merge update —
        the code form must be recognized for code/config extensions."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        (target / "scripts" / "x.py").write_bytes(_hash_marked_x(ORIGIN_X_V1))

        pin = resolve_source(str(origin), "main")
        plan = plan_updates(target, load_bundle(pin, cache), read_lock(target))
        actions = {a.get("path"): a for a in plan.get("actions") or []}
        self.assertIn(
            "scripts/x.py",
            actions,
            f"hash-marked local adaptation must merge, not conflict, plan: "
            f"{json.dumps(plan, default=str)[:600]}",
        )
        self.assertEqual(
            actions["scripts/x.py"].get("op"), "merge",
            "the marker-preserving path is a merge action",
        )
        self.assertNotIn("scripts/x.py", json.dumps(plan.get("conflicts") or []))

        apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)  # return unused; merged bytes below are the assertion
        merged = (target / "scripts" / "x.py").read_bytes()
        self.assertIn(b"x-v2", merged, "upstream v2 content must be applied")
        self.assertIn(X_HASH_OPEN, merged, "hash-form opener must survive the merge")
        self.assertIn(X_HASH_BODY, merged, "hash-form payload must survive the merge")
        self.assertIn(X_HASH_CLOSE, merged, "hash-form closer must survive the merge")
        entry = self._lock_entry(target, "scripts/x.py")
        self.assertEqual(entry.get("installed_sha256"), _sha(merged))
        self.assertEqual(entry.get("base_sha256"), _sha(ORIGIN_X_V2))

    def test_hash_form_survives_second_update_fast_forward(self):
        """п.1 chain with code-form markers: merge at v2 keeps the hash
        block; the NEXT update (fast-forward branch) must keep it too."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        # Install v1, then adapt scripts/x.py with a hash-form block.
        pin1 = resolve_source(str(origin), first_sha)
        self.assertEqual(
            apply_updates(
                target,
                plan_updates(target, load_bundle(pin1, cache), read_lock(target)),
                ACTOR_ID,
                INSTALLATION_ID,
            ).get("status"),
            "completed",
        )
        (target / "scripts" / "x.py").write_bytes(_hash_marked_x(ORIGIN_X_V1))

        # First update (merge at v2): hash block preserved.
        pin2 = resolve_source(str(origin), "main")
        plan2 = plan_updates(target, load_bundle(pin2, cache), read_lock(target))
        apply_updates(target, plan2, ACTOR_ID, INSTALLATION_ID)
        merged_v2 = (target / "scripts" / "x.py").read_bytes()
        self.assertIn(b"x-v2", merged_v2)
        self.assertIn(X_HASH_OPEN, merged_v2, "hash block must survive the first update")

        # Second update (v3): fast-forward branch — block must survive AGAIN.
        _commit_tree(origin, _manifest_v3(), _origin_files_v3_e2(), "c3: upstream drift v3")
        pin3 = resolve_source(str(origin), "main")
        plan3 = plan_updates(target, load_bundle(pin3, cache), read_lock(target))
        actions = {a.get("path"): a for a in plan3.get("actions") or []}
        self.assertIn("scripts/x.py", actions, "second update must plan an action")
        self.assertEqual(
            actions["scripts/x.py"].get("op"), "merge",
            "marker-bearing fast-forward must be a merge (re-inject), not a plain update",
        )
        self.assertIn(
            "hotfix",
            [str(t) for t in actions["scripts/x.py"].get("preserved_blocks") or []],
            "the preserved tag list must name the code-form block tag",
        )
        apply_updates(target, plan3, ACTOR_ID, INSTALLATION_ID)
        merged_v3 = (target / "scripts" / "x.py").read_bytes()
        self.assertIn(b"x-v3", merged_v3, "upstream v3 content must be applied")
        self.assertIn(X_HASH_OPEN, merged_v3, "hash opener must survive the SECOND update")
        self.assertIn(X_HASH_BODY, merged_v3, "hash payload must survive the SECOND update")
        self.assertIn(X_HASH_CLOSE, merged_v3, "hash closer must survive the SECOND update")

    def test_unknown_extension_accepts_both_marker_forms(self):
        """For extensions outside both tables the engine accepts BOTH forms:
        an HTML-form and a hash-form block in one file both survive."""
        self.require_engine(read_lock, plan_updates, apply_updates)
        target = _make_target(self.tmp)
        (target / "docs" / "notes.txt").write_bytes(NOTES_LOCAL)
        _write_lock(
            target,
            [
                {"path": "scripts/x.py", "kind": "script", "sha256": _sha(ORIGIN_X_V1)},
                {"path": "skills/y/SKILL.md", "kind": "skill", "sha256": _sha(ORIGIN_Y_V1)},
                {"path": "docs/notes.txt", "kind": "doc", "sha256": _sha(NOTES_V1)},
            ],
        )
        manifest = _manifest_v1()
        manifest["components"].append({"path": "docs/notes.txt", "kind": "doc", "requires": []})
        bundle = {
            "manifest": manifest,
            "files": dict(_origin_files_v1(), **{"docs/notes.txt": NOTES_V2}),
            "base": {
                "scripts/x.py": ORIGIN_X_V1,
                "skills/y/SKILL.md": ORIGIN_Y_V1,
                "docs/notes.txt": NOTES_V1,
            },
        }
        plan = plan_updates(target, bundle, read_lock(target))
        actions = {a.get("path"): a for a in plan.get("actions") or []}
        self.assertIn(
            "docs/notes.txt",
            actions,
            f"both-forms file must merge, not conflict, plan: {json.dumps(plan, default=str)[:600]}",
        )
        preserved = [str(t) for t in actions["docs/notes.txt"].get("preserved_blocks") or []]
        self.assertIn("local-context", preserved, "HTML-form block must be preserved")
        self.assertIn("ops-flag", preserved, "hash-form block must be preserved")
        apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        merged = (target / "docs" / "notes.txt").read_bytes()
        self.assertIn(b"team notes v2", merged, "upstream content applied")
        self.assertIn(b"<!-- local_repo_data:local-context -->", merged)
        self.assertIn(b"LOCALE = eu", merged)
        self.assertIn(b"# local_repo_data:ops-flag", merged)
        self.assertIn(b"OPFLAG = on", merged)


# ---------------------------------------------------------------------------
# TestRuntimeLayout (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestRuntimeLayout(WaveE2TestCase):
    def test_skill_component_maps_to_agents_skills_when_present(self):
        """Repo WITH .agents/skills/: skills/<name>/SKILL.md is written to
        .agents/skills/<name>/SKILL.md (no duplicate at root); the lock v2
        'target' field records the resolved destination."""
        self.require_engine(main, read_lock, check_updates)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        (target / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)

        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--components", "skills/w/SKILL.md",
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        try:
            rc, _out, err = self._run_main(argv)
        except SystemExit as exc:
            self.fail(f"apply must run (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 0, f"subset apply must succeed, stderr: {err}")

        runtime = target / ".agents" / "skills" / "w" / "SKILL.md"
        self.assertTrue(
            runtime.is_file(),
            f"skill must be installed at the runtime layout path: {runtime}",
        )
        self.assertFalse(
            (target / "skills" / "w").exists(),
            "no duplicate at the distribution path when the runtime layout applies",
        )
        entry = self._lock_entry(target, "skills/w/SKILL.md")
        self.assertEqual(
            entry.get("target"),
            ".agents/skills/w/SKILL.md",
            "lock v2 'target' must record the resolved destination",
        )
        self.assertEqual(entry.get("installed_sha256"), _sha(ORIGIN_W_V2))

        check = check_updates(target, str(origin), "main", cache)
        self.assertNotIn(
            "skills/w/SKILL.md",
            check.get("drifted") or [],
            f"the layout-mapped component must not be diagnosed as drift, "
            f"check: {json.dumps(check, default=str)[:600]}",
        )

    def test_without_agents_skills_distribution_path_unchanged(self):
        """Repo WITHOUT .agents/skills/: the distribution path is used, as
        today."""
        self.require_engine(main, read_lock)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)  # no .agents/skills
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
            "--components", "skills/w/SKILL.md",
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        rc, _out, err = self._run_main(argv)
        self.assertEqual(rc, 0, f"subset apply must succeed, stderr: {err}")
        self.assertTrue((target / "skills" / "w" / "SKILL.md").is_file())
        entry = self._lock_entry(target, "skills/w/SKILL.md")
        self.assertEqual(entry.get("target"), "skills/w/SKILL.md")

    def test_recorded_target_honored_over_fresh_layout_rule(self):
        """A component already installed at a recorded destination stays
        there on later updates — creating .agents/skills/ mid-life does not
        migrate nor duplicate it."""
        self.require_engine(main, read_lock)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        base_argv = [
            "apply", "--repo-root", str(target),
            "--cache-dir", str(cache),
            "--components", "skills/w/SKILL.md",
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        # First install pins "main" (commit 2): skills/w/SKILL.md first
        # appears in the v2 manifest — a first_sha pin could never provide
        # the component (fixture completion of the interrupted RED edit).
        rc, _out, err = self._run_main(base_argv + ["--source", str(origin), "--ref", "main"])
        self.assertEqual(rc, 0, f"first install must succeed, stderr: {err}")
        root_copy = target / "skills" / "w" / "SKILL.md"
        self.assertTrue(root_copy.is_file())

        # The runtime layout appears AFTER installation.
        (target / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
        _commit_tree(origin, _manifest_v3(), _origin_files_v3_e2(), "c3: upstream w v3")

        rc, _out, err = self._run_main(base_argv + ["--source", str(origin), "--ref", "main"])
        self.assertEqual(rc, 0, f"re-update must succeed, stderr: {err}")
        self.assertEqual(
            root_copy.read_bytes(), ORIGIN_W_V3,
            "the recorded destination stays authoritative and is updated in place",
        )
        self.assertFalse(
            (target / ".agents" / "skills" / "w").exists(),
            "a layout change must not silently duplicate the component",
        )
        entry = self._lock_entry(target, "skills/w/SKILL.md")
        self.assertEqual(entry.get("target"), "skills/w/SKILL.md")


# ---------------------------------------------------------------------------
# TestPlanSummaryMode (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestPlanSummaryMode(WaveE2TestCase):
    def _plan_args(self, target: Path, origin: Path, cache: Path):
        return [
            "plan", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main", "--cache-dir", str(cache),
        ]

    def test_default_plan_output_is_summary_without_content(self):
        """CLI plan default output carries NO content blobs: every action is
        described by ops/paths/shas, not by base64 content."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        try:
            rc, out, err = self._run_main(self._plan_args(target, origin, cache))
        except SystemExit as exc:
            self.fail(f"plan must run (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 0, f"plan must succeed, stderr: {err}")
        plan = json.loads(out)
        actions = plan.get("actions") or []
        self.assertTrue(actions, "fixture sanity: plan must carry actions")
        for action in actions:
            self.assertNotIn(
                "content", action,
                f"summary mode must omit content bytes for {action.get('path')}",
            )
            self.assertNotIn(
                "content_b64", action,
                f"summary mode must omit base64 content for {action.get('path')}",
            )
        self.assertNotIn(
            "content_b64", out, "no base64 blobs anywhere in summary stdout"
        )
        # Decision-relevant keys survive the summarization.
        first = actions[0]
        self.assertIn("upstream_sha256", first)
        self.assertIn("expected_before_sha256", first)
        self.assertIn("pin", plan)

    def test_full_flag_restores_content_and_apply_roundtrip(self):
        """--full restores the machine-consumable plan: actions carry
        content_b64 and the file applies verbatim via --plan-file."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        try:
            rc, out, err = self._run_main(
                self._plan_args(target, origin, cache) + ["--full"]
            )
        except SystemExit as exc:
            self.fail(f"plan must accept --full (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 0, f"plan --full must succeed, stderr: {err}")
        plan = json.loads(out)
        self.assertTrue(
            any("content_b64" in a for a in plan.get("actions") or []),
            "--full must restore base64 content in actions",
        )
        plan_file = self.tmp / "approved-full-plan.json"
        plan_file.write_text(out, encoding="utf-8")
        rc, _out2, err2 = self._run_main([
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main",
            "--plan-file", str(plan_file),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ])
        self.assertEqual(rc, 0, f"apply of the full plan must succeed, stderr: {err2}")
        self.assertEqual(
            (target / "scripts" / "x.py").read_bytes(),
            ORIGIN_X_V2,
            "the full plan's content applies verbatim",
        )

    def test_contentless_plan_rematerializes_from_pinned_source(self):
        """A summary (content-less) plan file stays executable: apply
        re-materializes content bytes from the pinned source and hash-verifies
        them against the plan's upstream_sha256."""
        self.require_engine(main)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        rc, out, err = self._run_main(
            self._plan_args(target, origin, cache) + ["--full"]
        )
        self.assertEqual(rc, 0, f"fixture plan must succeed, stderr: {err}")
        plan = json.loads(out)
        for action in plan.get("actions") or []:
            action.pop("content_b64", None)
            action.pop("content", None)
        summary_file = self.tmp / "approved-summary-plan.json"
        summary_file.write_text(json.dumps(plan, indent=2), encoding="utf-8")

        rc, _out2, err2 = self._run_main([
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", "main",
            "--plan-file", str(summary_file),
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ])
        self.assertEqual(
            rc, 0,
            f"a content-less approved plan must apply via hash-verified "
            f"re-materialization from the pinned source, stderr: {err2}",
        )
        self.assertEqual((target / "scripts" / "x.py").read_bytes(), ORIGIN_X_V2)
        self.assertEqual((target / "scripts" / "z.py").read_bytes(), ORIGIN_Z_V1)


# ---------------------------------------------------------------------------
# TestShaMatchAdoption (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestShaMatchAdoption(WaveE2TestCase):
    def _fixture(self):
        """Target holding an ORPHAN copy of scripts/z.py whose bytes are
        hash-equal to the pinned upstream content (unknown origin: not
        lock-recorded)."""
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        (target / "scripts" / "z.py").write_bytes(ORIGIN_Z_V1)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        pin = resolve_source(str(origin), first_sha)
        bundle = load_bundle(pin, cache)
        return origin, target, cache, bundle, read_lock(target)

    def test_adopt_existing_converts_sha_equal_unknown_origin(self):
        """plan_updates(adopt_existing=True) turns the sha-equal unknown-origin
        file into an 'adopt' action; apply records the lock entry WITHOUT
        rewriting the file bytes."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        _origin, target, _cache, bundle, lock = self._fixture()
        z_before = (target / "scripts" / "z.py").read_bytes()

        plan = plan_updates(target, bundle, lock, adopt_existing=True)
        actions = {a.get("path"): a for a in plan.get("actions") or []}
        self.assertIn(
            "scripts/z.py", actions,
            f"sha-equal unknown-origin file must be adoptable, plan: "
            f"{json.dumps(plan, default=str)[:600]}",
        )
        self.assertEqual(actions["scripts/z.py"].get("op"), "adopt")
        self.assertNotIn("scripts/z.py", json.dumps(plan.get("conflicts") or []))
        self.assertEqual(
            actions["scripts/z.py"].get("expected_before_sha256"), _sha(ORIGIN_Z_V1)
        )

        apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        self.assertEqual(
            (target / "scripts" / "z.py").read_bytes(),
            z_before,
            "adoption must NOT rewrite the file bytes",
        )
        entry = self._lock_entry(target, "scripts/z.py")
        self.assertEqual(entry.get("installed_sha256"), _sha(ORIGIN_Z_V1))
        self.assertEqual(entry.get("base_sha256"), _sha(ORIGIN_Z_V1))
        self.assertEqual(entry.get("target"), "scripts/z.py")

    def test_without_flag_conflict_unchanged(self):
        """Without --adopt-existing the sha-equal unknown-origin file stays a
        conflict (today's semantics preserved)."""
        self.require_engine(read_lock, plan_updates)
        _origin, target, _cache, bundle, lock = self._fixture()
        plan = plan_updates(target, bundle, lock)
        conflicts = json.dumps(plan.get("conflicts") or [])
        self.assertIn("scripts/z.py", conflicts, "default must stay a conflict")
        for action in plan.get("actions") or []:
            self.assertNotEqual(
                action.get("op"), "adopt", "no adopt actions without the flag"
            )

    def test_cli_adopt_existing_end_to_end(self):
        """CLI apply --adopt-existing adopts the orphan copy: rc=0, bytes
        untouched, lock records the component."""
        self.require_engine(main, read_lock)
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        (target / "scripts" / "z.py").write_bytes(ORIGIN_Z_V1)
        cache = _make_cache_dir(self.tmp / "cache", first_sha)
        argv = [
            "apply", "--repo-root", str(target),
            "--source", str(origin), "--ref", first_sha, "--cache-dir", str(cache),
            "--components", "scripts/z.py",
            "--adopt-existing",
            "--installation", INSTALLATION_ID, "--actor", ACTOR_ID,
        ]
        try:
            rc, _out, err = self._run_main(argv)
        except SystemExit as exc:
            self.fail(f"apply must accept --adopt-existing (argparse refused: rc={exc.code})")
        self.assertEqual(rc, 0, f"adoption apply must succeed, stderr: {err}")
        self.assertEqual(
            (target / "scripts" / "z.py").read_bytes(),
            ORIGIN_Z_V1,
            "adoption must not rewrite file bytes",
        )
        entry = self._lock_entry(target, "scripts/z.py")
        self.assertEqual(entry.get("installed_sha256"), _sha(ORIGIN_Z_V1))


# ---------------------------------------------------------------------------
# TestManifestReadabilityFallback (from tests/test_dwave_e2.py)
# ---------------------------------------------------------------------------
class TestManifestReadabilityFallback(WaveE2TestCase):
    def _make_origin_no_root_manifest(self, tmp: Path) -> Path:
        """Origin repo whose release manifest lives ONLY at the canonical
        templates/release_manifest.json (no root manifest.json)."""
        origin = tmp / "origin-noroot"
        origin.mkdir(parents=True, exist_ok=True)
        _git_ok(origin, "init", "-q", "-b", "main")
        _git_ok(origin, "config", "user.email", "fixture@example.com")
        _git_ok(origin, "config", "user.name", "Fixture Origin")
        _git_ok(origin, "config", "commit.gpgsign", "false")
        (origin / "templates").mkdir(parents=True, exist_ok=True)
        (origin / "templates" / "release_manifest.json").write_text(
            json.dumps(_manifest_v1(), indent=2), encoding="utf-8"
        )
        for rel, data in _origin_files_v1().items():
            target = origin / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        _git_ok(origin, "add", "-A")
        _git_ok(origin, "commit", "-qm", "c1: manifest only at templates/")
        return origin

    def test_upstream_tree_without_root_manifest_falls_back(self):
        """A source revision without a root manifest.json is readable: the
        engine falls back to templates/release_manifest.json."""
        self.require_engine(resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin = self._make_origin_no_root_manifest(self.tmp)
        target = _make_target(self.tmp)
        self.assertFalse(
            (self.tmp / "origin-noroot" / "manifest.json").exists(),
            "fixture sanity: no root manifest in the source",
        )

        pin = resolve_source(str(origin), "main")
        bundle = load_bundle(pin, None)
        files = bundle.get("files") or {}
        self.assertEqual(files.get("scripts/x.py"), ORIGIN_X_V1)
        self.assertEqual(
            (bundle.get("manifest") or {}).get("framework_version"),
            "1.0.0-fix.1",
        )

        plan = plan_updates(target, bundle, read_lock(target))
        apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
        self.assertEqual((target / "scripts" / "z.py").read_bytes(), ORIGIN_Z_V1)

    def test_framework_repo_itself_as_source(self):
        """The framework repository layout (manifest at
        templates/release_manifest.json, no root manifest.json) is consumable
        as an update source; the updater is a first-class component."""
        self.require_engine(resolve_source, load_bundle)
        head_sha = _git_ok(REPO_ROOT, "rev-parse", "HEAD").stdout.strip()
        manifest_bytes = (REPO_ROOT / "templates" / "release_manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        component_paths = [
            str(c.get("path", "")).strip("/")
            for c in manifest.get("components") or []
            if isinstance(c, dict) and str(c.get("path", "")).strip("/")
        ]
        self.assertIn(
            "scripts/update_meta_project.py",
            component_paths,
            "fixture sanity: the canonical manifest registers the updater",
        )

        # Integral cache bundle built from the PINNED COMMIT's git blobs (not
        # the working tree: a worktree copy under the HEAD pin is a lying
        # cache whenever the tree carries uncommitted changes — SEC-2 refuses
        # lying caches). Laid out exactly as the source repo (manifest ONLY at
        # templates/release_manifest.json, no root manifest.json).
        cache = self.tmp / "fw-cache"
        bundle_root = cache / head_sha
        for rel in component_paths:
            blob = subprocess.run(
                ["git", "-C", str(REPO_ROOT), "cat-file", "blob", f"{head_sha}:{rel}"],
                capture_output=True,
                check=True,
            ).stdout
            dst = bundle_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(blob)
        self.assertFalse(
            (bundle_root / "manifest.json").exists(),
            "fixture sanity: no root manifest.json in the bundle",
        )

        pin = resolve_source(str(REPO_ROOT), head_sha)
        bundle = load_bundle(pin, cache)
        self.assertEqual(
            bundle.get("origin"), "cache",
            "the framework bundle must be consumable via the integral cache",
        )
        files = bundle.get("files") or {}
        self.assertIn("scripts/update_meta_project.py", files)
        pinned_updater = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "cat-file", "blob",
             f"{head_sha}:scripts/update_meta_project.py"],
            capture_output=True,
            check=True,
        ).stdout
        self.assertEqual(
            files.get("scripts/update_meta_project.py"),
            pinned_updater,
            "cache-served bytes must equal the PINNED commit's blob",
        )


# ---------------------------------------------------------------------------
# TestCrossPinOriginBaseFetch (from tests/test_dwave_d6b.py)
# ---------------------------------------------------------------------------
class TestCrossPinOriginBaseFetch(unittest.TestCase):
    def test_cross_pin_merge_base_fetched_from_origin_history(self):
        """v1 install (empty cache) -> marked local edit -> v2 update must
        MERGE (marker preserved), not refuse with needs_base."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            origin, sha1 = _make_origin_repo(tmp)
            sha2 = _git_ok(origin, "rev-parse", "HEAD").stdout.strip()

            empty_cache = tmp / "empty-cache"
            empty_cache.mkdir()
            target = tmp / "consumer"
            target.mkdir()
            _git_init(target)

            # --- first install: engine creates files + lock (pin = sha1) ---
            pin1 = resolve_source(str(origin), sha1)
            bundle1 = load_bundle(pin1, empty_cache)
            plan1 = plan_updates(target, bundle1, None)
            self.assertEqual(plan1["conflicts"], [])
            self.assertEqual(plan1["needs_base"], [])
            result1 = apply_updates(
                target, plan1, ACTOR_ID, INSTALLATION_ID, resolved_pin=pin1
            )
            self.assertEqual(result1["status"], "completed")
            installed = (target / "scripts" / "x.py").read_bytes()
            self.assertEqual(installed, ORIGIN_X_V1)
            lock1 = read_lock(target)
            self.assertEqual(
                lock1["source"]["commit_sha"], sha1, "lock must pin sha1"
            )

            # --- marked local adaptation (code-form marker, D7) ---
            x_path = target / "scripts" / "x.py"
            x_path.write_bytes(
                ORIGIN_X_V1
                + CODE_MARKER_OPEN
                + b"\n"
                + CODE_MARKER_BODY
                + b"\n"
                + CODE_MARKER_CLOSE
                + b"\n"
            )

            # --- second update: v1 -> v2, STILL an empty cache ---
            pin2 = resolve_source(str(origin), sha2)
            bundle2 = load_bundle(pin2, empty_cache)
            plan2 = plan_updates(target, bundle2, read_lock(target))

            needs = [e["path"] for e in plan2["needs_base"]]
            self.assertEqual(
                needs,
                [],
                f"cross-pin base must be fetched from origin history, got needs_base: {needs}",
            )
            merges = {
                a["path"]: a for a in plan2["actions"] if a.get("op") == "merge"
            }
            self.assertIn("scripts/x.py", merges, "x.py must be a merge action")

            result2 = apply_updates(
                target, plan2, ACTOR_ID, INSTALLATION_ID, resolved_pin=pin2
            )
            self.assertEqual(result2["status"], "completed")
            final = x_path.read_bytes()
            self.assertIn(ORIGIN_X_V2, final, "upstream v2 content applied")
            self.assertIn(
                CODE_MARKER_BODY, final, "marked adaptation preserved (auditor п.1/S1)"
            )


# ---------------------------------------------------------------------------
# TestCrlfWorkingCopyIsNotDrift (from tests/test_gwave_h.py)
# ---------------------------------------------------------------------------
class TestCrlfWorkingCopyIsNotDrift(unittest.TestCase):
    """A fresh autocrlf checkout smudges LF-installed files to CRLF; the
    engine must classify that as an installed match (with an explicit
    diagnostic), not as drift/conflict."""

    def _smudged_target(self, tmp: Path) -> Path:
        origin, first_sha = _make_origin_repo(tmp)
        target = tmp / "consumer"
        target.mkdir()
        _git_init(target)
        pin = resolve_source(str(origin), first_sha)
        bundle = load_bundle(pin, None)
        plan = plan_updates(target, bundle, None)
        self.assertEqual(plan["conflicts"], [])
        result = apply_updates(
            target, plan, ACTOR_ID, INSTALLATION_ID, resolved_pin=pin
        )
        self.assertEqual(result["status"], "completed")
        # Simulate the smudge: same content, CRLF endings on disk.
        x_path = target / "scripts" / "x.py"
        x_path.write_bytes(_crlf(x_path.read_bytes()))
        return target, origin, first_sha

    def test_check_reports_eol_normalized_not_drifted(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            target, origin, first_sha = self._smudged_target(tmp)
            result = check_updates(target, str(origin), first_sha, None)
            self.assertEqual(
                result["drifted"],
                [],
                "CRLF-smudged working copy must NOT be classified as drift",
            )
            self.assertEqual(result["status"], "up_to_date")
            eol_entries = [
                d
                for d in result["diagnostics"]
                if d.get("status") == "eol_normalized"
            ]
            self.assertTrue(
                eol_entries,
                "an explicit eol_normalized diagnostic must be emitted",
            )
            self.assertEqual(
                {e["path"] for e in eol_entries}, {"scripts/x.py"}
            )

    def test_plan_fast_forwards_crlf_copy_without_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            target, origin, first_sha = self._smudged_target(tmp)
            pin = resolve_source(str(origin), first_sha)
            bundle = load_bundle(pin, None)
            plan = plan_updates(target, bundle, read_lock(target))
            self.assertEqual(
                plan["conflicts"],
                [],
                "EOL-only difference must not surface as a conflict",
            )
            self.assertEqual(
                [e["path"] for e in plan["needs_base"]],
                [],
                "EOL-only difference must not surface as needs_base",
            )
            updates = [
                a
                for a in plan["actions"]
                if a["path"] == "scripts/x.py" and a.get("op") == "update"
            ]
            self.assertTrue(
                updates,
                "plan re-normalizes the smudged copy to the pinned LF bytes",
            )
            # TOCTOU anchor stays EXACT (raw working-tree bytes):
            self.assertEqual(
                updates[0]["expected_before_sha256"],
                _sha((target / "scripts" / "x.py").read_bytes()),
            )


# ---------------------------------------------------------------------------
# TestDeadSymbolsRemoved (from tests/test_gwave_h.py)
# ---------------------------------------------------------------------------
class TestDeadSymbolsRemoved(unittest.TestCase):
    """U4 (engine-scoped): BaseUnavailableError is never raised and
    _atomic_write_text is never called in the update engine. The audit's
    finding is scoped to scripts/update_meta_project.py — the same-named
    atomic writer in record_obs.py is that script's own LIVE writer and
    stays. The grep lock keeps the engine clean."""

    def test_engine_module_has_no_dead_symbols(self):
        source = (
            (REPO_ROOT / "scripts" / "update_meta_project.py")
            .read_text(encoding="utf-8")
        )
        self.assertNotIn("BaseUnavailableError", source)
        self.assertNotIn("_atomic_write_text", source)

    def test_base_unavailable_error_gone_from_scripts(self):
        for py in (REPO_ROOT / "scripts").glob("*.py"):
            text = py.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn(
                "BaseUnavailableError",
                text,
                f"{py.name} still references dead symbol BaseUnavailableError",
            )


# ---------------------------------------------------------------------------
# TestCheckHasNoDeadFullFlag (from tests/test_gwave_h.py)
# ---------------------------------------------------------------------------
class TestCheckHasNoDeadFullFlag(unittest.TestCase):
    """U10: the --full flag on check is dead (help admits it) — removed."""

    def test_check_rejects_full_flag(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            origin, first = _make_origin_repo(tmp)
            target = tmp / "consumer"
            target.mkdir()
            _git_init(target)
            proc = _run_cli(
                [
                    "check",
                    "--source",
                    str(origin),
                    "--ref",
                    first,
                    "--repo-root",
                    str(target),
                    "--full",
                ]
            )
            self.assertNotEqual(
                proc.returncode,
                0,
                "--full must no longer be an accepted check flag (rc != 0)",
            )


if __name__ == "__main__":
    unittest.main()
