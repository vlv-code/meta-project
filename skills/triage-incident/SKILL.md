---
name: triage-incident
license: MIT
compatibility: "Requires Python 3.10+ and Git"
description: >-
  Evidence-first epistemic triage for split-runtime and silent-failure incidents:
  enforces empirical artifact checks, unmasked stderr capture, PROBE -> record-evidence -> promote
  gating via triage_incident.py, diagnostic Circuit Breaker, and Error-Path / Fallback-Masking audits.
---

# Incident Triage: Evidence-First Diagnostics & Split-Runtime Verification

Autonomous triage protocol preventing premature dispatch, speculative task churn, and silent fallback masking when debugging build pipelines, multi-container runtimes, or cross-toolchain failures.

---

## When to invoke skill

* The user asks to investigate, diagnose, or explain a silent failure, stale/template output, or split-runtime error ("посмотри в чем проблема", "triage incident", "debug silent failure", "why output is stub").
* A hypothesis about a defect was refuted, revised repeatedly, or contradicts code expectations.
* Diagnosis spans separate runtimes (e.g., local repo + container CLI, host IDE + remote build worker).

---

## Execution steps

**Core Epistemic Rule:** `Hypothesis != Fact`. NEVER create `- [ ] FIX` tasks, emit fix prompts, or declare `root cause` / `proven` / `финал` before empirical `evidence:` is recorded via `scripts/triage_incident.py`.

### Phase 0: Anti-Action-Bias & Scope Check
1. Audit existing task state read-only:
   ```bash
   python scripts/triage_incident.py check-tasks --tasks .agents/project_knowledge/tasks.md --json
   ```
2. Verify specialization (`Toolchain Handoff Tripwire`): if the failure lies in a foreign/external toolchain outside your role's Connected Skills Stack, restrict your work to `mode: investigate` (`Probe Bundle`: symptom + 1-step discriminator probes + refuting conditions — NEVER speculative fix code/prompts).
3. Register the diagnostic probe FIRST (never `- [ ] FIX`):
   ```bash
   python scripts/triage_incident.py probe --tasks .agents/project_knowledge/tasks.md \
     --actor <actor_id> --id <INC-id> --symptom "<symptom>" \
     --hypothesis "<testable hypothesis>" --discriminator "<1-step command>"
   ```
   *(Diagnostic Circuit Breaker: revising `<INC-id>` a second time without running `record-evidence` first fails closed with `[TRIAGE_CIRCUIT_BREAKER]`.)*

### Step 1: Artifact Identity (`artifact`)
Inspect actual output bytes before proposing causes or editing source files:
```bash
python scripts/triage_incident.py artifact --path <output_artifact> --compare <template_or_baseline> --json
```
Check `size_bytes`, `sha256`, `mtime_utc`, and whether `comparison` is `IDENTICAL_BYTES` (indicating an overwritten/pre-filled template fallback) or `DIFFERS`. File presence alone is NOT proof of a fresh build.

### Step 2: Runtime & Toolchain Presence
Verify environment parity in the **actual target runtime** (not host shell assumptions): confirm binary presence (`which <cli>` / `--version`), working directory, mount paths, and environment variables across the runtime boundary.

### Step 3: Unmasked Execution & Stderr Capture
Run or request a 1-step discriminating probe command capturing **raw `exit_code`, `stdout`, and `stderr`** directly from the failing CLI/runtime. Never treat unit tests, mocked calls, or swallowed `catch` logs as runtime proof.

### Step 4: Code-to-Fact Mapping & Error-Path / Fallback-Masking Audit
Trace BOTH execution paths against the captured output:
- **Data Path:** `Origin ➔ Transport ➔ Persistence ➔ Consumer`.
- **Error-Path / Fallback-Masking Audit:** `CLI exit/stderr ➔ pipe/wrapper capture ➔ catch-all / silent swallow ➔ template pre-fill / fallback ➔ verification log`. Locate ALL sibling call sites exhibiting the same pattern.

Then lock the fact atomically in `tasks.md`:
```bash
python scripts/triage_incident.py record-evidence --tasks .agents/project_knowledge/tasks.md \
  --actor <actor_id> --id <INC-id> --command "<executed command>" \
  --observed "<exact exit/stderr/hash observation>" --artifact <optional_path>
```

### Phase 5: Gated Promotion to `FIX` (`promote`)
Only AFTER empirical `evidence:` is recorded, promote `- [?] PROBE` to `- [ ] FIX` and generate the structured Handoff Packet:
```bash
python scripts/triage_incident.py promote --tasks .agents/project_knowledge/tasks.md \
  --actor <actor_id> --id <INC-id> --root-cause "<verified cause>" \
  --fix-scope "<minimal files>" --target-role <agent-role>
```
*(Calling `promote` without recorded `evidence:` fails closed with `rc=1` and `[EVIDENCE_REQUIRED]`.)*
