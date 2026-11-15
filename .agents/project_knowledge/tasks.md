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

> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

- [x] [vlv-code/meta-project::antigravity::ag-main::agent-dev-lead @ 2026-11-15 01:26] Step 58: Alignment of init-meta-project & manage-meta-project procedural skills complete (embedded 4 scenario dimensions and report generation in init; added pre-flight intake, fail-closed staleness check, scenario topology planning, and manage report in manage; synchronized mirrors with 0 drift; 17/17 integrity tests pass; handoff to Stage 4: Prompt 4.1) [COMPLETED]
- [x] [vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian @ 2026-11-15 01:45] Step 59: Acceptance test suite for report & manage cycle developed in tests/test_report_and_manage_cycle.py (verified 8 scenarios: scenario agreement in registry, init report contract & references, zero-write invariant under --read-only, foreign/incompatible report rejection, awaiting_decision/blocked fail-closed halt, scenario-driven topology adaptation, multi-harness binding preservation, and staleness detection; 118/118 tests pass, 0 template drift, 100% boundary coverage across 111 files; handoff to Stage 5: agent-github-steward) [COMPLETED]
- [x] [vlv-code/meta-project::antigravity::ag-main::agent-github-steward @ 2026-11-15 01:55] Step 60: Boundaries, project passport parity, ADR #20, and release commit for reports & scenario management (mapped .agents/reports/** to Yellow zone in boundaries.md, added scripts/manage_reports.py to Section 5 in AGENTS.md, recorded ADR #20 in docs/decisions_and_roadmap.md, updated architecture.md, verified 118/118 tests, 0 drift, 100% boundary coverage across 111 files, committed feat(reports)) [COMPLETED]
- [x] [vlv-code/meta-project::antigravity::ag-main::agent-quality-guardian @ 2026-11-15 02:26] Step 61: Global harness skills synchronization via update-meta-project and sync_templates.py (implemented --global-skills in scripts/sync_templates.py, added test_sync_global_skills_option in tests/test_sync_templates.py, synchronized all 9 canonical skills to ~/.gemini/config/skills/ with 0 drift, 119/119 tests pass, 100% boundary coverage across 111 files) [COMPLETED]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-dev-lead @ 2026-11-15 03:30] Step 62: External audit remediation Stage 1 (reproduction fixation) complete — triage of auditor list agreed with corrections; created tests/test_audit_regressions.py (42 tests: 39 RED reproductions across audit §2–§9 via real working functions/CLI + 3 lock-ins); rewrote self-implemented foreign-report check in tests/test_report_and_manage_cycle.py to call the real intake engine (RED until Stage 5); baseline preserved in docs/audit_4274bbd_regressions_baseline.md; full suite 161 tests / 40 expected RED / 0 regressions among 119 pre-existing tests [COMPLETED — Stage 2 (Red Zone: check_boundaries.py, ci.yml, CODEOWNERS) awaits explicit user confirmation]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-dev-lead @ 2026-11-15 04:20] Step 63: Audit remediation code stages S2–S9 complete under user Red-Zone confirmation — S2: check_boundaries fail-closed git queries, --no-renames, --repo-root scoping, status-mode rename parsing + ci.yml trusted-base enforcement (gate & policy from pinned base SHA, zero-before explicit failure, LICENSE removed from push paths-ignore) + CODEOWNERS owner @vlv-code; S3: verify_identity schema/status enums, harness↔installation matching, structured root diagnostics, valid team-less registries, planned≠admission; S4: inspector 8th state CONTEXT_UNRESOLVED, passport+registry-validity mandatory for HEALTHY, roles capability scoped to installation, worktree toplevel/hooks fix; S5: evaluate_manage_intake admission engine, input_fingerprints staleness (uncommitted inputs), relative pointers w/ containment, run_id no-overwrite, latest-attempt surfacing, project identity from registry (default removed), completed+empty-scenario rejected; S8: dispatcher hook (legacy as separate process, worktree/core.hooksPath, external-manager conflict); S9: in-table row insertion, exact-duplicate suppression, atomic writes, lock-free --dry-run, NOTE dedup + orphan re-homing, sync --write fail-closed + re-verify; S6-docs: --component→--path; 161/161 tests, 100% boundary coverage (127 files), 0 template drift; remaining: skills §6/§7 content, §10 live acceptance (Guardian), README badge & branch-protection report (Steward) [COMPLETED — handoff to agent-quality-guardian]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-quality-guardian @ 2026-11-15 04:28] Step 64: Independent verification of audit 4274bbd remediation + live §10 acceptance (verified 161/161 tests, 0 drift, 100% boundaries/128 files; RED baseline independently re-confirmed on a pre-fix 4274bbd git-archive export with the same test bytes — 39 RED + 3 lock-in ok + rewritten cycle RED — proving GREEN was reached without assert weakening, with a disclosed import-only BoundaryGateError stub in the throwaway export; live scenarios: clean foreign project NONE→scaffold→HEALTHY_REGISTERED/CONTEXT_UNRESOLVED, init→manage with registry-resolved project_id, repeat with latest-semantics, second installation with scoped role capabilities, folder move resolving own reports, Base Fallback battery without global skills (boundaries 100%, fail-closed record_obs category, lock-free dry-run), read-only 0-write via full-tree hash, non-destructive decommission to archive, upstream update preserving local_repo_data; native ZCode acceptance: verify_identity --actor admitted active + session prompt parity with .agents/team/agent-quality-guardian-zc/system_prompt.md; 1 integration defect found and logged to weak_spots.md §3: manage --action create CLI bypasses evaluate_manage_intake) [COMPLETED]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-dev-lead @ 2026-11-15 11:21] Step 65: Post-acceptance tail complete — (1) fixed Guardian Step 64 finding: manage --action create now fail-closed via evaluate_manage_intake + init-run existence check, CLI adversarial test added (missing/blocked/admitted runs); (2) resolve_team_topology redesigned per audit §5/§6 precedence: explicit collaboration_model never downgraded by LOC (RED-first: 3 new tests failed on old code), specialized_swarm → supported:false, contradictory wishes → conflicts list; (3) skills §6/§7 content aligned: init (explicit runtime context + CONTEXT_UNRESOLVED, manage_reports.py in mandatory deployment, Canonical Script Source Invariant, registry scaffold de-hardcoded, repeat-run semantics, local_overlay marked NOT YET VERIFIED), manage (machine-enforced intake, topology precedence, de-hardcoded examples, roster section 6→7), update (single canonical scripts/ with all 7 utilities + explicit legacy .agents/scripts/ migration), decommission (registry-aware Phase 0: binding-disable vs shared-role-archive, refusal while referenced by other installations, verify_identity post-check); mirrors synced 0 drift; 165/165 tests, 100% boundaries (127 files) [COMPLETED — remaining: Steward track (commits, branch-protection, README badge); decommission mechanical check functions deferred unless requested]


---

## Delegated Subtasks and Blockers
- `[agent-intake-dispatcher -> agent-qa-engineer @ 2026-11-06 22:15]`: Update integrity tests test_integrity.py (English section & zone contracts) [COMPLETED].
- `[agent-intake-dispatcher -> agent-meta-guardian @ 2026-11-06 22:15]`: Translate skills/, templates/, .agents/ specifications to English [COMPLETED].
- `[agent-intake-dispatcher -> agent-general-worker @ 2026-11-06 22:15]`: Create README.ru.md, translate README.md and .github templates [COMPLETED].
- `[agent-intake-dispatcher -> agent-github-steward @ 2026-11-07 01:00]`: Audit GitHub templates (.github/), CI/CD workflow, and git hygiene [COMPLETED].
- `[agent-intake-dispatcher -> agent-deep-auditor @ 2026-11-07 01:00]`: Audit translated markdown anchor links, residual test files, and terminology consistency [COMPLETED].
- `[agent-intake-dispatcher -> agent-qa-engineer @ 2026-11-07 01:00]`: Final verification pass.
