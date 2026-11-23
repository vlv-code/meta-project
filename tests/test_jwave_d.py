"""Wave jwave_d (external audit #4 follow-up, 2026-11-23): documentation locks.

P0-2: ``.agents/project_knowledge/weak_spots.md`` section 3 must contain an
OPEN entry recording the structural (non-behavioral) debt of
``scripts/inspect_meta_project.py`` (``inspect_repository()`` monolith,
section numbering gap, side-effecting classification ladder, raw state and
capability literals without a shared enum).

P1-2: ``docs/decisions_and_roadmap.md`` must contain the Icebox disposition
record for the audit-#4 layered-passport proposal, including the parked
ninth canonical state ``DUAL_PASSPORT_CONFLICT`` and the note that actor
attribution is already implemented via the inline ``[actor=...]`` tag in
``scripts/record_obs.py``.

Zero-dependency: Python 3.10+ standard library only.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEAK_SPOTS = REPO_ROOT / ".agents" / "project_knowledge" / "weak_spots.md"
ROADMAP = REPO_ROOT / "docs" / "decisions_and_roadmap.md"


class TestWeakSpotsStructuralDebtEntry(unittest.TestCase):
    """P0-2: inspect_meta_project.py structural debt registered as OPEN."""

    @classmethod
    def setUpClass(cls):
        # Distribution-branch guard (same contract as tests/test_gwave_s.py):
        # the knowledge slices are self-installation artifacts that exist on
        # the development branch only; the distribution branch (framework
        # content, no .agents/) skips this live-installation contract instead
        # of erroring in the sync battery.
        if not (REPO_ROOT / ".agents" / "meta-project.json").is_file():
            raise unittest.SkipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )
        cls.lines = WEAK_SPOTS.read_text(encoding="utf-8").splitlines()

    def _deferred_debt_section_bounds(self):
        start = self.lines.index("## 3. Deferred Technical Debt")
        end = self.lines.index("## 4. Resolved Vulnerabilities & Closed Risks")
        return start, end

    def test_open_entry_exists_in_deferred_debt_section(self):
        start, end = self._deferred_debt_section_bounds()
        section = self.lines[start + 1 : end]
        entry_lines = [
            line
            for line in section
            if line.lstrip().startswith("- `[OPEN 2026-11-23")
        ]
        self.assertTrue(
            entry_lines,
            "no bullet with status tag `[OPEN 2026-11-23...` in section 3",
        )

    def test_entry_names_script_and_function(self):
        start, end = self._deferred_debt_section_bounds()
        section = "\n".join(self.lines[start + 1 : end])
        self.assertIn("scripts/inspect_meta_project.py", section)
        self.assertIn("inspect_repository()", section)

    def test_entry_does_not_claim_silent_wrong_report(self):
        text = "\n".join(self.lines)
        self.assertNotIn("silently produces a wrong report", text)

    def test_preexisting_heading_unchanged(self):
        self.assertIn("## 3. Deferred Technical Debt", self.lines)

    def test_preexisting_resolved_entry_unchanged(self):
        self.assertTrue(
            any("[RESOLVED 2026-11-15, Step 65]" in line for line in self.lines),
            "pre-existing RESOLVED entry (manage_reports Step 65) disappeared",
        )


class TestRoadmapAudit4Disposition(unittest.TestCase):
    """P1-2: layered-passport proposal recorded as an Icebox disposition."""

    @classmethod
    def setUpClass(cls):
        cls.lines = ROADMAP.read_text(encoding="utf-8").splitlines()

    def test_dual_passport_conflict_iceboxed_on_one_line(self):
        # "Icebox" alone already occurs in the doc (sections 6 and 7), so the
        # disposition must tie the parked state and the Icebox verdict together.
        self.assertTrue(
            any(
                "DUAL_PASSPORT_CONFLICT" in line and "Icebox" in line
                for line in self.lines
            ),
            "no line marking DUAL_PASSPORT_CONFLICT as an Icebox disposition",
        )

    def test_overlay_layer_named(self):
        text = "\n".join(self.lines)
        self.assertIn("AGENTS.local.md", text)

    def test_actor_attribution_already_implemented_note(self):
        text = "\n".join(self.lines)
        self.assertIn("[actor=", text)
        self.assertIn("record_obs.py", text)

    def test_preexisting_p22_line_unchanged(self):
        expected = (
            "  - [ ] P2.2: MVP адаптер `PreToolUse` для быстрой валидации "
            "путей записи по Green/Yellow/Red до исполнения tool call."
        )
        self.assertIn(expected, self.lines)


if __name__ == "__main__":
    unittest.main()
