# Agent Observations Base

Cumulative registry of findings, non-obvious environment quirks, and practical solutions.
Entries are logged strictly via the `record-observation` skill in a concise table format (1 line per fact).

---

| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-06 | [init] | repo/init | Meta-project agent environment initialization | Deployed knowledge slices and local skills |
| 2026-11-06 | [boundaries] | templates/boundaries.md | Placing tests/** in green zone leads to test emasculation anti-pattern | Universal 3-tier model: new tests in green, regression suite in yellow with assert-preservation, contract/integrity tests in red |
| 2026-11-07 | [env] | repo/root | Residual empirical test files masked by .gitignore require explicit cleanup before release | Inspect ignored files via git status --ignored and confirm safe removal |
| 2026-11-07 | [orchestration] | skills/dispatching-parallel-agents | Batch file modifications cause serialization lag in single agent sessions | Split batch tasks across parallel subagents by non-overlapping directories |
| 2026-11-07 | [ci] | .github/workflows/ci.yml | Ignoring '**.md' in paths-ignore completely disables CI in markdown-based skill/template repos | Replaced '**.md' with explicit docs ignore list (resolved 2026-11-10) |
| 2026-11-07 | [decommission] | .agents/team | Batch archival of 6 roles into team/archive/ for re-deployment | Atomic move preserves notes and telemetry without data loss |
| 2026-11-09 | [incident] | docs/decisions_and_roadmap.md | Polyglot Monorepo Incident: agent screenshot hallucination, unmapped boundary breach, and ritualistic execution | Documented polyglot monorepo incident analysis and 7 systemic framework improvements in decisions_and_roadmap.md |
| 2026-11-10 | [orchestration] | skills/lifecycle | Tri-skill lifecycle suite (scan, tune, update) | Implemented with dual-path script detection, local_repo_data dual syntax, and offline fallback |
