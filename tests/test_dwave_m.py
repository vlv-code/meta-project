#!/usr/bin/env python3
"""
Wave D Lane M Test Suite — Manage Admission & Reports (plan §4, T2.1–T2.3).

Zero-dependency Python 3.10+ stdlib test suite.

Contract under test (plan 2026-11-15-wave-d-state-integrity-and-perimeter.md):

T2.1 — Pre-op admission + declared-delta verification (auditor п.3):
  - A fresh init report followed by a registry change EXACTLY equal to the
    manage operation's declared `changes[]` must be ADMITTED (previously the
    registry fingerprint delta produced a false "stale report" refusal).
  - A registry change NOT fully covered by the declared `changes[]` must be
    refused with an explicit diff listing (uncovered delta elements named).
  - Staleness for non-declared essential inputs (boundaries.md, AGENTS.md)
    must remain (declared deltas widen the contract ONLY for the registry).
  - Commit-HEAD freshness is replaced by init-report supersession: a newer
    init run for the installation refuses the older referenced report (with
    a pointer), while pure commit movement with fresh inputs is admitted.

T2.2 — `tune` CLI subcommand: `manage_reports.py tune --action create`
  creates a valid tune report via save_report; `latest --type tune` returns
  it (previously: argparse "invalid choice: 'tune'").

T2.3 — Bootstrap path documentation lives in
  skills/manage-meta-project/SKILL.md (Phase 0.5 — First-Role Bootstrap);
  this suite does not gate prose, only the engine behavior it documents.

RED-first discipline: T2.1 admission test, supersession test, commit-movement
test, and the T2.2 roundtrip FAIL on the pre-fix engine; the two refusal
tests are lock-in tests (they must stay green before AND after).
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
HARNESS = "antigravity"
INSTALLATION = "ag-main"
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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


class TestDeclaredDeltaIntake(unittest.TestCase):
    """T2.1: pre-op admission with declared-delta verification."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_m_")
        self.root = Path(self.temp_dir).resolve()
        self._seed_repo()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- fixture helpers ---------------------------------------------------

    def _seed_repo(self):
        root = self.root
        (root / "AGENTS.md").write_text(AGENTS_MD, encoding="utf-8")
        (root / BOUNDARIES_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / BOUNDARIES_REL).write_text(BOUNDARIES_MD, encoding="utf-8")
        self._write_registry(DEFAULT_ROLES)
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

    def _write_registry(self, roles: dict) -> dict:
        registry = {
            "schema_version": "1.1.0",
            "project_id": PROJECT_ID,
            "installations": {
                INSTALLATION: {
                    "harness_id": HARNESS,
                    "status": "active",
                    "description": "fixture installation",
                }
            },
            "roles": roles,
        }
        _write_json(self.root / REGISTRY_REL, registry)
        return registry

    def _add_registry_role(self, role_id: str):
        """Simulate the manage operation mutating the registry on disk."""
        registry = json.loads(
            (self.root / REGISTRY_REL).read_text(encoding="utf-8")
        )
        registry["roles"][role_id] = _role_entry(role_id)
        _write_json(self.root / REGISTRY_REL, registry)

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
        data_file = _write_json(
            self.root / f"manage_{tag}.json", payload
        )
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

    # -- T2.1 tests ---------------------------------------------------------

    def test_manage_allows_declared_registry_change(self):
        """Registry delta EXACTLY equal to declared changes[] must be
        admitted: the natural init -> manage(adds roles) -> report flow must
        not die on 'stale report: essential input changed' (auditor п.3)."""
        run_id = "init-20260101T000000Z-aaa00001"
        self._save_init_report(run_id)
        self._add_registry_role("agent-quality-guardian")
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
                "path": ".agents/team/agent-quality-guardian/profile.md",
            }
        ]
        res = self._manage_create(run_id, changes=changes)
        self.assertEqual(
            res.returncode,
            0,
            f"declared registry delta refused by intake "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))

        # Formalization: the saved manage report records the declared delta.
        report_path = Path(created["report_path"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(
            report.get("changes"),
            changes,
            "manage report must record the declared changes[] verbatim",
        )

    def test_manage_rejects_undeclared_registry_change(self):
        """A registry delta NOT fully covered by declared changes[] must be
        refused with an explicit diff listing naming the uncovered delta."""
        run_id = "init-20260101T000000Z-bbb00002"
        self._save_init_report(run_id)
        self._add_registry_role("agent-quality-guardian")
        # Second, UNDECLARED registry mutation.
        self._add_registry_role("agent-github-steward")
        changes = [
            {
                "kind": "add_role",
                "role_id": "agent-quality-guardian",
                "installation": INSTALLATION,
            }
        ]
        res = self._manage_create(run_id, changes=changes, tag="undeclared")
        self.assertNotEqual(
            res.returncode,
            0,
            f"partially declared registry delta admitted: {res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            "agent-github-steward",
            combined,
            f"refusal must list the uncovered registry delta element: {combined!r}",
        )
        self.assertTrue(
            "not covered" in combined.lower() or "delta" in combined.lower(),
            f"refusal must explain the declared-delta mismatch: {combined!r}",
        )

    def test_manage_rejects_unrelated_slice_change(self):
        """Lock-in: staleness for NON-declared essential inputs stays.
        boundaries.md changed since the init report -> refused even when the
        registry itself is untouched."""
        run_id = "init-20260101T000000Z-ccc00003"
        self._save_init_report(run_id)
        boundaries = self.root / BOUNDARIES_REL
        boundaries.write_text(
            BOUNDARIES_MD + "\n- `extra/path/**` appended post-report\n",
            encoding="utf-8",
        )
        res = self._manage_create(run_id, changes=[], tag="boundaries")
        self.assertNotEqual(
            res.returncode,
            0,
            f"boundaries.md drift admitted by intake: {res.stdout!r}",
        )
        combined = (res.stdout + res.stderr).lower()
        self.assertTrue(
            "boundaries" in combined or "stale" in combined,
            f"refusal must name the drifted input: {combined!r}",
        )

    def test_manage_rejects_superseded_init_report(self):
        """A newer init run for the installation supersedes the referenced
        report: refuse with a pointer to the newer run."""
        older = "init-20260101T000000Z-old00001"
        newer = "init-20260101T000000Z-new00002"
        self._save_init_report(older)
        self._save_init_report(newer)
        res = self._manage_create(older, tag="superseded")
        self.assertNotEqual(
            res.returncode,
            0,
            f"superseded init report still authorizes manage: {res.stdout!r}",
        )
        combined = res.stdout + res.stderr
        self.assertIn(
            newer,
            combined,
            f"supersession refusal must point at the newer init run: {combined!r}",
        )

    def test_manage_ignores_commit_movement_when_inputs_fresh(self):
        """Commit movement alone (fresh essential inputs, non-superseded
        report) must NOT refuse manage: the commit-moved false positive is
        replaced by the supersession check."""
        run_id = "init-20260101T000000Z-ddd00004"
        self._save_init_report(run_id)
        # Move HEAD without touching any essential input.
        src = self.root / "src"
        src.mkdir(exist_ok=True)
        (src / "feature.py").write_text("# feature\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "second commit: src only")
        res = self._manage_create(run_id, tag="commitmoved")
        self.assertEqual(
            res.returncode,
            0,
            f"commit movement with fresh inputs refused (false positive): "
            f"stdout={res.stdout!r}, stderr={res.stderr!r}",
        )


class TestTuneSubcommand(unittest.TestCase):
    """T2.2: `tune` CLI subcommand creating and locating tune reports."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_m_tune_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tune_create_and_latest_roundtrip(self):
        proposals = [
            {
                "id": "P-1",
                "target": "role topology",
                "proposal": "Add agent-quality-guardian binding for ag-main",
                "hypothesis": "verification throughput improves",
                "evidence": "friction cluster in handoff logs",
                "decision": "proposed",
            }
        ]
        data_file = _write_json(
            self.root / "tune_data.json", {"proposals": proposals}
        )
        res = _run_cli(
            self.root,
            "tune",
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
            "--project-id",
            PROJECT_ID,
            "--status",
            "awaiting_decision",
            "--data-file",
            str(data_file),
            "--json",
        )
        self.assertEqual(
            res.returncode,
            0,
            f"tune create failed (stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        created = json.loads(res.stdout)
        self.assertTrue(created.get("success"))
        report_path = Path(created["report_path"])
        self.assertTrue(report_path.exists(), "tune report file not written")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report.get("report_type"), "tune")
        self.assertEqual(report.get("proposals"), proposals)

        # Roundtrip: latest --type tune returns the created report.
        res_latest = _run_cli(
            self.root,
            "latest",
            "--repo-root",
            str(self.root),
            "--installation",
            INSTALLATION,
            "--type",
            "tune",
            "--json",
        )
        self.assertEqual(
            res_latest.returncode,
            0,
            f"latest --type tune failed: {res_latest.stdout!r} {res_latest.stderr!r}",
        )
        found = json.loads(res_latest.stdout)
        self.assertTrue(found.get("found"))
        self.assertEqual(found.get("run_id"), created["run_id"])

        # Verify action mirrors init/manage.
        res_verify = _run_cli(
            self.root,
            "tune",
            "--action",
            "verify",
            "--report",
            str(report_path),
            "--json",
        )
        self.assertEqual(res_verify.returncode, 0, res_verify.stdout + res_verify.stderr)
        self.assertTrue(json.loads(res_verify.stdout).get("valid"))


if __name__ == "__main__":
    unittest.main()
