#!/usr/bin/env python3
"""
scripts/_update_merge.py

Local adaptation preservation, 3-way merge helpers, protected patterns,
journal serialization, and report building (ADR #22 submodule).
Pure Python 3.10+ standard library, zero external dependencies.
"""

from __future__ import annotations

import base64
import fnmatch
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:  # package-style import
    from scripts.manage_reports import (
        collect_input_fingerprints,
        generate_run_id,
        get_git_state,
        save_report,
    )
except ImportError:
    try:
        from manage_reports import (
            collect_input_fingerprints,
            generate_run_id,
            get_git_state,
            save_report,
        )
    except ImportError:
        collect_input_fingerprints = None
        generate_run_id = None
        get_git_state = None
        save_report = None

try:
    from scripts.verify_identity import (
        evaluate_actor_admission,
        load_registry,
        resolve_actor_binding,
    )
except ImportError:
    try:
        from verify_identity import (
            evaluate_actor_admission,
            load_registry,
            resolve_actor_binding,
        )
    except ImportError:
        evaluate_actor_admission = None
        load_registry = None
        resolve_actor_binding = None

try:
    from scripts.check_boundaries import classify_path, parse_boundaries
except ImportError:
    try:
        from check_boundaries import classify_path, parse_boundaries
    except ImportError:
        classify_path = None
        parse_boundaries = None

try:
    from scripts._common import _utc_now_iso
except ImportError:
    from _common import _utc_now_iso

try:
    from scripts._update_bundle import (
        FRAMEWORK_LOCK_RELPATH,
        LOCK_SCHEMA_VERSION,
        PROJECT_BOUNDARIES_RELPATH,
        REPORT_TYPE,
        UPDATE_JOURNAL_RELPATH,
        LegacyDuplicateError,
        MixedBundleError,
        UpdateEngineError,
        _atomic_write_bytes,
        _components_of,
        _git_blob,
        _posix,
        _read_json,
        _sha256_bytes,
        _sha256_file,
        assert_within,
        load_bundle,
    )
except ImportError:
    from _update_bundle import (
        FRAMEWORK_LOCK_RELPATH,
        LOCK_SCHEMA_VERSION,
        PROJECT_BOUNDARIES_RELPATH,
        REPORT_TYPE,
        UPDATE_JOURNAL_RELPATH,
        LegacyDuplicateError,
        MixedBundleError,
        UpdateEngineError,
        _atomic_write_bytes,
        _components_of,
        _git_blob,
        _posix,
        _read_json,
        _sha256_bytes,
        _sha256_file,
        assert_within,
        load_bundle,
    )

DEFAULT_PROTECT_PATTERNS = (
    "scripts/check_boundaries.py",
    "*boundaries.md",
    ".github/workflows/**",
    ".github/CODEOWNERS",
    "tests/test_integrity.py",
    "LICENSE",
    ".gitignore",
)

# local_repo_data markers, HTML form (document/markup files):
# <!-- local_repo_data:TAG --> ... <!-- /local_repo_data:TAG -->
LOCAL_REPO_DATA_RE = re.compile(
    rb"<!--\s*local_repo_data:([A-Za-z0-9_.:-]+)\s*-->"  # opener
    rb".*?"                                              # preserved local payload
    rb"<!--\s*/local_repo_data:\1\s*-->",                # closer (same tag)
    re.DOTALL,
)

# local_repo_data markers, code form (code/config files, Wave D E2 D7):
# '# local_repo_data:TAG' ... '# /local_repo_data:TAG' (line-based).
HASH_LOCAL_REPO_DATA_RE = re.compile(
    rb"^[ \t]*#[ \t]*local_repo_data:([A-Za-z0-9_.:-]+)[ \t]*\r?\n"   # opener line
    rb".*?"                                                            # preserved local payload
    rb"^[ \t]*#[ \t]*/local_repo_data:\1[ \t]*(?:\r?\n|\Z)",           # closer line
    re.DOTALL | re.MULTILINE,
)

_HTML_MARKER_EXTENSIONS = frozenset({".md", ".html", ".xml"})
_HASH_MARKER_EXTENSIONS = frozenset(
    {".py", ".toml", ".yml", ".yaml", ".sh", ".cfg", ".ini"}
)


def _marker_regexes(rel: str) -> Tuple[Any, ...]:
    """Marker syntax selection per file extension (Wave D E2, D7):
    code/config extensions use the ``#``-comment form; document/markup
    extensions use the HTML-comment form; unknown extensions accept BOTH."""
    ext = Path(rel).suffix.lower()
    if ext in _HASH_MARKER_EXTENSIONS:
        return (HASH_LOCAL_REPO_DATA_RE,)
    if ext in _HTML_MARKER_EXTENSIONS:
        return (LOCAL_REPO_DATA_RE,)
    return (LOCAL_REPO_DATA_RE, HASH_LOCAL_REPO_DATA_RE)

RED_ZONE_REFUSAL_TEXT = (
    "no sanctioned mechanism exists for automated changes to protected "
    "components (Red-Zone sanction is an explicitly open item); apply a "
    "manual, user-confirmed change instead"
)



def _origin_base_candidate(
    bundle: Dict[str, Any], lock: Optional[Dict[str, Any]], rel: str, want_sha: str
) -> Optional[bytes]:
    """Merge-base candidate fetched from the ORIGIN repository at the
    lock-recorded source commit (Wave D dispatcher tail, live S1): a v1 -> v2
    update on a consumer without a populated cache must still find its base
    in the origin's git history — the lock pins the exact commit the current
    content was installed from. Content is hash-verified against the lock
    record before use; any failure (dead origin, missing path, hash drift)
    returns None so the needs_base refusal path stays fail-closed."""
    origin_repo = str((bundle or {}).get("origin_repo") or "")
    sha = str(((lock or {}).get("source") or {}).get("commit_sha") or "")
    if not origin_repo or not re.fullmatch(r"[0-9a-f]{40}", sha):
        return None
    try:
        blob = _git_blob(origin_repo, sha, rel)
    except MixedBundleError:
        return None
    if _sha256_bytes(blob) == want_sha:
        return blob
    return None


def _extract_local_blocks(
    data: bytes, rel: str = ""
) -> List[Tuple[bytes, bytes]]:
    """All local_repo_data blocks applicable to ``rel`` (syntax per
    extension, D7); duplicate raw blocks are reported once."""
    blocks: List[Tuple[bytes, bytes]] = []
    seen: List[bytes] = []
    for marker_re in _marker_regexes(rel):
        for m in marker_re.finditer(data):
            block = m.group(0)
            if block not in seen:
                seen.append(block)
                blocks.append((block, m.group(1)))
    return blocks


def _reinject_local_blocks(
    new_bytes: bytes, local_blocks: List[Tuple[bytes, bytes]]
) -> bytes:
    """Re-inject extracted local_repo_data blocks into fresh upstream bytes
    (append order preserved; blocks already present upstream are skipped)."""
    merged = new_bytes
    for block, _tag in local_blocks:
        if block in merged:
            continue
        if merged and not merged.endswith(b"\n"):
            merged += b"\n"
        if not block.endswith(b"\n"):
            block = block + b"\n"
        merged += block
    return merged


def _merge_marked(
    base: bytes, local: bytes, new: bytes, rel: str = ""
) -> Tuple[Optional[bytes], List[bytes]]:
    """Three-way merge honoring local_repo_data blocks (syntax selected per
    ``rel`` extension, D7).

    Returns (merged_bytes, preserved_tags) when the local tree differs from
    the base ONLY inside marker-wrapped blocks; returns (None, []) when an
    unmarked local modification exists (conflict — never silently
    overwritten).
    """
    local_blocks = _extract_local_blocks(local, rel)
    stripped_local = local
    stripped_base = base
    for marker_re in _marker_regexes(rel):
        stripped_local = marker_re.sub(b"", stripped_local)
        stripped_base = marker_re.sub(b"", stripped_base)
    if stripped_local.strip(b" \t\r\n") != stripped_base.strip(b" \t\r\n"):
        return None, []
    preserved: List[bytes] = [tag for _block, tag in local_blocks]
    return _reinject_local_blocks(new, local_blocks), preserved


def _is_protected(path: str, patterns: Tuple[str, ...]) -> bool:
    posix = _posix(path)
    return any(fnmatch.fnmatch(posix, _posix(p)) for p in patterns)


def _legacy_duplicates(repo_root: Path, manifest: Dict[str, Any]) -> None:
    """Legacy-path transition: canonical location is ``scripts/``. When a
    manifest component has a legacy copy under ``.agents/scripts/``:
    identical -> migration note; divergent -> HALT with a report naming both
    paths and hashes. Never silently use the first found."""
    notes: List[Dict[str, Any]] = []
    for comp in _components_of(manifest):
        rel = _posix(comp.get("path", ""))
        if not rel.startswith("scripts/"):
            continue
        canonical = repo_root / rel
        legacy_rel = ".agents/" + rel
        legacy = repo_root / legacy_rel
        if not legacy.is_file():
            continue
        legacy_sha = _sha256_file(legacy)
        if not canonical.is_file():
            notes.append({
                "path": legacy_rel,
                "sha256": legacy_sha,
                "note": "legacy copy without a canonical counterpart: schedule explicit migration to " + rel,
            })
            continue
        canonical_sha = _sha256_file(canonical)
        if canonical_sha != legacy_sha:
            raise LegacyDuplicateError(
                f"divergent duplicate copies of managed component '{rel}': "
                f"canonical '{rel}' sha256={canonical_sha} vs legacy "
                f"'{legacy_rel}' sha256={legacy_sha}; HALT: never silently "
                "use the first found — resolve via an explicit migration "
                "before updating"
            )
        notes.append({
            "path": legacy_rel,
            "sha256": legacy_sha,
            "note": "legacy copy identical to the canonical one: migrate (delete legacy) at next update",
        })
    return notes


# ---------------------------------------------------------------------------
# Perimeter: identity admission, project boundaries, runtime layout (Wave D E2)
# ---------------------------------------------------------------------------


def _actor_admission_denial(repo_root: Path, actor_id: str) -> Optional[str]:
    """Identity admission for the apply perimeter (Wave D E2, T6.1, п.5a).

    Mirrors ``scripts/inspect_meta_project.py``'s defensive import: when
    ``verify_identity`` is unavailable the check degrades to a no-op.
    Identity-LESS projects (no registry, or a registry without recorded role
    bindings — the bootstrap state, cf. manage-meta-project Phase 0.5) are
    not blocked either; otherwise the actor must be registered AND active on
    an active installation. Returns None when admitted, else a denial reason
    starting with ``actor not admitted``."""
    if resolve_actor_binding is None:
        return None
    repo_root = Path(repo_root)
    registry: Optional[Dict[str, Any]] = None
    if load_registry is not None:
        try:
            registry, _err = load_registry(repo_root)
        except Exception:  # noqa: BLE001 - admission must never crash apply setup
            registry = None
    if not isinstance(registry, dict) or not (registry.get("roles") or {}):
        return None  # identity-less installation (bootstrap): admission not applicable
    try:
        found, binding = resolve_actor_binding(repo_root, str(actor_id or ""))
    except Exception:  # noqa: BLE001 - fail closed on lookup errors
        found, binding = False, None
    if not found or not isinstance(binding, dict):
        return (
            f"actor not admitted: actor_id '{actor_id}' is not registered in "
            ".agents/meta-project.json; resolve the qualified identity "
            "(scripts/verify_identity.py) before applying updates"
        )
    if evaluate_actor_admission is not None:
        denial = evaluate_actor_admission(registry, binding)
        if denial:
            return f"actor not admitted: {denial}"
    return None


def _project_red_zones(repo_root: Path) -> Optional[Dict[str, List[str]]]:
    """Parse the project's ``boundaries.md`` into zone patterns (T6.2,
    п.5b). Returns None when the file is absent or the zone classifier is
    unavailable (defensive import, fail-open consult — the engine's own
    DEFAULT protect patterns always remain in force)."""
    if parse_boundaries is None:
        return None
    path = Path(repo_root) / PROJECT_BOUNDARIES_RELPATH
    if not path.is_file():
        return None
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        return parse_boundaries(content)
    except Exception:  # noqa: BLE001 - the consult must never break planning
        return None


def _project_red_reason(
    rel: str,
    dest_rel: str,
    zones: Optional[Dict[str, List[str]]],
) -> Optional[str]:
    """Explanatory string when the component identity path or its resolved
    on-disk target is classified Red by the project boundaries; else None.
    Only an explicit Red classification protects here (unmapped/Black paths
    are the boundary gate's commit-time business; the engine's DEFAULT
    patterns cover the framework's own protected set)."""
    if not zones or classify_path is None:
        return None
    for candidate in dict.fromkeys((rel, dest_rel)):
        try:
            zone, reason = classify_path(candidate, zones)
        except Exception:  # noqa: BLE001
            continue
        if zone == "red":
            return f"project boundaries Red zone match ({reason})"
    return None


_SKILL_RUNTIME_LAYOUT_RE = re.compile(r"^skills/([^/]+)/SKILL\.md$")
# Wave E Lane P2: skill resources ship WITH the skill (bootstrap invariant),
# so a resource component follows its skill into the runtime layout.
_SKILL_RESOURCE_RUNTIME_LAYOUT_RE = re.compile(r"^skills/([^/]+)/resources/(.+)$")


def _resolve_target(
    rel: str,
    repo_root: Path,
    lock_entry: Optional[Dict[str, Any]],
) -> str:
    """Resolved on-disk destination of a manifest component (T6.5).

    A previously recorded lock ``target`` stays authoritative (no silent
    migration of installed components); otherwise ``skills/<name>/SKILL.md``
    maps to the runtime layout ``.agents/skills/<name>/SKILL.md``, and
    ``skills/<name>/resources/<file>`` maps to
    ``.agents/skills/<name>/resources/<file>`` (Wave E Lane P2), when the
    target repository has ``.agents/skills/``; everything else installs at
    the distribution path."""
    recorded = _posix((lock_entry or {}).get("target") or "")
    if recorded:
        return recorded
    repo_root = Path(repo_root)
    match = _SKILL_RUNTIME_LAYOUT_RE.match(_posix(rel))
    if match and (repo_root / ".agents" / "skills").is_dir():
        return f".agents/skills/{match.group(1)}/SKILL.md"
    res_match = _SKILL_RESOURCE_RUNTIME_LAYOUT_RE.match(_posix(rel))
    if res_match and (repo_root / ".agents" / "skills").is_dir():
        return f".agents/skills/{res_match.group(1)}/resources/{res_match.group(2)}"
    return _posix(rel)



def _save_journal(repo_root: Path, journal: Dict[str, Any]) -> None:
    path = assert_within(Path(repo_root), UPDATE_JOURNAL_RELPATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(journal, indent=2, ensure_ascii=False) + "\n"
    tmp = path.parent / f".update-journal.tmp-{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def _b64(data: Optional[bytes]) -> Optional[str]:
    if data is None:
        return None
    return base64.b64encode(data).decode("ascii")


def _unb64(value: Optional[str]) -> Optional[bytes]:
    if value is None:
        return None
    return base64.b64decode(value.encode("ascii"))


# ---------------------------------------------------------------------------
# Plan serialization: CLI plan output must round-trip into `apply --plan-file`
# ---------------------------------------------------------------------------


def _plan_to_jsonable(plan: Dict[str, Any], full: bool = False) -> Dict[str, Any]:
    """Plan -> JSON-safe dict for CLI output (Wave D E2, T6.6).

    Summary mode (default): actions are described by ops/paths/shas — bytes
    values (content) are OMITTED entirely; the printed plan stays human- and
    audit-readable without base64 blobs. Full mode (``--full``): bytes values
    become ``<key>_b64`` strings, so a user-approved plan can be saved to a
    file and reloaded by ``apply --plan-file`` verbatim. A content-less
    summary plan is still executable: apply re-materializes content from the
    pinned source and hash-verifies it against ``upstream_sha256``."""
    out: Dict[str, Any] = {}
    for key, value in plan.items():
        if key == "actions" and isinstance(value, list):
            jsonable_actions: List[Any] = []
            for action in value:
                if not isinstance(action, dict):
                    jsonable_actions.append(action)
                    continue
                entry: Dict[str, Any] = {}
                for a_key, a_value in action.items():
                    if isinstance(a_value, bytes):
                        if full:
                            entry[f"{a_key}_b64"] = _b64(a_value)
                        # summary mode: content bytes are simply omitted
                    else:
                        entry[a_key] = a_value
                jsonable_actions.append(entry)
            out["actions"] = jsonable_actions
        else:
            out[key] = value
    return out


def _plan_from_jsonable(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Inverse of _plan_to_jsonable: restore bytes action content from
    ``<key>_b64`` fields."""
    plan = dict(obj or {})
    actions: List[Any] = []
    for action in plan.get("actions") or []:
        if not isinstance(action, dict):
            actions.append(action)
            continue
        entry = dict(action)
        for key in [k for k in entry if str(k).endswith("_b64")]:
            raw = entry.pop(key)
            try:
                entry[key[:-4]] = _unb64(raw)
            except (ValueError, TypeError) as exc:
                raise UpdateEngineError(
                    f"plan carries an invalid base64 payload for "
                    f"'{key[:-4]}': {exc}"
                )
        actions.append(entry)
    plan["actions"] = actions
    return plan


def _rematerialize_plan_content(
    repo_root: Path,
    plan: Dict[str, Any],
    cache_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Fill content bytes into a content-less (summary-mode) approved plan
    (Wave D E2, T6.6).

    Content is re-materialized from the plan's OWN pinned source revision
    (never a moving ref) and hash-verified against the action's
    ``upstream_sha256``. ``merge`` actions re-inject the local_repo_data
    blocks extracted from the on-disk local file — which apply re-verifies
    against ``expected_before_sha256`` before writing — so the materialized
    bytes equal the ones a full plan would carry. ``adopt`` actions carry no
    content by design."""
    repo_root = Path(repo_root)
    pin_block = plan.get("pin") or {}
    plan_sha = str(pin_block.get("commit_sha", "") or "")
    contentless = [
        a for a in plan.get("actions") or []
        if isinstance(a, dict) and "content" not in a
        and a.get("op") != "adopt"
    ]
    if not contentless:
        return plan
    if not re.fullmatch(r"[0-9a-f]{40}", plan_sha):
        raise UpdateEngineError(
            "approved plan carries no valid source pin; cannot re-materialize "
            "content for its content-less actions"
        )
    bundle = load_bundle(
        {
            "commit_sha": plan_sha,
            "origin_repo": str(pin_block.get("source", "") or ""),
            "ref": str(pin_block.get("ref") or plan_sha),
        },
        cache_dir,
        seal_cache=True,
    )
    bundle_files = bundle.get("files") or {}
    for action in contentless:
        rel = _posix(action.get("path", ""))
        upstream = bundle_files.get(rel)
        if upstream is None:
            raise UpdateEngineError(
                f"approved plan action '{rel}' carries no content and the "
                f"pinned source {plan_sha} does not provide the component"
            )
        expected = str(action.get("upstream_sha256", "") or "")
        if expected and _sha256_bytes(upstream) != expected:
            raise UpdateEngineError(
                f"re-materialized content for '{rel}' does not hash-match the "
                f"plan's upstream_sha256 (plan pins {expected}, pinned source "
                f"provides {_sha256_bytes(upstream)}); refusing to apply"
            )
        if action.get("op") == "merge":
            # SEC-1: the read of the local target is containment-checked.
            local_path = assert_within(
                repo_root, _posix(action.get("target") or rel)
            )
            if not local_path.is_file():
                raise UpdateEngineError(
                    f"approved merge action for '{rel}' has no local file to "
                    "extract local_repo_data blocks from; re-plan against the "
                    "current target state"
                )
            local_bytes = local_path.read_bytes()
            action["content"] = _reinject_local_blocks(
                upstream, _extract_local_blocks(local_bytes, rel)
            )
        else:
            action["content"] = upstream
    return plan


# ---------------------------------------------------------------------------
# Update report (via the canonical report engine)
# ---------------------------------------------------------------------------


def _build_update_report(
    repo_root: Path,
    installation_id: str,
    actor_id: str,
    plan: Dict[str, Any],
    applied_actions: List[Dict[str, Any]],
    lock_before: Optional[Dict[str, Any]],
    plan_file: Optional[str] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    registry: Dict[str, Any] = {}
    registry_path = repo_root / ".agents" / "meta-project.json"
    if registry_path.is_file():
        try:
            loaded = _read_json(registry_path)
            if isinstance(loaded, dict):
                registry = loaded
        except (OSError, ValueError):
            registry = {}
    project_id = str(registry.get("project_id") or "unknown-project")
    harness_id = str(
        ((registry.get("installations") or {}).get(installation_id) or {}).get(
            "harness_id"
        )
        or "unknown-harness"
    )

    meta = plan.get("meta") or {}
    before_source = (lock_before or {}).get("source") or {}
    before = str(before_source.get("commit_sha") or "unknown")
    # U7 (Wave F FX, T-X5): the post-update version is split into its two
    # identities — the human-readable framework version AND the exact pinned
    # commit sha (a version string alone is not an audit-grade pin).
    after = {
        "framework_version": str(meta.get("framework_version") or ""),
        "commit_sha": str(meta.get("commit_sha") or before),
    }

    fingerprints: List[Dict[str, str]] = []
    if collect_input_fingerprints is not None:
        raw = collect_input_fingerprints(repo_root)
        for rel, digest in sorted(raw.items()):
            if digest:
                fingerprints.append({"path": rel, "sha256": digest})
    lock_digest = None
    lock_path = repo_root / FRAMEWORK_LOCK_RELPATH
    if lock_path.is_file():
        try:
            lock_digest = _sha256_file(lock_path)
        except OSError:
            lock_digest = None
    if lock_digest:
        fingerprints.append({"path": FRAMEWORK_LOCK_RELPATH, "sha256": lock_digest})

    preserved_adaptations = [
        {
            "path": action["path"],
            "detail": "local_repo_data block(s) preserved: "
            + ", ".join(action.get("preserved_blocks") or []),
        }
        for action in applied_actions
        if action.get("op") == "merge"
    ]

    affected = [
        {
            "path": action["path"],
            "kind": action.get("kind", ""),
            "action": action.get("op", "updated"),
        }
        for action in applied_actions
    ]

    checks = [
        {
            "name": "update_apply",
            "command": "python scripts/update_meta_project.py apply",
            "status": "pass",
            "output_summary": (
                f"{len(applied_actions)} components affected, "
                f"{len(plan.get('conflicts') or [])} conflicts, "
                f"{len(plan.get('needs_base') or [])} needs-base, "
                f"{len(plan.get('protected') or [])} protected-refused, "
                f"journal written to {UPDATE_JOURNAL_RELPATH}"
            ),
        }
    ]

    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "report_type": REPORT_TYPE,
        "project_id": project_id,
        "installation_id": installation_id,
        "harness_id": harness_id,
        "actor_id": actor_id,
        # U11 (Wave F FX, T-X5): the report carries the APPLY RUN's run_id —
        # the same id the journal records — so restore can mark THIS report
        # "restored" (one run, one journal, one report).
        "run_id": str(run_id or (generate_run_id(REPORT_TYPE) if generate_run_id else REPORT_TYPE)),
        "created_at": _utc_now_iso(),
        "status": "completed",
        "git_state": (get_git_state(repo_root) if get_git_state else {}),
        "input_fingerprints": fingerprints,
        "versions": {"before": before, "after": after},
        "source": {
            "ref": str(meta.get("ref") or "unknown"),
            "commit_sha": str(meta.get("commit_sha") or "unknown"),
            "origin": str(meta.get("origin") or "unknown"),
        },
        "affected_components": affected,
        "approved_plan_file": plan_file,
        "executed_migrations": [],
        "preserved_adaptations": preserved_adaptations,
        "conflicts": [],
        "checks": checks,
        "remaining_manual_actions": [],
    }


# ---------------------------------------------------------------------------
# Apply (atomic, journaled) and restore
# ---------------------------------------------------------------------------



def _mark_update_report_restored(repo_root: Path, run_id: str) -> Optional[str]:
    """U11 (Wave F FX, T-X5): mark the update report of ``run_id``
    ``status: "restored"`` — in place, preserving the audit trail. Returns
    the report's repo-relative path, or None when no matching report exists
    (e.g. the report engine was unavailable during apply)."""
    reports_root = Path(repo_root) / ".agents" / "reports"
    needle = str(run_id or "").strip()
    if not needle or not reports_root.is_dir():
        return None
    marked: Optional[Path] = None
    for update_dir in sorted(reports_root.glob("*/update")):
        if not update_dir.is_dir():
            continue
        for report_file in sorted(update_dir.glob("*.json")):
            if report_file.name == "latest.json":
                continue
            try:
                data = _read_json(report_file)
            except (OSError, ValueError):
                continue
            if (
                not isinstance(data, dict)
                or str(data.get("report_type", "")) != REPORT_TYPE
                or str(data.get("run_id", "")) != needle
            ):
                continue
            data["status"] = "restored"
            try:
                assert_within(repo_root, _posix(
                    report_file.relative_to(Path(repo_root))
                ))
                _atomic_write_bytes(
                    report_file,
                    (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode(
                        "utf-8"
                    ),
                )
            except (OSError, ValueError, UpdateEngineError):
                continue
            marked = report_file
            # Keep the latest.json pointer coherent with the marked report.
            pointer = update_dir / "latest.json"
            try:
                if pointer.is_file():
                    ptr = _read_json(pointer)
                    if isinstance(ptr, dict) and str(ptr.get("run_id", "")) == needle:
                        ptr["status"] = "restored"
                        assert_within(repo_root, _posix(
                            pointer.relative_to(Path(repo_root))
                        ))
                        _atomic_write_bytes(
                            pointer,
                            (json.dumps(ptr, indent=2, ensure_ascii=False) + "\n").encode(
                                "utf-8"
                            ),
                        )
            except (OSError, ValueError, UpdateEngineError):
                pass
    if marked is None:
        return None
    return _posix(marked.relative_to(Path(repo_root)))


