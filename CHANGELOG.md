# Changelog

Все заметные изменения в проекте **Meta-Project** документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/), и проект придерживается [Семантического версионирования](https://semver.org/lang/ru/).

**Политика версионирования:** `1.0.0-alpha.*` — ломающие изменения допустимы в любой момент (до-контрактная фаза). `1.0.0-beta.*` — обратная совместимость внутри beta-линии является заявленной целью; ломающие изменения вносятся только при переходе на следующую минорную серию (`1.0.0-beta.N` → `1.1.0-alpha.1`, никогда как патч или пре-релизный бамп внутри `1.0.0-beta.*`), каждое — с заметкой о миграции. `>=1.0.0` — строгое семантическое версионирование (SemVer).

---

## [Unreleased]

### Planned / В планах
- Интеграция обратной связи сообщества и эмпирические тесты на многоязычных репозиториях.
- Разработка шаблонов адаптеров для альтернативных агентных сред.
- Экосистема хуков (Волна Z3): тонкие адаптеры PreToolUse / SessionStart / compact_memory и установщик `hooks/install.py`.

---

## [1.0.0-alpha.9] - 2026-11-25

### Added / Добавлено
- **Волна Z2 — Нативные маркетплейс-манифесты и фильтрация дистрибуции (Vendor Packaging, §11.2)**:
  - Добавлены нативные манифесты для Codex CLI (`.agents/plugins/marketplace.json`), Cursor (`.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`) и Gemini CLI (`gemini-extension.json`) с единым версионированием из `templates/release_manifest.json`.
  - Реализована строгая fail-closed фильтрация в `scripts/sync_dist_branch.py`, допускающая перенос `.agents/plugins/**` в дистрибутивную ветку `main` с полной изоляцией dogfooding-файлов (`.agents/team/**`, `.agents/project_knowledge/**`, `.agents/reports/**`).
  - Резервирование каталога адаптеров хуков `hooks/**` в `boundaries.md` для Wave Z3.
- **Волна Z2 — Progressive Disclosure процедурных навыков (Scalability & Token Optimization, §11.2)**:
  - Вынесение объёмных каталогов сценариев, матриц компетенций и справочников устранения неполадок в лениво подгружаемые файлы `references/` (`skills/init-meta-project/references/scenarios.md`, `skills/manage-meta-project/references/competencies.md`, `skills/update-meta-project/references/troubleshooting.md`).
  - Сохранение лимита контекста ключевого навыка `manage-meta-project/SKILL.md` (230 строк при ограничении <= 240) с контрактом `MISSING_RESOURCE`.
  - Регистрация компонентов `references/` в `templates/release_manifest.json` и их автоматическое зеркалирование в `scripts/sync_templates.py` (включая флаг `--global-skills`).
- **Волна T — Доменная консолидация тестов и параллельный тестовый раннер (Test Optimization & Modernization, §11.0)**:
  - Высокопроизводительный параллельный тестовый раннер `tests/run_parallel.py` на базе Python stdlib (`concurrent.futures.ProcessPoolExecutor`) с планировщиком LPT (Longest Processing Time first) и ускорением прогона батареи более чем в 7 раз (с ~12–13 мин до ~55–60 с).
  - Консолидация разрозненных исторических волновых файлов (`test_*wave_*.py`) в стабильные доменные модули (`test_manifests_and_packaging.py`, `test_update_engine.py`, `test_update_engine_security.py`, `test_skills_and_templates_contracts.py`, `test_sync_and_resources.py`, `test_triage_incident.py`, `test_lifecycle_acceptance.py`, `test_common_and_envelopes.py`, `test_docs_invariants.py`).
  - Оптимизация тестовых фикстур git через шаблонное клонирование (`tests/_git_fixtures.py`), устранившая узкие места ввода-вывода при генерации тестовых репозиториев на Windows.
- **Волна K — Эпистемический триаж и дисциплина доказательств (Split-Runtime Silent-Failure Remediation, §10)**:
  - Процедурный навык `skills/triage-incident/SKILL.md` и детерминированная CLI-утилита `scripts/triage_incident.py` на Python stdlib (`probe`, `record-evidence`, `promote`, `check-tasks`, `artifact`).
  - Двухфазная структура `tasks.md` с разделением диагностических проб (`- [?] PROBE`), обязательного поля доказательства (`evidence:`) и задач на исправление (`- [ ] FIX`).
  - Эпистемические инварианты `Evidence-First Triage`, расширенный `Circuit Breaker` (опровергнутые гипотезы + аудит `Error-Path / Fallback-Masking`), `Toolchain Handoff Tripwire` и переносимая анти-угодливость в `templates/AGENTS.md`, `templates/team/system_prompt.md`, `skills/manage-meta-project` и `skills/ground-meta-project`.

### Fixed / Исправлено
- **Волна Z2 — Hardening ротации задач и декомпозиция монолитов (Memory Compaction & Monolith Decomposition, §11.2)**:
  - Идемпотентная вставка блока `> [!NOTE]` об архивации задач в `scripts/compact_memory.py` с автоматическим схлопыванием дубликатов.
  - Гарантированное best-effort удаление `.lock`-файла после освобождения файловой блокировки в `compact_memory.py` (выравнивание с `record_obs.py` и `triage_incident.py`).
  - Защита активных чекпоинтов `- [>]` и диагностических блоков `- [?] PROBE` от случайной архивации при ротации `tasks.md`.
  - Декомпозиция крупноблочных монолитов ядра (ADR #22): разделение `scripts/inspect_meta_project.py`, `scripts/manage_reports.py` и `scripts/update_meta_project.py` на компактные модули (`_inspect_classifier.py`, `_report_models.py`, `_report_intake.py`, `_update_bundle.py`, `_update_merge.py`) с сохранением 100% обратной совместимости CLI и публичных импортов.
- **Волна Z1 — Устранение дефектов ядра, резолв плагинов и гигиена срезов (Core P1 Defects & Slice Hygiene, §11.1)**:
  - Нормализация форматов `input_fingerprints` (поддержка `list` и `dict`) в проверке устаревания отчётов `scripts/manage_reports.py` и синхронизация схемы `templates/reports/update_report.json`.
  - Зеркалирование ресурсов навыков (`resources/`) при глобальной синхронизации `scripts/sync_templates.py --global-skills`.
  - Динамический резолв корневого каталога скриптов `__root` в навыках (`skills/*/SKILL.md`) для поддержки сред с нативными кэшами плагинов (Claude Code, Cursor, Codex).
  - Автоопределение единственной активной инсталляции при запуске `scripts/inspect_meta_project.py --harness auto` (устранение ложного отказа при однозначной топологии).
  - Актуализация срезов знаний `architecture.md` и `weak_spots.md`, выравнивание флагов запуска утилит в `AGENTS.md` (§5).
- **Волна K.1 — Усиление шлюзов эпистемического триажа и зависимостей манифеста**:
  - Строгая валидация доказательств в шлюзе `triage_incident.py promote` (отклонение trailing-гипотез без верифицированного `evidence:`).
  - Явное декларирование зависимости `scripts/triage_incident.py` для навыка `ground-meta-project` в `templates/release_manifest.json` и детерминированный fallback-путь.
  - Синхронизация системных промптов и профилей 7 активных ролей команды (`.agents/team/`) с инвариантами Wave K (Правила 1–13, §4.8).

### Planned / В планах
- Интеграция обратной связи сообщества и эмпирические тесты на многоязычных репозиториях.
- Разработка шаблонов адаптеров для альтернативных агентных сред.

---

## [1.0.0-alpha.8] - 2026-11-19

### Added / Добавлено
- **Автоматизация релизов и замки версий**:
  - GitHub Actions workflow `release.yml` автоматически публикует релиз и артефакты при пуше тега `v*` с fail-fast проверкой соответствия версии манифесту и CHANGELOG.
  - Замок паритета бейджей версий в `README.md` и `README.ru.md` в `tests/test_integrity.py`.
- **Защита от Anchoring Bias и детекция среды выполнения (Step 89)**:
  - Автоопределение хост-харнесса (`detect_host_harness`) в `scripts/inspect_meta_project.py` и `scripts/verify_identity.py`.
  - Инвариант самоидентификации среды Step 0 в `init-meta-project` и Rule 11 (Anti-Anchoring Invariant) в системных промптах ролей.
- **Волна I — Audit Response III**:
  - Честный CLI-парсинг гейта границ (префиксные глаголы `python/pytest/git/pip`, разбор списков через запятую).
  - Верифицируемый `--read-only` через `sys.addaudithook`.
  - Замок 100% покрытия границ дерева репозитория (`--audit-tree`).
  - Автоматизация зеркалирования чистой дистрибуции `scripts/sync_dist_branch.py`.

### Fixed / Исправлено
- Исправлена совместимость CI-матрицы с Python 3.10 (`pyflakes==4.0.3`).
- Исправлена работа `scripts/sync_dist_branch.py` с `git ls-tree` и путями исключений.

---

## [1.0.0-alpha.7] - 2026-11-17

### Added / Добавлено
- **Волна P — Plugin Packaging: установка в один комманду через три канала**:
  - **Три манифеста каналов**: `plugin.json` (Agent Plugins 1.0.0), `.claude-plugin/plugin.json` (Claude Code plugin), `.claude-plugin/marketplace.json` (маркетплейс) — версионные замки приравнивают `version` обоих манифестов к `framework_version` релизного манифеста (single source of truth).
  - **Лицензионно-совместимый frontmatter** во всех девяти скиллах (`license`, `compatibility`) — требование плагинных каналов; ресурсные копии ресинхронизированы (0 drift).
  - **Каналы установки в README** (EN/RU): one-command пути для Claude Code plugin, Agent Plugins и skills.sh.
  - **CI-валидация формата** манифестов (pinned, non-blocking — Default Closed Tooling); zero dual-canon: скрипты остаются в корне репо, requires-граф — честная декларация зависимостей (per-skill embedding отклонён по уроку волны G).
  - `framework_version` = `1.0.0-alpha.7` (= тег = оба plugin-манифеста).

### Fixed / Исправлено
- **D7 (Step 86)**: частичное использование тройки sanction-флагов гейта падало сырым TypeError в глубине sanction-ридера (`open(NoneType)`); fail-closed сохранён, поверхность — чистая argparse usage error (rc=2) с именованием недостающих флагов.

---

## [1.0.0-alpha.6] - 2026-11-17

### Added / Добавлено
- **Волна G — Context Economy II и гигиенический хвост**:
  - **manage-slim (lane S, init-P2 паттерн)**: встроенные team-шаблоны вынесены в `skills/manage-meta-project/resources/` (байт-копии `templates/team/*`); SKILL.md сокращён 394 → ~230 строк с сохранением контракта загрузки ресурсов (конверт `MISSING_RESOURCE`), таблицы 5 операций и инвариантов топологии; `sync_templates` перевёл manage с EMBEDDED_TARGETS на RESOURCE_TARGETS; манифест вырос до 12 ресурсных компонентов (kind `resource`, requires manage-скилл) — runtime-layout маппинг движка покрывает их без изменений.
  - **`--facts-digest` (lane I)**: `inspect_meta_project` отдаёт детерминированный компактный JSON-отпечаток «проверенных фактов» (состояние репо, sha256 пяти срезов + реестра, матрица возможностей, версия тулинга); байт-стабилен на одинаковых входах; zero-write; ground-скилл: застэшенный дайджест заменяет перечитывание неизменённых срезов, несовпадение называет ровно те срезы, которые стоит перечитать.
  - **Словарь примитивов (lane D)**: `docs/primitives.md` — 4 повторяющиеся операции, смаппленные на работающие реализации (survey → `inspect_meta_project`, identity admission → `verify_identity.evaluate_actor_admission`, report intake → `manage_reports.evaluate_manage_intake`, observation recording → `record_obs.record_observation`).
  - **Канон документации (lane D)**: section-map drift устранён (decommission — канонические 8 секций паспорта; scan — фактический проверяемый набор секций); tune-поля протокола переведены на английский (артефактные поля, двуязычная-интервью-исключение не применяется).
- **Манифест**: `framework_version` = `1.0.0-alpha.6` (= тег).

### Removed / Удалено
- **Мёртвый код движка (lane H, U4/U10)**: `BaseUnavailableError` (никогда не поднимался) и `_atomic_write_text` (не вызывался) удалены; grep-lock тест против регенерации; мёртвый флаг `--full` команды `check` снят вместе с остатками парсинга.

### Fixed / Исправлено
- **EOL false-drift контракт (lane H)**: LF-запись в lock + CRLF-копия в рабочем дереве (симуляция свежего чекаута с autocrlf) больше не даёт ложный `drifted` — `check`/`plan` отдают диагностическое `eol_normalized: true`, когда LF-нормализованные байты совпадают с записью lock; подделка контента по-прежнему детектируется (EOL-флип — не тамперинг; семантика lock/installed_sha неизменна).

### Known Limitations / Известные ограничения
- SHA-привязанная авторизация Red-Zone правок мейнтейнером — [ОБНОВЛЕНО 2026-11-18] реализована волной H (механизм `.github/red-zone-sanction.json` + проверка пре-пуш base + push-actor, 13 adversarial тестов); Branch Protection: single required check **`All Checks Green`** (агрегат `all-checks` переименован) — действие владельца.
- Ресурсные байт-копии — parity с нормализацией EOL (контракт lane H); CRLF-writer синхронизатора — вне волны.

---

## [1.0.0-alpha.5] - 2026-11-17

### Added / Добавлено
- **Волна F — периметр безопасности (Security Perimeter)** — по внешнему аудиту v1.0.0-alpha.4 (7.5/10) и дополнению аудитора, триаж принят владельцем:
  - **Периметр движка обновления (lane FX, adversarial RED-first)**: сдерживание обхода путей для source/компонентных путей; отказ от подделанных байтов кеша (sha256-mismatch); исключение параллельного `apply` блокировкой; injected argv и мёртвый git — fail-closed; защищённое состояние с конвертами диагностики (26 состязательных тестов).
  - **Периметр отчётов (lane FR)**: отказ небезопасных идентификаторов, упрочение сериализации, исключение параллельной записи, структурные конверты (34 теста); схемы init/manage-отчётов обновлены.
  - **Консолидация `_common.py` (lane FC, ADR #22)**: общий модуль (`_error_envelope`, `_utc_now_iso`, git-subprocess helper, lock helper); все утилиты мигрированы на общие помощники; в манифесте граф зависимостей `requires` (прецедент: inspect/manage) — `_common` зарегистрирован как компонент, импортёры объявляют ребро; контракт закреплён тестами (single-source wiring, duplication lock).
  - **CI (lane FD, Red Zone — санкционировано планом, trusted-base не ослаблен)**: leg `windows-latest` × Python 3.12; **стабильный aggregate-job `all-checks`** поверх четырёх матричных имён + windows leg — одно имя для required checks; smoke-проверка rc-контракта `check` на синтетических репо (0 up-to-date / 1 updates-found); шаг `verify_identity --check`.
  - **Паспорт**: два новых North Star — Default Closed Tooling и Adversarial Testing Invariant (устранено живое нарушение собственного sync-инварианта).
- **Манифест**: `framework_version` = `1.0.0-alpha.5` (= тег).

### Fixed / Исправлено
- Документационный дрейф: бейджи README на линию релиза, карта CONTRIBUTING → 8 скриптов, D2 помечен resolved-in-alpha.3, snapshot-маркеры на исторических документах, устаревший оверрайд 2026-11-06 закрыт с резолюцией; сырой бэклог-чат перемещён в `docs/archive/`, структурные диспозиции — `docs/backlog-astra-dispositions.md`.
- Гигиена: редактирование остаточных machine-username вхождений в `.agents/**` → `machine username (redacted)`; NOTE-dedup в tasks.md (рецидив исправленного дефекта).
- Тесты: дедупликация байт-дубликата drift-теста; live-repo `--write` тесты переведены на temp-clone фикстуры; alpha-хардкод заменён локом «манифест == последний заголовок CHANGELOG»; устранён мёртвый класс — без ослабления ассертов.

### Known Limitations / Известные ограничения
- CRLF-конверсия ресурсных байт-копий и writer'а синхронизатора — вне волны (parity с нормализацией).
- Механизм SHA-привязанной авторизации Red-Zone правок мейнтейнером — открыт; **Branch Protection упростился**: с агрегатом `all-checks` достаточно одного required check имени.

---

## [1.0.0-alpha.4] - 2026-11-16

### Added / Добавлено
- **Волна E — экономия контекста (Context Economy)**:
  - **Компактные проверяемые форматы (lane T)**: шаблоны срезов `architecture.md` (depends-on колонка карты компонентов, условные e2e-флоу) и `tasks.md` (правило чекпоинтов `- [>]`) ужаты без потери верифицируемых инвариантов; текст init-скилла сокращён с ресинхронизацией встроенных блоков.
  - **Канон делегирования и маршрутов (lane C)**: Execution Routes (short/normal/extended — по последствиям и неопределённости; обязательные проверки согласованного сценария сохраняются всегда) и указатель на маршрутизацию делегирования в manage-meta-project (Phase 2 Execution Routing); tune-отчёты несут блок стоимости (`cost`: rereads, tool_calls, handoffs, rework, wall_time_s).
  - **Единые конверты ошибок (lane E)**: утилитарный пояс (check_boundaries, verify_identity, inspect_meta_project, manage_reports, record_obs, sync_templates, update_meta_project, compact_memory) отдаёт структурированную диагностику (код + сообщение + следующий шаг) вместо «голых» строк; compact_memory защищает чекпоинт-строки `- [>]` как блоки активной работы.
  - **Пилот ленивой загрузки init (lane P, evidence-gated)**: канонические источники вынесены в `resources/` скилла (байт-копии через sync_templates); явный контракт загрузки — повторная проверка исправной установки не читает шаблоны, чистая инициализация читает только необходимые, путь нового харнесса — только свою процедуру; отсутствующий обязательный ресурс блокирует зависимый шаг с конвертом `MISSING_RESOURCE`. Ресурсы объявлены в манифесте как новый сорт компонентов (`kind: resource` с зависимостью от init-скилла); `framework_version` = `1.0.0-alpha.4` (= тег).

### Known Limitations / Известные ограничения
- Ресурсные байт-копии чувствительны к CRLF-конверсии чекаута (`core.autocrlf`): parity проверяется с нормализацией переводов строк; конвертация writer'а синхронизатора остаётся вне волны.
- SHA-привязанная авторизация Red-Zone правок мейнтейнером — [ОБНОВЛЕНО 2026-11-18] реализована волной H этой же линейки (см. Added — волна H); Branch Protection на `main` — ручное действие владельца: single required check **`All Checks Green`** (агрегат; четыре матричных имени больше не нужны).

### Added / Добавлено — волна H (в этой же линейке, между alpha.6 и alpha.7)
- **SHA-привязанная санкция мейнтейнера (roadmap 7.2.2 п.4)**: `.github/red-zone-sanction.json` едет во входящем пушe, но верифицируется против пре-пуш base SHA (инвалидация при каждом новом пушe автоматична); push-actor дважды сверяется с авторизованным мейнтейнером; explicit-path покрытие, Default Deny не санкционируется; 13 adversarial тестов (`test_red_zone_sanction.py`).
- **Dist-гварды CI**: trusted-base шаги и identity-шаг скипаются на дистрибутивных ветках (`hashFiles(.agents/**)`) — чистый main гоняет тесты и parity без boundary-политики.
- **sync absent-mirror контракт**: дистрибутивное дерево без `.agents/skills/` валидно (mirror-parity применяется только при наличии зеркала).
- **`.gitattributes` `* text=auto eol=lf`**: корневой фикс CRLF-квирка (консистентные LF-чекауты).

---

## [1.0.0-alpha.3] - 2026-11-16

### Added / Добавлено
- **Волна D — целостность состояния и периметр движка обновления**:
  - Офлайн-фоллбэк кеша (D2): точный SHA + мёртвый origin + интегральный кеш теперь применяется через CLI (`origin=cache`); не-SHA ссылки по-прежнему отклоняются.
  - Расширение базовых кандидатов (D6): пиннинг-бандл участвует в подборе базы (повторный `apply` того же SHA больше не принуждается к `needs_base`), база берётся из origin-истории по lock-записи при смене пина.
  - Маппинг на runtime-layout: обновления движка попадают в раскладку, развёрнутую init (`.agents/skills/`), по авторитету записанных целей — вместо дублирования корневых копий.
  - Целостность согласованного плана: `apply` сверяется с `.agents/update-plan.json`, зафиксированным в update-отчёте (`approved_plan_file`).
  - `--adopt-existing`: усыновление init-скаффолда по sha-match при первом запуске движка; режим сводки плана вместо дампа полного содержимого.
  - Фоллбэк чтения манифеста: `manifest.json` → `templates/release_manifest.json` в origin.
- **Контракты: манифест приведён к машиночитаемому виду (D4/D5)**: 32 файловых компонента вместо directory-kind групп (интегральный-bundle контракт движка), включая сам `scripts/update_meta_project.py` (установка может обновить свой обновлятор); `framework_version` поднят до `1.0.0-alpha.3`.
- **Санкционирование Red Zone — сузилось**: scoped-овермайт `META_PROJECT_ALLOW_RED_ZONE=1` в pre-commit хуке (только явная единица, fail-closed; Default Deny никогда не пропускается) — административный `--no-verify` больше не нужен; SHA-привязанная авторизация мейнтейнера остаётся открытым пунктом.
- **tune-отчёты через CLI** и усиление допуска manage: `verify_declared_registry_delta` сверяет заявленные изменения с восстановленным базлайном реестра.
- **Единая категорийная шкала record_obs (D8)**: 16 категорий, документация скилла и движок синхронизированы (parity-тест doc==engine); легаси-теги живых баз (`deps`, `db`, `api`, `test`, `env`…) остаются принятыми.
- **Скаффолд init доставляет `.gitignore`** — соседний `.lock` от record_obs больше не ловит Default Deny на первых коммитах.

### Fixed / Исправлено
- D7: маркеры `local_repo_data` в кодовой форме (`# local_repo_data:TAG`) теперь распознаются наравне с HTML-комментариями — адаптации помеченных `.py` больше не дают жёсткий конфликт.

### Known Limitations / Известные ограничения
- SHA-привязанная авторизация санкционированных Red-Zone правок мейнтейнером — открыта (овермайт решает локальную эскалацию, не CI-доказательство).
- Кроссплатформенная CRLF-конверсия записи глобальных кешей скиллов (`sync_templates --global-skills --write` на Windows) — задокументирована в observations, вне волны.
- Branch Protection на `main` — по-прежнему требует ручного действия владельца (4 матричных имени required checks / aggregate-job, review+dismissal, запрет force-push).

---

## [1.0.0-alpha.2] - 2026-11-15

### Added / Добавлено
- **Управляемый движок обновления (волна 0.9.0, ADR #21)**: `scripts/update_meta_project.py` — SHA-пиннинг (произвольный ref разрешается ровно в один commit SHA; весь комплект компонентов материализуется строго из него), интегральный кеш с объявленным происхождением (частичный кеш отвергается, смешивание ревизий запрещено), zero-write `check`/`plan`, атомарный `apply` с журналом отката и update-отчётом, `restore` собственных изменений движка; `Bundle.base` сверяется по sha256 из lock (пустая база → `needs_base`, никогда не «safe merge» вслепую). Fetch бандла — через `git cat-file blob` (иммунитет к LF/CRLF-конверсии `git archive` на Windows).
- **Контракты компонентов: манифест ≠ lock (ADR #21)**: канонический манифест релиза `templates/release_manifest.json` (все доступные компоненты, типы, зависимости, миграции) и проектный lock `.agents/framework-lock.json` в целевых репозиториях (фактически установленное подмножество с sha256 каждого компонента); минимальный скаффолд остаётся валидной установкой, количество компонентов не заморожено. Релизы — слой удобства выбора версий, а не предусловие SHA-пиннинга.
- **Типы отчётов update и tune**: `scripts/manage_reports.py` расширен до `--type {init,manage,update,tune}` (на `latest`/`verify`); схемы `templates/reports/update_report.json` и `templates/reports/tune_report.json`; completed update-отчёт запрещает незакрытые конфликты.
- **Переработка `ground-meta-project` (Part 2)**: двухрежимный навык восстановления контекста и диагностики дрейфа — семантические триггеры вместо механических счётчиков, выборочное чтение канонических источников, идентичность через валидатор (сессия/пользователь назначает роль — реестр не подбирает агенту новую), условное продолжение вместо безусловной остановки; восстановление цели/состояния/идентичности/полномочий после смены сессии, переносов, обновлений и компакции.
- **Переработка `tune-meta-project` (Part 3)**: evidence-based калибровка вместо механических эвристик — разделение фактов и гипотез, проверяемые предложения через manage/update/decommission, верификация эффекта, гарантия повторяемости, read-only инвариант анализа, интеграция tune-отчётов.
- **Семантический Circuit Breaker и матрица ответственности скиллов**: паспорт, канонические шаблоны и системные промпты всех ролей переведены на семантический сигнальный инвариант (повторно падающие правки одного дефекта или регрессии в соседнем коде → обязательная трассировка пути данных; нормальный TDD-цикл нарушением не считается); добавлена матрица owns / must-not-do для init / manage / update / ground / tune.
- **Контрактные lock-in тесты волны**: +13 тестов в `tests/test_audit_regressions.py` (канон без механических счётчиков; контракты ground ×5; контракты tune ×7) и 17 тестов движка в `tests/test_update_meta_project.py`; итог серии — 197/197.
- **Набор навыков жизненного цикла репозитория (Tri-Skill Lifecycle Suite)**:
  - skills/scan-meta-project/ — навык экспресс-сканирования (--shallow) и глубокого аудита (--deep) целостности мета-знаний, проверки 100% покрытия границ и поиска слепых зон.
  - skills/tune-meta-project/ — навык калибровки и оптимизации агентной среды: диагностика трения Git, адаптация топологии ролей и кристаллизация фундаментальных инвариантов (не более 3 North Stars).
  - skills/update-meta-project/ — навык безопасного обновления фреймворка с GitHub или локального кэша с сохранением всех проектных данных в блоках local_repo_data.
- **Детектор архитектурного дрейфа (Architecture Drift Warning)**:
  - Эвристика мягкого предупреждения в scripts/check_boundaries.py: неблокирующее предупреждение при добавлении кодовых модулей (src/**, app/**, lib/**, skills/**) без актуализации architecture.md.
- **Регламент Definition of Done (Silent Pre-Close Checklist)**:
  - Обязательный чек-лист в системных промптах ролей (templates/team/system_prompt.md и активных промптах): актуализация architecture.md, закрытие рисков в weak_spots.md и фиксация телеметрии в profile.md.
- **Синхронизация глобального кэша навыков харнесса (Step 61)**:
  - Режим `--global-skills` в `scripts/sync_templates.py` для публикации всех канонических навыков в глобальный кэш харнесса (например, `~/.gemini/config/skills/`) поверх локального зеркала `.agents/skills/`.
- **Параллельная мультихарнессная установка**:
  - Активация второй параллельной установки `zc-main` (harness `zcode`) с полным трио ролей и отчётами сценариев в `.agents/reports/zc-main/` — практическое подтверждение протокола Scenario 4 (`HEALTHY_NEW_HARNESS`).

### Fixed / Исправлено
- **Полное устранение находок внешнего аудита коммита `38deed9` (стадии S2–S9, Steps 62–64)**:
  - S2 (гейт границ и CI): fail-closed git-запросы в `scripts/check_boundaries.py`, `--no-renames`, область действия `--repo-root`, парсинг переименований в режиме status; `ci.yml` переведён на доверенную базовую ревизию (гейт и политика материализуются из зафиксированного base SHA, пустой diff — явный отказ, LICENSE исключён из push paths-ignore); владелец закреплён в `CODEOWNERS` (`@vlv-code`).
  - S3 (идентичность): энумы схемы и статусов реестра `.agents/meta-project.json`, сопоставление харнесс↔установка, структурированная диагностика корня, валидность реестров без команды, `planned` ≠ допуск.
  - S4 (инспектор): 8-е каноническое состояние `CONTEXT_UNRESOLVED`, обязательная валидность паспорта и реестра для HEALTHY-статусов, возможности ролей в рамках конкретной установки, корректный учёт worktree toplevel и хуков.
  - S5 (manage intake): движок допуска `evaluate_manage_intake`, контроль свежести по отпечаткам входных данных, сдерживание относительных указателей, запрет перезаписи `run_id`, surfaced latest-attempt, идентичность проекта из реестра, отказ для отчётов со статусом completed и пустым сценарием.
  - S6 (документация): переименование `--component` → `--path` в `scripts/record_obs.py` и всех зеркалах (паспорт, шаблон, скиллы).
  - S8 (pre-commit хук): диспетчер с исполнением легаси-хука отдельным процессом, поддержка worktree и `core.hooksPath`, детекция конфликта с внешними менеджерами хуков.
  - S9 (память): вставка строк внутрь таблицы, подавление точных дубликатов, атомарная запись, lock-free `--dry-run`, дедупликация NOTE с возвращением осиротевших записей, fail-closed `--write` с повторной верификацией в `sync_templates.py`.
  - RED-базлайн воспроизведения зафиксирован в `tests/test_audit_regressions.py` (42 теста: 39 RED-воспроизведений + 3 lock-in) и `docs/audit_38deed9_regressions_baseline.md`; независимая верификация Гвардиана (Step 64) на до-фиксном экспорте `38deed9`: GREEN достигнут без ослабления ассертов; итог — 161/161 тестов, 0 drift, 100% покрытия границ (128 файлов), живая приёмка §10 пройдена.
- **Закрытие послеприёмочного хвоста аудита (Step 65)**: CLI `manage --action create` в `scripts/manage_reports.py` теперь проверяет существование init-запуска на диске и прогоняет его через `evaluate_manage_intake` (fail-closed rc=1 со структурированными ошибками) — прежнее известное ограничение снято; переработан `resolve_team_topology` по приоритетам §5/§6 аудита (явный `collaboration_model` не понижается LOC-эвристикой, `specialized_swarm` → `supported:false`, противоречивые пожелания попадают в список конфликтов); закреплено CLI-уровневым состязательным тестом `test_manage_create_cli_enforces_intake` и 3 RED-first тестами приоритета топологии (165/165).
- Кроссплатформенная безопасность вывода: замена Unicode-эмодзи в stderr/stdout check_boundaries.py на ASCII-маркеры для предотвращения UnicodeEncodeError в консолях Windows (cp1251).
- Относительные пути и ссылки на корневые документы в документации docs/.
- Включение обязательного ключа --audit-tree в GitHub Actions CI воркфлоу для проверки 100% покрытия файлов репозитория.

### Known Limitations / Известные ограничения
- **D2 (открыто, weak_spots §3)**: офлайн-путь через кеш недостижим из CLI `update_meta_project.py apply` — ref повторно резолвится по недоступному origin до обращения к `--cache-dir`; библиотечный контракт корректен и покрыт юнит-тестами. План исправления зафиксирован.
- **Санкционирование Red-Zone правок (открыто, ADR #21 п.4)**: подтверждение пользователя + локальный `--allow-red-zone` — временный локальный механизм, не доказывающий разрешение в CI; до создания SHA-привязанной авторизации движок обновления отказывает в автоматическом изменении защищённых компонентов и сообщает ручной путь.
- **Branch Protection на `main` не настроен** (`protected: false`): required checks матрицы, обязательный review с dismissal и запрет force-push — требуется действие владельца (роадмап §8.4).
- **Перезагрузка инструкций харнессом** после обновления не автоматизирована: живая сессия может нести до-волновой текст инвариантов, пока канон репозитория уже обновлён — перезапуск сессии/харнесса вручную.

---

## [1.0.0-alpha.1] - 2026-11-10

### Added / Добавлено
- **Машинный контроль границ и защита репозитория (Boundary Gate CLI & CI Enforcement)**:
  - Разработка zero-dependency утилиты `scripts/check_boundaries.py` на чистом Python 3.10+ stdlib для инспекции `git diff` локально и в GitHub Actions CI.
  - Поддержка трех зон ответственности: Зеленая (свободная модификация), Желтая (регрессионные тесты, шаблоны, форматирование с запретом ослабления `assert`), Красная (паспорт `AGENTS.md`, базы данных, секреты, миграции, CI/CD).
  - Реализация жесткого инварианта Default Deny (Черная зона): любые неклассифицированные файлы верхнего уровня блокируют коммит с кодом 1.
  - Режим `--audit-tree`: полное сканирование дерева репозитория с гарантией 100% покрытия директорий и обнаружением слепых зон.
  - Режим `--install-hook`: автоматическая генерация исполняемого кроссплатформенного pre-commit хука в `.git/hooks/pre-commit` для превентивной блокировки коммитов с нарушениями границ.
  - Устранение утечки `AGENTS.md` в Green Zone при наличии поясняющих комментариев в скобках.
  - Дифференциация тестов: специфичные маски файлов (`tests/test_*.py` в Green) имеют приоритет над общими масками каталогов (`tests/**` в Yellow).
  - Включение обязательного шага Boundary Gate в матричный CI (`.github/workflows/ci.yml`) для Python 3.10, 3.11, 3.12, 3.13.
- **Защита от деградации контекста и компактификация памяти (Context Rot Shield & Memory Compaction)**:
  - Разработка zero-dependency утилиты `scripts/compact_memory.py` для автоматической ротации разросшихся таблиц `.agents/project_knowledge/observations.md` (>20 строк) и выполненных задач `tasks.md` в архивные файлы каталога `.agents/project_knowledge/archive/`.
  - Механизм постоянных инвариантов `[pin]`: записи в `observations.md` с тегом `[pin]` (архитектурные правила, платформенные нюансы) перманентно удерживаются в активной таблице и защищены от архивации.
  - Поддержка dry-run режима (`--dry-run`) для безопасного предпросмотра изменений в CI и при локальном тестировании.
- **Автоматическая синхронизация шаблонов и паритет навыков (Template Injection & Skill Parity Synchronizer)**:
  - Разработка zero-dependency утилиты `scripts/sync_templates.py` для устранения проблемы «трёх копий» шаблонов.
  - Автоматическая инъекция канонических шаблонов из `templates/` во встроенные строковые блоки навыков `skills/init-meta-project/` и `skills/manage-meta-project/`.
  - Обеспечение строгого 1-в-1 зеркалирования канонических файлов `skills/` в локальное рабочее окружение `.agents/skills/`.
  - Режим `--check`: запуск в составе `tests/test_integrity.py` и GitHub Actions CI с кодом 1 при обнаружении любого дрейфа.
  - Режим `--write`: автоматическое синхронное обновление всех зависимых копий на месте.
- **Командный трекинг задач и расширение инициализации (Task Provenance & Target Scaffolding)**:
  - Внедрение стандартизированного среза `.agents/project_knowledge/tasks.md` для фиксации активных целей, задач и делегированных шагов с ролевым авторством `[agent-id @ ISO_DATETIME]`.
  - Включение `tasks.md` в Directive Meta-Knowledge Protocol в канонических шаблонах `templates/AGENTS.md` и `templates/global/AGENTS.md`.
  - Расширение навыка `skills/init-meta-project/`: автоматическая доставка исполняемых скриптов обвязки `scripts/check_boundaries.py` и `scripts/compact_memory.py` в целевые репозитории при инициализации в режиме Shared Setup.
  - Дополнение карт репозитория в `CONTRIBUTING.md` и `CONTRIBUTING.ru.md` каталогом `scripts/` и полным набором из 6 автономных навыков.
- **Комплексный тестовый контур (Integrity & Unit Test Suite)**:
  - Расширение набора автотестов до 47 проверок (100% прохождение без внешних зависимостей на чистом Python 3.10+ stdlib).
  - Добавлены модульные тесты гейта границ `tests/test_check_boundaries.py` (парсинг зон, маски glob, приоритеты, CLI, аудит дерева, установка хуков).
  - Добавлены модульные тесты компактификации памяти `tests/test_compact_memory.py` (ротация наблюдений, удержание `[pin]`, архивация задач).
  - Добавлены модульные тесты синхронизатора шаблонов `tests/test_sync_templates.py` (инъекция шаблонов, обратные кавычки, паритет директорий).
- **Архитектурные инварианты и надежность сред (Polyglot Monorepo Remediation & Platform Invariants)**:
  - Реализация инварианта Default Deny (Black Zone / Unmapped Paths) в `templates/project_knowledge/boundaries.md` и покрытие тестом `test_boundaries_default_deny_invariant`.
  - Добавление инвариантов Circuit Breaker и Target State Audit в шаблон системного промпта (`templates/team/system_prompt.md`).
  - Введение обязательного сквозного моделирования потоков данных (Pre-Flight Flow Tracing) в архитектурный шаблон (`templates/project_knowledge/architecture.md`).
  - Правила Polyglot Isolation, Mandatory Dispatcher и Zero Unmapped Dirs в навыках `init-meta-project` и `manage-meta-project`.
  - Добавление процедурного навыка декоммиссии и архивации ролей `skills/decommission-meta-project/` (поддержка безопасного переноса контекста в `.agents/team/archive/`).
  - Добавление процедурного навыка экстренного заземления `skills/ground-meta-project/` (остановка хаотичных правок, зум-аут и рекалибровка контекста).
  - Развертывание и регистрация канонической компактной триады ролей (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`).
- **Синхронизация документации и CI/CD (Code-to-README Parity & CI Optimization)**:
  - Синхронизация `README.md` и `README.ru.md`: добавление `skills/decommission-meta-project/`, среза `tasks.md`, шаблона `system_prompt.md` и оркестровки команды в дерево структуры и быстрый старт.
  - Оптимизация триггеров CI в `.github/workflows/ci.yml`: удалена маска `**.md` из `paths-ignore`, обеспечен запуск проверок при пушах изменений в навыки (`skills/**`) и шаблоны (`templates/**`).
- **Локализация экосистемы на английский язык и двуязычный фасад (English Ecosystem Localization & Bilingual Facade)**:
  - Полный перевод канонических шаблонов (`templates/`) и процедурных навыков (`skills/`) на английский язык как канонический.
  - Локализация активного окружения агентов (`AGENTS.md`, `.agents/`).
  - Создание двуязычного публичного фасада репозитория: `README.md` и `CONTRIBUTING.md` (английский канон) с русскоязычными версиями `README.ru.md` и `CONTRIBUTING.ru.md`.
  - Адаптация тестов целостности (`tests/test_integrity.py`) для поддержки англоязычных и двуязычных контрактов секций и зон.
  - Приведение шаблонов задач и pull requests (`.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/`) к единообразной англоязычной терминологии.

---

## [1.0.0-alpha] - 2026-11-06

### Добавлено
- **Базовая двухуровневая архитектура контекста агентов**:
  - Корневой навигатор `AGENTS.md` (North Stars, базовые инварианты, делегирование навыкам).
  - Каталог мета-знаний `.agents/project_knowledge/` с прогрессивным раскрытием контекста.
- **Шаблоны мета-знаний и команды (`templates/`)**:
  - `boundaries.md`: Разграничение зон ответственности через машиночитаемые glob-паттерны (зеленая, желтая, красная зоны).
  - `architecture.md`: Верхнеуровневый срез компонентов, потоков данных и инвариантов состояния.
  - `weak_spots.md`: Реестр хрупких модулей, рисков рантайма и технического долга.
  - `observations.md`: Накопительный журнал граблей и находок агентов (атомарная запись в 1 строку таблицы).
  - `tasks.md`: Командный трекинг задач с авторскими таймстемпами и блоком делегирования.
  - `team/`: Шаблоны паспорта роли (`profile.md`) и приватных заметок роли (`notes.md`).
- **Процедурные навыки (`skills/`)**:
  - `init-meta-project` (ранее `init-project-agent`):
    - Двухпроходная инициализация репозиториев (Паспорт -> Срезы).
    - Обязательный чек-лист чтения критических модулей (Core Inspection Checklist).
    - Протокол атомарной выгрузки знаний без дублирования (In-Memory Synthesis Flush).
    - Режим безопасного неразрушающего аудита и дооснащения существующих репозиториев (Non-Destructive Update).
  - `manage-meta-project`:
    - Аудит репозитория и формирование специализированной команды агентов (`.agents/team/`).
    - Матрица детекции 13 ролей (включая дефолтного воркера `agent-general-worker`, оркестровый, продуктовый и инженерный слои).
    - Контроль неактивных ролей (Role Pruning / Garbage Collection) через `agent-meta-guardian`.
    - Регламенты взаимодействия: User-Driven Dispatch, User-Mediated Handoffs (лимит hops=2), доказательный арбитраж, монополия на приватные заметки (`notes.md`) и неприкосновенность общих пометок.
  - `record-observation`: Регламентированная запись находок в `observations.md` с контролем дубликатов и размера.
  - `sync-architecture`: Анализ манифестов и точек входа с актуализацией карты компонентов.
- **Документация и эмпирическая база (`docs/`)**:
  - `decisions_and_roadmap.md`: Архитектурные решения ADR #1–#6 и перспективный роадмап.
  - `test_report_alpha_skill.md`: Полный отчет по эмпирическим тестам 1–6 на реальном проекте Telegram-бота.
  - `temporary_overrides.md`: Журнал временных калибровок правил агента.
- **Инфраструктура репозитория**:
  - Автоматические тесты целостности метаданных и навыков (`tests/test_integrity.py`).
  - CI-пайплайн GitHub Actions (`.github/workflows/ci.yml`).
  - Шаблоны сообщений об ошибках, запросах функций и Pull Request.
  - Файлы стандартов открытого исходного кода (`LICENSE`, `CONTRIBUTING.md`, `.gitignore`).
