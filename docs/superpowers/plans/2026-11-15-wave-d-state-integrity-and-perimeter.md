# Wave D — State Integrity & Perimeter (update engine, manage admission, scaffold hygiene)

**Date:** 2026-11-15
**Author:** agent-dev-lead (dispatcher)
**Baseline:** `a23f3c4` (tree clean except knowledge/telemetry records of Steps 73–74 — Yellow/Green, workers MUST NOT touch them)
**Sources:** external auditor report #2 (items 1–5), E2E consumer run findings (Step 73: D6, D7, layout mismatch, friction cluster, D8), deferred backlog (D2, D4, D5).
**Goal:** close all 14 open positions in one wave; the update engine must never lose state (adaptations, lock/journal coherence, approved-plan integrity) and must never operate outside the identity/boundary perimeter.

---

## 1. Global Invariants (every worker)

1. **Zero-dependency:** Python 3.10+ stdlib + Git only.
2. **RED-first TDD:** every task writes the failing test FIRST (adversarial boundary cases included), confirms RED with exact output, then implements to GREEN. Never edit/weaken a test to pass — a contradiction is reported, not patched.
3. **Scope discipline:** touch ONLY the files listed in your lane. Never write to `.agents/project_knowledge/*`, role profiles, telemetry, `tasks.md`; never commit; never run `sync_templates.py --write` (dispatcher does sync at integration).
4. **Own test file only:** each lane creates its own `tests/test_dwave_<lane>.py`. The ONLY pre-existing test file a lane may modify is the one explicitly listed in its spec (E1 owns `tests/test_update_meta_project.py`).
5. **Verification:** run your lane's exact commands and report actual output. Full battery (`python -m unittest discover -s tests -p "test_*.py"`) must be green at lane close.
6. **Baseline check:** before starting, `git status --porcelain` must show only the 4 known knowledge/telemetry files (`observations.md`, `tasks.md`, `weak_spots.md`, `agent-dev-lead-zc/profile.md`). Anything else — STOP and report.

---

## 2. Parallel Execution Model

Two flights. Flight 1 runs four lanes fully in parallel (disjoint files + disjoint test files). Flight 2 is a single engine lane strictly after E1 (same source file). Dispatcher (dev-lead) integrates between flights.

### File Ownership Matrix

| File | M | B | R | K | E1 | E2 |
|---|---|---|---|---|---|---|
| `scripts/update_meta_project.py` | – | – | – | – | **✓** | **✓** (after E1) |
| `tests/test_update_meta_project.py` | – | – | – | – | **✓** | extend only |
| `scripts/manage_reports.py` | **✓** | – | – | – | – | – |
| `skills/manage-meta-project/SKILL.md` | **✓** | – | – | – | – | – |
| `scripts/check_boundaries.py` | – | **✓** | – | – | – | – |
| `skills/init-meta-project/SKILL.md` | – | **✓** | – | – | – | – |
| `scripts/record_obs.py` | – | – | **✓** | – | – | – |
| `skills/record-observation/SKILL.md` | – | – | **✓** | – | – | – |
| `templates/release_manifest.json` | – | – | – | **✓** | – | – |
| `skills/update-meta-project/SKILL.md` | – | – | – | – | – | **✓** |
| `tests/test_dwave_<lane>.py` (new) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Flight 1 (parallel):** M, B, R, K, E1
**Flight 2 (sequential, after E1+K merged):** E2
**Integration (dispatcher only):** mirrors sync (`sync_templates.py --check`), canon test run, full battery, RED-discipline replay.

---

## 3. Lane E1 — Engine State Integrity (Flight 1, core lane)

**Files:** `scripts/update_meta_project.py`, `tests/test_update_meta_project.py`, new `tests/test_dwave_e1.py`.
**Closes:** auditor п.1 + D6, п.2, п.4.

### T1.1 — Lock v2: base vs installed (п.1 + D6, CRITICAL)
RED tests first:
- `test_second_update_preserves_markers`: install component → add marked block → apply upstream v2 (marker preserved) → apply upstream v3 (different bytes) → **markers still present** (currently FAILS: plain overwrite).
- `test_lock_records_base_and_installed`: after a merge-apply, lock entry carries BOTH `base_sha256` (pinned upstream bytes) and `installed_sha256` (on-disk bytes).
- `test_same_pin_base_available`: local drift vs lock on the SAME pin resolves without `needs_base` (D6): the pinned bundle itself is a valid base candidate when `pin.sha == lock.base_sha`.
Implementation:
- Lock component schema v2: `{"path", "kind", "base_sha256", "installed_sha256", "target"}` (`target` optional — reserved for E2 layout mapping; default = manifest path). Backward compat: v1 entries (`sha256`) are read as `base_sha256 = installed_sha256 = sha256`.
- `_collect_base_candidates`: drop the blanket `exclude_sha`; acceptance stays hash-verified against the lock record (a candidate whose sha256 matches `base_sha256` is valid regardless of which cache dir provided it).
- `plan_updates` fast-forward branch (`current == installed_sha`): NEVER plain-overwrite a file whose local content contains marker blocks — extract local blocks and re-inject into `new_bytes` (equivalent to merge with empty base delta); plain overwrite remains only for files with no markers.
- Journal/lock coherence: lock write is itself journaled (see T1.2).

### T1.2 — Restore rolls back files AND lock (п.2)
RED test first:
- `test_restore_returns_coherent_state`: successful apply → `restore` → files AND `.agents/framework-lock.json` revert to pre-apply content; a subsequent `check` reports `up_to_date` (currently FAILS: lock keeps new hashes → drift).
- Fix the existing restore test gap: the restore test must compare the lock too (auditor: "текущий тест восстановления исключает lock из сравнения").
Implementation: `apply_updates` appends a journal entry for the lock file (`before_b64` = previous lock bytes or None, `after_b64` = new) BEFORE writing it; `restore_updates` handles it like any other entry. `write_lock_atomic` keeps atomicity.

### T1.3 — Plan pins what apply may do (п.4, TOCTOU)
RED tests first:
- `test_apply_refuses_when_upstream_moved`: `plan --ref <branch>` → upstream branch moves → `apply --ref <branch>` with the approved plan must REFUSE (`plan/source revision changed: re-plan required`), not silently apply a different SHA.
- `test_apply_refuses_when_target_moved`: between plan and (library) `apply_updates`, a target file is edited → apply refuses with `target state changed since plan: <path>` and performs ZERO writes.
Implementation:
- Plan result carries `pin` (source + commit_sha) and per-action `expected_before_sha256` (target state at plan time: None for creates).
- `apply_updates(plan, ...)`: verifies pin.sha equality with re-resolved source when CLI re-resolves, and `expected_before_sha256` against disk before each write; any mismatch → `ApplyError`, zero writes (all-or-nothing preserved).
- CLI `apply`: accepts the plan from a `--plan-file` (new optional flag; when absent, re-plans internally and treats the fresh plan as approved — but re-plan output is shown with a `[RE-PLANNED]` notice) — user-approved plan file path is recorded in the update report.

**Acceptance (lane E1):** all new tests RED→GREEN; full battery green; `python scripts/update_meta_project.py check` on the framework repo still `up_to_date` semantics for itself (self-check unchanged).

---

## 4. Lane M — Manage Admission & Reports (Flight 1, parallel)

**Files:** `scripts/manage_reports.py`, `skills/manage-meta-project/SKILL.md`, new `tests/test_dwave_m.py`.
**Closes:** auditor п.3, friction (1) tune CLI, bootstrap documentation.

### T2.1 — Pre-op admission + declared-delta verification (п.3)
RED tests first:
- `test_manage_allows_declared_registry_change`: fresh init report → registry change EXACTLY equal to the report's declared `changes` → manage create succeeds (currently FAILS: `stale report: essential input changed`).
- `test_manage_rejects_undeclared_registry_change`: registry change NOT covered by declared changes → refused with explicit diff listing.
- `test_manage_rejects_unrelated_slice_change`: boundaries.md changed since init report → still refused (staleness for non-declared inputs stays).
Implementation:
- `evaluate_manage_intake` v2: registry/boundaries/AGENTS fingerprints split into (a) pre-checks that must be fresh (boundaries.md, AGENTS.md, project/installation/harness match, admitted actor, init run exists+completed) and (b) the registry delta, which must be EXACTLY covered by the report's declared `changes` (add_role/disable/archive with paths/ids). Report schema gains mandatory `changes[]` (already produced by the E2E flow — formalize).
- Commit-HEAD freshness: replaced by "init report not superseded" (a newer init run exists → refuse with pointer), removing the commit-moved false positive while keeping content freshness.

### T2.2 — `tune` CLI subcommand (friction 1)
RED test: `python scripts/manage_reports.py tune --action create ...` (mirroring init/manage flags + `--data-file` with `proposals[]`) creates a valid tune report via `save_report`; `latest --type tune` returns it. Currently FAILS (invalid choice).

### T2.3 — Bootstrap path documentation
`skills/manage-meta-project/SKILL.md`: new "Phase 0.5 — First-Role Bootstrap (roles: {})" section: the documented path is (1) init report with the initializing operator actor (identity-less repos record the invoking harness agent; admission not yet applicable), (2) manage adds roles + bindings per Phase 5, (3) manage report declares those changes (now allowed by T2.1). Mirror-sync note: embedded templates unchanged (skill text only).

**Acceptance:** new tests RED→GREEN; existing `test_manage_create_cli_enforces_intake` and intake tests stay green (semantics only widened for declared deltas).

---

## 5. Lane B — Boundary Gate & Scaffold Hygiene (Flight 1, parallel)

**Files:** `scripts/check_boundaries.py`, `skills/init-meta-project/SKILL.md`, new `tests/test_dwave_b.py`.
**Closes:** friction (2) hook override, (3) scaffold hygiene.

### T3.1 — Scoped hook override (friction 2)
RED tests first:
- Hook dispatcher honors `META_PROJECT_ALLOW_RED_ZONE=1`: red-zone staged files pass with a `[ALLOWED]` notice naming each file (default unchanged: refusal).
- Without the env var: refusal identical to current.
Implementation: dispatcher template in `install_git_hook` passes the env through to `python scripts/check_boundaries.py --staged`; `check_boundaries` staged mode reads the env var (fail-closed default). `--allow-red-zone` CLI flag semantics unchanged.

### T3.2 — Drift detector excludes bytecode caches (friction 3a)
RED test: staged `**/__pycache__/*.pyc` produces NO architecture-drift warning (currently FAILS). Implementation: drift classifier skips `__pycache__` and `*.pyc` paths (consistent with init's Zero Unmapped Dirs filter list).

### T3.3 — Scaffold ships baseline `.gitignore` (friction 3b)
`skills/init-meta-project/SKILL.md` Pass 1 step 5 (or Flush Step A): scaffold writes `.gitignore` (append-if-absent, never overwrite) with `__pycache__/`, `*.pyc`, `*.lock` + a note mapping it Green (hygiene paths). RED-check: canon/doc test asserts the string `.gitignore` appears in the init skill's scaffold steps (lock-in against regression).

**Acceptance:** hook behavior tests (2 existing POSIX-shell tests) stay green; full battery green.

---

## 6. Lane R — record_obs Hygiene (Flight 1, parallel)

**Files:** `scripts/record_obs.py`, `skills/record-observation/SKILL.md`, new `tests/test_dwave_r.py`.
**Closes:** D8 category drift, persistent `.lock` leftover.

### T4.1 — Category vocabulary unification (D8)
RED test: `--category test` succeeds; `--category deps|db|api|build|env|git|architecture|testing` all succeed. Currently FAILS for the doc-listed set. Implementation: accepted set = UNION of skill-doc list and engine list (`build, runtime, deps, db, api, test, env, ci, boundaries, orchestration, decommission, incident, init, testing, git, architecture` + explicit domain tags stay); skill doc canonical list updated to match exactly.

### T4.2 — Lock file cleanup
RED test: after `record_obs.py` completes, `<target>.lock` does NOT exist (currently FAILS — file persists). Implementation: release+unlink in `finally` (Windows-safe: unlink after `LK_UNLCK`/`flock(UN)`; if unlink races on Windows, retry-once then ignore — lock is advisory).

**Acceptance:** existing record_obs tests green (atomicity/locking tests must still pass — cleanup must not break concurrent-write protection).

---

## 7. Lane K — Canonical Manifest Repair (Flight 1, parallel)

**Files:** `templates/release_manifest.json`, new `tests/test_dwave_k.py`.
**Closes:** D4, D5, version hygiene.

### T5.1 — File-kind expansion (D4)
Expand `"templates/"` and `"templates/reports/"` directory-kind components into explicit file components (every file that exists under them at plan time; `requires` preserved where applicable). No directory-kind entries remain.

### T5.2 — Updater self-registration (D5)
Add `{"path": "scripts/update_meta_project.py", "kind": "script", "requires": []}`.

### T5.3 — Version hygiene
`framework_version` → `1.0.0-alpha.3` (the release this wave will cut; Steward tags to match — see §10).

### T5.4 — Canonical-manifest contract test (the coverage hole)
RED-first: `tests/test_dwave_k.py` loads the CANONICAL `templates/release_manifest.json` and asserts: every component `path` is file-kind (no trailing `/`), the updater is present, `framework_version` parses as semver, all component paths exist in the repo tree. This is the test class whose absence let D4/D5 ship (wave-0.9.0 C1 finding).

**Acceptance:** engine tests in E1/E2 that use fixtures are unaffected; the canonical manifest now validates against the engine's integral-bundle contract.

---

## 8. Lane E2 — Engine Perimeter & UX (Flight 2, strictly after E1 + K)

**Files:** `scripts/update_meta_project.py`, `skills/update-meta-project/SKILL.md`, extend `tests/test_update_meta_project.py` + new `tests/test_dwave_e2.py`.
**Closes:** auditor п.5, D2, D7, layout mismatch, friction (4) plan stdout, (5) sha-adoption; manifest readability.

### T6.1 — Identity admission (п.5a)
RED test: apply with unregistered actor → `APPLY-REFUSED ... actor not admitted` (verify_identity defensive import, mirroring `inspect_meta_project.py`). Registered+active actor passes.

### T6.2 — Project boundaries consult + `--protect` wiring (п.5b/c)
RED tests:
- Component whose TARGET path is Red in the project's `boundaries.md` → `protected` refusal with project-boundaries reason (default patterns still applied — union).
- `--protect scripts/x.py` actually protects `scripts/x.py` (currently FAILS: parsed, unused).
Implementation: defensive import of `check_boundaries` zone classifier; `plan_updates(patterns=user_patterns ∪ DEFAULT)`; CLI threads `args.protect`.

### T6.3 — Offline cache via CLI (D2)
RED test: dead origin + explicit 40-hex `--ref` + integral cache present → apply succeeds with `origin: cache` (currently FAILS: CLI re-resolves against origin first). Refs that are NOT exact SHAs still require origin (documented).

### T6.4 — Code-form markers (D7)
RED tests: marked block with `# local_repo_data:TAG` / `# /local_repo_data:TAG` in `.py` survives merge (currently FAILS); HTML form still works in `.md`. Implementation: marker regex selected per extension (`.py/.toml/.yml/.yaml/.sh/.cfg/.ini` → `#`-form; `.md/.html/.xml` → HTML-form; both accepted for unknown extensions). Skill doc: document BOTH forms with the extension table.

### T6.5 — Runtime-layout target mapping (layout mismatch)
RED test: repo with `.agents/skills/` present → apply of `skills/<name>/SKILL.md` writes to `.agents/skills/<name>/SKILL.md` (no duplicate at root); repo WITHOUT `.agents/skills/` → distribution path as today. Lock v2 `target` field (reserved in E1) records the resolved destination. Init skill cross-note lands in Lane B file — E2 only updates `skills/update-meta-project/SKILL.md` (layout section).

### T6.6 — Plan summary mode (friction 4)
CLI `plan`/`check` print summary by default (ops, paths, conflicts/protected/needs_base counts); full content only with `--full`. RED test: plan JSON default output has no `content`/`b'...'` blobs (summary mode), `--full` restores them.

### T6.7 — Sha-match adoption (friction 5)
RED test: unknown-origin conflict whose local bytes hash-equal the pinned content + `--adopt-existing` → action `adopt` (lock records entry, file bytes untouched, no rewrite). Without the flag → conflict as today.

### T6.8 — Manifest readability fallback
Engine reads `manifest.json` at source root, falling back to `templates/release_manifest.json` (canonical repo layout). RED test against the framework repo itself as source.

**Acceptance:** auditor scenario 4 (real release kit into a foreign project) passes end-to-end: fresh dir → engine apply from the framework repo at the new tag → runtime layout, lock v2, updater present (K), markers documented.

---

## 9. Integration (dispatcher) & Acceptance

1. After Flight 1: merge lanes, run `python scripts/sync_templates.py --check` (0 drift required; dispatcher runs `--write` once if embedded template sections changed), full battery, boundary audit 100%, identity check.
2. After Flight 2 (E2): same battery + the four auditor state-preservation scenarios LIVE (not unit tests):
   - **S1:** two sequential updates with adaptations → markers survive BOTH (п.1).
   - **S2:** update → restore → files AND lock coherent → check clean (п.2).
   - **S3:** full manage cycle with registry change, no adoption workaround (п.3).
   - **S4:** real release kit installed into a foreign scratch project via CLI offline+online (п.4/D2/D4/D5/layout).
3. RED-discipline replay: dispatcher reverts one fix per lane on a throwaway export and confirms the lane's new tests fail (spot-check, Guardian re-verifies fully).

## 10. Release Track (after Guardian verdict)

- Steward: atomic conventional commits per lane; tag `v1.0.0-alpha.3` matching `framework_version` (K/T5.3); GitHub Release **with `--prerelease`** (fixes the alpha.2 flag inconsistency); CHANGELOG; README parity check.
- Manual (owner, outside repo): branch protection (all four matrix-expanded check names); Red-Zone sanctioned mechanism REMAINS OPEN (T6.2 narrows the gap — engine now respects project Red zones — but the sanctioned-automation design is still pending).

## 11. Sequential Prompts (dispatcher → worker, verbatim)

> **Worker M:** Read `docs/superpowers/plans/2026-11-15-wave-d-state-integrity-and-perimeter.md`, execute ONLY Lane M (§4). Files: `scripts/manage_reports.py`, `skills/manage-meta-project/SKILL.md`, `tests/test_dwave_m.py`. RED-first per T2.1–T2.3. Verify: `python -m unittest tests.test_dwave_m -v` + full battery. Report: files changed, RED/GREEN outputs, deviations.

> **Worker B:** Read the plan, execute ONLY Lane B (§5). Files: `scripts/check_boundaries.py`, `skills/init-meta-project/SKILL.md`, `tests/test_dwave_b.py`. RED-first per T3.1–T3.3. Verify: `python -m unittest tests.test_dwave_b -v` + the 2 POSIX hook tests + full battery.

> **Worker R:** Read the plan, execute ONLY Lane R (§6). Files: `scripts/record_obs.py`, `skills/record-observation/SKILL.md`, `tests/test_dwave_r.py`. RED-first per T4.1–T4.2. Verify: `python -m unittest tests.test_dwave_r -v` + full battery.

> **Worker K:** Read the plan, execute ONLY Lane K (§7). Files: `templates/release_manifest.json`, `tests/test_dwave_k.py`. RED-first per T5.1–T5.4. Verify: `python -m unittest tests.test_dwave_k -v` + full battery. Enumerate the expansion file list from the repo tree and paste it into the report.

> **Worker E1:** Read the plan, execute ONLY Lane E1 (§3). Files: `scripts/update_meta_project.py`, `tests/test_update_meta_project.py`, `tests/test_dwave_e1.py`. RED-first per T1.1–T1.3; you OWN the existing engine test file — contract changes must be reflected as NEW assertions (v1-lock reading stays tested as backward compat), never as deletions. Verify: `python -m unittest tests.test_dwave_e1 tests.test_update_meta_project -v` + full battery.

> **Worker E2 (dispatch ONLY after E1+K are merged):** Read the plan, execute ONLY Lane E2 (§8). Files: `scripts/update_meta_project.py`, `skills/update-meta-project/SKILL.md`, `tests/test_dwave_e2.py` + extensions to `tests/test_update_meta_project.py`. RED-first per T6.1–T6.8. Verify: `python -m unittest tests.test_dwave_e2 tests.test_update_meta_project -v` + full battery + auditor scenario S4 live on a scratch dir.
