# Canonical Deployment Scenarios (Meta-Project Initialization Reference)

## Overview

This reference provides the exhaustive procedural details for the 7 canonical repository states and deployment scenarios executed by `init-meta-project`.

---

### Scenario 1: State `NONE` (Clean Scaffold Mode)

Standard two-pass algorithm for bootstrapping a fresh repository:

#### Pass 1: Express Scan and Skeleton Generation (Fast & High-Level)
1. **Express root inspection:** manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pom.xml`, `docker-compose.yml`); core directories (`src/`, `app/`, `tests/`, `migrations/`, `scripts/`, `data/`); project name, purpose, core concepts from `README.md`; required keys from `.env.example`.
   - **Zero Unmapped Dirs Rule:** after filtering `.gitignore` paths, VCS metadata, and standard caches (`.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `coverage`, `__pycache__`, `.pytest_cache`, `.idea`, `.vscode`), every remaining top-level source directory MUST be explicitly mapped to Green, Yellow, or Red in boundaries — unmapped falls under Default Deny / Red Zone.
2. **Stack and orientations:** concise stack string (e.g. `Python 3.12, FastAPI, uv, pytest, Docker`) + 2-3 baseline North Stars (simplicity, strict typing, data immutability, offline-first as applicable).
3. **Create directories:** `.agents/project_knowledge/`, `.agents/project_knowledge/archive/`, `.agents/skills/record-observation/`, `.agents/skills/sync-architecture/`, `.agents/skills/ground-meta-project/`, `scripts/`.
4. **Deploy bundled meta-project skills and runtime scripts** (READ: `resources/record-observation-SKILL.md`, `resources/sync-architecture-SKILL.md`, `resources/ground-meta-project-SKILL.md`): deploy the agreed SUBSET defined by `templates/release_manifest.json` of the pinned source. The 3 shell skills are deployed by VERBATIM FILE COPY of those resource files to `.agents/skills/<skill>/SKILL.md` (no in-context transit). Runtime scripts deploy verbatim from the resolved `SCRIPT_ROOT` (or pinned source) to `<target_repo>/scripts/`.
5. **Create initial knowledge slice drafts and registry:** (READ: `resources/observations.md`, `resources/boundaries.md`, `resources/weak_spots.md`) — materialize the three slice drafts from these resources into `.agents/project_knowledge/` byte-canonically (Pass 2 calibrates them in place). Write `.agents/meta-project.json` registering the CURRENT installation as `<installation_id>`/`<harness_id>` with status `active`.
6. **Scaffold baseline `.gitignore` hygiene block (append-if-absent, never overwrite):**
   ```gitignore
   # Meta-Project hygiene baseline (append-if-absent)
   __pycache__/
   *.pyc
   *.lock
   .agents/update-engine.lock
   .agents/update-plan.json
   .agents/update-journal.json
   ```

#### Pass 2: Repository Deep-Dive, Principles & Shell Skills
1. **Mandatory Core Inspection Checklist:**
   - Storage & Database: primary data access module (LOC, schema coupling, migration setup).
   - External API & Service Clients: retries, timeouts, fallbacks, global singletons.
   - Containerization & Runtime: `Dockerfile`, compose, CI workflows (system binaries, permissions, volume mounts).
   - User Interface & Input: keyboard/router modules (platform constraints, FSM states, destructive-action confirmation).
2. **Interactive Calibration Interview (Codified Two-Question Protocol):** exactly 2 focused questions:
   - **Question 1 (North Stars & Core Invariants):** *"Какие ключевые архитектурные инварианты, бизнес-правила и ограничения продакшена (North Stars) нельзя нарушать при любых доработках?"*
   - **Question 2 (Red Zone & Sensitive Paths):** *"Какие специфические каталоги или модули (биллинг, БД, криптография, ключи, легаси) являются критическими и должны быть заблокированы в Red Zone?"*
   - *Processing:* Q1 answers → Section 1 of `AGENTS.md`; Q2 answers → Red Zone of `boundaries.md`.
3. **Calibrate project concepts:** synthesize findings into 2-3 concise architectural orientations.
4. **Match stack skills from the agent shell registry:**
   - Python/uv/ruff → `python-pro`
   - FastAPI → `fastapi-pro`
   - TypeScript/JavaScript → `typescript-expert`
   - Next.js → `nextjs-best-practices`
   - Docker → `docker-expert`
   - PostgreSQL/SQL → `postgresql-optimization`, `sql-pro`
   - Kubernetes/Helm → `kubernetes-architect`
   - Telegram/aiogram → `telegram-bot-builder`
   - CI/CD → `github-actions-creator`
   - clean code & review → `clean-code`, `code-reviewer`
5. **Calibrate boundaries (`boundaries.md` draft from Pass 1):** refine globs for actual project directories. Default Deny / 100% path coverage with Black Zone rule. Never drop mandatory security defaults (`src/auth/**`, `*.pem`, `*.key`, `config/secrets/**`, `.github/workflows/**`, `scripts/check_boundaries.py`).
6. **Risk and weak spot analysis (`weak_spots.md` draft):** record technical debt from inspection.
7. **Populate architecture and tasks slices** (READ: `resources/architecture.md`, `resources/tasks.md`): compose `architecture.md` strictly from the resource (map-first card); compose `tasks.md` from the resource (team rules with `- [>]` checkpoint convention).
8. **In-Memory Synthesis Flush Protocol:** write in strict bottom-up order:
   - Step A: pre-installed skills and automation scripts.
   - Step B: knowledge slices (`observations.md` → `boundaries.md` → `weak_spots.md` → `architecture.md`).
   - Step C (READ: `resources/AGENTS.md`): root passport composed from the resource — strictly last.

---

### Scenario 2: State `FOREIGN_RULES` (Preserve & Merge Mode)
1. Strictly preserve foreign rule files (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, foreign `AGENTS.md`) — never delete or modify.
2. Map foreign rule files into Yellow or Green zones in `boundaries.md` (avoid false Red triggers).
3. Scaffold the `.agents/` structure non-destructively; incorporate foreign instructions into `AGENTS.md` by explicit reference or a designated coexistence section.

---

### Scenario 3: State `HEALTHY_REGISTERED` (Pass-Through / No-Op Mode)
1. Zero-diff verification: **0 modified files**, no temporary files, no locks; report "Meta-Project is intact, verified, and active for current harness. All capability levels operational. Ready for work."
2. Repeat-run semantics: fresh init report → strict no-op; no fresh report → ONE limited re-survey and an adoption init report (`python scripts/manage_reports.py init --action create`), WITHOUT re-scaffolding; read-only request → no report at all; `INCOMPATIBLE_SCHEMA` → diagnostics only, never automatic overwrite (Scenario 7).

---

### Scenario 4: State `HEALTHY_NEW_HARNESS` (Multi-Harness Adaptation Mode)
1. Preserve existing installations — strictly forbidden to delete, disconnect, or alter active entries in `.agents/meta-project.json`.
2. Register the new harness installation (e.g. `zc-main` / `zcode`) with active status.
3. Scaffold role bindings in `.agents/team/` for the new harness, maintaining qualified `actor_id` coordinates.

---

### Scenario 5: State `LEGACY_UNREGISTERED` (Legacy Adoption Mode)
1. Prohibition on destructive overwrite: preserve existing `observations.md` (all historical rows) and `tasks.md`.
2. Upgrade standards: North Stars and directive protocol in `AGENTS.md`; Default Deny / 100% coverage in `boundaries.md`; 5-column observations table with `Category` column.
3. Deploy registry and runtime utilities: `.agents/meta-project.json`, `scripts/inspect_meta_project.py`, `scripts/verify_identity.py`, `scripts/record_obs.py`.

---

### Scenario 6: State `PARTIAL_CORRUPTED` (Diagnose & Repair Mode)
Report exact missing components or syntax errors from the inspection report (`missing_components`, `conflicts`); surgically recreate ONLY missing/corrupted files without touching intact knowledge bases or profiles (READ only the resource matching the file being recreated).

---

### Scenario 7: State `INCOMPATIBLE_SCHEMA` (Read-Only Fallback Mode)
Fail-closed protection: no automatic writes when `schema_version` is incompatible; report the mismatch, enter read-only inspection mode, and provide manual migration instructions.

---

## Reference Loading Contract & Fallback
If `references/scenarios.md` is unavailable (`[MISSING_RESOURCE] references/scenarios.md`), rely on the summary routing table in `skills/init-meta-project/SKILL.md` and basic repository inspection without halting execution.
