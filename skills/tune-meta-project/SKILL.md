---
name: tune-meta-project
description: >-
  Calibrate and optimize the repository agent environment: analyze git friction and telemetry,
  adapt role topology, adjust boundary zones, and crystallize core project invariants.
---

# Repository Agent Environment Tuner (Tune Meta-Project)

Autonomous meta-reflection and calibration skill for evaluating how effectively agents operate within the repository, detecting friction between the framework and real code, and safely tuning the local instance.

The skill evaluates historical commit friction, role telemetry, and boundary exceptions, and produces a structured calibration plan covering team topology, boundary mappings, and core invariants with strict safeguards against context bloat.

---

## When to invoke skill

* The user requests: "tune-meta-project", "tune meta project", "калибровка обвязки", "прокачай инстанс", "устрани трение", "оптимизируй команду", "recalibrate environment".
* Repeated `Circuit Breaker` triggers or recurring bug regressions in the same files across recent commits.
* A single agent role is overloaded with heterogeneous technologies (e.g., Python backend + React UI + C++ bindings).
* Boundary Gate (`check_boundaries.py`) repeatedly reports unmapped paths during development.

---

## Execution steps

### Phase 1: Friction Diagnostics

1. **Commit History & Circuit Breaker Tracing:**
   - Execute `git log -n 15 --stat -p` to inspect recent commit dynamics.
   - Detect "hotspot" files touched 3+ times consecutively for bugfixes (symptom of surface patching rather than root-cause resolution).
   - Detect cross-component regression loops (fixes in Module A causing defects in Module B).
2. **Staging & Working Tree Hygiene:**
   - Execute `git status -s` to inspect untracked files, uncommitted temporary artifacts, or files falling outside `boundaries.md` mappings.
3. **Role Telemetry & Workload Balance:**
   - Inspect the `Role Invocation Log (Telemetry)` in all active `.agents/team/*/profile.md` files.
   - Detect role imbalances:
     * High invocation volume on a single role attempting to juggle multiple unrelated stacks.
     * Inactive roles that have not been invoked for >30 days.
4. **Knowledge Base Review:**
   - Read `.agents/project_knowledge/observations.md` and `weak_spots.md` to identify unresolved structural debt.

---

### Phase 2: Calibration Proposal (Advisory Gate)

The agent MUST NOT autonomously alter critical rules without user alignment. Synthesize a concise `Tuning Advisory Report` divided into 4 focus areas:

1. **Team Topology Recommendation:**
   - If workload overload or a new polyglot stack is identified ➔ Recommend invoking `manage-meta-project` to materialize a specialized role.
   - If a role is obsolete ➔ Recommend invoking `decommission-meta-project` to safely archive it.
   - *The `tune-meta-project` skill does not create or delete role folders directly; it delegates execution to dedicated skills.*
2. **Boundary Refinement (`boundaries.md`):**
   - Identify unmapped directories or files requiring explicit classification.
   - **Hard Invariant (Red Zone Protection):** Autonomous downgrading of paths from Red Zone to Yellow or Green Zone is strictly prohibited. Any change reducing Red Zone restrictions requires explicit human confirmation.
3. **Core Invariant Crystallization (Anti-Bloat Barrier):**
   - **Strict Limit:** Allowed to propose adding **at most 3 fundamental invariants** to Section 1 of `AGENTS.md` ("Principles and Architectural Orientations (North Stars)").
   - Each invariant MUST fit in exactly 1 concise sentence:
     `- **<Invariant Name>:** <1 concise sentence defining non-negotiable rule>.`
   - All tactical lessons, environment quirks, and temporary workarounds MUST be routed to `observations.md` and `weak_spots.md`, NOT `AGENTS.md`.
4. **System Prompt & Trigger Tuning:**
   - Suggest targeted additions to `.agents/team/*/system_prompt.md` to guide role behavior during recurring tasks.

---

### Phase 3: Safe Materialization & Marking (`local_repo_data`)

After receiving user confirmation, apply approved modifications using strict isolation tags:

1. **Format Standards for Local Adaptations:**
   - **For Markdown files (`.md`):**
     ```markdown
     <!-- local_repo_data:TAG -->
     ... adapted local rules / roles / boundaries ...
     <!-- /local_repo_data:TAG -->
     ```
   - **For YAML, Python, Shell, TOML files (`.yml`, `.yaml`, `.py`, `.sh`, `.toml`):**
     ```yaml
     # local_repo_data:TAG
     ... adapted local rules / roles / boundaries ...
     # /local_repo_data:TAG
     ```
2. **Apply Verified Updates:**
   - Insert marked blocks into `boundaries.md`, `system_prompt.md`, or `AGENTS.md`.
   - Never overwrite existing unrelated content.

---

### Phase 4: Post-Tuning Verification

1. **Verify Boundary Integrity:**
   - Run the Boundary Gate audit:
     ```bash
     python .agents/scripts/check_boundaries.py --audit-tree
     # Fallback: python scripts/check_boundaries.py --audit-tree
     ```
   - Ensure 100% path coverage is maintained.
2. **Run Integrity & Test Suites:**
   - Execute repository tests:
     ```bash
     python -m unittest discover -s tests -p "test_*.py" -v
     ```
3. **Log Telemetry & Observation:**
   - Record the tuning session in `.agents/project_knowledge/observations.md` under category `[orchestration]` using the `record-observation` skill.
   - Display a compact summary of calibrated components to the user.
