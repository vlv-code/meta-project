#!/usr/bin/env python3
"""
scripts/_report_models.py

Schemas, constants, fingerprinting helpers, and validation engines
for report generation and intake (ADR #22 submodule).
Pure Python 3.10+ standard library, zero external dependencies.
"""

from __future__ import annotations

import datetime
import hashlib
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# Wave F M10: the exact supported schema enumeration. The previous
# major-prefix acceptance ("1.*") let unsupported versions such as
# "1.9.9" through validation.
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1", "1.0.0", "1.1.0"}
VALID_REPORT_TYPES = {"init", "manage", "update", "tune"}
VALID_REPORT_STATUSES = {"completed", "awaiting_decision", "blocked"}
VALID_TUNE_DECISIONS = {"proposed", "accepted", "rejected"}

# Wave F M3: canonical staleness reason for an unverifiable git state.
GIT_STATE_UNAVAILABLE_REASON = "git state unavailable"

_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
# Wave F M2: a commit SHA handed to a git subprocess must be exactly a
# 40-character hex digest; anything else (notably values starting with
# "--") would be parsed as a git OPTION (argv injection).
_COMMIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")

# Essential decision inputs fingerprinted into every report (audit §5
# freshness). Reports and runtime logs are intentionally excluded.
ESSENTIAL_INPUT_PATHS = (
    ".agents/meta-project.json",
    ".agents/project_knowledge/boundaries.md",
    "AGENTS.md",
)

# The registry is the one essential input a manage operation may legitimately
# change (it deploys roles + bindings). Wave D T2.1 admits a registry delta
# ONLY when it is exactly covered by the operation's declared changes[].
REGISTRY_PATH = ".agents/meta-project.json"

# Declared-delta vocabulary (Wave D T2.1): the only registry mutations a
# manage operation may declare and have admitted at intake. Wave J adds the
# installation-level `set_orchestration` kind (an installation `orchestration`
# block change; declared as {"kind": "set_orchestration", "installation":
# <id>} with NO role_id and NO path).
VALID_MANAGE_CHANGE_KINDS = {"add_role", "disable", "archive", "set_orchestration"}
INSTALLATION_CHANGE_KINDS = {"set_orchestration"}
MANAGE_CHANGE_FIELDS = {"kind", "role_id", "installation", "path"}


def collect_input_fingerprints(repo_root: Path) -> Dict[str, Optional[str]]:
    """SHA-256 fingerprints of essential inputs; None marks a missing file."""
    fingerprints: Dict[str, Optional[str]] = {}
    for rel in ESSENTIAL_INPUT_PATHS:
        path = Path(repo_root) / rel
        if path.is_file():
            try:
                digest = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
            except OSError:
                digest = None
            fingerprints[rel] = digest
        else:
            fingerprints[rel] = None
    return fingerprints


def normalize_input_fingerprints(
    fingerprints: Any,
) -> Optional[Dict[str, Optional[str]]]:
    """
    Normalize input_fingerprints into a canonical mapping of path -> sha256_digest.

    Accepts:
      - dict[str, str | None]: returns dict after validating keys and values.
      - list[dict]: transforms [{'path': p, 'sha256': s}, ...] into {p: s}.
        If an element lacks 'path' or 'sha256' or either is not a str -> fail-closed (returns None).
    Returns None if input is invalid/malformed/unsupported.
    """
    if isinstance(fingerprints, dict):
        normalized: Dict[str, Optional[str]] = {}
        for k, v in fingerprints.items():
            if not isinstance(k, str):
                return None
            if not (v is None or isinstance(v, str)):
                return None
            normalized[k] = v
        return normalized

    if isinstance(fingerprints, list):
        normalized = {}
        for item in fingerprints:
            if not isinstance(item, dict):
                return None
            if "path" not in item or "sha256" not in item:
                return None
            p = item["path"]
            s = item["sha256"]
            if not isinstance(p, str) or not isinstance(s, str):
                return None
            normalized[p] = s
        return normalized

    return None


normalize_fingerprints = normalize_input_fingerprints

VALID_SCENARIO_PROFILES = {
    "active_development",
    "maintenance",
    "research",
    "audit",
    "documentation",
}
VALID_DEPLOYMENT_MODES = {"shared_repo", "local_overlay", "hybrid"}
VALID_COLLABORATION_MODELS = {"solo", "duo", "triad", "quad", "specialized_swarm"}
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


def _require_safe_identifier(value: str, label: str) -> str:
    """
    Path safety for identifiers that build report paths (audit §5, Wave F
    SEC-3): non-empty, a bare filename (no directory components), no '..'
    traversal, no path separators. The exact contract of the run_id check
    in save_report, applied to installation_id / init_run_id /
    report_type. Raises ValueError on refusal.
    """
    value = str(value)
    if (
        not value
        or value != Path(value).name
        or ".." in value
        or "/" in value
        or "\\" in value
    ):
        raise ValueError(f"Unsafe {label} refused: {value!r}")
    return value


def _require_commit_sha(commit_sha: str, context: str) -> Optional[str]:
    """
    Wave F M2: validate a commit SHA BEFORE it is handed to a git
    subprocess. Returns an error message on refusal, None when safe.
    Values starting with '-' would be parsed as git options (argv
    injection class).
    """
    sha = str(commit_sha or "").strip()
    if not _COMMIT_SHA_RE.fullmatch(sha):
        return (
            f"unsafe commit_sha refused in {context}: {commit_sha!r} "
            "(must be a 40-character hex SHA; values starting with '-' "
            "would be parsed as git options)"
        )
    return None


def get_git_state(repo_root: Path) -> Dict[str, Any]:
    """
    Extract current git state without external dependencies.

    Wave F M3 (fail-closed): any git subprocess failure (exception or
    nonzero exit at any of the three call sites) is recorded in
    'git_state_error' instead of being silently swallowed into a fake
    'clean / unknown-commit' state. 'is_clean' is False whenever the
    state could not be fully determined — an unqueryable repository is
    never reported as clean.
    """
    commit_sha = "unknown"
    branch = "unknown"
    is_clean = True
    modified_files: List[str] = []
    errors: List[str] = []

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
        else:
            errors.append(f"git rev-parse HEAD failed (rc={proc.returncode})")
    except Exception as exc:
        errors.append(f"git rev-parse HEAD failed: {exc}")

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
        else:
            errors.append(
                f"git rev-parse --abbrev-ref HEAD failed (rc={proc.returncode})"
            )
    except Exception as exc:
        errors.append(f"git rev-parse --abbrev-ref HEAD failed: {exc}")

    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-z"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=5,
        )
        if proc.returncode == 0:
            raw_entries = proc.stdout.split(b"\x00")
            # Wave F M9: porcelain -z rename/copy entries carry TWO path
            # fields — "XY NEW\0OLD\0" (non-z form: "R old -> new"). The
            # field following a rename/copy entry is the ORIGIN path with
            # no XY prefix; it must be consumed as the rename source and
            # never parsed as an independent entry (which previously left
            # sliced garbage in modified_files). The recorded path is the
            # NEW working-tree path so staleness sees renamed inputs.
            pending_origin = False
            for entry in raw_entries:
                if not entry:
                    continue
                if pending_origin:
                    pending_origin = False
                    continue
                status_letters = entry[:2]
                path_str = entry[3:].decode("utf-8", errors="replace")
                if path_str:
                    modified_files.append(path_str.replace("\\", "/"))
                if len(entry) >= 2 and any(
                    letter in (ord("R"), ord("C"))
                    for letter in status_letters
                ):
                    pending_origin = True
            is_clean = len(modified_files) == 0
        else:
            errors.append(
                f"git status --porcelain failed (rc={proc.returncode})"
            )
    except Exception as exc:
        errors.append(f"git status --porcelain failed: {exc}")

    if errors:
        is_clean = False

    return {
        "commit_sha": commit_sha,
        "branch": branch,
        "is_clean": is_clean,
        "modified_files": modified_files,
        "git_state_error": "; ".join(errors) if errors else None,
    }


def _validate_input_fingerprints(fingerprints: Any) -> List[str]:
    """
    Shape validation for the input_fingerprints mapping (Wave F M6): must
    be non-empty and cover every essential input; values are sha256 hex
    digests or null (null = file absent at fingerprinting time).
    """
    problems: List[str] = []
    norm = normalize_input_fingerprints(fingerprints)
    if norm is None or not norm:
        problems.append(
            "Completed init/manage report must carry a non-empty "
            "'input_fingerprints' mapping of essential decision inputs "
            "(audit §5 freshness; Wave F M6)"
        )
        return problems
    missing = [
        rel for rel in ESSENTIAL_INPUT_PATHS if rel not in norm
    ]
    if missing:
        problems.append(
            "input_fingerprints must cover the essential decision inputs; "
            "missing: " + ", ".join(missing)
        )
    malformed = [
        str(rel)
        for rel, value in norm.items()
        if not (
            value is None
            or (
                isinstance(value, str)
                and _SHA256_HEX_RE.fullmatch(value)
            )
        )
    ]
    if malformed:
        problems.append(
            "input_fingerprints values must be null or a 64-character "
            "lowercase sha256 hex digest; malformed: "
            + ", ".join(sorted(malformed))
        )
    return problems


def validate_report(
    data: Dict[str, Any],
    expected_type: Optional[str] = None,
    allow_legacy_fingerprints: bool = False,
) -> List[str]:
    """
    Validate report structure and schemas against fail-closed invariants.

    Wave F M6: completed init/manage reports must carry
    'input_fingerprints' covering the essential decision inputs. The check
    is STRICT by default (new reports: verify CLI, save_report, intake).
    Backward compatibility: callers that merely READ persisted reports
    (report directory resolution via find_latest_report) pass
    allow_legacy_fingerprints=True so legacy completed reports created
    before fingerprinting remain readable — they are surfaced with their
    recorded data and judged by the staleness legacy safeguards instead of
    being hidden as corrupt documents. update/tune reports are unaffected
    this lane.
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["Report content must be a JSON object"]

    schema_version = str(data.get("schema_version", "")).strip()
    if not schema_version:
        errors.append("Missing required field 'schema_version'")
    elif schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(
            f"Unsupported schema_version: '{schema_version}' "
            f"(allowed: {sorted(SUPPORTED_SCHEMA_VERSIONS)})"
        )

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

    # Wave F M6: freshness evidence is mandatory for completed init/manage
    # reports — without input_fingerprints the essential decision inputs
    # (registry, boundaries, passport) cannot be checked for drift.
    if (
        report_type in ("init", "manage")
        and status == "completed"
        and not allow_legacy_fingerprints
    ):
        errors.extend(_validate_input_fingerprints(data.get("input_fingerprints")))

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
            # A completed report must carry a real agreement (audit §5): no
            # empty scenarios, no unresolved mandatory questions, no failed
            # mandatory checks hidden behind status 'completed'.
            if status == "completed":
                if not profile:
                    errors.append(
                        "Completed init report must carry an agreed scenario "
                        "('scenario.profile' missing or empty)"
                    )
                unresolved = scenario.get("unresolved_questions")
                if isinstance(unresolved, list) and unresolved:
                    errors.append(
                        "Completed init report must not contain unresolved "
                        "scenario questions"
                    )

        if status == "completed" and isinstance(data.get("checks"), list):
            failed_required = [
                c.get("name", "<unnamed>")
                for c in data["checks"]
                if isinstance(c, dict)
                and c.get("status") in ("fail", "failed", "error")
            ]
            if failed_required:
                errors.append(
                    "Completed init report contains failed checks: "
                    + ", ".join(failed_required)
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

    elif report_type == "update":
        versions = data.get("versions")
        if (
            not isinstance(versions, dict)
            or not str(versions.get("before", "")).strip()
        ):
            errors.append(
                "Missing or invalid field 'versions' in update report "
                "(must be an object with non-empty 'before' and 'after')"
            )
        else:
            after = versions.get("after")
            if isinstance(after, dict):
                if (
                    not str(after.get("framework_version", "")).strip()
                    or not str(after.get("commit_sha", "")).strip()
                ):
                    errors.append(
                        "Invalid field 'versions.after' in update report "
                        "(object must carry non-empty 'framework_version' and 'commit_sha')"
                    )
            elif not str(after or "").strip():
                errors.append(
                    "Missing or invalid field 'versions' in update report "
                    "(must be an object with non-empty 'before' and 'after')"
                )

        source = data.get("source")
        if not isinstance(source, dict):
            errors.append(
                "Missing or invalid field 'source' in update report "
                "(must be an object)"
            )
        else:
            for sub_field in ("ref", "commit_sha", "origin"):
                if not str(source.get(sub_field, "")).strip():
                    errors.append(
                        f"Missing or invalid field 'source.{sub_field}' "
                        "in update report"
                    )

        affected = data.get("affected_components")
        if not isinstance(affected, list) or not affected:
            errors.append(
                "Missing or invalid field 'affected_components' in update "
                "report (must be a non-empty list)"
            )

        conflicts = data.get("conflicts")
        if status == "completed" and isinstance(conflicts, list) and conflicts:
            errors.append(
                "Completed update report must not carry unresolved conflicts: "
                "use status 'awaiting_decision' until conflicts are resolved"
            )

    elif report_type == "tune":
        proposals = data.get("proposals")
        if not isinstance(proposals, list) or not proposals:
            errors.append(
                "Missing or invalid field 'proposals' in tune report "
                "(must be a non-empty list)"
            )
        else:
            for idx, proposal in enumerate(proposals):
                if not isinstance(proposal, dict):
                    errors.append(
                        f"Invalid proposal at index {idx} in tune report "
                        "(must be an object)"
                    )
                    continue
                decision = str(proposal.get("decision", "")).strip()
                if not decision:
                    errors.append(
                        f"Proposal {idx} in tune report is missing required "
                        "field 'decision'"
                    )
                elif decision not in VALID_TUNE_DECISIONS:
                    errors.append(
                        f"Invalid decision '{decision}' for proposal {idx} in "
                        f"tune report. Allowed: {sorted(list(VALID_TUNE_DECISIONS))}"
                    )
                if (
                    decision == "rejected"
                    and not str(proposal.get("rationale", "")).strip()
                ):
                    errors.append(
                        f"Rejected proposal {idx} in tune report must carry "
                        "a non-empty 'rationale'"
                    )
                if status == "completed" and decision in ("", "proposed"):
                    errors.append(
                        f"Completed tune report requires a recorded decision "
                        f"for every proposal; proposal {idx} is undecided"
                    )

    return errors


def verify_update_report(data: Dict[str, Any]) -> List[str]:
    """Validate an update report document against schema and semantic invariants."""
    return validate_report(data, expected_type="update")
