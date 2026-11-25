#!/usr/bin/env python3
"""
scripts/_inspect_classifier.py

Canonical state classification ladder, capability matrix evaluator, and
report lookup helpers for inspect_meta_project (ADR #22 submodule).
Pure Python 3.10+ standard library, zero external dependencies.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class InspectionState(str, Enum):
    """Canonical repository states for Meta-Project."""
    NONE = "NONE"
    FOREIGN_RULES = "FOREIGN_RULES"
    HEALTHY_REGISTERED = "HEALTHY_REGISTERED"
    HEALTHY_NEW_HARNESS = "HEALTHY_NEW_HARNESS"
    CONTEXT_UNRESOLVED = "CONTEXT_UNRESOLVED"
    LEGACY_UNREGISTERED = "LEGACY_UNREGISTERED"
    PARTIAL_CORRUPTED = "PARTIAL_CORRUPTED"
    INCOMPATIBLE_SCHEMA = "INCOMPATIBLE_SCHEMA"


class CapabilityStatus(str, Enum):
    """5-dimension Capability Matrix status levels."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNTESTED = "untested"


SUPPORTED_SCHEMA_VERSIONS = {"1.0.0", "1.1.0", "1.0", "1.1", "1"}

CANONICAL_ACTIONS: Dict[str, str] = {
    InspectionState.NONE.value: "scaffold_clean",
    InspectionState.FOREIGN_RULES.value: "preserve_and_merge",
    InspectionState.HEALTHY_REGISTERED.value: "pass_through",
    InspectionState.HEALTHY_NEW_HARNESS.value: "bind_harness",
    InspectionState.CONTEXT_UNRESOLVED.value: "provide_runtime_context",
    InspectionState.LEGACY_UNREGISTERED.value: "adopt_legacy",
    InspectionState.PARTIAL_CORRUPTED.value: "diagnose_and_repair",
    InspectionState.INCOMPATIBLE_SCHEMA.value: "read_only_fallback",
}

STATE_DESCRIPTIONS: Dict[str, str] = {
    InspectionState.NONE.value: "No agent scaffolding or instructions found.",
    InspectionState.FOREIGN_RULES.value: "Foreign instructions found without Meta-Project framework.",
    InspectionState.HEALTHY_REGISTERED.value: (
        "Meta-Project intact and current harness installation is registered and active."
    ),
    InspectionState.HEALTHY_NEW_HARNESS.value: (
        "Meta-Project intact, but the active harness/installation is not registered or planned."
    ),
    InspectionState.CONTEXT_UNRESOLVED.value: (
        "Meta-Project structure is healthy, but no runtime context "
        "(--harness/--installation) was provided: registered status for the "
        "caller cannot be determined without silently adopting an arbitrary "
        "active installation (audit §4)."
    ),
    InspectionState.LEGACY_UNREGISTERED.value: (
        "Legacy Meta-Project structure detected without multi-harness registry."
    ),
    InspectionState.PARTIAL_CORRUPTED.value: (
        "Meta-Project structure is incomplete, corrupted, or missing critical slices."
    ),
    InspectionState.INCOMPATIBLE_SCHEMA.value: (
        "Registry schema version is incompatible with current inspector tooling."
    ),
}

FOREIGN_RULE_FILES: List[str] = [
    "CLAUDE.md",
    ".cursorrules",
    ".cursor/rules",
    ".windsurfrules",
    ".copilot-instructions.md",
]


def resolve_installation_matching(
    installations: Dict[str, Any],
    target_harness: Optional[str] = None,
    target_installation: Optional[str] = None,
) -> Tuple[InspectionState, Optional[str]]:
    """Resolve installation matching against harness/installation flags."""
    harness = target_harness
    inst_id = target_installation

    if inst_id:
        inst_info = installations.get(inst_id)
        if not isinstance(inst_info, dict) or inst_info.get("status") != "active":
            return InspectionState.HEALTHY_NEW_HARNESS, inst_id
        if harness and inst_info.get("harness_id") != harness:
            return InspectionState.HEALTHY_NEW_HARNESS, inst_id
        return InspectionState.HEALTHY_REGISTERED, inst_id

    if harness:
        # Search installation matching harness (Lane Z1-D: auto-resolve single active)
        active_matching = [
            iid
            for iid, info in installations.items()
            if isinstance(info, dict)
            and info.get("harness_id") == harness
            and info.get("status") == "active"
        ]
        if len(active_matching) == 1:
            return InspectionState.HEALTHY_REGISTERED, active_matching[0]
        if len(active_matching) > 1:
            return InspectionState.HEALTHY_REGISTERED, None
        return InspectionState.HEALTHY_NEW_HARNESS, None

    return InspectionState.CONTEXT_UNRESOLVED, None


def classify_repository_state(
    has_agents_md: bool,
    is_meta_agents: bool,
    agents_dir_exists: bool,
    pk_dir_exists: bool,
    registry_file_exists: bool,
    registry_file_is_file: bool,
    boundaries_file_is_file: bool,
    foreign_instructions: List[str],
    registry_corrupted: bool,
    schema_version: Optional[str],
    registry_errors: List[str],
    installations: Dict[str, Any],
    target_harness: Optional[str] = None,
    target_installation: Optional[str] = None,
) -> Tuple[InspectionState, Optional[str], List[str], List[str]]:
    """
    Classify repository state into one of the 8 canonical states.
    Returns: (state, resolved_target_installation, missing_components, conflicts)
    """
    missing_components: List[str] = []
    conflicts: List[str] = []
    resolved_inst = target_installation

    if not has_agents_md and not agents_dir_exists and not foreign_instructions:
        return InspectionState.NONE, resolved_inst, missing_components, conflicts

    if foreign_instructions and not is_meta_agents and not agents_dir_exists:
        return InspectionState.FOREIGN_RULES, resolved_inst, missing_components, conflicts

    if is_meta_agents or pk_dir_exists or registry_file_exists:
        if registry_corrupted:
            missing_components.append(".agents/meta-project.json (malformed JSON)")
            return InspectionState.PARTIAL_CORRUPTED, resolved_inst, missing_components, conflicts

        if not registry_file_is_file:
            missing_components.append(".agents/meta-project.json")
            return InspectionState.LEGACY_UNREGISTERED, resolved_inst, missing_components, conflicts

        supported_majors = [v.split(".")[0] for v in SUPPORTED_SCHEMA_VERSIONS]
        if schema_version and schema_version.split(".")[0] not in supported_majors:
            conflicts.append(f"Unsupported schema_version: {schema_version}")
            return InspectionState.INCOMPATIBLE_SCHEMA, resolved_inst, missing_components, conflicts

        if not boundaries_file_is_file:
            missing_components.append(".agents/project_knowledge/boundaries.md")
            return InspectionState.PARTIAL_CORRUPTED, resolved_inst, missing_components, conflicts

        if not (has_agents_md and is_meta_agents):
            missing_components.append(
                "AGENTS.md (project passport missing or not a Meta-Project passport)"
            )
            return InspectionState.PARTIAL_CORRUPTED, resolved_inst, missing_components, conflicts

        if registry_errors:
            conflicts.extend(f"registry invalid: {e}" for e in registry_errors[:5])
            return InspectionState.PARTIAL_CORRUPTED, resolved_inst, missing_components, conflicts

        # Valid registry, boundaries, and passport: evaluate installation matching
        state, resolved_inst = resolve_installation_matching(
            installations=installations,
            target_harness=target_harness,
            target_installation=target_installation,
        )
        return state, resolved_inst, missing_components, conflicts

    if foreign_instructions:
        return InspectionState.FOREIGN_RULES, resolved_inst, missing_components, conflicts

    return InspectionState.NONE, resolved_inst, missing_components, conflicts


def evaluate_capability_matrix(
    repo_root: Path,
    is_meta_agents: bool,
    pk_dir: Path,
    check_boundaries_script: Path,
    verify_identity_script: Path,
    agents_dir: Path,
    roles: Dict[str, Any],
    target_installation: Optional[str] = None,
    common_hooks_dir: Optional[Path] = None,
) -> Dict[str, Dict[str, str]]:
    """Evaluate 5-dimension Capability Matrix."""
    # 1. read_instructions
    can_read_instructions = is_meta_agents and pk_dir.is_dir()
    cap_read_instructions = {
        "status": CapabilityStatus.AVAILABLE.value if can_read_instructions else CapabilityStatus.UNAVAILABLE.value,
        "detail": (
            "Root AGENTS.md and knowledge slices accessible"
            if can_read_instructions
            else "AGENTS.md or .agents/project_knowledge missing"
        ),
    }

    # 2. local_checks
    can_local_checks = check_boundaries_script.is_file() and verify_identity_script.is_file()
    cap_local_checks = {
        "status": CapabilityStatus.AVAILABLE.value if can_local_checks else CapabilityStatus.UNAVAILABLE.value,
        "detail": (
            "check_boundaries.py and verify_identity.py present"
            if can_local_checks
            else "Local inspection and boundary scripts not deployed"
        ),
    }

    # 3. skills
    local_skills_dir = agents_dir / "skills"
    has_local_skills = False
    if local_skills_dir.is_dir():
        for item in local_skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").is_file():
                has_local_skills = True
                break
    cap_skills = {
        "status": CapabilityStatus.AVAILABLE.value if has_local_skills else CapabilityStatus.UNAVAILABLE.value,
        "detail": (
            "Local procedural skills deployed in .agents/skills/"
            if has_local_skills
            else "No local skills found in .agents/skills/"
        ),
    }

    # 4. roles — scoped to the TARGET installation
    if target_installation:
        has_roles = False
        for _r_name, r_info in roles.items():
            if isinstance(r_info, dict):
                b_info = r_info.get("bindings", {}).get(target_installation)
                if (
                    isinstance(b_info, dict)
                    and b_info.get("status") == "active"
                    and b_info.get("profile_path")
                ):
                    profile_path = repo_root / b_info["profile_path"]
                    if profile_path.is_file():
                        has_roles = True
                        break
        cap_roles = {
            "status": CapabilityStatus.AVAILABLE.value if has_roles else CapabilityStatus.UNAVAILABLE.value,
            "detail": (
                f"Active role profiles located and verified for installation '{target_installation}'"
                if has_roles
                else f"No active role profiles bound to installation '{target_installation}'"
            ),
        }
    else:
        cap_roles = {
            "status": CapabilityStatus.UNTESTED.value,
            "detail": (
                "Runtime context unknown (--installation not provided): "
                "role availability for a specific installation is undetermined"
            ),
        }

    # 5. hooks — resolved via the shared hooks directory
    hook_file = (common_hooks_dir / "pre-commit") if common_hooks_dir else None
    hook_available = False
    if hook_file and hook_file.is_file():
        try:
            hook_text = hook_file.read_text(encoding="utf-8")
            if "check_boundaries" in hook_text:
                hook_available = True
        except Exception:
            pass
    cap_hooks = {
        "status": CapabilityStatus.AVAILABLE.value if hook_available else CapabilityStatus.UNAVAILABLE.value,
        "detail": (
            "Git pre-commit hook incorporates check_boundaries"
            if hook_available
            else "Git pre-commit hook with boundary check not installed"
        ),
    }

    return {
        "read_instructions": cap_read_instructions,
        "local_checks": cap_local_checks,
        "skills": cap_skills,
        "roles": cap_roles,
        "hooks": cap_hooks,
    }


def find_latest_init_report(
    reports_base: Path,
    target_installation: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Locate latest init report for the given installation."""
    if not reports_base.is_dir() or not target_installation:
        return None

    init_dir = reports_base / target_installation / "init"
    if not init_dir.is_dir():
        return None

    ptr_file = init_dir / "latest.json"
    if ptr_file.is_file():
        try:
            ptr_data = json.loads(ptr_file.read_text(encoding="utf-8"))
            return {
                "run_id": ptr_data.get("run_id"),
                "status": ptr_data.get("status"),
                "created_at": ptr_data.get("created_at"),
                "path": ptr_data.get("path"),
                "installation_id": target_installation,
            }
        except Exception:
            pass

    report_files = sorted(
        [p for p in init_dir.glob("*.json") if p.name != "latest.json"],
        key=lambda p: p.name,
        reverse=True,
    )
    if report_files:
        try:
            rf_data = json.loads(report_files[0].read_text(encoding="utf-8"))
            return {
                "run_id": rf_data.get("run_id"),
                "status": rf_data.get("status"),
                "created_at": rf_data.get("created_at"),
                "path": str(report_files[0].resolve()).replace("\\", "/"),
                "installation_id": target_installation,
            }
        except Exception:
            pass

    return None
