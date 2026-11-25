# Meta-Project Thin Harness Hooks Ecosystem

The `hooks/` layer provides a **zero-dependency** (Python 3.10+ standard library), cross-platform (Windows, Linux, macOS) hook integration connecting AI coding harnesses directly to Meta-Project governance policies.

---

## 1. Architecture & Design Principles

1. **Thin Adapter Pattern:** The hooks layer contains **no duplicate policy engines**. It directly imports and delegates to the established Meta-Project scripts (`scripts/check_boundaries.py`, `scripts/inspect_meta_project.py`, `scripts/compact_memory.py`, `scripts/triage_incident.py`).
2. **Strict `stdout` Purity (Gemini CLI Golden Rule):** Every hook event emits **strictly one valid JSON object** on `stdout`. All diagnostic logs and errors are routed to `stderr`. Internal script invocations redirect and suppress standard output.
3. **Silent No-Op Outside Meta-Project Repositories:** When executed outside a repository containing `.agents/project_knowledge/boundaries.md`, `hooks/dispatch.py` immediately exits `0` with an empty or `allow` response without writing any files or generating latency.
4. **Zero-Write Read-Only Safety:** `session-start`, `pre-tool-use`, and `pre-compact` perform zero filesystem writes and create zero `.lock` files. `post-tool-use-failure` operates strictly via a temporary directory sliding window without touching the repository.

---

## 2. Supported Harnesses & Matrix

| Harness | Configuration File | Supported Events | PreToolUse Decision | Ask Policy | SessionStart Injected Context |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `claude-code` | `.claude/settings.json` | `SessionStart`, `PreToolUse` (`Edit`, `Bash`), `PostToolUseFailure`, `PreCompact` | `allow` / `deny` (`rc=2`) | Supported (`ask`) | `hookSpecificOutput.additionalContext` |
| `zcode` | `.claude/settings.json` | `SessionStart`, `PreToolUse` (`Edit`, `Bash`), `PostToolUseFailure`, `PreCompact` | `allow` / `deny` (`rc=2`) | Supported (`ask`) | `hookSpecificOutput.additionalContext` |
| `cursor` | `.cursor/hooks.json` | `sessionStart`, `preToolUse` | `allow` / `deny` (`rc=2`, `failClosed: true`) | Fail-closed → `deny` | `additionalContext` |
| `gemini` | `.gemini/settings.json` | `SessionStart`, `BeforeTool`, `AfterTool` | `allow` / `deny` (`rc=0`) | Supported (`ask`) | `systemMessage` |
| `copilot` | `.github/hooks/meta-project.json` | `sessionStart`, `preToolUse` | `allow` / `deny` (`rc=2`) | Fail-closed → `deny` | `additionalContext` |
| `codex` | `.codex/hooks.json` | `SessionStart`, `PreToolUse` | `allow` / `block` (`rc=2`) | Fail-closed → `deny` | `additionalContext` |

---

## 3. Security Boundaries & Important Caveats

1. **Bash Anti-Bypass Guard:** `PreToolUse` hooks targeting `Bash` actively intercept and reject known safety bypasses:
   - `git commit --no-verify` or `git commit -n` (prevents bypassing Git pre-commit boundary checks).
   - `git push --force`, `-f`, or `--force-with-lease` (prevents destructive remote rewrites).
   - Safe shell commands (`git status`, `git diff`, test runners, linters) execute unhindered.
   - Arbitrary shell mutations outside git remain caught by the git pre-commit hook and CI boundary gates (defense-in-depth).
2. **Circuit Breaker Sliding Window:** `PostToolUseFailure` maintains a 5-minute sliding window cache in the OS temp directory (`%TEMP%` / `/tmp`). When the same tool fails >=2 times, an advisory circuit-breaker message advises stopping blind iterative changes and using `triage-incident`.
3. **Pre-Compact & Grounding:** `PreCompact` checks for unverified open diagnostic probes (`DIAG-*`) and memory table sizes before compaction. `SessionStart` provides Post-Compaction Grounding to distinguish verified facts from unverified hypotheses.
4. **Codex CLI Trust:** Codex requires an interactive one-time `/hooks` command approval in its TUI before hooks in `.codex/hooks.json` are activated.
5. **ZCode Verification:** Verified using synthetic dry-run probes against `.claude/settings.json` hook schemas; live execution should be confirmed inside an active ZCode Desktop session.
6. **ADR #15 Read Permissions Invariant:** Read-only inspection tools (`Read`, `read_file`, `grep`, `glob`, `list_dir`) are never restricted by boundary gates even when targeting Red Zone files. This ensures agents can read boundaries and weak spots without deadlocking.

---

## 4. CLI Usage

### Installation (`hooks/install.py`)

```bash
# Install hooks for a specific harness (chains git pre-commit by default)
python hooks/install.py install --harness claude-code

# Install hooks for all supported harnesses without git hook (deduplicates claude-code / zcode settings)
python hooks/install.py install --harness all --no-git-hook

# Install with interactive confirmation for Red Zone files
python hooks/install.py install --harness cursor --red-policy ask

# Install with opt-in read journal gating for Yellow Zone files
python hooks/install.py install --harness claude-code --with-read-gate
```

### Verification (`hooks/install.py verify`)

Runs syntax checks, marker validation, and 5 live dry-run probes (`session-start`, `pre-tool-use` green allow, `pre-tool-use` red deny/ask, `pre-tool-use` read on Red Zone per ADR #15, and `pre-tool-use` Bash anti-bypass guard):

```bash
python hooks/install.py verify --harness claude-code
python hooks/install.py verify --harness all
```

### Uninstallation (`hooks/install.py uninstall`)

Safely removes only Meta-Project hook entries, leaving user hooks and custom configuration keys intact:

```bash
python hooks/install.py uninstall --harness claude-code
python hooks/install.py uninstall --harness all --with-git-hook
```

### Event Dispatcher (`hooks/dispatch.py`)

Direct dispatcher invocation (normally invoked by harness runner via `stdin`):

```bash
python hooks/dispatch.py --harness claude-code --event pre-tool-use
python hooks/dispatch.py --harness cursor --event session-start
python hooks/dispatch.py --harness gemini --event pre-tool-use --with-read-gate
```
