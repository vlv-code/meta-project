# Implementation Plan: Universal Repository Adoption & Deterministic Inspection (`init-meta-project`)

> **Execution Protocol:** Multi-Agent Lifecycle (`agent-dev-lead` ➔ `agent-quality-guardian` ➔ `agent-github-steward`).  
> **Target Baseline:** Commit `2dff18a` (`feat(identity): establish multi-harness identity registry and migration preparation`).  
> **Core Invariants:** Zero-dependency stdlib policy (Python 3.10+), Non-Destructive History Invariant, Survey-First (Zero-Write Inspection), Default Closed Tooling, and Fail-Closed Boundaries.

---

## 1. Context, Objectives, and Constraints

### 1.1 Background & Problem Statement
With the establishment of the multi-harness identity model (`actor_id = <project_id>::<harness_id>::<installation_id>::<role_id>`) in commit `2dff18a`, the repository ecosystem can unambiguously identify active and planned agents across platforms (Antigravity, ZCode).

However, `init-meta-project` currently operates primarily as a greenfield scaffolder or ad-hoc updater. It conflates **survey (discovery/audit)** with **execution (modification)**, assumes that the presence of `AGENTS.md` guarantees Meta-Project compliance, and relies heavily on external global skills (`python-pro`, `clean-code`). When introduced into unfamiliar repositories or when an agent lacks global environment skills, this causes:
1. Premature modification of foreign rule files (`CLAUDE.md`, `.cursorrules`, foreign `AGENTS.md`).
2. Lock file generation, telemetry row spam, and cache generation during pure inspection/audit requests.
3. Inability for an agent without global Meta-Project skills to navigate the repository autonomously using self-contained local instructions and zero-dependency CLI tools.
4. Ambiguity when running in `git worktree` environments or multi-harness target environments.

### 1.2 Core Goals
1. **Transform `init-meta-project` into a Universal Adoption Gateway:** A single deterministic entry point for greenfield scaffolding, foreign rule coexistence, legacy migration, multi-harness adaptation, and healthy repo verification.
2. **Dual-Entry Architecture:** Establish two aligned entry points:
   - *Procedural Entry:* Invocation of the `init-meta-project` skill.
   - *Declarative Entry:* Canonical README badge and onboarding block routing agents to `AGENTS.md` and fallback local CLI commands.
3. **Decouple Survey from Execution:** Guarantee that Phase 1 (Inspection) is strictly read-only: zero file modifications, zero telemetry spam, zero lock files, zero cache generation, and no execution of untrusted scripts or hooks.
4. **Deterministic stdlib Inspector (`scripts/inspect_meta_project.py`):** Pure Python 3.10+ CLI producing structured JSON and human-readable diagnostics for the 7 canonical states, schema validation, capability matrix, and worktree awareness.
5. **Self-Contained Project Passport (`templates/AGENTS.md`):** Ensure any agent landing in the repository can inspect boundaries, identify its role, run verification tests, and execute tasks using local stdlib commands without depending on external global skills.
6. **Capability & Readiness Levels Matrix:** Explicitly evaluate readiness across 5 dimensions (`read_instructions`, `local_checks`, `skills`, `roles`, `hooks`) into `available`, `unavailable`, and `untested`.
7. **Acceptance Verification across 9 Mandatory Scenarios:** Formulate comprehensive automated tests covering empty repos, foreign rules, 0-diff repeat runs, new harnesses, legacy setups, corruption, read-only mode, worktrees, and skill-less entry.

### 1.3 Architectural Invariants
- **Non-Destructive Invariant:** No pre-existing user instructions, foreign rules, historical tasks, or accumulated observations are ever overwritten or erased.
- **Survey-First Zero-Write:** Discovery must never execute found scripts, trigger git hooks, create `.lock` files, or write telemetry.
- **Fail-Closed State Machine:** If a repository state is ambiguous or the schema version is incompatible, fallback to read-only diagnostic mode and present specific discrepancies.
- **Pass-through Zero-Diff Invariant:** Running `init-meta-project` on a healthy, registered repository must produce **0 git diff** and zero temporary artifacts.
- **Multi-Harness Parity:** Introducing or adapting a new harness installation must never detach, deactivate, or rewrite existing active harness bindings.

---

## 2. Technical Specification

### 2.1 State Classification & Decision Matrix (The 7 Canonical States)

The presence of `AGENTS.md` or `.agents/` alone does NOT prove Meta-Project integrity. The inspector classifies repositories into exactly 7 states:

| State Code | Canonical State | Criteria & Signatures | Action & Strategy |
| :--- | :--- | :--- | :--- |
| `NONE` | Обвязки нет | No `AGENTS.md`, no `.agents/`, no recognized agent instructions. | **Scaffold Clean:** Generate full Meta-Project skeleton tailored to detected stack. |
| `FOREIGN_RULES` | Чужие инструкции | Foreign instructions found (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, or `AGENTS.md` without Meta-Project markers). | **Preserve & Merge:** Retain foreign files intact, establish section ownership, propose non-destructive coexistence wrapper. |
| `HEALTHY_REGISTERED` | Meta-Project исправен (активен) | Meta-Project intact (`AGENTS.md`, `.agents/meta-project.json`, `boundaries.md`, scripts); current harness is registered as `active`. | **Verify & Pass-Through:** No-op. Zero diff, zero locks, verify capability matrix and report ready status. |
| `HEALTHY_NEW_HARNESS` | Подключение нового харнесса | Meta-Project intact; target harness/installation is not registered or is registered with status `planned`. | **Bind Harness:** Scaffold role bindings and installation adapter for the new harness without disturbing existing active installations. |
| `LEGACY_UNREGISTERED` | Legacy-обвязка без реестра | Older Meta-Project structure (`AGENTS.md` + `.agents/project_knowledge/`), but missing `.agents/meta-project.json` or identity engine. | **Legacy Adoption:** Inventory existing files, upgrade table headers, generate `.agents/meta-project.json` preserving historical logs. |
| `PARTIAL_CORRUPTED` | Частичная или повреждённая | Missing critical files (e.g. `boundaries.md` absent, corrupted JSON, missing core scripts). | **Diagnose & Repair:** Report exact discrepancies and missing components; offer surgical repair plan without overwriting intact slices. |
| `INCOMPATIBLE_SCHEMA` | Несовместимая схема реестра | `.agents/meta-project.json` present but `schema_version` is major-incompatible with current tooling. | **Read-Only Fallback:** Lock into read-only audit mode, report required schema migration, refuse blind writes. |

### 2.2 Deterministic Inspection Engine: `scripts/inspect_meta_project.py`

#### CLI Interface Specification
```bash
python scripts/inspect_meta_project.py [OPTIONS]

Options:
  --repo-root PATH        Path to repository or subproject root (defaults to current working directory).
  --json                  Output results in machine-readable JSON format.
  --harness NAME          Current execution harness identifier (e.g., antigravity, zcode).
  --installation ID       Concrete installation identifier (e.g., ag-main, zc-main).
  --read-only             Enforce strict zero-write assertion (audit mode).
  --help, -h              Show usage documentation.
```

#### JSON Output Contract
```json
{
  "inspection_version": "1.0.0",
  "repo_root": "c:/Users/adm_zhuravlev/Documents/antigravity/meta-project",
  "is_git_worktree": false,
  "git_toplevel": "c:/Users/adm_zhuravlev/Documents/antigravity/meta-project",
  "state": "HEALTHY_REGISTERED",
  "state_description": "Meta-Project intact and current harness installation is registered and active.",
  "recommended_action": "pass_through",
  "schema_version": "1.0.0",
  "project_id": "vlv-code/meta-project",
  "installations": {
    "ag-main": {
      "harness_id": "antigravity",
      "status": "active"
    },
    "zc-main": {
      "harness_id": "zcode",
      "status": "planned"
    }
  },
  "capabilities": {
    "read_instructions": {
      "status": "available",
      "detail": "Root AGENTS.md and knowledge slices accessible"
    },
    "local_checks": {
      "status": "available",
      "detail": "check_boundaries.py, verify_identity.py, compact_memory.py executable"
    },
    "skills": {
      "status": "available",
      "detail": "Local skills deployed in .agents/skills/"
    },
    "roles": {
      "status": "available",
      "detail": "3 active role profiles in .agents/team/"
    },
    "hooks": {
      "status": "available",
      "detail": "Git pre-commit hook incorporates check_boundaries"
    }
  },
  "missing_components": [],
  "conflicts": [],
  "foreign_instructions": []
}
```

### 2.3 Capability & Readiness Levels Matrix

The inspector evaluates 5 distinct operational levels. Each level is assigned one of three statuses:
- `available`: Verified and operational.
- `unavailable`: Component missing, corrupted, or incompatible.
- `untested`: Operational environment context cannot confirm execution (e.g. IDE plugin presence).

```
+---------------------------------------------------------------------------------------------------+
|                                  CAPABILITY READINESS MATRIX                                      |
+---------------------+-------------------+---------------------------------------------------------+
| Level               | Evaluated By      | Criteria for 'available'                                |
+---------------------+-------------------+---------------------------------------------------------+
| read_instructions   | File system       | Valid AGENTS.md + .agents/project_knowledge/ readable   |
| local_checks        | Python stdlib     | check_boundaries.py & verify_identity.py present        |
| skills              | Local / Global    | .agents/skills/ contains valid SKILL.md mirrors         |
| roles               | Registry & Team   | .agents/meta-project.json has active role bindings      |
| hooks               | .git / core.hooks | .git/hooks/pre-commit chains check_boundaries.py        |
+---------------------+-------------------+---------------------------------------------------------+
```

### 2.4 Self-Contained Project Passport (`templates/AGENTS.md`)
The canonical project passport must provide complete operational autonomy to an agent landing without global skills:
1. **Direct Exploration Protocol:** Explicit listing of core directories (`.agents/project_knowledge/`), responsibility zones (`boundaries.md`), risks (`weak_spots.md`), and tasks (`tasks.md`).
2. **Local Verification Commands:** Explicit zero-dependency CLI commands for all required checks:
   - Boundary verification: `python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree`
   - Identity verification: `python scripts/verify_identity.py --check`
   - Inspection and readiness: `python scripts/inspect_meta_project.py --json`
   - Memory compaction: `python scripts/compact_memory.py --dry-run`
3. **Explicit Read-Only / Audit Mode:** Guidelines for agents performing exploration or code review without making modifications or generating telemetry.
4. **Harness & Role Identification:** Clear instructions on how an agent determines its role and installation via `.agents/meta-project.json`.

### 2.5 Dual-Entry & Canonical README Badge
For discovery by agents and humans alike, a standardized Markdown block is codified:

```markdown
<!-- META-PROJECT:ENTRY:BEGIN -->
[![Built with Meta-Project](https://img.shields.io/badge/Built%20with-Meta--Project-blueviolet)](https://github.com/vlv-code/meta-project)

Agent instructions: [AGENTS.md](AGENTS.md) | Policy: [.agents/project_knowledge/boundaries.md](.agents/project_knowledge/boundaries.md)
*To inspect, configure, or adapt your environment, run `python scripts/inspect_meta_project.py` or invoke the `init-meta-project` skill.*
<!-- META-PROJECT:ENTRY:END -->
```
- In **Shared Repositories:** The badge is placed in a dedicated section owned by Meta-Project.
- In **Personal Overlays:** Modifying `README.md` is strictly optional to avoid polluting upstream projects.

---

## 3. Work Breakdown Structure (WBS)

### Phase 1: Inspection Engine & Deterministic State Machine (Dev Lead)
- **1.1:** Develop `scripts/inspect_meta_project.py` with zero runtime dependencies.
- **1.2:** Support git worktree detection (`.git` file pointing to `gitdir:`), subproject roots, and environment harness detection.
- **1.3:** Implement state classifier for the 7 canonical states (`NONE`, `FOREIGN_RULES`, `HEALTHY_REGISTERED`, `HEALTHY_NEW_HARNESS`, `LEGACY_UNREGISTERED`, `PARTIAL_CORRUPTED`, `INCOMPATIBLE_SCHEMA`).
- **1.4:** Implement capability matrix evaluator across the 5 dimensions.
- **1.5:** Author comprehensive unit tests in `tests/test_inspect_meta_project.py`.

### Phase 2: Self-Contained Passport & Canonical Templates (Dev Lead)
- **2.1:** Update `templates/AGENTS.md` to be fully self-contained (local CLI commands, read-only mode, zero reliance on external skill availability).
- **2.2:** Update root `AGENTS.md` reflecting the new self-contained structure and local command catalog.
- **2.3:** Add the canonical README entry block specification to templates and documentation.

### Phase 3: Procedural Skills Alignment & Deployable Bundle (Dev Lead)
- **3.1:** Refactor `skills/init-meta-project/SKILL.md`:
  - Enforce Survey Phase (Phase 1) invoking `inspect_meta_project.py` before any write.
  - Structure actions according to the 7 canonical states.
  - Embed updated templates with explicit `<!-- TEMPLATE:BEGIN/END -->` sentinels.
  - Include `scripts/inspect_meta_project.py` in the list of deployed runtime utilities.
- **3.2:** Update `skills/manage-meta-project/SKILL.md` and `skills/update-meta-project/SKILL.md` to integrate inspection outputs.
- **3.3:** Run `python scripts/sync_templates.py --write` and verify 0 drift via `--check`.

### Phase 4: Acceptance Test Suite for the 9 Scenarios (Quality Guardian)
- **4.1:** Author `tests/test_acceptance_scenarios.py` implementing end-to-end integration tests for all 9 mandatory scenarios:
  1. `test_scenario_empty_project`: clean repo scaffold.
  2. `test_scenario_foreign_instructions`: coexistence with `.cursorrules` / `CLAUDE.md`.
  3. `test_scenario_healthy_registered_zero_diff`: repeat run yields 0 diff, 0 locks.
  4. `test_scenario_healthy_new_harness`: harness adaptation without disturbing existing active installations.
  5. `test_scenario_legacy_unregistered`: upgrading legacy setup without registry.
  6. `test_scenario_partial_corrupted`: detecting missing slices and recommending repair.
  7. `test_scenario_read_only_mode`: zero writes under `--read-only`.
  8. `test_scenario_git_worktree`: correct detection in a git worktree.
  9. `test_scenario_readme_entry_without_skills`: standalone execution via local instructions.
- **4.2:** Verify non-destructive invariants and capability matrix output.
- **4.3:** Run full regression suite and tree boundary audit.

### Phase 5: Documentation, README Parity, and Release Commit (GitHub Steward)
- **5.1:** Update `README.md` and `README.ru.md` with the new dual-entry badge, inspection tool documentation, and capability matrix.
- **5.2:** Verify Git hygiene, clean working tree, and pre-commit boundary checks.
- **5.3:** Create conventional commit:
  `feat(init): introduce deterministic inspection engine, self-contained passport, and universal adoption protocol`.
- **5.4:** Log release telemetry row in `.agents/team/agent-github-steward/profile.md`.

---

## 4. Sequential Agent Prompts

### Stage 1: Inspection Engine & Deterministic State Machine

#### Prompt 1.1: `@agent-dev-lead`
```markdown
@agent-dev-lead implement feature: разработка детерминированного скрипта обследования репозитория scripts/inspect_meta_project.py и тестов

Контекст: В рамках трансформации init-meta-project в универсальную точку входа требуется отделить обследование (survey) от применения изменений, реализовав легковесный инструмент на Python 3.10+ stdlib без внешних зависимостей.

Задача:
1. Создай scripts/inspect_meta_project.py:
   - CLI аргументы: --repo-root (по умолчанию "."), --json, --harness, --installation, --read-only.
   - Определение рабочего корня с поддержкой git worktree (через .git-файл и gitdir:) и явно заданного подпроекта.
   - Классификация состояния репозитория на 7 канонических состояний:
     * NONE (обвязки нет);
     * FOREIGN_RULES (чужой AGENTS.md или .cursorrules/CLAUDE.md/.windsurfrules без маркеров Meta-Project);
     * HEALTHY_REGISTERED (Meta-Project исправен, текущая установка активна);
     * HEALTHY_NEW_HARNESS (Meta-Project исправен, подключается новый или planned харнесс);
     * LEGACY_UNREGISTERED (старая обвязка без .agents/meta-project.json);
     * PARTIAL_CORRUPTED (частичная или повреждённая обвязка, отсутствуют границы/скрипты);
     * INCOMPATIBLE_SCHEMA (версия схемы meta-project.json не поддерживается).
   - Оценка доступных уровней работы (Capability Matrix):
     * read_instructions, local_checks, skills, roles, hooks (со статусами: available, unavailable, untested).
   - Инвариант Survey-First: скрипт выполняет ТОЛЬКО чтение; создание файлов, lock-файлов, телеметрии, а также запуск найденных хуков и сторонних скриптов строго запрещены.
2. В tests/test_inspect_meta_project.py напиши unit- и adversarial-тесты (TDD):
   - Проверка классификации для каждого из 7 состояний.
   - Проверка поддержки git worktree.
   - Проверка JSON-вывода и Capability Matrix.
   - Проверка инварианта отсутствия сайд-эффектов при обследовании (zero writes).
3. Запусти тесты:
   python -m unittest tests/test_inspect_meta_project.py -v
4. Зафиксируй шаг в .agents/project_knowledge/tasks.md и передай эстафету для Этапа 2 (Prompt 2.1).
```

---

### Stage 2: Self-Contained Passport & Canonical Templates

#### Prompt 2.1: `@agent-dev-lead`
```markdown
@agent-dev-lead develop component: актуализация templates/AGENTS.md и root AGENTS.md до самодостаточного паспорта и добавление канонической плашки README

Контекст: Скрипт обследования разработан. Необходимо сделать проектный паспорт самодостаточным, чтобы агент без глобальных скиллов понимал маршруты проверок и работы через локальные stdlib-команды.

Задача:
1. В templates/AGENTS.md:
   - Добавь каталог локальных проверок (Local Verification & Tooling) с командами:
     * python scripts/inspect_meta_project.py --json
     * python scripts/verify_identity.py --check
     * python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
     * python scripts/compact_memory.py --dry-run
     * python scripts/record_obs.py
   - Укажи явный протокол ознакомительного аудита без записи (Read-Only Exploration Mode).
   - Опиши протокол действий при отсутствии глобальных скиллов фреймворка (Base Fallback Mode).
   - Добавь секцию канонического блока для README (Dual-Entry Badge) со ссылками на AGENTS.md и inspect_meta_project.py.
2. В root AGENTS.md:
   - Синхронизируй изменения паспорта, внедрив каталог локальных утилит и режим знакомства.
3. Добавь канонический блок в README.md и README.ru.md:
   <!-- META-PROJECT:ENTRY:BEGIN --> ... <!-- META-PROJECT:ENTRY:END -->
4. Проверь отсутствие регрессий:
   python -m unittest discover -s tests -p "test_*.py" -v
5. Зафиксируй шаг в .agents/project_knowledge/tasks.md и передай эстафету для Этапа 3 (Prompt 3.1).
```

---

### Stage 3: Procedural Skills Alignment & Deployable Bundle

#### Prompt 3.1: `@agent-dev-lead`
```markdown
@agent-dev-lead develop component: переработка скилла init-meta-project на двухфазную архитектуру (survey ➔ execution) и синхронизация комплекта

Контекст: Разработаны скрипт обследования и самодостаточный паспорт. Требуется обновить procedural skills, встроив инспекцию и развёртывание нового комплекта утилит.

Задача:
1. В skills/init-meta-project/SKILL.md:
   - Внедрить Фазу 1 (Survey & Inspection): обязательный вызов python scripts/inspect_meta_project.py --json перед любыми действиями.
   - Разделить выполнение на сценарии, соответствующие 7 состояниям:
     * Чистая инициализация (NONE)
     * Сосуществование с чужими правилами (FOREIGN_RULES)
     * Подхват без изменений / no-op (HEALTHY_REGISTERED)
     * Подключение нового харнесса (HEALTHY_NEW_HARNESS)
     * Принятие legacy-структуры (LEGACY_UNREGISTERED)
     * Восстановление повреждений (PARTIAL_CORRUPTED)
     * Read-only режим при несовместимости схемы (INCOMPATIBLE_SCHEMA)
   - Обновить список развёртываемых скриптов в целевой проект (включить scripts/inspect_meta_project.py).
   - Обновить встроенные шаблоны с sentinels <!-- TEMPLATE:BEGIN/END -->.
2. В skills/manage-meta-project/SKILL.md и skills/update-meta-project/SKILL.md:
   - Добавить вызов предварительного обследования inspect_meta_project.py для проверки целостности перед оркестрацией и обновлениями.
3. Выполни синхронизацию встроенных шаблонов:
   python scripts/sync_templates.py --write
   python scripts/sync_templates.py --check
4. Запусти тесты целостности:
   python -m unittest tests/test_integrity.py -v
5. Зафиксируй шаг в .agents/project_knowledge/tasks.md и передай эстафету роли agent-quality-guardian (Prompt 4.1).
```

---

### Stage 4: Acceptance Test Suite for the 9 Scenarios

#### Prompt 4.1: `@agent-quality-guardian`
```markdown
@agent-quality-guardian verify meta-project structure: разработка приёмочного тестового набора для 9 обязательных сценариев и аудит неразрушающего поведения

Контекст: Двухфазный init-meta-project и скрипт обследования реализованы. Требуется провести независимую валидацию всех сценариев жизненного цикла.

Задача:
1. В tests/test_acceptance_scenarios.py разработай интеграционные тесты для 9 сценариев (во временных изолированных каталогах tempfile):
   - Сценарий 1 (empty project): пустой репозиторий ➔ определение NONE, корректный scaffold.
   - Сценарий 2 (foreign instructions): наличие CLAUDE.md / .cursorrules / чужого AGENTS.md ➔ определение FOREIGN_RULES, сохранение чужих файлов без изменений.
   - Сценарий 3 (healthy registered zero diff): повторный запуск на исправной обвязке ➔ определение HEALTHY_REGISTERED, 0 diff, 0 мусорных файлов/локов.
   - Сценарий 4 (healthy new harness): подключение новой установки ➔ определение HEALTHY_NEW_HARNESS, привязка без отключения действующих.
   - Сценарий 5 (legacy unregistered): обвязка без meta-project.json ➔ определение LEGACY_UNREGISTERED, сохранение истории tasks.md и observations.md.
   - Сценарий 6 (partial corrupted): повреждённый репозиторий ➔ определение PARTIAL_CORRUPTED, выявление точных расхождений.
   - Сценарий 7 (read-only mode): запуск с флагом --read-only ➔ успешный аудит без единой записи на диск.
   - Сценарий 8 (git worktree): работа через git worktree ➔ корректное определение родительского корня.
   - Сценарий 9 (readme entry without skills): навигация агента через самодостаточный AGENTS.md и локальные CLI при отсутствии глобальных скиллов.
2. Проверь инварианты неразрушающего поведения и сохранности истории.
3. Запусти все тесты:
   python -m unittest discover -s tests -p "test_*.py" -v
4. Проверь аудит границ:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
5. Зафиксируй шаг в .agents/project_knowledge/tasks.md, добавь строку телеметрии в .agents/team/agent-quality-guardian/profile.md и передай эстафету agent-github-steward (Prompt 5.1).
```

---

### Stage 5: Documentation, README Parity, and Release Commit

#### Prompt 5.1: `@agent-github-steward`
```markdown
@agent-github-steward git hygiene: верификация развёртываемого комплекта, актуализация документации и фиксация Conventional Commit

Контекст: Все компоненты обследования, самодостаточного паспорта и приёмочные тесты успешно реализованы и проверены. Требуется провести аудит Git-гигиены и зафиксировать релиз.

Задача:
1. Проведи аудит Code-to-README Parity:
   - Убедись, что новые возможности inspect_meta_project.py, плашка README и таблица состояний отражены в README.md и README.ru.md.
   - Проверь валидность ссылок и относительных путей.
2. Проверь статус Git и Boundary Gate:
   git status
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --diff HEAD --allow-red-zone
3. Сформируй атомарный коммит по стандарту Conventional Commits:
   - Заголовок:
     feat(init): introduce deterministic inspection engine, self-contained passport, and universal adoption protocol

   - Описание:
     - Add zero-dependency scripts/inspect_meta_project.py with 7-state classification and capability matrix
     - Make templates/AGENTS.md and root AGENTS.md self-contained with local stdlib CLI tooling catalog
     - Introduce dual-entry canonical README badge and routing block
     - Refactor init-meta-project skill to survey-first architecture with zero-write phase 1
     - Add acceptance test suite tests/test_acceptance_scenarios.py covering 9 mandatory repository states
     - Enforce non-destructive history preservation and zero-diff repeat execution invariant
4. Зафиксируй коммит (git add, git commit).
5. Проверь git log -1 --stat.
6. В .agents/team/agent-github-steward/profile.md добавь 1 строку телеметрии о фиксации релиза.
```

---

## 5. Definition of Done (DoD) & Acceptance Criteria

1. **Двухфазная архитектура `init-meta-project`:**
   - Фаза 1 (Обследование) строго изолирована: ни при каких условиях не создаёт файлы конфигураций, записи телеметрии, lock-файлы или архивы, и не исполняет найденные в репозитории сторонние скрипты/хуки.
2. **Детерминированный инспектор (`scripts/inspect_meta_project.py`):**
   - Написан исключительно на Python 3.10+ stdlib (ноль внешних зависимостей).
   - Поддерживает флаги `--repo-root`, `--json`, `--harness`, `--installation`, `--read-only`.
   - Корректно определяет `git worktree` и подпроекты.
   - Выдаёт классификацию по 7 каноническим состояниям и Capability Matrix по 5 уровням.
3. **Самодостаточный паспорт проекта:**
   - `templates/AGENTS.md` и корень `AGENTS.md` содержат полный каталог локальных команд для проверок. Агент без внешних глобальных скиллов способен выполнять аудит и проверки автономно.
4. **Каноническая плашка и двойной вход:**
   - В `README.md` и `README.ru.md` внедрён стандартизированный блок со ссылками на `AGENTS.md` и `inspect_meta_project.py`.
5. **Нулевой диф при повторном запуске (Zero-Diff Invariant):**
   - Повторный запуск на исправной установке (`HEALTHY_REGISTERED`) оставляет рабочую копию в состоянии `0 modified files` без временных артефактов.
6. **Сохранение чужих правил и истории:**
   - Чужие файлы (`.cursorrules`, `CLAUDE.md`, чужой `AGENTS.md`) не затираются;
   - Исторические записи в `tasks.md`, `observations.md` и `archive/` сохраняются без искажений.
7. **Зелёные проверки ядра и гейтов:**
   - 100% покрытие дерева файлов зонами ответственности (`check_boundaries.py --audit-tree`);
   - 0 дрейфа шаблонов (`sync_templates.py --check`);
   - Все 9 сценариев приёмки в `tests/test_acceptance_scenarios.py` проходят успешно;
   - Полный набор регрессионных тестов выполняется без ошибок.
