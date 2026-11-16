#!/usr/bin/env python3
"""
Audit Remediation Regression Suite — Stage 1: Reproduction Fixation.

Reproduces the defects confirmed by the external audit of base 38deed9
(+ uncommitted Step 61 working tree; 118 committed / 119 worktree tests).

Contract of this suite:
- Every test invokes the real working function or CLI responsible for the
  verified behavior (no self-implemented expected checks inside tests).
- Every test asserts the REQUIRED (post-fix) behavior, therefore on the
  pre-fix codebase the defect-reproducing tests fail (RED baseline).
- Remediation stages must turn them GREEN without weakening assertions.
- Tests marked "lock-in" target behavior that is already correct today and
  protect it from regressions during remediation.

RED baseline results are preserved in docs/audit_38deed9_regressions_baseline.md.

Stage 5 intake API contract expected by section D tests:

    evaluate_manage_intake(
        repo_root: Path,
        installation_id: str,
        harness_id: str,
        actor_id: str,
        report_path: Path,
    ) -> List[str]

    Returns a list of intake errors; an empty list means the init report
    authorizes a manage operation for this installation in this project.
    Format validation (validate_report) and intake admission are separate
    concerns: a valid-but-blocked report must produce intake errors.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_boundaries import (
    BoundaryGateError,
    get_git_modified_files,
    install_git_hook,
)
from scripts.compact_memory import compact_observations, main as compact_main
from scripts.inspect_meta_project import inspect_repository
from scripts.manage_reports import (
    check_report_staleness,
    create_init_report,
    find_latest_report,
    resolve_team_topology,
    save_report,
    validate_report,
)
from scripts.record_obs import record_observation
from scripts.sync_templates import main as sync_main
from scripts.verify_identity import (
    resolve_actor_binding,
    validate_identity_registry,
)

try:
    # Stage 5 intake engine: absent until the init -> manage contract is
    # implemented. Tests below must FAIL (not skip) while it is missing.
    from scripts.manage_reports import evaluate_manage_intake
except ImportError:
    evaluate_manage_intake = None

CHECK_BOUNDARIES_SCRIPT = REPO_ROOT / "scripts" / "check_boundaries.py"
VERIFY_IDENTITY_SCRIPT = REPO_ROOT / "scripts" / "verify_identity.py"
MANAGE_REPORTS_SCRIPT = REPO_ROOT / "scripts" / "manage_reports.py"
RECORD_OBS_SCRIPT = REPO_ROOT / "scripts" / "record_obs.py"

POSIX_SHELL = shutil.which("bash") or shutil.which("sh")

MINIMAL_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- `docs/**` and `*.md` documentation.

## Yellow Zone (Modification with Mandatory Verification)
- `AGENTS.md` root passport.

## Red Zone (Prohibited Without Direct User Confirmation)
- `LICENSE`
- `*boundaries.md`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def _init_repo(path: Path) -> Path:
    """Create a tiny committed git repository for gate/inspector fixtures."""
    path.mkdir(parents=True, exist_ok=True)
    res = _git(path, "init", "-q")
    assert res.returncode == 0, res.stderr
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    (path / ".agents" / "project_knowledge").mkdir(parents=True, exist_ok=True)
    (path / ".agents" / "project_knowledge" / "boundaries.md").write_text(
        MINIMAL_BOUNDARIES, encoding="utf-8"
    )
    (path / "README.md").write_text("# fixture\n", encoding="utf-8")
    _git(path, "add", "-A")
    res = _git(path, "commit", "-qm", "init")
    assert res.returncode == 0, res.stderr
    return path


def _run_gate(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_BOUNDARIES_SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


class TempRootTestCase(unittest.TestCase):
    """Base fixture with automatic temp directory cleanup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audit_reg_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def sub(self, name: str) -> Path:
        p = self.root / name
        p.mkdir(parents=True, exist_ok=True)
        return p


# ---------------------------------------------------------------------------
# Section A - Boundary Gate CLI (audit §2)
# ---------------------------------------------------------------------------


class TestBoundaryGateRegressions(TempRootTestCase):
    """Audit §2: diff base handling, rename coverage, --repo-root scope."""

    def test_invalid_diff_revision_fails_closed(self):
        """A missing/unresolvable diff revision must fail the check with an
        error. Forbidden: successful fallback to an empty git status."""
        repo = _init_repo(self.sub("repo"))
        res = _run_gate(
            repo,
            "--boundaries",
            str(repo / ".agents" / "project_knowledge" / "boundaries.md"),
            "--diff",
            "DEADBEEF123",
        )
        self.assertNotEqual(
            res.returncode,
            0,
            f"gate must fail on unresolvable revision, got rc=0 "
            f"(stdout={res.stdout!r})",
        )

    def test_rename_red_to_green_checks_old_path(self):
        """Renaming LICENSE -> docs/license.md must be blocked: the old (Red
        Zone) path must be evaluated, not only the new (Green Zone) one."""
        repo = _init_repo(self.sub("repo"))
        (repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(repo, "add", "LICENSE")
        assert _git(repo, "commit", "-qm", "add license").returncode == 0
        (repo / "docs").mkdir()
        res = _git(repo, "mv", "LICENSE", "docs/license.md")
        assert res.returncode == 0, res.stderr
        assert _git(repo, "commit", "-qm", "rename license").returncode == 0

        res = _run_gate(
            repo,
            "--boundaries",
            str(repo / ".agents" / "project_knowledge" / "boundaries.md"),
            "--diff",
            "HEAD~1",
        )
        self.assertEqual(
            res.returncode,
            1,
            f"rename of a Red Zone file must be blocked; stdout={res.stdout!r}",
        )
        self.assertIn(
            "LICENSE",
            res.stderr,
            "violation report must name the old Red Zone path LICENSE",
        )

    def test_repo_root_governs_git_operations(self):
        """--repo-root must define the repository for all git operations.
        Running the gate from an unrelated cwd with a violating target repo
        must detect the violation, not report an empty 'Clean' result."""
        target = _init_repo(self.sub("target"))
        (target / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(target, "add", "LICENSE")  # staged Red Zone change

        elsewhere = self.sub("elsewhere")  # not a git repository
        res = _run_gate(
            elsewhere,
            "--boundaries",
            str(target / ".agents" / "project_knowledge" / "boundaries.md"),
            "--repo-root",
            str(target),
            "--staged",
        )
        self.assertNotEqual(
            res.returncode,
            0,
            f"gate must audit the --repo-root repository, got 'Clean' "
            f"(stdout={res.stdout!r})",
        )

    def test_status_fallback_parsing_keeps_rename_old_path(self):
        """Default (status) mode must preserve the NUL-separated old-path
        record of a rename, and an explicit failing diff target must raise
        instead of silently degrading into a status fallback."""
        repo = _init_repo(self.sub("repo"))
        (repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(repo, "add", "LICENSE")
        assert _git(repo, "commit", "-qm", "add license").returncode == 0
        (repo / "docs").mkdir()
        assert _git(repo, "mv", "LICENSE", "docs/license.md").returncode == 0

        # Explicit failing diff target: hard error, no silent fallback.
        with self.assertRaises(BoundaryGateError):
            get_git_modified_files(diff_target="DEADBEEF123", repo_root=repo)

        # Default mode: status parsing keeps the rename old path intact.
        files = get_git_modified_files(repo_root=repo)
        self.assertIn(
            "LICENSE",
            files,
            f"rename old path must be present in status results: {files!r}",
        )
        self.assertFalse(
            any(f not in ("LICENSE", "docs/license.md") for f in files),
            f"status parsing produced mangled entries: {files!r}",
        )


# ---------------------------------------------------------------------------
# Section B - Identity registry (audit §3)
# ---------------------------------------------------------------------------


def _write_profile(root: Path, rel: str, *, harness: str = "antigravity") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        'name: "Dev Lead"\n'
        'role_id: "agent-dev-lead"\n'
        f'harness_id: "{harness}"\n'
        'installation_id: "ag-main"\n'
        'actor_id: "acme/app::antigravity::ag-main::agent-dev-lead"\n'
        'description: "fixture role"\n'
        "---\n"
        "# Agent Role Passport: Dev Lead\n",
        encoding="utf-8",
    )


def _write_registry(
    root: Path,
    *,
    schema_version: str = "1.1.0",
    actor_harness: str = "antigravity",
    installation_status: str = "active",
    binding_status: str = "active",
    roles: dict | None = None,
) -> None:
    if roles is None:
        roles = {
            "agent-dev-lead": {
                "description": "fixture role",
                "bindings": {
                    "ag-main": {
                        "actor_id": f"acme/app::{actor_harness}::ag-main::agent-dev-lead",
                        "status": binding_status,
                        "profile_path": ".agents/team/agent-dev-lead/profile.md",
                    }
                },
            }
        }
    registry = {
        "schema_version": schema_version,
        "project_id": "acme/app",
        "installations": {
            "ag-main": {
                "harness_id": "antigravity",
                "status": installation_status,
                "description": "fixture",
            }
        },
        "roles": roles,
    }
    path = root / ".agents" / "meta-project.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2), encoding="utf-8")


class TestIdentityRegistryRegressions(TempRootTestCase):
    """Audit §3: registry correctness, lookup vs admission, structured
    diagnostics."""

    def setUp(self):
        super().setUp()
        self.repo = self.sub("repo")
        _write_registry(self.repo)
        _write_profile(self.repo, ".agents/team/agent-dev-lead/profile.md")

    def test_harness_substitution_in_actor_id_rejected(self):
        """An actor_id whose harness component does not match the
        installation's harness_id must be reported as an error."""
        _write_registry(self.repo, actor_harness="zcode")
        _write_profile(self.repo, ".agents/team/agent-dev-lead/profile.md")
        is_valid, errors = validate_identity_registry(self.repo)
        self.assertFalse(is_valid, f"harness substitution accepted: {errors!r}")
        self.assertTrue(
            any("harness" in e.lower() for e in errors),
            f"no harness mismatch diagnostic: {errors!r}",
        )

    def test_schema_version_value_validated(self):
        """schema_version must be checked against supported versions, not
        merely for presence."""
        _write_registry(self.repo, schema_version="99.0.0")
        is_valid, errors = validate_identity_registry(self.repo)
        self.assertFalse(is_valid, f"unsupported schema accepted: {errors!r}")

    def test_installation_status_enum_validated(self):
        """Installation status must be a supported lifecycle value."""
        _write_registry(self.repo, installation_status="hibernating")
        is_valid, errors = validate_identity_registry(self.repo)
        self.assertFalse(is_valid, f"unknown installation status accepted: {errors!r}")

    def test_binding_status_enum_validated(self):
        """Binding status must be a supported lifecycle value."""
        _write_registry(self.repo, binding_status="maybe")
        is_valid, errors = validate_identity_registry(self.repo)
        self.assertFalse(is_valid, f"unknown binding status accepted: {errors!r}")

    def test_malformed_root_json_yields_structured_errors(self):
        """A registry whose root JSON is not an object must produce a
        structured error list, never a traceback."""
        path = self.repo / ".agents" / "meta-project.json"
        path.write_text("[1, 2, 3]\n", encoding="utf-8")
        try:
            is_valid, errors = validate_identity_registry(self.repo)
        except Exception as exc:  # noqa: BLE001 - the defect IS the traceback
            self.fail(
                f"registry validation raised {type(exc).__name__} instead of "
                f"structured diagnostics: {exc}"
            )
        self.assertFalse(is_valid)
        self.assertTrue(errors, "expected at least one structured error")

    def test_registry_without_roles_is_valid_base_installation(self):
        """A correct initial registry without a deployed team must be valid;
        validators must not force the creation of a fictitious role."""
        _write_registry(self.repo, roles={})
        is_valid, errors = validate_identity_registry(self.repo)
        self.assertTrue(
            is_valid,
            f"team-less base installation rejected: {errors!r}",
        )

    def test_planned_binding_is_not_admitted_as_active_identity(self):
        """Looking up a planned binding is legitimate inspection, but
        admission (verify_identity --actor) must deny runtime authorization."""
        registry = {
            "schema_version": "1.1.0",
            "project_id": "acme/app",
            "installations": {
                "zc-main": {
                    "harness_id": "zcode",
                    "status": "planned",
                    "description": "planned installation",
                }
            },
            "roles": {
                "agent-dev-lead": {
                    "description": "fixture role",
                    "bindings": {
                        "zc-main": {
                            "actor_id": "acme/app::zcode::zc-main::agent-dev-lead",
                            "status": "planned",
                            "profile_path": None,
                        }
                    },
                }
            },
        }
        path = self.repo / ".agents" / "meta-project.json"
        path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

        planned_actor = "acme/app::zcode::zc-main::agent-dev-lead"
        found, binding = resolve_actor_binding(self.repo, planned_actor)
        self.assertTrue(found, "lookup of a planned binding must remain possible")

        res = subprocess.run(
            [
                sys.executable,
                str(VERIFY_IDENTITY_SCRIPT),
                "--repo-root",
                str(self.repo),
                "--actor",
                planned_actor,
            ],
            capture_output=True,
            text=True,
        )
        combined = res.stdout + res.stderr
        self.assertNotEqual(
            res.returncode,
            0,
            f"planned binding admitted as active identity: {combined!r}",
        )
        self.assertTrue(
            "planned" in combined.lower() or "authoriz" in combined.lower(),
            f"denial must explain the planned/not-authorized reason: {combined!r}",
        )

    def test_profile_harness_mismatch_with_binding_detected(self):
        """Profile frontmatter harness must agree with the registry binding."""
        _write_profile(
            self.repo,
            ".agents/team/agent-dev-lead/profile.md",
            harness="zcode",
        )
        is_valid, errors = validate_identity_registry(self.repo)
        self.assertFalse(is_valid, f"profile/registry harness mismatch accepted: {errors!r}")


# ---------------------------------------------------------------------------
# Section C - State inspector (audit §4)
# ---------------------------------------------------------------------------


def _write_healthy_metaproject(
    root: Path,
    *,
    second_active_installation: bool = False,
    include_zc_binding: bool = False,
) -> None:
    (root / "AGENTS.md").write_text(
        "# Project Passport: Fixture\n\n"
        "## 1. Concept, Principles, and North Stars\n"
        "- Meta-Project fixture passport.\n",
        encoding="utf-8",
    )
    pk = root / ".agents" / "project_knowledge"
    pk.mkdir(parents=True, exist_ok=True)
    (pk / "boundaries.md").write_text(MINIMAL_BOUNDARIES, encoding="utf-8")
    (pk / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (pk / "observations.md").write_text("# Observations\n", encoding="utf-8")

    installations = {
        "ag-main": {
            "harness_id": "antigravity",
            "status": "active",
            "description": "primary",
        }
    }
    if second_active_installation:
        installations["zc-main"] = {
            "harness_id": "zcode",
            "status": "active",
            "description": "second",
        }

    dev_bindings = {
        "ag-main": {
            "actor_id": "acme/app::antigravity::ag-main::agent-dev-lead",
            "status": "active",
            "profile_path": ".agents/team/agent-dev-lead/profile.md",
        }
    }
    if include_zc_binding:
        dev_bindings["zc-main"] = {
            "actor_id": "acme/app::zcode::zc-main::agent-dev-lead",
            "status": "active",
            "profile_path": None,
        }

    registry = {
        "schema_version": "1.1.0",
        "project_id": "acme/app",
        "installations": installations,
        "roles": {
            "agent-dev-lead": {
                "description": "fixture role",
                "bindings": dev_bindings,
            }
        },
    }
    (root / ".agents" / "meta-project.json").write_text(
        json.dumps(registry, indent=2), encoding="utf-8"
    )
    _write_profile(root, ".agents/team/agent-dev-lead/profile.md")


class TestInspectorRegressions(TempRootTestCase):
    """Audit §4: mandatory components, runtime context, capability scoping,
    worktree directories."""

    def setUp(self):
        super().setUp()
        self.repo = self.sub("repo")

    def test_missing_passport_is_not_healthy_registered(self):
        """A healthy state requires the mandatory passport; its absence must
        yield PARTIAL_CORRUPTED with the precise missing component list."""
        _write_healthy_metaproject(self.repo)
        (self.repo / "AGENTS.md").unlink()

        report = inspect_repository(self.repo)
        self.assertEqual(
            report["state"],
            "PARTIAL_CORRUPTED",
            f"missing passport reported as {report['state']}",
        )
        self.assertTrue(
            any("AGENTS.md" in m for m in report["missing_components"]),
            f"missing passport not listed: {report['missing_components']!r}",
        )

    def test_unknown_runtime_context_reports_indeterminacy(self):
        """Without --harness/--installation the inspector must not silently
        resolve to any active installation."""
        _write_healthy_metaproject(self.repo, second_active_installation=True)

        report = inspect_repository(self.repo)  # no runtime context
        self.assertNotEqual(
            report["state"],
            "HEALTHY_REGISTERED",
            "unknown runtime context silently resolved to an active installation",
        )

    def test_roles_capability_scoped_to_target_installation(self):
        """Availability of Antigravity role profiles must not be reported as
        availability of roles for a ZCode installation."""
        _write_healthy_metaproject(
            self.repo,
            second_active_installation=True,
            include_zc_binding=True,
        )

        report = inspect_repository(
            self.repo,
            target_harness="zcode",
            target_installation="zc-main",
        )
        self.assertEqual(
            report["capabilities"]["roles"]["status"],
            "unavailable",
            "foreign-harness role profiles leaked into zc-main capability matrix",
        )

    def test_worktree_git_toplevel_reports_main_working_tree(self):
        """For a linked worktree, git_toplevel must resolve to the main
        working tree (or the worktree root), never the internal
        .git/worktrees metadata directory."""
        _write_healthy_metaproject(self.repo)
        _init_repo(self.repo)
        worktree = self.root / "wt"
        res = _git(self.repo, "worktree", "add", "--detach", str(worktree))
        assert res.returncode == 0, res.stderr

        report = inspect_repository(worktree)
        toplevel = Path(report["git_toplevel"])
        self.assertNotIn(
            ".git",
            toplevel.parts,
            f"git_toplevel points into git metadata: {toplevel}",
        )


# ---------------------------------------------------------------------------
# Section D - init -> manage intake contract (audit §5)
# ---------------------------------------------------------------------------


def _require_intake_engine() -> None:
    if evaluate_manage_intake is None:
        raise AssertionError(
            "Stage 5 not implemented: scripts.manage_reports.evaluate_manage_intake "
            "is absent; intake admission cannot be verified"
        )


class TestReportIntakeRegressions(TempRootTestCase):
    """Audit §5: admission control separated from format validation."""

    ACTOR = "acme/app::antigravity::ag-main::agent-dev-lead"

    def setUp(self):
        super().setUp()
        self.repo = self.sub("repo")
        _write_healthy_metaproject(self.repo)
        self.base_report = create_init_report(
            repo_root=self.repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id=self.ACTOR,
            project_id="acme/app",
            status="completed",
            scenario={
                "profile": "active_development",
                "collaboration_model": "triad",
                "verification_policy": "strict_independent",
            },
        )

    def _write_report(self, name: str, **overrides) -> Path:
        data = json.loads(json.dumps(self.base_report))  # deep copy
        for key, value in overrides.items():
            data[key] = value
        path = self.root / name
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def _intake(self, report_path: Path):
        _require_intake_engine()
        return evaluate_manage_intake(
            repo_root=self.repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id=self.ACTOR,
            report_path=report_path,
        )

    def test_foreign_project_report_rejected_by_intake(self):
        report = self._write_report("foreign.json", project_id="other-org/evil")
        errors = self._intake(report)
        self.assertTrue(
            any("project_id" in e for e in errors),
            f"foreign project report admitted: {errors!r}",
        )

    def test_blocked_report_rejected_by_intake(self):
        report = self._write_report("blocked.json", status="blocked")
        errors = self._intake(report)
        self.assertTrue(errors, "blocked report admitted for manage")

    def test_awaiting_decision_report_rejected_by_intake(self):
        report = self._write_report("awaiting.json", status="awaiting_decision")
        errors = self._intake(report)
        self.assertTrue(errors, "awaiting_decision report admitted for manage")

    def test_missing_report_file_rejected_by_intake(self):
        _require_intake_engine()
        errors = evaluate_manage_intake(
            repo_root=self.repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id=self.ACTOR,
            report_path=self.root / "does_not_exist.json",
        )
        self.assertTrue(errors, "missing report file admitted")

    def test_corrupted_report_file_rejected_by_intake(self):
        corrupted = self.root / "corrupted.json"
        corrupted.write_text("{ not valid json", encoding="utf-8")
        errors = self._intake(corrupted)
        self.assertTrue(
            any("parse" in e.lower() or "corrupt" in e.lower() or "json" in e.lower() for e in errors),
            f"corrupted report file admitted: {errors!r}",
        )

    def test_installation_or_harness_mismatch_rejected_by_intake(self):
        report = self._write_report("wrong_installation.json", installation_id="zc-main")
        errors = self._intake(report)
        self.assertTrue(
            any("installation" in e.lower() or "harness" in e.lower() for e in errors),
            f"report for a different installation admitted: {errors!r}",
        )

    def test_stale_uncommitted_inputs_rejected_by_intake(self):
        _init_repo(self.repo)  # committed fixture incl. boundaries.md
        report = self._write_report("fresh.json")
        # Essential input changed after the report without a commit:
        boundaries = self.repo / ".agents" / "project_knowledge" / "boundaries.md"
        boundaries.write_text(
            MINIMAL_BOUNDARIES + "\n- `extra/path/**` appended post-report\n",
            encoding="utf-8",
        )
        errors = self._intake(report)
        self.assertTrue(
            any("stale" in e.lower() or "uncommitted" in e.lower() or "input" in e.lower() for e in errors),
            f"uncommitted boundaries change not detected by intake: {errors!r}",
        )

    def test_manage_create_cli_enforces_intake(self):
        """Guardian Step 64 finding (locked post-fix): `manage --action
        create` must fail closed without an existing, admitted init report —
        the CLI is the machine gate, hand-built reports are not a bypass."""
        init_dir = self.repo / ".agents" / "reports" / "ag-main" / "init"
        init_dir.mkdir(parents=True, exist_ok=True)
        # Materialize a completed init run for the happy path reference.
        good_run = "init-20260101T000000Z-cli00001"
        (init_dir / f"{good_run}.json").write_text(
            json.dumps(self.base_report, indent=2), encoding="utf-8"
        )
        # And a blocked init run.
        blocked_run = "init-20260101T000000Z-block001"
        blocked_report = json.loads(json.dumps(self.base_report))
        blocked_report["status"] = "blocked"
        (init_dir / f"{blocked_run}.json").write_text(
            json.dumps(blocked_report, indent=2), encoding="utf-8"
        )

        def _create(init_run_id: str):
            return subprocess.run(
                [
                    sys.executable,
                    str(MANAGE_REPORTS_SCRIPT),
                    "manage",
                    "--action",
                    "create",
                    "--repo-root",
                    str(self.repo),
                    "--installation",
                    "ag-main",
                    "--harness",
                    "antigravity",
                    "--actor",
                    self.ACTOR,
                    "--init-run-id",
                    init_run_id,
                    "--status",
                    "completed",
                ],
                capture_output=True,
                text=True,
            )

        # 1. Referenced init run does not exist -> fail closed.
        res_missing = _create("init-20260101T000000Z-MISSING0")
        self.assertNotEqual(res_missing.returncode, 0)
        self.assertIn("not found", res_missing.stderr)

        # 2. Referenced init run is blocked -> intake refusal.
        res_blocked = _create(blocked_run)
        self.assertNotEqual(res_blocked.returncode, 0)
        combined = res_blocked.stdout + res_blocked.stderr
        self.assertTrue(
            "intake rejected" in combined.lower() or "status" in combined.lower(),
            f"blocked init run not refused by CLI intake: {combined!r}",
        )

        # 3. Admitted init run -> creation succeeds.
        res_ok = _create(good_run)
        self.assertEqual(res_ok.returncode, 0, f"admitted create failed: {res_ok.stderr}")


class TestReportStorageRegressions(TempRootTestCase):
    """Audit §5: storage, pointers, latest semantics, default identity,
    completed-with-empty-scenario."""

    def setUp(self):
        super().setUp()
        self.repo = self.sub("repo")
        _write_healthy_metaproject(self.repo)

    def _report(self, run_id: str, status: str = "completed") -> dict:
        return create_init_report(
            repo_root=self.repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="acme/app::antigravity::ag-main::agent-dev-lead",
            project_id="acme/app",
            status=status,
            scenario={"profile": "active_development"},
            run_id=run_id,
        )

    def test_create_does_not_stamp_default_project_id(self):
        """CLI creation without --project-id must not silently stamp
        vlv-code/meta-project; identity must come from the local registry or
        the creation must fail."""
        res = subprocess.run(
            [
                sys.executable,
                str(MANAGE_REPORTS_SCRIPT),
                "init",
                "--action",
                "create",
                "--repo-root",
                str(self.repo),
                "--installation",
                "ag-main",
                "--harness",
                "antigravity",
                "--actor",
                "acme/app::antigravity::ag-main::agent-dev-lead",
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            pointer = (
                self.repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json"
            )
            data = json.loads(pointer.read_text(encoding="utf-8"))
            report = json.loads(
                Path(data["path"]).read_text(encoding="utf-8")
            )
            self.assertNotEqual(
                report.get("project_id"),
                "vlv-code/meta-project",
                "hardcoded default project_id stamped into foreign project report",
            )
        # rc != 0 (fail-closed without registry identity) is also acceptable.

    def test_completed_with_empty_scenario_rejected(self):
        """A completed report with an empty scenario must not validate."""
        data = create_init_report(
            repo_root=self.repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="acme/app::antigravity::ag-main::agent-dev-lead",
            project_id="acme/app",
            status="completed",
            scenario={},
        )
        errors = validate_report(data, expected_type="init")
        self.assertTrue(
            errors,
            "completed report with empty scenario passed format validation",
        )

    def test_repo_copy_reads_its_own_reports(self):
        """Cross-contamination regression: when the ORIGINAL directory still
        exists, a copied repository must read its OWN latest report, not the
        original's, via the latest.json pointer."""
        original = self.repo
        save_report(original, "ag-main", "init", self._report("init-20260101T000000Z-orig0001"))

        copy = self.root / "copy"
        shutil.copytree(original, copy)

        path, data = find_latest_report(copy, "ag-main", "init")
        self.assertIsNotNone(path, "no report found in the copied repository")
        self.assertTrue(
            str(path.resolve()).startswith(str(copy.resolve())),
            f"copied repository resolved a foreign report via pointer: {path}",
        )

    def test_existing_run_id_cannot_be_overwritten(self):
        """Saving a report with an existing run_id must be refused, not
        silently overwrite the earlier run."""
        report = self._report("init-20260101T000000Z-fixed001")
        save_report(self.repo, "ag-main", "init", report)
        with self.assertRaises(
            Exception,
            msg="save_report silently overwrote an existing run_id",
        ):
            save_report(self.repo, "ag-main", "init", report)

    def test_latest_means_latest_attempt(self):
        """find_latest_report must surface the latest attempt (including a
        corrupted/blocked one), never silently fall back to an older valid
        report and hide the recent failure."""
        older = self._report("init-20260101T000000Z-old00001")
        newer = self._report("init-20260102T000000Z-new00001")
        save_report(self.repo, "ag-main", "init", older)
        save_report(self.repo, "ag-main", "init", newer)

        # Corrupt the newest report file after it became the latest attempt.
        newer_file = (
            self.repo / ".agents" / "reports" / "ag-main" / "init" / f"{newer['run_id']}.json"
        )
        newer_file.write_text("{ corrupted latest attempt", encoding="utf-8")

        path, data = find_latest_report(self.repo, "ag-main", "init")
        self.assertFalse(
            data is not None and data.get("run_id") == older["run_id"],
            "latest lookup silently returned the older valid report, "
            "hiding the corrupted latest attempt",
        )

    def test_staleness_detects_uncommitted_input_changes(self):
        """Staleness must account for uncommitted changes of essential
        inputs (boundaries), not only the commit SHA."""
        _init_repo(self.repo)
        # Report captures the current HEAD; report files stay untracked so
        # HEAD does not move and only the uncommitted input change differs.
        report = self._report("init-20260101T000000Z-stale001")
        save_report(self.repo, "ag-main", "init", report)

        boundaries = self.repo / ".agents" / "project_knowledge" / "boundaries.md"
        boundaries.write_text(MINIMAL_BOUNDARIES + "\n- `changed/**`\n", encoding="utf-8")

        is_stale, details = check_report_staleness(self.repo, report)
        self.assertTrue(
            is_stale,
            f"uncommitted boundaries change not detected: {details!r}",
        )


# ---------------------------------------------------------------------------
# Section I - Team topology selection (audit §5/§6)
# ---------------------------------------------------------------------------


class TestTopologyRegressions(TempRootTestCase):
    """Audit §5/§6: agreed user decisions must not be silently overridden by
    size heuristics; unsupported models must be explicit; contradictory
    wishes must surface a conflict instead of a silent choice."""

    def test_explicit_triad_not_downgraded_by_loc(self):
        result = resolve_team_topology(
            {"profile": "active_development", "collaboration_model": "triad"},
            loc_estimate=500,
        )
        self.assertEqual(
            result["target_topology"],
            "triad",
            f"agreed triad silently downgraded by LOC heuristic: {result!r}",
        )

    def test_specialized_swarm_explicitly_unsupported(self):
        result = resolve_team_topology(
            {"profile": "active_development", "collaboration_model": "specialized_swarm"}
        )
        self.assertEqual(result["target_topology"], "specialized_swarm")
        self.assertFalse(
            result.get("supported", True),
            "specialized_swarm must be explicitly marked as not yet implemented",
        )

    def test_contradictory_wishes_surface_conflict(self):
        result = resolve_team_topology(
            {
                "profile": "active_development",
                "collaboration_model": "solo",
                "verification_policy": "strict_independent",
            }
        )
        self.assertTrue(
            result.get("conflicts"),
            "contradictory scenario resolved silently instead of surfacing a conflict",
        )


# ---------------------------------------------------------------------------
# Section E - Git hook installer (audit §8)
# ---------------------------------------------------------------------------


class TestHookInstallerRegressions(TempRootTestCase):
    """Audit §8: dispatcher chaining, worktrees, external manager
    conflicts."""

    def setUp(self):
        super().setUp()
        self.repo = self.sub("repo")
        _init_repo(self.repo)
        # Deploy a working gate script so installed hooks are executable.
        scripts_dir = self.repo / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        shutil.copyfile(CHECK_BOUNDARIES_SCRIPT, scripts_dir / "check_boundaries.py")

    def _hook_path(self) -> Path:
        return self.repo / ".git" / "hooks" / "pre-commit"

    def _stage_violation(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

    @unittest.skipIf(POSIX_SHELL is None, "no POSIX shell available")
    def test_existing_hook_exit_zero_does_not_stop_gate(self):
        """An existing hook finishing with exit 0 must not terminate the
        dispatcher: the boundary check must still run and block a staged Red
        Zone change."""
        self._hook_path().write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
        ok, msg = install_git_hook(self.repo)
        assert ok, msg
        self._stage_violation()

        res = subprocess.run(
            [POSIX_SHELL, str(self._hook_path())],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(
            res.returncode,
            0,
            f"boundary gate never ran: prior hook exit 0 terminated dispatcher "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )

    @unittest.skipIf(POSIX_SHELL is None, "no POSIX shell available")
    def test_existing_hook_failure_propagates(self):
        """A failing existing hook must preserve the denial (lock-in)."""
        self._hook_path().write_text("#!/usr/bin/env sh\nexit 1\n", encoding="utf-8")
        ok, msg = install_git_hook(self.repo)
        assert ok, msg

        res = subprocess.run(
            [POSIX_SHELL, str(self._hook_path())],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res.returncode, 0, "existing hook failure was swallowed")

    def test_reinstall_is_idempotent(self):
        """Repeated installation must not duplicate the dispatcher block
        (lock-in)."""
        install_git_hook(self.repo)
        install_git_hook(self.repo)
        content = self._hook_path().read_text(encoding="utf-8")
        self.assertEqual(
            content.count("# Meta-Project Boundary Gate Pre-Commit Hook"),
            1,
            "dispatcher block duplicated by reinstall",
        )

    def test_worktree_installation_supported(self):
        """Installing the hook from a linked worktree must succeed instead of
        failing with 'Not a git repository'."""
        worktree = self.root / "wt"
        res = _git(self.repo, "worktree", "add", "--detach", str(worktree))
        assert res.returncode == 0, res.stderr

        ok, msg = install_git_hook(worktree)
        self.assertTrue(
            ok,
            f"hook installation in a worktree failed: {msg}",
        )

    def test_external_hook_manager_conflict_reported(self):
        """A pre-existing external hook manager (e.g. husky) must yield an
        explicit conflict result, not a false 'installed successfully'."""
        self._hook_path().write_text(
            "#!/usr/bin/env sh\n"
            "# husky managed hook\n"
            '. "$(dirname -- "$0")/_/husky.sh"\n',
            encoding="utf-8",
        )
        ok, msg = install_git_hook(self.repo)
        self.assertFalse(
            ok and "conflict" not in msg.lower(),
            f"external hook manager conflict reported as success: ok={ok}, msg={msg!r}",
        )


# ---------------------------------------------------------------------------
# Section F - Memory: observations and compaction (audit §9)
# ---------------------------------------------------------------------------

OBS_HEADER = (
    "# Agent Observations Base\n\n"
    "| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |\n"
    "| :--- | :--- | :--- | :--- | :--- |\n"
)


def _obs_row(n: int) -> str:
    return (
        f"| 2026-01-{n:02d} | [runtime] | src/mod{n}.py | Unique issue {n} | Solution {n} |"
    )


class TestMemoryRegressions(TempRootTestCase):
    """Audit §9: in-table insertion, dry-run purity, note duplication,
    record/compact cycle, duplicate suppression."""

    def setUp(self):
        super().setUp()
        self.obs = self.root / "observations.md"

    def test_row_inserted_inside_table_before_trailing_text(self):
        """New observations must be inserted into the table, before any
        subsequent text — not appended to the end of the file."""
        self.obs.write_text(
            OBS_HEADER + _obs_row(1) + "\n\n## Later Notes\nTrailing section.\n",
            encoding="utf-8",
        )
        record_observation(
            category="runtime",
            path="src/new.py",
            issue="UNIQUE_MARKER_NEW_ROW",
            solution="fixed",
            obs_file=self.obs,
        )
        lines = self.obs.read_text(encoding="utf-8").splitlines()
        marker_idx = next(
            (i for i, ln in enumerate(lines) if "UNIQUE_MARKER_NEW_ROW" in ln), None
        )
        trailing_idx = next(
            (i for i, ln in enumerate(lines) if ln.startswith("## Later Notes")), None
        )
        self.assertIsNotNone(marker_idx, "new row missing from file")
        self.assertIsNotNone(trailing_idx)
        self.assertLess(
            marker_idx,
            trailing_idx,
            "new observation row landed after the trailing section "
            "(outside the table)",
        )

    def test_dry_run_creates_no_lock_file(self):
        """compact_memory --dry-run must not create even a .lock file."""
        rows = "\n".join(_obs_row(n) for n in range(1, 26))
        self.obs.write_text(OBS_HEADER + rows + "\n", encoding="utf-8")

        with contextlib.redirect_stdout(io.StringIO()):
            compact_main(
                [
                    "--dry-run",
                    "--observations",
                    str(self.obs),
                    "--tasks",
                    str(self.root / "no_tasks.md"),
                    "--archive-dir",
                    str(self.root / "archive"),
                ]
            )
        self.assertFalse(
            Path(str(self.obs) + ".lock").exists(),
            "--dry-run created a .lock file",
        )

    def test_archive_note_not_duplicated(self):
        """Repeated compactions must not accumulate duplicate archive NOTE
        blocks (live precedent: 7x duplicated NOTE in production repo)."""
        content = OBS_HEADER + "\n".join(_obs_row(n) for n in range(1, 26)) + "\n"
        _, primary1, _ = compact_observations(content, max_rows=20, keep_rows=10)

        # Simulate 15 new in-table records after the first compaction.
        table_part, note_part = primary1.split("> [!NOTE]", 1)
        fresh = "\n".join(_obs_row(100 + n) for n in range(15))
        content2 = table_part + fresh + "\n\n> [!NOTE]" + note_part

        _, primary2, _ = compact_observations(content2, max_rows=20, keep_rows=10)
        self.assertEqual(
            primary2.count("> [!NOTE]"),
            1,
            "archive NOTE block duplicated by repeated compaction",
        )

    def test_record_compact_record_compact_cycle(self):
        """Mandatory integration scenario (audit §9): every unique record
        must survive the record -> compact -> record -> compact cycle within
        the primary table or the archive."""
        rows = "\n".join(_obs_row(n) for n in range(1, 26))
        self.obs.write_text(OBS_HEADER + rows + "\n", encoding="utf-8")
        archive_dir = self.root / "archive"

        argv = [
            "--observations",
            str(self.obs),
            "--tasks",
            str(self.root / "no_tasks.md"),
            "--archive-dir",
            str(archive_dir),
            "--max-observations",
            "20",
            "--keep-observations",
            "10",
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            compact_main(argv)  # compact #1

        record_observation(
            category="runtime",
            path="src/cycle.py",
            issue="CYCLE_MARKER_ROW",
            solution="kept",
            obs_file=self.obs,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            compact_main(argv)  # compact #2

        content = self.obs.read_text(encoding="utf-8")
        note_idx = content.find("> [!NOTE]")
        primary_table = content if note_idx == -1 else content[:note_idx]
        archived = ""
        for arch_file in sorted(archive_dir.glob("observations_*.md")):
            archived += arch_file.read_text(encoding="utf-8")

        # 1) The new record must be inside the primary table (before NOTE).
        self.assertIn("CYCLE_MARKER_ROW", primary_table)
        # 2) Every unique row must be counted in primary table or archive.
        for n in range(1, 26):
            self.assertTrue(
                _obs_row(n) in primary_table or _obs_row(n) in archived,
                f"unique row {n} lost from both primary table and archive",
            )
        # 3) No data row may linger after the NOTE block.
        tail = content[note_idx:] if note_idx != -1 else ""
        self.assertFalse(
            re.search(r"^\| 2026-", tail, re.MULTILINE),
            "data rows accumulated beyond the archive NOTE (invisible to compactor)",
        )

    def test_exact_duplicate_event_suppressed(self):
        """Recording the exact same event (category/path/issue/solution/date)
        twice must not duplicate the row."""
        self.obs.write_text(OBS_HEADER, encoding="utf-8")
        args = dict(
            category="runtime",
            path="src/dup.py",
            issue="identical issue",
            solution="identical solution",
            obs_file=self.obs,
            date_str="2026-01-15",
        )
        record_observation(**args)
        record_observation(**args)
        content = self.obs.read_text(encoding="utf-8")
        self.assertEqual(
            content.count("| 2026-01-15 | [runtime] | src/dup.py | identical issue |"),
            1,
            "exact duplicate observation not suppressed",
        )


# ---------------------------------------------------------------------------
# Section G - Template synchronizer exit codes (audit §9)
# ---------------------------------------------------------------------------


class TestSyncTemplatesExitCodes(TempRootTestCase):
    """Audit §9: non-zero exit on unrecoverable errors after --write, no
    [OK] for failures."""

    def _make_skill_fixture(self, root: Path) -> None:
        targets = {
            "init-meta-project": (
                "boundaries.md",
                "observations.md",
                "weak_spots.md",
                "architecture.md",
                "tasks.md",
                "AGENTS.md",
            ),
            "manage-meta-project": ("profile.md", "notes.md", "system_prompt.md"),
        }
        for skill_name, templates in targets.items():
            skill = root / "skills" / skill_name / "SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            blocks = []
            for tmpl in templates:
                blocks.append(
                    f"### Template: `{tmpl}`\n"
                    f"<!-- TEMPLATE:BEGIN {tmpl} -->\n"
                    "```markdown\nold content\n```\n"
                    f"<!-- TEMPLATE:END {tmpl} -->\n"
                )
            skill.write_text(f"# {skill_name}\n\n" + "\n".join(blocks), encoding="utf-8")

    def _write_canonical_templates(self, root: Path) -> None:
        tmpl_dir = root / "templates" / "project_knowledge"
        tmpl_dir.mkdir(parents=True, exist_ok=True)
        for name in (
            "boundaries.md",
            "observations.md",
            "weak_spots.md",
            "architecture.md",
            "tasks.md",
        ):
            (tmpl_dir / name).write_text(f"canonical {name}\n", encoding="utf-8")
        (root / "templates" / "AGENTS.md").write_text(
            "canonical AGENTS.md\n", encoding="utf-8"
        )
        team_dir = root / "templates" / "team"
        team_dir.mkdir(parents=True, exist_ok=True)
        for name in ("profile.md", "notes.md", "system_prompt.md"):
            (team_dir / name).write_text(f"canonical {name}\n", encoding="utf-8")
        # Wave E Lane P2: init resources also require canonical shell-skill
        # sources (RESOURCE_TARGETS maps them into skills/init-meta-project/resources/).
        for skill_name in (
            "record-observation",
            "sync-architecture",
            "ground-meta-project",
        ):
            skill_dir = root / "skills" / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"canonical {skill_name}\n", encoding="utf-8"
            )

    def test_write_with_missing_canonical_template_fails(self):
        """--write with a missing canonical template must exit non-zero and
        must not print [OK] for the unrecoverable error."""
        root = self.sub("repo")
        self._make_skill_fixture(root)
        (root / "templates" / "project_knowledge").mkdir(parents=True, exist_ok=True)
        # canonical templates intentionally absent

        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sync_main(["--write", "--repo-root", str(root)])

        self.assertNotEqual(
            rc,
            0,
            f"--write returned success despite missing canonical template "
            f"(stdout={out.getvalue()!r})",
        )
        self.assertFalse(
            "[OK] Missing canonical template" in out.getvalue(),
            "unrecoverable missing-template error reported with [OK]",
        )

    def test_write_then_check_leaves_zero_drift(self):
        """Lock-in: after a successful --write, a --check pass must report
        zero drift (post-write re-verification)."""
        root = self.sub("repo")
        self._make_skill_fixture(root)
        self._write_canonical_templates(root)

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            rc_write = sync_main(["--write", "--repo-root", str(root)])
            rc_check = sync_main(["--check", "--repo-root", str(root)])

        self.assertEqual(rc_write, 0)
        self.assertEqual(rc_check, 0, "drift remains after --write")


# ---------------------------------------------------------------------------
# Section H - Canonical docs must match actual CLI (audit §6)
# ---------------------------------------------------------------------------


class TestCanonicalDocsMatchCLI(unittest.TestCase):
    """Audit §6: example commands in canonical documents must invoke real
    CLI flags (e.g. --path, not the nonexistent --component)."""

    def test_record_obs_examples_use_supported_flags(self):
        res = subprocess.run(
            [sys.executable, str(RECORD_OBS_SCRIPT), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        supported = set(re.findall(r"--[a-zA-Z][\w-]*", res.stdout))

        offenders = []
        for doc in (REPO_ROOT / "AGENTS.md", REPO_ROOT / "templates" / "AGENTS.md"):
            self.assertTrue(doc.is_file(), f"missing canonical doc: {doc}")
            for line in doc.read_text(encoding="utf-8").splitlines():
                if "record_obs.py" in line and "--category" in line:
                    used = set(re.findall(r"--[a-zA-Z][\w-]*", line))
                    unknown = used - supported
                    if unknown:
                        offenders.append((str(doc), sorted(unknown)))
        self.assertFalse(
            offenders,
            f"canonical docs reference nonexistent record_obs.py flags: {offenders}",
        )

    def test_no_mechanical_edit_counter_in_canon(self):
        """Roadmap decision (2026-11-12 note to §7.1): the mechanical edit-count
        Circuit Breaker was rejected; canonical docs must carry the SEMANTIC
        trigger only (repeatedly failing edits on one defect / new adjacent
        regressions), never a '2nd attempt' counter."""
        canon = [
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "templates" / "AGENTS.md",
            REPO_ROOT / "templates" / "global" / "AGENTS.md",
            REPO_ROOT / "templates" / "team" / "system_prompt.md",
            REPO_ROOT / "skills" / "manage-meta-project" / "SKILL.md",
        ]
        banned = ("2nd consecutive", "second attempt", "Stop-Work on 2nd",
                  "2 consecutive failed attempts")
        offenders = []
        for doc in canon:
            text = doc.read_text(encoding="utf-8")
            for phrase in banned:
                if phrase.lower() in text.lower():
                    offenders.append((str(doc), phrase))
        self.assertFalse(offenders, f"mechanical edit counter still in canon: {offenders}")


GROUND_SKILL = REPO_ROOT / "skills" / "ground-meta-project" / "SKILL.md"


class TestGroundSkillContracts(unittest.TestCase):
    """Wave 0.9.0 Part 2 (roadmap §6–§8): semantic triggers, dual-mode
    operation, conditional continuation, validator-based identity."""

    @classmethod
    def setUpClass(cls):
        cls.text = GROUND_SKILL.read_text(encoding="utf-8")

    def test_no_mechanical_trigger(self):
        self.assertNotIn(
            "2 consecutive failed attempts", self.text,
            "ground still carries the mechanical 2-attempt trigger",
        )

    def test_no_unconditional_halt(self):
        self.assertNotIn(
            "MUST halt and wait for user confirmation before taking any further code action",
            self.text,
            "ground still ends with an unconditional halt",
        )

    def test_dual_mode_declared(self):
        self.assertIn("Recovery", self.text)
        self.assertIn("Drift", self.text)

    def test_identity_via_validator_not_guessing(self):
        self.assertIn("verify_identity", self.text)
        self.assertIn("--actor", self.text)
        self.assertNotIn("never infer or adopt a role from invoked skills or read files", self.text)

    def test_conditional_continuation_declared(self):
        for phrase in ("continue", "one concrete question"):
            self.assertIn(phrase, self.text.lower())


TUNE_SKILL = REPO_ROOT / "skills" / "tune-meta-project" / "SKILL.md"


class TestTuneSkillContracts(unittest.TestCase):
    """Wave 0.9.0 Part 3 (roadmap tune §1–§10): evidence over heuristics,
    total-set North Stars limit, effect verification, repeatability."""

    @classmethod
    def setUpClass(cls):
        cls.text = TUNE_SKILL.read_text(encoding="utf-8")

    def test_no_mechanical_heuristics(self):
        for banned in ("3+ times consecutively", "30 days",
                       "git log -n 15", "Repeated `Circuit Breaker` triggers"):
            self.assertNotIn(banned, self.text, f"mechanical heuristic remains: {banned}")

    def test_evidence_hypothesis_separation_declared(self):
        self.assertIn("hypothesis", self.text.lower())
        self.assertIn("evidence", self.text.lower())

    def test_north_stars_limit_is_total_set(self):
        self.assertNotIn("at most 3", self.text.lower())
        self.assertTrue(
            "total active set" in self.text.lower()
            or "active set" in self.text.lower(),
            "North Stars limit must apply to the total active set, not per-run additions",
        )

    def test_effect_verification_declared(self):
        for phrase in ("not verified", "no-effect", "regression"):
            self.assertIn(phrase, self.text.lower())

    def test_repeatability_declared(self):
        self.assertIn("rejected proposals", self.text.lower())

    def test_read_only_analysis_declared(self):
        self.assertIn("read-only", self.text.lower())

    def test_no_scan_writing_scenario_invoked(self):
        self.assertNotIn("scan-meta-project", self.text)


if __name__ == "__main__":
    unittest.main()
