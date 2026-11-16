#!/usr/bin/env python3
"""Wave F Lane FC — ``scripts/_common.py`` consolidation contract tests.

Plan source: docs/superpowers/plans/2026-11-16-wave-f-security-perimeter.md §6.

The shared Wave E helpers (``_error_envelope`` x7, ``_utc_now_iso`` x1 named +
x3 inline copies) are consolidated into a single source of truth,
``scripts/_common.py``, delivered to subset deployments through the manifest
``requires`` graph (ADR #22). The contract pinned here:

* ``scripts/_common.py`` is a registered manifest component
  (``kind: "script"``, ``requires: []``) — test_dwave_k-style;
* every script that imports ``_common`` carries the manifest
  ``requires: ["scripts/_common.py"]`` edge, so a subset deployment that
  selects the script also selects its helper module; scripts that do NOT
  import it must NOT carry the edge (no phantom edges);
* a grep-based lock: NO script defines its own ``_error_envelope`` /
  ``_utc_now_iso`` anymore — the duplicated copies are GONE;
* the imported helpers are the SAME function objects as ``_common``'s
  (single source of truth, not re-wrapped copies), and the canonical
  envelope / UTC-ISO formats are byte-identical to the pre-consolidation
  behavior (test_ewave_e stays green).

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MANIFEST_PATH = REPO_ROOT / "templates" / "release_manifest.json"
SCRIPTS_DIR = REPO_ROOT / "scripts"
COMMON_RELPATH = "scripts/_common.py"

# A script-level import of the shared helper module (package-style
# ``from scripts._common import ...`` or bare ``from _common import ...``
# inside direct CLI execution). The import sits inside the mirror
# try/except block, hence the leading indentation.
_IMPORT_RE = re.compile(r"^[ \t]*from (?:scripts\.)?_common import ", re.MULTILINE)

# A local (duplicated) helper definition that must no longer exist in any
# script once the consolidation landed.
_DEF_RE = re.compile(r"^def (_error_envelope|_utc_now_iso)\(", re.MULTILINE)

# The scripts that historically carried duplicated copies of the shared
# helpers (Wave E Lane E envelope x7; ``_utc_now_iso`` in the update engine,
# plus the three inline timestamp copies in manage_reports).
EXPECTED_IMPORTERS = frozenset(
    {
        "scripts/check_boundaries.py",
        "scripts/compact_memory.py",
        "scripts/inspect_meta_project.py",
        "scripts/manage_reports.py",
        "scripts/record_obs.py",
        "scripts/update_meta_project.py",
        "scripts/verify_identity.py",
    }
)


def _manifest_components():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest.get("components") or []


def _scan_importers():
    """Scripts that import scripts/_common.py (relative posix paths).
    ``_common.py`` itself is the definition site, not an importer (its
    docstring merely SHOWS the import convention)."""
    importers = set()
    for py in sorted(SCRIPTS_DIR.glob("*.py")):
        if py.name == "_common.py":
            continue
        text = py.read_text(encoding="utf-8")
        if _IMPORT_RE.search(text):
            importers.add(
                str(py.relative_to(REPO_ROOT)).replace("\\", "/")
            )
    return importers


class CommonModuleRegistered(unittest.TestCase):
    """(b) scripts/_common.py is a registered manifest component."""

    @classmethod
    def setUpClass(cls):
        cls.by_path = {
            str(c.get("path", "")): c for c in _manifest_components()
        }

    def test_common_exists_on_disk(self):
        self.assertTrue(
            (REPO_ROOT / COMMON_RELPATH).is_file(),
            f"{COMMON_RELPATH} absent from the repository tree",
        )

    def test_common_is_registered_component(self):
        entry = self.by_path.get(COMMON_RELPATH)
        self.assertIsNotNone(
            entry,
            f"{COMMON_RELPATH} missing from canonical manifest components",
        )
        self.assertEqual(str(entry.get("kind", "")), "script")

    def test_common_has_no_requires(self):
        entry = self.by_path.get(COMMON_RELPATH)
        if entry is None:  # clearer failure via the registration test
            self.fail(f"{COMMON_RELPATH} missing from canonical manifest")
        self.assertEqual(
            list(entry.get("requires") or []),
            [],
            "scripts/_common.py is a leaf helper module and must not "
            "declare requires",
        )


class ManifestRequiresGraphContract(unittest.TestCase):
    """(a) every script importing _common carries the requires edge."""

    @classmethod
    def setUpClass(cls):
        cls.components = _manifest_components()
        cls.by_path = {str(c.get("path", "")): c for c in cls.components}

    def test_common_is_actually_imported(self):
        importers = _scan_importers()
        self.assertTrue(
            importers,
            "no script imports scripts/_common.py — the consolidation "
            "did not happen",
        )
        missing = EXPECTED_IMPORTERS - importers
        self.assertEqual(
            sorted(missing),
            [],
            "expected importers missing the _common import: "
            f"{sorted(missing)}",
        )

    def test_every_importer_has_requires_edge(self):
        importers = _scan_importers()
        self.assertTrue(
            importers,
            "no script imports scripts/_common.py — the consolidation "
            "did not happen",
        )
        for rel in sorted(importers):
            entry = self.by_path.get(rel)
            self.assertIsNotNone(
                entry, f"{rel} imports _common but is not in the manifest"
            )
            requires = list(entry.get("requires") or [])
            self.assertIn(
                COMMON_RELPATH,
                requires,
                f"{rel} imports _common but its manifest requires lacks "
                f"the edge: {requires}",
            )

    def test_non_importing_scripts_have_no_phantom_edge(self):
        importers = _scan_importers()
        phantoms = []
        for path, entry in sorted(self.by_path.items()):
            if str(entry.get("kind", "")) != "script":
                continue
            if path not in importers and COMMON_RELPATH in list(
                entry.get("requires") or []
            ):
                phantoms.append(path)
        self.assertEqual(
            phantoms,
            [],
            "scripts carry a _common requires edge without importing it: "
            f"{phantoms}",
        )


class DuplicationLock(unittest.TestCase):
    """(c) the duplicated helper copies are GONE from every script."""

    def test_no_script_defines_its_own_helpers(self):
        offenders = {}
        for py in sorted(SCRIPTS_DIR.glob("*.py")):
            if py.name == "_common.py":
                continue  # the single sanctioned definition site
            dupes = sorted(set(_DEF_RE.findall(py.read_text(encoding="utf-8"))))
            if dupes:
                offenders[
                    str(py.relative_to(REPO_ROOT)).replace("\\", "/")
                ] = dupes
        self.assertEqual(
            offenders,
            {},
            "scripts still define their own _error_envelope/_utc_now_iso "
            f"copies (single source is {COMMON_RELPATH}): {offenders}",
        )


class SingleSourceWiring(unittest.TestCase):
    """Imported helpers ARE _common's objects (not re-wrapped copies), and
    the canonical formats are byte-identical to the pre-consolidation
    behavior."""

    def test_imported_error_envelope_is_common_object(self):
        import scripts._common as common

        for mod_name in (
            "check_boundaries",
            "compact_memory",
            "inspect_meta_project",
            "manage_reports",
            "record_obs",
            "update_meta_project",
            "verify_identity",
        ):
            mod = __import__(f"scripts.{mod_name}", fromlist=("_error_envelope",))
            self.assertIs(
                getattr(mod, "_error_envelope", None),
                common._error_envelope,
                f"scripts/{mod_name}.py does not use _common._error_envelope",
            )

    def test_error_envelope_format_unchanged(self):
        from scripts._common import _error_envelope

        self.assertEqual(
            _error_envelope("CODE", "file.py", "reason", "exp", "act", "next"),
            "[CODE] file.py: reason | expected: exp | actual: act | next: next",
        )

    def test_utc_now_iso_format_unchanged(self):
        from scripts._common import _utc_now_iso

        value = _utc_now_iso()
        self.assertRegex(value, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


if __name__ == "__main__":
    unittest.main()
