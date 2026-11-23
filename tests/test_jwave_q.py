#!/usr/bin/env python3
"""
Wave J Scripts Test Suite — inspector lane (Part C).

The inspector must report the DECLARED orchestration of the target
installation (agent-intake-dispatcher standalone vs orchestrator-hosted
binding): a `resolve_orchestration` helper, an always-present
"orchestration" key in the inspect_repository report, and a
"Dispatcher Binding:" line in the human-readable report. The --facts-digest
payload is NOT touched (its top-level key set is locked by
tests/test_gwave_i.py).

RED-first discipline: tests 14-17 (helper), 18-20 (report key) and 21
(human report line) fail on the pre-fix inspector.

Zero-dependency Python 3.10+ stdlib (unittest).
"""

from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import inspect_meta_project
from scripts.inspect_meta_project import (
    format_human_report,
    inspect_repository,
)

PROJECT_ID = "vlv-code/test-project"
HARNESS = "antigravity"
INSTALLATION = "ag-main"
ACTOR_ID = f"{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-dev-lead"


_ABSENT = object()


def _make_fixture(root: Path, orchestration) -> None:
    """Clean-room healthy meta-project fixture (modeled on
    tests/test_inspect_meta_project.py::_write_minimal_metaproject) whose
    active installation optionally carries an `orchestration` block
    (sentinel _ABSENT = key not written; None = explicit null in JSON)."""
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


if __name__ == "__main__":
    unittest.main()
