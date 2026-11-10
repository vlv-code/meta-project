# Polyglot Monorepo Incident Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Systematically integrate lessons and architectural invariants from the polyglot monorepo incident into meta-project: enforce Default Deny boundaries, eliminate ritualistic prompt theater, introduce Circuit Breaker and Target State Audit invariants, mandate polyglot stack isolation, and expand test integrity.

**Architecture:** Update canonical templates (`templates/`), upgrade procedural orchestration skills (`init-meta-project`, `manage-meta-project`), expand `tests/test_integrity.py` with structural invariant validations, update live repository slices, and synchronize global skills.

**Tech Stack:** Python 3.10+ (pure standard library: `unittest`, `pathlib`, `re`), Markdown, YAML frontmatter.

**Spec:** [`docs/decisions_and_roadmap.md`](docs/decisions_and_roadmap.md#L136-L245) (Section 5: "Инцидент с полиглотным монорепозиторием (Polyglot Monorepo Incident) и системные уроки для фреймворка")

## Global Constraints
- **Zero External Dependencies:** Runtime utilities, validation scripts, and tests must run exclusively on the Python standard library.
- **Backward Compatibility:** All existing English and Russian trigger words and section headings must remain valid in `test_integrity.py`.
- **No Context Bloat:** Passports (`AGENTS.md`) and role manifests must remain concise, free of dynamic conversation logs or unstructured dumps.
- **Skill Immutability (Unwritten Principle):** Skills are maintained centrally in `meta-project`; target repository agents must not modify their own `SKILL.md` files.

---

## File Structure

### 1. Canonical Templates (`templates/`)
- `templates/project_knowledge/boundaries.md`: Canonical boundary template defining Green/Yellow/Red zones + Default Deny (Black Zone) rule and 100% path coverage requirement.
- `templates/project_knowledge/architecture.md`: Canonical architecture template enriched with mandatory "End-to-End Data Flows" section.
- `templates/team/system_prompt.md`: Canonical role system prompt template with Circuit Breaker, Target State Audit, Handoff Tripwires, silent internal protocol check, and recalibrated minimal changes rule.
- `templates/team/profile.md`: Canonical role profile template enriched with unmapped directory boundary safeguards.
- `templates/AGENTS.md`: Canonical root passport template embedding Circuit Breaker, Pre-Flight Flow Tracing, and Default Deny invariants in Section 1 and Section 5.

### 2. Procedural Skills (`skills/`)
- `skills/init-meta-project/SKILL.md`: Scaffolding skill updated with 100% directory coverage checks, mandatory data-flow mapping, and synchronized embedded templates.
- `skills/manage-meta-project/SKILL.md`: Team orchestration skill updated with polyglot stack detection, polyglot isolation rules (no toxic bundles), mandatory intake dispatcher rule (>2 roles), and synchronized embedded templates.

### 3. Automated Integrity Suite (`tests/`)
- `tests/test_integrity.py`: Automated test suite expanded with assertions verifying Default Deny in boundaries, Circuit Breaker & Target State Audit in system prompts, and Data Flow in architecture templates.

### 4. Active Repository & Global Environment
- `AGENTS.md`, `.agents/project_knowledge/*`, `.agents/team/*`: Live active workspace files aligned with new invariants.
- `~/.gemini/config/skills/*`: Global Antigravity skill installations kept in 1-to-1 sync.

---

## Tasks

### Task 1: Update Canonical Knowledge & Passport Templates (`boundaries.md`, `architecture.md`, `AGENTS.md`)

**Files:**
- Modify: `templates/project_knowledge/boundaries.md`
- Modify: `templates/project_knowledge/architecture.md`
- Modify: `templates/AGENTS.md`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Existing template definitions in `templates/`
- Produces: Updated canonical templates with Default Deny, Data Flow structure, and Circuit Breaker invariants

- [x] **Step 1: Update `templates/project_knowledge/boundaries.md` with Default Deny rule**

Add the "Default Deny (Black Zone)" invariant to `templates/project_knowledge/boundaries.md`:
```markdown
---

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any directory or file path not explicitly listed in Green, Yellow, or Red zones above is strictly classified as **Red Zone by Default**. Autonomous modifications to unmapped paths are prohibited. Prior to touching unmapped code, the agent MUST consult the user and perform an *Opportunistic Refresh* of `boundaries.md` to map the path to its appropriate zone.
```

- [x] **Step 2: Update `templates/project_knowledge/architecture.md` with Data Flow section**

Add the mandatory "End-to-End Data Flows" schema template to `templates/project_knowledge/architecture.md`:
```markdown
---

## 4. End-to-End Data Flows (Pre-Flight Flow Tracing)
Every multi-tier feature or bugfix touching client-server, UI, or storage boundaries must map the flow across components before making code changes:

```
[Origin: UI/CLI/Event] ➔ [Transport: API Route / Message] ➔ [Domain / Storage: Persistence] ➔ [Assembly / Packager] ➔ [Consumer: Client / Daemon]
```
- **Primary Data Flow 1:** [e.g. User Configuration ➔ Sync Route ➔ Atomic Store ➔ Client Polling]
- **Single Source of Truth:** [Specify authoritative owner of state]
```

- [x] **Step 3: Update `templates/AGENTS.md` with Circuit Breaker and Pre-Flight Flow Tracing (No Context Bloat)**

In `templates/AGENTS.md`, add concise 1–2 sentence statements (strictly adhering to the *No Context Bloat* invariant) in Section 1 (North Stars) and Section 5 (Base Working Protocol):
- Add North Star in Section 1:
  `- **Circuit Breaker & Flow Tracing:** Prohibit repetitive code edits during cross-component defects without first mapping the data path. Stop on 2nd consecutive fix in the same module to perform root cause investigation.`
  `- **Default Deny Boundaries:** Any directory not explicitly mapped in boundaries is strictly Red Zone.`
- Add rule in Section 5:
  `Refactoring unrelated areas is prohibited; changes must be minimal in diff width, but maximal in root-cause depth.`

- [x] **Step 4: Run existing integrity tests to verify no syntax regressions**

Run: `python -m unittest discover -s tests -p "test_*.py" -v`
Expected: 4 tests pass (`OK`).

---

### Task 2: Update Role System Prompt & Profile Templates (`system_prompt.md`, `profile.md`)

**Files:**
- Modify: `templates/team/system_prompt.md`
- Modify: `templates/team/profile.md`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Lessons from polyglot monorepo incident recorded in `docs/decisions_and_roadmap.md`
- Produces: Updated role scaffolding templates eliminating prompt theater and embedding behavioral tripwires

- [x] **Step 1: Replace prompt theater with operational triggers in `templates/team/system_prompt.md`**

Replace lines 8–13 of `templates/team/system_prompt.md`:
Instead of a ritualistic reciting checklist, instruct:
```markdown
## Operational Protocol Before Taking Action
Perform silent internal verification before your first tool call or answer:
1. Verify target file paths against `.agents/project_knowledge/boundaries.md`. If unmapped, apply the **Default Deny** rule (treat as Red Zone).
2. Check your product scope and active skills. If the task requires tools/languages outside your skills (e.g. C++ in a TypeScript role), do NOT modify code blindly — trigger a **Handoff Packet**.
3. Do NOT recite this checklist in chat; reply directly and substantively to the user's request.
```

- [x] **Step 2: Add Circuit Breaker, Target State Audit, and Data-Flow Invariant to `templates/team/system_prompt.md`**

Add to Section `## Systemic Rules and Behavioral Regulations`:
```markdown
6. **Circuit Breaker (Stop-Work on 2nd Iteration):** If a bugfix requires a second attempt in the same module or produces a secondary regression in adjacent code, CEASE code modifications immediately. Zoom out, trace the full data lifecycle from origin to consumer, identify the architectural root cause, and present a systemic analysis before proposing any new diff.
7. **Target State Audit:** Before modifying non-trivial modules in Yellow or Red zones, determine:
   - *Single Source of Truth:* Who authoritatively owns this state?
   - *Persistence & Cache:* Where does state persist (disk, memory, `%APPDATA%`, registry) and how is it invalidated?
   - *Contract Duplication:* Is this logic mirrored in multiple languages or client modules?
8. **Minimal Diffs, Maximal Depth:** "Minimal changes" means minimal width of interference (no unrelated refactoring), but maximal depth of root-cause investigation. Never apply regex sanitizing or ad-hoc patches to suppress symptom errors.
9. **Mandatory Observations Trigger (Definition of Done):** If you resolve an undocumented environment quirk, compiler macro mismatch, or runtime edge-case, you MUST invoke `record-observation` before claiming the task is complete.
10. **Pragmatic Handoff vs Dogmatism:** If the user explicitly asks you to inspect or patch a minor issue within the current session, proceed without forcing a handoff. Only trigger a structured Handoff Packet if the task requires deep domain architecture outside your skills, or if you lack the required toolchain to test the change safely.
```

- [x] **Step 3: Update `templates/team/profile.md` with Default Deny safeguards**

In `templates/team/profile.md`, update Section 3 (Authority and Boundaries Matrix) to state:
```markdown
- **Unmapped Paths (Default Deny / Black Zone):** Any file or directory not explicitly listed in Green, Yellow, or Red zones is strictly Red Zone by default.
```

- [x] **Step 4: Run integrity tests to ensure template conformity**

Run: `python -m unittest discover -s tests -p "test_*.py" -v`
Expected: 4 tests pass (`OK`).

---

### Task 3: Expand Automated Integrity Suite (`tests/test_integrity.py`)

**Files:**
- Modify: `tests/test_integrity.py`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Invariants defined in `templates/project_knowledge/boundaries.md`, `templates/project_knowledge/architecture.md`, `templates/team/system_prompt.md`
- Produces: 3 new test methods verifying structural presence of Default Deny, Circuit Breaker, and Data Flow schemas

- [x] **Step 1: Write failing tests in `tests/test_integrity.py` with bilingual regex support**

Add tests to class `TestTemplatesIntegrity` using regex patterns supporting both English and Russian canonical variants:
```python
    def test_boundaries_default_deny_invariant(self):
        """Verify boundaries template contains the Default Deny / Black Zone rule."""
        boundaries_path = TEMPLATES_DIR / "project_knowledge" / "boundaries.md"
        content = boundaries_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Default Deny|Black Zone|Запрет по умолчанию|Черная зона", content, re.IGNORECASE),
            "boundaries.md template must define Default Deny / Black Zone rule"
        )

    def test_system_prompt_circuit_breaker_invariant(self):
        """Verify role system prompt template contains Circuit Breaker and Target State Audit."""
        prompt_path = TEMPLATES_DIR / "team" / "system_prompt.md"
        content = prompt_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Circuit Breaker|Стоп-кран|Circuit-breaker", content, re.IGNORECASE),
            "system_prompt.md template must define Circuit Breaker rule"
        )
        self.assertTrue(
            re.search(r"Target State Audit|Аудит состояния объекта", content, re.IGNORECASE),
            "system_prompt.md template must define Target State Audit rule"
        )

    def test_architecture_data_flow_section(self):
        """Verify architecture template contains Data Flow section."""
        arch_path = TEMPLATES_DIR / "project_knowledge" / "architecture.md"
        content = arch_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Data Flow|Потоки данных|Pre-Flight Flow Tracing", content, re.IGNORECASE),
            "architecture.md template must define Data Flows section"
        )
```

- [x] **Step 2: Run test suite to verify new assertions pass with Task 1 & 2 templates**

Run: `python -m unittest discover -s tests -p "test_*.py" -v`
Expected: 7 tests pass (`OK`).

- [x] **Step 3: Commit template and test changes**

Commit message: `feat(templates): implement Default Deny, Circuit Breaker, and Data-Flow invariants with integrity test coverage`

---

### Task 4: Upgrade Procedural Skills (`skills/init-meta-project`, `skills/manage-meta-project`)

**Files:**
- Modify: `skills/init-meta-project/SKILL.md`
- Modify: `skills/manage-meta-project/SKILL.md`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Updated templates and rules from Tasks 1, 2, and 3
- Produces: Production-ready scaffolding skills incorporating polyglot isolation, mandatory dispatcher routing, and 100% path mapping

- [x] **Step 1: Upgrade `skills/init-meta-project/SKILL.md`**

1. In Phase 1 & 2: Add explicit rule **Zero Unmapped Dirs (with noise filtering)**:
   - The scanner must list all real source-code top-level directories in the repository root.
   - Strictly filter out `.gitignore` paths, VCS metadata, and standard build/package/test caches (`.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `coverage`, `__pycache__`, `.pytest_cache`, `.idea`, `.vscode`).
   - Every remaining top-level source directory must be mapped to Green, Yellow, or Red zone in `boundaries.md`.
2. In Section on `architecture.md`: Generate the **End-to-End Data Flows** section conditionally (only when multi-tier, client-server, API, or UI components are detected; for pure CLI/stdlib packages, omit to prevent context bloat).
3. Synchronize embedded templates in `init-meta-project/SKILL.md` with the updated files from `templates/`.

- [x] **Step 2: Upgrade `skills/manage-meta-project/SKILL.md`**

1. In Phase 1 (Rapid Repository Scan): Add explicit marker inspection for **Secondary / Polyglot Stacks** (presence of `.cpp`, `.c`, `.h`, `.rs`, `.go` in subdirectories like `client/`, `native/`, `core/`).
2. In Phase 2 (Scale-Adaptive Sizing & Open Competency Matrix):
   - Add **Polyglot Stack Isolation Rule:** Forbid bundling secondary compiled stacks into `agent-general-worker` without specialized skills. Mandate either synthesizing a dedicated role (e.g. `agent-native-desktop`) or explicitly placing native directories into Red Zone with a mandatory Handoff requirement.
   - Add **Mandatory Dispatcher Rule (No Multi-Role Chaos):** When deploying 3 or more specialized roles, deploying an intake dispatcher (`agent-intake-dispatcher` or an integrated dispatcher in `agent-dev-lead`) is strictly mandatory. Forbid leaving the user with an unrouted bundle of 5 isolated roles.
3. In Phase 6 (Rules of Engagement):
   - Add **Circuit Breaker** and **Target State Audit** to the rules of engagement.
   - Add **Toolchain Handoff Tripwires** (compiler errors trigger immediate Handoff to devops/infra).
4. Synchronize embedded templates (`profile.md`, `system_prompt.md`) in `manage-meta-project/SKILL.md`.

- [x] **Step 3: Run integrity tests to verify skills frontmatter and sections**

Run: `python -m unittest discover -s tests -p "test_*.py" -v`
Expected: 7 tests pass (`OK`).

- [x] **Step 4: Commit skill upgrades**

Commit message: `feat(skills): add polyglot isolation, mandatory dispatcher, and Zero Unmapped Dirs to init and manage skills`

---

### Task 5: Live Workspace Knowledge & Team Alignment

**Files:**
- Modify: `AGENTS.md` (root)
- Modify: `.agents/project_knowledge/boundaries.md`
- Modify: `.agents/project_knowledge/architecture.md`
- Modify: `.agents/skills/init-meta-project/SKILL.md` (sync from `skills/`)
- Modify: `.agents/skills/manage-meta-project/SKILL.md` (sync from `skills/`)
- Modify: `.agents/team/agent-dev-lead/system_prompt.md`
- Modify: `.agents/team/agent-quality-guardian/system_prompt.md`
- Modify: `.agents/team/agent-github-steward/system_prompt.md`
- Test: `tests/test_integrity.py`

**Interfaces:**
- Consumes: Updated skills and templates
- Produces: Coherent, verified live repository state aligned with latest meta-project standards

- [x] **Step 1: Update live `.agents/project_knowledge/boundaries.md` and `architecture.md`**

1. In `.agents/project_knowledge/boundaries.md`, add Default Deny / Black Zone rule.
2. In `.agents/project_knowledge/architecture.md`, add End-to-End Data Flows diagram and schema.

- [x] **Step 2: Update live root `AGENTS.md`**

Incorporate Circuit Breaker, Pre-Flight Flow Tracing, and Default Deny into the live project passport.

- [x] **Step 3: Update live role system prompts in `.agents/team/*/system_prompt.md`**

Update `agent-dev-lead`, `agent-quality-guardian`, and `agent-github-steward` system prompts with:
- Silent internal verification (no prompt theater).
- Circuit Breaker rule.
- Target State Audit checklist.
- Mandatory observations logging trigger.

- [x] **Step 4: Sync local repo skills in `.agents/skills/`**

Ensure `.agents/skills/` mirrors `skills/`.

- [x] **Step 5: Run full test suite to verify zero broken windows**

Run: `python -m unittest discover -s tests -p "test_*.py" -v`
Expected: 7 tests pass (`OK`).

- [x] **Step 6: Commit live environment updates**

Commit message: `chore(meta): align live knowledge slices and team prompts with polyglot remediation standards`

---

### Task 6: Global Antigravity Skills Synchronization

> [!IMPORTANT]
> **User Authorization Required:** Modifying files in `~/.gemini/config/skills/*` affects the user's global Antigravity installation outside this repository. In accordance with Red Zone policy, Task 6 must be executed ONLY upon explicit confirmation from the user after Tasks 1–5 are verified.

**Files:**
- Modify: `~/.gemini/config/skills/init-meta-project/SKILL.md`
- Modify: `~/.gemini/config/skills/manage-meta-project/SKILL.md`

**Interfaces:**
- Consumes: Canonical upgraded skills from `skills/`
- Produces: Updated global skills in Antigravity user configuration directory

- [x] **Step 1: Copy upgraded `skills/init-meta-project/SKILL.md` to global config**

Copy file from `skills/init-meta-project/SKILL.md` to `~/.gemini/config/skills/init-meta-project/SKILL.md`.

- [x] **Step 2: Copy upgraded `skills/manage-meta-project/SKILL.md` to global config**

Copy file from `skills/manage-meta-project/SKILL.md` to `~/.gemini/config/skills/manage-meta-project/SKILL.md`.

- [x] **Step 3: Verify global skills exist and pass frontmatter checks**

Run Python one-liner to verify global skill files have valid YAML frontmatter and required sections.

- [x] **Step 4: Run full project test suite final verification**

Run: `python -m unittest discover -s tests -p "test_*.py" -v`
Expected: 7 tests pass (`OK`).

---

## Self-Review Checklist

- **Spec Coverage:**
  - Default Deny / 100% path coverage ➔ Task 1 & Task 4.
  - Elimination of prompt theater ➔ Task 2.
  - Polyglot stack detection & isolation (no toxic bundles) ➔ Task 4.
  - Mandatory dispatcher routing (>2 roles) ➔ Task 4.
  - Circuit Breaker & Target State Audit ➔ Task 2, Task 3, Task 4.
  - Pre-Flight Flow Tracing & Data Flow schema ➔ Task 1, Task 3, Task 5.
  - Automated integrity verification ➔ Task 3.
  - Centralized skill curation ➔ Global constraints & Task 6.
- **Placeholder Scan:** Zero placeholders, exact files, paths, and test commands provided.
- **Dependency Invariant:** Pure standard library Python only (`unittest`, `pathlib`, `re`).
