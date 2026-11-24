---
name: "Lead Developer & Dispatcher"
role_id: "agent-dev-lead"
harness_id: "zcode"
installation_id: "zc-main"
actor_id: "vlv-code/meta-project::zcode::zc-main::agent-dev-lead"
description: "Task decomposition, user request intake analysis, rapid execution of core Python utilities, scripts, and feature implementation."
tools:
  - read_file
  - write_file
  - edit_file
  - run_command
model: "inherit"
invocation_triggers:
  - "plan task"
  - "decompose request"
  - "implement feature"
  - "write script"
  - "develop component"
  - "fix logic"
---

# Agent Role Passport: agent-dev-lead (Lead Developer & Dispatcher) — ZCode Installation

## 1. Purpose and Scope of Responsibility
- **Role Identifier (`role_id`):** `agent-dev-lead`
- **Actor Identifier (`actor_id`):** `vlv-code/meta-project::zcode::zc-main::agent-dev-lead`
- **Harness / Installation:** `zcode` (`zc-main`)
- **Project Registry:** `.agents/meta-project.json`
- **Product Scope:** Task decomposition, user request intake analysis, rapid execution of core Python utilities, scripts, and feature implementation (`agent-intake-dispatcher` + `agent-general-worker`).
- **User Invocation Triggers:** "plan task", "decompose request", "implement feature", "write script", "develop component", "fix logic".
- **Parallel Deployment Note:** This is the ZCode-owned parallel copy of the canonical `agent-dev-lead` role; the Antigravity instance (`ag-main`) operates independently from `.agents/team/agent-dev-lead/` and is never modified by this installation.

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
4. **Workspace Privacy:** Role notes are kept in `.agents/team/agent-dev-lead-zc/notes.md` and cannot be modified by any other agent.
5. **Parallel Subagent Delegation (`dispatching-parallel-agents`):** Primary agents handling batch, parallel, or multi-directory workloads invoke `dispatching-parallel-agents` to coordinate transient subagents with clean boundary slices without human-mediated handoffs.
6. **Telemetry Closeout Invariant:** The telemetry log (Section 5) must contain strictly 1 summary row per completed task upon task closeout (no micro-step logging; detailed tracking belongs in `tasks.md`).
7. **Adversarial Testing Invariant:** When applying TDD, write negative/adversarial tests and confirm failure (RED) before writing code to transition to GREEN.
8. **Toolchain Handoff Tripwire:** When a defect originates from a foreign or unspecialized toolchain outside this role's environment, stop heuristic patching and emit a structured Probe Bundle (`mode: investigate`) via `scripts/triage_incident.py`.

---

## 5. Role Invocation Log (Telemetry)
*(Strictly 1 concise summary entry per completed task upon task closeout. Micro-step tracking belongs in `tasks.md`)*

| Date | Initiator | Actor ID | Task / Invocation | Status / Result |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-15 | System / User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Role initialization (ZCode parallel trio deployment) | Role activated |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | External audit remediation Stage 1: corrected triage + RED reproduction baseline (tests/test_audit_regressions.py: 42 tests, 39 RED + 3 lock-ins; baseline in docs/audit_38deed9_regressions_baseline.md; self-implemented cycle test rewritten to real intake call) | Complete — full suite 161 tests, 40 expected RED, 0 regressions among 119 pre-existing tests |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Audit remediation code stages S2–S9 under Red-Zone confirmation: gate/CI trusted-base, identity enums+admission, inspector CONTEXT_UNRESOLVED, report intake engine + fingerprints, hook dispatcher, memory in-table/atomic/dedup, sync fail-closed, --path docs fix | Complete — 161/161 tests GREEN, 100% boundary coverage, 0 drift; handoff packet issued to agent-quality-guardian |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Post-acceptance tail (Step 65): CLI intake gate for manage create (Guardian finding resolved), topology precedence redesign (RED-first, 3 tests), skills §6/§7 alignment across init/manage/update/decommission | Complete — 165/165 tests, 0 drift, 100% boundaries; audit scope on Dev side closed |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave 0.9.0 planning (Step 66): roadmap re-triaged on full skill evidence + 6 reviewer corrections integrated; Part 1 formal plan authored (update engine & contracts, Phases A/B/C/F) | Complete — plan saved to docs/superpowers/plans/2026-11-15-wave-0.9.0-update-engine-and-contracts.md; execution mode pending user choice |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave 0.9.0 Part 1 dispatch (Step 67): 3 parallel subagents (A/B/C1) + dispatcher integration (global-template fix, canon hardening, plan amendments from C1 findings) | Complete — 183 tests (166 GREEN + 17 engine RED by design), 0 drift, 100% boundaries/131 files, identity clean |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave 0.9.0 Part 1 implementation closeout (Step 68): flash-workers delivered engine (C2+C3), init manifest composition (C5), update skill on engine (C4); series plans Parts 2–3 authored | Complete — 184/184, 0 drift, 100%/134, engine CLI live; Part 2 running, Part 3 queued, F pending |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave 0.9.0 Parts 2–3 closeout (Step 69): ground dual-mode + tune evidence-based delivered by flash-workers; plan defect (T2↔T1 literals) caught by worker, resolved tests-first; dispatcher fixed stale ground descriptions | Complete — WAVE TOTAL 197/197, 0 drift, 100%/136; F acceptance packets issued to Guardian & Steward |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Consumer-side E2E on fresh subagents (Step 73): 2 throwaway repos, all 9 skills, 3 subagent trials (dev fix / guardian acceptance / grounding), full update-engine cycle with marker merge | Complete — framework verdict: core protocol works on cold-start agents; 3 new defects (D6, D7, layout) + friction cluster recorded to backlog |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Auditor report #2 triage + Wave D plan (Step 74): all 5 items code-verified (п.1 confirmed via E2E lock artifacts); 6-lane 2-flight parallel plan authored for subagent execution | Complete — plan at docs/superpowers/plans/2026-11-15-wave-d-state-integrity-and-perimeter.md; launch ON HOLD per user |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave D execution (Step 75): Flight 1 = 5 parallel flash-workers (E1/M/B/R/K, 244/244); E2 crashed on account limit mid-refactor, resumed via general-purpose from crash inventory; dispatcher tail fixed live-S1 plan gap (cross-pin origin-history base, RED-first) | Complete — 271/271, 0 drift, 100%/143, all 4 auditor scenarios live PASS, RED-replay 7/7 modules fail on pre-wave export; Guardian/Steward packets issued |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Astra backlog triage + Wave E plan (Step 76): stale doc mapped to built capabilities; new value scoped into 4-lane context-economy plan (formats/canon/envelopes/lazy-load pilot) with user-approved scope incl. Red-Zone envelope edits | Complete — plan at docs/superpowers/plans/2026-11-16-wave-e-context-economy.md; execution gated on Steward's Wave D commits |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave E execution (Steps 77-78): 4 flash lanes crashed on 5h quota -> general-purpose resume; P1 NO-GO handled honestly -> owner ADJUST decision; P2 on revived flash; dispatcher KEEP verdict with numbers | Complete — 323/323, 0 drift, 100%/166, init skill 41.6->19.4 KB with 9 resources, envelopes live, checkpoint convention in; RED-replay 4/4; Guardian/Steward packets issued |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Alpha.4 external audit triage + auditor addendum integration + Wave F plan (Step 80): 5/5 security claims code-verified personally; 4 rejections upheld by auditor after their own verification; 5 refinements folded in | Complete — plan at docs/superpowers/plans/2026-11-16-wave-f-security-perimeter.md (FX/FR/FD + FC Flight-2); awaiting launch; alpha.5 target |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave F execution (Step 81): 3+1 flash lanes, adversarial-RED-first throughout (FX's traversal reproduction actually escaped to %TEMP% pre-fix); dispatcher integrated lying-cache fixture fixes + missing engine row in architecture; live replays all green | Complete — SEC-1..4/M2/M3 + U6/U7/U8/U11 closed, 389/390 (commit-dependent 1), 0 drift, 100%/170; Guardian/Steward packets issued; alpha.5 staged |
| 2026-11-17 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Wave G execution (Step 83): 4 lanes on general-purpose workers (owner instruction), concurrency limit forced serialization with dispatcher doing lane H in-session; manage-slim 394->220, CRLF contract, facts digest, primitives vocabulary | Complete — battery 439 (1 commit-dependent), 0 drift, 100%/184, both engine-layout smokes PASS, architecture refreshed, CRLF-mirror quirk to backlog; packets issued |
| 2026-11-17 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Gap-analysis v1+v2 plugin triage + Wave P execution (Step 85): 4 parallel flash lanes (manifests w/ skip-guarded locks, frontmatter x9, README channels, CI+boundaries RED-ZONE-sanctioned); synthetic gate replication vs base policy; versions single-source locked | Complete — battery 481 OK, 0 drift, 100%/194, 3 manifests landed at alpha.6; Guardian/Steward packets + owner-verify (marketplace add) issued |
| 2026-11-18 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | External audit #3 (8.0/10) triage + Wave I execution (Step 87): 3 parallel flash lanes (gate parser honesty w/ map-identity proof, read-only sys.addaudithook assertion, self-check invariants + pyflakes blocking, docs/template sweep); its P0 pair pre-closed by wave P | Complete — battery 524/524, pyflakes 0 blocking, 0 drift, 100%/198; audit-response loop #3 closed; packets issued |
| 2026-11-23 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | External audit #4 follow-up (Step 90): 2 flash workers (README glossary; weak_spots structural-debt entry + Icebox disposition) + dispatcher lane (versioning policy, ADR #23 branch discipline, read-discipline dispositions, RU table-of-contents anchor fix) | Complete — battery 588/588, 0 drift, 100% boundaries (206 files); 3 owner decisions flagged (ADR option, CONTRIBUTING §5, beta wording); variant C clarification drafted for the auditor |
| 2026-11-23 | User | vlv-code/meta-project::zcode::zc-main::agent-dev-lead | Dispatcher-to-orchestrator binding (Step 91): 2 parallel flash workers (manage-skill binding block; registry validation, inspector reporting, intake gate `set_orchestration`, shared host detection in `_common.py`) + dispatcher lane | Complete — battery 633/633, 0 drift, 100% boundaries (210 files); a second stale host-detection copy found and consolidated; no orchestration block declared in the repo registry, per owner |
