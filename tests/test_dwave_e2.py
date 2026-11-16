#!/usr/bin/env python3
"""
Wave D, Lane E2 — Engine Perimeter & UX (RED phase contract tests).

Plan source: docs/superpowers/plans/2026-11-15-wave-d-state-integrity-and-perimeter.md (§8).

Closes auditor п.5 (T6.1 identity admission, T6.2 project boundaries consult
+ --protect wiring), D2 (T6.3 offline cache via CLI with exact-SHA refs),
D7 (T6.4 code-form markers), the skills runtime-layout mismatch (T6.5),
friction (4) plan stdout summary mode (T6.6), friction (5) sha-match
adoption (T6.7), and the manifest readability fallback (T6.8).

RED contract: the named per-task tests must fail against the post-E1 engine
and go GREEN after the E2 implementation. Never edited to pass; a
contradiction is reported, not patched.

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
    HARNESS_ID,
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
    _git_ok,
    _make_cache_dir,
    _make_origin_repo,
    _make_target,
    _manifest_v1,
    _manifest_v2,
    _origin_files_v1,
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

# ---------------------------------------------------------------------------
# Fixture constants
# ---------------------------------------------------------------------------

LOCK_RELPATH = ".agents/framework-lock.json"

STRANGER_ACTOR = "fixture-app/alpha::antigravity::ag-main::agent-intruder"

# T6.2: project boundaries that put scripts/x.py into the Red Zone (the
# shared fixture's MINIMAL_BOUNDARIES does NOT protect scripts/x.py).
BOUNDARIES_WITH_X_RED = """# Responsibility Zones and Change Boundaries

## Red Zone (Prohibited Without Direct User Confirmation)
- `scripts/x.py`
- `*boundaries.md`
- `LICENSE`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""

# T6.4: code-form (hash-comment) local_repo_data markers for .py-style files.
X_HASH_OPEN = b"# local_repo_data:hotfix"
X_HASH_CLOSE = b"# /local_repo_data:hotfix"
X_HASH_BODY = b"HOTFIX_VALUE = 'local-1'"


def _hash_marked_x(base: bytes) -> bytes:
    """Installed content of scripts/x.py carrying one local adaptation
    wrapped in hash-form local_repo_data markers (D7 code form)."""
    return base + b"\n" + X_HASH_OPEN + b"\n" + X_HASH_BODY + b"\n" + X_HASH_CLOSE + b"\n"


# T6.4: unknown-extension file carrying BOTH marker forms.
NOTES_V1 = b"team notes v1\n"
NOTES_V2 = b"team notes v2 (upstream edit)\n"
NOTES_LOCAL = (
    NOTES_V1
    + b"\n<!-- local_repo_data:local-context -->\nLOCALE = eu\n<!-- /local_repo_data:local-context -->\n"
    + b"# local_repo_data:ops-flag\nOPFLAG = on\n# /local_repo_data:ops-flag\n"
)

# T6.5: a THIRD upstream revision of skills/w/SKILL.md; T6.4: a THIRD
# upstream revision of scripts/x.py (the fixture completion wiring for the
# already-imported ORIGIN_X_V3 — without it the v3 commit leaves x.py at v2
# bytes that no engine could ever turn into x-v3 content).
ORIGIN_W_V3 = b"# Skill W v3\n\nW-V3-UPSTREAM content.\n"


def _manifest_v3() -> dict:
    manifest = _manifest_v2()
    manifest["framework_version"] = "1.0.0-fix.3"
    return manifest


def _origin_files_v3() -> dict:
    files = _origin_files_v2()
    files["skills/w/SKILL.md"] = ORIGIN_W_V3
    files["scripts/x.py"] = ORIGIN_X_V3
    return files


def _commit_tree(origin: Path, manifest: dict, files: dict, message: str) -> None:
    _write_tree(origin, manifest, files)
    _git_ok(origin, "add", "-A")
    _git_ok(origin, "commit", "-qm", message)


# ---------------------------------------------------------------------------
# Base test case
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
# T6.1 — Identity admission (auditor п.5a)
# ---------------------------------------------------------------------------


class TestIdentityAdmission(WaveE2TestCase):
    def test_apply_refuses_unregistered_actor_zero_writes(self):
        """apply with an actor that is not admitted by the project registry
        must raise ApplyError('actor not admitted ...') with ZERO writes."""
        self.require_engine(ApplyError, resolve_source, load_bundle, read_lock, plan_updates, apply_updates)
        origin, _first = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache = _make_cache_dir(self.tmp / "cache", _git_ok(origin, "rev-parse", "HEAD").stdout.strip())
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
# T6.2 — Project boundaries consult + --protect wiring (auditor п.5b/c)
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
# T6.3 — Offline cache via CLI with exact-SHA refs (D2)
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
# T6.4 — Code-form markers (D7)
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

        result = apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)
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
        _commit_tree(origin, _manifest_v3(), _origin_files_v3(), "c3: upstream drift v3")
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
# T6.5 — Runtime-layout target mapping (layout mismatch)
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
        _commit_tree(origin, _manifest_v3(), _origin_files_v3(), "c3: upstream w v3")

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
# T6.6 — Plan summary mode (friction 4)
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
# T6.7 — Sha-match adoption (friction 5)
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
# T6.8 — Manifest readability fallback
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

        # Integral cache bundle built from the framework WORKING TREE at the
        # HEAD pin — laid out exactly as the source repo (manifest ONLY at
        # templates/release_manifest.json, no root manifest.json).
        cache = self.tmp / "fw-cache"
        bundle_root = cache / head_sha
        for rel in component_paths:
            src = REPO_ROOT / rel
            self.assertTrue(src.is_file(), f"fixture component missing: {rel}")
            dst = bundle_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
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
        self.assertEqual(
            files.get("scripts/update_meta_project.py"),
            (REPO_ROOT / "scripts" / "update_meta_project.py").read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
