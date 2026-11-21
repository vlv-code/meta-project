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
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.inspect_meta_project import (
    detect_host_harness,
    format_human_report,
    inspect_repository,
)


class TestInspectMetaProject(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_inspect_")
        self.root = Path(self.test_dir)
        self.script_path = (
            Path(__file__).resolve().parent.parent / "scripts" / "inspect_meta_project.py"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_inspect(self, args=None, cwd=None, env=None):
        cmd = [sys.executable, str(self.script_path)]
        if args:
            cmd.extend(args)
        proc = subprocess.run(
            cmd,
            cwd=cwd or str(self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
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
            f"installation_id: {active_installation}\nactor_id: vlv-code/test-project::{active_harness}::{active_installation}::agent-dev-lead\n---\n",
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
                            "actor_id": f"vlv-code/test-project::{active_harness}::{active_installation}::agent-dev-lead",
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        },
                        "zc-main": {
                            "actor_id": "vlv-code/test-project::zcode::zc-main::agent-dev-lead",
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
    # Scenario and Latest Init Report Inspection
    # -------------------------------------------------------------------------
    def test_inspector_surfaces_agreed_scenario_and_latest_init_report(self):
        self._create_minimal_metaproject()

        # Update meta-project.json with schema 1.1.0 and scenario block
        registry_path = self.root / ".agents" / "meta-project.json"
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        registry["schema_version"] = "1.1.0"
        registry["scenario"] = {
            "profile": "active_development",
            "deployment_mode": "shared_repo",
            "collaboration_model": "triad",
            "verification_policy": "strict_independent",
            "delegation_level": "controlled",
            "constraints": ["zero_dependency_core", "fail_closed_boundaries"],
            "unresolved_questions": [],
        }
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        # Create latest init report
        reports_dir = self.root / ".agents" / "reports" / "ag-main" / "init"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_data = {
            "schema_version": "1.0.0",
            "report_type": "init",
            "project_id": "vlv-code/meta-project",
            "installation_id": "ag-main",
            "harness_id": "antigravity",
            "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "run_id": "20261115T005300Z-a1b2c3d4",
            "created_at": "2026-11-15T00:53:00Z",
            "status": "completed",
            "git_state": {"commit_sha": "abc", "branch": "main", "is_clean": True, "modified_files": []},
            "scenario": registry["scenario"],
            "next_step_readiness": {"ready_for_manage": True},
        }
        report_file = reports_dir / "20261115T005300Z-a1b2c3d4.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        latest_pointer = reports_dir / "latest.json"
        with open(latest_pointer, "w", encoding="utf-8") as f:
            json.dump({
                "run_id": "20261115T005300Z-a1b2c3d4",
                "status": "completed",
                "created_at": "2026-11-15T00:53:00Z",
                "path": str(report_file.resolve()).replace("\\", "/"),
            }, f, indent=2)

        proc = self.run_inspect(["--repo-root", str(self.root), "--installation", "ag-main", "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)

        self.assertIn("scenario", data)
        self.assertEqual(data["scenario"]["profile"], "active_development")
        self.assertIn("latest_init_report", data)
        self.assertIsNotNone(data["latest_init_report"])
        self.assertEqual(data["latest_init_report"]["run_id"], "20261115T005300Z-a1b2c3d4")
        self.assertEqual(data["latest_init_report"]["status"], "completed")

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


    # -------------------------------------------------------------------------
    # Host Harness Detection & Runtime Safeguards
    # -------------------------------------------------------------------------
    def test_detect_host_harness_antigravity(self):
        for var in ("ANTIGRAVITY_AGENT", "ANTIGRAVITY_APP_DATA_DIR", "AGY_BROWSER_WS_URL"):
            with mock.patch.dict("os.environ", {var: "val"}, clear=True):
                self.assertEqual(detect_host_harness(), "antigravity", f"Failed for {var}")

    def test_detect_host_harness_zcode(self):
        for var in ("ZCODE_AGENT", "ZCODE_WORKSPACE"):
            with mock.patch.dict("os.environ", {var: "val"}, clear=True):
                self.assertEqual(detect_host_harness(), "zcode", f"Failed for {var}")

    def test_detect_host_harness_cursor(self):
        for var in ("CURSOR_AGENT", "CURSOR_TRACE", "CURSOR_VERSION"):
            with mock.patch.dict("os.environ", {var: "val"}, clear=True):
                self.assertEqual(detect_host_harness(), "cursor", f"Failed for {var}")

    def test_detect_host_harness_claude_code(self):
        for var in ("CLAUDE_CODE", "CLAUDE_PROJECT_DIR"):
            with mock.patch.dict("os.environ", {var: "val"}, clear=True):
                self.assertEqual(detect_host_harness(), "claude-code", f"Failed for {var}")

    def test_detect_host_harness_codex(self):
        # Mini-tail 2026-11-22: CODEX_HOME dropped — machine-scoped (user
        # installation leaks into any harness), attests nothing. The stricter
        # form lives in TestDetectHostHarness
        # (test_codex_home_alone_is_machine_noise_not_codex).
        for var in ("CODEX_AGENT",):
            with mock.patch.dict("os.environ", {var: "val"}, clear=True):
                self.assertEqual(detect_host_harness(), "codex", f"Failed for {var}")

    def test_detect_host_harness_none_when_empty(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(detect_host_harness())

    def test_runtime_mismatch_warning(self):
        self._create_minimal_metaproject()
        with mock.patch.dict("os.environ", {"ANTIGRAVITY_AGENT": "1"}, clear=True):
            # 1. Direct inspect_repository call
            report = inspect_repository(
                self.root,
                target_harness="zcode",
                target_installation="zc-main",
            )
            self.assertIn("host_mismatch_warning", report["runtime_context"])
            expected_msg = "CLI flag --harness 'zcode' contradicts detected host environment 'antigravity'"
            self.assertEqual(report["runtime_context"]["host_mismatch_warning"], expected_msg)

            # 2. Reflected in format_human_report
            human_text = format_human_report(report)
            self.assertIn(expected_msg, human_text)
            self.assertIn("[WARNING]", human_text)

        # 3. Reflected on stderr via CLI run
        base_env = dict(os.environ)
        for k in list(base_env.keys()):
            if k.startswith(("ZCODE_", "CURSOR_", "CLAUDE_", "CODEX_")):
                del base_env[k]
        base_env["ANTIGRAVITY_AGENT"] = "1"
        proc = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "zcode", "--installation", "zc-main"],
            env=base_env,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn(
            "CLI flag --harness 'zcode' contradicts detected host environment 'antigravity'",
            proc.stderr,
        )
        self.assertIn("[WARNING]", proc.stderr)

    def test_runtime_no_mismatch_warning_when_matching(self):
        self._create_minimal_metaproject()
        with mock.patch.dict("os.environ", {"ANTIGRAVITY_AGENT": "1"}, clear=True):
            report = inspect_repository(
                self.root,
                target_harness="antigravity",
                target_installation="ag-main",
            )
            self.assertNotIn("host_mismatch_warning", report["runtime_context"])

    def test_context_unresolved_safe_envelope_notice(self):
        self._create_minimal_metaproject()
        proc = self.run_inspect(["--repo-root", str(self.root), "--json"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "CONTEXT_UNRESOLVED")

        # Must have canonical leading line
        self.assertIn("[CONTEXT_UNRESOLVED] .agents/meta-project.json:", proc.stderr)
        self.assertIn("expected:", proc.stderr)
        self.assertIn("actual:", proc.stderr)
        self.assertIn("next:", proc.stderr)

        # Safe text verification: MUST NOT say 'see .agents/meta-project.json'
        self.assertNotIn("see .agents/meta-project.json", proc.stderr)

        # Must contain anti-anchoring instructions
        safe_phrase = (
            "specify --harness <id> matching your ACTUAL agent host runtime "
            "(e.g. antigravity, zcode, cursor, claude-code). DO NOT copy an active "
            "harness from .agents/meta-project.json! If your harness is not yet "
            "registered, this will correctly trigger HEALTHY_NEW_HARNESS."
        )
        self.assertIn(safe_phrase, proc.stderr)

    def test_harness_auto_resolution(self):
        self._create_minimal_metaproject()

        # Case A: Antigravity detected -> resolves to registered ag-main (HEALTHY_REGISTERED)
        base_env = dict(os.environ)
        for k in list(base_env.keys()):
            if k.startswith(("ANTIGRAVITY_", "AGY_", "ZCODE_", "CURSOR_", "CLAUDE_", "CODEX_")):
                del base_env[k]
        base_env["ANTIGRAVITY_AGENT"] = "1"

        proc = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "auto", "--json"],
            env=base_env,
        )
        self.assertEqual(proc.returncode, 0, f"Stderr: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")
        self.assertEqual(data["runtime_context"]["target_harness"], "antigravity")
        self.assertNotIn("host_mismatch_warning", data["runtime_context"])

        # Case B: ZCode detected -> resolves to planned zc-main (HEALTHY_NEW_HARNESS)
        base_env_zc = dict(os.environ)
        for k in list(base_env_zc.keys()):
            if k.startswith(("ANTIGRAVITY_", "AGY_", "ZCODE_", "CURSOR_", "CLAUDE_", "CODEX_")):
                del base_env_zc[k]
        base_env_zc["ZCODE_WORKSPACE"] = "/some/workspace"

        proc_zc = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "auto", "--json"],
            env=base_env_zc,
        )
        self.assertEqual(proc_zc.returncode, 0, f"Stderr: {proc_zc.stderr}")
        data_zc = json.loads(proc_zc.stdout)
        self.assertEqual(data_zc["state"], "HEALTHY_NEW_HARNESS")
        self.assertEqual(data_zc["runtime_context"]["target_harness"], "zcode")
        self.assertNotIn("host_mismatch_warning", data_zc["runtime_context"])

        # Case C: Unknown host -> resolves to None -> CONTEXT_UNRESOLVED
        base_env_none = dict(os.environ)
        for k in list(base_env_none.keys()):
            if k.startswith(("ANTIGRAVITY_", "AGY_", "ZCODE_", "CURSOR_", "CLAUDE_", "CODEX_")):
                del base_env_none[k]

        proc_none = self.run_inspect(
            ["--repo-root", str(self.root), "--harness", "auto", "--json"],
            env=base_env_none,
        )
        self.assertEqual(proc_none.returncode, 0, f"Stderr: {proc_none.stderr}")
        data_none = json.loads(proc_none.stdout)
        self.assertEqual(data_none["state"], "CONTEXT_UNRESOLVED")
        self.assertIsNone(data_none["runtime_context"]["target_harness"])

        # Direct function call with target_harness="auto"
        with mock.patch.dict("os.environ", {"ANTIGRAVITY_AGENT": "1"}, clear=True):
            direct_rep = inspect_repository(self.root, target_harness="auto")
            self.assertEqual(direct_rep["state"], "HEALTHY_REGISTERED")
            self.assertEqual(direct_rep["runtime_context"]["target_harness"], "antigravity")
            self.assertNotIn("host_mismatch_warning", direct_rep["runtime_context"])


class TestDetectHostHarness(unittest.TestCase):
    """Mini-tail (2026-11-22, weak_spots OPEN entry): host-detect false
    positive on a REAL ZCode desktop session. Adversarial env-fixture tests
    per the approved design:

    1. zcode signature refreshed to real session markers (ZCODE_PROJECT_DIR,
       ZCODE_SESSION_ID); ZCODE_AGENT/ZCODE_WORKSPACE kept as legacy
       fallback.
    2. zcode ordered BEFORE claude-code: ZCode desktop bridges
       CLAUDE_PROJECT_DIR/CLAUDE_SESSION_ID into its own sessions, so a
       bridge-equipped zcode session must still resolve "zcode"; a genuine
       claude-code session has claude vars WITHOUT ZCODE_*.
    3. CODEX_HOME removed from the codex signature: machine-scoped
       (user-level Codex installation leaks into any harness), not session
       evidence. CODEX_AGENT stays.
    """

    def test_genuine_zcode_session(self):
        env = {"ZCODE_PROJECT_DIR": "p", "ZCODE_SESSION_ID": "sess_x"}
        self.assertEqual(detect_host_harness(env=env), "zcode")

    def test_zcode_session_with_claude_bridge_stays_zcode(self):
        env = {
            "ZCODE_PROJECT_DIR": "p",
            "ZCODE_SESSION_ID": "sess_x",
            "CLAUDE_PROJECT_DIR": "p",
            "CLAUDE_SESSION_ID": "sess_x",
        }
        self.assertEqual(
            detect_host_harness(env=env), "zcode",
            "bridged claude vars inside a zcode session must not flip the "
            "detection to claude-code",
        )

    def test_genuine_claude_code_session(self):
        env = {"CLAUDE_PROJECT_DIR": "p", "CLAUDE_SESSION_ID": "sess_x"}
        self.assertEqual(detect_host_harness(env=env), "claude-code")

    def test_codex_home_alone_is_machine_noise_not_codex(self):
        env = {"CODEX_HOME": "C:/Users/x/.codex"}
        self.assertIsNone(
            detect_host_harness(env=env),
            "CODEX_HOME is machine-scoped (user installation) and must not "
            "attest a codex session",
        )

    def test_codex_agent_attests_codex(self):
        self.assertEqual(detect_host_harness(env={"CODEX_AGENT": "1"}), "codex")

    def test_antigravity_env_still_detected(self):
        self.assertEqual(
            detect_host_harness(env={"ANTIGRAVITY_AGENT": "1"}), "antigravity"
        )

    def test_empty_env_is_none(self):
        self.assertIsNone(detect_host_harness(env={}))

    def test_cli_auto_resolves_zcode_without_warning(self):
        """Integration (design requirement 8): --harness auto on a
        clean-room zcode session env resolves 'zcode' (HEALTHY_REGISTERED)
        with NO host-mismatch WARNING on stderr."""
        import json
        import os
        import subprocess

        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("CLAUDE_", "CODEX_"))
        }
        env["ZCODE_PROJECT_DIR"] = str(REPO_ROOT)
        env["ZCODE_SESSION_ID"] = "sess_test_fixture"
        proc = subprocess.run(
            [
                sys.executable, "-B",
                str(REPO_ROOT / "scripts" / "inspect_meta_project.py"),
                "--json", "--harness", "auto",
            ],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report.get("state"), "HEALTHY_REGISTERED", proc.stderr)
        self.assertNotIn("WARNING", proc.stderr, proc.stderr)
        self.assertNotIn("contradicts", proc.stderr, proc.stderr)


if __name__ == "__main__":
    unittest.main()

