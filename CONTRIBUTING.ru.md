# Руководство по участию в проекте (Contributing Guide)

[English](CONTRIBUTING.md) | [Русский](CONTRIBUTING.ru.md)

Мы приветствуем вклад в развитие фреймворка среды агентов для репозиториев (**Meta-Project**)!

Этот документ описывает структуру репозитория, правила добавления и модификации навыков/шаблонов, а также процесс отправки Pull Request.

---

## 1. Архитектурные принципы фреймворка

Любые изменения и новые навыки должны соответствовать базовым принципам архитектуры:
1. **Разгрузка контекста (No Context Bloat):** `AGENTS.md` содержит только ключевые инварианты, принципы-ориентиры (North Stars), декларацию стека и карту навигации. Динамические логи и детали выносятся в `.agents/project_knowledge/`.
2. **Неразрывная актуализация (Read + Opportunistic Refresh):** При обращении к срезам мета-знаний агент обязан верифицировать их и дополнять найденные пробелы.
3. **Безопасность (Non-Destructive Update):** Инициализирующие и синхронизирующие скрипты обязаны сохранять существующие данные пользователя (`observations.md`, кастомные инварианты) при повторном запуске.
4. **Машиночитаемые границы (Glob Boundaries):** Ограничения и зоны ответственности в `boundaries.md` формулируются строгими glob-паттернами.

---

## 2. Структура репозитория

```text
meta-project/
├── .github/                       # Шаблоны issues, PR и CI workflows
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/ci.yml
├── docs/                          # Архитектурные решения, отчеты тестов и роадмап
├── scripts/                       # Скрипты автоматизации и контроля границ
│   ├── check_boundaries.py
│   ├── compact_memory.py
│   └── sync_templates.py
├── skills/                        # Каталог автономных навыков
│   ├── decommission-meta-project/
│   ├── ground-meta-project/
│   ├── init-meta-project/
│   ├── manage-meta-project/
│   ├── record-observation/
│   ├── scan-meta-project/
│   ├── sync-architecture/
│   ├── tune-meta-project/
│   └── update-meta-project/
├── templates/                     # Эталонные шаблоны для развертывания
│   ├── AGENTS.md
│   ├── global/
│   │   └── AGENTS.md
│   ├── project_knowledge/
│   │   ├── architecture.md
│   │   ├── boundaries.md
│   │   ├── observations.md
│   │   ├── tasks.md
│   │   └── weak_spots.md
│   └── team/
│       ├── profile.md
│       ├── notes.md
│       └── system_prompt.md
└── tests/                         # Автоматические тесты целостности структуры и метаданных
```

---

## 3. Разработка и стандарты

### Добавление или изменение навыков (`skills/`)
- Каждый навык хранится в отдельной папке `skills/<skill-name>/SKILL.md`.
- Файл `SKILL.md` обязан содержать валидный YAML frontmatter с полями `name` и `description`:
  ```markdown
  ---
  name: <skill-name>
  description: >-
    Четкое описание того, когда и для чего вызывается навык.
  ---
  ```
- Обязательные разделы тела навыка:
  - `## Когда вызывать навык`
  - `## Порядок выполнения` (пошаговый алгоритм с контрольными точками).

### Модификация шаблонов (`templates/`)
- Шаблоны `templates/AGENTS.md` и `templates/project_knowledge/*.md` должны оставаться лаконичными и не содержать специфики одного конкретного фреймворка или языка.
- Плейсхолдеры оформляются в формате `{{VARIABLE_NAME}}`.

---

## 4. Локальная проверка (Тестирование)

Перед созданием коммита запустите локальные тесты целостности репозитория (не требуют внешних зависимостей):

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Все тесты должны завершаться со статусом `OK`.

---

## 5. Процесс внесения изменений (PR Workflow)

1. Создайте тематическую ветку от `main`:
   - `feat/<название-фичи>` для новых возможностей и навыков.
   - `fix/<описание-исправления>` для исправления багов в шаблонах/навыках.
   - `docs/<тема>` для документации и отчетов.
2. Сделайте осмысленные атомарные коммиты по конвенции Conventional Commits:
   - `feat: add in-memory synthesis flush to init-meta-project`
   - `fix: correct glob pattern in boundaries template`
   - `docs: update empirical test report`
3. Убедитесь, что локальные тесты проходят.
4. Откройте Pull Request в ветку `main`, заполнив стандартный шаблон PR.
5. Дождитесь успешного прохождения проверки в GitHub Actions.
