#!/usr/bin/env python3
"""
Wave G, Lane I — Facts digest (Astra facts cache, honest minimal form).

Plan: docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md (§6).

Locks in the ``--facts-digest`` contract of scripts/inspect_meta_project.py:
a deterministic compact JSON fingerprint of the REPOSITORY (classified state,
per-slice sha256 for the 5 knowledge slices + the registry, capability matrix,
harness/installation echo) that an agent can stash and later diff cheaply
instead of re-reading every slice. No disk cache is ever written (zero new
state); without --harness/--installation the digest is still emitted, with
state CONTEXT_UNRESOLVED — the digest describes the repository, not the
runtime. Plus the auditor doc-contradiction lock: the module docstring must
admit the 8 canonical states (CONTEXT_UNRESOLVED included).

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import hashlib
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

from scripts.inspect_meta_project import FACTS_DIGEST_VERSION, compute_facts_digest

SCRIPT_PATH = REPO_ROOT / "scripts" / "inspect_meta_project.py"

SLICE_PATHS = (
    ".agents/project_knowledge/architecture.md",
    ".agents/project_knowledge/boundaries.md",
    ".agents/project_knowledge/weak_spots.md",
    ".agents/project_knowledge/observations.md",
    ".agents/project_knowledge/tasks.md",
    ".agents/meta-project.json",
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_snapshot(root: Path) -> dict:
    """Content snapshot of every file under root (catches writes, deletes,
    and same-size silent rewrites — stronger than size+mtime)."""
    snapshot: dict = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            snapshot[str(p.relative_to(root)).replace("\\", "/")] = _sha256_file(p)
    return snapshot


class TestFactsDigest(unittest.TestCase):
    """--facts-digest: deterministic, sensitive, zero-write, composable."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_gwave_i_")
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_minimal_metaproject(
        self, active_harness: str = "antigravity", active_installation: str = "ag-main"
    ) -> None:
        """Fixture reused from tests/test_inspect_meta_project.py (same
        structure; its registry passes the canonical identity validator)."""
        agents_md = self.root / "AGENTS.md"
        agents_md.write_text(
            "# Project Passport: Test\n## 1. Concept, Principles, and North Stars\n"
            "## 3. Directive Meta-Knowledge Protocol\n## 6. Project Agent Team & Multi-Harness Identity\n",
            encoding="utf-8",
        )
        pk = self.root / ".agents" / "project_knowledge"
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

        scripts_dir = self.root / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "check_boundaries.py").write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )
        (scripts_dir / "verify_identity.py").write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )

        skills_dir = self.root / ".agents" / "skills" / "record-observation"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            "---\nname: record-observation\n---\n# Skill\n", encoding="utf-8"
        )

        team_dir = self.root / ".agents" / "team" / "agent-dev-lead"
        team_dir.mkdir(parents=True)
        (team_dir / "profile.md").write_text(
            f"---\nrole_id: agent-dev-lead\nharness_id: {active_harness}\n"
            f"installation_id: {active_installation}\n"
            f"actor_id: vlv-code/test-project::{active_harness}::{active_installation}::agent-dev-lead\n---\n",
            encoding="utf-8",
        )

        registry = {
            "schema_version": "1.0.0",
            "project_id": "vlv-code/test-project",
            "installations": {
                active_installation: {
                    "harness_id": active_harness,
                    "status": "active",
                    "description": "Active installation",
                },
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
                        active_installation: {
                            "actor_id": (
                                f"vlv-code/test-project::{active_harness}"
                                f"::{active_installation}::agent-dev-lead"
                            ),
                            "status": "active",
                            "profile_path": ".agents/team/agent-dev-lead/profile.md",
                        },
                        "zc-main": {
                            "actor_id": "vlv-code/test-project::zcode::zc-main::agent-dev-lead",
                            "status": "planned",
                            "profile_path": None,
                        },
                    },
                }
            },
        }
        (self.root / ".agents" / "meta-project.json").write_text(
            json.dumps(registry, indent=2), encoding="utf-8"
        )

    def _run_digest(self, extra_args=None, cwd=None) -> subprocess.CompletedProcess:
        cmd = [sys.executable, "-B", str(SCRIPT_PATH), "--repo-root", str(self.root), "--facts-digest"]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def _digest_payload(self, extra_args=None) -> dict:
        proc = self._run_digest(extra_args)
        self.assertEqual(
            proc.returncode, 0, f"rc={proc.returncode}, stderr={proc.stderr}"
        )
        return json.loads(proc.stdout)

    # ------------------------------------------------------------------
    # Determinism (RED-first: two consecutive runs byte-identical)
    # ------------------------------------------------------------------
    def test_digest_two_consecutive_runs_byte_identical(self):
        self._create_minimal_metaproject()
        first = self._run_digest()
        second = self._run_digest()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            first.stdout,
            second.stdout,
            "facts digest must be byte-stable for identical inputs",
        )

    def test_digest_shape_and_version_constant(self):
        self._create_minimal_metaproject()
        data = self._digest_payload()
        self.assertEqual(data["facts_digest_version"], "1")
        self.assertEqual(data["facts_digest_version"], FACTS_DIGEST_VERSION)
        # Exact top-level key set — the digest is a stable contract, no
        # opportunistic extra keys (byte-stability depends on it).
        self.assertEqual(
            sorted(data.keys()),
            ["capabilities", "facts_digest_version", "harness", "installation", "slices", "state"],
        )
        self.assertEqual(sorted(data["slices"].keys()), sorted(SLICE_PATHS))
        self.assertEqual(
            sorted(data["capabilities"].keys()),
            ["hooks", "local_checks", "read_instructions", "roles", "skills"],
        )
        for cap in data["capabilities"].values():
            self.assertIsInstance(cap, str)
        for rel in SLICE_PATHS:
            digest_value = data["slices"][rel]
            self.assertIsInstance(digest_value, str)
            self.assertEqual(digest_value, _sha256_file(self.root / rel))

    # ------------------------------------------------------------------
    # Absent slices -> null
    # ------------------------------------------------------------------
    def test_digest_absent_slices_null_on_empty_repo(self):
        data = self._digest_payload()
        self.assertEqual(data["state"], "NONE")
        self.assertEqual(data["facts_digest_version"], "1")
        for rel in SLICE_PATHS:
            self.assertIsNone(data["slices"][rel], f"{rel} must be null when absent")

    # ------------------------------------------------------------------
    # Sensitivity: one modified slice -> exactly that hash flips
    # ------------------------------------------------------------------
    def test_digest_single_slice_flip_sensitivity(self):
        self._create_minimal_metaproject()
        before = self._digest_payload()
        # Modify exactly one knowledge slice (classification-safe append).
        tasks_path = self.root / ".agents" / "project_knowledge" / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8") + "- [ ] new step\n",
            encoding="utf-8",
        )
        after = self._digest_payload()
        changed = {
            rel for rel in SLICE_PATHS if before["slices"][rel] != after["slices"][rel]
        }
        self.assertEqual(
            changed,
            {".agents/project_knowledge/tasks.md"},
            "exactly the modified slice's hash must flip",
        )
        self.assertEqual(
            after["slices"][".agents/project_knowledge/tasks.md"],
            _sha256_file(tasks_path),
        )
        # The rest of the digest is unchanged (state classification included).
        self.assertEqual(before["state"], after["state"])
        self.assertEqual(before["capabilities"], after["capabilities"])

    # ------------------------------------------------------------------
    # Zero-write invariant (survey-first, no disk cache)
    # ------------------------------------------------------------------
    def test_digest_zero_write_invariant(self):
        self._create_minimal_metaproject()
        before = _tree_snapshot(self.root)
        proc = self._run_digest(["--read-only"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = _tree_snapshot(self.root)
        self.assertEqual(
            before,
            after,
            "--facts-digest must produce zero disk modifications "
            "(no lock files, no disk cache, no telemetry)",
        )

    # ------------------------------------------------------------------
    # Context-unresolved behavior (digest describes the REPOSITORY)
    # ------------------------------------------------------------------
    def test_digest_context_unresolved_without_flags(self):
        self._create_minimal_metaproject()
        data = self._digest_payload()
        self.assertEqual(data["state"], "CONTEXT_UNRESOLVED")
        self.assertIsNone(data["harness"])
        self.assertIsNone(data["installation"])
        self.assertEqual(data["capabilities"]["roles"], "untested")

    # ------------------------------------------------------------------
    # Compositability with --harness/--installation
    # ------------------------------------------------------------------
    def test_digest_composable_with_context_flags(self):
        self._create_minimal_metaproject()
        args = ["--harness", "antigravity", "--installation", "ag-main"]
        first = self._run_digest(args)
        second = self._run_digest(args)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            first.stdout,
            second.stdout,
            "digest with context flags must also be byte-stable",
        )
        data = json.loads(first.stdout)
        self.assertEqual(data["state"], "HEALTHY_REGISTERED")
        self.assertEqual(data["harness"], "antigravity")
        self.assertEqual(data["installation"], "ag-main")
        self.assertEqual(data["capabilities"]["roles"], "available")

    def test_digest_function_is_pure_and_ordered(self):
        """compute_facts_digest returns the payload without touching disk
        beyond reading slices, and the CLI serializes it deterministically
        (sort_keys + fixed separators)."""
        self._create_minimal_metaproject()
        from scripts.inspect_meta_project import inspect_repository

        report = inspect_repository(self.root)
        digest = compute_facts_digest(self.root, report)
        canonical = json.dumps(
            digest, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        # Same serialization the CLI emits (module-level contract, not a
        # call-site choice).
        proc = self._run_digest()
        self.assertEqual(proc.stdout.strip(), canonical)


class TestInspectDocstringCanon(unittest.TestCase):
    """Auditor doc-contradiction #3: the module docstring said 7 canonical
    states while the code implements 8 (CONTEXT_UNRESOLVED included)."""

    def test_docstring_lists_eight_canonical_states(self):
        doc = (REPO_ROOT / "scripts" / "inspect_meta_project.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("8 canonical states", doc)
        self.assertIn("CONTEXT_UNRESOLVED", doc)
        self.assertNotIn("7 canonical states", doc)


if __name__ == "__main__":
    unittest.main()
