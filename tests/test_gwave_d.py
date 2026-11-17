#!/usr/bin/env python3
"""
Wave G, Lane D — Doc canon + primitives vocabulary (Astra).

Plan: docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md (§5).

Lock-ins:
1. Section-map drift fixed (audit §7.2): decommission skill references the
   canonical 8-section passport roster (Section 7) — the stale
   "## 6. Project Agent Team" reference is gone; scan skill anchors its
   passport check to the canonical section names (Sections 2-5).
2. Tune skill Phase 3 proposal-record field names are English (no Cyrillic
   inside the English artifact).
3. docs/primitives.md maps the 4 Astra primitives to existing, importable
   implementations — documentation only, no behavior change.

Canonical passport structure verified against templates/AGENTS.md:
8 sections; the roster is "## 7. Project Agent Team & Multi-Harness Identity".

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# (script path relative to repo root, function symbol) — the 4 Astra
# primitives referenced by docs/primitives.md (plan §5.3).
PRIMITIVES = [
    ("scripts/inspect_meta_project.py", "inspect_repository"),
    ("scripts/verify_identity.py", "evaluate_actor_admission"),
    ("scripts/manage_reports.py", "evaluate_manage_intake"),
    ("scripts/record_obs.py", "record_observation"),
]

CANONICAL_ROSTER_HEADING = "## 7. Project Agent Team & Multi-Harness Identity"
STALE_ROSTER_REFERENCE = "## 6."

SCAN_SECTION_NAMES = [
    "Repository Meta-Map",
    "Directive Meta-Knowledge Protocol",
    "Procedural Skills Registry",
    "Local Verification Tooling & Autonomous Fallback",
]

TUNE_FIELD_NAMES = [
    "Observed problem",
    "Evidence and data limits",
    "Hypothesized cause",
    "Proposed change and scope",
    "Expected effect",
    "Verification method",
    "Preserved constraints",
    "Rollback method",
    "Executor",
]

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPrimitiveSymbolsExist(unittest.TestCase):
    """Plan §5.4(a): every primitive's referenced symbol exists at import
    level — primitives are names for existing implementations."""

    def test_all_primitive_symbols_importable(self):
        for script_rel, func_name in PRIMITIVES:
            module_path = script_rel.replace("/", ".").removesuffix(".py")
            module = __import__(module_path, fromlist=[func_name])
            self.assertTrue(
                hasattr(module, func_name),
                f"{script_rel} must expose {func_name}",
            )
            self.assertTrue(callable(getattr(module, func_name)))

    def test_primitive_scripts_exist_on_disk(self):
        for script_rel, _func_name in PRIMITIVES:
            self.assertTrue(
                (REPO_ROOT / script_rel).is_file(),
                f"primitive implementation missing: {script_rel}",
            )


class TestDecommissionSectionReferences(unittest.TestCase):
    """Plan §5.1 / §5.4(b): decommission references the canonical 8-section
    passport roster; the stale legacy "## 6. Project Agent Team" reference
    is gone (canonical structure verified against templates/AGENTS.md)."""

    def setUp(self):
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )


    def test_template_canon_is_8_sections_with_roster_at_7(self):
        template = _read(REPO_ROOT / "templates" / "AGENTS.md")
        headings = re.findall(r"^## (\d+)\. (.+)$", template, flags=re.M)
        self.assertEqual(
            [int(num) for num, _ in headings],
            list(range(1, 9)),
            "canonical passport must have exactly sections 1..8",
        )
        self.assertEqual(headings[6][1], "Project Agent Team & Multi-Harness Identity")

    def _assert_skill(self, skill_file: Path):
        text = _read(skill_file)
        self.assertIn(
            CANONICAL_ROSTER_HEADING,
            text,
            f"{skill_file} must reference the canonical Section 7 roster heading",
        )
        self.assertGreaterEqual(
            text.count(CANONICAL_ROSTER_HEADING),
            2,
            "both the targeted-sunset and batch-reset steps must reference Section 7",
        )
        self.assertNotIn(
            STALE_ROSTER_REFERENCE,
            text,
            f"{skill_file} still carries the stale legacy roster reference",
        )
        self.assertIn(
            "Section 7 roster",
            text,
            "Phase 0 must keep the consistent 'AGENTS.md Section 7 roster' wording",
        )

    def test_canonical_skill_references(self):
        self._assert_skill(
            REPO_ROOT / "skills" / "decommission-meta-project" / "SKILL.md"
        )

    def test_mirror_skill_references(self):
        self._assert_skill(
            REPO_ROOT
            / ".agents"
            / "skills"
            / "decommission-meta-project"
            / "SKILL.md"
        )


class TestScanSectionReferences(unittest.TestCase):
    """Plan §5.1 / §5.4(b): scan anchors its passport check to the canonical
    section names (Sections 2-5) instead of bare stale numbers — the names
    must match templates/AGENTS.md headings exactly (nothing invented)."""

    def setUp(self):
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )


    def _assert_skill(self, skill_file: Path):
        text = _read(skill_file)
        self.assertIn(
            "Ensure Sections 2-5 ("
            + ", ".join(f"`{name}`" for name in SCAN_SECTION_NAMES)
            + ")",
            text,
            f"{skill_file} must anchor Sections 2-5 to the canonical names",
        )
        self.assertNotIn(
            "Section 2, 3, 4, 5",
            text,
            f"{skill_file} still carries the bare stale section reference",
        )

    def test_canonical_skill_references(self):
        self._assert_skill(REPO_ROOT / "skills" / "scan-meta-project" / "SKILL.md")

    def test_mirror_skill_references(self):
        self._assert_skill(
            REPO_ROOT / ".agents" / "skills" / "scan-meta-project" / "SKILL.md"
        )

    def test_scan_section_names_match_template_headings(self):
        template = _read(REPO_ROOT / "templates" / "AGENTS.md")
        for name in SCAN_SECTION_NAMES:
            self.assertRegex(
                template,
                r"(?m)^## \d+\. " + re.escape(name) + r"\s*$",
                f"scan references '{name}' but the canonical passport has no such heading",
            )


class TestTuneFieldNamesEnglish(unittest.TestCase):
    """Plan §5.2 / §5.4(c): the Phase 3 proposal-record field names are
    English — the artifact must not mix Russian field names into an English
    procedure (init's bilingual interview exemption does not apply here)."""

    def setUp(self):
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )


    def _phase3_block(self, skill_file: Path) -> str:
        text = _read(skill_file)
        start = text.index("### Phase 3")
        end = text.index("### Phase 4")
        return text[start:end]

    def _assert_skill(self, skill_file: Path):
        block = self._phase3_block(skill_file)
        self.assertIsNone(
            CYRILLIC_RE.search(block),
            f"{skill_file} Phase 3 still contains Cyrillic field names",
        )
        normalized = " ".join(block.split())
        for field in TUNE_FIELD_NAMES:
            self.assertIn(field, normalized)

    def test_canonical_skill_phase3_english(self):
        self._assert_skill(REPO_ROOT / "skills" / "tune-meta-project" / "SKILL.md")

    def test_mirror_skill_phase3_english(self):
        self._assert_skill(
            REPO_ROOT / ".agents" / "skills" / "tune-meta-project" / "SKILL.md"
        )


class TestPrimitivesDoc(unittest.TestCase):
    """Plan §5.4(d): docs/primitives.md has the 4 primitive entries, and
    every script+function reference matches reality (file exists, symbol
    importable, name spelled identically to the module attribute)."""

    DOC = REPO_ROOT / "docs" / "primitives.md"

    def test_doc_exists_with_header_note(self):
        text = _read(self.DOC)
        self.assertIn("NAMES for existing implementations", text)
        self.assertIn("never re-implement", text)

    def test_doc_has_exactly_four_primitive_entries(self):
        text = _read(self.DOC)
        entries = re.findall(r"^## \d+\. (.+)$", text, flags=re.M)
        self.assertEqual(
            entries,
            [
                "Deterministic Survey",
                "Identity Admission",
                "Report Intake",
                "Observation Recording",
            ],
        )

    def test_doc_script_function_fields_match_reality(self):
        text = _read(self.DOC)
        for script_rel, func_name in PRIMITIVES:
            self.assertIn(script_rel, text, f"doc must name {script_rel}")
            self.assertIn(func_name, text, f"doc must name {func_name}")
            module = __import__(
                script_rel.replace("/", ".").removesuffix(".py"),
                fromlist=[func_name],
            )
            self.assertTrue(callable(getattr(module, func_name)))
        # every script path mentioned in the doc is one of the real ones
        for mentioned in re.findall(r"scripts/[A-Za-z_]+\.py", text):
            self.assertIn(
                mentioned,
                [script for script, _ in PRIMITIVES],
                f"doc references unknown script {mentioned}",
            )


if __name__ == "__main__":
    unittest.main()
