# Meta-Project v1.0.0-alpha.8 — Wave I: Audit Response III (draft notes, публикация при нарезке релиза)

> [!WARNING]
> **Pre-release (канал `preview`)**. Notes подготовлены стюардом заранее (Wave I, Step 88); публикуются при тегировании `v1.0.0-alpha.8` после Guardian приёмки.

## Контекст

Волна I закрывает находки внешнего аудита #3 (8.0/10, dev@7850151): P0-находки §6.2/§6.3 были закрыты волной P (PD mapping, D7) — эта волна покрывает новые: парсер гейта лгал молча, `--read-only` не был проверяемым утверждением, собственный репозиторий не имел лок-теста 100% покрытия границ, документация ссылалась на несуществующие ADR.

## Главные изменения

### Честность парсера границ (Lane IG, §6.4)
- Bullets трактуются как командные строки только при явном CLI-глаголе в начале (`python/pytest/git/pip` + пробел) — пути вида `docs/expected_behavior.md` больше не выпадают молча по подстроке «expect».
- Backtick-паттерны с запятыми (`docs/**, *.md`) разбираются на отдельные паттерны.
- Регрессионный барьер: зона-карта живого `boundaries.md` доказана идентичной до/после (audit-tree 100%, счётчики зон неизменны).

### `--read-only` — проверяемое утверждение (Lane IG, §6.1)
- На время инспекции ставится `sys.addaudithook`: записи внутри аудируемого репо (open w/a/+, replace/rename/remove) → конверт `READ_ONLY_VIOLATION`, rc≠0. Обычные прогоны байт-идентичны.

### Самопроверки и гигиена (Lane IT)
- Инвариант собственного репо: `--audit-tree` обязан быть 100% (лок-тест двери, через которую прошёл sanction-mapping баг; dogfood-gвард для dist-веток).
- CODEOWNERS ⊆ `SANCTION_AUTHORIZED_ACTORS` — список владельцев не может разойтись с санкционной властью.
- pyflakes по `scripts/ tests/` в CI (pinned, opt-in), тестовый декли: unused imports вычищены (29 строк), ассерты не тронуты.

### Doc sweep (Lane ID)
- Шаблон `boundaries.md` получил generic root-паттерны (`.gitattributes`, `.gitignore`, `LICENSE` → Green) — свежие установки перестают спотыкаться о Default Deny на стандартных файлах.
- README EN/RU: честный канонический диапазон ADR (#14–#22) вместо несуществующего «#1–#8»; однострочная пометка «защита в CI, локальный hook — convenience, `META_PROJECT_ALLOW_RED_ZONE=1` — операторский оверрайд».
- CONTRIBUTING EN/RU: пометка для контрибьюторов — `.agents/team/*/notes.md` и `observations.md` несут внутреннюю агентную историю мейнтейнеров (видна на форке намеренно — dogfooding).

### Branch-sync автоматизация (Steward, процессный пункт триажа)
- `scripts/sync_dist_branch.py` + `.github/workflows/sync-dist.yml`: зеркалирование дистрибутивного контента dev → main по фиксированному набору путей (исключая `.agents/**`, `docs/superpowers/**`, `docs/archive/**`), батарея на результате до пуша, no-op при синхроне.

### Открытые пункты
- CRLF-writer глобальных кешей (`--global-skills --write` на Windows) — вне волн.
- Branch Protection: single required check **`All Checks Green`** — действие владельца.

Полный список изменений: [`CHANGELOG.md`](CHANGELOG.md)
