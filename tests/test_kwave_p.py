#!/usr/bin/env python3
"""Adversarial parity & contract tests for Wave K Lanes K2-K3 (Priorities 3->2->1)."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


BANNED_CIRCUIT_BREAKER_PHRASES = (
    "2nd consecutive",
    "second attempt",
    "Stop-Work on 2nd",
    "2 consecutive failed attempts",
)


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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
        if (REPO_ROOT / ".agents").is_dir():
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
        if (REPO_ROOT / ".agents").is_dir():
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

        if (REPO_ROOT / ".agents").is_dir():
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
        if (REPO_ROOT / ".agents").is_dir():
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

        if (REPO_ROOT / ".agents").is_dir():
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

        if (REPO_ROOT / ".agents").is_dir():
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
        if (REPO_ROOT / ".agents").is_dir():
            ag_ground = REPO_ROOT / ".agents/skills/ground-meta-project/SKILL.md"
            self.assertEqual(ground_path.read_bytes(), ag_ground.read_bytes())


if __name__ == "__main__":
    unittest.main()
