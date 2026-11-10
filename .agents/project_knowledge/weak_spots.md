# Weak Spots, Risks, and Technical Debt

Registry of fragile areas, known bugs, and constraints of the repository. Agents MUST consult this registry before modifying listed modules.

---

## 1. Fragile Modules and High Coupling
- `tests/test_integrity.py` validates structural integrity: requires procedural sections (`## When to invoke skill` and `## Execution steps`), YAML frontmatter (`name`, `description`), and exact template file names in `templates/project_knowledge/` (`architecture.md`, `boundaries.md`, `observations.md`, `weak_spots.md`, `tasks.md`) and `templates/team/` (`profile.md`, `notes.md`, `system_prompt.md`). Any structural modifications without updating tests will cause CI failure.

## 2. Environment and Test Constraints
- Running checks requires Python 3.10+ standard library (`unittest`, `pathlib`, `re`).
- Zero-dependency principle: no third-party test runners or linters are used; test execution is performed via `python -m unittest discover -s tests -p "test_*.py" -v`.

## 3. Deferred Technical Debt
- Historical research documents in `docs/` (`decisions_and_roadmap.md`, `test_report_alpha_skill.md`, `temporary_overrides.md`) remain in Russian for historical provenance, whereas all active agent specifications, templates, and skills are 100% English canonical.
