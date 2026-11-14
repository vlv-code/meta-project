#!/usr/bin/env python3
"""
Unit and Adversarial Test Suite for scripts/inspect_meta_project.py.

Verifies:
1. 7 Canonical Repository States (NONE, FOREIGN_RULES, HEALTHY_REGISTERED,
   HEALTHY_NEW_HARNESS, LEGACY_UNREGISTERED, PARTIAL_CORRUPTED, INCOMPATIBLE_SCHEMA).
2. Git worktree detection via .git pointer file.
3. Capability Matrix calculation (read_instructions, local_checks, skills, roles, hooks).
4. Zero-write side-effect invariant (no files, locks, or telemetry created).
5. CLI JSON and human-readable output contracts.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestInspectMetaProject(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_inspect_")
        self.root = Path(self.test_dir)
        self.script_path = (
            Path(__file__).resolve().parent.parent / "scripts" / "inspect_meta_project.py"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_inspect(self, args=None, cwd=None):
        cmd = [sys.executable, str(self.script_path)]
        if args:
            cmd.extend(args)
        proc = subprocess.run(
            cmd,
            cwd=cwd or str(self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return proc

    # -------------------------------------------------------------------------
    # State 1: NONE
    # -------------------------------------------------------------------------
    def test_state_none_on_empty_repo(self):
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0, f"Stderr: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "NONE")
        self.assertEqual(data["recommended_action"], "scaffold_clean")
        self.assertEqual(data["capabilities"]["read_instructions"]["status"], "unavailable")

    # -------------------------------------------------------------------------
    # State 2: FOREIGN_RULES
    # -------------------------------------------------------------------------
    def test_state_foreign_rules_with_claude_or_cursor(self):
        (self.root / "CLAUDE.md").write_text("# Project rules\nDo this and that.", encoding="utf-8")
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "FOREIGN_RULES")
        self.assertEqual(data["recommended_action"], "preserve_and_merge")
        self.assertIn("CLAUDE.md", data["foreign_instructions"])

    def test_state_foreign_rules_with_non_metaproject_agents_md(self):
        (self.root / "AGENTS.md").write_text("# Generic Agent Instructions\nSome instructions.", encoding="utf-8")
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "FOREIGN_RULES")
        self.assertEqual(data["recommended_action"], "preserve_and_merge")

    # -------------------------------------------------------------------------
    # Helper to scaffold minimal Meta-Project structure
    # -------------------------------------------------------------------------
    def _create_minimal_metaproject(self, active_harness="antigravity", active_installation="ag-main"):
        agents_md = self.root / "AGENTS.md"
        agents_md.write_text(
            "# Project Passport: Test\n## 1. Concept, Principles, and North Stars\n"
            "## 3. Directive Meta-Knowledge Protocol\n## 6. Project Agent Team & Multi-Harness Identity\n",
            encoding="utf-8",
        )
        pk = self.root / ".agents" / "project_knowledge"
        pk.mkdir(parents=True)
        (pk / "boundaries.md").write_text("# Responsibility Zones\n## Green Zone\n- src/**\n", encoding="utf-8")
        (pk / "tasks.md").write_text("# Tasks\n- [x] Step 1\n", encoding="utf-8")
        (pk / "observations.md").write_text("# Obs\n| Date | Cat | Comp | Obs | Sol |\n", encoding="utf-8")
        (pk / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
        (pk / "weak_spots.md").write_text("# Weak spots\n", encoding="utf-8")

        scripts_dir = self.root / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "check_boundaries.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        (scripts_dir / "verify_identity.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        skills_dir = self.root / ".agents" / "skills" / "record-observation"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: record-observation\n---\n# Skill\n", encoding="utf-8")

        team_dir = self.root / ".agents" / "team" / "agent-dev-lead"
        team_dir.mkdir(parents=True)
        (team_dir / "profile.md").write_text(
            f"---\nrole_id: agent-dev-lead\nharness_id: {active_harness}\n"
            f"installation_id: {active_installation}\nactor_id: test::{active_harness}::{active_installation}::agent-dev-lead\n---\n",
            encoding="utf-8",
        )

        registry = {
            "schema_version": "1.0.0",
            "project_id": "vlv-code/test-project",
            "installations": {
                active_installation: {
                    "harness_id": active_harness,
                    "status": "active",
                    "description": "Active installation",
                },
                "zc-main": {
                    "harness_id": "zcode",
                    "status": "planned",
                    "description": "Planned target",
                },
            },
            "roles": {
                "agent-dev-lead": {
                    "description": "Dev Lead",
                    "bindings": {
                        active_installation: {
                            "actor_id": f"test::{active_harness}::{active_installation}::agent-dev-lead",
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        },
                        "zc-main": {
                            "actor_id": "test::zcode::zc-main::agent-dev-lead",
                            "status": "planned",
                            "profile_path": None,
                        },
                    },
                }
            },
        }
        (self.root / ".agents" / "meta-project.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")

    # -------------------------------------------------------------------------
    # State 3: HEALTHY_REGISTERED
    # -------------------------------------------------------------------------
    def test_state_healthy_registered(self):
        self._create_minimal_metaproject()
        proc = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "antigravity", "--installation", "ag-main", "--json"]
        )
        self.assertEqual(proc.returncode, 0, f"Stderr: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")
        self.assertEqual(data["recommended_action"], "pass_through")
        self.assertEqual(data["capabilities"]["read_instructions"]["status"], "available")
        self.assertEqual(data["capabilities"]["local_checks"]["status"], "available")
        self.assertEqual(data["capabilities"]["roles"]["status"], "available")
        self.assertEqual(data["capabilities"]["skills"]["status"], "available")

    # -------------------------------------------------------------------------
    # State 4: HEALTHY_NEW_HARNESS
    # -------------------------------------------------------------------------
    def test_state_healthy_new_harness_planned_or_unregistered(self):
        self._create_minimal_metaproject()
        # Query for zcode (which is planned)
        proc = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "zcode", "--installation", "zc-main", "--json"]
        )
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "HEALTHY_NEW_HARNESS")
        self.assertEqual(data["recommended_action"], "bind_harness")

        # Query for completely unmentioned harness
        proc2 = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "custom-harness", "--installation", "cust-1", "--json"]
        )
        self.assertEqual(proc2.returncode, 0)
        data2 = json.loads(proc2.stdout)
        self.assertEqual(data2["state"], "HEALTHY_NEW_HARNESS")
        self.assertEqual(data2["recommended_action"], "bind_harness")

    # -------------------------------------------------------------------------
    # State 5: LEGACY_UNREGISTERED
    # -------------------------------------------------------------------------
    def test_state_legacy_unregistered_missing_meta_project_json(self):
        self._create_minimal_metaproject()
        # Remove registry file
        (self.root / ".agents" / "meta-project.json").unlink()
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "LEGACY_UNREGISTERED")
        self.assertEqual(data["recommended_action"], "adopt_legacy")

    # -------------------------------------------------------------------------
    # State 6: PARTIAL_CORRUPTED
    # -------------------------------------------------------------------------
    def test_state_partial_corrupted_missing_boundaries(self):
        self._create_minimal_metaproject()
        (self.root / ".agents" / "project_knowledge" / "boundaries.md").unlink()
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "PARTIAL_CORRUPTED")
        self.assertEqual(data["recommended_action"], "diagnose_and_repair")
        self.assertIn(".agents/project_knowledge/boundaries.md", data["missing_components"])

    def test_state_partial_corrupted_malformed_json_registry(self):
        self._create_minimal_metaproject()
        (self.root / ".agents" / "meta-project.json").write_text("{ malformed json", encoding="utf-8")
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "PARTIAL_CORRUPTED")
        self.assertEqual(data["recommended_action"], "diagnose_and_repair")

    # -------------------------------------------------------------------------
    # State 7: INCOMPATIBLE_SCHEMA
    # -------------------------------------------------------------------------
    def test_state_incompatible_schema(self):
        self._create_minimal_metaproject()
        registry = json.loads((self.root / ".agents" / "meta-project.json").read_text(encoding="utf-8"))
        registry["schema_version"] = "99.0.0"
        (self.root / ".agents" / "meta-project.json").write_text(json.dumps(registry), encoding="utf-8")

        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "INCOMPATIBLE_SCHEMA")
        self.assertEqual(data["recommended_action"], "read_only_fallback")

    # -------------------------------------------------------------------------
    # Git Worktree Support
    # -------------------------------------------------------------------------
    def test_git_worktree_detection(self):
        # Emulate git worktree by creating a .git file pointing to a gitdir
        main_git = self.root / ".main_repo" / ".git"
        main_git.mkdir(parents=True)
        worktree_dir = self.root / "worktree1"
        worktree_dir.mkdir(parents=True)
        (worktree_dir / ".git").write_text(f"gitdir: {main_git}/worktrees/worktree1\n", encoding="utf-8")

        proc = self.run_inspect(["--repo-root", str(worktree_dir), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertTrue(data["is_git_worktree"])

    # -------------------------------------------------------------------------
    # Zero-Write Invariant (Survey-First)
    # -------------------------------------------------------------------------
    def test_zero_write_side_effect_invariant(self):
        self._create_minimal_metaproject()

        def snapshot_dir(path: Path):
            files = {}
            for p in path.rglob("*"):
                if p.is_file():
                    files[str(p.relative_to(path))] = (p.stat().st_size, p.stat().st_mtime_ns)
            return files

        initial_snapshot = snapshot_dir(self.root)

        # Run inspect in read-only and standard mode
        proc = self.run_inspect(["--repo-root", str(self.root), "--read-only", "--json"])
        self.assertEqual(proc.returncode, 0)

        proc2 = self.run_inspect(["--repo-root", str(self.root)])
        self.assertEqual(proc2.returncode, 0)

        post_snapshot = snapshot_dir(self.root)
        self.assertEqual(initial_snapshot, post_snapshot, "Survey phase must produce 0 file modifications or locks.")

    # -------------------------------------------------------------------------
    # Human-Readable CLI Output
    # -------------------------------------------------------------------------
    def test_human_readable_cli_output(self):
        self._create_minimal_metaproject()
        proc = self.run_inspect(["--repo-root", str(self.root)])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("[Meta-Project Inspection Report]", proc.stdout)
        self.assertIn("State:", proc.stdout)
        self.assertIn("Capability Matrix:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
