---
name: record-observation
description: >-
  Use this skill to record an undocumented bug, environment quirk, runtime edge-case,
  or non-obvious solution into the repository's `.agents/project_knowledge/observations.md` table.
---

# Record Observation in Repository Knowledge Base

This skill ensures disciplined, standardized addition of entries to the project observation registry without corrupting document structure or causing context bloat.

---

## When to invoke skill

* The agent or user encounters an unexpected environment, build, or runtime error that was successfully resolved.
* A critical behavioral nuance of a third-party library or internal API is discovered that is not documented in official project documentation.
* The user instructs: "record observation", "add to knowledge base", "log gotcha", "record finding".

---

## Execution steps

1. **Check file presence:**  
   Verify that `.agents/project_knowledge/observations.md` exists in the current repository. If missing, first create it using the 5-column table template (`Date`, `Category`, `Component / Path`, `Observation / Issue`, `Solution / Workaround`).

2. **Check for duplicates:**  
   Read the last 20 lines of `.agents/project_knowledge/observations.md`. Ensure that a similar observation has not already been logged. If an entry already exists but needs clarification, update the existing line.

3. **Format entry:**  
   Format the observation strictly as a single Markdown table line:
   ```markdown
   | YYYY-MM-DD | [<category>] | <Path_or_component> | <Brief issue summary/fact> | <Solution or workaround> |
   ```
   * Date: current date in ISO format (e.g., `2026-11-07`).
   * Category: one of the standardized tags: `[build]`, `[runtime]`, `[deps]`, `[db]`, `[api]`, `[test]`, `[env]`, `[ci]`, `[boundaries]`, `[orchestration]`, `[decommission]`, `[incident]`, `[init]`, or an explicit project domain tag (e.g. `[theme]`).
   * Permanent Invariant Tag `[pin]`: For fundamental architectural rules or environment invariants that must never be rotated into archive by `compact_memory.py`, append `[pin]` to the Category tag (e.g. `[env][pin]` or `[boundaries][pin]`). Pinned rows are permanently preserved in the primary table during compaction.
   * Conciseness: problem summary and solution must fit in a single sentence without line breaks.

4. **Atomic write:**  
   Append the row to the end of the table in `.agents/project_knowledge/observations.md`.

5. **Registry size control (Compaction Protocol):**  
   If the number of rows in the table exceeds 20–30, invoke the automated compaction utility:
   ```bash
   python scripts/compact_memory.py --max-observations 20 --keep-observations 10
   ```
   This automatically rotates older records into `.agents/project_knowledge/archive/observations_YYYYMM.md`, keeping the primary file lightweight and preventing context rot.
   *(If `scripts/compact_memory.py` is not present, manually archive older resolved records into `.agents/project_knowledge/archive/observations_YYYYMM.md`)*.
