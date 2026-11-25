#!/usr/bin/env python3
"""
scripts/_update_bundle.py

Cache bundle management, source resolution, integrity validation,
and lock file handling for the managed update engine (ADR #22 submodule).
Pure Python 3.10+ standard library, zero external dependencies.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FRAMEWORK_LOCK_RELPATH = ".agents/framework-lock.json"
UPDATE_JOURNAL_RELPATH = ".agents/update-journal.json"
PROJECT_BOUNDARIES_RELPATH = ".agents/project_knowledge/boundaries.md"
# SEC-4 (Wave F FX, T-X3): per-repository serialization of the mutating
# engine operations (apply, restore).
ENGINE_LOCK_RELPATH = ".agents/update-engine.lock"
# SEC-2 (Wave F FX, T-X2): per-cache-entry trust anchor.
CACHE_MANIFEST_RELPATH = "cache-manifest.json"
LOCK_SCHEMA_VERSION = "1.0.0"
REPORT_TYPE = "update"

# Manifest readability (Wave D E2, T6.8): a source revision carries its
# release manifest at the root ``manifest.json`` OR at the canonical framework
# repository layout ``templates/release_manifest.json``.
MANIFEST_RELPATH = "manifest.json"
CANONICAL_MANIFEST_RELPATH = "templates/release_manifest.json"
_EXACT_SHA_RE = re.compile(r"[0-9a-f]{40}")


class UpdateEngineError(Exception):
    """Base class for managed-update engine failures."""


class SourceResolutionError(UpdateEngineError):
    """A ref could not be pinned to an exact commit SHA."""


class PathContainmentError(UpdateEngineError):
    """SEC-1 (Wave F FX, T-X1): a managed path escapes (or threatens to
    escape) its containment root — absolute, parent-traversing, or a symlink
    destination. Refused with ZERO writes."""


class MixedBundleError(UpdateEngineError):
    """The bundle cannot be materialized as ONE integral revision."""


class PartialCacheError(MixedBundleError):
    """A cache entry exists but is not an integral bundle: refused."""


class CacheVerificationError(MixedBundleError):
    """SEC-2 (Wave F FX, T-X2): a cache bundle cannot be verified as integral
    and untouched (cache-manifest.json mismatch, wrong ref-pin, or origin
    cross-check mismatch). Unverified cache bytes are never used."""


class EngineBusyError(UpdateEngineError):
    """SEC-4 (Wave F FX, T-X3): another engine operation (apply/restore)
    holds the repository lock; concurrent operations are refused."""


class LegacyDuplicateError(UpdateEngineError):
    """Divergent canonical/legacy copies of a managed utility: halt."""


class ProtectedComponentError(UpdateEngineError):
    """Refusal to touch a protected (Red Zone) component."""


class ApplyError(UpdateEngineError):
    """The atomic apply failed; the journal preserves the recovery state."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------



def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _installed_match(local_bytes: Optional[bytes], recorded_sha: str) -> tuple:
    """Compare working-copy bytes against the lock-recorded installed sha256.

    Returns ``(matched, eol_only)``. A raw hash match is an exact match; a
    match after CRLF→LF normalization is an EOL-only match (autocrlf smudge
    on a fresh checkout) — still an installed match, flagged for an explicit
    diagnostic. Content changes never match. Cache-manifest verification and
    origin cross-verification do NOT use this helper: they stay byte-exact
    (Wave G Lane H)."""
    if not recorded_sha or local_bytes is None:
        return (False, False)
    if _sha256_bytes(local_bytes) == recorded_sha:
        return (True, False)
    normalized = local_bytes.replace(b"\r\n", b"\n")
    if _sha256_bytes(normalized) == recorded_sha:
        return (True, True)
    return (False, False)


def _entry_installed_sha(entry: Optional[Dict[str, Any]]) -> str:
    """Installed-state sha256 of a lock component entry.

    Lock component schema v2 records ``installed_sha256`` (bytes actually on
    disk); v1 entries carried a single ``sha256`` — read as the installed
    state (and as the base) for backward compatibility."""
    for key in ("installed_sha256", "sha256"):
        value = str((entry or {}).get(key, "") or "")
        if value:
            return value
    return ""


def _entry_base_sha(entry: Optional[Dict[str, Any]]) -> str:
    """Merge-base sha256 of a lock component entry.

    Schema v2 records ``base_sha256`` — the pinned upstream bytes the
    installation was built from; v1 ``sha256`` is read as the base for
    backward compatibility. Base-candidate acceptance stays hash-verified
    against this record regardless of which cache provided the bytes."""
    for key in ("base_sha256", "sha256"):
        value = str((entry or {}).get(key, "") or "")
        if value:
            return value
    return ""


_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


def _posix(rel: Any) -> str:
    """Normalize a managed relative path to posix form.

    SEC-1 layer (a) (Wave F FX, T-X1): paths that are absolute (posix- or
    Windows-style, including drive letters and UNC shares) or carry ANY
    ``..`` segment are hostile and REFUSED here — every component path, lock
    target, plan action target, journal path and cache-manifest component
    flows through this function, so a hostile manifest cannot even reach the
    write stage."""
    raw = str(rel)
    normalized = raw.replace("\\", "/")
    if (
        normalized.startswith("/")
        or Path(raw).is_absolute()
        or _WINDOWS_DRIVE_RE.match(normalized)
        or ".." in normalized.split("/")
    ):
        raise PathContainmentError(
            f"hostile managed path refused: {raw!r} must be a relative "
            "repo-internal path without '..' segments (SEC-1 containment)"
        )
    return normalized.strip("/")


def assert_within(root: Path, rel: str) -> Path:
    """SEC-1 layers (b)+(c) (Wave F FX, T-X1): resolve ``rel`` against
    ``root`` and REFUSE unless the resolved destination stays inside the
    resolved root, and the destination itself is not an existing symlink.

    Call before EVERY write/read of an engine-managed destination (apply,
    cache reads, restore, journal/lock/report writes): resolve() follows
    directory junctions and symlinks, so a link planted above the destination
    resolves outside the root and is refused; a symlink AT the destination is
    refused outright (U9 exfil guard). Returns the RESOLVED destination."""
    root_resolved = Path(root).resolve()
    dest = Path(root) / _posix(rel)
    if dest.is_symlink():
        raise PathContainmentError(
            f"destination '{_posix(rel)}' is an existing symlink; refusing "
            "to read or write through it (SEC-1 symlink guard)"
        )
    resolved = dest.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        raise PathContainmentError(
            f"managed path '{_posix(rel)}' resolves to '{resolved}' which is "
            f"OUTSIDE the containment root '{root_resolved}'; refusing "
            "(SEC-1 containment)"
        )
    return resolved


def _run_git(args: List[str], text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=text,
    )


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Per-file atomic replace: write to a sibling temp file, fsync the temp
    file (T-X7 durability: the payload survives a crash across the rename),
    then os.replace. On failure the temp file is cleaned up and the
    destination is left untouched."""
    tmp = path.parent / f".{path.name}.updtmp-{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def _split_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# SEC-4 serialization (Wave F FX, T-X3): ported from scripts/compact_memory.py
# (file_lock, lines 20-61) with a non-blocking engine-operation wrapper.
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def file_lock(target: Any, blocking: bool = True):
    """Cross-platform file locking context manager (Windows msvcrt / Unix
    fcntl). Accepts an open file object or a Path/str path."""
    opened_here = False
    if isinstance(target, (str, os.PathLike)):
        p = Path(target)
        p.parent.mkdir(parents=True, exist_ok=True)
        f = open(p, "a+b")
        opened_here = True
    else:
        f = target

    fd = f.fileno()

    if sys.platform == "win32":
        import msvcrt

        f.seek(0)
        mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK
        msvcrt.locking(fd, mode, 1)
        try:
            yield f
        finally:
            f.seek(0)
            try:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            finally:
                if opened_here:
                    f.close()
    else:
        import fcntl

        mode = fcntl.LOCK_EX if blocking else (fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, mode)
        try:
            yield f
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                if opened_here:
                    f.close()


@contextlib.contextmanager
def engine_operation_lock(repo_root: Path):
    """Serialize the MUTATING engine operations (apply, restore) per
    repository (SEC-4): a non-blocking exclusive lock on
    ``.agents/update-engine.lock`` (msvcrt/fcntl, per ``file_lock``). A
    second concurrent engine operation is refused immediately with
    EngineBusyError ("ENGINE_BUSY") — it never writes a journal or touches
    any file. Only lock ACQUISITION maps to EngineBusyError; body failures
    keep their own error types."""
    lock_path = Path(repo_root) / ENGINE_LOCK_RELPATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "a+b")
    fd = handle.fileno()
    try:
        if sys.platform == "win32":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise EngineBusyError(
            "ENGINE_BUSY: another update-engine operation (apply or restore) "
            "is already running on this repository; refusing concurrent "
            "execution"
        ) from exc
    try:
        yield handle
    finally:
        try:
            handle.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            handle.close()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def default_cache_dir() -> Path:
    """Cache resolution: explicit flag > env META_PROJECT_CACHE > OS cache
    path (Windows: %LOCALAPPDATA%/meta-project/cache; POSIX:
    ~/.cache/meta-project). The engine reads cache entries read-only; the
    only cache write is the SEC-2 trust anchor ``cache-manifest.json`` that
    apply writes (seal_cache=True) after cross-verifying an unsealed entry
    against the origin."""
    env = os.environ.get("META_PROJECT_CACHE")
    if env:
        return Path(env)
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(
            Path.home() / "AppData" / "Local"
        )
        return Path(base) / "meta-project" / "cache"
    return Path.home() / ".cache" / "meta-project"


# ---------------------------------------------------------------------------
# Source resolution and bundle materialization (fetch strictly by SHA)
# ---------------------------------------------------------------------------


def resolve_source(source: str, ref: str) -> Dict[str, str]:
    """Pin ``ref`` in ``source`` to ONE exact commit SHA.

    Returns a SourcePin dict: {commit_sha, origin_repo, ref}. Every bundle
    byte is later fetched from this SHA only — never from a moving ref.
    """
    repo = str(source)
    if not repo:
        raise SourceResolutionError("source must not be empty")
    if not str(ref or "").strip():
        raise SourceResolutionError("ref must not be empty")
    proc = _run_git(
        ["-C", repo, "rev-parse", "--verify", f"{ref}^{{commit}}"]
    )
    if proc.returncode != 0:
        raise SourceResolutionError(
            f"cannot resolve ref '{ref}' to an exact commit in source "
            f"repository '{repo}': {(proc.stderr or '').strip()}"
        )
    sha = (proc.stdout or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SourceResolutionError(
            f"ref '{ref}' in '{repo}' did not resolve to a 40-hex commit SHA "
            f"(got: {sha!r})"
        )
    return {"commit_sha": sha, "origin_repo": repo, "ref": str(ref)}


def resolve_pin_with_cache_fallback(
    source: str, ref: str, cache_dir: Optional[Path] = None
) -> Dict[str, str]:
    """CLI pin resolution (Wave D E2, T6.3/D2): resolve against the origin
    first; when the origin is UNREACHABLE but ``ref`` is already an EXACT
    40-hex commit SHA, trust it as the pin and let ``load_bundle`` satisfy
    the bundle from the integral cache (``origin: cache``). Refs that are
    NOT exact SHAs still require a resolvable origin — a moving ref can
    never be pinned offline."""
    try:
        return resolve_source(source, ref)
    except SourceResolutionError:
        raw = str(ref or "").strip().lower()
        if _EXACT_SHA_RE.fullmatch(raw):
            pin: Dict[str, str] = {
                "commit_sha": raw,
                "origin_repo": str(source),
                "ref": str(ref),
            }
            pinned_dir = (
                Path(cache_dir) / raw if cache_dir is not None else None
            )
            if pinned_dir is not None and pinned_dir.is_dir():
                return pin
            # No cache entry either: fall through to the original refusal so
            # the error names the unresolvable origin, not a missing cache.
        raise


def _git_blob(origin_repo: str, sha: str, path: str) -> bytes:
    """Read the RAW blob of ``<sha>:<path>`` via ``git cat-file`` — strictly
    by SHA. cat-file returns the object bytes verbatim (no checkout/EOL
    smudging), so bundle content is independent of core.autocrlf and
    .gitattributes on either side."""
    proc = subprocess.run(
        ["git", "-C", origin_repo, "cat-file", "blob", f"{sha}:{path}"],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise MixedBundleError(
            f"pinned commit {sha} in '{origin_repo}' does not provide "
            f"'{path}': {proc.stderr.decode(errors='replace').strip()}"
        )
    return proc.stdout


def _fetch_pinned_tree(origin_repo: str, sha: str) -> Dict[str, bytes]:
    """Materialize the pinned commit's component set — strictly by SHA,
    never re-floating a moving ref, never touching the working tree, and
    byte-exact (no EOL conversion). The release manifest is read at the
    source root, falling back to the canonical framework layout
    ``templates/release_manifest.json`` (T6.8)."""
    files: Dict[str, bytes] = {}
    try:
        manifest_blob = _git_blob(origin_repo, sha, MANIFEST_RELPATH)
        manifest_rel = MANIFEST_RELPATH
    except MixedBundleError:
        manifest_blob = _git_blob(origin_repo, sha, CANONICAL_MANIFEST_RELPATH)
        manifest_rel = CANONICAL_MANIFEST_RELPATH
    files[manifest_rel] = manifest_blob
    files[MANIFEST_RELPATH] = manifest_blob  # canonical alias
    try:
        manifest = json.loads(manifest_blob.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise MixedBundleError(
            f"manifest of pinned commit {sha} in '{origin_repo}' "
            f"({manifest_rel}) is not valid JSON: {exc}"
        )
    for comp in _components_of(manifest):
        rel = _posix(comp.get("path", ""))
        files[rel] = _git_blob(origin_repo, sha, rel)
    return files


def _components_of(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    comps = manifest.get("components") or []
    return [c for c in comps if isinstance(c, dict) and _posix(c.get("path", ""))]


# ---------------------------------------------------------------------------
# SEC-2 cache verification (Wave F FX, T-X2)
# ---------------------------------------------------------------------------


def build_cache_manifest(
    files: Dict[str, bytes], commit_sha: str, ref: str = ""
) -> Dict[str, Any]:
    """SEC-2 trust anchor for one cache entry: the ref-pin (commit sha) the
    bundle was built from + the sha256 of EVERY bundle file (manifest.json +
    all manifest components). Written at bundle build/seal time and verified
    at every load."""
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "commit_sha": str(commit_sha),
        "ref": str(ref or commit_sha),
        "files": {
            rel: _sha256_bytes(data) for rel, data in sorted(files.items())
        },
    }


def seal_cache_entry(
    pinned_dir: Path, files: Dict[str, bytes], commit_sha: str, ref: str = ""
) -> Optional[Path]:
    """Write ``<pinned_dir>/cache-manifest.json`` (SEC-2). Best-effort: a
    read-only cache directory degrades to an unsealed entry (future loads
    fall back to origin cross-verification)."""
    payload = json.dumps(
        build_cache_manifest(files, commit_sha, ref), indent=2, sort_keys=True
    ) + "\n"
    target = pinned_dir / CACHE_MANIFEST_RELPATH
    try:
        _atomic_write_bytes(target, payload.encode("utf-8"))
    except OSError:
        return None
    return target


def _load_cache_manifest(
    bundle_root: Path, expected_sha: str
) -> Optional[Dict[str, Any]]:
    """Read and validate the cache entry's trust anchor. Returns None when
    the entry is unsealed; raises CacheVerificationError on a malformed
    manifest or a WRONG REF-PIN (cache sealed for pin A but served for pin
    B — the post-rewrite window attack)."""
    cm_path = bundle_root / CACHE_MANIFEST_RELPATH
    if not cm_path.is_file():
        return None
    try:
        entry = _read_json(cm_path)
    except (OSError, ValueError) as exc:
        raise CacheVerificationError(
            f"cache manifest '{cm_path}' is unreadable (fail-closed): {exc}"
        )
    if (
        not isinstance(entry, dict)
        or not str(entry.get("commit_sha", "")).strip()
        or not isinstance(entry.get("files"), dict)
    ):
        raise CacheVerificationError(
            f"cache manifest '{cm_path}' is malformed (expected an object "
            "with 'commit_sha' and a 'files' sha256 map); refusing to use "
            "unverifiable cache bytes"
        )
    sealed_pin = str(entry["commit_sha"])
    if expected_sha and sealed_pin != expected_sha:
        raise CacheVerificationError(
            f"cache bundle '{bundle_root}' was sealed for commit {sealed_pin} "
            f"but the requested pin is {expected_sha}; refusing cross-pin "
            "cache reuse (SEC-2 ref-pin mismatch)"
        )
    return entry


def _read_bundle_tree(
    bundle_root: Path, expected_sha: str = ""
) -> Tuple[Dict[str, Any], Dict[str, bytes], bool]:
    """Read an INTEGRAL and VERIFIED bundle directory: the release manifest
    (root ``manifest.json`` or the canonical ``templates/release_manifest.json``
    fallback, T6.8) + EVERY manifest component.

    SEC-1: every component read is contained (assert_within) — a hostile
    cache manifest component ('../..' etc.) is refused, never read.
    SEC-2: when the entry carries ``cache-manifest.json``, every file hash
    and the ref-pin are verified; returns ``verified=True``. An unsealed
    entry returns ``verified=False`` (the caller must cross-verify against
    the origin or refuse). A missing component stays a PartialCacheError."""
    manifest_path = bundle_root / MANIFEST_RELPATH
    manifest_rel = MANIFEST_RELPATH
    if not manifest_path.is_file():
        manifest_path = bundle_root / Path(*CANONICAL_MANIFEST_RELPATH.split("/"))
        manifest_rel = CANONICAL_MANIFEST_RELPATH
    if not manifest_path.is_file():
        raise MixedBundleError(
            f"cache entry '{bundle_root}' carries no release manifest "
            f"(looked for '{MANIFEST_RELPATH}' and "
            f"'{CANONICAL_MANIFEST_RELPATH}'); refusing to guess an integral "
            "component set"
        )
    try:
        manifest = _read_json(manifest_path)
    except (OSError, ValueError) as exc:
        raise MixedBundleError(
            f"cache manifest '{manifest_path}' is unreadable: {exc}"
        )
    cache_entry = _load_cache_manifest(bundle_root, expected_sha)
    manifest_bytes = manifest_path.read_bytes()
    if cache_entry is not None:
        recorded = str(cache_entry["files"].get(manifest_rel, "") or "")
        if not recorded:
            raise CacheVerificationError(
                f"cache manifest does not cover '{manifest_rel}' of bundle "
                f"'{bundle_root}'; refusing an unverifiable bundle"
            )
        if _sha256_bytes(manifest_bytes) != recorded:
            raise CacheVerificationError(
                f"cache integrity failure for '{manifest_rel}' in bundle "
                f"'{bundle_root}': sha256 mismatch against cache-manifest.json "
                "(tampered or corrupted cache); refusing"
            )
    files: Dict[str, bytes] = {
        manifest_rel: manifest_bytes,
        MANIFEST_RELPATH: manifest_bytes,  # canonical alias
    }
    for comp in _components_of(manifest):
        rel = _posix(comp.get("path", ""))
        comp_path = assert_within(bundle_root, rel)
        if not comp_path.is_file():
            raise PartialCacheError(
                f"partial cache refused: bundle '{bundle_root}' is missing "
                f"manifest component '{rel}'; only an INTEGRAL single-revision "
                "bundle is acceptable (mixing revisions is prohibited)"
            )
        data = comp_path.read_bytes()
        if cache_entry is not None:
            recorded = str(cache_entry["files"].get(rel, "") or "")
            if not recorded:
                raise CacheVerificationError(
                    f"cache manifest does not cover component '{rel}' of "
                    f"bundle '{bundle_root}'; refusing an unverifiable bundle"
                )
            if _sha256_bytes(data) != recorded:
                raise CacheVerificationError(
                    f"cache integrity failure for '{rel}' in bundle "
                    f"'{bundle_root}': sha256 mismatch against "
                    "cache-manifest.json (tampered or corrupted cache); "
                    "refusing"
                )
        files[rel] = data
    return manifest, files, (cache_entry is not None)


def _collect_base_candidates(cache_root: Optional[Path]) -> Dict[str, bytes]:
    """Pool of merge-base candidates: contents of ALL cached bundles (keyed
    by path, first-found wins). NO blanket exclusion of the pinned bundle
    itself (Wave D E1, D6): when the pin matches the installed revision, the
    pinned cache entry holds the exact lock-recorded base bytes. plan_updates
    accepts a candidate only when its sha256 hash-verifies against the
    lock-recorded base sha — a candidate matching ``base_sha256`` is valid
    regardless of which cache directory provided it, and non-matching
    candidates are inert."""
    base: Dict[str, bytes] = {}
    if cache_root is None:
        return base
    cache_root = Path(cache_root)
    if not cache_root.is_dir():
        return base
    for child in sorted(cache_root.iterdir()):
        if not child.is_dir():
            continue
        manifest_path = child / MANIFEST_RELPATH
        if not manifest_path.is_file():
            manifest_path = child / Path(*CANONICAL_MANIFEST_RELPATH.split("/"))
        if not manifest_path.is_file():
            continue
        try:
            manifest = _read_json(manifest_path)
        except (OSError, ValueError):
            continue
        for comp in _components_of(manifest):
            rel = _posix(comp.get("path", ""))
            if not rel or rel in base:
                continue
            # SEC-1: cache reads are contained — a hostile component path in
            # a cached manifest is refused, never read outside the cache.
            comp_path = assert_within(child, rel)
            if comp_path.is_file():
                try:
                    base[rel] = comp_path.read_bytes()
                except OSError:
                    continue
    return base


def _verify_cache_against_origin(
    origin_repo: str, sha: str, files: Dict[str, bytes]
) -> None:
    """SEC-2 origin cross-check (Wave F FX, T-X2): compare a cache bundle
    against the origin's blobs for the SAME pinned commit — every COMPONENT
    hash must match the origin blob byte-exactly; the manifest file is
    compared newline-normalized (cache builders may have written it in text
    mode, while cat-file returns the canonical blob). Any mismatch — or an
    origin that cannot provide the pinned tree for an unsealed entry — is a
    CacheVerificationError; cache bytes are never served on trust."""
    check = _run_git(
        ["-C", origin_repo, "rev-parse", "--verify", f"{sha}^{{commit}}"]
    )
    if check.returncode != 0:
        raise CacheVerificationError(
            f"cache entry has no cache-manifest.json and the origin "
            f"'{origin_repo}' cannot provide pinned commit {sha} "
            f"({(check.stderr or '').strip()}); refusing unverified cache "
            "bytes (SEC-2 fail-closed)"
        )
    origin_files = _fetch_pinned_tree(origin_repo, sha)
    manifest_rels = {MANIFEST_RELPATH, CANONICAL_MANIFEST_RELPATH}
    for rel, data in sorted(files.items()):
        origin_data = origin_files.get(rel)
        if origin_data is None:
            raise CacheVerificationError(
                f"cache integrity failure for '{rel}': the origin blob of "
                f"pinned commit {sha} is missing; refusing the cache bundle"
            )
        if rel in manifest_rels:
            cached_norm = data.replace(b"\r\n", b"\n")
            origin_norm = origin_data.replace(b"\r\n", b"\n")
            if cached_norm != origin_norm:
                raise CacheVerificationError(
                    f"cache integrity failure for '{rel}': cached bytes "
                    f"differ from the origin blob of pinned commit {sha} "
                    "(tampered or corrupted cache); refusing"
                )
        elif origin_data != data:
            raise CacheVerificationError(
                f"cache integrity failure for '{rel}': cached bytes differ "
                f"from the origin blob of pinned commit {sha} (tampered or "
                "corrupted cache); refusing"
            )


def load_bundle(
    pin: Dict[str, str],
    cache_dir: Optional[Path],
    seal_cache: bool = False,
) -> Dict[str, Any]:
    """Materialize the ENTIRE component set from the pinned SHA.

    Resolution order: integral VERIFIED cache entry ``<cache_dir>/<commit_sha>/``
    first, then ``git cat-file <sha>:<path>`` from the origin repository.
    SEC-2 (Wave F FX, T-X2): a sealed cache entry (``cache-manifest.json``)
    is hash-verified on load and additionally cross-verified against the
    origin blobs whenever the origin provides the pinned commit; an UNSEALED
    cache entry must cross-verify against the origin or is REFUSED —
    unverified cache bytes are never served. ``seal_cache=True`` (apply/load
    time) writes the trust anchor for a cross-verified entry so future
    offline loads can verify it.

    Raises MixedBundleError when neither source yields one integral revision,
    PartialCacheError for a partial cache entry, and CacheVerificationError
    for a tampered/mis-pinned/unverifiable cache. A missing merge base is NOT
    an exception: the empty ``base`` pool flows into plan_updates, which
    turns it into ``needs_base`` entries.

    Returns: {manifest, files: {path: bytes}, base: {path: bytes},
    commit_sha, origin_repo, ref, origin: 'cache'|'upstream'}.
    """
    pin = dict(pin or {})
    sha = str(pin.get("commit_sha", ""))
    origin_repo = str(pin.get("origin_repo", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise MixedBundleError(f"invalid pin (commit_sha={sha!r})")

    cache_root = Path(cache_dir) if cache_dir is not None else None
    pinned_dir = cache_root / sha if cache_root is not None else None

    manifest: Optional[Dict[str, Any]] = None
    files: Optional[Dict[str, bytes]] = None
    origin_kind: str

    if pinned_dir is not None and pinned_dir.is_dir():
        manifest, files, verified = _read_bundle_tree(pinned_dir, expected_sha=sha)
        if verified:
            # SEC-2: sealed entry — hash-verified above; additionally
            # cross-verify against the origin whenever the origin still
            # provides the pinned commit (defense against a malicious sealer).
            check = _run_git(
                ["-C", origin_repo, "rev-parse", "--verify", f"{sha}^{{commit}}"]
            )
            if check.returncode == 0:
                _verify_cache_against_origin(origin_repo, sha, files)
        else:
            # SEC-2: unsealed entry — the origin is the only trust anchor.
            _verify_cache_against_origin(origin_repo, sha, files)
            if seal_cache:
                seal_cache_entry(pinned_dir, files, sha, str(pin.get("ref") or sha))
        origin_kind = "cache"

    if files is None:
        check = _run_git(
            ["-C", origin_repo, "rev-parse", "--verify", f"{sha}^{{commit}}"]
        )
        if check.returncode != 0:
            raise MixedBundleError(
                f"cannot materialize the integral bundle for pinned commit "
                f"{sha}: origin '{origin_repo}' does not provide it "
                f"({(check.stderr or '').strip()}) and no integral cache "
                f"entry exists under '{pinned_dir}'"
            )
        files = _fetch_pinned_tree(origin_repo, sha)
        manifest = json.loads(files["manifest.json"].decode("utf-8"))
        origin_kind = "upstream"

    # Merge-base candidate pool: every cached bundle (NO pinned-sha exclusion,
    # D6), then the pinned bundle's own files as fallback candidates. A
    # candidate becomes a merge base ONLY when its sha256 hash-verifies
    # against the lock record in plan_updates — the pinned bytes are by
    # definition the base whenever pin.sha == lock base_sha256, and inert
    # otherwise.
    base_pool = _collect_base_candidates(cache_root)
    for rel, data in files.items():
        if rel not in base_pool:
            base_pool[rel] = data

    return {
        "manifest": manifest,
        "files": files,
        "base": base_pool,
        "commit_sha": sha,
        "origin_repo": origin_repo,
        "ref": str(pin.get("ref") or sha),
        "origin": origin_kind,
    }


def _filter_bundle(bundle: Dict[str, Any], components: List[str]) -> Dict[str, Any]:
    """Restrict a bundle to an explicit component subset (manifest != lock:
    the caller selects the installed subset; `requires` companions must be
    selected explicitly)."""
    wanted = {_posix(c) for c in components}
    manifest = dict(bundle.get("manifest") or {})
    manifest["components"] = [
        c for c in _components_of(manifest)
        if _posix(c.get("path", "")) in wanted
    ]
    filtered = dict(bundle)
    filtered["manifest"] = manifest
    filtered["files"] = {
        p: b for p, b in (bundle.get("files") or {}).items()
        if p == "manifest.json" or p in wanted
    }
    filtered["base"] = {
        p: b for p, b in (bundle.get("base") or {}).items() if p in wanted
    }
    return filtered


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------


def read_lock(repo_root: Path) -> Optional[Dict[str, Any]]:
    """Read ``.agents/framework-lock.json``; None when absent. A corrupted
    lock fails closed."""
    path = Path(repo_root) / FRAMEWORK_LOCK_RELPATH
    if not path.is_file():
        return None
    try:
        lock = _read_json(path)
    except (OSError, ValueError) as exc:
        raise UpdateEngineError(
            f"framework lock '{path}' is corrupted (fail-closed): {exc}"
        )
    if not isinstance(lock, dict):
        raise UpdateEngineError(
            f"framework lock '{path}' must be a JSON object (fail-closed)"
        )
    return lock


def _lock_payload_bytes(lock: Dict[str, Any]) -> bytes:
    """Canonical on-disk bytes of a framework lock (deterministic, so the
    journal can record the exact after-image before the write)."""
    return (json.dumps(lock, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_lock_atomic(repo_root: Path, lock: Dict[str, Any]) -> None:
    """Atomically replace ``.agents/framework-lock.json`` (SEC-1 contained)."""
    path = assert_within(Path(repo_root), FRAMEWORK_LOCK_RELPATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _lock_payload_bytes(lock)
    tmp = path.parent / f".framework-lock.tmp-{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp, "wb") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Read-only modes: check and plan
# ---------------------------------------------------------------------------


