"""Wave J, Lane JR: README glossary tests (audit-#4 plan, task P0-1).

Specification (consolidated audit #4, section 3 Discoverability):

Both READMEs (English README.md, Russian README.ru.md) must gain a
glossary section (EN: "## Glossary", RU: "## Глоссарий") that:

1. defines each of the 14 canonical project terms (term label in the
   table's first column);
2. carries a relative link to the term's canonical doc on every row
   (in-page anchors count for README-internal terms);
3. appends the "(RU)" marker to links into the Russian-language docs
   (docs/framework_philosophy_and_vision.md, docs/decisions_and_roadmap.md);
4. is listed in the Table of Contents in the same relative position
   (after the Repository Inspection entry, before the Components entry);
5. sits in the body after the Repository Inspection section and before
   the Meta-Project Components section;
6. keeps bilingual line-for-line parity: identical line counts;
7. includes a 4-line zone mini-example (paths preserved in both
   languages).

Zero-dependency (stdlib unittest only).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_EN = REPO_ROOT / "README.md"
README_RU = REPO_ROOT / "README.ru.md"

GLOSSARY_HEADING_EN = "## Glossary"
GLOSSARY_HEADING_RU = "## Глоссарий"
TOC_HEADING_EN = "## Table of Contents"
TOC_HEADING_RU = "## Содержание"

BODY_PREV_SECTION_EN = "## Repository Inspection & Canonical States"
BODY_NEXT_SECTION_EN = "## Meta-Project Components"
BODY_PREV_SECTION_RU = "## Обследование репозитория и 8 канонических состояний"
BODY_NEXT_SECTION_RU = "## Компоненты репозитория Meta-Project"

TOC_PREV_ENTRY_EN = "[Repository Inspection & Canonical States]"
TOC_NEXT_ENTRY_EN = "[Meta-Project Components]"
TOC_PREV_ENTRY_RU = "[Обследование репозитория"
TOC_NEXT_ENTRY_RU = "[Компоненты репозитория Meta-Project]"

# The 14 canonical terms, in table order. Both language tables use the
# same English term labels (canonical project vocabulary, already used
# untranslated in README.ru.md).
TERMS = (
    "North Stars",
    "Passport",
    "Knowledge slice",
    "Zones",
    "Default Deny",
    "Canonical state",
    "Capability matrix",
    "Opportunistic refresh",
    "Facts digest",
    "Decision-RTL",
    "Astra primitives",
    "Harness",
    "Installation",
    "Deployment modes",
)

# Russian-language docs must be linked with the "(RU)" marker in the row.
TERMS_REQUIRING_RU_MARKER = ("North Stars", "Decision-RTL", "Installation")

# Verified canonical link targets, per language (in-page anchors differ).
EXPECTED_LINKS_EN = {
    "North Stars": "docs/framework_philosophy_and_vision.md",
    "Passport": "templates/AGENTS.md",
    "Knowledge slice": "templates/project_knowledge/",
    "Zones": "templates/project_knowledge/boundaries.md",
    "Default Deny": "templates/project_knowledge/boundaries.md",
    "Canonical state": "#repository-inspection--canonical-states",
    "Capability matrix": "scripts/inspect_meta_project.py",
    "Opportunistic refresh": "templates/AGENTS.md",
    "Facts digest": "scripts/inspect_meta_project.py",
    "Decision-RTL": "docs/framework_philosophy_and_vision.md",
    "Astra primitives": "docs/primitives.md",
    "Harness": "scripts/inspect_meta_project.py",
    "Installation": "docs/decisions_and_roadmap.md",
    "Deployment modes": (
        "#6-deployment-modes-shared-repo-level-vs-invisible-overlay"
    ),
}
EXPECTED_LINKS_RU = dict(EXPECTED_LINKS_EN)
EXPECTED_LINKS_RU.update(
    {
        "Canonical state": "#обследование-репозитория-и-8-канонических-состояний",
        "Deployment modes": (
            "#6-режимы-развертывания-открытый-стандарт-vs-невидимый-оверлей"
        ),
    }
)

# Zone mini-example: exactly 4 lines, paths preserved across languages.
ZONE_EXAMPLE_EN = (
    "Green: docs/**, tests/test_*.py — autonomous",
    "Yellow: AGENTS.md, pyproject.toml — only after local verification",
    "Red: .env*, migrations/**, src/auth/** — only with explicit permission",
    "Anything unmapped is Red (Default Deny).",
)
ZONE_EXAMPLE_RU = (
    "Green: docs/**, tests/test_*.py — автономно",
    "Yellow: AGENTS.md, pyproject.toml — только после локальной проверки",
    "Red: .env*, migrations/**, src/auth/** — только с явным разрешением",
    "Всё, что не сопоставлено с зоной, — Red (Default Deny).",
)
ZONE_EXAMPLE_ANCHOR_LINE = "Green: docs/**, tests/test_*.py"

_LINK_RE = re.compile(r"\]\(([^)]+)\)")
_FENCED_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(content: str, heading: str) -> str:
    """Return the text from ``heading`` up to the next '## ' heading."""
    start = content.index(heading)
    nxt = content.find("\n## ", start + len(heading))
    return content[start:] if nxt == -1 else content[start:nxt]


def _github_slug(heading_text: str) -> str:
    """Approximate GitHub's anchor slugger (unicode-aware, stdlib only)."""
    slug = re.sub(r"[^\w\- ]", "", heading_text.strip().lower())
    return slug.replace(" ", "-")


def _assert_relative_links_exist(
    test: unittest.TestCase, targets: "set[str]", readme: Path
) -> None:
    for target in sorted(targets):
        if target.startswith("#"):
            slug = target[1:]
            headings = re.findall(r"^#{1,6} (.+)$", _read(readme), re.MULTILINE)
            slugs = {_github_slug(h) for h in headings}
            test.assertIn(
                slug,
                slugs,
                f"{readme.name}: glossary in-page anchor {target!r} "
                f"does not resolve to any heading",
            )
        else:
            test.assertTrue(
                (REPO_ROOT / target).exists(),
                f"{readme.name}: glossary link target {target!r} "
                f"does not exist in the repository",
            )


class TestJWaveRGlossarySection(unittest.TestCase):
    """Glossary presence, terms, links, TOC, parity, zone example."""

    # -- Section presence ---------------------------------------------------

    def test_en_readme_declares_glossary_section(self):
        self.assertIn(GLOSSARY_HEADING_EN, _read(README_EN))

    def test_ru_readme_declares_glossary_section(self):
        self.assertIn(GLOSSARY_HEADING_RU, _read(README_RU))

    # -- Placement: after Repository Inspection, before Components ----------

    def test_en_glossary_between_inspection_and_components(self):
        content = _read(README_EN)
        idx = content.index(GLOSSARY_HEADING_EN)
        self.assertGreater(
            idx,
            content.index(BODY_PREV_SECTION_EN),
            "Glossary must come after the Repository Inspection section",
        )
        self.assertLess(
            idx,
            content.index(BODY_NEXT_SECTION_EN),
            "Glossary must come before the Meta-Project Components section",
        )

    def test_ru_glossary_between_inspection_and_components(self):
        content = _read(README_RU)
        idx = content.index(GLOSSARY_HEADING_RU)
        self.assertGreater(
            idx,
            content.index(BODY_PREV_SECTION_RU),
            "Раздел «Глоссарий» должен идти после раздела обследования",
        )
        self.assertLess(
            idx,
            content.index(BODY_NEXT_SECTION_RU),
            "Раздел «Глоссарий» должен идти перед разделом компонентов",
        )

    # -- The 14 terms, as first-column labels -------------------------------

    def _assert_all_terms_defined(self, readme: Path, heading: str) -> None:
        section = _section(_read(readme), heading)
        for term in TERMS:
            row = f"| {term} |"
            self.assertIn(
                row,
                section,
                f"{readme.name}: glossary table must define {term!r} "
                f"as a first-column label ({row!r})",
            )

    def test_en_glossary_defines_all_14_terms(self):
        self._assert_all_terms_defined(README_EN, GLOSSARY_HEADING_EN)

    def test_ru_glossary_defines_all_14_terms(self):
        self._assert_all_terms_defined(README_RU, GLOSSARY_HEADING_RU)

    # -- Relative canonical links on every row ------------------------------

    def _assert_row_links(self, readme: Path, heading: str, expected: dict) -> None:
        section = _section(_read(readme), heading)
        targets_seen = set()
        for term in TERMS:
            row = f"| {term} |"
            self.assertIn(row, section, f"{readme.name}: missing row for {term!r}")
            row_line = next(
                line for line in section.splitlines() if line.startswith(row)
            )
            targets = _LINK_RE.findall(row_line)
            self.assertTrue(
                targets,
                f"{readme.name}: row {term!r} carries no relative link",
            )
            for target in targets:
                self.assertFalse(
                    target.startswith("http://") or target.startswith("https://"),
                    f"{readme.name}: row {term!r} links to a non-relative "
                    f"target {target!r}",
                )
            self.assertIn(
                expected[term],
                targets,
                f"{readme.name}: row {term!r} must link its canonical doc "
                f"{expected[term]!r}; found {targets!r}",
            )
            targets_seen.update(targets)
        _assert_relative_links_exist(self, targets_seen, readme)

    def test_en_glossary_rows_link_canonical_docs(self):
        self._assert_row_links(README_EN, GLOSSARY_HEADING_EN, EXPECTED_LINKS_EN)

    def test_ru_glossary_rows_link_canonical_docs(self):
        self._assert_row_links(README_RU, GLOSSARY_HEADING_RU, EXPECTED_LINKS_RU)

    # -- "(RU)" marker on links into Russian-language docs ------------------

    def _assert_ru_markers(self, readme: Path, heading: str) -> None:
        section = _section(_read(readme), heading)
        for term in TERMS_REQUIRING_RU_MARKER:
            row_line = next(
                line
                for line in section.splitlines()
                if line.startswith(f"| {term} |")
            )
            self.assertIn(
                "(RU)",
                row_line,
                f"{readme.name}: row {term!r} links a Russian-language doc "
                f"and must carry the '(RU)' marker",
            )

    def test_en_glossary_marks_russian_docs(self):
        self._assert_ru_markers(README_EN, GLOSSARY_HEADING_EN)

    def test_ru_glossary_marks_russian_docs(self):
        self._assert_ru_markers(README_RU, GLOSSARY_HEADING_RU)

    # -- Table of Contents parity -------------------------------------------

    def _assert_toc_entry(self, readme: Path, toc_heading: str, entry: str) -> None:
        content = _read(readme)
        toc = _section(content, toc_heading)
        self.assertIn(entry, toc, f"{readme.name}: TOC must list the glossary")

    def test_en_toc_lists_glossary(self):
        self._assert_toc_entry(README_EN, TOC_HEADING_EN, "- [Glossary](#glossary)")

    def test_ru_toc_lists_glossary(self):
        self._assert_toc_entry(README_RU, TOC_HEADING_RU, "- [Глоссарий](#глоссарий)")

    def test_en_toc_glossary_position_matches_body(self):
        toc = _section(_read(README_EN), TOC_HEADING_EN)
        idx = toc.index("- [Glossary](#glossary)")
        self.assertGreater(
            idx,
            toc.index(TOC_PREV_ENTRY_EN),
            "TOC glossary entry must follow the Repository Inspection entry",
        )
        self.assertLess(
            idx,
            toc.index(TOC_NEXT_ENTRY_EN),
            "TOC glossary entry must precede the Components entry",
        )

    def test_ru_toc_glossary_position_matches_body(self):
        toc = _section(_read(README_RU), TOC_HEADING_RU)
        idx = toc.index("- [Глоссарий](#глоссарий)")
        self.assertGreater(
            idx,
            toc.index(TOC_PREV_ENTRY_RU),
            "Запись «Глоссарий» в содержании должна идти после записи об "
            "обследовании",
        )
        self.assertLess(
            idx,
            toc.index(TOC_NEXT_ENTRY_RU),
            "Запись «Глоссарий» в содержании должна идти перед записью о "
            "компонентах",
        )

    # -- Bilingual line-for-line parity --------------------------------------

    def test_both_readmes_keep_same_line_count(self):
        en_lines = _read(README_EN).splitlines()
        ru_lines = _read(README_RU).splitlines()
        self.assertGreater(
            len(en_lines), 100, "README.md unexpectedly short; fixture drift?"
        )
        self.assertEqual(
            len(en_lines),
            len(ru_lines),
            "README.md and README.ru.md must keep identical line counts "
            f"(en={len(en_lines)}, ru={len(ru_lines)})",
        )

    # -- Zone mini-example (exactly 4 lines) ---------------------------------

    def _assert_zone_example(self, readme: Path, expected_lines: tuple) -> None:
        content = _read(readme)
        blocks = [
            block
            for block in _FENCED_BLOCK_RE.findall(content)
            if ZONE_EXAMPLE_ANCHOR_LINE in block
        ]
        self.assertTrue(
            blocks,
            f"{readme.name}: no fenced zone mini-example found "
            f"(expected a 4-line block starting {ZONE_EXAMPLE_ANCHOR_LINE!r})",
        )
        lines = blocks[0].rstrip("\n").split("\n")
        self.assertEqual(
            len(lines),
            4,
            f"{readme.name}: zone mini-example must be exactly 4 lines, "
            f"got {len(lines)}: {lines!r}",
        )
        for expected in expected_lines:
            self.assertIn(
                expected,
                lines,
                f"{readme.name}: zone mini-example line missing: {expected!r}",
            )

    def test_en_zone_mini_example_is_4_lines(self):
        self._assert_zone_example(README_EN, ZONE_EXAMPLE_EN)

    def test_ru_zone_mini_example_is_4_lines(self):
        self._assert_zone_example(README_RU, ZONE_EXAMPLE_RU)


if __name__ == "__main__":
    unittest.main()
