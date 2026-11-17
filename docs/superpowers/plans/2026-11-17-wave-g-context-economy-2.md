# Wave G — Context Economy II & Hygiene Tail (manage-slim, primitives, facts digest, EOL contract)

**Date:** 2026-11-17
**Author:** agent-dev-lead (dispatcher)
**Baseline:** `0d18a59` (tag v1.0.0-alpha.5 committed, tree clean; battery self-closed 390/390 post-commit)
**Sources:** owner-selected backlog 2026-11-17 (audit §7.2 section-map drift, U4/U10 dead code, tune language mix, manage-slim via proven init-P2 pattern, Astra primitives dictionary + facts cache with their "after pilot" conditions MET by wave E §6b, CRLF false-drift contract). CHANGELOG/release-notes sync rides the Steward alpha.6 cycle (packet, not a lane).
**Workers:** general-purpose subagents (owner instruction — no flash this wave), 4 lanes in parallel, disjoint files.

---

## 1. Global Invariants
Zero-dependency; RED-first where machine behavior changes (engine dead-code removal proven by usage scan test, EOL compare, digest determinism); lane file ownership; no knowledge-slice/telemetry writes by workers; no commits; full battery green at lane close.

## 2. Lanes and File Ownership

| File | H (engine+tail) | S (manage-slim) | D (doc canon) | I (digest) |
|---|---|---|---|---|
| scripts/update_meta_project.py | **✓** | | | |
| skills/update-meta-project/SKILL.md (+mirror) | **✓** (EOL note) | | | |
| skills/manage-meta-project/SKILL.md (+mirror, resources/) | | **✓** | | |
| scripts/sync_templates.py | | **✓** | | |
| templates/release_manifest.json | | **✓** | | |
| tests/test_sync_templates.py (manage-embedded assertions) | | **✓** (supersede) | | |
| skills/decommission-meta-project/SKILL.md (+mirror) | | | **✓** | |
| skills/scan-meta-project/SKILL.md (+mirror) | | | **✓** | |
| skills/tune-meta-project/SKILL.md (+mirror) | | | **✓** | |
| docs/primitives.md (new) | | | **✓** | |
| scripts/inspect_meta_project.py | | | | **✓** |
| skills/ground-meta-project/SKILL.md (+mirror) | | | | **✓** (1 line) |
| tests/test_gwave_{h,s,d,i}.py (new, one per lane) | ✓ | ✓ | ✓ | ✓ |

## 3. Lane H — Engine Hygiene + EOL Contract
1. **U4 dead code:** remove `BaseUnavailableError` (never raised; docstring already admits it) and `_atomic_write_text` (uncalled) — usage-scan lock test proves absence and stays green. RED-first: scan test asserting "no dead symbols" fails pre-removal? (trivially green — instead: removal verified by grep lock + full battery; report honestly that this is a lock-in, not a behavior RED).
2. **U10:** remove the dead `--full` flag from `check` (help already admits it); remove any parsing remnants.
3. **CRLF false-drift contract (the real Windows tail):** RED — fixture with LF lock record + CRLF working-tree file (autocrlf fresh-checkout simulation) currently reports `drifted`. GREEN: check/plan treat raw-hash mismatch as up-to-date-with-diagnostic when LF-normalized bytes hash-match the lock record (`eol_normalized: true` diagnostic in check JSON, no action required); genuine content changes still drift/refuse (tamper detection unchanged — EOL-only flip is not tampering). Lock/installed_sha semantics unchanged (engine-written bytes stay the comparison anchor).
4. Skill doc (+mirror): document the EOL-normalization diagnostic in one line.

## 4. Lane S — manage-slim (init-P2 pattern applied to the heaviest skill)
1. Extract manage's embedded team-template blocks (profile/notes/system_prompt) to `skills/manage-meta-project/resources/` (byte-copies of `templates/team/*` — canonical stays templates/); restructure SKILL.md 394 → target ≤ ~230 lines: keep frontmatter, when-to-invoke, Resource Loading Contract (MISSING_RESOURCE envelope, verbatim guidance), 5-operations action table, competency catalog COMPRESSED to routing-relevant rows (or pointer to resources/competency-catalog.md — implementer's choice, justify), topology invariants, phases as short procedures, team rules of engagement. Fix the double `#### 2.` headers in Phase 2 as part of restructuring.
2. `scripts/sync_templates.py`: manage moves from EMBEDDED_TARGETS to RESOURCE_TARGETS (canonical `templates/team/{profile,notes,system_prompt}.md` → `resources/`; mirror sync covers resources/ — reuse init's mechanism verbatim).
3. Manifest: 3 resource components (kind "resource", requires ["skills/manage-meta-project/SKILL.md"]).
4. Tests: supersede test_sync_templates manage-embedded assertions to resource-equivalence (drift/fatal semantics preserved); new lock-ins: contract block present, resources byte-match canonical, no embedded TEMPLATE blocks remain in manage SKILL.md, manifest edges. Engine resource runtime-layout mapping (Wave E) already covers skills/<n>/resources/** — add a plan-level test proving a manage resource maps to .agents/skills in a runtime-layout consumer.

## 5. Lane D — Doc Canon + Primitives Vocabulary (Astra, condition met)
1. Section-map drift (audit §7.2): decommission skill — unify "Section 7" vs "## 6." references to the canonical 8-section passport (§7 roster); scan skill — "Sections 2-5" → the actual canonical set the scan checks (verify against templates/AGENTS.md section list; do not invent).
2. Tune skill: protocol field names (:56-58, Russian inside English artifact) → English (observability/evidence/executor fields); the bilingual-user-interview exemption (init) does NOT apply — these are artifact fields.
3. `docs/primitives.md` (new): Astra vocabulary — 4 recurring operations mapped to their working implementations: deterministic survey (`inspect_meta_project` state classification), identity admission (`verify_identity.evaluate_actor_admission`), report intake (`manage_reports.evaluate_manage_intake`), observation recording (`record_obs.record_observation`). Each entry: name, owning script/function, one-line contract, which skills route to it. NO behavior change — documentation + the canon lock test below.
4. tests/test_gwave_d.py: lock-ins — every primitive's referenced symbol exists (import-level check), section references in decommission/scan match the canonical passport structure, tune fields are English.

## 6. Lane I — Facts Digest (Astra facts cache, honest minimal form)
1. `scripts/inspect_meta_project.py` gains `--facts-digest` (read-only, with existing context flags): deterministic compact JSON — repository state, per-slice sha256 (the 5 knowledge slices + registry), capability matrix, tool version — the "verified facts" fingerprint an agent can stash and later diff cheaply instead of re-reading everything. Byte-stable output for identical inputs (same tree, same tool) — RED test: two consecutive runs byte-identical; one changed slice → exactly that slice's hash flips. NO disk cache (Astra: read-only mode keeps it in memory/stashable output — zero new state).
2. Ground skill: one line in the selective re-reads step — "a stashed facts digest (inspect --facts-digest) may replace re-reading unchanged slices; a digest mismatch names exactly what to re-read."
3. tests/test_gwave_i.py: determinism, sensitivity, read-only (0 writes), context-unresolved behavior unchanged without flags.

## 7. Integration & Acceptance (dispatcher)
sync (0 drift), battery 100% green (on the committed alpha.5 base; workers run on the clean tree), boundaries 100%, identity clean; manage-slim live check: scratch consumer with runtime layout receives manage resources via engine mapping; digest smoke on this repo; RED-discipline replay for machine lanes (H, I) on the pre-G export; Step 82 + telemetry; packets → Guardian → Steward (alpha.6; CHANGELOG + release-notes asymmetry fix rides the release cycle per owner triage).
