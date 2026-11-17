"""
Wave G — Lane S lock-in tests (manage-slim: the proven init-P2 pattern applied
to the heaviest skill).

Plan: docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md (§4 Lane S).

Locks in:
  (a) update-engine plan maps manage resource components
      `skills/manage-meta-project/resources/<file>` to the runtime layout
      `.agents/skills/manage-meta-project/resources/<file>` in a runtime-layout
      consumer fixture (the generic Wave E P2 engine rule already covers
      skills/<n>/resources/** — this proves manage rides it); recorded lock
      targets stay authoritative.
  (b) canonical manifest declares the 3 manage resource components
      (kind "resource", requires the manage SKILL.md); component edges intact.
  (c) manage SKILL.md carries the Resource Loading Contract: phase-based read
      policy (Phase 0.5 + Phase 5 read each resource exactly when its step
      needs it; the other phases read NO resources); a missing mandatory
      resource BLOCKS the dependent step with the MISSING_RESOURCE envelope
      and the pinned-source guidance; per-step resource pointers name all 3
      files; NO embedded TEMPLATE blocks remain; the duplicate `#### 2.`
      Phase 2 headers are fixed; the slim shape is locked.
  (d) sync_templates declares manage's canonical pairs in
      MANAGE_RESOURCE_TARGETS (canonical stays templates/team/) and registers
      both skill resource sets in RESOURCE_SYNC_SETS; the dead embedded
      injection machinery is gone. Zero-drift write/check remains canonically
      covered by tests/test_ewave_p.py TestSyncResourcesZeroDrift (temp-clone
      fixture — a test never runs sync --write against the live tree).
  (e) every manage resources/ file is byte-equal to its canonical
      templates/team/ source (and to its .agents/skills mirror).

Zero-dependency: Python 3.10+ stdlib only.
"""

from pathlib import Path
import json
import re
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
MANAGE_SKILL_PATH = ROOT_DIR / "skills" / "manage-meta-project" / "SKILL.md"
MANAGE_MIRROR_SKILL_PATH = ROOT_DIR / ".agents" / "skills" / "manage-meta-project" / "SKILL.md"
MANAGE_RESOURCES_DIR = ROOT_DIR / "skills" / "manage-meta-project" / "resources"
MANAGE_MIRROR_RESOURCES_DIR = ROOT_DIR / ".agents" / "skills" / "manage-meta-project" / "resources"
MANIFEST_PATH = ROOT_DIR / "templates" / "release_manifest.json"
MANAGE_SKILL_RELPATH = "skills/manage-meta-project/SKILL.md"

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
MANAGE_CANONICAL_SOURCES = {
    "profile.md": "templates/team/profile.md",
    "notes.md": "templates/team/notes.md",
    "system_prompt.md": "templates/team/system_prompt.md",
}

MISSING_RESOURCE_GUIDANCE = (
    "missing mandatory resource 'resources/<name>' — reinstall the skill "
    "from the pinned source (update-meta-project) or restore the file; "
    "do not improvise the template from memory"
)

# Slim-shape lock: wave target was <= ~230 lines; small margin for honest edits.
MANAGE_SKILL_MAX_LINES = 240


class TestEngineManageResourceRuntimeLayout(unittest.TestCase):
    """(a) Engine plan maps manage resources into the .agents/skills runtime layout."""

    def setUp(self):
        if _resolve_target is None:
            self.skipTest("update_meta_project engine module not importable")

    def _runtime_layout_consumer_repo(self, root: Path) -> Path:
        """Consumer fixture with the init-deployed runtime layout (.agents/skills/)."""
        (root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
        return root

    def test_manage_resource_component_maps_to_agents_skills_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._runtime_layout_consumer_repo(Path(tmp))
            for res_name in MANAGE_CANONICAL_SOURCES:
                self.assertEqual(
                    _resolve_target(
                        f"skills/manage-meta-project/resources/{res_name}", repo, None
                    ),
                    f".agents/skills/manage-meta-project/resources/{res_name}",
                    "manage resource component must install at the runtime layout path",
                )

    def test_manage_recorded_target_stays_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._runtime_layout_consumer_repo(Path(tmp))
            self.assertEqual(
                _resolve_target(
                    "skills/manage-meta-project/resources/profile.md",
                    repo,
                    {"target": "skills/manage-meta-project/resources/profile.md"},
                ),
                "skills/manage-meta-project/resources/profile.md",
                "a recorded lock target must win over the fresh layout rule",
            )

    def test_manage_without_agents_skills_distribution_path_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)  # no .agents/skills/ — distribution layout consumer
            self.assertEqual(
                _resolve_target(
                    "skills/manage-meta-project/resources/profile.md", repo, None
                ),
                "skills/manage-meta-project/resources/profile.md",
            )


class TestManifestManageResourceComponents(unittest.TestCase):
    """(b) Manifest gains the 3 manage resource components; edges intact."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.components = cls.manifest.get("components") or []

    def _resource_components(self):
        return {
            str(c.get("path", "")): c for c in self.components if c.get("kind") == "resource"
        }

    def test_three_manage_resource_components_declared(self):
        resources = self._resource_components()
        expected = {
            f"skills/manage-meta-project/resources/{name}" for name in MANAGE_CANONICAL_SOURCES
        }
        self.assertTrue(
            expected.issubset(resources),
            f"manifest must declare the 3 manage resource components; missing: "
            f"{sorted(expected - set(resources))}",
        )
        for path, comp in resources.items():
            if not path.startswith("skills/manage-meta-project/resources/"):
                continue
            self.assertEqual(
                comp.get("requires"),
                [MANAGE_SKILL_RELPATH],
                f"resource {path} must depend on the manage SKILL.md",
            )
            self.assertTrue(
                (ROOT_DIR / path).is_file(),
                f"manage resource component path absent from repo tree: {path}",
            )

    def test_resource_component_count_is_twelve(self):
        """Edge: 9 init resources (Wave E P2) + 3 manage resources (this wave)."""
        resources = self._resource_components()
        self.assertEqual(
            len(resources), 12,
            f"resource components must be exactly the 9 init + 3 manage set; got {sorted(resources)}",
        )

    def test_manage_skill_component_edge_intact(self):
        by_path = {str(c.get("path", "")): c for c in self.components}
        self.assertIn(MANAGE_SKILL_RELPATH, by_path)
        self.assertEqual(
            by_path[MANAGE_SKILL_RELPATH].get("kind"), "skill",
            "manage SKILL.md must remain a skill component",
        )
        self.assertEqual(
            by_path[MANAGE_SKILL_RELPATH].get("requires"), ["scripts/manage_reports.py"],
            "manage SKILL.md must keep its script dependency edge",
        )

    def test_resources_are_leaf_components(self):
        """Edge: no component may require a manage resource (resources are leaves)."""
        manage_res_prefix = "skills/manage-meta-project/resources/"
        for c in self.components:
            for req in c.get("requires") or []:
                self.assertFalse(
                    str(req).startswith(manage_res_prefix),
                    f"component {c.get('path')} must not depend on a manage resource: {req}",
                )


class TestManageSkillLoadingContract(unittest.TestCase):
    """(c) manage SKILL.md carries the Resource Loading Contract; slim shape;
    no embedded TEMPLATE blocks."""

    @classmethod
    def setUpClass(cls):
        cls.text = MANAGE_SKILL_PATH.read_text(encoding="utf-8")

    def test_loading_contract_block_present(self):
        self.assertIn("Resource Loading Contract", self.text)

    def test_phase_read_policy_clauses(self):
        self.assertIn(
            "reads NO resources",
            self.text,
            "contract must state that the non-materializing phases read no resources",
        )
        self.assertIn(
            "exactly when its step needs it",
            self.text,
            "contract must state on-demand reads for the materializing phases",
        )

    def test_missing_resource_envelope_and_guidance(self):
        self.assertIn(
            "MISSING_RESOURCE",
            self.text,
            "missing-resource envelope code absent from SKILL.md",
        )
        self.assertIn(MISSING_RESOURCE_GUIDANCE, self.text)

    def test_per_step_resource_pointers(self):
        for name in MANAGE_CANONICAL_SOURCES:
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
        self.assertNotIn(
            "Embedded Reference Templates",
            self.text,
            "the embedded-templates section must be gone from the slim skill",
        )

    def test_duplicate_phase2_headers_fixed(self):
        """The old skill had two `#### 2.` headings in Phase 2; the slim skill
        numbers its Phase 2 subsections 1..4 exactly once each."""
        numbered = re.findall(r"^#### (\d+)\.", self.text, flags=re.MULTILINE)
        self.assertEqual(
            numbered, ["1", "2", "3", "4"],
            f"Phase 2 subsection numbering must be 1..4 without duplicates: {numbered}",
        )

    def test_slim_shape_locked(self):
        lines = self.text.splitlines()
        self.assertLessEqual(
            len(lines), MANAGE_SKILL_MAX_LINES,
            f"manage SKILL.md must stay within the wave-G slim bound "
            f"({MANAGE_SKILL_MAX_LINES} lines); got {len(lines)}",
        )

    def test_behavioral_contracts_retained(self):
        """Slimming must not lose the phase-mandated contracts."""
        for marker in (
            "Fail-Closed Block",
            "Machine-Enforced Intake",
            "evaluate_manage_intake",
            "Staleness Protocol",
            "Topology Precedence Invariants",
            "Action Differentiation (The 5 Operations)",
            "Polyglot Stack Isolation Rule",
            "Mandatory Dispatcher Rule",
            "Open Competency Catalog",
            "task CERTAINTY beats task size",
            "acceptance criterion",
            "model tier",
            "verifier",
            "Prohibition on autonomous deletion",
            "Profile Created ≠ Loaded by Harness",
            "Execution Role Invariance",
            "Handoff Chain Limit",
            "dispatching-parallel-agents",
            "Circuit Breaker & Flow Tracing",
            "Toolchain Handoff Tripwire",
            "- [>]",
            "changes[]",
            "add_role",
        ):
            self.assertIn(marker, self.text, f"behavioral contract lost while slimming: {marker}")

    def test_handoff_packet_format_retained(self):
        self.assertIn("### Task Handoff Package: [agent-A -> agent-B]", self.text)
        for field in (
            "- Original goal:",
            "- Completed work:",
            "- Handoff boundary:",
            "- Recommended prompt for agent-B:",
        ):
            self.assertIn(field, self.text, f"handoff packet field lost: {field}")

    def test_skill_format_sections_present(self):
        self.assertRegex(self.text, r"^---\s*\n", "frontmatter missing")
        self.assertIn("name: manage-meta-project", self.text)
        self.assertIn("description:", self.text)
        self.assertIn("## When to invoke skill", self.text)
        self.assertIn("## Execution steps", self.text)


class TestManageResourcesByteCanonical(unittest.TestCase):
    """(e) Every manage resources/ file is byte-equal to its canonical source (and mirror)."""

    def setUp(self):
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )


    def test_resources_match_canonical_bytes(self):
        for name, canon_rel in MANAGE_CANONICAL_SOURCES.items():
            res_path = MANAGE_RESOURCES_DIR / name
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
        for name, canon_rel in MANAGE_CANONICAL_SOURCES.items():
            mirror_path = MANAGE_MIRROR_RESOURCES_DIR / name
            self.assertTrue(
                mirror_path.is_file(),
                f"missing mirrored resource file: {mirror_path}",
            )
            self.assertEqual(
                mirror_path.read_bytes(),
                (ROOT_DIR / canon_rel).read_bytes(),
                f"mirrored resource {name} diverges from canonical {canon_rel}",
            )

    def test_mirror_skill_matches_canonical_bytes(self):
        self.assertEqual(
            MANAGE_MIRROR_SKILL_PATH.read_bytes(),
            MANAGE_SKILL_PATH.read_bytes(),
            "manage SKILL.md mirror diverges from the canonical skill",
        )


class TestManageResourceTargetsDeclared(unittest.TestCase):
    """(d) sync_templates declares manage's canonical pairs; embedded machinery gone."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not importable")

    def test_manage_resource_targets_mapping(self):
        self.assertEqual(
            dict(sync_templates.MANAGE_RESOURCE_TARGETS), MANAGE_CANONICAL_SOURCES,
            "MANAGE_RESOURCE_TARGETS mapping mismatch",
        )

    def test_init_resource_targets_unchanged(self):
        """Cross-lock with tests/test_ewave_p.py: the init mapping stays the 9 entries."""
        self.assertEqual(
            dict(sync_templates.RESOURCE_TARGETS),
            {
                "observations.md": "templates/project_knowledge/observations.md",
                "boundaries.md": "templates/project_knowledge/boundaries.md",
                "weak_spots.md": "templates/project_knowledge/weak_spots.md",
                "architecture.md": "templates/project_knowledge/architecture.md",
                "tasks.md": "templates/project_knowledge/tasks.md",
                "AGENTS.md": "templates/AGENTS.md",
                "record-observation-SKILL.md": "skills/record-observation/SKILL.md",
                "sync-architecture-SKILL.md": "skills/sync-architecture/SKILL.md",
                "ground-meta-project-SKILL.md": "skills/ground-meta-project/SKILL.md",
            },
        )

    def test_resource_sync_sets_register_both_skills(self):
        self.assertEqual(
            dict(sync_templates.RESOURCE_SYNC_SETS),
            {
                sync_templates.INIT_RESOURCES_DIR: sync_templates.RESOURCE_TARGETS,
                sync_templates.MANAGE_RESOURCES_DIR: sync_templates.MANAGE_RESOURCE_TARGETS,
            },
        )

    def test_embedded_machinery_removed(self):
        for symbol in ("EMBEDDED_TARGETS", "replace_embedded_template", "sync_embedded_templates"):
            self.assertFalse(
                hasattr(sync_templates, symbol),
                f"removed embedded-sync symbol reappeared: {symbol}",
            )


if __name__ == "__main__":
    unittest.main()
