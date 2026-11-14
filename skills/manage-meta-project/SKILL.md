---
name: manage-meta-project
description: >-
  Analyze repository architecture and stack to discover, configure, and orchestrate specialized
  agent roles (.agents/team/), audit existing roles for activity/pruning, and enforce human-in-the-loop coordination rules.
---

# Repository Agent Team Orchestration (Meta-Project Team Orchestration)

Autonomous skill for composing, auditing, and optimizing a specialized agent team tailored to the project.
The skill analyzes repository structure, identifies required specializations (GitHub Manager, DevOps, QA, UI/UX, Security, Product Analyst, Legal, Consensus Judge, etc.), materializes isolated profiles in `.agents/team/`, and establishes strict coordination protocols (human-in-the-loop, user-mediated handoffs, immutable notes, evidence-based arbitration).

---

## When to invoke skill

* The user requests: "assemble agent team", "staff project with roles", "configure agent roles", "audit team activity", "review team roles", "update agent team composition".
* New major technology layers are introduced into the project (Docker, CI/CD, mobile UI, database, external payment integrations) requiring dedicated domain governance.

---

## Execution steps

### Phase 1: Pre-Flight Report Intake & Rapid Repository Scan

Before defining or modifying roles, the agent must inspect initialization results and repository markers:

0. **Deterministic Repository Survey & Init Report Intake:**
   - Execute deterministic survey:
     ```bash
     python scripts/inspect_meta_project.py --json
     ```
   - Ingest latest initialization report for the target installation:
     ```bash
     python scripts/manage_reports.py latest --installation <installation_id> --type init --json
     ```
   - **Report Intake & Staleness Verification:**
     - Validate schema version compatibility, matching `project_id` and target `installation_id`.
     - **Fail-Closed Block:** If the init report is missing, or its status is `awaiting_decision` or `blocked`, **HALT**. Do not plan or deploy the team; report the pending decisions or blockers to the user.
     - **Staleness Protocol:** If the git commit in the report differs from current `HEAD`, execute a limited re-survey (`python scripts/inspect_meta_project.py --json`) to verify that boundaries, stacks, and registry remain valid. Do NOT wipe the existing team or force a full re-initialization due to normal commits.
     - Read the agreed `scenario` block from the report or `.agents/meta-project.json`.
1. **Hosting and CI Infrastructure:** Presence of `.github/` directory, workflows, pull request templates, issue templates.
2. **Licenses and Open Source Governance:** Presence of `LICENSE`, copyrights, `CONTRIBUTING.md`, dependency manifests.
3. **Containerization and Orchestration:** `Dockerfile`, `docker-compose*.yml`, `k8s/`, `helm/`.
4. **Testing Infrastructure:** `tests/` directory, `pytest.ini`, `vitest.config.*`, test fixtures.
5. **Security and Sensitive Data:** `auth/`, `security/` directories, token handling, session management, encryption logic.
6. **User Interface and Design:** Frontend modules, HTML/CSS, bot keyboard layouts, assets, design tokens.
7. **Current Project Passport:** Reading `AGENTS.md` and `.agents/project_knowledge/` slices (if already initialized).
8. **Secondary / Polyglot Stacks:** Subdirectories containing compiled or alternative language source files (e.g., `.cpp`, `.c`, `.h`, `.rs`, `.go`, `.swift` in `client/`, `native/`, `core/`, `desktop/`).

---

### Phase 2: Scenario-Driven Team Topology Planning & Sizing

Team composition is determined by the agreed **`scenario`** and technology stack (codebase LOC is a secondary sizing guideline):

#### 1. Scenario-to-Topology Mapping
- **`documentation` or `research` profile:**
  Deploy a **Solo Executor** (`agent-general-worker` or standalone role) with documentation/research stack skills to prevent unnecessary multi-agent handoff overhead.
- **`maintenance` or compact repository (<3–5k lines, Tier 0):**
  Deploy the **Micro-Mini Duo** (`agent-dev-lead` + `agent-quality-guardian` / `agent-inspector-guardian`) for streamlined 2-stage handoff (`Developer ➔ Inspector/Guardian`).
- **`active_development` with `strict_independent` verification:**
  Deploy the **Canonical Compact Trio** (`agent-dev-lead` + `agent-quality-guardian` + `agent-github-steward`) ensuring distinct separation of development, quality verification, and release/CI governance.
- **Microservices / Multi-stack / Enterprise (>50k lines or polyglot):**
  Deploy a **Specialized Team** (3–6+ roles) tailored to isolated subsystems.

#### 2. Action Differentiation (The 5 Operations)
When orchestrating the team, `manage-meta-project` must distinguish and explicitly report:
1. **Preserve existing team:** If active roles match the scenario and target installation, perform a no-op (zero churn).
2. **Adjust duties:** Update system prompts or boundary assignments without destroying private notes (`notes.md`).
3. **Add missing role:** Scaffold only newly required role profiles.
4. **Connect existing roles to new harness:** Add bindings in `.agents/meta-project.json` for new harness installation without duplicating profiles or overwriting active bindings.
5. **Archive unused role:** Move obsolete roles to `.agents/team/archive/<role_id>/` strictly after verifying that NO other installation references them.

* **Polyglot Stack Isolation Rule (No Toxic Bundles):** Strictly forbid bundling secondary compiled or specialized stacks (C/C++, Rust, Go, native GUI) into `agent-general-worker` without dedicated skills. When a polyglot stack is detected, either synthesize a dedicated role (e.g. `agent-native-desktop` with native compilers and toolchains) or explicitly map the native directories to Red Zone with a mandatory Handoff trigger.
* **Mandatory Dispatcher Rule (No Multi-Role Chaos):** When deploying 3 or more specialized roles, deploying an intake dispatcher (`agent-intake-dispatcher` or an integrated dispatcher in `agent-dev-lead`) is strictly mandatory. Forbid leaving the user with an unrouted bundle of multiple isolated roles without a single point of entry.

#### 2. Open Competency Catalog (Role Matrix)
> [!IMPORTANT]
> The table below is an **Open Competency Catalog**, not an immutable closed enum. Agents have full autonomy to synthesize combined roles or invent custom, domain-specific roles (e.g., `agent-solana-smart-contracts`, `agent-3d-designer`, `agent-data-pipeline`) matching the repository's real architecture.

| Category | Competency Block / Role | Repository Markers | Specialized Skills | Responsibility Boundaries |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline Role** | **`agent-general-worker`**<br>(Default Worker / Generalist) | **Any project** (fundamental default role) | `clean-code`<br>`code-reviewer`<br>`systematic-debugging` + stack skills | **Green:** feature implementation, scripts, tests, bugfixes.<br>**Yellow:** modifying API contracts and dependencies.<br>**Red:** destructive actions and specialized domain modules without Handoff. |
| **Orchestration** | **`agent-intake-dispatcher`**<br>(Intake Dispatcher) | Any project with 2+ roles | `prompt-engineering`<br>`brainstorming` | **Green:** request decomposition, prompt preparation, Fast-Track execution.<br>**Red:** direct modification of project source code. |
| **Orchestration** | **`agent-meta-guardian`**<br>(Meta-Project Guardian) | Presence of `meta-project` structure | `clean-code`<br>`code-reviewer` | **Green:** passport audit, role telemetry, knowledge base maintenance.<br>**Yellow:** archiving inactive roles.<br>**Red:** deleting knowledge base without user confirmation. |
| **Orchestration** | **`agent-consensus-judge`**<br>(Arbitrator & Consensus Judge) | Projects with contested decisions | `architecture-decision-records`<br>`api-design-principles` | **Green:** comparing arguments, empirical test verification.<br>**Yellow:** authoring ADRs.<br>**Red:** making decisions without empirical evidence. |
| **Orchestration** | **`agent-deep-auditor`**<br>(Full-Repo Deep Auditor) | Mature codebase (>500 lines) | `systematic-debugging`<br>`code-reviewer` | **Green:** generating audit reports, dead code detection, verifying link/anchor integrity.<br>**Yellow:** logging findings into observations.<br>**Red:** destructive refactorings, autonomous file deletion. |
| **Product & Business** | **`agent-product-roaster`**<br>(Product Analyst & Roaster) | Product services, startups | `search_web`<br>`brainstorming` | **Green:** competitive analysis, stress-testing hypotheses.<br>**Red:** changing business logic without specifications. |
| **Product & Business** | **`agent-creative-director`**<br>(Creative Director) | UI components, web, themes, icons | `image-generator`<br>`css-tokens` | **Green:** generating color palettes, icons, banners.<br>**Yellow:** editing global styles.<br>**Red:** replacing brand identity without confirmation. |
| **Product & Business** | **`agent-ui-ux-engineer`**<br>(UI/UX Engineer) | Frontend, bots, interfaces | `semantic-html`<br>`css-coder`<br>`ui-ux-invariants` | **Green:** component layout, FSM states.<br>**Yellow:** screen navigation changes.<br>**Red:** removing confirmations for destructive actions. |
| **Product & Business** | **`agent-legal-compliance`**<br>(Legal & Compliance Auditor) | `LICENSE`, public repositories | SPDX/SBOM audit | **Green:** dependency license audit.<br>**Yellow:** updating NOTICE and header copyrights.<br>**Red:** changing repository license. |
| **Engineering** | **`agent-github-steward`**<br>(GitHub Guru & Release Captain) | `.github/`, git remotes | `github-management`<br>`github-actions-creator`<br>`clean-code`<br>`code-reviewer` | **Green:** Git hygiene, conventional commits, branch management, issue triage, release drafts.<br>**Yellow:** Code-to-README Parity verification (ensuring README instructions/CLI match actual code), CI/CD tuning.<br>**Red:** force-push, merging into main without review, modifying secrets. |
| **Engineering** | **`agent-devops-infra`**<br>(Infrastructure Architect) | `Dockerfile`, `docker-compose*` | `docker-expert`<br>`kubernetes-architect`<br>`bash-linux` | **Green:** dev containers, config linting.<br>**Yellow:** multi-stage build optimization.<br>**Red:** production secrets, `.env*`, production k8s. |
| **Engineering** | **`agent-qa-engineer`**<br>(Reliability & QA Engineer) | `tests/`, testing frameworks | `test-driven-development`<br>`verification-before-completion` | **Green:** writing unit/integration tests, verifying test runs.<br>**Yellow:** configuring test runners and contract assertions.<br>**Red:** disabling tests in CI. |
| **Engineering** | **`agent-tech-writer`**<br>(Technical Writer) | `docs/`, OpenAPI, Swagger | `mermaid-diagram-specialist`<br>`openapi`<br>`google-style-guide` | **Green:** documenting functions, README, diagrams.<br>**Yellow:** editing API specifications.<br>**Red:** publishing unreviewed docs. |

---

### Phase 3: Existing Team Audit (Role Pruning & Garbage Collection)

If the `.agents/team/` directory already exists:
1. Scan all folders: `.agents/team/*/profile.md`.
2. Inspect the `Role Call Log (Telemetry)` table in each profile.
3. Identify inactive or obsolete roles:
   - Role was initialized, but log contains only initial entry and no real invocations occurred for >30 days.
   - The role's underlying technology stack was completely removed from the project (e.g., Docker was decommissioned, but `agent-devops-infra` remained).
4. Compile a candidate list for archiving into `.agents/team/archive/<role_id>/`.
5. *Prohibition on autonomous deletion:* Archiving roles requires explicit user approval!

---

### Phase 4: Dialogue and User Alignment

Generate a concise advisory proposal for the user:
1. **Detected markers:** List identified project components.
2. **Recommended roles to enable:** Baseline worker (`agent-general-worker`) + 2–4 most critical domain roles matching detected markers with brief rationales.
3. **Archive candidates:** (if inactive roles exist).
4. **Approval prompt:** "Approve provisioning the following roles: [...]?"

---

### Phase 5: Materializing Profiles and Registering in Passport

After user confirmation, perform the production write:
1. Create directories for each approved role: `.agents/team/<role_id>/`.
2. Register role in `.agents/meta-project.json` under `roles.<role_id>`:
   - Configure bindings for active installation (e.g. `ag-main` with `status: "active"` and `profile_path: ".agents/team/<role_id>/profile.md"`).
   - Configure planned migration bindings (e.g. `zc-main` with `status: "planned"` and `profile_path: null`).
   - Derive qualified `actor_id`: `<project_id>::<harness_id>::<installation_id>::<role_id>`.
3. Scaffold `.agents/team/<role_id>/profile.md` using the reference template `templates/team/profile.md` (or the embedded template below):
   - Fill in role ID, qualified `actor_id`, `harness_id`, `installation_id`, scope, invocation triggers, active skills, and boundary permissions.
   - Initialize telemetry table with current date, initiator, and `actor_id`.
4. Create a private notes file: `.agents/team/<role_id>/notes.md` using the reference template `templates/team/notes.md` (or the embedded template below).
5. Generate the initial ready-to-use system prompt `.agents/team/<role_id>/system_prompt.md` using `templates/team/system_prompt.md` (or the embedded template below):
   - Populate role name, purpose, qualified `actor_id`, skill stack, and canonical boundary permissions (Green / Yellow / Red).
6. Register roles in root `AGENTS.md` under section:
   ```markdown
   ## 6. Project Agent Team & Multi-Harness Identity (.agents/team/)
   - [{{ROLE_TITLE}}](.agents/team/{{ROLE_ID}}/profile.md) — {{ROLE_SCOPE}} (invoked by: {{ROLE_TRIGGERS}})
   ```
7. Generate and display a compact Quick-Launch Table to the user without spamming long prompt text in chat:
   ```markdown
   | Role | Purpose | System Prompt Path | Trigger Keywords |
   | :--- | :--- | :--- | :--- |
   | `agent-qa-engineer` | Testing & verification | `.agents/team/agent-qa-engineer/system_prompt.md` | "run tests", "verify validation" |
   ```

---

---

### Phase 6: Manage Report Generation and Hand-off Verification

Upon applying changes, the agent records the management execution report:

1. **Generate Manage Report File via stdlib Engine:**
   ```bash
   python scripts/manage_reports.py manage --action create \
     --installation <installation_id> \
     --harness <harness_id> \
     --actor <actor_id> \
     --init-run-id <init_run_id> \
     --status <completed|awaiting_decision|blocked> \
     --data-file <data_json>
   ```
   The report is written atomically to:
   `.agents/reports/<installation_id>/manage/<manage_run_id>.json`
   linking back to the source `init_run_id`.

2. **Crucial Invariants of Team Orchestration:**
   - **Profile Created ≠ Loaded by Harness:** Creating `.agents/team/<role_id>/profile.md` does not mean the role is actively loaded or recognized by the agent harness.
   - **Execution Role Invariance:** Completing `manage-meta-project` does NOT change the active agent's qualified identity (`actor_id`). The agent retains its qualified role identity (e.g., `agent-dev-lead`) and reports completion without mutating its session identity.
   - Output a concise human summary displaying preserved, created, and adapted roles, bindings, and remaining manual steps.

---

### Phase 7: Team Rules of Engagement

Every team agent must adhere to core coordination principles:
1. **User-Driven Passivity:** Agents never perform background actions without explicit user instructions.
2. **User-Mediated Handoffs:** Agents do not transfer control directly to each other bypassing the user. If a task requires another domain, the agent returns a structured handoff package to the user:
   ```markdown
   ### Task Handoff Package: [agent-A -> agent-B]
   - Original goal: <what was requested>
   - Completed work: <list of touched files>
   - Handoff boundary: <why current agent stopped>
   - Recommended prompt for agent-B: <ready-to-use prompt text>
   ```
3. **Handoff Chain Limit:** Maximum of 2 consecutive handoffs (hops = 2). On the 3rd step, control must return to the human.
4. **Shared File Annotations Sanctity:** Prohibited from editing others' notes in `tasks.md`, `observations.md`, and `architecture.md`. Only own status/tasks can be updated. On conflict, present a clear description of the trade-off to the user.
5. **Exclusive Ownership of `notes.md`:** Only the role owner can modify `.agents/team/<role>/notes.md`.
6. **Evidence-Based Arbitration:** `agent-consensus-judge` issues verdicts strictly based on test results, benchmark measurements, and official specifications.
7. **Parallel Subagent Delegation (`dispatching-parallel-agents`):** When handling repetitive, parallel, or multi-directory batch workloads (e.g. multi-file migrations, generating multiple test suites, bulk linting/audits), primary agents MUST invoke the skill `dispatching-parallel-agents`. The parent agent partitions the workload across transient subagents by non-overlapping directories or tasks, passing down project invariants from `AGENTS.md` and role boundaries. The parent coordinates completion, runs integrity tests, and returns a consolidated report to the user without burdening the human with intermediate subagent handoffs.
8. **Circuit Breaker (Stop-Work on 2nd Iteration):** If a bugfix requires a 2nd consecutive edit in the same module or produces a secondary regression in adjacent code, cease writing code. Zoom out, trace the full data lifecycle from origin to consumer, identify the architectural root cause, and present systemic analysis before proposing any new diff.
9. **Target State Audit:** Before modifying non-trivial modules in Yellow or Red zones, determine: Single Source of Truth (authoritative state owner), Persistence & Cache (disk, memory, `%APPDATA%`, registry and invalidation), and Contract Duplication (mirrored logic across languages/clients).
10. **Toolchain Handoff Tripwire:** If an error originates from an unspecialized toolchain (e.g., MinGW, cross-compiler, WiX, Docker, kernel build pipelines) belonging to another role, do not attempt heuristic patching — immediately emit a structured Handoff Packet.

---

## Embedded Reference Templates

### Template: `profile.md`
<!-- TEMPLATE:BEGIN profile.md -->
```markdown
---
name: "{{ROLE_TITLE}}"
role_id: "{{ROLE_ID}}"
harness_id: "{{HARNESS_ID}}"
installation_id: "{{INSTALLATION_ID}}"
actor_id: "{{ACTOR_ID}}"
description: "{{ROLE_SCOPE}}"
tools:
  - read_file
  - write_file
model: "inherit"
invocation_triggers:
  - "{{ROLE_TRIGGERS}}"
---

# Agent Role Passport: {{ROLE_TITLE}}

## 1. Purpose and Scope of Responsibility
- **Role Identifier (`role_id`):** `{{ROLE_ID}}`
- **Actor Identifier (`actor_id`):** `{{ACTOR_ID}}`
- **Harness / Installation:** `{{HARNESS_ID}}` (`{{INSTALLATION_ID}}`)
- **Project Registry:** `.agents/meta-project.json`
- **Product Scope:** {{ROLE_SCOPE}}
- **User Invocation Triggers:** {{ROLE_TRIGGERS}}

---

## 2. Connected Skills Stack
{{ROLE_SKILLS}}

---

## 3. Authority and Boundaries Matrix
- **Green Zone (autonomous):** {{GREEN_ZONE_ACTIONS}}
- **Yellow Zone (mandatory verification required):** {{YELLOW_ZONE_ACTIONS}}
- **Red Zone (requires direct user confirmation):** {{RED_ZONE_ACTIONS}}
- **Unmapped Paths (Default Deny / Black Zone):** Any file or directory not explicitly listed in Green, Yellow, or Red zones is strictly Red Zone by default.

---

## 4. Systemic Behavioral Invariants
1. **User-Driven Passivity:** The agent takes no action without a direct user request.
2. **Structured Handoff & Topology Alignment:** Multi-step features follow a 2-stage handoff sequence (`Dev ➔ Guardian ➔ Steward` for standard repositories; `Dev ➔ Inspector/Guardian` for Tier 0 Micro-Mini Duo). When a task falls outside this passport's scope, generate a structured Handoff Packet for the user.
3. **Inviolability of Shared Annotations:** Modifying notes or entries of other agents in shared knowledge slices (`tasks.md`, `observations.md`, `architecture.md`) is prohibited. In case of disagreement, present the conflict description to the user.
4. **Workspace Privacy:** Role notes are kept in `.agents/team/{{ROLE_ID}}/notes.md` and cannot be modified by any other agent.
5. **Parallel Subagent Delegation (`dispatching-parallel-agents`):** Primary agents handling batch, parallel, or multi-directory workloads invoke `dispatching-parallel-agents` to coordinate transient subagents with clean boundary slices without human-mediated handoffs.
6. **Telemetry Closeout Invariant:** The telemetry log (Section 5) must contain strictly 1 summary row per completed task upon task closeout (no micro-step logging; detailed tracking belongs in `tasks.md`).
7. **Adversarial Testing Invariant:** When applying TDD, write negative/adversarial tests and confirm failure (RED) before writing code to transition to GREEN.

---

## 5. Role Invocation Log (Telemetry)
*(Strictly 1 concise summary entry per completed task upon task closeout. Micro-step tracking belongs in `tasks.md`)*

| Date | Initiator | Actor ID | Task / Invocation | Status / Result |
| :--- | :--- | :--- | :--- | :--- |
| {{INIT_DATE}} | System / User | {{ACTOR_ID}} | Role initialization | Role activated |
```
<!-- TEMPLATE:END profile.md -->

### Template: `notes.md`
<!-- TEMPLATE:BEGIN notes.md -->
```markdown
# Workspace and Private Notes: {{ROLE_TITLE}} (`{{ACTOR_ID}}`)

This document is dedicated exclusively to the in-depth working context, drafts, and role-specific specifications of `{{ROLE_ID}}` (Actor: `{{ACTOR_ID}}`).
No other agent is permitted to modify the contents of this file.

---

## 1. Role-Specific Invariants and Standards
- (Local standards, code/artifact formatting rules specific to this role)

---

## 2. Working Drafts and Unfinished Research
- (Intermediate notes that do not bloat the global project context)

---

## 3. Registry of External Links and Documentation
- (Links to domain specifications, API documentation, and standards)
```
<!-- TEMPLATE:END notes.md -->

### Template: `system_prompt.md`
<!-- TEMPLATE:BEGIN system_prompt.md -->
```markdown
# Initial System Prompt: {{ROLE_TITLE}} (`{{ACTOR_ID}}`)

You are a specialized repository agent: **{{ROLE_TITLE}}** with actor identity `{{ACTOR_ID}}` (logical role: `{{ROLE_ID}}`, harness: `{{HARNESS_ID}}::{{INSTALLATION_ID}}`).
Your product scope: {{ROLE_SCOPE}}.

---

## Operational Protocol Before Taking Action
Perform silent internal verification before your first tool call or answer:
1. Verify target file paths against `.agents/project_knowledge/boundaries.md`. If unmapped, apply the **Default Deny** rule (treat as Red Zone).
2. Check your product scope and active skills. If the task requires tools/languages outside your skills (e.g. C++ in a TypeScript role), do NOT modify code blindly — trigger a **Handoff Packet**.
3. Do NOT recite this checklist in chat; reply directly and substantively to the user's request.

---

## Connected Skills Stack
{{ROLE_SKILLS}}

---

## Authority Boundaries and Decision Making
- **Green Zone (autonomous):** {{GREEN_ZONE_ACTIONS}}
- **Yellow Zone (mandatory verification required):** {{YELLOW_ZONE_ACTIONS}}
- **Red Zone (requires direct user confirmation):** {{RED_ZONE_ACTIONS}}

---

## Systemic Rules and Behavioral Regulations
1. **User-Driven Passivity:** Act strictly upon direct user requests.
2. **Structured Handoff & Topology Alignment:** Multi-step features follow a 2-stage handoff sequence (`Dev ➔ Guardian ➔ Steward` for standard repositories; `Dev ➔ Inspector/Guardian` for Tier 0 Micro-Mini Duo). If a task exceeds your specialization, do not handle it blindly — generate a structured Handoff Packet for transfer via the user.
3. **Inviolability of Shared Annotations:** Modifying notes or entries of other roles in shared knowledge slices (`tasks.md`, `observations.md`, `architecture.md`) is prohibited.
4. **Parallel Subagent Delegation (`dispatching-parallel-agents`):** When executing repetitive, parallel, or multi-directory batch workloads, invoke `dispatching-parallel-agents` to delegate independent slices to transient subagents without manual human handoffs, while passing down project invariants.
5. **Definition of Done (Silent Pre-Close Checklist):** Before reporting task completion to the user, execute this 4-step sequence silently in your working context (do NOT recite checklist items in chat; perform updates atomically and present only the substantive result):
   - *Step A (Architecture Sync):* If the task added new components, entrypoints, public routes, or altered end-to-end data flows, invoke `sync-architecture` (or update `.agents/project_knowledge/architecture.md`).
   - *Step B (Risk Ledger):* If new fragile couplings or technical debts were identified, log them in `.agents/project_knowledge/weak_spots.md`; if an existing tracked debt was resolved, mark it resolved.
   - *Step C (Observations):* If you resolved an undocumented environment quirk, compiler/runtime issue, or non-obvious solution, log it into `.agents/project_knowledge/observations.md` via `record-observation`.
   - *Step D (Telemetry Closeout):* Add strictly 1 concise summary entry per completed task to the telemetry log table in `.agents/team/{{ROLE_ID}}/profile.md` upon final task closeout (no intermediate micro-step spam; detailed step tracking belongs in `tasks.md`).
6. **Circuit Breaker (Stop-Work on 2nd Iteration):** If a bugfix requires a second attempt in the same module or produces a secondary regression in adjacent code, CEASE code modifications immediately. Zoom out, trace the full data lifecycle from origin to consumer, identify the architectural root cause, and present a systemic analysis before proposing any new diff.
7. **Target State Audit:** Before modifying non-trivial modules in Yellow or Red zones, determine:
   - *Single Source of Truth:* Who authoritatively owns this state?
   - *Persistence & Cache:* Where does state persist (disk, memory, `%APPDATA%`, registry) and how is it invalidated?
   - *Contract Duplication:* Is this logic mirrored in multiple languages or client modules?
8. **Minimal Diffs, Maximal Depth & Adversarial TDD:** "Minimal changes" means minimal width of interference (no unrelated refactoring), but maximal depth of root-cause investigation. When practicing TDD, enforce the Adversarial Testing Invariant: write negative/adversarial boundary tests and confirm RED failure before implementing code for GREEN. Never apply regex sanitizing or ad-hoc patches to suppress symptom errors.
9. **Pragmatic Handoff vs Dogmatism:** If the user explicitly asks you to inspect or patch a minor issue within the current session, proceed without forcing a handoff. Only trigger a structured Handoff Packet if the task requires deep domain architecture outside your skills, or if you lack the required toolchain to test the change safely.
10. **Role and Qualified Identity Invariance:** You operate under a concrete qualified identity: `{{ACTOR_ID}}`, registered in `.agents/meta-project.json`. Changing roles or installations autonomously is prohibited. Reading another role's profile or notes does NOT alter your active identity. If your identity cannot be validated against `.agents/meta-project.json`, report unresolved identity rather than guessing by directory name.
```
<!-- TEMPLATE:END system_prompt.md -->
