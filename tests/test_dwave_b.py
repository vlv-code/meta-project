#!/usr/bin/env python3
"""Wave D Lane B — Boundary Gate & Scaffold Hygiene (plan 2026-11-15 §5).

RED-first specification (TDD):

- T3.1 Scoped hook override: the boundary gate's STAGED mode honors
  META_PROJECT_ALLOW_RED_ZONE=1 (fail-closed default) and lets Red Zone
  staged files pass with an `[ALLOWED]` notice naming each red file.
  Unmapped (Default Deny) files stay prohibited; `--allow-red-zone` flag
  semantics are unchanged; refusal without the env var is identical to
  the current behavior. The installed pre-commit dispatcher passes the
  env through to the gate.

- T3.2 Drift detector hygiene: architecture-drift classification excludes
  `__pycache__/` directories and `*.pyc` bytecode (consistent with the
  init skill's Zero Unmapped Dirs filter list).

- T3.3 Scaffold .gitignore: the init skill's scaffold steps must document
  a baseline `.gitignore` (append-if-absent, never overwrite) carrying
  `__pycache__/`, `*.pyc`, `*.lock`, with a note mapping the hygiene
  paths Green (lock-in strings against regression).

On the pre-fix codebase the tests marked RED below fail; lock-in tests
already pass and guard adjacent behavior while the fix lands.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_boundaries import (
    DISPATCHER_TEMPLATE,
    check_architecture_drift,
    install_git_hook,
    main as gate_main,
)

CHECK_BOUNDARIES_SCRIPT = REPO_ROOT / "scripts" / "check_boundaries.py"
INIT_SKILL = REPO_ROOT / "skills" / "init-meta-project" / "SKILL.md"

POSIX_SHELL = shutil.which("bash") or shutil.which("sh")

ENV_VAR = "META_PROJECT_ALLOW_RED_ZONE"

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

# Boundaries fixture that explicitly maps bytecode caches Green, so the
# staged-.pyc CLI test isolates the architecture-drift classifier from
# boundary violations.
PYCACHE_GREEN_BOUNDARIES = """# Responsibility Zones and Change Boundaries

## Green Zone (Autonomous Modification)
- `**/__pycache__/**`
- `*.pyc`
- `docs/**` and `*.md` documentation.

## Yellow Zone (Modification with Mandatory Verification)
- `AGENTS.md` root passport.

## Red Zone (Prohibited Without Direct User Confirmation)
- `LICENSE`
- `*boundaries.md`

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any unmapped path is strictly Red Zone by default.
"""


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def _init_repo(path: Path, boundaries: str = MINIMAL_BOUNDARIES) -> Path:
    """Create a tiny committed git repository with a boundaries fixture."""
    path.mkdir(parents=True, exist_ok=True)
    res = _git(path, "init", "-q")
    assert res.returncode == 0, res.stderr
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    pk = path / ".agents" / "project_knowledge"
    pk.mkdir(parents=True, exist_ok=True)
    (pk / "boundaries.md").write_text(boundaries, encoding="utf-8")
    (path / "README.md").write_text("# fixture\n", encoding="utf-8")
    _git(path, "add", "-A")
    res = _git(path, "commit", "-qm", "init")
    assert res.returncode == 0, res.stderr
    return path


def _run_gate(
    cwd: Path, *args: str, env_overrides: dict | None = None
) -> subprocess.CompletedProcess:
    """Run the real gate CLI against cwd with an optional env overlay."""
    env = dict(os.environ)
    env.pop(ENV_VAR, None)  # baseline: env var absent unless overridden
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(CHECK_BOUNDARIES_SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
    )


class TempRootTestCase(unittest.TestCase):
    """Base fixture with automatic temp directory cleanup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dwave_b_")
        self.root = Path(self.temp_dir).resolve()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def sub(self, name: str) -> Path:
        p = self.root / name
        p.mkdir(parents=True, exist_ok=True)
        return p


# ---------------------------------------------------------------------------
# T3.1 — Scoped hook override: META_PROJECT_ALLOW_RED_ZONE (staged mode)
# ---------------------------------------------------------------------------


class TestStagedEnvOverrideContract(TempRootTestCase):
    """Gate contract: staged mode honors the env var, fail-closed default."""

    def setUp(self):
        super().setUp()
        self.repo = _init_repo(self.sub("repo"))

    def _gate(self, *args: str, env_overrides: dict | None = None):
        return _run_gate(self.repo, *args, env_overrides=env_overrides)

    # RED: pre-fix the env var is ignored -> staged Red Zone file refused.
    def test_env_one_allows_staged_red_zone_with_allowed_notice(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._gate("--staged", env_overrides={ENV_VAR: "1"})

        self.assertEqual(
            res.returncode,
            0,
            f"env override must admit staged Red Zone file "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        self.assertIn(
            "[ALLOWED]",
            res.stdout,
            f"admitted Red Zone file must carry an [ALLOWED] notice "
            f"(stdout={res.stdout!r})",
        )

    # RED: pre-fix no notice exists at all.
    def test_allowed_notice_names_each_red_file(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")
        boundaries = (
            self.repo / ".agents" / "project_knowledge" / "boundaries.md"
        )
        boundaries.write_text(
            MINIMAL_BOUNDARIES + "\n- appended line\n", encoding="utf-8"
        )
        _git(self.repo, "add", ".agents/project_knowledge/boundaries.md")

        res = self._gate("--staged", env_overrides={ENV_VAR: "1"})

        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn(
            f"[ALLOWED] LICENSE",
            res.stdout,
            f"[ALLOWED] notice must name LICENSE (stdout={res.stdout!r})",
        )
        self.assertIn(
            "[ALLOWED] .agents/project_knowledge/boundaries.md",
            res.stdout,
            f"[ALLOWED] notice must name each red file "
            f"(stdout={res.stdout!r})",
        )

    # Lock-in: refusal without the env var is identical to current behavior.
    def test_default_refusal_identical_without_env(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._gate("--staged")

        self.assertNotEqual(
            res.returncode,
            0,
            f"Red Zone staged file must be refused without the env var "
            f"(stdout={res.stdout!r})",
        )
        self.assertIn("RED ZONE VIOLATION", res.stderr)
        self.assertIn("LICENSE", res.stderr)
        self.assertNotIn("[ALLOWED]", res.stdout)

    # Lock-in: only the explicit affirmative value "1" enables the override
    # (fail-closed contract; anything else must keep the refusal).
    def test_non_one_values_fail_closed(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        for value in ("0", "true", "yes", "on", ""):
            res = self._gate("--staged", env_overrides={ENV_VAR: value})
            self.assertNotEqual(
                res.returncode,
                0,
                f"{ENV_VAR}={value!r} must NOT admit a Red Zone staged file "
                f"(stdout={res.stdout!r})",
            )

    # Adversarial boundary case: the override is scoped to RED-zone files;
    # Default Deny (unmapped) paths must stay refused even under the env var.
    def test_unmapped_default_deny_stays_refused_under_override(self):
        (self.repo / "external_tool.cfg").write_text("k=v\n", encoding="utf-8")
        _git(self.repo, "add", "external_tool.cfg")

        res = self._gate("--staged", env_overrides={ENV_VAR: "1"})

        self.assertNotEqual(
            res.returncode,
            0,
            f"env override must not admit unmapped Default Deny files "
            f"(stdout={res.stdout!r})",
        )
        self.assertIn("DEFAULT DENY", res.stderr)

    # Scope lock-in: the env var is read in STAGED mode only; the default
    # working-tree mode keeps refusing regardless of the env var.
    def test_env_ignored_outside_staged_mode(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._gate(env_overrides={ENV_VAR: "1"})  # no --staged flag

        self.assertNotEqual(
            res.returncode,
            0,
            f"env override must stay scoped to --staged mode "
            f"(stdout={res.stdout!r})",
        )

    # In-process fast-path: same contract through main() (library entry).
    def test_main_honors_env_one_in_staged_mode(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {ENV_VAR: "1"}):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = gate_main(["--staged", "--repo-root", str(self.repo)])

        self.assertEqual(
            rc, 0, f"main() must honor the env override (err={err.getvalue()!r})"
        )
        self.assertIn("[ALLOWED] LICENSE", out.getvalue())

    def test_main_refuses_without_env_in_staged_mode(self):
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        out, err = io.StringIO(), io.StringIO()
        env = dict(os.environ)
        env.pop(ENV_VAR, None)
        with mock.patch.dict(os.environ, env, clear=True):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = gate_main(["--staged", "--repo-root", str(self.repo)])

        self.assertNotEqual(rc, 0, "refusal must be preserved without env var")
        self.assertNotIn("[ALLOWED]", out.getvalue())


class TestHookDispatcherEnvPassthrough(TempRootTestCase):
    """The installed pre-commit dispatcher must pass the env through."""

    def setUp(self):
        super().setUp()
        self.repo = _init_repo(self.sub("repo"))

    def test_installed_dispatcher_passes_env_through(self):
        # RED: dispatcher template does not mention the env var pre-fix.
        ok, msg = install_git_hook(self.repo)
        assert ok, msg
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        content = hook.read_text(encoding="utf-8")
        self.assertIn(
            ENV_VAR,
            content,
            "installed dispatcher must explicitly pass "
            "META_PROJECT_ALLOW_RED_ZONE through to the gate",
        )
        self.assertIn(
            ENV_VAR,
            DISPATCHER_TEMPLATE,
            "DISPATCHER_TEMPLATE must carry the env pass-through",
        )


class TestHookEndToEndEnvOverride(TempRootTestCase):
    """Full dispatcher path: hook script -> gate, with and without env."""

    def setUp(self):
        super().setUp()
        self.repo = _init_repo(self.sub("repo"))
        # Deploy a working gate script so installed hooks are executable.
        scripts_dir = self.repo / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        shutil.copyfile(CHECK_BOUNDARIES_SCRIPT, scripts_dir / "check_boundaries.py")
        ok, msg = install_git_hook(self.repo)
        assert ok, msg

    def _run_hook(self, env_overrides: dict | None = None):
        env = dict(os.environ)
        env.pop(ENV_VAR, None)
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            [POSIX_SHELL, str(self.repo / ".git" / "hooks" / "pre-commit")],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
            env=env,
        )

    @unittest.skipIf(POSIX_SHELL is None, "no POSIX shell available")
    def test_hook_with_env_one_passes_staged_red_zone(self):
        # RED: pre-fix the hook refuses despite the env var.
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._run_hook(env_overrides={ENV_VAR: "1"})

        self.assertEqual(
            res.returncode,
            0,
            f"hook must admit the staged Red Zone file under "
            f"{ENV_VAR}=1 (stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        self.assertIn(
            "[ALLOWED] LICENSE",
            res.stdout,
            f"hook output must carry the [ALLOWED] notice naming the file "
            f"(stdout={res.stdout!r})",
        )

    @unittest.skipIf(POSIX_SHELL is None, "no POSIX shell available")
    def test_hook_without_env_preserves_refusal(self):
        # Lock-in: without the env var the hook still blocks Red Zone files.
        (self.repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
        _git(self.repo, "add", "LICENSE")

        res = self._run_hook()

        self.assertNotEqual(
            res.returncode,
            0,
            f"hook must refuse the staged Red Zone file by default "
            f"(stdout={res.stdout!r})",
        )


# ---------------------------------------------------------------------------
# T3.2 — Drift detector excludes bytecode caches (__pycache__ / *.pyc)
# ---------------------------------------------------------------------------


class TestDriftDetectorExcludesBytecode(TempRootTestCase):
    """Architecture-drift classifier must treat bytecode caches as noise."""

    # RED: pre-fix scripts/__pycache__/*.pyc is framework code (scripts/
    # prefix) and triggers the drift warning.
    def test_pycache_pyc_not_flagged_as_functional_code(self):
        has_drift, drift_files = check_architecture_drift(
            [
                "scripts/__pycache__/mod.cpython-312.pyc",
                "skills/pkg/__pycache__/util.pyc",
            ]
        )
        self.assertFalse(
            has_drift,
            f"bytecode caches must not trigger architecture drift: {drift_files!r}",
        )
        self.assertEqual(drift_files, [])

    # RED: the whole __pycache__ directory is noise, whatever it contains.
    def test_pycache_dir_contents_not_flagged(self):
        has_drift, drift_files = check_architecture_drift(
            ["scripts/__pycache__/notes.txt"]
        )
        self.assertFalse(
            has_drift,
            f"__pycache__ directory contents must be skipped: {drift_files!r}",
        )

    # RED: *.pyc bytecode is skipped even outside a __pycache__ directory.
    def test_pyc_outside_pycache_not_flagged(self):
        has_drift, drift_files = check_architecture_drift(
            ["scripts/build/output.pyc"]
        )
        self.assertFalse(
            has_drift,
            f"*.pyc bytecode must be skipped: {drift_files!r}",
        )

    # Lock-in: real functional code still flags the drift.
    def test_functional_code_still_flagged(self):
        has_drift, drift_files = check_architecture_drift(
            ["scripts/new_util.py", "skills/new-skill/SKILL.md"]
        )
        self.assertTrue(has_drift, "functional code changes must still flag drift")
        self.assertIn("scripts/new_util.py", drift_files)

    # Lock-in: an architecture.md update still suppresses the warning.
    def test_arch_update_still_suppresses(self):
        has_drift, _ = check_architecture_drift(
            ["scripts/new_util.py", ".agents/project_knowledge/architecture.md"]
        )
        self.assertFalse(has_drift, "architecture update must suppress drift")

    # RED (CLI): staged __pycache__/*.pyc produces no drift warning on the
    # real gate output.
    def test_cli_staged_pycache_no_drift_warning(self):
        repo = _init_repo(self.sub("repo"), boundaries=PYCACHE_GREEN_BOUNDARIES)
        pyc_dir = repo / "scripts" / "__pycache__"
        pyc_dir.mkdir(parents=True, exist_ok=True)
        (pyc_dir / "mod.cpython-312.pyc").write_bytes(b"\x00fake bytecode")
        _git(repo, "add", "scripts/__pycache__/mod.cpython-312.pyc")

        res = _run_gate(repo, "--staged")

        self.assertNotIn(
            "ARCHITECTURE DRIFT",
            res.stdout + res.stderr,
            f"staged __pycache__/*.pyc must not produce a drift warning "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )
        self.assertEqual(
            res.returncode,
            0,
            f"green-mapped bytecode cache must pass the gate "
            f"(stdout={res.stdout!r}, stderr={res.stderr!r})",
        )


# ---------------------------------------------------------------------------
# T3.3 — Scaffold ships baseline .gitignore (append-if-absent, never overwrite)
# ---------------------------------------------------------------------------


class TestInitSkillGitignoreScaffold(unittest.TestCase):
    """Canon lock-in: init skill scaffold steps document the .gitignore."""

    def _scaffold_region(self) -> str:
        text = INIT_SKILL.read_text(encoding="utf-8")
        start_marker = "5. **Create initial knowledge slice drafts and registry:**"
        end_marker = "##### Pass 2:"
        start = text.find(start_marker)
        self.assertGreaterEqual(
            start, 0, "init skill Pass 1 step 5 (scaffold writes) not found"
        )
        end = text.find(end_marker, start)
        self.assertGreater(end, start, "Pass 2 header not found after step 5")
        return text[start:end]

    def test_scaffold_steps_lock_in_gitignore_block(self):
        # RED: pre-fix none of the append-if-absent semantics are documented.
        region = self._scaffold_region().lower()
        for needle in (
            ".gitignore",
            "append-if-absent",
            "never overwrite",
            "__pycache__/",
            "*.pyc",
            "*.lock",
            "green",
            "hygiene",
        ):
            self.assertIn(
                needle,
                region,
                f"init skill scaffold steps must document the baseline "
                f".gitignore semantics: missing {needle!r}",
            )


if __name__ == "__main__":
    unittest.main()
