#!/usr/bin/env python3
"""
Wave G, Lane H — Engine hygiene + EOL contract.

Plan: docs/superpowers/plans/2026-11-17-wave-g-context-economy-2.md (§3).

Closes: U4 (dead BaseUnavailableError / _atomic_write_text), U10 (dead
--full flag on check), and the consumer-side CRLF false-drift contract
(a fresh autocrlf checkout smudges LF-installed files to CRLF; the engine
must treat an EOL-only difference as an installed match with a diagnostic,
never as drift or conflict — tamper detection unchanged: an EOL-only flip
is not tampering, and cache-manifest / origin cross-verification stay
byte-exact).

Fixture conventions reuse tests/test_update_meta_project.py builders.
Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_update_meta_project import (  # fixture reuse (same package)
    ACTOR_ID,
    INSTALLATION_ID,
    _git_ok,
    _make_origin_repo,
)

from scripts.update_meta_project import (
    apply_updates,
    check_updates,
    load_bundle,
    plan_updates,
    read_lock,
    resolve_source,
)


def _git_init(path: Path) -> None:
    _git_ok(path, "init", "-q", "-b", "main")
    _git_ok(path, "commit", "-q", "--allow-empty", "-m", "baseline")


def _crlf(data: bytes) -> bytes:
    return data.replace(b"\n", b"\r\n")


class TestCrlfWorkingCopyIsNotDrift(unittest.TestCase):
    """A fresh autocrlf checkout smudges LF-installed files to CRLF; the
    engine must classify that as an installed match (with an explicit
    diagnostic), not as drift/conflict."""

    def _smudged_target(self, tmp: Path) -> Path:
        origin, first_sha = _make_origin_repo(tmp)
        target = tmp / "consumer"
        target.mkdir()
        _git_init(target)
        pin = resolve_source(str(origin), first_sha)
        bundle = load_bundle(pin, None)
        plan = plan_updates(target, bundle, None)
        self.assertEqual(plan["conflicts"], [])
        result = apply_updates(
            target, plan, ACTOR_ID, INSTALLATION_ID, resolved_pin=pin
        )
        self.assertEqual(result["status"], "completed")
        # Simulate the smudge: same content, CRLF endings on disk.
        x_path = target / "scripts" / "x.py"
        x_path.write_bytes(_crlf(x_path.read_bytes()))
        return target, origin, first_sha

    def test_check_reports_eol_normalized_not_drifted(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            target, origin, first_sha = self._smudged_target(tmp)
            result = check_updates(target, str(origin), first_sha, None)
            self.assertEqual(
                result["drifted"],
                [],
                "CRLF-smudged working copy must NOT be classified as drift",
            )
            self.assertEqual(result["status"], "up_to_date")
            eol_entries = [
                d
                for d in result["diagnostics"]
                if d.get("status") == "eol_normalized"
            ]
            self.assertTrue(
                eol_entries,
                "an explicit eol_normalized diagnostic must be emitted",
            )
            self.assertEqual(
                {e["path"] for e in eol_entries}, {"scripts/x.py"}
            )

    def test_plan_fast_forwards_crlf_copy_without_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            target, origin, first_sha = self._smudged_target(tmp)
            pin = resolve_source(str(origin), first_sha)
            bundle = load_bundle(pin, None)
            plan = plan_updates(target, bundle, read_lock(target))
            self.assertEqual(
                plan["conflicts"],
                [],
                "EOL-only difference must not surface as a conflict",
            )
            self.assertEqual(
                [e["path"] for e in plan["needs_base"]],
                [],
                "EOL-only difference must not surface as needs_base",
            )
            updates = [
                a
                for a in plan["actions"]
                if a["path"] == "scripts/x.py" and a.get("op") == "update"
            ]
            self.assertTrue(
                updates,
                "plan re-normalizes the smudged copy to the pinned LF bytes",
            )
            # TOCTOU anchor stays EXACT (raw working-tree bytes):
            self.assertEqual(
                updates[0]["expected_before_sha256"],
                _sha((target / "scripts" / "x.py").read_bytes()),
            )


def _sha(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def _entry_installed_sha(entry: dict) -> str:
    from scripts.update_meta_project import _entry_installed_sha as f

    return f(entry)


class TestDeadSymbolsRemoved(unittest.TestCase):
    """U4 (engine-scoped): BaseUnavailableError is never raised and
    _atomic_write_text is never called in the update engine. The audit's
    finding is scoped to scripts/update_meta_project.py — the same-named
    atomic writer in record_obs.py is that script's own LIVE writer and
    stays. The grep lock keeps the engine clean."""

    def test_engine_module_has_no_dead_symbols(self):
        source = (
            (REPO_ROOT / "scripts" / "update_meta_project.py")
            .read_text(encoding="utf-8")
        )
        self.assertNotIn("BaseUnavailableError", source)
        self.assertNotIn("_atomic_write_text", source)

    def test_base_unavailable_error_gone_from_scripts(self):
        for py in (REPO_ROOT / "scripts").glob("*.py"):
            text = py.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn(
                "BaseUnavailableError",
                text,
                f"{py.name} still references dead symbol BaseUnavailableError",
            )


class TestCheckHasNoDeadFullFlag(unittest.TestCase):
    """U10: the --full flag on check is dead (help admits it) — removed."""

    def test_check_rejects_full_flag(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            origin, first = _make_origin_repo(tmp)
            target = tmp / "consumer"
            target.mkdir()
            _git_init(target)
            proc = _run_cli(
                [
                    "check",
                    "--source",
                    str(origin),
                    "--ref",
                    first,
                    "--repo-root",
                    str(target),
                    "--full",
                ]
            )
            self.assertNotEqual(
                proc.returncode,
                0,
                "--full must no longer be an accepted check flag (rc != 0)",
            )


def _run_cli(args: list[str]):
    import subprocess

    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(REPO_ROOT / "scripts" / "update_meta_project.py"),
            *args,
        ],
        capture_output=True,
        cwd=str(REPO_ROOT),
    )


if __name__ == "__main__":
    unittest.main()
