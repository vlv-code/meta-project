"""Wave P, Lane PR: README installation section tests.

Specification (docs/superpowers/plans/2026-11-17-wave-p-plugin-packaging.md,
section 3 Lane PR / auditor section 4.3):

Both READMEs (English README.md, Russian README.ru.md) must gain an
Installation section (ru: "Установка") containing ALL of:

1. `claude plugin marketplace add vlv-code/meta-project`
2. `npx plugins add vlv-code/meta-project`
3. `npx skills add vlv-code/meta-project`

plus the named per-skill caveat: per-skill installers copy skill folders
only; `sync-architecture` is the single standalone skill; the other eight
require the repository's `scripts/` and `templates/` — install the full
plugin or package instead.

Section placement: after the intro/badges block, before the first major
section. Zero-dependency (stdlib unittest only).
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_EN = REPO_ROOT / "README.md"
README_RU = REPO_ROOT / "README.ru.md"

# The three installation channels required by the plan (§3 Lane PR).
CHANNEL_COMMANDS = (
    "claude plugin marketplace add vlv-code/meta-project",
    "npx plugins add vlv-code/meta-project",
    "npx skills add vlv-code/meta-project",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPWaveRInstallationSection(unittest.TestCase):
    """Installation section presence, placement, channels, and caveat."""

    # -- Section presence ---------------------------------------------------

    def test_en_readme_declares_installation_section(self):
        self.assertIn("## Installation", _read(README_EN))

    def test_ru_readme_declares_installation_section(self):
        self.assertIn("## Установка", _read(README_RU))

    # -- Placement: after intro/badges, before the first major section ------

    def test_en_section_after_intro_before_first_major_section(self):
        content = _read(README_EN)
        self.assertIn("## Installation", content)
        idx = content.index("## Installation")
        self.assertGreater(
            idx,
            content.index("<!-- META-PROJECT:ENTRY:END -->"),
            "Installation section must come after the intro/badges entry block",
        )
        self.assertLess(
            idx,
            content.index("## Architectural Principles"),
            "Installation section must come before the first major section",
        )

    def test_ru_section_after_intro_before_first_major_section(self):
        content = _read(README_RU)
        self.assertIn("## Установка", content)
        idx = content.index("## Установка")
        self.assertGreater(
            idx,
            content.index("<!-- META-PROJECT:ENTRY:END -->"),
            "Раздел «Установка» должен идти после блока интро/бейджей",
        )
        self.assertLess(
            idx,
            content.index("## Архитектурные принципы"),
            "Раздел «Установка» должен идти перед первым крупным разделом",
        )

    # -- Table of contents parity -------------------------------------------

    def test_en_toc_lists_installation(self):
        content = _read(README_EN)
        toc_start = content.index("## Table of Contents")
        self.assertIn("- [Installation](#installation)", content[toc_start:])

    def test_ru_toc_lists_installation(self):
        content = _read(README_RU)
        toc_start = content.index("## Содержание")
        self.assertIn("- [Установка](#установка)", content[toc_start:])

    # -- The three installation channels -------------------------------------

    def _assert_channels(self, content: str, label: str) -> None:
        for command in CHANNEL_COMMANDS:
            self.assertIn(
                command,
                content,
                f"{label}: missing installation channel command {command!r}",
            )

    def test_en_readme_lists_all_three_channels(self):
        self._assert_channels(_read(README_EN), "README.md")

    def test_ru_readme_lists_all_three_channels(self):
        self._assert_channels(_read(README_RU), "README.ru.md")

    def test_en_claude_channel_includes_plugin_install_step(self):
        self.assertIn("/plugin install meta-project", _read(README_EN))

    def test_ru_claude_channel_includes_plugin_install_step(self):
        self.assertIn("/plugin install meta-project", _read(README_RU))

    # -- Per-skill caveat (sync-architecture is the only standalone skill) ---

    def test_en_caveat_names_sync_architecture_as_single_standalone(self):
        content = _read(README_EN).replace("`", "")
        self.assertIn(
            "sync-architecture is the single standalone skill",
            content,
            "README.md must name sync-architecture as the single standalone skill",
        )
        self.assertIn(
            "the other eight require the repository's scripts/ and templates/",
            content,
            "README.md must state that the other eight skills need scripts/ and templates/",
        )
        self.assertIn(
            "install the full plugin or package",
            content,
            "README.md must recommend installing the full plugin or package",
        )

    def test_ru_caveat_names_sync_architecture_and_repo_requirements(self):
        content = _read(README_RU).replace("`", "")
        self.assertIn(
            "sync-architecture",
            content,
            "README.ru.md должен называть sync-architecture в оговорке о навыках",
        )
        self.assertIn(
            "единственный автономный навык",
            content,
            "README.ru.md должен называть sync-architecture единственным автономным навыком",
        )
        self.assertIn(
            "остальные восемь",
            content,
            "README.ru.md должен упомянуть остальные восемь навыков",
        )
        self.assertIn("scripts/", content)
        self.assertIn("templates/", content)
        self.assertIn(
            "полный плагин или пакет",
            content,
            "README.ru.md должен рекомендовать установку полного плагина или пакета",
        )


if __name__ == "__main__":
    unittest.main()
