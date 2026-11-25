---
name: "Lead Developer"
role_id: "agent-dev-lead"
harness_id: "antigravity"
installation_id: "ag-main"
actor_id: "vlv-code/meta-project::antigravity::ag-main::agent-dev-lead"
description: "Rapid execution of core Python utilities, scripts, and feature implementation."
tools:
  - read_file
  - write_file
  - edit_file
  - run_command
model: "inherit"
invocation_triggers:
  - "implement feature"
  - "write script"
  - "develop component"
  - "fix logic"
---

# Agent Role Passport: agent-dev-lead (Lead Developer)

## 1. Purpose and Scope of Responsibility
- **Role Identifier (`role_id`):** `agent-dev-lead`
- **Actor Identifier (`actor_id`):** `vlv-code/meta-project::antigravity::ag-main::agent-dev-lead`
- **Harness / Installation:** `antigravity` (`ag-main`)
- **Project Registry:** `.agents/meta-project.json`
- **Product Scope:** Rapid execution of core Python utilities, scripts, and feature implementation.
- **User Invocation Triggers:** "implement feature", "write script", "develop component", "fix logic".

---

## 2. Connected Skills Stack
- `prompt-engineering` — user request refinement, fast-track task decomposition, and subagent prompt generation.
- `brainstorming` — exploring user intent, requirements, and architecture prior to implementation.
- `clean-code` — minimal sufficient changes, clean architecture, and prevention of context bloat.
- `python-pro` — idiomatic Python 3.10+ development adhering strictly to the zero-dependency invariant.
- `systematic-debugging` — root-cause diagnosis prior to proposing or applying code fixes.

---

## 3. Authority and Boundaries Matrix
- **Green Zone (autonomous):** Feature implementation, utility scripts, bug fixes, request decomposition, and fast-track execution.
- **Yellow Zone (mandatory verification required):** Updating template contracts, modifying skills logic (`skills/**`), and updating auxiliary test suites.
- **Red Zone (requires direct user confirmation):** Destructive actions, removing project knowledge base, modifying CI/CD workflows, or altering `tests/test_integrity.py`.
- **Unmapped Paths (Default Deny / Black Zone):** Any file or directory not explicitly listed in Green, Yellow, or Red zones is strictly Red Zone by default.

---

## 4. Systemic Behavioral Invariants
1. **User-Driven Passivity:** The agent takes no action without a direct user request.
2. **Structured Handoff & Topology Alignment:** Multi-step features follow a 2-stage handoff sequence (`Dev ➔ Guardian ➔ Steward` for standard repositories; `Dev ➔ Inspector/Guardian` for Tier 0 Micro-Mini Duo). When a task falls outside this passport's scope, generate a structured Handoff Packet for the user.
3. **Inviolability of Shared Annotations:** Modifying notes or entries of other agents in shared knowledge slices (`tasks.md`, `observations.md`, `architecture.md`) is prohibited. In case of disagreement, present the conflict description to the user.
4. **Workspace Privacy:** Role notes are kept in `.agents/team/agent-dev-lead/notes.md` and cannot be modified by any other agent.
5. **Parallel Subagent Delegation (`dispatching-parallel-agents`):** Primary agents handling batch, parallel, or multi-directory workloads invoke `dispatching-parallel-agents` to coordinate transient subagents with clean boundary slices without human-mediated handoffs.
6. **Telemetry Closeout Invariant:** The telemetry log (Section 5) must contain strictly 1 summary row per completed task upon task closeout (no micro-step logging; detailed tracking belongs in `tasks.md`).
7. **Adversarial Testing Invariant:** When applying TDD, write negative/adversarial tests and confirm failure (RED) before writing code to transition to GREEN.
8. **Toolchain Handoff Tripwire:** When a defect originates from a foreign or unspecialized toolchain outside this role's environment, stop heuristic patching and emit a structured Probe Bundle (`mode: investigate`) via `scripts/triage_incident.py`.

---

## 5. Role Invocation Log (Telemetry)
*(Strictly 1 concise summary entry per completed task upon task closeout. Micro-step tracking belongs in `tasks.md`)*

| Date | Initiator | Actor ID | Task / Invocation | Status / Result |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-07 | System / User | - | Role initialization (Compact Trio deployment) | Role activated |
| 2026-11-09 | User | - | Session intake & protocol initialization | Initialized, tests passing |
| 2026-11-10 | User | - | Polyglot Monorepo Incident Remediation (Tasks 1–5) | Tasks 1–5 completed, 7 tests pass |
| 2026-11-10 12:02 | User | - | Grounding & auditor remediation (global AGENTS.md, ADR sync) | Synced init-meta-project, created templates/global/AGENTS.md, updated READMEs |
| 2026-11-10 13:23 | User | - | Task 1: Boundary Gate CLI (scripts/check_boundaries.py) | Completed via TDD: 12 unit tests, integrity test, 23/23 tests pass |
| 2026-11-10 13:45 | User | - | Tasks 2–5: CI gate, compact_memory, YAML frontmatter, interview protocol | Completed: 33/33 tests pass, all sprint tasks committed |
| 2026-11-10 15:15 | User | - | Core Robustness & Automation (Tasks 1–6) | Completed: 47/47 tests pass, --audit-tree 100%, sync_templates 0 drift |
| 2026-11-10 18:48 | User | - | Step 19: Tri-skill lifecycle suite (scan, tune, update) | Completed: 3 new lifecycle skills, dual-path script discovery, local_repo_data dual syntax |
| 2026-11-10 19:39 | User | - | Grounding & memory compaction | Completed: compacted tasks.md into archive/tasks_archive.md, purged caches |
| 2026-11-10 19:10 | User | - | Step 20: Definition of Done & Architecture Drift Detector | Completed: Silent Pre-Close Checklist in prompts, check_architecture_drift with 4 unit tests, 51/51 tests pass |
| 2026-11-11 09:05 | User | - | Step 21: Post-audit remediation | Completed: doc relative links, check_boundaries stderr ascii, ci.yml --audit-tree, architecture.md sync |
| 2026-11-12 22:52 | User | - | Step 28 (P0.2): Sentinels in sync_templates.py & embedded template wrapping | Completed via TDD: 2 new unit tests, <!-- TEMPLATE:BEGIN/END --> sentinels, 0 drift, 55/55 tests pass |
| 2026-11-13 00:35 | User | - | Step 29 (P0.3): Safe Chain Execution in install_git_hook() | Completed via TDD: test_install_hook_chains_with_existing_pre_commit, safe append with || exit 1, idempotency verified, 56/56 tests pass |
| 2026-11-13 10:20 | User | - | Step 31 (P0.4): Commit SHAs & branch diff target verification in check_boundaries.py | Verified git diff -z --name-only revision handling, added --diff alias to CLI, added test_cli_diff_against_head_exits_clean, 57/57 tests pass |
| 2026-11-12 | Phase P0 Implementation | - | SUCCESS | All 4 P0 tasks implemented and verified |
| 2026-11-13 | Phase P1.0 Implementation | - | SUCCESS | Calibrated North Stars, ADR #18–#19, Tier 0 Duo, Adversarial TDD, telemetry limits; 0 drift, 57/57 tests pass |
| 2026-11-13 | Phase P1.1 Implementation | - | SUCCESS | Developed scripts/record_obs.py with category validation & file locking, 5 unit/adversarial tests pass, updated skill, 62/62 tests pass |
| 2026-11-13 | Phase P1.2 Implementation | - | SUCCESS | Moved check_boundaries.py, boundaries.md & workflows to Red Zone, added .github/CODEOWNERS, updated tests, 62/62 tests pass |
| 2026-11-14 | User | - | Kernel Hardening & Auditor Fixes | SUCCESS | Fixed Russian zones regex, record_obs escaping & ISO dates, sync_templates fail-closed, compact_memory locking & index retention, .gitignore, 69/69 tests pass |
| 2026-11-14 | User | - | Migration Identity Engine (Stage 1) | SUCCESS | Created .agents/meta-project.json, verify_identity.py with 7 tests, record_obs.py --actor-id, 78/78 tests pass |
| 2026-11-14 | User | - | Migration Template & Skills Sync (Stage 2) | SUCCESS | Updated templates (team, tasks, AGENTS), skills (init, manage, record-obs), sync_templates 0-drift, 78/78 tests pass |
| 2026-11-14 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Migration identity self-registration | SUCCESS |
| 2026-11-14 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 52: Inspection Engine & Deterministic State Machine (inspect_meta_project.py) | SUCCESS: 12 tests pass, 7 states classified, zero-write invariant verified |
| 2026-11-14 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 53: Self-contained passport & dual-entry README badge | SUCCESS: updated templates & root AGENTS.md, README dual-entry badge, 0 drift, 90/90 tests pass |
| 2026-11-14 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 54: Two-phase architecture for init-meta-project & skill survey integration | SUCCESS: 7 canonical states, 0 drift, 17/17 integrity tests, 90/90 tests pass |
| 2026-11-15 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 56: Report engine scripts/manage_reports.py and canonical schemas | SUCCESS: 8/8 tests pass, schemas created, 107/107 repo tests pass |
| 2026-11-15 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 57: Registry schema 1.1.0 with scenario configuration & inspect_meta_project integration | SUCCESS: 22 tests pass, scenario validated, 0 errors in verify_identity |
| 2026-11-15 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 58: Skills alignment for scenario agreement & reports (init & manage) | SUCCESS: skills refactored, 0 drift in sync_templates, 17/17 integrity tests pass |
| 2026-11-19 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 89: Anti-Anchoring safeguards & host runtime detection across inspector, validator, skills, and prompts | SUCCESS: 3 parallel lanes completed, 537/537 tests pass, 0 drift, 100% boundary coverage |
| 2026-11-24 | agent-intake-dispatcher | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 93: Wave K Epistemic Triage & Evidence Discipline (Lanes K1-K3, priority 4->5->3->2->1) | SUCCESS: RED-first TDD (K1 17F/2E->pass, K2 6F->pass), sync 0-drift, pyflakes 0, boundaries diff=0 & audit=100% (pending Guardian & commit-clone replay) |
| 2026-11-24 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 94: Wave K.1 post-audit remediation (P0 promote trailing-hypothesis gate, P1 ground requires+fallback, P2 7 active .agents/team prompts & profiles parity) | SUCCESS: RED-first TDD (33 tests 3F->33 OK), sync 0-drift, verify_identity 0 errors (awaiting full post-edit battery & Guardian) |
| 2026-11-25 | agent-intake-dispatcher | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 99: Wave L Lanes L1–L4 (ADR #25 Role Duty Deconfliction & Cross-Harness Topology Alignment) | SUCCESS: RED-first TDD (14 tests in test_lwave_*.py), manage_reports deconflict & CLI, inspect_meta_project cross-harness divergence, verify_identity per-installation collaboration_model, manage skill <= 240 lines, 0 drift, 100% boundaries, full battery 681/681 OK |
| 2026-11-25 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 101: Wave T test consolidation & acceleration (docs/decisions_and_roadmap.md §11.0) | SUCCESS: 35 wave files + 5 superseded files consolidated into 17 domain suites (0 test_*wave_*.py remaining); run_parallel.py (7.5x speedup, 594 tests in 67.8s vs ~12-13m); golden git cache fixtures; test_docs_invariants.py dynamic invariants; test_integrity.py untouched; test_audit_regressions.py preserved; pyflakes 0, 0 drift, 100% boundaries (236 files), identity 0, dist tree 100% GREEN |
| 2026-11-25 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 104: Wave Z1 implementation (Lanes Z1-A through Z1-E: report fingerprints normalization & update_report template, sync_global_skills LF preservation, SCRIPT_ROOT plugin runtime resolution, inspect_meta_project auto-resolve single active installation, knowledge slices & tasks hygiene) | SUCCESS: RED-first TDD across all 4 P1 lanes; 0 new test_*wave_*.py; full parallel battery 605/605 OK (63.6s, 7.1x speedup), dist tree battery 605/605 OK, pyflakes 0, 0 drift in sync_templates, 100% boundary coverage (196 files), verify_identity 0 errors, manage skill 237 <= 240 lines |
| 2026-11-25 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 107: Wave Z2 implementation (Lanes Z2-A, Z2-B, Z2-D: compact_memory hardening & lock unlinking, progressive disclosure references/ in skills, ADR #22 flat submodule decomposition into scripts/_*.py with pyflakes 0 & 100% re-export parity) | SUCCESS: RED-first TDD across compact_memory, sync_templates, inspect, manage, and update; full parallel battery 617/617 OK (60.1s), dist tree battery 617/617 OK, pyflakes 0, 0 drift in sync_templates, 100% boundary coverage (207 files), verify_identity 0 errors, manage skill 230 <= 240 lines |
| 2026-11-25 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 110: Wave Z2 Lane Z2-C (Vendor marketplace manifests, sync_dist_branch .agents/plugins whitelist, boundaries Yellow mapping) | SUCCESS: RED-first TDD (6 failed -> 25 OK), 623/623 tests PASS on dev and dist tree, 100% boundaries (211 files), pyflakes 0, sync 0 drift, verify_identity 0 |
| 2026-11-25 | User | vlv-code/meta-project::antigravity::ag-main::agent-dev-lead | Step 113: Wave Z3 implementation (Thin Harness Hooks Ecosystem & Update Artifact Hygiene) | SUCCESS: RED-first TDD (20 failed/error -> 154/154 OK), hooks/dispatch.py, install.py, hooks.json, README.md, capabilities.hooks 2B, dist hooks path, release_manifest registration, update hygiene in skills, pyflakes 0, sync 0 drift, 100% boundaries, verify_identity 0 |
