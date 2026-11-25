# Architecture Decision Records and Lessons Learned (Canonical English Reference)

This document provides the canonical English summary of core architectural decisions (ADRs) and key lessons learned from production incidents across the Meta-Project ecosystem.

For the full chronological history, historical proposals, Russian notes, and detailed audit trails, refer to the provenance document: [`docs/decisions_and_roadmap.md`](decisions_and_roadmap.md).

---

## 1. Core Architectural Decisions (ADR #14–#23, ADR #25)

### ADR #14: Unified Stdlib Core and Thin Harness Adapters
- **Context:** Maintaining separate repositories or writing disparate boundary checks for each agent harness (Claude Code, Cursor, Codex, Gemini CLI) leads to policy drift and security loopholes.
- **Decision:** All core policy enforcement, boundary gate classification (`classify_path`), repository inspection, and template validation are implemented in a single Zero-Dependency Python 3.10+ standard library core (`scripts/check_boundaries.py`, `scripts/inspect_meta_project.py`). External harnesses interact through thin, non-intrusive adapters (`hooks/` and plugin manifests) that translate harness events to the core.

### ADR #15: Read Permissions vs Write Restrictions (Red Zone Asymmetry)
- **Context:** Treating Red Zone paths as blanket-denied for all operations blinds models from reading essential schemas, policies (`boundaries.md`), licenses, and tests (`test_integrity.py`), provoking hallucinations and circular deadlocks under read gates.
- **Decision:** Boundary Gate restricts **mutating operations** (`Write`, `Edit`, delete, git commit) on Red Zone files without explicit maintainer approval. Read-only operations (`read_file`, `view`, `grep`, `glob`, `search`) bypass the boundary gate immediately, ensuring models possess accurate context while keeping mutation strictly protected.

### ADR #16: Decision Rationale & Tracing Link (Decision-RTL)
- **Context:** Micro-edits across sessions can subtly erode fundamental architectural invariants (North Stars) without triggering boundary alerts. Requiring bureaucratic ADRs for routine bugfixes creates excessive friction.
- **Decision:** The Decision-RTL protocol applies **strictly to architecturally significant changes**: modifications to project scope, North Stars, external dependencies, or component contracts. It mandates a concise 5-field record:
  - `Goal:` Technical or architectural problem addressed.
  - `Affected North Stars:` Project invariants impacted.
  - `Rationale:` Why this solution was chosen over alternatives.
  - `Risks & Trade-offs:` Compromises or constraints introduced.
  - `Verification Result & Impact:` Verified empirical outcome and test evidence.

### ADR #17: Safe Git Pre-Commit Hook Chain Execution
- **Context:** Naive installation of pre-commit hooks (`--install-hook`) completely overwrote existing developer hooks (linters, formatters, test triggers).
- **Decision:** The installer never overwrites `.git/hooks/pre-commit`. It appends the boundary gate check using chained execution (`|| exit 1`), preserving pre-existing developer workflows with safe idempotency guards.

### ADR #18: Default Closed Tooling and Explicit Opt-In
- **Context:** Relying on external third-party tools by default compromises the Zero-Dependency Core invariant, while a dogmatic ban prevents legitimate use of battle-tested utilities (Gitleaks, specialized linters).
- **Decision:** The ecosystem operates in a **Default Closed** posture: core tools run strictly on Python 3.10+ stdlib and Git. Third-party tools are permitted only when explicitly declared (opt-in) in repository specification (`AGENTS.md`) or directly requested by the operator. Liability for external tool failures rests with the target project/operator.

### ADR #19: Micro-Repository Scale, Tier 0 Duo & Adversarial TDD
- **Context:** Deploying multi-role agent teams (Trio or Granular) on small repositories (<3–5k LOC) creates human-handoff fatigue and bureaucratic overhead. However, unconstrained solo agents eliminate objective quality oversight.
- **Decision:** For compact projects, Meta-Project formalizes **Tier 0 (Micro)**:
  - **Solo:** Single agent under deterministic boundary gates.
  - **Tier 0 Duo:** `Developer` (implementation) ➔ `Inspector/Guardian` (combined independent test verification and git commit).
  In addition, TDD mandates an **Adversarial Testing Invariant**: agents must write negative/boundary checks, confirm failure (RED), and verify non-trivial behavior before transition to GREEN.

### ADR #20: Scenario Agreement and Formal Hand-off Reports
- **Context:** The handoff between initial inspection (`init-meta-project`) and team orchestration (`manage-meta-project`) previously relied on informal prompt text, risking state loss across sessions.
- **Decision:** Initialization operates in Phase 1 under **Survey-First Zero-Write**, agreeing on the adaptation scenario (`greenfield`, `brownfield_adopt`, `reinit_repair`, `multi_harness_join`) with the user before writing files. Results are recorded in standardized JSON reports (`.agents/reports/<installation_id>/init/<run_id>.json`). Orchestration (`manage-meta-project`) validates this report in Phase 0 (fail-closed if missing or stale).

### ADR #21: Managed Update & Component Contracts
- **Context:** Updating an installed agent environment required explicit release tags, lacked a formal component manifest, and risked clobbering local repo adaptations.
- **Decision:**
  - **SHA Pinning:** The update engine resolves any ref to an exact commit SHA and materializes components from upstream git or an integral offline cache. Releases are a convenience layer, not a prerequisite.
  - **Manifest vs Lock:** Canonical manifest (`templates/release_manifest.json`) defines all available components and dependencies. The local lock (`.agents/framework-lock.json`) tracks installed components and hashes.
  - **Preservation:** User adaptations marked with `local_repo_data:TAG` markers are preserved across updates.

### ADR #22: Shared Helpers Module via Manifest Requires
- **Context:** Code duplication across CLI scripts led to docstring drift, duplicated error envelope logic, and synchronized patching overhead.
- **Decision:** Common stdlib primitives (`_error_envelope`, `_utc_now_iso`, safe subprocess, file locking) are consolidated into a single component `scripts/_common.py`. Delivery is enforced through the manifest `requires: ["scripts/_common.py"]` dependency graph, eliminating drift while preserving clean standalone CLI execution.

### ADR #23: Derived Distribution Branch Model
- **Context:** Maintaining separate repositories for core framework and distribution created synchronization lag. Direct merges between development and distribution trees risked leaking development dogfooding (`.agents/`) into release branches.
- **Decision:** `dev` is the sole source of truth; `main` is a derived distribution branch mirrored automatically via `.github/workflows/sync-dist.yml` and `scripts/sync_dist_branch.py`. Distribution paths exclude `.agents/**`, internal plans, and development scratchpads. Divergent git history is intentional; metric of health is an empty content diff for distributed files.

### ADR #25: Role Duty Deconfliction & Cross-Harness Alignment
- **Context:** Multi-role deployments on complex or multi-harness repositories suffered from trigger collisions, redundant role invocations, and asymmetric role distribution across installations.
- **Decision:** `manage_reports.py` and `manage-meta-project` implement proactive duty deconfliction: detecting overlapping triggers and responsibilities between proposed and active roles. `inspect_meta_project.py` flags cross-harness installation asymmetries to ensure unified role governance.

---

## 2. Key Lessons Learned from Real-World Incidents

### A. Polyglot Monorepo Incident (§5)
- **Problem:** Deploying 5 narrow agent roles without a dispatcher led to human-routing fatigue; developers dumped all tasks into a single chat. Concurrently, lack of UI/UX competencies caused backend workers to write C++ luminance algorithms for web themes, while speculative fix loops created cascading regressions.
- **Lessons & Safeguards:**
  1. **Mandatory Intake Dispatcher:** When deploying >2 roles, an intake dispatcher (`agent-intake-dispatcher`) is mandatory to route tasks and shield operators from routing fatigue.
  2. **Zero Unmapped Dirs Rule:** Every top-level repository directory must map to Green, Yellow, or Red zone in `boundaries.md`; unmapped directories trigger fail-closed Default Deny.
  3. **Semantic Circuit Breaker:** Repeated failed attempts to fix a defect or new regressions in adjacent code require an immediate coding halt, zoom-out, and full data-flow tracing (`UI ➔ API ➔ Storage ➔ Client`).
  4. **Opportunistic Meta-Knowledge Refresh:** Agents must actively record newly discovered risks, quirks, and architectural flows in `.agents/project_knowledge/` rather than treating sessions as ephemeral.

### B. External Audit `38deed9` (§8)
- **Problem:** External security audit revealed that PR boundary checks could be bypassed if the PR touched policy files in the same branch, `manage --action create` bypassed intake validation, and git path parsers misbehaved on non-ASCII or quoted paths.
- **Lessons & Safeguards:**
  1. **Trusted Base SHA in CI:** CI must evaluate PR diffs and policies against the trusted target base commit (`github.base_ref` / `github.event.before`), preventing PR branches from relaxing boundary rules.
  2. **Multi-Harness Identity Enums:** Strict verification of actor identity (`<project>::<harness>::<installation>::<role>`) preventing spoofed credentials.
  3. **NUL-Delimited Path Parsing:** Git commands must use `-z` flags (`git ls-files -z`, `git diff -z`) to safely handle spaces, tabs, and non-ASCII characters without fragile quote stripping.

### C. Split-Runtime Silent-Failure Incident (§10)
- **Problem:** In a split runtime (local repository + remote build container), a packaging failure was masked by three layers of error absorption (`stdout/stderr` piped, swallowed in internal catch-all, missing failure branch in caller) and pre-filled placeholder files. An agent spent 10 turns chasing false hypotheses due to Action Bias and code-first confirmation bias, and laundered speculative guesses into facts via `tasks.md` and context compaction.
- **Lessons & Safeguards:**
  1. **Evidence-First Triage:** All unverified diagnoses must be labeled `HYPOTHESIS`. Fixes require a 1-step discriminator probe before touching code, enforced via `scripts/triage_incident.py` and `skills/triage-incident/`.
  2. **Two-Phase Tasks Registry:** Tasks in `tasks.md` distinguish `- [?] PROBE` (with mandatory `evidence:`) from `- [ ] FIX`, preventing speculative hypotheses from laundering into facts.
  3. **Fallback-Masking Audits:** Flow tracing must specifically audit error paths: `exit/stderr ➔ catch ➔ fallback/pre-fill ➔ verification log`.
