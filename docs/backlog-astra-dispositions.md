# Astra Backlog Dispositions — Structured Decision Record

> Snapshot as of v1.0.0-alpha.4 (2026-11-16).

This document is the structured successor of the raw chat capture
[`docs/archive/НЕ ОБРАБОТАННЫЙ БЭКЛОГ meta-project.md`](archive/НЕ%20ОБРАБОТАННЫЙ%20БЭКЛОГ%20meta-project.md)
(moved to `docs/archive/` unchanged). The raw file mixed two backlog themes and a
free-form consultation answer; it was two release waves stale when triaged
(written against revision `4274bbd` / 197 tests; triage performed against the
post-Wave-D state).

**Triage provenance:** Step 77 (dispatcher, 2026-11-16 12:10, tasks.md) — backlog
triaged per user approvals ("это тоже включи в изменения"), new value scoped into
Wave E; Step 80 (dispatcher, 2026-11-16 20:20, tasks.md) — the "primitives
dictionary" follow-up scoped into Wave F lane FC. Outcomes verified at Wave E
acceptance (Step 79) and CHANGELOG `[1.0.0-alpha.4]`.

## Disposition Summary

| # | Theme (raw file) | Disposition | Wave / Pointer |
|---|---|---|---|
| 1 | Lazy-load resource pilot for `init-meta-project` | ACCEPTED — Wave E lane P | `docs/superpowers/plans/2026-11-16-wave-e-context-economy.md` (§6a/§6b), CHANGELOG `[1.0.0-alpha.4]` |
| 2a | Delegation routing matrix (script / cheap subagent / regular executor / strong model; certainty beats size; plan fields) | ACCEPTED — Wave E lane C (manage Phase 2 "Execution Routing") | Wave E plan, CHANGELOG `[1.0.0-alpha.4]` |
| 2b | Execution modes (short / normal / extended) | ACCEPTED — Wave E lane C | Root `AGENTS.md` §6 "Execution Routes", `templates/AGENTS.md` |
| 2c | Cost accounting in tune (preparation → execution → verification → rework chain) | ACCEPTED — Wave E lane C (`cost` block in tune effect records) | CHANGELOG `[1.0.0-alpha.4]` |
| 2d | Structured diagnostics (stable error code + expected/actual + next step, e.g. `STALE_INPUT`) | ACCEPTED — Wave E lane E (9 codes across 7 scripts, presentation-only) | Wave E plan, CHANGELOG `[1.0.0-alpha.4]` |
| 2e | Cross-session task checkpoint as a NEW artifact | DECLINED — no new artifact; `tasks.md` is the skeleton (lane T added the `- [>]` checkpoint convention instead) | Step 77 triage; Wave E lane T |
| 2f | Verified-facts cache (key = inputs + checker version + params, read-only first) | DECLINED for Wave E — not selected into scope; partial coverage via lane T (`architecture.md` v2 map with `Depends on` column + "update in the same change" rule); revisit after Wave F | Step 77 triage |
| 2g | Change-since-last-read summaries (impact feed after edits) | DECLINED for Wave E — depends on a trustworthy dependency map; prerequisite partially built by lane T (see 2f) | Step 77 triage |
| 3 | "Primitives dictionary" (`_common.py` consolidation: inspection, identity, intake, observation-writing operations) | ACCEPTED — Wave F lane FC (Flight 2) with ADR #22 | `docs/superpowers/plans/2026-11-16-wave-f-security-perimeter.md` §6 |
| 4 | Mass splitting of all other skills (beyond the init pilot) | DECLINED by design — kept out of the pilot scope pending pilot outcome | Raw file line 29; Wave E §6a/§6b |
| 5 | Offline/bundle resource delivery, engine contracts (partial raw-file overlap) | ALREADY BUILT before triage — waves 0.9.0 + D (manifest/lock, offline cache fallback, runtime-layout mapping) | CHANGELOG `[1.0.0-alpha.2]`, `[1.0.0-alpha.3]` |

## Theme 1 — Lazy-Load Resource Pilot (ACCEPTED, Wave E lane P)

Raw proposal: extract embedded templates from the init skill into separately
loaded resources; explicit loading semantics; missing-resource must block the
dependent step; pilot with before/after measurements and abort criteria.

Disposition (Step 77): accepted as Wave E lane P with an evidence gate —
P1 read-only measurements with abort criteria (including re-measured template
share of the grown init skill) before P2 extraction; bootstrap invariant:
resources ship with the skill via manifest / engine mapping / offline bundles;
`MISSING_RESOURCE` envelope.

Outcome (Steps 78–79, owner re-scope §6a marked post-hoc): P1 NO-GO for blanket
scope (worst case S1 9.8% < 15%); criterion re-scoped to recurring invocations
(owner decision, recorded in plan §6a with §6b KEEP rationale). P2 executed:
init `SKILL.md` 41,590 → 19,411 B / 665 → 165 lines / 0 embedded blocks; 9
resources byte-copied from canonical sources via `sync_templates`
(`RESOURCE_TARGETS`); manifest gained `kind: resource` components (+9);
`framework_version` → `1.0.0-alpha.4`.

## Theme 2 — Delegation and Token Economy (consultation answer)

Disposition per sub-item in the summary table (2a–2g). The delegation matrix,
execution modes, tune cost accounting, and structured diagnostics were codified
into Wave E lanes C and E. The checkpoint artifact was explicitly dropped
(tasks.md already is the cross-session skeleton — lane T formalized the `- [>]`
checkpoint convention instead of introducing a new file). The verified-facts
cache and change-since-last-read feed were declined for Wave E (no wave owns
them yet; lane T's `Depends on` map is the static prerequisite); they remain
candidate backlog items, to be re-triaged after Wave F.

## Theme 3 — Primitives Dictionary (ACCEPTED, Wave F lane FC)

Raw proposal ("следующий этап — словарь примитивов"): after the pilot confirms
contract repetition across skills, consolidate shared operations (inspection,
identity, intake, observation writing) under clear names referencing working
implementations.

Disposition (Step 80): accepted into Wave F as lane FC — `scripts/_common.py`
(`_error_envelope`, `_utc_now_iso`, git subprocess helper, lock helper), every
importing script gains `requires: ["scripts/_common.py"]` in the manifest, ADR
#22 documents the standalone-deployment tradeoff. Flight 2 (after FX+FR merge).

## Disposition Rules Applied

- Items already delivered by earlier waves were marked BUILT, not re-scoped.
- Acceptances carry pointers to the authorizing plan and the release CHANGELOG.
- Declines carry the rationale and, where applicable, the revisit condition.
- The raw chat capture is preserved verbatim in `docs/archive/` for provenance.
