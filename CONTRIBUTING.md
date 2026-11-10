# Contributing Guide

[English](CONTRIBUTING.md) | [Русский](CONTRIBUTING.ru.md)

We welcome contributions to the agent environment framework for repositories (**Meta-Project**)!

This document outlines repository structure, rules for adding and modifying skills and templates, and the Pull Request submission process.

---

## 1. Architectural Principles

All changes and new skills must align with core architectural principles:
1. **No Context Bloat:** `AGENTS.md` contains only essential invariants, guiding principles (North Stars), stack declarations, and navigation maps. Dynamic logs and details are delegated to `.agents/project_knowledge/`.
2. **Read + Opportunistic Refresh:** When reading meta-knowledge slices, agents must verify them and update discovered gaps.
3. **Non-Destructive Update:** Initialization and synchronization scripts must preserve existing user data (`observations.md`, custom invariants) on repeated runs.
4. **Machine-Readable Glob Boundaries:** Responsibility zones in `boundaries.md` are defined via strict glob patterns.

---

## 2. Repository Structure

```text
meta-project/
├── .github/                       # Issue & PR templates, CI workflows
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/ci.yml
├── docs/                          # Architecture decisions, test reports, and roadmap
├── scripts/                       # Automation and boundary enforcement scripts
│   ├── check_boundaries.py
│   ├── compact_memory.py
│   └── sync_templates.py
├── skills/                        # Autonomous skills catalog
│   ├── decommission-meta-project/
│   ├── ground-meta-project/
│   ├── init-meta-project/
│   ├── manage-meta-project/
│   ├── record-observation/
│   └── sync-architecture/
├── templates/                     # Canonical deployment templates
│   ├── AGENTS.md
│   ├── project_knowledge/
│   │   ├── architecture.md
│   │   ├── boundaries.md
│   │   ├── observations.md
│   │   ├── tasks.md
│   │   └── weak_spots.md
│   └── team/
│       ├── profile.md
│       ├── notes.md
│       └── system_prompt.md
└── tests/                         # Automated structural and metadata integrity tests
```

---

## 3. Development and Standards

### Adding or Modifying Skills (`skills/`)
- Each skill is placed in a separate directory: `skills/<skill-name>/SKILL.md`.
- `SKILL.md` must include valid YAML frontmatter with `name` and `description` fields:
  ```markdown
  ---
  name: <skill-name>
  description: >-
    Clear description of when and why the skill is invoked.
  ---
  ```
- Mandatory sections in the skill body:
  - `## When to invoke skill` (or `## When to Invoke`)
  - `## Execution steps` (or `## Execution Steps`, step-by-step algorithm with checkpoints).

### Modifying Templates (`templates/`)
- `templates/AGENTS.md` and `templates/project_knowledge/*.md` must remain concise and language/framework-agnostic.
- Placeholders follow the `{{VARIABLE_NAME}}` format.

---

## 4. Local Verification (Testing)

Run local repository integrity tests before committing (zero external dependencies required):

```bash
python -m unittest discover -s tests -p "test_*.py"
```

All tests must pass with an `OK` status.

---

## 5. Pull Request Workflow

1. Create a topic branch from `main`:
   - `feat/<feature-name>` for new features and skills.
   - `fix/<fix-description>` for bug fixes in templates or skills.
   - `docs/<topic>` for documentation and reports.
2. Make atomic Conventional Commits:
   - `feat: add in-memory synthesis flush to init-meta-project`
   - `fix: correct glob pattern in boundaries template`
   - `docs: update empirical test report`
3. Ensure local tests pass.
4. Open a Pull Request targeting `main`, filling out the standard PR template.
5. Wait for GitHub Actions CI checks to pass.
