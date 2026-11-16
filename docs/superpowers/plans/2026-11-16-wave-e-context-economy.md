# Wave E — Context Economy (formats, canon, error envelopes, lazy-load pilot)

**Date:** 2026-11-16
**Author:** agent-dev-lead (dispatcher)
**Baseline:** the Wave D tree AFTER Steward's alpha.3 commits land (EXECUTION GATE: do not start while the Steward session is committing Wave D — tree collision).
**Sources:** Astra backlog (docs/НЕ ОБРАБОТАННЫЙ БЭКЛОГ meta-project.md — themes 1-2, items 3/5/6), user approvals 2026-11-16 (formats rework, tune cost, routing+modes canon, envelopes, lazy-load pilot included).
**Goal:** cut agent context cost without new machinery: compact verifiable formats, canonized delegation practice, uniform diagnostics, and an evidence-gated lazy-load pilot for init.

---

## 1. Global Invariants (same as Wave D §1)
Zero-dependency; RED-first where machine behavior changes (compact_memory `[>]`, envelopes, engine resource mapping); tests-as-spec; lane file ownership; no worker writes to knowledge slices/telemetry; no commits; full battery green at lane close. Workers run on general-purpose while the flash account is quota-limited (reset 2026-11-21 18:35).

---

## 2. Lanes and Flights

| File | T (formats) | C (canon) | E (envelopes) | P1 (measure) | P2 (pilot) |
|---|---|---|---|---|---|
| templates/project_knowledge/architecture.md | ✓ | | | | |
| templates/project_knowledge/tasks.md | ✓ | | | | |
| skills/init-meta-project/SKILL.md (+mirror, embedded blocks) | ✓ | | | | ✓ (after T) |
| scripts/sync_templates.py (EMBEDDED_TARGETS) | ✓ | | | | |
| AGENTS.md + templates/AGENTS.md | | ✓ | | | |
| skills/manage-meta-project/SKILL.md (+mirror) | | ✓ | | | |
| skills/tune-meta-project/SKILL.md (+mirror) | | ✓ | | | |
| templates/reports/tune_report.json | | ✓ | | | |
| scripts/check_boundaries.py (RED ZONE — sanctioned by user approval of this plan) | | | ✓ | | |
| scripts/{verify_identity,inspect_meta_project,manage_reports,record_obs,sync_templates,update_meta_project,compact_memory}.py | | | ✓ | | |
| tests/test_ewave_{t,c,e,p}.py (new, one per lane) | ✓ | ✓ | ✓ | – | ✓ |
| templates/release_manifest.json | | | | | ✓ |

**Flight 1 (parallel):** T, C, E, P1(read-only measurements).
**Flight 2 (after Flight 1):** P2 (init restructure + resources + manifest + engine mapping).
**Integration:** dispatcher (sync, battery, live checks), then Guardian → Steward (tag v1.0.0-alpha.4).

---

## 3. Lane T — Compact Formats (Flight 1)

1. **architecture.md v2** (template + init skill step 7 rewrite): map-first card — header rule "map is updated IN THE SAME CHANGE that touches a component"; Component Map table with **Depends on** column; Stack/State/Contracts as 3 one-line slots; E2E flows section kept conditional (multi-tier only). Design Patterns section removed. Approved draft verbatim (user session 2026-11-16).
2. **tasks.md checkpoint**: Team Rules gain rule 5 — `- [>]` in-flight/handoff status with the 5-field compact block (goal/decided/done/open/next); collapses to `- [x]` at completion; ground resumes from the last `- [>]`. Template example updated.
3. **Canonical embedding:** add `architecture.md` and `tasks.md` to `EMBEDDED_TARGETS` of init (sync_templates) so scaffolds stop free-form-composing these slices; embedded TEMPLATE blocks inserted into the init skill; mirrors synced.
4. RED-first machine change belongs to Lane E (compact_memory); Lane T only defines the format.

## 4. Lane C — Canon Texts (Flight 1)

1. **Routing matrix** (AGENTS.md §4/§6 area + manage skill Phase 2): script / cheap subagent / regular executor / strong model + independent verification; principle "task CERTAINTY beats task size" (Red-Zone one-liner → strong model; batch of identical spec'd edits → cheap executor); plan fields: responsible role / execution route / model tier / change scope / acceptance / verifier.
2. **Execution modes** (AGENTS.md Base Working Protocol ×2 copies): short (local unambiguous task → action+check+result; read-only mode is the canonical short route) / normal (related changes with known contracts) / extended (migrations, ambiguous defects, protected components). Mode choice by consequences+uncertainty; scenario-mandated checks preserved.
3. **Checkpoint cross-refs** in manage (handoff) and ground (recovery source).
4. **Tune cost accounting**: tune skill Phase 2 mandatory cost evidence + Phase 6 effect_records gain `"cost": {"rereads","tool_calls","handoffs","rework","wall_time_s"}`; honesty rules: available metrics only, no invented currency, before/after only on comparable tasks, smaller file ≠ proven launch economy. tune_report.json example updated with a filled cost block.

## 5. Lane E — Error Envelopes + `[>]` Support (Flight 1)

1. **Uniform envelope** across the 8 scripts for canonical failure paths (stderr block):
   `[CODE] <file>: <reason> | expected: <X> | actual: <Y> | next: <step>`
   Codes seed set: STALE_INPUT, INTAKE_REJECTED, APPLY_REFUSED, BOUNDARY_VIOLATION, IDENTITY_UNRESOLVED, CONTEXT_UNRESOLVED, NEEDS_BASE, LOCK_MISMATCH. Existing Wave D structured refusals keep their payloads (envelope wraps/reformats exit diagnostics; no behavior change — same rc semantics). Scripts stay standalone (no shared module import — distribution invariant); a `_print_envelope()` local helper per script is acceptable duplication.
2. **RED-first tests** (tests/test_ewave_e.py): one canonical failure per script asserts the envelope (code + file + next-step present).
3. **compact_memory `[>`]**: RED test — `- [>]` checkpoint rows are never re-homed/archived (active work); only `- [x]` compaction semantics apply. Implementation + envelope for compact_memory's own failures.
4. check_boundaries.py is Red Zone: edited under the user's explicit approval of this wave's scope (recorded here); Guardian re-verifies no gate weakening (envelope is presentation, rc/exit codes unchanged — locked by existing hook tests).

## 6. Lane P — Lazy-Load Pilot (P1 Flight 1 read-only; P2 Flight 2)

**P1 (measure, zero writes):** on the current canon — repeat-run on a healthy repo, clean init, new-harness adoption: record bytes read per scenario, file reads, SKILL.md share (embedded templates % of init text), wall time. Deliver numbers → go/no-go against the pilot criteria (abort if projected saving < 15% of init-invocation context or portability risk emerges).
**P2 (extract, only on GO):**
- Move init's embedded templates + bulky per-scenario detail to `skills/init-meta-project/resources/*.md`; SKILL.md keeps invocation conditions, scenario routing, short sequences, critical invariants, and explicit when-to-read pointers.
- Bootstrap invariant: resources ship WITH the skill in every distribution (manifest components; engine target mapping extends to `skills/<n>/resources/**` → `.agents/skills/<n>/resources/**`; offline cache bundles include them). No reads from a framework clone.
- Explicit loading contract: healthy-install re-check reads NO templates; clean init reads only needed templates; new-harness path reads only its procedure; a missing mandatory resource blocks the dependent step with the Lane E envelope (code: MISSING_RESOURCE) and a clear next step.
- Verification: P1 scenarios re-run identically; read-only stays 0-write; before/after comparison table recorded in the pilot section of the plan file itself (single source).
- Manifest gains resource components; framework_version → 1.0.0-alpha.4 (Steward tags to match).

## 7. Acceptance (dispatcher, then Guardian)

Battery 100% green; 0 drift; boundaries 100%; identity clean. Live checks: (1) fresh scratch repo init produces architecture.md/tasks.md matching templates byte-canonically; (2) a `- [>]` checkpoint survives compact_memory --dry-run untouched; (3) one envelope per script reproduced live; (4) pilot before/after table complete with an explicit keep/adjust/abandon decision. RED-discipline replay on the pre-wave export for machine lanes (E, P2).

## 8. Sequential Prompts — same verbatim style as Wave D §11, one per lane (T, C, E, P1, P2-after-Flight-1), each: plan path, lane section, files, RED-first where applicable, verify commands, report format.
