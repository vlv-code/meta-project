#!/usr/bin/env python3
"""Lane L1/L4: Tests for cross-harness topology alignment and duty deconfliction."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from inspect_meta_project import (
        detect_cross_harness_divergence,
        inspect_repository,
        format_human_report,
        compute_facts_digest,
    )
except ImportError:
    detect_cross_harness_divergence = None  # type: ignore
    inspect_repository = None  # type: ignore
    format_human_report = None  # type: ignore
    compute_facts_digest = None  # type: ignore

try:
    from verify_identity import validate_identity_registry, VALID_COLLABORATION_MODELS
except ImportError:
    validate_identity_registry = None  # type: ignore
    VALID_COLLABORATION_MODELS = set()  # type: ignore


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
        self.assertIsNotNone(inspect_repository, "inspect_repository not defined")
        rep = inspect_repository(REPO_ROOT)
        self.assertIn("cross_harness_divergence", rep)
        self.assertIn("asymmetric_roles", rep)
        # In this repository, ag-main has 4 roles and zc-main has 3 roles
        self.assertTrue(rep["cross_harness_divergence"])
        asym_role_ids = [r["role_id"] for r in rep["asymmetric_roles"]]
        self.assertIn("agent-intake-dispatcher", asym_role_ids)

    def test_format_human_report_cross_harness_output(self):
        self.assertIsNotNone(format_human_report, "format_human_report not defined")
        rep = inspect_repository(REPO_ROOT)
        output = format_human_report(rep)
        self.assertIn("Cross-Harness Roles: asymmetric", output)
        self.assertIn("agent-intake-dispatcher", output)

    def test_facts_digest_invariance(self):
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
