#!/usr/bin/env python3
"""Canonical domain tests for skills and templates contracts.
Consolidated from test_kwave_p.py, test_ewave_t.py, and test_jwave_o.py.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_DIR = REPO_ROOT
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TEMPLATES_DIR = REPO_ROOT / "templates"
SKILL = REPO_ROOT / "skills" / "manage-meta-project" / "SKILL.md"
INIT_SKILL_PATH = REPO_ROOT / "skills" / "init-meta-project" / "SKILL.md"

SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import sync_templates
except ImportError:
    sync_templates = None

BANNED_CIRCUIT_BREAKER_PHRASES = (
    "2nd consecutive",
    "second attempt",
    "Stop-Work on 2nd",
    "2 consecutive failed attempts",
)

BINDING_HEADING = "Dispatcher Runtime Binding (harness-dependent)"
MATRIX_HEADING = "#### 3. Open Competency Catalog"
FORBIDDEN_HARNESS_NAMES = (
    "zcode",
    "antigravity",
    "claude",
    "cursor",
    "codex",
    "gemini",
    "copilot",
    "windsurf",
)


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _phase(text, start_heading, end_heading):
    start = text.find(start_heading)
    if start == -1:
        return None
    if end_heading is None:
        return text[start:]
    end = text.find(end_heading, start)
    if end == -1:
        return None
    return text[start:end]


class TestSystemPromptAndProfileContracts(unittest.TestCase):
    """Verify P3/P5 contracts in team system_prompt.md and profile.md across mirrors."""

    def test_system_prompt_has_wave_k_invariants_and_mirror_parity(self) -> None:
        tpl_path = REPO_ROOT / "templates/team/system_prompt.md"
        res_path = REPO_ROOT / "skills/manage-meta-project/resources/system_prompt.md"
        ag_path = REPO_ROOT / ".agents/skills/manage-meta-project/resources/system_prompt.md"

        tpl_bytes = tpl_path.read_bytes()
        self.assertEqual(
            tpl_bytes,
            res_path.read_bytes(),
            "skills/manage-meta-project/resources/system_prompt.md drifted from template",
        )
        if (REPO_ROOT / ".agents/skills").is_dir():
            self.assertTrue(ag_path.is_file(), "missing .agents mirror for system_prompt.md")
            self.assertEqual(
                tpl_bytes,
                ag_path.read_bytes(),
                ".agents mirror of system_prompt.md drifted from template",
            )

        text = tpl_bytes.decode("utf-8")
        for token in (
            "Shared File Annotations Sanctity",
            "Parallel Subagent Delegation",
            "dispatching-parallel-agents",
            "Circuit Breaker",
            "Error-Path",
            "Fallback-Masking",
            "Target State Audit",
            "Pragmatic Handoff",
            "Probe Bundle",
            "mode: investigate",
            "Toolchain Handoff Tripwire",
            "Evidence-First Triage",
            "HYPOTHESIS",
            "discriminator",
        ):
            self.assertIn(token, text, f"Missing Wave K contract token {token!r} in system_prompt.md")

    def test_profile_template_has_toolchain_handoff_tripwire_and_parity(self) -> None:
        tpl_path = REPO_ROOT / "templates/team/profile.md"
        res_path = REPO_ROOT / "skills/manage-meta-project/resources/profile.md"
        ag_path = REPO_ROOT / ".agents/skills/manage-meta-project/resources/profile.md"

        tpl_bytes = tpl_path.read_bytes()
        self.assertEqual(tpl_bytes, res_path.read_bytes())
        if (REPO_ROOT / ".agents/skills").is_dir():
            self.assertTrue(ag_path.is_file())
            self.assertEqual(tpl_bytes, ag_path.read_bytes())

        self.assertIn("Toolchain Handoff Tripwire", tpl_bytes.decode("utf-8"))

    def test_active_team_prompts_and_profiles_match_wave_k_invariants(self) -> None:
        team_dir = REPO_ROOT / ".agents/team"
        if not team_dir.is_dir():
            self.skipTest("dogfood-branch contract: requires .agents/team/")

        active_roles = (
            ("agent-intake-dispatcher", "vlv-code/meta-project::antigravity::ag-main::agent-intake-dispatcher", False),
            ("agent-dev-lead", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead", False),
            ("agent-quality-guardian", "vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian", False),
            ("agent-github-steward", "vlv-code/meta-project::antigravity::ag-main::agent-github-steward", False),
            ("agent-dev-lead-zc", "vlv-code/meta-project::zcode::zc-main::agent-dev-lead", True),
            ("agent-quality-guardian-zc", "vlv-code/meta-project::zcode::zc-main::agent-quality-guardian", True),
            ("agent-github-steward-zc", "vlv-code/meta-project::zcode::zc-main::agent-github-steward", True),
        )
        required_prompt_tokens = (
            "Shared File Annotations Sanctity",
            "Error-Path",
            "Fallback-Masking",
            "Probe Bundle",
            "mode: investigate",
            "12. **Toolchain Handoff Tripwire:**",
            "13. **Evidence-First Triage & Anti-Sycophancy:**",
            "HYPOTHESIS",
            "discriminator",
        )
        for role_dir, expected_actor_id, is_zc in active_roles:
            sp_path = team_dir / role_dir / "system_prompt.md"
            prof_path = team_dir / role_dir / "profile.md"
            self.assertTrue(sp_path.is_file(), f"Missing {sp_path}")
            self.assertTrue(prof_path.is_file(), f"Missing {prof_path}")

            sp_text = sp_path.read_text(encoding="utf-8")
            for token in required_prompt_tokens:
                self.assertIn(token, sp_text, f"Missing {token!r} in {sp_path}")
            self.assertIn(f".agents/team/{role_dir}/profile.md", sp_text)
            self.assertIn(expected_actor_id, sp_text)
            if is_zc:
                self.assertIn("parallel Antigravity instance", sp_text)

            prof_text = prof_path.read_text(encoding="utf-8")
            self.assertIn(f'actor_id: "{expected_actor_id}"', prof_text)
            self.assertIn(
                "8. **Toolchain Handoff Tripwire:**",
                prof_text,
                f"Missing Rule 8 Toolchain Handoff Tripwire in {prof_path}",
            )

    def test_no_mechanical_edit_counters_in_wave_k_prose(self) -> None:
        targets = (
            "AGENTS.md",
            "templates/AGENTS.md",
            "templates/team/system_prompt.md",
            "skills/manage-meta-project/SKILL.md",
            "skills/triage-incident/SKILL.md",
        )
        for rel in targets:
            content = _read(rel)
            for banned in BANNED_CIRCUIT_BREAKER_PHRASES:
                self.assertNotIn(
                    banned,
                    content,
                    f"Mechanical circuit-breaker counter {banned!r} forbidden in {rel}",
                )


class TestManageSkillParityAndBudget(unittest.TestCase):
    """Verify manage-meta-project/SKILL.md stays <= 240 lines while codifying Probe Bundle."""

    def test_manage_skill_under_240_lines_and_has_probe_bundle(self) -> None:
        skill_path = REPO_ROOT / "skills/manage-meta-project/SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertLessEqual(
            len(lines),
            240,
            f"skills/manage-meta-project/SKILL.md exceeded 240 lines ({len(lines)})",
        )
        for token in (
            "Probe Bundle",
            "mode: investigate",
            "Toolchain Handoff Tripwire",
            "Shared File Annotations Sanctity",
            "Target State Audit",
            "Parallel Subagent Delegation",
            "dispatching-parallel-agents",
            "Error-Path",
            "Fallback-Masking",
        ):
            self.assertIn(token, text, f"Missing {token!r} in manage-meta-project/SKILL.md")

        if (REPO_ROOT / ".agents/skills").is_dir():
            ag_skill = REPO_ROOT / ".agents/skills/manage-meta-project/SKILL.md"
            self.assertTrue(ag_skill.is_file())
            self.assertEqual(skill_path.read_bytes(), ag_skill.read_bytes())


class TestPassportContracts(unittest.TestCase):
    """Verify templates/AGENTS.md and root AGENTS.md carry P5 Evidence-First & Circuit Breaker contracts."""

    def test_template_and_root_passports_contain_wave_k_contracts(self) -> None:
        for rel in ("templates/AGENTS.md", "AGENTS.md"):
            text = _read(rel)
            for token in (
                "Evidence-First Triage",
                "HYPOTHESIS",
                "testable hypothesis",
                "discriminator",
                "Circuit Breaker",
                "Error-Path",
                "Fallback-Masking",
                "triage-incident",
                "| triage |",
                "triage_incident.py",
            ):
                self.assertIn(token, text, f"Missing {token!r} in {rel}")

        root_text = _read("AGENTS.md")
        self.assertIn("`triage-incident`", root_text)
        self.assertIn("`scripts/triage_incident.py`", root_text)


class TestTasksAndGroundContracts(unittest.TestCase):
    """Verify P4 contracts in templates/project_knowledge/tasks.md and skills/ground-meta-project/SKILL.md."""

    def test_tasks_template_preserves_rule5_and_adds_rule6_epistemic_triage(self) -> None:
        tpl_path = REPO_ROOT / "templates/project_knowledge/tasks.md"
        res_path = REPO_ROOT / "skills/init-meta-project/resources/tasks.md"
        text = tpl_path.read_text(encoding="utf-8")

        self.assertEqual(tpl_path.read_bytes(), res_path.read_bytes())
        if (REPO_ROOT / ".agents/skills").is_dir():
            ag_res = REPO_ROOT / ".agents/skills/init-meta-project/resources/tasks.md"
            self.assertTrue(ag_res.is_file())
            self.assertEqual(tpl_path.read_bytes(), ag_res.read_bytes())

        # Preserve Rule 5 Checkpoint contract tokens (test_ewave_t.py)
        for token in ("- [>]", "goal:", "decided:", "done:", "open:", "next:", "ground"):
            self.assertIn(token, text, f"Rule 5 checkpoint token {token!r} lost from tasks.md template")

        # Require Rule 6 Epistemic Triage tokens
        for token in ("- [?] PROBE", "evidence:", "- [ ] FIX", "Epistemic Triage"):
            self.assertIn(token, text, f"Rule 6 triage token {token!r} missing from tasks.md template")

        # Adversarial self-check: template itself must emit 0 check-tasks warnings via CLI
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/triage_incident.py"),
                "check-tasks",
                "--tasks",
                str(tpl_path),
                "--json",
                "--strict",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report["summary"]["unverified_count"], 0, msg=proc.stdout)
        self.assertEqual(report["summary"]["thrashing_count"], 0, msg=proc.stdout)

    def test_ground_skill_enforces_facts_vs_hypotheses_and_check_tasks(self) -> None:
        skill_path = REPO_ROOT / "skills/ground-meta-project/SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        for token in (
            "FACTS vs HYPOTHESES",
            "triage_incident.py check-tasks",
            "evidence:",
            "Discrepancies & unknown facts",
        ):
            self.assertIn(token, text, f"Missing {token!r} in skills/ground-meta-project/SKILL.md")

        if (REPO_ROOT / ".agents/skills").is_dir():
            ag_skill = REPO_ROOT / ".agents/skills/ground-meta-project/SKILL.md"
            self.assertTrue(ag_skill.is_file())
            self.assertEqual(skill_path.read_bytes(), ag_skill.read_bytes())


class TestManifestAndInspectorInvariance(unittest.TestCase):
    """Verify release manifest registration, mirror parity, and inspector --facts-digest invariance."""

    def test_release_manifest_registers_triage_components_and_mirror(self) -> None:
        manifest = json.loads(_read("templates/release_manifest.json"))
        components = manifest.get("components", [])
        by_path = {entry.get("path"): entry for entry in components}

        self.assertIn("scripts/triage_incident.py", by_path)
        self.assertEqual(by_path["scripts/triage_incident.py"].get("requires"), ["scripts/_common.py"])

        self.assertIn("skills/triage-incident/SKILL.md", by_path)
        self.assertEqual(
            by_path["skills/triage-incident/SKILL.md"].get("requires"),
            ["scripts/triage_incident.py"],
        )

        if (REPO_ROOT / ".agents/skills").is_dir():
            src_skill = REPO_ROOT / "skills/triage-incident/SKILL.md"
            mir_skill = REPO_ROOT / ".agents/skills/triage-incident/SKILL.md"
            self.assertTrue(mir_skill.is_file())
            self.assertEqual(src_skill.read_bytes(), mir_skill.read_bytes())

    def test_facts_digest_top_level_keys_unchanged(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/inspect_meta_project.py"),
                "--facts-digest",
                "--read-only",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(
            set(payload.keys()),
            {"capabilities", "facts_digest_version", "harness", "installation", "slices", "state"},
        )

    def test_ground_manifest_requires_triage_script_and_phase2_has_fallback(self) -> None:
        manifest = json.loads(_read("templates/release_manifest.json"))
        by_path = {entry.get("path"): entry for entry in manifest.get("components", [])}

        self.assertIn("skills/ground-meta-project/SKILL.md", by_path)
        self.assertEqual(
            by_path["skills/ground-meta-project/SKILL.md"].get("requires"),
            ["scripts/inspect_meta_project.py", "scripts/triage_incident.py"],
        )

        ground_path = REPO_ROOT / "skills/ground-meta-project/SKILL.md"
        res_ground_path = REPO_ROOT / "skills/init-meta-project/resources/ground-meta-project-SKILL.md"
        text = ground_path.read_text(encoding="utf-8")
        phase2 = text.split("### Phase 2:")[1].split("### Phase 3:")[0]
        self.assertIn("triage_incident.py check-tasks", phase2)
        self.assertRegex(
            phase2.lower(),
            r"(when|if)[^\n]*(present|available|installed)",
            msg="ground-meta-project Phase 2 must guard triage_incident.py with a presence check",
        )
        self.assertRegex(
            phase2.lower(),
            r"(otherwise|else|fallback|if absent|if missing|manually)",
            msg="ground-meta-project Phase 2 must state manual fallback when triage_incident.py is absent",
        )
        self.assertEqual(ground_path.read_bytes(), res_ground_path.read_bytes())
        if (REPO_ROOT / ".agents/skills").is_dir():
            ag_ground = REPO_ROOT / ".agents/skills/ground-meta-project/SKILL.md"
            self.assertEqual(ground_path.read_bytes(), ag_ground.read_bytes())

class TestArchitectureTemplateV2(unittest.TestCase):
    """(a) Map-first architecture card: Depends on column + same-change rule, no Design Patterns."""

    def setUp(self):
        self.content = read(TEMPLATES_DIR / "project_knowledge" / "architecture.md")

    def test_component_map_has_depends_on_column(self):
        self.assertIn("Component Map", self.content)
        self.assertIn("| Component | Location | Role | Depends on |", self.content)

    def test_same_change_update_rule_present(self):
        self.assertIn(
            "The map is updated IN THE SAME CHANGE that touches a component",
            self.content,
            "Same-change map update rule missing from architecture template header",
        )
        self.assertIn("a decision without a map update is an incomplete change", self.content)
        self.assertIn("One row per component, no prose", self.content)

    def test_design_patterns_removed(self):
        self.assertNotIn(
            "Design Patterns",
            self.content,
            "Design Patterns section must be removed from architecture template v2",
        )

    def test_stack_and_invariants_one_line_slots(self):
        self.assertIn("Stack and Invariants", self.content)
        for slot in ("Stack:", "State + Single Source of Truth:", "Cross-border contracts:"):
            self.assertIn(slot, self.content, f"Missing one-line slot: {slot}")

    def test_conditional_e2e_flows_section(self):
        self.assertIn("End-to-End Data Flows", self.content)
        self.assertIn("multi-tier", self.content.lower())


class TestTasksTemplateCheckpointRule(unittest.TestCase):
    """(b) Team Task Management Rules rule 5: Checkpoint (pause/handoff) with - [>] example."""

    def setUp(self):
        self.content = read(TEMPLATES_DIR / "project_knowledge" / "tasks.md")

    def test_rule5_checkpoint_present(self):
        self.assertIn("Checkpoint (pause/handoff)", self.content)

    def test_checkpoint_status_marker_example(self):
        self.assertIn(
            "- [>]",
            self.content,
            "Template must contain a - [>] checkpoint example",
        )

    def test_checkpoint_compact_fields(self):
        for field in ("goal:", "decided:", "done:", "open:", "next:"):
            self.assertIn(field, self.content, f"Missing checkpoint field: {field}")

    def test_ground_resumes_from_checkpoint(self):
        self.assertIn("ground", self.content.lower())


# (c, superseded per plan §6a owner decision ADJUST AND PROCEED, 2026-11-16):
# Lane P2 extracted the embedded TEMPLATE blocks into
# skills/init-meta-project/resources/. The byte-match-canonical invariant now
# lives canonically in tests/test_ewave_p.py
# (TestResourcesByteCanonical — all 9 resources, superset of the
# architecture.md/tasks.md subset previously asserted here). The superseded
# class TestInitSkillResourcesCanonical was removed as a byte-duplicate in
# Wave F (T-D6 #1/#4): one canonical byte test, no drift-test forks.


class TestSyncTargetsAndZeroDrift(unittest.TestCase):
    """(d, superseded per plan §6a) RESOURCE_TARGETS declares the canonical
    pairs for init (formerly EMBEDDED_TARGETS).

    Wave F T-D6: the byte-identical write-then-check drift test that lived
    here was deduplicated — the canonical implementation is
    tests/test_ewave_p.py (TestSyncResourcesZeroDrift.
    test_write_then_check_zero_drift) as a temp-clone fixture, since a test
    must never run ``sync --write`` against the LIVE repo tree."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not implemented yet")

    def test_resource_targets_declare_canonical_pairs(self):
        targets = getattr(sync_templates, "RESOURCE_TARGETS", {})
        self.assertEqual(
            targets.get("architecture.md"),
            "templates/project_knowledge/architecture.md",
        )
        self.assertEqual(
            targets.get("tasks.md"),
            "templates/project_knowledge/tasks.md",
        )

class TestDispatcherRuntimeBinding(unittest.TestCase):
    """The binding block in Phase 2: table, contract, establishment rule."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()

    def _line_at(self, needle):
        idx = self.text.find(needle)
        self.assertNotEqual(idx, -1, f"marker not found: {needle!r}")
        return self.lines[self.text[:idx].count("\n")]

    def test_dispatcher_matrix_row_names_the_orchestrator_executor(self):
        # Wave Z2-B: progressive disclosure moved matrix to references/competencies.md
        ref_path = REPO_ROOT / "skills/manage-meta-project/references/competencies.md"
        source_text = ref_path.read_text(encoding="utf-8") if ref_path.is_file() else self.text
        rows = [
            line
            for line in source_text.splitlines()
            if line.startswith("| `agent-intake-dispatcher` |")
        ]
        self.assertEqual(len(rows), 1, "expected exactly one dispatcher matrix row")
        self.assertIn("native orchestrator", rows[0])
        self.assertIn("binding above", rows[0])

    def test_binding_block_sits_between_dispatcher_rule_and_role_matrix(self):
        binding = self.text.find(BINDING_HEADING)
        rule = self.text.find("Mandatory Dispatcher Rule")
        matrix = self.text.find(MATRIX_HEADING)
        self.assertNotEqual(binding, -1, "binding block heading missing")
        self.assertNotEqual(rule, -1, "Mandatory Dispatcher Rule missing")
        self.assertNotEqual(matrix, -1, "role matrix heading missing")
        self.assertGreater(binding, rule)
        self.assertLess(binding, matrix)

    def test_binding_table_lists_standalone_first(self):
        standalone_idx = self.text.find("| `standalone` (default) |")
        hosted_idx = self.text.find("| `orchestrator-hosted` |")
        self.assertNotEqual(standalone_idx, -1, "standalone binding row missing")
        self.assertNotEqual(hosted_idx, -1, "orchestrator-hosted binding row missing")
        self.assertLess(standalone_idx, hosted_idx)
        standalone_line = self._line_at("| `standalone` (default) |")
        hosted_line = self._line_at("| `orchestrator-hosted` |")
        self.assertIn("user-mediated handoff packages", standalone_line)
        self.assertIn("same dispatcher passport", hosted_line)

    def test_hosted_row_gates_dispatch_on_every_delegation_level(self):
        hosted_line = self._line_at("| `orchestrator-hosted` |")
        for token in (
            "delegation_level",
            "strictly_manual",
            "controlled",
            "autonomous",
        ):
            self.assertIn(token, hosted_line)

    def test_binding_is_never_inferred_and_defaults_to_standalone(self):
        self.assertIn(
            "never inferred from the harness name, environment variables "
            "or another installation's records",
            self.text,
        )
        self.assertIn("Unknown or absent orchestrator means `standalone`", self.text)

    def test_binding_block_names_no_specific_harness(self):
        block = _phase(self.text, BINDING_HEADING, MATRIX_HEADING)
        self.assertIsNotNone(block, "binding block slice not found")
        lowered = block.lower()
        for harness in FORBIDDEN_HARNESS_NAMES:
            self.assertNotIn(harness, lowered, f"harness named: {harness!r}")

    def test_contract_is_identical_in_both_bindings(self):
        intro_line = self._line_at("**" + BINDING_HEADING + ":**")
        for token in (
            "passport",
            "qualified `actor_id`",
            "verification policy",
            "identical in both bindings",
        ):
            self.assertIn(token, intro_line)

    def test_transient_subagents_stay_allowed(self):
        self.assertIn(
            "Transient subagents (rule 7) stay allowed under every binding",
            self.text,
        )


class TestBindingClausesInPhases(unittest.TestCase):
    """Binding guidance threaded through Phases 4, 5, 6 and 7."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()

    def test_phase4_proposal_asks_for_the_binding(self):
        phase4 = _phase(self.text, "### Phase 4:", "### Phase 5:")
        self.assertIsNotNone(phase4, "Phase 4 slice not found")
        self.assertIn("Dispatcher binding", phase4)
        self.assertIn("default `standalone`", phase4)

    def test_phase5_appends_binding_clause_under_hosted(self):
        step5 = [
            line
            for line in self.lines
            if line.startswith("5. Generate the initial ready-to-use system prompt")
        ]
        self.assertEqual(len(step5), 1, "expected exactly one Phase 5 step 5 line")
        self.assertIn("orchestrator-hosted", step5[0])
        self.assertIn("append to every generated prompt", step5[0])

    def test_phase6_treats_orchestrator_load_as_manual_step(self):
        target = [
            line
            for line in self.lines
            if "Profile Created ≠ Loaded by Harness" in line
        ]
        self.assertEqual(len(target), 1, "expected exactly one invariant bullet")
        self.assertIn("orchestrator-hosted", target[0])
        self.assertIn("manual step", target[0])

    def test_rule2_points_hosted_dispatch_to_delegation_level(self):
        phase7 = _phase(self.text, "### Phase 7:", None)
        self.assertIsNotNone(phase7, "Phase 7 slice not found")
        self.assertIn(
            "Under the `orchestrator-hosted` dispatcher binding, "
            "role-to-role dispatch follows the agreed `delegation_level`",
            phase7,
        )


class TestHostIdentificationMarkers(unittest.TestCase):
    """Phase 1 anti-anchoring example must use real session markers."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_host_identification_example_uses_real_session_markers(self):
        self.assertNotIn("ZCODE_AGENT", self.text)
        self.assertIn("`ZCODE_PROJECT_DIR` / `ZCODE_SESSION_ID`", self.text)


class TestMandatoryDispatcherRulePreserved(unittest.TestCase):
    """Lock-in: the original dispatcher rule sentence stays verbatim."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_mandatory_dispatcher_rule_keeps_its_original_sentence(self):
        self.assertIn(
            "Forbid leaving the user with an unrouted bundle of multiple "
            "isolated roles without a single point of entry.",
            self.text,
        )


class TestScriptRootCanonicalResolution(unittest.TestCase):
    """Canonical SCRIPT_ROOT resolution rules across skills and external repo smoke test."""

    def test_init_and_scan_skills_formalize_script_root_resolution(self) -> None:
        init_skill = (REPO_ROOT / "skills" / "init-meta-project" / "SKILL.md").read_text(encoding="utf-8")
        scan_skill = (REPO_ROOT / "skills" / "scan-meta-project" / "SKILL.md").read_text(encoding="utf-8")

        for skill_name, text in (("init-meta-project", init_skill), ("scan-meta-project", scan_skill)):
            self.assertIn("SCRIPT_ROOT", text, f"{skill_name} missing SCRIPT_ROOT formalization")
            self.assertIn("./scripts/", text, f"{skill_name} missing local ./scripts/ order 1")
            self.assertIn("${CLAUDE_PLUGIN_ROOT}", text, f"{skill_name} missing CLAUDE_PLUGIN_ROOT order 2")
            self.assertTrue(
                "../../scripts" in text or "dir of SKILL.md" in text or "<dir_of_SKILL.md>" in text,
                f"{skill_name} missing sibling / plugin root order 3",
            )

    def test_inspect_meta_project_external_empty_repo_smoke(self) -> None:
        script_path = REPO_ROOT / "scripts" / "inspect_meta_project.py"
        with tempfile.TemporaryDirectory() as temp_empty:
            cmd = [
                sys.executable,
                str(script_path),
                "--repo-root",
                str(temp_empty),
                "--read-only",
                "--json",
            ]
            res = subprocess.run(cmd, cwd=str(temp_empty), capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Expected rc=0, got {res.returncode}: stderr={res.stderr}")
            data = json.loads(res.stdout)
            self.assertEqual(data.get("state"), "NONE", f"Expected state NONE, got {data.get('state')}")

    def test_manage_skill_references_script_root_and_stays_within_budget(self) -> None:
        manage_skill = (REPO_ROOT / "skills" / "manage-meta-project" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("SCRIPT_ROOT", manage_skill)
        lines = manage_skill.splitlines()
        self.assertLessEqual(
            len(lines),
            240,
            f"skills/manage-meta-project/SKILL.md exceeded 240 lines ({len(lines)})",
        )


class TestProgressiveDisclosureSkillContracts(unittest.TestCase):
    """Wave Z2-B: progressive disclosure contracts for heavy skills."""

    def test_manage_references_competencies_exists_and_has_roles(self):
        ref_path = REPO_ROOT / "skills/manage-meta-project/references/competencies.md"
        self.assertTrue(ref_path.is_file(), f"Missing {ref_path}")
        text = ref_path.read_text(encoding="utf-8")
        self.assertIn("Open Competency Catalog", text)
        for role in (
            "agent-general-worker",
            "agent-intake-dispatcher",
            "agent-meta-guardian",
            "agent-consensus-judge",
            "agent-deep-auditor",
            "agent-product-roaster",
            "agent-creative-director",
            "agent-ui-ux-engineer",
            "agent-legal-compliance",
            "agent-github-steward",
            "agent-devops-infra",
            "agent-qa-engineer",
            "agent-tech-writer",
        ):
            self.assertIn(role, text, f"Missing role {role!r} in competencies.md")

    def test_init_references_scenarios_exists_and_has_seven_scenarios(self):
        ref_path = REPO_ROOT / "skills/init-meta-project/references/scenarios.md"
        self.assertTrue(ref_path.is_file(), f"Missing {ref_path}")
        text = ref_path.read_text(encoding="utf-8")
        for sc in (
            "Scenario 1: State `NONE`",
            "Scenario 2: State `FOREIGN_RULES`",
            "Scenario 3: State `HEALTHY_REGISTERED`",
            "Scenario 4: State `HEALTHY_NEW_HARNESS`",
            "Scenario 5: State `LEGACY_UNREGISTERED`",
            "Scenario 6: State `PARTIAL_CORRUPTED`",
            "Scenario 7: State `INCOMPATIBLE_SCHEMA`",
        ):
            self.assertIn(sc, text, f"Missing scenario {sc!r} in scenarios.md")

    def test_update_references_troubleshooting_exists_and_has_diagnostics(self):
        ref_path = REPO_ROOT / "skills/update-meta-project/references/troubleshooting.md"
        self.assertTrue(ref_path.is_file(), f"Missing {ref_path}")
        text = ref_path.read_text(encoding="utf-8")
        for topic in (
            "conflicts",
            "protected",
            "needs_base",
            "local_repo_data",
            "ENGINE_BUSY",
        ):
            self.assertIn(topic, text, f"Missing topic {topic!r} in troubleshooting.md")

    def test_skills_carry_missing_resource_and_reference_contracts(self):
        manage_text = (REPO_ROOT / "skills/manage-meta-project/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/competencies.md", manage_text)
        self.assertIn("MISSING_RESOURCE", manage_text)
        self.assertIn("Phase", manage_text)

        init_text = (REPO_ROOT / "skills/init-meta-project/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/scenarios.md", init_text)
        self.assertIn("MISSING_RESOURCE", init_text)

        update_text = (REPO_ROOT / "skills/update-meta-project/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/troubleshooting.md", update_text)
        self.assertIn("MISSING_RESOURCE", update_text)

    def test_manage_skill_stays_under_240_lines(self):
        manage_path = REPO_ROOT / "skills/manage-meta-project/SKILL.md"
        lines = manage_path.read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 240, f"manage-meta-project/SKILL.md has {len(lines)} lines > 240")


class TestUpdateEngineArtifactHygieneContracts(unittest.TestCase):
    """Contracts for Wave Z3: Update Engine artifact hygiene in skills and gitignore."""

    def test_init_skill_and_scenarios_gitignore_hygiene(self):
        init_skill = (REPO_ROOT / "skills/init-meta-project/SKILL.md").read_text(encoding="utf-8")
        scenarios = (REPO_ROOT / "skills/init-meta-project/references/scenarios.md").read_text(encoding="utf-8")

        for artifact in [
            ".agents/update-engine.lock",
            ".agents/update-plan.json",
            ".agents/update-journal.json",
        ]:
            self.assertIn(artifact, init_skill, f"Missing {artifact} in init-meta-project/SKILL.md")
            self.assertIn(artifact, scenarios, f"Missing {artifact} in init-meta-project/references/scenarios.md")

    def test_update_skill_closeout_separates_persistent_and_transient_artifacts(self):
        update_skill = (REPO_ROOT / "skills/update-meta-project/SKILL.md").read_text(encoding="utf-8")

        # Persistent audit/lock state to commit
        self.assertIn(".agents/framework-lock.json", update_skill)
        self.assertIn(".agents/reports/*/update/*.json", update_skill)

        # Transient session files NOT to commit
        self.assertIn(".agents/update-engine.lock", update_skill)
        self.assertIn(".agents/update-plan.json", update_skill)
        self.assertIn(".agents/update-journal.json", update_skill)


class TestDecisionRtlContracts(unittest.TestCase):
    """Contracts for Wave Z4 (P2.4): Decision-RTL in AGENTS.md templates, root, and sync-architecture."""

    def test_decision_rtl_in_templates_and_root_agents(self):
        targets = [
            REPO_ROOT / "templates/AGENTS.md",
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "skills/init-meta-project/resources/AGENTS.md",
        ]
        for p in targets:
            self.assertTrue(p.is_file(), f"Missing target passport: {p}")
            content = p.read_text(encoding="utf-8")
            self.assertTrue(
                re.search(r"Decision[- ]RTL", content),
                f"Missing Decision-RTL section in {p}",
            )
            for field in [
                "Goal",
                "Affected North Stars",
                "Rationale",
                "Risks & Trade-offs",
                "Verification Result & Impact",
            ]:
                self.assertIn(
                    field,
                    content,
                    f"Missing Decision-RTL field '{field}' in {p}",
                )
            # Must state scope: architecturally significant changes
            self.assertTrue(
                re.search(r"architecturally significant", content, re.IGNORECASE),
                f"Missing architectural significance scope in {p}",
            )

    def test_sync_architecture_checks_decision_rtl(self):
        sync_skill = (REPO_ROOT / "skills/sync-architecture/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Decision[- ]RTL", sync_skill),
            "Missing Decision-RTL audit step in skills/sync-architecture/SKILL.md",
        )


if __name__ == '__main__':
    unittest.main()
