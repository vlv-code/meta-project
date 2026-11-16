#!/usr/bin/env python3
"""
Wave F Lane FR — Reports Perimeter Adversarial Test Suite.

ADVERSARIAL-RED-FIRST (plan §1, methodological commitment): every test in
this suite reproduces a confirmed attack or defect against
scripts/manage_reports.py and asserts the REQUIRED post-fix behavior. On
the pre-fix codebase the attack-reproducing tests FAIL (RED baseline).

Tasks covered (plan 2026-11-16-wave-f-security-perimeter.md §4, Lane FR):

- T-R1 SEC-3: `installation_id` and `init_run_id` are validated exactly
  like `run_id` (no "..", no path separators, no directory components) at
  `get_report_dir` and the manage-create read path. Attack: a hostile
  --installation "../../evil" (or a crafted init_run_id) escapes the
  reports directory and materializes directories OUTSIDE the repository.
  Required: refusal with ZERO directories created outside the repo.

- T-R2 M2: `commit_sha` must be a 40-character hex SHA before it is handed
  to the `git show` subprocess in `_recover_registry_baseline` and before
  it is trusted from report data in `verify_declared_registry_delta`.
  Attack: a value starting with "--" (argv injection class, e.g.
  "--upload-pack=..." / "--output=...") reaches git as an OPTION.

- T-R3 M3 fail-closed git state: `get_git_state` returns an explicit
  `git_state_error` on any git subprocess failure (exception or nonzero
  rc; three call sites); staleness treats reports carrying (or facing) a
  git failure as stale/suspect with the STALE_INPUT envelope reason
  "git state unavailable". Attack: a dead/hijacked git silently yields a
  "clean, unknown-commit" state and the report is admitted as fresh.

- T-R4 M4/M5: deterministic latest for same-second runs (chosen design:
  find_latest_report fallback resolves by mtime with name as final
  tiebreak — see find_latest_report docstring) and a race-safe overwrite
  guard in save_report via O_EXCL creation of the final report file.
  Attacks: (a) two same-second runs resolve latest by random UUID name
  order; (b) two writers racing past the exists() check silently clobber
  each other's report (TOCTOU between exists() and replace()).

- T-R5 M6: init/manage report templates gain `input_fingerprints` (valid
  filled examples) and `validate_report` REQUIRES them for completed
  init/manage reports. Backward-compat decision (documented): validation
  is strict for NEW reports (verify CLI, save_report, intake); legacy
  completed reports without fingerprints REMAIN READABLE via the report
  directory resolution path (`_load_valid_report` is legacy-tolerant) so
  staleness/supersession logic can still surface them. Attack: a
  "completed" init report with no fingerprints — freshness of essential
  inputs unverifiable — is accepted as valid and fresh.

- T-R6 M9/M10: `git status --porcelain -z` rename entries ("R old -> new"
  in non-z form; "R  NEW\\0OLD\\0" in -z form) parse to the NEW path in
  `modified_files` (staleness must be able to see renamed essential
  inputs), and `schema_version` is checked against the exact supported
  set {"1.0", "1.1", "1.0.0", "1.1.0"} — not the bare "1.*" major-prefix
  acceptance that lets "1.9.9" through today.

Zero-dependency: Python 3.10+ standard library only.
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts import manage_reports
from scripts.manage_reports import (
    ESSENTIAL_INPUT_PATHS,
    SUPPORTED_SCHEMA_VERSIONS,
    _recover_registry_baseline,
    check_report_staleness,
    collect_input_fingerprints,
    create_init_report,
    create_manage_report,
    find_latest_report,
    get_git_state,
    get_report_dir,
    save_report,
    validate_report,
)

REGISTRY_REL = ".agents/meta-project.json"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )


def _init_git_repo(path: Path) -> Path:
    """Create a tiny committed git repository fixture."""
    path.mkdir(parents=True, exist_ok=True)
    res = _git(path, "init", "-q")
    assert res.returncode == 0, res.stderr
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test Operator")
    return path


def _commit_all(path: Path, message: str = "fixture commit") -> str:
    _git(path, "add", ".")
    res = _git(path, "commit", "-q", "-m", message)
    assert res.returncode == 0, res.stderr
    sha = _git(path, "rev-parse", "HEAD").stdout.strip()
    assert len(sha) == 40, sha
    return sha


def _base_init_report(
    repo: Path, run_id: str, status: str = "completed"
) -> dict:
    """A canonical completed init report for the fixture repo."""
    return create_init_report(
        repo_root=repo,
        installation_id="ag-main",
        harness_id="antigravity",
        actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
        project_id="vlv-code/meta-project",
        status=status,
        scenario={
            "profile": "active_development",
            "collaboration_model": "triad",
            "verification_policy": "strict_independent",
            "unresolved_questions": [],
        },
        run_id=run_id,
    )


class TempDirTestCase(unittest.TestCase):
    """Each test gets a fresh temporary base directory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


# ---------------------------------------------------------------------------
# T-R1 SEC-3 — installation_id / init_run_id path traversal
# ---------------------------------------------------------------------------


class TestTR1UnsafeIdentifiersRefused(TempDirTestCase):
    """SEC-3: identifiers that build report paths must be validated exactly
    like run_id. Attack reproduction: --installation "../../evil" escapes
    the reports directory and creates directories outside the repository."""

    def test_get_report_dir_refuses_traversal_and_separators(self):
        # RED (pre-fix): get_report_dir returns escape paths verbatim.
        for unsafe in ("../../evil", "..", "a/b", "a\\b", "", "../up"):
            with self.assertRaises(
                ValueError,
                msg=f"get_report_dir accepted unsafe installation_id {unsafe!r}",
            ):
                get_report_dir(self.base, unsafe, "init")

    def test_get_report_dir_accepts_normal_ids(self):
        # Lock-in: well-formed identifiers keep working.
        d = get_report_dir(self.base, "ag-main", "init")
        self.assertEqual(
            d, self.base / ".agents" / "reports" / "ag-main" / "init"
        )

    def test_cli_init_create_traversal_refused_zero_dirs_outside_repo(self):
        """Attack: init create with a hostile --installation must be refused
        and must create ZERO directories outside the repo root."""
        repo = self.base / "repo"
        repo.mkdir()
        # Valid scenario payload so the ONLY defect is the hostile
        # installation identifier (the refusal must come from the SEC-3
        # path check, not from earlier schema validation). The scenario
        # file lives INSIDE the repo: everything outside the repo root
        # must stay untouched.
        scenario_file = repo / "scenario.json"
        scenario_file.write_text(
            json.dumps({"profile": "active_development"}),
            encoding="utf-8",
        )
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "init",
            "--action", "create",
            "--repo-root", str(repo),
            "--installation", "../../evil",
            "--harness", "antigravity",
            "--actor", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id", "vlv-code/meta-project",
            "--status", "completed",
            "--scenario-file", str(scenario_file),
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        # 1. Refused (post-fix: save_report raises via validated
        #    get_report_dir -> rc 1 with a refusal message).
        self.assertNotEqual(
            proc.returncode, 0, "hostile --installation must be refused"
        )
        combined = proc.stdout + proc.stderr
        self.assertIn("refused", combined, "refusal must be explicit")
        # 2. ZERO directories created outside the repo (pre-fix:
        #    <base>/evil/init/<run_id>.json materializes).
        self.assertFalse(
            (self.base / "evil").exists(),
            "traversal created directories OUTSIDE the repository root",
        )
        outside = [p.name for p in self.base.iterdir() if p.name != "repo"]
        self.assertEqual(
            outside, [], f"artifacts escaped the repo root: {outside}"
        )
        # 3. Nothing written inside the repo either (refusal precedes mkdir).
        self.assertFalse(
            (repo / ".agents" / "reports").exists(),
            "refused run must not create report directories",
        )

    def test_cli_manage_create_unsafe_init_run_id_refused(self):
        """Attack: a crafted --init-run-id probes/reads outside the init
        report directory; must be refused before any path is built."""
        repo = self.base / "repo"
        repo.mkdir()
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "manage",
            "--action", "create",
            "--repo-root", str(repo),
            "--installation", "ag-main",
            "--harness", "antigravity",
            "--actor", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id", "vlv-code/meta-project",
            "--init-run-id", "../../evil",
            "--status", "completed",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "unsafe init_run_id must be refused")
        self.assertIn("Unsafe", proc.stderr, "refusal must name the unsafe identifier")
        self.assertNotIn("Traceback", proc.stderr, "refusal must be a clean error")

    def test_cli_manage_create_traversal_installation_refused(self):
        """Attack: hostile --installation in manage create probes the init
        report directory outside the repo; must be refused before intake."""
        repo = self.base / "repo"
        repo.mkdir()
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "manage",
            "--action", "create",
            "--repo-root", str(repo),
            "--installation", "../outside-installation",
            "--harness", "antigravity",
            "--actor", "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            "--project-id", "vlv-code/meta-project",
            "--init-run-id", "20261116T000000Z-cafe0001",
            "--status", "completed",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "unsafe installation must be refused")
        self.assertIn("Unsafe", proc.stderr, "refusal must name the unsafe identifier")
        self.assertNotIn("Traceback", proc.stderr, "refusal must be a clean error")
        self.assertFalse(
            (self.base / "outside-installation").exists(),
            "traversal must not create or read targets outside the repo",
        )

    def test_cli_latest_traversal_installation_refused_cleanly(self):
        """latest --installation "../x" must refuse cleanly (no traceback,
        explicit unsafe-identifier error)."""
        repo = self.base / "repo"
        repo.mkdir()
        cli = REPO_ROOT / "scripts" / "manage_reports.py"
        cmd = [
            sys.executable,
            str(cli),
            "latest",
            "--repo-root", str(repo),
            "--installation", "../../evil",
            "--type", "init",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(
            proc.returncode, 2, f"unsafe installation must refuse with rc 2: {proc.stderr}"
        )
        self.assertIn("Unsafe", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr, "refusal must be a clean error")


# ---------------------------------------------------------------------------
# T-R2 M2 — commit_sha 40-hex validation before `git show`
# ---------------------------------------------------------------------------


class _RecordingRunner:
    """subprocess.run stand-in that records argv, then delegates to the
    real implementation (used to prove whether git was invoked)."""

    def __init__(self):
        self.calls = []
        self._real = subprocess.run

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        return self._real(args, **kwargs)


class TestTR2CommitShaInjection(TempDirTestCase):
    """M2: a report-controlled commit_sha reaching `git show` as an argv
    element that starts with "--" is an OPTION to git (argv injection
    class). Required: 40-hex validation BEFORE the subprocess."""

    def _committed_repo(self) -> Path:
        repo = _init_git_repo(self.base / "repo")
        (repo / REGISTRY_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / REGISTRY_REL).write_text(
            json.dumps({"project_id": "vlv-code/meta-project"}), encoding="utf-8"
        )
        _commit_all(repo)
        return repo

    def test_recover_registry_baseline_refuses_option_like_sha_without_git_call(self):
        repo = self._committed_repo()
        runner = _RecordingRunner()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", runner
        ):
            blob, err = _recover_registry_baseline(repo, "--upload-pack=evil")

        self.assertIsNone(blob, "injected commit_sha must not yield a baseline")
        self.assertIn("40", err, f"refusal must require a 40-char hex SHA: {err}")
        self.assertEqual(
            runner.calls,
            [],
            f"git must never be invoked with an option-like commit_sha; saw: {runner.calls}",
        )

    def test_recover_registry_baseline_refuses_short_non_hex_sha(self):
        repo = self._committed_repo()
        blob, err = _recover_registry_baseline(repo, "deadbeef")
        self.assertIsNone(blob)
        self.assertIn("40", err, f"refusal must require a 40-char hex SHA: {err}")

    def test_recover_registry_baseline_accepts_real_sha(self):
        # Lock-in: a genuine 40-hex SHA still recovers the committed blob.
        repo = self._committed_repo()
        sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        blob, err = _recover_registry_baseline(repo, sha)
        self.assertIsNone(err, err)
        self.assertIn("vlv-code/meta-project", blob.decode("utf-8"))

    def _delta_reaching_git_show(self, repo: Path, sha: str) -> dict:
        """A completed init report whose recorded registry fingerprint does
        NOT match the current registry (registry drifted after the report)
        and a valid declared change, so delta verification proceeds to the
        git baseline recovery (git show)."""
        report = _base_init_report(repo, "init-20261116T000000Z-inject01")
        report["git_state"]["commit_sha"] = sha
        fingerprints = collect_input_fingerprints(repo)
        fingerprints[REGISTRY_REL] = "0" * 64  # recorded != current -> delta path
        report["input_fingerprints"] = fingerprints
        return report

    def test_verify_delta_refuses_option_like_report_sha_without_git_call(self):
        repo = self._committed_repo()
        # Drift the registry after the report so the declared-delta path runs.
        (repo / REGISTRY_REL).write_text(
            json.dumps({"project_id": "vlv-code/meta-project", "drifted": True}),
            encoding="utf-8",
        )
        report = self._delta_reaching_git_show(repo, "--output=evil.txt")
        runner = _RecordingRunner()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", runner
        ):
            refusal = manage_reports.verify_declared_registry_delta(
                repo, report, [{"kind": "add_role", "role_id": "r1"}]
            )

        self.assertIsNotNone(refusal, "injected sha must refuse the delta")
        self.assertIn("40", refusal, f"refusal must require a 40-char hex SHA: {refusal}")
        self.assertEqual(
            runner.calls,
            [],
            f"git show must never run with an option-like commit_sha; saw: {runner.calls}",
        )

    def test_verify_delta_refuses_short_report_sha(self):
        repo = self._committed_repo()
        (repo / REGISTRY_REL).write_text(
            json.dumps({"project_id": "vlv-code/meta-project", "drifted": True}),
            encoding="utf-8",
        )
        report = self._delta_reaching_git_show(repo, "deadbeef")
        refusal = manage_reports.verify_declared_registry_delta(
            repo, report, [{"kind": "add_role", "role_id": "r1"}]
        )
        self.assertIsNotNone(refusal)
        self.assertIn("40", refusal, f"refusal must require a 40-char hex SHA: {refusal}")


# ---------------------------------------------------------------------------
# T-R3 M3 — fail-closed git state
# ---------------------------------------------------------------------------


class _FailingGit:
    """subprocess.run stand-in simulating a dead/hijacked git binary."""

    def __init__(self, exc=None, returncode=1):
        self.exc = exc
        self.returncode = returncode

    def __call__(self, args, **kwargs):
        if self.exc is not None:
            raise self.exc
        return subprocess.CompletedProcess(
            args, self.returncode, stdout="", stderr="fatal: simulated git outage"
        )


class TestTR3GitStateFailClosed(TempDirTestCase):
    """M3: a git subprocess failure must produce an explicit
    git_state_error (never a silent clean/unknown state), and staleness
    must refuse to certify such reports as fresh (STALE_INPUT, reason
    'git state unavailable')."""

    def _repo_with_fresh_report(self) -> Path:
        repo = _init_git_repo(self.base / "repo")
        (repo / "AGENTS.md").write_text("# Passport\n", encoding="utf-8")
        _commit_all(repo)
        report = _base_init_report(repo, "init-20261116T010000Z-fresh001")
        save_report(repo, "ag-main", "init", report)
        return repo

    def test_get_git_state_reports_error_on_exception(self):
        repo = self._repo_with_fresh_report()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", _FailingGit(exc=OSError("git dead"))
        ):
            state = get_git_state(repo)
        self.assertTrue(
            state.get("git_state_error"),
            "git failure must surface an explicit git_state_error",
        )
        self.assertFalse(
            state.get("is_clean", True),
            "cleanliness must fail closed when git cannot be consulted",
        )
        self.assertEqual(state.get("commit_sha"), "unknown")

    def test_get_git_state_reports_error_on_nonzero_rc(self):
        repo = self._repo_with_fresh_report()
        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", _FailingGit(returncode=128)
        ):
            state = get_git_state(repo)
        self.assertTrue(state.get("git_state_error"))
        # All three git call sites feed the error state.
        self.assertIn("HEAD", state["git_state_error"])
        self.assertFalse(state.get("is_clean", True))

    def test_get_git_state_clean_when_git_works(self):
        # Lock-in: healthy git produces no error state.
        repo = self._repo_with_fresh_report()
        state = get_git_state(repo)
        self.assertIsNone(state.get("git_state_error"))
        self.assertEqual(len(state["commit_sha"]), 40)

    def test_staleness_refuses_fresh_verdict_when_current_git_fails(self):
        """Attack: dead git at staleness check time must NOT let the report
        pass as fresh."""
        repo = self._repo_with_fresh_report()
        report = _base_init_report(repo, "init-20261116T010000Z-fresh001")
        self.assertFalse(check_report_staleness(repo, report)[0])

        with unittest.mock.patch.object(
            manage_reports.subprocess, "run", _FailingGit(exc=OSError("git dead"))
        ):
            is_stale, details = check_report_staleness(repo, report)

        self.assertTrue(
            is_stale,
            f"report admitted fresh while git state was unavailable: {details!r}",
        )
        self.assertTrue(
            any(
                r.startswith("git state unavailable") for r in details["reasons"]
            ),
            f"reason must be 'git state unavailable': {details['reasons']}",
        )

    def test_staleness_marks_reports_carrying_git_error_as_suspect(self):
        """Attack: a report created during a git outage records the failure;
        it must never be certified fresh."""
        repo = self._repo_with_fresh_report()
        report = _base_init_report(repo, "init-20261116T010000Z-outage01")
        report["git_state"]["commit_sha"] = "unknown"
        report["git_state"]["git_state_error"] = (
            "git rev-parse HEAD failed: simulated outage"
        )
        is_stale, details = check_report_staleness(repo, report)
        self.assertTrue(
            is_stale,
            f"report carrying git_state_error admitted as fresh: {details!r}",
        )
        self.assertTrue(
            any(
                r.startswith("git state unavailable") for r in details["reasons"]
            ),
            f"reason must be 'git state unavailable': {details['reasons']}",
        )

    def test_cli_latest_emits_stale_input_envelope_on_git_error(self):
        repo = self._repo_with_fresh_report()
        # A report created during a git outage (failure recorded).
        report = _base_init_report(repo, "init-20261116T010000Z-outage02")
        report["git_state"]["commit_sha"] = "unknown"
        report["git_state"]["git_state_error"] = "simulated outage"
        save_report(repo, "ag-main", "init", report)

        out, err = __import__("io").StringIO(), __import__("io").StringIO()
        with __import__("contextlib").redirect_stdout(out), \
                __import__("contextlib").redirect_stderr(err):
            with unittest.mock.patch(
                "sys.argv",
                [
                    "manage_reports.py",
                    "latest",
                    "--repo-root", str(repo),
                    "--installation", "ag-main",
                    "--type", "init",
                    "--json",
                ],
            ):
                rc = manage_reports.main()

        self.assertEqual(rc, 0, "envelope is presentation-only; rc unchanged")
        payload = json.loads(out.getvalue())
        self.assertTrue(
            payload.get("is_stale"),
            f"report NOT admitted fresh: {payload}",
        )
        self.assertTrue(
            any(
                r.startswith("git state unavailable")
                for r in payload.get("staleness_reasons", [])
            ),
            f"staleness reason must be 'git state unavailable': {payload}",
        )
        self.assertIn("STALE_INPUT", err.getvalue(), "STALE_INPUT envelope required")
        self.assertIn("git state unavailable", err.getvalue())


# ---------------------------------------------------------------------------
# T-R4 M4/M5 — deterministic latest + O_EXCL overwrite guard
# ---------------------------------------------------------------------------


class TestTR4DeterministicLatestAndExclusiveSave(TempDirTestCase):
    """M4: two same-second runs must resolve 'latest' deterministically by
    creation order (chosen design: fallback resolution by mtime with the
    run_id name as final tiebreak — see find_latest_report). M5: a second
    writer with the same run_id must fail LOUDLY, even when it raced past
    its exists() check before the first writer published."""

    def _same_second_ids(self):
        # Name order (ffff... > aaaa...) deliberately contradicts write order.
        return (
            "init-20261116T120000Z-ffff0001",  # written FIRST, greater name
            "init-20261116T120000Z-aaaa0002",  # written SECOND, smaller name
        )

    def _save(self, repo: Path, run_id: str, marker: str) -> Path:
        report = _base_init_report(repo, run_id)
        report["race_marker"] = marker
        return save_report(repo, "ag-main", "init", report)

    def test_same_second_latest_resolves_by_write_order(self):
        repo = self.base / "repo"
        repo.mkdir()
        first_id, second_id = self._same_second_ids()
        first_file = self._save(repo, first_id, "first")
        second_file = self._save(repo, second_id, "second")

        # Force unambiguous creation-order mtimes (filesystem independence).
        os.utime(first_file, ns=(1_000_000_000, 1_000_000_000))
        os.utime(second_file, ns=(2_000_000_000, 2_000_000_000))

        # Attack surface: the fallback path (no latest.json pointer).
        (repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json").unlink()

        path, data = find_latest_report(repo, "ag-main", "init")
        self.assertIsNotNone(path)
        self.assertEqual(
            data.get("run_id"),
            second_id,
            "same-second latest must resolve to the LAST-WRITTEN run "
            "(mtime with name tiebreak), not the lexicographically "
            "greatest run_id",
        )
        # Determinism: the resolution is stable across repeated calls.
        for _ in range(3):
            path2, data2 = find_latest_report(repo, "ag-main", "init")
            self.assertEqual(path2, path)
            self.assertEqual(data2.get("run_id"), second_id)

    def test_same_second_latest_reverse_mtime_is_deterministic(self):
        repo = self.base / "repo"
        repo.mkdir()
        first_id, second_id = self._same_second_ids()
        first_file = self._save(repo, first_id, "first")
        second_file = self._save(repo, second_id, "second")
        os.utime(first_file, ns=(5_000_000_000, 5_000_000_000))
        os.utime(second_file, ns=(1_000_000_000, 1_000_000_000))
        (repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json").unlink()

        _, data = find_latest_report(repo, "ag-main", "init")
        self.assertEqual(data.get("run_id"), first_id)

    def test_pointer_still_authoritative_over_mtime(self):
        # Lock-in: an intact latest.json pointer wins regardless of mtimes.
        repo = self.base / "repo"
        repo.mkdir()
        first_id, second_id = self._same_second_ids()
        self._save(repo, first_id, "first")
        pointer = (
            repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json"
        )
        second_file = self._save(repo, second_id, "second")
        # Newer mtime on the OLDER run; the pointer still names the newest run.
        os.utime(
            repo / ".agents" / "reports" / "ag-main" / "init" / f"{first_id}.json",
            ns=(9_000_000_000, 9_000_000_000),
        )
        del pointer, second_file
        _, data = find_latest_report(repo, "ag-main", "init")
        self.assertEqual(data.get("run_id"), second_id)

    def test_racing_same_run_id_writer_fails_loudly_content_intact(self):
        """M5 attack: writer B's exists() check races BEFORE writer A's
        publish (simulated deterministically by lying exists()); without an
        atomic reservation B silently clobbers A's report. Required: the
        second writer fails loudly and A's content survives untouched."""
        repo = self.base / "repo"
        repo.mkdir()
        run_id = "init-20261116T130000Z-race0001"
        target = (
            repo / ".agents" / "reports" / "ag-main" / "init" / f"{run_id}.json"
        )
        self._save(repo, run_id, "writer-A")

        real_exists = type(target).exists
        target_resolved = str(target)

        def lying_exists(path_self):
            # Simulate writer B having checked exists() BEFORE A published.
            if str(path_self) == target_resolved:
                return False
            return real_exists(path_self)

        with unittest.mock.patch.object(
            type(target), "exists", lying_exists
        ):
            with self.assertRaises(
                ValueError,
                msg="second same-run_id writer must fail loudly even after "
                "racing past the exists() check",
            ):
                self._save(repo, run_id, "writer-B")

        # Writer A's content is intact — no silent clobber.
        with open(target, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(
            saved.get("race_marker"),
            "writer-A",
            "the racing writer silently overwrote the first writer's report",
        )

    def test_threaded_same_run_id_exactly_one_winner(self):
        """M5 stress: N concurrent writers with the same run_id — exactly
        one wins, the stored content belongs to that single winner, and the
        pointer agrees."""
        repo = self.base / "repo"
        repo.mkdir()
        run_id = "init-20261116T130000Z-thread01"
        results = {}
        errors = {}
        barrier = threading.Barrier(5)

        def writer(idx: int):
            try:
                barrier.wait()
                report = _base_init_report(repo, run_id)
                report["race_marker"] = f"thread-{idx}"
                save_report(repo, "ag-main", "init", report)
                results[idx] = f"thread-{idx}"
            except Exception as exc:  # noqa: BLE001 — losers must raise loudly
                errors[idx] = exc

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(
            len(results), 1, f"exactly one writer must win: {results}"
        )
        self.assertGreaterEqual(
            len(errors), 4, f"losing writers must fail loudly: {errors}"
        )
        target = (
            repo / ".agents" / "reports" / "ag-main" / "init" / f"{run_id}.json"
        )
        with open(target, "r", encoding="utf-8") as f:
            saved = json.load(f)
        winner_marker = next(iter(results.values()))
        self.assertEqual(saved.get("race_marker"), winner_marker)
        with open(
            repo / ".agents" / "reports" / "ag-main" / "init" / "latest.json",
            "r",
            encoding="utf-8",
        ) as f:
            pointer = json.load(f)
        self.assertEqual(pointer.get("run_id"), run_id)


# ---------------------------------------------------------------------------
# T-R5 M6 — input_fingerprints required for completed init/manage reports
# ---------------------------------------------------------------------------


class TestTR5FingerprintsRequired(TempDirTestCase):
    """M6: completed init/manage reports must carry input_fingerprints.
    Contract (documented): STRICT for new reports (validate_report default,
    verify CLI, save_report, intake); legacy completed reports without
    fingerprints remain READABLE via the report directory resolution path
    (_load_valid_report / find_latest_report) for staleness/supersession;
    update/tune are unaffected this lane."""

    def test_completed_init_without_fingerprints_is_invalid(self):
        repo = self.base / "repo"
        repo.mkdir()
        report = _base_init_report(repo, "init-20261116T140000Z-nofps001")
        report.pop("input_fingerprints")
        errors = validate_report(report, expected_type="init")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"completed init report without fingerprints must be INVALID: {errors}",
        )

    def test_completed_manage_without_fingerprints_is_invalid(self):
        repo = self.base / "repo"
        repo.mkdir()
        report = create_manage_report(
            repo_root=repo,
            installation_id="ag-main",
            harness_id="antigravity",
            actor_id="vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
            project_id="vlv-code/meta-project",
            init_run_id="init-20261116T140000Z-nofps001",
            status="completed",
            scenario={"profile": "active_development"},
            roles={"preserved": [], "created": [], "adapted": [], "archived": []},
            bindings={},
        )
        report.pop("input_fingerprints")
        errors = validate_report(report, expected_type="manage")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"completed manage report without fingerprints must be INVALID: {errors}",
        )

    def test_fingerprint_entry_shape_is_enforced(self):
        repo = self.base / "repo"
        repo.mkdir()
        report = _base_init_report(repo, "init-20261116T140000Z-shape01")
        # Missing essential keys.
        report["input_fingerprints"] = {"custom/thing.md": "a" * 64}
        errors = validate_report(report, expected_type="init")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"fingerprints missing essential inputs must be invalid: {errors}",
        )
        # Non-hex / wrong-length values are refused.
        report["input_fingerprints"] = {
            rel: ("z" * 64 if rel == ESSENTIAL_INPUT_PATHS[0] else "b" * 64)
            for rel in ESSENTIAL_INPUT_PATHS
        }
        errors = validate_report(report, expected_type="init")
        self.assertTrue(
            any("input_fingerprints" in e for e in errors),
            f"non-sha256 fingerprint values must be invalid: {errors}",
        )

    def test_noncompleted_reports_without_fingerprints_stay_valid(self):
        """Decision ledger reports (blocked/awaiting) are not 'completed'
        and remain valid without fingerprints."""
        repo = self.base / "repo"
        repo.mkdir()
        for status in ("blocked", "awaiting_decision"):
            report = _base_init_report(repo, f"init-20261116T140000Z-{status[:4]}1", status=status)
            report.pop("input_fingerprints")
            errors = validate_report(report, expected_type="init")
            self.assertEqual(
                errors, [], f"{status} init report must stay valid: {errors}"
            )

    def test_completed_update_and_tune_unaffected(self):
        """Lock-in: the fingerprint requirement does not extend to
        update/tune reports this lane."""
        with open(
            REPO_ROOT / "templates" / "reports" / "update_report.json",
            "r",
            encoding="utf-8",
        ) as f:
            update_report = json.load(f)
        update_report.pop("input_fingerprints")
        self.assertEqual(
            validate_report(update_report, expected_type="update"), []
        )

    def test_cli_verify_rejects_completed_init_without_fingerprints(self):
        """Attack surface: `verify` must answer INVALID_REPORT (envelope,
        rc 1) for a completed init report without fingerprints."""
        repo = self.base / "repo"
        repo.mkdir()
        report = _base_init_report(repo, "init-20261116T140000Z-cliprobe01")
        report.pop("input_fingerprints")
        report_file = repo / "report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        out, err = __import__("io").StringIO(), __import__("io").StringIO()
        with __import__("contextlib").redirect_stdout(out), \
                __import__("contextlib").redirect_stderr(err):
            with unittest.mock.patch(
                "sys.argv",
                [
                    "manage_reports.py",
                    "verify",
                    "--report", str(report_file),
                    "--type", "init",
                    "--json",
                ],
            ):
                rc = manage_reports.main()

        self.assertEqual(
            rc, 1, f"completed init report without fingerprints must fail: {out.getvalue()}"
        )
        self.assertIn("INVALID_REPORT", err.getvalue(), "envelope required")
        payload = json.loads(out.getvalue())
        self.assertFalse(payload.get("valid"))
        self.assertTrue(
            any("input_fingerprints" in e for e in payload.get("errors", []))
        )

    def test_legacy_completed_report_remains_readable(self):
        """Backward-compat (documented decision): a legacy completed report
        without fingerprints is still READABLE via the report directory
        resolution path (find_latest_report), so supersession/staleness
        logic keeps working — it is just not VALID as a new document."""
        repo = self.base / "repo"
        repo.mkdir()
        report_dir = repo / ".agents" / "reports" / "ag-main" / "init"
        report_dir.mkdir(parents=True)
        report = _base_init_report(repo, "init-20261116T140000Z-legacy01")
        report.pop("input_fingerprints")
        legacy_file = report_dir / "init-20261116T140000Z-legacy01.json"
        with open(legacy_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        path, data = find_latest_report(repo, "ag-main", "init")
        self.assertEqual(path, legacy_file)
        self.assertIsNotNone(
            data, "legacy completed report must remain readable (not 'corrupted')"
        )
        self.assertEqual(data.get("run_id"), "init-20261116T140000Z-legacy01")

    def test_templates_carry_valid_input_fingerprints(self):
        """The canonical init/manage templates define the contract: they
        must carry valid, filled input_fingerprints examples and pass the
        strict validator."""
        for name, expected_type in (
            ("init_report.json", "init"),
            ("manage_report.json", "manage"),
        ):
            template_path = REPO_ROOT / "templates" / "reports" / name
            with open(template_path, "r", encoding="utf-8") as f:
                template = json.load(f)
            self.assertIn(
                "input_fingerprints",
                template,
                f"{name} must define input_fingerprints",
            )
            fps = template["input_fingerprints"]
            self.assertIsInstance(fps, dict)
            for rel in ESSENTIAL_INPUT_PATHS:
                self.assertIn(rel, fps, f"{name} must fingerprint {rel}")
                value = fps[rel]
                self.assertIsInstance(value, str)
                self.assertRegex(value, r"^[0-9a-f]{64}$")
            errors = validate_report(template, expected_type=expected_type)
            self.assertEqual(
                errors, [], f"{name} must pass strict validation: {errors}"
            )


# ---------------------------------------------------------------------------
# T-R6 M9/M10 — porcelain rename parsing + schema_version exact set
# ---------------------------------------------------------------------------


class TestTR6RenameParsingAndSchemaExactSet(TempDirTestCase):
    """M9: `git status --porcelain -z` rename entries are 'XY NEW\\0OLD\\0'
    (the non-z form is 'R old -> new'); modified_files must record the NEW
    working-tree path and never the sliced garbage of the ORIG_PATH field.
    M10: schema_version must be an exact member of the supported set."""

    def test_porcelain_rename_parsed_to_new_path(self):
        repo = _init_git_repo(self.base / "repo")
        (repo / "dir").mkdir()
        (repo / "dir" / "oldname.txt").write_text("payload\n", encoding="utf-8")
        _commit_all(repo)
        res = _git(repo, "mv", "dir/oldname.txt", "dir/newname.txt")
        self.assertEqual(res.returncode, 0, res.stderr)

        state = get_git_state(repo)
        self.assertEqual(
            state["modified_files"],
            ["dir/newname.txt"],
            f"rename must parse to the NEW path only, got: {state['modified_files']!r} "
            "(pre-fix bug: the ORIG_PATH field is sliced as 'XY PATH' and lands "
            "in modified_files as garbage)",
        )
        self.assertFalse(state["is_clean"])

    def test_rename_of_essential_input_is_visible_to_staleness(self):
        """A renamed essential input must be detectable: the fingerprint of
        the old path no longer matches (file gone) AND the new path appears
        in modified_files."""
        repo = _init_git_repo(self.base / "repo")
        (repo / "AGENTS.md").write_text("# Passport\n", encoding="utf-8")
        _commit_all(repo)
        report = _base_init_report(repo, "init-20261116T150000Z-renme001")
        self.assertFalse(check_report_staleness(repo, report)[0])

        _git(repo, "mv", "AGENTS.md", "AGENTS.v2.md")
        state = get_git_state(repo)
        self.assertIn("AGENTS.v2.md", state["modified_files"])
        self.assertNotIn("AGENTS.md", state["modified_files"])
        is_stale, details = check_report_staleness(repo, report)
        self.assertTrue(
            is_stale,
            f"renamed essential input must make the report stale: {details!r}",
        )

    def test_schema_version_exact_set_membership(self):
        report_base = {
            "schema_version": "1.0.0",
            "report_type": "init",
            "project_id": "p",
            "installation_id": "ag-main",
            "harness_id": "antigravity",
            "actor_id": "a",
            "run_id": "r",
            "status": "blocked",
            "git_state": {},
            "scenario": {},
            "next_step_readiness": {},
        }

        def with_schema(version: str) -> dict:
            data = dict(report_base)
            data["schema_version"] = version
            return data

        # M10 attack: the old check accepted ANY "1.*" via major-prefix
        # matching, so "1.9.9" sailed through.
        for bad in ("1.9.9", "1", "1.999.0", "0.9", "2.0", "1.2"):
            errors = validate_report(with_schema(bad), expected_type="init")
            self.assertTrue(
                any("schema_version" in e for e in errors),
                f"schema_version {bad!r} must be refused (exact set), got: {errors}",
            )

        for good in ("1.0", "1.1", "1.0.0", "1.1.0"):
            errors = validate_report(with_schema(good), expected_type="init")
            self.assertEqual(
                errors, [], f"schema_version {good!r} must stay valid: {errors}"
            )

    def test_supported_schema_versions_is_exact_enumeration(self):
        self.assertEqual(
            SUPPORTED_SCHEMA_VERSIONS,
            {"1.0", "1.1", "1.0.0", "1.1.0"},
            "SUPPORTED_SCHEMA_VERSIONS must be the exact major.minor "
            "enumeration (plan T-R6), not the legacy {'1.0.0','1.0','1'}",
        )


if __name__ == "__main__":
    unittest.main()
