---
name: update-meta-project
description: >-
  Safely update meta-project canonical skills, templates, and scripts from upstream GitHub
  or local cache, preserving all local_repo_data adaptations and knowledge slices.
---

# Upstream Meta-Project Updater (Update Meta-Project)

Autonomous non-destructive skill for updating procedural skills, runtime scripts, and canonical templates from the upstream official `meta-project` framework into a target repository.

The skill features automatic dual-tier source resolution (GitHub Raw with timeout fallback to local cache), preserves all locally adapted blocks marked with `local_repo_data`, strictly shields project knowledge slices from overwrite, and performs post-update Boundary Gate validation.

---

## When to invoke skill

* The user requests: "update-meta-project", "update meta project", "обнови обвязку", "накати апдейты meta-project", "pull upstream skills", "upgrade meta framework".
* New skills, templates, or bugfixes were released in the official `meta-project` repository.
* Upstream utilities (`check_boundaries.py`, `compact_memory.py`) have received security or feature improvements.

---

## Execution steps

### Phase 1: Upstream Source Discovery & Resolution

1. **Dual-Tier Source Selection:**
   - **Tier 1 (Online Upstream — Primary):**
     Attempt to fetch latest manifest and skill files from the official upstream repository:
     `https://raw.githubusercontent.com/vlv-code/meta-project/main/`
     *Connection constraint:* Enforce a strict **3-second timeout** per request using pure standard library (`urllib.request`).
   - **Tier 2 (Offline Local Cache — Fallback):**
     If network access fails (timeout, `URLError`, offline sandbox, airgapped environment) or if invoked with `--offline`, seamlessly fallback to the local global skills cache:
     `~/.gemini/config/skills/` (Windows: `%USERPROFILE%\.gemini\config\skills\`).
2. **Determine Target Repository Context:**
   - If running inside the core `meta-project` repository itself: inform the user that upstream updates are managed via git pull/checkout on `main`, not via self-overwrite.
   - If running inside a target application repository: proceed with the Three-Way Safe Merge below.

---

### Phase 2: Pre-Flight Safety & Local Data Harvesting

1. **Working Tree Inspection:**
   - Run `git status -s` to ensure there are no uncommitted collisions in target update areas.
2. **Harvest Local Adaptations (`local_repo_data`):**
   - Scan all existing files in `.agents/skills/`, `.agents/scripts/`, `boundaries.md`, `system_prompt.md`, and `AGENTS.md`.
   - Extract and store in memory all customized blocks enclosed by:
     * **Markdown markers:**
       ```markdown
       <!-- local_repo_data:TAG -->
       ...
       <!-- /local_repo_data:TAG -->
       ```
     * **Code / Config markers:**
       ```yaml
       # local_repo_data:TAG
       ...
       # /local_repo_data:TAG
       ```
3. **Establish Inviolability Perimeter:**
   - The `.agents/project_knowledge/` directory (accumulated observations, weak spots, tasks, architecture history) and role private notes `.agents/team/*/notes.md` are **strictly protected from destructive overwrite**.
   - Only non-destructive opportunistic schema additions (e.g. adding a new standard column header) are permitted.

---

### Phase 3: Three-Way Safe Merge & Rollout

1. **Update Procedural Skills:**
   - Copy or download updated `SKILL.md` files into `.agents/skills/<skill>/SKILL.md`.
   - Restore any harvested `local_repo_data` blocks into their respective skills.
2. **Update Runtime Scripts:**
   - Copy or download updated zero-dependency scripts into `.agents/scripts/`:
     * `.agents/scripts/check_boundaries.py`
     * `.agents/scripts/compact_memory.py`
3. **Synchronize Canonical Templates & Passport:**
   - If upstream introduces new canonical invariants or sections, merge them into `boundaries.md` or `AGENTS.md`, immediately re-inserting preserved local blocks at their marked locations.

---

### Phase 4: Post-Update Validation

1. **Run Boundary Gate Audit:**
   - Verify that updated skills and scripts maintain 100% boundary mapping coverage:
     ```bash
     python .agents/scripts/check_boundaries.py --audit-tree
     # Fallback: python scripts/check_boundaries.py --audit-tree
     ```
2. **Execute Repository Test Suite:**
   - Verify that test assertions pass without regression:
     ```bash
     python -m unittest discover -s tests -p "test_*.py" -v
     ```
3. **Deliver Update Report:**
   Present a concise summary to the user:
   ```markdown
   ### 🚀 Update Report (Meta-Project Updater)
   - **Source:** Online Upstream (GitHub Raw) | Offline Local Cache
   - **Updated Skills:** [list of updated skills]
   - **Updated Scripts:** [list of updated scripts in .agents/scripts/]
   - **Preserved Adaptations:** N `local_repo_data` blocks preserved without loss
   - **Boundary Gate:** 100% path coverage verified
   - **Test Suite Status:** Passing
   ```
