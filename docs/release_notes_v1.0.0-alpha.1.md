# Meta-Project v1.0.0-alpha.1

> [!WARNING]
> **Active Development & Experimental Status (Alpha)**
> Meta-Project is currently under rapid iterative development and empirical testing. Specifications, boundary rules, CLI utilities, and skill formats may evolve based on real-world findings.
> 
> 💡 **Community Help Wanted:** We welcome testing on diverse repositories, feedback, bug reports, and pull requests! See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## 🚀 Highlights & Core Capabilities

Meta-Project is a context organization framework and separation-of-concerns architecture between permanent rules (`AGENTS.md`), focused dynamic meta-knowledge slices (`project_knowledge/`), and procedural skills (`skills/`) for Google Antigravity and compatible agent environments.

### 🛡️ Machine-Enforced Boundary Gate (`scripts/check_boundaries.py`)
- Zero runtime external dependencies (pure Python 3.10+ standard library).
- Enforces Green (autonomous), Yellow (assert-protected), and Red (approval-required) zones.
- Enforces strict **Default Deny (Black Zone)** rule: unmapped paths halt execution.
- `--audit-tree`: Verifies 100% path coverage across repository files.
- `--install-hook`: Automatically sets up executable `.git/hooks/pre-commit` to prevent boundary breaches.

### 🧹 Context Rot Shield & Memory Compaction (`scripts/compact_memory.py`)
- Automatically rotates oversized `observations.md` (>20 rows) and completed tasks into `.agents/project_knowledge/archive/`.
- `[pin]` invariant tags guarantee permanent retention of critical architectural learnings.
- Safe `--dry-run` mode for CI/CD and inspection.

### 🔄 Template Injection Synchronizer (`scripts/sync_templates.py`)
- Eliminates "three-copy drift" by injecting canonical `templates/` into skill markdown files.
- Guarantees 1-to-1 parity between `skills/` and `.agents/skills/`.
- Enforced in CI via `--check` mode.

### 👥 Scale-Adaptive Agent Team & Compact Trio
- Pre-configured specialized agent roles in `.agents/team/`: `agent-dev-lead`, `agent-quality-guardian`, and `agent-github-steward`.
- Non-destructive role decommissioning and archival via `skills/decommission-meta-project/`.
- Emergency grounding and context recovery via `skills/ground-meta-project/`.

### 💖 Sponsorship & Donations
- GitHub Sponsor button configured via `.github/FUNDING.yml` (Boosty).
- Direct cryptocurrency donations via USDT TON network.

### 🧪 Comprehensive Integrity & Unit Test Suite
- 47 automated tests running in <10 seconds on Python 3.10, 3.11, 3.12, and 3.13 without third-party dependencies.

---

## 📦 What's Changed
- Full transition to English canonical specifications with a bilingual public facade ([README.md](../README.md) / [README.ru.md](../README.ru.md)).
- CI/CD workflow matrix testing across Python 3.10–3.13 in GitHub Actions.
- Complete changelog details in [CHANGELOG.md](../CHANGELOG.md).
