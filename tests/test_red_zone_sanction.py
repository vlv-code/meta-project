"""
Wave H: SHA-bound Red Zone sanction contract (scripts/check_boundaries.py).

A maintainer-sanctioned Red Zone push is admitted by the gate when ALL of
the following hold (roadmap 7.2.2 item 4, all three requirements):

1. WHO  - the sanction's authorized_by actor is in the gate's authorized
          maintainer set AND the CI push actor matches it (--sanction-actor).
2. WHICH REVISION - the sanction is bound to the exact base revision being
          diffed (--sanction-base-sha must equal sanction.base_sha); a new
          push shifts the base and invalidates the sanction automatically.
3. INVALIDATION - explicit paths (no wildcards): every Red Zone violation
          must be covered by the sanction's paths list.

Without sanction flags the gate keeps its historical fail-closed behavior.
Tampered/malformed/stale sanctions fail closed with SANCTION-REJECTED
diagnostics.
"""

from pathlib import Path
import json
import sys
import tempfile
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import check_boundaries
    from check_boundaries import main
except ImportError:
    check_boundaries = None
    main = None
# Wave H: the authorized-actor set is NEW in this contract; absence = RED.
SANCTION_AUTHORIZED_ACTORS = getattr(check_boundaries, "SANCTION_AUTHORIZED_ACTORS", None)

SAMPLE_BOUNDARIES_MD = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- Creating new tests (`tests/test_unit_*.py`) for auxiliary utilities.
- `docs/**`, `*.md` — technical documentation.
- `src/utils/**` — helper functions.

---

## Yellow Zone (Modification with Mandatory Verification)
- `skills/**` — procedural skills.
- `templates/**` — meta-project templates.
- `src/core/**` — business logic.

---

## Red Zone (Prohibited Without Direct User Confirmation)
- Root project passport `AGENTS.md` (except the root AGENTS.md of this framework repository).
- Database files (`*.db`, `*.sqlite`).
- `secrets/**` — credentials and keys.
- `.github/workflows/ci.yml`.
"""

BASE_SHA = "a" * 40
AUTHORIZED_ACTOR = "vlv-code"
UNAUTHORIZED_ACTOR = "drive-by-contributor"


def _sanction(paths, base_sha=BASE_SHA, actor=AUTHORIZED_ACTOR, kind="red_zone_sanction"):
    return {
        "schema_version": "1.0.0",
        "kind": kind,
        "base_sha": base_sha,
        "authorized_by": actor,
        "paths": paths,
        "reason": "test",
    }


@unittest.skipIf(main is None, "check_boundaries module unavailable")
class TestRedZoneSanctionContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.boundaries = self.root / "boundaries.md"
        self.boundaries.write_text(SAMPLE_BOUNDARIES_MD, encoding="utf-8")
        self.sanction_file = self.root / "red-zone-sanction.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, files, sanction=None, base_sha=BASE_SHA, actor=AUTHORIZED_ACTOR):
        if sanction is not None:
            self.sanction_file.write_text(
                json.dumps(sanction, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        argv = [
            "--boundaries", str(self.boundaries),
            "--files", *files,
            "--sanction-file", str(self.sanction_file),
            "--sanction-base-sha", base_sha,
            "--sanction-actor", actor,
        ]
        return main(argv)

    def _run_no_sanction(self, files):
        return main(
            ["--boundaries", str(self.boundaries), "--files", *files]
        )

    # -- requirement: green path needs no sanction ------------------------

    def test_green_zone_change_still_needs_no_sanction(self):
        self.assertEqual(0, self._run_no_sanction(["docs/readme.md"]))
        self.assertEqual(0, self._run(["docs/readme.md"], _sanction(["docs/readme.md"])))

    # -- historical fail-closed behavior preserved ------------------------

    def test_red_zone_without_sanction_flags_refused(self):
        self.assertEqual(1, self._run_no_sanction([".github/workflows/ci.yml"]))

    # -- happy path: all three requirements satisfied ----------------------

    def test_valid_sanction_admits_red_zone_change(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"]),
        )
        self.assertEqual(0, rc)

    def test_sanction_is_path_explicit_no_wildcards(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/**"]),
        )
        self.assertNotEqual(0, rc)

    # -- requirement 1: WHO ------------------------------------------------

    def test_unauthorized_actor_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], actor=UNAUTHORIZED_ACTOR),
            actor=UNAUTHORIZED_ACTOR,
        )
        self.assertNotEqual(0, rc)

    def test_authorized_set_contains_single_owner(self):
        self.assertIn(AUTHORIZED_ACTOR, SANCTION_AUTHORIZED_ACTORS)
        self.assertNotIn(UNAUTHORIZED_ACTOR, SANCTION_AUTHORIZED_ACTORS)

    def test_actor_mismatch_with_sanction_author_refused(self):
        # Sanction issued by the maintainer, but the push actor differs.
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], actor=AUTHORIZED_ACTOR),
            actor=UNAUTHORIZED_ACTOR,
        )
        self.assertNotEqual(0, rc)

    # -- requirement 2: WHICH REVISION -------------------------------------

    def test_stale_base_sha_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], base_sha="b" * 40),
        )
        self.assertNotEqual(0, rc)

    # -- requirement 3: INVALIDATION / coverage ------------------------------

    def test_uncovered_red_path_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction(["secrets/key.pem"]),
        )
        self.assertNotEqual(0, rc)

    def test_partial_coverage_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml", "secrets/key.pem"],
            _sanction([".github/workflows/ci.yml"]),
        )
        self.assertNotEqual(0, rc)

    # -- tamper resistance ---------------------------------------------------

    def test_malformed_json_refused(self):
        self.sanction_file.write_text("{ not json", encoding="utf-8")
        rc = self._run([".github/workflows/ci.yml"], sanction=None)
        self.assertNotEqual(0, rc)

    def test_wrong_kind_refused(self):
        rc = self._run(
            [".github/workflows/ci.yml"],
            _sanction([".github/workflows/ci.yml"], kind="post_factum_approval"),
        )
        self.assertNotEqual(0, rc)

    def test_missing_sanction_file_refused(self):
        (self.sanction_file).unlink(missing_ok=True)
        rc = self._run([".github/workflows/ci.yml"], sanction=None)
        self.assertNotEqual(0, rc)


if __name__ == "__main__":
    unittest.main()
