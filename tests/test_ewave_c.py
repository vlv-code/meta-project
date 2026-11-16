#!/usr/bin/env python3
"""Wave E Lane C — Canon Texts (plan docs/superpowers/plans/2026-11-16-wave-e-context-economy.md §4).

RED-first specification (TDD): on the pre-wave canon none of the asserted
markers exist, so every canon assertion below fails until its text lands.

- C.1 Execution Routes (AGENTS.md §6 and templates/AGENTS.md §6, ×2 copies):
  a compact subsection naming all three routes — short (unambiguous local
  task: action → needed check → result; Read-Only Exploration Mode is the
  canonical short route) / normal (several related changes with known
  contracts) / extended (migrations, ambiguous defects, architecture,
  protected components); mode chosen by consequences and uncertainty;
  scenario-mandated checks always preserved.

- C.2 Routing matrix (manage-meta-project Phase 2 "Execution Routing"):
  routes script / cheap subagent / regular executor / strong model +
  independent verification; principle "task CERTAINTY beats task size";
  delegation plan fields. AGENTS.md §4 connected-skills note carries a
  pointer to that routing block.

- C.3 Checkpoint cross-refs: manage skill handoff section references the
  `- [>]` checkpoint convention (generic wording, per tasks.md rules);
  ground skill selective recovery lists the last `- [>]` checkpoint among
  its re-read sources.

- C.4 Tune cost accounting: tune skill Phase 2 mandatory cost-evidence
  honesty rules (available metrics only; no invented currency conversion;
  before/after only on comparable tasks; smaller file ≠ proven launch
  economy) and Phase 6 effect records documenting the 5-field cost block;
  templates/reports/tune_report.json example effect record carries the
  filled cost object.

- C.5 Skill mirrors (.agents/skills/) stay byte-identical to canonical
  skills/ for the three touched skills (lock-in).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

AGENTS_MD = REPO_ROOT / "AGENTS.md"
AGENTS_TEMPLATE = REPO_ROOT / "templates" / "AGENTS.md"
MANAGE_SKILL = REPO_ROOT / "skills" / "manage-meta-project" / "SKILL.md"
GROUND_SKILL = REPO_ROOT / "skills" / "ground-meta-project" / "SKILL.md"
TUNE_SKILL = REPO_ROOT / "skills" / "tune-meta-project" / "SKILL.md"
TUNE_REPORT = REPO_ROOT / "templates" / "reports" / "tune_report.json"

COST_FIELDS = {"rereads", "tool_calls", "handoffs", "rework", "wall_time_s"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def squash(text: str) -> str:
    """Collapse whitespace runs so phrase assertions tolerate line wrapping."""
    return " ".join(text.split())


class TestExecutionRoutes(unittest.TestCase):
    """C.1: both passport copies gain the compact 'Execution Routes' block."""

    def test_root_agents_md_execution_routes(self):
        text = read_text(AGENTS_MD)
        self.assertIn("Execution Routes", text)
        self.assertIn("**short**", text)
        self.assertIn("**normal**", text)
        self.assertIn("**extended**", text)
        self.assertIn("consequences and uncertainty", text)
        self.assertIn("Read-Only Exploration Mode", text)
        self.assertIn("always preserved", text)

    def test_root_agents_md_route_semantics(self):
        text = read_text(AGENTS_MD)
        self.assertIn("unambiguous local task", text)
        self.assertIn("known contracts", text)
        self.assertIn("migrations, ambiguous defects", text)

    def test_template_agents_md_execution_routes(self):
        text = read_text(AGENTS_TEMPLATE)
        self.assertIn("Execution Routes", text)
        self.assertIn("**short**", text)
        self.assertIn("**normal**", text)
        self.assertIn("**extended**", text)
        self.assertIn("consequences and uncertainty", text)
        self.assertIn("always preserved", text)


class TestRoutingMatrix(unittest.TestCase):
    """C.2: manage skill Phase 2 routing table + AGENTS.md §4 pointer."""

    def test_manage_skill_routing_table(self):
        text = read_text(MANAGE_SKILL)
        self.assertIn("Execution Routing", text)
        self.assertIn("cheap subagent", text)
        self.assertIn("CERTAINTY", text)
        self.assertIn("regular executor", text)
        self.assertIn("strong model", text)
        self.assertIn("independent verification", text)
        self.assertIn("Red-Zone policy", text)

    def test_manage_skill_routing_principle_and_plan_fields(self):
        text = read_text(MANAGE_SKILL)
        self.assertIn("task CERTAINTY beats task size", text)
        self.assertIn("acceptance criterion", text)
        self.assertIn("model tier", text)
        self.assertIn("verifier", text)

    def test_agents_md_routing_pointer(self):
        text = read_text(AGENTS_MD)
        self.assertIn("manage-meta-project", text)
        self.assertIn("Execution Routing", text)


class TestCheckpointCrossRefs(unittest.TestCase):
    """C.3: `- [>]` checkpoint convention referenced generically."""

    def test_manage_skill_handoff_references_checkpoint(self):
        text = read_text(MANAGE_SKILL)
        self.assertIn("- [>]", text)
        self.assertIn("checkpoint", text)

    def test_ground_skill_recovery_reads_checkpoint(self):
        text = read_text(GROUND_SKILL)
        self.assertIn("- [>]", text)
        self.assertIn("checkpoint", text)


class TestTuneCostAccounting(unittest.TestCase):
    """C.4: cost-evidence honesty rules + documented cost block + example."""

    def test_tune_skill_phase2_cost_evidence_rules(self):
        text = squash(read_text(TUNE_SKILL))
        self.assertIn("cost evidence", text)
        self.assertIn("no invented currency", text)
        self.assertIn("comparable tasks", text)
        self.assertIn("smaller file", text)

    def test_tune_skill_phase6_cost_block_documented(self):
        text = read_text(TUNE_SKILL)
        for field in sorted(COST_FIELDS):
            self.assertIn(field, text)

    def test_tune_report_example_effect_record_has_cost(self):
        data = json.loads(read_text(TUNE_REPORT))
        records = data.get("effect_records")
        self.assertIsInstance(records, list)
        self.assertTrue(records, "tune_report.json example must contain effect records")
        cost = records[0].get("cost")
        self.assertIsInstance(cost, dict, "first effect record must carry a cost object")
        self.assertEqual(set(cost.keys()), COST_FIELDS)
        for field, value in cost.items():
            self.assertIsInstance(value, int, f"cost.{field} must be an integer")
            self.assertGreaterEqual(value, 0, f"cost.{field} must be non-negative")


class TestSkillMirrorsByteIdentical(unittest.TestCase):
    """C.5 lock-in: mirrors of the three touched skills stay byte-identical."""

    def test_manage_mirror_in_sync(self):
        canonical = read_text(MANAGE_SKILL)
        mirror = read_text(REPO_ROOT / ".agents" / "skills" / "manage-meta-project" / "SKILL.md")
        self.assertEqual(canonical, mirror)

    def test_ground_mirror_in_sync(self):
        canonical = read_text(GROUND_SKILL)
        mirror = read_text(REPO_ROOT / ".agents" / "skills" / "ground-meta-project" / "SKILL.md")
        self.assertEqual(canonical, mirror)

    def test_tune_mirror_in_sync(self):
        canonical = read_text(TUNE_SKILL)
        mirror = read_text(REPO_ROOT / ".agents" / "skills" / "tune-meta-project" / "SKILL.md")
        self.assertEqual(canonical, mirror)


if __name__ == "__main__":
    unittest.main()
