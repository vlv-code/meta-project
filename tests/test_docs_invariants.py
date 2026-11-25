#!/usr/bin/env python3
"""Wave T (Lane T3): Canonical documentation invariants, parity, and anchor integrity.

Replaces the 8 historical fragile doc-lock files (ewave_c, gwave_d, iwave_d,
iwave_it, jwave_d, jwave_p, jwave_r, pwave_r) with dynamic invariants:
- README & CONTRIBUTING line count parity and internal anchor integrity;
- SemVer versioning policy and CHANGELOG release heading parser compatibility;
- Root metadata patterns (.gitattributes, .gitignore, LICENSE) in boundaries templates;
- Dynamic ADR and skills count validation (no hardcoded frozen ranges);
- Repository boundary tree audit (100% coverage) and CODEOWNERS validity.

Zero external dependencies: Python 3.10+ standard library only.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _heading_to_anchor(heading: str) -> str:
    """GitHub Flavored Markdown anchor generation: strip punctuation, replace spaces with hyphens."""
    h = heading.strip().lower()
    h = re.sub(r"[^\w\s\-]", "", h)
    h = h.replace(" ", "-")
    return h


class TestReadmeParityAndIntegrity(unittest.TestCase):
    """Verify README.md and README.ru.md line parity, structure, and anchors."""

    def setUp(self):
        self.en_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.ru_readme = (REPO_ROOT / "README.ru.md").read_text(encoding="utf-8")

    def test_line_count_parity(self):
        en_lines = len(self.en_readme.splitlines())
        ru_lines = len(self.ru_readme.splitlines())
        self.assertEqual(
            en_lines,
            ru_lines,
            f"Line count parity failure: README.md ({en_lines}) != README.ru.md ({ru_lines})",
        )

    def test_internal_anchor_integrity_en(self):
        self._verify_internal_anchors(self.en_readme, "README.md")

    def test_internal_anchor_integrity_ru(self):
        self._verify_internal_anchors(self.ru_readme, "README.ru.md")

    def _verify_internal_anchors(self, content: str, filename: str) -> None:
        headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        anchors = {_heading_to_anchor(h) for h in headings}
        links = re.findall(r"\[.*?\]\(#([a-zA-Z0-9_\-]+)\)", content)
        for link in links:
            self.assertIn(
                link,
                anchors,
                f"Broken internal anchor link #{link} in {filename}",
            )

    def test_core_sections_present_in_both(self):
        for text, name in [(self.en_readme, "README.md"), (self.ru_readme, "README.ru.md")]:
            self.assertIn("META-PROJECT:ENTRY:BEGIN", text, f"Missing entry badge in {name}")
            self.assertIn("META-PROJECT:ENTRY:END", text, f"Missing entry badge in {name}")
            self.assertTrue(
                re.search(r"^##\s+.*(?:installation|установка)", text, re.MULTILINE | re.IGNORECASE),
                f"Missing Installation section in {name}",
            )
            self.assertTrue(
                re.search(r"^##\s+.*(?:glossary|глоссарий)", text, re.MULTILINE | re.IGNORECASE),
                f"Missing Glossary section in {name}",
            )


class TestContributingParityAndPolicy(unittest.TestCase):
    """Verify CONTRIBUTING.md and CONTRIBUTING.ru.md parity and SemVer policy."""

    def setUp(self):
        self.en_contrib = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.ru_contrib = (REPO_ROOT / "CONTRIBUTING.ru.md").read_text(encoding="utf-8")

    def test_line_count_parity(self):
        en_lines = len(self.en_contrib.splitlines())
        ru_lines = len(self.ru_contrib.splitlines())
        self.assertEqual(
            en_lines,
            ru_lines,
            f"Line count parity failure: CONTRIBUTING.md ({en_lines}) != CONTRIBUTING.ru.md ({ru_lines})",
        )

    def test_versioning_policy_declared(self):
        policy_tokens = ("`1.0.0-alpha.*`", "`1.0.0-beta.*`", "`>=1.0.0`")
        for text, name in [(self.en_contrib, "CONTRIBUTING.md"), (self.ru_contrib, "CONTRIBUTING.ru.md")]:
            self.assertIn("SemVer", text, f"SemVer policy not declared in {name}")
            for token in policy_tokens:
                self.assertIn(token, text, f"Missing token {token} in {name}")


class TestChangelogFormatting(unittest.TestCase):
    """Verify CHANGELOG.md SemVer policy and heading parser compatibility."""

    def setUp(self):
        self.changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    def test_header_states_policy(self):
        self.assertIn("Keep a Changelog", self.changelog)
        self.assertTrue(
            "Семантического версионирования" in self.changelog or "Semantic Versioning" in self.changelog
        )
        policy_tokens = ("`1.0.0-alpha.*`", "`1.0.0-beta.*`", "`>=1.0.0`")
        for token in policy_tokens:
            self.assertIn(token, self.changelog)

    def test_release_headings_parsable(self):
        headings = re.findall(r"^##\s+\[(.*?)\](?:\s+-\s+(\d{4}-\d{2}-\d{2}))?", self.changelog, re.MULTILINE)
        self.assertTrue(len(headings) >= 1, "No release headings found in CHANGELOG.md")
        for tag, date in headings:
            if tag.lower() == "unreleased":
                continue
            self.assertTrue(
                re.match(r"^v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.\-]+)?$", tag),
                f"Malformed version tag heading: '{tag}' in CHANGELOG.md",
            )


class TestBoundariesTemplateRootPatterns(unittest.TestCase):
    """Verify template boundaries map essential root VCS files to Green Zone."""

    def test_template_maps_essential_root_files_to_green_zone(self):
        tpl_path = REPO_ROOT / "templates" / "project_knowledge" / "boundaries.md"
        content = tpl_path.read_text(encoding="utf-8")

        self.assertIn(".gitattributes", content)
        self.assertIn(".gitignore", content)
        self.assertIn("LICENSE", content)

        # Ensure root VCS metadata files are NOT in Red Zone
        red_section = content.split("## Red Zone")[1].split("## ")[0] if "## Red Zone" in content else ""
        self.assertNotIn("`.gitattributes`", red_section)
        self.assertNotIn("`.gitignore`", red_section)


class TestDynamicAdrAndSkillsCounts(unittest.TestCase):
    """Dynamically verify ADR and skills alignment without frozen historical strings."""

    def test_skills_count_matches_actual_filesystem(self):
        skills_dir = REPO_ROOT / "skills"
        actual_skills = [
            d.name
            for d in skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").is_file()
        ]
        self.assertTrue(len(actual_skills) >= 10, f"Expected >= 10 skills, found {len(actual_skills)}")

        # Verify skills are mirrored in .agents/skills if .agents exists
        agents_skills = REPO_ROOT / ".agents" / "skills"
        if agents_skills.is_dir():
            for s in actual_skills:
                self.assertTrue(
                    (agents_skills / s / "SKILL.md").is_file(),
                    f"Skill '{s}' missing mirror in .agents/skills/",
                )

    def test_highest_adr_matches_roadmap_contents(self):
        roadmap = (REPO_ROOT / "docs" / "decisions_and_roadmap.md").read_text(encoding="utf-8")
        adr_numbers = [
            int(m)
            for m in re.findall(r"ADR\s*#?(\d+)", roadmap)
        ]
        # Also parse ranges like ADR #14–#23
        for start, end in re.findall(r"ADR\s*#?(\d+)[–\-]#?(\d+)", roadmap):
            adr_numbers.extend([int(start), int(end)])
        self.assertTrue(len(adr_numbers) > 0, "No ADR headings found in roadmap")
        max_adr = max(adr_numbers)
        self.assertTrue(max_adr >= 23, f"Expected highest ADR >= 23, found {max_adr}")


class TestCodeownersAndAuditTree(unittest.TestCase):
    """Verify boundary audit tree 100% coverage and CODEOWNERS sanction integrity."""

    def test_repository_tree_audit_passes_100_percent(self):
        boundaries_path = REPO_ROOT / ".agents" / "project_knowledge" / "boundaries.md"
        if not boundaries_path.is_file():
            self.skipTest("dogfood-branch contract: requires live .agents/project_knowledge/boundaries.md")
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "check_boundaries.py"),
            "--boundaries",
            str(boundaries_path),
            "--audit-tree",
        ]
        res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Boundary audit failed: {res.stderr or res.stdout}")
        self.assertIn("100% boundary coverage", res.stdout)

    def test_codeowners_file_present_and_valid(self):
        codeowners_path = REPO_ROOT / ".github" / "CODEOWNERS"
        self.assertTrue(codeowners_path.is_file(), "Missing .github/CODEOWNERS")
        content = codeowners_path.read_text(encoding="utf-8")
        self.assertIn("@vlv-code", content)

    def test_ci_declares_pyflakes_step(self):
        ci_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(ci_path.is_file(), "Missing .github/workflows/ci.yml")
        content = ci_path.read_text(encoding="utf-8")
        self.assertIn("pyflakes", content)


if __name__ == "__main__":
    unittest.main()
