---
name: update-meta-project
description: >-
  Safely update an installed meta-project framework (skills, templates, scripts)
  by driving the managed update engine scripts/update_meta_project.py:
  read-only check and plan, user alignment, atomic journaled apply, and
  restore; preserves local_repo_data adaptations and knowledge slices.
---

# Managed Framework Updater (Update Meta-Project)

Autonomous non-destructive skill for updating procedural skills, runtime scripts, and canonical templates in a target repository, driven by the SHA-pinned, atomic, crash-recoverable engine `scripts/update_meta_project.py` (subcommands: `check | plan | apply | restore`).

**Division of responsibility:** the engine owns resolution, merging, atomic replacement, the journal, the framework lock, and update reports. The AGENT owns context inspection, conflict/protected/needs-base analysis, user alignment, and post-update verification. The agent never copies framework files manually.

---

## When to invoke skill

* The user requests: "update-meta-project", "update meta project", "обнови обвязку", "накати апдейты meta-project", "pull upstream skills", "upgrade meta framework".
* New skills, templates, or bugfixes were released in the official `meta-project` repository.
* Upstream utilities (`check_boundaries.py`, `compact_memory.py`) have received security or feature improvements.

---

## Execution steps

### Phase 1: Pre-Flight — Context Inspection & Availability Check

1. **Inspect the execution context:**
   - `python scripts/inspect_meta_project.py --json --harness <harness_id> --installation <installation_id>` — diagnose repository state and schema compatibility. If the repository is in `INCOMPATIBLE_SCHEMA`, halt and report the required schema migration to the user.
   - `python scripts/verify_identity.py --check` — validate the registry and role bindings; resolve the qualified `actor_id` (`<project_id>::<harness_id>::<installation_id>::<role_id>`) required by `apply` later.
   - `git status -s` — ensure there are no uncommitted collisions in the target update areas.
2. **Read the framework lock** (`.agents/framework-lock.json`) if present: it records the actually-installed component subset, the pinned source/ref/commit SHA, the channel, and a sha256 per component. No lock means this installation was not produced by the managed engine — surface that to the user before proceeding.
3. **Check available updates THROUGH THE ENGINE** (strictly read-only, zero writes):
   ```bash
   python scripts/update_meta_project.py check --source <upstream_repo_path_or_url> --ref <ref>
   ```
   - `--ref` is a branch, tag, or full commit SHA (default `main`); the engine pins ONE exact SHA and materializes every component from that single revision (never mixing revisions).
   - State the source and its constraints to the user explicitly: a local repository path works directly; a remote URL requires a prior local `git fetch`.
   - Cache resolution (used when the origin is unavailable): `--cache-dir` flag > `META_PROJECT_CACHE` env var > OS cache path (`%LOCALAPPDATA%/meta-project/cache` on Windows, `~/.cache/meta-project` on POSIX). Only INTEGRAL single-revision bundles are accepted; a partial cache is refused.
   - Interpret the JSON output: `updates_available`, `drifted` (installed files differing from the lock record — local edits of unknown origin), `lock_present`, `diagnostics`. Exit code 1 means updates or drift were found (or the check failed — read stderr); exit code 0 means up to date.
4. **Framework repository itself:** when running inside the core `meta-project` repository, self-overwrite via the engine is PROHIBITED — the framework evolves through ordinary Git edits in its own repository. The update engine targets OTHER repositories with installed frameworks.

---

### Phase 2: Plan & User Alignment (read-only)

1. **Build the three-way merge plan:**
   ```bash
   python scripts/update_meta_project.py plan --source <...> --ref <...> [--repo-root .] [--components path1,path2] [--protect pattern1,pattern2]
   ```
   Zero-write. Default scope is the full component set declared in the source's `templates/release_manifest.json`; `--components` narrows it (dependencies from `requires` stay with their dependents); `--protect` overrides the default protect patterns.
2. **Analyze the plan — this analysis is the agent's job** (the engine only refuses; the agent explains):
   - `conflicts` — unmarked local modifications (outside `local_repo_data` markers) that the engine refuses to overwrite. Present each conflict (path + nature of the local change) to the user. HOW to resolve — add `local_repo_data` markers, merge manually, or skip the component — is the USER's decision; the agent never picks silently.
   - `protected` — components matching protect patterns (boundary gate, workflows, integrity tests, LICENSE, ...). Automated changes are refused: the Red-Zone sanction is an explicitly OPEN item, no sanctioned mechanism exists. Only the manual, user-confirmed path is available for these.
   - `needs_base` — locally modified components with no merge base matching the lock-recorded sha256 in the cache. Either supply an integral cache containing the base content, or the user explicitly gives up "safe merge" for those components (manual decision). The engine never claims a safe merge without a base.
3. **Agreement gate:** do NOT proceed to Phase 3 without the user's explicit approval of the plan (scope + per-conflict resolutions).

---

### Phase 3: Apply (engine-driven, atomic)

1. **After user approval:**
   ```bash
   python scripts/update_meta_project.py apply --source <...> --ref <...> --repo-root . --installation <installation_id> --actor <qualified_actor_id> [--cache-dir ...] [--components ...]
   ```
2. **What the engine guarantees** (no manual steps by the agent):
   - per-file atomic replacement from the single pinned SHA;
   - `local_repo_data`-marked blocks re-injected into merged files;
   - operation journal `.agents/update-journal.json` (before/after sha256 per file);
   - framework lock `.agents/framework-lock.json` rewritten atomically;
   - an `update` report recorded through the canonical report engine (`scripts/manage_reports.py`).
3. **Refusal handling:** `[APPLY-REFUSED]` for protected components, unresolved conflicts, or needs_base entries means ZERO writes were performed. Return to Phase 2, resolve with the user, retry or abandon.

---

### Phase 4: Verification & Recovery

1. **Boundary gate audit:**
   ```bash
   python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree
   ```
   100% boundary mapping coverage is required.
2. **Repository test suite:**
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
3. **Identity re-check:** `python scripts/verify_identity.py --check` — the update must not have altered role bindings or `.agents/meta-project.json`.
4. **Interrupted or failed operation:** restore ONLY the engine's own changes from the last operation journal:
   ```bash
   python scripts/update_meta_project.py restore --repo-root .
   ```
   Third-party edits made during the apply window are kept and reported, never clobbered.
5. **Status truthfulness (session reload):** an updated runtime file on disk is NOT the version loaded by the harness in the current session. After `apply`, instruct the user to reload/restart the session so the new skills/passport take effect, and do not claim updated behavior is already active.
6. **Deliver the update summary to the user:** pinned source + commit SHA, affected components, preserved adaptations (merged `local_repo_data` blocks), remaining manual actions (protected/conflicted components), journal and report locations.

---

## Background Notes (user-facing explanation only)

* **`local_repo_data` mechanism (implemented inside the engine; the agent does not harvest manually):** local adaptations wrapped in markers are preserved through updates:
  ```markdown
  <!-- local_repo_data:TAG -->
  ...locally customized content...
  <!-- /local_repo_data:TAG -->
  ```
  (in code/config files the same markers are written as `# local_repo_data:TAG` comments). The engine re-injects these blocks into merged content; any local change OUTSIDE such markers is an explicit conflict requiring a user decision.
* **Inviolability perimeter:** `.agents/project_knowledge/` slices and role private notes (`.agents/team/*/notes.md`) are never part of the managed component set and survive updates untouched.
* **Component composition:** the default update scope is the component set of `templates/release_manifest.json` at the pinned source; the project lock records the installed subset — a minimal scaffold is a valid installation.
