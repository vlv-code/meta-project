#!/usr/bin/env python3
"""
Wave J Scripts Test Suite — manage intake lane (Part D).

The manage intake registry-delta gate must cover the installation-level
`orchestration` declaration: a new change kind `set_orchestration`
({"kind": "set_orchestration", "installation": "<installation_id>"}, no
role_id, no path) whose delta element is ("set_orchestration", "",
installation_id). Previously an orchestration-only registry change was
either refused as an unsupported declaration or — worse — slipped through
unnoticed alongside an unrelated declared role change.

Fixture modeled on tests/test_dwave_m.py::TestDeclaredDeltaIntake (seeded
git repo, committed baseline registry, init report saved at that commit,
registry mutated, manage CLI invoked). Own helpers; the dwave class is not
modified.

RED-first discipline: tests 22, 24, 25 and 26 fail on the pre-fix engine;
tests 23, 27 and 28 are lock-in tests (refuse-no-declaration and the
unchanged-registry admission must survive the vocabulary extension).

Zero-dependency Python 3.10+ stdlib (unittest).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MANAGE_REPORTS_SCRIPT = REPO_ROOT / "scripts" / "manage_reports.py"

PROJECT_ID = "acme/app"
HARNESS = "zcode"
INSTALLATION = "t9"
ACTOR = f"{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-dev-lead"

REGISTRY_REL = ".agents/meta-project.json"
BOUNDARIES_REL = ".agents/project_knowledge/boundaries.md"

AGENTS_MD = (
    "# Project Passport: Fixture\n\n"
    "## 1. Concept, Principles, and North Stars\n"
    "- Meta-Project fixture passport.\n"
)

BOUNDARIES_MD = (
    "# Responsibility Zones and Change Boundaries\n\n"
    "## Green Zone (Autonomous Modification)\n"
    "- `docs/**`\n\n"
    "## Yellow Zone (Modification with Mandatory Verification)\n"
    "- `scripts/**`\n\n"
    "## Red Zone (Prohibited Without Direct User Confirmation)\n"
    "- `LICENSE`\n"
)

DECLARED_BLOCK = {
    "native_orchestrator": True,
    "dispatcher_binding": "orchestrator-hosted",
}

# Sentinel distinguishing "orchestration key absent" from "explicit null".
ABSENT = object()


def _binding(role_id: str, status: str = "active") -> dict:
    return {
        "actor_id": f"{PROJECT_ID}::{HARNESS}::{INSTALLATION}::{role_id}",
        "status": status,
        "profile_path": f".agents/team/{role_id}/profile.md",
    }


def _role_entry(role_id: str) -> dict:
    return {
        "description": f"fixture role {role_id}",
        "bindings": {INSTALLATION: _binding(role_id)},
    }


DEFAULT_ROLES = {
    "agent-dev-lead": {
        "description": "fixture lead role",
        "bindings": {INSTALLATION: _binding("agent-dev-lead")},
    }
}


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    res = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )
    assert res.returncode == 0, f"git {' '.join(args)} failed: {res.stderr}"
    return res


def _run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MANAGE_REPORTS_SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def _write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return path


class TestSetOrchestrationDelta(unittest.TestCase):
    """Part D: the set_orchestration intake vocabulary."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="jwave_m_")
        self.root = Path(self.temp_dir).resolve()
        self._seed_repo()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- fixture helpers ---------------------------------------------------

    def _seed_repo(self, roles=None, orchestration=ABSENT):
        root = self.root
        (root / "AGENTS.md").write_text(AGENTS_MD, encoding="utf-8")
        (root / BOUNDARIES_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / BOUNDARIES_REL).write_text(BOUNDARIES_MD, encoding="utf-8")
        self._write_registry(roles if roles is not None else DEFAULT_ROLES, orchestration)
        profile = root / ".agents" / "team" / "agent-dev-lead" / "profile.md"
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Dev Lead"\n'
            'role_id: "agent-dev-lead"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{ACTOR}"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "fixture@example.com")
        _git(root, "config", "user.name", "Fixture")
        _git(root, "add", "-A")
        _git(root, "commit", "-qm", "fixture: committed registry baseline")

    def _write_registry(self, roles: dict, orchestration) -> dict:
        installation = {
            "harness_id": HARNESS,
            "status": "active",
            "description": "fixture installation",
        }
        if orchestration is not ABSENT:
            installation["orchestration"] = orchestration
        registry = {
            "schema_version": "1.1.0",
            "project_id": PROJECT_ID,
            "installations": {INSTALLATION: installation},
            "roles": roles,
        }
        _write_json(self.root / REGISTRY_REL, registry)
        return registry

    def _current_registry(self) -> dict:
        return json.loads(
            (self.root / REGISTRY_REL).read_text(encoding="utf-8")
        )

    def _save_registry(self, registry: dict) -> None:
        """Simulate the manage operation mutating the registry on disk."""
        _write_json(self.root / REGISTRY_REL, registry)

    def _add_registry_role(self, registry: dict, role_id: str) -> dict:
        registry = json.loads(json.dumps(registry))
        registry["roles"][role_id] = _role_entry(role_id)
        return registry

    def _set_orchestration(self, registry: dict, orchestration) -> dict:
        registry = json.loads(json.dumps(registry))
        installation = registry["installations"][INSTALLATION]
        if orchestration is ABSENT:
            installation.pop("orchestration", None)
        else:
            installation["orchestration"] = orchestration
        return registry

    def _save_init_report(self, run_id: str) -> dict:
        from scripts.manage_reports import create_init_report, save_report

        report = create_init_report(
            repo_root=self.root,
            installation_id=INSTALLATION,
            harness_id=HARNESS,
            actor_id=ACTOR,
            project_id=PROJECT_ID,
            status="completed",
            scenario={
                "profile": "active_development",
                "collaboration_model": "duo",
                "verification_policy": "duo_peer_review",
            },
            run_id=run_id,
        )
        save_report(self.root, INSTALLATION, "init", report)
        return report

    def _manage_create(
        self,
        init_run_id: str,
        changes=None,
        tag: str = "data",
    ) -> subprocess.CompletedProcess:
        payload = {
            "scenario": {
                "profile": "active_development",
                "collaboration_model": "duo",
            },
            "roles": {
                "preserved": ["agent-dev-lead"],
                "created": [],
                "adapted": [],
                "archived": [],
            },
            "bindings": {},
        }
        if changes is not None:
            payload["changes"] = changes
        data_file = _write_json(self.root / f"manage_{tag}.json", payload)
        return _run_cli(
            self.root,
            "manage",
            "--action",
            "create",
            "--repo-root",
            str(self.root),
            "--installation",
            INSTALLATION,
            "--harness",
            HARNESS,
            "--actor",
            ACTOR,
            "--init-run-id",
            init_run_id,
            "--status",
            "completed",
            "--data-file",
            str(data_file),
            "--json",
        )

    # -- tests ---------------------------------------------------------------

    def test_orchestration_only_change_with_declaration_admitted(self):
        """Test 22: an orchestration-only registry change declared via
        {"kind": "set_orchestration", "installation": "t9"} must be
        admitted (today: refused as an unsupported kind)."""
        run_id = "init-20261123T000000Z-aaa00001"
        self._save_init_report(run_id)
        self._save_registry(self._set_orchestration(self._current_registry(), DECLARED_BLOCK))
        changes = [{"kind": "set_orchestration", "installation": INSTALLATION}]
        res = self._manage_create(run_id, changes=changes, tag="orch_admitted")
        self.assertEqual(
            res.returncode,
            0,
            f"declared set_orchestration delta refused by intake "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))

    def test_orchestration_only_change_without_declaration_refused(self):
        """Test 23 (lock-in): an orchestration-only registry change with no
        declaration must still be refused as stale."""
        run_id = "init-20261123T000000Z-bbb00002"
        self._save_init_report(run_id)
        self._save_registry(self._set_orchestration(self._current_registry(), DECLARED_BLOCK))
        res = self._manage_create(run_id, tag="orch_undeclared")
        self.assertNotEqual(
            res.returncode,
            0,
            f"undeclared registry change admitted: {res.stdout!r}",
        )
        combined = (res.stdout + res.stderr).lower()
        self.assertTrue(
            "stale" in combined or "declare" in combined,
            f"refusal must present as stale/undeclared delta: {combined!r}",
        )

    def test_undeclared_orchestration_change_alongside_declared_role_refused(self):
        """Test 24 (adversarial): an UNDECLARED orchestration change made
        alongside a correctly declared add_role must be refused with the
        refusal naming set_orchestration and the installation (today: the
        orchestration change is admitted silently)."""
        run_id = "init-20261123T000000Z-ccc00003"
        self._save_init_report(run_id)
        registry = self._current_registry()
        registry = self._add_registry_role(registry, "agent-quality-guardian")
        registry = self._set_orchestration(registry, DECLARED_BLOCK)
        self._save_registry(registry)
        profile = (
            self.root / ".agents" / "team" / "agent-quality-guardian" / "profile.md"
        )
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Quality Guardian"\n'
            'role_id: "agent-quality-guardian"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-quality-guardian"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
            }
        ]
        res = self._manage_create(run_id, changes=changes, tag="orch_hidden")
        self.assertNotEqual(
            res.returncode,
            0,
            f"undeclared orchestration change admitted silently alongside a "
            f"declared role change: {res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            "set_orchestration",
            combined,
            f"refusal must name the set_orchestration delta element: {combined!r}",
        )
        self.assertIn(
            INSTALLATION,
            combined,
            f"refusal must name the installation: {combined!r}",
        )

    def test_declared_set_orchestration_without_matching_delta_refused(self):
        """Test 25: a declared set_orchestration with NO actual orchestration
        change must be refused as a declaration without a matching delta,
        even when the role part is correctly declared."""
        run_id = "init-20261123T000000Z-ddd00004"
        self._save_init_report(run_id)
        registry = self._current_registry()
        registry = self._add_registry_role(registry, "agent-quality-guardian")
        self._save_registry(registry)
        profile = (
            self.root / ".agents" / "team" / "agent-quality-guardian" / "profile.md"
        )
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "---\n"
            'name: "Quality Guardian"\n'
            'role_id: "agent-quality-guardian"\n'
            f'harness_id: "{HARNESS}"\n'
            f'installation_id: "{INSTALLATION}"\n'
            f'actor_id: "{PROJECT_ID}::{HARNESS}::{INSTALLATION}::agent-quality-guardian"\n'
            "---\n# Role Passport\n",
            encoding="utf-8",
        )
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
            },
            {"kind": "set_orchestration", "installation": INSTALLATION},
        ]
        res = self._manage_create(run_id, changes=changes, tag="orch_unmatched")
        self.assertNotEqual(
            res.returncode,
            0,
            f"declaration without a matching registry delta admitted: "
            f"{res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            "no matching registry delta",
            combined,
            f"refusal must classify set_orchestration as unmatched "
            f"declaration: {combined!r}",
        )
        self.assertIn("set_orchestration", combined)

    def test_invalid_set_orchestration_declarations_refused(self):
        """Test 26 (adversarial): set_orchestration must not carry role_id
        or path, and requires the installation field."""
        run_id = "init-20261123T000000Z-eee00005"
        self._save_init_report(run_id)
        # Make the registry actually differ so declaration normalization
        # runs (an unchanged registry short-circuits before validation).
        self._save_registry(self._set_orchestration(self._current_registry(), DECLARED_BLOCK))

        cases = [
            (
                {"kind": "set_orchestration", "role_id": "agent-x", "installation": INSTALLATION},
                "must not carry role_id",
            ),
            (
                {"kind": "set_orchestration"},
                "installation is required for kind 'set_orchestration'",
            ),
            (
                {"kind": "set_orchestration", "installation": INSTALLATION, "path": "x.md"},
                "must not carry path",
            ),
        ]
        for idx, (declared, expected_problem) in enumerate(cases):
            with self.subTest(case=idx):
                res = self._manage_create(
                    run_id, changes=[declared], tag=f"orch_invalid_{idx}"
                )
                self.assertNotEqual(
                    res.returncode,
                    0,
                    f"invalid declaration admitted: {res.stdout!r}",
                )
                combined = res.stdout + res.stderr
                self.assertIn(
                    "invalid changes[] declaration",
                    combined,
                    f"refusal must classify the declaration as invalid: {combined!r}",
                )
                self.assertIn(
                    expected_problem,
                    combined,
                    f"refusal must carry the exact problem message "
                    f"{expected_problem!r}: {combined!r}",
                )

    def test_removing_block_is_set_orchestration_delta(self):
        """Test 27: removing an existing orchestration block (block -> key
        absent) is a set_orchestration delta and admits when declared."""
        run_id = "init-20261123T000000Z-fff00006"
        self._seed_repo(orchestration=DECLARED_BLOCK)
        self._save_init_report(run_id)
        self._save_registry(self._set_orchestration(self._current_registry(), ABSENT))
        changes = [{"kind": "set_orchestration", "installation": INSTALLATION}]
        res = self._manage_create(run_id, changes=changes, tag="orch_removal")
        self.assertEqual(
            res.returncode,
            0,
            f"declared block-removal delta refused by intake "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))

    def test_unchanged_roles_and_orchestration_admitted_without_declarations(self):
        """Test 28 (lock-in): a registry whose roles AND orchestration are
        unchanged since the init report is admitted without declarations."""
        run_id = "init-20261123T000000Z-ggg00007"
        self._seed_repo(orchestration=DECLARED_BLOCK)
        self._save_init_report(run_id)
        res = self._manage_create(run_id, tag="orch_untouched")
        self.assertEqual(
            res.returncode,
            0,
            f"unchanged registry refused (false positive): "
            f"stdout={res.stdout!r}, stderr={res.stderr!r}",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))


if __name__ == "__main__":
    unittest.main()
