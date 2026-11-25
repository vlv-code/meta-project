# Design Spec: Wave Z3 — Thin Harness Hooks Ecosystem & Update Artifact Hygiene

- **Date:** 2026-11-25
- **Status:** Approved by owner (design choices: Option A, Red-Zone policy `deny` default + `--red-policy ask` for Claude Code / ZCode / Gemini CLI, `capabilities.hooks` option 2B)
- **Roadmap Reference:** `docs/decisions_and_roadmap.md` (§7.1 ADR #14, §7.3 P2.1–P2.3, §9 Audit #4 Variant A, §11.3 Wave Z3)
- **Baseline:** `v1.0.0-alpha.9` (`af03cb0`)
- **Red Zone Impact:** **None.** `hooks/**` is already mapped in Yellow Zone (`.agents/project_knowledge/boundaries.md:34`). `scripts/check_boundaries.py` (Red Zone) is imported/invoked read-only without modification.

---

## 1. Goals & Non-Goals

### Goals
1. Provide a **zero-dependency** (Python 3.10+ stdlib), cross-platform (Windows + Linux/macOS) thin hook layer in `hooks/` delegating 100% of policy logic to existing `scripts/*.py` engines.
2. Support **6 harnesses** (`claude-code`, `zcode`, `cursor`, `gemini`, `copilot`, `codex`) plus local Git `pre-commit` via a single non-destructive installer (`hooks/install.py`: `install`, `verify`, `uninstall`).
3. Ship a native Claude Code plugin manifest (`hooks/hooks.json`) with a **strict silent no-op guard** outside Meta-Project repositories.
4. Close `§11.3 item 5` (update-engine temporary artifact hygiene in `init-meta-project` `.gitignore` block and `update-meta-project/SKILL.md`).

### Non-Goals
- No OS-level sandboxing of arbitrary `Bash` writes (`git pre-commit` + CI trusted-base remain the backstop per `docs/framework_philosophy_and_vision.md §3.1`).
- No hooks attached to the interactive `Stop` event (prohibited by `docs/framework_philosophy_and_vision.md §3.2`).
- No third-party runtime dependencies (`jq`, Node.js, bash-only wrappers).

---

## 2. File Layout & Distribution

```text
hooks/
├── dispatch.py    # Unified stdlib event dispatcher (PreToolUse / PostToolUse / SessionStart)
├── install.py     # Idempotent installer, live dry-run verifier, clean uninstaller + git pre-commit
├── hooks.json     # Native Claude Code plugin hook manifest (${CLAUDE_PLUGIN_ROOT}/hooks/dispatch.py)
└── README.md      # Protocol specification, per-harness caveats, security boundaries, CLI examples
```

### Packaging & Manifest Wiring
- **`scripts/sync_dist_branch.py`:** Add `"hooks"` to `DIST_PATHS` so `main` ships `hooks/` to plugin channels.
- **`templates/release_manifest.json`:** Register:
  - `hooks/dispatch.py` (`kind: "script"`, `requires: ["scripts/check_boundaries.py", "scripts/inspect_meta_project.py", "scripts/compact_memory.py", "scripts/triage_incident.py", "scripts/_common.py"]`)
  - `hooks/install.py` (`kind: "script"`, `requires: ["hooks/dispatch.py", "scripts/check_boundaries.py", "scripts/_common.py"]`)
  - `hooks/hooks.json` (`kind: "resource"`, `requires: ["hooks/dispatch.py"]`)
  - `hooks/README.md` (`kind: "resource"`, `requires: ["hooks/install.py"]`)

---

## 3. Component 1: `hooks/dispatch.py`

### CLI Contract
```bash
python hooks/dispatch.py \
  --harness <claude-code|zcode|cursor|gemini|copilot|codex> \
  --event <pre-tool-use|post-tool-use|session-start> \
  [--with-read-gate] \
  [--red-policy <deny|ask>]
```

### Global Invariants
1. **Strict `stdout` Purity (Gemini CLI Golden Rule):** Emit **exactly one valid JSON object** on `stdout` per invocation. Any internal calls to `scripts/*` MUST suppress/redirect accidental `stdout` (e.g. `contextlib.redirect_stdout(io.StringIO())`). Diagnostics and errors go strictly to `stderr`.
2. **Repo Root Discovery & Silent No-Op Guard:**
   - Resolve working directory from `payload.get("cwd")` (fallback: `Path.cwd()`).
   - Walk upward (bounded by git root / filesystem root) looking for `.agents/project_knowledge/boundaries.md`.
   - If not found (non-Meta-Project repository): immediately emit a harness-valid `allow` / empty response and exit `0` (zero latency, zero noise, zero disk writes).
3. **Zero-Write Read-Only Safety:** `session-start` and non-read-gate `pre-tool-use` MUST perform zero disk writes and create zero `.lock` files.

### Event 1: `pre-tool-use` (Boundary Gate, P2.2 + Opt-In Read-Journal Gate)
- **Path Extraction:**
  - Inspect `payload.get("tool_input")` (dict) for candidate path keys: `file_path`, `path`, `TargetFile`, `target_file`, `AbsolutePath`, `Path`, `file`.
  - For Codex `apply_patch` payloads (string or `tool_input.input`/`patch`), parse `*** (Update|Add|Delete) File: <path>` headers and validate **every** touched path (most restrictive zone wins: `black`/`red` > `yellow` > `green`).
  - If the tool call does not target a path inside `repo_root` (or is a non-file / read-only tool) → silent `allow` (`exit 0`).
- **Zone Classification:**
  - Read `<repo_root>/.agents/project_knowledge/boundaries.md` and call `check_boundaries.parse_boundaries(content)` + `check_boundaries.classify_path(rel_path, zones)`.
  - If `boundaries.md` exists but fails to read/parse or payload JSON is malformed inside a Meta-Project repo → **fail-closed `deny`**.
- **Decision Matrix:**
  - **`green`:** `allow` (silent, `rc=0`).
  - **`yellow`:**
    - If `--with-read-gate` is enabled AND `session_id` is present in payload:
      - Check temp read journal (`<tempdir>/meta-project-reads-<sha256(repo_root + ":" + session_id)[:16]>.txt`, never inside the repository).
      - Require `.agents/project_knowledge/boundaries.md` to be recorded as read in this session.
      - If `<repo_root>/.agents/project_knowledge/weak_spots.md` exists and mentions `rel_path` (or its parent component name), also require `.agents/project_knowledge/weak_spots.md` in the read journal.
      - Missing required slice → **`deny`** with explicit guidance naming the unread slice(s).
    - Otherwise → `allow` (optionally with a 1-line Yellow-Zone test reminder in context/systemMessage).
  - **`red` or `black` (Default Deny):**
    - If `os.environ.get("META_PROJECT_ALLOW_RED_ZONE") == "1"` → `allow` (explicit local operator override, matching `check_boundaries.py --staged`).
    - Else if `--red-policy == "ask"` AND `--harness in ("claude-code", "zcode", "gemini")` → emit harness-native **`ask`** decision (`exit 0`, forces interactive user confirmation).
    - Else (default `deny`, and **fail-closed fallback to `deny`** for `cursor`, `copilot`, `codex` even if `--red-policy ask` is passed) → emit harness-native **`deny`** decision with matched zone/pattern and remediation hint.

### Event 2: `post-tool-use` (Opt-In Read-Journal Recorder, `--with-read-gate`)
- Triggered only when `--with-read-gate` is enabled.
- Recognizes read tools (`Read`, `read_file`, `view_file`, `GetFile`).
- Extracts target path, normalizes relative to `repo_root`, and appends to `<tempdir>/meta-project-reads-<sha256(repo_root + ":" + session_id)[:16]>.txt` (deduplicated, capped at 512 entries, outside Git).
- If `session_id` is absent or tool is not a read tool → silent no-op (`exit 0`, `{}`).

### Event 3: `session-start` (Compact Context Injection, P2.3)
- Strictly read-only (`0` writes, `0` `.lock` files).
- Gathers:
  1. `inspect_meta_project.inspect_repository(...)` → `state`, `project_id`, `facts_digest` (short slice digest).
  2. `triage_incident` (`check-tasks` logic on `.agents/project_knowledge/tasks.md` if present) → count/IDs of open `unverified_hypotheses` and `thrashing_ids` (prevents epistemic laundering across session restarts).
  3. `compact_memory` (read-only threshold check on `observations.md` and `tasks.md`) → 1-line advisory alert if compaction is recommended.
- **Hard Budget:** Rendered context MUST be `<= 4000` characters (`< 1500` tokens), deterministically truncated with an explicit ellipsis marker if ever exceeded.

### Per-Harness Output Mapping Table

| Harness | `allow` (`PreToolUse`) | `deny` (`PreToolUse`) | `ask` (`PreToolUse`) | `SessionStart` output |
| :--- | :--- | :--- | :--- | :--- |
| `claude-code`, `zcode` | `rc=0`, `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}` | `rc=2`, `stderr` reason + `stdout` JSON `permissionDecision: "deny"` with `permissionDecisionReason` | `rc=0`, `permissionDecision: "ask"` with `permissionDecisionReason` | `rc=0`, `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"..."}}` |
| `gemini` | `rc=0`, `{"decision":"allow"}` | `rc=0`, `{"decision":"deny","reason":"...","systemMessage":"..."}` | `rc=0`, `{"decision":"ask","reason":"...","systemMessage":"..."}` | `rc=0`, `{"systemMessage":"..."}` |
| `cursor` | `rc=0`, `{"permission":"allow"}` | `rc=2`, `{"permission":"deny","user_message":"...","agent_message":"..."}` | Fail-closed → `deny` (`rc=2`) | `rc=0`, `{"additionalContext":"..."}` |
| `copilot` | `rc=0`, `{"permissionDecision":"allow"}` | `rc=2`, `{"permissionDecision":"deny","permissionDecisionReason":"..."}` | Fail-closed → `deny` (`rc=2`) | `rc=0`, `{"additionalContext":"..."}` |
| `codex` | `rc=0`, `{"decision":"allow"}` | `rc=2`, `{"decision":"block","reason":"..."}` | Fail-closed → `deny` (`rc=2`) | `rc=0`, `{"additionalContext":"..."}` |

---

## 4. Component 2: `hooks/install.py` (`P2.1`)

### CLI Contract
```bash
python hooks/install.py install   --harness <claude-code|zcode|cursor|gemini|copilot|codex|all> [--repo-root .] [--with-read-gate] [--red-policy deny|ask] [--no-git-hook]
python hooks/install.py verify    --harness <...|all> [--repo-root .]
python hooks/install.py uninstall --harness <...|all> [--repo-root .] [--with-git-hook]
```

### Target Config Files & Merging Rules
- `claude-code` / `zcode` → `.claude/settings.json` (merges under `hooks.PreToolUse`, `hooks.SessionStart`, and `hooks.PostToolUse` when `--with-read-gate`).
- `cursor` → `.cursor/hooks.json` (`version: 1`, `hooks.preToolUse` with `"failClosed": true`, `hooks.sessionStart`, and `hooks.postToolUse` when `--with-read-gate`).
- `gemini` → `.gemini/settings.json` (`hooks.BeforeTool` matcher `"write_file|replace|replace_string|edit_file"`, `hooks.SessionStart` matcher `"startup"`, and `hooks.AfterTool` when `--with-read-gate`).
- `copilot` → `.github/hooks/meta-project.json` (`version: 1`, `hooks.preToolUse`, `hooks.sessionStart`; BOTH `"bash"` and `"powershell"` command keys populated).
- `codex` → `.codex/hooks.json` (`hooks.PreToolUse`, `hooks.SessionStart`; prints clear notice that Codex requires one-time `/hooks` trust in TUI).

### Non-Destructive Idempotency & Cleanup
- Every Meta-Project hook entry is identified by the deterministic marker substring `hooks/dispatch.py` (with `--harness`).
- **`install`:** Reads existing JSON (if present; fails closed on invalid JSON rather than overwriting!), replaces/updates ONLY Meta-Project entries, preserves all user hooks intact, writes atomically. Unless `--no-git-hook` is set, also calls `check_boundaries.install_git_hook(...)` (ADR #17 safe chaining) and reports status.
- **`uninstall`:** Removes ONLY entries matching our marker, preserving all other keys and user hooks. Removes `.github/hooks/meta-project.json` cleanly when empty. Does not touch git `pre-commit` unless `--with-git-hook` is passed (and then restores legacy hook if present).
- **`verify`:** Checks config syntax + marker presence + runs **3 live dry-run probes** through `hooks/dispatch.py` with synthetic `stdin` JSON:
  1. `session-start` → valid JSON, `rc=0`, output length `<= 4000` chars;
  2. `pre-tool-use` on a Green path → `allow`, `rc=0`;
  3. `pre-tool-use` on a Red path (`scripts/check_boundaries.py` or `LICENSE`) → `deny`/`ask` (matches configured `--red-policy`).
  Prints explicit ZCode live-session verification note when verifying `--harness zcode`.

---

## 5. Component 3: Native Plugin Manifest `hooks/hooks.json`

- Placed at `hooks/hooks.json` for Claude Code plugin auto-discovery.
- Uses `${CLAUDE_PLUGIN_ROOT}/hooks/dispatch.py` (with `python3` / `python` portable command invocation) for `SessionStart` and `PreToolUse` (`matcher: "Edit|Write|MultiEdit"`), default `--red-policy deny`.
- Safe in every non-Meta-Project repository due to `dispatch.py`'s silent no-op guard when `.agents/project_knowledge/boundaries.md` is absent.

---

## 6. Component 4: Inspector `capabilities.hooks` Update (Choice `2B`)

- File: `scripts/_inspect_classifier.py` (`evaluate_capability_matrix`).
- Detect both:
  1. Local Git `pre-commit` hook containing `check_boundaries` (existing check).
  2. Installed harness hook adapters in `repo_root` referencing `hooks/dispatch.py` across `.claude/settings.json`, `.cursor/hooks.json`, `.gemini/settings.json`, `.codex/hooks.json`, `.github/hooks/meta-project.json`.
- **Status rule (`2B`):** `CapabilityStatus.AVAILABLE` if **either** Git `pre-commit` **or** ≥1 harness hook adapter is detected; `UNAVAILABLE` only when neither is present.
- **`detail` string:** Explicitly states which layers are active (e.g. `"Git pre-commit + harness hooks active (claude-code, cursor)"`, `"Git pre-commit hook incorporates check_boundaries"`, or `"Harness hooks active (claude-code); git pre-commit not installed (recommended for Bash-write backstop)"`).
- `--facts-digest` top-level JSON keys remain strictly unchanged.

---

## 7. Component 5: Update Engine Artifact Hygiene (§11.3 Item 5)

- **`skills/init-meta-project/SKILL.md`:** Extend the append-if-absent `.gitignore` hygiene block with:
  ```gitignore
  .agents/update-engine.lock
  .agents/update-plan.json
  .agents/update-journal.json
  ```
- **`skills/update-meta-project/SKILL.md`:** Explicitly state in the closeout/commit guidance:
  - Commit persistent audit/lock state: `.agents/framework-lock.json`, `.agents/reports/*/update/*.json`.
  - Do NOT commit transient session files: `.agents/update-engine.lock`, `.agents/update-plan.json`, `.agents/update-journal.json`.
- Run `python scripts/sync_templates.py --write` to keep all mirrors and resources in 0 drift.

---

## 8. Testing & Verification Strategy (`tests/test_hooks.py`)

New canonical domain suite `tests/test_hooks.py` (Green Zone, zero-dependency, RED-first TDD):
1. **Dispatcher unit & adversarial tests:**
   - All 6 harnesses (`claude-code`, `zcode`, `cursor`, `gemini`, `copilot`, `codex`) × (`green` allow, `yellow` allow, `red` deny, `black` Default Deny, `META_PROJECT_ALLOW_RED_ZONE=1` override).
   - `--red-policy ask`: returns `ask` on `claude-code`/`zcode`/`gemini`; fails closed to `deny` on `cursor`/`copilot`/`codex`.
   - Codex `apply_patch` multi-file patch targeting 1 Green + 1 Red file → denied (most restrictive wins).
   - Gemini `stdout` purity: strictly 1 valid JSON object on `stdout`, zero stray text even on warnings/errors.
   - Non-Meta-Project directory (no `boundaries.md`) → silent no-op `allow` (`rc=0`).
   - Malformed JSON / broken `boundaries.md` inside Meta-Project repo → fail-closed `deny`.
   - `session-start`: read-only (0 writes, 0 `.lock`), `<= 4000` chars, surfaces open `unverified_hypotheses` from `tasks.md` and `compact_memory` advisory alert when thresholds exceeded.
   - `--with-read-gate`: `post-tool-use` records read in `%TEMP%` (never in repo); `pre-tool-use` blocks Yellow write until `boundaries.md` is read, then allows; handles missing `session_id` cleanly.
2. **Installer lifecycle tests (`hooks/install.py`):**
   - `install` → `verify` → idempotent re-`install` → `uninstall` across all 6 harnesses; preserves pre-existing user hooks intact; fails closed on corrupted existing JSON.
   - Copilot manifest carries both `bash` and `powershell`; Cursor manifest sets `failClosed: true`.
   - Git `pre-commit` hook installation (and `--no-git-hook` skip).
3. **Inspector & packaging tests:**
   - `tests/test_inspect_meta_project.py`: `capabilities.hooks` returns `available` with harness hook only (`2B`), with git `pre-commit` only, and with both; returns `unavailable` with neither.
   - `tests/test_manifests_and_packaging.py`: `hooks/` registered in `templates/release_manifest.json` (`requires` graph valid) and included in `scripts/sync_dist_branch.py` `DIST_PATHS`.
   - `tests/test_skills_and_templates_contracts.py`: update artifact `.gitignore` + `update-meta-project/SKILL.md` hygiene clause locked.
