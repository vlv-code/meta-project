#!/usr/bin/env python3
"""Canonical domain tests for scripts/_common.py and uniform error envelopes.
Consolidated from test_fwave_c.py and test_ewave_e.py.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MANIFEST_PATH = REPO_ROOT / "templates" / "release_manifest.json"
SCRIPTS_DIR = REPO_ROOT / "scripts"
COMMON_RELPATH = "scripts/_common.py"

from scripts.check_boundaries import main as gate_main
from scripts.compact_memory import main as compact_main
from scripts.inspect_meta_project import main as inspect_main
from scripts.manage_reports import main as manage_reports_main
from scripts.record_obs import main as record_obs_main
from scripts.update_meta_project import main as update_main
from scripts.verify_identity import main as identity_main


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
    script_candidates = sorted([*SCRIPTS_DIR.glob("*.py"), *(REPO_ROOT / "hooks").glob("*.py")])
    for py in script_candidates:
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

MINIMAL_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- `docs/**` and `*.md` documentation.

## Yellow Zone (Modification with Mandatory Verification)
- `AGENTS.md` root passport.

## Red Zone (Prohibited Without Direct User Confirmation)
- `LICENSE`
- `*boundaries.md`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""


class TempRootTestCase(unittest.TestCase):
    """Base fixture with automatic temp directory cleanup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ewave_e_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def sub(self, name: str) -> Path:
        p = self.root / name
        p.mkdir(parents=True, exist_ok=True)
        return p


def assert_envelope_leading(testcase, stderr_text, code, file_fragment):
    """The envelope must be the LEADING stderr line in canonical format:
    [CODE] <file>: <reason> | expected: <X> | actual: <Y> | next: <step>"""
    lines = stderr_text.splitlines()
    testcase.assertTrue(lines, "envelope expected on stderr, got nothing")
    leading = lines[0]
    testcase.assertIn(
        f"[{code}]", leading, f"envelope code missing in leading line: {leading!r}"
    )
    testcase.assertIn(
        file_fragment, leading, f"envelope must name the file: {leading!r}"
    )
    testcase.assertIn("expected:", leading, f"'expected:' missing: {leading!r}")
    testcase.assertIn("actual:", leading, f"'actual:' missing: {leading!r}")
    testcase.assertIn("next:", leading, f"'next:' missing: {leading!r}")
    return leading


# ---------------------------------------------------------------------------
# scripts/check_boundaries.py — BOUNDARY_VIOLATION / CONTEXT_UNRESOLVED
# (RED ZONE file: presentation-only envelope; refusal content, rc unchanged)
# ---------------------------------------------------------------------------


class TestBoundaryGateEnvelope(TempRootTestCase):
    """Canonical gate failures carry the envelope as the leading stderr line
    while the full Wave D refusal report and rc semantics stay intact."""

    def test_boundary_violation_envelope_leading_line(self):
        boundaries_path = self.sub("cfg") / "boundaries.md"
        boundaries_path.write_text(MINIMAL_BOUNDARIES, encoding="utf-8")

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = gate_main(["--files", "LICENSE", "--boundaries", str(boundaries_path)])

        self.assertEqual(rc, 1, "Red Zone violation must keep refusal rc=1")
        assert_envelope_leading(self, err.getvalue(), "BOUNDARY_VIOLATION", "LICENSE")
        # Wave D structured refusal content preserved verbatim after the wrap.
        self.assertIn("[FAILURE] BOUNDARY GATE FAILURE", err.getvalue())
        self.assertIn("[!] [RED ZONE VIOLATION] LICENSE", err.getvalue())
        self.assertIn("Total violations: 1", err.getvalue())

    def test_missing_boundaries_file_context_envelope(self):
        absent = self.root / "absent_boundaries.md"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = gate_main(["--files", "LICENSE", "--boundaries", str(absent)])

        self.assertEqual(rc, 1, "missing boundaries.md must keep failure rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "CONTEXT_UNRESOLVED", str(absent)
        )
        # Original diagnostic line preserved after the envelope.
        self.assertIn("boundaries.md file not found", err.getvalue())


# ---------------------------------------------------------------------------
# scripts/verify_identity.py — IDENTITY_UNRESOLVED
# ---------------------------------------------------------------------------


class TestVerifyIdentityEnvelope(TempRootTestCase):
    """Unknown actor resolution refuses with an IDENTITY_UNRESOLVED envelope
    naming the registry, keeping the original [ERROR] line and rc=1."""

    def test_unresolved_actor_envelope(self):
        registry_dir = self.root / ".agents"
        registry_dir.mkdir()
        (registry_dir / "meta-project.json").write_text(
            json.dumps(
                {"schema_version": "1.0", "project_id": "p", "installations": {}}
            ),
            encoding="utf-8",
        )
        unknown_actor = "p::harness-x::inst-x::role-x"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = identity_main(["--repo-root", str(self.root), "--actor", unknown_actor])

        self.assertEqual(rc, 1, "unresolved identity must keep refusal rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "IDENTITY_UNRESOLVED", ".agents/meta-project.json"
        )
        # Wave D structured refusal content preserved.
        self.assertIn("Unresolved identity", err.getvalue())
        self.assertIn(unknown_actor, err.getvalue())


# ---------------------------------------------------------------------------
# scripts/inspect_meta_project.py — CONTEXT_UNRESOLVED (diagnostic notice)
# ---------------------------------------------------------------------------


class TestInspectEnvelope(TempRootTestCase):
    """A healthy installation inspected without runtime context resolves to
    the CONTEXT_UNRESOLVED state: the report (stdout JSON, rc 0) is unchanged
    and the envelope appears on stderr as the leading line."""

    def setUp(self):
        # Dogfood-branch contract: the envelope contract under test is defined
        # against the live meta-project installation schema.
        if not (Path(__file__).resolve().parent.parent / ".agents" / "meta-project.json").is_file():
            self.skipTest(
                "dogfood-branch contract: requires the live meta-project installation"
            )
        super().setUp()

    def test_context_unresolved_state_envelope(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch(
                "sys.argv",
                ["inspect_meta_project.py", "--repo-root", str(REPO_ROOT), "--json"],
            ):
                rc = inspect_main()

        self.assertEqual(rc, 0, "inspection rc semantics must not change")
        report = json.loads(out.getvalue())
        self.assertEqual(report["state"], "CONTEXT_UNRESOLVED")
        assert_envelope_leading(
            self, err.getvalue(), "CONTEXT_UNRESOLVED", ".agents/meta-project.json"
        )


# ---------------------------------------------------------------------------
# scripts/manage_reports.py — INVALID_REPORT
# ---------------------------------------------------------------------------


class TestManageReportsEnvelope(TempRootTestCase):
    """Structurally invalid report verification gains an INVALID_REPORT
    envelope on stderr; the stdout [FAIL] verdict and rc=1 are unchanged."""

    def test_invalid_report_envelope(self):
        bad_report = self.root / "bad_report.json"
        bad_report.write_text(
            json.dumps({"schema_version": "1.0.0", "report_type": "init"}),
            encoding="utf-8",
        )

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch(
                "sys.argv",
                ["manage_reports.py", "verify", "--report", str(bad_report)],
            ):
                rc = manage_reports_main()

        self.assertEqual(rc, 1, "invalid report must keep failure rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "INVALID_REPORT", "bad_report.json"
        )
        # Existing stdout verdict (structured refusal content) preserved.
        self.assertIn("[FAIL] Invalid report", out.getvalue())


# ---------------------------------------------------------------------------
# scripts/record_obs.py — INVALID_CATEGORY
# ---------------------------------------------------------------------------


class TestRecordObsEnvelope(TempRootTestCase):
    """A non-canonical observation category is refused with an
    INVALID_CATEGORY envelope naming the observations file; the original
    validation message and rc=1 are preserved (and nothing is written)."""

    def test_invalid_category_envelope(self):
        obs_file = self.root / "observations.md"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = record_obs_main(
                [
                    "--category", "bogus",
                    "--path", "somewhere",
                    "--issue", "issue text",
                    "--solution", "solution text",
                    "--obs-file", str(obs_file),
                ]
            )

        self.assertEqual(rc, 1, "invalid category must keep failure rc=1")
        assert_envelope_leading(
            self, err.getvalue(), "INVALID_CATEGORY", "observations.md"
        )
        # Original validation message preserved after the envelope.
        self.assertIn("Invalid category 'bogus'", err.getvalue())
        self.assertFalse(obs_file.exists(), "refused record must not write files")


# ---------------------------------------------------------------------------
# scripts/update_meta_project.py — APPLY_REFUSED
# ---------------------------------------------------------------------------


class TestUpdateEngineEnvelope(TempRootTestCase):
    """A plan file that is not a serialized plan is refused at apply with an
    APPLY_REFUSED envelope wrapping the [APPLY-REFUSED] payload; rc=1 and the
    payload content are unchanged."""

    def test_apply_refused_envelope(self):
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps({"not": "a plan"}), encoding="utf-8")

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = update_main(
                [
                    "apply",
                    "--repo-root", str(self.root),
                    "--installation", "inst-main",
                    "--actor", "p::h::i::r",
                    "--plan-file", str(plan_file),
                ]
            )

        self.assertEqual(rc, 1, "apply refusal must keep rc=1")
        assert_envelope_leading(self, err.getvalue(), "APPLY_REFUSED", "plan.json")
        # Wave D structured refusal payload preserved verbatim after the wrap.
        self.assertIn("[APPLY-REFUSED]", err.getvalue())
        self.assertIn("not a serialized update plan", err.getvalue())


# ---------------------------------------------------------------------------
# scripts/compact_memory.py — STALE_INPUT (unreadable input) + `[>]` support
# ---------------------------------------------------------------------------


class TestCompactMemoryEnvelope(TempRootTestCase):
    """An unreadable/corrupt compaction input is refused with a STALE_INPUT
    envelope instead of a traceback; rc stays non-zero (crash path today)."""

    def test_unreadable_input_envelope(self):
        corrupt_obs = self.root / "observations.md"
        corrupt_obs.write_bytes(b"\xff\xfe\x00corrupt-not-utf8")
        absent_tasks = self.root / "absent_tasks.md"
        archive_dir = self.root / "archive"

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = compact_main(
                [
                    "--observations", str(corrupt_obs),
                    "--tasks", str(absent_tasks),
                    "--archive-dir", str(archive_dir),
                ]
            )

        self.assertNotEqual(rc, 0, "unreadable input must fail, not crash silently")
        assert_envelope_leading(
            self, err.getvalue(), "STALE_INPUT", "observations.md"
        )
        self.assertFalse(archive_dir.exists(), "failed compaction must not archive")

if __name__ == '__main__':
    unittest.main()
