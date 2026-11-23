"""Wave J, dispatcher lane (external audit #4 follow-up, 2026-11-23):
versioning policy, branch-discipline ADR, read-discipline dispositions.

P0-3: CONTRIBUTING.md, CONTRIBUTING.ru.md and the CHANGELOG.md header state
the versioning policy (alpha = pre-contract, beta = compatibility goal,
>=1.0.0 = SemVer); the two contributing guides keep line parity.

P0-4: docs/decisions_and_roadmap.md records the branch discipline as ADR #23
(two independent histories, one-way content mirror dev -> main), and the
canonical ADR range #14-#23 is stated consistently in the roadmap and both
READMEs.

P1-1: the read-discipline proposals of audit #4 (§4) are disposed without new
code: variant A rides the existing P2.2 adapter (note under P2.2), variant B
is rejected with its reason, variant C points at P2.3.

Zero-dependency: Python 3.10+ standard library only.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRIB_EN = REPO_ROOT / "CONTRIBUTING.md"
CONTRIB_RU = REPO_ROOT / "CONTRIBUTING.ru.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
ROADMAP = REPO_ROOT / "docs" / "decisions_and_roadmap.md"
README_EN = REPO_ROOT / "README.md"
README_RU = REPO_ROOT / "README.ru.md"
MANAGE_SKILL = REPO_ROOT / "skills" / "manage-meta-project" / "SKILL.md"

# En dash (U+2013) as in the documents.
ADR_CANONICAL_RANGE = "ADR #14–#23"
ADR_PREVIOUS_RANGE = "ADR #14–#22"

POLICY_VERSION_TOKENS = ("`1.0.0-alpha.*`", "`1.0.0-beta.*`", "`>=1.0.0`")


def _lines(path: Path) -> list:
    return path.read_text(encoding="utf-8").splitlines()


class TestVersioningPolicy(unittest.TestCase):
    """P0-3: the policy is stated on a single line in each of the three files."""

    def _assert_policy_line(self, path: Path, label: str) -> None:
        policy_lines = [
            line for line in _lines(path) if label in line and "SemVer" in line
        ]
        self.assertEqual(len(policy_lines), 1, f"{path.name}: expected one policy line")
        for token in POLICY_VERSION_TOKENS:
            self.assertIn(token, policy_lines[0], f"{path.name}: missing {token}")

    def test_contributing_en_states_policy(self):
        self._assert_policy_line(CONTRIB_EN, "Versioning policy")

    def test_contributing_ru_states_policy(self):
        self._assert_policy_line(CONTRIB_RU, "Политика версионирования")

    def test_changelog_header_states_policy(self):
        lines = _lines(CHANGELOG)
        first_release_heading = next(
            index for index, line in enumerate(lines) if line.startswith("## [")
        )
        header = "\n".join(lines[:first_release_heading])
        self.assertIn("Политика версионирования", header)
        for token in POLICY_VERSION_TOKENS:
            self.assertIn(token, header, f"CHANGELOG header: missing {token}")

    def test_policy_does_not_disturb_release_heading_parser(self):
        """The release lock reads the first ``## [version] - date`` heading;
        the policy line must not look like a release heading."""
        lines = _lines(CHANGELOG)
        release_headings = [line for line in lines if line.startswith("## [")]
        self.assertEqual(release_headings[0].strip(), "## [Unreleased]")
        self.assertFalse(any("alpha.*" in line for line in release_headings))

    def test_contributing_guides_keep_line_parity(self):
        self.assertEqual(
            len(_lines(CONTRIB_EN)), len(_lines(CONTRIB_RU)),
            "CONTRIBUTING.md and CONTRIBUTING.ru.md drifted apart in length",
        )


class TestBranchDisciplineAdr(unittest.TestCase):
    """P0-4: ADR #23 exists and the canonical range is stated consistently."""

    @classmethod
    def setUpClass(cls):
        cls.lines = _lines(ROADMAP)

    def _adr_entry_bounds(self, number: str) -> tuple:
        start = next(
            index
            for index, line in enumerate(self.lines)
            if line.startswith(f"{number}. **")
        )
        end = next(
            index
            for index in range(start + 1, len(self.lines))
            if re.match(r"\d+\. \*\*", self.lines[index])
            or self.lines[index].startswith("### ")
            or self.lines[index].startswith("## ")
        )
        return start, end

    def test_roadmap_adr_heading_states_canonical_range(self):
        self.assertIn(
            f"### 1. Зафиксированные архитектурные решения ({ADR_CANONICAL_RANGE})",
            self.lines,
        )
        self.assertFalse(
            any(
                line.startswith("### 1. Зафиксированные архитектурные решения")
                and ADR_PREVIOUS_RANGE in line
                for line in self.lines
            ),
            "stale ADR range in the section heading",
        )

    def test_roadmap_note_states_canonical_range(self):
        self.assertTrue(
            any("(ADR #14–#23," in line for line in self.lines[:12]),
            "the header NOTE still points at the previous ADR range",
        )

    def test_adr_23_follows_adr_22(self):
        _, end_22 = self._adr_entry_bounds("22")
        start_23, _ = self._adr_entry_bounds("23")
        self.assertEqual(start_23, end_22, "ADR #23 must directly follow ADR #22")

    def test_adr_23_records_facts_rules_and_rejected_alternatives(self):
        start, end = self._adr_entry_bounds("23")
        body = "\n".join(self.lines[start:end])
        for token in (
            "sync_dist_branch.py",  # the mirror mechanism under decision
            "sync-dist.yml",
            "`cef3802`",  # the cherry-pick data loss that motivates the rules
            "26",  # main-only commits
            "41",  # dev-only commits
            "*Решение:*",
            "*Отклонённые альтернативы:*",
            "(б)",
            "(в)",
            "`source.commit_sha`",  # why rewriting main is not an option
            "*Следствия:*",
        ):
            self.assertIn(token, body, f"ADR #23: missing {token!r}")

    def test_adr_23_decision_is_the_derived_branch_model(self):
        start, end = self._adr_entry_bounds("23")
        body = "\n".join(self.lines[start:end])
        self.assertIn("`dev` — единственный источник истины", body)
        self.assertIn("`main` — производная ветка", body)

    def test_adr_23_records_owner_definition_and_closed_scope_items(self):
        """The owner defined the model in words (2026-11-23): main is the
        repository without the meta-project scaffolding, everything else is
        mirrored. The ADR must carry that definition; the owner decision of
        2026-11-23 closed both scope questions explicitly (scaffolding =
        .agents/ plus working documents; release tags on the mirrored main
        commit, published tags are not moved) instead of leaving them open."""
        start, end = self._adr_entry_bounds("23")
        body = "\n".join(self.lines[start:end])
        self.assertIn("*Определение владельца (2026-11-23):*", body)
        self.assertIn("полное зеркалирование за исключением обвязки", body)
        self.assertNotIn(
            "[OPEN 2026-11-23]",
            body,
            "scope questions must be closed by the owner decision, not left open",
        )
        closed = [
            line for line in self.lines[start:end] if "[ЗАКРЫТО 2026-11-23" in line
        ]
        self.assertTrue(
            any("docs/superpowers/plans" in line for line in closed),
            "the scaffolding-scope closure is not recorded",
        )
        self.assertTrue(
            any(
                "v1.0.0-alpha.7" in line
                for line in closed
            ),
            "the release-tag placement closure is not recorded",
        )

    def test_readmes_state_canonical_range_only(self):
        for path in (README_EN, README_RU):
            text = path.read_text(encoding="utf-8")
            self.assertIn(ADR_CANONICAL_RANGE, text, f"{path.name}: stale ADR range")
            self.assertNotIn(ADR_PREVIOUS_RANGE, text, f"{path.name}: previous range left")


class TestRuTableOfContents(unittest.TestCase):
    """Found by the glossary lane: the RU table of contents still linked
    "7 canonical states" to the heading "8 canonical states" (broken anchor)."""

    def test_ru_toc_inspection_entry_matches_its_heading(self):
        lines = _lines(README_RU)
        entry = next(
            line for line in lines if line.startswith("- [Обследование репозитория")
        )
        heading = next(
            line for line in lines if line.startswith("## Обследование репозитория")
        )
        label = entry[entry.index("[") + 1 : entry.index("]")]
        self.assertEqual(
            label, heading[len("## ") :],
            "RU table-of-contents label differs from the heading it links to",
        )


class TestReadDisciplineDispositions(unittest.TestCase):
    """P1-1: audit #4 §4 variants A/B/C disposed without new code."""

    @classmethod
    def setUpClass(cls):
        cls.lines = _lines(ROADMAP)

    P22_LINE = (
        "  - [ ] P2.2: MVP адаптер `PreToolUse` для быстрой валидации "
        "путей записи по Green/Yellow/Red до исполнения tool call."
    )

    def test_p22_line_untouched_and_followed_by_read_journal_note(self):
        index = self.lines.index(self.P22_LINE)
        note = "\n".join(self.lines[index + 1 : index + 4])
        self.assertIn("журнал чтений", note, "no read-journal note under P2.2")
        self.assertIn("`PreToolUse`", note)

    def test_audit4_disposition_covers_variants_a_b_c(self):
        start = next(
            index
            for index, line in enumerate(self.lines)
            if line.startswith("## 9.")
        )
        section = "\n".join(self.lines[start:])
        self.assertIn("аудит #4, §4", section)
        self.assertIn("*Вариант A", section)
        self.assertIn("*Вариант B", section)
        self.assertIn("*Вариант C", section)

    def test_variant_b_rejected_with_reason(self):
        start = next(
            index for index, line in enumerate(self.lines) if line.startswith("## 9.")
        )
        section = "\n".join(self.lines[start:])
        variant_b = next(
            line for line in section.splitlines() if "- *Вариант B" in line
        )
        self.assertIn("отклонён", variant_b)
        self.assertIn("чтение не оставляет следа", variant_b)

    def test_variant_c_points_at_p23_without_new_work(self):
        start = next(
            index for index, line in enumerate(self.lines) if line.startswith("## 9.")
        )
        section = "\n".join(self.lines[start:])
        variant_c = next(
            line for line in section.splitlines() if "- *Вариант C" in line
        )
        self.assertIn("P2.3", variant_c)
        self.assertIn("уточняется у автора аудита", variant_c)


class TestManageSkillRecordsBindingInRegistry(unittest.TestCase):
    """The dispatcher binding is a declared registry fact, not only prose:
    manage must record it under installations.<id>.orchestration and declare
    the registry change (the intake gate refuses an undeclared one)."""

    @classmethod
    def setUpClass(cls):
        cls.text = MANAGE_SKILL.read_text(encoding="utf-8")

    def test_binding_block_points_at_the_registry(self):
        self.assertIn("`installations.<id>.orchestration`", self.text)
        self.assertIn("`native_orchestrator`", self.text)
        self.assertIn("`dispatcher_binding`", self.text)

    def test_phase5_records_and_declares_the_orchestration_change(self):
        start = self.text.index("### Phase 5:")
        phase5 = self.text[start : self.text.index("### Phase 6:")]
        self.assertIn("installations.<installation_id>.orchestration", phase5)
        self.assertIn(
            '{"kind": "set_orchestration", "installation": "<installation_id>"}',
            phase5,
        )
        self.assertIn("refuses an undeclared orchestration change", phase5)


if __name__ == "__main__":
    unittest.main()
