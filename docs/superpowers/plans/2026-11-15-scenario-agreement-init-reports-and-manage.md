# Implementation Plan: Scenario Agreement, Initialization Reports, and Scenario-Driven Team Management

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.  
> **Execution Protocol:** Multi-Agent Lifecycle (`agent-dev-lead` ➔ `agent-quality-guardian` ➔ `agent-github-steward`).  
> **Target Baseline:** Commit `37d864b` (`feat(init): introduce deterministic inspection engine, self-contained passport, and universal adoption protocol`).  
> **Core Invariants:** Zero-dependency stdlib policy (Python 3.10+), Non-Destructive History Invariant, Survey-First Zero-Write, Explicit User Decision Separation, Machine Boundary Gate, and Strict Multi-Harness Identity Isolation.

**Goal:** Establish a deterministic contract and machine-readable handoff protocol between `init-meta-project` and `manage-meta-project` via structured scenario agreement, formal initialization reports (`.agents/reports/<installation_id>/init/<init_run_id>.json`), and scenario-driven team management reports (`.agents/reports/<installation_id>/manage/<manage_run_id>.json`).

**Architecture:** A two-stage pipeline where `init-meta-project` surveys the repository and formalizes user decisions into a validated `scenario` in `.agents/meta-project.json` and a machine-readable init report. `manage-meta-project` consumes the verified report, cross-references project boundaries and harness capabilities, plans an appropriate role topology (solo, duo, triad, specialized), executes minimal role adjustments, and produces a manage report linking back to the initialization run.

**Tech Stack:** Python 3.10+ (standard library only: `json`, `pathlib`, `unittest`, `argparse`, `dataclasses`, `subprocess`, `datetime`, `uuid`), Markdown templates.

**Spec:** User specification for Migration Preparation Part 2 ("Вторая часть плана: согласование сценария → отчёт инициализации → настройка команды через manage-meta-project") and ADR #20 ("Scenario Agreement & Formal Hand-off Reports between Init and Manage").

## Global Constraints

- **Zero-Dependency Invariant:** All report generators, schema validators, inspection routines, and tests must run exclusively on the Python 3.10+ standard library.
- **Survey-First Zero-Write:** An inspection or audit run (invoked with `--read-only` or when no changes are requested) must produce strictly 0 file writes, 0 report files, and 0 lock artifacts.
- **Explicit Separation of Truth:** System outputs and reports must strictly separate User Decisions, Established Facts, and Agent Recommendations. Agent proposals must never be recorded as approved user decisions without explicit confirmation.
- **Non-Destructive History Invariant:** Existing active harness installations, historical telemetry, role notes (`notes.md`), and accumulated observations (`observations.md`) must never be deleted, truncated, or overwritten.
- **Multi-Harness Identity Invariant:** Operating on or connecting a new harness (e.g. `zc-main`) must never mutate or deactivate bindings of existing active harnesses (e.g. `ag-main`). Archiving a role is permitted only if no active or planned installations reference it.
- **Status Truthfulness:** The states `planned`, `prepared` (staged files), and `verified` (tested in live harness) must never be conflated. A created profile file does not prove it is active in the harness.
- **Fail-Closed Gate:** If an init report is missing, corrupted, marked `awaiting_decision`, or `blocked`, `manage-meta-project` must refuse team modification and request user clarification or limited re-survey.

---

## File Structure & Responsibilities

| Path | Responsibility |
|---|---|
| `scripts/manage_reports.py` | Core CLI and library for generating, validating, locating, and inspecting initialization and management JSON reports (Python 3.10+ stdlib). |
| `templates/reports/init_report.json` | Canonical schema and golden template for `init` run reports. |
| `templates/reports/manage_report.json` | Canonical schema and golden template for `manage` run reports. |
| `tests/test_manage_reports.py` | Unit and adversarial test suite for report schemas, validation, latest lookup, and atomic file writes. |
| `.agents/meta-project.json` | Project identity and configuration registry, updated to schema version `1.1.0` with canonical `scenario` block. |
| `scripts/verify_identity.py` | Extended identity validator verifying the `scenario` block and schema `1.1.0`. |
| `scripts/inspect_meta_project.py` | Extended survey CLI reporting scenario status and references to latest init reports. |
| `skills/init-meta-project/SKILL.md` | Refactored skill incorporating Phase 2 (Scenario Agreement) and Phase 4 (Init Report Generation). |
| `skills/manage-meta-project/SKILL.md` | Refactored skill incorporating pre-flight report intake, scenario-dependent team planning, and manage report creation. |
| `tests/test_report_and_manage_cycle.py` | End-to-end integration test suite verifying the 8 mandatory acceptance scenarios of the init ➔ manage cycle. |
| `.agents/project_knowledge/boundaries.md` | Updated boundary policy explicitly mapping `.agents/reports/**` to Yellow Zone. |
| `templates/project_knowledge/boundaries.md` | Canonical boundary template mirror updated with `.agents/reports/**`. |
| `templates/AGENTS.md` & `AGENTS.md` | Section 5 updated with `scripts/manage_reports.py` in Local Verification Tooling. |
| `docs/decisions_and_roadmap.md` | Updated roadmap and formalization of ADR #20. |

---

## Detailed Task Breakdown

### Task 1: Report Contract Specification & Engine (`scripts/manage_reports.py`)

**Files:**
- Create: `scripts/manage_reports.py`
- Create: `templates/reports/init_report.json`
- Create: `templates/reports/manage_report.json`
- Create: `tests/test_manage_reports.py`

**Interfaces:**
- Consumes: `sys`, `json`, `pathlib`, `argparse`, `datetime`, `uuid`, `subprocess`, `inspect_meta_project.py` (capabilities format)
- Produces: CLI `scripts/manage_reports.py [init|manage|latest|verify]` and library functions `create_init_report()`, `create_manage_report()`, `validate_report()`, `get_latest_report()`.

#### Step 1.1: Write failing unit and adversarial tests
Create `tests/test_manage_reports.py`:
- `test_init_report_schema_validation_passes`: Valid init report passes validation.
- `test_init_report_missing_mandatory_field_fails`: Omitting `scenario` or `actor_id` raises fail-closed validation error.
- `test_manage_report_requires_init_run_id`: Manage report without `init_run_id` fails validation.
- `test_atomic_write_and_latest_symlink_or_pointer`: Report writes safely and updates latest pointer without race conditions.
- `test_corrupted_json_fails_closed`: Corrupted report file returns graceful failure, not crash.
- `test_cli_init_create_and_verify`: CLI interface execution verification.

#### Step 1.2: Run test to confirm RED phase
Run: `python -m unittest tests/test_manage_reports.py`  
Expected: FAIL (`ModuleNotFoundError: No module named 'scripts.manage_reports'`)

#### Step 1.3: Implement `scripts/manage_reports.py` and templates
Implement zero-dependency engine:
- Report schema `1.0.0` for `init` and `manage`.
- Strict fields: `schema_version`, `project_id`, `installation_id`, `harness_id`, `actor_id`, `run_id`, `created_at`, `status` (`completed`, `awaiting_decision`, `blocked`), `git_state`, `references`, `scenario`, `environment`, `components`, `checks`, `recommendations_for_manage`, `blockers_and_unresolved`, `next_step_readiness`.
- `manage` report fields: `init_run_id`, `roles` (`preserved`, `created`, `adapted`, `archived`), `bindings`, `effective_capabilities`, `checks`, `remaining_manual_actions`.
- CLI subcommands:
  - `python scripts/manage_reports.py init --action create --installation <id> --harness <harness> --actor <actor> --status <status> --data <json_or_args>`
  - `python scripts/manage_reports.py init --action verify --report <path>`
  - `python scripts/manage_reports.py manage --action create --installation <id> --init-run-id <run_id> --data <json_or_args>`
  - `python scripts/manage_reports.py latest --installation <id> --type [init|manage]`

#### Step 1.4: Run tests to confirm GREEN phase
Run: `python -m unittest tests/test_manage_reports.py`  
Expected: PASS (all tests pass)

---

### Task 2: Registry Schema 1.1.0 & Scenario Configuration

**Files:**
- Modify: `.agents/meta-project.json`
- Modify: `scripts/verify_identity.py`
- Modify: `scripts/inspect_meta_project.py`
- Modify: `tests/test_verify_identity.py`
- Modify: `tests/test_inspect_meta_project.py`

**Interfaces:**
- Consumes: `.agents/meta-project.json`, `scripts/manage_reports.py:get_latest_report`
- Produces: `schema_version: "1.1.0"`, `"scenario"` key in registry, extended survey diagnostics in `inspect_meta_project.py`.

#### Step 2.1: Write failing tests for Scenario validation and inspection
In `tests/test_verify_identity.py` and `tests/test_inspect_meta_project.py`:
- `test_registry_with_valid_scenario_passes_verification`: Registry containing scenario block passes.
- `test_registry_invalid_scenario_profile_fails`: Profile not in allowed enum (`active_development`, `maintenance`, `research`, `audit`, `documentation`) reports validation error.
- `test_inspector_surfaces_agreed_scenario_and_latest_init_report`: `inspect_meta_project.py` reports scenario and latest init report in JSON output.

#### Step 2.2: Confirm RED phase
Run: `python -m unittest tests/test_verify_identity.py tests/test_inspect_meta_project.py`  
Expected: FAIL on new checks.

#### Step 2.3: Update registry and scripts
- In `.agents/meta-project.json`: bump `schema_version` to `"1.1.0"` and add canonical `scenario` block for current project:
  ```json
  "scenario": {
    "profile": "active_development",
    "deployment_mode": "shared_repo",
    "collaboration_model": "triad",
    "verification_policy": "strict_independent",
    "delegation_level": "controlled",
    "constraints": [
      "zero_dependency_core",
      "fail_closed_boundaries"
    ],
    "unresolved_questions": []
  }
  ```
- In `scripts/verify_identity.py`: add `validate_scenario_section(registry)` ensuring enum checks and required keys.
- In `scripts/inspect_meta_project.py`: add `scenario` and `latest_init_report` fields to inspection dictionary.

#### Step 2.4: Confirm GREEN phase
Run: `python -m unittest tests/test_verify_identity.py tests/test_inspect_meta_project.py`  
Expected: PASS

---

### Task 3: Survey-First `init-meta-project` Refactoring (Scenario Agreement & Init Report)

**Files:**
- Modify: `skills/init-meta-project/SKILL.md`
- Modify: `.agents/skills/init-meta-project/SKILL.md`
- Modify: `scripts/sync_templates.py`

**Interfaces:**
- Consumes: `scripts/inspect_meta_project.py`, `scripts/manage_reports.py`
- Produces: Multi-phase protocol: Phase 1 (Survey), Phase 2 (Scenario Agreement), Phase 3 (Preparation & Scaffolding), Phase 4 (Report Generation & Manage Handoff).

#### Step 3.1: Refactor `skills/init-meta-project/SKILL.md`
- Embed the 4 Scenario Agreement Dimensions:
  1. **Application:** `active_development` | `maintenance` | `research` | `audit` | `documentation`
  2. **Placement:** `shared_repo` | `local_overlay` | `hybrid`
  3. **Collaboration:** `solo` | `duo` | `triad` | `specialized_swarm`
  4. **Execution Rules:** `self_check` | `duo_peer_review` | `strict_independent` (with delegation constraints and platform limits)
- Add Agreement Protocol:
  - On repeat run in `HEALTHY_REGISTERED`: do NOT re-interview; reuse existing scenario.
  - On conflict between desires and environment capabilities: present explicit binary choices.
  - Separate User Decisions, Facts, and Recommendations.
- Add Phase 4 (Initialization Report Generation):
  - Command: `python scripts/manage_reports.py init --action create ...`
  - Output human-readable summary in chat.
  - Explicit rule: Team deployment is NOT automatically done; handoff to `manage-meta-project` is recommended.
- Synchronize to `.agents/skills/init-meta-project/SKILL.md` via `scripts/sync_templates.py --write`.

#### Step 3.2: Confirm integrity and drift
Run: `python scripts/sync_templates.py --check && python -m unittest tests/test_integrity.py`  
Expected: PASS (0 drift, all integrity tests pass).

---

### Task 4: Scenario-Driven `manage-meta-project` Refactoring (Report Intake & Team Topology)

**Files:**
- Modify: `skills/manage-meta-project/SKILL.md`
- Modify: `.agents/skills/manage-meta-project/SKILL.md`
- Modify: `scripts/sync_templates.py`

**Interfaces:**
- Consumes: Latest init report from `.agents/reports/<installation_id>/init/`, `.agents/meta-project.json`
- Produces: Scenario-driven team topologies (solo, duo, triad, specialized) and manage report generation via `scripts/manage_reports.py manage`.

#### Step 4.1: Refactor `skills/manage-meta-project/SKILL.md`
- Step 1: Pre-flight Report Intake:
  - Run `python scripts/manage_reports.py latest --type init --installation <id>`.
  - Validate schema compatibility, matching project_id and installation_id.
  - Check staleness against current git revision. If stale, run limited re-survey (`python scripts/inspect_meta_project.py --json`), do NOT wipe existing config.
  - Fail-closed: If report status is `awaiting_decision` or `blocked`, HALT and present required decisions to user.
- Step 2: Scenario-Driven Team Topology Planning:
  - Map scenario to team structure:
    * `documentation` / `research` ➔ Solo Executor
    * `maintenance` / compact repo (<3-5k LOC) ➔ Tier 0 Duo (`agent-dev-lead` + `agent-quality-guardian`)
    * `active_development` + `strict_independent` ➔ Canonical Triad (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`)
    * Multi-stack / microservices ➔ Specialized Team
  - Enforce action differentiation:
    1. Preserve existing team (no-op on healthy active bindings).
    2. Adjust duties / update prompts.
    3. Add missing role.
    4. Connect existing roles to new harness (without duplicating profiles or overwriting active bindings).
    5. Archive unused role (strictly verify no other installation references it).
- Step 3: Manage Report Generation:
  - Run `python scripts/manage_reports.py manage --action create ... --init-run-id <run_id>`.
  - Record preserved, created, adapted, and archived roles.
  - Record remaining manual actions.
  - Explicit rule: Created profile does not equal loaded by harness. Agent executing manage does NOT automatically switch identity.

#### Step 4.2: Synchronize and verify mirrors
Run: `python scripts/sync_templates.py --write && python scripts/sync_templates.py --check`  
Expected: PASS (0 drift).

---

### Task 5: Comprehensive Acceptance Test Suite (`tests/test_report_and_manage_cycle.py`)

**Files:**
- Create: `tests/test_report_and_manage_cycle.py`

**Interfaces:**
- Consumes: `scripts/manage_reports.py`, `scripts/inspect_meta_project.py`, `scripts/verify_identity.py`, `skills/`
- Produces: 8 mandatory end-to-end integration tests in isolated `tempfile.TemporaryDirectory` sandboxes.

#### Step 5.1: Implement 8 Mandatory Acceptance Tests
1. `test_scenario_agreement_persisted_in_registry`: Validates that user choices in all 4 dimensions are persisted in `meta-project.json` without data corruption.
2. `test_init_report_generation_and_contract`: Validates that init report contains all required fields and links to passport, boundaries, and registry.
3. `test_read_only_mode_never_generates_reports`: Validates that running survey with `--read-only` generates strictly 0 files in `.agents/reports/`.
4. `test_manage_rejects_foreign_or_incompatible_report`: Validates fail-closed behavior when report has mismatched `project_id` or unsupported schema.
5. `test_manage_blocked_on_awaiting_decision`: Validates that manage halts if init report is `awaiting_decision` or `blocked`.
6. `test_manage_adapts_team_based_on_scenario`: Validates that scenario `maintenance` produces Duo, while `active_development` produces Triad.
7. `test_manage_preserves_other_harness_bindings`: Validates that configuring roles for `zc-main` preserves `ag-main` bindings and notes.
8. `test_stale_report_triggers_opportunistic_resurvey_without_full_reinit`: Validates that git commit delta triggers opportunistic check rather than full reset.

#### Step 5.2: Execute test suite
Run: `python -m unittest tests/test_report_and_manage_cycle.py -v`  
Expected: PASS (all 8 scenarios pass).

---

### Task 6: Boundaries, Passport Parity, Documentation, ADR #20, and Release Commit

**Files:**
- Modify: `.agents/project_knowledge/boundaries.md`
- Modify: `templates/project_knowledge/boundaries.md`
- Modify: `templates/AGENTS.md`
- Modify: `AGENTS.md`
- Modify: `.agents/project_knowledge/architecture.md`
- Modify: `.agents/project_knowledge/tasks.md`
- Modify: `docs/decisions_and_roadmap.md`
- Modify: `.agents/team/*/profile.md`

#### Step 6.1: Update boundaries
Map `.agents/reports/**` into Yellow Zone in `boundaries.md` and `templates/project_knowledge/boundaries.md`:
```markdown
- `.agents/reports/**` — initialization and team management audit reports.
```
Run boundary audit:
`python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree`  
Expected: 100% boundary coverage.

#### Step 6.2: Update project passport
Add `manage_reports.py` to Section 5 (Local Verification Tooling) in `templates/AGENTS.md` and root `AGENTS.md`:
```markdown
- **Initialization & Management Report Audit:**
  `python scripts/manage_reports.py [init|manage|latest|verify]`
```
Run template sync:
`python scripts/sync_templates.py --write && python scripts/sync_templates.py --check`

#### Step 6.3: Record ADR #20 in `docs/decisions_and_roadmap.md`
Formulate ADR #20: "Scenario Agreement & Formal Hand-off Reports between Init and Manage":
- Context, problem, decision, invariants, schema contracts, and outcomes.

#### Step 6.4: Update architecture and tasks
- Update `.agents/project_knowledge/architecture.md` with `scripts/manage_reports.py` and report data flows.
- Register completed steps in `.agents/project_knowledge/tasks.md`.
- Log telemetry row in each role profile (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`).

#### Step 6.5: Full Verification and Conventional Commit
- `python scripts/verify_identity.py --check`
- `python scripts/sync_templates.py --check`
- `python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree`
- `python -m unittest discover tests` (all tests pass)
- `git status`
- Commit: `feat(reports): introduce scenario agreement protocol, init reports, and scenario-driven team management`

---

## Sequential Prompts for Repository Agent Roles

### Prompt 1.1: Core Report Engine & Schemas (`agent-dev-lead`)
```text
@agent-dev-lead implement feature: разработка движка отчётов scripts/manage_reports.py и схем отчётов

Контекст: В рамках реализации второй части плана подготовки к миграции (согласование сценария ➔ отчёт инициализации ➔ настройка команды через manage-meta-project) требуется разработать легковесный zero-dependency инструмент на Python 3.10+ stdlib для создания, валидации и поиска отчётов инициализации и управления командой.

Задача:
1. Создай канонические шаблоны отчётов:
   - templates/reports/init_report.json (schema_version: "1.0.0")
   - templates/reports/manage_report.json (schema_version: "1.0.0")
2. В tests/test_manage_reports.py напиши unit- и adversarial-тесты (TDD Red phase):
   - test_init_report_schema_validation_passes
   - test_init_report_missing_mandatory_field_fails
   - test_manage_report_requires_init_run_id
   - test_atomic_write_and_latest_symlink_or_pointer
   - test_corrupted_json_fails_closed
   - test_cli_init_create_and_verify
3. Реализуй scripts/manage_reports.py:
   - CLI: init, manage, latest, verify.
   - Поддержка путей: .agents/reports/<installation_id>/init/<init_run_id>.json и .agents/reports/<installation_id>/manage/<manage_run_id>.json.
   - Детерминированная генерация run_id (ISO UTC timestamp + short uuid).
   - Атомарная запись через временный файл и безопасное обновление latest.json.
   - Извлечение данных Git (ревизия HEAD, ветка, статус рабочей копии).
   - Валидация обязательных полей и статусов (completed, awaiting_decision, blocked).
4. Добейся прохождения тестов:
   python -m unittest tests/test_manage_reports.py
5. Добавь запись о шаге в .agents/project_knowledge/tasks.md и 1 строку телеметрии в .agents/team/agent-dev-lead/profile.md.
```

### Prompt 2.1: Registry Schema 1.1.0 & Scenario Agreement (`agent-dev-lead`)
```text
@agent-dev-lead develop component: обновление реестра .agents/meta-project.json до схемы 1.1.0 с поддержкой согласованного сценария и расширение инспектора

Контекст: Разработан движок отчётов. Требуется формализовать блок согласованного сценария в действующей конфигурации проекта и интегрировать его с инспектором и валидатором идентичности.

Задача:
1. В tests/test_verify_identity.py и tests/test_inspect_meta_project.py добавь тесты:
   - test_registry_with_valid_scenario_passes_verification
   - test_registry_invalid_scenario_profile_fails
   - test_inspector_surfaces_agreed_scenario_and_latest_init_report
2. В .agents/meta-project.json:
   - Обнови schema_version до "1.1.0".
   - Добавь каноническую секцию "scenario" (profile: "active_development", deployment_mode: "shared_repo", collaboration_model: "triad", verification_policy: "strict_independent", delegation_level: "controlled", constraints, unresolved_questions: []).
3. В scripts/verify_identity.py:
   - Добавь проверку секции scenario (валидация enum профилей, режима размещения, политики верификации).
4. В scripts/inspect_meta_project.py:
   - Добавь вывод согласованного сценария и ссылки на актуальный init-отчёт в JSON-выводе.
5. Проверь прохождение тестов:
   python -m unittest tests/test_verify_identity.py tests/test_inspect_meta_project.py
6. Добавь запись в tasks.md и строку телеметрии в agent-dev-lead/profile.md.
```

### Prompt 3.1: Alignment of `init-meta-project` & `manage-meta-project` Skills (`agent-dev-lead`)
```text
@agent-dev-lead develop component: переработка процедурных навыков init-meta-project и manage-meta-project на протокол согласования сценария и отчётов

Контекст: Движок отчётов и конфигурация сценария разработаны. Требуется связать procedural skills в единый двухстадийный пайплайн с передачей проверенного контекста.

Задача:
1. В skills/init-meta-project/SKILL.md:
   - Внедри Фазу 2 (Scenario Agreement) после обследования: опрос/согласование 4 измерений (Application, Placement, Collaboration, Execution Rules).
   - Правило повторного запуска: при HEALTHY_REGISTERED не переспрашивать, использовать существующий сценарий.
   - Разделение: решения пользователя, факты и рекомендации агента.
   - Внедри Фазу 4 (Report Generation): генерация .agents/reports/<installation_id>/init/<init_run_id>.json через scripts/manage_reports.py.
   - Явное правило: развёртывание команды НЕ выполняется автоматически; даётся рекомендация вызвать manage-meta-project.
2. В skills/manage-meta-project/SKILL.md:
   - Внедри Шаг 1 (Pre-flight Report Intake): чтение и валидация актуального отчёта через scripts/manage_reports.py latest --type init.
   - Fail-closed: если статус awaiting_decision или blocked, остановить выполнение.
   - При устаревании отчёта — ограниченное повторное обследование (не полный сброс).
   - Внедри Шаг 2 (Scenario-Driven Topology Planning): выбор топологии (solo, duo, triad, specialized) на основе сценария и стека, а не только LOC.
   - Чёткое разделение действий: сохранить, адаптировать, добавить, подключить харнесс, архивировать.
   - Внедри Шаг 3 (Manage Report Generation): создание manage-отчёта со ссылкой на init_run_id.
3. Выполни синхронизацию зеркал:
   python scripts/sync_templates.py --write
   python scripts/sync_templates.py --check
4. Проверь целостность:
   python -m unittest tests/test_integrity.py
5. Добавь запись в tasks.md и строку телеметрии в agent-dev-lead/profile.md.
```

### Prompt 4.1: Acceptance Test Suite for the 8 Scenarios (`agent-quality-guardian`)
```text
@agent-quality-guardian verify meta-project structure: разработка полного приёмочного тестового набора для цикла согласования, отчётов и управления командой

Контекст: Реализована вторая часть миграционного плана. Требуется провести независимую проверку и автоматизировать контроль 8 ключевых инвариантов и сценариев взаимодействия init и manage.

Задача:
1. Создай tests/test_report_and_manage_cycle.py с тестами в изолированных temp-каталогах:
   - test_scenario_agreement_persisted_in_registry: корректное сохранение решений по 4 группам.
   - test_init_report_generation_and_contract: формирование отчёта со всеми обязательными ссылками и полями.
   - test_read_only_mode_never_generates_reports: инвариант строго 0 записей при --read-only.
   - test_manage_rejects_foreign_or_incompatible_report: fail-closed отказ при чужом project_id или несовместимой схеме.
   - test_manage_blocked_on_awaiting_decision: блокировка развёртывания при статусе awaiting_decision / blocked.
   - test_manage_adapts_team_based_on_scenario: корректный выбор Solo/Duo/Triad по согласованному сценарию.
   - test_manage_preserves_other_harness_bindings: сохранение активных привязок ag-main при операциях с zc-main.
   - test_stale_report_triggers_opportunistic_resurvey_without_full_reinit: устойчивость к изменению коммитов без стирания настроек.
2. Запусти приёмочный набор и полный тестовый прогон:
   python -m unittest tests/test_report_and_manage_cycle.py -v
   python -m unittest discover tests
3. Проверь отсутствие деструктивных правок, сохранение истории и заметок ролей.
4. Добавь запись в tasks.md и строку телеметрии в agent-quality-guardian/profile.md.
```

### Prompt 5.1: Boundaries, Documentation Parity, and Release Commit (`agent-github-steward`)
```text
@agent-github-steward git hygiene: обновление политик границ, паспорта, документации решений (ADR #20) и фиксация релиза

Контекст: Все компоненты движка отчётов, схемы и приёмочные тесты успешно реализованы и проверены Quality Guardian. Требуется актуализировать границы ответственности, документацию решений и зафиксировать атомарный коммит.

Задача:
1. В boundaries.md и templates/project_knowledge/boundaries.md:
   - Добавь явное правило для .agents/reports/** в Жёлтую зону.
   - Проверь 100% покрытие: python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
2. В templates/AGENTS.md и root AGENTS.md:
   - Добавь утилиту scripts/manage_reports.py в секцию 5 (Local Verification Tooling).
   - Выполни синхронизацию: python scripts/sync_templates.py --write && python scripts/sync_templates.py --check
3. В docs/decisions_and_roadmap.md:
   - Зафиксируй ADR #20: "Scenario Agreement & Formal Hand-off Reports between Init and Manage" с обоснованием, контрактами схем и инвариантами.
4. Актуализируй .agents/project_knowledge/architecture.md и tasks.md.
5. Проверь чистоту рабочей копии и отсутствие побочных изменений:
   python scripts/verify_identity.py --check
   python -m unittest discover tests
   git status
6. Сформируй атомарный Conventional Commit:
   feat(reports): introduce scenario agreement protocol, init reports, and scenario-driven team management
7. Внеси запись телеметрии в agent-github-steward/profile.md.
```
