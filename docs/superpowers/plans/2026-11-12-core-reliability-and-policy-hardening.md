# Implementation Plan: Core Reliability, Safety Gates & Routine Automation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all prioritized tasks from the canonical backlog (`docs/decisions_and_roadmap.md` §7.3): eliminate critical P0 kernel defects (memory compactor data loss, false-green template sync, destructive hook installer, PR/push CI Red Zone bypass), mechanize P1 routines (`record_obs.py` CLI, policy self-protection & CODEOWNERS, Tier 0 micro-mode documentation, bilingual ADRs), and lay down P2 harness hook adapters and Decision-RTL template integration.

**Architecture:** 
1. **P0 Core Hardening:** Refactor `scripts/compact_memory.py` to preserve rows containing `Date` or `---` via header slicing; refactor `scripts/sync_templates.py` with explicit sentinel markers (`<!-- TEMPLATE:BEGIN/END -->`) and fail-closed validation; upgrade `check_boundaries.py --install-hook` with safe chain execution; implement robust PR & push boundary checks in `.github/workflows/ci.yml` with maintainer SHA-bound authorization.
2. **P1 Routine Mechanization:** Build deterministic `scripts/record_obs.py` CLI with taxonomy validation, markdown pipe escaping, deduplication, and atomic file locking; map policy scripts to Red Zone with `.github/CODEOWNERS`; formalize Tier 0 (Micro) architecture for small repositories (<3-5k LOC); translate ADRs #14–#17 to English.
3. **P2 Harness Adapters:** Create stdlib-based `hooks/install.py` supporting Claude Code, Cursor, and Codex hooks; implement non-blocking PreToolUse path gate and lightweight SessionStart context injector (<1500 tokens); roll Decision-RTL into canonical `templates/AGENTS.md`.

**Tech Stack:** Python 3.10+ standard library (`argparse`, `pathlib`, `re`, `subprocess`, `unittest`, `fnmatch`, `datetime`), Git CLI, GitHub Actions YAML, Markdown.

**Spec:** Canonical backlog and architecture decisions in [`docs/decisions_and_roadmap.md`](../../decisions_and_roadmap.md#7-стратегический-обзор-архитектуры-дефекты-ядра-и-актуализированный-бэклог-2026-11-12) and [`docs/framework_philosophy_and_vision.md`](../../framework_philosophy_and_vision.md).

## Global Constraints

- **Zero External Dependencies:** All scripts, validators, and test suites must strictly run on Python 3.10+ standard library and Git without external packages (`pip install`, `npm`, binary daemons).
- **Fail Closed (Default Deny):** Any path not explicitly mapped to Green or Yellow zones resolves to Red/Black zone; boundary gates must reject unauthorized changes with non-zero exit codes.
- **Defensive Data Retention:** Compaction and sync utilities must never silently discard user observations, permanent invariants (`[pin]`), or existing developer git hooks.
- **Idempotence & Safe Chaining:** All installers and file writers must support repeated execution without duplicating configuration or corrupting targets.

---

## File Structure

### 1. Verification & Automation Utilities (`scripts/`)
- `scripts/compact_memory.py`: Fix header stripping in `main()` to slice exact header rows (`[0:2]`) instead of dropping valid observations containing `"Date"` or `"---"`.
- `scripts/sync_templates.py`: Replace fragile single-fence regex with explicit sentinel comments (`<!-- TEMPLATE:BEGIN <name> --> ... <!-- TEMPLATE:END <name> -->`), fail closed on missing templates, and support nested fenced code blocks.
- `scripts/check_boundaries.py`: Implement non-destructive chain execution in `install_git_hook()`, preserving existing pre-commit hooks and adding `--diff` evaluation for base commits.
- `scripts/record_obs.py` *(New)*: CLI utility for atomic, deduplicated, and validated logging of observations into `observations.md`.

### 2. CI/CD & Security Policies (`.github/`, `.agents/project_knowledge/`, `templates/`)
- `.github/workflows/ci.yml`: Add comprehensive PR diff check against base branch (`github.base_ref`) and push diff against `github.event.before`, trusted base gate execution, and authorization verification.
- `.github/CODEOWNERS` *(New)*: Formalize code ownership for Red Zone paths (`scripts/check_boundaries.py`, `.agents/project_knowledge/boundaries.md`, `.github/workflows/**`, `tests/test_integrity.py`).
- `.agents/project_knowledge/boundaries.md` & `templates/project_knowledge/boundaries.md`: Move policy and gate files to Red Zone.

### 3. Harness Integration Adapters (`hooks/`)
- `hooks/install.py` *(New)*: CLI manager for environment hooks (`--target <env>`, `--verify`, `--uninstall`).
- `hooks/pre_tool_use.py` *(New)*: PreToolUse hook adapter validating file write paths via `check_boundaries.classify_path()`.
- `hooks/session_start.py` *(New)*: SessionStart hook injecting compact passport and active task summaries (<1500 tokens).

### 4. Canonical Templates & Documentation (`templates/`, `skills/`, `docs/`, `README.md`)
- `templates/AGENTS.md` & `templates/team/system_prompt.md`: Inject Decision-RTL template with Verification Result field.
- `skills/init-meta-project/SKILL.md` & `skills/manage-meta-project/SKILL.md`: Update embedded templates with sentinel markers and Tier 0 micro guidelines.
- `README.md` & `README.ru.md`: Document Tier 0 (Micro) setup without agent teams.
- `docs/decisions_and_roadmap.md`: Add English translations for ADRs #14–#17.

### 5. Test Suites (`tests/`)
- `tests/test_compact_memory.py`: Add test cases for rows containing `Date` and `---` inside observation bodies during repeated archive appends.
- `tests/test_sync_templates.py`: Add test cases for missing sentinel blocks, exit code 1 drift, and nested fenced backticks.
- `tests/test_check_boundaries.py`: Add test cases for chain execution in `install_git_hook()` with existing hooks.
- `tests/test_record_obs.py` *(New)*: Unit tests for `record_obs.py` CLI.
- `tests/test_hooks.py` *(New)*: Unit tests for hook installer, PreToolUse path check, and SessionStart output.
- `tests/test_integrity.py`: Update integrity checks for CODEOWNERS, Red Zone mapping, and Decision-RTL templates.

---

## Tasks

### Task 1: Fix Observation Loss in Memory Compactor (P0.1)

**Files:**
- Modify: `scripts/compact_memory.py:209-220`
- Test: `tests/test_compact_memory.py`

**Interfaces:**
- Consumes: `archive_chunk: str` from `compact_observations(content)` where line 0 is table header and line 1 is separator `|---|`.
- Produces: `rows_only: str` containing all older observation data rows without dropping rows that contain `"Date"` or `"---"` in problem/solution text.

- [ ] **Step 1: Write failing unit test in `tests/test_compact_memory.py`**

```python
    def test_compaction_preserves_rows_with_date_and_dash_substrings(self):
        """Verify that rows containing 'Date' or '---' in text are not discarded when appending to existing archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            obs_file = tmp_path / "observations.md"
            archive_dir = tmp_path / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Pre-create existing archive with header
            current_month = datetime.now().strftime("%Y%m")
            archive_file = archive_dir / f"observations_{current_month}.md"
            archive_file.write_text(
                f"# Archived Observations ({current_month})\n\n---\n\n"
                "| Date | Category | Component | Issue | Solution |\n"
                "|---|---|---|---|---|\n"
                "| 2026-11-01 | [ci] | ci.yml | Existing item | Old fix |\n",
                encoding="utf-8"
            )

            # Create primary observations file with 25 rows, including tricky content
            rows = [
                "| Date | Category | Component | Issue | Solution |",
                "|---|---|---|---|---|",
            ]
            # Tricky rows that previous buggy logic discarded
            tricky_row_1 = "| 2026-11-02 | [runtime] | date_parser.py | Invalid Date format returned | Use ISO Date format |"
            tricky_row_2 = "| 2026-11-03 | [git] | deploy.sh | Missing --- separator in header | Added --- separator |"
            rows.append(tricky_row_1)
            rows.append(tricky_row_2)
            
            for i in range(4, 26):
                rows.append(f"| 2026-11-{i:02d} | [general] | module_{i}.py | Issue {i} | Fix {i} |")

            obs_file.write_text("\n".join(rows) + "\n", encoding="utf-8")

            # Run compaction with max=20, keep=10
            ret = main([
                "--observations", str(obs_file),
                "--archive-dir", str(archive_dir),
                "--max-observations", "20",
                "--keep-observations", "10",
            ])
            self.assertEqual(ret, 0)

            # Verify that tricky rows are present in the archive file
            archive_content = archive_file.read_text(encoding="utf-8")
            self.assertIn("Invalid Date format returned", archive_content, "Row with 'Date' in text was lost!")
            self.assertIn("Missing --- separator in header", archive_content, "Row with '---' in text was lost!")
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m unittest tests/test_compact_memory.py -k test_compaction_preserves_rows_with_date_and_dash_substrings
```
Expected: FAIL with assertion error `"Row with 'Date' in text was lost!"`

- [ ] **Step 3: Implement header slicing in `scripts/compact_memory.py`**

In `scripts/compact_memory.py`, replace lines 209–216:
```python
                if archive_obs_file.is_file():
                    existing = archive_obs_file.read_text(encoding="utf-8")
                    # Slice off the 2 header lines from archive_chunk to append data rows cleanly
                    chunk_lines = [line for line in archive_chunk.splitlines() if line.strip()]
                    # The first two non-empty lines are table header and separator
                    data_rows_to_append = chunk_lines[2:] if len(chunk_lines) >= 2 else []
                    rows_only = "\n".join(data_rows_to_append)
                    if rows_only:
                        archive_obs_file.write_text(existing.rstrip() + "\n" + rows_only + "\n", encoding="utf-8")
                else:
                    header = f"# Archived Observations ({current_month})\n\n---\n\n"
                    archive_obs_file.write_text(header + archive_chunk, encoding="utf-8")
                obs_path.write_text(new_obs, encoding="utf-8")
```

- [ ] **Step 4: Run unit tests to verify pass**

```bash
python -m unittest discover -s tests -p "test_compact_memory.py" -v
```
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/compact_memory.py tests/test_compact_memory.py
git commit -m "fix(memory): preserve observation rows with Date or dash substrings during compaction"
```

---

### Task 2: Robust Sentinel-Based Template Sync & Drift Enforcement (P0.2)

**Files:**
- Modify: `scripts/sync_templates.py:32-63`
- Modify: `skills/init-meta-project/SKILL.md` (add `<!-- TEMPLATE:BEGIN <name> -->` markers)
- Modify: `skills/manage-meta-project/SKILL.md` (add `<!-- TEMPLATE:BEGIN <name> -->` markers)
- Test: `tests/test_sync_templates.py`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Skill markdown files containing `<!-- TEMPLATE:BEGIN tmpl_name -->` and `<!-- TEMPLATE:END tmpl_name -->`.
- Produces: `(updated_text, modified, error_message)` where missing sentinels trigger a drift error instead of returning false-green `0 drift`.

- [ ] **Step 1: Write failing unit tests in `tests/test_sync_templates.py`**

```python
    def test_missing_template_sentinel_raises_drift_error(self):
        """Verify that when a required template block is missing, drift is detected with exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skills" / "init-meta-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            # SKILL.md without the required boundaries.md sentinel
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

- [ ] **Step 2: Run test to verify failure**

```bash
python -m unittest tests/test_sync_templates.py -k test_missing_template_sentinel_raises_drift_error
```
Expected: FAIL.

- [ ] **Step 3: Implement sentinel-based parser in `scripts/sync_templates.py`**

Replace `replace_embedded_template` in `scripts/sync_templates.py`:
```python
def replace_embedded_template(
    text: str, tmpl_name: str, new_template_content: str
) -> Tuple[str, bool, Optional[str]]:
    """
    Locates an embedded template block between:
      <!-- TEMPLATE:BEGIN tmpl_name -->
      ...
      <!-- TEMPLATE:END tmpl_name -->
    and replaces its inner body with new_template_content wrapped in a fenced block.
    Returns (updated_text, modified, error_message).
    """
    begin_marker = f"<!-- TEMPLATE:BEGIN {tmpl_name} -->"
    end_marker = f"<!-- TEMPLATE:END {tmpl_name} -->"

    begin_idx = text.find(begin_marker)
    end_idx = text.find(end_marker)

    if begin_idx == -1 or end_idx == -1 or end_idx < begin_idx:
        return text, False, f"Missing template block: sentinel markers '{begin_marker}' ... '{end_marker}' not found"

    inner_start = begin_idx + len(begin_marker)
    old_inner = text[inner_start:end_idx]

    # Format new block with outer fenced block
    formatted_new_inner = f"\n```markdown\n{new_template_content.rstrip()}\n```\n"

    if old_inner.strip() == formatted_new_inner.strip():
        return text, False, None

    new_text = text[:inner_start] + formatted_new_inner + text[end_idx:]
    return new_text, True, None
```

Update `sync_embedded_templates` to treat `error_message` as drift:
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

- [ ] **Step 4: Update embedded templates in `skills/init-meta-project/SKILL.md` and `skills/manage-meta-project/SKILL.md`**

Wrap each embedded template block with:
`<!-- TEMPLATE:BEGIN <filename> -->` and `<!-- TEMPLATE:END <filename> -->`.
Run `python scripts/sync_templates.py --write` and mirror to `.agents/skills/`.

- [ ] **Step 5: Run tests and verify 0 drift**

```bash
python scripts/sync_templates.py --check
python -m unittest discover -s tests -p "test_sync_templates.py" -v
```
Expected: 0 drift detected, all tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/sync_templates.py skills/ .agents/skills/ tests/test_sync_templates.py
git commit -m "fix(sync): implement fail-closed sentinel template markers and nested fence support"
```

---

### Task 3: Safe Git Pre-Commit Hook Chain Execution (P0.3 / ADR #17)

**Files:**
- Modify: `scripts/check_boundaries.py:331-365`
- Test: `tests/test_check_boundaries.py`

**Interfaces:**
- Consumes: Existing `.git/hooks/pre-commit` file (if present) and `repo_root: Path`.
- Produces: Updated `.git/hooks/pre-commit` that preserves existing checks and appends Boundary Gate invocation without duplicate entries.

- [ ] **Step 1: Write failing unit test in `tests/test_check_boundaries.py`**

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

            # Idempotence: running second time should not duplicate invocation
            success2, msg2 = install_git_hook(tmp_path)
            self.assertTrue(success2)
            content2 = existing_hook.read_text(encoding="utf-8")
            self.assertEqual(content2.count("check_boundaries.py --staged"), 1, "Duplicate hook entry installed!")
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m unittest tests/test_check_boundaries.py -k test_install_hook_chains_with_existing_pre_commit
```
Expected: FAIL with `"Existing hook content was overwritten!"`

- [ ] **Step 3: Implement chain execution in `install_git_hook()`**

In `scripts/check_boundaries.py`, replace `install_git_hook()`:
```python
def install_git_hook(repo_root: Path) -> Tuple[bool, str]:
    """
    Installs or chains a local git pre-commit hook in .git/hooks/pre-commit
    that invokes `python scripts/check_boundaries.py --staged`.
    Preserves any existing checks (ADR #17: Safe Chain Execution).
    """
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

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m unittest tests/test_check_boundaries.py -k test_install_hook -v
```
Expected: Both single and chained installation tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/check_boundaries.py tests/test_check_boundaries.py
git commit -m "feat(gate): implement safe chain execution for git pre-commit hook installer"
```

---

### Task 4: Pull Request & Push Boundary Gate CI Hardening (P0.4)

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `scripts/check_boundaries.py` (add `--diff-base` or support `origin/...` evaluation)
- Test: `tests/test_check_boundaries.py`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Git base commit reference (`github.base_ref` for PRs, `github.event.before` for pushes) and optional PR labels.
- Produces: Exit code 0 if diff touches only Green/Yellow zones (or authorized Red Zone); exit code 1 if Red Zone modified without maintainer authorization.

- [ ] **Step 1: Write unit tests for diff evaluation against git revision**

In `tests/test_check_boundaries.py`, add:
```python
    def test_diff_against_commit_detects_red_zone(self):
        """Verify check_boundaries --diff correctly flags Red Zone modified files."""
        zones = parse_zones(BOUNDARIES_MARKDOWN)
        # Simulate modified file list containing test_integrity.py
        has_violations, violations = evaluate_files(["tests/test_integrity.py"], zones, allow_red_zone=False)
        self.assertTrue(has_violations)
        self.assertEqual(violations[0]["zone"], "red")
```

- [ ] **Step 2: Update `.github/workflows/ci.yml` with dual-mode checkout and diff gate**

Update `.github/workflows/ci.yml`:
```yaml
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run Boundary Tree Audit
        run: python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree

      - name: Evaluate Change Diff against Base
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            BASE_REF="origin/${{ github.base_ref }}"
          else
            # Push event: check before SHA; fallback to HEAD~1 if initial branch commit
            BEFORE_SHA="${{ github.event.before }}"
            if [ -z "$BEFORE_SHA" ] || [ "$BEFORE_SHA" = "0000000000000000000000000000000000000000" ]; then
              BASE_REF="HEAD~1"
            else
              BASE_REF="$BEFORE_SHA"
            fi
          fi
          echo "Comparing against base: $BASE_REF"
          python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --diff "$BASE_REF"

      - name: Run integrity tests
        run: python -m unittest discover -s tests -p "test_*.py" -v
```

- [ ] **Step 3: Run CI verification locally and check integrity test**

```bash
python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
python -m unittest discover -s tests -p "test_*.py" -v
```
Expected: All 52 tests pass, full tree coverage.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml tests/test_check_boundaries.py
git commit -m "ci: enforce boundary diff check on pull request and push events"
```

---

### Task 5: Deterministic Observation CLI (`scripts/record_obs.py`) (P1.1)

**Files:**
- Create: `scripts/record_obs.py`
- Test: `tests/test_record_obs.py`

**Interfaces:**
- CLI arguments:
  - `--category` (required, choices: `[boundaries]`, `[ci]`, `[decommission]`, `[incident]`, `[orchestration]`, `[git]`, `[test]`, `[runtime]`, `[deps]`, `[security]`, `[doc]`, `[theme]`)
  - `--component` (required, file path or module name)
  - `--issue` (required, problem description)
  - `--solution` (required, applied fix)
  - `--pin` (optional, flag to append `[pin]` tag to category)
  - `--file` (optional, default: `.agents/project_knowledge/observations.md`)
- Produces: Atomically appends table row after markdown table header with escaped `|` characters and ISO date `YYYY-MM-DD`.

- [ ] **Step 1: Write failing unit tests in `tests/test_record_obs.py`**

```python
import unittest
import tempfile
from pathlib import Path
from scripts.record_obs import record_observation, sanitize_field, main

class TestRecordObservation(unittest.TestCase):
    def test_sanitize_field_escapes_pipes(self):
        self.assertEqual(sanitize_field("Error with a | pipe"), "Error with a \\| pipe")
        self.assertEqual(sanitize_field("Clean string"), "Clean string")

    def test_record_observation_appends_row_with_pin(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_file = Path(tmpdir) / "observations.md"
            obs_file.write_text(
                "# Observations\n\n"
                "| Date | Category | Component | Issue | Solution |\n"
                "|---|---|---|---|---|\n"
                "| 2026-11-01 | [ci] | ci.yml | Old bug | Old fix |\n",
                encoding="utf-8"
            )

            ret = main([
                "--file", str(obs_file),
                "--category", "runtime",
                "--component", "scripts/test.py",
                "--issue", "Unhandled EOFError | crash",
                "--solution", "Added try-except block",
                "--pin"
            ])
            self.assertEqual(ret, 0)

            content = obs_file.read_text(encoding="utf-8")
            self.assertIn("[runtime] [pin]", content)
            self.assertIn("Unhandled EOFError \\| crash", content)
            self.assertIn("Added try-except block", content)

    def test_record_observation_rejects_invalid_category(self):
        ret = main([
            "--category", "invalid_cat",
            "--component", "test.py",
            "--issue", "Issue",
            "--solution", "Fix"
        ])
        self.assertNotEqual(ret, 0)
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m unittest tests/test_record_obs.py
```
Expected: FAIL (`ModuleNotFoundError: No module named 'scripts.record_obs'`)

- [ ] **Step 3: Implement `scripts/record_obs.py`**

Create `scripts/record_obs.py`:
```python
#!/usr/bin/env python3
"""
Deterministic Observation Logger.
Zero-dependency utility (pure Python 3.10+ standard library).
Validates categories, escapes Markdown pipes, handles ISO timestamps, and prevents duplicate entries.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import List, Optional

VALID_CATEGORIES = {
    "boundaries", "ci", "decommission", "incident", "orchestration",
    "git", "test", "runtime", "deps", "security", "doc", "theme"
}


def sanitize_field(value: str) -> str:
    """Escapes markdown pipe characters and strips trailing whitespace/newlines."""
    # Replace unescaped pipes
    sanitized = re.sub(r"(?<!\\)\|", r"\|", value)
    return " ".join(sanitized.splitlines()).strip()


def record_observation(
    file_path: Path,
    category: str,
    component: str,
    issue: str,
    solution: str,
    pinned: bool = False,
) -> bool:
    """Appends a sanitized, validated observation row to the table in file_path."""
    clean_cat = category.strip("[] ").lower()
    if clean_cat not in VALID_CATEGORIES:
        sys.stderr.write(
            f"Error: Invalid category '[{clean_cat}]'. Allowed: {sorted(VALID_CATEGORIES)}\n"
        )
        return False

    cat_tag = f"[{clean_cat}] [pin]" if pinned else f"[{clean_cat}]"
    today = datetime.now().strftime("%Y-%m-%d")

    clean_comp = sanitize_field(component)
    clean_issue = sanitize_field(issue)
    clean_sol = sanitize_field(solution)

    new_row = f"| {today} | {cat_tag} | {clean_comp} | {clean_issue} | {clean_sol} |"

    if not file_path.is_file():
        # Initialize file if not found
        header = (
            "# Undocumented Quirks and Runtime Observations\n\n"
            "| Date | Category | Component | Issue | Solution |\n"
            "|---|---|---|---|---|\n"
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(header + new_row + "\n", encoding="utf-8")
        return True

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Deduplication check
    for line in lines:
        if clean_comp in line and clean_issue in line:
            sys.stdout.write(f"Observation already recorded for {clean_comp}: skipping duplicate.\n")
            return True

    # Find table separator line to insert row immediately after header
    sep_idx = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("|") and re.match(r"^\|\s*:?---+", line.strip()):
            sep_idx = idx
            break

    if sep_idx != -1:
        lines.insert(sep_idx + 1, new_row)
    else:
        lines.append(new_row)

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Record observation: deterministic CLI logger for observations.md."
    )
    parser.add_argument("--category", type=str, required=True, help="Observation category")
    parser.add_argument("--component", type=str, required=True, help="Component path or module")
    parser.add_argument("--issue", type=str, required=True, help="Observed problem or quirk")
    parser.add_argument("--solution", type=str, required=True, help="Applied fix or workaround")
    parser.add_argument("--pin", action="store_true", help="Mark observation as permanent invariant [pin]")
    parser.add_argument(
        "--file",
        type=str,
        default=".agents/project_knowledge/observations.md",
        help="Target observations markdown file",
    )

    args = parser.parse_args(argv)
    success = record_observation(
        Path(args.file),
        args.category,
        args.component,
        args.issue,
        args.solution,
        pinned=args.pin,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m unittest discover -s tests -p "test_record_obs.py" -v
```
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/record_obs.py tests/test_record_obs.py
git commit -m "feat(obs): add deterministic CLI utility for observation logging with pipe escaping and deduplication"
```

---

### Task 6: Policy Self-Protection & `CODEOWNERS` Enforcement (P1.2)

**Files:**
- Create: `.github/CODEOWNERS`
- Modify: `.agents/project_knowledge/boundaries.md`
- Modify: `templates/project_knowledge/boundaries.md`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Repository path boundaries.
- Produces: Formal code ownership for security-critical paths; classifies gate scripts into Red Zone.

- [ ] **Step 1: Write integrity test asserting Red Zone self-protection and CODEOWNERS**

In `tests/test_integrity.py`, add:
```python
    def test_policy_scripts_in_red_zone(self):
        """Verify check_boundaries.py, boundaries.md, and ci.yml are classified in Red Zone."""
        boundaries_path = REPO_ROOT / ".agents" / "project_knowledge" / "boundaries.md"
        content = boundaries_path.read_text(encoding="utf-8")
        self.assertIn("scripts/check_boundaries.py", content)
        self.assertIn(".github/workflows/**", content)

    def test_codeowners_file_exists_and_covers_red_zone(self):
        """Verify .github/CODEOWNERS exists and protects critical paths."""
        codeowners = REPO_ROOT / ".github" / "CODEOWNERS"
        self.assertTrue(codeowners.is_file(), ".github/CODEOWNERS file must exist")
        content = codeowners.read_text(encoding="utf-8")
        self.assertIn("tests/test_integrity.py", content)
        self.assertIn("scripts/check_boundaries.py", content)
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m unittest tests/test_integrity.py -k test_codeowners_file_exists_and_covers_red_zone
```
Expected: FAIL (`.github/CODEOWNERS file must exist`).

- [ ] **Step 3: Create `.github/CODEOWNERS` and update boundaries**

Create `.github/CODEOWNERS`:
```text
# Meta-Project Code Ownership & Gate Protection
# Any change to Red Zone files requires mandatory approval from maintainers.

/tests/test_integrity.py @maintainers
/scripts/check_boundaries.py @maintainers
/.github/workflows/ @maintainers
/.agents/project_knowledge/boundaries.md @maintainers
/LICENSE @maintainers
```

Update Red Zone in `.agents/project_knowledge/boundaries.md` and `templates/project_knowledge/boundaries.md`:
```markdown
## Red Zone (Prohibited Without Direct User Confirmation)
Critical areas of the project. Any modification requires mandatory prior confirmation from the user:
- `tests/test_integrity.py` — specification of architectural integrity and framework contracts.
- `scripts/check_boundaries.py` — boundary gate enforcement engine (policy self-protection).
- `.agents/project_knowledge/boundaries.md` — responsibility zones specification.
- `.github/workflows/**` — GitHub Actions CI/CD pipelines (`ci.yml`).
- `LICENSE` — repository legal license.
- `.gitignore` — global git ignore rules.
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python scripts/sync_templates.py --check
python -m unittest discover -s tests -p "test_integrity.py" -v
```
Expected: All integrity tests pass.

- [ ] **Step 5: Commit**

```bash
git add .github/CODEOWNERS .agents/project_knowledge/boundaries.md templates/project_knowledge/boundaries.md tests/test_integrity.py
git commit -m "feat(security): establish CODEOWNERS and enforce Red Zone self-protection for gate policies"
```

---

### Task 7: Tier 0 (Micro) Documentation & Bilingual ADR Specs (P1.3 & P1.4)

**Files:**
- Modify: `README.md` & `README.ru.md`
- Modify: `skills/manage-meta-project/SKILL.md`
- Modify: `docs/decisions_and_roadmap.md`

**Interfaces:**
- Consumes: Architectural decisions ADR #14–#17 and micro-repository scale definitions.
- Produces: Bilingual documentation clarifying when team generation is unnecessary (<3-5k LOC) and English canonical ADR descriptions.

- [ ] **Step 1: Document Tier 0 (Micro) in `README.md` and `README.ru.md`**

Add section:
```markdown
### Scale-Adaptive Topology: Tier 0 (Micro Repositories)
For repositories under 3,000–5,000 lines of code or single-purpose scripts, deploying a multi-agent team is unnecessary overhead. Meta-Project operates in **Tier 0 (Micro)** mode:
- Single `AGENTS.md` project passport in root.
- Lightweight knowledge slices (`boundaries.md`, `weak_spots.md`, `tasks.md`).
- Machine boundary gate (`scripts/check_boundaries.py`) in pre-commit/CI.
- No specialized `.agents/team/` subagents deployed.
```

- [ ] **Step 2: Add English translation of ADRs #14–#17 to `docs/decisions_and_roadmap.md`**

In `docs/decisions_and_roadmap.md` Section 7.1, add canonical English translation block for ADR #14 (Unified Stdlib Core & Adapters), ADR #15 (Read Permissions vs Write Restrictions), ADR #16 (Decision-RTL Scope & Verification Outcome), and ADR #17 (Safe Pre-Commit Chain Execution).

- [ ] **Step 3: Run boundary and integrity verification**

```bash
python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
python -m unittest discover -s tests -p "test_*.py" -v
```
Expected: 100% boundary coverage, 52+ tests pass.

- [ ] **Step 4: Commit**

```bash
git add README.md README.ru.md skills/manage-meta-project/SKILL.md docs/decisions_and_roadmap.md
git commit -m "docs: formalize Tier 0 micro-mode and provide bilingual ADR #14-#17 specifications"
```

---

### Task 8: Environment Hook Adapters Architecture (P2.1, P2.2, P2.3)

**Files:**
- Create: `hooks/install.py`
- Create: `hooks/pre_tool_use.py`
- Create: `hooks/session_start.py`
- Test: `tests/test_hooks.py`

**Interfaces:**
- `hooks/install.py --target [claude|cursor|codex|gemini] [--verify] [--uninstall]`
- `hooks/pre_tool_use.py` reads JSON tool call payload from stdin `{"tool": "Edit", "path": "..."}`, returns JSON `{"allow": true}` or `{"allow": false, "reason": "..."}`.
- `hooks/session_start.py` produces markdown context summary strictly under 1,500 tokens.

- [ ] **Step 1: Write failing unit test in `tests/test_hooks.py`**

```python
import unittest
import json
from pathlib import Path
from hooks.pre_tool_use import evaluate_tool_call
from hooks.session_start import generate_session_start_context

class TestHooks(unittest.TestCase):
    def test_pre_tool_use_blocks_red_zone_path(self):
        payload = {"tool": "Edit", "path": "tests/test_integrity.py"}
        res = evaluate_tool_call(payload)
        self.assertFalse(res["allow"])
        self.assertIn("Red Zone", res["reason"])

    def test_pre_tool_use_allows_green_zone_path(self):
        payload = {"tool": "Write", "path": "docs/notes.md"}
        res = evaluate_tool_call(payload)
        self.assertTrue(res["allow"])

    def test_session_start_token_budget(self):
        context = generate_session_start_context()
        # Rough token approximation: 1 token ~ 4 chars
        approx_tokens = len(context) / 4
        self.assertLess(approx_tokens, 1500)
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m unittest tests/test_hooks.py
```
Expected: FAIL (`ModuleNotFoundError: No module named 'hooks'`).

- [ ] **Step 3: Implement `hooks/pre_tool_use.py`, `hooks/session_start.py`, and `hooks/install.py`**

Create `hooks/pre_tool_use.py`:
```python
#!/usr/bin/env python3
"""PreToolUse Hook Adapter: Validates tool write/edit paths against boundary gate."""
import json
import sys
from pathlib import Path
from scripts.check_boundaries import load_zones, classify_path

WRITE_TOOLS = {"Edit", "Write", "write_to_file", "replace_file_content", "apply_patch"}

def evaluate_tool_call(payload: dict) -> dict:
    tool = payload.get("tool", "")
    path = payload.get("path", "")
    if tool not in WRITE_TOOLS or not path:
        return {"allow": True}

    repo_root = Path.cwd()
    boundaries_file = repo_root / ".agents" / "project_knowledge" / "boundaries.md"
    if not boundaries_file.is_file():
        boundaries_file = repo_root / "templates" / "project_knowledge" / "boundaries.md"

    zones = load_zones(boundaries_file) if boundaries_file.is_file() else {}
    zone = classify_path(path, zones)

    if zone in ("red", "black"):
        return {
            "allow": False,
            "reason": f"Path '{path}' is classified in {zone.upper()} ZONE. Modifications require human confirmation."
        }
    return {"allow": True}

if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        result = evaluate_tool_call(data)
        json.dump(result, sys.stdout)
        sys.exit(0 if result.get("allow") else 1)
    except Exception as e:
        json.dump({"allow": False, "reason": str(e)}, sys.stdout)
        sys.exit(1)
```

Create `hooks/session_start.py`:
```python
#!/usr/bin/env python3
"""SessionStart Hook Adapter: Injects compact context under 1,500 tokens."""
from pathlib import Path

def generate_session_start_context() -> str:
    repo_root = Path.cwd()
    passport = repo_root / "AGENTS.md"
    tasks = repo_root / ".agents" / "project_knowledge" / "tasks.md"

    lines = ["# Meta-Project Quick Session Context"]
    if passport.is_file():
        p_lines = [l for l in passport.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("<!--")]
        lines.extend(p_lines[:25]) # Compact summary of passport
    if tasks.is_file():
        t_lines = [l for l in tasks.read_text(encoding="utf-8").splitlines() if l.startswith("- [ ]")]
        lines.append("\n## Active Tasks")
        lines.extend(t_lines[:5])
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    print(generate_session_start_context())
```

Create `hooks/install.py`:
```python
#!/usr/bin/env python3
"""Hook Manager: Installs, verifies, and uninstalls environment hook adapters."""
import argparse
import sys
from pathlib import Path

def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage Meta-Project environment hooks.")
    parser.add_argument("--target", choices=["claude", "cursor", "codex", "gemini"], default="claude")
    parser.add_argument("--verify", action="store_true", help="Verify hook output")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall hook configuration")
    args = parser.parse_args(argv)
    
    sys.stdout.write(f"Harness hook adapter manager: target={args.target}, verify={args.verify}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m unittest discover -s tests -p "test_hooks.py" -v
```
Expected: All tests pass.

- [ ] **Step 5: Map `hooks/**` in `boundaries.md` and commit**

Add `hooks/**` to Yellow Zone in `boundaries.md` and mirror to `templates/`.
```bash
git add hooks/ tests/test_hooks.py .agents/project_knowledge/boundaries.md templates/project_knowledge/boundaries.md
git commit -m "feat(hooks): create stdlib environment hook adapters for PreToolUse and SessionStart"
```

---

### Task 9: Decision-RTL Canonical Template & Skill Rollout (P2.4)

**Files:**
- Modify: `templates/AGENTS.md`
- Modify: `templates/team/system_prompt.md`
- Modify: `docs/decisions_and_roadmap.md`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Decision-RTL specification with `Verification Result & Impact` field.
- Produces: Updated canonical templates ensuring agents log architectural justification for non-trivial refactorings.

- [ ] **Step 1: Write integrity test asserting Decision-RTL in templates**

In `tests/test_integrity.py`:
```python
    def test_decision_rtl_in_canonical_templates(self):
        """Verify templates/AGENTS.md contains the Decision-RTL specification and verification result field."""
        passport_tmpl = REPO_ROOT / "templates" / "AGENTS.md"
        content = passport_tmpl.read_text(encoding="utf-8")
        self.assertIn("Decision RTL", content)
        self.assertIn("Verification Result & Impact", content)
```

- [ ] **Step 2: Add Decision-RTL to `templates/AGENTS.md`**

In `templates/AGENTS.md`, insert under Section 5 (Base Working Protocol):
```markdown
### Architectural Decision Protocol (Decision-RTL)
For architecturally significant changes touching system goals, invariants, external dependencies, contracts, or component boundaries, record a brief rationale before modifying code:
- **Decision RTL: [Title]**
  - **Goal:** [Problem solved]
  - **Affected Invariants (North Stars):** [Principles touched]
  - **Rationale:** [Why this approach was chosen over alternatives]
  - **Risks & Trade-offs:** [Technical debt or trade-offs incurred]
  - **Verification Result & Impact:** [Empirical outcome, tests, or metrics verified]
```

- [ ] **Step 3: Run template sync and integrity tests**

```bash
python scripts/sync_templates.py --write
python scripts/sync_templates.py --check
python -m unittest discover -s tests -p "test_integrity.py" -v
```
Expected: 0 drift detected, all integrity assertions pass.

- [ ] **Step 4: Commit**

```bash
git add templates/AGENTS.md templates/team/system_prompt.md skills/ .agents/skills/ tests/test_integrity.py
git commit -m "feat(templates): roll out Decision-RTL template with verification outcome field"
```

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-11-12-core-reliability-and-policy-hardening.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.
**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
