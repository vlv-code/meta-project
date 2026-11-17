# Primitives Vocabulary (Astra)

Recurring agent operations of this framework, each mapped to its working
implementation. **Primitives are NAMES for existing implementations — nothing
here is a new mechanism.** Skills reference these implementations (direct
script invocation or import) and never re-implement them; when a skill needs
one of these operations, it routes to the owning script/function below.

Every referenced symbol is import-level and locked by
`tests/test_gwave_d.py`. Documentation only — this page introduces no
behavior.

---

## 1. Deterministic Survey

- **Implementation:** `scripts/inspect_meta_project.py::inspect_repository`
  (CLI: `python scripts/inspect_meta_project.py --json [--read-only] [--harness <h> --installation <i>]`)
- **Contract:** read-only repository survey returning one structured JSON
  diagnostic — canonical repository state classification (NONE,
  FOREIGN_RULES, HEALTHY_REGISTERED, HEALTHY_NEW_HARNESS, CONTEXT_UNRESOLVED,
  LEGACY_UNREGISTERED, PARTIAL_CORRUPTED, INCOMPATIBLE_SCHEMA), 5-dimension
  capability matrix, worktree/subproject/foreign-instruction detection —
  with zero disk writes, zero lock files, and zero telemetry rows.
- **Routed by:** `init-meta-project` (survey step), `manage-meta-project`
  (Phase 0 survey), `tune-meta-project` (Phase 1 configuration survey),
  `update-meta-project` (state/schema diagnosis).

## 2. Identity Admission

- **Implementation:** `scripts/verify_identity.py::evaluate_actor_admission`
  (CLI parity check: `python scripts/verify_identity.py --check`)
- **Contract:** separate admission control for a located registry binding —
  the actor may act only when both the binding and its installation are
  `active`; returns `None` when admitted, otherwise a human-readable denial
  reason (a successful lookup is not an admission). Also imported by
  `manage_reports.py` and `update_meta_project.py` for fail-closed admission.
- **Routed by:** `decommission-meta-project` (post-change integrity
  verification), `ground-meta-project` (identity recovery),
  `init-meta-project`, `tune-meta-project` (Phase 1 survey),
  `update-meta-project` (admission before framework changes).

## 3. Report Intake

- **Implementation:** `scripts/manage_reports.py::evaluate_manage_intake`
  (CLI: fail-closed inside `python scripts/manage_reports.py manage --action create ...`)
- **Contract:** admission gate for the init → manage contract — separates
  format validation from admission (a blocked report can be a correct
  document and is still refused); checks registry
  project/installation/harness match, admitted actor, existing init run,
  freshness of essential inputs; a registry change since the init report is
  admitted only when exactly covered by `declared_changes`. Returns intake
  errors; an empty list admits the operation.
- **Routed by:** `init-meta-project` (repeat-run and manage-admission
  semantics), `manage-meta-project` (Machine-Enforced Intake in Phase 0),
  `update-meta-project` (canonical report engine requirement).

## 4. Observation Recording

- **Implementation:** `scripts/record_obs.py::record_observation`
  (CLI: `python scripts/record_obs.py --category <cat> --path <path> --issue <text> --solution <text> [--actor-id <actor_id>]`)
- **Contract:** validates, formats, and atomically inserts one observation
  row into `observations.md` under a cross-platform file lock; recording the
  exact same event (same date, category, path, issue, solution, pin) is a
  duplicate-suppressed no-op; returns the table row.
- **Routed by:** `record-observation` (canonical procedure — the only writer
  path); `init-meta-project` deploys the utility and routes its own logging
  through the `record-observation` skill.
