#!/usr/bin/env python3
"""
scripts/_report_intake.py

Report storage, creation, duty reconciliation, delta verification,
and manage intake evaluation (ADR #22 submodule).
Pure Python 3.10+ standard library, zero external dependencies.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

try:
    from scripts.verify_identity import (
        VALID_DISPATCHER_BINDINGS,
        evaluate_actor_admission,
        load_registry,
        resolve_actor_binding,
        validate_identity_registry,
    )
except ImportError:
    try:
        from verify_identity import (
            VALID_DISPATCHER_BINDINGS,
            evaluate_actor_admission,
            load_registry,
            resolve_actor_binding,
            validate_identity_registry,
        )
    except ImportError:
        evaluate_actor_admission = None
        load_registry = None
        resolve_actor_binding = None
        validate_identity_registry = None
        VALID_DISPATCHER_BINDINGS = ("standalone", "orchestrator-hosted")

try:
    from scripts._common import _utc_now_iso
except ImportError:
    from _common import _utc_now_iso

try:
    from scripts._report_models import (
        ESSENTIAL_INPUT_PATHS,
        GIT_STATE_UNAVAILABLE_REASON,
        INSTALLATION_CHANGE_KINDS,
        MANAGE_CHANGE_FIELDS,
        REGISTRY_PATH,
        VALID_COLLABORATION_MODELS,
        VALID_MANAGE_CHANGE_KINDS,
        _require_commit_sha,
        _require_safe_identifier,
        collect_input_fingerprints,
        generate_run_id,
        get_git_state,
        normalize_input_fingerprints,
        validate_report,
    )
except ImportError:
    from _report_models import (
        ESSENTIAL_INPUT_PATHS,
        GIT_STATE_UNAVAILABLE_REASON,
        INSTALLATION_CHANGE_KINDS,
        MANAGE_CHANGE_FIELDS,
        REGISTRY_PATH,
        VALID_COLLABORATION_MODELS,
        VALID_MANAGE_CHANGE_KINDS,
        _require_commit_sha,
        _require_safe_identifier,
        collect_input_fingerprints,
        generate_run_id,
        get_git_state,
        normalize_input_fingerprints,
        validate_report,
    )

def get_report_dir(
    repo_root: Path, installation_id: str, report_type: str
) -> Path:
    """
    Return destination directory for reports.

    Wave F SEC-3: installation_id and report_type are validated exactly
    like run_id before any path is built, so a hostile identifier cannot
    escape the reports directory — and cannot cause directory creation
    outside the repository via save_report's mkdir.
    """
    _require_safe_identifier(installation_id, "installation_id")
    _require_safe_identifier(report_type, "report_type")
    return repo_root / ".agents" / "reports" / installation_id / report_type


def save_report(
    repo_root: Path,
    installation_id: str,
    report_type: str,
    report_data: Dict[str, Any],
) -> Path:
    """
    Atomically write report to disk and update latest.json pointer.
    Raises ValueError if data is invalid, an identifier (run_id,
    installation_id) is unsafe, or the run already exists (audit §5:
    existing runs must never be overwritten — the guard is the atomic
    O_EXCL reservation below, Wave F M5).
    """
    errors = validate_report(report_data, expected_type=report_type)
    if errors:
        raise ValueError(f"Cannot save invalid report: {'; '.join(errors)}")

    run_id = str(report_data["run_id"])
    # Path safety (audit §5, Wave F SEC-3): identifiers must not escape
    # the report dir. installation_id is validated inside get_report_dir.
    _require_safe_identifier(run_id, "run_id")

    target_dir = get_report_dir(repo_root, installation_id, report_type)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / f"{run_id}.json"
    if target_file.exists():
        raise ValueError(
            f"Refusing to overwrite existing run: {target_file} "
            "(each attempt must use a unique run_id)"
        )
    temp_file = target_dir / f".tmp_{run_id}_{uuid.uuid4().hex[:6]}.json"

    # 1. Atomic write of full report
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 2. Wave F M5 overwrite-guard: atomically RESERVE the final name via
    # O_EXCL creation. The exists() check above is advisory (it races
    # across processes); the O_EXCL create is the authoritative
    # serialization point, so a second concurrent writer with the same
    # run_id fails loudly instead of silently clobbering the first
    # writer's report with its replace().
    try:
        reservation_fd = os.open(
            str(target_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY
        )
    except FileExistsError:
        temp_file.unlink(missing_ok=True)
        raise ValueError(
            f"Refusing to overwrite existing run: {target_file} "
            "(each attempt must use a unique run_id)"
        ) from None
    os.close(reservation_fd)
    try:
        temp_file.replace(target_file)
    except Exception:
        # Best effort: do not leave a zero-byte reservation tombstone on a
        # failed publish. A tombstone left by a hard kill is surfaced by
        # find_latest_report as a corrupted attempt and is never silently
        # overwritten (audit §5).
        try:
            target_file.unlink()
        except OSError:
            pass
        raise

    # 2. Atomic write of latest pointer (relative path so a repository copy
    # resolves its OWN reports; audit §5 cross-contamination fix).
    latest_pointer_file = target_dir / "latest.json"
    temp_latest = target_dir / f".tmp_latest_{uuid.uuid4().hex[:6]}.json"
    pointer_data = {
        "run_id": run_id,
        "status": report_data["status"],
        "created_at": report_data.get("created_at"),
        "report_type": report_type,
        "installation_id": installation_id,
        "path": target_file.name,
    }
    with open(temp_latest, "w", encoding="utf-8") as f:
        json.dump(pointer_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    temp_latest.replace(latest_pointer_file)
    return target_file


def _load_valid_report(path: Path, expected_type: str) -> Optional[Dict[str, Any]]:
    """
    Load a report file and return it when structurally valid, else None.

    Wave F M6 backward compatibility: this is the READ path for persisted
    reports, so legacy completed init/manage reports created before
    fingerprinting remain readable (allow_legacy_fingerprints=True) —
    find_latest_report must still surface them, and staleness applies its
    legacy safeguards. Strictness for NEW reports lives in the default
    validate_report (verify CLI, save_report, intake).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None
    if validate_report(
        data, expected_type=expected_type, allow_legacy_fingerprints=True
    ):
        return None
    return data


def find_latest_report(
    repo_root: Path, installation_id: str, report_type: str
) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
    """
    Find the LATEST ATTEMPT for given installation and type (audit §5):
    'latest' includes blocked or corrupted attempts and is never silently
    substituted with an older valid report. Pointer paths are resolved
    relative to the report directory (repository-copy isolation).

    Pointer resolution is authoritative when latest.json is intact. The
    fallback (no usable pointer) resolves the newest attempt by file
    mtime with the report file name as the final deterministic tiebreak
    (Wave F M4): generate_run_id embeds a 1-second timestamp plus a random
    UUID suffix, so two same-second runs sort randomly by name alone —
    mtime restores creation order while keeping the resolution fully
    deterministic for a given directory state. Files whose mtime cannot
    be stat'ed sort oldest.
    Returns (path, data) for a valid latest attempt, (path, None) when the
    latest attempt is corrupted/foreign, or (None, None) when absent.
    """
    target_dir = get_report_dir(repo_root, installation_id, report_type)
    if not target_dir.exists():
        return None, None

    def _belongs(data: Optional[Dict[str, Any]]) -> bool:
        return (
            data is not None
            and data.get("installation_id") == installation_id
            and data.get("report_type") == report_type
        )

    # Check latest.json first
    latest_pointer = target_dir / "latest.json"
    if latest_pointer.exists():
        try:
            with open(latest_pointer, "r", encoding="utf-8") as f:
                ptr = json.load(f)
        except Exception:
            ptr = None
        if ptr:
            raw = str(ptr.get("path", ""))
            cand = Path(raw)
            if not cand.is_absolute():
                cand = target_dir / raw
            # Containment: pointer must resolve inside the report directory.
            try:
                cand.resolve().relative_to(target_dir.resolve())
            except (ValueError, OSError):
                cand = None
            if cand is not None and cand.is_file():
                data = _load_valid_report(cand, report_type)
                if _belongs(data):
                    return cand, data
                # Surface the latest attempt as corrupted/foreign instead of
                # hiding it behind an older valid report.
                return cand, None

    # No usable pointer: newest attempt by mtime (creation order) with the
    # file name as the final deterministic tiebreak (Wave F M4 — see the
    # docstring; name-only ordering is random for same-second run_ids).
    def _recency_key(p: Path) -> Tuple[int, str]:
        try:
            return (p.stat().st_mtime_ns, p.name)
        except OSError:
            return (0, p.name)

    candidates = sorted(
        [p for p in target_dir.glob("*.json") if p.name != "latest.json"],
        key=_recency_key,
        reverse=True,
    )
    for cand in candidates:
        data = _load_valid_report(cand, report_type)
        if _belongs(data):
            return cand, data
        return cand, None  # newest attempt is unreadable: surface it

    return None, None


def create_init_report(
    repo_root: Path,
    installation_id: str,
    harness_id: str,
    actor_id: str,
    project_id: str,
    status: str,
    scenario: Dict[str, Any],
    environment: Optional[Dict[str, Any]] = None,
    components: Optional[Dict[str, Any]] = None,
    checks: Optional[List[Dict[str, Any]]] = None,
    recommendations: Optional[Dict[str, Any]] = None,
    blockers: Optional[List[str]] = None,
    next_step_readiness: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to assemble a canonical init report dictionary."""
    git_state = get_git_state(repo_root)
    actual_run_id = run_id or generate_run_id("init")
    now_iso = _utc_now_iso()

    return {
        "schema_version": "1.0.0",
        "report_type": "init",
        "project_id": project_id,
        "installation_id": installation_id,
        "harness_id": harness_id,
        "actor_id": actor_id,
        "run_id": actual_run_id,
        "created_at": now_iso,
        "status": status,
        "git_state": git_state,
        "input_fingerprints": collect_input_fingerprints(repo_root),
        "references": {
            "registry": ".agents/meta-project.json",
            "passport": "AGENTS.md",
            "boundaries": ".agents/project_knowledge/boundaries.md",
        },
        "scenario": scenario,
        "environment": environment or {"capabilities": {}, "constraints": []},
        "components": components
        or {"created": [], "modified": [], "preserved": []},
        "checks": checks or [],
        "recommendations_for_manage": recommendations
        or {"suggested_roles": [], "target_topology": "", "rationale": ""},
        "blockers_and_unresolved": blockers or [],
        "next_step_readiness": next_step_readiness
        or {
            "ready_for_manage": status == "completed",
            "details": "Initialization complete"
            if status == "completed"
            else "Awaiting resolution",
        },
    }


def create_manage_report(
    repo_root: Path,
    installation_id: str,
    harness_id: str,
    actor_id: str,
    project_id: str,
    init_run_id: str,
    status: str,
    scenario: Dict[str, Any],
    roles: Dict[str, List[str]],
    bindings: Dict[str, Any],
    effective_capabilities: Optional[Dict[str, Any]] = None,
    checks: Optional[List[Dict[str, Any]]] = None,
    remaining_manual_actions: Optional[List[str]] = None,
    changes: Optional[List[Dict[str, Any]]] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to assemble a canonical manage report dictionary."""
    git_state = get_git_state(repo_root)
    actual_run_id = run_id or generate_run_id("manage")
    now_iso = _utc_now_iso()

    return {
        "schema_version": "1.0.0",
        "report_type": "manage",
        "project_id": project_id,
        "installation_id": installation_id,
        "harness_id": harness_id,
        "actor_id": actor_id,
        "run_id": actual_run_id,
        "init_run_id": init_run_id,
        "created_at": now_iso,
        "status": status,
        "git_state": git_state,
        "input_fingerprints": collect_input_fingerprints(repo_root),
        "scenario": scenario,
        "roles": roles,
        "bindings": bindings,
        # Wave D T2.1 formalization: the declared registry delta this
        # operation applied (add_role/disable/archive with ids/paths).
        "changes": list(changes or []),
        "effective_capabilities": effective_capabilities
        or {"team_readiness": "ready"},
        "checks": checks or [],
        "remaining_manual_actions": remaining_manual_actions or [],
    }


def create_tune_report(
    repo_root: Path,
    installation_id: str,
    harness_id: str,
    actor_id: str,
    project_id: str,
    status: str,
    proposals: List[Dict[str, Any]],
    checks: Optional[List[Dict[str, Any]]] = None,
    remaining_manual_actions: Optional[List[str]] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to assemble a canonical tune report dictionary (Wave D T2.2)."""
    git_state = get_git_state(repo_root)
    actual_run_id = run_id or generate_run_id("tune")
    now_iso = _utc_now_iso()

    return {
        "schema_version": "1.0.0",
        "report_type": "tune",
        "project_id": project_id,
        "installation_id": installation_id,
        "harness_id": harness_id,
        "actor_id": actor_id,
        "run_id": actual_run_id,
        "created_at": now_iso,
        "status": status,
        "git_state": git_state,
        "input_fingerprints": collect_input_fingerprints(repo_root),
        "proposals": proposals,
        "checks": checks or [],
        "remaining_manual_actions": remaining_manual_actions or [],
    }


def resolve_team_topology(
    scenario: Dict[str, Any],
    loc_estimate: int = 0,
    target_installation: Optional[str] = None,
    registry_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Map scenario configuration to recommended agent team topology.

    Decision precedence (audit §5/§6):
    1. An explicitly agreed collaboration_model is a USER DECISION and always
       wins; size heuristics (LOC) must never silently downgrade it.
    2. Contradictory wishes (e.g. 'solo' + strict_independent verification)
       surface a non-empty 'conflicts' list for explicit resolution instead
       of a silent choice.
    3. 'specialized_swarm' is declared but NOT YET IMPLEMENTED: the result
       carries "supported": False and must be resolved with the user.
    4. Without an explicit choice, the profile/verification rules apply and
       LOC is only a secondary sizing guideline.
    Returns:
    {
        "target_topology": "solo" | "duo" | "triad" | "specialized_swarm",
        "suggested_roles": [...],
        "rationale": "...",
        "supported": bool,            # always present
        "conflicts": [str, ...],      # always present
    }
    """
    profile = scenario.get("profile", "active_development")
    collab = scenario.get("collaboration_model", "")
    verification = scenario.get("verification_policy", "")

    conflicts: List[str] = []

    if target_installation and isinstance(registry_data, dict):
        inst_info = registry_data.get("installations", {}).get(target_installation)
        if isinstance(inst_info, dict) and "collaboration_model" in inst_info:
            inst_collab = inst_info.get("collaboration_model")
            if inst_collab in VALID_COLLABORATION_MODELS:
                collab = inst_collab
            elif inst_collab:
                conflicts.append(
                    f"Installation '{target_installation}' has unsupported collaboration_model '{inst_collab}'. "
                    f"Allowed: {sorted(VALID_COLLABORATION_MODELS)}"
                )

    def _result(topology: str, roles: List[str], rationale: str,
                supported: bool = True) -> Dict[str, Any]:
        return {
            "target_topology": topology,
            "suggested_roles": roles,
            "rationale": rationale,
            "supported": supported,
            "conflicts": conflicts,
        }

    # 1. Explicit user decision takes precedence.
    if collab == "solo":
        if verification == "strict_independent":
            conflicts.append(
                "collaboration_model 'solo' conflicts with verification_policy "
                "'strict_independent': independent verification requires a "
                "second role; resolve explicitly with the user"
            )
        return _result(
            "solo", ["agent-general-worker"],
            f"Solo Executor honored as explicit user decision (profile '{profile}').",
        )
    if collab == "duo":
        return _result(
            "duo", ["agent-dev-lead", "agent-quality-guardian"],
            "Micro-Mini Duo honored as explicit user decision (2-stage handoff).",
        )
    if collab == "triad":
        return _result(
            "triad",
            ["agent-dev-lead", "agent-quality-guardian", "agent-github-steward"],
            "Canonical Compact Trio honored as explicit user decision; "
            "LOC estimates do not override agreed collaboration models.",
        )
    if collab == "quad":
        return _result(
            "quad",
            [
                "agent-intake-dispatcher",
                "agent-dev-lead",
                "agent-quality-guardian",
                "agent-github-steward",
            ],
            "Canonical Quad (Dispatcher + Triad) honored as explicit user decision.",
        )
    if collab == "specialized_swarm":
        return _result(
            "specialized_swarm", [],
            "specialized_swarm was requested but is NOT YET IMPLEMENTED; "
            "present the user with an explicit choice (proceed as triad now "
            "or defer until swarm support lands).",
            supported=False,
        )

    # 2. No explicit choice: profile/verification rules; LOC is secondary.
    if profile in ("documentation", "research"):
        return _result(
            "solo", ["agent-general-worker"],
            f"Solo Executor derived for '{profile}' profile (no explicit model agreed).",
        )
    if verification == "strict_independent":
        return _result(
            "triad",
            ["agent-dev-lead", "agent-quality-guardian", "agent-github-steward"],
            "Triad derived from strict_independent verification (independent "
            "verifier + release governance), regardless of repository size.",
        )
    if profile == "maintenance" or (0 < loc_estimate < 3000):
        return _result(
            "duo", ["agent-dev-lead", "agent-quality-guardian"],
            "Micro-Mini Duo derived for maintenance/compact repository "
            f"(profile '{profile}', LOC estimate {loc_estimate}).",
        )
    return _result(
        "duo", ["agent-dev-lead", "agent-quality-guardian"],
        "Standard development team configuration.",
    )


def _extract_triggers_from_profile(profile_path: Path) -> List[str]:
    """Extract invocation triggers from a role profile.md (frontmatter or Section 1)."""
    if not profile_path.is_file():
        return []
    try:
        content = profile_path.read_text(encoding="utf-8")
    except Exception:
        return []

    triggers: List[str] = []
    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
    if fm_match:
        fm_text = fm_match.group(1)
        in_triggers = False
        for line in fm_text.splitlines():
            sline = line.strip()
            if sline.startswith("invocation_triggers:"):
                in_triggers = True
                after = sline[len("invocation_triggers:"):].strip()
                if after.startswith("[") and after.endswith("]"):
                    for item in after[1:-1].split(","):
                        cleaned = item.strip().strip("'\"")
                        if cleaned:
                            triggers.append(cleaned)
                    in_triggers = False
                continue
            if in_triggers:
                if sline.startswith("-"):
                    val = sline[1:].strip().strip("'\"")
                    if val:
                        triggers.append(val)
                elif ":" in sline:
                    in_triggers = False

    if not triggers:
        sec1_match = re.search(r"-\s*\*\*User Invocation Triggers:\*\*\s*(.+)", content)
        if sec1_match:
            line_val = sec1_match.group(1).strip()
            quotes = re.findall(r'["\']([^"\']+)["\']', line_val)
            if quotes:
                triggers.extend(quotes)
            else:
                for part in line_val.rstrip(".").split(","):
                    cleaned = part.strip()
                    if cleaned and not cleaned.startswith("("):
                        triggers.append(cleaned)

    seen = set()
    result = []
    for t in triggers:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def detect_role_duty_conflicts(
    repo_root: Union[str, Path],
    target_installation: str,
    new_role_id: str,
    new_triggers: Optional[List[str]] = None,
    registry_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Wave L (ADR #25): Detect trigger and responsibility overlaps between a new or target
    role and existing active roles bound to target_installation.
    """
    repo_root = Path(repo_root)
    if registry_data is None:
        reg_file = repo_root / ".agents" / "meta-project.json"
        if reg_file.is_file():
            try:
                registry_data = json.loads(reg_file.read_text(encoding="utf-8"))
            except Exception:
                registry_data = {}
        else:
            registry_data = {}

    installations = registry_data.get("installations", {})
    if not isinstance(installations, dict) or target_installation not in installations:
        return {
            "conflicts_detected": False,
            "conflicts": [],
            "duty_reconciliation": {},
            "warning": f"Installation '{target_installation}' not registered in meta-project.json",
        }

    if new_triggers is None:
        new_prof = repo_root / ".agents" / "team" / new_role_id / "profile.md"
        new_triggers = _extract_triggers_from_profile(new_prof)

    normalized_new = [t.strip() for t in new_triggers if t and t.strip()]

    conflicts: List[Dict[str, Any]] = []
    duty_reconciliation: Dict[str, Any] = {}

    roles = registry_data.get("roles", {})
    if isinstance(roles, dict):
        for role_id, rdata in sorted(roles.items()):
            if role_id == new_role_id or not isinstance(rdata, dict):
                continue
            bindings = rdata.get("bindings", {})
            if not isinstance(bindings, dict):
                continue
            binfo = bindings.get(target_installation)
            if not isinstance(binfo, dict) or binfo.get("status") != "active":
                continue

            prof_rel = binfo.get("profile_path", f".agents/team/{role_id}/profile.md")
            prof_path = repo_root / prof_rel
            if not prof_path.is_file():
                continue

            role_triggers = _extract_triggers_from_profile(prof_path)
            overlap = [t for t in role_triggers if t in normalized_new]
            if overlap:
                retained = [t for t in role_triggers if t not in overlap]
                rel_display = str(prof_path.relative_to(repo_root) if prof_path.is_relative_to(repo_root) else prof_path).replace("\\", "/")
                conflicts.append({
                    "role_id": role_id,
                    "profile_path": rel_display,
                    "overlapping_triggers": overlap,
                    "retained_triggers": retained,
                })
                duty_reconciliation[role_id] = {
                    "profile_path": rel_display,
                    "remove_triggers": overlap,
                    "retained_triggers": retained,
                }

    return {
        "conflicts_detected": bool(conflicts),
        "conflicts": conflicts,
        "duty_reconciliation": duty_reconciliation,
    }


def apply_duty_reconciliation(
    repo_root: Union[str, Path], duty_reconciliation: Dict[str, Any]
) -> List[str]:
    """
    Apply duty reconciliation delta to conflicting role profiles, pruning overlapping triggers
    while strictly preserving Section 5 Telemetry, notes.md, and all invariants.
    """
    repo_root = Path(repo_root)
    updated_paths: List[str] = []

    for role_id, recon in sorted(duty_reconciliation.items()):
        if not isinstance(recon, dict):
            continue
        rel_path = recon.get("profile_path")
        if not rel_path:
            continue
        prof_path = Path(rel_path)
        if not prof_path.is_absolute():
            prof_path = repo_root / prof_path
        if not prof_path.is_file():
            continue

        content = prof_path.read_text(encoding="utf-8")
        retained = recon.get("retained_triggers", [])

        # 1. Update frontmatter invocation_triggers
        fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
        if not fm_match:
            continue
        fm_text = fm_match.group(1)

        fm_lines = fm_text.splitlines()
        new_fm_lines: List[str] = []
        skip_triggers = False
        triggers_inserted = False

        for line in fm_lines:
            sline = line.strip()
            if sline.startswith("invocation_triggers:"):
                skip_triggers = True
                new_fm_lines.append("invocation_triggers:")
                for t in retained:
                    new_fm_lines.append(f'  - "{t}"')
                if not retained:
                    new_fm_lines[-1] = "invocation_triggers: []"
                triggers_inserted = True
                after = sline[len("invocation_triggers:"):].strip()
                if after.startswith("[") and after.endswith("]"):
                    skip_triggers = False
                continue
            if skip_triggers:
                if sline.startswith("-"):
                    continue
                else:
                    skip_triggers = False
            new_fm_lines.append(line)

        if not triggers_inserted:
            new_fm_lines.append("invocation_triggers:")
            for t in retained:
                new_fm_lines.append(f'  - "{t}"')
            if not retained:
                new_fm_lines[-1] = "invocation_triggers: []"

        new_fm = "\n".join(new_fm_lines)

        # 2. Update Section 1 User Invocation Triggers in body
        body = content[fm_match.end():]
        if retained:
            trig_str = ", ".join(f'"{t}"' for t in retained)
            new_sec1_line = f'- **User Invocation Triggers:** {trig_str}.'
        else:
            new_sec1_line = '- **User Invocation Triggers:** (none autonomous; delegated).'

        new_body = re.sub(
            r"^-\s*\*\*User Invocation Triggers:\*\*.*$",
            new_sec1_line,
            body,
            flags=re.MULTILINE,
        )

        new_content = f"---\n{new_fm.strip()}\n---{new_body}"
        prof_path.write_text(new_content, encoding="utf-8")
        updated_paths.append(str(prof_path).replace("\\", "/"))

    return updated_paths


def check_report_staleness(
    repo_root: Path, report_data: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluate report freshness (audit §5): a report is stale when the commit
    SHA moved OR when any essential input (registry, boundaries, passport)
    drifted from its recorded fingerprint — including uncommitted changes.
    Wave F M3: a git subprocess failure on either side (current repository
    or recorded in the report) makes freshness uncertifiable — the report
    is treated as stale/suspect with the canonical reason
    'git state unavailable' (STALE_INPUT envelope on the CLI).
    Returns (is_stale, details).
    """
    current_git = get_git_state(repo_root)
    current_sha = current_git.get("commit_sha", "unknown")
    report_git = report_data.get("git_state", {})
    report_sha = report_git.get("commit_sha", "unknown")

    reasons: List[str] = []

    # Wave F M3: fail-closed git state — never certify fresh when git
    # could not be consulted (now) or was already failing at creation.
    current_err = current_git.get("git_state_error")
    if current_err:
        reasons.append(
            f"{GIT_STATE_UNAVAILABLE_REASON}: current repository git state "
            f"could not be determined ({current_err})"
        )
    report_err = (
        report_git.get("git_state_error")
        if isinstance(report_git, dict)
        else None
    )
    if report_err:
        reasons.append(
            f"{GIT_STATE_UNAVAILABLE_REASON}: report recorded a git "
            f"failure at creation ({report_err})"
        )
    if (
        current_sha != "unknown"
        and report_sha != "unknown"
        and current_sha != report_sha
    ):
        reasons.append(
            f"commit moved: report {report_sha[:8]} != HEAD {current_sha[:8]}"
        )

    raw_fingerprints = report_data.get("input_fingerprints")
    if raw_fingerprints is not None:
        norm_fps = normalize_input_fingerprints(raw_fingerprints)
        if norm_fps is None:
            reasons.append(
                "input_fingerprints is malformed: entries must carry valid path and sha256 strings"
            )
        else:
            current_fps = collect_input_fingerprints(repo_root)
            for rel in sorted(norm_fps):
                if rel in current_fps:
                    actual = current_fps[rel]
                else:
                    target_file = Path(repo_root) / rel
                    if target_file.is_file():
                        try:
                            actual = hashlib.sha256(
                                target_file.read_bytes()
                            ).hexdigest()
                        except OSError:
                            actual = None
                    else:
                        actual = None
                if actual != norm_fps[rel]:
                    reasons.append(f"essential input changed since report: {rel}")
    elif current_sha != "unknown":
        # Report predates fingerprinting: freshness of essential inputs is
        # unverifiable; treat dirty essential inputs as stale.
        dirty = [
            rel
            for rel in ESSENTIAL_INPUT_PATHS
            if rel in current_git.get("modified_files", [])
        ]
        if dirty:
            reasons.append(
                "essential inputs have uncommitted changes while the report "
                "carries no fingerprints: " + ", ".join(dirty)
            )

    is_stale = bool(reasons)
    details = {
        "is_stale": is_stale,
        "reasons": reasons,
        "current_commit": current_sha,
        "report_commit": report_sha,
        "current_branch": current_git.get("branch", "unknown"),
        "report_branch": report_git.get("branch", "unknown"),
    }
    return is_stale, details


def _registry_identity_delta(
    old_registry: Any, new_registry: Any
) -> Set[Tuple[str, str, str]]:
    """
    Structural identity delta between two registry documents, expressed in
    the declared-change vocabulary: (kind, role_id, installation) tuples.
    Binding mutations the vocabulary cannot express (actor re-pointing,
    planned -> active promotions, field edits) surface as 'mutate_role'
    elements, which no declaration may cover (fail-closed). Wave J: an
    installation `orchestration` block change (add, edit, or removal)
    surfaces as a ('set_orchestration', '', installation) element.
    """
    old_roles = (
        old_registry.get("roles")
        if isinstance(old_registry, dict)
        and isinstance(old_registry.get("roles"), dict)
        else {}
    )
    new_roles = (
        new_registry.get("roles")
        if isinstance(new_registry, dict)
        and isinstance(new_registry.get("roles"), dict)
        else {}
    )
    delta: Set[Tuple[str, str, str]] = set()
    for role_id in set(old_roles) | set(new_roles):
        old_role = old_roles.get(role_id)
        new_role = new_roles.get(role_id)
        old_bindings = (
            old_role.get("bindings")
            if isinstance(old_role, dict)
            and isinstance(old_role.get("bindings"), dict)
            else {}
        )
        new_bindings = (
            new_role.get("bindings")
            if isinstance(new_role, dict)
            and isinstance(new_role.get("bindings"), dict)
            else {}
        )
        for inst_id in set(old_bindings) | set(new_bindings):
            old_binding = old_bindings.get(inst_id)
            new_binding = new_bindings.get(inst_id)
            if old_binding is None and new_binding is not None:
                delta.add(("add_role", role_id, inst_id))
            elif new_binding is None and old_binding is not None:
                delta.add(("archive", role_id, inst_id))
            elif old_binding != new_binding:
                old_status = (old_binding or {}).get("status")
                new_status = (new_binding or {}).get("status")
                if old_status == "active" and new_status != "active":
                    delta.add(("disable", role_id, inst_id))
                else:
                    delta.add(("mutate_role", role_id, inst_id))
    # Wave J: installation-level `orchestration` blocks surface as
    # ('set_orchestration', '', installation) delta elements. The block
    # value is compared as a whole (absent -> None), so adding, editing,
    # and removing a declaration all produce exactly one element.
    old_installations = (
        old_registry.get("installations")
        if isinstance(old_registry, dict)
        and isinstance(old_registry.get("installations"), dict)
        else {}
    )
    new_installations = (
        new_registry.get("installations")
        if isinstance(new_registry, dict)
        and isinstance(new_registry.get("installations"), dict)
        else {}
    )
    for inst_id in set(old_installations) | set(new_installations):
        old_entry = old_installations.get(inst_id)
        new_entry = new_installations.get(inst_id)
        old_orchestration = (
            old_entry.get("orchestration")
            if isinstance(old_entry, dict)
            else None
        )
        new_orchestration = (
            new_entry.get("orchestration")
            if isinstance(new_entry, dict)
            else None
        )
        if old_orchestration != new_orchestration:
            delta.add(("set_orchestration", "", inst_id))
    return delta


def _normalize_declared_changes(
    declared_changes: Any,
) -> Tuple[Set[Tuple[str, str, Optional[str]]], List[str]]:
    """
    Validate and normalize a declared changes[] list into (kind, role_id,
    installation) tuples (installation None = wildcard for that pair).
    Wave J: installation-level kinds (INSTALLATION_CHANGE_KINDS, i.e.
    'set_orchestration') are declared as {"kind": ..., "installation":
    <id>} with NO role_id and NO path, and normalize to (kind, '',
    installation). Returns (declared_set, problems); a non-empty problems
    list refuses.
    """
    problems: List[str] = []
    declared: Set[Tuple[str, str, Optional[str]]] = set()
    if not isinstance(declared_changes, list) or not declared_changes:
        return set(), ["changes[] must be a non-empty list of change objects"]
    for idx, entry in enumerate(declared_changes):
        label = f"changes[{idx}]"
        if not isinstance(entry, dict):
            problems.append(f"{label} must be an object")
            continue
        unknown = sorted(set(entry) - MANAGE_CHANGE_FIELDS)
        if unknown:
            problems.append(
                f"{label} carries unsupported fields: {', '.join(unknown)} "
                "(allowed: kind, role_id, installation, path)"
            )
        kind = str(entry.get("kind", "")).strip()
        role_id = str(entry.get("role_id", "")).strip()
        installation = str(entry.get("installation", "")).strip()
        if kind not in VALID_MANAGE_CHANGE_KINDS:
            problems.append(
                f"{label}.kind '{kind}' is unsupported (allowed: "
                + ", ".join(sorted(VALID_MANAGE_CHANGE_KINDS))
                + ")"
            )
        if kind in INSTALLATION_CHANGE_KINDS:
            # Wave J installation-level kinds: identified by the
            # installation alone — role_id and path are prohibited.
            if role_id:
                problems.append(
                    f"{label}.kind '{kind}' must not carry role_id"
                )
            if not installation:
                problems.append(
                    f"{label}.installation is required for kind '{kind}'"
                )
            path = entry.get("path")
            if path is not None:
                problems.append(f"{label}.kind '{kind}' must not carry path")
            if kind in VALID_MANAGE_CHANGE_KINDS and installation:
                declared.add((kind, "", installation))
        else:
            if not role_id:
                problems.append(f"{label}.role_id is missing or empty")
            path = entry.get("path")
            if path is not None and not isinstance(path, str):
                problems.append(f"{label}.path must be a string")
            if kind in VALID_MANAGE_CHANGE_KINDS and role_id:
                declared.add((kind, role_id, installation or None))
    return declared, problems


def _recover_registry_baseline(
    repo_root: Path, commit_sha: str
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Registry bytes as committed at the init report's commit (git only,
    per the zero-dependency policy: stdlib + Git). Wave F M2: the commit
    SHA is validated (40-character hex) BEFORE it reaches the git
    subprocess — option-like values (argv injection) refuse here.
    Returns (bytes, None) or (None, error_message).
    """
    sha_error = _require_commit_sha(commit_sha, "git baseline lookup")
    if sha_error:
        return None, sha_error
    try:
        proc = subprocess.run(
            ["git", "show", f"{commit_sha}:{REGISTRY_PATH}"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=15,
        )
    except Exception as exc:
        return None, f"git baseline lookup failed: {exc}"
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        first_line = stderr.splitlines()[0] if stderr else "git show failed"
        return None, (
            f"registry '{REGISTRY_PATH}' not found in the git tree at report "
            f"commit '{commit_sha[:8]}' ({first_line})"
        )
    return proc.stdout, None


def verify_declared_registry_delta(
    repo_root: Path,
    report_data: Dict[str, Any],
    declared_changes: Any,
) -> Optional[str]:
    """
    Wave D T2.1: registry delta admission for manage intake.

    A registry unchanged since the init report is admitted. A changed
    registry is admitted ONLY when the delta is EXACTLY covered by the
    operation's declared changes[] (add_role/disable/archive with role ids
    and installations; Wave J adds the installation-level set_orchestration
    kind, declared as {"kind": "set_orchestration", "installation": <id>}
    with no role_id/path): the baseline registry is recovered from git at the
    report's recorded commit and hash-verified against the report's
    recorded fingerprint, so deltas rooted in uncommitted init-time state
    refuse instead of silently admitting. Every registry element not named
    by a declaration — and every declaration without a matching registry
    element — is refused with an explicit diff listing.

    Returns None when admitted, an intake refusal message otherwise.
    """
    fingerprints = report_data.get("input_fingerprints")
    norm_fps = normalize_input_fingerprints(fingerprints)
    recorded = (
        norm_fps.get(REGISTRY_PATH)
        if isinstance(norm_fps, dict)
        else None
    )
    registry_file = Path(repo_root) / REGISTRY_PATH
    current_bytes: Optional[bytes] = None
    if registry_file.is_file():
        try:
            current_bytes = registry_file.read_bytes()
        except OSError:
            current_bytes = None
    current_sha = (
        hashlib.sha256(current_bytes).hexdigest()
        if current_bytes is not None
        else None
    )

    if recorded is not None and recorded == current_sha:
        return None  # registry fresh
    if recorded is None and current_bytes is None:
        return None  # registry absent on both sides

    if not declared_changes:
        return (
            "Intake rejected: stale report (essential input changed since "
            f"report: {REGISTRY_PATH}; declare the registry delta via "
            "changes[] in the manage data file)"
        )

    declared, declaration_problems = _normalize_declared_changes(
        declared_changes
    )
    if declaration_problems:
        return (
            "Intake rejected: invalid changes[] declaration: "
            + "; ".join(declaration_problems)
        )

    git_state = report_data.get("git_state") or {}
    report_sha = str(git_state.get("commit_sha", "unknown")).strip()
    if recorded is None:
        return (
            "Intake rejected: cannot verify declared registry delta: the "
            "init report records no registry fingerprint; re-run init"
        )
    if not report_sha or report_sha == "unknown":
        return (
            "Intake rejected: cannot verify declared registry delta: the "
            "init report carries no commit reference; re-run init"
        )
    # Wave F M2: the report-recorded SHA is validated before the git
    # subprocess — option-like values (argv injection) refuse here.
    sha_error = _require_commit_sha(report_sha, "init report git_state")
    if sha_error:
        return (
            "Intake rejected: cannot verify declared registry delta: "
            + sha_error
        )

    baseline_bytes, baseline_err = _recover_registry_baseline(
        repo_root, report_sha
    )
    if baseline_err:
        return (
            "Intake rejected: cannot verify declared registry delta: "
            + baseline_err
        )
    # Sanity anchor: the baseline must be the registry state the report
    # fingerprinted. core.autocrlf environments store LF-normalized blobs
    # while Windows working trees carry CRLF, so the recorded fingerprint
    # (taken from raw working-tree bytes) may correspond to either EOL form
    # of the blob. Accept a match on the raw bytes, their LF-normalized
    # form, or their CRLF form; the delta verification below parses JSON,
    # which is line-ending agnostic — the hash only guards against
    # baselines rooted in uncommitted init-time state.
    lf_bytes = baseline_bytes.replace(b"\r\n", b"\n")
    baseline_variants = {
        hashlib.sha256(baseline_bytes).hexdigest(),
        hashlib.sha256(lf_bytes).hexdigest(),
        hashlib.sha256(lf_bytes.replace(b"\n", b"\r\n")).hexdigest(),
    }
    if recorded not in baseline_variants:
        return (
            "Intake rejected: cannot verify declared registry delta: "
            f"registry baseline at report commit '{report_sha[:8]}' does "
            "not match the report's recorded fingerprint (uncommitted "
            "registry changes at init time); re-run init"
        )

    try:
        baseline_registry = json.loads(baseline_bytes.decode("utf-8"))
        current_registry = (
            json.loads(current_bytes.decode("utf-8"))
            if current_bytes is not None
            else {}
        )
    except Exception as exc:
        return (
            "Intake rejected: cannot verify declared registry delta: "
            f"registry content is not valid JSON: {exc}"
        )

    delta = _registry_identity_delta(baseline_registry, current_registry)
    declared_full = {(k, r, i) for (k, r, i) in declared}
    declared_wild = {(k, r) for (k, r, i) in declared if i is None}

    def _covered(element: Tuple[str, str, str]) -> bool:
        kind, role_id, installation = element
        if (kind, role_id, installation) in declared_full:
            return True
        return (kind, role_id) in declared_wild

    uncovered = sorted(el for el in delta if not _covered(el))
    matched_wild_pairs = {
        (k, r) for (k, r, _i) in delta if (k, r) in declared_wild
    }
    unmatched: List[Tuple[str, str, Optional[str]]] = []
    unmatched.extend(sorted(declared_full - delta))
    unmatched.extend(
        sorted(
            (k, r, None) for (k, r) in declared_wild - matched_wild_pairs
        )
    )

    if not uncovered and not unmatched:
        return None

    def _describe(kind: str, role_id: str, installation: Optional[str]) -> str:
        # Wave J: installation-level kinds (set_orchestration) carry no
        # role — describe them as "<kind> (installation '<id>')".
        if kind in INSTALLATION_CHANGE_KINDS:
            return f"{kind} (installation '{installation}')"
        suffix = (
            f" (installation '{installation}')"
            if installation
            else " (any installation)"
        )
        return f"{kind} role '{role_id}'{suffix}"

    listings: List[str] = []
    for kind, role_id, installation in uncovered:
        listings.append(f"uncovered registry delta: {_describe(kind, role_id, installation)}")
    for kind, role_id, installation in unmatched:
        listings.append(
            f"declared change with no matching registry delta: "
            f"{_describe(kind, role_id, installation)}"
        )
    return (
        "Intake rejected: registry delta not covered by declared "
        "changes[]: " + "; ".join(listings)
    )


def evaluate_manage_intake(
    repo_root: Path,
    installation_id: str,
    harness_id: str,
    actor_id: str,
    report_path: Path,
    declared_changes: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    """
    Intake admission for the init -> manage contract (audit §5, Wave D T2.1).

    Separates two mechanisms: format validation (is the report a correct
    document?) and intake admission (may THIS document authorize a manage
    operation in THIS project/installation?). A blocked report can be a
    correct document and must still be refused.

    The registry (`.agents/meta-project.json`) is the one essential input a
    manage operation may legitimately change (it deploys roles + bindings).
    A registry change since the init report is admitted only when it is
    EXACTLY covered by `declared_changes` (the manage operation's changes[]
    list, add_role/disable/archive with role ids/installations) — see
    `verify_declared_registry_delta`. Staleness for the other essential
    inputs (boundaries.md, AGENTS.md) is unaffected; commit movement alone
    no longer refuses (supersession by a newer init run is checked instead).

    Returns a list of intake errors; an empty list admits the operation.
    """
    repo_root = Path(repo_root)
    report_path = Path(report_path)
    errors: List[str] = []

    # 1. The report file must exist and parse (structured diagnostics).
    if not report_path.is_file():
        return [f"Intake rejected: report file not found: {report_path}"]
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return [f"Intake rejected: report file is corrupted (JSON parse error): {exc}"]
    if not isinstance(data, dict):
        return ["Intake rejected: report content must be a JSON object"]

    # 2. Format validation (fail-closed on structurally invalid documents).
    format_errors = validate_report(data, expected_type="init")
    if format_errors:
        return [f"Intake rejected: invalid init report: {e}" for e in format_errors]

    # 3. Project identity comes from the local registry, never from a
    # hardcoded default; explicit mismatch is refused.
    if load_registry is None:
        return ["Intake rejected: identity engine unavailable in this environment"]
    registry, reg_err = load_registry(repo_root)
    if registry is None:
        return [f"Intake rejected: local registry unavailable: {reg_err}"]
    registry_project = registry.get("project_id")
    if data.get("project_id") != registry_project:
        errors.append(
            f"Intake rejected: report project_id '{data.get('project_id')}' does "
            f"not match local registry project_id '{registry_project}'"
        )

    # 4. Installation and harness must match the local registry and report.
    inst_info = (registry.get("installations") or {}).get(installation_id)
    if not isinstance(inst_info, dict):
        errors.append(
            f"Intake rejected: installation '{installation_id}' is not "
            f"registered in the local registry"
        )
    else:
        if inst_info.get("harness_id") != harness_id:
            errors.append(
                f"Intake rejected: harness '{harness_id}' does not match "
                f"installation '{installation_id}' harness_id "
                f"'{inst_info.get('harness_id')}'"
            )
        if inst_info.get("status") != "active":
            errors.append(
                f"Intake rejected: installation '{installation_id}' status is "
                f"'{inst_info.get('status')}', not 'active'"
            )
    if data.get("installation_id") != installation_id:
        errors.append(
            f"Intake rejected: report installation_id "
            f"'{data.get('installation_id')}' != target '{installation_id}'"
        )
    if data.get("harness_id") != harness_id:
        errors.append(
            f"Intake rejected: report harness_id "
            f"'{data.get('harness_id')}' != target '{harness_id}'"
        )

    # 5. Actor admission: the initiator must be a registered, ACTIVE identity.
    if resolve_actor_binding is not None and evaluate_actor_admission is not None:
        found, binding = resolve_actor_binding(repo_root, actor_id)
        if not found:
            errors.append(
                f"Intake rejected: actor_id '{actor_id}' not found in registry"
            )
        else:
            denial = evaluate_actor_admission(registry, binding)
            if denial:
                errors.append(f"Intake rejected: {denial}")
    else:
        errors.append("Intake rejected: identity engine unavailable")

    # 6. Status & readiness: only a completed, ready initialization
    # authorizes manage; blocked/awaiting reports are decision ledgers.
    status = data.get("status")
    if status != "completed":
        errors.append(
            f"Intake rejected: init report status is '{status}'; only "
            f"'completed' authorizes manage operations"
        )
    else:
        readiness = data.get("next_step_readiness")
        if not isinstance(readiness, dict) or readiness.get("ready_for_manage") is not True:
            errors.append(
                "Intake rejected: next_step_readiness.ready_for_manage is not "
                "true for a completed report"
            )

    # 7. Freshness (Wave D T2.1): content freshness of the non-registry
    # essential inputs stays mandatory — uncommitted changes to
    # boundaries.md/AGENTS.md make the report stale. The registry delta is
    # NOT a blanket staleness trigger; it is admitted via declared
    # changes[] in step 7c.
    fingerprints = data.get("input_fingerprints")
    if fingerprints is not None:
        norm_fps = normalize_input_fingerprints(fingerprints)
        if norm_fps is None:
            errors.append(
                "Intake rejected: malformed input_fingerprints in report"
            )
        else:
            current_fps = collect_input_fingerprints(repo_root)
            for rel in sorted(norm_fps):
                if rel == REGISTRY_PATH:
                    continue  # handled by declared-delta admission (7c)
                if rel in current_fps:
                    actual = current_fps[rel]
                else:
                    p = Path(repo_root) / rel
                    actual = (
                        hashlib.sha256(p.read_bytes()).hexdigest()
                        if p.is_file()
                        else None
                    )
                if actual != norm_fps.get(rel):
                    errors.append(
                        "Intake rejected: stale report (essential input changed "
                        f"since report: {rel})"
                    )
    else:
        # Report predates fingerprinting: freshness of essential inputs is
        # unverifiable; treat dirty non-registry essential inputs as stale.
        current_git = get_git_state(repo_root)
        dirty = [
            rel
            for rel in ESSENTIAL_INPUT_PATHS
            if rel != REGISTRY_PATH
            and rel in current_git.get("modified_files", [])
        ]
        if dirty:
            errors.append(
                "Intake rejected: stale report (essential inputs have "
                "uncommitted changes while the report carries no "
                "fingerprints: " + ", ".join(dirty) + ")"
            )

    # 7b. Supersession (Wave D T2.1): a newer init run for this installation
    # supersedes the referenced report. This replaces the removed
    # commit-moved staleness trigger: pure HEAD movement with fresh inputs
    # is admitted, but planning against an outdated initialization is not.
    latest_path, latest_data = find_latest_report(
        repo_root, installation_id, "init"
    )
    if latest_path is not None:
        referenced_id = str(data.get("run_id", "")).strip()
        latest_id = (
            str(latest_data.get("run_id", "")).strip()
            if isinstance(latest_data, dict)
            else ""
        ) or latest_path.stem
        if latest_id and latest_id != referenced_id:
            errors.append(
                "Intake rejected: init report is superseded by a newer init "
                f"run '{latest_id}' ({latest_path}); re-plan against the "
                "current initialization"
            )

    # 7c. Registry delta admission (Wave D T2.1): unchanged registry passes;
    # a changed registry must be EXACTLY covered by the declared changes[].
    registry_error = verify_declared_registry_delta(
        repo_root, data, declared_changes
    )
    if registry_error:
        errors.append(registry_error)

    return errors


def _resolve_project_id(
    repo_root: Path, explicit: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Project identity resolution (audit §5): explicit argument wins, otherwise
    the local registry is the source of truth. The hardcoded default
    'vlv-code/meta-project' is removed — foreign projects must never be
    silently stamped with another project's identity.
    Returns (project_id, error_message).
    """
    if explicit:
        return explicit, None
    if load_registry is not None:
        registry, _ = load_registry(Path(repo_root))
        if isinstance(registry, dict) and registry.get("project_id"):
            return registry["project_id"], None
    return None, (
        "--project-id is required when no local registry "
        "(.agents/meta-project.json) defines the project identity"
    )


