#!/usr/bin/env python3
"""
Unit and Adversarial Test Suite for Report Engine (scripts/manage_reports.py).
Zero-dependency Python 3.10+ stdlib test suite.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.manage_reports import (
        SUPPORTED_SCHEMA_VERSIONS,
        VALID_REPORT_STATUSES,
        create_init_report,
        create_manage_report,
        find_latest_report,
        generate_run_id,
        get_git_state,
        save_report,
        validate_report,
    )
except ImportError:
    # Allow tests to run in Red phase before module implementation
    create_init_report = None
    create_manage_report = None
    find_latest_report = None
    generate_run_id = None
    get_git_state = None
    save_report = None
    validate_report = None
    SUPPORTED_SCHEMA_VERSIONS = {"1.0.0"}
    VALID_REPORT_STATUSES = {"completed", "awaiting_decision", "blocked"}


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
        self.assertTrue(Path(pointer_data.get("path")).exists())

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
        """Verifies CLI execution for creating and verifying manage reports."""
        cli_script = REPO_ROOT / "scripts" / "manage_reports.py"
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


if __name__ == "__main__":
    unittest.main()
