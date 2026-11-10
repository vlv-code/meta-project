# Responsibility Zones and Change Boundaries

This document defines the agent's level of autonomy when modifying the repository using explicit file path glob patterns.

---

## Green Zone (Autonomous Modification)
Files and directories that the agent can modify autonomously to accomplish the current task:
- Creating new tests (`tests/test_*.py`, `tests/test_unit_*.py`) for auxiliary utilities.
- `docs/**`, `*.md` (except the root `AGENTS.md`) — technical documentation and reports (`CHANGELOG.md`, `CONTRIBUTING.md`, `README.md`).
- `.agents/team/*/notes.md` — private workspace notes modified exclusively by the role owner.
- In-code documentation (docstrings, function comments).

---

## Yellow Zone (Modification with Mandatory Verification)
Areas requiring elevated caution and mandatory local test execution (`python -m unittest discover -s tests -p "test_*.py" -v`):
- `AGENTS.md` — root project passport (requires careful verification and opportunistic refresh).
- `tests/**` (auxiliary project tests). **Test emasculation protection invariant:** weakening `assert` checks or adjusting golden data to match broken code is strictly prohibited.
- `skills/**` — procedural skills (`SKILL.md`) and their logic.
- `templates/**` — meta-project templates (`AGENTS.md`, `project_knowledge/**`, `team/**`).
- `scripts/**` — automation tools and boundary enforcement scripts.
- `.agents/skills/**` — local repository agent skills.
- `.agents/project_knowledge/**` — meta-knowledge slices (updated via opportunistic refresh protocol).
- `.agents/team/**` — active role passports, system prompts, and team archive.
- `.github/*.yml`, `.github/*.yaml` — repository-level GitHub configurations (e.g., `FUNDING.yml`).

---

## Red Zone (Prohibited Without Direct User Confirmation)
Critical areas of the project. Any modification requires mandatory prior confirmation from the user:
- `tests/test_integrity.py` — specification of architectural integrity and framework contracts (modifying checks is equivalent to altering platform specs).
- `.github/workflows/**` — GitHub Actions CI/CD pipelines (`ci.yml`).
- `LICENSE` — repository legal license (MIT).
- `.gitignore` — global git ignore rules.

---

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any directory or file path not explicitly listed in Green, Yellow, or Red zones above is strictly classified as **Red Zone by Default**. Autonomous modifications to unmapped paths are prohibited. Prior to touching unmapped code, the agent MUST consult the user and perform an *Opportunistic Refresh* of `boundaries.md` to map the path to its appropriate zone.

