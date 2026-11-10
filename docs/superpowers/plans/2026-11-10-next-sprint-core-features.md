# Next Sprint Implementation Plan: Boundary Gate, Memory Compaction, Team Frontmatter & Interactive Interview

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 4 high-priority items from the active roadmap: an automated Boundary Gate CLI (`scripts/check_boundaries.py`) with CI enforcement, a memory compaction mechanism (`scripts/compact_memory.py`), standardized YAML frontmatter for `.agents/team/` profiles, and a codified interactive interview protocol in `init-meta-project`.

**Architecture:** Build zero-dependency Python stdlib utilities (`scripts/`), integrate the boundary gate into `.github/workflows/ci.yml`, expand test coverage in `tests/`, update team templates and active role profiles, and codify the interview pass in `init-meta-project`.

**Tech Stack:** Python 3.10+ (pure standard library: `argparse`, `pathlib`, `fnmatch`, `subprocess`, `unittest`, `re`), Markdown, YAML frontmatter, GitHub Actions CI.

**Spec:** [`docs/decisions_and_roadmap.md`](../../../docs/decisions_and_roadmap.md) (Section 2: Ideas 1 & 2; Section 6: Items 255–259).

## Global Constraints
- **Zero External Dependencies:** All utilities (`scripts/*.py`) and tests must run exclusively using the Python 3.10+ standard library. External packages (PyYAML, Click, GitPython) are strictly prohibited.
- **Default Deny Invariant:** Unmapped paths in `boundaries.md` are treated as Red Zone. The boundary gate must fail closed.
- **Skill & Template Parity:** Any update to canonical templates or skills (`skills/`) must be mirrored 1-to-1 in local dogfooding copies (`.agents/skills/`) and verified by `tests/test_integrity.py`.
- **No Context Bloat:** Memory compaction must preserve active goals and architectural rules while rotating historical records cleanly into `.agents/project_knowledge/archive/`.

---

## File Structure

### 1. Automation Scripts (`scripts/`)
- `scripts/check_boundaries.py`: Boundary verification CLI that reads `boundaries.md`, extracts Red/Yellow/Green zone glob patterns, checks git modified/staged files, and exits with code 1 if Red Zone or unmapped files are modified without an explicit override flag.
- `scripts/compact_memory.py`: Context rot compaction utility that rotates stale `observations.md` (>30 rows) and completed tasks in `tasks.md` into `.agents/project_knowledge/archive/`.

### 2. Integrity and Unit Tests (`tests/`)
- `tests/test_check_boundaries.py`: Unit tests for `check_boundaries.py` testing glob matching, Default Deny evaluation, exit codes, and flag handling.
- `tests/test_compact_memory.py`: Unit tests for `compact_memory.py` testing threshold triggering, markdown table preservation, and archive file creation.
- `tests/test_integrity.py`: Updated suite validating that `scripts/check_boundaries.py` exists, team profiles have valid YAML frontmatter, and embedded interview steps match specifications.

### 3. CI/CD Workflows (`.github/workflows/`)
- `.github/workflows/ci.yml`: Added `boundary-gate` job or step running `python scripts/check_boundaries.py` on pull requests and pushes.

### 4. Canonical Templates & Active Environment
- `templates/team/profile.md`: Added standardized YAML frontmatter (`name`, `role_id`, `description`, `tools`, `model`, `triggers`).
- `.agents/team/*/profile.md`: Aligned active profiles (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`) with YAML frontmatter.
- `skills/init-meta-project/SKILL.md` and `.agents/skills/init-meta-project/SKILL.md`: Upgraded Pass 2 with codified 2-question interactive interview.

---

## Tasks

### Task 1: Boundary Gate Script & Unit Tests (`scripts/check_boundaries.py`)

**Files:**
- Create: `scripts/check_boundaries.py`
- Create: `tests/test_check_boundaries.py`
- Modify: `tests/test_integrity.py`

**Interfaces:**
- Consumes: `.agents/project_knowledge/boundaries.md` (or `templates/project_knowledge/boundaries.md`), Git diff output via `git diff --name-only` or `--cached`.
- Produces: CLI interface `python scripts/check_boundaries.py [--boundaries PATH] [--allow-red-zone] [--diff-target REF]` returning exit code 0 on pass, exit code 1 on boundary violation.

- [x] **Step 1: Write unit tests for boundary checker (`tests/test_check_boundaries.py`)**
  Cover:
  - Parsing zones from markdown tables (extracting globs for Green, Yellow, Red).
  - Verifying matching against Red Zone globs (`fnmatch.fnmatch`).
  - Verifying Default Deny behavior: any file not matching Green, Yellow, or Red patterns raises a violation.
  - Flag `--allow-red-zone` overriding exit code.
  - Return code 0 when only Green/Yellow files are touched.

- [x] **Step 2: Run test to confirm it fails**
  Run: `python -m unittest tests/test_check_boundaries.py` (fails because script doesn't exist yet).

- [x] **Step 3: Implement `scripts/check_boundaries.py`**
  Implement:
  - Markdown table parser extracting globs from `boundaries.md`.
  - Git diff extractor (invoking `git diff --name-only` with fallback to explicit file list argument `--files`).
  - Zone classification engine with Default Deny logic.
  - Human-readable violation report printed to `sys.stderr`.
  - Exit code 0 if all clean or `--allow-red-zone` is passed; exit code 1 if violations found.

- [x] **Step 4: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_check_boundaries.py` (must pass).

- [x] **Step 5: Add integrity test in `tests/test_integrity.py`**
  Add `test_boundary_gate_script_exists_and_functional` checking that `scripts/check_boundaries.py` is present and runs `--help` cleanly.

- [x] **Step 6: Run full test suite and commit**
  Run: `python -m unittest discover -s tests -p "test_*.py"`
  Commit: `feat(gate): add zero-dependency boundary check script and tests`

---

### Task 2: Integrate Boundary Gate into CI Workflow

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `scripts/check_boundaries.py`
- Produces: Automated PR & push gate in GitHub Actions.

- [x] **Step 1: Update `.github/workflows/ci.yml`**
  Add step in CI job:
  ```yaml
  - name: Run Boundary Gate Check
    run: python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md
  ```

- [x] **Step 2: Validate CI workflow syntax**
  Verify `.github/workflows/ci.yml` indentation and run existing tests.

- [x] **Step 3: Commit**
  Commit: `ci(gate): enforce boundary check script in GitHub Actions workflow`

---

### Task 3: Memory Compaction Script & Telemetry Shield (`scripts/compact_memory.py`)

**Files:**
- Create: `scripts/compact_memory.py`
- Create: `tests/test_compact_memory.py`
- Modify: `skills/record-observation/SKILL.md`
- Modify: `.agents/skills/record-observation/SKILL.md`

**Interfaces:**
- Consumes: `.agents/project_knowledge/observations.md`, `.agents/project_knowledge/tasks.md`
- Produces: Archived files in `.agents/project_knowledge/archive/` and pruned primary markdown files.

- [x] **Step 1: Write unit tests for compaction (`tests/test_compact_memory.py`)**
  Cover:
  - Count rows in `observations.md` table. If > 20 rows, rotate older entries (keeping header + newest 10 rows) into `.agents/project_knowledge/archive/observations_YYYYMM.md`.
  - Parse `tasks.md` for closed items (`- [x]`). Rotate completed items when list exceeds threshold.
  - Dry-run mode (`--dry-run`) returning compaction diff without writing to disk.

- [x] **Step 2: Run test to confirm it fails**
  Run: `python -m unittest tests/test_compact_memory.py`

- [x] **Step 3: Implement `scripts/compact_memory.py`**
  Implement pure Python logic:
  - Table parser identifying Markdown table dividers and rows.
  - Archive directory manager creating `.agents/project_knowledge/archive/` if not present.
  - Atomic write with backup or in-place overwrite.
  - CLI flags: `--dry-run`, `--max-observations=20`, `--archive-dir`.

- [x] **Step 4: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_compact_memory.py`

- [x] **Step 5: Sync `record-observation` skills**
  Update `skills/record-observation/SKILL.md` and `.agents/skills/record-observation/SKILL.md` to reference `python scripts/compact_memory.py` when observations table exceeds 20 rows.

- [x] **Step 6: Run full test suite and commit**
  Run: `python -m unittest discover -s tests -p "test_*.py"`
  Commit: `feat(memory): add memory compaction utility and update record-observation protocol`

---

### Task 4: Standardize YAML Frontmatter in Team Profiles (`.agents/team/`)

**Files:**
- Modify: `templates/team/profile.md`
- Modify: `.agents/team/agent-dev-lead/profile.md`
- Modify: `.agents/team/agent-quality-guardian/profile.md`
- Modify: `.agents/team/agent-github-steward/profile.md`
- Modify: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Existing markdown role passports.
- Produces: Standardized role passports with YAML frontmatter compliant with subagent executors.

- [x] **Step 1: Add failing test in `tests/test_integrity.py`**
  Add `test_team_profiles_have_valid_yaml_frontmatter` that verifies:
  - File starts with `---` and contains closing `---`.
  - Required fields exist: `name`, `role_id`, `description`, `tools`, `model`, `invocation_triggers`.
  - Checked for both `templates/team/profile.md` and all files matching `.agents/team/*/profile.md`.

- [x] **Step 2: Run test to confirm it fails**
  Run: `python -m unittest tests/test_integrity.py -k test_team_profiles_have_valid_yaml_frontmatter`

- [x] **Step 3: Update `templates/team/profile.md`**
  Add frontmatter block:
  ```yaml
  ---
  name: "{{ROLE_TITLE}}"
  role_id: "{{ROLE_ID}}"
  description: "{{ROLE_SCOPE}}"
  tools:
  {{ROLE_TOOLS_YAML}}
  model: "inherit"
  invocation_triggers:
  {{ROLE_TRIGGERS_YAML}}
  ---
  ```

- [x] **Step 4: Update active `.agents/team/*/profile.md` files**
  Add YAML frontmatter to:
  - `.agents/team/agent-dev-lead/profile.md`
  - `.agents/team/agent-quality-guardian/profile.md`
  - `.agents/team/agent-github-steward/profile.md`

- [x] **Step 5: Run tests to verify pass**
  Run: `python -m unittest tests/test_integrity.py -k test_team_profiles_have_valid_yaml_frontmatter`

- [x] **Step 6: Commit**
  Commit: `feat(team): add standardized YAML frontmatter to canonical templates and active team profiles`

---

### Task 5: Codify Interactive Interview Protocol in `init-meta-project`

**Files:**
- Modify: `skills/init-meta-project/SKILL.md`
- Modify: `.agents/skills/init-meta-project/SKILL.md`
- Modify: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Pass 2 scanning logic in `init-meta-project`.
- Produces: Codified interactive prompt block (2 questions) asking user for core North Stars and Red Zone exceptions before writing `AGENTS.md`.

- [x] **Step 1: Update Pass 2 in `skills/init-meta-project/SKILL.md`**
  Formalize the interactive interview protocol:
  - Question 1 (North Stars / Core Invariants): "Какие ключевые архитектурные инварианты и бизнес-правила (North Stars) нельзя нарушать при любых доработках?"
  - Question 2 (Red Zone / Boundaries): "Какие каталоги или модули (БД, секреты, легаси) являются критическими и должны быть заблокированы в Red Zone?"
  - Record answers into `AGENTS.md` (Section 1) and `boundaries.md` before single-pass flush.

- [x] **Step 2: Synchronize `.agents/skills/init-meta-project/SKILL.md`**
  Ensure identical content between canonical and agent copies.

- [x] **Step 3: Update integrity test in `tests/test_integrity.py`**
  Verify `test_skills_parity_between_canonical_and_agent_copies` passes and add check for interview protocol presence in `init-meta-project`.

- [x] **Step 4: Run full test suite and commit**
  Run: `python -m unittest discover -s tests -p "test_*.py"`
  Commit: `feat(init): codify two-question interactive interview protocol in init-meta-project skill`

---

## Execution Summary & Next Actions for `agent-dev-lead`
1. Execute Task 1 (Boundary Gate CLI) via TDD.
2. Execute Task 2 (CI integration).
3. Execute Task 3 (Memory compaction).
4. Execute Task 4 (YAML frontmatter).
5. Execute Task 5 (Interactive interview).
6. Perform final end-to-end test run and update `tasks.md` and role telemetry.
