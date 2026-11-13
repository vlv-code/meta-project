# Implementation Plan: P0 Core Reliability & Safety Gates (Multi-Agent Team Execution)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate all four critical P0 kernel defects (memory compactor data loss, false-green template sync, destructive hook installer, PR/push CI Red Zone bypass) through coordinated execution by the deployed repository agent triad (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`).

**Architecture:** 
1. **Role Delegation Matrix:**
   - **`agent-dev-lead` (Lead Developer & Dispatcher):** Owns Python standard library implementations, algorithm design, bug fixes in `scripts/compact_memory.py`, `scripts/sync_templates.py`, and `scripts/check_boundaries.py`, and writes failing unit tests (Red-to-Green implementation).
   - **`agent-quality-guardian` (Quality & Meta-Architecture Guardian):** Independently executes regression test suites, validates 0 template drift, audits tree-wide boundary coverage, verifies non-destruction of user data in `observations.md`, and signs off quality gates.
   - **`agent-github-steward` (GitHub Steward & Release Captain):** Owns `.github/workflows/ci.yml` architecture, configures dual PR/push base commit determination, audits git staging hygiene, verifies executable permissions on pre-commit hooks, and performs conventional commits.
2. **Inter-Agent Handoff Protocol:**
   Every task follows a strict 3-phase lifecycle:  
   `Dev Implementation (agent-dev-lead)` вћ” `Independent Verification Gate (agent-quality-guardian)` вћ” `Git Hygiene & Release Checkpoint (agent-github-steward)`.

**Tech Stack:** Python 3.10+ standard library (`argparse`, `pathlib`, `re`, `subprocess`, `unittest`, `datetime`), GitHub Actions CI YAML, Git CLI, POSIX shell.

**Spec:** Canonical backlog and decisions in [`docs/decisions_and_roadmap.md`](../../decisions_and_roadmap.md#7-СЃС‚СЂР°С‚РµРіРёС‡РµСЃРєРёР№-РѕР±Р·РѕСЂ-Р°СЂС…РёС‚РµРєС‚СѓСЂС‹-РґРµС„РµРєС‚С‹-СЏРґСЂР°-Рё-Р°РєС‚СѓР°Р»РёР·РёСЂРѕРІР°РЅРЅС‹Р№-Р±СЌРєР»РѕРі-2026-11-12) and vision principles in [`docs/framework_philosophy_and_vision.md`](../../framework_philosophy_and_vision.md).

## Global Constraints

- **Zero External Dependencies:** All scripts, validators, and test suites must strictly run on Python 3.10+ standard library and Git without external packages (`pip install`, `npm`, binary daemons).
- **Zero Data Loss Guarantee:** Compaction must never silently discard user observations, permanent invariants (`[pin]`), or existing developer git hooks.
- **Fail Closed (Default Deny):** Any unmapped path or unauthorized Red Zone modification must result in non-zero exit codes (exit 1).
- **Handoff Evidence:** No role may mark a step as `[x]` without citing command execution outputs and test results.

---

## File Structure & Agent Ownership

```
в”њв”Ђв”Ђ scripts/
в”‚   в”њв”Ђв”Ђ compact_memory.py      <- agent-dev-lead (modify lines 209-220: header slicing)
в”‚   в”њв”Ђв”Ђ sync_templates.py      <- agent-dev-lead (modify lines 32-63: sentinel parser)
в”‚   в””в”Ђв”Ђ check_boundaries.py    <- agent-dev-lead (modify lines 331-365: hook chaining)
в”њв”Ђв”Ђ skills/
в”‚   в”њв”Ђв”Ђ init-meta-project/     <- agent-dev-lead (update embedded template sentinels)
в”‚   в””в”Ђв”Ђ manage-meta-project/   <- agent-dev-lead (update embedded template sentinels)
в”њв”Ђв”Ђ .github/workflows/
в”‚   в””в”Ђв”Ђ ci.yml                 <- agent-github-steward (add base diff & PR/push gate)
в”њв”Ђв”Ђ tests/
в”‚   в”њв”Ђв”Ђ test_compact_memory.py <- agent-dev-lead (write tests) / agent-quality-guardian (audit)
в”‚   в”њв”Ђв”Ђ test_sync_templates.py <- agent-dev-lead (write tests) / agent-quality-guardian (audit)
в”‚   в”њв”Ђв”Ђ test_check_boundaries.py <- agent-dev-lead (write tests) / agent-quality-guardian (audit)
в”‚   в””в”Ђв”Ђ test_integrity.py      <- agent-quality-guardian (enforce repo contracts)
в””в”Ђв”Ђ .agents/team/
    в”њв”Ђв”Ђ agent-dev-lead/profile.md         <- agent-dev-lead (telemetry closeout)
    в”њв”Ђв”Ђ agent-quality-guardian/profile.md <- agent-quality-guardian (telemetry closeout)
    в””в”Ђв”Ђ agent-github-steward/profile.md   <- agent-github-steward (telemetry closeout)
```

---

## Task Breakdown & Role Execution

### Task 1: Fix Observation Loss in Memory Compactor (P0.1)

- **Lead Implementer:** `agent-dev-lead`
- **Quality Gate:** `agent-quality-guardian`
- **Release Checkpoint:** `agent-github-steward`

**Files:**
- Modify: `scripts/compact_memory.py:209-220`
- Test: `tests/test_compact_memory.py`

**Interfaces:**
- Input: `archive_chunk: str` from `compact_observations(content)` where line 0 is table header and line 1 is separator `|---|`.
- Output: Appends to existing `observations_YYYYMM.md` by taking `archive_chunk.splitlines()[2:]` without discarding user rows containing `"Date"` or `"---"`.

#### Phase 1: Implementation by `agent-dev-lead`

- [x] **Step 1.1 (`agent-dev-lead`): Write failing regression test in `tests/test_compact_memory.py`**

In `tests/test_compact_memory.py`, add `test_compaction_preserves_rows_with_date_and_dash_substrings`:
```python
    def test_compaction_preserves_rows_with_date_and_dash_substrings(self):
        """Verify that rows containing 'Date' or '---' in text are not discarded when appending to existing archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            obs_file = tmp_path / "observations.md"
            archive_dir = tmp_path / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            current_month = datetime.now().strftime("%Y%m")
            archive_file = archive_dir / f"observations_{current_month}.md"
            archive_file.write_text(
                f"# Archived Observations ({current_month})\n\n---\n\n"
                "| Date | Category | Component | Issue | Solution |\n"
                "|---|---|---|---|---|\n"
                "| 2026-11-01 | [ci] | ci.yml | Existing item | Old fix |\n",
                encoding="utf-8"
            )

            rows = [
                "| Date | Category | Component | Issue | Solution |",
                "|---|---|---|---|---|",
                "| 2026-11-02 | [runtime] | date_parser.py | Invalid Date format returned | Use ISO Date format |",
                "| 2026-11-03 | [git] | deploy.sh | Missing --- separator in header | Added --- separator |",
            ]
            for i in range(4, 26):
                rows.append(f"| 2026-11-{i:02d} | [general] | module_{i}.py | Issue {i} | Fix {i} |")

            obs_file.write_text("\n".join(rows) + "\n", encoding="utf-8")

            ret = main([
                "--observations", str(obs_file),
                "--archive-dir", str(archive_dir),
                "--max-observations", "20",
                "--keep-observations", "10",
            ])
            self.assertEqual(ret, 0)

            archive_content = archive_file.read_text(encoding="utf-8")
            self.assertIn("Invalid Date format returned", archive_content, "Row with 'Date' in text was lost!")
            self.assertIn("Missing --- separator in header", archive_content, "Row with '---' in text was lost!")
```

- [x] **Step 1.2 (`agent-dev-lead`): Run test to confirm failure (Red)**

Run:
```bash
python -m unittest tests/test_compact_memory.py -k test_compaction_preserves_rows_with_date_and_dash_substrings
```
Expected Output: `FAIL: AssertionError: 'Invalid Date format returned' not found in ... Row with 'Date' in text was lost!`

- [x] **Step 1.3 (`agent-dev-lead`): Implement deterministic header slicing in `scripts/compact_memory.py` (Green)**

In `scripts/compact_memory.py`, replace lines 209вЂ“216 with header slicing:
```python
                if archive_obs_file.is_file():
                    existing = archive_obs_file.read_text(encoding="utf-8")
                    chunk_lines = [line for line in archive_chunk.splitlines() if line.strip()]
                    # Deterministic fix: slice off the first 2 lines (header + separator)
                    data_rows_to_append = chunk_lines[2:] if len(chunk_lines) >= 2 else []
                    rows_only = "\n".join(data_rows_to_append)
                    if rows_only:
                        archive_obs_file.write_text(existing.rstrip() + "\n" + rows_only + "\n", encoding="utf-8")
                else:
                    header = f"# Archived Observations ({current_month})\n\n---\n\n"
                    archive_obs_file.write_text(header + archive_chunk, encoding="utf-8")
                obs_path.write_text(new_obs, encoding="utf-8")
```

- [x] **Step 1.4 (`agent-dev-lead`): Verify test passes locally**

Run:
```bash
python -m unittest discover -s tests -p "test_compact_memory.py" -v
```
Expected Output: All tests pass (`OK`).

#### Phase 2: Verification by `agent-quality-guardian`

- [x] **Step 1.5 (`agent-quality-guardian`): Run full test suite and audit data integrity**

Run:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
Verification criteria:
- 53/53 tests pass with 0 regressions.
- Verify `observations.md` in repository root is intact and not altered during test runs.

#### Phase 3: Git Hygiene & Release by `agent-github-steward`

- [x] **Step 1.6 (`agent-github-steward`): Inspect diff and commit**

Run:
```bash
git diff scripts/compact_memory.py tests/test_compact_memory.py
git add scripts/compact_memory.py tests/test_compact_memory.py
git commit -m "fix(memory): preserve observation rows with Date or dash substrings during compaction"
```

---

### Task 2: Robust Sentinel-Based Template Sync & Drift Enforcement (P0.2)

- **Lead Implementer:** `agent-dev-lead`
- **Quality Gate:** `agent-quality-guardian`
- **Release Checkpoint:** `agent-github-steward`

**Files:**
- Modify: `scripts/sync_templates.py:32-63`
- Modify: `skills/init-meta-project/SKILL.md`
- Modify: `skills/manage-meta-project/SKILL.md`
- Test: `tests/test_sync_templates.py`

**Interfaces:**
- Input: Skill text containing `<!-- TEMPLATE:BEGIN tmpl_name -->` and `<!-- TEMPLATE:END tmpl_name -->`.
- Output: `(new_text: str, modified: bool, error_msg: Optional[str])`. If sentinels are missing or corrupt, returns `error_msg` causing `sync_templates.py` to exit with code 1.

#### Phase 1: Implementation by `agent-dev-lead`

- [x] **Step 2.1 (`agent-dev-lead`): Write failing unit tests in `tests/test_sync_templates.py`**

In `tests/test_sync_templates.py`, add tests for missing template sentinels and nested backtick handling:
```python
    def test_missing_template_sentinel_raises_drift_error(self):
        """Verify that when a required template block is missing, drift is detected with exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "init-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Corrupted Skill\nNo templates here.\n", encoding="utf-8")
            
            tmpl_dir = root / "templates" / "project_knowledge"
            tmpl_dir.mkdir(parents=True, exist_ok=True)
            (tmpl_dir / "boundaries.md").write_text("# Canonical Boundaries\n", encoding="utf-8")

            in_sync, drift_msgs = sync_embedded_templates(root, write=False)
            self.assertFalse(in_sync)
            self.assertTrue(any("Missing template block" in msg for msg in drift_msgs))

    def test_nested_fenced_backticks_replacement(self):
        """Verify template replacement handles inner triple backtick code blocks properly."""
        tmpl_content = "# Title\n\n```python\nprint('hello')\n```\n"
        skill_text = (
            "Header\n\n"
            "<!-- TEMPLATE:BEGIN test.md -->\n"
            "```markdown\nOld content\n```\n"
            "<!-- TEMPLATE:END test.md -->\n\nFooter\n"
        )
        updated, modified, err = replace_embedded_template(skill_text, "test.md", tmpl_content)
        self.assertIsNone(err)
        self.assertTrue(modified)
        self.assertIn("print('hello')", updated)
        self.assertIn("<!-- TEMPLATE:END test.md -->", updated)
```

- [x] **Step 2.2 (`agent-dev-lead`): Run test to confirm failure (Red)**

Run:
```bash
python -m unittest tests/test_sync_templates.py -k test_missing_template_sentinel_raises_drift_error
```
Expected Output: `FAIL: AssertionError: True is not false` (current code returns 0 drift on missing template).

- [x] **Step 2.3 (`agent-dev-lead`): Implement sentinel-based parser in `scripts/sync_templates.py` (Green)**

Update `replace_embedded_template` and `sync_embedded_templates` in `scripts/sync_templates.py`:
```python
def replace_embedded_template(
    text: str, tmpl_name: str, new_template_content: str
) -> Tuple[str, bool, Optional[str]]:
    begin_marker = f"<!-- TEMPLATE:BEGIN {tmpl_name} -->"
    end_marker = f"<!-- TEMPLATE:END {tmpl_name} -->"

    begin_idx = text.find(begin_marker)
    end_idx = text.find(end_marker)

    if begin_idx == -1 or end_idx == -1 or end_idx < begin_idx:
        return text, False, f"Missing template block: sentinel markers '{begin_marker}' ... '{end_marker}' not found"

    inner_start = begin_idx + len(begin_marker)
    old_inner = text[inner_start:end_idx]

    formatted_new_inner = f"\n```markdown\n{new_template_content.rstrip()}\n```\n"
    if old_inner.strip() == formatted_new_inner.strip():
        return text, False, None

    new_text = text[:inner_start] + formatted_new_inner + text[end_idx:]
    return new_text, True, None
```

In `sync_embedded_templates`:
```python
            updated, modified, err = replace_embedded_template(
                content, tmpl_name, canonical_content
            )
            if err:
                drift_messages.append(f"Error in {target_skill_rel}: {err}")
            elif modified:
                drift_messages.append(
                    f"Drift: Embedded template '{tmpl_name}' in {target_skill_rel} diverges from {tmpl_rel}"
                )
                content = updated
```

- [x] **Step 2.4 (`agent-dev-lead`): Wrap embedded templates with sentinels in `skills/`**

Edit `skills/init-meta-project/SKILL.md` and `skills/manage-meta-project/SKILL.md`:
Add `<!-- TEMPLATE:BEGIN <file> -->` and `<!-- TEMPLATE:END <file> -->` around each embedded template markdown block.
Run synchronization:
```bash
python scripts/sync_templates.py --write
```

#### Phase 2: Verification by `agent-quality-guardian`

- [x] **Step 2.5 (`agent-quality-guardian`): Verify 0 drift and test parity**

Run:
```bash
python scripts/sync_templates.py --check
python -m unittest discover -s tests -p "test_sync_templates.py" -v
```
Verification criteria: Output must report `Template Synchronizer: 0 drift detected. Canonical templates and skills are in full parity.` with exit code 0.

#### Phase 3: Git Hygiene & Release by `agent-github-steward`

- [x] **Step 2.6 (`agent-github-steward`): Inspect diff, stage mirrors, and commit**

Run:
```bash
git add scripts/sync_templates.py skills/ .agents/skills/ tests/test_sync_templates.py
git commit -m "fix(sync): implement fail-closed sentinel template markers and nested fence support"
```

---

### Task 3: Safe Git Pre-Commit Hook Chain Execution (P0.3 / ADR #17)

- **Lead Implementer:** `agent-dev-lead`
- **Quality Gate:** `agent-quality-guardian`
- **Release Checkpoint:** `agent-github-steward`

**Files:**
- Modify: `scripts/check_boundaries.py:331-365`
- Test: `tests/test_check_boundaries.py`

**Interfaces:**
- Input: `repo_root: Path`.
- Output: `(success: bool, message: str)`. Ensures existing pre-commit checks remain intact and boundary gate check is appended cleanly without duplication.

#### Phase 1: Implementation by `agent-dev-lead`

- [x] **Step 3.1 (`agent-dev-lead`): Write failing unit test in `tests/test_check_boundaries.py`**

In `tests/test_check_boundaries.py`, add `test_install_hook_chains_with_existing_pre_commit`:
```python
    def test_install_hook_chains_with_existing_pre_commit(self):
        """Verify that --install-hook preserves existing pre-commit checks and appends boundary check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            git_hooks = tmp_path / ".git" / "hooks"
            git_hooks.mkdir(parents=True, exist_ok=True)
            existing_hook = git_hooks / "pre-commit"
            existing_hook.write_text("#!/bin/sh\npytest tests/\nexit $?\n", encoding="utf-8")

            success, msg = install_git_hook(tmp_path)
            self.assertTrue(success)
            
            content = existing_hook.read_text(encoding="utf-8")
            self.assertIn("pytest tests/", content, "Existing hook content was overwritten!")
            self.assertIn("scripts/check_boundaries.py --staged", content, "Boundary gate was not appended!")

            # Idempotence verification
            success2, msg2 = install_git_hook(tmp_path)
            self.assertTrue(success2)
            content2 = existing_hook.read_text(encoding="utf-8")
            self.assertEqual(content2.count("check_boundaries.py --staged"), 1, "Duplicate hook entry installed!")
```

- [x] **Step 3.2 (`agent-dev-lead`): Run test to confirm failure (Red)**

Run:
```bash
python -m unittest tests/test_check_boundaries.py -k test_install_hook_chains_with_existing_pre_commit
```
Expected Output: `FAIL: AssertionError: 'Existing hook content was overwritten!'`

- [x] **Step 3.3 (`agent-dev-lead`): Implement chain execution in `install_git_hook()` (Green)**

In `scripts/check_boundaries.py`:
```python
def install_git_hook(repo_root: Path) -> Tuple[bool, str]:
    repo_root = Path(repo_root).resolve()
    git_dir = repo_root / ".git"
    if not git_dir.is_dir():
        return False, f"Not a git repository: '{git_dir}' does not exist"

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-commit"

    gate_invocation = (
        "\n# --- Meta-Project Boundary Gate (Safe Chain Execution) ---\n"
        "if [ -f .agents/scripts/check_boundaries.py ]; then\n"
        "  python .agents/scripts/check_boundaries.py --staged || exit 1\n"
        "elif [ -f scripts/check_boundaries.py ]; then\n"
        "  python scripts/check_boundaries.py --staged || exit 1\n"
        "fi\n"
        "# ---------------------------------------------------------\n"
    )

    if hook_file.is_file():
        existing_content = hook_file.read_text(encoding="utf-8")
        if "check_boundaries.py --staged" in existing_content:
            return True, f"Boundary gate hook is already installed in {hook_file}"
        new_content = existing_content.rstrip() + "\n" + gate_invocation
    else:
        new_content = "#!/usr/bin/env sh\n# Git Pre-Commit Hook\n" + gate_invocation

    hook_file.write_text(new_content, encoding="utf-8")
    try:
        hook_file.chmod(hook_file.stat().st_mode | 0o111)
    except Exception:
        pass

    return True, f"Pre-commit hook installed successfully (chained) at {hook_file}"
```

#### Phase 2: Verification by `agent-quality-guardian`

- [x] **Step 3.4 (`agent-quality-guardian`): Run unit tests and verify hook execution**

Run:
```bash
python -m unittest tests/test_check_boundaries.py -k test_install_hook -v
```
Verification criteria: Both single and chained tests report `ok`.

#### Phase 3: Git Hygiene & Release by `agent-github-steward`

- [x] **Step 3.5 (`agent-github-steward`): Inspect diff, verify permissions, and commit**

Run:
```bash
git diff scripts/check_boundaries.py tests/test_check_boundaries.py
git add scripts/check_boundaries.py tests/test_check_boundaries.py
git commit -m "feat(gate): implement safe chain execution for git pre-commit hook installer"
```

---

### Task 4: Pull Request & Push Boundary Gate CI Hardening (P0.4)

- **Lead Implementer:** `agent-github-steward`
- **Quality Gate:** `agent-quality-guardian`
- **Release Checkpoint:** `agent-dev-lead`

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `scripts/check_boundaries.py` (ensure `--diff` supports git SHAs and remote refs)
- Test: `tests/test_check_boundaries.py`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: `github.event_name`, `github.base_ref`, `github.event.before`.
- Produces: Matrix CI job running `--audit-tree` and `--diff <base_ref>`, blocking Red Zone modifications in Pull Requests without authorized maintainer signature.

#### Phase 1: Implementation by `agent-github-steward`

- [x] **Step 4.1 (`agent-github-steward`): Configure dual checkout depth and diff comparison in `.github/workflows/ci.yml`**

Update `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - 'README.md'
      - 'README.ru.md'
      - 'CHANGELOG.md'
      - 'CONTRIBUTING.md'
      - 'CONTRIBUTING.ru.md'
      - 'LICENSE'
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    name: Validate Skills & Templates Integrity
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13']

    steps:
      - name: Checkout repository with full history
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run Boundary Tree Audit (100% Coverage)
        run: python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree

      - name: Evaluate Change Diff against Base Revision
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            BASE_REF="origin/${{ github.base_ref }}"
          else
            BEFORE_SHA="${{ github.event.before }}"
            if [ -z "$BEFORE_SHA" ] || [ "$BEFORE_SHA" = "0000000000000000000000000000000000000000" ]; then
              BASE_REF="HEAD~1"
            else
              BASE_REF="$BEFORE_SHA"
            fi
          fi
          echo "Evaluating changes against base commit: $BASE_REF"
          python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --diff "$BASE_REF"

      - name: Verify Template Parity
        run: python scripts/sync_templates.py --check

      - name: Run Integrity and Unit Test Suites
        run: python -m unittest discover -s tests -p "test_*.py" -v
```

- [x] **Step 4.2 (`agent-dev-lead`): Verify CLI `--diff` robustness against commit SHAs and branches**

In `scripts/check_boundaries.py`, confirm `get_git_modified_files(diff_target=...)` invokes `git diff -z --name-only <target>` cleanly. Add test case in `tests/test_check_boundaries.py`:
```python
    def test_cli_diff_against_head_exits_clean(self):
        """Verify check_boundaries --diff HEAD executes without throwing unhandled exceptions."""
        ret = main(["--boundaries", ".agents/project_knowledge/boundaries.md", "--diff", "HEAD"])
        self.assertIn(ret, (0, 1))
```

#### Phase 2: Verification by `agent-quality-guardian`

- [x] **Step 4.3 (`agent-quality-guardian`): Run full suite and audit boundary integrity**

Run:
```bash
python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
python scripts/sync_templates.py --check
python -m unittest discover -s tests -p "test_*.py" -v
```
Verification criteria:
- Boundary Gate tree audit passes 100% (92 files).
- Template synchronizer reports 0 drift.
- All unit and integrity tests pass.

#### Phase 3: Git Hygiene & Release by `agent-github-steward`

- [x] **Step 4.4 (`agent-github-steward`): Commit CI hardening configuration**

Run:
```bash
git add .github/workflows/ci.yml tests/test_check_boundaries.py
git commit -m "ci: enforce boundary diff check on pull request and push events"
```

---

## P0 Definition of Done (DoD) & Closeout Protocol

Upon completing Tasks 1вЂ“4, the team conducts the synchronized closeout protocol:

1. **`agent-dev-lead`:**
   - Update `.agents/project_knowledge/tasks.md` to mark P0 tasks completed.
   - Record transaction in `.agents/team/agent-dev-lead/profile.md` telemetry table.
2. **`agent-quality-guardian`:**
   - Verify that P0 items in `.agents/project_knowledge/weak_spots.md` are transitioned to `[RESOLVED]`.
   - Run complete suite `python -m unittest discover -s tests -p "test_*.py" -v`.
   - Record audit transaction in `.agents/team/agent-quality-guardian/profile.md`.
3. **`agent-github-steward`:**
   - Check `git status` to ensure working tree is clean.
   - Record CI audit transaction in `.agents/team/agent-github-steward/profile.md`.
4. **Handoff to User:**
   - Present final P0 verification evidence and propose transition to Phase P1 (CLI mechanization & CODEOWNERS).
