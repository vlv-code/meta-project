#!/usr/bin/env python3
"""
Wave J Scripts Test Suite — verify_identity lane (Parts A + B).

Part A — single source of truth for host-harness detection:
  scripts/_common.py owns HOST_HARNESS_SIGNATURES + detect_host_harness
  (the corrected 2026-11-22 mini-tail signatures). verify_identity.py used
  to carry a STALE second copy (HARNESS_ENV_MAP with ZCODE_AGENT /
  CLAUDE_CODE / CODEX_AGENT markers) that returns None in a real ZCode
  session, so the `--actor` "Host harness mismatch" warning could never
  fire there. Both modules must consume the shared implementation.

Part B — optional `orchestration` block validation on registry
  installations (native_orchestrator declaration + dispatcher_binding
  standalone|orchestrator-hosted). Additive fields under schema 1.1.0.

RED-first discipline: Part A tests 1-4 and Part B tests 8-12 fail on the
pre-fix scripts; Part B tests 5-7 and 13 are lock-in tests.

Zero-dependency Python 3.10+ stdlib (unittest).
"""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import inspect_meta_project, verify_identity

PROJECT_ID = "vlv-code/meta-project"
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_identity.py"


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


# Sentinel distinguishing "key absent" from "explicit null" in fixtures.
_ABSENT = object()


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
