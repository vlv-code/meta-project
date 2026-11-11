# Current and Active Project Tasks

Coordination registry for tasks and progress between agents and the user.
Before starting work, every agent MUST review the active task list and, if necessary, log subtasks with their authorship.

---

## Team Task Management Rules
1. **Authorship and Timestamp Logging:** Every task and subtask is logged in the format:
   `- [ ] [agent-id @ YYYY-MM-DD HH:MM] Task description`
2. **Delegation (Out-of-Scope Handoff):** If a subtask exceeds the current agent's boundaries, it is logged in "Delegated Subtasks" with the target role (`agent-<role>`).
3. **Step Completion:** Upon completing a task, change the status to `- [x]` and optionally append a 1-line summary result.
4. **Sanctity of Other Agents' Notes:** Agents are prohibited from deleting or modifying entries written by others. Editing is restricted to own entries (status, details).

---

## Active Objective
- **Task:** Full transition of agentic ecosystem to English (English canonical) and establishing bilingual public interface (EN/RU)
- **Initiator:** User
- **Start Date:** 2026-11-06

---

## Execution Plan and Checklist
> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

- [x] [agent-quality-guardian @ 2026-11-10 01:22] Step 16: Synchronized .agents/skills/init-meta-project with canonical skills/, added ground-meta-project to architecture.md, and mapped .agents/team/** in boundaries.md [COMPLETED]
- [x] [agent-dev-lead @ 2026-11-10 13:45] Step 17: Next sprint core features implementation (Boundary Gate CLI & CI check, Memory Compactor, YAML Frontmatter for team profiles, Codified Interactive Interview in init-meta-project) [COMPLETED]
- [x] [agent-dev-lead @ 2026-11-10 15:15] Step 18: Core robustness and automation sprint (zero-depth glob fix, AGENTS.md boundary protection, tree-wide audit mode --audit-tree, intelligent compaction with [pin] protection, automated template synchronizer scripts/sync_templates.py, init-meta-project scripts scaffolding, --install-hook pre-commit installer; 47/47 tests pass) [COMPLETED]
- [x] [agent-dev-lead @ 2026-11-10 18:48] Step 19: Tri-skill lifecycle sprint (scan-meta-project with --shallow/--deep, tune-meta-project with friction tracing & <=3 North Stars limit, update-meta-project with dual-tier source & local_repo_data preservation; dual-path check_boundaries hook fix, sync-architecture pre-flight preservation; 47/47 tests pass, 100% boundary coverage) [COMPLETED]
- [x] [agent-dev-lead @ 2026-11-10 19:10] Step 20: Definition of Done & Architecture Drift Detector sprint (Silent Pre-Close Checklist codified in system prompts, check_architecture_drift non-blocking warning in scripts/check_boundaries.py with 4 unit tests, templates synchronized, 51/51 unit tests pass) [COMPLETED]
- [x] [agent-dev-lead @ 2026-11-11 09:05] Step 21: Post-audit remediation (fixed relative doc links in docs/, purged Unicode emojis in check_boundaries.py stderr for Windows cp1251 safety, added --audit-tree to CI workflow, added templates/global/AGENTS.md to architecture.md; 51/51 tests pass, 100% boundary coverage) [COMPLETED]


---

## Delegated Subtasks and Blockers
- `[agent-intake-dispatcher -> agent-qa-engineer @ 2026-11-06 22:15]`: Update integrity tests test_integrity.py (English section & zone contracts) [COMPLETED].
- `[agent-intake-dispatcher -> agent-meta-guardian @ 2026-11-06 22:15]`: Translate skills/, templates/, .agents/ specifications to English [COMPLETED].
- `[agent-intake-dispatcher -> agent-general-worker @ 2026-11-06 22:15]`: Create README.ru.md, translate README.md and .github templates [COMPLETED].
- `[agent-intake-dispatcher -> agent-github-steward @ 2026-11-07 01:00]`: Audit GitHub templates (.github/), CI/CD workflow, and git hygiene [COMPLETED].
- `[agent-intake-dispatcher -> agent-deep-auditor @ 2026-11-07 01:00]`: Audit translated markdown anchor links, residual test files, and terminology consistency [COMPLETED].
- `[agent-intake-dispatcher -> agent-qa-engineer @ 2026-11-07 01:00]`: Final verification pass.
