# Open Competency Catalog (Role Matrix & Competency Guidelines)

## Overview

The catalog below is an **Open Competency Catalog**, not an immutable closed enum. Agents have full autonomy to synthesize combined roles or invent custom, domain-specific roles (e.g., `agent-solana-smart-contracts`, `agent-3d-designer`, `agent-data-pipeline`) matching the repository's real architecture.

---

## 1. Role Matrix

| Role | Deploy when (repository markers) | Stack skills | Red-zone defaults (never autonomous) |
| :--- | :--- | :--- | :--- |
| `agent-general-worker` | Any project — fundamental default role | `clean-code`, `code-reviewer`, `systematic-debugging` + stack skills | destructive actions; specialized domain modules without Handoff |
| `agent-intake-dispatcher` | Any project with 2+ roles; executed by a role session or by the harness's native orchestrator (binding above) | `prompt-engineering`, `brainstorming`, `triage-incident` | direct modification of project source code; speculative fix prompts on unverified hypotheses |
| `agent-meta-guardian` | `meta-project` structure present | `clean-code`, `code-reviewer` | deleting the knowledge base without user confirmation |
| `agent-consensus-judge` | Contested decisions | `architecture-decision-records`, `api-design-principles` | decisions without empirical evidence |
| `agent-deep-auditor` | Mature codebase (>500 lines) | `systematic-debugging`, `code-reviewer` | destructive refactorings, autonomous file deletion |
| `agent-product-roaster` | Product services, startups | `search_web`, `brainstorming` | changing business logic without specifications |
| `agent-creative-director` | UI components, web, themes, icons | `image-generator`, `css-tokens` | replacing brand identity without confirmation |
| `agent-ui-ux-engineer` | Frontend, bots, interfaces | `semantic-html`, `css-coder`, `ui-ux-invariants` | removing confirmations for destructive actions |
| `agent-legal-compliance` | `LICENSE`, public repositories | SPDX/SBOM audit | changing repository license |
| `agent-github-steward` | `.github/`, git remotes | `github-management`, `github-actions-creator`, `clean-code`, `code-reviewer` | force-push, merging into main without review, modifying secrets |
| `agent-devops-infra` | `Dockerfile`, `docker-compose*` | `docker-expert`, `kubernetes-architect`, `bash-linux` | production secrets, `.env*`, production k8s |
| `agent-qa-engineer` | `tests/`, testing frameworks | `test-driven-development`, `verification-before-completion` | disabling tests in CI |
| `agent-tech-writer` | `docs/`, OpenAPI, Swagger | `mermaid-diagram-specialist`, `openapi`, `google-style-guide` | publishing unreviewed docs |

---

## 2. Role Synthesis and Duty Deconfliction Guidelines

1. **Topology Sizing:**
   - **Solo Executor:** for documentation or research profiles, one general worker without handoff overhead.
   - **Micro-Mini Duo:** (`agent-dev-lead` + `agent-quality-guardian`) for maintenance or compact repos (<3–5k LOC).
   - **Canonical Compact Trio:** (`agent-dev-lead` + `agent-quality-guardian` + `agent-github-steward`) for active development with strict independent verification.
   - **Specialized Multi-Role Team:** (4–6+ roles) for microservices or polyglot enterprise architectures.

2. **Polyglot Stack Isolation:**
   - Do NOT bundle secondary compiled languages (C/C++, Rust, Go, native GUI) into a general worker without dedicated skills.
   - Synthesize a specialized role (e.g., `agent-native-desktop`) or place native directories into Red Zone with a mandatory handoff trigger.

3. **Trigger Deconfliction (`detect_role_duty_conflicts`):**
   - When multiple roles share overlapping triggers (e.g. both claiming "test" or "audit"), run deconfliction to prune duplicates without touching notes or telemetry.

---

## 3. Reference Loading Contract & Fallback

- **Expected Path:** `skills/manage-meta-project/references/competencies.md`
- **Missing Resource Handling:**
  If this reference file is absent (`[MISSING_RESOURCE] references/competencies.md`), the agent must NOT fail closed. Instead, fall back to core generalist roles (`agent-dev-lead`, `agent-quality-guardian`, `agent-github-steward`, `agent-general-worker`) or solicit explicit role definitions and domain requirements directly from the user.
