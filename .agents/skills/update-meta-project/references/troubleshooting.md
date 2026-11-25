# Managed Framework Update Troubleshooting & Diagnostics

## Overview

This reference provides exhaustive diagnostic guides, conflict resolution procedures, and recovery patterns for the SHA-pinned atomic update engine (`scripts/update_meta_project.py`).

---

## 1. Conflict Resolution Strategies (`conflicts`)

| Problem Signature | Root Cause | Safe Resolution Procedure |
| :--- | :--- | :--- |
| `conflicts: ["<path>"]` | Local edits exist outside `local_repo_data` markers. | **Option 1 (Adaptation):** Wrap local changes in `local_repo_data` markers (`<!-- local_repo_data:TAG -->` or `# local_repo_data:TAG`).<br>**Option 2 (Adoption):** If byte-identical to upstream, pass `--adopt-existing`.<br>**Option 3 (Manual Merge):** Inspect diff, apply upstream updates manually.<br>**Option 4 (Omission):** Exclude component via `--components` in plan. |
| `protected: ["<path>"]` | Component matches protect pattern or Red Zone in `boundaries.md`. | Automated updates are strictly forbidden. Perform manual review and operator-confirmed diff apply. |
| `needs_base: ["<path>"]` | Missing merge base matching lock-recorded SHA in cache and history. | Run `git fetch` to pull upstream history, or supply integral cache with base content via `--cache-dir`. Never force merge without base. |

---

## 2. Marker Syntax by File Type (`local_repo_data`)

The update engine automatically preserves blocks enclosed in valid `local_repo_data` tags across 3-way merges and fast-forward updates:

- **Markdown / HTML / XML (`.md`, `.html`, `.xml`):**
  ```markdown
  <!-- local_repo_data:CUSTOM_INVARIANTS -->
  Project-specific rules and local adaptations.
  <!-- /local_repo_data:CUSTOM_INVARIANTS -->
  ```
- **Python / YAML / Shell / Config (`.py`, `.yml`, `.yaml`, `.sh`, `.cfg`, `.ini`):**
  ```python
  # local_repo_data:LOCAL_SETTINGS
  custom_config = True
  # /local_repo_data:LOCAL_SETTINGS
  ```

---

## 3. Runtime Engine Contention & Lock Diagnostics

### `[ENGINE-BUSY]` / `ENGINE_BUSY`
- **Cause:** Another `apply` or `restore` operation is running concurrently, or a prior operation crashed leaving `.agents/update-engine.lock`.
- **Handling:**
  1. Verify if an active process is holding the lock.
  2. If the previous process crashed, inspect `.agents/update-journal.json`.
  3. If safe, remove the stale `.agents/update-engine.lock` and re-run.

### Containment Perimeter Violations
- **Cause:** Manifest, lock, or plan references absolute paths (`C:/...`, `/...`), paths with `..`, or symlinks escaping repository boundaries.
- **Handling:** Zero writes performed. Fix relative path specifications to stay within repository root.

### Cache Verification Failures (`cache-manifest.json`)
- **Cause:** Tampered or corrupted bundle files, or bundle sealed for a different commit SHA.
- **Handling:** Refuse cache. Re-fetch clean bundle from origin.

---

## 4. Crash Recovery and Rollback Protocol

If an update is interrupted or causes regressions, execute atomic restoration:
```bash
python scripts/update_meta_project.py restore --repo-root .
```
- Restores all modified files to pre-update state from `.agents/update-journal.json`.
- Preserves third-party edits made during the update window.
- Updates the update report status to `"restored"`.

---

## 5. Reference Loading Contract & Fallback

If `references/troubleshooting.md` is absent (`[MISSING_RESOURCE] references/troubleshooting.md`), fall back to standard engine failure codes on stderr or consult the core guidelines in `skills/update-meta-project/SKILL.md`.
