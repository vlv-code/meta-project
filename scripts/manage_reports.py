__all__ = [
    'ESSENTIAL_INPUT_PATHS',
    'GIT_STATE_UNAVAILABLE_REASON',
    'INSTALLATION_CHANGE_KINDS',
    'MANAGE_CHANGE_FIELDS',
    'REGISTRY_PATH',
    'SUPPORTED_SCHEMA_VERSIONS',
    'VALID_COLLABORATION_MODELS',
    'VALID_DELEGATION_LEVELS',
    'VALID_DEPLOYMENT_MODES',
    'VALID_MANAGE_CHANGE_KINDS',
    'VALID_REPORT_STATUSES',
    'VALID_REPORT_TYPES',
    'VALID_SCENARIO_PROFILES',
    'VALID_TUNE_DECISIONS',
    'VALID_VERIFICATION_POLICIES',
    '_COMMIT_SHA_RE',
    '_SHA256_HEX_RE',
    '_require_commit_sha',
    '_require_safe_identifier',
    '_validate_input_fingerprints',
    'collect_input_fingerprints',
    'generate_run_id',
    'get_git_state',
    'normalize_fingerprints',
    'normalize_input_fingerprints',
    'validate_report',
    'verify_update_report',
    '_extract_triggers_from_profile',
    '_load_valid_report',
    '_normalize_declared_changes',
    '_recover_registry_baseline',
    '_registry_identity_delta',
    '_resolve_project_id',
    'apply_duty_reconciliation',
    'check_report_staleness',
    'create_init_report',
    'create_manage_report',
    'create_tune_report',
    'detect_role_duty_conflicts',
    'evaluate_manage_intake',
    'find_latest_report',
    'get_report_dir',
    'resolve_team_topology',
    'save_report',
    'verify_declared_registry_delta',
    'build_cli_parser',
    'main',
    'subprocess',
]

#!/usr/bin/env python3
"""
Meta-Project Report Management Engine (scripts/manage_reports.py)

Deterministic, zero-dependency Python 3.10+ stdlib CLI and library for creating,
validating, locating, and inspecting initialization ('init') and management ('manage')
JSON reports in .agents/reports/<installation_id>/{init,manage}/.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

try:
    from scripts.verify_identity import (
        evaluate_actor_admission,
        load_registry,
        resolve_actor_binding,
    )
except ImportError:  # direct script execution: python scripts/manage_reports.py
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

try:  # shared helpers (ADR #22): package-style import (tests: from
    # scripts.manage_reports import ...)
    from scripts._common import _error_envelope
except ImportError:  # direct script execution: python scripts/manage_reports.py
    from _common import _error_envelope


try:
    from scripts._report_models import (
        ESSENTIAL_INPUT_PATHS,
        GIT_STATE_UNAVAILABLE_REASON,
        INSTALLATION_CHANGE_KINDS,
        MANAGE_CHANGE_FIELDS,
        REGISTRY_PATH,
        SUPPORTED_SCHEMA_VERSIONS,
        VALID_COLLABORATION_MODELS,
        VALID_DELEGATION_LEVELS,
        VALID_DEPLOYMENT_MODES,
        VALID_MANAGE_CHANGE_KINDS,
        VALID_REPORT_STATUSES,
        VALID_REPORT_TYPES,
        VALID_SCENARIO_PROFILES,
        VALID_TUNE_DECISIONS,
        VALID_VERIFICATION_POLICIES,
        _COMMIT_SHA_RE,
        _SHA256_HEX_RE,
        _require_commit_sha,
        _require_safe_identifier,
        _validate_input_fingerprints,
        collect_input_fingerprints,
        generate_run_id,
        get_git_state,
        normalize_fingerprints,
        normalize_input_fingerprints,
        validate_report,
        verify_update_report,
    )
except ImportError:
    from _report_models import (
        ESSENTIAL_INPUT_PATHS,
        GIT_STATE_UNAVAILABLE_REASON,
        INSTALLATION_CHANGE_KINDS,
        MANAGE_CHANGE_FIELDS,
        REGISTRY_PATH,
        SUPPORTED_SCHEMA_VERSIONS,
        VALID_COLLABORATION_MODELS,
        VALID_DELEGATION_LEVELS,
        VALID_DEPLOYMENT_MODES,
        VALID_MANAGE_CHANGE_KINDS,
        VALID_REPORT_STATUSES,
        VALID_REPORT_TYPES,
        VALID_SCENARIO_PROFILES,
        VALID_TUNE_DECISIONS,
        VALID_VERIFICATION_POLICIES,
        _COMMIT_SHA_RE,
        _SHA256_HEX_RE,
        _require_commit_sha,
        _require_safe_identifier,
        _validate_input_fingerprints,
        collect_input_fingerprints,
        generate_run_id,
        get_git_state,
        normalize_fingerprints,
        normalize_input_fingerprints,
        validate_report,
        verify_update_report,
    )

try:
    from scripts._report_intake import (
        _extract_triggers_from_profile,
        _load_valid_report,
        _normalize_declared_changes,
        _recover_registry_baseline,
        _registry_identity_delta,
        _resolve_project_id,
        apply_duty_reconciliation,
        check_report_staleness,
        create_init_report,
        create_manage_report,
        create_tune_report,
        detect_role_duty_conflicts,
        evaluate_manage_intake,
        find_latest_report,
        get_report_dir,
        resolve_team_topology,
        save_report,
        verify_declared_registry_delta,
    )
except ImportError:
    from _report_intake import (
        _extract_triggers_from_profile,
        _load_valid_report,
        _normalize_declared_changes,
        _recover_registry_baseline,
        _registry_identity_delta,
        _resolve_project_id,
        apply_duty_reconciliation,
        check_report_staleness,
        create_init_report,
        create_manage_report,
        create_tune_report,
        detect_role_duty_conflicts,
        evaluate_manage_intake,
        find_latest_report,
        get_report_dir,
        resolve_team_topology,
        save_report,
        verify_declared_registry_delta,
    )


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
        "--project-id",
        default=None,
        help="Project ID (default: resolved from the local registry, never hardcoded)",
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
        "--project-id",
        default=None,
        help="Project ID (default: resolved from the local registry, never hardcoded)",
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
        "--type",
        choices=["init", "manage", "update", "tune"],
        required=True,
        help="Report type",
    )
    p_latest.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    # 5. tune subcommand (Wave D T2.2: friction 1 — tune reports were
    # validatable but had no CLI to create them)
    p_tune = subparsers.add_parser(
        "tune", help="Manage tuning (tune) reports"
    )
    p_tune.add_argument(
        "--action", choices=["create", "verify"], required=True
    )
    p_tune.add_argument(
        "--repo-root", default=".", help="Target repository root path"
    )
    p_tune.add_argument(
        "--installation", help="Target installation ID (e.g. ag-main)"
    )
    p_tune.add_argument("--harness", help="Harness ID (e.g. antigravity)")
    p_tune.add_argument("--actor", help="Qualified actor_id")
    p_tune.add_argument(
        "--project-id",
        default=None,
        help="Project ID (default: resolved from the local registry, never hardcoded)",
    )
    p_tune.add_argument(
        "--status",
        choices=["completed", "awaiting_decision", "blocked"],
        default="completed",
    )
    p_tune.add_argument(
        "--data-file",
        help="Path to JSON file containing proposals[] and checks",
    )
    p_tune.add_argument(
        "--report", help="Path to report file for verification"
    )
    p_tune.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    # 4. verify subcommand
    p_verify = subparsers.add_parser(
        "verify", help="Validate an existing report file"
    )
    p_verify.add_argument("--report", required=True, help="Path to report file")
    p_verify.add_argument(
        "--type",
        choices=["init", "manage", "update", "tune"],
        help="Expected report type (optional)",
    )
    p_verify.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    # 5. deconflict subcommand
    p_deconflict = subparsers.add_parser(
        "deconflict",
        help="Scan and deconflict role duties and invocation triggers across roles on an installation",
    )
    p_deconflict.add_argument(
        "--repo-root", default=".", help="Target repository root path"
    )
    p_deconflict.add_argument(
        "--installation", required=True, help="Target installation identifier"
    )
    p_deconflict.add_argument(
        "--new-role", required=True, help="New or target role identifier"
    )
    p_deconflict.add_argument(
        "--new-triggers",
        nargs="*",
        default=None,
        help="Invocation triggers for the new/target role",
    )
    p_deconflict.add_argument(
        "--apply",
        action="store_true",
        help="Apply duty reconciliation delta to conflicting role profiles",
    )
    p_deconflict.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    return parser


def _emit_invalid_report_envelope(report_path: Path, errors: List[str]) -> None:
    """Writes the INVALID_REPORT envelope (Wave E) for a failed report
    verification. Presentation only: verdicts and rc are unchanged."""
    first = errors[0] if errors else "unknown validation error"
    sys.stderr.write(_error_envelope(
        "INVALID_REPORT",
        str(report_path),
        "report file failed schema validation",
        "a JSON report matching the canonical report schema",
        f"{len(errors)} validation error(s), first: {first}",
        "regenerate the report via the matching '<type> create' action, or "
        "repair the file to satisfy the errors listed in the verdict",
    ) + "\n")


def _emit_stale_input_envelope(report_path: Path, reason: str) -> None:
    """Writes the STALE_INPUT envelope (Wave E format) when a report's
    freshness cannot be certified because git state is unavailable
    (Wave F M3). Presentation only: verdicts and rc are unchanged."""
    sys.stderr.write(_error_envelope(
        "STALE_INPUT",
        str(report_path),
        f"report freshness cannot be certified: {reason}",
        "a report whose recorded git state can be verified against the "
        "current repository git state",
        "git state unavailable: freshness is suspect, not certified",
        "restore git operation (or resolve the recorded git failure), then "
        "re-run 'latest' to re-certify freshness",
    ) + "\n")


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
                    _emit_invalid_report_envelope(report_path, errors)
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
                sys.stderr.write(_error_envelope(
                    "INVALID_REPORT",
                    str(report_path),
                    "report file is not readable/parsable JSON",
                    "a JSON report file loadable as UTF-8 JSON",
                    f"read/parse error: {e}",
                    "regenerate the report via the matching '<type> create' "
                    "action, or repair the file encoding/JSON syntax",
                ) + "\n")
                sys.stderr.write(f"Error reading report: {e}\n")
                return 1

        elif args.action == "create":
            if not args.installation or not args.harness or not args.actor:
                sys.stderr.write(
                    "Error: --installation, --harness, and --actor are required for create action\n"
                )
                return 2
            project_id, pid_err = _resolve_project_id(repo_root, args.project_id)
            if pid_err:
                sys.stderr.write(f"Error: {pid_err}\n")
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
                project_id=project_id,
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
                    _emit_invalid_report_envelope(report_path, errors)
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
                sys.stderr.write(_error_envelope(
                    "INVALID_REPORT",
                    str(report_path),
                    "report file is not readable/parsable JSON",
                    "a JSON report file loadable as UTF-8 JSON",
                    f"read/parse error: {e}",
                    "regenerate the report via the matching '<type> create' "
                    "action, or repair the file encoding/JSON syntax",
                ) + "\n")
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
            project_id, pid_err = _resolve_project_id(repo_root, args.project_id)
            if pid_err:
                sys.stderr.write(f"Error: {pid_err}\n")
                return 2

            # Load the operation payload BEFORE intake: its declared
            # changes[] participate in the admission decision (Wave D T2.1).
            extra_data: Dict[str, Any] = {}
            if args.data_file:
                try:
                    with open(args.data_file, "r", encoding="utf-8") as f:
                        extra_data = json.load(f)
                except Exception as e:
                    sys.stderr.write(
                        f"Error: cannot read --data-file "
                        f"'{args.data_file}': {e}\n"
                    )
                    return 1
            if not isinstance(extra_data, dict):
                sys.stderr.write(
                    "Error: --data-file content must be a JSON object\n"
                )
                return 1

            # Intake admission (audit §5 + Guardian Step 64 finding): a
            # manage operation is authorized ONLY by an admitted init report
            # for this installation. The referenced init run must exist and
            # pass evaluate_manage_intake; hand-built or foreign init
            # references fail closed. A registry delta since the init report
            # is admitted only when exactly covered by the declared
            # changes[] below (Wave D T2.1).
            # Wave F SEC-3: identifiers that build report paths are
            # validated BEFORE any path is constructed or read, so a
            # hostile --installation/--init-run-id cannot probe or read
            # outside the reports directory.
            try:
                _require_safe_identifier(args.installation, "installation_id")
                _require_safe_identifier(args.init_run_id, "init_run_id")
            except ValueError as exc:
                sys.stderr.write(f"Error: {exc}\n")
                return 2
            init_file = (
                get_report_dir(repo_root, args.installation, "init")
                / f"{args.init_run_id}.json"
            )
            if not init_file.is_file():
                sys.stderr.write(
                    f"Error: referenced init run '{args.init_run_id}' not found "
                    f"at {init_file}\n"
                )
                return 1
            intake_errors = evaluate_manage_intake(
                repo_root=repo_root,
                installation_id=args.installation,
                harness_id=args.harness,
                actor_id=args.actor,
                report_path=init_file,
                declared_changes=extra_data.get("changes"),
            )
            if intake_errors:
                sys.stderr.write(
                    "Error: manage intake rejected "
                    f"({len(intake_errors)} issue(s)):\n"
                )
                for e in intake_errors:
                    sys.stderr.write(f"  * {e}\n")
                return 1

            report = create_manage_report(
                repo_root=repo_root,
                installation_id=args.installation,
                harness_id=args.harness,
                actor_id=args.actor,
                project_id=project_id,
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
                changes=extra_data.get("changes") or [],
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

    elif args.subcommand == "tune":
        # Wave D T2.2: tune report CLI (friction 1). Tune output is
        # read-only analysis evidence; creation mirrors init/manage flags
        # and requires a non-empty proposals[] payload.
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
                errors = validate_report(data, expected_type="tune")
                if errors:
                    _emit_invalid_report_envelope(report_path, errors)
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
                            f"[FAIL] Invalid tune report '{report_path}':\n"
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
                    print(f"[OK] Tune report '{report_path}' is valid.")
                return 0
            except Exception as e:
                sys.stderr.write(_error_envelope(
                    "INVALID_REPORT",
                    str(report_path),
                    "report file is not readable/parsable JSON",
                    "a JSON report file loadable as UTF-8 JSON",
                    f"read/parse error: {e}",
                    "regenerate the report via the matching '<type> create' "
                    "action, or repair the file encoding/JSON syntax",
                ) + "\n")
                sys.stderr.write(f"Error reading report: {e}\n")
                return 1

        elif args.action == "create":
            if not args.installation or not args.harness or not args.actor:
                sys.stderr.write(
                    "Error: --installation, --harness, and --actor are required for tune create\n"
                )
                return 2
            project_id, pid_err = _resolve_project_id(repo_root, args.project_id)
            if pid_err:
                sys.stderr.write(f"Error: {pid_err}\n")
                return 2

            extra_data: Dict[str, Any] = {}
            if args.data_file:
                try:
                    with open(args.data_file, "r", encoding="utf-8") as f:
                        extra_data = json.load(f)
                except Exception as e:
                    sys.stderr.write(
                        f"Error: cannot read --data-file '{args.data_file}': {e}\n"
                    )
                    return 1
            if not isinstance(extra_data, dict):
                sys.stderr.write(
                    "Error: --data-file content must be a JSON object\n"
                )
                return 1

            proposals = extra_data.get("proposals")
            if not isinstance(proposals, list) or not proposals:
                sys.stderr.write(
                    "Error: --data-file must contain a non-empty "
                    "'proposals' list for tune create\n"
                )
                return 2

            report = create_tune_report(
                repo_root=repo_root,
                installation_id=args.installation,
                harness_id=args.harness,
                actor_id=args.actor,
                project_id=project_id,
                status=args.status,
                proposals=proposals,
                checks=extra_data.get("checks"),
                remaining_manual_actions=extra_data.get(
                    "remaining_manual_actions"
                ),
            )

            try:
                saved_path = save_report(
                    repo_root, args.installation, "tune", report
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
                        f"[OK] Tune report created: {saved_path} (run_id={report['run_id']})"
                    )
                return 0
            except Exception as e:
                sys.stderr.write(f"Error saving report: {e}\n")
                return 1

    elif args.subcommand == "latest":
        # Wave F SEC-3: an unsafe installation identifier refuses cleanly
        # (no traceback) before any report directory is resolved.
        try:
            report_path, report_data = find_latest_report(
                repo_root, args.installation, args.type
            )
        except ValueError as exc:
            sys.stderr.write(f"Error: {exc}\n")
            return 2
        if report_path is not None and report_data is None:
            # Latest attempt exists but is corrupted/foreign: surface it
            # instead of silently hiding it behind an older valid report.
            if args.json:
                print(
                    json.dumps(
                        {
                            "found": False,
                            "corrupted_latest_attempt": str(report_path),
                            "installation": args.installation,
                            "type": args.type,
                        }
                    )
                )
            else:
                print(
                    f"[FAIL] Latest {args.type} attempt for installation "
                    f"'{args.installation}' is corrupted or foreign: {report_path}"
                )
            return 1
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
        # Wave F M3: git-state unavailability is surfaced with the
        # STALE_INPUT envelope (presentation only; rc unchanged).
        if is_stale and any(
            str(r).startswith(GIT_STATE_UNAVAILABLE_REASON)
            for r in stale_info.get("reasons", [])
        ):
            _emit_stale_input_envelope(report_path, GIT_STATE_UNAVAILABLE_REASON)
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
                        "staleness_reasons": stale_info.get("reasons", []),
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
                reasons = "; ".join(
                    stale_info.get("reasons")
                    or [f"commit {stale_info.get('report_commit')} != HEAD {stale_info.get('current_commit')}"]
                )
                print(f"  * Staleness:  STALE ({reasons})")
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
                _emit_invalid_report_envelope(report_path, errors)
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
            sys.stderr.write(_error_envelope(
                "INVALID_REPORT",
                str(report_path),
                "report file is not readable/parsable JSON",
                "a JSON report file loadable as UTF-8 JSON",
                f"read/parse error: {e}",
                "regenerate the report via the matching '<type> create' "
                "action, or repair the file encoding/JSON syntax",
            ) + "\n")
            sys.stderr.write(f"Error reading report: {e}\n")
            return 1

    elif args.subcommand == "deconflict":
        repo_root = Path(args.repo_root)
        new_triggers = args.new_triggers
        result = detect_role_duty_conflicts(
            repo_root=repo_root,
            target_installation=args.installation,
            new_role_id=args.new_role,
            new_triggers=new_triggers,
        )
        if args.apply and result.get("conflicts_detected"):
            applied = apply_duty_reconciliation(
                repo_root=repo_root,
                duty_reconciliation=result.get("duty_reconciliation", {}),
            )
            result["applied_updates"] = applied

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("conflicts_detected"):
                print(f"[CONFLICT] Duty/trigger conflicts detected for '{args.new_role}':")
                for c in result.get("conflicts", []):
                    print(f"  * Role '{c['role_id']}': overlapping triggers {c['overlapping_triggers']}")
                if args.apply:
                    print(f"[APPLIED] Pruned overlapping triggers from {len(result.get('applied_updates', []))} profiles.")
            else:
                print(f"[OK] No duty/trigger conflicts detected for '{args.new_role}' on installation '{args.installation}'.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
