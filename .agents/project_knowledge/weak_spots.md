# Weak Spots, Risks, and Technical Debt

Registry of fragile areas, known bugs, and constraints of the repository. Agents MUST consult this registry before modifying listed modules.

---

## 1. Fragile Modules and High Coupling
- `tests/test_integrity.py` validates structural integrity: requires procedural sections (`## When to invoke skill` and `## Execution steps`), YAML frontmatter (`name`, `description`), and exact template file names in `templates/project_knowledge/` (`architecture.md`, `boundaries.md`, `observations.md`, `weak_spots.md`, `tasks.md`) and `templates/team/` (`profile.md`, `notes.md`, `system_prompt.md`). Any structural modifications without updating tests will cause CI failure.
- `[RESOLVED 2026-11-15]` `check_boundaries.py` hook chaining (append + `|| exit 1`, marked resolved 2026-11-13) was proven insufficient by the external audit: a prior hook finishing with `exit 0` terminated the dispatcher before the boundary check ran; worktrees/`core.hooksPath`/external hook managers were unsupported. Superseded by the dispatcher hook (`pre-commit.legacy-meta` companion executed as a separate process) in audit Stage S8; locked by `tests/test_audit_regressions.py` hook tests.

## 2. Environment and Test Constraints
- Running checks requires Python 3.10+ standard library (`unittest`, `pathlib`, `re`).
- Zero-dependency principle: no third-party test runners or linters are used; test execution is performed via `python -m unittest discover -s tests -p "test_*.py" -v`.
- 2 behavioral hook tests in `tests/test_audit_regressions.py` (§8: prior-hook `exit 0` chaining, failure propagation) require a POSIX shell (`bash`/`sh`); on hosts without one they are skipped, silently reducing Stage S8 RED coverage (Windows hosts usually resolve Git Bash; CI ubuntu-latest always has bash).
- GitHub required status checks match check-run names exactly, and the `ci.yml` matrix expands the gate into `Validate Skills & Templates Integrity (3.10)`…`(3.13)`: requiring the plain job name alone gates nothing. Branch protection must require all four expanded names, or `ci.yml` must gain a stable aggregate job (roadmap §8.4, owner action; observed via `gh api .../commits/main/check-runs` 2026-11-15).

## 3. Deferred Technical Debt
- Historical research documents in `docs/` (`decisions_and_roadmap.md`, `test_report_alpha_skill.md`, `temporary_overrides.md`) remain in Russian for historical provenance, whereas all active agent specifications, templates, and skills are 100% English canonical.
- `[OPEN 2026-11-15, audit §10 live acceptance]` `scripts/manage_reports.py`: the Stage S5 intake engine `evaluate_manage_intake` is library-only — the CLI path `manage --action create` never calls it, so a manage report can be created for an unregistered installation referencing a foreign `init_run_id` (reproduced live: `ag-ghost` create returned rc=0/success and wrote `.agents/reports/ag-ghost/`). Unit tests stay green because they invoke the engine directly. Fix: wire `evaluate_manage_intake` (fail-closed rc!=0 on intake errors) plus registry actor/installation validation into the create subcommand; cover via CLI-level adversarial test.

## 4. Resolved Vulnerabilities & Closed Risks
- `[RESOLVED 2026-11-12] compact_memory.py`: Row filtering previously dropped observation records containing substring 'Date' or '---' when appending to an existing monthly archive. Resolved by switching to deterministic header slice `chunk_lines[2:]` and verified via unit tests.
- `[RESOLVED 2026-11-12] sync_templates.py`: Regex-based template replacement exhibited false-green behavior on missing template blocks and failed on nested triple-backtick fenced blocks. Resolved by explicit HTML sentinel comments (`<!-- TEMPLATE:BEGIN/END -->`) and strict drift error detection.
- `[RESOLVED 2026-11-13] check_boundaries.py`: Pre-commit hook installation (`--install-hook`) previously completely overwrote existing `.git/hooks/pre-commit` scripts. Resolved via non-destructive safe chaining (append with `|| exit 1`) and idempotency guard.
- `[RESOLVED 2026-11-14] check_boundaries.py`: Russian zone regex character class defect fixed with non-capturing groups.
- `[RESOLVED 2026-11-14] sync_templates.py`: Silent continue on missing templates/skills replaced with fail-closed drift reporting.
- `[RESOLVED 2026-11-14] compact_memory.py`: Concurrency race condition with record_obs.py resolved via cross-platform file locking; id(r) anti-pattern replaced with enumeration index retention.
