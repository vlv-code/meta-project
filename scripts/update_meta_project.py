#!/usr/bin/env python3
"""
Managed Update Engine for the Meta-Project framework (scripts/update_meta_project.py)

Wave 0.9.0, Task C2. Deterministic, crash-recoverable update of an installed
framework (ADR #21 contracts):

* **SHA pinning without releases:** a ref (branch/tag/SHA) resolves to ONE
  exact commit SHA; every component is materialized from that single SHA
  (raw blobs via `git cat-file <sha>:<path>` — byte-exact, no EOL smudging);
  mixing revisions in one update is prohibited.
* **Manifest != lock:** the bundle manifest describes ALL available
  components; the project lock (``.agents/framework-lock.json``) records the
  actually-installed SUBSET — component schema v2 carries base_sha256
  (pinned upstream bytes) and installed_sha256 (on-disk bytes) per component
  (``target`` = resolved on-disk destination); v1 entries (single
  ``sha256``) are read as base = installed.
* **The plan pins what apply may do:** a plan is computed against ONE source
  revision (``pin``) and one target state (per-action
  ``expected_before_sha256``); apply re-verifies both and refuses with ZERO
  writes on any deviation. The CLI apply executes a user-approved plan file
  (``--plan-file``) or prints a ``[RE-PLANNED]`` notice when it computes its
  own plan.
* **Integral, VERIFIED cache fallback:** ``<cache_dir>/<commit_sha>/`` holds
  a full single-revision bundle; a partial cache is refused loudly
  (``PartialCacheError``), never mixed. SEC-2 (Wave F FX, T-X2): every cache
  load is verified — a sealed entry (``cache-manifest.json``: per-file
  sha256 + the ref-pin it was built from) is hash-checked on load and
  cross-verified against the origin blobs whenever the origin provides the
  pinned commit; an unsealed entry must cross-verify against the origin or
  is refused (``CacheVerificationError``). apply seals a cross-verified
  entry so later offline loads can verify it.
* **Containment (SEC-1, Wave F FX, T-X1):** managed paths must be relative
  without ``..`` segments (``_posix`` refuses absolutes, drive letters, UNC
  shares and traversal), every destination read/write is resolved and
  contained inside its root (``assert_within``), and existing symlink
  destinations are refused — a hostile manifest, lock, plan file, journal or
  cache cannot move a single byte outside the repository (or cache) root.
* **Serialization (SEC-4, Wave F FX, T-X3):** apply AND restore hold
  ``.agents/update-engine.lock`` exclusively (non-blocking); a concurrent
  second engine operation is refused with an ``ENGINE_BUSY`` envelope and
  writes nothing.
* **Three-way merge with base honesty:** for locally modified components the
  merge base is cached content whose sha256 matches the lock record; without
  a matching base the plan yields a ``needs_base`` entry, never a "safe
  merge" claim. ``local_repo_data``-marked blocks are re-injected into the
  merged content; unmarked local edits surface as explicit conflicts.
* **Red Zone refusal:** automated changes to protected components are
  refused: no sanctioned mechanism exists (explicitly open item). The
  perimeter is enforced in layers (Wave D E2): apply requires an ADMITTED
  actor (registered + active binding in ``.agents/meta-project.json``;
  identity-less bootstrap projects are not blocked), and every component
  target path is additionally consulted against the project's
  ``boundaries.md`` Red zone and the ``--protect`` patterns (union with the
  engine defaults).
* **Offline exact-SHA cache:** when the origin cannot resolve an EXACT
  40-hex ref but an integral cache bundle exists for that SHA, the update
  proceeds with ``origin: cache``; refs that are not exact SHAs still
  require a resolvable origin (Wave D E2, D2).
* **Manifest readability fallback:** the engine reads ``manifest.json`` at
  the source root and falls back to ``templates/release_manifest.json``
  (the canonical framework repository layout).
* **Atomicity & recovery:** per-file atomic replace via temp + ``os.replace``,
  an operation journal (``.agents/update-journal.json``) with before/after
  sha256 (and content), and a restore mode that reverts ONLY the engine's own
  changes, keeping third-party edits made during the apply window. The lock
  write is itself journaled: restore rolls back files AND
  ``.agents/framework-lock.json`` to the coherent pre-apply state.
* **check/plan are strictly read-only:** zero writes to the project, reports,
  cache, and lock files.
* **Legacy transition:** canonical runtime location is ``scripts/``; a
  divergent legacy copy under ``.agents/scripts/`` halts the update with a
  report of both paths and hashes.

Update reports are recorded through the canonical report engine
(``scripts/manage_reports.save_report`` with ``report_type="update"``).

Zero-dependency: Python 3.10+ stdlib + Git CLI only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple
import uuid

try:  # package-style import (tests: from scripts.update_meta_project import ...)
    from scripts.manage_reports import (
        collect_input_fingerprints,
        generate_run_id,
        get_git_state,
        save_report,
    )
except ImportError:  # direct script execution: python scripts/update_meta_project.py
    try:
        from manage_reports import (
            collect_input_fingerprints,
            generate_run_id,
            get_git_state,
            save_report,
        )
    except ImportError:  # report engine unavailable in this environment
        collect_input_fingerprints = None
        generate_run_id = None
        get_git_state = None
        save_report = None

try:  # identity admission (Wave D E2, T6.1): defensive import mirroring
    # scripts/inspect_meta_project.py — the engine degrades to a no-op
    # admission check when the identity engine is unavailable.
    from scripts.verify_identity import (
        evaluate_actor_admission,
        load_registry,
        resolve_actor_binding,
    )
except ImportError:  # direct script execution: python scripts/update_meta_project.py
    try:
        from verify_identity import (
            evaluate_actor_admission,
            load_registry,
            resolve_actor_binding,
        )
    except ImportError:  # identity engine unavailable in this environment
        evaluate_actor_admission = None
        load_registry = None
        resolve_actor_binding = None

try:  # project boundary zone classifier (Wave D E2, T6.2): defensive import
    from scripts.check_boundaries import classify_path, parse_boundaries
except ImportError:  # direct script execution: python scripts/update_meta_project.py
    try:
        from check_boundaries import classify_path, parse_boundaries
    except ImportError:  # boundary gate unavailable in this environment
        classify_path = None
        parse_boundaries = None

try:  # shared helpers (ADR #22): package-style import (tests: from
    # scripts.update_meta_project import ...)
    from scripts._common import _error_envelope, _utc_now_iso
except ImportError:  # direct script execution: python scripts/update_meta_project.py
    from _common import _error_envelope, _utc_now_iso


try:
    from scripts._update_bundle import (
        CACHE_MANIFEST_RELPATH,
        CANONICAL_MANIFEST_RELPATH,
        ENGINE_LOCK_RELPATH,
        FRAMEWORK_LOCK_RELPATH,
        LOCK_SCHEMA_VERSION,
        MANIFEST_RELPATH,
        PROJECT_BOUNDARIES_RELPATH,
        REPORT_TYPE,
        UPDATE_JOURNAL_RELPATH,
        _EXACT_SHA_RE,
        _WINDOWS_DRIVE_RE,
        ApplyError,
        CacheVerificationError,
        EngineBusyError,
        LegacyDuplicateError,
        MixedBundleError,
        PartialCacheError,
        PathContainmentError,
        ProtectedComponentError,
        SourceResolutionError,
        UpdateEngineError,
        _atomic_write_bytes,
        _collect_base_candidates,
        _components_of,
        _entry_base_sha,
        _entry_installed_sha,
        _fetch_pinned_tree,
        _filter_bundle,
        _git_blob,
        _installed_match,
        _load_cache_manifest,
        _lock_payload_bytes,
        _posix,
        _read_bundle_tree,
        _read_json,
        _run_git,
        _sha256_bytes,
        _sha256_file,
        _split_list,
        _verify_cache_against_origin,
        assert_within,
        build_cache_manifest,
        default_cache_dir,
        engine_operation_lock,
        file_lock,
        load_bundle,
        read_lock,
        resolve_pin_with_cache_fallback,
        resolve_source,
        seal_cache_entry,
        write_lock_atomic,
    )
except ImportError:
    from _update_bundle import (
        CACHE_MANIFEST_RELPATH,
        CANONICAL_MANIFEST_RELPATH,
        ENGINE_LOCK_RELPATH,
        FRAMEWORK_LOCK_RELPATH,
        LOCK_SCHEMA_VERSION,
        MANIFEST_RELPATH,
        PROJECT_BOUNDARIES_RELPATH,
        REPORT_TYPE,
        UPDATE_JOURNAL_RELPATH,
        _EXACT_SHA_RE,
        _WINDOWS_DRIVE_RE,
        ApplyError,
        CacheVerificationError,
        EngineBusyError,
        LegacyDuplicateError,
        MixedBundleError,
        PartialCacheError,
        PathContainmentError,
        ProtectedComponentError,
        SourceResolutionError,
        UpdateEngineError,
        _atomic_write_bytes,
        _collect_base_candidates,
        _components_of,
        _entry_base_sha,
        _entry_installed_sha,
        _fetch_pinned_tree,
        _filter_bundle,
        _git_blob,
        _installed_match,
        _load_cache_manifest,
        _lock_payload_bytes,
        _posix,
        _read_bundle_tree,
        _read_json,
        _run_git,
        _sha256_bytes,
        _sha256_file,
        _split_list,
        _verify_cache_against_origin,
        assert_within,
        build_cache_manifest,
        default_cache_dir,
        engine_operation_lock,
        file_lock,
        load_bundle,
        read_lock,
        resolve_pin_with_cache_fallback,
        resolve_source,
        seal_cache_entry,
        write_lock_atomic,
    )

try:
    from scripts._update_merge import (
        DEFAULT_PROTECT_PATTERNS,
        HASH_LOCAL_REPO_DATA_RE,
        LOCAL_REPO_DATA_RE,
        RED_ZONE_REFUSAL_TEXT,
        _HASH_MARKER_EXTENSIONS,
        _HTML_MARKER_EXTENSIONS,
        _SKILL_RESOURCE_RUNTIME_LAYOUT_RE,
        _SKILL_RUNTIME_LAYOUT_RE,
        _actor_admission_denial,
        _b64,
        _build_update_report,
        _extract_local_blocks,
        _is_protected,
        _legacy_duplicates,
        _mark_update_report_restored,
        _marker_regexes,
        _merge_marked,
        _origin_base_candidate,
        _plan_from_jsonable,
        _plan_to_jsonable,
        _project_red_reason,
        _project_red_zones,
        _reinject_local_blocks,
        _rematerialize_plan_content,
        _resolve_target,
        _save_journal,
        _unb64,
    )
except ImportError:
    from _update_merge import (
        DEFAULT_PROTECT_PATTERNS,
        HASH_LOCAL_REPO_DATA_RE,
        LOCAL_REPO_DATA_RE,
        RED_ZONE_REFUSAL_TEXT,
        _HASH_MARKER_EXTENSIONS,
        _HTML_MARKER_EXTENSIONS,
        _SKILL_RESOURCE_RUNTIME_LAYOUT_RE,
        _SKILL_RUNTIME_LAYOUT_RE,
        _actor_admission_denial,
        _b64,
        _build_update_report,
        _extract_local_blocks,
        _is_protected,
        _legacy_duplicates,
        _mark_update_report_restored,
        _marker_regexes,
        _merge_marked,
        _origin_base_candidate,
        _plan_from_jsonable,
        _plan_to_jsonable,
        _project_red_reason,
        _project_red_zones,
        _reinject_local_blocks,
        _rematerialize_plan_content,
        _resolve_target,
        _save_journal,
        _unb64,
    )

def check_updates(
    repo_root: Path,
    source: str,
    ref: str,
    cache_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Read-only availability and drift check (zero-write).

    Diagnoses every lock-recorded component against the working tree and
    the pinned bundle. A locally modified installed component is classified
    as 'diverged' with unknown origin — the engine never assumes such an
    edit is upstream content.
    """
    repo_root = Path(repo_root)
    # U6 (Wave F FX, T-X4): check answers through the SAME source resolution
    # as plan/apply — a dead origin with an exact-SHA ref and a verified
    # integral cache yields ONE answer for the repo state, not a check
    # failure where apply would succeed.
    pin = resolve_pin_with_cache_fallback(source, ref, cache_dir)
    bundle = load_bundle(pin, cache_dir)
    lock = read_lock(repo_root)

    lock_components = (lock or {}).get("components") or []
    lock_by_path = {
        _posix(c.get("path", "")): c
        for c in lock_components
        if isinstance(c, dict) and _posix(c.get("path", ""))
    }

    bundle_files = bundle.get("files") or {}
    diagnostics: List[Dict[str, Any]] = []
    drifted: List[str] = []
    updates: List[Dict[str, Any]] = []

    for path in sorted(lock_by_path):
        entry = lock_by_path[path]
        # Runtime layout (T6.5): a recorded ``target`` destination stays
        # authoritative — diagnose the file where it actually lives.
        local = repo_root / _posix(entry.get("target") or path)
        recorded = _entry_installed_sha(entry)
        if not local.is_file():
            diagnostics.append({
                "path": path,
                "status": "missing",
                "detail": "lock-recorded component is absent from the working tree",
            })
            drifted.append(path)
            continue
        local_bytes = local.read_bytes()
        matched, eol_only = _installed_match(local_bytes, recorded)
        if recorded and not matched:
            diagnostics.append({
                "path": path,
                "status": "diverged",
                "origin": "unknown",
                "detail": (
                    "installed content differs from the lock record: local "
                    "edit of unknown origin (drifted from the pinned "
                    "installation); update engine will treat it via merge "
                    "base or surface a conflict"
                ),
            })
            drifted.append(path)
        elif eol_only:
            # Wave G Lane H: a fresh autocrlf checkout smudges LF-installed
            # files to CRLF. Line-endings-only difference is NOT drift — the
            # content matches the installation record (an EOL-only flip is
            # not tampering; cache-manifest and origin cross-verification
            # remain byte-exact). Surface an explicit diagnostic instead.
            diagnostics.append({
                "path": path,
                "status": "eol_normalized",
                "detail": (
                    "working-copy bytes differ from the lock record by "
                    "CRLF/LF line endings only (autocrlf checkout); content "
                    "matches the installation record"
                ),
            })

    for comp in _components_of(bundle.get("manifest") or {}):
        path = _posix(comp.get("path", ""))
        if path not in lock_by_path:
            continue
        new_sha = _sha256_bytes(bundle_files.get(path, b""))
        if new_sha != _entry_installed_sha(lock_by_path[path]):
            updates.append({
                "path": path,
                "kind": comp.get("kind", ""),
                "action": "update_available",
            })

    return {
        "source": {
            "repository": pin["origin_repo"],
            "ref": pin.get("ref") or ref,
            "commit_sha": pin["commit_sha"],
            "origin": bundle.get("origin"),
        },
        "lock_present": lock is not None,
        "updates_available": updates,
        "drifted": drifted,
        "diagnostics": diagnostics,
        "status": "updates_available" if updates else "up_to_date",
    }



def plan_updates(
    repo_root: Path,
    bundle: Dict[str, Any],
    lock: Optional[Dict[str, Any]],
    protect_patterns: Optional[Tuple[str, ...]] = None,
    adopt_existing: bool = False,
) -> Dict[str, Any]:
    """Compute the three-way merge plan. STRICTLY READ-ONLY (zero-write).

    Returns PlanResult: {actions, conflicts, protected, needs_base, pin}
    plus informational keys (up_to_date, legacy, meta). Actions carry the
    exact bytes to write, the resolved on-disk target, the pinned upstream
    sha256, and expected_before_sha256 — the target state this plan was
    computed against (None for creates), which apply_updates re-verifies
    before writing (п.4: the plan pins what apply may do). Base-less local
    modifications become needs_base entries, never "safe merge" actions.

    Perimeter (Wave D E2):
    * ``protect_patterns`` are ADDITIONAL glob patterns united with
      DEFAULT_PROTECT_PATTERNS (T6.2) — user patterns never replace the
      defaults;
    * every component identity path and its resolved target path is
      consulted against the project's ``.agents/project_knowledge/
      boundaries.md`` Red zone (п.5b);
    * ``adopt_existing`` (friction 5): an unknown-origin local file whose
      bytes hash-equal the pinned upstream content becomes an ``adopt``
      action (lock record only, bytes untouched) instead of a conflict.
    """
    repo_root = Path(repo_root)
    bundle_files = bundle.get("files") or {}
    manifest = bundle.get("manifest") or {}
    lock = lock or {}
    lock_components = lock.get("components") or []
    lock_by_path = {
        _posix(c.get("path", "")): c
        for c in lock_components
        if isinstance(c, dict) and _posix(c.get("path", ""))
    }

    actions: List[Dict[str, Any]] = []
    conflicts: List[Dict[str, Any]] = []
    protected: List[Dict[str, Any]] = []
    needs_base: List[Dict[str, Any]] = []
    up_to_date: List[Dict[str, Any]] = []

    legacy_notes = _legacy_duplicates(repo_root, manifest)
    effective_patterns: Tuple[str, ...] = tuple(DEFAULT_PROTECT_PATTERNS) + tuple(
        protect_patterns or ()
    )
    red_zones = _project_red_zones(repo_root)

    for comp in _components_of(manifest):
        rel = _posix(comp.get("path", ""))
        kind = comp.get("kind", "")
        new_bytes = bundle_files.get(rel)
        if new_bytes is None:
            conflicts.append({
                "path": rel,
                "reason": "manifest component is missing from the integral bundle",
            })
            continue

        lock_entry = lock_by_path.get(rel)
        dest_rel = _resolve_target(rel, repo_root, lock_entry)

        if _is_protected(rel, effective_patterns):
            protected.append({
                "path": rel,
                "kind": kind,
                "reason": (
                    f"protected component '{rel}': {RED_ZONE_REFUSAL_TEXT}"
                ),
            })
            continue
        project_red = _project_red_reason(rel, dest_rel, red_zones)
        if project_red:
            protected.append({
                "path": rel,
                "kind": kind,
                "reason": (
                    f"protected component '{rel}': classified Red by the "
                    f"project's {PROJECT_BOUNDARIES_RELPATH} "
                    f"({project_red}); {RED_ZONE_REFUSAL_TEXT}"
                ),
            })
            continue

        local_path = repo_root / dest_rel
        local_bytes = local_path.read_bytes() if local_path.is_file() else None
        # Lock component schema v2: installed (on-disk) and base (pinned
        # upstream) shas recorded separately; v1 entries carry a single
        # sha256 read as BOTH (backward compatibility).
        recorded_installed = _entry_installed_sha(lock_entry)
        recorded_base = _entry_base_sha(lock_entry)
        current_sha = _sha256_bytes(local_bytes) if local_bytes is not None else None
        upstream_sha = _sha256_bytes(new_bytes)

        if lock_entry is None:
            if local_bytes is None:
                actions.append({
                    "path": rel, "kind": kind, "op": "create",
                    "target": dest_rel,
                    "content": new_bytes,
                    "upstream_sha256": upstream_sha,
                    "expected_before_sha256": None,
                })
            elif (
                adopt_existing
                and current_sha
                and current_sha == upstream_sha
            ):
                # Sha-match adoption (T6.7, friction 5): the verified local
                # bytes ARE the pinned content of unknown provenance — adopt
                # them into the lock without rewriting the file.
                actions.append({
                    "path": rel, "kind": kind, "op": "adopt",
                    "target": dest_rel,
                    "upstream_sha256": upstream_sha,
                    "expected_before_sha256": current_sha,
                })
            else:
                conflicts.append({
                    "path": rel,
                    "reason": (
                        "target path holds a local file that is not recorded "
                        "in the framework lock (unknown origin); explicit "
                        "user decision required before first install"
                    ),
                })
            continue

        if local_bytes is None:
            actions.append({
                "path": rel, "kind": kind, "op": "install_missing",
                "target": dest_rel,
                "content": new_bytes,
                "upstream_sha256": upstream_sha,
                "expected_before_sha256": None,
            })
            continue

        matched_installed, eol_only = _installed_match(
            local_bytes, recorded_installed
        )
        if matched_installed:
            # Local content matches the installation record (exact, or
            # EOL-only after an autocrlf smudge — Wave G Lane H): fast-
            # forward, no merge base bytes needed. NEVER a plain overwrite
            # when the local file carries local_repo_data blocks (п.1): the
            # blocks are extracted and re-injected into the new bytes —
            # equivalent to a merge with an empty base delta. Plain overwrite
            # remains only for marker-free files. EOL-only matches always
            # produce a write (normalizing the copy back to pinned LF bytes);
            # expected_before_sha256 stays the RAW working-tree sha so the
            # apply-time TOCTOU guard remains exact.
            if new_bytes == local_bytes and not eol_only:
                up_to_date.append({"path": rel, "kind": kind, "sha256": current_sha})
            else:
                local_blocks = _extract_local_blocks(local_bytes, rel)
                if local_blocks:
                    actions.append({
                        "path": rel, "kind": kind, "op": "merge",
                        "target": dest_rel,
                        "content": _reinject_local_blocks(new_bytes, local_blocks),
                        "preserved_blocks": [
                            tag.decode("utf-8", "replace") for _block, tag in local_blocks
                        ],
                        "upstream_sha256": upstream_sha,
                        "expected_before_sha256": current_sha,
                    })
                else:
                    actions.append({
                        "path": rel, "kind": kind, "op": "update",
                        "target": dest_rel,
                        "content": new_bytes,
                        "upstream_sha256": upstream_sha,
                        "expected_before_sha256": current_sha,
                    })
            continue

        # Local content diverged from the lock record: an honest three-way
        # merge needs the base (content whose sha256 matches the recorded
        # base — the pinned upstream bytes of the installed revision).
        base_bytes = (bundle.get("base") or {}).get(rel)
        base_ok = (
            base_bytes is not None
            and bool(recorded_base)
            and _sha256_bytes(base_bytes) == recorded_base
        )
        if not base_ok and recorded_base:
            fetched = _origin_base_candidate(bundle, lock, rel, recorded_base)
            if fetched is not None:
                base_bytes = fetched
                base_ok = True
        if not base_ok:
            needs_base.append({
                "path": rel,
                "reason": (
                    "merge base unavailable: no cached or origin-history content "
                    "matches the lock-recorded base sha256; refusing to claim a "
                    "safe merge (needs_base)"
                ),
                "lock_sha256": recorded_base,
            })
            continue

        merged, preserved = _merge_marked(base_bytes, local_bytes, new_bytes, rel)
        if merged is None:
            conflicts.append({
                "path": rel,
                "reason": (
                    "unmarked local modification outside local_repo_data "
                    "blocks (relative to the recorded base); manual "
                    "resolution required, file will NOT be overwritten"
                ),
                "local_sha256": current_sha,
                "base_sha256": recorded_base,
                "new_sha256": upstream_sha,
            })
        else:
            actions.append({
                "path": rel, "kind": kind, "op": "merge",
                "target": dest_rel,
                "content": merged,
                "preserved_blocks": [tag.decode("utf-8", "replace") for tag in preserved],
                "upstream_sha256": upstream_sha,
                "expected_before_sha256": current_sha,
            })

    plan: Dict[str, Any] = {
        "actions": actions,
        "conflicts": conflicts,
        "protected": protected,
        "needs_base": needs_base,
        "up_to_date": up_to_date,
        "legacy": legacy_notes,
        # п.4: the plan pins the exact source revision it was computed at;
        # apply must refuse any deviation from this pin.
        "pin": {
            "source": bundle.get("origin_repo"),
            "commit_sha": bundle.get("commit_sha"),
            "ref": bundle.get("ref"),
        },
        "meta": {
            "commit_sha": bundle.get("commit_sha"),
            "ref": bundle.get("ref"),
            "origin": bundle.get("origin"),
            "repository": bundle.get("origin_repo"),
            "framework_version": (manifest or {}).get("framework_version"),
            "channel": (manifest or {}).get("channel"),
            "components_total": len(_components_of(manifest)),
        },
    }
    return plan


# ---------------------------------------------------------------------------
# Journal
# ---------------------------------------------------------------------------



def apply_updates(
    repo_root: Path,
    plan: Dict[str, Any],
    actor_id: str,
    installation_id: str,
    resolved_pin: Optional[Dict[str, str]] = None,
    plan_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply the plan atomically, per file, with a crash-recovery journal.

    The plan pins what apply may do (п.4): when ``resolved_pin`` carries a
    freshly re-resolved source pin (CLI path), it must equal the plan's
    pinned commit sha; every action's ``expected_before_sha256`` must match
    the target state on disk BEFORE the first write. Any mismatch is an
    ApplyError with ZERO writes (all-or-nothing preserved).

    Refuses loudly (no writes at all) when the plan carries protected
    components, unresolved conflicts, or needs_base entries. On success the
    framework lock is rewritten atomically — the lock write is itself
    journaled (before/after bytes), so restore rolls back files AND lock
    (п.2) — and an 'update' report is stored via
    scripts/manage_reports.save_report (recording the user-approved plan
    file, when one was given).

    Perimeter (Wave D E2, T6.1): apply is a write operation — the actor
    must be ADMITTED by the project identity registry (registered + active
    binding; identity-less bootstrap projects are not blocked) BEFORE any
    journal or file write. ``adopt`` actions (T6.7) write no file bytes:
    they only record the verified pre-existing content in the lock.

    SEC-4 (Wave F FX, T-X3): the whole operation holds the repository engine
    lock (``.agents/update-engine.lock``, non-blocking) — a second concurrent
    apply/restore is refused with EngineBusyError before ANY state change.
    SEC-1 (Wave F FX, T-X1): every destination read/write is contained via
    assert_within BEFORE any journal entry is created.
    """
    repo_root = Path(repo_root)
    with engine_operation_lock(repo_root):
        return _apply_updates_locked(
            repo_root, plan, actor_id, installation_id,
            resolved_pin=resolved_pin, plan_file=plan_file,
        )


def _apply_updates_locked(
    repo_root: Path,
    plan: Dict[str, Any],
    actor_id: str,
    installation_id: str,
    resolved_pin: Optional[Dict[str, str]] = None,
    plan_file: Optional[str] = None,
) -> Dict[str, Any]:
    """apply_updates body, running under the exclusive engine lock (SEC-4)."""

    admission_denial = _actor_admission_denial(repo_root, actor_id)
    if admission_denial:
        raise ApplyError(admission_denial)

    protected = plan.get("protected") or []
    if protected:
        paths = ", ".join(str(p.get("path")) for p in protected)
        raise ProtectedComponentError(
            f"refusing to apply updates touching protected components: "
            f"{paths}; {RED_ZONE_REFUSAL_TEXT}"
        )
    conflicts = plan.get("conflicts") or []
    if conflicts:
        paths = ", ".join(str(c.get("path")) for c in conflicts)
        raise ApplyError(
            f"plan carries unresolved conflict(s) for: {paths}; apply "
            "refuses to overwrite local modifications — resolve them "
            "explicitly (local_repo_data markers or manual merge) first"
        )
    needs_base = plan.get("needs_base") or []
    if needs_base:
        paths = ", ".join(str(n.get("path")) for n in needs_base)
        raise ApplyError(
            f"plan carries needs_base component(s): {paths}; no merge base "
            "matching the lock record is available, so no safe merge can "
            "be claimed — provide an integral cache with the base content "
            "or decide manually"
        )

    actions = plan.get("actions") or []
    if not actions:
        return {
            "status": "nothing_to_apply",
            "applied": [],
            "installation_id": installation_id,
            "actor_id": actor_id,
        }

    # п.4 (TOCTOU guard, source side): the freshly re-resolved pin must
    # equal the plan's pin — never silently apply a different revision.
    plan_pin = plan.get("pin") or {}
    plan_sha = str(plan_pin.get("commit_sha", "") or "")
    if resolved_pin is not None and plan_sha:
        resolved_sha = str((resolved_pin or {}).get("commit_sha", "") or "")
        if resolved_sha != plan_sha:
            raise ApplyError(
                f"plan/source revision changed: re-plan required (approved "
                f"plan pins {plan_sha}; source now resolves to "
                f"{resolved_sha or 'unresolvable'})"
            )

    # п.4 (TOCTOU guard, target side): verify EVERY action's expected
    # target state before the first write; any mismatch -> ApplyError with
    # ZERO writes. The resolved destination is the action's ``target``
    # (runtime layout, T6.5), falling back to the manifest path.
    # SEC-1: each destination is containment-checked BEFORE it is read — a
    # plan (or approved plan file) carrying an escaping target is refused
    # before the journal is even created.
    stale_targets: List[str] = []
    for action in actions:
        rel = _posix(action.get("path", ""))
        if not rel or "expected_before_sha256" not in action:
            continue
        expected = action.get("expected_before_sha256")
        dest = assert_within(repo_root, _posix(action.get("target") or rel))
        actual = _sha256_file(dest) if dest.is_file() else None
        if actual != expected:
            stale_targets.append(
                f"{rel} (plan expected sha256={expected or 'absent'}; "
                f"found {actual or 'absent'})"
            )
    if stale_targets:
        raise ApplyError(
            "target state changed since plan: " + "; ".join(stale_targets)
            + "; NOTHING was written (all-or-nothing preserved) — re-plan "
            "before applying"
        )

    run_id = generate_run_id("apply") if generate_run_id else f"apply-{uuid.uuid4().hex[:12]}"
    lock_before = read_lock(repo_root)
    journal: Dict[str, Any] = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "run_id": run_id,
        "actor_id": actor_id,
        "installation_id": installation_id,
        "status": "started",
        "started_at": _utc_now_iso(),
        "plan_meta": plan.get("meta") or {},
        "entries": [],
    }

    def _persist_journal() -> None:
        _save_journal(repo_root, journal)

    # The journal must exist BEFORE the first file is replaced.
    _persist_journal()

    applied_actions: List[Dict[str, Any]] = []
    try:
        for action in actions:
            rel = _posix(action["path"])
            dest_rel = _posix(action.get("target") or rel)
            # SEC-1: contained, symlink-refused destination — the plan's
            # target must resolve INSIDE the repository root before any
            # byte is read or written through it.
            dest = assert_within(repo_root, dest_rel)
            if action.get("op") == "adopt":
                # Sha-match adoption (T6.7): the on-disk bytes were verified
                # against expected_before_sha256 above — record them in the
                # lock WITHOUT rewriting the file.
                applied_actions.append(action)
                continue
            content = action.get("content")
            if not isinstance(content, bytes):
                raise ApplyError(
                    f"plan action for '{rel}' carries no content bytes"
                )
            before_bytes = dest.read_bytes() if dest.is_file() else None
            entry = {
                "path": rel,
                "op": action.get("op", "update"),
                "kind": action.get("kind", ""),
                "before_sha256": _sha256_bytes(before_bytes) if before_bytes is not None else None,
                "after_sha256": _sha256_bytes(content),
                "before_b64": _b64(before_bytes),
                "after_b64": _b64(content),
                "status": "pending",
            }
            journal["entries"].append(entry)
            _persist_journal()
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                _atomic_write_bytes(dest, content)
            except OSError as exc:
                entry["status"] = "failed"
                entry["error"] = str(exc)
                journal["status"] = "aborted"
                journal["aborted_at"] = _utc_now_iso()
                _persist_journal()
                raise ApplyError(
                    f"apply failed at '{rel}': {exc}; per-file writes before "
                    f"the failure are journaled in '{UPDATE_JOURNAL_RELPATH}' "
                    "— run restore_updates to return the tree to the "
                    "pre-apply state"
                )
            entry["status"] = "applied"
            applied_actions.append(action)
            _persist_journal()
    except ApplyError:
        raise

    # Success: rewrite the lock atomically to the installed subset.
    # Component schema v2 (Wave D E1, T1.1): base_sha256 = pinned upstream
    # bytes, installed_sha256 = bytes actually written, target = resolved
    # destination (reserved; defaults to the manifest path). Entries not
    # touched by this apply keep their previous (possibly v1) shape.
    lock = dict(lock_before or {})
    lock["schema_version"] = LOCK_SCHEMA_VERSION
    components = [
        dict(c) for c in (lock_before or {}).get("components") or []
        if isinstance(c, dict) and _posix(c.get("path", ""))
    ]
    by_path = {_posix(c.get("path", "")): c for c in components}
    meta = plan.get("meta") or {}
    for action in applied_actions:
        rel = _posix(action["path"])
        dest_rel = _posix(action.get("target") or rel)
        if action.get("op") == "adopt":
            # Adoption (T6.7): installed bytes are the verified pre-existing
            # content; the base is the pinned upstream it hash-equals.
            installed_sha = str(action.get("expected_before_sha256") or "")
            base_sha = str(action.get("upstream_sha256") or installed_sha)
        else:
            content = action["content"]
            installed_sha = _sha256_bytes(content)
            base_sha = str(action.get("upstream_sha256") or installed_sha)
        entry = {
            "path": rel,
            "kind": action.get("kind", ""),
            "base_sha256": base_sha,
            "installed_sha256": installed_sha,
            "target": dest_rel,
        }
        if rel in by_path:
            components[components.index(by_path[rel])] = entry
        else:
            components.append(entry)
        by_path[rel] = entry
    lock["components"] = components
    old_source = (lock_before or {}).get("source") or {}
    lock["source"] = {
        "repository": str(meta.get("repository") or old_source.get("repository") or "unknown"),
        "ref": str(meta.get("ref") or old_source.get("ref") or "unknown"),
        "commit_sha": str(meta.get("commit_sha") or "unknown"),
        "origin": str(meta.get("origin") or old_source.get("origin") or "unknown"),
        "channel": str(
            meta.get("channel") or old_source.get("channel") or "preview"
        ),
    }
    lock["installed_at"] = _utc_now_iso()

    # Journal the lock write itself (Wave D E1, T1.2/п.2): before/after
    # bytes recorded BEFORE the lock is replaced, so restore_updates rolls
    # the lock back like any other journaled entry. Atomicity of the lock
    # write itself is preserved (write_lock_atomic).
    lock_path = repo_root / FRAMEWORK_LOCK_RELPATH
    lock_before_bytes = lock_path.read_bytes() if lock_path.is_file() else None
    new_lock_bytes = _lock_payload_bytes(lock)
    lock_journal_entry = {
        "path": FRAMEWORK_LOCK_RELPATH,
        "op": "lock_write",
        "kind": "lock",
        "before_sha256": (
            _sha256_bytes(lock_before_bytes) if lock_before_bytes is not None else None
        ),
        "after_sha256": _sha256_bytes(new_lock_bytes),
        "before_b64": _b64(lock_before_bytes),
        "after_b64": _b64(new_lock_bytes),
        "status": "pending",
    }
    journal["entries"].append(lock_journal_entry)
    _persist_journal()
    write_lock_atomic(repo_root, lock)
    lock_journal_entry["status"] = "applied"

    journal["status"] = "completed"
    journal["completed_at"] = _utc_now_iso()
    _persist_journal()

    # Update report through the canonical report engine (report_type='update').
    report_path: Optional[str] = None
    if save_report is not None:
        report = _build_update_report(
            repo_root=repo_root,
            installation_id=installation_id,
            actor_id=actor_id,
            plan=plan,
            applied_actions=applied_actions,
            lock_before=lock_before,
            plan_file=plan_file,
            run_id=run_id,
        )
        saved = save_report(repo_root, installation_id, REPORT_TYPE, report)
        report_path = str(saved)

    # Harness session reload notice (parity hardening item 4): harnesses
    # cache the system prompt and skills at session start, so an apply that
    # touched core instruction files leaves the LIVE session running on the
    # pre-update texts (observed 2026-11-15 and 2026-11-18). Surface the
    # restart requirement to the operator directly on the apply result —
    # stdout stays machine-readable, the notice goes to stderr.
    # Manifest component casing is authoritative: the core passport ships
    # as templates/AGENTS.md (see templates/release_manifest.json); the root
    # AGENTS.md and templates/global/AGENTS.md variants are covered by the
    # casefold-comparison below so no casing drift can silence the notice.
    def _is_instruction_file(rel: str) -> bool:
        posix = _posix(rel).casefold()
        return (
            posix == "agents.md"
            or posix == "templates/agents.md"
            or posix.startswith("skills/")
            or posix.startswith("templates/global/")
        )

    instruction_updates = [
        action["path"]
        for action in applied_actions
        if _is_instruction_file(action.get("path", ""))
    ]
    if instruction_updates:
        sys.stderr.write(
            "[NOTICE] Core instructions or skills updated "
            f"({len(instruction_updates)} file(s), e.g. {instruction_updates[0]}). "
            "Restart harness session to reload prompt context.\n"
        )

    return {
        "status": "completed",
        "run_id": run_id,
        "applied": [a["path"] for a in applied_actions],
        "journal": UPDATE_JOURNAL_RELPATH,
        "lock": FRAMEWORK_LOCK_RELPATH,
        "report_path": report_path,
        "approved_plan_file": plan_file,
        "installation_id": installation_id,
        "actor_id": actor_id,
    }



def restore_updates(repo_root: Path) -> Dict[str, Any]:
    """Restore ONLY the engine's own changes recorded in the journal.

    Each journaled path is reverted only when its current sha256 still
    matches what the engine wrote; third-party edits made during the apply
    window are detected and preserved (never clobbered). The framework lock
    is an ordinary journaled entry since Wave D E1 (п.2): apply journals it
    with before/after bytes before writing, so a successful restore returns
    files AND ``.agents/framework-lock.json`` to the coherent pre-apply
    state.

    SEC-4 (Wave F FX, T-X3): restore holds the repository engine lock — a
    concurrent apply/restore is refused (EngineBusyError). SEC-1: every
    journaled path is containment-checked (hostile journal paths and symlink
    destinations are refused, never followed). U11 (T-X5): the update report
    of the journaled run is marked ``status: "restored"`` (audit trail
    preserved in place).
    """
    repo_root = Path(repo_root)
    with engine_operation_lock(repo_root):
        return _restore_updates_locked(repo_root)



def _restore_updates_locked(repo_root: Path) -> Dict[str, Any]:
    """restore_updates body, running under the exclusive engine lock (SEC-4)."""
    journal_path = repo_root / UPDATE_JOURNAL_RELPATH
    if not journal_path.is_file():
        return {
            "status": "nothing_to_restore",
            "restored": [],
            "kept": [],
            "skipped": [],
        }
    journal = _read_json(journal_path)
    entries = journal.get("entries") or []
    restored: List[Dict[str, Any]] = []
    kept: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        rel = _posix(entry.get("path", ""))
        if not rel:
            continue
        # SEC-1: a journal is engine data, but restore never follows a path
        # outside the repository root or through a symlink.
        target = assert_within(repo_root, rel)
        after_sha = entry.get("after_sha256")
        before_sha = entry.get("before_sha256")
        before_bytes = _unb64(entry.get("before_b64"))
        current_bytes = target.read_bytes() if target.is_file() else None
        current_sha = _sha256_bytes(current_bytes) if current_bytes is not None else None

        if entry.get("status") == "failed":
            skipped.append({
                "path": rel,
                "reason": "apply never completed this step; nothing to revert",
            })
            continue
        if current_bytes is not None and after_sha and current_sha == after_sha:
            # Exactly the engine's own write: safe to revert.
            if before_bytes is None:
                try:
                    target.unlink()
                except OSError as exc:
                    kept.append({"path": rel, "reason": f"removal failed: {exc}"})
                    continue
                restored.append({"path": rel, "action": "removed (created by apply)"})
            else:
                _atomic_write_bytes(target, before_bytes)
                restored.append({"path": rel, "action": "reverted to pre-apply content"})
            continue
        if current_bytes is not None and before_sha and current_sha == before_sha:
            skipped.append({"path": rel, "reason": "already at the pre-apply state"})
            continue
        if current_bytes is None and before_bytes is None:
            skipped.append({"path": rel, "reason": "target absent; nothing created"})
            continue
        kept.append({
            "path": rel,
            "reason": (
                "content changed after the engine wrote it (third-party "
                "edit during the apply window); preserved, never clobbered"
            ),
        })

    journal["status"] = "restored"
    journal["restored_at"] = _utc_now_iso()
    _save_journal(repo_root, journal)

    # U11 (T-X5): the report of the journaled run is marked "restored" so
    # the audit trail shows the update was rolled back.
    marked_report = _mark_update_report_restored(
        repo_root, str(journal.get("run_id", "") or "")
    )

    return {
        "status": "restored",
        "journal": UPDATE_JOURNAL_RELPATH,
        "restored": restored,
        "kept": kept,
        "skipped": skipped,
        "marked_report": marked_report,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------



def _add_source_args(parser: argparse.ArgumentParser, repo_root_required: bool) -> None:
    parser.add_argument(
        "--repo-root",
        required=repo_root_required,
        default=None if repo_root_required else ".",
        help="Target repository root path",
    )
    parser.add_argument(
        "--source",
        help="Upstream source: local git repository path (remote URLs require "
        "a prior local fetch; remote origin support needs `git fetch` first)",
    )
    parser.add_argument(
        "--ref",
        default="main",
        help="Ref to pin: branch, tag, or (full) commit SHA (default: main)",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Integral bundle cache directory (default: META_PROJECT_CACHE "
        "env, else the OS cache path)",
    )
    parser.add_argument(
        "--components",
        default=None,
        help="Comma-separated subset of manifest component paths to include",
    )
    parser.add_argument(
        "--protect",
        default=None,
        help="Comma-separated ADDITIONAL protect patterns, united with the "
        "engine defaults (union; user patterns never replace the defaults)",
    )


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="update_meta_project",
        description="Meta-Project Managed Update Engine (SHA-pinned, atomic, journaled)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    p_check = subparsers.add_parser(
        "check", help="Read-only availability & drift check (zero-write)"
    )
    _add_source_args(p_check, repo_root_required=False)

    p_plan = subparsers.add_parser(
        "plan", help="Read-only three-way merge plan (zero-write)"
    )
    _add_source_args(p_plan, repo_root_required=False)
    p_plan.add_argument(
        "--full",
        action="store_true",
        help="Print the machine-consumable plan: actions carry content_b64 "
        "bytes (default output is a content-less summary; a summary plan "
        "file still applies via hash-verified re-materialization)",
    )

    p_apply = subparsers.add_parser(
        "apply", help="Apply the update atomically with journal, lock and update report"
    )
    _add_source_args(p_apply, repo_root_required=True)
    p_apply.add_argument(
        "--adopt-existing",
        action="store_true",
        help="Adopt unknown-origin local files whose bytes hash-equal the "
        "pinned upstream content: record them in the lock WITHOUT rewriting "
        "the file bytes (sha-match adoption)",
    )
    p_apply.add_argument(
        "--plan-file",
        default=None,
        help="Path to a user-approved plan file (output of `plan`). When "
        "absent, a fresh plan is computed and treated as approved — the "
        "[RE-PLANNED] notice is printed. The approved plan's pin is "
        "re-verified against the source before any write.",
    )
    p_apply.add_argument(
        "--installation", required=True, help="Installation ID (e.g. ag-main)"
    )
    p_apply.add_argument(
        "--actor", required=True, help="Qualified actor_id executing the update"
    )

    p_restore = subparsers.add_parser(
        "restore",
        help="Restore ONLY the engine's own changes from the last operation journal",
    )
    p_restore.add_argument(
        "--repo-root", default=".", help="Target repository root path"
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: check | plan | apply | restore."""
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    repo_root = Path(getattr(args, "repo_root", ".") or ".").resolve()

    # --protect patterns are ADDITIONAL: plan_updates unites them with
    # DEFAULT_PROTECT_PATTERNS (T6.2 union; user patterns never replace the
    # defaults).
    user_protects = tuple(_split_list(getattr(args, "protect", None)))
    components = _split_list(getattr(args, "components", None))
    cache_dir: Optional[Path]
    explicit_cache = getattr(args, "cache_dir", None)
    if explicit_cache:
        cache_dir = Path(explicit_cache)
    else:
        cache_dir = default_cache_dir()

    if args.subcommand == "check":
        try:
            result = check_updates(repo_root, args.source, args.ref, cache_dir)
        except UpdateEngineError as exc:
            # U8 (Wave F FX, T-X6): a failing check reports itself in the
            # JSON payload as check_status="failed"; the rc contract is
            # UNCHANGED (rc 1 on failure).
            sys.stderr.write(f"[CHECK-FAILED] {exc}\n")
            print(json.dumps({"check_status": "failed", "error": str(exc)}))
            return 1
        result["check_status"] = "ok"
        print(json.dumps(result, indent=2, default=str))
        return 0 if not (result["updates_available"] or result["drifted"]) else 1

    if args.subcommand == "plan":
        try:
            pin = resolve_pin_with_cache_fallback(args.source, args.ref, cache_dir)
            bundle = load_bundle(pin, cache_dir)
            if components:
                bundle = _filter_bundle(bundle, components)
            lock = read_lock(repo_root)
            plan = plan_updates(
                repo_root, bundle, lock, protect_patterns=user_protects
            )
        except UpdateEngineError as exc:
            sys.stderr.write(f"[PLAN-HALT] {exc}\n")
            return 1
        print(json.dumps(
            _plan_to_jsonable(plan, full=bool(getattr(args, "full", False))),
            indent=2,
            default=str,
        ))
        return 0

    if args.subcommand == "apply":
        plan_file = getattr(args, "plan_file", None)
        try:
            if plan_file:
                # The user-approved plan is loaded verbatim; --source/--ref,
                # when given, re-resolve the source to verify the plan's pin
                # (п.4). When omitted, source/ref fall back to the plan's own
                # pin block. A content-less (summary) plan is executable:
                # content bytes are re-materialized from the plan's own pin
                # and hash-verified (T6.6).
                loaded = _read_json(Path(plan_file))
                if not isinstance(loaded, dict) or not isinstance(
                    loaded.get("actions"), list
                ):
                    raise UpdateEngineError(
                        f"plan file '{plan_file}' is not a serialized update "
                        "plan (expected an object with an 'actions' list)"
                    )
                plan = _plan_from_jsonable(loaded)
                pin_block = plan.get("pin") or {}
                source_arg = str(args.source or pin_block.get("source") or "")
                ref_arg = str(args.ref) if args.source else str(
                    pin_block.get("ref") or args.ref
                )
                pin = resolve_pin_with_cache_fallback(source_arg, ref_arg, cache_dir)
                plan = _rematerialize_plan_content(repo_root, plan, cache_dir)
            else:
                pin = resolve_pin_with_cache_fallback(args.source, args.ref, cache_dir)
                # SEC-2 (T-X2): apply seals a cross-verified cache entry at
                # load time so later offline loads can verify it.
                bundle = load_bundle(pin, cache_dir, seal_cache=True)
                if components:
                    bundle = _filter_bundle(bundle, components)
                lock = read_lock(repo_root)
                plan = plan_updates(
                    repo_root,
                    bundle,
                    lock,
                    protect_patterns=user_protects,
                    adopt_existing=bool(getattr(args, "adopt_existing", False)),
                )
                sys.stderr.write(
                    "[RE-PLANNED] no --plan-file provided; a freshly computed "
                    "plan was treated as approved\n"
                )
            result = apply_updates(
                repo_root,
                plan,
                args.actor,
                args.installation,
                resolved_pin=pin,
                plan_file=plan_file,
            )
        except UpdateEngineError as exc:
            if isinstance(exc, EngineBusyError):
                # SEC-4 (T-X3): a concurrent engine operation holds the
                # repository lock.
                sys.stderr.write(_error_envelope(
                    "ENGINE_BUSY",
                    str(repo_root),
                    "another engine operation (apply or restore) is already "
                    "running on this repository",
                    "exclusive acquisition of .agents/update-engine.lock",
                    str(exc),
                    "wait for the running apply/restore to finish, then retry",
                ) + "\n")
                sys.stderr.write(f"[ENGINE-BUSY] {exc}\n")
                return 1
            sys.stderr.write(_error_envelope(
                "APPLY_REFUSED",
                str(plan_file) if plan_file else str(repo_root),
                "apply refused with zero writes (plan perimeter or "
                "preconditions violated)",
                "an admitted actor applying a serialized, pin-matching, "
                "conflict-free plan over the pinned base",
                str(exc),
                "re-run scripts/update_meta_project.py check/plan, resolve "
                "the refusal cause above, and apply the regenerated plan",
            ) + "\n")
            sys.stderr.write(f"[APPLY-REFUSED] {exc}\n")
            return 1
        except (OSError, ValueError) as exc:
            sys.stderr.write(_error_envelope(
                "APPLY_FAILED",
                str(plan_file) if plan_file else str(repo_root),
                "apply failed before completing (journal preserves the "
                "recovery state)",
                "every plan action applied atomically over writable targets",
                str(exc),
                "inspect the journal (.agents/update_journal.json) and use "
                "'restore' to return to the pre-apply state, then re-apply",
            ) + "\n")
            sys.stderr.write(f"[APPLY-FAILED] {exc}\n")
            return 1
        print(json.dumps(result, indent=2, default=str))
        return 0

    if args.subcommand == "restore":
        try:
            result = restore_updates(repo_root)
        except EngineBusyError as exc:
            # SEC-4 (T-X3): a concurrent engine operation holds the lock.
            sys.stderr.write(_error_envelope(
                "ENGINE_BUSY",
                str(repo_root),
                "another engine operation (apply or restore) is already "
                "running on this repository",
                "exclusive acquisition of .agents/update-engine.lock",
                str(exc),
                "wait for the running apply/restore to finish, then retry",
            ) + "\n")
            sys.stderr.write(f"[ENGINE-BUSY] {exc}\n")
            return 1
        except (UpdateEngineError, OSError, ValueError) as exc:
            sys.stderr.write(f"[RESTORE-FAILED] {exc}\n")
            return 1
        print(json.dumps(result, indent=2, default=str))
        return 0

    parser.error(f"unknown subcommand: {args.subcommand}")
    return 2


if __name__ == "__main__":
    sys.exit(main())

__all__ = [
    'CACHE_MANIFEST_RELPATH',
    'CANONICAL_MANIFEST_RELPATH',
    'DEFAULT_PROTECT_PATTERNS',
    'ENGINE_LOCK_RELPATH',
    'FRAMEWORK_LOCK_RELPATH',
    'HASH_LOCAL_REPO_DATA_RE',
    'LOCAL_REPO_DATA_RE',
    'LOCK_SCHEMA_VERSION',
    'MANIFEST_RELPATH',
    'PROJECT_BOUNDARIES_RELPATH',
    'REPORT_TYPE',
    'UPDATE_JOURNAL_RELPATH',
    '_EXACT_SHA_RE',
    '_HASH_MARKER_EXTENSIONS',
    '_HTML_MARKER_EXTENSIONS',
    '_SKILL_RESOURCE_RUNTIME_LAYOUT_RE',
    '_SKILL_RUNTIME_LAYOUT_RE',
    '_WINDOWS_DRIVE_RE',
    'ApplyError',
    'CacheVerificationError',
    'EngineBusyError',
    'LegacyDuplicateError',
    'MixedBundleError',
    'PartialCacheError',
    'PathContainmentError',
    'ProtectedComponentError',
    'SourceResolutionError',
    'UpdateEngineError',
    '_atomic_write_bytes',
    '_collect_base_candidates',
    '_components_of',
    '_entry_base_sha',
    '_entry_installed_sha',
    '_fetch_pinned_tree',
    '_filter_bundle',
    '_git_blob',
    '_installed_match',
    '_load_cache_manifest',
    '_lock_payload_bytes',
    '_marker_regexes',
    '_posix',
    '_read_bundle_tree',
    '_read_json',
    '_run_git',
    '_sha256_bytes',
    '_sha256_file',
    '_split_list',
    '_verify_cache_against_origin',
    'apply_updates',
    'assert_within',
    'build_cache_manifest',
    'check_updates',
    'file_lock',
    'load_bundle',
    'main',
    'plan_updates',
    'read_lock',
    'resolve_source',
    'restore_updates',
    'seal_cache_entry',
]
