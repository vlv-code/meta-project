# Wave I — Audit Response III (parser honesty, read-only assertion, self-check invariants, doc sweep)

**Date:** 2026-11-18
**Author:** agent-dev-lead (dispatcher)
**Base:** dev @ ca5c7a1 (alpha.7 committed, tree clean)
**Sources:** external audit #3 (8.0/10, dev@7850151) — triage accepted by owner 2026-11-18 ("делай параллельными субагентами"). Overlap note: audit P0s (§6.2 mapping, §6.3 crash) were ALREADY fixed by wave P (PD mapping, D7 Step 86) — this wave covers the NEW findings only.
**Goal:** the gate's parser stops lying silently, `--read-only` becomes a verifiable assertion, the framework's own repo is lock-tested for 100% boundary coverage, docs stop referencing nonexistent ADRs. No release bump (rides the next Steward cycle).

---

## 1. Global Invariants
Zero-dependency (stdlib only — `sys.addaudithook` is stdlib); RED-first; lane file ownership; no knowledge-slice/telemetry writes by workers; no commits; full battery green at lane close. ci.yml edit in Lane IT is RED ZONE — sanctioned by the owner's approval of this wave scope (pyflakes step explicitly recommended and accepted).

**Critical regression bar for Lane IG:** the parser change MUST leave the framework's own `.agents/project_knowledge/boundaries.md` classification IDENTICAL (same zone per path, audit-tree 100%, same Green/Yellow/Red counts) — verify by capturing the zone map before and after the change.

## 2. Lanes

| File | IG (gate/parser/inspector) | IT (tests/CI) | ID (docs/templates) |
|---|---|---|---|
| scripts/check_boundaries.py (parser §6.4 + black_violations §6.8) | **✓** | | |
| scripts/inspect_meta_project.py (--read-only §6.1 + dead code §6.8) | **✓** | | |
| scripts/compact_memory.py (compacted_any), scripts/update_meta_project.py (journal_path) | **✓** | | |
| tests/test_iwave_g.py (new) | **✓** | | |
| .github/workflows/ci.yml (pyflakes step, RED ZONE sanctioned) | | **✓** | |
| tests/*.py unused-import cleanup (pre-existing files; EXCLUDE test_iwave_*) | | **✓** | |
| tests/test_iwave_it.py (new) | | **✓** | |
| templates/project_knowledge/boundaries.md (generic root patterns §6.6) | | | **✓** |
| README.md / README.ru.md (ADR numbering §6.7; protection-in-CI note §7.2) | | | **✓** |
| CONTRIBUTING.md / CONTRIBUTING.ru.md (fork/notes.md note §7.3) | | | **✓** |
| tests/test_iwave_d.py (new) | | | **✓** |

## 3. Lane IG — Gate Honesty (parser + read-only assertion + dead code)

**T-G1 §6.4 parser (RED-first, THE machine change):**
RED probes: (a) Green-zone line containing `docs/expected_behavior.md` silently dropped (substring "expect") — reproduce via parse_boundaries; (b) backticked multi-pattern `docs/**, *.md` parsed as ONE pattern (comma inside); both must fail current, pass fixed.
Implementation: a bullet line is treated as a COMMAND LINE only if it STARTS with a known CLI verb (python/pytest/git/pip + space) or is a bare continuation; path candidates are otherwise parsed as paths. Backtick-quoted patterns are split on commas into separate patterns (whitespace-trimmed). DOCUMENT the rule in the parser docstring.
Regression bar (§1): capture full zone classification of the live `.agents/project_knowledge/boundaries.md` before the change (path→zone map, audit-tree counts 100%/Green75/Yellow108/Red11) and prove the map is IDENTICAL after. Property/edge tests: expect/assert/pytest-substring PATHS now map; command lines still skipped; comma multi-patterns split; existing boundaries.md map unchanged.

**T-G2 §6.1 --read-only assertion (RED-first):**
RED: `inspect_meta_project --read-only` on a fixture where a planted write occurs during inspection → currently succeeds silently; must REFUSE.
Implementation: when `--read-only` is set, install `sys.addaudithook` for the duration of the inspection call: on audit events `open` (mode contains w/a/+) / `os.replace` / `os.remove` / `os.rename` targeting paths INSIDE the audited repo (outside-temp exceptions: tempfile used by the tool itself is none — inspection is pure), raise → CLI catches and emits the Wave-E envelope `READ_ONLY_VIOLATION` (rc≠0). Careful: the audit hook must not break legitimate reads; limit to the inspection window; document in --help that the assertion covers the inspection call only. Keep output byte-identical when no violation (normal runs unchanged).
**T-G3 §6.8 dead code:** remove `black_violations` (check_boundaries:767 — assigned, unused), `compacted_any` (compact_memory:411), `tasks_file`/`obs_file` unused locals + unused `os`/`re` imports (inspect_meta_project), `journal_path` (update_meta_project:2115). Verify each by grep before removal; battery green after.

**Verify:** `python -m unittest tests.test_iwave_g tests.test_check_boundaries tests.test_inspect_meta_project tests.test_gwave_i -v` GREEN + full battery 100% green + the §1 regression map proof in the report.

## 4. Lane IT — Self-Check Invariants + CI Hygiene
**T-T1 §6.2 invariant:** test (skipTest when `.agents/project_knowledge/boundaries.md` absent — main branch) asserting `check_boundaries.py --audit-tree` on THIS repository exits 0 with 100% coverage. Locks the door the sanction-mapping bug walked through.
**T-T2 §6.5:** test asserting every owner in `.github/CODEOWNERS` is in `SANCTION_AUTHORIZED_ACTORS` (superset allowed; parse CODEOWNERS `@owner` tokens, skip `@dependabot`-style bots if any).
**T-T3 §6.8/P3#9 test-import cleanup:** remove unused imports/vars in pre-existing `tests/*.py` (pyflakes clean); do NOT touch `tests/test_iwave_*.py` (other lanes) or weaken anything.
**T-T4 ci.yml pyflakes step (RED ZONE, sanctioned by owner approval):** additive step after "Run integrity tests": `python -m pyflakes scripts/ tests/` — pyflakes is a declared opt-in CI dev-tool (pinned `pyflakes@3.x` via pip install in-step, `continue-on-error: false` AFTER Lane IG/IT cleanups make it pass; if flaky on runner, `continue-on-error: true` with a follow-up note — decide by actual first run). Trusted-base steps untouched.
**Verify:** `python -m unittest tests.test_iwave_it -v` GREEN; battery 100% green; `pyflakes scripts/ tests/` clean locally (report the before-count ~29 → 0).

## 5. Lane ID — Docs & Template Sweep
**T-D1 §6.6:** `templates/project_knowledge/boundaries.md` gains generic root-file mappings: `.gitattributes`, `.gitignore`, `LICENSE` (Green — VCS/metadata hygiene; match existing style). Verify the template still parses 100%-clean against the framework repo root under the CURRENT parser (integration will re-verify under IG's parser).
**T-D2 §6.7:** README.md/README.ru.md: replace the nonexistent `ADR #1–#8` claim with the real canonical range (`ADR #14–#22`, docs/decisions_and_roadmap.md) — verify the actual range by reading the doc first.
**T-D3 §7.2:** one-line README note (EN/RU) near the boundaries/gate mention: repository protection is enforced in CI (trusted-base gate); the local pre-commit hook is a convenience layer and `META_PROJECT_ALLOW_RED_ZONE=1` is a local operator override.
**T-D4 §7.3:** CONTRIBUTING EN/RU: one-line note for contributors that `.agents/team/*/notes.md` and `observations.md` contain the maintainers' internal agent workflow history (revealed on fork by design — dogfooding is intentional).
**T-D5:** `tests/test_iwave_d.py` lock-ins: template boundaries contains the three generic patterns; README ADR range matches docs reality; CONTRIBUTING notes present EN/RU.
**Verify:** lane suite GREEN; full battery green; `sync_templates.py --check` 0 drift AFTER your edits (template edit may drift init resources — run `--write` and disclose, mirroring wave P PF procedure; byte-normalize CRLF artifacts like PF did).

## 6. Integration (dispatcher)
sync 0 drift; battery 100% green; boundaries audit-tree 100% + the IG map-identity proof review; Step 87 + telemetry; packets → Guardian → Steward (rides alpha.8 or next cycle; CHANGELOG Known-Limitations wording fix + §6.7 already covered by ID; branch-sync automation stays a Steward process item).

## 7. Sequential Prompts — embedded in dispatch (flash workers), same format as waves D–P.
