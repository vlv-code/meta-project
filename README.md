# Agent Environment Framework for Repositories (Meta-Project)

[English](README.md) | [Русский](README.ru.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Status: Alpha](https://img.shields.io/badge/Status-1.0.0--alpha.8-orange.svg)](CHANGELOG.md)
[![CI](https://github.com/vlv-code/meta-project/actions/workflows/ci.yml/badge.svg)](https://github.com/vlv-code/meta-project/actions/workflows/ci.yml)
[![Boosty](https://img.shields.io/badge/Donate-Boosty-F15F2C.svg)](https://boosty.to/oovlvoo)
[![USDT TON](https://img.shields.io/badge/Donate-USDT%20TON-26A17B.svg)](#support-the-project)

<!-- META-PROJECT:ENTRY:BEGIN -->
[![Built with Meta-Project](https://img.shields.io/badge/Built%20with-Meta--Project-blueviolet)](https://github.com/vlv-code/meta-project)

Agent instructions: [AGENTS.md](AGENTS.md) | Policy: [.agents/project_knowledge/boundaries.md](.agents/project_knowledge/boundaries.md)  
*To inspect, configure, or adapt your environment, run `python scripts/inspect_meta_project.py` or invoke the `init-meta-project` skill.*
<!-- META-PROJECT:ENTRY:END -->

Context organization framework and separation of concerns between permanent rules (`AGENTS.md`), focused meta-knowledge slices (`project_knowledge/`), and procedural skills (`skills/`) in Google Antigravity and compatible agent environments.

> [!WARNING]
> **Active Development & Work in Progress (Alpha)**
> Meta-Project is currently under rapid iterative development and empirical testing. Specifications, boundary rules, CLI utilities, and skill formats may evolve based on real-world findings.
> 
> 💡 **Help & Feedback Wanted:** We actively welcome your help! Whether it is stress-testing skills on your tech stack, proposing new agent invariants, reporting edge cases, or opening Pull Requests — see [Contributing](#contributing) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Table of Contents

- [Installation](#installation)
- [Architectural Principles](#architectural-principles)
- [Target Repository Structure](#target-repository-structure)
- [Repository Inspection & Canonical States](#repository-inspection--canonical-states)
- [Glossary](#glossary)
- [Meta-Project Components](#meta-project-components)
- [Quickstart](#quickstart)
- [Testing and Validation](#testing-and-validation)
- [Documentation and Research](#documentation-and-research)
- [Contributing](#contributing)
- [Support the Project](#support-the-project)
- [License](#license)

---

## Installation

Install Meta-Project as a plugin or package — no manual copying required. Three channels are supported:

### Claude Code (plugin marketplace)

```bash
claude plugin marketplace add vlv-code/meta-project
```

Then inside Claude Code: `/plugin install meta-project`

### Agent Plugins (VS Code, Cursor, Copilot, Codex)

```bash
npx plugins add vlv-code/meta-project
```

Installs the Agent Plugins 1.0.0 package for compatible hosts.

### skills.sh (per-skill install)

```bash
npx skills add vlv-code/meta-project
```

> [!IMPORTANT]
> Per-skill installers copy the skill folders only. `sync-architecture` is the single standalone skill; the other nine require the repository's `scripts/` and `templates/` to run — install the full plugin or package instead of cherry-picking individual skills.

---

## Architectural Principles

1. **No Context Bloat:**  
   The root `AGENTS.md` contains only fundamental invariants, guiding principles (North Stars), stack declarations, and navigation protocols. Because it is permanently loaded into context [by documentation], it remains free of dynamic logs and bulky descriptions.
2. **Guards Against Architectural Contradictions:**  
   The project passport establishes core principles and decision guardrails (e.g., zero external dependencies, no redundant abstractions, strict typing), preventing foreign or conflicting decisions.
3. **Read + Opportunistic Refresh:**  
   When consulting any meta-knowledge slice before taking action, an agent does not merely read it passively; it is required to close discovered gaps, record inaccuracies, and maintain the integrity of the project picture.
4. **Non-Destructive Update:**  
   The `init-meta-project` skill automatically recognizes an existing meta-project structure in the target repo, preserves all accumulated data (`observations.md`, custom invariants), and safely equips the project with updated standards.
5. **Delegation to Stack Domain Skills:**  
   Instead of hardcoding build and linting commands, the passport connects specialized domain skills from the agent environment (`python-pro`, `typescript-expert`, `docker-expert`, etc.), which hold built-in command knowledge and idioms.
6. **Machine-Readable Glob Boundaries:**  
   Responsibility zones in `boundaries.md` are defined via explicit glob path patterns, eliminating subjective interpretation by agents.

---

## Target Repository Structure

After initialization, the following standardized structure is created in any target project:

```text
<project_root>/
├── AGENTS.md                          # Passport & navigator (North Stars, stack, refresh protocol, skills)
└── .agents/
    ├── project_knowledge/             # Meta-knowledge slices (loaded on-demand)
    │   ├── architecture.md            # Architectural foundations & component relationships
    │   ├── boundaries.md              # Machine-readable zones (Green, Yellow, Red)
    │   ├── weak_spots.md              # Known pitfalls, risks, and technical debt
    │   ├── observations.md            # Cumulative agent observation log (categorized)
    │   └── tasks.md                   # Active task registry and cross-agent checklist
    ├── skills/                        # Pre-installed repository skills
    │   ├── ground-meta-project/       # Context recovery and drift diagnosis (dual-mode)
    │   │   └── SKILL.md
    │   ├── record-observation/        # Atomic observation logging to observations.md
    │   │   └── SKILL.md
    │   └── sync-architecture/         # Architecture & component sync to architecture.md
    │       └── SKILL.md
    └── team/                          # (Optional) Specialized subagent team (via manage-meta-project)
        ├── agent-<role>/
        │   ├── profile.md             # Role passport and invocation telemetry
        │   ├── notes.md               # Private role-isolated working notes
        │   └── system_prompt.md       # Tailored role system prompt with invariants
        └── archive/                   # Safely decommissioned roles (via decommission-meta-project)
```

---

## Repository Inspection & Canonical States

Meta-Project features a deterministic, zero-write inspection engine (`scripts/inspect_meta_project.py`) using only the Python 3.10+ standard library. It classifies any repository into one of 8 canonical states and evaluates readiness across 5 capability dimensions (`read_instructions`, `local_checks`, `skills`, `roles`, `hooks`):

| State Code | Canonical State | Criteria & Signatures | Action & Strategy |
| :--- | :--- | :--- | :--- |
| `NONE` | Greenfield repository | No `AGENTS.md`, no `.agents/`, no recognized agent instructions. | **Scaffold Clean:** Generate full Meta-Project skeleton tailored to detected stack. |
| `FOREIGN_RULES` | Foreign agent rules | Foreign instructions found (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, or foreign `AGENTS.md`). | **Preserve & Merge:** Retain foreign files intact, establish coexistence wrapper. |
| `HEALTHY_REGISTERED` | Meta-Project intact (active) | Meta-Project intact (`AGENTS.md`, `.agents/meta-project.json`, `boundaries.md`, scripts); current harness is active. | **Verify & Pass-Through:** No-op. Zero diff, zero locks, report ready status. |
| `HEALTHY_NEW_HARNESS` | New harness onboarding | Meta-Project intact; target harness/installation is not registered or is registered as `planned`. | **Bind Harness:** Scaffold role bindings and installation adapter without disturbing active setups. |
| `CONTEXT_UNRESOLVED` | Runtime context not provided | Meta-Project structure is intact, but no `--harness`/`--installation` was provided; the registered status of the caller cannot be determined without silently adopting an arbitrary active installation. | **Provide Runtime Context:** Re-run with `--harness` and `--installation` matching a registered installation. |
| `LEGACY_UNREGISTERED` | Legacy setup without registry | Older Meta-Project structure without `.agents/meta-project.json` or identity engine. | **Legacy Adoption:** Upgrade table headers, generate `.agents/meta-project.json`, preserve historical logs. |
| `PARTIAL_CORRUPTED` | Partial / corrupted setup | Missing critical files (e.g. `boundaries.md` absent, corrupted JSON, missing core scripts). | **Diagnose & Repair:** Report exact discrepancies; offer surgical repair plan without overwriting intact slices. |
| `INCOMPATIBLE_SCHEMA` | Incompatible registry schema | `.agents/meta-project.json` present but `schema_version` is major-incompatible with current tooling. | **Read-Only Fallback:** Lock into read-only audit mode, report required schema migration. |

To inspect your repository without modifying any files:
```bash
python scripts/inspect_meta_project.py --read-only
# -> CONTEXT_UNRESOLVED: the structure is healthy, but the caller context is unknown.
# Provide a registered harness + installation to resolve the runtime status:
python scripts/inspect_meta_project.py --harness zcode --installation zc-main --read-only
# Or machine-readable JSON format:
python scripts/inspect_meta_project.py --harness zcode --installation zc-main --json
```

---

## Glossary

Project vocabulary used across this README, the skills, and the scripts — every term links to its canonical source.

| Term | Definition | Canonical source |
| :--- | :--- | :--- |
| North Stars | The project's non-negotiable invariants. | [Framework Philosophy and Vision (RU)](docs/framework_philosophy_and_vision.md) |
| Passport | The root `AGENTS.md`: invariants plus navigation to the knowledge slices. | [templates/AGENTS.md](templates/AGENTS.md) |
| Knowledge slice | A themed knowledge file under `.agents/project_knowledge/`, read just in time. | [templates/project_knowledge/](templates/project_knowledge/) |
| Zones | Green (autonomous) / Yellow (mandatory verification) / Red (explicit user confirmation only). | [templates/project_knowledge/boundaries.md](templates/project_knowledge/boundaries.md) |
| Default Deny | Anything not mapped to a zone is treated as Red. | [templates/project_knowledge/boundaries.md](templates/project_knowledge/boundaries.md) |
| Canonical state | One of the 8 repository states reported by inspection. | [Repository Inspection & Canonical States](#repository-inspection--canonical-states) |
| Capability matrix | 5 readiness dimensions: `read_instructions`, `local_checks`, `skills`, `roles`, `hooks`. | [scripts/inspect_meta_project.py](scripts/inspect_meta_project.py) |
| Opportunistic refresh | When reading a slice, close gaps without destructive overwriting. | [templates/AGENTS.md](templates/AGENTS.md) |
| Facts digest | SHA-256 fingerprints of the slices so unchanged ones need not be re-read (`inspect --facts-digest`). | [scripts/inspect_meta_project.py](scripts/inspect_meta_project.py) |
| Decision-RTL | The template for justifying an architectural decision. | [Framework Philosophy and Vision (RU)](docs/framework_philosophy_and_vision.md) |
| Astra primitives | Names for 4 existing operations: deterministic survey, identity admission, report intake, observation recording. | [docs/primitives.md](docs/primitives.md) |
| Harness | An agent environment (Claude Code, Cursor, Windsurf, ZCode, ...) detected from environment signatures. | [scripts/inspect_meta_project.py](scripts/inspect_meta_project.py) |
| Installation | An entry in `.agents/meta-project.json` registering a harness in this repository. | [Architecture Decision Records and Roadmap (RU)](docs/decisions_and_roadmap.md) |
| Deployment modes | Shared (committed to Git) / invisible overlay (local only). | [Deployment Modes (Quickstart #6)](#6-deployment-modes-shared-repo-level-vs-invisible-overlay) |

Zone mini-example (paths are illustrative):

```text
Green: docs/**, tests/test_*.py — autonomous
Yellow: AGENTS.md, pyproject.toml — only after local verification
Red: .env*, migrations/**, src/auth/** — only with explicit permission
Anything unmapped is Red (Default Deny).
```

---

## Meta-Project Components

- **`templates/`**:
  - `templates/AGENTS.md` — Canonical project passport template featuring guiding principles (North Stars) and the opportunistic refresh protocol.
  - `templates/global/AGENTS.md` — Universal global agent harness configuration template (First-Contact Rule, Default Deny, Circuit Breaker).
  - `templates/project_knowledge/` — Baseline templates for the project meta-knowledge repository (`architecture.md`, `boundaries.md`, `weak_spots.md`, `observations.md`, `tasks.md`).
  - `templates/team/` — Role passport template (`profile.md`), isolated private notes (`notes.md`), and system prompt (`system_prompt.md`).
- **`skills/`**:
  - `skills/init-meta-project/` — Autonomous skill supporting two execution modes: safe audit/update of an existing `meta-project` without data loss, or clean repository two-pass initialization with a mandatory Core Inspection Checklist, codified interactive interview, and atomic In-Memory Synthesis Flush.
  - `skills/manage-meta-project/` — Skill for creating, auditing, and orchestrating a specialized subagent team (.agents/team/) with a scale-adaptive competency matrix, role pruning, and User-Mediated Handoff protocols.
  - `skills/decommission-meta-project/` — Skill for safe, non-destructive decommissioning, resizing, and archiving of specialized agent roles (.agents/team/) into `.agents/team/archive/` with telemetry closeout, root `AGENTS.md` synchronization, and orphaned tasks reassignment without data loss.
  - `skills/ground-meta-project/` — Dual-mode context recovery and drift diagnosis skill: recovers goal, state, identity, and authority after session changes, repository moves, updates, or memory compaction; semantic triggers, selective canonical reading, validator-based identity, and conditional continuation instead of an unconditional halt.
  - `skills/scan-meta-project/` — Express and deep-dive inspection skill: audits repository meta-knowledge integrity, verifies 100% boundary coverage, detects architectural drift, and backfills missing facts without re-initialization.
  - `skills/tune-meta-project/` — Calibration and optimization skill: diagnoses git friction, analyzes telemetry, tunes role topology, refines boundary zones, and crystallizes North Star invariants.
  - `skills/update-meta-project/` — Non-destructive upstream updating skill from GitHub or local cache with dual-tier source resolution and seamless `local_repo_data` preservation.
  - `skills/record-observation/` — Skill for categorized logging of observations into `observations.md` with duplicate suppression and compaction triggers.
  - `skills/sync-architecture/` — Skill for structural manifest analysis and component map synchronization.
  - `skills/triage-incident/` — Evidence-first epistemic triage skill for split-runtime silent failures: enforces empirical artifact checks, unmasked stderr capture, PROBE -> record-evidence -> promote gating, diagnostic Circuit Breaker, and Error-Path / Fallback-Masking audits (see docs/decisions_and_roadmap.md §10).
- **`scripts/`**:
  - `scripts/inspect_meta_project.py` — Zero-dependency deterministic inspection engine evaluating the 8 canonical repository states, capability matrix, and worktree awareness (supports `--json`, `--read-only`, and `--harness`/`--installation` runtime context).
  - `scripts/check_boundaries.py` — Zero-dependency Boundary Gate CLI enforcing Green/Yellow/Red zones and Default Deny (Black Zone) on Git diffs locally and in GitHub Actions CI (supports `--audit-tree` for 100% path coverage and `--install-hook` for pre-commit installation; the installed hook admits a user-sanctioned Red Zone change only via the explicit `META_PROJECT_ALLOW_RED_ZONE=1` commit environment).
    Enforcement against self-certification is handled in CI (trusted-base gate); the local pre-commit hook is a convenience layer, and `META_PROJECT_ALLOW_RED_ZONE=1` is a local operator override.
  - `scripts/compact_memory.py` — Context Rot Shield utility automatically rotating oversized observation tables (>20 rows) and completed tasks into `.agents/project_knowledge/archive/`, retaining permanent `[pin]` invariants with cross-platform file locking (`msvcrt`/`fcntl`).
  - `scripts/sync_templates.py` — Zero-dependency utility synchronizing canonical templates into embedded skills, byte-copying canonical sources into the init lazy-load pilot `resources/` payload, and maintaining 1-to-1 parity between `skills/` and `.agents/skills/` (with `--check` mode for CI).
  - `scripts/record_obs.py` — Zero-dependency CLI for atomic observation logging into `observations.md` with a unified 16-category vocabulary shared with the skill documentation, Markdown pipe escaping, `--actor-id` attribution, and file locking.
  - `scripts/verify_identity.py` — Zero-dependency multi-harness identity validator verifying `.agents/meta-project.json` registry, qualified `actor_id` bindings, and role profile synchronization.
  - `scripts/manage_reports.py` — Zero-dependency report engine for init/manage/update/tune scenario reports: canonical schemas (`templates/reports/`), deterministic run IDs, staleness and intake admission checks (`latest`/`verify` accept `--type {init,manage,update,tune}`).
  - `scripts/update_meta_project.py` — Managed update engine (SHA-pinned, atomic, journaled): read-only `check`/`plan`, atomic `apply` with rollback journal, approved-plan integrity and update report, offline cache fallback (dead origin + exact SHA + integral cache), runtime-layout target mapping, manifest `resource` component mapping, `--adopt-existing` sha-match adoption, and `restore` of the engine's own changes.
  - `scripts/triage_incident.py` — Zero-dependency epistemic triage CLI implementing deterministic subcommands: `probe`, `record-evidence`, `promote` (fail-closed gate preventing premature fix tasks), `check-tasks`, and `artifact` comparison.
- **`docs/`**:
  - `docs/decisions_and_roadmap.md` — Architecture Decision Records (canonical range ADR #14–#23, Polyglot Monorepo Incident, and Split-Runtime Silent-Failure Incident §10) and roadmap.
  - `docs/test_report_alpha_skill.md` — Empirical test report from test cycles (Tests 1–6) on a sample bot service.
  - `docs/temporary_overrides.md` — Temporary rule calibrations.

---

## Quickstart

### 1. Preparing the Global Agent Harness (Universal First-Contact Setup)
To enable autonomous agents to discover and respect Meta-Project passports (`AGENTS.md`) and knowledge slices across all repositories, configure your environment using `templates/global/AGENTS.md`:

| Agent Harness | Global Configuration Path | Recommended Action |
| :--- | :--- | :--- |
| **Google Antigravity / Gemini CLI** | `~/.gemini/GEMINI.md` | Append content from `templates/global/AGENTS.md` |
| **Claude Code** | `~/.claude/CLAUDE.md` | Append content from `templates/global/AGENTS.md` |
| **Cursor / Windsurf** | Global User Rules / `.cursorrules` | Paste content from `templates/global/AGENTS.md` |
| **Open Agent Runners** | `~/AGENTS.md` | Copy `templates/global/AGENTS.md` |

### 2. Connecting Skills to the Agent Environment
Copy the meta-project skills (`init-meta-project`, `manage-meta-project`, `decommission-meta-project`, `ground-meta-project`) to your agent environment's skill directory:
- For Google Antigravity: `~/.gemini/config/skills/<skill-name>`
- Or use locally as part of your tooling suite.

### 3. Project Initialization
Navigate to the root of any target repository and issue the command to the agent:
```text
Prepare the repository for agent workflows using the init-meta-project skill
```

The agent will:
1. Analyze manifests and directory structure.
2. Inspect critical components (Core Inspection Checklist: Database, API, Docker, UI/Validation).
3. Generate root `AGENTS.md` and meta-knowledge directory `.agents/project_knowledge/`.
4. Install local repository skills (`record-observation`, `sync-architecture`).

### 4. Agent Team Orchestration and Decommissioning (Optional)
To deploy and orchestrate specialized agent roles:
```text
Assemble agent team using manage-meta-project skill
```
To safely archive or resize agent roles without data loss:
```text
Decommission agent team using decommission-meta-project skill
```

### 5. Context Recovery & Drift Diagnosis
If an agent loses its goal, state, identity, or authority after a session change, repository move, update, or memory compaction — or drifts, loops across speculative fixes, or breaches role boundaries:
```text
Recover agent context using ground-meta-project skill
```

### 6. Deployment Modes: Shared Repo-Level vs Invisible Overlay

Meta-Project supports two usage scenarios:
- **Shared Repo-Level (Team / Open Standard):**  
  `AGENTS.md` and `.agents/` are committed to Git. Rules, architecture maps, and risk logs are shared across all developers, agents, and CI pipelines.
- **Invisible Overlay (Personal Dashboard for Third-Party/Work Repos):**  
  `AGENTS.md` and `.agents/` are added to the target project's local `.git/info/exclude`. The agent gains full access to meta-knowledge on your local machine, keeping Git commits completely clean in external repositories.

#### Optional Easter Egg Badge
To indicate that a project is designed or maintained with an agentic environment, add the badge to its `README.md`:
```markdown
[![Agent Environment: Meta-Project](https://img.shields.io/badge/Agent%20Environment-Meta--Project-5865F2)](https://github.com/vlv-code/meta-project)
```

---

## Testing and Validation

The project includes automated integrity tests for skills, YAML frontmatter, templates, and canonical structure:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Tests have zero external dependencies and run on any platform with Python 3.10+.

---

## Documentation and Research

- [Architecture Decision Records and Roadmap (ADR)](docs/decisions_and_roadmap.md)
- [Framework Philosophy and Vision](docs/framework_philosophy_and_vision.md)
- [Empirical Skill Test Report (Tests 1–6)](docs/test_report_alpha_skill.md)
- [Orchestration Team Empirical Report](docs/test_report_orchestration_team.md)
- [Temporary Rule Calibrations](docs/temporary_overrides.md)

---

## Contributing

Meta-Project is in active development, and community contributions are very welcome! We are especially looking for help with:
- **Real-World Stress Testing:** Test `init-meta-project` and agent teams across diverse tech stacks (Rust, Go, Node.js, C/C++, mobile, microservices) and share your findings.
- **Edge Cases & Invariants:** Help identify boundary leaks, model drift patterns, or architectural friction points to enrich `observations.md` and default boundary templates.
- **Tooling & Integrations:** Extend zero-dependency CLI utilities (`check_boundaries.py`, `compact_memory.py`, `sync_templates.py`) or contribute agent adapter templates for other environments.
- **Documentation & Localization:** Improve guides, bilingual parity, or add new usage examples.

Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a Pull Request.

All version changes are tracked in [CHANGELOG.md](CHANGELOG.md).

---

## Support the Project

If Meta-Project has been useful, you can support its development:
- **[Boosty](https://boosty.to/oovlvoo)**
- **Cryptocurrency:** USDT, network TON (USDT only and only this network, otherwise funds will be lost):
  ```text
  UQDASKlEmcoPuBr5-u5jSjLdXWfCiSfARjPc_wWW0qLbSreC
  ```

---

## License

Distributed under the [MIT](LICENSE) License.
