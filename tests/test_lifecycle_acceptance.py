#!/usr/bin/env python3
"""Canonical lifecycle and orchestration acceptance tests (Zero External Dependencies).
Consolidated from test_acceptance_scenarios.py and test_report_and_manage_cycle.py.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, Tuple
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

INSPECT_SCRIPT = SCRIPTS_DIR / "inspect_meta_project.py"
VERIFY_SCRIPT = SCRIPTS_DIR / "verify_identity.py"
BOUNDARIES_SCRIPT = SCRIPTS_DIR / "check_boundaries.py"
REPORTS_SCRIPT = SCRIPTS_DIR / "manage_reports.py"

from scripts.manage_reports import (
    check_report_staleness,
    create_init_report,
    create_manage_report,
    find_latest_report,
    get_git_state,
    resolve_team_topology,
    save_report,
    validate_report,
)
from scripts.verify_identity import validate_scenario_section, validate_identity_registry
from scripts.inspect_meta_project import inspect_repository

try:
    from scripts.manage_reports import evaluate_manage_intake
except ImportError:
    evaluate_manage_intake = None


class TestAcceptanceScenarios(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_acceptance_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_inspect(self, args: list[str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(INSPECT_SCRIPT)]
        if args:
            cmd.extend(args)
        return subprocess.run(
            cmd,
            cwd=str(cwd or self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def _snapshot_tree(self, path: Path) -> Dict[str, Tuple[int, int]]:
        """Returns relative path -> (size, mtime_ns) for all files."""
        tree = {}
        for p in path.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(path)).replace("\\", "/")
                tree[rel] = (p.stat().st_size, p.stat().st_mtime_ns)
        return tree

    def _create_healthy_metaproject(
        self,
        target_dir: Path | None = None,
        harness: str = "antigravity",
        installation: str = "ag-main",
    ) -> Path:
        base = target_dir or self.root
        # 1. Root AGENTS.md
        agents_md = base / "AGENTS.md"
        agents_md.write_text(
            "# Project Passport: Meta-Project Test\n\n"
            "## 1. Concept, Principles, and North Stars\n"
            "- Service Purpose: Agentic environment test fixture.\n"
            "## 3. Directive Meta-Knowledge Protocol\n"
            "- Boundaries: .agents/project_knowledge/boundaries.md\n"
            "## 5. Local Verification Tooling & Autonomous Fallback\n"
            "- Base Fallback Mode commands.\n"
            "## 6. Project Agent Team & Multi-Harness Identity (.agents/team/)\n"
            "- Lead Developer: agent-dev-lead\n",
            encoding="utf-8",
        )

        # 2. Knowledge Slices
        pk = base / ".agents" / "project_knowledge"
        pk.mkdir(parents=True, exist_ok=True)
        (pk / "boundaries.md").write_text(
            "# Responsibility Zones\n\n## Green Zone\n- src/**\n\n## Yellow Zone\n- scripts/**\n\n## Red Zone\n- LICENSE\n",
            encoding="utf-8",
        )
        (pk / "tasks.md").write_text(
            "# Tasks\n\n- [x] [test::antigravity::ag-main::agent-dev-lead @ 2026-11-14 20:00] Initial scaffold complete\n",
            encoding="utf-8",
        )
        (pk / "observations.md").write_text(
            "# Observations\n\n| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| 2026-11-14 | [init] | repo/init | Initialized healthy fixture | Valid fixture deployed |\n",
            encoding="utf-8",
        )
        (pk / "architecture.md").write_text("# Architecture Map\nComponent mapping.\n", encoding="utf-8")
        (pk / "weak_spots.md").write_text("# Weak Spots\nKnown risks.\n", encoding="utf-8")

        # 3. Scripts
        scripts_dir = base / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BOUNDARIES_SCRIPT, scripts_dir / "check_boundaries.py")
        shutil.copy2(VERIFY_SCRIPT, scripts_dir / "verify_identity.py")
        shutil.copy2(INSPECT_SCRIPT, scripts_dir / "inspect_meta_project.py")

        # 4. Local Skills
        skill_dir = base / ".agents" / "skills" / "record-observation"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: record-observation\ndescription: Test skill\n---\n## When to invoke skill\nWhen logging.\n## Execution steps\nRun CLI.\n",
            encoding="utf-8",
        )

        # 5. Team Profiles
        team_dir = base / ".agents" / "team" / "agent-dev-lead"
        team_dir.mkdir(parents=True, exist_ok=True)
        actor_id = f"vlv-code/test::{harness}::{installation}::agent-dev-lead"
        (team_dir / "profile.md").write_text(
            f"---\nname: Lead Dev\nrole_id: agent-dev-lead\nharness_id: {harness}\ninstallation_id: {installation}\n"
            f"actor_id: {actor_id}\ndescription: Dev\ntools: [read_file]\nmodel: inherit\ninvocation_triggers: [dev]\n---\n",
            encoding="utf-8",
        )

        # 6. Registry
        registry = {
            "schema_version": "1.0.0",
            "project_id": "vlv-code/test",
            "installations": {
                installation: {
                    "harness_id": harness,
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
                        installation: {
                            "actor_id": actor_id,
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        },
                        "zc-main": {
                            "actor_id": "vlv-code/test::zcode::zc-main::agent-dev-lead",
                            "status": "planned",
                            "profile_path": None,
                        },
                    },
                }
            },
        }
        (base / ".agents" / "meta-project.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
        return base

    # =========================================================================
    # Scenario 1 (empty project)
    # =========================================================================
    def test_scenario_1_empty_project(self):
        """Scenario 1: Empty repo classified as NONE with recommended action scaffold_clean."""
        res = self._run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)

        self.assertEqual(data["state"], "NONE")
        self.assertEqual(data["recommended_action"], "scaffold_clean")
        self.assertEqual(data["capabilities"]["read_instructions"]["status"], "unavailable")
        self.assertEqual(data["capabilities"]["local_checks"]["status"], "unavailable")

        # Non-destructive invariant: verify nothing was created on disk
        self.assertEqual(len(list(self.root.iterdir())), 0, "Inspection of empty repository must not create any files.")

    # =========================================================================
    # Scenario 2 (foreign instructions)
    # =========================================================================
    def test_scenario_2_foreign_instructions(self):
        """Scenario 2: Foreign instructions (CLAUDE.md, .cursorrules) classified as FOREIGN_RULES and kept intact."""
        claude_content = "# Claude Instructions\nFollow these guidelines carefully.\n"
        cursor_content = '{"rules": ["strict_types", "no_console"]}\n'
        generic_agents_content = "# Generic Agent Guide\nCustom instructions not following Meta-Project.\n"

        (self.root / "CLAUDE.md").write_text(claude_content, encoding="utf-8")
        (self.root / ".cursorrules").write_text(cursor_content, encoding="utf-8")
        (self.root / "AGENTS.md").write_text(generic_agents_content, encoding="utf-8")

        res = self._run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)

        self.assertEqual(data["state"], "FOREIGN_RULES")
        self.assertEqual(data["recommended_action"], "preserve_and_merge")
        self.assertIn("CLAUDE.md", data["foreign_instructions"])
        self.assertIn(".cursorrules", data["foreign_instructions"])
        self.assertIn("AGENTS.md", data["foreign_instructions"])

        # Non-destructive invariant: verify foreign files are byte-for-byte identical
        self.assertEqual((self.root / "CLAUDE.md").read_text(encoding="utf-8"), claude_content)
        self.assertEqual((self.root / ".cursorrules").read_text(encoding="utf-8"), cursor_content)
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8"), generic_agents_content)

    # =========================================================================
    # Scenario 3 (healthy registered zero diff)
    # =========================================================================
    def test_scenario_3_healthy_registered_zero_diff(self):
        """Scenario 3: Repeated runs on healthy registered repo yield HEALTHY_REGISTERED, pass_through, and 0 diff."""
        self._create_healthy_metaproject()
        snapshot_before = self._snapshot_tree(self.root)

        # Run inspect twice
        res1 = self._run_inspect(
            ["--repo-root", str(self.root), "--harness", "antigravity", "--installation", "ag-main", "--json"]
        )
        self.assertEqual(res1.returncode, 0, f"Stderr: {res1.stderr}")
        data1 = json.loads(res1.stdout)
        self.assertEqual(data1["state"], "HEALTHY_REGISTERED")
        self.assertEqual(data1["recommended_action"], "pass_through")
        self.assertEqual(data1["capabilities"]["read_instructions"]["status"], "available")
        self.assertEqual(data1["capabilities"]["local_checks"]["status"], "available")

        res2 = self._run_inspect(
            ["--repo-root", str(self.root), "--harness", "antigravity", "--installation", "ag-main"]
        )
        self.assertEqual(res2.returncode, 0)
        self.assertIn("[Meta-Project Inspection Report]", res2.stdout)

        snapshot_after = self._snapshot_tree(self.root)
        self.assertEqual(
            snapshot_before,
            snapshot_after,
            "Pass-through Zero-Diff Invariant violated: inspection modified files or created locks/cache.",
        )

    # =========================================================================
    # Scenario 4 (healthy new harness)
    # =========================================================================
    def test_scenario_4_healthy_new_harness(self):
        """Scenario 4: Connecting new or planned harness yields HEALTHY_NEW_HARNESS without disturbing active ones."""
        self._create_healthy_metaproject()
        registry_path = self.root / ".agents" / "meta-project.json"
        registry_orig = json.loads(registry_path.read_text(encoding="utf-8"))

        # Query for planned zcode harness
        res = self._run_inspect(
            ["--repo-root", str(self.root), "--harness", "zcode", "--installation", "zc-main", "--json"]
        )
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["state"], "HEALTHY_NEW_HARNESS")
        self.assertEqual(data["recommended_action"], "bind_harness")

        # Invariant: active installation 'ag-main' remains intact in registry
        registry_after = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(registry_orig, registry_after)
        self.assertEqual(registry_after["installations"]["ag-main"]["status"], "active")
        self.assertEqual(
            registry_after["roles"]["agent-dev-lead"]["bindings"]["ag-main"]["status"],
            "active",
        )

    # =========================================================================
    # Scenario 5 (legacy unregistered)
    # =========================================================================
    def test_scenario_5_legacy_unregistered(self):
        """Scenario 5: Legacy repo without meta-project.json yields LEGACY_UNREGISTERED, preserving history."""
        self._create_healthy_metaproject()
        # Remove registry file to emulate legacy setup
        reg_file = self.root / ".agents" / "meta-project.json"
        reg_file.unlink()

        tasks_orig = (self.root / ".agents" / "project_knowledge" / "tasks.md").read_text(encoding="utf-8")
        obs_orig = (self.root / ".agents" / "project_knowledge" / "observations.md").read_text(encoding="utf-8")

        res = self._run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)

        self.assertEqual(data["state"], "LEGACY_UNREGISTERED")
        self.assertEqual(data["recommended_action"], "adopt_legacy")
        self.assertIn(".agents/meta-project.json", data["missing_components"])

        # History Preservation Invariant: tasks.md and observations.md must remain untouched
        tasks_after = (self.root / ".agents" / "project_knowledge" / "tasks.md").read_text(encoding="utf-8")
        obs_after = (self.root / ".agents" / "project_knowledge" / "observations.md").read_text(encoding="utf-8")
        self.assertEqual(tasks_orig, tasks_after, "Historical tasks.md must not be modified during legacy inspection.")
        self.assertEqual(obs_orig, obs_after, "Historical observations.md must not be modified during legacy inspection.")

    # =========================================================================
    # Scenario 6 (partial corrupted)
    # =========================================================================
    def test_scenario_6_partial_corrupted(self):
        """Scenario 6: Corrupted repo (missing boundaries or malformed json) yields PARTIAL_CORRUPTED with exact discrepancies."""
        self._create_healthy_metaproject()

        # Case A: Missing boundaries.md
        boundaries_file = self.root / ".agents" / "project_knowledge" / "boundaries.md"
        boundaries_file.unlink()

        res_a = self._run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(res_a.returncode, 0)
        data_a = json.loads(res_a.stdout)
        self.assertEqual(data_a["state"], "PARTIAL_CORRUPTED")
        self.assertEqual(data_a["recommended_action"], "diagnose_and_repair")
        self.assertIn(".agents/project_knowledge/boundaries.md", data_a["missing_components"])

        # Case B: Malformed registry JSON
        (self.root / ".agents" / "project_knowledge" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
        (self.root / ".agents" / "meta-project.json").write_text("{ unclosed json: [1, 2,", encoding="utf-8")

        res_b = self._run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(res_b.returncode, 0)
        data_b = json.loads(res_b.stdout)
        self.assertEqual(data_b["state"], "PARTIAL_CORRUPTED")
        self.assertEqual(data_b["recommended_action"], "diagnose_and_repair")
        self.assertTrue(
            any("malformed" in mc.lower() for mc in data_b["missing_components"]),
            "Missing components must explicitly report malformed registry JSON",
        )

    # =========================================================================
    # Scenario 7 (read-only mode)
    # =========================================================================
    def test_scenario_7_read_only_mode(self):
        """Scenario 7: Inspection under --read-only guarantees strictly 0 writes on disk."""
        self._create_healthy_metaproject()
        snapshot_before = self._snapshot_tree(self.root)

        res = self._run_inspect(
            ["--repo-root", str(self.root), "--read-only", "--json",
             "--harness", "antigravity", "--installation", "ag-main"]
        )
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")

        # Also run in human-readable mode with --read-only
        res_human = self._run_inspect(
            ["--repo-root", str(self.root), "--read-only",
             "--harness", "antigravity", "--installation", "ag-main"]
        )
        self.assertEqual(res_human.returncode, 0)

        snapshot_after = self._snapshot_tree(self.root)
        self.assertEqual(
            snapshot_before,
            snapshot_after,
            "Strict read-only invariant violated: disk writes or metadata updates detected.",
        )

    # =========================================================================
    # Scenario 8 (git worktree)
    # =========================================================================
    def test_scenario_8_git_worktree(self):
        """Scenario 8: Running in a git worktree correctly identifies is_git_worktree and git_toplevel."""
        main_repo = self.root / "main_repo"
        main_repo.mkdir(parents=True)
        (main_repo / ".git").mkdir()

        worktree_dir = self.root / "worktree_sub"
        worktree_dir.mkdir(parents=True)
        (worktree_dir / ".git").write_text(f"gitdir: {main_repo}/.git/worktrees/worktree_sub\n", encoding="utf-8")

        self._create_healthy_metaproject(target_dir=worktree_dir)

        res = self._run_inspect(["--repo-root", str(worktree_dir), "--json"])
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)

        self.assertTrue(data["is_git_worktree"], "Must detect git worktree via .git pointer file.")
        main_repo_str = str(main_repo.resolve()).replace("\\", "/")
        self.assertTrue(
            data["git_toplevel"].replace("\\", "/").startswith(main_repo_str),
            f"Git toplevel must resolve within main repository root: expected {main_repo_str}, got {data['git_toplevel']}",
        )

    # =========================================================================
    # Scenario 9 (readme entry without skills)
    # =========================================================================
    def test_scenario_9_readme_entry_without_skills(self):
        """Scenario 9: Agent without global skills navigates via self-contained AGENTS.md and local CLIs."""
        if not (REPO_ROOT / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )
        super().setUp()
        # Verify repository canonical entry in root README.md
        readme_path = REPO_ROOT / "README.md"
        self.assertTrue(readme_path.is_file(), "Root README.md must exist")
        readme_content = readme_path.read_text(encoding="utf-8")
        self.assertIn("<!-- META-PROJECT:ENTRY:BEGIN -->", readme_content)
        self.assertIn("<!-- META-PROJECT:ENTRY:END -->", readme_content)
        self.assertIn("AGENTS.md", readme_content)
        self.assertIn("python scripts/inspect_meta_project.py", readme_content)

        # Verify self-contained AGENTS.md in repository root
        agents_path = REPO_ROOT / "AGENTS.md"
        self.assertTrue(agents_path.is_file(), "Root AGENTS.md must exist")
        agents_content = agents_path.read_text(encoding="utf-8")

        # Must list local verification commands in Section 5 Base Fallback Mode
        expected_commands = [
            "python scripts/inspect_meta_project.py",
            "python scripts/verify_identity.py",
            "python scripts/check_boundaries.py",
            "python scripts/compact_memory.py",
            "python scripts/record_obs.py",
        ]
        for cmd in expected_commands:
            self.assertIn(
                cmd,
                agents_content,
                f"Root AGENTS.md must document standalone local CLI command '{cmd}' for skill-less agents.",
            )

        # Execute local fallback CLI commands directly in repository context
        proc_inspect = subprocess.run(
            [sys.executable, str(INSPECT_SCRIPT), "--json",
             "--harness", "antigravity", "--installation", "ag-main"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(proc_inspect.returncode, 0, f"Local inspect failed: {proc_inspect.stderr}")
        inspect_data = json.loads(proc_inspect.stdout)
        self.assertEqual(inspect_data["state"], "HEALTHY_REGISTERED")

        proc_verify = subprocess.run(
            [sys.executable, str(VERIFY_SCRIPT), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(proc_verify.returncode, 0, f"Local verify_identity failed: {proc_verify.stderr}")
        self.assertIn("[OK] Identity verification passed", proc_verify.stdout)

class TestReportAndManageCycle(unittest.TestCase):
    """Integration and acceptance test suite for Meta-Project report and management cycle."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_cycle_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _snapshot_tree(self, path: Path) -> Dict[str, Tuple[int, int]]:
        """Returns relative path -> (size, mtime_ns) for all files in tree."""
        tree = {}
        for p in path.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(path)).replace("\\", "/")
                tree[rel] = (p.stat().st_size, p.stat().st_mtime_ns)
        return tree

    def _setup_healthy_repo(
        self,
        project_id: str = "vlv-code/meta-project",
        harness: str = "antigravity",
        installation: str = "ag-main",
        scenario: Dict[str, Any] | None = None,
    ) -> Path:
        """Sets up a canonical healthy Meta-Project fixture in self.root."""
        base = self.root

        # 1. Root AGENTS.md
        agents_md = base / "AGENTS.md"
        agents_md.write_text(
            "# Project Passport: Meta-Project Test\n\n"
            "## 1. Concept, Principles, and North Stars\n"
            "- Service Purpose: Acceptance testing fixture.\n"
            "## 3. Directive Meta-Knowledge Protocol\n"
            "- Responsibilities and Boundaries: .agents/project_knowledge/boundaries.md\n"
            "## 5. Local Verification Tooling & Autonomous Fallback\n"
            "- Standalone CLI tools.\n"
            "## 6. Project Agent Team & Multi-Harness Identity (.agents/team/)\n"
            "- [Lead Developer](.agents/team/agent-dev-lead/profile.md) (invoked by: dev lead)\n",
            encoding="utf-8",
        )

        # 2. Knowledge Slices
        pk = base / ".agents" / "project_knowledge"
        pk.mkdir(parents=True, exist_ok=True)
        (pk / "boundaries.md").write_text(
            "# Responsibility Zones\n\n## Green Zone\n- src/**\n- tests/**\n\n## Yellow Zone\n- scripts/**\n\n## Red Zone\n- LICENSE\n",
            encoding="utf-8",
        )
        (pk / "tasks.md").write_text(
            f"# Active Tasks\n- [x] [{project_id}::{harness}::{installation}::agent-dev-lead @ 2026-11-15T00:00:00Z] Setup fixture\n",
            encoding="utf-8",
        )
        (pk / "observations.md").write_text(
            "# Observations\n| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| 2026-11-15 | [init] | repo/init | Initial fixture deployment | Valid fixture deployed |\n",
            encoding="utf-8",
        )
        (pk / "architecture.md").write_text("# Architecture Map\nComponent mapping.\n", encoding="utf-8")
        (pk / "weak_spots.md").write_text("# Weak Spots\nKnown risks.\n", encoding="utf-8")

        # 3. Scripts
        scripts_dir = base / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BOUNDARIES_SCRIPT, scripts_dir / "check_boundaries.py")
        shutil.copy2(VERIFY_SCRIPT, scripts_dir / "verify_identity.py")
        shutil.copy2(INSPECT_SCRIPT, scripts_dir / "inspect_meta_project.py")
        shutil.copy2(REPORTS_SCRIPT, scripts_dir / "manage_reports.py")

        # 4. Role: agent-dev-lead
        lead_dir = base / ".agents" / "team" / "agent-dev-lead"
        lead_dir.mkdir(parents=True, exist_ok=True)
        lead_actor_id = f"{project_id}::{harness}::{installation}::agent-dev-lead"
        (lead_dir / "profile.md").write_text(
            f"---\nname: Lead Developer\nrole_id: agent-dev-lead\nharness_id: {harness}\n"
            f"installation_id: {installation}\nactor_id: {lead_actor_id}\n"
            f"description: Lead Developer\ntools: [read_file, write_file]\nmodel: inherit\n"
            f"invocation_triggers: [dev lead, implement feature]\n---\n"
            f"# Role Profile\n\n### 5. Role Call Log (Telemetry)\n"
            f"| Date | Initiator | Actor ID | Task Summary | Result / Artifact |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"| 2026-11-15 | User | {lead_actor_id} | Initial fixture | OK |\n",
            encoding="utf-8",
        )
        (lead_dir / "notes.md").write_text(
            "# Private Notes: Lead Developer\n- Persistent memory: do not touch.\n",
            encoding="utf-8",
        )

        # 5. Registry (.agents/meta-project.json)
        default_scenario = {
            "profile": "active_development",
            "deployment_mode": "shared_repo",
            "collaboration_model": "triad",
            "verification_policy": "strict_independent",
            "delegation_level": "controlled",
            "constraints": ["No direct commits to main"],
            "unresolved_questions": [],
        }
        effective_scenario = scenario if scenario is not None else default_scenario

        registry_data = {
            "schema_version": "1.1.0",
            "project_id": project_id,
            "scenario": effective_scenario,
            "installations": {
                installation: {
                    "harness_id": harness,
                    "status": "active",
                    "description": "Primary active installation",
                }
            },
            "roles": {
                "agent-dev-lead": {
                    "description": "Task decomposition and development lead",
                    "bindings": {
                        installation: {
                            "actor_id": lead_actor_id,
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        }
                    },
                }
            },
        }

        registry_path = base / ".agents" / "meta-project.json"
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

        return base

    def test_scenario_agreement_persisted_in_registry(self):
        """
        Scenario 1: Persistence of scenario decisions across 4 groups.
        Verifies that decisions (profile, deployment_mode, collaboration_model, verification_policy)
        are cleanly saved in .agents/meta-project.json, pass verify_registry, surface in inspect_repository,
        and fail-closed on invalid values.
        """
        scenario = {
            "profile": "active_development",
            "deployment_mode": "shared_repo",
            "collaboration_model": "triad",
            "verification_policy": "strict_independent",
            "delegation_level": "controlled",
            "constraints": ["Require review before push", "Zero external runtime deps"],
            "unresolved_questions": [],
        }

        self._setup_healthy_repo(scenario=scenario)
        registry_path = self.root / ".agents" / "meta-project.json"

        # 1. Verify via Python function validate_identity_registry
        with open(registry_path, "r", encoding="utf-8") as f:
            reg_data = json.load(f)
        valid, errors = validate_identity_registry(self.root)
        self.assertTrue(valid, f"Registry verification failed: {errors}")

        # 2. Verify via CLI scripts/verify_identity.py --check
        res = subprocess.run(
            [sys.executable, str(VERIFY_SCRIPT), "--check", "--repo-root", str(self.root)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"CLI verification failed: {res.stderr}\n{res.stdout}")
        self.assertIn("[OK]", res.stdout)

        # 3. Verify via scripts/inspect_meta_project.py
        # (explicit runtime context: unknown context must yield
        # CONTEXT_UNRESOLVED, never silent any-active resolution — audit §4)
        inspection = inspect_repository(
            self.root, target_harness="antigravity", target_installation="ag-main"
        )
        self.assertEqual(inspection["state"], "HEALTHY_REGISTERED")
        surfaced_scenario = inspection.get("scenario")
        self.assertIsInstance(surfaced_scenario, dict)
        self.assertEqual(surfaced_scenario["profile"], "active_development")
        self.assertEqual(surfaced_scenario["deployment_mode"], "shared_repo")
        self.assertEqual(surfaced_scenario["collaboration_model"], "triad")
        self.assertEqual(surfaced_scenario["verification_policy"], "strict_independent")
        self.assertEqual(surfaced_scenario["delegation_level"], "controlled")
        self.assertEqual(surfaced_scenario["constraints"], ["Require review before push", "Zero external runtime deps"])

        # 4. Adversarial tests: Invalid values for each group must fail-closed
        adversarial_cases = [
            ("profile", "non_existent_profile", "Invalid scenario profile"),
            ("deployment_mode", "cloud_direct", "Invalid scenario deployment_mode"),
            ("collaboration_model", "swarm_infinite", "Invalid scenario collaboration_model"),
            ("verification_policy", "blind_trust", "Invalid scenario verification_policy"),
            ("delegation_level", "unrestricted", "Invalid scenario delegation_level"),
            ("constraints", "not_a_list", "must be a list"),
        ]

        for key, bad_val, expected_err in adversarial_cases:
            corrupted = dict(reg_data)
            corrupted_scenario = dict(scenario)
            corrupted_scenario[key] = bad_val
            corrupted["scenario"] = corrupted_scenario

            corrupted_errs = validate_scenario_section(corrupted_scenario)
            self.assertTrue(
                any(expected_err in err for err in corrupted_errs),
                f"Expected error mentioning '{expected_err}' for bad {key}='{bad_val}', got: {corrupted_errs}",
            )

    def test_init_report_generation_and_contract(self):
        """
        Scenario 2: Init report generation and schema contract compliance.
        Verifies that create_init_report generates a valid schema 1.0.0 report
        containing all mandatory references (registry, passport, boundaries) and fields.
        """
        self._setup_healthy_repo()
        installation_id = "ag-main"
        harness_id = "antigravity"
        project_id = "vlv-code/meta-project"
        actor_id = f"{project_id}::{harness_id}::{installation_id}::agent-dev-lead"

        scenario = {
            "profile": "maintenance",
            "deployment_mode": "shared_repo",
            "collaboration_model": "duo",
            "verification_policy": "duo_peer_review",
            "delegation_level": "controlled",
            "constraints": [],
            "unresolved_questions": [],
        }

        # 1. Assemble and save init report
        init_report = create_init_report(
            repo_root=self.root,
            installation_id=installation_id,
            harness_id=harness_id,
            actor_id=actor_id,
            project_id=project_id,
            status="completed",
            scenario=scenario,
            environment={"capabilities": {"local_checks": True}, "constraints": []},
            components={"created": ["AGENTS.md"], "modified": [], "preserved": []},
            checks=[{"name": "boundary_audit", "status": "pass"}],
            recommendations={"suggested_roles": ["agent-dev-lead", "agent-quality-guardian"], "target_topology": "duo"},
            blockers=[],
            next_step_readiness={"ready_for_manage": True, "details": "Ready for team deployment"},
        )

        saved_path = save_report(
            repo_root=self.root,
            installation_id=installation_id,
            report_type="init",
            report_data=init_report,
        )

        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.name, f"{init_report['run_id']}.json")

        # 2. Check latest.json pointer
        pointer_file = self.root / ".agents" / "reports" / installation_id / "init" / "latest.json"
        self.assertTrue(pointer_file.exists())
        with open(pointer_file, "r", encoding="utf-8") as f:
            pointer_data = json.load(f)
        self.assertEqual(pointer_data["run_id"], init_report["run_id"])
        self.assertEqual(pointer_data["status"], "completed")

        # 3. Validate schema and required references
        with open(saved_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        validation_errors = validate_report(loaded_data, expected_type="init")
        self.assertEqual(validation_errors, [], f"Validation errors: {validation_errors}")

        self.assertEqual(loaded_data["schema_version"], "1.0.0")
        self.assertEqual(loaded_data["report_type"], "init")
        self.assertEqual(loaded_data["project_id"], project_id)
        self.assertEqual(loaded_data["actor_id"], actor_id)
        self.assertEqual(loaded_data["status"], "completed")

        # Invariant: Mandatory reference paths
        refs = loaded_data.get("references", {})
        self.assertIn("registry", refs)
        self.assertIn("passport", refs)
        self.assertIn("boundaries", refs)
        self.assertEqual(refs["registry"], ".agents/meta-project.json")
        self.assertEqual(refs["passport"], "AGENTS.md")
        self.assertEqual(refs["boundaries"], ".agents/project_knowledge/boundaries.md")

        # Invariant: Target files pointed to by references must exist
        self.assertTrue((self.root / refs["registry"]).exists())
        self.assertTrue((self.root / refs["passport"]).exists())
        self.assertTrue((self.root / refs["boundaries"]).exists())

        # Invariant: Readiness flag
        readiness = loaded_data.get("next_step_readiness", {})
        self.assertTrue(readiness.get("ready_for_manage"))

    def test_read_only_mode_never_generates_reports(self):
        """
        Scenario 3: Survey-First Zero-Write Invariant under --read-only.
        Verifies that running inspect_meta_project under --read-only never creates
        .agents/reports/ or writes any file to disk.
        """
        self._setup_healthy_repo()

        reports_dir = self.root / ".agents" / "reports"
        self.assertFalse(reports_dir.exists(), "Reports dir must not exist before read-only inspection")

        pre_snapshot = self._snapshot_tree(self.root)

        # Execute inspection with --read-only (explicit runtime context —
        # audit §4: unknown context yields CONTEXT_UNRESOLVED)
        proc = subprocess.run(
            [sys.executable, str(INSPECT_SCRIPT), "--repo-root", str(self.root),
             "--read-only", "--json", "--harness", "antigravity",
             "--installation", "ag-main"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Inspection failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")

        # Invariant: .agents/reports must NOT exist
        self.assertFalse(reports_dir.exists(), ".agents/reports must strictly not be created under --read-only")

        # Invariant: Entire tree must remain byte-identical
        post_snapshot = self._snapshot_tree(self.root)
        self.assertEqual(pre_snapshot, post_snapshot, "File tree was modified during --read-only execution")

    def test_manage_rejects_foreign_or_incompatible_report(self):
        """
        Scenario 4: Fail-closed rejection of foreign or incompatible reports.
        Verifies that manage ingestion halts when project_id is foreign or schema is invalid.
        """
        self._setup_healthy_repo(project_id="vlv-code/meta-project")

        # Load valid template
        template_path = REPO_ROOT / "templates" / "reports" / "init_report.json"
        with open(template_path, "r", encoding="utf-8") as f:
            valid_template = json.load(f)

        # 1. Incompatible schema version
        corrupted_schema = dict(valid_template)
        corrupted_schema["schema_version"] = "99.0.0"
        errs = validate_report(corrupted_schema, expected_type="init")
        self.assertTrue(any("schema_version" in err for err in errs))

        # 2. Incompatible report type
        corrupted_type = dict(valid_template)
        corrupted_type["report_type"] = "foreign_audit"
        errs = validate_report(corrupted_type, expected_type="init")
        self.assertTrue(any("report_type" in err for err in errs))

        # 3. Foreign project_id must be rejected by the REAL intake engine.
        # Audit §1 fix: this expectation was previously self-implemented
        # inside the test, which proved nothing about application behavior.
        if evaluate_manage_intake is None:
            self.fail(
                "Stage 5 not implemented: intake engine "
                "(scripts.manage_reports.evaluate_manage_intake) is absent"
            )
        foreign_file = self.root / "foreign_report.json"
        foreign_report = dict(valid_template)
        foreign_report["project_id"] = "other-org/malicious-project"
        with open(foreign_file, "w", encoding="utf-8") as f:
            json.dump(foreign_report, f)

        intake_errors = evaluate_manage_intake(
            repo_root=self.root,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            report_path=foreign_file,
        )
        self.assertTrue(
            any("project_id" in e for e in intake_errors),
            f"foreign report admitted by intake engine: {intake_errors!r}",
        )

        # 4. CLI verify subcommand exits with code 1 on corrupted report
        bad_file = self.root / "bad_report.json"
        with open(bad_file, "w", encoding="utf-8") as f:
            json.dump(corrupted_schema, f)

        proc = subprocess.run(
            [sys.executable, str(REPORTS_SCRIPT), "verify", "--report", str(bad_file)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[FAIL]", proc.stdout)

    def test_manage_blocked_on_awaiting_decision(self):
        """
        Scenario 5: Fail-closed block when init report status is awaiting_decision or blocked.
        Verifies that team deployment cannot proceed when pending decisions or blockers exist.
        """
        self._setup_healthy_repo()
        installation_id = "ag-main"

        # Case A: status = awaiting_decision
        scenario = {"profile": "active_development", "collaboration_model": "triad"}
        init_awaiting = create_init_report(
            repo_root=self.root,
            installation_id=installation_id,
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            status="awaiting_decision",
            scenario=scenario,
            blockers=["Unresolved ADR #20 on DB provider"],
            next_step_readiness={
                "ready_for_manage": False,
                "details": "Awaiting user confirmation of database stack",
            },
        )
        save_report(self.root, installation_id, "init", report_data=init_awaiting)

        path, loaded = find_latest_report(self.root, installation_id, "init")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["status"], "awaiting_decision")
        self.assertFalse(loaded["next_step_readiness"]["ready_for_manage"])
        self.assertEqual(loaded["blockers_and_unresolved"], ["Unresolved ADR #20 on DB provider"])

        # Case B: status = blocked
        init_blocked = create_init_report(
            repo_root=self.root,
            installation_id=installation_id,
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            status="blocked",
            scenario=scenario,
            blockers=["Missing CI boundary rules"],
            next_step_readiness={
                "ready_for_manage": False,
                "details": "Blocked by policy gate",
            },
        )
        save_report(self.root, installation_id, "init", report_data=init_blocked)

        path_b, loaded_b = find_latest_report(self.root, installation_id, "init")
        self.assertIsNotNone(loaded_b)
        self.assertEqual(loaded_b["status"], "blocked")
        self.assertFalse(loaded_b["next_step_readiness"]["ready_for_manage"])

    def test_manage_adapts_team_based_on_scenario(self):
        """
        Scenario 6: Scenario-driven team topology adaptation.
        Verifies:
        - maintenance -> Duo (agent-dev-lead, agent-quality-guardian)
        - active_development + strict_independent -> Triad (agent-dev-lead, agent-quality-guardian, agent-github-steward)
        - documentation -> Solo (agent-general-worker)
        """
        # 1. Maintenance -> Duo
        scen_maint = {
            "profile": "maintenance",
            "collaboration_model": "duo",
            "verification_policy": "duo_peer_review",
        }
        res_maint = resolve_team_topology(scen_maint)
        self.assertEqual(res_maint["target_topology"], "duo")
        self.assertIn("agent-dev-lead", res_maint["suggested_roles"])
        self.assertIn("agent-quality-guardian", res_maint["suggested_roles"])

        # 2. Active Development + Strict Independent -> Triad
        scen_active = {
            "profile": "active_development",
            "collaboration_model": "triad",
            "verification_policy": "strict_independent",
        }
        res_active = resolve_team_topology(scen_active)
        self.assertEqual(res_active["target_topology"], "triad")
        self.assertEqual(
            sorted(res_active["suggested_roles"]),
            sorted(["agent-dev-lead", "agent-quality-guardian", "agent-github-steward"]),
        )

        # 3. Documentation -> Solo
        scen_doc = {
            "profile": "documentation",
            "collaboration_model": "solo",
            "verification_policy": "self_check",
        }
        res_doc = resolve_team_topology(scen_doc)
        self.assertEqual(res_doc["target_topology"], "solo")
        self.assertEqual(res_doc["suggested_roles"], ["agent-general-worker"])

        # 4. Generate and validate manage report for Triad
        self._setup_healthy_repo()
        manage_rep = create_manage_report(
            repo_root=self.root,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            init_run_id="init-20261115T010000Z-abc12345",
            status="completed",
            scenario=scen_active,
            roles={
                "preserved": ["agent-dev-lead"],
                "created": ["agent-quality-guardian", "agent-github-steward"],
                "adapted": [],
                "archived": [],
            },
            bindings={
                "agent-dev-lead": {"installation": "ag-main", "status": "active"},
                "agent-quality-guardian": {"installation": "ag-main", "status": "active"},
                "agent-github-steward": {"installation": "ag-main", "status": "active"},
            },
            effective_capabilities={"target_topology": "triad", "ready": True},
        )
        saved = save_report(self.root, "ag-main", "manage", manage_rep)
        self.assertTrue(saved.exists())

        errs = validate_report(manage_rep, expected_type="manage")
        self.assertEqual(errs, [])

    def test_manage_preserves_other_harness_bindings(self):
        """
        Scenario 7: Multi-Harness Coexistence & Non-Destructive Binding.
        Verifies that connecting a new harness (zc-main) strictly preserves
        active installations (ag-main) and role notes without overwriting.
        """
        self._setup_healthy_repo()
        registry_path = self.root / ".agents" / "meta-project.json"

        # Check initial notes in agent-dev-lead
        notes_file = self.root / ".agents" / "team" / "agent-dev-lead" / "notes.md"
        self.assertTrue(notes_file.exists())
        initial_notes_content = notes_file.read_text(encoding="utf-8")
        initial_notes_mtime = notes_file.stat().st_mtime_ns

        # Load registry
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        # Simulate connecting zc-main for zcode harness
        registry["installations"]["zc-main"] = {
            "harness_id": "zcode",
            "status": "planned",
            "description": "ZCode secondary installation",
        }
        zc_actor_id = "vlv-code/meta-project::zcode::zc-main::agent-dev-lead"
        registry["roles"]["agent-dev-lead"]["bindings"]["zc-main"] = {
            "actor_id": zc_actor_id,
            "status": "planned",
            "profile_path": None,
        }

        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        # Verify registry integrity
        valid, errs = validate_identity_registry(self.root)
        self.assertTrue(valid, f"Multi-harness registry verification failed: {errs}")

        # Invariant 1: ag-main installation remains active
        self.assertEqual(registry["installations"]["ag-main"]["status"], "active")

        # Invariant 2: ag-main binding for agent-dev-lead is untouched
        ag_binding = registry["roles"]["agent-dev-lead"]["bindings"]["ag-main"]
        self.assertEqual(ag_binding["status"], "active")
        self.assertEqual(
            ag_binding["actor_id"],
            "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
        )

        # Invariant 3: Private notes untouched
        self.assertEqual(notes_file.read_text(encoding="utf-8"), initial_notes_content)
        self.assertEqual(notes_file.stat().st_mtime_ns, initial_notes_mtime)

        # Invariant 4: Manage report for zc-main records ag-main role as preserved
        manage_rep = create_manage_report(
            repo_root=self.root,
            installation_id="zc-main",
            harness_id="zcode",
            actor_id=zc_actor_id,
            project_id="vlv-code/meta-project",
            init_run_id="init-20261115T010000Z-zc0001",
            status="completed",
            scenario=registry.get("scenario", {}),
            roles={
                "preserved": ["agent-dev-lead"],
                "created": [],
                "adapted": [],
                "archived": [],
            },
            bindings={
                "agent-dev-lead": {"installation": "zc-main", "status": "active"}
            },
        )
        saved_zc_report = save_report(self.root, "zc-main", "manage", manage_rep)
        self.assertTrue(saved_zc_report.exists())
        self.assertIn("agent-dev-lead", manage_rep["roles"]["preserved"])

    def test_stale_report_triggers_opportunistic_resurvey_without_full_reinit(self):
        """
        Scenario 8: Staleness protocol triggers opportunistic re-survey without wiping config.
        Verifies that a commit delta between report git_state and HEAD is detected as stale,
        and re-surveying captures new commit without destroying existing knowledge slices or notes.
        """
        self._setup_healthy_repo()

        # Initialize git repository in self.root
        subprocess.run(["git", "init"], cwd=str(self.root), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Tester"], cwd=str(self.root), capture_output=True)
        subprocess.run(["git", "config", "user.email", "tester@test.local"], cwd=str(self.root), capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(self.root), capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(self.root), capture_output=True, check=True)

        git_state_1 = get_git_state(self.root)
        sha1 = git_state_1["commit_sha"]
        self.assertNotEqual(sha1, "unknown")

        # Generate initial report tied to sha1
        scenario = {"profile": "active_development", "collaboration_model": "triad"}
        init_rep = create_init_report(
            repo_root=self.root,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            status="completed",
            scenario=scenario,
        )
        saved_init = save_report(self.root, "ag-main", "init", init_rep)
        self.assertTrue(saved_init.exists())

        # Check staleness before second commit -> Not stale
        is_stale, stale_info = check_report_staleness(self.root, init_rep)
        self.assertFalse(is_stale)
        self.assertEqual(stale_info["current_commit"], sha1)
        self.assertEqual(stale_info["report_commit"], sha1)

        # Make a second commit
        new_file = self.root / "src" / "feature.py"
        new_file.parent.mkdir(parents=True, exist_ok=True)
        new_file.write_text("# New feature\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(self.root), capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "Second commit"], cwd=str(self.root), capture_output=True, check=True)

        git_state_2 = get_git_state(self.root)
        sha2 = git_state_2["commit_sha"]
        self.assertNotEqual(sha1, sha2)

        # Check staleness after second commit -> Stale!
        is_stale_after, stale_info_after = check_report_staleness(self.root, init_rep)
        self.assertTrue(is_stale_after)
        self.assertEqual(stale_info_after["report_commit"], sha1)
        self.assertEqual(stale_info_after["current_commit"], sha2)

        # Snapshot critical knowledge slices before opportunistic update
        passport_content = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        boundaries_content = (self.root / ".agents" / "project_knowledge" / "boundaries.md").read_text(encoding="utf-8")
        tasks_content = (self.root / ".agents" / "project_knowledge" / "tasks.md").read_text(encoding="utf-8")
        notes_content = (self.root / ".agents" / "team" / "agent-dev-lead" / "notes.md").read_text(encoding="utf-8")

        # Perform opportunistic resurvey without wipe
        updated_rep = create_init_report(
            repo_root=self.root,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            status="completed",
            scenario=scenario,
        )
        saved_updated = save_report(self.root, "ag-main", "init", updated_rep)
        self.assertTrue(saved_updated.exists())

        # Invariant 1: Updated report captures sha2
        self.assertEqual(updated_rep["git_state"]["commit_sha"], sha2)

        # Invariant 2: Staleness resolved on updated report
        is_stale_new, _ = check_report_staleness(self.root, updated_rep)
        self.assertFalse(is_stale_new)

        # Invariant 3: Zero destruction of existing knowledge slices and notes
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8"), passport_content)
        self.assertEqual((self.root / ".agents" / "project_knowledge" / "boundaries.md").read_text(encoding="utf-8"), boundaries_content)
        self.assertEqual((self.root / ".agents" / "project_knowledge" / "tasks.md").read_text(encoding="utf-8"), tasks_content)
        self.assertEqual((self.root / ".agents" / "team" / "agent-dev-lead" / "notes.md").read_text(encoding="utf-8"), notes_content)

if __name__ == '__main__':
    unittest.main()
