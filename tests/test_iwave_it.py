#!/usr/bin/env python3
"""
Wave IT lock-ins (plan docs/superpowers/plans/2026-11-18-wave-i-audit-response.md, Lane IT).

These are PERMANENT LOCK tests over conditions that hold on the dev branch
today. Their RED-first meaning is prospective: each asserts an invariant that
once regressed must fail loudly, because a real defect walked through exactly
this door before.

T-T1 (audit §6.2): `check_boundaries.py --audit-tree` over THIS repository
    must exit 0 with "Audit passed" and 100% coverage. The sanction-mapping
    bug walked through a door where a boundaries.md bullet was silently
    unmapped (dropped as a command line), leaving a Red Zone-adjacent path
    unaudited; wave P (PD) fixed the mapping — this lock keeps that door
    shut. Skipped on distribution branches where the dogfood policy file
    (.agents/project_knowledge/boundaries.md) is absent by design.

T-T2 (audit §6.5): every maintainer owner declared in .github/CODEOWNERS
    must appear in SANCTION_AUTHORIZED_ACTORS (the gate's authorized
    maintainer set for SHA-bound Red Zone sanctions). Superset is allowed:
    actors may exceed owners, but a CODEOWNERS owner that is NOT sanctioned
    would make review ownership and sanction authority drift apart. Spray
    automation bots (@dependabot etc.) are excluded: they open dependency
    PRs, they never sanction Red Zone changes.

T-T5: ci.yml must declare the pinned pyflakes static-lint step (scripts/ +
    tests/), so the declared opt-in CI dev-tool cannot silently disappear.
"""

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_boundaries import SANCTION_AUTHORIZED_ACTORS

BOUNDARIES_MD = REPO_ROOT / ".agents" / "project_knowledge" / "boundaries.md"
CODEOWNERS = REPO_ROOT / ".github" / "CODEOWNERS"
CI_YML = REPO_ROOT / ".github" / "workflows" / "ci.yml"

# Spray automation identities that may appear in CODEOWNERS without being
# sanction authorities (they never authorize Red Zone changes).
WELL_KNOWN_BOTS = frozenset({
    "@dependabot",
    "@dependabot[bot]",
    "@github-actions",
    "@github-actions[bot]",
})

PYFLAKES_STEP_NAME = "Static lint: pyflakes (scripts/ + tests/)"
# The CONTRACT is "pinned to an exact version, never @latest" — the concrete
# version is a matrix-compatibility detail (4.1.0 requires Python >=3.11 and
# breaks the 3.10 leg; the pin tracks the newest full-matrix release).
PYFLAKES_PIN_PREFIX = "pyflakes=="


class TestBoundaryAuditTreeInvariant(unittest.TestCase):
    """T-T1 §6.2: the framework's own repo keeps 100% boundary coverage."""

    def test_framework_repo_audit_tree_passes_100_percent(self):
        if not BOUNDARIES_MD.is_file():
            self.skipTest(
                ".agents/project_knowledge/boundaries.md absent "
                "(distribution branch): the audit-tree invariant is a "
                "dogfood-branch contract"
            )
        proc = subprocess.run(
            [
                sys.executable, str(REPO_ROOT / "scripts" / "check_boundaries.py"),
                "--boundaries", str(BOUNDARIES_MD),
                "--audit-tree",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        output = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            f"audit-tree must exit 0 on the framework repo itself; got "
            f"rc={proc.returncode}\n{output}",
        )
        self.assertIn("Audit passed", output)
        self.assertIn("100%", output)


class TestCodeownersSanctionSync(unittest.TestCase):
    """T-T2 §6.5: CODEOWNERS owners ⊆ SANCTION_AUTHORIZED_ACTORS."""

    def _parse_owner_names(self) -> set:
        owners = set()
        for line in CODEOWNERS.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue  # comments and blanks carry no ownership
            for token in stripped.split():
                if token.startswith("@") and token not in WELL_KNOWN_BOTS:
                    owners.add(token[1:])  # strip the leading "@"
        return owners

    def test_every_codeowners_owner_is_sanction_authorized(self):
        self.assertTrue(CODEOWNERS.is_file(), ".github/CODEOWNERS must exist")
        owners = self._parse_owner_names()
        self.assertTrue(
            owners, "parsed at least one maintainer owner from CODEOWNERS"
        )
        unsanctioned = owners - set(SANCTION_AUTHORIZED_ACTORS)
        self.assertEqual(
            unsanctioned, set(),
            "CODEOWNERS owners missing from SANCTION_AUTHORIZED_ACTORS "
            f"(superset allowed, subset forbidden): {sorted(unsanctioned)}",
        )


class TestCiPyflakesStepDeclared(unittest.TestCase):
    """T-T5: the pinned pyflakes CI step cannot silently disappear."""

    def test_ci_yml_declares_pinned_pyflakes_step(self):
        self.assertTrue(CI_YML.is_file(), ".github/workflows/ci.yml must exist")
        text = CI_YML.read_text(encoding="utf-8")
        self.assertIn(PYFLAKES_STEP_NAME, text)
        # Exact pin (never @latest) — Default Closed Tooling exception is
        # declared per-version, not per-package. The version itself is a
        # matrix-compatibility detail: only the pin prefix is locked here.
        self.assertIn(PYFLAKES_PIN_PREFIX, text)
        self.assertIn("python -m pyflakes scripts/ tests/", text)


if __name__ == "__main__":
    unittest.main()
