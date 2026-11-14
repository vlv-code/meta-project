# RED Baseline: External Audit Regressions (base 4274bbd)

> [!NOTE]
> **Outcome (2026-11-15, Stage 2 remediation complete):** all 39 RED
> reproductions and the rewritten cycle test are GREEN; full suite
> **161/161 OK**, boundary coverage 100% (127 files), template parity 0
> drift. The tables below preserve the ORIGINAL pre-fix results as required
> by the audit (reproduction → change → verification). Code-level stages
> implemented: S2 (gate/CI/CODEOWNERS), S3 (identity), S4 (inspector),
> S5 (intake/storage), S8 (hook dispatcher), S9 (memory/sync), S6-docs
> (--path flag). Remaining non-code scope: skills content §6/§7, §10 live
> acceptance (Guardian), README badge & branch-protection report (Steward).

Preserved original verification results for the audit remediation (Stage 1:
Reproduction Fixation). Each failing test below reproduces a confirmed defect
on the pre-fix codebase and asserts the required post-fix behavior.
Remediation stages must turn them GREEN without weakening assertions.

## Environment

- Base: commit `4274bbd` + uncommitted Step 61 working tree
  (`scripts/sync_templates.py` `--global-skills`, +1 test) and local `zc-main`
  activation. One HEAD does not describe the uncommitted tree; this matches
  the auditor's note (118 committed vs 119 worktree tests).
- Run: `python -m unittest tests.test_audit_regressions -v`
- Full: `python -m unittest discover -s tests -p "test_*.py"`
- Host: Windows, Python 3.14.4, Git Bash.
- Results: suite `tests/test_audit_regressions.py` — **42 tests, 39 RED, 3
  lock-in pass**. Full repo suite — **161 tests, 40 failures** (39 RED + the
  rewritten cycle test, RED until Stage 5). All 119 pre-existing tests remain
  green; no regressions introduced.

## RED inventory (test → audit § → fixing stage)

Stage codes: S2 gate+CI, S3 identity, S4 inspector, S5 report intake/storage,
S6 skills/docs, S8 hook installer, S9 memory/sync.

### Boundary Gate (§2 → S2, Red Zone files)

| Test | Defect reproduced |
|---|---|
| `test_invalid_diff_revision_fails_closed` | unresolvable `--diff` revision falls back to empty `git status` and exits 0 "Clean" |
| `test_rename_red_to_green_checks_old_path` | rename `LICENSE → docs/license.md` passes: only new (Green) path diffed, old Red path never checked |
| `test_repo_root_governs_git_operations` | `--repo-root` ignored by git diff/status (wrong repository audited from unrelated cwd) |
| `test_status_fallback_parsing_keeps_rename_old_path` | fallback parser slices the NUL-separated rename old-path record as `XY PATH` (mangles `LICENSE` → `ENSE`) |

### Identity registry (§3 → S3)

| Test | Defect reproduced |
|---|---|
| `test_harness_substitution_in_actor_id_rejected` | actor_id harness component never matched against installation `harness_id` |
| `test_schema_version_value_validated` | `schema_version` presence checked, value not validated (`99.0.0` accepted) |
| `test_installation_status_enum_validated` | installation status enum not validated |
| `test_binding_status_enum_validated` | binding status enum not validated |
| `test_malformed_root_json_yields_structured_errors` | non-dict registry root raises AttributeError traceback instead of structured errors |
| `test_registry_without_roles_is_valid_base_installation` | team-less base registry rejected → forces fictitious roles (no bootstrap initiator concept) |
| `test_planned_binding_is_not_admitted_as_active_identity` | `verify_identity --actor` admits a planned binding as a valid identity (lookup vs admission not separated) |
| `test_profile_harness_mismatch_with_binding_detected` | profile frontmatter `harness_id` never matched against the binding |

### Inspector (§4 → S4)

| Test | Defect reproduced |
|---|---|
| `test_missing_passport_is_not_healthy_registered` | missing mandatory `AGENTS.md` still reports `HEALTHY_REGISTERED` instead of `PARTIAL_CORRUPTED` with a precise list |
| `test_unknown_runtime_context_reports_indeterminacy` | unknown runtime context silently resolved via any active installation |
| `test_roles_capability_scoped_to_target_installation` | Antigravity role profiles reported as role availability for a ZCode installation |
| `test_worktree_git_toplevel_reports_main_working_tree` | `git_toplevel` for a linked worktree resolves into `.git/worktrees` metadata |

### Report intake & storage (§5 → S5)

| Test | Defect reproduced |
|---|---|
| `test_foreign_project_report_rejected_by_intake` | no intake engine exists; format validation never decides admission |
| `test_blocked_report_rejected_by_intake` | blocked report cannot be refused (no admission control) |
| `test_awaiting_decision_report_rejected_by_intake` | awaiting_decision report cannot be refused |
| `test_missing_report_file_rejected_by_intake` | missing report file cannot be refused |
| `test_corrupted_report_file_rejected_by_intake` | corrupted JSON cannot be refused with structured diagnostics |
| `test_installation_or_harness_mismatch_rejected_by_intake` | report for a different installation/harness cannot be refused |
| `test_stale_uncommitted_inputs_rejected_by_intake` | uncommitted essential-input changes invisible to intake |
| `test_create_does_not_stamp_default_project_id` | CLI default `--project-id="vlv-code/meta-project"` stamped into foreign projects |
| `test_completed_with_empty_scenario_rejected` | `completed` report with empty scenario passes validation |
| `test_repo_copy_reads_its_own_reports` | absolute path in `latest.json` pointer → repo copy reads the ORIGINAL's report (cross-contamination) |
| `test_existing_run_id_cannot_be_overwritten` | saving an existing `run_id` silently overwrites |
| `test_latest_means_latest_attempt` | corrupted latest attempt silently skipped, older valid report returned |
| `test_staleness_detects_uncommitted_input_changes` | staleness compares only commit SHA; uncommitted boundaries change undetected |

### Git hook installer (§8 → S8, Red Zone file)

| Test | Defect reproduced |
|---|---|
| `test_existing_hook_exit_zero_does_not_stop_gate` | append-chaining: prior hook `exit 0` terminates the script before the boundary check runs |
| `test_worktree_installation_supported` | worktree `.git` file → "Not a git repository" failure |
| `test_external_hook_manager_conflict_reported` | husky-managed hook overwritten/extended with false "installed successfully" |

### Memory & sync (§9 → S9)

| Test | Defect reproduced |
|---|---|
| `test_row_inserted_inside_table_before_trailing_text` | observation appended at end of file, outside the table |
| `test_dry_run_creates_no_lock_file` | `--dry-run` still creates `.lock` |
| `test_archive_note_not_duplicated` | repeated compactions stack duplicate archive NOTE blocks (live precedent: 7× in production repo) |
| `test_record_compact_record_compact_cycle` | rows recorded after compaction land beyond the NOTE block, invisible to future compactions |
| `test_exact_duplicate_event_suppressed` | exact duplicate events recorded twice (documented suppression not implemented) |
| `test_write_with_missing_canonical_template_fails` | `sync_templates --write` exits 0 and prints `[OK]` for unrecoverable missing-template errors |

### Canonical docs (§6 → S6)

| Test | Defect reproduced |
|---|---|
| `test_record_obs_examples_use_supported_flags` | `AGENTS.md` + `templates/AGENTS.md` reference nonexistent `--component` flag (actual CLI: `--path`) |

## Lock-ins (already correct, protected from regressions)

- `test_existing_hook_failure_propagates` — failing existing hook preserves denial.
- `test_reinstall_is_idempotent` — reinstall does not duplicate dispatcher block.
- `test_write_then_check_leaves_zero_drift` — after successful `--write`, `--check` is clean.

## Related RED outside this suite

- `tests/test_report_and_manage_cycle.py::test_manage_rejects_foreign_or_incompatible_report`
  — rewritten per audit §1: the self-implemented "simulation" check was
  replaced with a call to the real intake engine; RED until Stage 5.

## Exclusions (per corrected triage, not defects)

- CODEOWNERS `*boundaries.md` depth matching — pattern is correct per
  CODEOWNERS/gitignore rules; separate owner-rights verification required.
- Inspector read-only zero-write invariant — already implemented and covered.
- NUL separation itself — already used; only fallback parsing and rename
  coverage are defective (covered above).
- manage-own-changes staleness — Stage 5 design requirement, not a reproduced
  defect.
- Physical loss of observation rows — not asserted; rows become invisible to
  compaction (covered by the cycle test).
