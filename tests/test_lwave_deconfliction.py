#!/usr/bin/env python3
"""Lane L1/L4: Tests for role duty/trigger deconfliction in scripts/manage_reports.py."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from manage_reports import detect_role_duty_conflicts, apply_duty_reconciliation
except ImportError:
    detect_role_duty_conflicts = None  # type: ignore
    apply_duty_reconciliation = None  # type: ignore


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
