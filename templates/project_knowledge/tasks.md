# Current and Active Project Tasks

Coordination registry for tasks and progress between agents and the user.
Before starting work, every agent MUST review the active task list and, if necessary, log subtasks with their authorship.

---

## Team Task Management Rules
1. **Authorship and Timestamp Logging:** Every task and subtask is logged with qualified actor attribution in the format:
   `- [ ] [<actor_id> @ YYYY-MM-DD HH:MM] Task description`
2. **Delegation (Out-of-Scope Handoff):** If a subtask exceeds the current agent's boundaries, it is logged in "Delegated Subtasks" with explicit sender and recipient actors (`[<from_actor_id> -> <to_actor_id> @ YYYY-MM-DD HH:MM]`).
3. **Step Completion:** Upon completing a task, change the status to `- [x]` and optionally append a 1-line summary result.
4. **Sanctity of Other Agents' Notes:** Agents are prohibited from deleting or modifying entries written by others. Editing is restricted to own entries (status, details). Upon finding an error in another agent's note, present the conflict description with arguments to the user.

---

## Active Objective
- **Task:** {{CURRENT_OBJECTIVE}} (Brief summary of the current objective)
- **Initiator:** {{INITIATOR}} (User / Agent Role)
- **Start Date:** {{CURRENT_DATE}}

---

## Execution Plan and Checklist
- [ ] [{{ACTOR_ID}} @ {{CURRENT_DATE}}] Step 1: Preparation and context gathering
- [ ] [{{ACTOR_ID}} @ {{CURRENT_DATE}}] Step 2: Implementing minimal changes
- [ ] [{{ACTOR_ID}} @ {{CURRENT_DATE}}] Step 3: Verification with tests and linters
- [ ] [{{ACTOR_ID}} @ {{CURRENT_DATE}}] Step 4: Recording observations and task closure

---

## Delegated Subtasks and Blockers
- *(Example)* `[{{FROM_ACTOR_ID}} -> {{TO_ACTOR_ID}} @ {{CURRENT_DATE}}]`: HTTPS configuration required in nginx for secure cookies.
