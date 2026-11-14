"""
Unit and adversarial tests for scripts/verify_identity.py (Multi-Harness Identity Engine).
Adheres to Adversarial TDD Invariant: tests failure modes (conflicts, mismatches, premature activation, unknown actors).
Pure Python 3.10+ standard library (unittest).
"""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import verify_identity
except ImportError:
    verify_identity = None


SAMPLE_VALID_REGISTRY = {
    "schema_version": "1.0.0",
    "project_id": "vlv-code/meta-project",
    "installations": {
        "ag-main": {
            "harness_id": "antigravity",
            "status": "active",
            "description": "Primary Antigravity environment",
        },
        "zc-main": {
            "harness_id": "zcode",
            "status": "planned",
            "description": "Planned ZCode migration target",
        },
    },
    "roles": {
        "agent-dev-lead": {
            "description": "Lead Developer & Dispatcher",
            "bindings": {
                "ag-main": {
                    "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
                    "status": "active",
                    "profile_path": ".agents/team/agent-dev-lead/profile.md",
                },
                "zc-main": {
                    "actor_id": "vlv-code/meta-project::zcode::zc-main::agent-dev-lead",
                    "status": "planned",
                    "profile_path": None,
                },
            },
        }
    },
}

SAMPLE_ACTIVE_PROFILE = """---
name: "Lead Developer & Dispatcher"
role_id: "agent-dev-lead"
harness_id: "antigravity"
installation_id: "ag-main"
actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"
---
# Role Passport
"""


class TestVerifyIdentity(unittest.TestCase):
    """Adversarial and structural unit tests for identity validation."""

    def setUp(self):
        if verify_identity is None:
            self.skipTest("scripts/verify_identity.py is not yet implemented")

    def test_valid_registry_passes(self):
        """Verify that a syntactically valid registry with matching active profiles passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "meta-project.json").write_text(
                json.dumps(SAMPLE_VALID_REGISTRY, indent=2), encoding="utf-8"
            )

            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            (profile_dir / "profile.md").write_text(SAMPLE_ACTIVE_PROFILE, encoding="utf-8")

            valid, errors = verify_identity.validate_identity_registry(root)
            self.assertTrue(valid, f"Validation unexpectedly failed: {errors}")
            self.assertEqual(len(errors), 0)

    def test_conflicting_actor_ids_fails(self):
        """Adversarial check: duplicate actor_ids across different roles or installations must be rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)

            corrupted_registry = {
                "schema_version": "1.0.0",
                "project_id": "vlv-code/meta-project",
                "installations": {
                    "ag-main": {"harness_id": "antigravity", "status": "active"},
                    "zc-main": {"harness_id": "zcode", "status": "planned"},
                },
                "roles": {
                    "role-one": {
                        "bindings": {
                            "ag-main": {
                                "actor_id": "vlv-code/meta-project::antigravity::ag-main::duplicate-actor",
                                "status": "active",
                                "profile_path": ".agents/team/role-one/profile.md",
                            }
                        }
                    },
                    "role-two": {
                        "bindings": {
                            "ag-main": {
                                "actor_id": "vlv-code/meta-project::antigravity::ag-main::duplicate-actor",
                                "status": "active",
                                "profile_path": ".agents/team/role-two/profile.md",
                            }
                        }
                    },
                },
            }
            (agents_dir / "meta-project.json").write_text(
                json.dumps(corrupted_registry), encoding="utf-8"
            )

            valid, errors = verify_identity.validate_identity_registry(root)
            self.assertFalse(valid)
            self.assertTrue(any("Duplicate actor_id" in err for err in errors))

    def test_mismatched_profile_actor_id_fails(self):
        """Adversarial check: discrepancy between profile.md actor_id and registry must fail closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "meta-project.json").write_text(
                json.dumps(SAMPLE_VALID_REGISTRY), encoding="utf-8"
            )

            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            mismatched_profile = SAMPLE_ACTIVE_PROFILE.replace(
                "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
                "vlv-code/meta-project::antigravity::ag-main::tampered-actor",
            )
            (profile_dir / "profile.md").write_text(mismatched_profile, encoding="utf-8")

            valid, errors = verify_identity.validate_identity_registry(root)
            self.assertFalse(valid)
            self.assertTrue(any("Mismatch" in err for err in errors))

    def test_planned_installation_marked_active_in_profile_fails(self):
        """Adversarial check: planned installation cannot be marked active in profile without official registry status change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "meta-project.json").write_text(
                json.dumps(SAMPLE_VALID_REGISTRY), encoding="utf-8"
            )

            # Create profile claiming zc-main is active while registry says it's planned
            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            premature_profile = """---
name: "Lead Developer"
role_id: "agent-dev-lead"
harness_id: "zcode"
installation_id: "zc-main"
actor_id: "vlv-code/meta-project::zcode::zc-main::agent-dev-lead"
---
# Role Passport
"""
            (profile_dir / "profile.md").write_text(premature_profile, encoding="utf-8")

            valid, errors = verify_identity.validate_identity_registry(root)
            self.assertFalse(valid)
            self.assertTrue(any("planned" in err.lower() or "status" in err.lower() for err in errors))

    def test_unknown_binding_raises_unresolved_identity_error(self):
        """Adversarial check: querying an unknown actor_id fails closed without directory guessing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "meta-project.json").write_text(
                json.dumps(SAMPLE_VALID_REGISTRY), encoding="utf-8"
            )

            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            (profile_dir / "profile.md").write_text(SAMPLE_ACTIVE_PROFILE, encoding="utf-8")

            valid, binding = verify_identity.resolve_actor_binding(
                root, "vlv-code/meta-project::antigravity::ag-main::unknown-role"
            )
            self.assertFalse(valid)
            self.assertIsNone(binding)

    def test_registry_with_valid_scenario_passes_verification(self):
        """Verifies that registry with schema 1.1.0 and valid scenario passes verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)

            registry = dict(SAMPLE_VALID_REGISTRY)
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
            (agents_dir / "meta-project.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")

            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            (profile_dir / "profile.md").write_text(SAMPLE_ACTIVE_PROFILE, encoding="utf-8")

            valid, errors = verify_identity.validate_identity_registry(root)
            self.assertTrue(valid, f"Validation failed: {errors}")
            self.assertEqual(len(errors), 0)

    def test_registry_invalid_scenario_profile_fails(self):
        """Adversarial test: invalid scenario profile or malformed scenario section fails validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)

            registry = dict(SAMPLE_VALID_REGISTRY)
            registry["schema_version"] = "1.1.0"
            registry["scenario"] = {
                "profile": "invalid_unknown_profile",
                "deployment_mode": "shared_repo",
                "collaboration_model": "triad",
                "verification_policy": "strict_independent",
            }
            (agents_dir / "meta-project.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")

            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            (profile_dir / "profile.md").write_text(SAMPLE_ACTIVE_PROFILE, encoding="utf-8")

            valid, errors = verify_identity.validate_identity_registry(root)
            self.assertFalse(valid, "Expected validation failure for invalid scenario profile")
            self.assertTrue(any("scenario" in e.lower() for e in errors), f"Errors: {errors}")


class TestVerifyIdentityCLI(unittest.TestCase):
    """Test CLI exit codes and output formatting."""

    def setUp(self):
        self.script_path = SCRIPTS_DIR / "verify_identity.py"
        if not self.script_path.is_file():
            self.skipTest("scripts/verify_identity.py does not exist yet")

    def test_cli_help(self):
        res = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("usage:", res.stdout.lower())

    def test_cli_check_fails_on_missing_registry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = subprocess.run(
                [sys.executable, str(self.script_path), "--check", "--repo-root", tmpdir],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("missing", res.stderr.lower() + res.stdout.lower())


if __name__ == "__main__":
    unittest.main()
