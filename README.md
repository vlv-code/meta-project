# Agent Environment Framework for Repositories (Meta-Project)

[English](README.md) | [Русский](README.ru.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Status: Alpha](https://img.shields.io/badge/Status-1.0.0--alpha.1-orange.svg)](CHANGELOG.md)
[![Tests: Passing](https://img.shields.io/badge/Tests-Passing-success.svg)](tests/)
[![Boosty](https://img.shields.io/badge/Donate-Boosty-F15F2C.svg)](https://boosty.to/oovlvoo)
[![USDT TON](https://img.shields.io/badge/Donate-USDT%20TON-26A17B.svg)](#support-the-project)

Context organization framework and separation of concerns between permanent rules (`AGENTS.md`), focused meta-knowledge slices (`project_knowledge/`), and procedural skills (`skills/`) in Google Antigravity and compatible agent environments.

> [!WARNING]
> **Active Development & Work in Progress (Alpha)**
> Meta-Project is currently under rapid iterative development and empirical testing. Specifications, boundary rules, CLI utilities, and skill formats may evolve based on real-world findings.
> 
> 💡 **Help & Feedback Wanted:** We actively welcome your help! Whether it is stress-testing skills on your tech stack, proposing new agent invariants, reporting edge cases, or opening Pull Requests — see [Contributing](#contributing) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Table of Contents

- [Architectural Principles](#architectural-principles)
- [Target Repository Structure](#target-repository-structure)
- [Meta-Project Components](#meta-project-components)
- [Quickstart](#quickstart)
- [Testing and Validation](#testing-and-validation)
- [Documentation and Research](#documentation-and-research)
- [Contributing](#contributing)
- [Support the Project](#support-the-project)
- [License](#license)

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
    │   ├── ground-meta-project/       # Emergency grounding and context recalibration
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
  - `skills/ground-meta-project/` — Emergency grounding and context recalibration skill: halts runaway edits, forces a zoom-out, re-reads canonical sources, and anchors the agent back into its operating corridor.
  - `skills/scan-meta-project/` — Express and deep-dive inspection skill: audits repository meta-knowledge integrity, verifies 100% boundary coverage, detects architectural drift, and backfills missing facts without re-initialization.
  - `skills/tune-meta-project/` — Calibration and optimization skill: diagnoses git friction, analyzes telemetry, tunes role topology, refines boundary zones, and crystallizes North Star invariants.
  - `skills/update-meta-project/` — Non-destructive upstream updating skill from GitHub or local cache with dual-tier source resolution and seamless `local_repo_data` preservation.
  - `skills/record-observation/` — Skill for categorized logging of observations into `observations.md` with duplicate suppression and compaction triggers.
  - `skills/sync-architecture/` — Skill for structural manifest analysis and component map synchronization.
- **`scripts/`**:
  - `scripts/check_boundaries.py` — Zero-dependency Boundary Gate CLI enforcing Green/Yellow/Red zones and Default Deny (Black Zone) on Git diffs locally and in GitHub Actions CI (supports `--audit-tree` for 100% path coverage and `--install-hook` for pre-commit installation).
  - `scripts/compact_memory.py` — Context Rot Shield utility automatically rotating oversized observation tables (>20 rows) and completed tasks into `.agents/project_knowledge/archive/`, retaining permanent `[pin]` invariants.
  - `scripts/sync_templates.py` — Zero-dependency utility synchronizing canonical templates into embedded skills and maintaining 1-to-1 parity between `skills/` and `.agents/skills/` (with `--check` mode for CI).
- **`docs/`**:
  - `docs/decisions_and_roadmap.md` — Architecture Decision Records (ADR #1–#8 + Polyglot Monorepo Incident) and roadmap.
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

### 5. Emergency Grounding & Forced Zoom-Out
If an agent exhibits context drift, loops across speculative fixes, or breaches role boundaries:
```text
Recalibrate agent using ground-meta-project skill
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
- [Empirical Skill Test Report (Tests 1–6)](docs/test_report_alpha_skill.md)
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
