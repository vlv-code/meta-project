#!/usr/bin/env python3
"""Canonical domain test suite for inspect_meta_project (scripts/inspect_meta_project.py).

Consolidated in Wave T (Lane T2) from:
- tests/test_inspect_meta_project.py
- tests/test_gwave_i.py
- tests/test_jwave_q.py
- tests/test_lwave_topology.py

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import inspect_meta_project
from scripts.inspect_meta_project import (
    FACTS_DIGEST_VERSION,
    compute_facts_digest,
    detect_cross_harness_divergence,
    detect_host_harness,
    format_human_report,
    inspect_repository,
)
from scripts.verify_identity import (
    validate_identity_registry,
)

SCRIPT_PATH = REPO_ROOT / "scripts" / "inspect_meta_project.py"
SLICE_PATHS = (
    ".agents/project_knowledge/architecture.md",
    ".agents/project_knowledge/boundaries.md",
    ".agents/project_knowledge/weak_spots.md",
    ".agents/project_knowledge/observations.md",
    ".agents/project_knowledge/tasks.md",
    ".agents/meta-project.json",
)

PROJECT_ID = "acme/app"
HARNESS = "zcode"
INSTALLATION = "t9"
ACTOR_ID = f"{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-dev-lead"
_ABSENT = object()


def _write_minimal_metaproject(
    root: Path, active_harness: str = "antigravity", active_installation: str = "ag-main"
) -> None:
    agents_md = root / "AGENTS.md"
    agents_md.write_text(
        "# Project Passport: Test\n## 1. Concept, Principles, and North Stars\n"
        "## 3. Directive Meta-Knowledge Protocol\n## 6. Project Agent Team & Multi-Harness Identity\n",
        encoding="utf-8",
    )
    pk = root / ".agents" / "project_knowledge"
    pk.mkdir(parents=True)
    (pk / "boundaries.md").write_text("# Responsibility Zones\n## Green Zone\n- src/**\n", encoding="utf-8")
    (pk / "tasks.md").write_text("# Tasks\n- [x] Step 1\n", encoding="utf-8")
    (pk / "observations.md").write_text("# Obs\n| Date | Cat | Comp | Obs | Sol |\n", encoding="utf-8")
    (pk / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    (pk / "weak_spots.md").write_text("# Weak spots\n", encoding="utf-8")

    scripts_dir = root / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "check_boundaries.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    (scripts_dir / "verify_identity.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    skills_dir = root / ".agents" / "skills" / "record-observation"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("---\nname: record-observation\n---\n# Skill\n", encoding="utf-8")

    team_dir = root / ".agents" / "team" / "agent-dev-lead"
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
    (root / ".agents" / "meta-project.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_snapshot(root: Path) -> dict:
    snap = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            snap[str(p.relative_to(root))] = _sha256_file(p)
    return snap


def _make_fixture(root: Path, orchestration) -> None:
    agents_md = root / "AGENTS.md"
    agents_md.write_text(
        "# Project Passport: Test\n## 1. Concept, Principles, and North Stars\n"
        "## 3. Directive Meta-Knowledge Protocol\n## 6. Project Agent Team & Multi-Harness Identity\n",
        encoding="utf-8",
    )
    pk = root / ".agents" / "project_knowledge"
    pk.mkdir(parents=True)
    (pk / "boundaries.md").write_text(
        "# Responsibility Zones\n## Green Zone\n- src/**\n", encoding="utf-8"
    )
    (pk / "tasks.md").write_text("# Tasks\n- [x] Step 1\n", encoding="utf-8")
    (pk / "observations.md").write_text(
        "# Obs\n| Date | Cat | Comp | Obs | Sol |\n", encoding="utf-8"
    )
    (pk / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    (pk / "weak_spots.md").write_text("# Weak spots\n", encoding="utf-8")

    scripts_dir = root / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "check_boundaries.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )
    (scripts_dir / "verify_identity.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )

    skills_dir = root / ".agents" / "skills" / "record-observation"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text(
        "---\nname: record-observation\n---\n# Skill\n", encoding="utf-8"
    )

    team_dir = root / ".agents" / "team" / "agent-dev-lead"
    team_dir.mkdir(parents=True)
    (team_dir / "profile.md").write_text(
        f"---\nrole_id: agent-dev-lead\nharness_id: {HARNESS}\n"
        f"installation_id: {INSTALLATION}\nactor_id: {ACTOR_ID}\n---\n",
        encoding="utf-8",
    )

    installation = {
        "harness_id": HARNESS,
        "status": "active",
        "description": "Active installation",
    }
    if orchestration is not _ABSENT:
        installation["orchestration"] = orchestration
    registry = {
        "schema_version": "1.1.0",
        "project_id": PROJECT_ID,
        "installations": {
            INSTALLATION: installation,
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
                    INSTALLATION: {
                        "actor_id": ACTOR_ID,
                        "status": "active",
                        "profile_path": ".agents/team/agent-dev-lead/profile.md",
                    },
                    "zc-main": {
                        "actor_id": f"{PROJECT_ID}::zcode::zc-main::agent-dev-lead",
                        "status": "planned",
                        "profile_path": None,
                    },
                },
            }
        },
    }
    (root / ".agents" / "meta-project.json").write_text(
        json.dumps(registry, indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# TestInspectMetaProject (from tests/test_inspect_meta_project.py)
# ---------------------------------------------------------------------------
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
        _write_minimal_metaproject(self.root, active_harness, active_installation)
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


# ---------------------------------------------------------------------------
# TestDetectHostHarness (from tests/test_inspect_meta_project.py)
# ---------------------------------------------------------------------------
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

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_inspect_")
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

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
        with NO host-mismatch WARNING on stderr. Self-contained fixture:
        the audited repo carries its own registry with an active zcode
        installation, so the contract holds on any branch (dist included)."""
        import json
        import os
        import subprocess

        _write_minimal_metaproject(self.root, active_harness="zcode", active_installation="zc-test")
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(
                ("ANTIGRAVITY_", "AGY_", "CURSOR_", "CLAUDE_", "CODEX_", "ZCODE_")
            )
        }
        env["ZCODE_PROJECT_DIR"] = str(self.root)
        env["ZCODE_SESSION_ID"] = "sess_test_fixture"
        proc = subprocess.run(
            [
                sys.executable, "-B",
                str(REPO_ROOT / "scripts" / "inspect_meta_project.py"),
                "--json", "--harness", "auto", "--repo-root", str(self.root),
            ],
            capture_output=True, text=True, cwd=str(self.root), env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report.get("state"), "HEALTHY_REGISTERED", proc.stderr)
        self.assertNotIn("WARNING", proc.stderr, proc.stderr)
        self.assertNotIn("contradicts", proc.stderr, proc.stderr)


# ---------------------------------------------------------------------------
# TestFactsDigest (from tests/test_gwave_i.py)
# ---------------------------------------------------------------------------
class TestFactsDigest(unittest.TestCase):
    """--facts-digest: deterministic, sensitive, zero-write, composable."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_gwave_i_")
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_minimal_metaproject(
        self, active_harness: str = "antigravity", active_installation: str = "ag-main"
    ) -> None:
        """Fixture reused from tests/test_inspect_meta_project.py (same
        structure; its registry passes the canonical identity validator)."""
        agents_md = self.root / "AGENTS.md"
        agents_md.write_text(
            "# Project Passport: Test\n## 1. Concept, Principles, and North Stars\n"
            "## 3. Directive Meta-Knowledge Protocol\n## 6. Project Agent Team & Multi-Harness Identity\n",
            encoding="utf-8",
        )
        pk = self.root / ".agents" / "project_knowledge"
        pk.mkdir(parents=True)
        (pk / "boundaries.md").write_text(
            "# Responsibility Zones\n## Green Zone\n- src/**\n", encoding="utf-8"
        )
        (pk / "tasks.md").write_text("# Tasks\n- [x] Step 1\n", encoding="utf-8")
        (pk / "observations.md").write_text(
            "# Obs\n| Date | Cat | Comp | Obs | Sol |\n", encoding="utf-8"
        )
        (pk / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
        (pk / "weak_spots.md").write_text("# Weak spots\n", encoding="utf-8")

        scripts_dir = self.root / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "check_boundaries.py").write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )
        (scripts_dir / "verify_identity.py").write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )

        skills_dir = self.root / ".agents" / "skills" / "record-observation"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            "---\nname: record-observation\n---\n# Skill\n", encoding="utf-8"
        )

        team_dir = self.root / ".agents" / "team" / "agent-dev-lead"
        team_dir.mkdir(parents=True)
        (team_dir / "profile.md").write_text(
            f"---\nrole_id: agent-dev-lead\nharness_id: {active_harness}\n"
            f"installation_id: {active_installation}\n"
            f"actor_id: vlv-code/test-project::{active_harness}::{active_installation}::agent-dev-lead\n---\n",
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
                            "actor_id": (
                                f"vlv-code/test-project::{active_harness}"
                                f"::{active_installation}::agent-dev-lead"
                            ),
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
        (self.root / ".agents" / "meta-project.json").write_text(
            json.dumps(registry, indent=2), encoding="utf-8"
        )

    def _run_digest(self, extra_args=None, cwd=None) -> subprocess.CompletedProcess:
        cmd = [sys.executable, "-B", str(SCRIPT_PATH), "--repo-root", str(self.root), "--facts-digest"]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def _digest_payload(self, extra_args=None) -> dict:
        proc = self._run_digest(extra_args)
        self.assertEqual(
            proc.returncode, 0, f"rc={proc.returncode}, stderr={proc.stderr}"
        )
        return json.loads(proc.stdout)

    # ------------------------------------------------------------------
    # Determinism (RED-first: two consecutive runs byte-identical)
    # ------------------------------------------------------------------
    def test_digest_two_consecutive_runs_byte_identical(self):
        self._create_minimal_metaproject()
        first = self._run_digest()
        second = self._run_digest()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            first.stdout,
            second.stdout,
            "facts digest must be byte-stable for identical inputs",
        )

    def test_digest_shape_and_version_constant(self):
        self._create_minimal_metaproject()
        data = self._digest_payload()
        self.assertEqual(data["facts_digest_version"], "1")
        self.assertEqual(data["facts_digest_version"], FACTS_DIGEST_VERSION)
        # Exact top-level key set — the digest is a stable contract, no
        # opportunistic extra keys (byte-stability depends on it).
        self.assertEqual(
            sorted(data.keys()),
            ["capabilities", "facts_digest_version", "harness", "installation", "slices", "state"],
        )
        self.assertEqual(sorted(data["slices"].keys()), sorted(SLICE_PATHS))
        self.assertEqual(
            sorted(data["capabilities"].keys()),
            ["hooks", "local_checks", "read_instructions", "roles", "skills"],
        )
        for cap in data["capabilities"].values():
            self.assertIsInstance(cap, str)
        for rel in SLICE_PATHS:
            digest_value = data["slices"][rel]
            self.assertIsInstance(digest_value, str)
            self.assertEqual(digest_value, _sha256_file(self.root / rel))

    # ------------------------------------------------------------------
    # Absent slices -> null
    # ------------------------------------------------------------------
    def test_digest_absent_slices_null_on_empty_repo(self):
        data = self._digest_payload()
        self.assertEqual(data["state"], "NONE")
        self.assertEqual(data["facts_digest_version"], "1")
        for rel in SLICE_PATHS:
            self.assertIsNone(data["slices"][rel], f"{rel} must be null when absent")

    # ------------------------------------------------------------------
    # Sensitivity: one modified slice -> exactly that hash flips
    # ------------------------------------------------------------------
    def test_digest_single_slice_flip_sensitivity(self):
        self._create_minimal_metaproject()
        before = self._digest_payload()
        # Modify exactly one knowledge slice (classification-safe append).
        tasks_path = self.root / ".agents" / "project_knowledge" / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8") + "- [ ] new step\n",
            encoding="utf-8",
        )
        after = self._digest_payload()
        changed = {
            rel for rel in SLICE_PATHS if before["slices"][rel] != after["slices"][rel]
        }
        self.assertEqual(
            changed,
            {".agents/project_knowledge/tasks.md"},
            "exactly the modified slice's hash must flip",
        )
        self.assertEqual(
            after["slices"][".agents/project_knowledge/tasks.md"],
            _sha256_file(tasks_path),
        )
        # The rest of the digest is unchanged (state classification included).
        self.assertEqual(before["state"], after["state"])
        self.assertEqual(before["capabilities"], after["capabilities"])

    # ------------------------------------------------------------------
    # Zero-write invariant (survey-first, no disk cache)
    # ------------------------------------------------------------------
    def test_digest_zero_write_invariant(self):
        self._create_minimal_metaproject()
        before = _tree_snapshot(self.root)
        proc = self._run_digest(["--read-only"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = _tree_snapshot(self.root)
        self.assertEqual(
            before,
            after,
            "--facts-digest must produce zero disk modifications "
            "(no lock files, no disk cache, no telemetry)",
        )

    # ------------------------------------------------------------------
    # Context-unresolved behavior (digest describes the REPOSITORY)
    # ------------------------------------------------------------------
    def test_digest_context_unresolved_without_flags(self):
        self._create_minimal_metaproject()
        data = self._digest_payload()
        self.assertEqual(data["state"], "CONTEXT_UNRESOLVED")
        self.assertIsNone(data["harness"])
        self.assertIsNone(data["installation"])
        self.assertEqual(data["capabilities"]["roles"], "untested")

    # ------------------------------------------------------------------
    # Compositability with --harness/--installation
    # ------------------------------------------------------------------
    def test_digest_composable_with_context_flags(self):
        self._create_minimal_metaproject()
        args = ["--harness", "antigravity", "--installation", "ag-main"]
        first = self._run_digest(args)
        second = self._run_digest(args)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            first.stdout,
            second.stdout,
            "digest with context flags must also be byte-stable",
        )
        data = json.loads(first.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")
        self.assertEqual(data["harness"], "antigravity")
        self.assertEqual(data["installation"], "ag-main")
        self.assertEqual(data["capabilities"]["roles"], "available")

    def test_digest_function_is_pure_and_ordered(self):
        """compute_facts_digest returns the payload without touching disk
        beyond reading slices, and the CLI serializes it deterministically
        (sort_keys + fixed separators)."""
        self._create_minimal_metaproject()
        from scripts.inspect_meta_project import inspect_repository

        report = inspect_repository(self.root)
        digest = compute_facts_digest(self.root, report)
        canonical = json.dumps(
            digest, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        # Same serialization the CLI emits (module-level contract, not a
        # call-site choice).
        proc = self._run_digest()
        self.assertEqual(proc.stdout.strip(), canonical)


# ---------------------------------------------------------------------------
# TestInspectDocstringCanon (from tests/test_gwave_i.py)
# ---------------------------------------------------------------------------
class TestInspectDocstringCanon(unittest.TestCase):
    """Auditor doc-contradiction #3: the module docstring said 7 canonical
    states while the code implements 8 (CONTEXT_UNRESOLVED included)."""

    def test_docstring_lists_eight_canonical_states(self):
        doc = (REPO_ROOT / "scripts" / "inspect_meta_project.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("8 canonical states", doc)
        self.assertIn("CONTEXT_UNRESOLVED", doc)
        self.assertNotIn("7 canonical states", doc)


# ---------------------------------------------------------------------------
# TestOrchestrationReporting (from tests/test_jwave_q.py)
# ---------------------------------------------------------------------------
class TestOrchestrationReporting(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="jwave_q_")
        self.root = Path(self.temp_dir).resolve()
        # Accessed via the module object so a RED-state AttributeError lands
        # on the individual tests instead of failing module import.
        self.resolve_orchestration = inspect_meta_project.resolve_orchestration

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- helper outcomes (tests 14-17) --------------------------------------

    def test_resolve_orchestration_none_without_context(self):
        """Falsy installation id or unknown/non-object entry -> None."""
        self.assertIsNone(self.resolve_orchestration({}, "t9"))
        self.assertIsNone(self.resolve_orchestration({INSTALLATION: {}}, None))
        self.assertIsNone(self.resolve_orchestration({INSTALLATION: {}}, ""))
        self.assertIsNone(self.resolve_orchestration({INSTALLATION: {}}, "ghost"))
        # A non-object installation entry is not a declared context either.
        self.assertIsNone(self.resolve_orchestration({INSTALLATION: "x"}, INSTALLATION))
        self.assertIsNone(self.resolve_orchestration(None, INSTALLATION))

    def test_resolve_orchestration_default_when_not_declared(self):
        installations = {
            INSTALLATION: {"harness_id": HARNESS, "status": "active"},
        }
        self.assertEqual(
            self.resolve_orchestration(installations, INSTALLATION),
            {
                "installation": INSTALLATION,
                "native_orchestrator": None,
                "dispatcher_binding": "standalone",
                "dispatcher_binding_source": "default",
            },
        )
        # Explicit null block means "not declared" as well.
        installations[INSTALLATION]["orchestration"] = None
        self.assertEqual(
            self.resolve_orchestration(installations, INSTALLATION),
            {
                "installation": INSTALLATION,
                "native_orchestrator": None,
                "dispatcher_binding": "standalone",
                "dispatcher_binding_source": "default",
            },
        )

    def test_resolve_orchestration_invalid_block(self):
        for malformed in ("hosted", ["x"]):
            with self.subTest(block=malformed):
                installations = {
                    INSTALLATION: {
                        "harness_id": HARNESS,
                        "status": "active",
                        "orchestration": malformed,
                    },
                }
                self.assertEqual(
                    self.resolve_orchestration(installations, INSTALLATION),
                    {
                        "installation": INSTALLATION,
                        "native_orchestrator": None,
                        "dispatcher_binding": None,
                        "dispatcher_binding_source": "invalid",
                    },
                )

    def test_resolve_orchestration_registry_declared_variants(self):
        base = {"harness_id": HARNESS, "status": "active"}
        # native True + orchestrator-hosted
        declared = dict(base)
        declared["orchestration"] = {
            "native_orchestrator": True,
            "dispatcher_binding": "orchestrator-hosted",
        }
        self.assertEqual(
            self.resolve_orchestration({INSTALLATION: declared}, INSTALLATION),
            {
                "installation": INSTALLATION,
                "native_orchestrator": True,
                "dispatcher_binding": "orchestrator-hosted",
                "dispatcher_binding_source": "registry",
            },
        )
        # native False declared
        declared = dict(base)
        declared["orchestration"] = {
            "native_orchestrator": False,
            "dispatcher_binding": "standalone",
        }
        self.assertEqual(
            self.resolve_orchestration({INSTALLATION: declared}, INSTALLATION),
            {
                "installation": INSTALLATION,
                "native_orchestrator": False,
                "dispatcher_binding": "standalone",
                "dispatcher_binding_source": "registry",
            },
        )
        # binding declared alone (native absent -> None)
        declared = dict(base)
        declared["orchestration"] = {"dispatcher_binding": "standalone"}
        self.assertEqual(
            self.resolve_orchestration({INSTALLATION: declared}, INSTALLATION),
            {
                "installation": INSTALLATION,
                "native_orchestrator": None,
                "dispatcher_binding": "standalone",
                "dispatcher_binding_source": "registry",
            },
        )
        # Malformed binding value inside an otherwise valid registry falls
        # back to standalone/default without raising.
        declared = dict(base)
        declared["orchestration"] = {
            "native_orchestrator": True,
            "dispatcher_binding": "HOSTED",
        }
        self.assertEqual(
            self.resolve_orchestration({INSTALLATION: declared}, INSTALLATION),
            {
                "installation": INSTALLATION,
                "native_orchestrator": True,
                "dispatcher_binding": "standalone",
                "dispatcher_binding_source": "default",
            },
        )

    # -- inspect_repository report key (tests 18-20) ------------------------

    def test_inspect_report_declared_orchestrator_hosted(self):
        _make_fixture(
            self.root,
            {
                "native_orchestrator": True,
                "dispatcher_binding": "orchestrator-hosted",
            },
        )
        report = inspect_repository(self.root, HARNESS, INSTALLATION)
        self.assertEqual(report["state"], "HEALTHY_REGISTERED", report["conflicts"])
        self.assertEqual(
            report["orchestration"]["dispatcher_binding"],
            "orchestrator-hosted",
        )
        self.assertEqual(
            report["orchestration"]["dispatcher_binding_source"], "registry"
        )
        self.assertTrue(report["orchestration"]["native_orchestrator"] is True)

    def test_inspect_report_default_when_not_declared(self):
        _make_fixture(self.root, _ABSENT)
        report = inspect_repository(self.root, HARNESS, INSTALLATION)
        self.assertEqual(report["state"], "HEALTHY_REGISTERED")
        self.assertEqual(
            report["orchestration"]["dispatcher_binding"], "standalone"
        )
        self.assertEqual(
            report["orchestration"]["dispatcher_binding_source"], "default"
        )

    def test_inspect_report_orchestration_none_without_context(self):
        _make_fixture(self.root, _ABSENT)
        report = inspect_repository(self.root)
        self.assertIn("orchestration", report)
        self.assertIsNone(report["orchestration"])

    # -- human-readable report (test 21) ------------------------------------

    def test_human_report_carries_dispatcher_binding_line(self):
        _make_fixture(
            self.root,
            {
                "native_orchestrator": True,
                "dispatcher_binding": "orchestrator-hosted",
            },
        )
        declared_report = inspect_repository(self.root, HARNESS, INSTALLATION)
        declared_lines = format_human_report(declared_report).splitlines()
        self.assertTrue(
            any(line.startswith("Dispatcher Binding:") for line in declared_lines),
            "human report must contain a 'Dispatcher Binding:' line "
            "(declared case); got:\n" + "\n".join(declared_lines),
        )
        self.assertTrue(
            any(
                "orchestrator-hosted" in line and "declared in the registry" in line
                for line in declared_lines
            ),
            "declared case must name the binding and its registry source",
        )

        default_root = self.root.parent / (
            self.root.name + "_default"
        )
        default_root.mkdir(parents=True, exist_ok=True)
        _make_fixture(default_root, _ABSENT)
        default_report = inspect_repository(default_root, HARNESS, INSTALLATION)
        default_lines = format_human_report(default_report).splitlines()
        self.assertTrue(
            any(line.startswith("Dispatcher Binding:") for line in default_lines),
            "human report must contain a 'Dispatcher Binding:' line "
            "(default case); got:\n" + "\n".join(default_lines),
        )
        self.assertTrue(
            any("standalone" in line and "default" in line for line in default_lines),
            "default case must describe the standalone fallback",
        )


# ---------------------------------------------------------------------------
# TestCrossHarnessTopologyDivergence (from tests/test_lwave_topology.py)
# ---------------------------------------------------------------------------
class TestCrossHarnessTopologyDivergence(unittest.TestCase):
    """Test detect_cross_harness_divergence and inspector reporting."""

    def test_detect_cross_harness_divergence_symmetric_or_single(self):
        self.assertIsNotNone(
            detect_cross_harness_divergence, "detect_cross_harness_divergence not defined"
        )
        # Single installation -> no divergence possible
        installations_single = {"inst-a": {"harness_id": "h-a", "status": "active"}}
        roles_single = {
            "role-1": {
                "bindings": {
                    "inst-a": {"status": "active", "actor_id": "p::h-a::inst-a::r1"}
                }
            }
        }
        res = detect_cross_harness_divergence(installations_single, roles_single)
        self.assertFalse(res["divergence_detected"])
        self.assertEqual(res["asymmetric_roles"], [])

        # Multiple installations, all roles symmetric
        installations_multi = {
            "inst-a": {"harness_id": "h-a", "status": "active"},
            "inst-b": {"harness_id": "h-b", "status": "active"},
        }
        roles_symmetric = {
            "role-1": {
                "bindings": {
                    "inst-a": {"status": "active", "actor_id": "p::h-a::inst-a::r1"},
                    "inst-b": {"status": "active", "actor_id": "p::h-b::inst-b::r1"},
                }
            }
        }
        res = detect_cross_harness_divergence(installations_multi, roles_symmetric)
        self.assertFalse(res["divergence_detected"])
        self.assertEqual(res["asymmetric_roles"], [])

    def test_detect_cross_harness_divergence_asymmetric(self):
        self.assertIsNotNone(
            detect_cross_harness_divergence, "detect_cross_harness_divergence not defined"
        )
        installations = {
            "ag-main": {"harness_id": "antigravity", "status": "active"},
            "zc-main": {"harness_id": "zcode", "status": "active"},
        }
        roles = {
            "agent-dev-lead": {
                "bindings": {
                    "ag-main": {"status": "active", "actor_id": "p::ag::ag-main::dev"},
                    "zc-main": {"status": "active", "actor_id": "p::zc::zc-main::dev"},
                }
            },
            "agent-intake-dispatcher": {
                "bindings": {
                    "ag-main": {"status": "active", "actor_id": "p::ag::ag-main::dispatcher"}
                }
            },
        }
        res = detect_cross_harness_divergence(installations, roles)
        self.assertTrue(res["divergence_detected"])
        self.assertEqual(len(res["asymmetric_roles"]), 1)
        asym = res["asymmetric_roles"][0]
        self.assertEqual(asym["role_id"], "agent-intake-dispatcher")
        self.assertEqual(asym["present_in"], ["ag-main"])
        self.assertEqual(asym["missing_in"], ["zc-main"])

    def test_inspect_repository_includes_cross_harness_keys(self):
        if not (REPO_ROOT / ".agents" / "meta-project.json").is_file():
            self.skipTest("dogfood-branch contract: requires live .agents/meta-project.json")
        self.assertIsNotNone(inspect_repository, "inspect_repository not defined")
        rep = inspect_repository(REPO_ROOT)
        self.assertIn("cross_harness_divergence", rep)
        self.assertIn("asymmetric_roles", rep)
        # In this repository, ag-main has 4 roles and zc-main has 3 roles
        self.assertTrue(rep["cross_harness_divergence"])
        asym_role_ids = [r["role_id"] for r in rep["asymmetric_roles"]]
        self.assertIn("agent-intake-dispatcher", asym_role_ids)

    def test_format_human_report_cross_harness_output(self):
        if not (REPO_ROOT / ".agents" / "meta-project.json").is_file():
            self.skipTest("dogfood-branch contract: requires live .agents/meta-project.json")
        self.assertIsNotNone(format_human_report, "format_human_report not defined")
        rep = inspect_repository(REPO_ROOT)
        output = format_human_report(rep)
        self.assertIn("Cross-Harness Roles: asymmetric", output)
        self.assertIn("agent-intake-dispatcher", output)

    def test_facts_digest_invariance(self):
        if not (REPO_ROOT / ".agents" / "meta-project.json").is_file():
            self.skipTest("dogfood-branch contract: requires live .agents/meta-project.json")
        self.assertIsNotNone(compute_facts_digest, "compute_facts_digest not defined")
        rep = inspect_repository(REPO_ROOT)
        digest = compute_facts_digest(REPO_ROOT, rep)
        expected_keys = {
            "capabilities",
            "facts_digest_version",
            "harness",
            "installation",
            "slices",
            "state",
        }
        self.assertEqual(
            set(digest.keys()),
            expected_keys,
            "compute_facts_digest top-level keys must remain strictly invariant",
        )


# ---------------------------------------------------------------------------
# TestPerInstallationCollaborationModel (from tests/test_lwave_topology.py)
# ---------------------------------------------------------------------------
class TestPerInstallationCollaborationModel(unittest.TestCase):
    """Test validation of optional installations.<id>.collaboration_model."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_collab_"))
        self.agents_dir = self.temp_dir / ".agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.team_dir = self.agents_dir / "team"
        self.team_dir.mkdir(parents=True, exist_ok=True)

        # Basic role profile
        rdir = self.team_dir / "agent-worker"
        rdir.mkdir(parents=True, exist_ok=True)
        (rdir / "profile.md").write_text(
            "---\nrole_id: agent-worker\ninvocation_triggers:\n  - work\n---\n# Worker\n",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_collaboration_model_passes(self):
        self.assertIsNotNone(validate_identity_registry, "validate_identity_registry not defined")
        reg = {
            "schema_version": "1.1.0",
            "project_id": "test-repo",
            "installations": {
                "ag-main": {
                    "harness_id": "antigravity",
                    "status": "active",
                    "collaboration_model": "quad",
                },
                "zc-main": {
                    "harness_id": "zcode",
                    "status": "active",
                    "collaboration_model": "triad",
                },
            },
            "roles": {
                "agent-worker": {
                    "description": "Worker",
                    "bindings": {
                        "ag-main": {
                            "actor_id": "test-repo::antigravity::ag-main::agent-worker",
                            "status": "active",
                            "profile_path": ".agents/team/agent-worker/profile.md",
                        }
                    },
                }
            },
        }
        reg_file = self.agents_dir / "meta-project.json"
        reg_file.write_text(json.dumps(reg, indent=2), encoding="utf-8")

        is_valid, errors = validate_identity_registry(self.temp_dir)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [], f"Unexpected validation errors: {errors}")

    def test_resolve_team_topology_supports_quad(self):
        from manage_reports import resolve_team_topology
        res = resolve_team_topology({"profile": "active_development", "collaboration_model": "quad"})
        self.assertEqual(res["target_topology"], "quad")
        self.assertTrue(res["supported"])
        self.assertEqual(
            res["suggested_roles"],
            [
                "agent-intake-dispatcher",
                "agent-dev-lead",
                "agent-quality-guardian",
                "agent-github-steward",
            ],
        )

    def test_invalid_collaboration_model_fails(self):
        self.assertIsNotNone(validate_identity_registry, "validate_identity_registry not defined")
        reg = {
            "schema_version": "1.1.0",
            "project_id": "test-repo",
            "installations": {
                "ag-main": {
                    "harness_id": "antigravity",
                    "status": "active",
                    "collaboration_model": "invalid_model_abc",
                }
            },
            "roles": {
                "agent-worker": {
                    "description": "Worker",
                    "bindings": {
                        "ag-main": {
                            "actor_id": "test-repo::antigravity::ag-main::agent-worker",
                            "status": "active",
                            "profile_path": ".agents/team/agent-worker/profile.md",
                        }
                    },
                }
            },
        }
        reg_file = self.agents_dir / "meta-project.json"
        reg_file.write_text(json.dumps(reg, indent=2), encoding="utf-8")

        is_valid, errors = validate_identity_registry(self.temp_dir)
        self.assertFalse(is_valid)
        self.assertTrue(
            any("unsupported collaboration_model 'invalid_model_abc'" in e for e in errors),
            f"Expected error about invalid collaboration_model, got: {errors}",
        )


# ---------------------------------------------------------------------------
# TestManageSkillWaveLContracts (from tests/test_lwave_topology.py)
# ---------------------------------------------------------------------------
class TestManageSkillWaveLContracts(unittest.TestCase):
    """Verify manage-meta-project/SKILL.md line budget and Wave L protocol."""

    def test_manage_skill_under_240_lines(self):
        skill_path = REPO_ROOT / "skills/manage-meta-project/SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertLessEqual(
            len(lines),
            240,
            f"skills/manage-meta-project/SKILL.md exceeded 240 lines ({len(lines)})",
        )

    def test_manage_skill_contains_duty_deconfliction_and_asymmetry(self):
        skill_path = REPO_ROOT / "skills/manage-meta-project/SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        for token in (
            "detect_role_duty_conflicts",
            "deconflict",
            "keep-as-is",
            "mirror-to-harness",
        ):
            self.assertIn(token, text, f"Missing {token!r} in manage-meta-project/SKILL.md")


# ---------------------------------------------------------------------------
# TestAgentsMdSection7Annotations (from tests/test_lwave_topology.py)
# ---------------------------------------------------------------------------
class TestAgentsMdSection7Annotations(unittest.TestCase):
    """Verify Section 7 in AGENTS.md annotates role bindings to installations."""

    def test_section_7_role_annotations(self):
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(
            "[Intake Dispatcher](.agents/team/agent-intake-dispatcher/profile.md) [ag-main]",
            agents_md,
        )
        self.assertIn(
            "[Lead Developer](.agents/team/agent-dev-lead/profile.md) [ag-main, zc-main]",
            agents_md,
        )
        self.assertIn(
            "[Quality & Meta-Architecture Guardian](.agents/team/agent-quality-guardian/profile.md) [ag-main, zc-main]",
            agents_md,
        )
        self.assertIn(
            "[GitHub Steward & Release Captain](.agents/team/agent-github-steward/profile.md) [ag-main, zc-main]",
            agents_md,
        )


if __name__ == "__main__":
    unittest.main()
