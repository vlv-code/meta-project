# Wave F — Security Perimeter (containment, cache trust, serialization, fail-closed state)

**Date:** 2026-11-16
**Author:** agent-dev-lead (dispatcher)
**Baseline:** `cd343f8` (tag v1.0.0-alpha.4; tree clean; audit base verified by grounding 2026-11-16)
**Sources:** external audit `audit_meta-project_v1.0.0-alpha.4.md` (7.5/10) + auditor addendum (no unresolved disagreements); triage accepted by owner 2026-11-16; owner decision on U8 design-note: ACCEPT (JSON field, rc contract unchanged).
**Goal:** the update/report subsystem's security catches up with its own ambitions: no path escapes, no unverified cache bytes, no parallel clobbering, no silent git failures; CI covers Windows and machine-checks the rc contract; docs stop drifting. Release v1.0.0-alpha.5.
**Methodological commitment (audit lesson, recorded in weak_spots at start):** every guard ships with an ADVERSARIAL RED reproduction of the attack (hostile source, tampered cache, parallel process, injected argv, dead git) BEFORE the fix — we previously tested fail-closed on errors, not on adversaries.

---

## 1. Global Invariants (same as Waves D/E §1)
Zero-dependency; RED-first adversarial; lane file ownership; own test file `tests/test_fwave_<lane>.py` (FX additionally extends `tests/test_update_meta_project.py`); no knowledge-slice/telemetry writes by workers; no commits; full battery green at lane close; workers per user preference on flash, fallback general-purpose on quota (standing pattern: dispatcher inventories and resumes).

---

## 2. Lanes and Flights

| File | FX (engine) | FR (reports) | FD (docs/ops/CI) | FC (_common, Flight 2) |
|---|---|---|---|---|
| `scripts/update_meta_project.py` | **✓** | | | ✓ (envelope import only) |
| `tests/test_update_meta_project.py` + `tests/test_fwave_x.py` | **✓** | | | |
| `skills/update-meta-project/SKILL.md` (+mirror) | **✓** | | | |
| `scripts/manage_reports.py` | | **✓** | | ✓ (envelope import only) |
| `templates/reports/{init,manage}_report.json` | | **✓** | | |
| `tests/test_fwave_r.py` | | **✓** | | |
| `AGENTS.md` (2 North Stars) | | | **✓** | |
| `README.md`/`README.ru.md` (badge), `CONTRIBUTING{,.ru}.md` (map 8) | | | **✓** | |
| `docs/decisions_and_roadmap.md` (D2 status, ADR #22), historical snapshot-markers ×3, backlog file restructure, `temporary_overrides.md` closure | | | **✓** | |
| `.github/workflows/ci.yml` (**RED ZONE — sanctioned by owner approval of this plan**, §3 FD) | | | **✓** | |
| hygiene: PII redaction in `.agents/**`, tasks.md NOTE-dedup | | | **✓** | |
| test fixes ×4 (dup, live-repo `--write`, alpha hardcode, dead class) | | | **✓** | |
| `scripts/_common.py` (new), manifest requires, migration ×8, ADR | | | | **✓** |
| `templates/release_manifest.json` | | | | **✓** |

**Flight 1 (parallel):** FX, FR, FD.
**Flight 2 (after 1 merges):** FC (single lane, all-script refactor).
**Integration:** dispatcher (sync, battery, live adversarial replays on scratch repos), Guardian acceptance, Steward release alpha.5.

---

## 3. Lane FX — Engine Perimeter (Flight 1)

**T-X1. SEC-1 containment guard (3-layer, per addendum):**
RED: hostile origin with manifest component `path: "../../evil"`, `"C:/evil"`, `"//server/share"`, symlinked dest — apply/plan refuse with ZERO writes (assert disk unchanged); cache `_read_bundle_tree` and `restore` journal paths likewise refuse.
Implementation: (a) `_posix` rejects absolute paths and any `..` segment; (b) `assert_within(root, rel)` = `dest.resolve().relative_to(root.resolve())` before every write/read in apply, cache, restore, journal; (c) refusal when dest is an existing symlink (covers U9 exfil). Pattern reference in-repo: manage_reports.py:476-479.

**T-X2. SEC-2 cache verification:**
RED: tampered cache bytes with live origin → apply REFUSES (hash mismatch vs origin); tampered cache offline → REFUSED via sha256-manifest mismatch; cache built for pin A served for pin B (post-rewrite) → REFUSED (ref-pin recorded in manifest).
Implementation: on cache load, verify per-file sha256 against a cache manifest `<sha>/cache-manifest.json` (written at bundle build/load time; includes component files + `manifest.json` + the ref-pin it was built from); when origin is reachable, cross-verify component hashes against origin blobs; any mismatch → PartialCacheError-style refusal, never silent use.

**T-X3. SEC-4 serialization:** file_lock (port from compact_memory.py:20-61) held across apply AND restore; RED: second concurrent apply on same repo → refused with envelope (`ENGINE_BUSY`), journal untouched.

**T-X4. M3-adjacent U6:** `check` uses the same cache-fallback resolution as plan/apply (one answer per repo state). RED: dead origin + exact-SHA + valid cache → check reports via cache (today: fails).

**T-X5. U7 + U11:** `versions.after` split into `framework_version` + `commit_sha`; restore marks the update report `status: "restored"` (audit trail preserved). RED both.

**T-X6. U8 design-note (owner-accepted):** `check` JSON gains `check_status: "ok" | "failed"` (rc contract unchanged — locked by CI smoke in FD). RED: failing check → rc 1 AND `check_status: "failed"`; updates-found → rc 1 AND `check_status: "ok"`.

**T-X7. fsync durability:** `_atomic_write_bytes` fsyncs temp file before `os.replace` (lock/registry/journal class files). Cheap; no test beyond existing atomicity suites + new one confirming no behavior change.

Skill doc (+mirror): cache verification, serialization, containment semantics, check_status field.

## 4. Lane FR — Reports Perimeter (Flight 1)

**T-R1. SEC-3:** `installation_id`, `init_run_id` validated like `run_id` (manage_reports.py:385-388 pattern) at `get_report_dir` and manage-create read path. RED: `--installation "../../evil"` → refused, no directories created.
**T-R2. M2:** 40-hex validation for `commit_sha` before `git show` at :909 AND in `verify_declared_registry_delta` (:988). RED: `--upload-pack`-style value → refused.
**T-R3. M3 fail-closed git state:** `get_git_state` returns explicit `git_state_error` on any git subprocess failure (3 sites); staleness treats such reports as stale/suspect with envelope `STALE_INPUT` reason `git state unavailable`. RED: monkeypatched git failure → report NOT admitted as fresh.
**T-R4. M4/M5:** run_id gains monotonic sequence suffix (or latest resolved by mtime+name tiebreak — implementer's choice, documented); save_report overwrite-guard via O_EXCL create. RED: two same-second runs have deterministic latest; concurrent same-run_id second writer fails loudly.
**T-R5. M6:** init/manage report templates gain `input_fingerprints`; validator requires them for completed init/manage reports (update/tune unaffected this lane). RED: completed init report without fingerprints → INVALID_REPORT.
**T-R6. M9/M10:** rename `R old -> new` parsed to new path in modified_files (staleness detects renamed essential inputs); `schema_version` exact-set check ({"1.0","1.1","1.0.0","1.1.0"} major.minor enumeration, not bare prefix). RED both.

## 5. Lane FD — Docs, Ops, CI, Hygiene (Flight 1)

**T-D1. Passport sync:** root AGENTS.md §1 gains the two template North Stars (Default Closed Tooling, Adversarial Testing Invariant) — the live violation of our own sync invariant.
**T-D2. Doc-sync (live docs only):** README badge ×2 → current release line; CONTRIBUTING map 3/8 → 8 scripts ×2; roadmap §8.4 D2 marked resolved-in-alpha.3; `temporary_overrides.md` stale 🔴 override (2026-11-06) closed with resolution note; backlog file `НЕ ОБРАБОТАННЫЙ БЭКЛОГ` → structured doc (decision record: which items accepted into waves E/F, which declined with rationale), raw chat moved to archive.
**T-D3. Snapshot-markers (addendum):** one-line `> Snapshot as of <release>; superseded facts kept for provenance` into decisions_and_roadmap §7/§8, test_report_alpha_skill.md, audit_38deed9 baseline.
**T-D4. CI (RED ZONE, sanctioned by owner approval of this plan — no gate weakening; trusted-base untouched):** windows-latest × 1 Python (3.12) in matrix; stable aggregate job (`all-checks`) depending on the four expanded names + windows job — for required-checks wiring; smoke step: `check` rc contract on synthetic repos (rc 0 up-to-date / rc 1 updates-found) machine-verified; `verify_identity --check` step added.
**T-D5. Hygiene:** redact residual machine-username occurrences in `.agents/**` → `machine username (redacted)` (2 sites per audit); tasks.md NOTE-dedup (relapse of a fixed defect).
**T-D6. Test fixes ×4:** byte-duplicate drift test dedup (keep one, others import or delete); `--write`-on-live-repo tests → temp clone fixtures; alpha-version hardcode → read `framework_version` from manifest PLUS keep a lock test "manifest version == latest CHANGELOG version heading"; remove superseded dead test class. No assertion weakening — replacements only.

## 6. Lane FC — `_common.py` consolidation (Flight 2, after FX+FR merge)

Create `scripts/_common.py` (`_error_envelope`, `_utc_now_iso`, git subprocess helper, lock helper); add to manifest as component with `requires: []`; every script that uses these gains `requires: ["scripts/_common.py"]` (manifest `requires` graph — precedent: inspect/manage) and imports via the mirror try/except pattern with explicit degraded-mode fallback; FX/FR scripts migrate their local copies; ADR #22 documents the standalone-deployment tradeoff. RED: manifest contract test (test_dwave_k-style) requires _common for every script that imports it (grep-based); battery green.

## 7. Acceptance

Battery 100% green; 0 drift; boundaries 100%; identity clean. LIVE adversarial replays (dispatcher, scratch repos): traversal manifest refused; tampered cache refused online+offline; wrong-pin cache refused; parallel apply serialized; injection ids refused; git-failure → stale; check rc smoke matches contract. RED-discipline replay on pre-F export for test_fwave_{x,r,d}. Guardian independent acceptance incl. line-audit that NO gate was weakened (ci.yml diff, check_boundaries untouched this wave).

## 8. Sequential Prompts
Verbatim per lane (FX, FR, FD parallel; FC after merge) — same format as Waves D/E §11: plan path, lane section, files, adversarial-RED-first requirement, verify commands, report format.
