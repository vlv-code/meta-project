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
  (d) scripts/sync_templates.py declares the canonical pairs in RESOURCE_TARGETS
      (formerly EMBEDDED_TARGETS — same supersession) and the real repo reaches
      0 drift after --write then --check.
"""

from pathlib import Path
import subprocess
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT_DIR / "templates"
INIT_SKILL_PATH = ROOT_DIR / "skills" / "init-meta-project" / "SKILL.md"
INIT_RESOURCES_DIR = ROOT_DIR / "skills" / "init-meta-project" / "resources"
SYNC_SCRIPT = ROOT_DIR / "scripts" / "sync_templates.py"

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


class TestInitSkillResourcesCanonical(unittest.TestCase):
    """(c, superseded per plan §6a) init skill resources match canonical
    templates byte-identically (sync convention moved from embedded
    TEMPLATE blocks to skills/init-meta-project/resources/)."""

    def setUp(self):
        if sync_templates is None:
            self.skipTest("sync_templates module not implemented yet")

    def _assert_resource_matches_template(self, res_name: str, tmpl_rel: str):
        res_path = INIT_RESOURCES_DIR / res_name
        self.assertTrue(
            res_path.is_file(),
            f"missing init resource file: {res_path} (run sync_templates --write)",
        )
        self.assertEqual(
            res_path.read_bytes(),
            (ROOT_DIR / tmpl_rel).read_bytes(),
            f"Init resource {res_name} diverges from {tmpl_rel} "
            f"(run sync_templates --write)",
        )

    def test_resource_architecture_matches_template(self):
        self._assert_resource_matches_template(
            "architecture.md", "templates/project_knowledge/architecture.md"
        )

    def test_resource_tasks_matches_template(self):
        self._assert_resource_matches_template(
            "tasks.md", "templates/project_knowledge/tasks.md"
        )


class TestSyncTargetsAndZeroDrift(unittest.TestCase):
    """(d, superseded per plan §6a) RESOURCE_TARGETS declares the canonical
    pairs for init (formerly EMBEDDED_TARGETS); repo is at 0 drift after
    --write then --check."""

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

    def test_write_then_check_zero_drift(self):
        write_res = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--write", "--repo-root", str(ROOT_DIR)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            write_res.returncode,
            0,
            f"sync_templates --write failed: {write_res.stdout}\n{write_res.stderr}",
        )
        check_res = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--check", "--repo-root", str(ROOT_DIR)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            check_res.returncode,
            0,
            f"sync_templates --check detected drift: {check_res.stdout}\n{check_res.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
