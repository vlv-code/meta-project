#!/usr/bin/env python3
"""
Meta-Project Report Management Engine (scripts/manage_reports.py)

Deterministic, zero-dependency Python 3.10+ stdlib CLI and library for creating,
validating, locating, and inspecting initialization ('init') and management ('manage')
JSON reports in .agents/reports/<installation_id>/{init,manage}/.
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple
import uuid

SUPPORTED_SCHEMA_VERSIONS = {"1.0.0", "1.0", "1"}
VALID_REPORT_TYPES = {"init", "manage"}
VALID_REPORT_STATUSES = {"completed", "awaiting_decision", "blocked"}

VALID_SCENARIO_PROFILES = {
    "active_development",
    "maintenance",
    "research",
    "audit",
    "documentation",
}
VALID_DEPLOYMENT_MODES = {"shared_repo", "local_overlay", "hybrid"}
VALID_COLLABORATION_MODELS = {"solo", "duo", "triad", "specialized_swarm"}
VALID_VERIFICATION_POLICIES = {
    "self_check",
    "duo_peer_review",
    "strict_independent",
}
VALID_DELEGATION_LEVELS = {"strictly_manual", "controlled", "autonomous"}


def generate_run_id(prefix: str = "") -> str:
    """Generate deterministic UTC timestamp + short UUID run identifier."""
    now = datetime.datetime.now(datetime.timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%SZ")
    uid = uuid.uuid4().hex[:8]
    return f"{prefix}{ts}-{uid}" if not prefix else f"{prefix}-{ts}-{uid}"


def get_git_state(repo_root: Path) -> Dict[str, Any]:
    """Extract current git state without external dependencies."""
    commit_sha = "unknown"
    branch = "unknown"
    is_clean = True
    modified_files: List[str] = []

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0:
            commit_sha = proc.stdout.strip()
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0:
            branch = proc.stdout.strip()
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-z"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=5,
        )
        if proc.returncode == 0 and proc.stdout:
            raw_entries = proc.stdout.split(b"\x00")
            for entry in raw_entries:
                if entry:
                    # Format: XY PATH
                    path_str = entry[3:].decode("utf-8", errors="replace")
                    if path_str:
                        modified_files.append(path_str.replace("\\", "/"))
            is_clean = len(modified_files) == 0
    except Exception:
        pass

    return {
        "commit_sha": commit_sha,
        "branch": branch,
        "is_clean": is_clean,
        "modified_files": modified_files,
    }


def validate_report(
    data: Dict[str, Any], expected_type: Optional[str] = None
) -> List[str]:
    """Validate report structure and schemas against fail-closed invariants."""
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["Report content must be a JSON object"]

    schema_version = str(data.get("schema_version", "")).strip()
    if not schema_version:
        errors.append("Missing required field 'schema_version'")
    elif (
        schema_version not in SUPPORTED_SCHEMA_VERSIONS
        and schema_version.split(".")[0]
        not in [v.split(".")[0] for v in SUPPORTED_SCHEMA_VERSIONS]
    ):
        errors.append(f"Unsupported schema_version: '{schema_version}'")

    report_type = str(data.get("report_type", "")).strip()
    if not report_type:
        errors.append("Missing required field 'report_type'")
    elif report_type not in VALID_REPORT_TYPES:
        errors.append(
            f"Invalid report_type: '{report_type}'. Allowed: {sorted(list(VALID_REPORT_TYPES))}"
        )
    elif expected_type and report_type != expected_type:
        errors.append(
            f"Expected report_type '{expected_type}', got '{report_type}'"
        )

    for field in [
        "project_id",
        "installation_id",
        "harness_id",
        "actor_id",
        "run_id",
    ]:
        val = str(data.get(field, "")).strip()
        if not val:
            errors.append(f"Missing required field '{field}'")

    status = str(data.get("status", "")).strip()
    if not status:
        errors.append("Missing required field 'status'")
    elif status not in VALID_REPORT_STATUSES:
        errors.append(
            f"Invalid status: '{status}'. Allowed: {sorted(list(VALID_REPORT_STATUSES))}"
        )

    git_state = data.get("git_state")
    if not isinstance(git_state, dict):
        errors.append("Missing or invalid field 'git_state' (must be an object)")

    # Type-specific validation
    if report_type == "init":
        scenario = data.get("scenario")
        if not isinstance(scenario, dict):
            errors.append("Missing or invalid field 'scenario' in init report")
        else:
            profile = scenario.get("profile")
            if profile and profile not in VALID_SCENARIO_PROFILES:
                errors.append(
                    f"Invalid scenario profile: '{profile}'. Allowed: {sorted(list(VALID_SCENARIO_PROFILES))}"
                )

        readiness = data.get("next_step_readiness")
        if not isinstance(readiness, dict):
            errors.append(
                "Missing or invalid field 'next_step_readiness' in init report"
            )

    elif report_type == "manage":
        init_run_id = str(data.get("init_run_id", "")).strip()
        if not init_run_id:
            errors.append(
                "Missing required field 'init_run_id' in manage report"
            )

        roles = data.get("roles")
        if not isinstance(roles, dict):
            errors.append("Missing or invalid field 'roles' in manage report")

        bindings = data.get("bindings")
        if not isinstance(bindings, dict):
            errors.append("Missing or invalid field 'bindings' in manage report")

    return errors


def get_report_dir(
    repo_root: Path, installation_id: str, report_type: str
) -> Path:
    """Return destination directory for reports."""
    return repo_root / ".agents" / "reports" / installation_id / report_type


def save_report(
    repo_root: Path,
    installation_id: str,
    report_type: str,
    report_data: Dict[str, Any],
) -> Path:
    """
    Atomically write report to disk and update latest.json pointer.
    Raises ValueError if data is invalid.
    """
    errors = validate_report(report_data, expected_type=report_type)
    if errors:
        raise ValueError(f"Cannot save invalid report: {'; '.join(errors)}")

    target_dir = get_report_dir(repo_root, installation_id, report_type)
    target_dir.mkdir(parents=True, exist_ok=True)

    run_id = report_data["run_id"]
    target_file = target_dir / f"{run_id}.json"
    temp_file = target_dir / f".tmp_{run_id}_{uuid.uuid4().hex[:6]}.json"

    # 1. Atomic write of full report
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    temp_file.replace(target_file)

    # 2. Atomic write of latest pointer
    latest_pointer_file = target_dir / "latest.json"
    temp_latest = target_dir / f".tmp_latest_{uuid.uuid4().hex[:6]}.json"
    pointer_data = {
        "run_id": run_id,
        "status": report_data["status"],
        "created_at": report_data.get("created_at"),
        "report_type": report_type,
        "installation_id": installation_id,
        "path": str(target_file.resolve()).replace("\\", "/"),
    }
    with open(temp_latest, "w", encoding="utf-8") as f:
        json.dump(pointer_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    temp_latest.replace(latest_pointer_file)
    return target_file


def find_latest_report(
    repo_root: Path, installation_id: str, report_type: str
) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
    """
    Find and load the latest valid report for given installation and type.
    Returns (Path, Dict) or (None, None).
    """
    target_dir = get_report_dir(repo_root, installation_id, report_type)
    if not target_dir.exists():
        return None, None

    # Check latest.json first
    latest_pointer = target_dir / "latest.json"
    if latest_pointer.exists():
        try:
            with open(latest_pointer, "r", encoding="utf-8") as f:
                ptr = json.load(f)
            report_path = Path(ptr.get("path", ""))
            if report_path.exists():
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not validate_report(data, expected_type=report_type):
                    return report_path, data
        except Exception:
            pass

    # Fallback: scan all JSON files sorted descending
    candidates = sorted(
        [p for p in target_dir.glob("*.json") if p.name != "latest.json"],
        key=lambda p: p.name,
        reverse=True,
    )
    for cand in candidates:
        try:
            with open(cand, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not validate_report(data, expected_type=report_type):
                return cand, data
        except Exception:
            continue

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
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

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
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to assemble a canonical manage report dictionary."""
    git_state = get_git_state(repo_root)
    actual_run_id = run_id or generate_run_id("manage")
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

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
        "scenario": scenario,
        "roles": roles,
        "bindings": bindings,
        "effective_capabilities": effective_capabilities
        or {"team_readiness": "ready"},
        "checks": checks or [],
        "remaining_manual_actions": remaining_manual_actions or [],
    }


def resolve_team_topology(
    scenario: Dict[str, Any], loc_estimate: int = 0
) -> Dict[str, Any]:
    """
    Map scenario configuration to recommended agent team topology according to Phase 2 of manage-meta-project.
    Returns:
    {
        "target_topology": "solo" | "duo" | "triad" | "specialized_swarm",
        "suggested_roles": [...],
        "rationale": "..."
    }
    """
    profile = scenario.get("profile", "active_development")
    collab = scenario.get("collaboration_model", "")
    verification = scenario.get("verification_policy", "")

    if profile in ("documentation", "research") or collab == "solo":
        return {
            "target_topology": "solo",
            "suggested_roles": ["agent-general-worker"],
            "rationale": f"Solo Executor deployed for '{profile}' profile to prevent multi-agent handoff overhead.",
        }

    if (
        profile == "maintenance"
        or (0 < loc_estimate < 3000)
        or collab == "duo"
    ):
        return {
            "target_topology": "duo",
            "suggested_roles": ["agent-dev-lead", "agent-quality-guardian"],
            "rationale": "Micro-Mini Duo deployed for maintenance/compact repository with 2-stage handoff.",
        }

    if (
        profile == "active_development"
        and verification == "strict_independent"
    ) or collab == "triad":
        return {
            "target_topology": "triad",
            "suggested_roles": [
                "agent-dev-lead",
                "agent-quality-guardian",
                "agent-github-steward",
            ],
            "rationale": "Canonical Compact Trio deployed for active development with strict independent verification.",
        }

    return {
        "target_topology": "triad" if collab == "triad" else "duo",
        "suggested_roles": ["agent-dev-lead", "agent-quality-guardian"],
        "rationale": "Standard development team configuration.",
    }


def check_report_staleness(
    repo_root: Path, report_data: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluate if report's recorded git commit differs from the repository's current HEAD.
    Returns (is_stale, details).
    """
    current_git = get_git_state(repo_root)
    current_sha = current_git.get("commit_sha", "unknown")
    report_git = report_data.get("git_state", {})
    report_sha = report_git.get("commit_sha", "unknown")

    is_stale = False
    if (
        current_sha != "unknown"
        and report_sha != "unknown"
        and current_sha != report_sha
    ):
        is_stale = True

    details = {
        "is_stale": is_stale,
        "current_commit": current_sha,
        "report_commit": report_sha,
        "current_branch": current_git.get("branch", "unknown"),
        "report_branch": report_git.get("branch", "unknown"),
    }
    return is_stale, details


def build_cli_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Meta-Project Report Management Engine"
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # 1. init subcommand
    p_init = subparsers.add_parser(
        "init", help="Manage initialization (init) reports"
    )
    p_init.add_argument(
        "--action", choices=["create", "verify"], required=True
    )
    p_init.add_argument(
        "--repo-root", default=".", help="Target repository root path"
    )
    p_init.add_argument(
        "--installation", help="Target installation ID (e.g. ag-main)"
    )
    p_init.add_argument("--harness", help="Harness ID (e.g. antigravity)")
    p_init.add_argument("--actor", help="Qualified actor_id")
    p_init.add_argument(
        "--project-id", default="vlv-code/meta-project", help="Project ID"
    )
    p_init.add_argument(
        "--status",
        choices=["completed", "awaiting_decision", "blocked"],
        default="completed",
    )
    p_init.add_argument(
        "--scenario-file", help="Path to JSON file containing scenario data"
    )
    p_init.add_argument(
        "--data-file", help="Path to JSON file with additional init data"
    )
    p_init.add_argument("--report", help="Path to report file for verification")
    p_init.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    # 2. manage subcommand
    p_manage = subparsers.add_parser(
        "manage", help="Manage team management (manage) reports"
    )
    p_manage.add_argument(
        "--action", choices=["create", "verify"], required=True
    )
    p_manage.add_argument(
        "--repo-root", default=".", help="Target repository root path"
    )
    p_manage.add_argument(
        "--installation", help="Target installation ID (e.g. ag-main)"
    )
    p_manage.add_argument("--harness", help="Harness ID (e.g. antigravity)")
    p_manage.add_argument("--actor", help="Qualified actor_id")
    p_manage.add_argument(
        "--project-id", default="vlv-code/meta-project", help="Project ID"
    )
    p_manage.add_argument(
        "--init-run-id", help="Reference to preceding init run ID"
    )
    p_manage.add_argument(
        "--status",
        choices=["completed", "awaiting_decision", "blocked"],
        default="completed",
    )
    p_manage.add_argument(
        "--data-file",
        help="Path to JSON file containing roles, bindings, and capabilities",
    )
    p_manage.add_argument(
        "--report", help="Path to report file for verification"
    )
    p_manage.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    # 3. latest subcommand
    p_latest = subparsers.add_parser(
        "latest", help="Find latest report for an installation"
    )
    p_latest.add_argument(
        "--repo-root", default=".", help="Target repository root path"
    )
    p_latest.add_argument(
        "--installation", required=True, help="Installation ID"
    )
    p_latest.add_argument(
        "--type", choices=["init", "manage"], required=True, help="Report type"
    )
    p_latest.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    # 4. verify subcommand
    p_verify = subparsers.add_parser(
        "verify", help="Validate an existing report file"
    )
    p_verify.add_argument("--report", required=True, help="Path to report file")
    p_verify.add_argument(
        "--type",
        choices=["init", "manage"],
        help="Expected report type (optional)",
    )
    p_verify.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_cli_parser()
    args = parser.parse_args()
    repo_root = Path(getattr(args, "repo_root", ".")).resolve()

    if args.subcommand == "init":
        if args.action == "verify":
            if not args.report:
                sys.stderr.write("Error: --report is required for verify action\n")
                return 2
            report_path = Path(args.report)
            if not report_path.exists():
                sys.stderr.write(f"Error: File '{report_path}' not found\n")
                return 1
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                errors = validate_report(data, expected_type="init")
                if errors:
                    if args.json:
                        print(
                            json.dumps(
                                {
                                    "valid": False,
                                    "report": str(report_path),
                                    "errors": errors,
                                }
                            )
                        )
                    else:
                        print(
                            f"[FAIL] Invalid init report '{report_path}':\n"
                            + "\n".join(f"  * {e}" for e in errors)
                        )
                    return 1
                if args.json:
                    print(
                        json.dumps(
                            {
                                "valid": True,
                                "report": str(report_path),
                                "run_id": data.get("run_id"),
                                "status": data.get("status"),
                            }
                        )
                    )
                else:
                    print(f"[OK] Init report '{report_path}' is valid.")
                return 0
            except Exception as e:
                sys.stderr.write(f"Error reading report: {e}\n")
                return 1

        elif args.action == "create":
            if not args.installation or not args.harness or not args.actor:
                sys.stderr.write(
                    "Error: --installation, --harness, and --actor are required for create action\n"
                )
                return 2

            scenario = {}
            if args.scenario_file:
                with open(args.scenario_file, "r", encoding="utf-8") as f:
                    scenario = json.load(f)

            extra_data = {}
            if args.data_file:
                with open(args.data_file, "r", encoding="utf-8") as f:
                    extra_data = json.load(f)

            report = create_init_report(
                repo_root=repo_root,
                installation_id=args.installation,
                harness_id=args.harness,
                actor_id=args.actor,
                project_id=args.project_id,
                status=args.status,
                scenario=scenario or extra_data.get("scenario", {}),
                environment=extra_data.get("environment"),
                components=extra_data.get("components"),
                checks=extra_data.get("checks"),
                recommendations=extra_data.get("recommendations_for_manage"),
                blockers=extra_data.get("blockers_and_unresolved"),
                next_step_readiness=extra_data.get("next_step_readiness"),
            )

            try:
                saved_path = save_report(
                    repo_root, args.installation, "init", report
                )
                if args.json:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "run_id": report["run_id"],
                                "report_path": str(
                                    saved_path.resolve()
                                ).replace("\\", "/"),
                                "status": report["status"],
                            }
                        )
                    )
                else:
                    print(
                        f"[OK] Init report created: {saved_path} (run_id={report['run_id']})"
                    )
                return 0
            except Exception as e:
                sys.stderr.write(f"Error saving report: {e}\n")
                return 1

    elif args.subcommand == "manage":
        if args.action == "verify":
            if not args.report:
                sys.stderr.write("Error: --report is required for verify action\n")
                return 2
            report_path = Path(args.report)
            if not report_path.exists():
                sys.stderr.write(f"Error: File '{report_path}' not found\n")
                return 1
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                errors = validate_report(data, expected_type="manage")
                if errors:
                    if args.json:
                        print(
                            json.dumps(
                                {
                                    "valid": False,
                                    "report": str(report_path),
                                    "errors": errors,
                                }
                            )
                        )
                    else:
                        print(
                            f"[FAIL] Invalid manage report '{report_path}':\n"
                            + "\n".join(f"  * {e}" for e in errors)
                        )
                    return 1
                if args.json:
                    print(
                        json.dumps(
                            {
                                "valid": True,
                                "report": str(report_path),
                                "run_id": data.get("run_id"),
                                "status": data.get("status"),
                            }
                        )
                    )
                else:
                    print(f"[OK] Manage report '{report_path}' is valid.")
                return 0
            except Exception as e:
                sys.stderr.write(f"Error reading report: {e}\n")
                return 1

        elif args.action == "create":
            if (
                not args.installation
                or not args.harness
                or not args.actor
                or not args.init_run_id
            ):
                sys.stderr.write(
                    "Error: --installation, --harness, --actor, and --init-run-id are required for manage create\n"
                )
                return 2

            extra_data = {}
            if args.data_file:
                with open(args.data_file, "r", encoding="utf-8") as f:
                    extra_data = json.load(f)

            report = create_manage_report(
                repo_root=repo_root,
                installation_id=args.installation,
                harness_id=args.harness,
                actor_id=args.actor,
                project_id=args.project_id,
                init_run_id=args.init_run_id,
                status=args.status,
                scenario=extra_data.get("scenario", {}),
                roles=extra_data.get(
                    "roles",
                    {
                        "preserved": [],
                        "created": [],
                        "adapted": [],
                        "archived": [],
                    },
                ),
                bindings=extra_data.get("bindings", {}),
                effective_capabilities=extra_data.get(
                    "effective_capabilities"
                ),
                checks=extra_data.get("checks"),
                remaining_manual_actions=extra_data.get(
                    "remaining_manual_actions"
                ),
            )

            try:
                saved_path = save_report(
                    repo_root, args.installation, "manage", report
                )
                if args.json:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "run_id": report["run_id"],
                                "report_path": str(
                                    saved_path.resolve()
                                ).replace("\\", "/"),
                                "status": report["status"],
                            }
                        )
                    )
                else:
                    print(
                        f"[OK] Manage report created: {saved_path} (run_id={report['run_id']})"
                    )
                return 0
            except Exception as e:
                sys.stderr.write(f"Error saving report: {e}\n")
                return 1

    elif args.subcommand == "latest":
        report_path, report_data = find_latest_report(
            repo_root, args.installation, args.type
        )
        if not report_path or not report_data:
            if args.json:
                print(
                    json.dumps(
                        {
                            "found": False,
                            "installation": args.installation,
                            "type": args.type,
                        }
                    )
                )
            else:
                print(
                    f"No {args.type} report found for installation '{args.installation}'"
                )
            return 1

        is_stale, stale_info = check_report_staleness(repo_root, report_data)
        if args.json:
            print(
                json.dumps(
                    {
                        "found": True,
                        "report_path": str(report_path.resolve()).replace(
                            "\\", "/"
                        ),
                        "run_id": report_data.get("run_id"),
                        "status": report_data.get("status"),
                        "created_at": report_data.get("created_at"),
                        "is_stale": is_stale,
                        "current_commit": stale_info.get("current_commit"),
                        "report_commit": stale_info.get("report_commit"),
                    }
                )
            )
        else:
            print(f"[OK] Latest {args.type} report: {report_path}")
            print(f"  * Run ID:     {report_data.get('run_id')}")
            print(f"  * Status:     {report_data.get('status')}")
            print(f"  * Created At: {report_data.get('created_at')}")
            if is_stale:
                print(
                    f"  * Staleness:  STALE (report commit {stale_info.get('report_commit')[:8]} != HEAD {stale_info.get('current_commit')[:8]})"
                )
            else:
                print("  * Staleness:  UP TO DATE (matches repository HEAD)")
        return 0

    elif args.subcommand == "verify":
        report_path = Path(args.report)
        if not report_path.exists():
            sys.stderr.write(f"Error: File '{report_path}' not found\n")
            return 1
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            errors = validate_report(data, expected_type=args.type)
            if errors:
                if args.json:
                    print(
                        json.dumps(
                            {
                                "valid": False,
                                "report": str(report_path),
                                "errors": errors,
                            }
                        )
                    )
                else:
                    print(
                        f"[FAIL] Invalid report '{report_path}':\n"
                        + "\n".join(f"  * {e}" for e in errors)
                    )
                return 1
            if args.json:
                print(
                    json.dumps(
                        {
                            "valid": True,
                            "report": str(report_path),
                            "report_type": data.get("report_type"),
                            "run_id": data.get("run_id"),
                            "status": data.get("status"),
                        }
                    )
                )
            else:
                print(f"[OK] Report '{report_path}' is valid.")
            return 0
        except Exception as e:
            sys.stderr.write(f"Error reading report: {e}\n")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
