# Current and Active Project Tasks

Coordination registry for tasks and progress between agents and the user.
Before starting work, every agent MUST review the active task list and, if necessary, log subtasks with their authorship.

---

## Team Task Management Rules
1. **Authorship and Timestamp Logging:** Every task and subtask is logged in the format:
   `- [ ] [agent-id @ YYYY-MM-DD HH:MM] Task description`
2. **Delegation (Out-of-Scope Handoff):** If a subtask exceeds the current agent's boundaries, it is logged in "Delegated Subtasks" with the target role (`agent-<role>`).
3. **Step Completion:** Upon completing a task, change the status to `- [x]` and optionally append a 1-line summary result.
4. **Sanctity of Other Agents' Notes:** Agents are prohibited from deleting or modifying entries written by others. Editing is restricted to own entries (status, details).

---

## Active Objective
- **Task:** Full transition of agentic ecosystem to English (English canonical) and establishing bilingual public interface (EN/RU)
- **Initiator:** User
- **Start Date:** 2026-11-06

---

## Execution Plan and Checklist
> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.

> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.


> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.


---




> [!NOTE]
> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.


- [x] [vlv-code/meta-project::antigravity::ag-main::agent-github-steward @ 2026-11-19 17:25] Clean distribution synchronization to main branch & pyflakes 4.0.3 pin fix: fixed scripts/sync_dist_branch.py pathspec handling, pinned pyflakes 4.0.3 for Python 3.10 CI compatibility, mirrored pure distribution files (114 files) to main with 0 .agents/telemetry/notes, verified GitHub Actions CI run 44504739918 all checks green [COMPLETED]
- [x] [vlv-code/meta-project::antigravity::ag-main::agent-github-steward @ 2026-11-19 17:42] Release v1.0.0-alpha.8 published on main: bumped release manifest, plugin manifests, README badges, and CHANGELOG to 1.0.0-alpha.8, mirrored clean dist to main, created and pushed tag v1.0.0-alpha.8, verified GitHub Actions Release run 44507838203 (pre-release created with zip assets) and main CI run 44507680773 (All Checks Green) [COMPLETED]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-dev-lead @ 2026-11-23 12:40] Step 90: Wave J (external audit #4 follow-up) EXECUTED — 2 parallel flash workers + a dispatcher lane on owner instructions ("делай flash воркерами"; P0-3/P0-4 executed by the dispatcher under explicit owner authorization instead of Steward sign-off). Workers: P0-1 glossary (14 terms + 4-line zone example in README EN/RU with table-of-contents entries; every link target and in-page anchor verified; tests/test_jwave_r.py 17 tests), P0-2 structural-debt entry for inspect_repository() in weak_spots §3 (facts re-verified by line: one ~330-line function, section numbering skips #6, raw state/capability literals without a shared enum; hardening debt, no live defect; tests/test_jwave_d.py 9 tests), P1-2 Icebox disposition for DUAL_PASSPORT_CONFLICT (roadmap §9). Dispatcher lane (tests/test_jwave_p.py, 16 tests, 13 RED before the edits): P0-3 versioning policy stated on one line in CONTRIBUTING.md, CONTRIBUTING.ru.md (new subsection, line parity kept) and the CHANGELOG header; P0-4 ADR #23 in the roadmap — content of main and dev is identical (empty diff over dist paths), only history diverges (26 main-only commits = 5 sync-dist mirrors + 2 split strips + 19 direct; 41 dev-only); scripts/sync_dist_branch.py is a restore-based mirror, so a direct commit on main inside dist paths is overwritten unless the same change lands on dev (one such loss already happened: cef3802); decision recorded = keep the model, rebase/merge rejected (they would carry .agents/ into main or require rewriting a published history and invalidating pinned SHAs); ADR range updated to #14–#23 in the roadmap heading, the header NOTE, both READMEs and the test_iwave_d lock; P1-1 read-discipline dispositions (note under P2.2 for variant A, variant B rejected with its reason, variant C pointed at P2.3 pending an auditor clarification). Fixed on the way: RU table-of-contents anchor ("7 canonical states" against the "8" heading). Verification: battery 588/588 OK (1 platform skip), boundary gate 8 files with no violations and no override, audit-tree 100% (206 files), 0 drift, identity 0, pyflakes clean. Open for the owner: ADR #23 records option (a) = the status quo (confirm or switch); CONTRIBUTING §5 still tells contributors to open PRs against main, which the mirror would overwrite (flagged inside ADR #23, deliberately not changed); the phrase "next minor" in the beta policy line is ambiguous; the variant C clarification is drafted for the auditor [COMPLETED — Guardian packet, then Steward: lane commits]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-dev-lead @ 2026-11-23 14:55] Step 91: Dispatcher-to-orchestrator binding EXECUTED (owner request: align the agent-intake-dispatcher matrix entry with the native orchestrator agents that harnesses now ship and make it work on harnesses with AND without one; the owner then asked for the machine part as well) — 2 parallel flash workers + a dispatcher lane. EVIDENCE that fixes the design: a probe inside a subagent session returned an environment IDENTICAL to this orchestrator session (same variable names and label values) while reporting no subagent-launch tool, so native-orchestrator availability is not observable from the environment and the binding is DECLARED, never inferred. Matrix lane: skills/manage-meta-project/SKILL.md gains "Dispatcher Runtime Binding" (standalone = dedicated role session, default, works on every harness; orchestrator-hosted = the harness's native orchestrator loaded with the same dispatcher passport; role-to-role dispatch under the hosted binding follows the agreed delegation_level), a note on the matrix row, clauses in Phase 4/5/6 and rule 2; 236 lines against the 240 lock; the stale ZCODE_AGENT host-identification example replaced by the real session markers; tests/test_jwave_o.py 14 tests (13 RED). Scripts lane: optional per-installation registry block `orchestration` (native_orchestrator: bool; dispatcher_binding: standalone | orchestrator-hosted, hosted requires native_orchestrator true) validated by verify_identity via validate_orchestration_block (schema stays 1.1.0, additive); inspector report key `orchestration` with its source (registry | default | invalid) plus a Dispatcher Binding line in the human report; manage intake gate gains the installation-level declared kind `set_orchestration` (RED reproduced an undeclared orchestration change being admitted silently beside a declared role); host-harness detection consolidated into scripts/_common.py after a SECOND stale copy was found in verify_identity.py (returned None in real ZCode sessions, so its --actor host-mismatch warning could never fire); tests/test_jwave_v.py, _q.py, _m.py = 29 tests, every part RED-first. Dispatcher lane: the skill text now records the binding in the registry and declares set_orchestration (2 lock tests in tests/test_jwave_p.py). Owner decision: no orchestration block is declared in this repository's own registry for now (.agents/meta-project.json untouched). Dispatcher verification: diffs reviewed; live — both modules detect zcode in this session, the foreign-harness actor warning fires (advisory, rc 0 as designed), the inspector reports standalone/default for zc-main, and a 4-case CLI scenario on a scratch repository behaves as designed (declared change admitted; undeclared refused as stale; undeclared beside a declared role refused naming set_orchestration; both declared admitted); battery 633/633 OK (1 platform skip; +87 wave J tests over the 546 baseline), pyflakes 0, boundary gate 16 files clean without override, audit-tree 100% (210 files), 0 drift, identity 0. Corrections to earlier records by this agent: the working tree is LF (an earlier "CRLF" remark came from a broken grep measurement) and the wave J tree held 13 files at Step 90, not 12. HANDOFF-TIME FINDING (dispatcher, replay of the distribution tree: origin/main + the wave's 19 distribution files, no .agents/): tests/test_jwave_d.py read the dev-only weak_spots slice without the distribution-branch skip guard and errored in setUpClass (FileNotFoundError) — it would have failed the sync-dist battery on main; the guard was added with the test_gwave_s pattern (RED reproduced on that tree; after the fix the class is skipped there and all 9 tests still run on dev). RED replay of the seven wave test files on 9480860: d 5 of 9, p 10+6 of 18, r 6+10 of 17, o 13 of 14, v 14 of 14, q 8 of 8, m 7 of 7. Closing battery on the dev tree with the knowledge records: 633/633 OK (1 platform skip). Distribution-tree battery (a committed git copy of origin/main plus the wave's 19 distribution files, no .agents/, HEAD present — the tree sync-dist tests on main): 628 tests, OK, 32 skipped (development-branch installation contracts). A first replay of that tree without git showed 10 failures, all in two test classes that read HEAD through git — an artifact of the stand, not of the wave [COMPLETED — Guardian packet; then Steward: lane commits]
- [x] [vlv-code/meta-project::zcode::zc-main::agent-quality-guardian @ 2026-11-23 15:53] Step 92: INDEPENDENT Wave J acceptance (Steps 90-91) — battery 633/633 OK, pyflakes 0, 0 drift, 100%/210, identity 0; Red Zone untouched; gate 25/25 wave files rc=0 no override; RED replay on 9480860: all 7 lane counts byte-equal to disclosure (d 5F/9, p 10F+6E/18, r 6F+10E/17, o 13F/14, v 14F/14, q 8E/8, m 7F/7); docs: glossary 14 terms anchors-clean 328/328 parity, versioning one-liner x3, RU TOC 8 states, weak_spots inspect_repository facts exact (333 lines, #1-5+#7 no #6, 17 raw literals), icebox + A/B/C dispositions with sound B rejection; ADR #23 recomputed 26/41, dist diff EMPTY, sync_dist restore-based confirmed, range #14-#23 in 4 places + test lock updated; manage binding 236/240, declared-never-inferred, ZCODE_AGENT example replaced, mirror identical; PROBE SUBAGENT: env identical to orchestrator, no subagent-launch tool -> declared-binding design confirmed live; scripts live: validate_orchestration_block 6/6, orchestration key always-present + None w/o ctx + human line + digest keys unchanged, set_orchestration 4/4 CLI flows, host-detect single source in _common (same object x2), advisory strength ACCEPTED; dist tree 44 OK 1 dogfood-skip; disclosures honest (3 Guardian mid-check FAILs were own fixture artifacts, resolved); OPEN owner decisions noted: ADR #23 (a), CONTRIBUTING PR->main vs dist mirror, 'next minor' wording [COMPLETED — verdict: PASS, zero open defects; recommended commit split issued to Steward]

---

## Delegated Subtasks and Blockers
- `[agent-intake-dispatcher -> agent-qa-engineer @ 2026-11-06 22:15]`: Update integrity tests test_integrity.py (English section & zone contracts) [COMPLETED].
- `[agent-intake-dispatcher -> agent-meta-guardian @ 2026-11-06 22:15]`: Translate skills/, templates/, .agents/ specifications to English [COMPLETED].
- `[agent-intake-dispatcher -> agent-general-worker @ 2026-11-06 22:15]`: Create README.ru.md, translate README.md and .github templates [COMPLETED].
- `[agent-intake-dispatcher -> agent-github-steward @ 2026-11-07 01:00]`: Audit GitHub templates (.github/), CI/CD workflow, and git hygiene [COMPLETED].
- `[agent-intake-dispatcher -> agent-deep-auditor @ 2026-11-07 01:00]`: Audit translated markdown anchor links, residual test files, and terminology consistency [COMPLETED].
- `[agent-intake-dispatcher -> agent-qa-engineer @ 2026-11-07 01:00]`: Final verification pass.
