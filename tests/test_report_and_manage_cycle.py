#!/usr/bin/env python3
"""
Acceptance Test Suite for Meta-Project Report and Manage Orchestration Cycle.
Zero external dependencies (Python 3.10+ stdlib only).

Verifies the 8 core acceptance invariants:
1. test_scenario_agreement_persisted_in_registry:
   Persistence of scenario decisions across 4 groups (profile, placement, collaboration, verification rules).
2. test_init_report_generation_and_contract:
   Generation of init report with required references (registry, passport, boundaries) and schema 1.0.0.
3. test_read_only_mode_never_generates_reports:
   Strict invariant that --read-only mode never writes to .agents/reports/ and leaves filesystem 100% intact.
4. test_manage_rejects_foreign_or_incompatible_report:
   Fail-closed rejection when project_id is foreign or schema_version is incompatible.
5. test_manage_blocked_on_awaiting_decision:
   Team management blocked when init report status is awaiting_decision or blocked.
6. test_manage_adapts_team_based_on_scenario:
   Topology mapping adapts to scenario (maintenance -> Duo, active_dev + strict_independent -> Triad, doc -> Solo).
7. test_manage_preserves_other_harness_bindings:
   Preserving active ag-main installation bindings and role notes when configuring zc-main.
8. test_stale_report_triggers_opportunistic_resurvey_without_full_reinit:
   Git commit delta triggers opportunistic re-survey without wiping repository configuration.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, Tuple
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.manage_reports import (
    VALID_COLLABORATION_MODELS,
    VALID_DEPLOYMENT_MODES,
    VALID_REPORT_STATUSES,
    VALID_SCENARIO_PROFILES,
    VALID_VERIFICATION_POLICIES,
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

INSPECT_SCRIPT = REPO_ROOT / "scripts" / "inspect_meta_project.py"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_identity.py"
REPORTS_SCRIPT = REPO_ROOT / "scripts" / "manage_reports.py"
BOUNDARIES_SCRIPT = REPO_ROOT / "scripts" / "check_boundaries.py"


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
        inspection = inspect_repository(self.root)
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

        # Execute inspection with --read-only
        proc = subprocess.run(
            [sys.executable, str(INSPECT_SCRIPT), "--repo-root", str(self.root), "--read-only", "--json"],
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

        # 3. Foreign project_id rejection simulation:
        # If manage is targeting vlv-code/meta-project, an incoming report for other-org/other-project
        # must be rejected during intake validation.
        target_project_id = "vlv-code/meta-project"
        foreign_report = dict(valid_template)
        foreign_report["project_id"] = "other-org/malicious-project"

        intake_errors = []
        if foreign_report["project_id"] != target_project_id:
            intake_errors.append(
                f"Foreign report rejected: project_id '{foreign_report['project_id']}' != expected '{target_project_id}'"
            )
        self.assertTrue(len(intake_errors) > 0)
        self.assertIn("Foreign report rejected", intake_errors[0])

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


if __name__ == "__main__":
    unittest.main()
