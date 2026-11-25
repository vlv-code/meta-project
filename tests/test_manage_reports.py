#!/usr/bin/env python3
"""Canonical domain test suite for manage_reports (scripts/manage_reports.py).

Consolidated in Wave T (Lane T2) from:
- tests/test_manage_reports.py
- tests/test_dwave_m.py
- tests/test_fwave_r.py
- tests/test_jwave_m.py
- tests/test_lwave_deconfliction.py

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import manage_reports
from scripts.manage_reports import (
    ESSENTIAL_INPUT_PATHS,
    SUPPORTED_SCHEMA_VERSIONS,
    _recover_registry_baseline,
    apply_duty_reconciliation,
    check_report_staleness,
    collect_input_fingerprints,
    create_init_report,
    create_manage_report,
    detect_role_duty_conflicts,
    find_latest_report,
    get_git_state,
    get_report_dir,
    save_report,
    validate_report,
)

MANAGE_REPORTS_SCRIPT = REPO_ROOT / "scripts" / "manage_reports.py"
SCRIPTS_DIR = REPO_ROOT / "scripts"

PROJECT_ID = "acme/app"
HARNESS = "antigravity"
INSTALLATION = "ag-main"
ACTOR = f"{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-dev-lead"

REGISTRY_REL = ".agents/meta-project.json"
BOUNDARIES_REL = ".agents/project_knowledge/boundaries.md"

AGENTS_MD = (
    "# Project Passport: Fixture\n\n"
    "## 1. Concept, Principles, and North Stars\n"
    "- Meta-Project fixture passport.\n"
)

BOUNDARIES_MD = (
    "# Responsibility Zones and Change Boundaries\n\n"
    "## Green Zone (Autonomous Modification)\n"
    "- `docs/**`\n\n"
    "## Yellow Zone (Modification with Mandatory Verification)\n"
    "- `scripts/**`\n\n"
    "## Red Zone (Prohibited Without Direct User Confirmation)\n"
    "- `LICENSE`\n"
)

DECLARED_BLOCK = {
    "native_orchestrator": True,
    "dispatcher_binding": "orchestrator-hosted",
}

ABSENT = object()


def _binding(role_id: str, status: str = "active", harness: str = HARNESS, installation: str = INSTALLATION) -> dict:
    return {
        "actor_id": f"{PROJECT_ID}::{harness}::{installation}::{role_id}",
        "status": status,
        "profile_path": f".agents/team/{role_id}/profile.md",
    }


def _role_entry(role_id: str) -> dict:
    return {
        "description": f"fixture role {role_id}",
        "bindings": {INSTALLATION: _binding(role_id)},
    }


DEFAULT_ROLES = {
    "agent-dev-lead": {
        "description": "fixture lead role",
        "bindings": {INSTALLATION: _binding("agent-dev-lead")},
    }
}


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    res = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )
    assert res.returncode == 0, f"git {' '.join(args)} failed: {res.stderr}"
    return res


def _init_git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    res = _git(path, "init", "-q")
    assert res.returncode == 0, res.stderr
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test Operator")
    return path


def _commit_all(path: Path, message: str = "fixture commit") -> str:
    _git(path, "add", ".")
    res = _git(path, "commit", "-q", "-m", message)
    assert res.returncode == 0, res.stderr
    sha = _git(path, "rev-parse", "HEAD").stdout.strip()
    assert len(sha) == 40, sha
    return sha


def _run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MANAGE_REPORTS_SCRIPT), *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _base_init_report(
    repo: Path, run_id: str, status: str = "completed"
) -> dict:
    return create_init_report(
        repo_root=repo,
        installation_id="ag-main",
        harness_id="antigravity",
        actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
        project_id="vlv-code/meta-project",
        status=status,
        scenario={
            "profile": "active_development",
            "collaboration_model": "triad",
            "verification_policy": "strict_independent",
            "unresolved_questions": [],
        },
        run_id=run_id,
    )


# ---------------------------------------------------------------------------
# TestManageReports (from tests/test_manage_reports.py)
# ---------------------------------------------------------------------------
class TestManageReports(unittest.TestCase):
    """Test suite for initialization and management report validation and lifecycle."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.init_template_path = REPO_ROOT / "templates" / "reports" / "init_report.json"
        self.manage_template_path = REPO_ROOT / "templates" / "reports" / "manage_report.json"

        with open(self.init_template_path, "r", encoding="utf-8") as f:
            self.valid_init_data = json.load(f)

        with open(self.manage_template_path, "r", encoding="utf-8") as f:
            self.valid_manage_data = json.load(f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_report_schema_validation_passes(self):
        """Verifies that canonical init report template passes schema validation."""
        self.assertIsNotNone(validate_report, "manage_reports module must be implemented")
        errors = validate_report(self.valid_init_data, expected_type="init")
        self.assertEqual(errors, [], f"Validation failed with errors: {errors}")

    def test_init_report_missing_mandatory_field_fails(self):
        """Adversarial test: omitting mandatory fields results in validation errors."""
        self.assertIsNotNone(validate_report, "manage_reports module must be implemented")
        mandatory_fields = [
            "schema_version",
            "report_type",
            "project_id",
            "installation_id",
            "harness_id",
            "actor_id",
            "run_id",
            "status",
            "scenario",
            "git_state",
            "next_step_readiness",
        ]
        for field in mandatory_fields:
            corrupted_data = dict(self.valid_init_data)
            del corrupted_data[field]
            errors = validate_report(corrupted_data, expected_type="init")
            self.assertTrue(
                any(field in err for err in errors),
                f"Expected validation error mentioning missing field '{field}', got: {errors}",
            )

    def test_manage_report_requires_init_run_id(self):
        """Verifies that manage report strictly requires a non-empty init_run_id."""
        self.assertIsNotNone(validate_report, "manage_reports module must be implemented")
        # Valid manage report passes
        errors = validate_report(self.valid_manage_data, expected_type="manage")
        self.assertEqual(errors, [])

        # Missing init_run_id fails
        corrupted = dict(self.valid_manage_data)
        del corrupted["init_run_id"]
        errors = validate_report(corrupted, expected_type="manage")
        self.assertTrue(any("init_run_id" in err for err in errors))

        # Empty init_run_id fails
        corrupted["init_run_id"] = "   "
        errors = validate_report(corrupted, expected_type="manage")
        self.assertTrue(any("init_run_id" in err for err in errors))

    def test_atomic_write_and_latest_symlink_or_pointer(self):
        """Verifies atomic report write and latest.json pointer creation without races."""
        self.assertIsNotNone(save_report, "manage_reports module must be implemented")
        installation_id = "ag-main"
        report_path = save_report(
            repo_root=self.root,
            installation_id=installation_id,
            report_type="init",
            report_data=self.valid_init_data,
        )

        self.assertTrue(report_path.exists())
        self.assertEqual(report_path.name, f"{self.valid_init_data['run_id']}.json")

        # Verify latest.json pointer exists in the report directory
        latest_pointer = self.root / ".agents" / "reports" / installation_id / "init" / "latest.json"
        self.assertTrue(latest_pointer.exists())

        with open(latest_pointer, "r", encoding="utf-8") as f:
            pointer_data = json.load(f)

        self.assertEqual(pointer_data.get("run_id"), self.valid_init_data["run_id"])
        self.assertEqual(pointer_data.get("status"), self.valid_init_data["status"])
        # Audit §5 contract: pointer stores a RELATIVE path resolvable inside
        # the report directory (repository copies must read their OWN reports).
        pointer_path = Path(pointer_data.get("path"))
        self.assertFalse(pointer_path.is_absolute(), "pointer path must be relative")
        self.assertTrue((latest_pointer.parent / pointer_path).exists())

    def test_corrupted_json_fails_closed(self):
        """Adversarial test: malformed JSON or invalid schema version fails gracefully."""
        self.assertIsNotNone(validate_report, "manage_reports module must be implemented")
        # Incompatible schema version
        corrupted = dict(self.valid_init_data)
        corrupted["schema_version"] = "99.0.0"
        errors = validate_report(corrupted, expected_type="init")
        self.assertTrue(any("schema_version" in err for err in errors))

        # Invalid report_type
        corrupted = dict(self.valid_init_data)
        corrupted["report_type"] = "invalid_type"
        errors = validate_report(corrupted, expected_type="init")
        self.assertTrue(any("report_type" in err for err in errors))

        # Invalid status
        corrupted = dict(self.valid_init_data)
        corrupted["status"] = "unknown_status"
        errors = validate_report(corrupted, expected_type="init")
        self.assertTrue(any("status" in err for err in errors))

    def test_cli_init_create_and_verify(self):
        """Verifies CLI execution for creating and verifying init reports."""
        cli_script = REPO_ROOT / "scripts" / "manage_reports.py"
        scenario_file = self.root / "scenario.json"
        with open(scenario_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_init_data["scenario"], f)

        # 1. Create init report via CLI
        cmd_create = [
            sys.executable,
            str(cli_script),
            "init",
            "--action",
            "create",
            "--repo-root",
            str(self.root),
            "--installation",
            "ag-main",
            "--harness",
            "antigravity",
            "--actor",
            "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id",
            "vlv-code/meta-project",
            "--status",
            "completed",
            "--scenario-file",
            str(scenario_file),
            "--json",
        ]
        proc = subprocess.run(cmd_create, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"CLI create failed: {proc.stderr}\n{proc.stdout}")

        created_info = json.loads(proc.stdout)
        self.assertTrue(created_info.get("success"))
        report_path = Path(created_info["report_path"])
        self.assertTrue(report_path.exists())

        # 2. Verify init report via CLI
        cmd_verify = [
            sys.executable,
            str(cli_script),
            "init",
            "--action",
            "verify",
            "--report",
            str(report_path),
            "--json",
        ]
        proc_verify = subprocess.run(cmd_verify, capture_output=True, text=True)
        self.assertEqual(proc_verify.returncode, 0, f"CLI verify failed: {proc_verify.stderr}\n{proc_verify.stdout}")
        verify_info = json.loads(proc_verify.stdout)
        self.assertTrue(verify_info.get("valid"))

    def test_cli_manage_create_and_verify(self):
        """Verifies CLI execution for creating and verifying manage reports.

        Audit §5 + Guardian Step 64: manage create is admitted only by an
        existing, admitted init report for the installation (fail-closed
        intake via evaluate_manage_intake)."""
        cli_script = REPO_ROOT / "scripts" / "manage_reports.py"

        # Intake-valid context: registry with an active ag-main installation
        # and an admitted init report for the referenced run.
        registry = {
            "schema_version": "1.1.0",
            "project_id": "vlv-code/meta-project",
            "installations": {
                "ag-main": {
                    "harness_id": "antigravity",
                    "status": "active",
                    "description": "fixture",
                }
            },
            "roles": {
                "agent-dev-lead": {
                    "description": "fixture role",
                    "bindings": {
                        "ag-main": {
                            "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        }
                    },
                }
            },
        }
        agents_dir = self.root / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "meta-project.json").write_text(
            json.dumps(registry, indent=2), encoding="utf-8"
        )
        profile_path = agents_dir / "team" / "agent-dev-lead" / "profile.md"
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.write_text(
            "---\n"
            'name: "Dev Lead"\n'
            'role_id: "agent-dev-lead"\n'
            'harness_id: "antigravity"\n'
            'installation_id: "ag-main"\n'
            'actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        init_data = create_init_report(
            repo_root=self.root,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            status="completed",
            scenario=self.valid_init_data["scenario"],
            next_step_readiness=self.valid_init_data.get("next_step_readiness"),
            run_id="20261115T005300Z-a1b2c3d4",
        )
        save_report(self.root, "ag-main", "init", init_data)

        data_file = self.root / "manage_data.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scenario": self.valid_manage_data["scenario"],
                    "roles": self.valid_manage_data["roles"],
                    "bindings": self.valid_manage_data["bindings"],
                    "effective_capabilities": self.valid_manage_data["effective_capabilities"],
                    "checks": self.valid_manage_data["checks"],
                    "remaining_manual_actions": [],
                },
                f,
            )

        cmd_create = [
            sys.executable,
            str(cli_script),
            "manage",
            "--action",
            "create",
            "--repo-root",
            str(self.root),
            "--installation",
            "ag-main",
            "--harness",
            "antigravity",
            "--actor",
            "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id",
            "vlv-code/meta-project",
            "--init-run-id",
            "20261115T005300Z-a1b2c3d4",
            "--status",
            "completed",
            "--data-file",
            str(data_file),
            "--json",
        ]
        proc = subprocess.run(cmd_create, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"CLI manage create failed: {proc.stderr}\n{proc.stdout}")

        created_info = json.loads(proc.stdout)
        self.assertTrue(created_info.get("success"))
        report_path = Path(created_info["report_path"])
        self.assertTrue(report_path.exists())

        cmd_verify = [
            sys.executable,
            str(cli_script),
            "manage",
            "--action",
            "verify",
            "--report",
            str(report_path),
            "--json",
        ]
        proc_verify = subprocess.run(cmd_verify, capture_output=True, text=True)
        self.assertEqual(proc_verify.returncode, 0, f"CLI manage verify failed: {proc_verify.stderr}\n{proc_verify.stdout}")
        verify_info = json.loads(proc_verify.stdout)
        self.assertTrue(verify_info.get("valid"))

    def test_update_report_type_validates(self):
        """Wave 0.9.0 Task C3: the 'update' report type validates against the
        canonical template; mandatory update fields are enforced fail-closed
        and 'completed' with unresolved conflicts is refused."""
        self.assertIsNotNone(validate_report, "manage_reports module must be implemented")
        update_template_path = REPO_ROOT / "templates" / "reports" / "update_report.json"
        with open(update_template_path, "r", encoding="utf-8") as f:
            valid_update_data = json.load(f)

        # 1. Canonical template passes validation.
        errors = validate_report(valid_update_data, expected_type="update")
        self.assertEqual(errors, [], f"Validation failed with errors: {errors}")

        # 2. Missing mandatory update fields fail.
        mandatory_fields = ["versions", "source", "affected_components"]
        for field in mandatory_fields:
            corrupted_data = dict(valid_update_data)
            del corrupted_data[field]
            errors = validate_report(corrupted_data, expected_type="update")
            self.assertTrue(
                any(field in err for err in errors),
                f"Expected validation error mentioning missing field '{field}', got: {errors}",
            )

        # 3. 'completed' with non-empty conflicts is invalid (must be
        #    'awaiting_decision'); 'awaiting_decision' with conflicts is valid.
        conflicted_data = dict(valid_update_data)
        conflicted_data["conflicts"] = [
            {"path": "scripts/x.py", "reason": "unmarked local edit"}
        ]
        errors = validate_report(conflicted_data, expected_type="update")
        self.assertTrue(
            any("awaiting_decision" in err for err in errors),
            f"Completed update report with conflicts must be refused, got: {errors}",
        )
        conflicted_data["status"] = "awaiting_decision"
        errors = validate_report(conflicted_data, expected_type="update")
        self.assertEqual(
            errors, [], f"awaiting_decision update report with conflicts must be valid: {errors}"
        )

    def test_tune_report_type_validates(self):
        """Wave 0.9.0 Task T3: the 'tune' report type validates against the
        canonical template; proposals are a mandatory non-empty list, every
        proposal carries a decision, rejected proposals carry rationale, and
        'completed' with an undecided proposal is refused."""
        self.assertIsNotNone(validate_report, "manage_reports module must be implemented")
        tune_template_path = REPO_ROOT / "templates" / "reports" / "tune_report.json"
        with open(tune_template_path, "r", encoding="utf-8") as f:
            valid_tune_data = json.load(f)

        # 1. Canonical template passes validation.
        errors = validate_report(valid_tune_data, expected_type="tune")
        self.assertEqual(errors, [], f"Validation failed with errors: {errors}")

        # 2. Missing 'proposals' fails (mandatory non-empty list).
        corrupted = dict(valid_tune_data)
        del corrupted["proposals"]
        errors = validate_report(corrupted, expected_type="tune")
        self.assertTrue(
            any("proposals" in err for err in errors),
            f"Expected validation error mentioning missing field 'proposals', got: {errors}",
        )

        # 3. A proposal without 'decision' fails.
        corrupted = json.loads(json.dumps(valid_tune_data))
        del corrupted["proposals"][0]["decision"]
        errors = validate_report(corrupted, expected_type="tune")
        self.assertTrue(
            any("decision" in err for err in errors),
            f"Expected validation error mentioning missing 'decision', got: {errors}",
        )

        # 4. 'completed' with an undecided ('proposed') proposal fails.
        corrupted = json.loads(json.dumps(valid_tune_data))
        corrupted["proposals"][0]["decision"] = "proposed"
        errors = validate_report(corrupted, expected_type="tune")
        self.assertTrue(
            any("undecided" in err.lower() for err in errors),
            f"Completed tune report with undecided proposal must be refused, got: {errors}",
        )

        # 5. A rejected proposal without 'rationale' fails.
        rejected_idx = next(
            i
            for i, p in enumerate(valid_tune_data["proposals"])
            if p.get("decision") == "rejected"
        )
        corrupted = json.loads(json.dumps(valid_tune_data))
        del corrupted["proposals"][rejected_idx]["rationale"]
        errors = validate_report(corrupted, expected_type="tune")
        self.assertTrue(
            any("rationale" in err for err in errors),
            f"Rejected proposal without rationale must be refused, got: {errors}",
        )

    def test_find_latest_report(self):
        """Verifies finding the latest report when multiple reports exist."""
        self.assertIsNotNone(save_report, "manage_reports module must be implemented")
        installation_id = "ag-main"

        # Create older report
        older_data = dict(self.valid_init_data)
        older_data["run_id"] = "20261115T001000Z-11111111"
        save_report(self.root, installation_id, "init", older_data)

        # Create newer report
        newer_data = dict(self.valid_init_data)
        newer_data["run_id"] = "20261115T002000Z-22222222"
        save_report(self.root, installation_id, "init", newer_data)

        latest_path, latest_data = find_latest_report(self.root, installation_id, "init")
        self.assertIsNotNone(latest_path)
        self.assertEqual(latest_data["run_id"], "20261115T002000Z-22222222")


# ---------------------------------------------------------------------------
# TestDeclaredDeltaIntake (from tests/test_dwave_m.py)
# ---------------------------------------------------------------------------
class TestDeclaredDeltaIntake(unittest.TestCase):
    """T2.1: pre-op admission with declared-delta verification."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_m_")
        self.root = Path(self.temp_dir).resolve()
        self._seed_repo()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- fixture helpers ---------------------------------------------------

    def _seed_repo(self):
        root = self.root
        (root / "AGENTS.md").write_text(AGENTS_MD, encoding="utf-8")
        (root / BOUNDARIES_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / BOUNDARIES_REL).write_text(BOUNDARIES_MD, encoding="utf-8")
        self._write_registry(DEFAULT_ROLES)
        profile = root / ".agents" / "team" / "agent-dev-lead" / "profile.md"
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Dev Lead"\n'
            'role_id: "agent-dev-lead"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{ACTOR}"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "fixture@example.com")
        _git(root, "config", "user.name", "Fixture")
        _git(root, "add", "-A")
        _git(root, "commit", "-qm", "fixture: committed registry baseline")

    def _write_registry(self, roles: dict) -> dict:
        registry = {
            "schema_version": "1.1.0",
            "project_id": PROJECT_ID,
            "installations": {
                INSTALLATION: {
                    "harness_id": HARNESS,
                    "status": "active",
                    "description": "fixture installation",
                }
            },
            "roles": roles,
        }
        _write_json(self.root / REGISTRY_REL, registry)
        return registry

    def _add_registry_role(self, role_id: str):
        """Simulate the manage operation mutating the registry on disk."""
        registry = json.loads(
            (self.root / REGISTRY_REL).read_text(encoding="utf-8")
        )
        registry["roles"][role_id] = _role_entry(role_id)
        _write_json(self.root / REGISTRY_REL, registry)

    def _save_init_report(self, run_id: str) -> dict:
        from scripts.manage_reports import create_init_report, save_report

        report = create_init_report(
            repo_root=self.root,
            installation_id=INSTALLATION,
            harness_id=HARNESS,
            actor_id=ACTOR,
            project_id=PROJECT_ID,
            status="completed",
            scenario={
                "profile": "active_development",
                "collaboration_model": "duo",
                "verification_policy": "duo_peer_review",
            },
            run_id=run_id,
        )
        save_report(self.root, INSTALLATION, "init", report)
        return report

    def _manage_create(
        self,
        init_run_id: str,
        changes=None,
        tag: str = "data",
    ) -> subprocess.CompletedProcess:
        payload = {
            "scenario": {
                "profile": "active_development",
                "collaboration_model": "duo",
            },
            "roles": {
                "preserved": ["agent-dev-lead"],
                "created": [],
                "adapted": [],
                "archived": [],
            },
            "bindings": {},
        }
        if changes is not None:
            payload["changes"] = changes
        data_file = _write_json(
            self.root / f"manage_{tag}.json", payload
        )
        return _run_cli(
            self.root,
            "manage",
            "--action",
            "create",
            "--repo-root",
            str(self.root),
            "--installation",
            INSTALLATION,
            "--harness",
            HARNESS,
            "--actor",
            ACTOR,
            "--init-run-id",
            init_run_id,
            "--status",
            "completed",
            "--data-file",
            str(data_file),
            "--json",
        )

    # -- T2.1 tests ---------------------------------------------------------

    def test_manage_allows_declared_registry_change(self):
        """Registry delta EXACTLY equal to declared changes[] must be
        admitted: the natural init -> manage(adds roles) -> report flow must
        not die on 'stale report: essential input changed' (auditor п.3)."""
        run_id = "init-20260101T000000Z-aaa00001"
        self._save_init_report(run_id)
        self._add_registry_role("agent-quality-guardian")
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
                "path": ".agents/team/agent-quality-guardian/profile.md",
            }
        ]
        res = self._manage_create(run_id, changes=changes)
        self.assertEqual(
            res.returncode,
            0,
            f"declared registry delta refused by intake "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))

        # Formalization: the saved manage report records the declared delta.
        report_path = Path(created["report_path"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(
            report.get("changes"),
            changes,
            "manage report must record the declared changes[] verbatim",
        )

    def test_manage_rejects_undeclared_registry_change(self):
        """A registry delta NOT fully covered by declared changes[] must be
        refused with an explicit diff listing naming the uncovered delta."""
        run_id = "init-20260101T000000Z-bbb00002"
        self._save_init_report(run_id)
        self._add_registry_role("agent-quality-guardian")
        # Second, UNDECLARED registry mutation.
        self._add_registry_role("agent-github-steward")
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
            }
        ]
        res = self._manage_create(run_id, changes=changes, tag="undeclared")
        self.assertNotEqual(
            res.returncode,
            0,
            f"partially declared registry delta admitted: {res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            "agent-github-steward",
            combined,
            f"refusal must list the uncovered registry delta element: {combined!r}",
        )
        self.assertTrue(
            "not covered" in combined.lower() or "delta" in combined.lower(),
            f"refusal must explain the declared-delta mismatch: {combined!r}",
        )

    def test_manage_rejects_unrelated_slice_change(self):
        """Lock-in: staleness for NON-declared essential inputs stays.
        boundaries.md changed since the init report -> refused even when the
        registry itself is untouched."""
        run_id = "init-20260101T000000Z-ccc00003"
        self._save_init_report(run_id)
        boundaries = self.root / BOUNDARIES_REL
        boundaries.write_text(
            BOUNDARIES_MD + "\n- `extra/path/**` appended post-report\n",
            encoding="utf-8",
        )
        res = self._manage_create(run_id, changes=[], tag="boundaries")
        self.assertNotEqual(
            res.returncode,
            0,
            f"boundaries.md drift admitted by intake: {res.stdout!r}",
        )
        combined = (res.stdout + res.stderr).lower()
        self.assertTrue(
            "boundaries" in combined or "stale" in combined,
            f"refusal must name the drifted input: {combined!r}",
        )

    def test_manage_rejects_superseded_init_report(self):
        """A newer init run for the installation supersedes the referenced
        report: refuse with a pointer to the newer run."""
        older = "init-20260101T000000Z-old00001"
        newer = "init-20260101T000000Z-new00002"
        self._save_init_report(older)
        self._save_init_report(newer)
        res = self._manage_create(older, tag="superseded")
        self.assertNotEqual(
            res.returncode,
            0,
            f"superseded init report still authorizes manage: {res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            newer,
            combined,
            f"supersession refusal must point at the newer init run: {combined!r}",
        )

    def test_manage_ignores_commit_movement_when_inputs_fresh(self):
        """Commit movement alone (fresh essential inputs, non-superseded
        report) must NOT refuse manage: the commit-moved false positive is
        replaced by the supersession check."""
        run_id = "init-20260101T000000Z-ddd00004"
        self._save_init_report(run_id)
        # Move HEAD without touching any essential input.
        src = self.root / "src"
        src.mkdir(exist_ok=True)
        (src / "feature.py").write_text("# feature\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "second commit: src only")
        res = self._manage_create(run_id, tag="commitmoved")
        self.assertEqual(
            res.returncode,
            0,
            f"commit movement with fresh inputs refused (false positive): "
            f"stdout={res.stdout!r}, stderr={res.stderr!r}",
        )


# ---------------------------------------------------------------------------
# TestTuneSubcommand (from tests/test_dwave_m.py)
# ---------------------------------------------------------------------------
class TestTuneSubcommand(unittest.TestCase):
    """T2.2: `tune` CLI subcommand creating and locating tune reports."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_m_tune_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tune_create_and_latest_roundtrip(self):
        proposals = [
            {
                "id": "P-1",
                "target": "role topology",
                "proposal": "Add agent-quality-guardian binding for ag-main",
                "hypothesis": "verification throughput improves",
                "evidence": "friction cluster in handoff logs",
                "decision": "proposed",
            }
        ]
        data_file = _write_json(
            self.root / "tune_data.json", {"proposals": proposals}
        )
        res = _run_cli(
            self.root,
            "tune",
            "--action",
            "create",
            "--repo-root",
            str(self.root),
            "--installation",
            INSTALLATION,
            "--harness",
            HARNESS,
            "--actor",
            ACTOR,
            "--project-id",
            PROJECT_ID,
            "--status",
            "awaiting_decision",
            "--data-file",
            str(data_file),
            "--json",
        )
        self.assertEqual(
            res.returncode,
            0,
            f"tune create failed (stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))
        report_path = Path(created["report_path"])
        self.assertTrue(report_path.exists(), "tune report file not written")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report.get("report_type"), "tune")
        self.assertEqual(report.get("proposals"), proposals)

        # Roundtrip: latest --type tune returns the created report.
        res_latest = _run_cli(
            self.root,
            "latest",
            "--repo-root",
            str(self.root),
            "--installation",
            INSTALLATION,
            "--type",
            "tune",
            "--json",
        )
        self.assertEqual(
            res_latest.returncode,
            0,
            f"latest --type tune failed: {res_latest.stdout!r} {res_latest.stderr!r}",
        )
        found = json.loads(res_latest.stdout)
        self.assertTrue(found.get("found"))
        self.assertEqual(found.get("run_id"), created["run_id"])

        # Verify action mirrors init/manage.
        res_verify = _run_cli(
            self.root,
            "tune",
            "--action",
            "verify",
            "--report",
            str(report_path),
            "--json",
        )
        self.assertEqual(res_verify.returncode, 0, res_verify.stdout + res_verify.stderr)
        self.assertTrue(json.loads(res_verify.stdout).get("valid"))


# ---------------------------------------------------------------------------
# TempDirTestCase (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TempDirTestCase(unittest.TestCase):
    """Each test gets a fresh temporary base directory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


# ---------------------------------------------------------------------------
# TestTR1UnsafeIdentifiersRefused (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TestTR1UnsafeIdentifiersRefused(TempDirTestCase):
    """SEC-3: identifiers that build report paths must be validated exactly
    like run_id. Attack reproduction: --installation "../../evil" escapes
    the reports directory and creates directories outside the repository."""

    def test_get_report_dir_refuses_traversal_and_separators(self):
        # RED (pre-fix): get_report_dir returns escape paths verbatim.
        for unsafe in ("../../evil", "..", "a/b", "a\\b", "", "../up"):
            with self.assertRaises(
                ValueError,
                msg=f"get_report_dir accepted unsafe installation_id {unsafe!r}",
            ):
                get_report_dir(self.base, unsafe, "init")

    def test_get_report_dir_accepts_normal_ids(self):
        # Lock-in: well-formed identifiers keep working.
        d = get_report_dir(self.base, "ag-main", "init")
        self.assertEqual(
            d, self.base / ".agents" / "reports" / "ag-main" / "init"
        )

    def test_cli_init_create_traversal_refused_zero_dirs_outside_repo(self):
        """Attack: init create with a hostile --installation must be refused
        and must create ZERO directories outside the repo root."""
        repo = self.base / "repo"
        repo.mkdir()
        # Valid scenario payload so the ONLY defect is the hostile
        # installation identifier (the refusal must come from the SEC-3
        # path check, not from earlier schema validation). The scenario
        # file lives INSIDE the repo: everything outside the repo root
        # must stay untouched.
        scenario_file = repo / "scenario.json"
        scenario_file.write_text(
            json.dumps({"profile": "active_development"}),
            encoding="utf-8",
        )
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "init",
            "--action", "create",
            "--repo-root", str(repo),
            "--installation", "../../evil",
            "--harness", "antigravity",
            "--actor", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id", "vlv-code/meta-project",
            "--status", "completed",
            "--scenario-file", str(scenario_file),
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        # 1. Refused (post-fix: save_report raises via validated
        #    get_report_dir -> rc 1 with a refusal message).
        self.assertNotEqual(
            proc.returncode, 0, "hostile --installation must be refused"
        )
        combined = proc.stdout + proc.stderr
        self.assertIn("refused", combined, "refusal must be explicit")
        # 2. ZERO directories created outside the repo (pre-fix:
        #    <base>/evil/init/<run_id>.json materializes).
        self.assertFalse(
            (self.base / "evil").exists(),
            "traversal created directories OUTSIDE the repository root",
        )
        outside = [p.name for p in self.base.iterdir() if p.name != "repo"]
        self.assertEqual(
            outside, [], f"artifacts escaped the repo root: {outside}"
        )
        # 3. Nothing written inside the repo either (refusal precedes mkdir).
        self.assertFalse(
            (repo / ".agents" / "reports").exists(),
            "refused run must not create report directories",
        )

    def test_cli_manage_create_unsafe_init_run_id_refused(self):
        """Attack: a crafted --init-run-id probes/reads outside the init
        report directory; must be refused before any path is built."""
        repo = self.base / "repo"
        repo.mkdir()
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "manage",
            "--action", "create",
            "--repo-root", str(repo),
            "--installation", "ag-main",
            "--harness", "antigravity",
            "--actor", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id", "vlv-code/meta-project",
            "--init-run-id", "../../evil",
            "--status", "completed",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "unsafe init_run_id must be refused")
        self.assertIn("Unsafe", proc.stderr, "refusal must name the unsafe identifier")
        self.assertNotIn("Traceback", proc.stderr, "refusal must be a clean error")

    def test_cli_manage_create_traversal_installation_refused(self):
        """Attack: hostile --installation in manage create probes the init
        report directory outside the repo; must be refused before intake."""
        repo = self.base / "repo"
        repo.mkdir()
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "manage",
            "--action", "create",
            "--repo-root", str(repo),
            "--installation", "../outside-installation",
            "--harness", "antigravity",
            "--actor", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id", "vlv-code/meta-project",
            "--init-run-id", "20261116T000000Z-cafe0001",
            "--status", "completed",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "unsafe installation must be refused")
        self.assertIn("Unsafe", proc.stderr, "refusal must name the unsafe identifier")
        self.assertNotIn("Traceback", proc.stderr, "refusal must be a clean error")
        self.assertFalse(
            (self.base / "outside-installation").exists(),
            "traversal must not create or read targets outside the repo",
        )

    def test_cli_latest_traversal_installation_refused_cleanly(self):
        """latest --installation "../x" must refuse cleanly (no traceback,
        explicit unsafe-identifier error)."""
        repo = self.base / "repo"
        repo.mkdir()
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "latest",
            "--repo-root", str(repo),
            "--installation", "../../evil",
            "--type", "init",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(
            proc.returncode, 2, f"unsafe installation must refuse with rc 2: {proc.stderr}"
        )
        self.assertIn("Unsafe", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr, "refusal must be a clean error")


# ---------------------------------------------------------------------------
# _RecordingRunner (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class _RecordingRunner:
    """subprocess.run stand-in that records argv, then delegates to the
    real implementation (used to prove whether git was invoked)."""

    def __init__(self):
        self.calls = []
        self._real = subprocess.run

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        return self._real(args, **kwargs)


# ---------------------------------------------------------------------------
# TestTR2CommitShaInjection (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TestTR2CommitShaInjection(TempDirTestCase):
    """M2: a report-controlled commit_sha reaching `git show` as an argv
    element that starts with "--" is an OPTION to git (argv injection
    class). Required: 40-hex validation BEFORE the subprocess."""

    def _committed_repo(self) -> Path:
        repo = _init_git_repo(self.base / "repo")
        (repo / REGISTRY_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / REGISTRY_REL).write_text(
            json.dumps({"project_id": "vlv-code/meta-project"}), encoding="utf-8"
        )
        _commit_all(repo)
        return repo

    def test_recover_registry_baseline_refuses_option_like_sha_without_git_call(self):
        repo = self._committed_repo()
        runner = _RecordingRunner()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", runner
        ):
            blob, err = _recover_registry_baseline(repo, "--upload-pack=evil")

        self.assertIsNone(blob, "injected commit_sha must not yield a baseline")
        self.assertIn("40", err, f"refusal must require a 40-char hex SHA: {err}")
        self.assertEqual(
            runner.calls,
            [],
            f"git must never be invoked with an option-like commit_sha; saw: {runner.calls}",
        )

    def test_recover_registry_baseline_refuses_short_non_hex_sha(self):
        repo = self._committed_repo()
        blob, err = _recover_registry_baseline(repo, "deadbeef")
        self.assertIsNone(blob)
        self.assertIn("40", err, f"refusal must require a 40-char hex SHA: {err}")

    def test_recover_registry_baseline_accepts_real_sha(self):
        # Lock-in: a genuine 40-hex SHA still recovers the committed blob.
        repo = self._committed_repo()
        sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        blob, err = _recover_registry_baseline(repo, sha)
        self.assertIsNone(err, err)
        self.assertIn("vlv-code/meta-project", blob.decode("utf-8"))

    def _delta_reaching_git_show(self, repo: Path, sha: str) -> dict:
        """A completed init report whose recorded registry fingerprint does
        NOT match the current registry (registry drifted after the report)
        and a valid declared change, so delta verification proceeds to the
        git baseline recovery (git show)."""
        report = _base_init_report(repo, "init-20261116T000000Z-inject01")
        report["git_state"]["commit_sha"] = sha
        fingerprints = collect_input_fingerprints(repo)
        fingerprints[REGISTRY_REL] = "0" * 64  # recorded != current -> delta path
        report["input_fingerprints"] = fingerprints
        return report

    def test_verify_delta_refuses_option_like_report_sha_without_git_call(self):
        repo = self._committed_repo()
        # Drift the registry after the report so the declared-delta path runs.
        (repo / REGISTRY_REL).write_text(
            json.dumps({"project_id": "vlv-code/meta-project", "drifted": True}),
            encoding="utf-8",
        )
        report = self._delta_reaching_git_show(repo, "--output=evil.txt")
        runner = _RecordingRunner()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", runner
        ):
            refusal = manage_reports.verify_declared_registry_delta(
                repo, report, [{"kind": "add_role", "role_id": "r1"}]
            )

        self.assertIsNotNone(refusal, "injected sha must refuse the delta")
        self.assertIn("40", refusal, f"refusal must require a 40-char hex SHA: {refusal}")
        self.assertEqual(
            runner.calls,
            [],
            f"git show must never run with an option-like commit_sha; saw: {runner.calls}",
        )

    def test_verify_delta_refuses_short_report_sha(self):
        repo = self._committed_repo()
        (repo / REGISTRY_REL).write_text(
            json.dumps({"project_id": "vlv-code/meta-project", "drifted": True}),
            encoding="utf-8",
        )
        report = self._delta_reaching_git_show(repo, "deadbeef")
        refusal = manage_reports.verify_declared_registry_delta(
            repo, report, [{"kind": "add_role", "role_id": "r1"}]
        )
        self.assertIsNotNone(refusal)
        self.assertIn("40", refusal, f"refusal must require a 40-char hex SHA: {refusal}")


# ---------------------------------------------------------------------------
# _FailingGit (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class _FailingGit:
    """subprocess.run stand-in simulating a dead/hijacked git binary."""

    def __init__(self, exc=None, returncode=1):
        self.exc = exc
        self.returncode = returncode

    def __call__(self, args, **kwargs):
        if self.exc is not None:
            raise self.exc
        return subprocess.CompletedProcess(
            args, self.returncode, stdout="", stderr="fatal: simulated git outage"
        )


# ---------------------------------------------------------------------------
# TestTR3GitStateFailClosed (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TestTR3GitStateFailClosed(TempDirTestCase):
    """M3: a git subprocess failure must produce an explicit
    git_state_error (never a silent clean/unknown state), and staleness
    must refuse to certify such reports as fresh (STALE_INPUT, reason
    'git state unavailable')."""

    def _repo_with_fresh_report(self) -> Path:
        repo = _init_git_repo(self.base / "repo")
        (repo / "AGENTS.md").write_text("# Passport\n", encoding="utf-8")
        _commit_all(repo)
        report = _base_init_report(repo, "init-20261116T010000Z-fresh001")
        save_report(repo, "ag-main", "init", report)
        return repo

    def test_get_git_state_reports_error_on_exception(self):
        repo = self._repo_with_fresh_report()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", _FailingGit(exc=OSError("git dead"))
        ):
            state = get_git_state(repo)
        self.assertTrue(
            state.get("git_state_error"),
            "git failure must surface an explicit git_state_error",
        )
        self.assertFalse(
            state.get("is_clean", True),
            "cleanliness must fail closed when git cannot be consulted",
        )
        self.assertEqual(state.get("commit_sha"), "unknown")

    def test_get_git_state_reports_error_on_nonzero_rc(self):
        repo = self._repo_with_fresh_report()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", _FailingGit(returncode=128)
        ):
            state = get_git_state(repo)
        self.assertTrue(state.get("git_state_error"))
        # All three git call sites feed the error state.
        self.assertIn("HEAD", state["git_state_error"])
        self.assertFalse(state.get("is_clean", True))

    def test_get_git_state_clean_when_git_works(self):
        # Lock-in: healthy git produces no error state.
        repo = self._repo_with_fresh_report()
        state = get_git_state(repo)
        self.assertIsNone(state.get("git_state_error"))
        self.assertEqual(len(state["commit_sha"]), 40)

    def test_staleness_refuses_fresh_verdict_when_current_git_fails(self):
        """Attack: dead git at staleness check time must NOT let the report
        pass as fresh."""
        repo = self._repo_with_fresh_report()
        report = _base_init_report(repo, "init-20261116T010000Z-fresh001")
        self.assertFalse(check_report_staleness(repo, report)[0])

        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", _FailingGit(exc=OSError("git dead"))
        ):
            is_stale, details = check_report_staleness(repo, report)

        self.assertTrue(
            is_stale,
            f"report admitted fresh while git state was unavailable: {details!r}",
        )
        self.assertTrue(
            any(
                r.startswith("git state unavailable") for r in details["reasons"]
            ),
            f"reason must be 'git state unavailable': {details['reasons']}",
        )

    def test_staleness_marks_reports_carrying_git_error_as_suspect(self):
        """Attack: a report created during a git outage records the failure;
        it must never be certified fresh."""
        repo = self._repo_with_fresh_report()
        report = _base_init_report(repo, "init-20261116T010000Z-outage01")
        report["git_state"]["commit_sha"] = "unknown"
        report["git_state"]["git_state_error"] = (
            "git rev-parse HEAD failed: simulated outage"
        )
        is_stale, details = check_report_staleness(repo, report)
        self.assertTrue(
            is_stale,
            f"report carrying git_state_error admitted as fresh: {details!r}",
        )
        self.assertTrue(
            any(
                r.startswith("git state unavailable") for r in details["reasons"]
            ),
            f"reason must be 'git state unavailable': {details['reasons']}",
        )

    def test_cli_latest_emits_stale_input_envelope_on_git_error(self):
        repo = self._repo_with_fresh_report()
        # A report created during a git outage (failure recorded).
        report = _base_init_report(repo, "init-20261116T010000Z-outage02")
        report["git_state"]["commit_sha"] = "unknown"
        report["git_state"]["git_state_error"] = "simulated outage"
        save_report(repo, "ag-main", "init", report)

        out, err = __import__("io").StringIO(), __import__("io").StringIO()
        with __import__("contextlib").redirect_stdout(out), \
                __import__("contextlib").redirect_stderr(err):
            with unittest.mock.patch(
                "sys.argv",
                [
                    "manage_reports.py",
                    "latest",
                    "--repo-root", str(repo),
                    "--installation", "ag-main",
                    "--type", "init",
                    "--json",
                ],
            ):
                rc = manage_reports.main()

        self.assertEqual(rc, 0, "envelope is presentation-only; rc unchanged")
        payload = json.loads(out.getvalue())
        self.assertTrue(
            payload.get("is_stale"),
            f"report NOT admitted fresh: {payload}",
        )
        self.assertTrue(
            any(
                r.startswith("git state unavailable")
                for r in payload.get("staleness_reasons", [])
            ),
            f"staleness reason must be 'git state unavailable': {payload}",
        )
        self.assertIn("STALE_INPUT", err.getvalue(), "STALE_INPUT envelope required")
        self.assertIn("git state unavailable", err.getvalue())


# ---------------------------------------------------------------------------
# TestTR4DeterministicLatestAndExclusiveSave (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TestTR4DeterministicLatestAndExclusiveSave(TempDirTestCase):
    """M4: two same-second runs must resolve 'latest' deterministically by
    creation order (chosen design: fallback resolution by mtime with the
    run_id name as final tiebreak — see find_latest_report). M5: a second
    writer with the same run_id must fail LOUDLY, even when it raced past
    its exists() check before the first writer published."""

    def _same_second_ids(self):
        # Name order (ffff... > aaaa...) deliberately contradicts write order.
        return (
            "init-20261116T120000Z-ffff0001",  # written FIRST, greater name
            "init-20261116T120000Z-aaaa0002",  # written SECOND, smaller name
        )

    def _save(self, repo: Path, run_id: str, marker: str) -> Path:
        report = _base_init_report(repo, run_id)
        report["race_marker"] = marker
        return save_report(repo, "ag-main", "init", report)

    def test_same_second_latest_resolves_by_write_order(self):
        repo = self.base / "repo"
        repo.mkdir()
        first_id, second_id = self._same_second_ids()
        first_file = self._save(repo, first_id, "first")
        second_file = self._save(repo, second_id, "second")

        # Force unambiguous creation-order mtimes (filesystem independence).
        os.utime(first_file, ns=(1_000_000_000, 1_000_000_000))
        os.utime(second_file, ns=(2_000_000_000, 2_000_000_000))

        # Attack surface: the fallback path (no latest.json pointer).
        (repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json").unlink()

        path, data = find_latest_report(repo, "ag-main", "init")
        self.assertIsNotNone(path)
        self.assertEqual(
            data.get("run_id"),
            second_id,
            "same-second latest must resolve to the LAST-WRITTEN run "
            "(mtime with name tiebreak), not the lexicographically "
            "greatest run_id",
        )
        # Determinism: the resolution is stable across repeated calls.
        for _ in range(3):
            path2, data2 = find_latest_report(repo, "ag-main", "init")
            self.assertEqual(path2, path)
            self.assertEqual(data2.get("run_id"), second_id)

    def test_same_second_latest_reverse_mtime_is_deterministic(self):
        repo = self.base / "repo"
        repo.mkdir()
        first_id, second_id = self._same_second_ids()
        first_file = self._save(repo, first_id, "first")
        second_file = self._save(repo, second_id, "second")
        os.utime(first_file, ns=(5_000_000_000, 5_000_000_000))
        os.utime(second_file, ns=(1_000_000_000, 1_000_000_000))
        (repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json").unlink()

        _, data = find_latest_report(repo, "ag-main", "init")
        self.assertEqual(data.get("run_id"), first_id)

    def test_pointer_still_authoritative_over_mtime(self):
        # Lock-in: an intact latest.json pointer wins regardless of mtimes.
        repo = self.base / "repo"
        repo.mkdir()
        first_id, second_id = self._same_second_ids()
        self._save(repo, first_id, "first")
        pointer = (
            repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json"
        )
        second_file = self._save(repo, second_id, "second")
        # Newer mtime on the OLDER run; the pointer still names the newest run.
        os.utime(
            repo / ".agents" / "reports" / "ag-main" / "init" / f"{first_id}.json",
            ns=(9_000_000_000, 9_000_000_000),
        )
        del pointer, second_file
        _, data = find_latest_report(repo, "ag-main", "init")
        self.assertEqual(data.get("run_id"), second_id)

    def test_racing_same_run_id_writer_fails_loudly_content_intact(self):
        """M5 attack: writer B's exists() check races BEFORE writer A's
        publish (simulated deterministically by lying exists()); without an
        atomic reservation B silently clobbers A's report. Required: the
        second writer fails loudly and A's content survives untouched."""
        repo = self.base / "repo"
        repo.mkdir()
        run_id = "init-20261116T130000Z-race0001"
        target = (
            repo / ".agents" / "reports" / "ag-main" / "init" / f"{run_id}.json"
        )
        self._save(repo, run_id, "writer-A")

        real_exists = type(target).exists
        target_resolved = str(target)

        def lying_exists(path_self):
            # Simulate writer B having checked exists() BEFORE A published.
            if str(path_self) == target_resolved:
                return False
            return real_exists(path_self)

        with unittest.mock.patch.object(
            type(target), "exists", lying_exists
        ):
            with self.assertRaises(
                ValueError,
                msg="second same-run_id writer must fail loudly even after "
                "racing past the exists() check",
            ):
                self._save(repo, run_id, "writer-B")

        # Writer A's content is intact — no silent clobber.
        with open(target, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(
            saved.get("race_marker"),
            "writer-A",
            "the racing writer silently overwrote the first writer's report",
        )

    def test_threaded_same_run_id_exactly_one_winner(self):
        """M5 stress: N concurrent writers with the same run_id — exactly
        one wins, the stored content belongs to that single winner, and the
        pointer agrees."""
        repo = self.base / "repo"
        repo.mkdir()
        run_id = "init-20261116T130000Z-thread01"
        results = {}
        errors = {}
        barrier = threading.Barrier(5)

        def writer(idx: int):
            try:
                barrier.wait()
                report = _base_init_report(repo, run_id)
                report["race_marker"] = f"thread-{idx}"
                save_report(repo, "ag-main", "init", report)
                results[idx] = f"thread-{idx}"
            except Exception as exc:  # noqa: BLE001 — losers must raise loudly
                errors[idx] = exc

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(
            len(results), 1, f"exactly one writer must win: {results}"
        )
        self.assertGreaterEqual(
            len(errors), 4, f"losing writers must fail loudly: {errors}"
        )
        target = (
            repo / ".agents" / "reports" / "ag-main" / "init" / f"{run_id}.json"
        )
        with open(target, "r", encoding="utf-8") as f:
            saved = json.load(f)
        winner_marker = next(iter(results.values()))
        self.assertEqual(saved.get("race_marker"), winner_marker)
        with open(
            repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json",
            "r",
            encoding="utf-8",
        ) as f:
            pointer = json.load(f)
        self.assertEqual(pointer.get("run_id"), run_id)


# ---------------------------------------------------------------------------
# TestTR5FingerprintsRequired (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TestTR5FingerprintsRequired(TempDirTestCase):
    """M6: completed init/manage reports must carry input_fingerprints.
    Contract (documented): STRICT for new reports (validate_report default,
    verify CLI, save_report, intake); legacy completed reports without
    fingerprints remain READABLE via the report directory resolution path
    (_load_valid_report / find_latest_report) for staleness/supersession;
    update/tune are unaffected this lane."""

    def test_completed_init_without_fingerprints_is_invalid(self):
        repo = self.base / "repo"
        repo.mkdir()
        report = _base_init_report(repo, "init-20261116T140000Z-nofps001")
        report.pop("input_fingerprints")
        errors = validate_report(report, expected_type="init")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"completed init report without fingerprints must be INVALID: {errors}",
        )

    def test_completed_manage_without_fingerprints_is_invalid(self):
        repo = self.base / "repo"
        repo.mkdir()
        report = create_manage_report(
            repo_root=repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            init_run_id="init-20261116T140000Z-nofps001",
            status="completed",
            scenario={"profile": "active_development"},
            roles={"preserved": [], "created": [], "adapted": [], "archived": []},
            bindings={},
        )
        report.pop("input_fingerprints")
        errors = validate_report(report, expected_type="manage")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"completed manage report without fingerprints must be INVALID: {errors}",
        )

    def test_fingerprint_entry_shape_is_enforced(self):
        repo = self.base / "repo"
        repo.mkdir()
        report = _base_init_report(repo, "init-20261116T140000Z-shape01")
        # Missing essential keys.
        report["input_fingerprints"] = {"custom/thing.md": "a" * 64}
        errors = validate_report(report, expected_type="init")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"fingerprints missing essential inputs must be invalid: {errors}",
        )
        # Non-hex / wrong-length values are refused.
        report["input_fingerprints"] = {
            rel: ("z" * 64 if rel == ESSENTIAL_INPUT_PATHS[0] else "b" * 64)
            for rel in ESSENTIAL_INPUT_PATHS
        }
        errors = validate_report(report, expected_type="init")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"non-sha256 fingerprint values must be invalid: {errors}",
        )

    def test_noncompleted_reports_without_fingerprints_stay_valid(self):
        """Decision ledger reports (blocked/awaiting) are not 'completed'
        and remain valid without fingerprints."""
        repo = self.base / "repo"
        repo.mkdir()
        for status in ("blocked", "awaiting_decision"):
            report = _base_init_report(repo, f"init-20261116T140000Z-{status[:4]}1", status=status)
            report.pop("input_fingerprints")
            errors = validate_report(report, expected_type="init")
            self.assertEqual(
                errors, [], f"{status} init report must stay valid: {errors}"
            )

    def test_completed_update_and_tune_unaffected(self):
        """Lock-in: the fingerprint requirement does not extend to
        update/tune reports this lane."""
        with open(
            REPO_ROOT / "templates" / "reports" / "update_report.json",
            "r",
            encoding="utf-8",
        ) as f:
            update_report = json.load(f)
        update_report.pop("input_fingerprints")
        self.assertEqual(
            validate_report(update_report, expected_type="update"), []
        )

    def test_cli_verify_rejects_completed_init_without_fingerprints(self):
        """Attack surface: `verify` must answer INVALID_REPORT (envelope,
        rc 1) for a completed init report without fingerprints."""
        repo = self.base / "repo"
        repo.mkdir()
        report = _base_init_report(repo, "init-20261116T140000Z-cliprobe01")
        report.pop("input_fingerprints")
        report_file = repo / "report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        out, err = __import__("io").StringIO(), __import__("io").StringIO()
        with __import__("contextlib").redirect_stdout(out), \
                __import__("contextlib").redirect_stderr(err):
            with unittest.mock.patch(
                "sys.argv",
                [
                    "manage_reports.py",
                    "verify",
                    "--report", str(report_file),
                    "--type", "init",
                    "--json",
                ],
            ):
                rc = manage_reports.main()

        self.assertEqual(
            rc, 1, f"completed init report without fingerprints must fail: {out.getvalue()}"
        )
        self.assertIn("INVALID_REPORT", err.getvalue(), "envelope required")
        payload = json.loads(out.getvalue())
        self.assertFalse(payload.get("valid"))
        self.assertTrue(
            any("input_fingerprints" in e for e in payload.get("errors", []))
        )

    def test_legacy_completed_report_remains_readable(self):
        """Backward-compat (documented decision): a legacy completed report
        without fingerprints is still READABLE via the report directory
        resolution path (find_latest_report), so supersession/staleness
        logic keeps working — it is just not VALID as a new document."""
        repo = self.base / "repo"
        repo.mkdir()
        report_dir = repo / ".agents" / "reports" / "ag-main" / "init"
        report_dir.mkdir(parents=True)
        report = _base_init_report(repo, "init-20261116T140000Z-legacy01")
        report.pop("input_fingerprints")
        legacy_file = report_dir / "init-20261116T140000Z-legacy01.json"
        with open(legacy_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        path, data = find_latest_report(repo, "ag-main", "init")
        self.assertEqual(path, legacy_file)
        self.assertIsNotNone(
            data, "legacy completed report must remain readable (not 'corrupted')"
        )
        self.assertEqual(data.get("run_id"), "init-20261116T140000Z-legacy01")

    def test_templates_carry_valid_input_fingerprints(self):
        """The canonical init/manage templates define the contract: they
        must carry valid, filled input_fingerprints examples and pass the
        strict validator."""
        for name, expected_type in (
            ("init_report.json", "init"),
            ("manage_report.json", "manage"),
        ):
            template_path = REPO_ROOT / "templates" / "reports" / name
            with open(template_path, "r", encoding="utf-8") as f:
                template = json.load(f)
            self.assertIn(
                "input_fingerprints",
                template,
                f"{name} must define input_fingerprints",
            )
            fps = template["input_fingerprints"]
            self.assertIsInstance(fps, dict)
            for rel in ESSENTIAL_INPUT_PATHS:
                self.assertIn(rel, fps, f"{name} must fingerprint {rel}")
                value = fps[rel]
                self.assertIsInstance(value, str)
                self.assertRegex(value, r"^[0-9a-f]{64}$")
            errors = validate_report(template, expected_type=expected_type)
            self.assertEqual(
                errors, [], f"{name} must pass strict validation: {errors}"
            )


# ---------------------------------------------------------------------------
# TestTR6RenameParsingAndSchemaExactSet (from tests/test_fwave_r.py)
# ---------------------------------------------------------------------------
class TestTR6RenameParsingAndSchemaExactSet(TempDirTestCase):
    """M9: `git status --porcelain -z` rename entries are 'XY NEW\\0OLD\\0'
    (the non-z form is 'R old -> new'); modified_files must record the NEW
    working-tree path and never the sliced garbage of the ORIG_PATH field.
    M10: schema_version must be an exact member of the supported set."""

    def test_porcelain_rename_parsed_to_new_path(self):
        repo = _init_git_repo(self.base / "repo")
        (repo / "dir").mkdir()
        (repo / "dir" / "oldname.txt").write_text("payload\n", encoding="utf-8")
        _commit_all(repo)
        res = _git(repo, "mv", "dir/oldname.txt", "dir/newname.txt")
        self.assertEqual(res.returncode, 0, res.stderr)

        state = get_git_state(repo)
        self.assertEqual(
            state["modified_files"],
            ["dir/newname.txt"],
            f"rename must parse to the NEW path only, got: {state['modified_files']!r} "
            "(pre-fix bug: the ORIG_PATH field is sliced as 'XY PATH' and lands "
            "in modified_files as garbage)",
        )
        self.assertFalse(state["is_clean"])

    def test_rename_of_essential_input_is_visible_to_staleness(self):
        """A renamed essential input must be detectable: the fingerprint of
        the old path no longer matches (file gone) AND the new path appears
        in modified_files."""
        repo = _init_git_repo(self.base / "repo")
        (repo / "AGENTS.md").write_text("# Passport\n", encoding="utf-8")
        _commit_all(repo)
        report = _base_init_report(repo, "init-20261116T150000Z-renme001")
        self.assertFalse(check_report_staleness(repo, report)[0])

        _git(repo, "mv", "AGENTS.md", "AGENTS.v2.md")
        state = get_git_state(repo)
        self.assertIn("AGENTS.v2.md", state["modified_files"])
        self.assertNotIn("AGENTS.md", state["modified_files"])
        is_stale, details = check_report_staleness(repo, report)
        self.assertTrue(
            is_stale,
            f"renamed essential input must make the report stale: {details!r}",
        )

    def test_schema_version_exact_set_membership(self):
        report_base = {
            "schema_version": "1.0.0",
            "report_type": "init",
            "project_id": "p",
            "installation_id": "ag-main",
            "harness_id": "antigravity",
            "actor_id": "a",
            "run_id": "r",
            "status": "blocked",
            "git_state": {},
            "scenario": {},
            "next_step_readiness": {},
        }

        def with_schema(version: str) -> dict:
            data = dict(report_base)
            data["schema_version"] = version
            return data

        # M10 attack: the old check accepted ANY "1.*" via major-prefix
        # matching, so "1.9.9" sailed through.
        for bad in ("1.9.9", "1", "1.999.0", "0.9", "2.0", "1.2"):
            errors = validate_report(with_schema(bad), expected_type="init")
            self.assertTrue(
                any("schema_version" in e for e in errors),
                f"schema_version {bad!r} must be refused (exact set), got: {errors}",
            )

        for good in ("1.0", "1.1", "1.0.0", "1.1.0"):
            errors = validate_report(with_schema(good), expected_type="init")
            self.assertEqual(
                errors, [], f"schema_version {good!r} must stay valid: {errors}"
            )

    def test_supported_schema_versions_is_exact_enumeration(self):
        self.assertEqual(
            SUPPORTED_SCHEMA_VERSIONS,
            {"1.0", "1.1", "1.0.0", "1.1.0"},
            "SUPPORTED_SCHEMA_VERSIONS must be the exact major.minor "
            "enumeration (plan T-R6), not the legacy {'1.0.0','1.0','1'}",
        )


# ---------------------------------------------------------------------------
# TestSetOrchestrationDelta (from tests/test_jwave_m.py)
# ---------------------------------------------------------------------------
class TestSetOrchestrationDelta(unittest.TestCase):
    """Part D: the set_orchestration intake vocabulary."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="jwave_m_")
        self.root = Path(self.temp_dir).resolve()
        self._seed_repo()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- fixture helpers ---------------------------------------------------

    def _seed_repo(self, roles=None, orchestration=ABSENT):
        root = self.root
        (root / "AGENTS.md").write_text(AGENTS_MD, encoding="utf-8")
        (root / BOUNDARIES_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / BOUNDARIES_REL).write_text(BOUNDARIES_MD, encoding="utf-8")
        self._write_registry(roles if roles is not None else DEFAULT_ROLES, orchestration)
        profile = root / ".agents" / "team" / "agent-dev-lead" / "profile.md"
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Dev Lead"\n'
            'role_id: "agent-dev-lead"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{ACTOR}"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "fixture@example.com")
        _git(root, "config", "user.name", "Fixture")
        _git(root, "add", "-A")
        _git(root, "commit", "-qm", "fixture: committed registry baseline")

    def _write_registry(self, roles: dict, orchestration) -> dict:
        installation = {
            "harness_id": HARNESS,
            "status": "active",
            "description": "fixture installation",
        }
        if orchestration is not ABSENT:
            installation["orchestration"] = orchestration
        registry = {
            "schema_version": "1.1.0",
            "project_id": PROJECT_ID,
            "installations": {INSTALLATION: installation},
            "roles": roles,
        }
        _write_json(self.root / REGISTRY_REL, registry)
        return registry

    def _current_registry(self) -> dict:
        return json.loads(
            (self.root / REGISTRY_REL).read_text(encoding="utf-8")
        )

    def _save_registry(self, registry: dict) -> None:
        """Simulate the manage operation mutating the registry on disk."""
        _write_json(self.root / REGISTRY_REL, registry)

    def _add_registry_role(self, registry: dict, role_id: str) -> dict:
        registry = json.loads(json.dumps(registry))
        registry["roles"][role_id] = _role_entry(role_id)
        return registry

    def _set_orchestration(self, registry: dict, orchestration) -> dict:
        registry = json.loads(json.dumps(registry))
        installation = registry["installations"][INSTALLATION]
        if orchestration is ABSENT:
            installation.pop("orchestration", None)
        else:
            installation["orchestration"] = orchestration
        return registry

    def _save_init_report(self, run_id: str) -> dict:
        from scripts.manage_reports import create_init_report, save_report

        report = create_init_report(
            repo_root=self.root,
            installation_id=INSTALLATION,
            harness_id=HARNESS,
            actor_id=ACTOR,
            project_id=PROJECT_ID,
            status="completed",
            scenario={
                "profile": "active_development",
                "collaboration_model": "duo",
                "verification_policy": "duo_peer_review",
            },
            run_id=run_id,
        )
        save_report(self.root, INSTALLATION, "init", report)
        return report

    def _manage_create(
        self,
        init_run_id: str,
        changes=None,
        tag: str = "data",
    ) -> subprocess.CompletedProcess:
        payload = {
            "scenario": {
                "profile": "active_development",
                "collaboration_model": "duo",
            },
            "roles": {
                "preserved": ["agent-dev-lead"],
                "created": [],
                "adapted": [],
                "archived": [],
            },
            "bindings": {},
        }
        if changes is not None:
            payload["changes"] = changes
        data_file = _write_json(self.root / f"manage_{tag}.json", payload)
        return _run_cli(
            self.root,
            "manage",
            "--action",
            "create",
            "--repo-root",
            str(self.root),
            "--installation",
            INSTALLATION,
            "--harness",
            HARNESS,
            "--actor",
            ACTOR,
            "--init-run-id",
            init_run_id,
            "--status",
            "completed",
            "--data-file",
            str(data_file),
            "--json",
        )

    # -- tests ---------------------------------------------------------------

    def test_orchestration_only_change_with_declaration_admitted(self):
        """Test 22: an orchestration-only registry change declared via
        {"kind": "set_orchestration", "installation": "t9"} must be
        admitted (today: refused as an unsupported kind)."""
        run_id = "init-20261123T000000Z-aaa00001"
        self._save_init_report(run_id)
        self._save_registry(self._set_orchestration(self._current_registry(), DECLARED_BLOCK))
        changes = [{"kind": "set_orchestration", "installation": INSTALLATION}]
        res = self._manage_create(run_id, changes=changes, tag="orch_admitted")
        self.assertEqual(
            res.returncode,
            0,
            f"declared set_orchestration delta refused by intake "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))

    def test_orchestration_only_change_without_declaration_refused(self):
        """Test 23 (lock-in): an orchestration-only registry change with no
        declaration must still be refused as stale."""
        run_id = "init-20261123T000000Z-bbb00002"
        self._save_init_report(run_id)
        self._save_registry(self._set_orchestration(self._current_registry(), DECLARED_BLOCK))
        res = self._manage_create(run_id, tag="orch_undeclared")
        self.assertNotEqual(
            res.returncode,
            0,
            f"undeclared registry change admitted: {res.stdout!r}",
        )
        combined = (res.stdout + res.stderr).lower()
        self.assertTrue(
            "stale" in combined or "declare" in combined,
            f"refusal must present as stale/undeclared delta: {combined!r}",
        )

    def test_undeclared_orchestration_change_alongside_declared_role_refused(self):
        """Test 24 (adversarial): an UNDECLARED orchestration change made
        alongside a correctly declared add_role must be refused with the
        refusal naming set_orchestration and the installation (today: the
        orchestration change is admitted silently)."""
        run_id = "init-20261123T000000Z-ccc00003"
        self._save_init_report(run_id)
        registry = self._current_registry()
        registry = self._add_registry_role(registry, "agent-quality-guardian")
        registry = self._set_orchestration(registry, DECLARED_BLOCK)
        self._save_registry(registry)
        profile = (
            self.root / ".agents" / "team" / "agent-quality-guardian" / "profile.md"
        )
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Quality Guardian"\n'
            'role_id: "agent-quality-guardian"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-quality-guardian"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
            }
        ]
        res = self._manage_create(run_id, changes=changes, tag="orch_hidden")
        self.assertNotEqual(
            res.returncode,
            0,
            f"undeclared orchestration change admitted silently alongside a "
            f"declared role change: {res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            "set_orchestration",
            combined,
            f"refusal must name the set_orchestration delta element: {combined!r}",
        )
        self.assertIn(
            INSTALLATION,
            combined,
            f"refusal must name the installation: {combined!r}",
        )

    def test_declared_set_orchestration_without_matching_delta_refused(self):
        """Test 25: a declared set_orchestration with NO actual orchestration
        change must be refused as a declaration without a matching delta,
        even when the role part is correctly declared."""
        run_id = "init-20261123T000000Z-ddd00004"
        self._save_init_report(run_id)
        registry = self._current_registry()
        registry = self._add_registry_role(registry, "agent-quality-guardian")
        self._save_registry(registry)
        profile = (
            self.root / ".agents" / "team" / "agent-quality-guardian" / "profile.md"
        )
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Quality Guardian"\n'
            'role_id: "agent-quality-guardian"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-quality-guardian"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
            },
            {"kind": "set_orchestration", "installation": INSTALLATION},
        ]
        res = self._manage_create(run_id, changes=changes, tag="orch_unmatched")
        self.assertNotEqual(
            res.returncode,
            0,
            f"declaration without a matching registry delta admitted: "
            f"{res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            "no matching registry delta",
            combined,
            f"refusal must classify set_orchestration as unmatched "
            f"declaration: {combined!r}",
        )
        self.assertIn("set_orchestration", combined)

    def test_invalid_set_orchestration_declarations_refused(self):
        """Test 26 (adversarial): set_orchestration must not carry role_id
        or path, and requires the installation field."""
        run_id = "init-20261123T000000Z-eee00005"
        self._save_init_report(run_id)
        # Make the registry actually differ so declaration normalization
        # runs (an unchanged registry short-circuits before validation).
        self._save_registry(self._set_orchestration(self._current_registry(), DECLARED_BLOCK))

        cases = [
            (
                {"kind": "set_orchestration", "role_id": "agent-x", "installation": INSTALLATION},
                "must not carry role_id",
            ),
            (
                {"kind": "set_orchestration"},
                "installation is required for kind 'set_orchestration'",
            ),
            (
                {"kind": "set_orchestration", "installation": INSTALLATION, "path": "x.md"},
                "must not carry path",
            ),
        ]
        for idx, (declared, expected_problem) in enumerate(cases):
            with self.subTest(case=idx):
                res = self._manage_create(
                    run_id, changes=[declared], tag=f"orch_invalid_{idx}"
                )
                self.assertNotEqual(
                    res.returncode,
                    0,
                    f"invalid declaration admitted: {res.stdout!r}",
                )
                combined = res.stdout + res.stderr
                self.assertIn(
                    "invalid changes[] declaration",
                    combined,
                    f"refusal must classify the declaration as invalid: {combined!r}",
                )
                self.assertIn(
                    expected_problem,
                    combined,
                    f"refusal must carry the exact problem message "
                    f"{expected_problem!r}: {combined!r}",
                )

    def test_removing_block_is_set_orchestration_delta(self):
        """Test 27: removing an existing orchestration block (block -> key
        absent) is a set_orchestration delta and admits when declared."""
        run_id = "init-20261123T000000Z-fff00006"
        self._seed_repo(orchestration=DECLARED_BLOCK)
        self._save_init_report(run_id)
        self._save_registry(self._set_orchestration(self._current_registry(), ABSENT))
        changes = [{"kind": "set_orchestration", "installation": INSTALLATION}]
        res = self._manage_create(run_id, changes=changes, tag="orch_removal")
        self.assertEqual(
            res.returncode,
            0,
            f"declared block-removal delta refused by intake "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))

    def test_unchanged_roles_and_orchestration_admitted_without_declarations(self):
        """Test 28 (lock-in): a registry whose roles AND orchestration are
        unchanged since the init report is admitted without declarations."""
        run_id = "init-20261123T000000Z-ggg00007"
        self._seed_repo(orchestration=DECLARED_BLOCK)
        self._save_init_report(run_id)
        res = self._manage_create(run_id, tag="orch_untouched")
        self.assertEqual(
            res.returncode,
            0,
            f"unchanged registry refused (false positive): "
            f"stdout={res.stdout!r}, stderr={res.stderr!r}",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))


# ---------------------------------------------------------------------------
# TestRoleDutyDeconfliction (from tests/test_lwave_deconfliction.py)
# ---------------------------------------------------------------------------
class TestRoleDutyDeconfliction(unittest.TestCase):
    """Test detect_role_duty_conflicts and apply_duty_reconciliation."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_deconflict_"))
        self.agents_dir = self.temp_dir / ".agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.team_dir = self.agents_dir / "team"
        self.team_dir.mkdir(parents=True, exist_ok=True)

        # Create mock meta-project.json
        self.registry_data = {
            "schema_version": "1.1.0",
            "project_id": "test-repo",
            "installations": {
                "inst-a": {"harness_id": "harness-a", "status": "active"},
                "inst-b": {"harness_id": "harness-b", "status": "active"},
            },
            "roles": {
                "agent-worker": {
                    "description": "General Worker",
                    "bindings": {
                        "inst-a": {
                            "actor_id": "test-repo::harness-a::inst-a::agent-worker",
                            "status": "active",
                            "profile_path": ".agents/team/agent-worker/profile.md",
                        },
                        "inst-b": {
                            "actor_id": "test-repo::harness-b::inst-b::agent-worker",
                            "status": "active",
                            "profile_path": ".agents/team/agent-worker/profile.md",
                        },
                    },
                },
                "agent-dev-lead": {
                    "description": "Lead Developer",
                    "bindings": {
                        "inst-a": {
                            "actor_id": "test-repo::harness-a::inst-a::agent-dev-lead",
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        }
                    },
                },
            },
        }
        (self.agents_dir / "meta-project.json").write_text(
            json.dumps(self.registry_data, indent=2), encoding="utf-8"
        )

        # Create profile for agent-worker
        worker_dir = self.team_dir / "agent-worker"
        worker_dir.mkdir(parents=True, exist_ok=True)
        self.worker_profile = worker_dir / "profile.md"
        self.worker_profile.write_text(
            "---\n"
            "name: General Worker\n"
            "role_id: agent-worker\n"
            "harness_id: harness-a\n"
            "installation_id: inst-a\n"
            "actor_id: test-repo::harness-a::inst-a::agent-worker\n"
            "description: General tasks.\n"
            "tools:\n  - read_file\n"
            "model: inherit\n"
            "invocation_triggers:\n"
            '  - "general task"\n'
            '  - "plan task"\n'
            '  - "decompose request"\n'
            "---\n\n"
            "# Agent Role Passport: General Worker\n\n"
            "## 1. Purpose and Scope of Responsibility\n"
            "- **Role Identifier (`role_id`):** `agent-worker`\n"
            '- **Product Scope:** General execution.\n'
            '- **User Invocation Triggers:** "general task", "plan task", "decompose request".\n\n'
            "## 2. Connected Skills Stack\n"
            "- `clean-code` — standards.\n\n"
            "## 3. Authority and Boundaries Matrix\n"
            "- **Green Zone (autonomous):** work.\n\n"
            "## 4. Systemic Behavioral Invariants\n"
            "1. Invariant.\n\n"
            "## 5. Role Invocation Log (Telemetry)\n"
            "| Date | Initiator | Actor ID | Task / Invocation | Status / Result |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| 2026-11-20 | User | test-repo::harness-a::inst-a::agent-worker | Init | OK |\n",
            encoding="utf-8",
        )
        self.worker_notes = worker_dir / "notes.md"
        self.worker_notes.write_text("# Worker Private Notes\nKeep safe.\n", encoding="utf-8")

        # Create profile for agent-dev-lead
        dev_dir = self.team_dir / "agent-dev-lead"
        dev_dir.mkdir(parents=True, exist_ok=True)
        self.dev_profile = dev_dir / "profile.md"
        self.dev_profile.write_text(
            "---\n"
            "name: Lead Developer\n"
            "role_id: agent-dev-lead\n"
            "harness_id: harness-a\n"
            "installation_id: inst-a\n"
            "actor_id: test-repo::harness-a::inst-a::agent-dev-lead\n"
            "description: Feature execution.\n"
            "tools:\n  - read_file\n"
            "model: inherit\n"
            "invocation_triggers:\n"
            '  - "implement feature"\n'
            '  - "write script"\n'
            "---\n\n"
            "# Agent Role Passport: Lead Developer\n\n"
            "## 1. Purpose and Scope of Responsibility\n"
            "- **User Invocation Triggers:** \"implement feature\", \"write script\".\n",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_no_conflicts_when_triggers_disjoint(self):
        self.assertIsNotNone(detect_role_duty_conflicts, "detect_role_duty_conflicts not defined")
        res = detect_role_duty_conflicts(
            repo_root=self.temp_dir,
            target_installation="inst-a",
            new_role_id="agent-qa-engineer",
            new_triggers=["run tests", "verify validation"],
        )
        self.assertFalse(res["conflicts_detected"])
        self.assertEqual(len(res["conflicts"]), 0)
        self.assertEqual(res["duty_reconciliation"], {})

    def test_detect_conflicts_and_form_reconciliation_delta(self):
        self.assertIsNotNone(detect_role_duty_conflicts, "detect_role_duty_conflicts not defined")
        # Adding agent-intake-dispatcher which takes over "plan task" and "decompose request"
        res = detect_role_duty_conflicts(
            repo_root=self.temp_dir,
            target_installation="inst-a",
            new_role_id="agent-intake-dispatcher",
            new_triggers=["plan task", "decompose request", "intake", "route task"],
        )
        self.assertTrue(res["conflicts_detected"])
        self.assertEqual(len(res["conflicts"]), 1)
        conflict = res["conflicts"][0]
        self.assertEqual(conflict["role_id"], "agent-worker")
        self.assertEqual(
            sorted(conflict["overlapping_triggers"]),
            ["decompose request", "plan task"],
        )
        self.assertEqual(conflict["retained_triggers"], ["general task"])

        # Check duty_reconciliation structure
        recon = res["duty_reconciliation"]
        self.assertIn("agent-worker", recon)
        self.assertEqual(recon["agent-worker"]["retained_triggers"], ["general task"])
        self.assertEqual(
            sorted(recon["agent-worker"]["remove_triggers"]),
            ["decompose request", "plan task"],
        )

    def test_apply_duty_reconciliation_updates_profile_cleanly(self):
        self.assertIsNotNone(apply_duty_reconciliation, "apply_duty_reconciliation not defined")
        res = detect_role_duty_conflicts(
            repo_root=self.temp_dir,
            target_installation="inst-a",
            new_role_id="agent-intake-dispatcher",
            new_triggers=["plan task", "decompose request"],
        )
        updated_paths = apply_duty_reconciliation(self.temp_dir, res["duty_reconciliation"])
        self.assertEqual(len(updated_paths), 1)

        # Verify updated profile content
        updated_text = self.worker_profile.read_text(encoding="utf-8")
        # Frontmatter updated
        self.assertIn('  - "general task"', updated_text)
        self.assertNotIn('  - "plan task"', updated_text)
        self.assertNotIn('  - "decompose request"', updated_text)

        # Section 1 User Invocation Triggers updated
        self.assertIn('- **User Invocation Triggers:** "general task".', updated_text)
        self.assertNotIn('"plan task"', updated_text)

        # Section 5 Telemetry must be completely preserved!
        self.assertIn("2026-11-20 | User | test-repo::harness-a::inst-a::agent-worker | Init | OK", updated_text)

        # Notes.md must be untouched
        self.assertEqual(self.worker_notes.read_text(encoding="utf-8"), "# Worker Private Notes\nKeep safe.\n")

    def test_cli_deconflict_subcommand(self):
        # Test CLI integration: python scripts/manage_reports.py deconflict ...
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "manage_reports.py"),
            "deconflict",
            "--repo-root",
            str(self.temp_dir),
            "--installation",
            "inst-a",
            "--new-role",
            "agent-intake-dispatcher",
            "--new-triggers",
            "plan task",
            "decompose request",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"CLI error: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertTrue(data["conflicts_detected"])
        self.assertEqual(len(data["conflicts"]), 1)
        self.assertEqual(data["conflicts"][0]["role_id"], "agent-worker")

        # Test CLI with --apply
        cmd_apply = cmd + ["--apply"]
        proc_apply = subprocess.run(cmd_apply, capture_output=True, text=True)
        self.assertEqual(proc_apply.returncode, 0, f"CLI --apply error: {proc_apply.stderr}")

        updated_text = self.worker_profile.read_text(encoding="utf-8")
        self.assertNotIn('  - "plan task"', updated_text)


if __name__ == "__main__":
    unittest.main()
