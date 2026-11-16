"""
Wave E — Lane T lock-in tests (compact formats).

Plan: docs/superpowers/plans/2026-11-16-wave-e-context-economy.md (§3 Lane T).

Locks in (RED-first):
  (a) architecture.md template v2: map-first card — Component Map table with the
      "Depends on" column and the same-change update rule; NO "Design Patterns".
  (b) tasks.md template: Team Task Management Rules gain rule 5 — Checkpoint
      (pause/handoff) with "- [>]" status and a compact example block.
  (c) init-meta-project carries canonical architecture.md and tasks.md matching
      the template files byte-wise (sync canon).
      SUPERSEDED per plan §6a owner decision ADJUST AND PROCEED (2026-11-16):
      Lane P2 extracted the embedded TEMPLATE blocks into
      skills/init-meta-project/resources/ — the same invariant now holds for
      the resource files (byte-match canonical templates), not embedded blocks.
      Wave F T-D6: the superseded duplicate byte test was removed; the
      canonical lock-in is tests/test_ewave_p.py TestResourcesByteCanonical.
  (d) scripts/sync_templates.py declares the canonical pairs in RESOURCE_TARGETS
      (formerly EMBEDDED_TARGETS — same supersession).
      Wave F T-D6: the 0-drift write/check lock-in moved canonically to
      tests/test_ewave_p.py TestSyncResourcesZeroDrift (temp-clone fixture;
      a test never runs sync --write against the live repo tree).
"""

from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT_DIR / "templates"
INIT_SKILL_PATH = ROOT_DIR / "skills" / "init-meta-project" / "SKILL.md"

SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import sync_templates
except ImportError:
    sync_templates = None


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestArchitectureTemplateV2(unittest.TestCase):
    """(a) Map-first architecture card: Depends on column + same-change rule, no Design Patterns."""

    def setUp(self):
        self.content = read(TEMPLATES_DIR / "project_knowledge" / "architecture.md")

    def test_component_map_has_depends_on_column(self):
        self.assertIn("Component Map", self.content)
        self.assertIn("| Component | Location | Role | Depends on |", self.content)

    def test_same_change_update_rule_present(self):
        self.assertIn(
            "The map is updated IN THE SAME CHANGE that touches a component",
            self.content,
            "Same-change map update rule missing from architecture template header",
        )
        self.assertIn("a decision without a map update is an incomplete change", self.content)
        self.assertIn("One row per component, no prose", self.content)

    def test_design_patterns_removed(self):
        self.assertNotIn(
            "Design Patterns",
            self.content,
            "Design Patterns section must be removed from architecture template v2",
        )

    def test_stack_and_invariants_one_line_slots(self):
        self.assertIn("Stack and Invariants", self.content)
        for slot in ("Stack:", "State + Single Source of Truth:", "Cross-border contracts:"):
            self.assertIn(slot, self.content, f"Missing one-line slot: {slot}")

    def test_conditional_e2e_flows_section(self):
        self.assertIn("End-to-End Data Flows", self.content)
        self.assertIn("multi-tier", self.content.lower())


class TestTasksTemplateCheckpointRule(unittest.TestCase):
    """(b) Team Task Management Rules rule 5: Checkpoint (pause/handoff) with - [>] example."""

    def setUp(self):
        self.content = read(TEMPLATES_DIR / "project_knowledge" / "tasks.md")

    def test_rule5_checkpoint_present(self):
        self.assertIn("Checkpoint (pause/handoff)", self.content)

    def test_checkpoint_status_marker_example(self):
        self.assertIn(
            "- [>]",
            self.content,
            "Template must contain a - [>] checkpoint example",
        )

    def test_checkpoint_compact_fields(self):
        for field in ("goal:", "decided:", "done:", "open:", "next:"):
            self.assertIn(field, self.content, f"Missing checkpoint field: {field}")

    def test_ground_resumes_from_checkpoint(self):
        self.assertIn("ground", self.content.lower())


# (c, superseded per plan §6a owner decision ADJUST AND PROCEED, 2026-11-16):
# Lane P2 extracted the embedded TEMPLATE blocks into
# skills/init-meta-project/resources/. The byte-match-canonical invariant now
# lives canonically in tests/test_ewave_p.py
# (TestResourcesByteCanonical — all 9 resources, superset of the
# architecture.md/tasks.md subset previously asserted here). The superseded
# class TestInitSkillResourcesCanonical was removed as a byte-duplicate in
# Wave F (T-D6 #1/#4): one canonical byte test, no drift-test forks.


class TestSyncTargetsAndZeroDrift(unittest.TestCase):
    """(d, superseded per plan §6a) RESOURCE_TARGETS declares the canonical
    pairs for init (formerly EMBEDDED_TARGETS).

    Wave F T-D6: the byte-identical write-then-check drift test that lived
    here was deduplicated — the canonical implementation is
    tests/test_ewave_p.py (TestSyncResourcesZeroDrift.
    test_write_then_check_zero_drift) as a temp-clone fixture, since a test
    must never run ``sync --write`` against the LIVE repo tree."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not implemented yet")

    def test_resource_targets_declare_canonical_pairs(self):
        targets = getattr(sync_templates, "RESOURCE_TARGETS", {})
        self.assertEqual(
            targets.get("architecture.md"),
            "templates/project_knowledge/architecture.md",
        )
        self.assertEqual(
            targets.get("tasks.md"),
            "templates/project_knowledge/tasks.md",
        )


if __name__ == "__main__":
    unittest.main()
