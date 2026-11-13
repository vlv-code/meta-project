# Architectural Foundations: Meta-Project

## 1. High-Level System Overview
- **Project Type:** Specification, templates, and agentic context & knowledge framework (Agentic Context & Knowledge Framework).
- **Core Stack:** Python 3.10+ (stdlib `unittest`), Markdown, GitHub Actions CI.
- **Architectural Principle:** Zero runtime dependencies. All validation checks and templates operate autonomously using standard library Python.

## 2. Key Components and Data Flows
- **Templates (`templates/`):**
  - `templates/AGENTS.md` — canonical project passport with North Stars and opportunistic refresh protocol.
  - `templates/global/AGENTS.md` — global user-level passport template for `~/.gemini/AGENTS.md` or home directory environments.
  - `templates/project_knowledge/` — meta-knowledge slices (`architecture.md`, `boundaries.md`, `weak_spots.md`, `observations.md`, `tasks.md`).
  - `templates/team/` — role profile templates (`profile.md`), private notes (`notes.md`), and system prompts (`system_prompt.md`).
- **Procedural Skills (`skills/`):**
  - `skills/init-meta-project/` — two-pass initialization and audit of agent environment in any repository.
  - `skills/manage-meta-project/` — formation, audit, and orchestration of specialized agent roles.
  - `skills/decommission-meta-project/` — non-destructive decommissioning, resizing, and archiving of agent roles.
  - `skills/ground-meta-project/` — emergency grounding, runaway edit halt, and context recalibration.
  - `skills/scan-meta-project/` — integrity inspection, boundary coverage audit, and backfilling meta-knowledge without re-init.
  - `skills/tune-meta-project/` — git friction diagnostics, role topology tuning, and non-bloating North Star crystallization.
  - `skills/update-meta-project/` — non-destructive upstream updating from GitHub or local cache with local_repo_data preservation.
  - `skills/record-observation/` — standardized logging of quirks and solutions into `observations.md`.
  - `skills/sync-architecture/` — structural analysis and generation of the architectural slice.
- **Automation Scripts (`scripts/`):**
  - `scripts/check_boundaries.py` — zero-dependency CLI enforcing Default Deny and responsibility zones via Git diff (supports `--audit-tree` for 100% path coverage, `--diff` for base revision comparison, and `--install-hook` for safe pre-commit chaining).
  - `scripts/compact_memory.py` — memory compaction utility rotating oversized observation tables and completed tasks into `.agents/project_knowledge/archive/`, permanently preserving `[pin]` invariant entries.
  - `scripts/sync_templates.py` — zero-dependency template injection and skill parity synchronizer (`--check` and `--write`).
- **Verification Layer (`tests/`):**
  - `tests/test_integrity.py` — YAML frontmatter validation, mandatory procedural sections, CI configuration, and canonical template checks.
  - `tests/test_check_boundaries.py` — unit tests for boundary gate parser, zone classification engine, and CLI exit codes.
  - `tests/test_compact_memory.py` — unit tests for observation row rotation, task checklist archiving, and dry-run execution.
  - `tests/test_sync_templates.py` — unit tests for template injection, embedded backtick handling, and parity validation.
- **CI/CD Layer (`.github/workflows/`):**
  - `ci.yml` — matrix testing across Python 3.10, 3.11, 3.12, and 3.13 with automated Boundary Gate verification step in GitHub Actions.

## 3. Data and State Invariants
- **Specification Format:** Markdown with YAML frontmatter for skills; Markdown tables for observations; path glob patterns for responsibility zones.
- **Contract Stability:** File names of knowledge slices and templates are fixed in integrity tests.

## 4. End-to-End Data Flows (Pre-Flight Flow Tracing)
Every multi-tier feature or modification touching agent orchestration, templates, or skills must map the lifecycle across framework layers:

```
[User Request / Goal] ➔ [Intake Dispatcher / agent-dev-lead] ➔ [Stack Skills / Subagents] ➔ [Templates / Knowledge Slices / Integrity Tests] ➔ [Verified Delivery]
```
- **Primary Data Flow 1 (Scaffolding):** User prompt ➔ `init-meta-project` ➔ In-Memory Analysis ➔ Materialized `.agents/` + `AGENTS.md` ➔ `test_integrity.py` validation.
- **Primary Data Flow 2 (Orchestration):** User request ➔ `agent-dev-lead` (fast-track) or decomposition ➔ domain role / subagent ➔ telemetry logging in `profile.md` + opportunistic refresh in `project_knowledge/`.
- **Single Source of Truth:** `templates/` and canonical `skills/` in the repository root are authoritative; `.agents/team/` and `.agents/skills/` reflect active deployed instances.

## 5. Design Patterns
- **Separation of Concerns:** Division of static passport rules (`AGENTS.md`), dynamic meta-knowledge slices (`project_knowledge/`), and procedural actions (`skills/`).
- **Opportunistic Knowledge Refresh:** Protocol for continuous knowledge refinement upon every consultation.
