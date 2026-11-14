#!/usr/bin/env python3
"""
Acceptance Test Suite for Meta-Project Lifecycle Scenarios (Zero External Dependencies).

Verifies the 9 mandatory acceptance scenarios defined in the Universal Repository Adoption Plan:
- Scenario 1 (empty project): Empty repository -> NONE, recommended_action=scaffold_clean.
- Scenario 2 (foreign instructions): Foreign instructions (CLAUDE.md, .cursorrules, foreign AGENTS.md)
  -> FOREIGN_RULES, preserve_and_merge, foreign files 100% intact.
- Scenario 3 (healthy registered zero diff): Repeat run on healthy registered harness
  -> HEALTHY_REGISTERED, pass_through, 0 diff, 0 locks/junk files.
- Scenario 4 (healthy new harness): Connecting new or planned harness -> HEALTHY_NEW_HARNESS,
  bind_harness, active installations preserved without deactivation.
- Scenario 5 (legacy unregistered): Legacy setup without meta-project.json -> LEGACY_UNREGISTERED,
  adopt_legacy, history in tasks.md and observations.md preserved.
- Scenario 6 (partial corrupted): Corrupted repository (missing boundaries / malformed JSON)
  -> PARTIAL_CORRUPTED, diagnose_and_repair, exact discrepancies reported.
- Scenario 7 (read-only mode): Run with --read-only -> audit succeeds with strictly 0 writes on disk.
- Scenario 8 (git worktree): Execution in a git worktree -> correctly detected with parent git_toplevel.
- Scenario 9 (readme entry without skills): Agent navigation via self-contained AGENTS.md
  and local stdlib CLIs when global environment skills are absent.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
INSPECT_SCRIPT = SCRIPTS_DIR / "inspect_meta_project.py"
VERIFY_SCRIPT = SCRIPTS_DIR / "verify_identity.py"
BOUNDARIES_SCRIPT = SCRIPTS_DIR / "check_boundaries.py"


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
                            "actor_id": f"vlv-code/test::zcode::zc-main::agent-dev-lead",
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

        res = self._run_inspect(["--repo-root", str(self.root), "--read-only", "--json"])
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")

        # Also run in human-readable mode with --read-only
        res_human = self._run_inspect(["--repo-root", str(self.root), "--read-only"])
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
            [sys.executable, str(INSPECT_SCRIPT), "--json"],
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


if __name__ == "__main__":
    unittest.main()
