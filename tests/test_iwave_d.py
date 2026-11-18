"""Wave I, Lane ID: docs & template sweep lock-ins.

Specification (docs/superpowers/plans/2026-11-18-wave-i-audit-response.md,
section 5 Lane ID / audit sections 6.6, 6.7, 7.2, 7.3):

1. T-D1 §6.6: templates/project_knowledge/boundaries.md maps the generic
   root files `.gitattributes`, `.gitignore`, `LICENSE` in the GREEN zone
   (VCS / repository metadata hygiene) so they stop falling into the
   Default Deny (Black Zone) bucket.
2. T-D2 §6.7: README.md and README.ru.md reference the REAL canonical ADR
   range (#14–#22, verified against docs/decisions_and_roadmap.md §7.1)
   instead of the nonexistent `ADR #1–#8`; the pointer to the canonical
   doc remains.
3. T-D3 §7.2: both READMEs carry the trusted-base note near the gate
   description — enforcement against self-certification lives in CI
   (trusted-base gate); the local pre-commit hook is a convenience layer;
   `META_PROJECT_ALLOW_RED_ZONE=1` is a local operator override.
4. T-D4 §7.3: both CONTRIBUTING guides tell contributors that the dev
   branch carries the maintainers' live agent installation, so
   `.agents/team/*/notes.md` and `.agents/project_knowledge/observations.md`
   intentionally contain internal agent-workflow history (dogfooding by
   design; visible on fork).

Zero-dependency (stdlib unittest only).
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_BOUNDARIES = REPO_ROOT / "templates" / "project_knowledge" / "boundaries.md"
README_EN = REPO_ROOT / "README.md"
README_RU = REPO_ROOT / "README.ru.md"
CONTRIB_EN = REPO_ROOT / "CONTRIBUTING.md"
CONTRIB_RU = REPO_ROOT / "CONTRIBUTING.ru.md"

# Canonical ADR range verified in docs/decisions_and_roadmap.md §7.1
# (heading "Зафиксированные архитектурные решения (ADR #14–#22)"; the
# numbered entries run 14..22). The pre-fix READMEs claimed "#1–#8",
# which corresponds to no real ADR numbering. En dash (U+2013) as in the doc.
ADRS_CANONICAL_RANGE = "ADR #14–#22"
ADRS_STALE_RANGE = "ADR #1–#8"

# T-D1: generic root-file patterns that must be mapped in the Green zone.
GREEN_ROOT_PATTERNS = ("`.gitattributes`", "`.gitignore`", "`LICENSE`")

# T-D3 key literals (EN / RU) for the trusted-base gate note.
CI_NOTE_LITERALS_EN = (
    "trusted-base gate",
    "the local pre-commit hook is a convenience layer",
    "`META_PROJECT_ALLOW_RED_ZONE=1` is a local operator override",
)
CI_NOTE_LITERALS_RU = (
    "trusted-base gate",
    "слой удобства",
    "локальное переопределение оператора",
    "`META_PROJECT_ALLOW_RED_ZONE=1`",
)

# T-D4 key literals (EN / RU) for the dogfooding note in CONTRIBUTING.
DOGFOOD_PATHS = (
    ".agents/team/*/notes.md",
    ".agents/project_knowledge/observations.md",
)
DOGFOOD_LITERALS_EN = (
    "dogfooding by design",
    "development branch (`dev`) carries the maintainers' live agent installation",
)
DOGFOOD_LITERALS_RU = (
    "dogfooding by design",
    "ветка разработки (`dev`) несёт живую агентную установку мейнтейнеров",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _green_zone_section(text: str) -> str:
    """Slice of the boundaries template between the Green and Yellow headers."""
    start = text.index("## Green Zone")
    end = text.index("## Yellow Zone")
    return text[start:end]


class TestIWaveDTemplateBoundariesRootPatterns(unittest.TestCase):
    """T-D1 §6.6: generic root files mapped in the template Green zone."""

    def test_template_maps_gitattributes_in_green_zone(self):
        green = _green_zone_section(_read(TEMPLATE_BOUNDARIES))
        self.assertIn(
            "`.gitattributes`",
            green,
            "templates/project_knowledge/boundaries.md must map `.gitattributes` in the Green zone",
        )

    def test_template_maps_gitignore_in_green_zone(self):
        green = _green_zone_section(_read(TEMPLATE_BOUNDARIES))
        self.assertIn(
            "`.gitignore`",
            green,
            "templates/project_knowledge/boundaries.md must map `.gitignore` in the Green zone",
        )

    def test_template_maps_bare_license_in_green_zone(self):
        green = _green_zone_section(_read(TEMPLATE_BOUNDARIES))
        self.assertIn(
            "`LICENSE`",
            green,
            "templates/project_knowledge/boundaries.md must map bare `LICENSE` "
            "(no extension, so `*.md` does not cover it) in the Green zone",
        )

    def test_root_patterns_absent_from_red_zone(self):
        """Adversarial: the hygiene files must be mapped Green, not prohibited."""
        text = _read(TEMPLATE_BOUNDARIES)
        red = text[text.index("## Red Zone") :]
        for pattern in GREEN_ROOT_PATTERNS:
            self.assertNotIn(
                pattern,
                red,
                f"{pattern} must not be classified in the Red zone",
            )

    def test_green_zone_bullet_describes_vcs_metadata_hygiene(self):
        green = _green_zone_section(_read(TEMPLATE_BOUNDARIES))
        self.assertIn(
            "VCS and repository metadata hygiene",
            green,
            "Green-zone bullet for the root hygiene files must describe "
            "VCS / repository metadata hygiene",
        )


class TestIWaveDReadmeAdrRange(unittest.TestCase):
    """T-D2 §6.7: READMEs reference the real canonical ADR range."""

    def test_en_readme_states_canonical_adr_range(self):
        content = _read(README_EN)
        self.assertIn(
            ADRS_CANONICAL_RANGE,
            content,
            "README.md must reference the real canonical ADR range "
            "(#14–#22 per docs/decisions_and_roadmap.md)",
        )

    def test_ru_readme_states_canonical_adr_range(self):
        content = _read(README_RU)
        self.assertIn(
            ADRS_CANONICAL_RANGE,
            content,
            "README.ru.md must reference the real canonical ADR range "
            "(#14–#22 per docs/decisions_and_roadmap.md)",
        )

    def test_en_readme_no_stale_adr_range(self):
        """Adversarial: the nonexistent `ADR #1–#8` claim must be gone."""
        self.assertNotIn(
            ADRS_STALE_RANGE,
            _read(README_EN),
            "README.md still references the nonexistent ADR #1–#8",
        )

    def test_ru_readme_no_stale_adr_range(self):
        """Adversarial: the nonexistent `ADR #1–#8` claim must be gone."""
        self.assertNotIn(
            ADRS_STALE_RANGE,
            _read(README_RU),
            "README.ru.md still references the nonexistent ADR #1–#8",
        )

    def test_en_readme_keeps_pointer_to_canonical_doc(self):
        content = _read(README_EN)
        self.assertIn(
            "docs/decisions_and_roadmap.md",
            content,
            "README.md must keep the pointer to the canonical ADR document",
        )

    def test_ru_readme_keeps_pointer_to_canonical_doc(self):
        content = _read(README_RU)
        self.assertIn(
            "docs/decisions_and_roadmap.md",
            content,
            "README.ru.md must keep the pointer to the canonical ADR document",
        )


class TestIWaveDReadmeTrustedBaseNote(unittest.TestCase):
    """T-D3 §7.2: trusted-base gate note near the gate description."""

    def test_en_readme_trusted_base_note_present(self):
        content = _read(README_EN)
        for literal in CI_NOTE_LITERALS_EN:
            self.assertIn(
                literal,
                content,
                f"README.md trusted-base note is missing literal {literal!r}",
            )

    def test_ru_readme_trusted_base_note_present(self):
        content = _read(README_RU)
        for literal in CI_NOTE_LITERALS_RU:
            self.assertIn(
                literal,
                content,
                f"README.ru.md trusted-base note is missing literal {literal!r}",
            )


class TestIWaveDContributingDogfoodingNote(unittest.TestCase):
    """T-D4 §7.3: dogfooding note in both CONTRIBUTING guides."""

    def _assert_dogfood_note(self, content: str, literals, label: str) -> None:
        for literal in DOGFOOD_PATHS + tuple(literals):
            self.assertIn(
                literal,
                content,
                f"{label} dogfooding note is missing literal {literal!r}",
            )

    def test_en_contributing_dogfooding_note_present(self):
        self._assert_dogfood_note(_read(CONTRIB_EN), DOGFOOD_LITERALS_EN, "CONTRIBUTING.md")

    def test_ru_contributing_dogfooding_note_present(self):
        self._assert_dogfood_note(_read(CONTRIB_RU), DOGFOOD_LITERALS_RU, "CONTRIBUTING.ru.md")


if __name__ == "__main__":
    unittest.main()
