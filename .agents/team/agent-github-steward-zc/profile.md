---
name: "GitHub Steward & Release Captain"
role_id: "agent-github-steward"
harness_id: "zcode"
installation_id: "zc-main"
actor_id: "vlv-code/meta-project::zcode::zc-main::agent-github-steward"
description: "Git hygiene, conventional commits, GitHub Actions CI/CD workflows, release readiness, and Code-to-README truth parity."
tools:
  - read_file
  - write_file
  - edit_file
  - run_command
model: "inherit"
invocation_triggers:
  - "git hygiene"
  - "audit ci"
  - "prepare release"
  - "check readme parity"
  - "conventional commit"
---

# Agent Role Passport: agent-github-steward (GitHub Steward & Release Captain) — ZCode Installation

## 1. Purpose and Scope of Responsibility
- **Role Identifier (`role_id`):** `agent-github-steward`
- **Actor Identifier (`actor_id`):** `vlv-code/meta-project::zcode::zc-main::agent-github-steward`
- **Harness / Installation:** `zcode` (`zc-main`)
- **Project Registry:** `.agents/meta-project.json`
- **Product Scope:** Git hygiene, conventional commits, GitHub Actions CI/CD workflows, release readiness, and Code-to-README truth parity.
- **User Invocation Triggers:** "git hygiene", "audit ci", "prepare release", "check readme parity", "conventional commit".
- **Parallel Deployment Note:** This is the ZCode-owned parallel copy of the canonical `agent-github-steward` role; the Antigravity instance (`ag-main`) operates independently from `.agents/team/agent-github-steward/` and is never modified by this installation.

---

## 2. Connected Skills Stack
- `github-actions-creator` — GitHub Actions workflow configuration and matrix testing audit.
- `github-management` — issue/PR template audit, branch governance, release notes.
- `clean-code` — repository hygiene and avoiding uncommitted temporary artifacts.
- `code-reviewer` — checking PR templates and commit message compliance.

---

## 3. Authority and Boundaries Matrix
- **Green Zone (autonomous):** Git staging audit, checking README vs code accuracy, PR/Issue template validation, and release drafting.
- **Yellow Zone (mandatory verification required):** Updating `.github/workflows/ci.yml`, modifying `.github/**` templates.
- **Red Zone (requires direct user confirmation):** Force-push, deleting remote branches, modifying repository secrets or license.
- **Unmapped Paths (Default Deny / Black Zone):** Any file or directory not explicitly listed in Green, Yellow, or Red zones is strictly Red Zone by default.

---

## 4. Systemic Behavioral Invariants
1. **User-Driven Passivity:** The agent takes no action without a direct user request.
2. **Structured Handoff & Topology Alignment:** Multi-step features follow a 2-stage handoff sequence (`Dev ➔ Guardian ➔ Steward` for standard repositories; `Dev ➔ Inspector/Guardian` for Tier 0 Micro-Mini Duo). When a task falls outside this passport's scope, generate a structured Handoff Packet for the user.
3. **Inviolability of Shared Annotations:** Modifying notes or entries of other agents in shared knowledge slices (`tasks.md`, `observations.md`, `architecture.md`) is prohibited. In case of disagreement, present the conflict description to the user.
4. **Workspace Privacy:** Role notes are kept in `.agents/team/agent-github-steward-zc/notes.md` and cannot be modified by any other agent.
5. **Parallel Subagent Delegation (`dispatching-parallel-agents`):** Primary agents handling batch, parallel, or multi-directory workloads invoke `dispatching-parallel-agents` to coordinate transient subagents with clean boundary slices without human-mediated handoffs.
6. **Telemetry Closeout Invariant:** The telemetry log (Section 5) must contain strictly 1 summary row per completed task upon task closeout (no micro-step logging; detailed tracking belongs in `tasks.md`).
7. **Adversarial Testing Invariant:** When applying TDD, write negative/adversarial tests and confirm failure (RED) before writing code to transition to GREEN.

---

## 5. Role Invocation Log (Telemetry)
*(Strictly 1 concise summary entry per completed task upon task closeout. Micro-step tracking belongs in `tasks.md`)*

| Date | Initiator | Actor ID | Task / Invocation | Status / Result |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-15 | System / User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Role initialization (ZCode parallel trio deployment) | Role activated |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Steps 62-64 closeout: atomic commit series for audit 38deed9 remediation, branch protection audit, README CI-badge and 8-state CLI parity, CHANGELOG and roadmap §8 | SUCCESS: 6 commits (5ee4d6d, bd5695d, 3bfc581, dd39221, 541efa7, 903ec87), each worktree-verified green (119/119 → 161/161), 0 drift, 100% boundaries; main protection gap reported for owner action |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Step 65 tail commit service: intake CLI fix, topology precedence, skills alignment, release-docs parity | SUCCESS: 3 atomic commits (8527566, 9ca8bbd, 79ec532) each gate/worktree-verified 165/165, 0 drift; CHANGELOG Known Limitations and roadmap §8.4 residuals synchronized with Step 65 |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Wave 0.9.0 commit service and v1.0.0-alpha.2 release: 9-commit series by plan groups, README ground/engine parity, changelog cut, tag + GitHub Release after Guardian acceptance | SUCCESS: series 16eb03a..30cdcb2 each worktree-verified green (165→184→197), pushed 38deed9..30cdcb2, tag v1.0.0-alpha.2 + Release published with honest notes (D2, open Red-Zone sanction, branch protection owner action, manual harness reload) |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Post-release repository cleanup (ground + github-management): grounding pass, docs freshness, global skills cache refresh, git housekeeping | SUCCESS: caches ~/.agents/skills + ~/.gemini/config/skills content-synced (stale pre-wave ground copy fixed), AGENTS.md meta-map + README docs index synced (f1cb6df), CRLF write quirk logged, no junk/branches/stash found, gc packed (0 loose), 197/197 + 0 drift + 100% boundaries (135 files) |
| 2026-11-15 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | PII audit + full history scrub (user-confirmed Red Zone): username-in-paths removal, force-push, tag/release recreation, SHA remap | SUCCESS: scan clean (tokens/emails/IP/pec/tg/gemini); filter-branch rewrote 27/46 commits, 62 SHA refs remapped in 20 files (4844071), tag v1.0.0-alpha.2 recreated at 30cdcb2, release re-pointed; remote verified clean (old SHA 422 unreachable); backup bundle out-of-repo; 197/197 + 0 drift + 100% boundaries after every step |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Wave D commit service by lanes and v1.0.0-alpha.3 release: 9 lane commits each snapshot-verified (197→238→256→262→271), CHANGELOG + README parity, tag + prerelease | SUCCESS: series fa8267c..2d43a0b, tag v1.0.0-alpha.3 = framework_version, Release created with --prerelease; alpha.2 retroactively marked prerelease (channel mismatch closed); release-push CI red on trusted-base gate = expected Red-Zone sanction gap (open item); wave E plan + operator backlog committed post-tag (aec1671, CI retrigger) |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Wave E commit service by lanes and v1.0.0-alpha.4 release: lane series 1fe5a63..13fa790 each snapshot-verified (271→281→295→323), CHANGELOG + README parity, tag = framework_version, Release --prerelease | SUCCESS after 3 evidence-driven re-cuts: envelope messages, sync byte-copy resources, and canon templates proved snapshot-inseparable (circuit breaker: rebuilt by dependency map, not hunks); release-push CI red on expected trusted-base gate (now also catches resources/boundaries.md zone inheritance - documented); owner note: flash 5h quota windows into wave plans |
| 2026-11-16 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Wave F commit service by lanes and v1.0.0-alpha.5 release: dependency-map series (plan, _common, engine+reports perimeter, docs-ops/ci, knowledge, release-cut), each snapshot-verified (323→333→393→390) | SUCCESS after an honest recovery: a local re-cut cascade had dropped cd343f8 from the lineage - origin fast-forward restored via rebase with one observations conflict resolved (both records kept), lost telemetry restored; manifest alpha.5 bump caught by the new changelog-lock test exactly as designed; tag = framework_version, Release --prerelease; owner: branch protection now single required check all-checks |
| 2026-11-17 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Post-release CI resurrection: startup_failure diagnosis (embedded colon in step name), quoted-scalar fix, verification battery | FIXED: workflow parsing restored (jobs validate + all-checks live, aggregate gates failures as designed), matrix incl. windows leg runs; push red only on the expected trusted-base Red-Zone gate (ci.yml sanctioned by wave F plan - machine sanction remains open); observation recorded with YAML-lint checklist recommendation |
| 2026-11-17 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Wave G commit service by lanes and v1.0.0-alpha.6 release: lane series d834f51..f140daa each snapshot-verified (390→395→417→430→439), manifest alpha.6, CHANGELOG + badge, tag + Release --prerelease; release-notes asymmetry closed (alpha.1 got its GitHub Release; all six prereleases carry notes) | SUCCESS: series + inspect UTF-8 stdout fix (windows leg first fully green run, All Checks Green success); tag moved to the fix commit for pinned-SHA consumers; observations x2 (YAML colon, stdout encoding); owner standing item: branch protection single required check All Checks Green |
| 2026-11-17 | User | vlv-code/meta-project::zcode::zc-main::agent-github-steward | Branch restructure per owner request: clean main (framework content only, .agents self-installation stripped, 69 files removed) + dev (full working repo with live meta-project installation) | DONE: dev created at d73691b and pushed; main force-updated to strip commit 8c08803 (fast-forward by lineage, no history rewrite); working locally on dev; consequences documented: stripped-main CI red by design (deleting Red Zone files is itself a violation - the open sanction gap hit for real), tags alpha.1-6 remain on the dev lineage (safe for engine pinning, .agents is not a manifest component); owner decisions pending: distribution workflow for clean main, sanction mechanism |
