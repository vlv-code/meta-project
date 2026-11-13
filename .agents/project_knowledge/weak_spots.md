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

## 4. Resolved Vulnerabilities & Closed Risks
- `[RESOLVED 2026-11-12] compact_memory.py`: Row filtering previously dropped observation records containing substring 'Date' or '---' when appending to an existing monthly archive. Resolved by switching to deterministic header slice `chunk_lines[2:]` and verified via unit tests.
- `[RESOLVED 2026-11-12] sync_templates.py`: Regex-based template replacement exhibited false-green behavior on missing template blocks and failed on nested triple-backtick fenced blocks. Resolved by explicit HTML sentinel comments (`<!-- TEMPLATE:BEGIN/END -->`) and strict drift error detection.
- `[RESOLVED 2026-11-13] check_boundaries.py`: Pre-commit hook installation (`--install-hook`) previously completely overwrote existing `.git/hooks/pre-commit` scripts. Resolved via non-destructive safe chaining (append with `|| exit 1`) and idempotency guard.
