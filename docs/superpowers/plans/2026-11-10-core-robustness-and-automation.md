# Implementation Plan: Core Robustness, Pattern Matching, Template Sync & Intelligent Compaction

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate 6 validated code vulnerabilities and blind spots (boundary leaks for `AGENTS.md`, test precedence conflict, zero-depth `**` glob matching, missing `tasks.md` in passport template, documentation drift), implement template injection automation (`scripts/sync_templates.py`), enrich memory compaction with `[pin]` protection, enable full-tree boundary auditing (`--audit-tree`), and package runtime scripts for target repository deployments.

**Architecture:** 
1. Fix core pattern matching and boundary classification in `scripts/check_boundaries.py`.
2. Implement automated template-to-skill injection (`scripts/sync_templates.py`) to eliminate manual drift while preserving self-contained skill distribution.
3. Enhance `scripts/compact_memory.py` with `[pin]` retention logic.
4. Upgrade `skills/init-meta-project` to scaffold `scripts/` into target repositories.
5. Expand unit and integrity test suites in `tests/`.

**Tech Stack:** Python 3.10+ standard library (`argparse`, `pathlib`, `re`, `subprocess`, `unittest`, `fnmatch`), Markdown.

**Spec:** Current session audit and decisions in `docs/decisions_and_roadmap.md`.

## Global Constraints
- **Zero External Dependencies:** All scripts and test suites must strictly use Python 3.10+ standard library modules only.
- **Self-Contained Skill Distribution:** Procedural skills (`skills/init-meta-project/`) must remain 100% self-contained so they function seamlessly in foreign repositories without requiring `meta-project` cloning.
- **Fail Closed (Default Deny):** Any path not explicitly allowed in Green or Yellow zones must resolve to Red or Black zone.
- **Preserve Defensive Security Globs:** Boundary checks must never discard or delete empty Red Zone globs (`*.pem`, `*.key`, `src/billing/**`, `config/secrets/**`) as "dead code".

---

## File Structure

### 1. Automation & Verification Scripts (`scripts/`)
- `scripts/check_boundaries.py`: Enhanced with exception-parenthesis stripping, specific-over-broad precedence (Green test masks over broad `tests/**`), zero-depth `**` matching (`src/**/test.py` matches `src/test.py`), explicit `AGENTS.md` protection, and `--audit-tree` mode.
- `scripts/compact_memory.py`: Enhanced with `[pin]` tag preservation to shield permanent invariants from FIFO archival.
- `scripts/sync_templates.py`: Developer utility that parses canonical templates in `templates/` and injects them into embedded template sections in `skills/init-meta-project/SKILL.md` and `skills/manage-meta-project/SKILL.md`, then mirrors to `.agents/skills/`.

### 2. Canonical Templates & Skills (`templates/`, `skills/`)
- `templates/AGENTS.md`: Enriched with Section 3 directive slice for `tasks.md`.
- `templates/project_knowledge/boundaries.md`: Explicitly anchor `AGENTS.md` in Yellow/Red zones, refine test patterns.
- `skills/init-meta-project/SKILL.md`: Synchronized embedded templates; added deployment of `scripts/` into target repos.
- `CONTRIBUTING.md` and `CONTRIBUTING.ru.md`: Updated repository tree with all 6 skills and `scripts/`.

### 3. Test Suites (`tests/`)
- `tests/test_check_boundaries.py`: Expanded with test cases for `AGENTS.md` protection, zero-depth `**`, test precedence, and `--audit-tree`.
- `tests/test_compact_memory.py`: Expanded with test cases for `[pin]` tag retention.
- `tests/test_sync_templates.py`: Unit tests verifying that template sync runs cleanly and preserves parity.
- `tests/test_integrity.py`: Updated integrity assertions.

---

## Tasks

### Task 1: Fix Boundary Classifier, Exception Parsing & Zero-Depth Globs (`scripts/check_boundaries.py`)

**Files:**
- Modify: `scripts/check_boundaries.py`
- Modify: `templates/project_knowledge/boundaries.md`
- Modify: `.agents/project_knowledge/boundaries.md`
- Test: `tests/test_check_boundaries.py`

**Interfaces:**
- Consumes: `boundaries.md` markdown text, file paths.
- Produces: Correct zone classifications:
  - `AGENTS.md` -> `yellow` or `red` (never `green`).
  - `tests/test_something.py` -> `green` (when Green contains `tests/test_*.py`).
  - `src/test.py` -> matches `src/**/test.py`.

- [ ] **Step 1: Write failing unit tests in `tests/test_check_boundaries.py`**
  Add test cases:
  1. `test_agents_md_is_not_classified_as_green`: verify `classify_path('AGENTS.md', zones)` returns `yellow` or `red`.
  2. `test_parenthesis_exceptions_not_extracted_as_globs`: verify string `*.md (except the root AGENTS.md)` does not add `AGENTS.md` to `zones['green']`.
  3. `test_zero_depth_double_star_matching`: verify `glob_to_regex('src/**/test.py').match('src/test.py')` returns truthy.
  4. `test_specific_test_mask_precedence_over_broad_yellow`: verify that when Green has `tests/test_*.py` and Yellow has `tests/**`, `classify_path('tests/test_foo.py', zones)` returns `green`.

- [ ] **Step 2: Run test suite to verify failures**
  Run: `python -m unittest tests/test_check_boundaries.py`

- [ ] **Step 3: Implement fixes in `scripts/check_boundaries.py`**
  1. In `parse_boundaries`: strip parentheses `line_clean = re.sub(r"\(.*?\)", "", line_str)` *before* scanning for backticks `re.findall(r"`([^`]+)`", line_clean)`.
  2. In `glob_to_regex`: handle `/**/` specifically by converting `/**/` into `(?:/.+/|/)`, allowing zero intermediate directories.
  3. In `classify_path`: check specific Green file masks before broad directory patterns in Yellow, OR evaluate Green patterns with filename wildcards prior to catch-all directory globs (`tests/**`).
  4. In `boundaries.md`: explicitly list `AGENTS.md` in Yellow Zone (`AGENTS.md` — project passport requiring verification) or Red Zone.

- [ ] **Step 4: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_check_boundaries.py` (all tests pass).

- [ ] **Step 5: Run full test suite and commit**
  Run: `python -m unittest discover -s tests -p "test_*.py"`
  Commit: `fix(gate): resolve AGENTS.md leak, test precedence, and zero-depth glob matching`

---

### Task 2: Implement Tree-Wide Boundary Audit Mode (`scripts/check_boundaries.py --audit-tree`)

**Files:**
- Modify: `scripts/check_boundaries.py`
- Test: `tests/test_check_boundaries.py`

**Interfaces:**
- Consumes: Repository file tree, `.gitignore`.
- Produces: CLI mode `python scripts/check_boundaries.py --audit-tree` reporting:
  - Any unmapped files/directories (Default Deny violations across entire repo).
  - Warnings for non-defensive unused patterns (differentiating between defensive security globs and stale paths).

- [ ] **Step 1: Write failing unit test for tree audit**
  Add `test_audit_tree_detects_unmapped_files` in `tests/test_check_boundaries.py`.

- [ ] **Step 2: Run test to confirm failure**
  Run: `python -m unittest tests/test_check_boundaries.py -k test_audit_tree`

- [ ] **Step 3: Implement `--audit-tree` in `scripts/check_boundaries.py`**
  - Walk directory tree respecting git status / `.gitignore`.
  - Classify every tracked/untracked source file.
  - Report unmapped paths with remediation suggestions.
  - Return exit code 1 if unmapped source paths exist, 0 if 100% covered.

- [ ] **Step 4: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_check_boundaries.py`

- [ ] **Step 5: Commit**
  Commit: `feat(gate): add full-tree boundary coverage audit mode`

---

### Task 3: Intelligent Memory Compaction with `[pin]` Tag Support (`scripts/compact_memory.py`)

**Files:**
- Modify: `scripts/compact_memory.py`
- Modify: `skills/record-observation/SKILL.md`
- Modify: `.agents/skills/record-observation/SKILL.md`
- Test: `tests/test_compact_memory.py`

**Interfaces:**
- Consumes: `observations.md` table lines containing `[pin]`.
- Produces: Compaction that retains pinned entries in the primary file regardless of their age/row index.

- [ ] **Step 1: Write failing unit tests in `tests/test_compact_memory.py`**
  Add `test_pinned_observations_never_archived`:
  - Create table with 10 rows where rows 1 and 2 have `[pin]`.
  - Run `compact_observations` with `max_rows=4, keep_rows=2`.
  - Verify that rows 1 and 2 remain in the primary table alongside the newest rows, and are NOT moved to archive.

- [ ] **Step 2: Run test to confirm failure**
  Run: `python -m unittest tests/test_compact_memory.py -k test_pinned_observations_never_archived`

- [ ] **Step 3: Implement `[pin]` support in `scripts/compact_memory.py`**
  In `compact_observations`:
  - Identify rows containing `[pin]` tag.
  - Exclude pinned rows from candidate rotation list.
  - Archive only non-pinned older rows.
  - Reassemble table: table header + pinned historical rows + newest retained rows.

- [ ] **Step 4: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_compact_memory.py`

- [ ] **Step 5: Update `record-observation` skill documentation**
  Document the `[pin]` convention in `skills/record-observation/SKILL.md` and `.agents/skills/record-observation/SKILL.md`:
  *"Use `[pin]` tag in Category (e.g. `[env][pin]` or `[pin]`) for permanent architectural invariants that must never be rotated into archive."*

- [ ] **Step 6: Commit**
  Commit: `feat(memory): add [pin] tag retention to protect permanent invariants from compaction`

---

### Task 4: Template Injection & Synchronization Automation (`scripts/sync_templates.py`)

**Files:**
- Create: `scripts/sync_templates.py`
- Create: `tests/test_sync_templates.py`
- Modify: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Canonical templates in `templates/` (`boundaries.md`, `architecture.md`, `system_prompt.md`, `profile.md`, `AGENTS.md`).
- Produces: Automatically injected embedded template sections inside `skills/init-meta-project/SKILL.md` and `skills/manage-meta-project/SKILL.md`, and mirrors canonical skills to `.agents/skills/`.

- [ ] **Step 1: Write unit tests for template synchronizer (`tests/test_sync_templates.py`)**
  Cover:
  - Marker-based template replacement (identifying embedded code fences).
  - Parity verification between `skills/` and `.agents/skills/`.
  - CLI `--check` flag returning exit code 1 if drift is detected without modifying files.

- [ ] **Step 2: Run test to confirm failure**
  Run: `python -m unittest tests/test_sync_templates.py`

- [ ] **Step 3: Implement `scripts/sync_templates.py`**
  Implement:
  - Embedder mapping canonical templates (`templates/project_knowledge/boundaries.md`, etc.) into `skills/init-meta-project/SKILL.md` and `skills/manage-meta-project/SKILL.md`.
  - Mirroring from `skills/<name>/SKILL.md` to `.agents/skills/<name>/SKILL.md`.
  - CLI flags: `--check` (dry-run validator) and `--write` (in-place synchronization).

- [ ] **Step 4: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_sync_templates.py`

- [ ] **Step 5: Integrate `--check` into `tests/test_integrity.py` and CI**
  Add test asserting that `scripts/sync_templates.py --check` exits with 0 (zero drift between templates and embedded skills).

- [ ] **Step 6: Commit**
  Commit: `feat(build): add zero-dependency template injection and skill sync utility`

---

### Task 5: Upgrade `init-meta-project` to Deploy `scripts/` and Fix Template Slices

**Files:**
- Modify: `templates/AGENTS.md`
- Modify: `skills/init-meta-project/SKILL.md`
- Modify: `.agents/skills/init-meta-project/SKILL.md`
- Modify: `CONTRIBUTING.md`
- Modify: `CONTRIBUTING.ru.md`

**Interfaces:**
- Consumes: Upgraded scaffolding logic.
- Produces:
  - Target repositories receive `.agents/skills/` AND `scripts/` (`check_boundaries.py`, `compact_memory.py`).
  - Target `AGENTS.md` includes `tasks.md` in Section 3.
  - `CONTRIBUTING` documentation reflects all 6 skills and `scripts/`.

- [ ] **Step 1: Add `tasks.md` to `templates/AGENTS.md`**
  Add directive slice block for `.agents/project_knowledge/tasks.md` in Section 3.

- [ ] **Step 2: Update `skills/init-meta-project/SKILL.md` scaffolding**
  - Add deployment of `scripts/` (`scripts/check_boundaries.py`, `scripts/compact_memory.py`) into target repositories.
  - Update embedded templates via `python scripts/sync_templates.py --write`.

- [ ] **Step 3: Update `CONTRIBUTING.md` and `CONTRIBUTING.ru.md`**
  Align repository tree: include all 6 skills and `scripts/`.

- [ ] **Step 4: Run full test suite**
  Run: `python -m unittest discover -s tests -p "test_*.py"`

- [ ] **Step 5: Commit**
  Commit: `fix(init): scaffold scripts directory into target repos and align passport templates`

---

### Task 6: Add Git Pre-Commit Hook Installer Option

**Files:**
- Modify: `scripts/check_boundaries.py`
- Test: `tests/test_check_boundaries.py`

**Interfaces:**
- CLI flag: `python scripts/check_boundaries.py --install-hook`
- Produces: Executable `.git/hooks/pre-commit` running `python scripts/check_boundaries.py --staged`.

- [ ] **Step 1: Write unit test for hook installation**
  Add test verifying `.git/hooks/pre-commit` generation in temporary directory.

- [ ] **Step 2: Implement `--install-hook` in `scripts/check_boundaries.py`**
  Writes POSIX/Windows compatible pre-commit script invoking boundary check on staged files.

- [ ] **Step 3: Run unit tests to verify pass**
  Run: `python -m unittest tests/test_check_boundaries.py -k test_install_hook`

- [ ] **Step 4: Commit**
  Commit: `feat(gate): add --install-hook flag to configure local git pre-commit boundary enforcement`

---

## Execution Checklist & Final Verification
1. Run `python scripts/sync_templates.py --check` (must pass with 0 drift).
2. Run `python scripts/check_boundaries.py --audit-tree` (must confirm 100% path coverage).
3. Run full test suite: `python -m unittest discover -s tests -p "test_*.py" -v`.
4. Synchronize updated global skills: copy `skills/` to `~/.gemini/config/skills/`.
5. Update `tasks.md` and role telemetry in `.agents/team/agent-dev-lead/profile.md`.
