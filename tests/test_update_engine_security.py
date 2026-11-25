#!/usr/bin/env python3
"""
Wave F Lane FX — adversarial security-perimeter suite for the managed update
engine ``scripts/update_meta_project.py`` (RED-first discipline).

Plan source: docs/superpowers/plans/2026-11-16-wave-f-security-perimeter.md §3.

Every guard test reproduces the ATTACK first and only then pins the refusal:

* SEC-1 (T-X1) containment, 3 layers — hostile manifest component paths
  (``../`` traversal, drive-absolute ``C:/evil``, UNC ``//server/share``),
  junction/symlink destinations, hostile restore-journal paths, and hostile
  cache-bundle paths must be REFUSED with ZERO writes (no journal, no file
  created outside the repository root, no exfiltrated bytes).
* SEC-2 (T-X2) cache verification — ``<sha>/cache-manifest.json`` (component
  files + manifest.json + the ref-pin) is verified on every cache load;
  tampered cache bytes are refused online (origin cross-check) and offline
  (manifest hash mismatch); a cache sealed for pin A is refused for pin B;
  unsealed caches are cross-verified against reachable origins and sealed at
  apply/load time.
* SEC-4 (T-X3) serialization — apply AND restore hold a per-repository file
  lock; a concurrent second engine operation is refused with an ENGINE_BUSY
  envelope and the journal stays untouched.
* U6 (T-X4) — ``check`` resolves its source pin through the SAME
  cache-fallback resolution as plan/apply (one answer per repo state).
* U7+U11 (T-X5) — the update report's ``versions.after`` is split into
  ``framework_version`` + ``commit_sha``; ``restore`` marks the update report
  ``status: "restored"`` (audit trail preserved).
* U8 (T-X6) — ``check`` JSON gains ``check_status: "ok" | "failed"``; the rc
  contract is UNCHANGED (rc 0 up-to-date, rc 1 updates/drift/failure).
* T-X7 — ``_atomic_write_bytes`` fsyncs the temp file before ``os.replace``
  (durability, no behavior change).

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import io
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

from scripts.manage_reports import validate_report
from scripts.update_meta_project import (
    _atomic_write_bytes,
    UpdateEngineError,
    apply_updates,
    load_bundle,
    main,
    plan_updates,
    read_lock,
    resolve_pin_with_cache_fallback,
    restore_updates,
)
from tests._git_fixtures import (
    ACTOR_ID,
    INSTALLATION_ID,
    ORIGIN_X_V1,
    ORIGIN_X_V2,
    ORIGIN_Y_V1,
    ORIGIN_Z_V1,
    _git_ok,
    _make_origin_repo,
    _make_target,
    _manifest_v1,
    _origin_files_v1,
    _origin_files_v2,
    _seal_bundle_dir,
    _sha,
    _write_tree,
)


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

EVIL_BYTES = b"ATTACKER-CONTROLLED-PAYLOAD (never inside the repo)\n"
SECRET_BYTES = b"TOP-SECRET-OUTSIDE-THE-REPO (exfil canary)\n"
ENGINE_LOCK_RELPATH = ".agents/update-engine.lock"
JOURNAL_RELPATH = ".agents/update-journal.json"


def _run_main(argv: list) -> tuple:
    """In-process CLI run; returns (rc, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def _run_cli(argv: list) -> tuple:
    """Real subprocess CLI run (real parallelism for SEC-4)."""
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "update_meta_project.py"), *argv],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=180,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _write_bundle(bundle_root: Path, manifest: dict, files: dict) -> None:
    _write_tree(bundle_root, manifest, files)


def _write_cache(
    cache_root: Path,
    dir_name: str,
    manifest: dict,
    files: dict,
    seal_for: "str | None" = None,
    ref: str = "",
) -> Path:
    """Build a cache entry ``<cache_root>/<dir_name>/`` (optionally sealed for
    ``seal_for`` — deliberately decoupled from the directory name so the
    cross-pin attack can be reproduced)."""
    bundle_root = cache_root / dir_name
    bundle_root.mkdir(parents=True, exist_ok=True)
    _write_bundle(bundle_root, manifest, files)
    if seal_for is not None:
        _seal_bundle_dir(bundle_root, seal_for, ref)
    return bundle_root


def _write_journal(target: Path, entries: list, status: str = "completed") -> None:
    journal = {
        "schema_version": "1.0.0",
        "run_id": "fx-hostile-run",
        "actor_id": ACTOR_ID,
        "installation_id": INSTALLATION_ID,
        "status": status,
        "started_at": "2026-11-16T00:00:00Z",
        "entries": entries,
    }
    path = target / JOURNAL_RELPATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")


def _repo_files(root: Path) -> dict:
    """relpath -> sha256 snapshot of every file (except .git internals)."""
    snap = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".git/") or not path.is_file():
            continue
        snap[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snap


def _make_dir_link(link: Path, pointee: Path) -> None:
    """Directory link: junction on Windows (no privilege needed), symlink
    elsewhere."""
    if sys.platform == "win32":
        import _winapi  # stdlib on Windows

        _winapi.CreateJunction(str(pointee), str(link))
    else:
        os.symlink(str(pointee), str(link), target_is_directory=True)


def _lock_engine(target: Path):
    """Acquire the engine operation lock WITHOUT engine helpers (the RED
    phase has no file_lock to import yet); returns the open handle."""
    lock_path = target / ENGINE_LOCK_RELPATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "a+b")
    fd = handle.fileno()
    if sys.platform == "win32":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return handle


def _unlock_engine(handle) -> None:
    fd = handle.fileno()
    try:
        handle.seek(0)
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        handle.close()


class FxWaveTestCase(unittest.TestCase):
    """Temp-dir fixture with automatic cleanup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="fwave_x_")
        self.tmp = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def latest_update_report(self, target: Path) -> dict:
        report_dir = target / ".agents" / "reports" / INSTALLATION_ID / "update"
        self.assertTrue(report_dir.is_dir(), f"update report dir missing: {report_dir}")
        candidates = [
            p for p in sorted(report_dir.glob("*.json")) if p.name != "latest.json"
        ]
        self.assertTrue(candidates, f"no update report found in {report_dir}")
        return json.loads(candidates[-1].read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# T-X1 — SEC-1: containment guard (3 layers)
# ---------------------------------------------------------------------------


class TestSEC1Traversal(FxWaveTestCase):
    """Hostile manifest component paths must never reach the disk outside the
    repository root; plan/apply/cache/restore all refuse with ZERO writes."""

    def _traversal_fixture(self) -> tuple:
        """Layout engineered so the hostile component resolves to DIFFERENT
        escape targets on read vs write:

        * cache bundle at ``<tmp>/a/cache/<sha>/`` — the hostile component
          ``../../evil`` reads ``<tmp>/a/evil`` (must exist for the bundle to
          look integral), and
        * the target repo at ``<tmp>/target-app`` — the same component
          resolves the WRITE to ``<tmp>/evil`` (outside the repo, absent).

        The origin is moved away AFTER the pin sha is captured: ``--source``
        keeps pointing at the now-dead path, so only the cache can answer.
        The repo is nested one level deeper (``<tmp>/nest/target-app``) so the
        two-segment ``../..`` escape lands at ``<tmp>/evil`` — inside the
        auto-cleaned fixture directory, outside the repository root.
        """
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp / "nest")
        nested = self.tmp / "a" / "cache"
        hostile_manifest = _manifest_v1()
        hostile_manifest["components"].append(
            {"path": "../../evil", "kind": "script", "requires": []}
        )
        outside_of_cache = self.tmp / "a" / "evil"
        outside_of_cache.parent.mkdir(parents=True, exist_ok=True)
        outside_of_cache.write_bytes(EVIL_BYTES)
        bundle_files = dict(_origin_files_v1())
        _write_cache(nested, first_sha, hostile_manifest, bundle_files)
        dead_source = str(origin)
        hidden = self.tmp / "origin-repo-hidden"
        shutil.move(str(origin), str(hidden))  # origin dead: pin via exact SHA
        return target, dead_source, first_sha, outside_of_cache

    def test_traversal_component_apply_refused_zero_writes(self):
        target, dead_source, first_sha, _outside_of_cache = self._traversal_fixture()
        escape_target = self.tmp / "evil"  # target-app/../../evil
        cache = self.tmp / "a" / "cache"
        before = _repo_files(target)

        rc, _out, err = _run_main([
            "apply",
            "--repo-root", str(target),
            "--source", dead_source,
            "--ref", first_sha,
            "--cache-dir", str(cache),
            "--installation", INSTALLATION_ID,
            "--actor", ACTOR_ID,
        ])

        self.assertFalse(
            escape_target.exists(),
            f"SEC-1 RED: apply wrote '{escape_target}' OUTSIDE the repository "
            f"root — the hostile '../../evil' manifest component was not "
            f"contained (rc={rc}, stderr={err!r})",
        )
        self.assertEqual(rc, 1, f"apply must refuse a hostile path, stderr: {err}")
        self.assertFalse(
            (target / JOURNAL_RELPATH).exists(),
            "SEC-1: hostile plan must be refused with ZERO writes (no journal)",
        )
        self.assertEqual(
            _repo_files(target),
            before,
            "SEC-1: the repository tree must be untouched by the refused apply",
        )

    def test_traversal_component_plan_refused(self):
        target, dead_source, first_sha, _outside_of_cache = self._traversal_fixture()
        cache = self.tmp / "a" / "cache"
        before = _repo_files(target)

        rc, out, err = _run_main([
            "plan",
            "--repo-root", str(target),
            "--source", dead_source,
            "--ref", first_sha,
            "--cache-dir", str(cache),
        ])

        self.assertEqual(rc, 1, f"plan must refuse a hostile path, stderr: {err}")
        self.assertNotIn(
            "../../evil", out, "plan output must not carry the hostile component"
        )
        self.assertEqual(_repo_files(target), before, "plan must stay zero-write")

    def test_cache_read_of_hostile_component_refused(self):
        target, dead_source, first_sha, outside_of_cache = self._traversal_fixture()
        cache = self.tmp / "a" / "cache"

        served = None
        try:
            bundle = load_bundle(
                resolve_pin_with_cache_fallback(dead_source, first_sha, cache),
                cache,
            )
            served = sorted((bundle.get("files") or {}).keys())
        except UpdateEngineError:
            pass
        self.assertIsNone(
            served,
            f"SEC-1 RED: the engine READ a hostile cache component and served "
            f"paths {served} — '../..' escaped the cache directory "
            f"(read source: {outside_of_cache})",
        )
        self.assertTrue(
            outside_of_cache.is_file(),
            "the out-of-cache canary file itself must stay untouched",
        )

    def test_restore_hostile_journal_path_refused(self):
        target = _make_target(self.tmp)
        escape_target = self.tmp / "evil"  # target-app/../../evil
        escape_target.write_bytes(EVIL_BYTES)
        _write_journal(target, [{
            "path": "../../evil",
            "op": "update",
            "kind": "script",
            "before_sha256": None,
            "after_sha256": _sha(EVIL_BYTES),
            "before_b64": None,
            "after_b64": base64.b64encode(EVIL_BYTES).decode("ascii"),
            "status": "applied",
        }])
        journal_before = (target / JOURNAL_RELPATH).read_bytes()

        refused = False
        try:
            restore_updates(target)
        except UpdateEngineError:
            refused = True
        self.assertTrue(
            refused,
            "SEC-1 RED: restore followed a hostile journal path outside the "
            "repository root instead of refusing it",
        )
        self.assertTrue(
            escape_target.is_file(),
            "SEC-1 RED: restore DELETED a file outside the repository root "
            "(the hostile journal entry was executed)",
        )
        self.assertEqual(
            (target / JOURNAL_RELPATH).read_bytes(),
            journal_before,
            "a refused restore must not rewrite the journal",
        )


class TestSEC1AbsoluteAndUNC(FxWaveTestCase):
    """Drive-absolute (``C:/evil``) and UNC (``//server/share``) component
    paths must be refused at plan AND apply — zero writes, no journal."""

    def _craft_plan(self, hostile_rel: str) -> dict:
        content = b"pwned"
        return {
            "pin": {"source": "adversarial", "commit_sha": "0" * 40, "ref": "main"},
            "meta": {},
            "actions": [{
                "path": hostile_rel,
                "op": "create",
                "kind": "script",
                "target": hostile_rel,
                "content": content,
                "upstream_sha256": _sha(content),
                "expected_before_sha256": None,
            }],
            "conflicts": [],
            "protected": [],
            "needs_base": [],
            "up_to_date": [],
        }

    def _assert_plan_refuses(self, hostile_rel: str) -> None:
        target = _make_target(self.tmp)
        manifest = _manifest_v1()
        manifest["components"].append(
            {"path": hostile_rel, "kind": "script", "requires": []}
        )
        bundle = {
            "manifest": manifest,
            "files": dict(_origin_files_v1(), **{hostile_rel: b"pwned"}),
            "base": {},
        }
        with self.assertRaises(UpdateEngineError) as ctx:
            plan_updates(target, bundle, read_lock(target))
        return ctx

    def test_drive_absolute_plan_refused(self):
        self._assert_plan_refuses("C:/evil")

    def test_unc_plan_refused(self):
        self._assert_plan_refuses("//server/share")

    def _assert_apply_zero_writes(self, hostile_rel: str, outside: Path) -> None:
        target = _make_target(self.tmp)
        try:
            apply_updates(
                target, self._craft_plan(hostile_rel), ACTOR_ID, INSTALLATION_ID
            )
        except UpdateEngineError:
            pass  # refusing loudly is the contract; zero writes is the proof
        self.assertFalse(
            (target / JOURNAL_RELPATH).exists(),
            f"SEC-1 RED: hostile target '{hostile_rel}' reached the write "
            "stage — the operation journal was already written (ZERO-write "
            "contract broken for an out-of-root destination)",
        )
        self.assertFalse(
            outside.exists(),
            f"SEC-1 RED: a file was written outside the repository root at "
            f"'{outside}'",
        )

    def test_drive_absolute_apply_zero_writes(self):
        self._assert_apply_zero_writes("C:/evil", Path("C:/evil"))

    def test_unc_apply_zero_writes(self):
        self._assert_apply_zero_writes("//server/share", Path("//server/share"))

    def tearDown(self):
        # RED-phase safety net: never leave an artifact on the real drive.
        try:
            if Path("C:/evil").is_file():
                Path("C:/evil").unlink()
        except OSError:
            pass
        super().tearDown()


class TestSEC1SymlinksAndJunctions(FxWaveTestCase):
    """U9-class exfil: a link planted at (or above) the destination must never
    let bytes escape the repository."""

    def test_junction_escape_write_refused(self):
        if sys.platform != "win32":
            self.skipTest("junction variant is Windows-specific; symlink variant covers POSIX")
        target = _make_target(self.tmp)
        outside = self.tmp / "outside-area"
        outside.mkdir()
        (outside / "keep.txt").write_bytes(b" bystander\n")
        scripts = target / "scripts"
        shutil.rmtree(scripts)
        _make_dir_link(scripts, outside)

        manifest = _manifest_v1()
        manifest["components"] = [
            {"path": "scripts/escaped.py", "kind": "script", "requires": []}
        ]
        bundle = {
            "manifest": manifest,
            "files": {"scripts/escaped.py": b"ESCAPED-PAYLOAD\n"},
            "base": {},
        }
        plan = plan_updates(target, bundle, read_lock(target))

        with self.assertRaises(UpdateEngineError):
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)

        self.assertFalse(
            (outside / "escaped.py").exists(),
            "SEC-1 RED: apply wrote through the junction OUTSIDE the "
            "repository root — the destination was not contained",
        )
        self.assertFalse(
            (target / JOURNAL_RELPATH).exists(),
            "SEC-1: refused apply must not write a journal",
        )

    def test_symlinked_dest_refused_no_exfil(self):
        target = _make_target(self.tmp)
        secret = self.tmp / "outside-secret.txt"
        secret.write_bytes(SECRET_BYTES)
        dest = target / "scripts" / "x.py"
        try:
            dest.unlink()
            os.symlink(str(secret), str(dest))
        except OSError:
            self.skipTest(
                "symbolic link privilege unavailable on this host; the "
                "junction variant covers the escape class"
            )
        # Crafted lock: the symlinked bytes ARE the recorded installation, so
        # the fast-forward path would journal the linked content (exfil).
        _lock = {
            "schema_version": "1.0.0",
            "source": {"repository": "adv", "ref": "main", "commit_sha": "0" * 40,
                       "origin": "upstream", "channel": "preview"},
            "components": [{
                "path": "scripts/x.py", "kind": "script",
                "base_sha256": _sha(SECRET_BYTES),
                "installed_sha256": _sha(SECRET_BYTES),
                "target": "scripts/x.py",
            }],
            "installed_at": "2026-11-16T00:00:00Z",
        }
        (target / ".agents" / "framework-lock.json").write_text(
            json.dumps(_lock, indent=2), encoding="utf-8"
        )
        bundle = {
            "manifest": _manifest_v1(),
            "files": {"scripts/x.py": ORIGIN_X_V2, "scripts/z.py": ORIGIN_Z_V1,
                      "skills/y/SKILL.md": ORIGIN_Y_V1},
            "base": {},
        }
        plan = plan_updates(target, bundle, read_lock(target))

        with self.assertRaises(UpdateEngineError):
            apply_updates(target, plan, ACTOR_ID, INSTALLATION_ID)

        journal = target / JOURNAL_RELPATH
        self.assertFalse(
            journal.exists(),
            "SEC-1 RED: the symlinked destination was followed — the journal "
            "captured the linked-outside content (exfil channel)",
        )
        if journal.exists():
            self.assertNotIn(
                base64.b64encode(SECRET_BYTES).decode("ascii"),
                journal.read_text(encoding="utf-8", errors="replace"),
            )
        self.assertTrue(secret.is_file(), "the outside secret must stay intact")


# ---------------------------------------------------------------------------
# T-X2 — SEC-2: cache verification (cache-manifest.json + origin cross-check)
# ---------------------------------------------------------------------------


class TestSEC2CacheVerification(FxWaveTestCase):
    def _sealed_cache(self, files: "dict | None" = None) -> tuple:
        origin, first_sha = _make_origin_repo(self.tmp)
        cache_root = self.tmp / "cache"
        _write_cache(
            cache_root,
            first_sha,
            _manifest_v1(),
            files if files is not None else _origin_files_v1(),
            seal_for=first_sha,
        )
        return origin, first_sha, cache_root

    def _tamper(self, cache_root: Path, sha: str) -> None:
        victim = cache_root / sha / "scripts" / "x.py"
        victim.write_bytes(ORIGIN_X_V1 + b"# TAMPERED BY ADVERSARY\n")

    def test_tampered_cache_offline_refused(self):
        origin, first_sha, cache_root = self._sealed_cache()
        self._tamper(cache_root, first_sha)
        dead_source = str(origin)
        hidden = self.tmp / "origin-gone"
        shutil.move(str(origin), str(hidden))
        pin = resolve_pin_with_cache_fallback(dead_source, first_sha, cache_root)

        served = None
        try:
            bundle = load_bundle(pin, cache_root)
            served = (bundle.get("files") or {}).get("scripts/x.py")
        except UpdateEngineError:
            pass
        self.assertIsNone(
            served,
            f"SEC-2 RED: tampered cache bytes served OFFLINE "
            f"(scripts/x.py={served!r}) — cache-manifest.json was not verified",
        )

    def test_tampered_cache_offline_apply_refused_cli(self):
        origin, first_sha, cache_root = self._sealed_cache()
        self._tamper(cache_root, first_sha)
        target = _make_target(self.tmp)
        dead_source = str(origin)
        hidden = self.tmp / "origin-gone"
        shutil.move(str(origin), str(hidden))
        lock_before = (target / ".agents" / "framework-lock.json").read_bytes()

        rc, _out, err = _run_main([
            "apply",
            "--repo-root", str(target),
            "--source", dead_source,
            "--ref", first_sha,
            "--cache-dir", str(cache_root),
            "--installation", INSTALLATION_ID,
            "--actor", ACTOR_ID,
        ])

        self.assertEqual(
            rc, 1, f"tampered cache must be refused offline, stderr: {err}"
        )
        self.assertEqual(
            (target / ".agents" / "framework-lock.json").read_bytes(),
            lock_before,
            "refused apply must not touch the framework lock",
        )
        self.assertFalse((target / JOURNAL_RELPATH).exists())

    def test_tampered_cache_online_refused(self):
        origin, first_sha, cache_root = self._sealed_cache()
        self._tamper(cache_root, first_sha)
        pin = resolve_pin_with_cache_fallback(str(origin), first_sha, cache_root)

        served = None
        try:
            bundle = load_bundle(pin, cache_root)
            served = (bundle.get("files") or {}).get("scripts/x.py")
        except UpdateEngineError:
            pass
        self.assertIsNone(
            served,
            f"SEC-2 RED: tampered cache bytes served with the origin "
            f"REACHABLE (scripts/x.py={served!r})",
        )

    def test_tampered_unsealed_cache_refused_against_origin(self):
        origin, first_sha = _make_origin_repo(self.tmp)
        cache_root = self.tmp / "cache"
        _write_cache(cache_root, first_sha, _manifest_v1(), _origin_files_v1())
        self._tamper(cache_root, first_sha)
        pin = resolve_pin_with_cache_fallback(str(origin), first_sha, cache_root)

        served = None
        try:
            bundle = load_bundle(pin, cache_root)
            served = (bundle.get("files") or {}).get("scripts/x.py")
        except UpdateEngineError:
            pass
        self.assertIsNone(
            served,
            f"SEC-2 RED: tampered UNSEALED cache served although the origin "
            f"could cross-verify (scripts/x.py={served!r})",
        )

    def test_wrong_pin_cache_refused(self):
        origin, first_sha = _make_origin_repo(self.tmp)
        head_sha = _git_ok(origin, "rev-parse", "HEAD").stdout.strip()
        cache_root = self.tmp / "cache"
        # Cache directory CLAIMS the post-rewrite pin (head_sha) but was
        # sealed for the old pin (first_sha) — the post-rewrite window attack.
        _write_cache(
            cache_root, head_sha, _manifest_v1(), _origin_files_v1(),
            seal_for=first_sha,
        )
        dead_source = str(origin)
        hidden = self.tmp / "origin-gone"
        shutil.move(str(origin), str(hidden))
        pin = resolve_pin_with_cache_fallback(dead_source, head_sha, cache_root)

        served = None
        try:
            bundle = load_bundle(pin, cache_root)
            served = _sha((bundle.get("files") or {}).get("scripts/x.py", b""))
        except UpdateEngineError:
            pass
        self.assertIsNone(
            served,
            f"SEC-2 RED: cache sealed for pin {first_sha} was served for "
            f"pin {head_sha} (served x.py sha256={served}) — ref-pin was "
            "not checked",
        )

    def test_unsealed_valid_cache_served_and_sealed_on_apply(self):
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache_root = self.tmp / "cache"
        _write_cache(cache_root, first_sha, _manifest_v1(), _origin_files_v1())

        pin = resolve_pin_with_cache_fallback(str(origin), first_sha, cache_root)
        bundle = load_bundle(pin, cache_root)
        self.assertEqual(
            (bundle.get("files") or {}).get("scripts/x.py"),
            ORIGIN_X_V1,
            "unsealed cache with origin-reachable matching bytes must serve "
            "(cross-verified)",
        )

        rc, _out, err = _run_main([
            "apply",
            "--repo-root", str(target),
            "--source", str(origin),
            "--ref", first_sha,
            "--cache-dir", str(cache_root),
            "--installation", INSTALLATION_ID,
            "--actor", ACTOR_ID,
        ])
        self.assertEqual(rc, 0, f"apply over a valid unsealed cache must succeed, stderr: {err}")
        sealed = cache_root / first_sha / "cache-manifest.json"
        self.assertTrue(
            sealed.is_file(),
            "SEC-2: apply/load must seal a cross-verified cache entry with "
            "cache-manifest.json (written at bundle load time)",
        )


# ---------------------------------------------------------------------------
# T-X3 — SEC-4: serialization (file lock held across apply AND restore)
# ---------------------------------------------------------------------------


class TestSEC4Serialization(FxWaveTestCase):
    def test_concurrent_apply_subprocess_refused_engine_busy(self):
        origin, _first = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        holder = _lock_engine(target)
        try:
            rc, out, err = _run_cli([
                "apply",
                "--repo-root", str(target),
                "--source", str(origin),
                "--ref", "main",
                "--installation", INSTALLATION_ID,
                "--actor", ACTOR_ID,
            ])
        finally:
            _unlock_engine(holder)

        self.assertEqual(
            rc, 1,
            f"SEC-4 RED: a second concurrent engine operation was NOT refused "
            f"(rc={rc}) — apply is not serialized",
        )
        self.assertIn(
            "ENGINE_BUSY", err,
            f"the refusal must carry the ENGINE_BUSY envelope, stderr: {err!r}",
        )
        self.assertFalse(
            (target / JOURNAL_RELPATH).exists(),
            "a refused concurrent operation must leave the journal untouched",
        )
        self.assertNotEqual(
            (target / "scripts" / "x.py").read_bytes(), ORIGIN_X_V2,
            "a refused concurrent operation must not install anything",
        )

    def test_concurrent_restore_library_refused_engine_busy(self):
        target = _make_target(self.tmp)
        _write_journal(target, [])

        holder = _lock_engine(target)
        try:
            refused = False
            try:
                restore_updates(target)
            except UpdateEngineError as exc:
                refused = True
                self.assertIn("ENGINE_BUSY", str(exc))
        finally:
            _unlock_engine(holder)
        self.assertTrue(
            refused,
            "SEC-4 RED: restore ran while another engine operation held the "
            "repository lock — restore is not serialized",
        )


# ---------------------------------------------------------------------------
# T-X4 — U6: check shares the plan/apply cache-fallback resolution
# ---------------------------------------------------------------------------


class TestU6CheckCacheFallback(FxWaveTestCase):
    def test_check_dead_origin_exact_sha_valid_cache_succeeds(self):
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache_root = self.tmp / "cache"
        _write_cache(cache_root, first_sha, _manifest_v1(), _origin_files_v1(),
                     seal_for=first_sha)
        dead_source = str(origin)
        hidden = self.tmp / "origin-gone"
        shutil.move(str(origin), str(hidden))

        rc, out, err = _run_main([
            "check",
            "--repo-root", str(target),
            "--source", dead_source,
            "--ref", first_sha,
            "--cache-dir", str(cache_root),
        ])

        self.assertEqual(
            rc, 0,
            f"U6 RED: check with a dead origin + exact-SHA ref + valid "
            f"integral cache must answer via the cache (like plan/apply), "
            f"stderr: {err!r}",
        )
        payload = json.loads(out)
        self.assertEqual(payload.get("status"), "up_to_date")
        self.assertEqual(payload.get("source", {}).get("origin"), "cache")

    def test_check_reports_updates_via_cache(self):
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        cache_root = self.tmp / "cache"
        manifest = _manifest_v1()
        _write_cache(cache_root, first_sha, manifest,
                     _origin_files_v2(), seal_for=first_sha)
        dead_source = str(origin)
        hidden = self.tmp / "origin-gone"
        shutil.move(str(origin), str(hidden))

        rc, out, err = _run_main([
            "check",
            "--repo-root", str(target),
            "--source", dead_source,
            "--ref", first_sha,
            "--cache-dir", str(cache_root),
        ])

        self.assertEqual(
            rc, 1, f"updates found must keep the rc=1 contract, stderr: {err!r}"
        )
        payload = json.loads(out)
        self.assertTrue(payload.get("updates_available"), "updates must be reported via the cache")
        self.assertEqual(payload.get("check_status"), "ok")


# ---------------------------------------------------------------------------
# T-X5 — U7 + U11: versions.after split; restore marks the report restored
# ---------------------------------------------------------------------------


class TestU7U11ReportSemantics(FxWaveTestCase):
    def _apply_via_cli(self) -> tuple:
        origin, _first = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        rc, out, err = _run_main([
            "apply",
            "--repo-root", str(target),
            "--source", str(origin),
            "--ref", "main",
            "--installation", INSTALLATION_ID,
            "--actor", ACTOR_ID,
        ])
        self.assertEqual(rc, 0, f"apply fixture must succeed, stderr: {err}")
        return origin, target

    def test_update_report_versions_after_split(self):
        _origin, target = self._apply_via_cli()
        report = self.latest_update_report(target)

        after = (report.get("versions") or {}).get("after")
        self.assertIsInstance(
            after, dict,
            f"U7 RED: versions.after must be split into framework_version + "
            f"commit_sha (got {after!r})",
        )
        self.assertEqual(after.get("framework_version"), "1.0.0-fix.2")
        self.assertTrue(
            after.get("commit_sha"),
            "versions.after must carry the exact pinned commit_sha",
        )
        self.assertEqual(
            validate_report(report, expected_type="update"),
            [],
            "the reshaped report must still pass canonical validation",
        )

    def test_restore_marks_update_report_restored(self):
        _origin, target = self._apply_via_cli()
        report_path = (
            target / ".agents" / "reports" / INSTALLATION_ID / "update"
        )
        pointer = json.loads((report_path / "latest.json").read_text(encoding="utf-8"))

        rc, out, err = _run_main(["restore", "--repo-root", str(target)])
        self.assertEqual(rc, 0, f"restore fixture must succeed, stderr: {err}")

        restored = json.loads(
            (report_path / pointer["path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            restored.get("status"),
            "restored",
            "U11 RED: restore must mark the update report "
            "status='restored' (audit trail preserved)",
        )


# ---------------------------------------------------------------------------
# T-X6 — U8: check JSON carries check_status; rc contract unchanged
# ---------------------------------------------------------------------------


class TestU8CheckStatus(FxWaveTestCase):
    def test_failing_check_rc1_and_check_status_failed(self):
        origin, _first = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)
        dead_source = str(origin)
        hidden = self.tmp / "origin-gone"
        shutil.move(str(origin), str(hidden))
        empty_cache = self.tmp / "empty-cache"
        empty_cache.mkdir()

        rc, out, err = _run_main([
            "check",
            "--repo-root", str(target),
            "--source", dead_source,
            "--ref", "main",
            "--cache-dir", str(empty_cache),
        ])

        self.assertEqual(rc, 1, "a failing check keeps the rc=1 contract")
        self.assertIn("[CHECK-FAILED]", err)
        payload = json.loads(out)
        self.assertEqual(
            payload.get("check_status"), "failed",
            f"U8 RED: failing check must emit check_status='failed' (stdout: {out!r})",
        )

    def test_updates_found_rc1_and_check_status_ok(self):
        origin, _first = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        rc, out, _err = _run_main([
            "check",
            "--repo-root", str(target),
            "--source", str(origin),
            "--ref", "main",
        ])

        self.assertEqual(rc, 1, "updates-found keeps the rc=1 contract (unchanged)")
        payload = json.loads(out)
        self.assertTrue(payload.get("updates_available"))
        self.assertEqual(
            payload.get("check_status"), "ok",
            "U8 RED: a successful check that finds updates must carry "
            "check_status='ok'",
        )

    def test_up_to_date_rc0_and_check_status_ok(self):
        origin, first_sha = _make_origin_repo(self.tmp)
        target = _make_target(self.tmp)

        rc, out, _err = _run_main([
            "check",
            "--repo-root", str(target),
            "--source", str(origin),
            "--ref", first_sha,
        ])

        self.assertEqual(rc, 0, "up-to-date keeps the rc=0 contract (unchanged)")
        payload = json.loads(out)
        self.assertEqual(payload.get("check_status"), "ok")
        self.assertEqual(payload.get("status"), "up_to_date")


# ---------------------------------------------------------------------------
# T-X7 — fsync durability in _atomic_write_bytes (no behavior change)
# ---------------------------------------------------------------------------


class TestTX7AtomicWriteFsync(FxWaveTestCase):
    def test_atomic_write_replaces_content_without_temp_litter(self):
        dest = self.tmp / "lockish.json"
        dest.write_bytes(b"{\"old\": true}\n")
        _atomic_write_bytes(dest, b"{\"new\": true}\n")
        self.assertEqual(dest.read_bytes(), b"{\"new\": true}\n")
        litter = [p.name for p in self.tmp.iterdir() if "updtmp" in p.name]
        self.assertEqual(
            litter, [],
            f"atomic write must clean up its temp file, found: {litter}",
        )


if __name__ == "__main__":
    unittest.main()
