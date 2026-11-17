# Wave P — Plugin Packaging (manifests ×3, version locks, frontmatter ×9, README installation, CI validation)

**Date:** 2026-11-17
**Author:** agent-dev-lead (dispatcher)
**Base:** dev @ 7850151 (v1.0.0-alpha.6); main = clean distribution branch (no `.agents/`) — verified by gap-analysis v2 §1
**Sources:** gap-analysis v1 + v2 (auditor), triage accepted 2026-11-17; owner decision "го пока в порядок приведем. Это будет плагин" = the wave's Red-Zone authorization provenance (recorded in the sanction file reason).
**Goal:** one-command installation through Claude Code plugin channel, Agent Plugins 1.0.0 channel, and skills.sh; format validation in CI; zero dual-canon (scripts stay at repo root, requires-graph is the honest dependency declaration — per-skill embedding DECLINED per wave G lesson).

---

## 1. Global Invariants
Zero-dependency at runtime (external validators = declared opt-in CI tooling, pinned, non-blocking); lane file ownership; no knowledge-slice writes by workers; no commits; full battery green at lane close. This wave touches RED ZONE (ci.yml, boundaries.md) — sanctioned by the owner decision above; the dispatcher finalizes the sanction file at integration (base_sha = actual pre-push HEAD, authorized_by vlv-code, reason = owner decision in-session). Workers must NOT create the sanction file.

## 2. Push Mechanics (v2 §2.1 — plan ahead, not discover)
First push of wave P is a red-zone event: 3 unmapped new paths + ci.yml edit + boundaries.md refresh, judged by the BASE policy (trusted-base gate). Bundle: ONE push per branch = sanction (bound to that branch's pre-push HEAD) + boundaries refresh + all artifacts. dev first, cherry-pick to main with its OWN sanction (separate base). Dispatcher owns both sanction files.

## 3. Lanes (4 parallel flash workers)

| File | PM (manifests+locks) | PF (frontmatter) | PR (README) | PD (CI+boundaries) |
|---|---|---|---|---|
| .claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugin.json (root) | **✓** | | | |
| tests/test_pwave_p.py | **✓** | | | |
| skills/*/SKILL.md ×9 (+ .agents mirrors via sync) | | **✓** | | |
| tests/test_pwave_f.py | | **✓** | | |
| README.md, README.ru.md, tests/test_pwave_r.py | | | **✓** | |
| .github/workflows/ci.yml, .agents/project_knowledge/boundaries.md | | | | **✓** (Red Zone, sanctioned) |

**Lane PM — manifests + version locks (locks FIRST, skipTest-guarded):**
1. `tests/test_pwave_p.py` BEFORE manifests: (a) version lock — both manifests' `version` == `templates/release_manifest.json.framework_version` (skipTest when a manifest is absent); (b) Agent Plugins contract (v2 §4.2): `$schema` + `name` required, closed 10-key top-level set, name regex `^[a-z0-9][a-z0-9.-]{0,63}$`, schema URL pinned; (c) Claude plugin contract: `name` (kebab) + `author.name` required, `version`/`homepage`/`repository`/`license` present; (d) marketplace contract: `name`, `owner.name`, `plugins[]` each with `name`+`source`.
2. Then the manifests (auditor A.1/A.2/A.3 verbatim structure, version = current `framework_version` from release_manifest — read it, do not hardcode): `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (source `"./"`), root `plugin.json` (`$schema` pinned to agent-plugins.org 1.0.0).
3. GREEN: locks stop skipping and pass; battery green.

**Lane PF — frontmatter ×9:**
1. Every `skills/*/SKILL.md` gains `license: MIT` and `compatibility: "Requires Python 3.10+ and Git"` (top-level frontmatter keys; descriptions untouched; NO `metadata.version` — version's single source stays release_manifest).
2. `tests/test_pwave_f.py`: all 9 skills carry both fields (glob skills/*/SKILL.md), no `metadata:` block with version anywhere, descriptions unchanged (compare against git HEAD via subprocess git show to prevent accidental description edits).
3. Mirrors: `python scripts/sync_templates.py --write` then `--check` → 0 drift (dev carries .agents/skills mirrors; resources byte-copies must not drift — if resources drift, that is init/manage SKILL.md frontmatter? NO — resources are templates/skill copies WITHOUT frontmatter needs; verify only, report if unexpected).

**Lane PR — README installation:**
1. README.md + README.ru.md: new `Installation` section after Introduction/before Usage (auditor §4.3 sketch): three channels — `claude plugin marketplace add vlv-code/meta-project` + `/plugin install meta-project`, `npx plugins add vlv-code/meta-project` (Agent Plugins 1.0.0: VS Code, Cursor, Copilot, Codex), `npx skills add vlv-code/meta-project` (skills.sh) — plus the NAMED per-skill caveat: per-skill installers copy skill folders only; `sync-architecture` is the single standalone skill; the other eight require the repository's `scripts/` and `templates/` — install the full plugin or package instead.
2. `tests/test_pwave_r.py`: both READMEs contain the section, the three channel commands, and the sync-architecture caveat.

**Lane PD — CI validation + boundaries refresh (Red Zone, sanctioned by owner decision; NO gate weakening — trusted-base materialization steps untouched):**
1. `boundaries.md` refresh: map `.claude-plugin/**` and `plugin.json` into Yellow Zone (packaging manifests: declarative metadata, version-locked by tests). One Opportunistic Refresh edit, minimal diff.
2. `ci.yml`: (a) a step running the in-repo contract tests over plugin manifests — they are part of the normal battery (no extra step needed if battery already runs; VERIFY and state it); (b) a NON-BLOCKING pinned external validator step (`npx --yes skill-validator@<pinned> check --strict ./skills/` or `skills-ref validate` — pick whichever command is real per auditor §А.4, pin exact version, `continue-on-error: true`, comment why); (c) an OPT-IN `workflow_dispatch` job `claude-validate` running `claude plugin validate --strict .` (separate job, never blocks; comment: requires Claude Code CLI, manual until validated).
3. `tests/test_gwave-style` not needed for PD; instead the lane verifies YAML loads as valid (python -c json? NO — YAML: validate structurally by careful minimal diff; ci.yml has no local parser) and reports the exact added lines.
4. SANCTION TEMPLATE (do NOT finalize): create `.github/red-zone-sanction.json` draft with base_sha PLACEHOLDER `<<BASE_SHA>>`, paths covering `scripts/check_boundaries.py`? — NO: only the paths this wave actually touches in the push: `.github/workflows/ci.yml`, `.agents/project_knowledge/boundaries.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin.json`, plus `README.md`, `README.ru.md`, `skills/*/SKILL.md` IF those are Red-Zone-matched (check: `*.md` in skills is Green — verify against boundaries.md and include only true red-zone paths; the gate only flags violations). authorized_by `vlv-code`, reason: "Wave P: plugin packaging (owner decision in-session 2026-11-17: 'это будет плагин'); expires with the bound revision." The DISPATCHER replaces the placeholder with the real pre-push HEAD at integration — the file must not carry a literal placeholder at close; emit the finalized file with base_sha filled from `git rev-parse HEAD` at your close and note it expires if more commits land before the push (dispatcher re-fills).

## 4. Integration (dispatcher)
Order: locks/tests land → manifests → frontmatter → README → CI+boundaries → sanction finalized (base_sha = `git rev-parse HEAD` at that moment) → sync 0 drift → full battery (expect green; commit-dependent e2 class self-closes at Steward commit) → boundaries audit 100% → synthetic sanction check (run trusted-gate command locally: materialize base policy, `--diff HEAD~0`? — replicate ci.yml's command with BASE_SHA = pre-push HEAD and verify pass) → Step 84 → packets (Guardian; Steward: commits per lane, alpha.7 bump of framework_version + both manifests via the lock, zips, push sequence dev→main each with own sanction; OWNER-VERIFY: `claude plugin marketplace add ./` + install locally; post-merge skills.sh re-index observation).

## 5. Sequential Prompts — embedded per lane in dispatch (flash workers), each: plan path, lane section, owned files, RED/lock-first for PM, battery-green close, report format.
