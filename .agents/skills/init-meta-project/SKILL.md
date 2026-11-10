---
name: init-meta-project
description: >-
  Scaffold and initialize the meta-project agent environment in any repository:
  checks for existing setup to safely upgrade without data loss, or runs a 2-pass
  scan to create AGENTS.md, .agents/project_knowledge/, and install skills.
---

# Agent Environment Initialization and Upgrade (Meta-Project Init & Audit)

Autonomous skill for preparing any repository for agent workflows. Automatically checks for an existing `meta-project` structure, prevents overwriting accumulated data, and performs a safe upgrade to the latest standard or bootstraps the structure from scratch.

Relies on the principle of continuous/opportunistic refresh: when accessing meta-knowledge slices, the agent must close gaps and maintain a cohesive vision of the project.

---

## When to invoke skill

* The user requests: "prepare repo for agents", "initialize meta-project", "check agents.md", "update agent structure", "refresh meta-knowledge".

---

## Execution steps

### Phase 0: Check Existing Meta-Project Environment

Before performing any writes, check for the presence of meta-project components:
1. Check for `AGENTS.md` at the repository root.
2. Check for `.agents/project_knowledge/` and `.agents/skills/` directories.

### Scenario A: Structure Already Exists (Audit & Safe Upgrade Mode)
If `AGENTS.md` or `.agents/` folder is already present in the repository:
1. **Prohibition on Destructive Overwrite:**
   - Strictly prohibited from deleting or overwriting `observations.md` — all accumulated observations must be preserved.
   - Prohibited from deleting custom invariants and user descriptions from the existing `AGENTS.md`.
2. **Standards Compliance Audit:**
   - Check `AGENTS.md` for the "Principles and Architectural Orientations (North Stars)" section. If missing, add it without modifying the service purpose and invariants.
   - Check `AGENTS.md` for the directive protocol with the "access + opportunistic refresh" link. If outdated, update the section.
   - Check `boundaries.md` for glob pattern usage, data directory protection (`data/**`, `*.db`), assigning formatting/rendering modules to the Yellow zone, and presence of the Default Deny (Black Zone) invariant.
   - Check the `observations.md` table for the `Category` column. If using the legacy 4-column format, update the table header without deleting data rows.
   - Verify freshness of `SKILL.md` files in `.agents/skills/` (`record-observation`, `sync-architecture`, `ground-meta-project`).
3. **Safe Enhancement:**
   - Create missing slices (for example, if `weak_spots.md` is absent).
   - Supplement the skill registry in `AGENTS.md` with new specialized stack skills for the repository.
4. **Upgrade Report:**
   - Inform the user: "Existing meta-project detected. Audited and upgraded to the latest standard without loss of accumulated data."

---

### Scenario B: Initial Setup (Clean Scaffold Mode)
If no structure exists, execute the standard two-pass algorithm:

#### Pass 1: Express Scan and Skeleton Generation (Fast & High-Level)
1. **Express inspection of repository root:**
   List the root directory and identify:
   - Manifests: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pom.xml`, `docker-compose.yml`.
   - Core directories: `src/`, `app/`, `tests/`, `migrations/`, `scripts/`, `data/`.
   - **Zero Unmapped Dirs Rule:** Enumerate all top-level source directories in repository root. Strictly filter out `.gitignore` paths, VCS metadata, and standard build/package/test caches (`.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `coverage`, `__pycache__`, `.pytest_cache`, `.idea`, `.vscode`). Every remaining top-level source directory MUST be explicitly accounted for and mapped to Green, Yellow, or Red zone in `boundaries.md` (unmapped directories fall under Default Deny / Red Zone by default).
   - Project name, purpose, and core concepts from `README.md` (if present).
   - Required keys and dependencies from `.env.example` (if present).

2. **Identify tech stack and core principles:**
   - Formulate a concise stack string (e.g., `Python 3.12, FastAPI, uv, pytest, Docker`).
   - Highlight 2–3 baseline orientations (e.g., architectural simplicity, strict typing, data immutability, offline-first).

3. **Create directory structure:**
   Create directories:
   - .agents/project_knowledge/
   - .agents/project_knowledge/archive/
   - .agents/skills/record-observation/
   - .agents/skills/sync-architecture/
   - .agents/skills/ground-meta-project/
   - scripts/

4. **Deploy bundled meta-project skills and runtime scripts:**
   Write SKILL.md files from the embedded templates below to:
   - .agents/skills/record-observation/SKILL.md
   - .agents/skills/sync-architecture/SKILL.md
   - .agents/skills/ground-meta-project/SKILL.md
   Deploy zero-dependency boundary and compaction automation scripts to repository scripts/:
   - scripts/check_boundaries.py (Boundary Gate CLI)
   - scripts/compact_memory.py (Context Rot Shield & Memory Compactor)

5. **Create initial knowledge slice drafts:**
   Write files in .agents/project_knowledge/:
   - observations.md (5-column table with the first initialization row; use cross-platform command examples, e.g.: python -m pytest).
   - oundaries.md (zones template with basic glob patterns: formatting in Yellow zone, data in Red).
   - weak_spots.md (baseline risk registry structure).
   - rchitecture.md (baseline architecture scaffold).
   - 	asks.md (active objective, team checklist, and delegation registry).
#### Pass 2: Repository Deep-Dive, Principles & Shell Skills

1. **Mandatory Core Inspection Checklist:**
   *Prohibited from populating `weak_spots.md` and `architecture.md` with boilerplate templates without reading source code of key modules!* The agent must execute `read_file` calls for the following critical areas:
   - **Storage & Database:** Read the primary data access module (`storage.py`, repositories, models). Assess monolithic size (LOC count), schema coupling, and migration setup.
   - **External API & Service Clients:** Read integration modules (AI model SDKs, external clients). Check for retries, timeouts, fallbacks, and global singletons.
   - **Containerization & Runtime:** Read `Dockerfile`, `docker-compose.yml`, and CI workflows (`.github/workflows/`). Check system binary dependencies (FFmpeg, utilities), user permissions (UID), and data volume mounts.
   - **User Interface & Input:** Read keyboard/router modules. Check platform constraints (e.g., 64-byte limit for Telegram `callback_data`, FSM states, confirmation for destructive actions).

2. **Interactive Calibration Interview (Codified Two-Question Protocol):**
   Automated scans identify what exists in code, but cannot detect unwritten historical context, business invariants, or production sensitivities. The agent conducts a brief, structured interactive interview (via `ask_question` tool or a direct interactive prompt) asking exactly 2 focused questions:
   - **Question 1 (North Stars & Core Invariants):** *"Какие ключевые архитектурные инварианты, бизнес-правила и ограничения продакшена (North Stars) нельзя нарушать при любых доработках?"* (What core architectural invariants, business rules, and production constraints must never be broken?)
   - **Question 2 (Red Zone & Sensitive Paths):** *"Какие специфические каталоги или модули (биллинг, БД, криптография, ключи, легаси) являются критическими и должны быть заблокированы в Red Zone?"* (Which directories, databases, credentials, or legacy modules must be strictly placed into Red Zone?)
   
   *Processing answers:*
   - User answers to Question 1 are immediately integrated into Section 1 of `AGENTS.md` ("Principles and Architectural Orientations (North Stars)").
   - User answers to Question 2 are mapped into the Red Zone of `boundaries.md` before single-pass flush.
   - If the user skips or provides an empty response, fallback gracefully to the orientations deduced from the Core Inspection Checklist.

3. **Calibrate project concepts and principles:**
   Synthesize the checklist findings and interview answers into 2–3 concise architectural orientations (North Stars) preventing contradictory agent actions.

4. **Match stack skills from agent shell registry:**
   Map the repository stack to specialized skills available in the agent environment (`~/.gemini/config/skills/` and built-in):
   - Python / uv / ruff → `python-pro`
   - FastAPI → `fastapi-pro`
   - TypeScript / JavaScript → `typescript-expert`
   - Next.js → `nextjs-best-practices`
   - Docker / Dockerfile / Compose → `docker-expert`
   - PostgreSQL / SQL / migrations → `postgresql-optimization`, `sql-pro`
   - Kubernetes / Helm → `kubernetes-architect`
   - Telegram bot / aiogram → `telegram-bot-builder`
   - CI/CD pipelines → `github-actions-creator`
   - Clean code & review → `clean-code`, `code-reviewer`

5. **Calibrate boundaries (`boundaries.md`):**
   Refine glob patterns in `.agents/project_knowledge/boundaries.md` for actual project directories:
   - **Default Deny / 100% Path Coverage (Zero Unmapped Dirs):** Guarantee that every non-ignored top-level source directory is explicitly assigned to a zone. Add the Default Deny (Black Zone) rule: any unmapped path is strictly Red Zone by default.
   - **Test Zone Differentiation:**
     - Creating new tests for new functionality — Green zone.
     - Existing regression test suite (`tests/**`, `*_test.*`, `*.spec.*`) — strictly Yellow zone with invariant prohibiting weakening assertions (`assert`/`expect`).
     - Architectural integrity, API contract, and data schema tests (`*integrity*`, `*contract*`, `*schema*`, E2E) — strictly Red zone.
   - Formatting/escaping modules and template engines — strictly Yellow zone.
   - Database files and directories (`data/**`, `*.db`, `*.sqlite*`) — strictly Red zone.
   - Replace placeholder paths with actual migration paths (`alembic/versions/**`, `prisma/migrations/**`, etc.).
   - Replace route/controller paths with actual subsystem locations.

6. **Risk and weak spot analysis (`weak_spots.md`):**
   Record concrete technical debt identified during core inspection (monoliths, singletons), external runtime dependencies (Redis, Postgres, message brokers, system utilities like FFmpeg), platform constraints, and mandatory variables from `.env.example`.

7. **Populate architecture slice (`architecture.md`):**
   Describe high-level stack, subsystems, background tasks/schedulers, and data flows based on inspected core modules.
   - **Conditional End-to-End Data Flows:** Generate the "End-to-End Data Flows (Pre-Flight Flow Tracing)" schema whenever multi-tier, client-server, API, or UI components are detected (mapping `[Origin: UI/CLI/Event] ➔ [Transport: API Route / Message] ➔ [Domain / Storage: Persistence] ➔ [Assembly / Packager] ➔ [Consumer: Client / Daemon]`). For pure single-layer CLI or stdlib libraries without external communication or persistence layers, omit this section to prevent context bloat.

8. **In-Memory Synthesis Flush Protocol:**
   The agent does not write intermediate drafts to disk. All invariants are synthesized in working memory during Passes 1 and 2, after which files are written in strict bottom-up order:
   - Step A: Pre-installed skills (`.agents/skills/record-observation/`, `sync-architecture/`, and `ground-meta-project/`) and automation scripts (`scripts/check_boundaries.py`, `scripts/compact_memory.py` if shared repository setup).
   - Step B: Knowledge slices (`observations.md` -> `boundaries.md` -> `weak_spots.md` -> `architecture.md`).
   - Step C: Root passport (`AGENTS.md`) — strictly last, as the aggregator of references to slices and stack skills.

---

### Finalization and Verification

1. Verify created/updated files using `Get-ChildItem -Recurse .agents` or `ls -R .agents`.
2. **Local Invisible Overlay Option:**
   If initializing in an external/client project or if personal mode without Git commits is requested:
   - Add `AGENTS.md` and `.agents/` to `.git/info/exclude` in target repository.
   - Verify `git status`: meta-project files must not appear in Untracked files.
3. Output concise summary to user:
   - Execution mode (initial setup vs audit with upgrade; shared vs invisible overlay).
   - Created/updated file tree.
   - Captured project orientations (North Stars).
   - List of linked stack skills.

---

## Embedded Reference Templates

### Template: `record-observation/SKILL.md`
```markdown
---
name: record-observation
description: >-
  Use this skill to record an undocumented bug, environment quirk, runtime edge-case,
  or non-obvious solution into the repository's `.agents/project_knowledge/observations.md` table.
---

# Record Observation in Repository Knowledge Base

1. Verify `.agents/project_knowledge/observations.md` exists.
2. Check the last 20 rows for duplicates.
3. Append entry strictly as a single Markdown table line:
   `| YYYY-MM-DD | [<category>] | <Path_or_component> | <Brief issue summary/fact> | <Solution or workaround> |`
   Categories: `[build]`, `[runtime]`, `[deps]`, `[db]`, `[api]`, `[test]`, `[env]`, `[ci]`, `[boundaries]`, `[orchestration]`, `[decommission]`, `[incident]`, `[init]`, or explicit domain tag (e.g. `[theme]`).
4. If row count > 30–40, archive resolved records into `.agents/project_knowledge/archive/observations-YYYY.md`.
```

### Template: `sync-architecture/SKILL.md`
```markdown
---
name: sync-architecture
description: >-
  Use this skill to analyze repository modules, dependencies, and entry points,
  and generate or update `.agents/project_knowledge/architecture.md`.
---

# Sync Project Architecture Slice

1. Read dependency and build manifests.
2. Identify entry points and top-level directories.
3. Identify 3–5 subsystems, their roles, and data flows.
4. Update `.agents/project_knowledge/architecture.md`.
5. Display a brief summary of changes to the user.
```

### Template: `ground-meta-project/SKILL.md`
```markdown
---
name: ground-meta-project
description: >-
  Emergency grounding and recalibration skill: halts runaway edits, forces a zoom-out, re-reads AGENTS.md,
  the active role passport, boundaries.md, and architecture map, diagnoses context drift, and resets the agent into its operating corridor.
---

# Agent Grounding & Emergency Context Reset (Ground Meta-Project)

1. Cease all writing operations and run git status -s.
2. Sequentially re-read AGENTS.md, boundaries.md, .agents/team/<role>/profile.md, and architecture.md.
3. Diagnose context drift, symptom masking, or boundary breaches.
4. Present a structured Grounding Report with root-cause analysis and a 2-3 step recovery plan.
5. Halt and await user confirmation before taking any further code action.
```

### Template: `observations.md`
```markdown
# Agent Observations Base

Cumulative registry of findings, non-obvious environment quirks, and practical solutions.
Entries are logged strictly via the `record-observation` skill in a concise table format (1 line per fact).

---

| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-05 | [init] | example/init | Example registry entry | Solution provided for demonstration |
```

### Template: `boundaries.md`
```markdown
# Responsibility Zones and Change Boundaries

This document defines the agent's level of autonomy when modifying the repository using explicit file path glob patterns.

---

## Green Zone (Autonomous Modification)
Files and directories that the agent can modify autonomously to accomplish the current task:
- Creating new test files (`tests/test_*.py`, `*_test.go`, `*.test.ts`, `*.spec.ts`) to cover new features within a TDD session.
- `src/utils/**`, `src/helpers/**`, `lib/utils/**` — auxiliary local utilities without side effects.
- `docs/**`, `*.md` (except the root `AGENTS.md`) — technical documentation.
- In-code documentation (docstrings, JSDoc, function comments).

---

## Yellow Zone (Modification with Mandatory Verification)
Areas requiring elevated caution and mandatory local test and linter execution prior to delivery:
- `AGENTS.md` — root project passport (requires careful verification and opportunistic refresh).
- `tests/**` (existing regression test suite). **Test emasculation protection invariant:** It is forbidden to weaken `assert`/`expect`, comment out checks, or adjust golden data to match broken code. A test failure indicates a bug in implementation, not a need to rewrite the test. Modifying existing checks is permitted only when user requirements change explicitly.
- `src/api/**`, `src/routes/**`, `src/controllers/**` — public endpoints and routing.
- `src/services/**`, `src/domain/**` — core business logic.
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `requirements.txt` — project dependencies.
- `src/schemas/**`, `src/models/**` — input/output validation schemas (Pydantic / Zod / DTO).
- `scripts/**` — automation scripts and verification utilities.
- `*formatting*`, `*render*`, `templates/**` — formatting modules, template engines, and markup escaping (parsing errors break message delivery).
- `keyboards.*`, `ui/**` — keyboard layouts and UI components.
- `.github/*.yml`, `.github/*.yaml` — repository-level GitHub configurations (e.g., `FUNDING.yml`).

---

## Red Zone (Prohibited Without Direct User Confirmation)
Critical areas of the project. Any modification requires mandatory prior confirmation from the user:
- Architectural integrity and external contract tests: `*integrity*`, `*contract*`, `*schema*`, E2E/snapshot tests of public APIs and integrations.
- `migrations/**`, `alembic/**`, `liquibase/**` — database schema and migration files.
- `data/**`, `*.db`, `*.sqlite*` — local database files and directories.
- `.env*`, `config/secrets/**`, `*.pem`, `*.key` — configurations containing secrets and environment variables.
- `Dockerfile*`, `docker-compose*.yml`, `k8s/**`, `helm/**` — containerization and deployment infrastructure.
- `.github/workflows/**`, `.gitlab-ci.yml`, `Jenkinsfile` — CI/CD pipelines.
- `src/auth/**`, `src/security/**`, `src/crypto/**` — authentication, authorization, sessions, tokens.
- `src/billing/**`, `src/payments/**` — billing and financial transactions.

---

## Default Deny (Black Zone / Unmapped Paths Invariant)
Any directory or file path not explicitly listed in Green, Yellow, or Red zones above is strictly classified as **Red Zone by Default**. Autonomous modifications to unmapped paths are prohibited. Prior to touching unmapped code, the agent MUST consult the user and perform an *Opportunistic Refresh* of `boundaries.md` to map the path to its appropriate zone.
```

### Template: `weak_spots.md`
```markdown
# Weak Spots, Risks, and Technical Debt

Registry of fragile areas, known bugs, and constraints of the repository. Agents MUST consult this registry before modifying listed modules.

---

## 1. Fragile Modules and High Coupling
- *(Example)* `src/legacy_client.py`: high coupling with third-party API; timeout modifications break background workers.

## 2. Environment and Test Constraints
- *(Example)* Integration tests require local Redis running on port 6379, otherwise fail with timeout.
- *(Example)* Windows build fails when paths exceed 260 characters unless LongPathsEnabled is enabled.

## 3. Deferred Technical Debt
- *(Example)* Missing request idempotency locks in transaction processor.
- *(Example)* Hardcoded configuration parameters in report generation module.
```

### Template: `AGENTS.md`
```markdown
# Project Passport: {{PROJECT_NAME}}

## 1. Concept, Principles, and North Stars
- **Service Purpose:** {{PROJECT_DESCRIPTION}}
- **Technology Stack:** {{PROJECT_STACK}}
- **Key Invariant:** {{CRITICAL_INVARIANT}} (e.g.: API backward compatibility, data immutability, preserving DB schema).
- **Principles and Architectural Orientations (North Stars):**
  - {{PRINCIPLE_1}} (e.g.: dependency minimalism, avoiding unnecessary abstractions).
  - {{PRINCIPLE_2}} (e.g.: strict typing and validation at system boundaries).
  - {{PRINCIPLE_3}} (e.g.: explicit error handling without swallowing exceptions).
  - **Circuit Breaker & Flow Tracing:** Prohibit repetitive code edits during cross-component defects without first mapping the data path. Stop on 2nd consecutive fix in the same module to perform root cause investigation.
  - **Default Deny Boundaries:** Any directory not explicitly mapped in boundaries is strictly Red Zone.
  *(Any decisions contradicting these principles are prohibited)*

## 2. Repository Meta-Map
- Core Code: `{{SRC_PATH}}`
- Entry Points: `{{ENTRY_POINTS}}`
- Configuration: `{{CONFIG_PATHS}}`
- Tests: `{{TEST_PATHS}}`

## 3. Directive Meta-Knowledge Protocol
Before taking any action, the agent MUST consult the corresponding knowledge slices.
**Opportunistic Knowledge Refresh:** when reading any slice, evaluate data completeness — fill in missing details, fix outdated information, and eliminate blind spots without destructive overwriting:

- **Responsibilities and Boundaries (`.agents/project_knowledge/boundaries.md`):**
  - *When to consult:* before modifying data schemas, module boundaries, dependencies, security, or configs.
  - *What to update:* supplement and refine glob path patterns to match the real repository structure.
- **Weak Spots and Risks (`.agents/project_knowledge/weak_spots.md`):**
  - *When to consult:* before modifying fragile services, external APIs, queues, or complex legacy code.
  - *What to update:* record newly identified risks, hidden couplings, and remove resolved issues.
- **Architectural Foundations (`.agents/project_knowledge/architecture.md`):**
  - *When to consult:* before adding new components, changing data flows, or modifying interaction contracts.
  - *What to update:* eliminate blind spots in the subsystem map, describe actual connections and data flows (directly or via the `sync-architecture` skill).
- **Observation Base (`.agents/project_knowledge/observations.md`):**
  - *When to consult:* upon build failures, runtime errors, or unexpected environment behavior.
  - *What to update:* immediately and atomically record solved non-trivial bugs using the `record-observation` skill.
- **Active Tasks (`.agents/project_knowledge/tasks.md`):**
  - *When to consult:* at the beginning of any session and upon completing subtasks.
  - *What to update:* track execution progress, register new tasks and delegated steps with author and timestamp `[agent-id @ ISO_DATETIME]`.

## 4. Procedural Skills Registry
### Built-in meta-project skills:
- `ground-meta-project` — emergency grounding, runaway edit halt, and context recalibration.
- `record-observation` — atomic logging of findings and quirks into `observations.md`.
- `sync-architecture` — updating the component map and data flows in `architecture.md`.

### Connected stack skills from environment:
{{STACK_SKILLS}}
*(Managing build, linting, testing, and framework specifics is delegated to these skills)*

## 5. Base Working Protocol
1. Verify against Section 1: ensure the planned solution does not contradict project principles and invariants.
2. Consult the target slice from Section 3; update the slice immediately upon discovering gaps or inaccuracies.
3. Apply stack skills from Section 4 to modify code and run tests.
4. Changes must be minimally sufficient; refactoring of unrelated areas is prohibited; changes must be minimal in diff width, but maximal in root-cause depth.
5. When encountering hidden environment quirks, record the fact via `record-observation`.
```
