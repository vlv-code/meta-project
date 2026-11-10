---
name: ground-meta-project
description: >-
  Emergency grounding and recalibration skill: halts runaway edits, forces a zoom-out, re-reads AGENTS.md,
  the active role passport, boundaries.md, and architecture map, diagnoses context drift, and resets the agent into its operating corridor.
---

# Agent Grounding & Emergency Context Reset (Ground Meta-Project)

Emergency operational skill for immediately recovering context, stopping runaway or speculative code modifications, and anchoring the agent back to the repository's ground truth.

Use this skill whenever an agent loses context, exhibits model drift, loops across speculative fixes, breaches role boundaries, or when the user explicitly calls for a "zoom-out" / "grounding".

---

## When to invoke skill

* The user requests: "ground-meta-project", "recall-meta-project", "зум аут", "zoom out", "напоминалка", "заземлись", "вспомни роль", "прочти agents.md", "вернись в контекст", "калибровка роли", "ты зациклился".
* The agent detects 2 consecutive failed attempts to fix an issue in the same component (Circuit Breaker trigger).
* The agent realizes it has begun modifying files outside its assigned role boundaries or without understanding the underlying data flow.

---

## Execution steps

### Phase 1: Emergency Brake (Stop Code Modifications)
1. **Cease all writing operations:** Immediately stop editing, generating, or creating code files.
2. **Snapshot working directory:** Run `git status -s` and `git diff --stat` to inspect modified/untracked files.
3. **Establish baseline anchor:** Note which files were touched during the runaway iteration.

### Phase 2: Grounding in Canonical Sources (Re-Read Truth)
The agent MUST sequentially re-read the core repository knowledge slices:
1. **Root Passport (`AGENTS.md`):** Re-read Section 1 (North Stars, Invariants), Section 5 (Base Working Protocol), and Section 6 (Role Team).
2. **Responsibility Boundaries (`.agents/project_knowledge/boundaries.md`):** Re-read Green, Yellow, Red zones, and the **Default Deny (Black Zone)** rule.
3. **Current Role Passport & Cabinet:**
   - `.agents/team/<role_id>/profile.md`: authority limits, active stack skills, and telemetry.
   - `.agents/team/<role_id>/system_prompt.md`: behavioral rules, Circuit Breaker, Target State Audit.
   - `.agents/team/<role_id>/notes.md`: private accumulated context.
4. **Architecture Map (`.agents/project_knowledge/architecture.md`):** Re-read component dependencies and **End-to-End Data Flows**.
5. **Active Tasks (`.agents/project_knowledge/tasks.md`):** Re-read the original goal, active checklist, and pending blockers.

### Phase 3: Drift & Root Cause Diagnosis
Compare the current working directory diff against the canonical specifications:
1. **Boundary Drift:** Did the agent touch files outside its Green/Yellow zone without user confirmation or a Handoff Packet?
2. **Symptom Masking vs Root Cause:** Did the agent apply speculative regexes, temporary flags, or local `if` patches instead of identifying where data originates?
3. **Data Flow Tracing:** Is the complete lifecycle (`Origin ➔ Transport/API ➔ Persistence ➔ Consumer`) mapped?
4. **Contract Duplication:** Is the logic duplicated across multiple clients, languages, or layers?

### Phase 4: Grounding Report & Alignment
Deliver a concise, disciplined orientation report to the user without conversational fluff:

```markdown
### 🧭 Grounding Report (Forced Zoom-Out)
- **Active Role:** `{{ROLE_ID}}` (Current authority: Green: {{GREEN}}, Yellow: {{YELLOW}}, Red: {{RED}})
- **Repository Status:** {{GIT_STATUS_SUMMARY}} (Clean / N modified files)
- **Original User Objective:** <verbatim goal from user prompt or tasks.md>
- **Identified Drift & Root Cause:** <concise explanation of why the agent drifted or got stuck>
- **Data Flow Trace:** <Origin ➔ Transport ➔ Persistence ➔ Consumer>
- **Recovery Plan (Max 2–3 steps):**
  1. [Action 1: e.g. revert speculative edits / update boundaries]
  2. [Action 2: target root cause at source]
```
The agent MUST halt and wait for user confirmation before taking any further code action.
