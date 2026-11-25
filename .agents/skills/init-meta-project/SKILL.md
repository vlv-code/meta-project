---
name: init-meta-project
license: MIT
compatibility: "Requires Python 3.10+ and Git"
description: >-
  Scaffold and initialize the meta-project agent environment in any repository:
  checks for existing setup to safely upgrade without data loss, or runs a 2-pass
  scan to create AGENTS.md, .agents/project_knowledge/, and install skills.
---

# Agent Environment Initialization and Upgrade (Meta-Project Init & Audit)

Autonomous skill for preparing any repository for agent workflows: checks for an existing `meta-project` structure, prevents overwriting accumulated data, and performs a safe upgrade to the latest standard or bootstraps the structure from scratch.

Relies on continuous/opportunistic refresh: when accessing meta-knowledge slices, close gaps and maintain a cohesive project vision.

---

## When to invoke skill

* The user requests: "prepare repo for agents", "initialize meta-project", "check agents.md", "update agent structure", "refresh meta-knowledge".

---

## Resource Loading Contract

This skill ships with its resources in `resources/` (sibling directory of this file). Resources are sync-managed copies of the canonical templates (`templates/project_knowledge/*.md`, `templates/AGENTS.md`, `skills/*/SKILL.md`) — read them from the skill's own installed directory; NEVER from a framework clone, and never re-create their content from memory.

| Invocation | Resource reads |
|---|---|
| Repeat-run / healthy-repo re-check (Scenario 3) | **reads NO resources** — zero-diff verification and capability reporting only. |
| Clean init (Scenario 1) | Each resource is read exactly when its step needs it — every step below names its file. |
| New-harness adoption (Scenario 4) | reads only its procedure in this file; no resources. |
| Repair scenarios (2, 5-7) | Read only the resource(s) the repaired step names. |

**Missing mandatory resource:** the dependent step is BLOCKED. Emit the envelope and stop the step:

```text
[MISSING_RESOURCE] resources/<name>: missing mandatory resource | expected: resource shipped with the skill | actual: file absent | next: restore the file from the pinned source, then re-run the blocked step
```

Guidance (verbatim contract): missing mandatory resource 'resources/<name>' — reinstall the skill from the pinned source (update-meta-project) or restore the file; do not improvise the template from memory.

---

## Execution steps

### Phase 1: Survey and Deterministic Inspection (Zero-Write Phase)

**Survey-First Zero-Write Invariant:** Phase 1 performs only discovery and diagnosis — no file creation, telemetry, `.lock` files, or execution of untrusted repository scripts.

0. **Step 0: Host Runtime Self-Identification & SCRIPT_ROOT Resolution:**
   - **Host Runtime Self-Identification (Anti-Anchoring Invariant):**
     The agent MUST identify its current harness_id strictly from its own host execution environment (e.g. environment variables `ANTIGRAVITY_AGENT` -> `'antigravity'`, `ZCODE_AGENT` -> `'zcode'`, system prompt, or AppData path), NEVER by reading existing active entries in `.agents/meta-project.json` or `AGENTS.md`.
     - **Strict Prohibition:** Do NOT copy `--harness` from the registry to force a green `HEALTHY_REGISTERED` status.
     - **Key Semantics:** If the current harness is not registered or is planned, state `HEALTHY_NEW_HARNESS` (Scenario 4) is the expected, correct state triggering multi-harness adaptation. It is NOT an error to be bypassed.
   - **Canonical SCRIPT_ROOT Resolution Order:**
     When resolving and executing framework runtime scripts (`scripts/<script>.py`), locate `SCRIPT_ROOT` in the following canonical precedence order:
     1. `./scripts/<script>.py` in the target repository (if already deployed);
     2. `${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py` (if set by environment);
     3. `<dir_of_SKILL.md>/../../scripts/<script>.py` (sibling / plugin root of the installed skill).

1. **Execute deterministic inspection** with EXPLICIT runtime context via resolved `<SCRIPT_ROOT>/inspect_meta_project.py` (registration states are undetermined without it — the survey reports `CONTEXT_UNRESOLVED` instead of silently adopting any active installation):
   ```bash
   python <SCRIPT_ROOT>/inspect_meta_project.py --repo-root . --json --harness <MY_ACTUAL_HARNESS> (or --harness auto) --installation <installation_id>
   ```
   *(If the script is not yet present in SCRIPT_ROOT, perform equivalent read-only inspection with pure Python stdlib, zero writes.)*
2. **Classify into one of 8 canonical states:** `NONE` (no scaffolding), `FOREIGN_RULES` (foreign instruction files: `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, foreign `AGENTS.md`), `HEALTHY_REGISTERED`, `HEALTHY_NEW_HARNESS` (target harness/installation unregistered or `planned`), `CONTEXT_UNRESOLVED` (no `--harness`/`--installation` — re-run with explicit context before routing), `LEGACY_UNREGISTERED` (legacy structure without `.agents/meta-project.json`), `PARTIAL_CORRUPTED` (missing/corrupted critical slices), `INCOMPATIBLE_SCHEMA` (registry schema incompatible with current tooling).
3. **Evaluate capability matrix:** readiness per `read_instructions`, `local_checks`, `skills`, `roles`, `hooks` (`available` / `unavailable` / `untested`).
4. **Select execution strategy:** route to Phase 2 (Scenario Agreement) and the Phase 3 scenario matching the state.

---

### Phase 2: Scenario Agreement and Decision Capture (Alignment Phase)

Agree the scenario across 4 dimensions (present options, capture decisions):
1. **profile:** `active_development` | `maintenance` | `research` | `audit` | `documentation`.
2. **deployment_mode:** `shared_repo` (committed to Git for team sync and CI gates) | `local_overlay` (`.git/info/exclude`, experimental — NOT yet test-verified; present as such) | `hybrid` (passport committed, agent notes/reports local).
3. **collaboration_model:** `solo` | `duo` (Tier 0 Micro-Mini Duo) | `triad` (Canonical Compact Trio) | `specialized_swarm` (declared but NOT implemented in `resolve_team_topology` — offer triad-now-or-defer explicitly). Multi-harness: identify primary and planned harnesses by identifiers agreed with the user for THIS project (configuration, not fixed constants).
4. **execution rules:** `verification_policy`: `strict_independent` | `duo_peer_review` | `self_check`; `delegation_level`: `strictly_manual` | `controlled` | `autonomous`; constraints: zero-dependency core, platform limits, sensitive paths.

#### Core Invariants of Scenario Agreement:
- **Repeat Run Invariant:** `HEALTHY_REGISTERED` with a scenario already recorded in `.agents/meta-project.json` → do NOT re-interview the user; reuse the existing scenario.
- **Strict Separation of Truth:** outputs strictly separate User Decisions, Established Facts, Agent Recommendations; proposals are never recorded as approved user decisions without confirmation.
- **Capability-Desire Conflict Resolution:** desires conflicting with environment capabilities (e.g. independent verification requested, solo-only harness) → present a concrete binary choice.
- **Persistence:** save the agreed scenario into `.agents/meta-project.json` under the `"scenario"` block with `schema_version: "1.1.0"`.

---

### Phase 3: Execution and Scaffolding by Canonical State

Detailed execution steps and deep-dive checklists for all 7 scenarios are maintained in `references/scenarios.md`.
If `references/scenarios.md` is absent (`[MISSING_RESOURCE] references/scenarios.md`), execute using the compact scenario routing below:

#### Scenario Outline & Resource Loading Matrix:
- **Scenario 1: State `NONE` (Clean Scaffold Mode):**
  - **Pass 1 (Express Scan):** Manifests, core directories, North Stars; deploy bundled skills (`resources/record-observation-SKILL.md`, `resources/sync-architecture-SKILL.md`, `resources/ground-meta-project-SKILL.md`);
  5. **Create initial knowledge slice drafts and registry:** (READ: `resources/observations.md`, `resources/boundaries.md`, `resources/weak_spots.md`) — materialize the three slice drafts from these resources into `.agents/project_knowledge/` byte-canonically. Write `.agents/meta-project.json` registering the CURRENT installation as `<installation_id>`/`<harness_id>` with status `active`.
  Scaffold baseline `.gitignore` hygiene block (append-if-absent, never overwrite): generated bytecode and lock artifacts are hygiene paths mapped Green: ignored by VCS (`__pycache__/`, `*.pyc`, `*.lock`, `.agents/update-engine.lock`, `.agents/update-plan.json`, `.agents/update-journal.json`).
  ##### Pass 2: Repository Deep-Dive, Principles & Shell Skills
  - Mandatory Core Inspection Checklist: database/storage, external APIs, runtime containerization, UI/inputs.
  - **Interactive Calibration Interview (Codified Two-Question Protocol):**
    - Question 1 (North Stars & Core Invariants): project invariants and production constraints.
    - Question 2 (Red Zone & Sensitive Paths): directories and credentials placed in Red Zone.
  - Boundary calibration: Default Deny / 100% path coverage with Black Zone rule. Never drop mandatory security defaults: `src/auth/**`, `src/billing/**`, `src/payments/**`, `src/crypto/**`, `*.pem`, `*.key`, `config/secrets/**`, `.github/workflows/**`, `scripts/check_boundaries.py`.
  - Populate architecture card, tasks checklist, and root passport (READ: `resources/architecture.md`, `resources/tasks.md`, `resources/AGENTS.md`) via in-memory synthesis flush protocol.
  - Full 2-pass deep-dive instructions: `references/scenarios.md`.
- **Scenario 2: State `FOREIGN_RULES` (Preserve & Merge Mode):**
  Preserve foreign rules (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`), map to Yellow/Green in boundaries, scaffold non-destructively. Detailed rules in `references/scenarios.md`.
- **Scenario 3: State `HEALTHY_REGISTERED` (Pass-Through / No-Op Mode):**
  Zero-diff verification (0 modified files). Issue adoption report if needed. Detailed rules in `references/scenarios.md`.
- **Scenario 4: State `HEALTHY_NEW_HARNESS` (Multi-Harness Adaptation Mode):**
  Preserve existing installations in registry, register new harness as active, scaffold role bindings in `.agents/team/`. Detailed rules in `references/scenarios.md`.
- **Scenario 5: State `LEGACY_UNREGISTERED` (Legacy Adoption Mode):**
  Preserve historical `observations.md` and `tasks.md`, upgrade passport and boundaries to Default Deny / 100% coverage, deploy runtime utilities. Detailed rules in `references/scenarios.md`.
- **Scenario 6: State `PARTIAL_CORRUPTED` (Diagnose & Repair Mode):**
  Surgically recreate only missing/corrupted files (READ matching resource from `resources/`) without touching intact knowledge bases. Detailed rules in `references/scenarios.md`.
- **Scenario 7: State `INCOMPATIBLE_SCHEMA` (Read-Only Fallback Mode):**
  Fail-closed protection: report schema mismatch, enter read-only inspection, provide manual migration instructions. Detailed rules in `references/scenarios.md`.

**Reference Loading Contract (`MISSING_RESOURCE`):**
If `references/scenarios.md` is absent or unreadable, emit `[MISSING_RESOURCE] references/scenarios.md: reference file absent` and fall back to the scenario outline above and basic discovery. Do not block execution if core steps can proceed.

---

### Phase 4: Formal Initialization Report Generation and Manage Handoff

1. **Generate report file via stdlib engine:**
   ```bash
   python scripts/manage_reports.py init --action create \
     --installation <installation_id> \
     --harness <harness_id> \
     --actor <actor_id> \
     --status <completed|awaiting_decision|blocked> \
     --scenario-file <path_or_inline>
   ```
   Written atomically to `.agents/reports/<installation_id>/init/<init_run_id>.json` and safely updates `latest.json`.
2. **Status semantics:** `completed` (slices initialized, scenario agreed, baseline checks passed) | `awaiting_decision` (critical choices unresolved; a decision ledger, NOT deployment authorization) | `blocked` (environment incompatibility or broken invariants).
3. **Machine-Enforced Manage Admission:** manage-side intake runs through the same engine — `python scripts/manage_reports.py manage --action create ...` fails closed (`evaluate_manage_intake`: local-registry project/installation/harness match, admitted actor, existing init run, completed + ready status, fresh input fingerprints). NEVER assemble manage reports by hand; a refused intake must be resolved, not bypassed.
4. **No Automatic Team Deployment Invariant:** `init-meta-project` NEVER deploys agent roles or teams — deploying or adapting roles is the exclusive responsibility of `manage-meta-project`. End initialization with a concise human-readable summary:
   ```text
   Initialization complete. Report saved to .agents/reports/<installation_id>/init/<init_run_id>.json.
   Recommended next step: Invoke 'manage-meta-project' to configure team roles according to the agreed scenario.
   ```

---

### Finalization and Verification

1. Verify created/updated files (`ls -R .agents`).
2. **Local Invisible Overlay Option:** in an external/client project or personal no-commit mode, add `AGENTS.md` and `.agents/` to `.git/info/exclude`; verify they do not appear in `git status` untracked files.
3. Output a concise summary: execution mode (initial setup vs audit upgrade; shared vs invisible overlay), created/updated file tree, captured North Stars, linked stack skills.
