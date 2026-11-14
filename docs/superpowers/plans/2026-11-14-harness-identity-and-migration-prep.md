# Implementation Plan: Harness Identity & Migration Preparation (Antigravity ➔ ZCode)

> **Execution Protocol:** Multi-Agent Lifecycle (`agent-dev-lead` ➔ `agent-quality-guardian` ➔ `agent-github-steward`).  
> **Target Baseline:** Commit `724c7e3` (`fix(kernel): resolve external auditor findings and harden core utilities`).  
> **Core Invariant:** Zero external dependencies (pure Python 3.10+ stdlib), Default Closed Tooling, Single Source of Truth (`.agents/meta-project.json`), and Non-Destructive History Invariant.

---

## 1. Context, Objectives, and Constraints

### 1.1 Background
The repository currently operates under the **Antigravity** harness with a Compact Trio agent topology:
- `agent-dev-lead`
- `agent-quality-guardian`
- `agent-github-steward`

To prepare for a gradual and transparent transition to **ZCode** without vendor lock-in or split-brain states, each logical role must be given an unambiguous, traceable identity within the scope of the project and its specific harness installation.

### 1.2 Core Goals
1. Establish a machine-readable project registry: `.agents/meta-project.json`.
2. Formalize the quad-coordinate identity schema:
   `actor_id = <project_id>::<harness_id>::<installation_id>::<role_id>`.
3. Provide pure Python 3.10+ stdlib identity validation (`scripts/verify_identity.py`).
4. Extend `scripts/record_obs.py` with optional `--actor-id` while keeping the 5-column Markdown table contract.
5. Perform non-destructive self-registration for all 3 active Antigravity roles.
6. Synchronize canonical templates (`templates/`) and procedural skills (`skills/init-meta-project/`, `skills/manage-meta-project/`, `skills/record-observation/`).
7. Keep historical records immutable: legacy tasks and observations retain original authorship without retroactive harness attribution.

### 1.3 Key Architectural Invariants
- **Attribution, Not Security Isolation:** `actor_id` provides auditability and traceability; it does not grant permissions or bypass boundaries.
- **Single Source of Truth:** `.agents/meta-project.json` is the sole authoritative registry for installations and role bindings.
- **Fail-Closed on Unknown Actors:** Undetermined contexts or unknown bindings must raise an explicit error rather than guessing identity by directory name.
- **ZCode as Planned Integration:** `zc-main` / `zcode` is registered with status `"planned"`. No active execution or assumed capability is asserted for ZCode during this stage.

---

## 2. Technical Specification

### 2.1 Identity Coordinate System
```
+---------------------------------------------------------------------------------------------------+
|                                        ACTOR IDENTIFIER                                           |
|  vlv-code/meta-project  ::      antigravity      ::       ag-main       ::     agent-dev-lead     |
|     [project_id]        ::     [harness_id]      ::  [installation_id]  ::       [role_id]        |
+---------------------------------------------------------------------------------------------------+
```

- `project_id`: Stable repository slug (`vlv-code/meta-project`).
- `role_id`: Logical role identifier (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`).
- `harness_id`: Agent platform engine (`antigravity`, `zcode`).
- `installation_id`: Concrete local or host deployment (`ag-main`, `zc-main`).
- `actor_id`: Delimited string joining the four coordinates via `::`.
*(Excluded from identity: model name, git branch, absolute disk paths).*

### 2.2 Project Registry Schema: `.agents/meta-project.json`
```json
{
  "schema_version": "1.0.0",
  "project_id": "vlv-code/meta-project",
  "installations": {
    "ag-main": {
      "harness_id": "antigravity",
      "status": "active",
      "description": "Primary Antigravity environment"
    },
    "zc-main": {
      "harness_id": "zcode",
      "status": "planned",
      "description": "Planned ZCode migration target"
    }
  },
  "roles": {
    "agent-dev-lead": {
      "description": "Lead Developer & Dispatcher",
      "bindings": {
        "ag-main": {
          "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead",
          "status": "active",
          "profile_path": ".agents/team/agent-dev-lead/profile.md"
        },
        "zc-main": {
          "actor_id": "vlv-code/meta-project::zcode::zc-main::agent-dev-lead",
          "status": "planned",
          "profile_path": null
        }
      }
    },
    "agent-quality-guardian": {
      "description": "Quality & Meta-Architecture Guardian",
      "bindings": {
        "ag-main": {
          "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian",
          "status": "active",
          "profile_path": ".agents/team/agent-quality-guardian/profile.md"
        },
        "zc-main": {
          "actor_id": "vlv-code/meta-project::zcode::zc-main::agent-quality-guardian",
          "status": "planned",
          "profile_path": null
        }
      }
    },
    "agent-github-steward": {
      "description": "GitHub Steward & Release Captain",
      "bindings": {
        "ag-main": {
          "actor_id": "vlv-code/meta-project::antigravity::ag-main::agent-github-steward",
          "status": "active",
          "profile_path": ".agents/team/agent-github-steward/profile.md"
        },
        "zc-main": {
          "actor_id": "vlv-code/meta-project::zcode::zc-main::agent-github-steward",
          "status": "planned",
          "profile_path": null
        }
      }
    }
  }
}
```

### 2.3 Action Attribution Formats
1. **Tasks (`tasks.md`):**
   ```markdown
   - [x] [vlv-code/meta-project::antigravity::ag-main::agent-dev-lead @ 2026-11-14 20:30] Step 44: Action description
   ```
2. **Handoff Packets:**
   ```markdown
   Handoff Packet:
   - from_actor_id: vlv-code/meta-project::antigravity::ag-main::agent-dev-lead
   - to_actor_id: vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian
   ```
3. **Telemetry Table (`profile.md`):**
   ```markdown
   | Date | Initiator | Actor ID | Task / Invocation | Status / Result |
   | :--- | :--- | :--- | :--- | :--- |
   | 2026-11-14 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Migration identity self-registration | SUCCESS |
   ```
4. **Observations (`observations.md`):**
   Keep 5 columns intact; prepend `[actor=<actor_id>] ` to Issue/Observation:
   ```markdown
   | Date | Category | Component / Path | Observation / Issue | Solution / Workaround |
   | :--- | :--- | :--- | :--- | :--- |
   | 2026-11-14 | [runtime] | scripts/verify_identity.py | [actor=vlv-code/meta-project::antigravity::ag-main::agent-dev-lead] Missing JSON schema causes unhandled exit | Enforce jsonschema structure validation via stdlib |
   ```

---

## 3. Work Breakdown Structure (WBS)

### Phase 1: Core Engine & Identity Verification (Dev Lead)
- **1.1:** Author `.agents/meta-project.json` registry.
- **1.2:** Implement `scripts/verify_identity.py` (CLI with `--check`, `--repo-root`, `--actor`).
- **1.3:** Author unit and adversarial tests in `tests/test_verify_identity.py`.
- **1.4:** Extend `scripts/record_obs.py` with optional `--actor-id` flag + tests in `tests/test_record_obs.py`.

### Phase 2: Canonical Templates & Skills Synchronization (Dev Lead)
- **2.1:** Update `templates/team/profile.md`, `templates/team/system_prompt.md`, `templates/team/notes.md` with identity metadata blocks.
- **2.2:** Update `templates/project_knowledge/tasks.md` with qualified actor format.
- **2.3:** Update `templates/AGENTS.md` and root `AGENTS.md` with actor determination protocol.
- **2.4:** Update procedural skills:
  - `skills/init-meta-project/SKILL.md` (deploy `.agents/meta-project.json`, `verify_identity.py`, `record_obs.py`).
  - `skills/manage-meta-project/SKILL.md` (scaffold identity coordinates for newly provisioned roles).
  - `skills/record-observation/SKILL.md` (pass `--actor-id` to `record_obs.py`).
- **2.5:** Run `python scripts/sync_templates.py --write` and verify 0 drift via `--check`.

### Phase 3: Autonomous Self-Registration of Active Roles
- **3.1:** `agent-dev-lead` updates `.agents/team/agent-dev-lead/` (`profile.md`, `system_prompt.md`, `notes.md`) and logs 1 telemetry row.
- **3.2:** `agent-quality-guardian` updates `.agents/team/agent-quality-guardian/` (`profile.md`, `system_prompt.md`, `notes.md`) and logs 1 telemetry row.
- **3.3:** `agent-github-steward` updates `.agents/team/agent-github-steward/` (`profile.md`, `system_prompt.md`, `notes.md`) and logs 1 telemetry row.

### Phase 4: Acceptance Audit & Quality Verification (Quality Guardian)
- **4.1:** Verify `verify_identity.py` passes cleanly against repository.
- **4.2:** Run full regression test suite (expect 70+ tests to pass).
- **4.3:** Verify 0 drift across templates (`sync_templates.py --check`).
- **4.4:** Verify 100% boundary tree coverage (`check_boundaries.py --audit-tree`).
- **4.5:** Verify Boundary Gate diff clean (`check_boundaries.py --diff HEAD --allow-red-zone`).
- **4.6:** Update `.agents/project_knowledge/tasks.md` with verified completion.

### Phase 5: Git Hygiene & Atomic Conventional Commit (GitHub Steward)
- **5.1:** Audit working copy status and `.gitignore` integrity.
- **5.2:** Verify pre-commit boundary checks.
- **5.3:** Create conventional commit:
  `feat(identity): establish multi-harness identity registry and migration preparation`.
- **5.4:** Log release telemetry row in `.agents/team/agent-github-steward/profile.md`.

---

## 4. Sequential Agent Prompts

### Stage 1: Core Engine & Identity Verification

#### Prompt 1.1: `@agent-dev-lead`
```markdown
@agent-dev-lead implement feature: разработка проектного реестра .agents/meta-project.json, утилиты scripts/verify_identity.py и расширение record_obs.py

Контекст: В рамках подготовки к последующей миграции на ZCode требуется разделить логическую роль и её исполнение в конкретном харнессе, внедрив единый формат идентичности actor_id (<project_id>::<harness_id>::<installation_id>::<role_id>) с единым источником истины в .agents/meta-project.json.

Задача:
1. Создай файл .agents/meta-project.json:
   - schema_version: "1.0.0"
   - project_id: "vlv-code/meta-project"
   - Установки:
     * ag-main (harness: "antigravity", status: "active")
     * zc-main (harness: "zcode", status: "planned")
   - Привязки для 3 ролей (agent-dev-lead, agent-quality-guardian, agent-github-steward) с активным статусом в ag-main и planned в zc-main.
2. В tests/test_verify_identity.py напиши юнит- и adversarial-тесты (TDD Red phase):
   - test_valid_registry_passes: проверка корректного реестра и активных профилей.
   - test_conflicting_actor_ids_fails: выявление дублирующихся actor_id.
   - test_mismatched_profile_actor_id_fails: обнаружение расхождения actor_id в profile.md с реестром.
   - test_planned_installation_marked_active_in_profile_fails: запрет активации planned-установки zc-main без официального переключения.
   - test_unknown_binding_raises_unresolved_identity_error: при неизвестной роли скрипт возвращает ошибку, запрещая угадывание по имени папки.
3. Убедись в падении тестов (Red):
   python -m unittest tests/test_verify_identity.py -v
4. Разработай scripts/verify_identity.py на Python 3.10+ stdlib (zero dependencies):
   - Аргументы: --check, --repo-root (по умолчанию "."), --actor (опциональная валидация конкретного actor_id).
   - Валидация формата реестра, наличия профилей для активных привязок, соответствия actor_id и статуса planned.
   - Выходной код 0 при валидности, 1 при ошибках с информативным выводом в stderr/stdout.
5. В scripts/record_obs.py добавь опциональный аргумент --actor-id:
   - При передаче --actor-id вставляй префикс [actor=<actor_id>] в начало поля Observation/Issue.
   - Сохраняй исходную 5-колоночную структуру таблицы.
   - В tests/test_record_obs.py добавь test_observation_with_actor_id.
6. Запусти тесты:
   python -m unittest tests/test_verify_identity.py tests/test_record_obs.py -v
7. Передай эстафету роли agent-dev-lead для этапа синхронизации шаблонов (Prompt 2.1).
```

---

### Stage 2: Templates & Skills Synchronization

#### Prompt 2.1: `@agent-dev-lead`
```markdown
@agent-dev-lead develop component: актуализация канонических шаблонов, procedural skills и синхронизация зеркал для поддержки actor_id

Контекст: Разработан реестр и скрипт проверки идентичности. Необходимо поддержать единый формат идентичности в шаблонах ролей, задачах и скиллах инициализации/оркестрации.

Задача:
1. В templates/team/:
   - profile.md: добавь переменные {{ACTOR_ID}}, {{HARNESS_ID}}, {{INSTALLATION_ID}}, ссылку на реестр .agents/meta-project.json в секцию 1, и колонку "Actor ID" в таблицу телеметрии (секция 5).
   - system_prompt.md: добавь инвариант идентичности (агент осознаёт свой actor_id, сверяет его с реестром, чтение чужого профиля не меняет текущего актора).
   - notes.md: добавь связку приватного контекста с actor_id.
2. В templates/project_knowledge/tasks.md:
   - Обнови формат авторства чек-листа: [<actor_id> @ <ISO_DATETIME>].
3. В templates/AGENTS.md и root AGENTS.md:
   - Добавь протокол определения исполнителя через .agents/meta-project.json.
4. В procedural skills:
   - skills/init-meta-project/SKILL.md: включи генерацию .agents/meta-project.json и развёртывание scripts/verify_identity.py и scripts/record_obs.py при инициализации.
   - skills/manage-meta-project/SKILL.md: включи регистрацию новых ролей в .agents/meta-project.json при их материализации.
   - skills/record-observation/SKILL.md: опиши передачу аргумента --actor-id при вызове утилиты.
5. Выполни синхронизацию встроенных шаблонов и зеркал:
   python scripts/sync_templates.py --write
   python scripts/sync_templates.py --check
6. Запусти тесты целостности:
   python -m unittest tests/test_integrity.py -v
7. Передай эстафету для саморегистрации активных ролей (Prompt 3.1).
```

---

### Stage 3: Self-Registration of Active Roles

#### Prompt 3.1: `@agent-dev-lead`
```markdown
@agent-dev-lead implement feature: саморегистрация роли agent-dev-lead в формате actor_id

Контекст: Реестр .agents/meta-project.json и шаблоны обновлены. Требуется провести саморегистрацию роли agent-dev-lead в текущем харнессе Antigravity.

Задача:
1. В .agents/team/agent-dev-lead/profile.md:
   - В YAML frontmatter укажи:
     role_id: "agent-dev-lead"
     harness_id: "antigravity"
     installation_id: "ag-main"
     actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"
   - В секции 1 добавь блок идентификации с ссылкой на .agents/meta-project.json.
   - В таблицу телеметрии добавь колонку "Actor ID" и запиши 1 строку о саморегистрации (инициатор: User, исполнитель: actor_id).
2. В .agents/team/agent-dev-lead/system_prompt.md:
   - Актуализируй системный промпт инвариантом квалифицированной идентичности.
3. В .agents/team/agent-dev-lead/notes.md:
   - Зафиксируй привязку приватного блокнота к actor_id.
4. Проверь статус валидатором:
   python scripts/verify_identity.py --check --actor vlv-code/meta-project::antigravity::ag-main::agent-dev-lead
5. Передай эстафету роли agent-quality-guardian для саморегистрации (Prompt 3.2).
```

#### Prompt 3.2: `@agent-quality-guardian`
```markdown
@agent-quality-guardian verify meta-project structure: саморегистрация роли agent-quality-guardian в формате actor_id

Контекст: Роль agent-dev-lead зарегистрирована. Требуется провести саморегистрацию роли agent-quality-guardian в текущем харнессе Antigravity.

Задача:
1. В .agents/team/agent-quality-guardian/profile.md:
   - В YAML frontmatter укажи:
     role_id: "agent-quality-guardian"
     harness_id: "antigravity"
     installation_id: "ag-main"
     actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian"
   - В секции 1 добавь блок идентификации со ссылкой на .agents/meta-project.json.
   - В таблицу телеметрии добавь колонку "Actor ID" и запиши 1 строку о саморегистрации (инициатор: User, исполнитель: actor_id).
2. В .agents/team/agent-quality-guardian/system_prompt.md:
   - Актуализируй системный промпт инвариантом квалифицированной идентичности.
3. В .agents/team/agent-quality-guardian/notes.md:
   - Зафиксируй привязку приватного блокнота к actor_id.
4. Проверь статус валидатором:
   python scripts/verify_identity.py --check --actor vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian
5. Передай эстафету роли agent-github-steward для саморегистрации (Prompt 3.3).
```

#### Prompt 3.3: `@agent-github-steward`
```markdown
@agent-github-steward git hygiene: саморегистрация роли agent-github-steward в формате actor_id

Контекст: Роли agent-dev-lead и agent-quality-guardian зарегистрированы. Требуется провести саморегистрацию роли agent-github-steward в текущем харнессе Antigravity.

Задача:
1. В .agents/team/agent-github-steward/profile.md:
   - В YAML frontmatter укажи:
     role_id: "agent-github-steward"
     harness_id: "antigravity"
     installation_id: "ag-main"
     actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-github-steward"
   - В секции 1 добавь блок идентификации со ссылкой на .agents/meta-project.json.
   - В таблицу телеметрии добавь колонку "Actor ID" и запиши 1 строку о саморегистрации (инициатор: User, исполнитель: actor_id).
2. В .agents/team/agent-github-steward/system_prompt.md:
   - Актуализируй системный промпт инвариантом квалифицированной идентичности.
3. В .agents/team/agent-github-steward/notes.md:
   - Зафиксируй привязку приватного блокнота к actor_id.
4. Проверь статус валидатором:
   python scripts/verify_identity.py --check --actor vlv-code/meta-project::antigravity::ag-main::agent-github-steward
5. Передай эстафету роли agent-quality-guardian для финального аудита качества (Prompt 4.1).
```

---

### Stage 4: Full Quality Gate & Acceptance Verification

#### Prompt 4.1: `@agent-quality-guardian`
```markdown
@agent-quality-guardian verify meta-project structure: комплексная приёмочная верификация идентичности ролей и готовности к миграции на ZCode

Контекст: Все 3 роли выполнили саморегистрацию. Требуется провести независимый аудит целостности экосистемы, тестов и границ репозитория.

Задача:
1. Запусти валидатор идентичности для всего репозитория:
   python scripts/verify_identity.py --check
2. Запусти полный набор регрессионных тестов:
   python -m unittest discover -s tests -p "test_*.py" -v
3. Проверь отсутствие дрейфа шаблонов:
   python scripts/sync_templates.py --check
4. Проверь 100% покрытие дерева файлов зонами ответственности:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
5. Проверь дифф-гейт рабочей копии с флагом Красной зоны:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --diff HEAD --allow-red-zone
   (Убедись в отсутствии непредусмотренных изменений и архитектурного дрейфа).
6. Проверь сохранность истории:
   - Убедись, что исторические записи в tasks.md, observations.md и profile.md не были переписаны и сохранили оригинальный формат.
7. В .agents/project_knowledge/tasks.md зафиксируй завершение этапа подготовки к миграции в новом формате [<actor_id> @ <ISO_DATETIME>].
8. В .agents/team/agent-quality-guardian/profile.md добавь 1 строку телеметрии об успешном аудите.
9. Передай эстафету роли agent-github-steward для фиксации коммита (Prompt 5.1).
```

---

### Stage 5: Git Hygiene & Conventional Commit

#### Prompt 5.1: `@agent-github-steward`
```markdown
@agent-github-steward git hygiene: фиксация Conventional Commit этапа подготовки идентичности к миграции на ZCode

Контекст: Приёмочный аудит роли agent-quality-guardian успешно пройден. Все роли маркированы actor_id, реестр .agents/meta-project.json сформирован, ZCode зафиксирован в статусе planned, тесты и гейты пройдены на 100%.

Задача:
1. Проведи аудит Git-гигиены:
   git status
   (Убедись в отсутствии лишних неотслеживаемых файлов; временные файлы игнорируются).
2. Запусти контрольную проверку Boundary Gate перед коммитом:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --diff HEAD --allow-red-zone
3. Сформируй атомарный коммит по стандарту Conventional Commits:
   - Заголовок:
     feat(identity): establish multi-harness identity registry and migration preparation

   - Описание:
     - Add project registry .agents/meta-project.json (ag-main active, zc-main planned)
     - Add pure Python stdlib identity validator scripts/verify_identity.py with comprehensive tests
     - Add optional --actor-id flag to scripts/record_obs.py preserving 5-column table format
     - Update canonical templates (profile, prompt, notes, tasks, AGENTS.md) and sync skills
     - Perform non-destructive self-registration for agent-dev-lead, agent-quality-guardian, and agent-github-steward
     - Preserve all historical logs, notes, and legacy task records intact
4. Зафиксируй изменения (git add, git commit).
5. Проверь вывод git log -1 --stat.
6. В .agents/team/agent-github-steward/profile.md добавь 1 строку телеметрии о фиксации релиза.
```

---

## 5. Definition of Done (DoD) & Acceptance Criteria

1. **Однозначная идентичность:**
   - Все 3 проектные роли имеют явные `actor_id` в пределах проекта `vlv-code/meta-project` и текущей установки `ag-main` (`antigravity`).
2. **Planned ZCode Integration:**
   - Установка `zc-main` (`zcode`) зарегистрирована в `.agents/meta-project.json` строго со статусом `"planned"`. Ни один профиль не активирует ZCode преждевременно.
3. **Неприкосновенность истории:**
   - Все исторические записи в `tasks.md`, `observations.md`, `archive/` и `notes.md` сохранены без изменений и без ретроактивного присвоения им харнесса.
4. **Атрибуция новых действий:**
   - Новые задачи в `tasks.md` фиксируются в формате `[<actor_id> @ <ISO_DATETIME>]`.
   - Новые наблюдения через `record_obs.py --actor-id` содержат префикс `[actor=<actor_id>]`.
   - Handoff в системных промптах требует явных `from_actor_id` и `to_actor_id`.
5. **Безотказный контроль (Fail-Closed):**
   - Попытка выполнить действие с неизвестной или незарегистрированной привязкой завершается явной ошибкой `verify_identity.py`, без автоматического угадывания по имени каталога.
6. **Зелёные проверки ядра:**
   - `python scripts/verify_identity.py --check` ➔ exit code 0.
   - `python -m unittest discover -s tests -p "test_*.py" -v` ➔ все 70+ тестов OK.
   - `python scripts/sync_templates.py --check` ➔ 0 drift.
   - `python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree` ➔ 100% coverage.
