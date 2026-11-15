#!/usr/bin/env python3
"""
Engine unit and adversarial test suite for scripts/update_meta_project.py
(Wave 0.9.0, Task C1 — RED phase).

Plan source: docs/superpowers/plans/2026-11-15-wave-0.9.0-update-engine-and-contracts.md
(Task C1 classifier verbatim; engine signatures from Task C2 Interfaces).

RED contract: until scripts/update_meta_project.py exists, every test in this
suite MUST fail with ``AssertionError: engine not implemented (RED)`` — the
suite never skips and never passes vacuously.

Fixture contracts pinned by this suite (Task C2 implementation must satisfy):
* Project lock lives at ``.agents/framework-lock.json`` (ADR #21, schema 1.0.0:
  {schema_version, source{repository, ref, commit_sha, origin, channel},
  components[{path, kind, sha256}], installed_at}).
* Cache layout: ``<cache_dir>/<commit_sha>/`` holds the INTEGRAL bundle tree
  (manifest.json + every manifest component file) of exactly that commit.
* Plan/Check/Apply/Restore results are dict-like mapping collections exposing
  the keys named in the plan Interfaces (``obj["key"]`` or attribute access);
  PlanResult = {actions, conflicts, protected, needs_base}.
* Bundle = {manifest, files: {path: bytes}, base: {path: bytes}}; load_bundle
  refuses a partial cache loudly (exception) and never mixes revisions.
* Apply journal: ``.agents/update-journal.json``; update reports are stored
  through scripts/manage_reports.save_report under
  ``.agents/reports/<installation_id>/update/``.
* CLI ``main(argv)`` supports subcommands check|plan|apply|restore with the
  plan flags --source --ref --cache-dir --components --protect, plus
  --repo-root, --installation and --actor (the target repository and identity
  inputs implied by the apply_updates signature; the Interfaces flag list is
  not exhaustive on these).

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.manage_reports import validate_report  # real module (gains the 'update' branch in Task C3)

try:
    from scripts.update_meta_project import (
        apply_updates,
        check_updates,
        load_bundle,
        main,
        plan_updates,
        read_lock,
        resolve_source,
        restore_updates,
        write_lock_atomic,
    )
except ImportError:
    # Allow the suite to run in RED phase before the engine is implemented.
    apply_updates = None
    check_updates = None
    load_bundle = None
    main = None
    plan_updates = None
    read_lock = None
    resolve_source = None
    restore_updates = None
    write_lock_atomic = None

# ---------------------------------------------------------------------------
# Fixture constants (origin component bytes, two-commit history)
# ---------------------------------------------------------------------------

PROJECT_ID = "fixture-app/alpha"
INSTALLATION_ID = "ag-main"
HARNESS_ID = "antigravity"
ACTOR_ID = "fixture-app/alpha::antigravity::ag-main::agent-dev-lead"

ORIGIN_X_V1 = b'"""Component X v1 (origin commit 1)."""\nVALUE_X = "x-v1"\n'
ORIGIN_X_V2 = b'"""Component X v2 (origin commit 2)."""\nVALUE_X = "x-v2"\n'
ORIGIN_X_V3 = (
    b'"""Component X v3 (origin commit 3, committed AFTER resolve_source)."""\n'
    b'VALUE_X = "x-v3"\n'
)
ORIGIN_Z_V1 = b'"""Component Z v1 (origin commit 1)."""\nVALUE_Z = "z-v1"\n'
ORIGIN_Y_V1 = b"# Skill Y v1\n\nPhase 1: do v1 things (Y-V1-UPSTREAM).\n"
ORIGIN_Y_V2 = b"# Skill Y v2\n\nPhase 1: do v2 things (Y-V2-UPSTREAM).\n"
ORIGIN_W_V2 = b"# Skill W v2\n\nBrand-new upstream component (W-V2-UPSTREAM).\n"

MARKER_OPEN = b"<!-- local_repo_data:team-conventions -->"
MARKER_CLOSE = b"<!-- /local_repo_data:team-conventions -->"
MARKER_BODY = b"TEAM RULE: every test stays stdlib-only."

X_GHOST_BASE = b'"""Ghost base content (hash recorded in lock, bytes available nowhere)."""\n'
X_GHOST_LOCAL = X_GHOST_BASE + b"# local edit on top of a missing base\n"

MINIMAL_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Red Zone (Prohibited Without Direct User Confirmation)
- `*boundaries.md`
- `LICENSE`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""

# Engine-owned metadata paths excluded from tree-content comparisons around
# apply/restore (restore must revert ENGINE FILE changes; journal/report/lock
# bookkeeping and .git internals are not working-tree content).
_ENGINE_METADATA_PREFIXES = (
    ".git/",
    ".agents/update-journal.json",
    ".agents/reports/",
    ".agents/framework-lock.json",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_v1() -> dict:
    return {
        "schema_version": "1.0.0",
        "framework_version": "1.0.0-fix.1",
        "channel": "preview",
        "components": [
            {"path": "scripts/x.py", "kind": "script", "requires": []},
            {"path": "scripts/z.py", "kind": "script", "requires": []},
            {"path": "skills/y/SKILL.md", "kind": "skill", "requires": []},
        ],
        "migrations": [],
    }


def _manifest_v2() -> dict:
    manifest = _manifest_v1()
    manifest["framework_version"] = "1.0.0-fix.2"
    manifest["components"].append(
        {"path": "skills/w/SKILL.md", "kind": "skill", "requires": []}
    )
    return manifest


def _origin_files_v1() -> dict[str, bytes]:
    return {
        "scripts/x.py": ORIGIN_X_V1,
        "scripts/z.py": ORIGIN_Z_V1,
        "skills/y/SKILL.md": ORIGIN_Y_V1,
    }


def _origin_files_v2() -> dict[str, bytes]:
    files = _origin_files_v1()
    files["scripts/x.py"] = ORIGIN_X_V2
    files["skills/y/SKILL.md"] = ORIGIN_Y_V2
    files["skills/w/SKILL.md"] = ORIGIN_W_V2
    return files


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def _git_ok(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    res = _git(cwd, *args)
    assert res.returncode == 0, f"git {' '.join(args)} failed: {res.stderr}"
    return res


def _write_tree(root: Path, manifest: dict, files: dict[str, bytes]) -> None:
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


# ---------------------------------------------------------------------------
# Fixture builders (Task C1 Interfaces: temp-dir origin/cache/target)
# ---------------------------------------------------------------------------


def _make_origin_repo(tmp: Path) -> tuple[Path, str]:
    """Origin 'upstream' repository with manifest + component files and TWO
    commits:

    * commit 1 ("component set v1"): manifest v1 + x.py(X_V1) + z.py(Z_V1)
      + skills/y/SKILL.md(Y_V1)
    * commit 2 ("upstream drift v2"): x.py -> X_V2, y/SKILL.md -> Y_V2,
      adds skills/w/SKILL.md(W_V2), manifest v2

    Returns (origin_path, first_commit_sha). HEAD is commit 2, so resolving
    ref "main" yields commit 2 while the FIRST sha stays available for
    explicit-SHA pinning and integral-cache fixtures.
    """
    origin = tmp / "origin-repo"
    origin.mkdir(parents=True, exist_ok=True)
    _git_ok(origin, "init", "-q", "-b", "main")
    _git_ok(origin, "config", "user.email", "fixture@example.com")
    _git_ok(origin, "config", "user.name", "Fixture Origin")
    _git_ok(origin, "config", "commit.gpgsign", "false")

    _write_tree(origin, _manifest_v1(), _origin_files_v1())
    _git_ok(origin, "add", "-A")
    _git_ok(origin, "commit", "-qm", "c1: component set v1")
    first_sha = _git_ok(origin, "rev-parse", "HEAD").stdout.strip()

    _write_tree(origin, _manifest_v2(), _origin_files_v2())
    _git_ok(origin, "add", "-A")
    _git_ok(origin, "commit", "-qm", "c2: upstream drift v2")
    return origin, first_sha


def _make_cache_dir(parent: Path, origin_sha: str) -> Path:
    """Integral cache: a full copy of the FIRST sha's component set laid out
    as ``<cache_dir>/<commit_sha>/`` (manifest + all component files)."""
    bundle_root = parent / origin_sha
    bundle_root.mkdir(parents=True, exist_ok=True)
    _write_tree(bundle_root, _manifest_v1(), _origin_files_v1())
    return parent


def _write_lock(target: Path, components: list[dict]) -> None:
    lock = {
        "schema_version": "1.0.0",
        "source": {
            "repository": "https://example.invalid/fixture/origin",
            "ref": "main",
            "commit_sha": "0" * 40,
            "origin": "upstream",
            "channel": "preview",
        },
        "components": components,
        "installed_at": "2026-11-15T00:00:00Z",
    }
    (target / ".agents" / "framework-lock.json").write_text(
        json.dumps(lock, indent=2), encoding="utf-8"
    )


def _make_target(tmp: Path) -> Path:
    """Target project: minimal scaffold + lock v1.

    Installed SUBSET of the origin v1 set (manifest != lock): scripts/x.py and
    skills/y/SKILL.md are installed (lock-recorded sha256s of the v1 bytes);
    scripts/z.py is NOT installed. Includes the protected knowledge slice
    (``.agents/project_knowledge/boundaries.md``), the identity registry, and
    user files outside the managed set.
    """
    target = tmp / "target-app"
    (target / ".agents" / "project_knowledge").mkdir(parents=True, exist_ok=True)
    (target / "scripts").mkdir(parents=True, exist_ok=True)
    (target / "skills" / "y").mkdir(parents=True, exist_ok=True)
    (target / "docs").mkdir(parents=True, exist_ok=True)

    (target / ".agents" / "project_knowledge" / "boundaries.md").write_text(
        MINIMAL_BOUNDARIES, encoding="utf-8"
    )
    (target / ".agents" / "project_knowledge" / "observations.md").write_text(
        "# Observations\n\nOBS-1: fixture observation (user data).\n", encoding="utf-8"
    )
    registry = {
        "schema_version": "1.1.0",
        "project_id": PROJECT_ID,
        "installations": {
            INSTALLATION_ID: {
                "harness_id": HARNESS_ID,
                "status": "active",
                "description": "fixture installation",
            }
        },
        "roles": {
            "agent-dev-lead": {
                "description": "fixture role",
                "bindings": {
                    INSTALLATION_ID: {
                        "actor_id": ACTOR_ID,
                        "status": "active",
                        "profile_path": ".agents/team/agent-dev-lead/profile.md",
                    }
                },
            }
        },
    }
    (target / ".agents" / "meta-project.json").write_text(
        json.dumps(registry, indent=2), encoding="utf-8"
    )
    (target / "scripts" / "x.py").write_bytes(ORIGIN_X_V1)
    (target / "skills" / "y" / "SKILL.md").write_bytes(ORIGIN_Y_V1)
    (target / "docs" / "user-notes.md").write_bytes(b"USER NOTE v1\n")
    _write_lock(
        target,
        [
            {"path": "scripts/x.py", "kind": "script", "sha256": _sha(ORIGIN_X_V1)},
            {"path": "skills/y/SKILL.md", "kind": "skill", "sha256": _sha(ORIGIN_Y_V1)},
        ],
    )

    _git_ok(target, "init", "-q", "-b", "main")
    _git_ok(target, "config", "user.email", "fixture@example.com")
    _git_ok(target, "config", "user.name", "Fixture Target")
    _git_ok(target, "config", "commit.gpgsign", "false")
    _git_ok(target, "add", "-A")
    _git_ok(target, "commit", "-qm", "target scaffold")
    return target


# ---------------------------------------------------------------------------
# Result-shape tolerant accessors and tree snapshots
# ---------------------------------------------------------------------------


def _get(obj, key, default=None):
    """Read ``key`` from a dict-like or attribute-style engine result."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _dump(obj) -> str:
    """Serialize any engine result to inspectable text."""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except TypeError:
        return str(obj)


def _bundle_files(bundle) -> dict:
    files = _get(bundle, "files")
    if not isinstance(files, dict):
        raise AssertionError(f"bundle['files'] must be a path->bytes mapping, got: {type(files)}")
    return files


def _write_fingerprint(root: Path) -> dict:
    """Zero-write snapshot: relative path -> (size, mtime_ns). Strictest form:
    even a metadata-only touch (mtime) counts as a write."""
    snap = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".git/"):
            continue
        if path.is_file():
            stat = path.stat()
            snap[rel] = (stat.st_size, stat.st_mtime_ns)
    return snap


def _content_fingerprint(root: Path, exclude_prefixes=_ENGINE_METADATA_PREFIXES) -> dict:
    """Content snapshot: relative path -> sha256 (engine metadata excluded)."""
    snap = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(exclude_prefixes):
            continue
        if path.is_file():
            snap[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snap


@contextlib.contextmanager
def _chdir(path: Path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


# ---------------------------------------------------------------------------
# Base test case
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
# Task C1 classifier: test classes and cases
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
        components = {_get(c, "path"): _get(c, "sha256") for c in (_get(lock, "components") or [])}
        self.assertEqual(components.get("scripts/z.py"), _sha(ORIGIN_Z_V1))

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
            "restore must return the working tree to the pre-apply state",
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
        components = {_get(c, "path"): _get(c, "sha256") for c in (_get(lock, "components") or [])}
        self.assertEqual(
            set(components),
            {"scripts/x.py", "skills/y/SKILL.md"},
            "lock must record exactly the installed subset",
        )
        self.assertEqual(components["scripts/x.py"], _sha(ORIGIN_X_V2))
        self.assertEqual(components["skills/y/SKILL.md"], _sha(ORIGIN_Y_V1))
        # Recorded hashes match the bytes actually on disk.
        self.assertEqual(
            components["scripts/x.py"],
            hashlib.sha256((target / "scripts" / "x.py").read_bytes()).hexdigest(),
        )
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


if __name__ == "__main__":
    unittest.main()
