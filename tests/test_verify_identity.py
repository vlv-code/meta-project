#!/usr/bin/env python3
"""Canonical domain test suite for verify_identity (scripts/verify_identity.py).

Consolidated in Wave T (Lane T2) from:
- tests/test_verify_identity.py
- tests/test_jwave_v.py

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verify_identity
from scripts import inspect_meta_project

SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_identity.py"
PROJECT_ID = "vlv-code/test-project"
_ABSENT = object()

SAMPLE_VALID_REGISTRY = {
    "schema_version": "1.0.0",
    "project_id": "vlv-code/meta-project",
    "installations": {
        "ag-main": {
            "harness_id": "antigravity",
            "status": "active",
            "description": "Primary development installation",
        },
        "zc-main": {
            "harness_id": "zcode",
            "status": "planned",
            "description": "Planned target installation",
        },
    },
    "roles": {
        "agent-dev-lead": {
            "description": "Lead developer role",
            "bindings": {
                "ag-main": {
                    "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
                    "status": "active",
                    "profile_path": ".agents/team/agent-dev-lead/profile.md",
                },
                "zc-main": {
                    "actor_id": "vlv-code/meta-project::zcode::zc-main::agent-dev-lead",
                    "status": "planned",
                    "profile_path": ".agents/team/agent-dev-lead-zc/profile.md",
                },
            },
        }
    },
}

SAMPLE_ACTIVE_PROFILE = """---
name: "Dev Lead"
role_id: "agent-dev-lead"
harness_id: "antigravity"
installation_id: "ag-main"
actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"
---
# Role Passport: Dev Lead
"""


# ---------------------------------------------------------------------------
# TestVerifyIdentity (from tests/test_verify_identity.py)
# ---------------------------------------------------------------------------
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

    def test_detect_host_harness(self):
        """Verify host harness detection for supported environment variables."""
        cases = [
            ("ANTIGRAVITY_AGENT", "antigravity"),
            ("ZCODE_AGENT", "zcode"),
            ("CURSOR_AGENT", "cursor"),
            ("CLAUDE_CODE", "claude-code"),
            ("CODEX_AGENT", "codex"),
        ]
        for env_var, expected_harness in cases:
            with self.subTest(env_var=env_var):
                with mock.patch.dict(os.environ, {env_var: "1"}, clear=True):
                    self.assertEqual(verify_identity.detect_host_harness(), expected_harness)

        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(verify_identity.detect_host_harness())


# ---------------------------------------------------------------------------
# TestVerifyIdentityCLI (from tests/test_verify_identity.py)
# ---------------------------------------------------------------------------
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

    def test_actor_host_harness_mismatch_warning_emitted(self):
        """CLI emits warning on stderr when detected host harness does not match actor_id harness."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            registry = {
                "schema_version": "1.0.0",
                "project_id": "vlv-code/meta-project",
                "installations": {
                    "zc-main": {
                        "harness_id": "zcode",
                        "status": "active",
                    },
                },
                "roles": {
                    "agent-dev-lead": {
                        "bindings": {
                            "zc-main": {
                                "actor_id": "vlv-code/meta-project::zcode::zc-main::agent-dev-lead",
                                "status": "active",
                            },
                        },
                    },
                },
            }
            (agents_dir / "meta-project.json").write_text(
                json.dumps(registry, indent=2), encoding="utf-8"
            )

            actor_id = "vlv-code/meta-project::zcode::zc-main::agent-dev-lead"
            test_env = os.environ.copy()
            for var in (
                "ANTIGRAVITY_AGENT",
                "ZCODE_AGENT",
                "CURSOR_AGENT",
                "CLAUDE_CODE",
                "CODEX_AGENT",
            ):
                test_env.pop(var, None)
            test_env["ANTIGRAVITY_AGENT"] = "1"

            with mock.patch.dict(os.environ, test_env, clear=True):
                res = subprocess.run(
                    [
                        sys.executable,
                        str(self.script_path),
                        "--repo-root",
                        str(root),
                        "--actor",
                        actor_id,
                    ],
                    capture_output=True,
                    text=True,
                    env=os.environ,
                )
                self.assertEqual(res.returncode, 0)
                expected_warning = (
                    "[WARNING] Host harness mismatch: Current process environment appears to be 'antigravity', "
                    "but checked actor_id specifies harness 'zcode'. "
                    "Verify that you are not running in a foreign harness session."
                )
                self.assertIn(expected_warning, res.stderr)

    def test_actor_host_harness_matching_no_warning(self):
        """CLI does not emit warning when detected host harness matches actor_id harness."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            registry = {
                "schema_version": "1.0.0",
                "project_id": "vlv-code/meta-project",
                "installations": {
                    "ag-main": {
                        "harness_id": "antigravity",
                        "status": "active",
                    },
                },
                "roles": {
                    "agent-dev-lead": {
                        "bindings": {
                            "ag-main": {
                                "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
                                "status": "active",
                            },
                        },
                    },
                },
            }
            (agents_dir / "meta-project.json").write_text(
                json.dumps(registry, indent=2), encoding="utf-8"
            )

            actor_id = "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"
            test_env = os.environ.copy()
            for var in (
                "ANTIGRAVITY_AGENT",
                "ZCODE_AGENT",
                "CURSOR_AGENT",
                "CLAUDE_CODE",
                "CODEX_AGENT",
            ):
                test_env.pop(var, None)
            test_env["ANTIGRAVITY_AGENT"] = "1"

            with mock.patch.dict(os.environ, test_env, clear=True):
                res = subprocess.run(
                    [
                        sys.executable,
                        str(self.script_path),
                        "--repo-root",
                        str(root),
                        "--actor",
                        actor_id,
                    ],
                    capture_output=True,
                    text=True,
                    env=os.environ,
                )
                self.assertEqual(res.returncode, 0)
                self.assertNotIn("Host harness mismatch", res.stderr)


# ---------------------------------------------------------------------------
# TestSingleHostDetectionSource (from tests/test_jwave_v.py)
# ---------------------------------------------------------------------------
class TestSingleHostDetectionSource(unittest.TestCase):
    """Part A: one shared host-harness detector, no stale duplicates."""

    def test_both_modules_share_one_function(self):
        """verify_identity and inspect_meta_project must expose the SAME
        detect_host_harness implementation (imported from scripts/_common)."""
        self.assertIs(
            verify_identity.detect_host_harness,
            inspect_meta_project.detect_host_harness,
            "verify_identity.detect_host_harness and "
            "inspect_meta_project.detect_host_harness must be the same "
            "function object (single source of truth in scripts/_common.py)",
        )

    def test_no_second_signature_table_outside_common(self):
        """No script other than _common.py may carry a private copy of the
        signature table (the stale HARNESS_ENV_MAP must be deleted)."""
        scripts_dir = REPO_ROOT / "scripts"
        offenders: list = []
        for py_file in sorted(scripts_dir.glob("*.py")):
            if py_file.name == "_common.py":
                continue
            text = py_file.read_text(encoding="utf-8")
            if "HARNESS_ENV_MAP" in text:
                offenders.append(f"{py_file.name}: contains HARNESS_ENV_MAP")
            for line in text.splitlines():
                if line.lstrip().startswith("HOST_HARNESS_SIGNATURES"):
                    offenders.append(
                        f"{py_file.name}: defines HOST_HARNESS_SIGNATURES"
                    )
        self.assertEqual(
            offenders,
            [],
            "host-harness signature table duplicated outside "
            "scripts/_common.py",
        )

    def test_verify_identity_detects_a_real_zcode_session(self):
        """A real ZCode desktop session exposes ZCODE_PROJECT_DIR /
        ZCODE_SESSION_ID (plus bridged CLAUDE_* variables) and NO
        ZCODE_AGENT. The corrected signatures must resolve 'zcode' (the
        stale HARNESS_ENV_MAP copy returned None here)."""
        env = {
            "ZCODE_PROJECT_DIR": "p",
            "ZCODE_SESSION_ID": "s",
            "CLAUDE_PROJECT_DIR": "p",
        }
        self.assertEqual(verify_identity.detect_host_harness(env=env), "zcode")

    def test_actor_check_host_mismatch_warning_works_in_a_zcode_session(self):
        """End-to-end: `verify_identity --actor` run inside a REAL ZCode
        session environment must warn when the actor's harness is foreign,
        and stay silent when it matches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            registry = {
                "schema_version": "1.1.0",
                "project_id": PROJECT_ID,
                "installations": {
                    "zc-main": {"harness_id": "zcode", "status": "active"},
                    "ag-main": {
                        "harness_id": "antigravity",
                        "status": "active",
                    },
                },
                "roles": {
                    "agent-dev-lead": {
                        "bindings": {
                            "zc-main": {
                                "actor_id": (
                                    f"{PROJECT_ID}::zcode::zc-main::"
                                    "agent-dev-lead"
                                ),
                                "status": "active",
                                "profile_path": (
                                    ".agents/team/agent-dev-lead/"
                                    "profile.zc-main.md"
                                ),
                            },
                            "ag-main": {
                                "actor_id": (
                                    f"{PROJECT_ID}::antigravity::ag-main::"
                                    "agent-dev-lead"
                                ),
                                "status": "active",
                                "profile_path": (
                                    ".agents/team/agent-dev-lead/"
                                    "profile.ag-main.md"
                                ),
                            },
                        },
                    },
                },
            }
            (agents_dir / "meta-project.json").write_text(
                json.dumps(registry, indent=2), encoding="utf-8"
            )
            profile_dir = agents_dir / "team" / "agent-dev-lead"
            profile_dir.mkdir(parents=True)
            (profile_dir / "profile.zc-main.md").write_text(
                '---\nrole_id: "agent-dev-lead"\nharness_id: "zcode"\n'
                'installation_id: "zc-main"\n'
                f'actor_id: "{PROJECT_ID}::zcode::zc-main::agent-dev-lead"\n'
                "---\n# Role Passport\n",
                encoding="utf-8",
            )
            (profile_dir / "profile.ag-main.md").write_text(
                '---\nrole_id: "agent-dev-lead"\nharness_id: "antigravity"\n'
                'installation_id: "ag-main"\n'
                f'actor_id: "{PROJECT_ID}::antigravity::ag-main'
                '::agent-dev-lead"\n'
                "---\n# Role Passport\n",
                encoding="utf-8",
            )

            zcode_actor = f"{PROJECT_ID}::zcode::zc-main::agent-dev-lead"
            antigravity_actor = (
                f"{PROJECT_ID}::antigravity::ag-main::agent-dev-lead"
            )

            # A real ZCode session: session-scoped markers only, no
            # ZCODE_AGENT legacy variable, no foreign harness markers.
            with mock.patch.dict(
                os.environ,
                {"ZCODE_PROJECT_DIR": "p", "ZCODE_SESSION_ID": "s"},
                clear=True,
            ):
                res_zc = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT_PATH),
                        "--repo-root",
                        str(root),
                        "--actor",
                        zcode_actor,
                    ],
                    capture_output=True,
                    text=True,
                    env=os.environ,
                )
                res_ag = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT_PATH),
                        "--repo-root",
                        str(root),
                        "--actor",
                        antigravity_actor,
                    ],
                    capture_output=True,
                    text=True,
                    env=os.environ,
                )

            self.assertEqual(
                res_zc.returncode,
                0,
                f"zcode actor not resolved: {res_zc.stderr!r}",
            )
            self.assertNotIn(
                "Host harness mismatch",
                res_zc.stderr,
                "matching harness must not warn",
            )
            self.assertEqual(
                res_ag.returncode,
                0,
                f"antigravity actor not resolved: {res_ag.stderr!r}",
            )
            self.assertIn(
                "Host harness mismatch",
                res_ag.stderr,
                "a zcode session checking an antigravity actor must emit the "
                "host harness mismatch warning (the stale HARNESS_ENV_MAP "
                "copy never detected the zcode session)",
            )


# ---------------------------------------------------------------------------
# TestOrchestrationBlockValidation (from tests/test_jwave_v.py)
# ---------------------------------------------------------------------------
class TestOrchestrationBlockValidation(unittest.TestCase):
    """Part B: optional installation `orchestration` block validation."""

    def _validate(self, orchestration, status="active", inst_id="t9"):
        """Write a minimal registry with a single installation carrying the
        given orchestration value (or none when _ABSENT) and validate it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".agents"
            agents_dir.mkdir(parents=True)
            installation = {
                "harness_id": "zcode",
                "status": status,
            }
            if orchestration is not _ABSENT:
                installation["orchestration"] = orchestration
            registry = {
                "schema_version": "1.1.0",
                "project_id": PROJECT_ID,
                "installations": {inst_id: installation},
                "roles": {},
            }
            (agents_dir / "meta-project.json").write_text(
                json.dumps(registry, indent=2), encoding="utf-8"
            )
            return verify_identity.validate_identity_registry(root)

    def assertValid(self, orchestration, status="active", inst_id="t9"):
        valid, errors = self._validate(orchestration, status=status, inst_id=inst_id)
        self.assertTrue(
            valid,
            f"expected valid registry, got errors: {errors}",
        )
        self.assertEqual(errors, [])

    def assertInvalid(self, orchestration, *must_contain, status="active", inst_id="t9"):
        valid, errors = self._validate(orchestration, status=status, inst_id=inst_id)
        self.assertFalse(
            valid,
            f"expected invalid registry for orchestration={orchestration!r}",
        )
        for fragment in must_contain:
            self.assertTrue(
                any(fragment in err for err in errors),
                f"no error mentions {fragment!r}; errors: {errors}",
            )

    # -- lock-in: absence and null stay valid ------------------------------

    def test_registry_without_orchestration_block_stays_valid(self):
        self.assertValid(_ABSENT)

    def test_explicit_null_block_is_valid_not_declared(self):
        self.assertValid(None)

    def test_partial_blocks_are_valid(self):
        self.assertValid({"native_orchestrator": False})
        self.assertValid({"dispatcher_binding": "standalone"})

    def test_full_valid_block(self):
        self.assertValid(
            {
                "native_orchestrator": True,
                "dispatcher_binding": "orchestrator-hosted",
            }
        )

    def test_valid_block_on_planned_installation(self):
        self.assertValid(
            {
                "native_orchestrator": True,
                "dispatcher_binding": "orchestrator-hosted",
            },
            status="planned",
        )

    # -- adversarial: malformed blocks must fail ---------------------------

    def test_non_object_block_invalid(self):
        self.assertInvalid(
            "hosted", "t9", "must be an object", "orchestration"
        )
        self.assertInvalid(
            ["x"], "t9", "must be an object", "orchestration"
        )

    def test_unknown_key_inside_block_invalid(self):
        self.assertInvalid(
            {"native_orchestrator": True, "bogus": 1},
            "t9",
            "unsupported fields",
            "bogus",
            "orchestration",
        )

    def test_non_boolean_native_orchestrator_invalid(self):
        # 1 and 0 must be rejected too: JSON booleans are not integers here.
        for bad_value in ("yes", 1, 0, None):
            with self.subTest(value=bad_value):
                self.assertInvalid(
                    {"native_orchestrator": bad_value},
                    "t9",
                    "orchestration.native_orchestrator",
                    "boolean",
                )

    def test_invalid_dispatcher_binding_invalid(self):
        for bad_value in ("hosted", "ORCHESTRATOR-HOSTED", ""):
            with self.subTest(value=bad_value):
                self.assertInvalid(
                    {"dispatcher_binding": bad_value},
                    "t9",
                    "orchestration.dispatcher_binding",
                    "unsupported",
                )

    def test_orchestrator_hosted_requires_native_orchestrator_true(self):
        self.assertInvalid(
            {"dispatcher_binding": "orchestrator-hosted"},
            "t9",
            "orchestration.dispatcher_binding",
            "requires native_orchestrator = true",
        )
        self.assertInvalid(
            {
                "native_orchestrator": False,
                "dispatcher_binding": "orchestrator-hosted",
            },
            "t9",
            "orchestration.dispatcher_binding",
            "requires native_orchestrator = true",
        )


if __name__ == "__main__":
    unittest.main()
