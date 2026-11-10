# Project Passport: Meta-Project

## 1. Concept, Principles, and North Stars
- **Service Purpose:** Agentic environment and context organization framework for repositories: project passport (`AGENTS.md`), dynamic knowledge slices (`.agents/project_knowledge/`), and procedural skills (`skills/`).
- **Technology Stack:** Python 3.10+ (stdlib `unittest`), Markdown, GitHub Actions CI.
- **Key Invariant:** Zero-dependency policy — all templates, validation utilities, and integrity tests must run without external runtime dependencies, using only the Python standard library.
- **Principles and Architectural Orientations (North Stars):**
  - **No Context Bloat:** The root `AGENTS.md` is concise, free of dynamic logs, and contains only fundamental guidelines, meta-map, and protocols.
  - **Structural Canonicity and Validation:** All skills and templates must strictly conform to the format specification (YAML frontmatter, "When to invoke skill" and "Execution steps" sections) and be verified by `test_integrity.py`.
  - **Opportunistic Refresh (Read + Opportunistic Refresh):** When consulting any meta-knowledge slice, the agent closes identified gaps and updates the repository picture without destructive overwriting of accumulated data.
  - **Circuit Breaker & Flow Tracing:** Prohibit repetitive code edits during cross-component defects without first mapping the data path. Stop on 2nd consecutive fix in the same module to perform root cause investigation.
  - **Default Deny Boundaries:** Any directory not explicitly mapped in boundaries is strictly Red Zone.
  *(Any decisions contradicting these principles are prohibited)*

## 2. Repository Meta-Map
- Core Code & Skills: `skills/` (`init-meta-project`, `manage-meta-project`, `decommission-meta-project`, `ground-meta-project`, `scan-meta-project`, `tune-meta-project`, `update-meta-project`, `record-observation`, `sync-architecture`)
- Canonical Templates: `templates/` (`templates/AGENTS.md`, `templates/project_knowledge/`, `templates/team/`)
- CI/CD Configuration: `.github/workflows/ci.yml`
- Integrity Tests: `tests/test_integrity.py`
- Automation Scripts: `scripts/check_boundaries.py`, `scripts/compact_memory.py`, `scripts/sync_templates.py`
- Documentation and Decisions: `docs/decisions_and_roadmap.md`, `README.md`, `CHANGELOG.md`

## 3. Directive Meta-Knowledge Protocol
Before taking any action, the agent MUST consult the corresponding knowledge slices.
**Opportunistic Knowledge Refresh:** when reading any slice, evaluate data completeness — fill in missing details, fix outdated information, and eliminate blind spots without destructive overwriting:

- **Responsibilities and Boundaries (`.agents/project_knowledge/boundaries.md`):**
  - *When to consult:* before modifying skills structure, templates, CI/CD, or documentation.
  - *What to update:* supplement and refine glob path patterns to match the real repository structure.
- **Weak Spots and Risks (`.agents/project_knowledge/weak_spots.md`):**
  - *When to consult:* before modifying integrity tests, skills format, or template structures.
  - *What to update:* record newly identified risks, hidden couplings, and remove resolved issues.
- **Architectural Foundations (`.agents/project_knowledge/architecture.md`):**
  - *When to consult:* before adding new skills, templates, or orchestration changes.
  - *What to update:* eliminate blind spots in the component map, describe actual connections and data flows (directly or via `sync-architecture`).
- **Observation Base (`.agents/project_knowledge/observations.md`):**
  - *When to consult:* upon test validation errors, runtime issues, or suspicious environment behavior.
  - *What to update:* immediately and atomically record solved non-trivial bugs using `record-observation`.
- **Active Tasks (`.agents/project_knowledge/tasks.md`):**
  - *When to consult:* at the beginning of any session and upon completing subtasks.
  - *What to update:* track execution progress, register new tasks and delegated steps.

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
- `python-pro` — Python development and refactoring, adhering to Python 3.10+ standards.
- `github-actions-creator` — audit and maintenance of GitHub Actions CI/CD workflows.
- `clean-code` — adherence to clean code principles and minimal sufficient changes.
- `code-reviewer` — verification of code and template quality prior to commit.
*(Managing build, linting, testing, and framework specifics is delegated to these skills)*

## 5. Base Working Protocol
1. Verify against Section 1: ensure the planned solution does not contradict project principles and invariants.
2. Consult the target slice from Section 3; update the slice immediately upon discovering gaps or inaccuracies.
3. Apply stack skills from Section 4 to modify code and run tests.
4. Changes must be minimally sufficient; refactoring of unrelated areas is prohibited; changes must be minimal in diff width, but maximal in root-cause depth.
5. When encountering hidden environment quirks, record the fact via `record-observation`.

## 6. Project Agent Team (.agents/team/)
- [Lead Developer & Dispatcher](.agents/team/agent-dev-lead/profile.md) — Task decomposition, user request intake analysis, rapid execution of core Python utilities, scripts, and feature implementation (invoked by: "plan task", "decompose request", "implement feature", "write script", "develop component", "fix logic")
- [Quality & Meta-Architecture Guardian](.agents/team/agent-quality-guardian/profile.md) — Ecosystem integrity oversight, canonical passport audit, test suite execution, knowledge base consistency, and dead code/broken links auditing (invoked by: "verify meta-project structure", "run tests", "audit passport", "audit knowledge base", "check links", "check dead code")
- [GitHub Steward & Release Captain](.agents/team/agent-github-steward/profile.md) — Git hygiene, conventional commits, GitHub Actions CI/CD workflows, release readiness, and Code-to-README truth parity (invoked by: "git hygiene", "audit ci", "prepare release", "check readme parity", "conventional commit")
*(Granular legacy roles archived in `.agents/team/archive/`)*
