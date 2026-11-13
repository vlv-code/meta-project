# Implementation Plan: P1 Core Hardening & Architecture Calibration

> **Execution Protocol:** 2-Handoff Lifecycle per Task (`agent-dev-lead` ➔ `agent-quality-guardian` ➔ `agent-github-steward`).
> **Core Principle:** Default Closed Tooling (Zero-Dependency Core by default; Opt-in required for third-party tools; liability assigned to operator/spec).
> **Adversarial Testing:** Mandatory negative/boundary tests in TDD before moving from Red to Green.

---

## Task Breakdown

### Task 1: Architecture Calibration & Invariants Update (P1.0)
- **Goal:** Codify Default Closed tooling policy, Adversarial TDD requirement, Tier 0 (Micro-Mini Duo) model, and clean telemetry rules across canonical templates and framework documentation.
- **Files to modify:**
  - `docs/framework_philosophy_and_vision.md` (§3.1 Default Closed, §3.2 Adversarial TDD, §3.5 Tier 0 Duo)
  - `docs/decisions_and_roadmap.md` (ADR #18: Default Closed Tooling, ADR #19: Micro-Tier Duo & Adversarial TDD, update backlog)
  - `templates/AGENTS.md` & `templates/global/AGENTS.md` (North Star on Default Closed tooling)
  - `templates/team/system_prompt.md` & `templates/team/profile.md` (Rules 2, 5, 8: 2-handoff, 1 row telemetry, adversarial TDD)
  - `skills/manage-meta-project/SKILL.md` (Tier 0 Duo topology)
- **Tooling:** Python `scripts/sync_templates.py --write` to mirror templates.

### Task 2: CLI Utility for Observations Recording (P1.1)
- **Goal:** Eliminate human/agent formatting errors and race conditions in `observations.md` via an automated zero-dependency CLI.
- **Files to create/modify:**
  - `scripts/record_obs.py` (CLI with category validation, Markdown pipe escaping, cross-platform file locking via `msvcrt`/`fcntl`, `--pin` flag)
  - `tests/test_record_obs.py` (comprehensive TDD suite including adversarial malformed input and concurrency tests)
  - `skills/record-observation/SKILL.md` (update execution steps to invoke `record_obs.py`)

### Task 3: Policy Boundary Hardening & CODEOWNERS (P1.2)
- **Goal:** Protect security-critical enforcement scripts and policy files from autonomous agent tampering.
- **Files to modify/create:**
  - `.agents/project_knowledge/boundaries.md` & `templates/project_knowledge/boundaries.md` (move `scripts/check_boundaries.py`, `boundaries.md`, `.github/workflows/**` from Yellow to Red Zone)
  - `.github/CODEOWNERS` (assign human maintainer oversight to Red Zone policy files)
  - `tests/test_check_boundaries.py` (update expected zone classification tests)

---

## Sequential Prompts for Repository Agents

### Task 1 (P1.0): Architecture Calibration

#### Prompt 1.1 (`@agent-dev-lead`)
```markdown
@agent-dev-lead implement feature: калибровка North Stars, ADR #18–#19 и шаблонов ролей (Default Closed, Adversarial TDD, Tier 0 Duo)

Контекст: По итогам аудита P0 и согласования архитектурных принципов внедряется политика «Default Closed» для стороннего тулинга (закрытый контур по умолчанию, opt-in для сторонних утилит), обязательное требование негативного тестирования в TDD, топология Tier 0 (Micro-Mini Duo: Dev ➔ Inspector/Guardian) и ограничение телеметрии ролей 1 строкой на задачу.

Задача:
1. В docs/framework_philosophy_and_vision.md актуализируй:
   - §3.1: зафиксируй принцип «Default Closed Tooling» (нулевые зависимости по умолчанию; сторонние утилиты разрешены только при явном opt-in в спецификации; ответственность за сбои сторонних утилит ложится на проект/оператора).
   - §3.2: добавь «Adversarial Testing Invariant» (обязательное включение негативных и граничных проверок в TDD до перехода в Green).
   - §3.5: опиши режим «Tier 0 (Micro-Mini Duo)» для репозиториев <3–5k LOC (команда сокращается до дуэта: Developer ➔ Inspector/Guardian).
2. В docs/decisions_and_roadmap.md добавь:
   - ADR #18: Default Closed Tooling and Opt-In External Tools.
   - ADR #19: Micro-Tier Duo and Mandatory Adversarial TDD.
   - Обнови канонический бэклог (§7.3).
3. В templates/AGENTS.md и templates/global/AGENTS.md:
   - Синхронизируй формулировки инварианта тулинга (Default Closed) и требование негативного тестирования.
4. В templates/team/system_prompt.md и templates/team/profile.md:
   - Правило 2: зафиксируй 2-ступенчатую эстафету (Dev ➔ Guardian ➔ Steward) и режим Tier 0 Duo.
   - Правило 5: зафиксируй правило «1 строка телеметрии на задачу (Task Closeout) в profile.md».
   - Правило 8: зафиксируй требование Adversarial TDD.
5. В skills/manage-meta-project/SKILL.md добавь топологию Tier 0 (Micro-Mini Duo).
6. Выполни синхронизацию шаблонов:
   python scripts/sync_templates.py --write
   python scripts/sync_templates.py --check
7. Запусти тесты целостности:
   python -m unittest discover -s tests -p "test_integrity.py" -v
8. Внеси запись о завершении P1.0 в .agents/project_knowledge/tasks.md и 1 строку в .agents/team/agent-dev-lead/profile.md.
9. Передай эстафету роли agent-quality-guardian.
```

#### Prompt 1.2 (`@agent-quality-guardian`)
```markdown
@agent-quality-guardian verify meta-project structure: аудит калибровки архитектурных инвариантов и шаблонов ролей (P1.0)

Контекст: Роль agent-dev-lead выполнила задачу P1.0: зафиксированы ADR #18 и #19, обновлены vision, canonical templates, skills и правила телеметрии.

Задача:
1. Проверь паритет шаблонов:
   python scripts/sync_templates.py --check
   Убедись, что дрейф равен строго 0 (0 drift).
2. Запусти полный сьют тестов репозитория:
   python -m unittest discover -s tests -p "test_*.py" -v
   Убедись, что все 57 тестов проходят (OK).
3. Проверь 100% покрытие карты границ:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
4. Проверь корректность формулировок Default Closed в templates/AGENTS.md и templates/global/AGENTS.md.
5. Внеси 1 строку о верификации P1.0 в .agents/team/agent-quality-guardian/profile.md.
6. Передай эстафету роли agent-github-steward для коммита.
```

#### Prompt 1.3 (`@agent-github-steward`)
```markdown
@agent-github-steward git hygiene: фиксация коммита архитектурной калибровки P1.0

Контекст: Роли agent-dev-lead и agent-quality-guardian завершили и проверили реализацию задачи P1.0.

Задача:
1. Проверь статус рабочей копии:
   git status -s
2. Зафиксируй изменения в conventional commit:
   git add docs/ templates/ skills/ .agents/
   git commit -m "docs(core): calibrate default closed tooling, adversarial TDD, and Tier 0 duo topology"
3. Внеси 1 строку о фиксации P1.0 в .agents/team/agent-github-steward/profile.md.
4. Доложи о готовности к задаче P1.1.
```

---

### Task 2 (P1.1): CLI Utility for Observations (`scripts/record_obs.py`)

#### Prompt 2.1 (`@agent-dev-lead`)
```markdown
@agent-dev-lead develop component: разработка CLI-утилиты scripts/record_obs.py с валидацией категорий и файловой блокировкой

Контекст: Ручное добавление строк в observations.md агентами приводит к поломкам синтаксиса таблиц, рассинхрону категорий и гонкам при параллельной записи. Требуется создать надежную stdlib CLI-утилиту.

Задача:
1. В tests/test_record_obs.py напиши модульные и негативные (adversarial) тесты:
   - test_valid_observation_appends_row: проверка корректной вставки строки с текущей датой.
   - test_invalid_category_fails_exit_1: проверка отклонения невалидной категории.
   - test_pipe_escaping_in_issue_and_solution: проверка экранирования символов `|` в тексте проблемы и решения.
   - test_pinned_observation_flag: проверка добавления тега [pin] при флаге --pin.
   - test_file_lock_concurrent_access: проверка корректной работы файловой блокировки (msvcrt / fcntl).
2. Запусти тесты и убедись в падении (Red-фаза):
   python -m unittest discover -s tests -p "test_record_obs.py" -v
3. Создай scripts/record_obs.py на Python 3.10+ stdlib:
   - Аргументы: --category, --path, --issue, --solution, --pin, --obs-file (по умолчанию .agents/project_knowledge/observations.md).
   - Валидация категории по каноническому списку: [boundaries], [ci], [decommission], [incident], [orchestration], [runtime], [git], [init], [testing], [architecture].
   - Автоматическое экранирование пайпов `|` -> `\|`.
   - Кроссплатформенная блокировка файла перед чтением/записью.
4. Добейся прохождения тестов (Green-фаза):
   python -m unittest discover -s tests -p "test_record_obs.py" -v
5. Обнови skills/record-observation/SKILL.md для вызова record_obs.py.
6. Выполни синхронизацию шаблонов:
   python scripts/sync_templates.py --write
7. Добавь отметку в tasks.md и 1 строку в .agents/team/agent-dev-lead/profile.md.
8. Передай эстафету роли agent-quality-guardian.
```

#### Prompt 2.2 (`@agent-quality-guardian`)
```markdown
@agent-quality-guardian verify meta-project structure: независимый аудит CLI record_obs.py и проверка неразрушения базы наблюдений

Контекст: Роль agent-dev-lead реализовала утилиту scripts/record_obs.py и покрыла её тестами.

Задача:
1. Запусти модульные тесты утилиты:
   python -m unittest discover -s tests -p "test_record_obs.py" -v
   Убедись, что все тесты проходят.
2. Проверь работу утилиты вживую на временном файле:
   python scripts/record_obs.py --category runtime --path "scripts/record_obs.py" --issue "CLI verification test" --solution "Verified by QA guardian"
   Проверь, что строка корректно записана в .agents/project_knowledge/observations.md, а затем удали тестовую строку.
3. Запусти полный регрессионный сьют репозитория:
   python -m unittest discover -s tests -p "test_*.py" -v
4. Проверь аудит карты границ и паритет шаблонов:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
   python scripts/sync_templates.py --check
5. Внеси 1 строку о приёмке P1.1 в .agents/team/agent-quality-guardian/profile.md.
6. Передай эстафету роли agent-github-steward.
```

#### Prompt 2.3 (`@agent-github-steward`)
```markdown
@agent-github-steward git hygiene: проверка чистоты и коммит утилиты record_obs.py (P1.1)

Контекст: Утилита scripts/record_obs.py разработана и верифицирована.

Задача:
1. Проверь статус рабочей копии:
   git status -s
2. Проверь diff:
   git diff scripts/record_obs.py tests/test_record_obs.py skills/record-observation/
3. Зафиксируй изменения в conventional commit:
   git add scripts/record_obs.py tests/test_record_obs.py skills/record-observation/ .agents/
   git commit -m "feat(obs): implement robust stdlib CLI for atomic observations logging"
4. Внеси 1 строку в .agents/team/agent-github-steward/profile.md.
5. Доложи о готовности к задаче P1.2.
```

---

### Task 3 (P1.2): Core Boundary Hardening & CODEOWNERS

#### Prompt 3.1 (`@agent-dev-lead`)
```markdown
@agent-dev-lead implement feature: перевод охранных скриптов в Красную зону и создание .github/CODEOWNERS

Контекст: Для исключения несанкционированного изменения гейтов безопасности агентами файлы check_boundaries.py, boundaries.md и CI-конфигурация должны быть защищены статусом Red Zone и правилами CODEOWNERS.

Задача:
1. В .agents/project_knowledge/boundaries.md и templates/project_knowledge/boundaries.md:
   - Перенеси `scripts/check_boundaries.py`, `boundaries.md` (все файлы с этим именем) и `.github/workflows/**` в **Красную зону** (Red Zone).
   - Убедись, что в Жёлтой зоне этих путей больше нет.
2. Создай файл .github/CODEOWNERS:
   - Назначь владельца на файлы Красной зоны:
     ```text
     # Critical Security & Policy Enforcement
     /scripts/check_boundaries.py @maintainer
     *.md @maintainer
     .github/workflows/ @maintainer
     ```
3. В tests/test_check_boundaries.py актуализируй тесты:
   - Убедись, что тест test_red_zone_classification проверяет `scripts/check_boundaries.py` и `boundaries.md` как Red Zone.
4. Запусти тесты:
   python -m unittest tests/test_check_boundaries.py -v
5. Выполни синхронизацию шаблонов:
   python scripts/sync_templates.py --write
6. Внеси запись в tasks.md и 1 строку в .agents/team/agent-dev-lead/profile.md.
7. Передай эстафету роли agent-quality-guardian.
```

#### Prompt 3.2 (`@agent-quality-guardian`)
```markdown
@agent-quality-guardian verify meta-project structure: аудит ужесточения Красной зоны и правил CODEOWNERS (P1.2)

Контекст: Файлы политик переведены в Красную зону, создан .github/CODEOWNERS.

Задача:
1. Запусти аудит дерева границ:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
   Убедись, что 100% файлов покрыты, а количество файлов в Red Zone увеличилось соответственно.
2. Проверь блокировку при попытке симуляции правки Red Zone файла:
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --files scripts/check_boundaries.py
   Убедись, что команда завершается с кодом 1 и выводит `[RED ZONE VIOLATION]`.
3. Запусти полный регрессионный сьют:
   python -m unittest discover -s tests -p "test_*.py" -v
4. Проверь паритет шаблонов:
   python scripts/sync_templates.py --check
5. Внеси 1 строку о верификации P1.2 в .agents/team/agent-quality-guardian/profile.md.
6. Передай эстафету роли agent-github-steward.
```

#### Prompt 3.3 (`@agent-github-steward`)
```markdown
@agent-github-steward git hygiene: фиксация ужесточения Красной зоны и CODEOWNERS (P1.2)

Контекст: Перенос охранных скриптов в Красную зону и CODEOWNERS верифицированы quality-guardian.

Задача:
1. Проверь git status:
   git status -s
2. Зафиксируй изменения:
   git add .github/CODEOWNERS .agents/ templates/ tests/test_check_boundaries.py
   git commit -m "sec(boundaries): harden policy scripts into red zone and enforce CODEOWNERS"
3. Внеси 1 строку в .agents/team/agent-github-steward/profile.md.
4. Доложи о завершении спринта P1 (задачи P1.0, P1.1, P1.2).
```
