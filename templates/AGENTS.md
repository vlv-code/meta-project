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
  - **Default Closed Tooling:** Core framework and agents operate in a zero-dependency closed loop by default. External tools and third-party dependencies are permitted ONLY when explicitly declared (opt-in) in project specification or requested by user. Liability for external tool failures rests on the project/operator.
  - **Adversarial Testing Invariant:** When applying TDD, write negative/adversarial tests (boundary conditions, malformed input, failure modes) and confirm RED before writing implementation code to transition to GREEN.
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
- `init-meta-project` — repository scaffolding and non-destructive initialization.
- `manage-meta-project` — scale-adaptive agent team orchestration and materialization.
- `decommission-meta-project` — non-destructive decommissioning, resizing, and archiving of agent roles.
- `ground-meta-project` — emergency grounding, runaway edit halt, and context recalibration.
- `scan-meta-project` — integrity inspection, boundary coverage audit, and backfilling meta-knowledge without re-init.
- `tune-meta-project` — git friction diagnostics, role topology tuning, and non-bloating North Star crystallization.
- `update-meta-project` — non-destructive upstream updating from GitHub or local cache with local_repo_data preservation.
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
