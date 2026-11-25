#!/usr/bin/env python3
"""Shared hermetic Git fixtures and fast copytree builders for update engine tests.

Zero-dependency: Python 3.10+ stdlib only.
Caches canonical golden git repositories in a session temp directory and yields
isolated copies via fast shutil.copytree(), accelerating git fixture setup by ~50-70x.
"""

from __future__ import annotations

import atexit
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional, Tuple

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

_ENGINE_METADATA_PREFIXES = (
    ".git/",
    ".agents/update-journal.json",
    ".agents/update-engine.lock",
    ".agents/reports/",
)


def _entry_sha_compat(entry: dict) -> str:
    """Installed-state sha256 of a lock component entry."""
    return str(entry.get("installed_sha256") or entry.get("sha256") or "")


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


def _manifest_v3() -> dict:
    manifest = _manifest_v2()
    manifest["framework_version"] = "1.0.0-fix.3"
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


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "meta-project-tests",
        "GIT_AUTHOR_EMAIL": "tests@meta-project.invalid",
        "GIT_COMMITTER_NAME": "meta-project-tests",
        "GIT_COMMITTER_EMAIL": "tests@meta-project.invalid",
    }
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
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


def _seal_bundle_dir(bundle_root: Path, commit_sha: str, ref: str = "") -> None:
    files: dict[str, str] = {}
    for path in sorted(bundle_root.rglob("*")):
        if path.is_file() and path.name != "cache-manifest.json":
            files[path.relative_to(bundle_root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    payload = {
        "schema_version": "1.0.0",
        "commit_sha": commit_sha,
        "ref": ref or commit_sha,
        "files": files,
    }
    (bundle_root / "cache-manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _make_cache_dir(parent: Path, origin_sha: str) -> Path:
    bundle_root = parent / origin_sha
    bundle_root.mkdir(parents=True, exist_ok=True)
    _write_tree(bundle_root, _manifest_v1(), _origin_files_v1())
    _seal_bundle_dir(bundle_root, origin_sha)
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


def _build_raw_origin_repo(tmp: Path) -> Tuple[Path, str]:
    origin = tmp / "golden-origin-repo"
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


def _build_raw_target(tmp: Path) -> Path:
    target = tmp / "golden-target-app"
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


# Cached golden instances for fast copytree cloning
_GOLDEN_ORIGIN: Optional[Path] = None
_GOLDEN_FIRST_SHA: Optional[str] = None
_GOLDEN_TARGET: Optional[Path] = None
_GOLDEN_DIR: Optional[tempfile.TemporaryDirectory] = None


def _ensure_golden() -> None:
    global _GOLDEN_ORIGIN, _GOLDEN_FIRST_SHA, _GOLDEN_TARGET, _GOLDEN_DIR
    if _GOLDEN_ORIGIN is None:
        _GOLDEN_DIR = tempfile.TemporaryDirectory(prefix="meta_git_golden_")
        root = Path(_GOLDEN_DIR.name)
        _GOLDEN_ORIGIN, _GOLDEN_FIRST_SHA = _build_raw_origin_repo(root)
        _GOLDEN_TARGET = _build_raw_target(root)


def _cleanup_golden() -> None:
    global _GOLDEN_DIR
    if _GOLDEN_DIR is not None:
        try:
            _GOLDEN_DIR.cleanup()
        except Exception:
            pass
        _GOLDEN_DIR = None


atexit.register(_cleanup_golden)


def _make_origin_repo(tmp: Path) -> Tuple[Path, str]:
    """Return an isolated copy of the two-commit upstream origin repo."""
    _ensure_golden()
    assert _GOLDEN_ORIGIN is not None and _GOLDEN_FIRST_SHA is not None
    dest = tmp / "origin-repo"
    shutil.copytree(_GOLDEN_ORIGIN, dest)
    return dest, _GOLDEN_FIRST_SHA


def _make_target(tmp: Path) -> Path:
    """Return an isolated copy of the target scaffold app."""
    _ensure_golden()
    assert _GOLDEN_TARGET is not None
    dest = tmp / "target-app"
    shutil.copytree(_GOLDEN_TARGET, dest)
    return dest


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Read key from dict-like or attribute-style engine result."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _dump(obj: Any) -> str:
    """Serialize any engine result to inspectable text."""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except TypeError:
        return str(obj)


def _tree_snapshot(root: Path) -> dict[str, bytes]:
    """Mapping of {rel_path: content_bytes} for every regular file under root,
    excluding _ENGINE_METADATA_PREFIXES.
    """
    snapshot: dict[str, bytes] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(rel.startswith(prefix) for prefix in _ENGINE_METADATA_PREFIXES):
            continue
        snapshot[rel] = p.read_bytes()
    return snapshot


def _bundle_files(bundle: Any) -> dict:
    files = _get(bundle, "files")
    if not isinstance(files, dict):
        raise AssertionError(f"bundle['files'] must be a path->bytes mapping, got: {type(files)}")
    return files


def _write_fingerprint(root: Path) -> dict:
    """Zero-write snapshot: relative path -> (size, mtime_ns)."""
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
