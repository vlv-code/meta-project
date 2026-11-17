"""
Wave E — Lane P2 lock-in tests (init lazy-load pilot: resource extraction).

Plan: docs/superpowers/plans/2026-11-16-wave-e-context-economy.md
(§6 Lane P + §6a owner decision ADJUST AND PROCEED).

Locks in (RED-first where machine behavior changes):
  (a) update engine maps resource components `skills/<name>/resources/<file>`
      to the runtime layout `.agents/skills/<name>/resources/<file>` when the
      target repo has `.agents/skills/` (recorded lock targets stay
      authoritative; distribution path unchanged without `.agents/skills/`).
  (b) canonical manifest declares the 9 init resource components
      (kind "resource", requires the init SKILL.md) and bumps
      framework_version to 1.0.0-alpha.4.
  (c) init SKILL.md carries the Resource Loading Contract: repeat-run reads
      NO resources; clean init reads each resource exactly when its step
      needs it; Scenario 4 reads only its procedure; a missing mandatory
      resource BLOCKS the dependent step with the Lane E envelope
      (code: MISSING_RESOURCE) and the pinned-source guidance; per-step
      resource pointers name all 9 files; no embedded TEMPLATE blocks remain.
  (d) sync_templates reaches 0 drift on the real repo after --write (--check).
  (e) every resources/ file is byte-equal to its canonical source.

Zero-dependency: Python 3.10+ stdlib only.
"""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = ROOT_DIR / "CHANGELOG.md"
RESOURCES_DIR = ROOT_DIR / "skills" / "init-meta-project" / "resources"
MIRROR_RESOURCES_DIR = ROOT_DIR / ".agents" / "skills" / "init-meta-project" / "resources"
INIT_SKILL_PATH = ROOT_DIR / "skills" / "init-meta-project" / "SKILL.md"
MANIFEST_PATH = ROOT_DIR / "templates" / "release_manifest.json"
SYNC_SCRIPT = ROOT_DIR / "scripts" / "sync_templates.py"

SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import sync_templates
except ImportError:
    sync_templates = None

try:
    from scripts.update_meta_project import _resolve_target
except ImportError:
    _resolve_target = None

# resource file name -> canonical source (relative to repo root)
CANONICAL_SOURCES = {
    "observations.md": "templates/project_knowledge/observations.md",
    "boundaries.md": "templates/project_knowledge/boundaries.md",
    "weak_spots.md": "templates/project_knowledge/weak_spots.md",
    "architecture.md": "templates/project_knowledge/architecture.md",
    "tasks.md": "templates/project_knowledge/tasks.md",
    "AGENTS.md": "templates/AGENTS.md",
    "record-observation-SKILL.md": "skills/record-observation/SKILL.md",
    "sync-architecture-SKILL.md": "skills/sync-architecture/SKILL.md",
    "ground-meta-project-SKILL.md": "skills/ground-meta-project/SKILL.md",
}

MISSING_RESOURCE_GUIDANCE = (
    "missing mandatory resource 'resources/<name>' — reinstall the skill "
    "from the pinned source (update-meta-project) or restore the file; "
    "do not improvise the template from memory"
)


def _latest_changelog_version() -> str:
    """Latest release version heading from CHANGELOG.md
    (``## [1.0.0-alpha.4] - YYYY-MM-DD`` style), skipping [Unreleased]."""
    for line in CHANGELOG_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## [") and "]" in stripped:
            version = stripped[4:stripped.index("]")].strip()
            if version and version.lower() != "unreleased":
                return version
    raise AssertionError("no release version heading found in CHANGELOG.md")


class TestEngineResourceRuntimeLayout(unittest.TestCase):
    """(a) Engine maps resource components into the .agents/skills runtime layout."""

    def setUp(self):
        if _resolve_target is None:
            self.skipTest("update_meta_project engine module not importable")

    def _repo_with_runtime_layout(self, root: Path) -> Path:
        (root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
        return root

    def test_resource_component_maps_to_agents_skills_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_runtime_layout(Path(tmp))
            for res_name in ("AGENTS.md", "record-observation-SKILL.md"):
                self.assertEqual(
                    _resolve_target(
                        f"skills/init-meta-project/resources/{res_name}", repo, None
                    ),
                    f".agents/skills/init-meta-project/resources/{res_name}",
                    "resource component must install at the runtime layout path",
                )

    def test_recorded_target_stays_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_runtime_layout(Path(tmp))
            self.assertEqual(
                _resolve_target(
                    "skills/init-meta-project/resources/AGENTS.md",
                    repo,
                    {"target": "skills/init-meta-project/resources/AGENTS.md"},
                ),
                "skills/init-meta-project/resources/AGENTS.md",
                "a recorded lock target must win over the fresh layout rule",
            )

    def test_without_agents_skills_distribution_path_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)  # no .agents/skills/
            self.assertEqual(
                _resolve_target(
                    "skills/init-meta-project/resources/AGENTS.md", repo, None
                ),
                "skills/init-meta-project/resources/AGENTS.md",
            )

    def test_plain_skill_mapping_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_runtime_layout(Path(tmp))
            self.assertEqual(
                _resolve_target("skills/w/SKILL.md", repo, None),
                ".agents/skills/w/SKILL.md",
            )


class TestManifestResourceComponents(unittest.TestCase):
    """(b) Manifest gains the 9 resource components and bumps to alpha.4."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.components = cls.manifest.get("components") or []

    def test_framework_version_matches_changelog_latest(self):
        """Wave F T-D6 lock: manifest framework_version must equal the latest
        release version heading in CHANGELOG.md (the two are bumped together
        at release time). Supersedes the frozen '1.0.0-alpha.4' hardcode,
        which went stale at every release bump while still asserting exact
        equality."""
        self.assertEqual(
            self.manifest.get("framework_version"),
            _latest_changelog_version(),
            "manifest framework_version must equal the latest CHANGELOG "
            "release heading (bump both together at release time)",
        )

    def test_init_resource_components_declared(self):
        """Wave G Lane S supersession (plan
        docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md §4 —
        mandated manifest change): the manifest resource set grew from 9 to 12
        (3 manage resources riding the same init-P2 pattern), so the former
        exact-set equality over ALL resource components is superseded to a
        subset lock: the 9 init resources are declared with their init-SKILL.md
        requires edge. The 3 manage components are locked by
        tests/test_gwave_s.py (TestManifestManageResourceComponents)."""
        resources = {
            str(c.get("path", "")): c
            for c in self.components
            if c.get("kind") == "resource"
        }
        expected = {
            f"skills/init-meta-project/resources/{name}" for name in CANONICAL_SOURCES
        }
        self.assertTrue(
            expected.issubset(resources),
            f"manifest resource components must cover the 9 init resources; "
            f"missing: {sorted(expected - set(resources))}",
        )
        for path, comp in resources.items():
            if not path.startswith("skills/init-meta-project/resources/"):
                continue
            self.assertEqual(
                comp.get("requires"),
                ["skills/init-meta-project/SKILL.md"],
                f"resource {path} must depend on the init SKILL.md",
            )
            self.assertTrue(
                (ROOT_DIR / path).is_file(),
                f"resource component path absent from repo tree: {path}",
            )


class TestInitSkillLoadingContract(unittest.TestCase):
    """(c) SKILL.md carries the Resource Loading Contract + per-step pointers."""

    @classmethod
    def setUpClass(cls):
        cls.text = INIT_SKILL_PATH.read_text(encoding="utf-8")

    def test_loading_contract_block_present(self):
        self.assertIn("Resource Loading Contract", self.text)

    def test_scenario_read_policy_clauses(self):
        self.assertIn(
            "reads NO resources",
            self.text,
            "contract must state that the healthy repeat-run reads no resources",
        )
        self.assertIn(
            "exactly when its step needs it",
            self.text,
            "contract must state on-demand reads for clean init (Scenario 1)",
        )
        self.assertIn(
            "only its procedure",
            self.text,
            "contract must state Scenario 4 reads only its procedure",
        )

    def test_missing_resource_envelope_and_guidance(self):
        self.assertIn(
            "MISSING_RESOURCE",
            self.text,
            "missing-resource envelope code absent from SKILL.md",
        )
        self.assertIn(MISSING_RESOURCE_GUIDANCE, self.text)

    def test_per_step_resource_pointers(self):
        for name in CANONICAL_SOURCES:
            self.assertIn(
                f"resources/{name}",
                self.text,
                f"SKILL.md must name the resource file per step: resources/{name}",
            )

    def test_no_embedded_template_blocks_remain(self):
        self.assertNotIn(
            "<!-- TEMPLATE:BEGIN",
            self.text,
            "embedded template blocks must be extracted to resources/",
        )


class TestSyncResourcesZeroDrift(unittest.TestCase):
    """(d) The repo tree is at 0 template drift: a full temp CLONE of the
    repository reaches 0 drift after ``sync_templates --write`` then
    ``--check``.

    Wave F T-D6: a test must never run ``sync --write`` against the LIVE
    repo tree — the fixture clones the tree (minus ``.git``/bytecode caches)
    and writes only inside the clone. A drifted live tree is still detected,
    because the clone inherits the drifted bytes byte-for-byte.
    """

    def test_write_then_check_zero_drift(self):
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            clone_root = Path(tmp) / "repo-clone"
            shutil.copytree(
                ROOT_DIR,
                clone_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            write_res = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--write", "--repo-root", str(clone_root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                write_res.returncode,
                0,
                f"sync_templates --write failed on the repo clone: "
                f"{write_res.stdout}\n{write_res.stderr}",
            )
            check_res = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--check", "--repo-root", str(clone_root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                check_res.returncode,
                0,
                f"sync_templates --check detected drift in the repo clone: "
                f"{check_res.stdout}\n{check_res.stderr}",
            )


class TestResourcesByteCanonical(unittest.TestCase):
    """(e) Every resources/ file is byte-equal to its canonical source (and mirror)."""

    def test_resources_match_canonical_bytes(self):
        for name, canon_rel in CANONICAL_SOURCES.items():
            res_path = RESOURCES_DIR / name
            canon_path = ROOT_DIR / canon_rel
            self.assertTrue(
                res_path.is_file(), f"missing resource file: {res_path}"
            )
            self.assertEqual(
                res_path.read_bytes(),
                canon_path.read_bytes(),
                f"resource {name} diverges from canonical {canon_rel} "
                f"(run sync_templates --write)",
            )

    def test_mirror_resources_match_canonical_bytes(self):
        for name, canon_rel in CANONICAL_SOURCES.items():
            mirror_path = MIRROR_RESOURCES_DIR / name
            self.assertTrue(
                mirror_path.is_file(),
                f"missing mirrored resource file: {mirror_path}",
            )
            self.assertEqual(
                mirror_path.read_bytes(),
                (ROOT_DIR / canon_rel).read_bytes(),
                f"mirrored resource {name} diverges from canonical {canon_rel}",
            )


class TestResourceTargetsDeclared(unittest.TestCase):
    """RESOURCE_TARGETS declares the canonical -> resource mapping in sync_templates."""

    def test_resource_targets_cover_all_nine(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not importable")
        targets = getattr(sync_templates, "RESOURCE_TARGETS", None)
        self.assertIsNotNone(targets, "RESOURCE_TARGETS missing from sync_templates")
        self.assertEqual(
            dict(targets), CANONICAL_SOURCES, "RESOURCE_TARGETS mapping mismatch"
        )


if __name__ == "__main__":
    unittest.main()
