"""
Wave P — Lane PF lock-in tests (plugin-packaging frontmatter).

Plan: docs/superpowers/plans/2026-11-17-wave-p-plugin-packaging.md (§3 Lane PF).
Wave K supersession: added skills/triage-incident/SKILL.md (expanding the
canonical skill inventory from 9 to 10); packaging metadata (license +
compatibility + no metadata.version) applies to ALL 10 skills, while the
byte-identical HEAD description lock scopes to the 9 pre-existing Wave P
skills so pre-commit runs do not fail on a newly added Wave K skill.

Locks in:
  (a) every skills/*/SKILL.md (glob; 10 including triage-incident) carries
      top-level frontmatter keys `license` (value MIT) and `compatibility`
      (value containing "Python 3.10+") — the plugin-channel packaging metadata.
  (b) NO frontmatter contains a `metadata:` block with a `version` key:
      version stays single-sourced in templates/release_manifest.json
      (framework_version) and the packaging manifests, never duplicated
      into skill frontmatter.
  (c) the 9 Wave P skill descriptions stay byte-identical to git HEAD.

Zero-dependency: Python 3.10+ stdlib only (subprocess `git` is host
tooling explicitly mandated by the plan for the HEAD comparison).
"""

from pathlib import Path
import re
import subprocess
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT_DIR / "skills"
EXPECTED_SKILL_COUNT = 10
WAVE_P_SKILLS = (
    "decommission-meta-project",
    "ground-meta-project",
    "init-meta-project",
    "manage-meta-project",
    "record-observation",
    "scan-meta-project",
    "sync-architecture",
    "tune-meta-project",
    "update-meta-project",
)
EXPECTED_LICENSE = "MIT"
EXPECTED_COMPAT_SUBSTR = "Python 3.10+"


def read_frontmatter(text: str):
    """Return the raw frontmatter block (between the opening and closing
    --- delimiter lines), or None if absent/malformed."""
    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", text, re.DOTALL)
    return match.group(1) if match else None


def top_level_scalar(frontmatter: str, key: str):
    """Return the single-line scalar value of a top-level `key: value`
    frontmatter entry (column-0 key only), or None. Surrounding quotes
    are stripped; the raw text form is the caller's concern."""
    match = re.search(
        rf"^{re.escape(key)}:[ \t]*(.+?)[ \t]*$", frontmatter, re.MULTILINE
    )
    if not match:
        return None
    value = match.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def description_block(frontmatter: str) -> str:
    """Extract the raw description entry chunk: the `description:` line plus
    every following continuation line (indented or blank, folded-block style)
    up to the next top-level key or the end of the frontmatter block."""
    captured = []
    in_block = False
    for line in frontmatter.split("\n"):
        if line.startswith("description:"):
            in_block = True
            captured.append(line)
            continue
        if in_block:
            if line == "" or line[0] in " \t":
                captured.append(line)
            else:
                break
    return "\n".join(captured)


def metadata_version_present(frontmatter: str) -> bool:
    """True if the frontmatter declares a version under a `metadata:` block —
    either block-style (indented sub-keys) or inline flow-style."""
    lines = frontmatter.split("\n")
    in_metadata = False
    for line in lines:
        if re.match(r"^metadata:[ \t]*$", line):
            in_metadata = True
            continue
        if re.match(r"^metadata:[ \t]*\{", line):
            # inline flow-style mapping: look for a version key on the line
            if re.search(r"[{,]\s*['\"]?version['\"]?\s*:", line):
                return True
            continue
        if in_metadata:
            if line == "" or line[0] in " \t":
                if re.match(r"^[ \t]+['\"]?version['\"]?[ \t]*:", line):
                    return True
            else:
                break  # next top-level key: metadata block ended
    return False


def head_text(relpath: str) -> str:
    """Return file content at git HEAD via `git show HEAD:<relpath>`."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"],
        cwd=str(ROOT_DIR),
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git show HEAD:{relpath} failed: "
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )
    return result.stdout.decode("utf-8")


class TestSkillInventory(unittest.TestCase):
    def test_skill_glob_is_exactly_nine(self):
        skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
        self.assertEqual(
            len(skill_files),
            EXPECTED_SKILL_COUNT,
            "The packaging frontmatter contract is scoped to exactly "
            f"{EXPECTED_SKILL_COUNT} skills; found {len(skill_files)}: "
            f"{[str(p.relative_to(ROOT_DIR)) for p in skill_files]}",
        )


class TestPackagingFrontmatter(unittest.TestCase):
    def test_every_skill_has_license_and_compatibility(self):
        for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            with self.subTest(skill=skill_file.parent.name):
                frontmatter = read_frontmatter(
                    skill_file.read_text(encoding="utf-8")
                )
                self.assertIsNotNone(
                    frontmatter,
                    f"{skill_file}: missing or malformed frontmatter",
                )
                license_value = top_level_scalar(frontmatter, "license")
                self.assertIsNotNone(
                    license_value,
                    f"{skill_file}: top-level frontmatter key 'license' missing",
                )
                self.assertEqual(
                    license_value,
                    EXPECTED_LICENSE,
                    f"{skill_file}: license must be {EXPECTED_LICENSE!r}",
                )
                compat_value = top_level_scalar(frontmatter, "compatibility")
                self.assertIsNotNone(
                    compat_value,
                    f"{skill_file}: top-level frontmatter key 'compatibility' missing",
                )
                self.assertIn(
                    EXPECTED_COMPAT_SUBSTR,
                    compat_value,
                    f"{skill_file}: compatibility must mention "
                    f"{EXPECTED_COMPAT_SUBSTR!r}",
                )

    def test_no_frontmatter_metadata_version_block(self):
        for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            with self.subTest(skill=skill_file.parent.name):
                frontmatter = read_frontmatter(
                    skill_file.read_text(encoding="utf-8")
                )
                self.assertIsNotNone(frontmatter, f"{skill_file}: no frontmatter")
                self.assertFalse(
                    metadata_version_present(frontmatter),
                    f"{skill_file}: frontmatter carries a version under a "
                    "'metadata:' block — version is single-sourced in "
                    "templates/release_manifest.json; do not duplicate it",
                )

    def test_descriptions_byte_identical_to_head(self):
        for skill_name in WAVE_P_SKILLS:
            skill_file = SKILLS_DIR / skill_name / "SKILL.md"
            relpath = skill_file.relative_to(ROOT_DIR).as_posix()
            with self.subTest(skill=skill_name):
                working = read_frontmatter(
                    skill_file.read_text(encoding="utf-8")
                )
                self.assertIsNotNone(working, f"{skill_file}: no frontmatter")
                head = read_frontmatter(head_text(relpath))
                self.assertIsNotNone(
                    head, f"HEAD:{relpath}: no frontmatter at HEAD"
                )
                self.assertEqual(
                    description_block(working),
                    description_block(head),
                    f"{relpath}: description entry diverged from git HEAD — "
                    "Wave PF must add packaging keys without touching "
                    "descriptions",
                )


if __name__ == "__main__":
    unittest.main()
