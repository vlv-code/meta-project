# https://github.com/vlv-code/meta-project Чекни репо, ч скаж…

> [https://github.com/vlv-code/meta-project](https://github.com/vlv-code/meta-project)
>
> Чекни репо, ч скажешь?

<details><summary>7 previous messages</summary>

> Посмотрю структуру, README и ключевой код, затем дам оценку: что выглядит удачно, где есть риски и что стоит поправить первым.
>
> Проверку окружения сделаю по навыку [cloud-environment-runtime](skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md), затем скачаю репозиторий для чтения кода.
>
> <details><summary>Ran 6 commands, called 3 tools</summary>
>
> MCP tool call
>
> codex_apps.cloud_environment.environment_status
>
> ```json
> {}
> ```
>
> ```text
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "offline",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "starting",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> ```json
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "offline",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "starting",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "open": [
>     {
>       "ref_id": "https://github.com/vlv-code/meta-project"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ```text
> GitHub - vlv-code/meta-project: Agentic context organization framework: project passports (AGENTS.md), dynamic knowledge slices, zero-dependency boundary enforcement, and procedural skills for AI agents. · GitHub (https://github.com/vlv-code/meta-project)
> 【turn214396view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://github.com/vlv-code/meta-project","lineno":null}); Total lines: 431
> L0: 【0†Skip to content】
> L1: ## Navigation Menu
> L2: 
> L3:   * Products
> L4: 
> L5:     *       * 【1†GitHub Repository hosting, code review, and collaboration】
> L6:       * 【2†Copilot AI coding agent for tasks, projects, and automated work】
> L7: 
> L8:     * Build & Ship
> L9:       * 【3†Actions CI/CD and automation】
> L10:       * 【4†Code Quality Quality analysis, fixes, and enforcement】
> L11:       * 【5†Codespaces Cloud development environments】
> L12:     * Secure
> L13:       * 【6†Code Security Vulnerability detection and remediation】
> L14:       * 【7†Secret Protection Secret scanning and leak prevention】
> L15: 
> L16: 【8†All Features】
> L17: 
> L18:   * Developers
> L19: 
> L20:     * Learn
> L21:       * 【9†Documentation†docs.github.com】
> L22:       * 【10†Training†learn.github.com】
> L23:       * 【11†Certifications†learn.github.com】
> L24: 
> L25:     * Build
> L26:       * 【12†Build with Copilot】
> L27:       * 【13†Customize Copilot†docs.github.com】
> L28:       * 【14†Integrations】
> L29:     * Explore
> L30:       * 【15†Trending repos】
> L31:       * 【16†GitHub Sponsors】
> L32:       * 【17†Developer articles】
> L33: 
> L34:     *       * 【18†Changelog Your source for the latest features, improvements, and fixes across GitHub products, all in one place.†github.blog】
> L35: 
> L36:   * Businesses
> L37: 
> L38:     * By Stage
> L39:       * 【19†Enterprises】
> L40:       * 【20†Team】
> L41:       * 【21†Startups】
> L42:       * 【22†Nonprofits】
> L43:     * By Industry
> L44:       * 【23†Healthcare】
> L45:       * 【24†Financial services】
> L46:       * 【25†Manufacturing】
> L47:       * 【26†Government】
> L48:       * 【27†See all industries】
> L49: 
> L50:     * Evaluate GitHub
> L51:       * 【28†Why GitHub】
> L52:       * 【29†Customer Stories】
> L53:       * 【30†Business insights】
> L54:       * 【31†Trust Center】
> L55: 
> L56:     * Add-ons
> L57:       * 【32†GitHub Advanced Security Enterprise-grade code security】
> L58:       * 【33†Copilot for business Enterprise-grade AI features】
> L59:       * 【34†Premium Support Enterprise-grade 24/7 support】
> L60:   * Resources
> L61: 
> L62:     * Learn & Connect
> L63:       * 【9†Documentation†docs.github.com】
> L64:       * 【35†Resource center】
> L65:       * 【36†Blog†github.blog】
> L66:       * 【37†Events & webinars】
> L67:       * 【38†Community Forum】
> L68:       * 【29†Customer Stories】
> L69:       * 【14†Integrations】
> L70: 
> L71:     * Support
> L72:       * 【39†Customer support†help.github.com】
> L73:       * 【10†Training†learn.github.com】
> L74:       * 【40†GitHub Status†www.githubstatus.com】
> L75: 
> L76:     * Company
> L77:       * 【41†About】
> L78:       * 【42†Partners】
> L79:       * 【18†Changelog†github.blog】
> L80:     *       * 【43†GitHub Universe The event for developers, by developers — talks, workshops, and what’s next for GitHub.†githubuniverse.com】
> L81: 
> L82:   * 【44†Pricing】
> L83: 
> L84: Search`/`
> L85: 
> L86: 【45†Sign in】
> L87: 
> L88: 【46†Sign up】
> L89: 
> L90: Appearance settings
> L91: 
> L92: You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert
> L93: 
> L94:   1. 【47†vlv-code】
> L95:   2. 【48†meta-project】
> L96: ## Repository navigation
> L97: 
> L98:   *   * 【48†Code】
> L99:   * 【49†Issues】
> L100:   * 【50†Pull requests】
> L101:   * 【51†Actions】
> L102:   * 【52†Projects】
> L103:   * 【53†Security and quality】
> L104:   * 【54†Insights】
> L105: 
> L106: More items
> L107: 
> L108: 【55†Image: vlv-code†avatars.githubusercontent.com】
> L109: 
> L110: 【48†meta-project】
> L111: 
> L112: Public
> L113: 
> L114:   * 【56†Notifications】You must be signed in to change notification settings
> L115:   * 【56†Fork 0 (0)】
> L116:   * 【56†Star 0 (0)】You must be signed in to star a repository
> L117: ## About
> L118: 
> L119: Agentic context organization framework: project passports (AGENTS.md), dynamic knowledge slices, zero-dependency boundary enforcement, and procedural skills for AI agents.
> L120: 
> L121: 【48†github.com/vlv-code/meta-project】
> L122: 
> L123: ### Topics
> L124: 
> L125: 【57†agentic-framework】【58†agents】【59†agents-md】【60†ai-agents】【61†antigravity】【62†autonomous-agents】【63†code-quality】【64†context-management】【65†developer-tools】【66†llm-agents】【67†prompt-engineering】【68†python】【69†skills】【70†zero-dependencies】
> L126: ### Resources
> L127: 
> L128: 【71†Readme】
> L129: 
> L130: 【72†MIT license】
> L131: 
> L132: ### Contributing
> L133: 
> L134: 【73†Contributing】
> L135: 
> L136: 【74†Activity】
> L137: 
> L138: ### Stars
> L139: 
> L140: 0 stars
> L141: 
> L142: ### Watchers
> L143: 
> L144: 0 watching
> L145: 
> L146: ### Forks
> L147: 
> L148: 【75†0 forks】
> L149: 
> L150: 【76†Report repository】
> L151: 
> L152: main
> L153: 
> L154: 【77†Branches】【78†Tags】
> L155: 
> L156: [Input: Go to file]
> L157: 
> L158: Go to file
> L159: 
> L160: Code
> L161: 
> L162: Open more actions menu
> L163: 
> L164: ## Latest commit
> L165: 
> L166: 
> L167: 
> L168: ## History
> L169: 
> L170: 8 Commits
> L171: ## Folders and files
> L172: Name  | Name  | Last commit message  | Last commit date
> L173: --- | --- | --- | ---
> L174: 【79†.agents】  | 【79†.agents】  |    |
> L175: 【80†.github】  | 【80†.github】  |    |
> L176: 【81†docs】  | 【81†docs】  |    |
> L177: 【82†scripts】  | 【82†scripts】  |    |
> L178: 【83†skills】  | 【83†skills】  |    |
> L179: 【84†templates】  | 【84†templates】  |    |
> L180: 【85†tests】  | 【85†tests】  |    |
> L181: 【86†.gitignore】  | 【86†.gitignore】  |    |
> L182: 【87†AGENTS.md】  | 【87†AGENTS.md】  |    |
> L183: 【88†CHANGELOG.md】  | 【88†CHANGELOG.md】  |    |
> L184: 【89†CONTRIBUTING.md】  | 【89†CONTRIBUTING.md】  |    |
> L185: 【90†CONTRIBUTING.ru.md】  | 【90†CONTRIBUTING.ru.md】  |    |
> L186: 【91†LICENSE】  | 【91†LICENSE】  |    |
> L187: 【92†README.md】  | 【92†README.md】  |    |
> L188: 【93†README.ru.md】  | 【93†README.ru.md】  |    |
> L189: [Button: View all files]
> L190: ## Repository files navigation
> L191: 
> L192:   *   * 【94†README】
> L193:   * 【94†Contributing】
> L194:   * 【94†MIT license】
> L195: 
> L196: More items
> L197: # Agent Environment Framework for Repositories (Meta-Project)
> L198: 
> L199: 【92†English】 | 【93†Русский】
> L200: 
> L201: Context organization framework and separation of concerns between permanent rules (`AGENTS.md`), focused meta-knowledge slices (`project_knowledge/`), and procedural skills (`skills/`) in Google Antigravity and compatible agent environments.
> L202: 
> L203: Warning
> L204: Active Development & Work in Progress (Alpha) Meta-Project is currently under rapid iterative development and empirical testing. Specifications, boundary rules, CLI utilities, and skill formats may evolve based on real-world findings.
> L205: 
> L206: 💡 Help & Feedback Wanted: We actively welcome your help! Whether it is stress-testing skills on your tech stack, proposing new agent invariants, reporting edge cases, or opening Pull Requests — see 【95†Contributing】 and 【89†CONTRIBUTING.md】.
> L207: 
> L208: * * *
> L209: ## Table of Contents
> L210: 
> L211:   * 【96†Architectural Principles】
> L212:   * 【97†Target Repository Structure】
> L213:   * 【98†Meta-Project Components】
> L214:   * 【99†Quickstart】
> L215:   * 【100†Testing and Validation】
> L216:   * 【101†Documentation and Research】
> L217:   * 【95†Contributing】
> L218:   * 【102†Support the Project】
> L219:   * 【103†License】
> L220: 
> L221: * * *
> L222: ## Architectural Principles
> L223:   1. No Context Bloat:
> L224: The root `AGENTS.md` contains only fundamental invariants, guiding principles (North Stars), stack declarations, and navigation protocols. Because it is permanently loaded into context [by documentation], it remains free of dynamic logs and bulky descriptions.
> L225:   2. Guards Against Architectural Contradictions:
> L226: The project passport establishes core principles and decision guardrails (e.g., zero external dependencies, no redundant abstractions, strict typing), preventing foreign or conflicting decisions.
> L227:   3. Read + Opportunistic Refresh:
> L228: When consulting any meta-knowledge slice before taking action, an agent does not merely read it passively; it is required to close discovered gaps, record inaccuracies, and maintain the integrity of the project picture.
> L229:   4. Non-Destructive Update:
> L230: The `init-meta-project` skill automatically recognizes an existing meta-project structure in the target repo, preserves all accumulated data (`observations.md`, custom invariants), and safely equips the project with updated standards.
> L231:   5. Delegation to Stack Domain Skills:
> L232: Instead of hardcoding build and linting commands, the passport connects specialized domain skills from the agent environment (`python-pro`, `typescript-expert`, `docker-expert`, etc.), which hold built-in command knowledge and idioms.
> L233:   6. Machine-Readable Glob Boundaries:
> L234: Responsibility zones in `boundaries.md` are defined via explicit glob path patterns, eliminating subjective interpretation by agents.
> L235: * * *
> L236: ## Target Repository Structure
> L237: After initialization, the following standardized structure is created in any target project:
> L238: 
> L239:     `<project_root>/
> L240:     ├── AGENTS.md                          # Passport & navigator (North Stars, stack, refresh protocol, skills)
> L241:     └── .agents/
> L242:         ├── project_knowledge/             # Meta-knowledge slices (loaded on-demand)
> L243:         │   ├── architecture.md            # Architectural foundations & component relationships
> L244:         │   ├── boundaries.md              # Machine-readable zones (Green, Yellow, Red)
> L245:         │   ├── weak_spots.md              # Known pitfalls, risks, and technical debt
> L246:         │   ├── observations.md            # Cumulative agent observation log (categorized)
> L247:         │   └── tasks.md                   # Active task registry and cross-agent checklist
> L248:         ├── skills/                        # Pre-installed repository skills
> L249:         │   ├── ground-meta-project/       # Emergency grounding and context recalibration
> L250:         │   │   └── SKILL.md
> L251:         │   ├── record-observation/        # Atomic observation logging to observations.md
> L252:         │   │   └── SKILL.md
> L253:         │   └── sync-architecture/         # Architecture & component sync to architecture.md
> L254:         │       └── SKILL.md
> L255:         └── team/                          # (Optional) Specialized subagent team (via manage-meta-project)
> L256:             ├── agent-<role>/
> L257:             │   ├── profile.md             # Role passport and invocation telemetry
> L258:             │   ├── notes.md               # Private role-isolated working notes
> L259:             │   └── system_prompt.md       # Tailored role system prompt with invariants
> L260:             └── archive/                   # Safely decommissioned roles (via decommission-meta-project)
> L261:     `
> L262: * * *
> L263: ## Meta-Project Components
> L264:   * `templates/`:
> L265:     * `templates/AGENTS.md` — Canonical project passport template featuring guiding principles (North Stars) and the opportunistic refresh protocol.
> L266:     * `templates/global/AGENTS.md` — Universal global agent harness configuration template (First-Contact Rule, Default Deny, Circuit Breaker).
> L267:     * `templates/project_knowledge/` — Baseline templates for the project meta-knowledge repository (`architecture.md`, `boundaries.md`, `weak_spots.md`, `observations.md`, `tasks.md`).
> L268:     * `templates/team/` — Role passport template (`profile.md`), isolated private notes (`notes.md`), and system prompt (`system_prompt.md`).
> L269:   * `skills/`:
> L270:     * `skills/init-meta-project/` — Autonomous skill supporting two execution modes: safe audit/update of an existing `meta-project` without data loss, or clean repository two-pass initialization with a mandatory Core Inspection Checklist, codified interactive interview, and atomic In-Memory Synthesis Flush.
> L271:     * `skills/manage-meta-project/` — Skill for creating, auditing, and orchestrating a specialized subagent team (.agents/team/) with a scale-adaptive competency matrix, role pruning, and User-Mediated Handoff protocols.
> L272:     * `skills/decommission-meta-project/` — Skill for safe, non-destructive decommissioning, resizing, and archiving of specialized agent roles (.agents/team/) into `.agents/team/archive/` with telemetry closeout, root `AGENTS.md` synchronization, and orphaned tasks reassignment without data loss.
> L273:     * `skills/ground-meta-project/` — Emergency grounding and context recalibration skill: halts runaway edits, forces a zoom-out, re-reads canonical sources, and anchors the agent back into its operating corridor.
> L274:     * `skills/scan-meta-project/` — Express and deep-dive inspection skill: audits repository meta-knowledge integrity, verifies 100% boundary coverage, detects architectural drift, and backfills missing facts without re-initialization.
> L275:     * `skills/tune-meta-project/` — Calibration and optimization skill: diagnoses git friction, analyzes telemetry, tunes role topology, refines boundary zones, and crystallizes North Star invariants.
> L276:     * `skills/update-meta-project/` — Non-destructive upstream updating skill from GitHub or local cache with dual-tier source resolution and seamless `local_repo_data` preservation.
> L277:     * `skills/record-observation/` — Skill for categorized logging of observations into `observations.md` with duplicate suppression and compaction triggers.
> L278:     * `skills/sync-architecture/` — Skill for structural manifest analysis and component map synchronization.
> L279:   * `scripts/`:
> L280:     * `scripts/check_boundaries.py` — Zero-dependency Boundary Gate CLI enforcing Green/Yellow/Red zones and Default Deny (Black Zone) on Git diffs locally and in GitHub Actions CI (supports `--audit-tree` for 100% path coverage and `--install-hook` for pre-commit installation).
> L281:     * `scripts/compact_memory.py` — Context Rot Shield utility automatically rotating oversized observation tables (>20 rows) and completed tasks into `.agents/project_knowledge/archive/`, retaining permanent `[pin]` invariants.
> L282:     * `scripts/sync_templates.py` — Zero-dependency utility synchronizing canonical templates into embedded skills and maintaining 1-to-1 parity between `skills/` and `.agents/skills/` (with `--check` mode for CI).
> L283:   * `docs/`:
> L284:     * `docs/decisions_and_roadmap.md` — Architecture Decision Records (ADR #1–#8 + Polyglot Monorepo Incident) and roadmap.
> L285:     * `docs/test_report_alpha_skill.md` — Empirical test report from test cycles (Tests 1–6) on a sample bot service.
> L286:     * `docs/temporary_overrides.md` — Temporary rule calibrations.
> L287: * * *
> L288: ## Quickstart
> L289: ### 1. Preparing the Global Agent Harness (Universal First-Contact Setup)
> L290: 
> L291: To enable autonomous agents to discover and respect Meta-Project passports (`AGENTS.md`) and knowledge slices across all repositories, configure your environment using `templates/global/AGENTS.md`:
> L292: Agent Harness  | Global Configuration Path  | Recommended Action
> L293: --- | --- | ---
> L294: Google Antigravity / Gemini CLI  | `~/.gemini/GEMINI.md`  | Append content from `templates/global/AGENTS.md`
> L295: Claude Code  | `~/.claude/CLAUDE.md`  | Append content from `templates/global/AGENTS.md`
> L296: Cursor / Windsurf  | Global User Rules / `.cursorrules`  | Paste content from `templates/global/AGENTS.md`
> L297: Open Agent Runners  | `~/AGENTS.md`  | Copy `templates/global/AGENTS.md`
> L298: ### 2. Connecting Skills to the Agent Environment
> L299: 
> L300: Copy the meta-project skills (`init-meta-project`, `manage-meta-project`, `decommission-meta-project`, `ground-meta-project`) to your agent environment's skill directory:
> L301: 
> L302:   * For Google Antigravity: `~/.gemini/config/skills/<skill-name>`
> L303:   * Or use locally as part of your tooling suite.
> L304: ### 3. Project Initialization
> L305: 
> L306: Navigate to the root of any target repository and issue the command to the agent:
> L307: 
> L308:     `Prepare the repository for agent workflows using the init-meta-project skill
> L309:     `
> L310: 
> L311: The agent will:
> L312:   1. Analyze manifests and directory structure.
> L313:   2. Inspect critical components (Core Inspection Checklist: Database, API, Docker, UI/Validation).
> L314:   3. Generate root `AGENTS.md` and meta-knowledge directory `.agents/project_knowledge/`.
> L315:   4. Install local repository skills (`record-observation`, `sync-architecture`).
> L316: ### 4. Agent Team Orchestration and Decommissioning (Optional)
> L317: 
> L318: To deploy and orchestrate specialized agent roles:
> L319: 
> L320:     `Assemble agent team using manage-meta-project skill
> L321:     `
> L322: 
> L323: To safely archive or resize agent roles without data loss:
> L324: 
> L325:     `Decommission agent team using decommission-meta-project skill
> L326:     `
> L327: ### 5. Emergency Grounding & Forced Zoom-Out
> L328: 
> L329: If an agent exhibits context drift, loops across speculative fixes, or breaches role boundaries:
> L330: 
> L331:     `Recalibrate agent using ground-meta-project skill
> L332:     `
> L333: ### 6. Deployment Modes: Shared Repo-Level vs Invisible Overlay
> L334: 
> L335: Meta-Project supports two usage scenarios:
> L336:   * Shared Repo-Level (Team / Open Standard):
> L337: `AGENTS.md` and `.agents/` are committed to Git. Rules, architecture maps, and risk logs are shared across all developers, agents, and CI pipelines.
> L338:   * Invisible Overlay (Personal Dashboard for Third-Party/Work Repos):
> L339: `AGENTS.md` and `.agents/` are added to the target project's local `.git/info/exclude`. The agent gains full access to meta-knowledge on your local machine, keeping Git commits completely clean in external repositories.
> L340: #### Optional Easter Egg Badge
> L341: 
> L342: To indicate that a project is designed or maintained with an agentic environment, add the badge to its `README.md`:
> L343: 
> L344:     [![Agent Environment: Meta-Project](https://img.shields.io/badge/Agent%20Environment-Meta--Project-5865F2)](https://github.com/vlv-code/meta-project)
> L345: 
> L346: * * *
> L347: ## Testing and Validation
> L348: 
> L349: The project includes automated integrity tests for skills, YAML frontmatter, templates, and canonical structure:
> L350: 
> L351:     python -m unittest discover -s tests -p "test_*.py" -v
> L352: 
> L353: Tests have zero external dependencies and run on any platform with Python 3.10+.
> L354: 
> L355: * * *
> L356: 
> L357: ## Documentation and Research
> L358: 
> L359:   * 【104†Architecture Decision Records and Roadmap (ADR)】
> L360:   * 【105†Empirical Skill Test Report (Tests 1–6)】
> L361:   * 【106†Temporary Rule Calibrations】
> L362: 
> L363: * * *
> L364: ## Contributing
> L365: 
> L366: Meta-Project is in active development, and community contributions are very welcome! We are especially looking for help with:
> L367:   * Real-World Stress Testing: Test `init-meta-project` and agent teams across diverse tech stacks (Rust, Go, Node.js, C/C++, mobile, microservices) and share your findings.
> L368:   * Edge Cases & Invariants: Help identify boundary leaks, model drift patterns, or architectural friction points to enrich `observations.md` and default boundary templates.
> L369:   * Tooling & Integrations: Extend zero-dependency CLI utilities (`check_boundaries.py`, `compact_memory.py`, `sync_templates.py`) or contribute agent adapter templates for other environments.
> L370:   * Documentation & Localization: Improve guides, bilingual parity, or add new usage examples.
> L371: Please review 【89†CONTRIBUTING.md】 before submitting a Pull Request.
> L372: 
> L373: All version changes are tracked in 【88†CHANGELOG.md】.
> L374: 
> L375: * * *
> L376: ## Support the Project
> L377: 
> L378: If Meta-Project has been useful, you can support its development:
> L379: 
> L380:   * 【107†Boosty†boosty.to】
> L381:   * Cryptocurrency: USDT, network TON (USDT only and only this network, otherwise funds will be lost):
> L382: 
> L383:     `UQDASKlEmcoPuBr5-u5jSjLdXWfCiSfARjPc_wWW0qLbSreC
> L384:     `
> L385: 
> L386: * * *
> L387: 
> L388: ## License
> L389: 
> L390: Distributed under the 【91†MIT】 License.
> L391: ## About
> L392: 
> L393: Agentic context organization framework: project passports (AGENTS.md), dynamic knowledge slices, zero-dependency boundary enforcement, and procedural skills for AI agents.
> L394: 
> L395: 【48†github.com/vlv-code/meta-project】
> L396: 
> L397: ### Topics
> L398: 
> L399: 【57†agentic-framework】【58†agents】【59†agents-md】【60†ai-agents】【61†antigravity】【62†autonomous-agents】【63†code-quality】【64†context-management】【65†developer-tools】【66†llm-agents】【67†prompt-engineering】【68†python】【69†skills】【70†zero-dependencies】
> L400: ### Resources
> L401: 
> L402: 【71†Readme】
> L403: 
> L404: 【72†MIT license】
> L405: 
> L406: ### Contributing
> L407: 
> L408: 【73†Contributing】
> L409: 
> L410: 【74†Activity】
> L411: 
> L412: ### Stars
> L413: 
> L414: 0 stars
> L415: 
> L416: ### Watchers
> L417: 
> L418: 0 watching
> L419: 
> L420: ### Forks
> L421: 
> L422: 【75†0 forks】
> L423: 
> L424: 【76†Report repository】
> L425: 
> L426: ## Contributors
> L427: 
> L428: ## Languages
> L429: 
> L430: You can’t perform that action at this time.
> ```
>
> MCP tool call
>
> codex_apps.cloud_environment.environment_status
>
> ```json
> {}
> ```
>
> ```text
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> ```json
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> - Ran `pwd && rg --files -g AGENTS.md -g '*SKILL.md' -g '!node_modules' -g '!vendor' -g '!work/**' . && cat /etc/codex/network-policy.json`
>
> - Ran `ls -la /workspace && if [ -f /AGENTS.md ]; then cat /AGENTS.md; fi && if [ -f /workspace/AGENTS.md ]; then cat /workspace/AGENTS.md; fi && cat /etc/codex/network-policy.json`
>
> - Ran `mkdir -p /workspace/work && git clone --depth 1 https://github.com/vlv-code/meta-project.git /workspace/work/meta-project`
>
> - Ran `cat AGENTS.md && git log -1 --format='%H%n%s%n%ci' && rg --files --hidden -g '!.git/**' -g '!AGENTS.md'`
>
> - Ran `cat .agents/project_knowledge/tasks.md .agents/project_knowledge/boundaries.md .agents/project_knowledge/weak_spots.md .agents/project_knowledge/architecture.md && cat .github/workflows/ci.yml`
>
> - Ran `wc -l scripts/*.py tests/*.py skills/*/SKILL.md templates/AGENTS.md templates/global/AGENTS.md && sed -n '1,260p' scripts/check_boundaries.py`
>
> </details>
>
> Основа выглядит разумно: постоянные правила отделены от памяти, а часть требований проверяется Python-утилитами. Сейчас проверяю, как реально работают ограничения изменений, синхронизация шаблонов и сохранение памяти — здесь важнее поведение, чем формулировки в README.
>
> <details><summary>Explored 5 files, ran 6 commands</summary>
>
> - Ran `cat tests/test_integrity.py && cat tests/test_compact_memory.py tests/test_sync_templates.py`
>
> <details><summary>Explored 6 files</summary>
>
> - Read `./scripts/check_boundaries.py`
> - Read `./scripts/compact_memory.py`
> - Read `./scripts/sync_templates.py`
> - Read `./tests/test_check_boundaries.py`
> - Read `./scripts/sync_templates.py`
> - Read `./tests/test_integrity.py`
>
> </details>
>
> - Ran `python scripts/check_boundaries.py --boundaries .agents/project_knowledge/boundaries.md --audit-tree && python scripts/sync_templates.py --check`
>
> - Ran `python -m unittest discover -s tests -p 'test_*.py' -v`
>
> - Ran `cat skills/scan-meta-project/SKILL.md skills/tune-meta-project/SKILL.md skills/record-observation/SKILL.md skills/sync-architecture/SKILL.md && sed -n '1,150p' skills/manage-meta-project/SKILL.md`
>
> - Ran `sed -n '1,145p' skills/init-meta-project/SKILL.md && cat skills/update-meta-project/SKILL.md && cat templates/global/AGENTS.md templates/project_knowledge/boundaries.md`
>
> - Ran `cat docs/test_report_alpha_skill.md docs/test_report_orchestration_team.md && cat docs/temporary_overrides.md`
>
> </details>
>
> Штатные проверки прошли: 51 тест, аудит покрытия границ и синхронизация шаблонов. При этом CI запускает у Boundary Gate только проверку покрытия файлов правилами; она не запрещает изменения в Red Zone. Проверю это на отдельном временном репозитории, а также один возможный случай потери записей при архивации.
>
> <details><summary>Explored 3 files, ran 5 commands</summary>
>
> - Ran `rg -n '100%|99%|детермин|[0-9]+ шаг|вызов|оценк|сравн|[Мм]одел|baseline|token|токен' docs/test_report_alpha_skill.md docs/test_report_orchestration_team.md docs/decisions_and_roadmap.md && git status --short && python --version`
>
> - Ran `sed -n '1,150p' skills/manage-meta-project/SKILL.md && sed -n '140,198p' skills/init-meta-project/SKILL.md && cat templates/team/system_prompt.md templates/AGENTS.md`
>
> - Ran `sed -n '1,140p' skills/scan-meta-project/SKILL.md && cat skills/record-observation/SKILL.md skills/sync-architecture/SKILL.md && sed -n '1,115p' skills/tune-meta-project/SKILL.md`
>
> - Ran `python - <<'PY'
> import contextlib
> from datetime import datetime
> import io
> from pathlib import Path
> import subprocess
> import sys
> import tempfile
>
> repo = Path('/workspace/work/meta-project')
> sys.path.insert(0, str(repo / 'scripts'))
> import check_boundaries as boundary
> import compact_memory
>
> with tempfile.TemporaryDirectory(prefix='meta-review-') as tmp:
>     root = Path(tmp)
>     subprocess.run(['git', 'init', '-q', str(root)], check=True)
>     (root / 'LICENSE').write_text('original license\n')
>     pk = root / '.agents/project_knowledge'
>     pk.mkdir(parents=True)
>     (pk / 'boundaries.md').write_text((repo / '.agents/project_knowledge/boundaries.md').read_text())
>     subprocess.run(['git', 'add', '.'], cwd=root, check=True)
>     subprocess.run(['git', '-c', 'user.name=Review', '-c', 'user.email=review@example.invalid', 'commit', '-qm', 'baseline'], cwd=root, check=True)
>     (root / 'LICENSE').write_text('changed license\n')
>     script = str(repo / 'scripts/check_boundaries.py')
>     audit = subprocess.run([sys.executable, script, '--boundaries', '.agents/project_knowledge/boundaries.md', '--audit-tree'], cwd=root, text=True, capture_output=True)
>     diff = subprocess.run([sys.executable, script], cwd=root, text=True, capture_output=True)
>     print('RED ZONE: changed LICENSE; CI audit return code =', audit.returncode, '; diff gate return code =', diff.returncode)
>     print(audit.stdout.strip())
>     subprocess.run(['git', 'add', 'LICENSE'], cwd=root, check=True)
>     staged_default = subprocess.run([sys.executable, script], cwd=root, text=True, capture_output=True)
>     print('STAGED LICENSE: default gate return code =', staged_default.returncode, '; message =', staged_default.stdout.strip())
>     hook = root / '.git/hooks/pre-commit'
>     hook.write_text('#!/bin/sh\necho existing-quality-check\n')
>     ok, message = boundary.install_git_hook(root)
>     print('HOOK INSTALL: return =', ok, '; pre-existing check preserved =', 'existing-quality-check' in hook.read_text())
>
> with tempfile.TemporaryDirectory(prefix='meta-memory-review-') as tmp:
>     root = Path(tmp)
>     obs = root / 'observations.md'
>     table = '| Date | Category | Component / Path | Observation / Issue | Solution / Workaround |\n| :--- | :--- | :--- | :--- | :--- |\n'
>     table += '| 2026-11-01 | [code] | parser | DateTime parsing bug | fixed |\n'
>     table += '| 2026-11-02 | [code] | markdown | literal --- separator bug | fixed |\n'
>     table += '| 2026-11-03 | [code] | regular | ordinary older row | fixed |\n'
>     table += '| 2026-11-04 | [code] | newest | latest row | fixed |\n'
>     obs.write_text(table)
>     archive = root / 'archive'
>     archive.mkdir()
>     archive_file = archive / ('observations_' + datetime.now().strftime('%Y%m') + '.md')
>     archive_file.write_text('# Existing archive\n\n' + table.splitlines()[0] + '\n' + table.splitlines()[1] + '\n')
>     with contextlib.redirect_stdout(io.StringIO()):
>         rc = compact_memory.main(['--observations', str(obs), '--tasks', str(root / 'absent-tasks.md'), '--archive-dir', str(archive), '--max-observations', '2', '--keep-observations', '1'])
>     all_text = obs.read_text() + archive_file.read_text()
>     print('MEMORY APPEND: return code =', rc, '; DateTime row preserved =', 'DateTime parsing bug' in all_text, '; --- row preserved =', 'literal --- separator bug' in all_text, '; ordinary row preserved =', 'ordinary older row' in all_text)
> PY`
>
> <details><summary>Explored 3 files</summary>
>
> - Read `./.github/workflows/ci.yml`
> - Read `./scripts/compact_memory.py`
> - Read `./scripts/check_boundaries.py`
>
> </details>
>
> - Ran `sed -n '1,56p' docs/test_report_alpha_skill.md && sed -n '144,181p' skills/init-meta-project/SKILL.md && git status --porcelain && git rev-parse --short HEAD`
>
> </details>
</details>

**Идея здравая, но надёжность инструментов пока отстаёт от строгости правил.** Для alpha — полезная основа.

Посмотрел код на коммите `398a171`, прогнал проверки на Python 3.12: **51/51 тестов проходят**, шаблоны синхронизированы, все 89 файлов покрыты правилами границ.

Понравилось разделение на постоянный `AGENTS.md`, память по запросу и процедурные навыки. Это помогает организовать контекст. Python-утилиты без зависимостей тоже удачный выбор.

При этом воспроизвёл три проблемы:

1. **Архиватор может терять наблюдения.** Если месячный архив уже существует, строки с `Date` или `---` внутри текста отбрасываются как заголовки, а из основного файла удаляются. Проверил на записи про `DateTime`: она исчезла из обоих файлов. [Место ошибки](https://github.com/vlv-code/meta-project/blob/398a1719ca10f7153c73d3dcb83e80d102d6973d/scripts/compact_memory.py#L209-L220).

2. **CI не блокирует изменения Red Zone.** В workflow запускается только `--audit-tree`: он проверяет, что файл относится к какой-то зоне. Изменённый `LICENSE` проходит эту проверку с кодом `0`, хотя обычная проверка diff его запрещает. Нужна отдельная проверка изменений относительно базы PR. [Workflow](https://github.com/vlv-code/meta-project/blob/398a1719ca10f7153c73d3dcb83e80d102d6973d/.github/workflows/ci.yml#L42-L46).

3. **Установка hook затирает существующий `pre-commit`.** Без проверки и сохранения предыдущего содержимого. Так можно случайно убрать уже работающие проверки проекта. [Установщик](https://github.com/vlv-code/meta-project/blob/398a1719ca10f7153c73d3dcb83e80d102d6973d/scripts/check_boundaries.py#L317-L350).

Ещё осторожнее сформулировал бы выводы экспериментов. В отчётах есть полезные наблюдения, но заявления про «100% обнаружение дефектов» и доказанную детерминированность намного сильнее представленных данных. Нужны повторяемые сравнения: одинаковые задачи и версии моделей, несколько прогонов, расход токенов, время и подтверждённые дефекты. [Отчёт](https://github.com/vlv-code/meta-project/blob/398a1719ca10f7153c73d3dcb83e80d102d6973d/docs/test_report_alpha_skill.md#L122-L158).

Я бы следующим шагом исправил эти три бага и добавил регрессионные проверки. Самая ценная часть проекта — управление контекстом и проверяемые ограничения; именно их надёжность сейчас даст наибольший прирост пользы.

> ку, чекни отчет аудитора:
> \
> По порядку.
> \
> 1\. Soft control → что делать
> \
> Принцип: каждое правило должно оставлять машинно-проверяемый след. Нет следа — автоматизируй или удали. Конкретно для этого репо:
> \
> Rituals → scripts. Телеметрия не ведётся, потому что это отдельный акт добродетели после задачи. Сделайте её побочным продуктом действия: post-commit хук, который аппендит строку в profile.md из git log (у них это уже есть как идея P2 — я бы поднял в P0, это убивает весь класс «карго-культа»). То же с record-observation: пусть скилл вызывает scripts/record_obs.py --category ci --fact "..." — детерминированный append, дедуп, [pin]. LLM решает когда, скрипт делает как. Забыть становится физически нельзя.
> \
> DoD → verify_dod.py в CI/pre-push. Механически проверяемая часть чек-листа: задача закрыта в tasks.md → в диффе есть строка телеметрии с её ID; добавлен модуль в src/\*\* → тронут architecture.md (сейчас это soft warning — сделать конфигурируемым fail). Аудит guardian'а — структурированный вывод (YAML/JSON findings), который скрипт материализует в weak_spots.md. Их главный провал («нашёл 3 риска, не записал ни строки») лечится именно разделением «суждение — LLM, запись — скрипт».
> \
> Hard enforcement на уровне харнесса, а не промпта. У Claude Code есть PreToolUse-хуки и deny-правила в settings: можно заставить сам харнесс отказывать в записи по Red-глобам, прогоняя classify_path до write. Запланированные адаптеры (P2) должны генерировать не текст правил, а конфиг принуждения. Это и есть настоящий выход из «markdown против природы LLM».
> \
> Диета правил. Всё, что нельзя ни проверить, ни автоматизировать, — сокращать до минимума и подавать just-in-time (в момент действия), а не держать в перманентном контексте. У них уже есть «≤3 North Stars» в tune — распространить тот же принцип на все протоколы и мерить compliance в их же тестовых циклах: правило, не меняющее поведение агента, — балласт, съедающий контекст.
> \
> 2\. Semantic gate — предложения
> \
> Ярусами, не ломая zero-dependency ядро:
> \
> Детектор ослабления тестов на stdlib ast. Для изменённых тестов сравнить old (git show HEAD:file) и new: уменьшение числа assert по тестовым функциям, добавленные skip/xfail, удалённый pytest.raises, изменённые expected-константы в том же коммите, что и код под тестом, закомментированные ассерты (regex по диффу). Не доказательство семантики — эвристики, но цель и не доказательство, а сделать читерство видимым и потребовать override. Снапшоты/голден-файлы (\*.snap, \_\_snapshots\_\_/\*\*) — в Red по умолчанию. Для JS/TS — regex-ярус, tree-sitter опциональным плагином позже.
> \
> Danger-pattern lint по добавленным строкам (тоже ast): eval/exec, pickle.loads, shell=True, verify=False, except: pass. Дёшево, а на агентном коде сигнал высокий.
> \
> Секреты: мини-сканер на stdlib (известные форматы токенов + энтропия) в ядро, gitleaks — отдельной опциональной CI-джобой. Их аргумент «Gitleaks нарушает zero-dependency» — подмена: инвариант должен означать «ядро на stdlib», а не «в пайплайне нет других инструментов». Джоба с запиненным бинарником не добавляет ни одной Python-зависимости.
> \
> Самозащита гейта — вот это дыра поважнее семантики: scripts/\*\* сейчас Yellow, то есть агент может отредактировать сам check_boundaries.py или boundaries.md, чтобы пропустить себя. Гейт, границы и workflows — в Red + CODEOWNERS; --allow-red-zone — с записью в аудит-лог; CI как backstop против --no-verify (есть) + required checks в branch protection.
> \
> 3\. Масштаб — да, тут ты прав
> \
> Перечитал скилл: там явный Scale-Adaptive Sizing — <10k LOC → компактная триада совмещённых ролей, 10–50k → 3–5, >50k → 6+, плюс обязательный диспетчер от 3 ролей. И команда вообще опциональна: малый репо при init получает только 3 локальных скилла и 2 скрипта. Мой тезис про оверкилл был неточен — признаю. Что остаётся валидным: даже триада для соло-репо на 5k строк — это три паспорта, три notes, три телеметрии; я бы добавил явный нулевой тир («micro → команда не разворачивается вовсе, один агент + паспорт, manage не вызывать») и вынес это в README одной строкой, потому что при беглом чтении (как у меня) масштабирование не считывается — оно спрятано в Phase 2 скилла.
> \
> 4\. «Мелочи» — что именно смущает
> \
> Regex-инъекция. Теперь с конкретикой, я посмотрел тесты: покрыты backticks в заголовке и простой replace, но нет теста на отсутствующий блок и на вложенные fences. А в коде: replace_embedded_template при несовпадении regex возвращает (text, False) — это неотличимо от «всё синхронно». Переименовали заголовок ### Template: или потеряли блок — --check отрапортует зелёный ноль дрейфа. Ложноотрицательный гейт — это хуже отсутствия гейта. Плюс non-greedy DOTALL до первого ^\`\`\` сломается на шаблоне с внутренним fenced-блоком. Фиксы по возрастанию: (а) «блок не найден» = drift-ошибка, тест на это; (б) явные сентинелы \<!-- TEMPLATE:BEGIN name -->…END вместо угадывания заголовков; (в) идеально — инвертировать: шаблоны живут отдельными файлами, SKILL.md \*\*генерируется\*\* из исходника с плейсхолдерами, --check = regenerate + diff. Regex-хирургия исчезает как класс.
> \
> Русские ADR/changelog. Не идеология, а воронка: репо зовёт мир на стресс-тесты, канон английский, а самое ценное — постмортем инцидента и ADR — доступно только русскоязычным. Потенциальный контрибьютор не может понять почему правила такие. Достаточно перевести решения ADR и lessons learned инцидента; changelog — английский хотя бы дальше по времени.
> \
> Крипта. Честно: это вкусовщина, не дефект, потому и «на любителя». Два нюанса: недельный анонимный репо с голым USDT-адресом у осторожного читателя паттерн-матчится на скам-донаты (GitHub Sponsors выглядит легитимнее); и предупреждение «только сеть TON, иначе средства потеряны» — это ловушка необратимой ошибки, хостед-страница доната с выбором сети безопаснее статичного адреса. Приоритет — низкий, можно оставить как есть.
> \
>
> \
> Что из этого актуально, что применимо, а что не нужно для данного репо?

<details><summary>4 previous messages</summary>

> Сверю отчёт с текущим кодом и разделю рекомендации на нужные исправления, полезные следующие шаги и избыточные для этого репо. Отдельно проверю, где предлагаемая автоматизация действительно даёт контроль, а где только добавляет ритуал.
>
> <details><summary>Explored 6 files, a search, ran 2 commands, called 3 tools</summary>
>
> - Ran `git status --short && git log -1 --format='%H%n%s' && cat /etc/codex/network-policy.json`
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "open": [
>     {
>       "ref_id": "https://code.claude.com/docs/en/hooks"
>     },
>     {
>       "ref_id": "https://code.claude.com/docs/en/permissions"
>     },
>     {
>       "ref_id": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ```text
> Hooks reference - Claude Code Docs (https://code.claude.com/docs/en/hooks)
> 【turn989820view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://code.claude.com/docs/en/hooks","lineno":null}); Total lines: 4119
> L0: > ## Documentation Index
> L1: >
> L2: > Fetch the complete documentation index at: 【0†/docs/llms.txt】
> L3: >
> L4: > Use this file to discover all available pages before exploring further.
> L5: 
> L6: 【1†Skip to main content】
> L7: 
> L8: 【2†Claude Code Docs home page】
> L9: 
> L10: Search...
> L11: 
> L12: Navigation
> L13: 
> L14: Reference
> L15: 
> L16: Hooks reference
> L17: 
> L18: Getting started
> L19: 
> L20: Build with Claude Code
> L21: 
> L22: Plugins
> L23: 
> L24: Administration
> L25: 
> L26: Configuration
> L27: 
> L28: Reference
> L29: 
> L30: Agent SDK
> L31: 
> L32: 【3†Resources】
> L33: ## On this page
> L34: 
> L35: Back to top
> L36:   * 【4†Hook lifecycle】
> L37:     * 【5†How a hook resolves】
> L38:   * 【6†Configuration】
> L39:     * 【7†Hook locations】
> L40:     * 【8†Matcher patterns】
> L41:     * 【9†Match MCP tools】
> L42:     * 【10†Match Monitor commands】
> L43:     * 【11†Hook handler fields】
> L44:     * 【12†Common fields】
> L45:     * 【13†How if patterns match Bash commands】
> L46:     * 【14†Command hook fields】
> L47:     * 【15†HTTP hook fields】
> L48:     * 【16†MCP tool hook fields】
> L49:     * 【17†Prompt and agent hook fields】
> L50:     * 【18†Reference scripts by path】
> L51:     * 【19†Hooks in skills and agents】
> L52:     * 【20†Limits on skill hooks】
> L53:     * 【21†The /hooks menu】
> L54:     * 【22†Disable or remove hooks】
> L55:   * 【23†Hook input and output】
> L56:     * 【24†Common input fields】
> L57:     * 【25†Exit code output】
> L58:     * 【26†Exit code 0】
> L59:     * 【27†Exit code 2】
> L60:     * 【28†Other exit codes】
> L61:     * 【29†Timeouts】
> L62:     * 【30†Hooks that start a background process】
> L63:     * 【31†Block the action when a hook fails】
> L64:     * 【32†Failed hooks on Windows without Git Bash】
> L65:     * 【33†PowerShell started no program】
> L66:     * 【34†Exit code 2 behavior per event】
> L67:     * 【35†HTTP response handling】
> L68:     * 【36†JSON output】
> L69:     * 【37†Emit terminal notifications】
> L70:     * 【38†Get terminal notifications inside tmux or GNU screen】
> L71:     * 【39†Add context for Claude】
> L72:     * 【40†Decision control】
> L73:   * 【41†Hook events】
> L74:     * 【42†SessionStart】
> L75:     * 【43†SessionStart input】
> L76:     * 【44†SessionStart decision control】
> L77:     * 【45†Reload skills that a hook installs】
> L78:     * 【46†Persist environment variables】
> L79:     * 【47†Setup】
> L80:     * 【48†Setup input】
> L81:     * 【49†Setup decision control】
> L82:     * 【50†InstructionsLoaded】
> L83:     * 【51†InstructionsLoaded input】
> L84:     * 【52†InstructionsLoaded decision control】
> L85:     * 【53†UserPromptSubmit】
> L86:     * 【54†Esc during a prompt check】
> L87:     * 【55†UserPromptSubmit input】
> L88:     * 【56†UserPromptSubmit decision control】
> L89:     * 【57†What a blocked prompt leaves behind】
> L90:     * 【58†UserPromptExpansion】
> L91:     * 【59†UserPromptExpansion input】
> L92:     * 【60†UserPromptExpansion decision control】
> L93:     * 【61†MessageDisplay】
> L94:     * 【62†MessageDisplay input】
> L95:     * 【63†MessageDisplay output】
> L96:     * 【64†PreToolUse】
> L97:     * 【65†PreToolUse input】
> L98:     * 【66†PreToolUse decision control】
> L99:     * 【67†PreToolUse updatedInput in auto mode】
> L100:     * 【68†PreToolUse ask decisions in auto mode】
> L101:     * 【69†Tools that require user interaction】
> L102:     * 【70†Defer a tool call for later】
> L103:     * 【71†PermissionRequest】
> L104:     * 【72†PermissionRequest input】
> L105:     * 【73†PermissionRequest decision control】
> L106:     * 【74†Permission update entries】
> L107:     * 【75†PostToolUse】
> L108:     * 【76†PostToolUse after an interrupt】
> L109:     * 【77†PostToolUse input】
> L110:     * 【78†PostToolUse decision control】
> L111:     * 【79†Annotate a result for the auto mode classifier】
> L112:     * 【80†PostToolUseFailure】
> L113:     * 【81†PostToolUseFailure input】
> L114:     * 【82†PostToolUseFailure decision control】
> L115:     * 【83†PostToolBatch】
> L116:     * 【84†PostToolBatch input】
> L117:     * 【85†PostToolBatch decision control】
> L118:     * 【86†PermissionDenied】
> L119:     * 【87†PermissionDenied input】
> L120:     * 【88†PermissionDenied decision control】
> L121:     * 【89†Notification】
> L122:     * 【90†Notification input】
> L123:     * 【91†SubagentStart】
> L124:     * 【92†SubagentStart input】
> L125:     * 【93†SubagentStop】
> L126:     * 【94†SubagentStop input】
> L127:     * 【95†TaskCreated】
> L128:     * 【96†TaskCreated input】
> L129:     * 【97†TaskCreated decision control】
> L130:     * 【98†TaskCompleted】
> L131:     * 【99†TaskCompleted input】
> L132:     * 【100†TaskCompleted decision control】
> L133:     * 【101†Stop】
> L134:     * 【102†Stop input】
> L135:     * 【103†Stop decision control】
> L136:     * 【104†StopFailure】
> L137:     * 【105†StopFailure input】
> L138:     * 【106†TeammateIdle】
> L139:     * 【107†TeammateIdle input】
> L140:     * 【108†TeammateIdle decision control】
> L141:     * 【109†ConfigChange】
> L142:     * 【110†ConfigChange input】
> L143:     * 【111†ConfigChange decision control】
> L144:     * 【112†CwdChanged】
> L145:     * 【113†CwdChanged input】
> L146:     * 【114†CwdChanged output】
> L147:     * 【115†DirectoryAdded】
> L148:     * 【116†DirectoryAdded input】
> L149:     * 【117†FileChanged】
> L150:     * 【118†FileChanged input】
> L151:     * 【119†FileChanged output】
> L152:     * 【120†WorktreeCreate】
> L153:     * 【121†WorktreeCreate input】
> L154:     * 【122†WorktreeCreate output】
> L155:     * 【123†WorktreeRemove】
> L156:     * 【124†WorktreeRemove input】
> L157:     * 【125†PreCompact】
> L158:     * 【126†PreCompact input】
> L159:     * 【127†PreCompact output】
> L160:     * 【128†PostCompact】
> L161:     * 【129†PostCompact input】
> L162:     * 【130†PreModelSwitch】
> L163:     * 【131†PreModelSwitch input】
> L164:     * 【132†PreModelSwitch decision control】
> L165:     * 【133†PreModelSwitch timeouts and other exit codes】
> L166:     * 【134†PostModelSwitch】
> L167:     * 【135†PostModelSwitch input】
> L168:     * 【136†PostModelSwitch decision control】
> L169:     * 【137†SessionEnd】
> L170:     * 【138†SessionEnd input】
> L171:     * 【139†Elicitation】
> L172:     * 【140†Elicitation input】
> L173:     * 【141†Elicitation output】
> L174:     * 【142†Other ways to decline an elicitation】
> L175:     * 【143†Answer a form request from a script】
> L176:     * 【144†ElicitationResult】
> L177:     * 【145†ElicitationResult input】
> L178:     * 【146†ElicitationResult output】
> L179:   * 【147†Prompt-based hooks】
> L180:     * 【148†How prompt-based hooks work】
> L181:     * 【149†Prompt hook configuration】
> L182:     * 【150†Response schema】
> L183:     * 【151†Check multiple conditions before stopping】
> L184:   * 【152†Agent-based hooks】
> L185:     * 【153†How agent hooks work】
> L186:     * 【154†Agent hook configuration】
> L187:   * 【155†Run hooks in the background】
> L188:     * 【156†Configure an async hook】
> L189:     * 【157†How async hooks execute】
> L190:     * 【158†Run tests after file changes】
> L191:     * 【159†Limitations】
> L192:   * 【160†Security considerations】
> L193:     * 【161†Disclaimer】
> L194:     * 【162†Workspace trust】
> L195:     * 【163†Security best practices】
> L196:   * 【164†Windows PowerShell tool】
> L197:     * 【165†Reference scripts by path in PowerShell hooks】
> L198:   * 【166†Debug hooks】
> L199: Reference
> L200: # Hooks reference
> L201: 
> L202: Reference for Claude Code hook events, configuration schema, JSON input/output formats, exit codes, async hooks, HTTP hooks, prompt hooks, and MCP tool hooks.
> L203: 
> L204: Copy page Copy page
> L205: 
> L206: For a quickstart guide with examples, see 【167†Automate actions with hooks】.
> L207: Hooks are user-defined shell commands, HTTP endpoints, MCP tool calls, LLM prompts, or subagents that execute automatically at specific points in Claude Code’s lifecycle. Claude Code fires the same hook events wherever it runs: sessions in the terminal, IDE extensions, the 【168†Desktop app】, and 【169†cloud sessions】. Use this reference to look up event schemas, configuration options, JSON input/output formats, and advanced features like async hooks, HTTP hooks, and MCP tool hooks.
> L208: A plugin can also register hooks as JavaScript functions that Claude Code calls in its own process, which can draw in the interface as well as act on events. A plugin that does is a 【170†mod】, and those function hooks are covered in 【171†React to events】 rather than here. The hooks on this page keep working alongside mods.
> L209: ##
> L210: 
> L211: 【4†​】
> L212: 
> L213: Hook lifecycle
> L214: 
> L215: Claude Code runs hooks at specific points during a session. When an event fires and a matcher matches, Claude Code passes JSON context about the event to your hook handler. For command hooks, input arrives on stdin. For HTTP hooks, it arrives as the POST request body. Your handler can then inspect the input, take action, and optionally return a decision. Events fall into three cadences:
> L216:   * per session: `SessionStart` and `SessionEnd`
> L217:   * per turn: `UserPromptSubmit`, `Stop`, and `StopFailure`
> L218:   * on every tool call inside the agentic loop: `PreToolUse` and `PostToolUse`, except 【172†`EndConversation`】 calls, which skip both
> L219: 【173†Image: Hook lifecycle diagram showing optional Setup feeding into SessionStart, then a per-turn loop containing UserPromptSubmit, UserPromptExpansion for slash commands, the nested agentic loop (PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, PostToolBatch, SubagentStart/Stop, TaskCreated, TaskCompleted), and Stop or StopFailure, followed by TeammateIdle, PreCompact, PostCompact, and SessionEnd, with Elicitation and ElicitationResult nested inside MCP tool execution, PermissionDenied as a side branch from PermissionRequest for auto-mode denials, WorktreeCreate, WorktreeRemove, Notification, ConfigChange, InstructionsLoaded, CwdChanged, FileChanged, and DirectoryAdded as standalone async events, PreModelSwitch as a standalone sequential event that runs before a requested model switch, PostModelSwitch as a standalone async event that runs after the session's model changes, and MessageDisplay as a display-only event that runs while assistant message text streams†mintcdn.com】【174†Image: Hook lifecycle diagram showing optional Setup feeding into SessionStart, then a per-turn loop containing UserPromptSubmit, UserPromptExpansion for slash commands, the nested agentic loop (PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, PostToolBatch, SubagentStart/Stop, TaskCreated, TaskCompleted), and Stop or StopFailure, followed by TeammateIdle, PreCompact, PostCompact, and SessionEnd, with Elicitation and ElicitationResult nested inside MCP tool execution, PermissionDenied as a side branch from PermissionRequest for auto-mode denials, WorktreeCreate, WorktreeRemove, Notification, ConfigChange, InstructionsLoaded, CwdChanged, FileChanged, and DirectoryAdded as standalone async events, PreModelSwitch as a standalone sequential event that runs before a requested model switch, PostModelSwitch as a standalone async event that runs after the session's model changes, and MessageDisplay as a display-only event that runs while assistant message text streams†mintcdn.com】
>
> --------------------------------------------------------------------------------
> Configure permissions - Claude Code Docs (https://code.claude.com/docs/en/permissions)
> 【turn989820view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://code.claude.com/docs/en/permissions","lineno":null}); Total lines: 821
> L0: > ## Documentation Index
> L1: >
> L2: > Fetch the complete documentation index at: 【0†/docs/llms.txt】
> L3: >
> L4: > Use this file to discover all available pages before exploring further.
> L5: 
> L6: 【1†Skip to main content】
> L7: 
> L8: 【2†Claude Code Docs home page】
> L9: 
> L10: Search...
> L11: 
> L12: Navigation
> L13: 
> L14: Permissions and sandboxing
> L15: 
> L16: Configure permissions
> L17: 
> L18: Getting started
> L19: 
> L20: Build with Claude Code
> L21: 
> L22: Plugins
> L23: 
> L24: Administration
> L25: 
> L26: Configuration
> L27: 
> L28: Reference
> L29: 
> L30: Agent SDK
> L31: 
> L32: 【3†Resources】
> L33: ## On this page
> L34: 
> L35: Back to top
> L36:   * 【4†Permission system】
> L37:     * 【5†Add a comment when you answer a permission prompt】
> L38:   * 【6†Manage permissions】
> L39:   * 【7†Permission modes】
> L40:   * 【8†Permission rule syntax】
> L41:     * 【9†Match all uses of a tool】
> L42:     * 【10†Use specifiers for fine-grained control】
> L43:     * 【11†Match by input parameter】
> L44:     * 【12†Wildcard patterns】
> L45:     * 【13†Tool name wildcards】
> L46:   * 【14†Tool-specific permission rules】
> L47:     * 【15†Bash】
> L48:     * 【16†Compound commands】
> L49:     * 【17†Wrappers】
> L50:     * 【18†Exec wrappers and find actions】
> L51:     * 【19†What a Bash rule doesn’t match】
> L52:     * 【20†Read-only commands】
> L53:     * 【21†Redirections】
> L54:     * 【22†PowerShell】
> L55:     * 【23†Read and Edit】
> L56:     * 【24†What Read and Edit rules cover】
> L57:     * 【25†Write(path), Glob(path), and Grep(path) rules don’t match】
> L58:     * 【26†How path patterns match】
> L59:     * 【27†Special characters and ! negation】
> L60:     * 【28†Symlinks】
> L61:     * 【29†Network paths】
> L62:     * 【30†WebFetch】
> L63:     * 【31†Allow or deny every fetch】
> L64:     * 【32†MCP】
> L65:     * 【33†Agent (subagents)】
> L66:     * 【34†Cd】
> L67:   * 【35†Extend permissions with hooks】
> L68:     * 【36†Precedence among rules, hooks, and mods】
> L69:     * 【37†Hook approvals in plan mode】
> L70:   * 【38†Working directories】
> L71:     * 【39†Block file-tool reads and writes outside the working directories】
> L72:     * 【40†Move the session to another directory】
> L73:     * 【41†Additional directories grant file access, not configuration】
> L74:     * 【42†Where output styles, hooks, and local settings load from】
> L75:   * 【43†How permissions interact with sandboxing】
> L76:   * 【44†Managed settings】
> L77:   * 【45†Settings precedence】
> L78:   * 【46†Project allow rules and workspace trust】
> L79:     * 【47†When your local settings file needs trust】
> L80:     * 【48†What runs before you trust a folder】
> L81:   * 【49†Example configurations】
> L82:   * 【50†See also】
> L83: Permissions and sandboxing
> L84: # Configure permissions
> L85: 
> L86: Control what Claude Code can access and do with fine-grained permission rules, modes, and managed policies.
> L87: 
> L88: Copy page Copy page
> L89: 
> L90: Claude Code supports fine-grained permissions so that you can specify exactly what the agent is allowed to do and what it can’t. You can check permission settings into version control to share them with every developer in your organization, and each developer can customize their own.
> L91: ##
> L92: 
> L93: 【4†​】
> L94: 
> L95: Permission system
> L96: 
> L97: Claude Code uses a tiered permission system to balance power and safety. The table shows, for each tool type, whether Manual mode asks before the action runs. The other 【7†permission modes】 change which of these ask you; in auto mode a classifier reviews actions instead of you, and 【51†how the classifier evaluates actions】 lists which ones it sees.
> L98: Tool type  | Example  | Approval required  | ”Yes, and don’t ask again” behavior
> L99: --- | --- | --- | ---
> L100: Read-only  | File reads, Grep  | No, within the 【38†working directory and additional directories】  | N/A
> L101: Bash commands  | Shell execution  | Yes, except a built-in set of 【20†read-only commands】  | Permanently per repository and command
> L102: File modification  | Edit/write files  | Yes  | Until session end
> L103: Web fetch  | WebFetch  | Yes, except a built-in set of 【52†preapproved documentation domains】  | Permanently per repository and domain
> L104: Web search  | WebSearch  | Yes  | Permanently per repository
> L105: A permission prompt shows what Claude is about to do, followed by your options. This example is the prompt for a Bash command, from a session in Manual mode:
> L106: 【53†Image: A Claude Code permission prompt titled Bash command. Under a tip about auto mode, it shows the description 'Run the test suite', the command npm test, and the line 'This command requires approval', then asks 'Do you want to proceed?' with four options: Yes; Yes, and don't ask again for: npm test *; Yes, and switch to auto mode; and No. A footer lists two keys: Esc to cancel and Tab to amend.†mintcdn.com】【54†Image: A Claude Code permission prompt titled Bash command.
> L107: Under a tip about auto mode, it shows the description 'Run the test suite', the command npm test, and the line 'This command requires approval', then asks 'Do you want to proceed?' with four options: Yes; Yes, and don't ask again for: npm test *; Yes, and switch to auto mode; and No. A footer lists two keys: Esc to cancel and Tab to amend.†mintcdn.com】
> L108: The third option, Yes, and switch to auto mode, 【55†doesn’t appear on every prompt】. When you choose “Yes, and don’t ask again” and the approval saves permanently, such as for a Bash command or a WebFetch domain, Claude Code saves the rule to `.claude/settings.local.json` at the root of the git repository, resolved through 【56†worktrees】 to the main checkout. The rule applies to future sessions anywhere in that repository, including sessions started in subdirectories and in worktrees.
> L109: A file-modification approval isn’t saved to the file: as the table shows, it lasts until the session ends. In some cases, such as outside a git repository or on Windows, Claude Code doesn’t use the repository root; 【57†Where Claude Code looks for each file】 lists those cases and where it saves the rule instead. Sometimes a permission prompt offers only a one-time approval, with no “don’t ask again” option and no option to allow the action for the rest of the session.
> L110: Claude Code offers those options only when the prompt can show you everything they would allow, so a rule you save from a prompt covers only what its option named. When a prompt offers only the one-time approval, approve the action once, or add the rule yourself in 【6†`/permissions`】. To stop the prompts for a command that starts with an exec wrapper such as `watch`, or for a `find` command with an action such as `-delete`, see 【18†Exec wrappers and `find` actions】.
> L111: ###
> L112: 
> L113: 【5†​】
> L114: 
> L115: Add a comment when you answer a permission prompt
> L116: You can attach a note to Claude when you approve or deny a single action. On most permission prompts, including Bash, PowerShell, file, and MCP tool prompts, move to Yes or No and press `Tab` to open a comment field on that option. WebFetch and browser prompts don’t offer the field. The options that allow the action for the rest of the session or save a rule don’t take one either. With the field open, type the comment and then press one of these keys:
> L117:   * `Enter`: submits your answer with the comment attached. If you leave the field empty, Claude Code submits the answer without a comment.
> L118:   * `Tab`: closes the field without answering. Claude Code keeps the text you typed and still sends it if you answer with that option.
> L119:   * `Shift+Tab`: on a file prompt, such as an Edit or Write prompt, closes the field the same as `Tab`. Before v2.1.235, pressing `Shift+Tab` inside the field instead selected the option that allows the action for the rest of the session, so Claude Code approved the action for the rest of the session and discarded the comment.
> L120: Claude Code delivers the comment differently depending on how you answered:
> L121:   * Yes: Claude Code runs the action, then sends your comment to Claude after the result.
> L122:   * No: Claude Code sends your comment to Claude as the reason for the denial, and Claude continues working. If you select No without a comment on a prompt from the main conversation, Claude Code stops the turn.
> L123: ##
> L124: 
> L125: 【6†​】
> L126: 
> L127: Manage permissions
> L128: 
> L129: You can view and manage Claude Code’s tool permissions with `/permissions`. The dialog lists all permission rules and the `settings.json` file each rule comes from. You can open the dialog while Claude is working: when you add or remove a rule, Claude Code applies the change starting with Claude’s next tool call in the same turn. Before v2.1.234, Claude Code queued the command until the turn finished.
> L130:   * Allow rules let Claude Code use the specified tool without manual approval.
> L131:   * Ask rules prompt for confirmation whenever Claude Code tries to use the specified tool.
> L132:   * Deny rules prevent Claude Code from using the specified tool.
>
> --------------------------------------------------------------------------------
> About code owners - GitHub Docs (https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
> 【turn989820view2】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners","lineno":null}); Total lines: 175
> L0:   1.   2. 【0†GitHub Docs】
> L1: 
> L2: Search or ask Copilot/
> L3: 
> L4: Menu
> L5: 
> L6: Collapse sidebar
> L7: 
> L8: Expand sidebar
> L9: 
> L10:   1. 【0†Home】
> L11:   2. 【1†Repositories】
> L12:   3. 【2†Manage repository settings】
> L13:   4. 【3†Customize your repository】
> L14:   5. About code owners
> L15: 
> L16: In this article
> L17: 
> L18: # About code owners
> L19: 
> L20: You can use a CODEOWNERS file to define individuals or teams that are responsible for code in a repository.
> L21: 
> L22: Copy markdown
> L23: ## Who can use this feature?
> L24: 
> L25: People with write permissions for the repository can create or edit the CODEOWNERS file and be listed as code owners. People with admin or owner permissions can require that pull requests have to be approved by code owners before they can be merged.
> L26: You can define code owners in public repositories with GitHub Free and GitHub Free for organizations, and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server. See 【4†GitHub's plans】.
> L27: ## In this article
> L28: 
> L29:   * 【5†About code owners】
> L30: 
> L31:   * 【6†CODEOWNERS file location】
> L32: 
> L33:   * 【7†CODEOWNERS and forks】
> L34: 
> L35:   * 【8†CODEOWNERS file size】
> L36: 
> L37:   * 【9†CODEOWNERS syntax】
> L38: 
> L39:   * 【10†CODEOWNERS and branch protection】
> L40: 
> L41:   * 【11†Further reading】
> L42: The people you choose as code owners must have write permissions for the repository. When the code owner is a team, that team must be visible and it must have write permissions, even if all the individual members of the team already have write permissions directly, through organization membership, or through another team membership.
> L43: ## 【5†About code owners】
> L44: Code owners are automatically requested for review when someone opens a pull request that modifies code that they own. Code owners are not automatically requested to review draft pull requests. For more information about draft pull requests, see 【12†Pull requests】. When you mark a draft pull request as ready for review, code owners are automatically notified. If you convert a pull request to a draft, people who are already subscribed to notifications are not automatically unsubscribed.
> L45: For more information, see 【13†Changing the stage of a pull request】.
> L46: When someone with admin or owner permissions has enabled required reviews, they also can optionally require approval from a code owner before the author can merge a pull request in the repository. For more information, see 【14†About protected branches】.
> L47: 
> L48: If a file has a code owner, you can see who the code owner is before you open a pull request. In the repository, you can browse to the file and hover over to see a tool tip with codeownership details.
> L49: 【15†Image: Screenshot showing the header for a file. The cursor hovers over a shield icon with the tooltip "Owned by USER or TEAM (from CODEOWNERS line NUMBER)."】
> L50: ## 【6†CODEOWNERS file location】
> L51: 
> L52: To use a CODEOWNERS file, create a new file called `CODEOWNERS` in the `.github/`, root, or `docs/` directory of the repository, in the branch where you'd like to add the code owners. If `CODEOWNERS` files exist in more than one of those locations, GitHub will search for them in that order and use the first one it finds.
> L53: Each CODEOWNERS file assigns the code owners for a single branch in the repository. Thus, you can assign different code owners for different branches, such as `@octo-org/codeowners-team` for a code base on the default branch and `@octocat` for a GitHub Pages site on the `gh-pages` branch.
> L54: For code owners to receive review requests, the CODEOWNERS file must be on the base branch of the pull request. For example, if you assign `@octocat` as the code owner for .js files on the `gh-pages` branch of your repository, `@octocat` will receive review requests when a pull request with changes to .js files is opened between the head branch and `gh-pages`.
> L55: ## 【7†CODEOWNERS and forks】
> L56: 
> L57: To trigger review requests, pull requests use the version of `CODEOWNERS` from the base branch of the pull request. The base branch is the branch that a pull request will modify if the pull request is merged.
> L58: If you create a pull request from a fork, and the base branch is in the upstream repository, then the pull request will use the `CODEOWNERS` file from that branch in the upstream repository. If the base branch is a branch within your fork, then the pull request will use the `CODEOWNERS` file from that branch in your fork, but this will only trigger review requests if the code owners are added to your fork specifically with `write` access.
> L59: When you view who is responsible for a file by hovering over , you will see information from the `CODEOWNERS` file for whichever branch in whichever repository you're looking at.
> L60: ## 【8†CODEOWNERS file size】
> L61: 
> L62: CODEOWNERS files must be under 3 MB in size. A CODEOWNERS file over this limit will not be loaded, which means that code owner information is not shown and the appropriate code owners will not be requested to review changes in a pull request.
> L63: 
> L64: To reduce the size of your CODEOWNERS file, consider using wildcard patterns to consolidate multiple entries into a single entry.
> L65: ## 【9†CODEOWNERS syntax】
> L66: 
> L67: Warning
> L68: 
> L69: There are some syntax rules for gitignore files that do not work in CODEOWNERS files:
> L70: 
> L71:   * Escaping a pattern starting with `#` using `\` so it is treated as a pattern and not a comment doesn't work
> L72:   * Using `!` to negate a pattern doesn't work
> L73:   * Using `[ ]` to define a character range doesn't work
> L74: A CODEOWNERS file uses a pattern that follows most of the same rules used in 【16†gitignore†git-scm.com】 files. The pattern is followed by one or more GitHub usernames or team names using the standard `@username` or `@org/team-name` format. Users and teams must have explicit `write` access to the repository, even if the team's members already have access.
> L75: If you want to match two or more code owners with the same pattern, all the code owners must be on the same line. If the code owners are not on the same line, the pattern matches only the last mentioned code owner.
> L76: In most cases, you can also refer to a user by an email address that has been added to their account, for example `user@example.com`. You cannot use an email address to refer to a managed user account. For more information about managed user accounts, see 【17†About Enterprise Managed Users】" in the GitHub Enterprise Cloud documentation.
> L77: CODEOWNERS paths are case sensitive, because GitHub uses a case sensitive file system. Since CODEOWNERS are evaluated by GitHub, even systems that are case insensitive (for example, macOS) must use paths and files that are cased correctly in the CODEOWNERS file.
> L78: If any line in your CODEOWNERS file contains invalid syntax, that line will be skipped. When you navigate to the CODEOWNERS file in your repository, you can see any errors highlighted. A list of errors in a repository's CODEOWNERS file is also accessible via the API. For more information, see 【18†REST API endpoints for repositories】.
> L79: 
> L80: If you specify a user or team that doesn't exist or has insufficient access, a code owner will not be assigned.
> L81: ### 【19†Example of a CODEOWNERS file】
> L82: 
> L83:     `# This is a comment.
> L84:     # Each line is a file pattern followed by one or more owners.
> L85: 
> L86:     # These owners will be the default owners for everything in
> L87:     # the repo. Unless a later match takes precedence,
> L88:     # @global-owner1 and @global-owner2 will be requested for
> L89:     # review when someone opens a pull request.
> L90:     *       @global-owner1 @global-owner2
> L91: 
> L92:     # Order is important; the last matching pattern takes the most
> L93:     # precedence. When someone opens a pull request that only
> L94:     # modifies JS files, only @js-owner and not the global
> L95:     # owner(s) will be requested for a review.
> L96:     *.js    @js-owner #This is an inline comment.
> L97: 
> L98:     # You can also use email addresses if you prefer. They'll be
> L99:     # used to look up users just like we do for commit author
> L100:     # emails.
> L101:     *.go docs@example.com
> L102: 
> L103:     # Teams can be specified as code owners as well. Teams should
> L104:     # be identified in the format @org/team-name. Teams must have
> L105:     # explicit write access to the repository. In this example,
> L106:     # the octocats team in the octo-org organization owns all .txt files.
> L107:     *.txt @octo-org/octocats
> L108: 
> L109:     # In this example, @doctocat owns any files in the build/logs
> L110:     # directory at the root of the repository and any of its
> L111:     # subdirectories.
> L112:     /build/logs/ @doctocat
> L113: 
> L114:     # The `docs/*` pattern will match files like
> ```
>
> MCP tool call
>
> codex_apps.cloud_environment.environment_status
>
> ```json
> {}
> ```
>
> ```text
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> ```json
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> - Ran `git ls-remote origin refs/heads/main && rg -n 'P[012]|telemetr|Telemetr|gitleaks|Gitleaks|semantic|Semantic|secret|Secret|CODEOWNERS|protection|adapter|Adapter|North Stars|Scale-Adaptive|10k|50k|local_repo_data' docs/decisions_and_roadmap.md skills/manage-meta-project/SKILL.md skills/tune-meta-project/SKILL.md .agents/team/agent-dev-lead/profile.md templates/team/profile.md .agents/project_knowledge/tasks.md && cat .github/workflows/ci.yml && sed -n '1,165p' scripts/sync_templates.py`
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "find": [
>     {
>       "pattern": "permissionDecision",
>       "ref_id": "https://code.claude.com/docs/en/hooks"
>     },
>     {
>       "pattern": "What Read and Edit rules cover",
>       "ref_id": "https://code.claude.com/docs/en/permissions"
>     },
>     {
>       "pattern": "Bash and other shell commands",
>       "ref_id": "https://code.claude.com/docs/en/permissions"
>     },
>     {
>       "pattern": "protect",
>       "ref_id": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ```text
> Hooks reference - Claude Code Docs (https://code.claude.com/docs/en/hooks)
> 【turn615946view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://code.claude.com/docs/en/hooks","pattern":"permissionDecision"}); Total lines: 4119
> L287: The script reads the JSON input from stdin, extracts the command, and returns a `permissionDecision` of `"deny"` if it contains `rm -rf`. Save it to `.claude/hooks/block-rm.sh` in your project and make it executable with `chmod +x .claude/hooks/block-rm.sh` so Claude Code can run it:
> L288: 
> L289:     `#!/bin/bash
> L290:     # .claude/hooks/block-rm.sh
> L291:     COMMAND=$(jq -r '.tool_input.command')
> L292: 
> L293:     if echo "$COMMAND" | grep -q 'rm -rf'; then
> L294:       jq -n '{
> L295:         hookSpecificOutput: {
> L296:           hookEventName: "PreToolUse",
> L297:           permissionDecision: "deny",
> L298:           permissionDecisionReason: "Destructive command blocked by hook"
> L299:         }
> L300:       }'
> L301:     else
> L302:       exit 0  # no decision; normal permission flow applies
> L303:     fi
> L304:     `
> L305: This script, like the other Bash examples on this page that parse JSON input, uses `jq`, so install `jq` and make sure it is on your `PATH` before trying them.
> L306: The matcher `Bash|PowerShell` covers the 【176†PowerShell tool】 as well as Bash. A single `if` rule names one tool, so each tool gets its own handler: the first narrows to Bash subcommands matching `rm *`, the second to PowerShell commands matching `Remove-Item *`. Both run the same script through `powershell.exe`:
> L307: 
> L308:     `{
> L309:       "hooks": {
> L310:         "PreToolUse": [
> L311:           {
> L312:             "matcher": "Bash|PowerShell",
> L313:             "hooks": [
> L314:               {
> L315:                 "type": "command",
> L316:                 "if": "Bash(rm *)",
> L317:                 "command": "powershell.exe",
> L318:                 "args": [
> L319:                   "-NoProfile",
> L320:                   "-ExecutionPolicy",
> L321:                   "Bypass",
> L322:                   "-File",
> L323:                   "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.ps1"
> L324:                 ]
> L325:               },
> L326:               {
> L327:                 "type": "command",
> L328:                 "if": "PowerShell(Remove-Item *)",
> L329:                 "command": "powershell.exe",
> L330:                 "args": [
> L331:                   "-NoProfile",
> L332:                   "-ExecutionPolicy",
> L333:                   "Bypass",
> L334:                   "-File",
> L335:                   "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.ps1"
> L336:                 ]
> L337:               }
> L338:             ]
> L339:           }
> L340:         ]
> L341:       }
> L342:     }
> L343:     `
> L344: The `-NoProfile` flag skips loading your PowerShell profile so the hook starts fast, and `-ExecutionPolicy Bypass` lets PowerShell run the local script file.The script reads the JSON input from stdin, extracts the command, and returns a `permissionDecision` of `"deny"` if it contains `rm -rf` or `Remove-Item` followed by `-Recurse`. Save it to `.claude/hooks/block-rm.ps1` in your project:
> L345: 
> L346:     `# .claude/hooks/block-rm.ps1
> L347:     $callInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
> L348:     $command = $callInput.tool_input.command
> L349: 
> L350:     if ($command -match 'rm -rf|Remove-Item.*-Recurse') {
> L351:       @{
> L352:         hookSpecificOutput = @{
> L353:           hookEventName = "PreToolUse"
> L354:           permissionDecision = "deny"
> L355:           permissionDecisionReason = "Destructive command blocked by hook"
> L356:         }
> L357:       } | ConvertTo-Json
> L358:     } else {
> L359:       exit 0  # no decision; normal permission flow applies
> L360:     }
> L361:     `
> L362: Now suppose Claude Code decides to run `Bash "rm -rf /tmp/build"` against the macOS/Linux config. Here’s what happens:
> L363: 【177†Image: Diagram of hook resolution: PreToolUse fires, the matcher checks for a Bash match, then the if condition checks for a Bash(rm *) match. If both match, the hook command runs and returns permissionDecision deny, so the tool call is blocked and Claude Code continues.
> L364: If either check fails to match, the hook is skipped and the tool call is allowed to proceed.†mintcdn.com】【178†Image: Diagram of hook resolution: PreToolUse fires, the matcher checks for a Bash match, then the if condition checks for a Bash(rm *) match. If both match, the hook command runs and returns permissionDecision deny, so the tool call is blocked and Claude Code continues. If either check fails to match, the hook is skipped and the tool call is allowed to proceed.†mintcdn.com】
> L365: 1
> L366: 
> L367: Event fires
> L368: 
> L369: The `PreToolUse` event fires. Claude Code sends the tool input as JSON on stdin to the hook:
> L370: 
> L371:     `{ "tool_name": "Bash", "tool_input": { "command": "rm -rf /tmp/build" }, ... }
> L372:     `
> L373: 
> L374: 2
> L375: 
> L376: Matcher checks
> L377: 
> L378: The matcher `"Bash"` matches the tool name, so this hook group activates. If you omit the matcher or use `"*"`, the group activates on every occurrence of the event.
> L379: 
> L380: 3
> L381: 
> L382: If condition checks
> L383: The `if` condition `"Bash(rm *)"` matches because `rm -rf /tmp/build` is a subcommand matching `rm *`, so this handler spawns. If the command had been `npm test`, the `if` check would fail and `block-rm.sh` would never run, avoiding the process spawn overhead. The `if` field is optional; without it, every handler in the matched group runs.
> L384: 
> L385: 4
> L386: 
> L387: Hook handler runs
> L388: The script inspects the full command and finds `rm -rf`, so it prints a decision to stdout:
> L389: 
> L390:     `{
> L391:       "hookSpecificOutput": {
> L392:         "hookEventName": "PreToolUse",
> L393:         "permissionDecision": "deny",
> L394:         "permissionDecisionReason": "Destructive command blocked by hook"
> L395:       }
> L396:     }
> L397:     `
> L398: If the command had been a safer `rm` variant like `rm file.txt`, the script would hit `exit 0` instead. Exit code 0 with no output means the hook has no decision to report, so the tool call continues through the normal 【179†permission flow】. The hook can deny the call, but staying silent doesn’t approve it.
> L399: 
> L400: 5
> L401: 
> L402: Claude Code acts on the result
> L403: 
> L404: Claude Code reads the JSON decision, blocks the tool call, and shows Claude the reason.
> L1235: PreToolUse  | `hookSpecificOutput`  | `permissionDecision` (allow/deny/ask/defer), `permissionDecisionReason`
> L1236: PreModelSwitch  | `hookSpecificOutput` or top-level `decision`  | `permissionDecision` (allow/deny/ask), `permissionDecisionReason`. `decision: "block"` also 【132†cancels the switch】
> L1237: PermissionRequest  | `hookSpecificOutput`  | `decision.behavior` (allow/deny)
> L1938: `updatedInput`  | Modifies the tool’s input parameters before execution. Replaces the entire input object, so include unchanged fields alongside modified ones. Claude Code evaluates permission rules and a Bash command’s 【287†auto-background eligibility】 against the input your hook returns, not the input Claude sent. Combine with `"allow"` to auto-approve, or `"ask"` to show the modified input to the user. For `"defer"`, ignored. With no `permissionDecision`, 【67†auto mode can deny the changed call】
> L1939: `additionalContext`  | String added to Claude’s context alongside the tool result. Ignored when `permissionDecision` is `"defer"`. See 【39†Add context for Claude】
> L1940: When multiple PreToolUse hooks return different decisions, precedence is `deny` > `defer` > `ask` > `allow`. A hook that blocks by exiting 2 routes the same way as `"deny"`: Claude sees the stderr message as the denial reason.
> L1941: When a hook returns `"ask"`, the permission prompt displayed to the user includes a label identifying where the hook came from: `[settings]` for a hook from any settings file or from agent frontmatter, `[plugin:<name>]` for a plugin’s hook, or `[skill]` for a hook from skill frontmatter. This helps users understand which configuration source is requesting confirmation.
> L1942: 
> L1943:     `{
> L1944:       "hookSpecificOutput": {
> L1945:         "hookEventName": "PreToolUse",
> L1946:         "permissionDecision": "allow",
> L1947:         "permissionDecisionReason": "My reason here",
> L1948:         "updatedInput": {
> L1949:           "field_to_modify": "new value"
> L1950:         },
> L1951:         "additionalContext": "Current environment: production. Proceed with caution."
> L1952:       }
> L1953:     }
> L1954:     `
> L1955: PreToolUse previously used top-level `decision` and `reason` fields, but these are deprecated for this event. Use `hookSpecificOutput.permissionDecision` and `hookSpecificOutput.permissionDecisionReason` instead. The deprecated values `"approve"` and `"block"` map to `"allow"` and `"deny"` respectively. Other events like PostToolUse and Stop continue to use top-level `decision` and `reason` as their current format.
> L1956: ####
> L1957: 
> L1958: 【67†​】
> L1959: 
> L1960: PreToolUse `updatedInput` in auto mode
> L1961: 
> L1962: When your hook returns `updatedInput` with no `permissionDecision` in 【278†auto mode】, Claude Code can deny the changed call. 【288†The server reviewed】 the input Claude wrote, not the input your hook returned. In interactive terminal sessions and VS Code sessions on a direct connection to the Anthropic API, the denial includes this text:
> L1963: 
> L1964:     `a hook changed this call's input after auto mode reviewed it
> L1965:     `
> L1966: After a denial with this text, Claude can issue the changed call again so that the server reviews it. If Claude repeats the changed input exactly in its next response, your hook still runs:
> L1967:   * It can deny the call or send it to the permission prompt
> L1968:   * Any `updatedInput` it returns is dropped, so what runs is what the server reviewed
> L1969: You don’t need to change your hook for this denial unless 【289†Claude tells you in its reply that auto mode couldn’t check the call】. In the sessions that show this text, a 【14†`command` hook】 in settings or a plugin’s hooks file can change Bash, PowerShell, Monitor, Edit, Write, and NotebookEdit calls without this denial. The denial can still appear, such as when any hook changed an earlier call in the same Claude response or a Bash command asks to run outside the sandbox.
> L1970: ####
> L1971: 
> L1972: 【68†​】
> L1973: 
> L1974: PreToolUse `ask` decisions in auto mode
> L1975: 
> L1976: In 【278†auto mode】, a PreToolUse hook’s `"ask"` normally sends the tool call to the permission prompt, and the 【290†classifier】 doesn’t decide it. Some calls take a different path:
> L1987:   1. Reads the tool’s input from stdin
> L1988:   2. Collects the answer through your own UI
> L1989:   3. Returns `permissionDecision: "allow"` together with `updatedInput` that holds the answer, so the tool runs without prompting
> L1990: Returning `"allow"` alone is not sufficient for these tools. For `AskUserQuestion`, echo back the original `questions` array and add an 【293†`answers`】 object mapping each question’s text to the chosen answer. This output answers one question with `React`:
> L1991: 
> L1992:     `{
> L1993:       "hookSpecificOutput": {
> L1994:         "hookEventName": "PreToolUse",
> L1995:         "permissionDecision": "allow",
> L1996:         "updatedInput": {
> L1997:           "questions": [
> L1998:             {
> L1999:               "question": "Which framework?",
> L2000:               "header": "Framework",
> L2001:               "options": [{"label": "React", "description": "Component library"}, {"label": "Vue", "description": "Progressive framework"}],
> L2002:               "multiSelect": false
> L2003:             }
> L2004:           ],
> L2005:           "answers": {"Which framework?": "React"}
> L2021:   1. Claude calls `AskUserQuestion`. The `PreToolUse` hook fires.
> L2022:   2. The hook returns `permissionDecision: "defer"`. The tool doesn’t execute. The turn ends with a result carrying `stop_reason: "tool_deferred"`, and the pending tool call stays in the transcript.
> L2023:   3. The calling process reads `deferred_tool_use` from the SDK result, surfaces the question in its own UI, and waits for an answer.
> L2024:   4. The calling process runs `claude -p --resume <session-id>` with the same permission host. The same tool call fires `PreToolUse` again.
> L2025:   5. The hook returns `permissionDecision: "allow"` with the answer in `updatedInput`. The tool executes and Claude continues.
> L2026: The `deferred_tool_use` field carries the tool’s `id`, `name`, and `input`:
> L2027: 
> L2028:     `{
> L2029:       "type": "result",
> L2030:       "subtype": "success",
> L2031:       "stop_reason": "tool_deferred",
> L2032:       "session_id": "abc123",
> L2033:       "deferred_tool_use": {
>
> --------------------------------------------------------------------------------
> Configure permissions - Claude Code Docs (https://code.claude.com/docs/en/permissions)
> 【turn615946view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://code.claude.com/docs/en/permissions","pattern":"What Read and Edit rules cover"}); Total lines: 821
> L51:     * 【19†What a Bash rule doesn’t match】
> L52:     * 【20†Read-only commands】
> L53:     * 【21†Redirections】
> L54:     * 【22†PowerShell】
> L55:     * 【23†Read and Edit】
> L56:     * 【24†What Read and Edit rules cover】
> L57:     * 【25†Write(path), Glob(path), and Grep(path) rules don’t match】
> L58:     * 【26†How path patterns match】
> L59:     * 【27†Special characters and ! negation】
> L60:     * 【28†Symlinks】
> L61:     * 【29†Network paths】
> L62:     * 【30†WebFetch】
> L63:     * 【31†Allow or deny every fetch】
> L64:     * 【32†MCP】
> L65:     * 【33†Agent (subagents)】
> L66:     * 【34†Cd】
> L385: Common aliases are canonicalized before matching. A rule written for the cmdlet name also matches those aliases, so `PowerShell(Get-ChildItem *)` matches `gci`, `ls`, and `dir` as well. Matching is case-insensitive. Claude Code parses the PowerShell AST and checks each command in a compound command independently. Pipeline operators `|`, statement separators `;`, and on PowerShell 7+ the chain operators `&&` and `||` split a compound command into subcommands.
> L386: Every subcommand must be allowed for the compound command to run without a prompt, for example by matching an allow rule.
> L387: ###
> L388: 
> L389: 【23†​】
> L390: 
> L391: Read and Edit
> L392: 
> L393: To block Claude’s file tools from reading a file or directory, add a `Read` deny rule for its path, such as `Read(./.env)` or `Read(./secrets/**)`; 【84†Exclude sensitive files】 has a paste-ready example. If your project has a `.claudeignore` file, it has no effect, so move its entries into `Read` deny rules.
> L394: ####
> L395: 
> L396: 【24†​】
> L397: 
> L398: What `Read` and `Edit` rules cover
> L399: `Edit` rules apply to all built-in tools that edit files. Claude makes a best-effort attempt to apply `Read(path)` deny rules to all built-in tools that read files like Grep and Glob. It makes the same attempt to apply `Read(path)` deny rules to `@file` mentions in your prompts and to the selection and open-file context that a connected 【85†IDE】 shares with Claude. A `Read(path)` deny rule also applies to image paths you paste into a prompt and directories you @-mention:
> L400:   * Image path: when you paste an image’s path or drag an image file into your prompt in the terminal and the rule matches that path, Claude Code doesn’t attach the image. If the paste holds no other image, the path stays in your prompt as text.
> L401:   * Directory: the 【86†listing Claude receives】 leaves out the file and directory names the rule matches.
> L402: Claude Code checks pasted image paths and directory listings in v2.1.290 and later. A `Read` deny rule also blocks the 【87†Edit and Write tools】 on the same path, including creating a new file there. NotebookEdit isn’t covered, so add an `Edit` deny rule for paths no tool may change. For the Write tool, the check requires Claude Code v2.1.228 or later.
> L403: Read and Edit deny rules apply to Claude’s built-in file tools, to file commands Claude Code recognizes in Bash, such as `cat`, `head`, `tail`, `sed`, and `tee`, and to the targets of Bash 【21†redirections】 such as `> file` and `< file`. They don’t apply to a command that reads files without naming them, such as `grep -r pattern .` run from the directory that holds the file, or to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself.
> L404: For OS-level enforcement that blocks all processes from accessing a path, 【80†enable the sandbox】.
> L405: ####
> L406: 
> L407: 【25†​】
> L408: 
> L409: `Write(path)`, `Glob(path)`, and `Grep(path)` rules don’t match
> L410: 
> L411: Claude Code checks file permissions against `Edit(path)` and `Read(path)` rules. It accepts a rule with a path other than `*` for one of the tools below but doesn’t match a read, search, or edit against it. A `Grep(docs/**)` deny rule doesn’t stop Grep from searching `docs`. Write the `Edit` or `Read` rule in its place:
> L412:   * `Write`, `NotebookEdit`, or legacy `MultiEdit`: use `Edit(docs/**)` in place of `Write(docs/**)`.
> L413:   * `Glob` or `Grep`: use `Read(docs/**)` in place of `Grep(docs/**)`. As an ask rule, `Read(docs/**)` prompts when Claude calls Grep or Glob on a matching path, but not when a search of a working directory above it returns matching files.
> L414: To match every use of one of these tools regardless of path, 【9†write only the tool name】.
> L415: ####
> L416: 
> L417: 【26†​】
> L418: 
> L419: How path patterns match
> L420: 
> L421: Read and Edit rules both use 【88†gitignore†git-scm.com】 pattern syntax with four distinct pattern types:
> L422: Pattern  | Meaning  | Example  | Matches
> L423: --- | --- | --- | ---
> L424: `//path`  | Absolute path from filesystem root  | `Read(//Users/alice/secrets/**)`  | `/Users/alice/secrets/**`
> L425: `~/path`  | Path from home directory  | `Read(~/Documents/*.pdf)`  | `/Users/alice/Documents/*.pdf`
> L426: `/path`  | Path relative to the settings source  | `Edit(/src/**/*.ts)`  | `<primary working directory>/src/**/*.ts` in project settings
> L427: `path` or `./path`  | Path relative to current directory  | `Read(*.env)`  | `<cwd>/*.env`
> L605: Adding any `Cd` allow rule switches `/cd` to allowlist mode: the resolved target directory must match one of your allow rules, or `/cd` refuses. With no `Cd` rules configured, `/cd` keeps its default behavior and prompts you to trust an unfamiliar directory. Path patterns share the `//`, `~/`, and `/` anchors from 【23†Read and Edit rules】, but matching is anchored to the whole directory path rather than gitignore-style. `*` matches exactly one path segment and `**` matches across segments.
>
> --------------------------------------------------------------------------------
> Configure permissions - Claude Code Docs (https://code.claude.com/docs/en/permissions)
> 【turn615946view2】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://code.claude.com/docs/en/permissions","pattern":"Bash and other shell commands"}); Total lines: 821
> L146: Mode  | Description
> L147: --- | ---
> L148: `default`  | Prompts for permission on first use of each tool. Labeled Manual in the CLI, the VS Code and JetBrains extensions, and the desktop app, and Claude Code accepts `manual` as an alias
> L149: `acceptEdits`  | Automatically accepts file edits and common filesystem commands such as `mkdir`, `touch`, `mv`, and `cp` for paths in the working directory or `additionalDirectories`
> L150: `plan`  | Claude reads files and runs read-only shell commands to explore but doesn’t edit your source files; with 【61†auto mode】 available, classifier-approved commands also run. Labeled Plan in the CLI and the VS Code extension
> L151: `auto`  | Runs without routine prompts; before actions such as shell commands and network requests run, a background 【61†classifier】 checks that they align with your request
> L152: `dontAsk`  | Auto-denies every call that would otherwise prompt, though a 【65†mod】 you installed can still approve some of those calls. File reads in your working directories and other actions that need no approval still run, as do tools pre-approved via `/permissions` or `permissions.allow` rules.
> L153: `AskUserQuestion`, MCP tools marked 【66†`requiresUserInteraction`】, 【29†reads from network paths】, and connector tools 【67†your organization set to `ask`】 in sessions where that setting reaches Claude Code are denied even if you’ve allowed them
> L154: `bypassPermissions`  | Skips permission prompts, except for the 【68†actions no mode auto-approves】
> L155: In `bypassPermissions` mode, Claude Code skips permission prompts, including for writes to 【69†protected paths】 such as `.git` and `.claude`. The 【70†cross-session messaging safeguards】 still apply. Only use this mode in isolated environments like containers or VMs where Claude Code can’t cause damage.
> L156: To prevent `bypassPermissions` or `auto` mode from being used, set `permissions.disableBypassPermissionsMode` or `permissions.disableAutoMode` to `"disable"` in any 【63†settings file】. These are most useful in 【44†managed settings】 where they can’t be overridden.
> L157: ##
> L158: 
> L159: 【8†​】
> L160: 
> L161: Permission rule syntax
> L162: 
> L163: Permission rules follow the format `Tool` or `Tool(specifier)`. Parentheses inside the specifier are literal, so a command or path that contains them needs no escaping.
> L164: ###
> L165: 
> L166: 【9†​】
> L167: 
> L168: Match all uses of a tool
> L169: 
> L170: To match all uses of a tool, use only the tool name without parentheses:
> L171: 
> L172: Rule  | Effect
> L173: --- | ---
> L174: `Bash`  | Matches all Bash commands
> L175: `WebFetch`  | Matches all web fetch requests
> L176: `Read`  | Matches all file reads
> L177: `Bash(*)` is equivalent to `Bash` and matches all Bash commands. As a deny rule, both forms remove the tool from Claude’s context. The label shown for a tool in the transcript and permission dialog can differ from its canonical name. For example, the tool labeled `Stop Task` in the transcript has the canonical name `TaskStop`. Permission rules and 【71†hook matchers】 don’t match the label, so a rule written as `Stop Task` doesn’t match. For deny and ask rules, a 【72†startup warning】 says so.
> L178: Use the canonical names listed in the 【73†tools reference】.
> L179: ###
> L180: 
> L181: 【10†​】
> L182: 
> L183: Use specifiers for fine-grained control
> L184: 
> L185: Add a specifier in parentheses to match specific tool uses:
> L186: 
> L187: Rule  | Effect
> L188: --- | ---
> L189: `Bash(npm run build)`  | Matches the exact command `npm run build`
> L190: `Read(./.env)`  | Matches reading the `.env` file in the current directory
> L191: `WebFetch(domain:example.com)`  | Matches fetch requests to example.com
> L192: ###
> L193: 
> L194: 【11†​】
> L195: 
> L196: Match by input parameter
> L197: Deny and ask rules can match a top-level input parameter on any built-in tool with `Tool(param:value)`. To match a parameter on an MCP tool, pass a deny rule with 【74†`--disallowedTools`】. When Claude Code loads a settings file, it skips any `mcp__` rule that has parentheses. Claude Code lists the skipped rule in the invalid-settings dialog when an interactive session starts, and in 【75†`claude doctor`】 output. A parameter rule matches when Claude calls the tool with that parameter set to that exact value.
> L208:   * The value supports `*` as a wildcard that matches any sequence of characters, so `Agent(isolation:*)` matches any explicit isolation value. Without `*` the match is exact
> L209:   * A parameter the model omits is never matched, so `Agent(model:*)` doesn’t match a call that leaves `model` unset
> L210:   * The value is compared against the literal input Claude sends, before any normalization. `Agent(model:opus)` matches the alias `opus` but not a full model ID
> L211:   * A `Skill(skill:<name>)` deny rule instead 【76†matches the skill under any of its names】, such as its alias or display name
> L212:   * Run with 【77†`--verbose`】 to see the exact parameter names and values in each tool call
> L213:   * Whitespace around the colon is ignored
> L214: You can’t match a tool’s primary content field this way: `command` for Bash and PowerShell, `file_path` for Read, Edit, and Write, `path` for Grep and Glob, `notebook_path` for NotebookEdit, and `url` for WebFetch. A rule like `Bash(command:rm *)` would be bypassable by a compound command, so Claude Code ignores it and emits a startup warning. Use `Bash(rm *)`, `Read(./path)`, or `WebFetch(domain:host)` instead.
> L215: ###
> L216: 
> L217: 【12†​】
> L218: 
> L219: Wildcard patterns
> L220: 
> L221: A `*` in a Bash rule matches any text, including spaces, so one rule covers a family of commands. A rule with no `*` matches one exact command.
> L524: Shell commands have their own check: in Manual mode, a read-only Bash or PowerShell command whose arguments include a UNC path 【20†still prompts on Windows】. In Claude Code v2.1.292 and later, each of these leaves the prompt in place:
> L579: In a 【97†Cowork†claude.com】 session in the Claude Desktop app, Claude runs shell commands through Cowork’s `mcp__workspace__bash` tool rather than the built-in `Bash` tool, and Cowork likewise provides `mcp__workspace__web_fetch` for web fetches. Claude Code also applies deny rules that name the whole `Bash` or `WebFetch` tool to these Cowork tools, so a managed `Bash` deny rule stops Claude from running shell commands in Cowork.
> L612: ##
> L613: 
> L614: 【35†​】
> L615: 
> L616: Extend permissions with hooks
> L617: 
> L618: 【100†Claude Code hooks】 let you register custom shell commands that evaluate permissions at runtime. When Claude Code makes a tool call, PreToolUse hooks run before the permission prompt, for every tool except 【59†`EndConversation`】. The hook output can deny the tool call, force a prompt, or skip the prompt to let the call proceed.
> L666:   * 【116†`permissions.blockWritesOutsideWorkingDirectories`】: the `Write`, `Edit`, and `NotebookEdit` tools refuse writes there, apart from some of Claude Code’s own files such as plan files. The key doesn’t limit shell commands, MCP tools, or the programs hooks run, so use 【80†sandboxing】 to limit where shell commands write. Requires Claude Code v2.1.314 or later.
> L667: To keep one outside directory reachable while either key is `true`, 【117†add it as a working directory】.
> L702: Claude Code discovers output styles from the current working directory and its parents, your user directory at `~/.claude/`, and managed settings. Hooks and other `.claude/settings.json` keys load from the current working directory’s `.claude/` folder with no parent-directory fallback, alongside your user `~/.claude/settings.json` and managed settings.
> L703: `.claude/settings.local.json` loads from the git repository root instead, even when you start Claude Code in a subdirectory, except where Claude Code 【57†doesn’t use the repository root】, such as on Windows. To share that configuration across projects, use one of these approaches:
> L704:   * User-level configuration: place files in `~/.claude/agents/`, `~/.claude/output-styles/`, or `~/.claude/settings.json` to make them available in every project
> L705:   * Plugins: package and distribute configuration as a 【122†plugin】 that teams can install
> L706:   * Launch from the config directory: run Claude Code from the directory containing the `.claude/` configuration you want
> L707: ##
> L708: 
> L709: 【43†​】
> L710: 
> L711: How permissions interact with sandboxing
> L712: 
> L713: Permissions and 【80†sandboxing】 are complementary security layers:
> L714:   * Permissions control which tools Claude Code can use and which files or domains it can access. They apply to Bash, Read, Edit, WebFetch, MCP, and every other tool, except that a deny or ask rule can’t block 【59†`EndConversation`】 while any other tool remains.
> L715:   * Sandboxing provides OS-level enforcement that restricts shell commands’ filesystem and network access. It applies to Bash, PowerShell, and 【135†Monitor】 tool commands and their child processes.
> L716: Use both for defense-in-depth, since sandbox restrictions still apply even if a prompt injection bypasses Claude’s decision-making. Paths and domains from both sandbox settings and permission rules are 【136†merged into the final sandbox configuration】.
> L717: When you enable sandboxing and leave `autoAllowBashIfSandboxed` at its default of `true`, sandboxed Bash commands run without prompting even if your permissions include a bare `Bash` ask rule, or the 【9†equivalent `Bash(*)` form】: the sandbox boundary substitutes for that whole-tool prompt. In 【111†plan mode】, Claude Code skips this substitution.
> L718: Without an ask rule, the 【20†built-in read-only commands】 still run without prompting, and any other shell command goes through the regular permission flow while you are still planning; see 【111†plan mode】 for how Claude Code gates commands there. With a bare `Bash` ask rule, every Bash command prompts, including sandboxed read-only commands, the same as outside sandboxing. These checks still apply:
> L719:   * Content-scoped ask rules like `Bash(git push *)` still force a prompt
> L720:   * Other sandboxed commands can go through the regular permission flow too, as 【137†Auto-allow mode】 describes
> L721: Commands that won’t run sandboxed, such as excluded commands, respect the bare `Bash` ask rule as usual. See 【138†sandbox modes】 to change this behavior.
> L722: ##
> L723: 
> L724: 【44†​】
> L725: 
> L726: Managed settings
> L727: For organizations that need centralized control, administrators deploy managed settings that user and project settings can’t override, apart from a few 【139†security-sensitive keys】. 【140†Deploy managed settings】 covers the delivery mechanisms, precedence within the managed tier, and the 【141†keys that only managed settings can set】. One of those keys, 【142†`allowManagedPermissionRulesOnly`】, makes managed settings the only settings source of permission rules.
>
> --------------------------------------------------------------------------------
> About code owners - GitHub Docs (https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
> 【turn615946view3】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners","pattern":"protect"}); Total lines: 175
> L162: To protect a repository fully against unauthorized changes, you also need to define an owner for the CODEOWNERS file itself. The most secure method is to define a CODEOWNERS file in the `.github` directory of the repository and define the repository owner as the owner of either the CODEOWNERS file (`/.github/CODEOWNERS @owner_username`) or the whole directory (`/.github/ @owner_username`).
> L163: As an alternative to branch protection rules, you can create rulesets. Rulesets have a few advantages over branch protection rules, such as statuses, and better discoverability without requiring admin access. You can also apply multiple rulesets at the same time. For more information, see 【21†About rulesets】.
> ```
>
> <details><summary>Explored 6 files, a search</summary>
>
> - Read `./skills/manage-meta-project/SKILL.md`
> - Read `./docs/decisions_and_roadmap.md`
> - Read `./.agents/project_knowledge/boundaries.md`
> - Read `./templates/team/profile.md`
> - Read `./.agents/team/agent-dev-lead/profile.md`
> - Searched for ````Template:|^```|^~~~```` in `SKILL.md`
> - Read `./CHANGELOG.md`
>
> </details>
>
> </details>
>
> Ключевые замечания подтвердились: CI проверяет покрытие границ, но не запрещает изменения Red Zone; синхронизатор может принять отсутствующий блок за отсутствие дрейфа. В рекомендациях есть и завышенные обещания: скрипт записи не гарантирует, что агент его вызовет, а данные Git не позволяют достоверно восстановить активность ролей. Проверяю ещё случай с вложенными блоками кода и ограничения хуков Claude Code.
>
> <details><summary>Ran 2 commands, called a tool</summary>
>
> - Ran ````python - <<'PY'
> import contextlib
> import io
> from pathlib import Path
> import shutil
> import subprocess
> import sys
> import tempfile
>
> repo = Path('/workspace/work/meta-project')
> sys.path.insert(0, str(repo / 'scripts'))
> import sync_templates
>
> with tempfile.TemporaryDirectory(prefix='meta-auditor-review-') as tmp:
>     root = Path(tmp) / 'repo'
>     shutil.copytree(repo, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
>     for relative in ['skills/init-meta-project/SKILL.md', '.agents/skills/init-meta-project/SKILL.md']:
>         path = root / relative
>         text = path.read_text()
>         text = text.replace('### Template: `observations.md`', '### Renamed block: `observations.md`')
>         path.write_text(text)
>     result = subprocess.run([sys.executable, str(root / 'scripts/sync_templates.py'), '--check'], cwd=root, capture_output=True, text=True)
>     print('Missing expected observations block: --check exit =', result.returncode)
>     print(result.stdout.strip())
>     test_result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'], cwd=root, capture_output=True, text=True)
>     print('Full existing tests after renaming both headings: exit =', test_result.returncode)
>     print(test_result.stderr.splitlines()[-5:])
>
> skill_text = '### Template: `sample.md`\n```markdown\n# Before\n```python\nprint("old")\n```\n# After\n```\n'
> canonical = '# Before\n```python\nprint("new")\n```\n# After\n'
> updated, modified = sync_templates.replace_embedded_template(skill_text, 'sample.md', canonical)
> print('Nested fences: modified =', modified, '; old source remains after replacement =', 'print("old")' in updated)
> print(updated)
> PY````
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "open": [
>     {
>       "ref_id": "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews"
>     },
>     {
>       "ref_id": "https://github.com/gitleaks/gitleaks#usage"
>     }
>   ],
>   "response_length": "short"
> }
> ```
>
> ```text
> Approving a pull request with required reviews - GitHub Docs (https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews ; rewritten summary of https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)
> 【turn441886view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews","lineno":null}); Redirected to URL: https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews; Total lines: 64
> L0:   1.   2. 【0†GitHub Docs】
> L1: 
> L2: Search or ask Copilot/
> L3: 
> L4: Menu
> L5: 
> L6: Collapse sidebar
> L7: 
> L8: Expand sidebar
> L9: 
> L10:   1. 【0†Home】
> L11:   2. 【1†Pull requests】
> L12:   3. 【2†How-tos】
> L13:   4. 【3†Review pull requests】
> L14:   5. Approve PRs
> L15: # Approving a pull request with required reviews
> L16: 
> L17: Approve pull requests with required reviews, including setting approval rules, reviewing changes, and submitting feedback before merging.
> L18: 
> L19: Copy markdown
> L20: 
> L21: You can comment on a pull request, approve the changes, or request improvements before approving. See 【4†Reviewing proposed changes in a pull request】.
> L22: You can find a pull request where you or a team you're a member of is requested for review with the search qualifier `review-requested:[USERNAME]` or `team-review-requested:[TEAMNAME]`. For more information, see 【5†Searching issues and pull requests】.
> L23: 
> L24: Tip
> L25: 
> L26: If a pull request you approved has changed significantly, you can dismiss your review. The pull request will need a new review before it can be merged. See 【6†Dismissing a pull request review】.
> L27: 
> L28:   1. Under your repository name, click Pull requests.
> L29:   2. In the list of pull requests, click the pull request you'd like to review.
> L30: 
> L31:   3. On the pull request, click Files changed.
> L32: 
> L33: 【7†Image: Screenshot of the tabs for a pull request. The "Files changed" tab is outlined in dark orange.】
> L34: 
> L35:   4. Review the changes in the pull request. Optionally, comment on specific lines or files. See 【8†Reviewing proposed changes in a pull request】.
> L36: 
> L37:   5. Above the changed code, click Review changes.
> L38: 【9†Image: Screenshot of the "Files changed" tab of a pull request. The "Review changes" button is outlined in dark orange.】
> L39: 
> L40:   6. Type a comment summarizing your feedback on the proposed changes.
> L41: 
> L42:   7. Select Approve to approve merging the proposed changes.
> L43: 
> L44:   8. Click Submit review.
> L45: 
> L46: Tip
> L47:   * The Request changes option is purely informational and will not prevent merging unless a ruleset or classic branch protection rule is configured with the "require a pull request" option. If configured and a collaborator with `admin`, `owner`, or `write` access to the repository submits a review requesting changes, the pull request cannot be merged until the same collaborator submits another review approving the changes in the pull request.
> L48:   * Repository owners and administrators can merge a pull request even if it hasn't received an approving review, or if a reviewer who requested changes has left the organization or is unavailable.
> L49:   * If both required reviews and stale review dismissal are enabled and a code-modifying commit is pushed to the branch of an approved pull request, the approval is dismissed. The pull request must be reviewed and approved again before it can be merged.
> L50:   * When several open pull requests each have a head branch pointing to the same commit, you won’t be able to merge them if one or both have a pending or rejected review.
> L51:   * If your repository requires approving reviews from people with write or admin permissions, the reviewers sidebar groups approvals by permission level. Approvals can appear in two sections:
> L52:     * The top section mostly contains approvals from people with write or admin permissions that count toward merge requirements. Approvals by GitHub Copilot also appear in this section even though GitHub Copilot reviews do not count toward those requirements.
> L53:     * The collapsible section (if present) shows approvals from reviewers whose reviews do not affect whether the pull request can be merged.
> L54:   * Pull request authors cannot approve their own pull requests. You will also not be able to approve a pull request that was raised by GitHub Copilot if it was you who assigned Copilot to the issue to which the pull request relates.
> L55: ## 【10†Further reading】
> L56: 
> L57:   * 【11†About protected branches】
> L58:   * 【4†Reviewing proposed changes in a pull request】
> L59:   * 【12†Commenting on a pull request】
> L60: 
> L61: Back to top
> L62: 
> L63: GitHub Inc. © 2026【13†Terms】【14†Privacy】【15†Status†www.githubstatus.com】【16†Pricing†github.com】
>
> --------------------------------------------------------------------------------
> GitHub - gitleaks/gitleaks: Find secrets with Gitleaks 🔑 · GitHub (https://github.com/gitleaks/gitleaks)
> 【turn441886view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://github.com/gitleaks/gitleaks#usage","lineno":null}); Total lines: 791
> L0: 【0†Skip to content】
> L1: ## Navigation Menu
> L2: 
> L3:   * Products
> L4: 
> L5:     *       * 【1†GitHub Repository hosting, code review, and collaboration】
> L6:       * 【2†Copilot AI coding agent for tasks, projects, and automated work】
> L7: 
> L8:     * Build & Ship
> L9:       * 【3†Actions CI/CD and automation】
> L10:       * 【4†Code Quality Quality analysis, fixes, and enforcement】
> L11:       * 【5†Codespaces Cloud development environments】
> L12:     * Secure
> L13:       * 【6†Code Security Vulnerability detection and remediation】
> L14:       * 【7†Secret Protection Secret scanning and leak prevention】
> L15: 
> L16: 【8†All Features】
> L17: 
> L18:   * Developers
> L19: 
> L20:     * Learn
> L21:       * 【9†Documentation†docs.github.com】
> L22:       * 【10†Training†learn.github.com】
> L23:       * 【11†Certifications†learn.github.com】
> L24: 
> L25:     * Build
> L26:       * 【12†Build with Copilot】
> L27:       * 【13†Customize Copilot†docs.github.com】
> L28:       * 【14†Integrations】
> L29:     * Explore
> L30:       * 【15†Trending repos】
> L31:       * 【16†GitHub Sponsors】
> L32:       * 【17†Developer articles】
> L33: 
> L34:     *       * 【18†Changelog Your source for the latest features, improvements, and fixes across GitHub products, all in one place.†github.blog】
> L35: 
> L36:   * Businesses
> L37: 
> L38:     * By Stage
> L39:       * 【19†Enterprises】
> L40:       * 【20†Team】
> L41:       * 【21†Startups】
> L42:       * 【22†Nonprofits】
> L43:     * By Industry
> L44:       * 【23†Healthcare】
> L45:       * 【24†Financial services】
> L46:       * 【25†Manufacturing】
> L47:       * 【26†Government】
> L48:       * 【27†See all industries】
> L49: 
> L50:     * Evaluate GitHub
> L51:       * 【28†Why GitHub】
> L52:       * 【29†Customer Stories】
> L53:       * 【30†Business insights】
> L54:       * 【31†Trust Center】
> L55: 
> L56:     * Add-ons
> L57:       * 【32†GitHub Advanced Security Enterprise-grade code security】
> L58:       * 【33†Copilot for business Enterprise-grade AI features】
> L59:       * 【34†Premium Support Enterprise-grade 24/7 support】
> L60:   * Resources
> L61: 
> L62:     * Learn & Connect
> L63:       * 【9†Documentation†docs.github.com】
> L64:       * 【35†Resource center】
> L65:       * 【36†Blog†github.blog】
> L66:       * 【37†Events & webinars】
> L67:       * 【38†Community Forum】
> L68:       * 【29†Customer Stories】
> L69:       * 【14†Integrations】
> L70: 
> L71:     * Support
> L72:       * 【39†Customer support†help.github.com】
> L73:       * 【10†Training†learn.github.com】
> L74:       * 【40†GitHub Status†www.githubstatus.com】
> L75: 
> L76:     * Company
> L77:       * 【41†About】
> L78:       * 【42†Partners】
> L79:       * 【18†Changelog†github.blog】
> L80:     *       * 【43†GitHub Universe The event for developers, by developers — talks, workshops, and what’s next for GitHub.†githubuniverse.com】
> L81: 
> L82:   * 【44†Pricing】
> L83: 
> L84: Search`/`
> L85: 
> L86: 【45†Sign in】
> L87: 
> L88: 【46†Sign up】
> L89: 
> L90: Appearance settings
> L91: 
> L92: You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert
> L93: 
> L94:   1. 【47†gitleaks】
> L95:   2. 【48†gitleaks】
> L96: ## Repository navigation
> L97: 
> L98:   *   * 【48†Code】
> L99:   * 【49†Issues 285 (285)】
> L100:   * 【50†Pull requests 254 (254)】
> L101:   * 【51†Discussions】
> L102:   * 【52†Actions】
> L103:   * 【53†Projects】
> L104:   * 【54†Security and quality】
> L105:   * 【55†Insights】
> L106: 
> L107: More items
> L108: 
> L109: 【56†Image: gitleaks†avatars.githubusercontent.com】
> L110: 
> L111: 【48†gitleaks】
> L112: 
> L113: Public
> L114: 
> L115:   * Sponsor
> L116:   * 【57†Notifications】You must be signed in to change notification settings
> L117:   * 【57†Fork 2.4k (2.4k)】
> L118:   * 【57†Star 30.9k (30.9k)】You must be signed in to star a repository
> L119: ## About
> L120: 
> L121: Find secrets with Gitleaks 🔑
> L122: 
> L123: 【58†gitleaks.io†gitleaks.io】
> L124: 
> L125: ### Topics
> L126: 
> L127: 【59†ai-powered】【60†ci-cd】【61†cicd】【62†cli】【63†data-loss-prevention】【64†devsecops】【65†dlp】【66†git】【67†gitleaks】【68†go】【69†golang】【70†hacktoberfest】【71†llm】【72†llm-inference】【73†llm-training】【74†nhi】【75†open-source】【76†secret】【77†security】【78†security-tools】
> L128: 
> L129: ### Resources
> L130: 
> L131: 【79†Readme】
> L132: 
> L133: 【80†MIT license】
> L134: 
> L135: ### Contributing
> L136: 
> L137: 【81†Contributing】
> L138: 
> L139: ### Security policy
> L140: 
> L141: 【82†Security policy】
> L142: 
> L143: 【83†Activity】
> L144: 
> L145: 【84†Custom properties】
> L146: ### Stars
> L147: 
> L148: 30.9k stars
> L149: 
> L150: ### Watchers
> L151: 
> L152: 181 watching
> L153: 
> L154: ### Forks
> L155: 
> L156: 【85†2.4k forks】
> L157: 
> L158: 【86†Report repository】
> L159: 
> L160: master
> L161: 
> L162: 【87†Branches】【88†Tags】
> L163: 
> L164: [Input: Go to file]
> L165: 
> L166: Go to file
> L167: 
> L168: Code
> L169: 
> L170: Open more actions menu
> L171: 
> L172: ## Latest commit
> L173: 
> L174: 
> L175: 
> L176: ## History
> L177: 
> L178: 1,293 Commits
> L179: ## Folders and files
> L180: Name  | Name  | Last commit message  | Last commit date
> L181: --- | --- | --- | ---
> L182: 【89†.github】  | 【89†.github】  |    |
> L183: 【90†cmd】  | 【90†cmd】  |    |
> L184: 【91†config】  | 【91†config】  |    |
> L185: 【92†detect】  | 【92†detect】  |    |
> L186: 【93†logging】  | 【93†logging】  |    |
> L187: 【94†regexp】  | 【94†regexp】  |    |
> L188: 【95†report】  | 【95†report】  |    |
> L189: 【96†report_templates】  | 【96†report_templates】  |    |
> L190: 【97†scripts】  | 【97†scripts】  |    |
> L191: 【98†sources】  | 【98†sources】  |    |
> L192: 【99†testdata】  | 【99†testdata】  |    |
> L193: 【100†version】  | 【100†version】  |    |
> L194: 【101†.gitignore】  | 【101†.gitignore】  |    |
> L195: 【102†.gitleaks.toml】  | 【102†.gitleaks.toml】  |    |
> L196: 【103†.gitleaksignore】  | 【103†.gitleaksignore】  |    |
> L197: 【104†.golangci.yaml】  | 【104†.golangci.yaml】  |    |
> L198: 【105†.goreleaser.yml】  | 【105†.goreleaser.yml】  |    |
> L199: 【106†.pre-commit-hooks.yaml】  | 【106†.pre-commit-hooks.yaml】  |    |
> L200: 【107†CONTRIBUTING.md】  | 【107†CONTRIBUTING.md】  |    |
> L201: 【108†Dockerfile】  | 【108†Dockerfile】  |    |
> L202: 【109†LICENSE】  | 【109†LICENSE】  |    |
> L203: 【110†Makefile】  | 【110†Makefile】  |    |
> L204: 【111†README.md】  | 【111†README.md】  |    |
> L205: 【112†SECURITY.md】  | 【112†SECURITY.md】  |    |
> L206: 【113†USERS.md】  | 【113†USERS.md】  |    |
> L207: 【114†go.mod】  | 【114†go.mod】  |    |
> L208: 【115†go.sum】  | 【115†go.sum】  |    |
> L209: 【116†main.go】  | 【116†main.go】  |    |
> L210: [Button: View all files]
> L211: ## Repository files navigation
> L212: 
> L213:   *   * 【117†README】
> L214:   * 【117†Contributing】
> L215:   * 【117†MIT license】
> L216:   * 【117†Security】
> L217: 
> L218: More items
> L219: # Gitleaks
> L220: 
> L221:     `┌─○───┐
> L222:     │ │╲  │
> L223:     │ │ ○ │
> L224:     │ ○ ░ │
> L225:     └─░───┘
> L226:     `
> L227: 
> L228: Warning
> L229: 
> L230: Gitleaks is feature complete. I'm not merging new features into Gitleaks. Future releases will be security patches only. I'm shifting my focus to 【118†Betterleaks】
> ```
>
> - Ran `nl -ba scripts/sync_templates.py | sed -n '39,99p' && nl -ba skills/tune-meta-project/SKILL.md | sed -n '48,62p' && nl -ba .agents/project_knowledge/boundaries.md | sed -n '17,44p' && rg -n 'src/|HEAD|check_architecture_drift|has_arch_update|allow_red_zone' scripts/check_boundaries.py && git status --short`
>
> </details>
</details>

**Взял бы из отчёта исправления гейтов, надёжную запись памяти и упрощение правил. Автотелеметрию как P0, обязательный «семантический контроль» и собственный сканер секретов сейчас не добавлял бы.**

Сверил с текущим `main` — это по-прежнему `398a171`. В отчёте есть подтверждённые дефекты, полезные направления и несколько слишком сильных обещаний.

Для ближайшего спринта актуальны следующие вещи.

1. **Исправить синхронизатор. Замечание аудитора подтверждается полностью.** Во временной копии переименовал заголовок блока `observations.md` в обеих копиях скилла: `--check` сообщил `0 drift`, все **51 тест прошли**. На примере с вложенными fences замена оставляет старый фрагмент после нового. Сейчас достаточно явных маркеров BEGIN/END, проверки их уникальности и ошибки при отсутствии обязательного блока. Полная генерация `SKILL.md` — возможное дальнейшее развитие. [Код](https://github.com/vlv-code/meta-project/blob/398a1719ca10f7153c73d3dcb83e80d102d6973d/scripts/sync_templates.py#L44-L95).

2. **Доделать контроль границ в CI и защитить его правила.** Фраза аудитора «CI как backstop против `--no-verify` — есть» пока неточна: CI запускает только аудит покрытия путей. Нужна проверка diff относительно базы PR. Сам проверяющий код и политика должны браться из доверенной базовой версии, иначе PR может одновременно ослабить правила и пройти проверку. В Red стоит вынести конкретные файлы гейта и политики; переводить вообще все `scripts/**` необязательно. [Workflow](https://github.com/vlv-code/meta-project/blob/398a1719ca10f7153c73d3dcb83e80d102d6973d/.github/workflows/ci.yml#L42-L46).

3. **Сначала устранить уже найденные проблемы сохранности данных:** потерю наблюдений при повторной архивации и перезапись существующего `pre-commit`. Они непосредственно ломают обещание безопасного внедрения фреймворка.

Остальные рекомендации я бы оценил так:

| Предложение | Что применимо для этого репо |
|---|---|
| `record_obs.py` | **Да.** Небольшой stdlib-скрипт для валидации, экранирования таблицы, дедупликации и безопасной записи полезен. При параллельных вызовах нужны защита от гонок и повторного добавления. |
| Post-commit → телеметрия ролей | **Не P0 и не в предложенном виде.** Коммит не равен вызову роли. Git не знает об аудитах без изменений, нескольких участниках задачи и фактическом исполнителе. Автор коммита тоже не обязательно исполнитель. Из Git можно строить отчёт о коммитах. |
| `verify_dod.py` | **Частично.** Проверять форматы, ссылки и обязательные поля можно. Связь «закрытая задача → телеметрия с ID» требует сначала ввести устойчивые ID и определить, зачем эта связь нужна. |
| Новый модуль → обязательное изменение `architecture.md` | **Предупреждение по умолчанию, настраиваемый fail.** Касание файла не доказывает актуальность архитектуры. Для самого meta-project важны также `skills/`, `templates/`, `scripts/`, а не только отсутствующий здесь `src/`. |
| JSON findings → `weak_spots.md` | **Полезно при регулярных аудитах.** JSON подходит stdlib-ядру. Но попадание находки в постоянную базу должно учитывать подтверждение, дубликаты и статус; автоматическая запись не делает вывод аудитора истинным. |
| AST-детектор ослабления тестов | **Позже, сначала как предупреждения.** Для этого репо нужно понимать `unittest` и `self.assert*`, а не только `ast.Assert` и pytest. Снижение числа проверок бывает нормальным рефакторингом, изменение expected — частью правильного исправления. |
| Danger-pattern lint | **Опциональная проверка.** Наличие `eval`, `pickle.loads` или `shell=True` само по себе не определяет дефект. Строить универсальный анализатор безопасности внутри этого фреймворка сейчас избыточно. |
| Мини-сканер секретов в ядре | **Не стал бы писать.** Форматы токенов и энтропия потребуют постоянной поддержки и исключений. Опциональный готовый сканер в CI выглядит практичнее. |
| Все snapshots/golden-файлы в Red | **Не универсальный default.** Критические контракты можно защищать жёстко; обычные UI-снапшоты часто обновляют штатно. В этом репо их сейчас вообще нет. |
| Нулевой уровень без команды | **Да, как явный вариант в README.** Команда уже опциональна, а скилл предлагает для малого проекта **2–3 роли**, не обязательную триаду. Выбирать режим лучше по сложности и потребности в специализации, не только по LOC. |
| Английские ADR и lessons learned | **Да, полезно для внешних контрибьюторов.** Начать с актуальных решений и причин ограничений; перевод всей исторической переписки необязателен. |
| Донатный адрес | **Продуктовое предпочтение, низкий приоритет.** Тезис про впечатление скама субъективен; технический бэклог из него не следует. |

Три принципиальных уточнения к отчёту:

**«Каждое правило автоматизируй или удали» — слишком жёстко.** Форматы, права и операции записи хорошо автоматизируются. Архитектурные ориентиры вроде совместимости API сохраняют смысл и при необходимости экспертной оценки. А требование «тронуть нужный Markdown» легко превращается в новый формальный ритуал.

**«Забыть становится физически нельзя» — неверно.** `record_obs.py` гарантирует корректность записи **после вызова**. Решение вызвать его остаётся за агентом. Аналогично аудит-лог `--allow-red-zone` фиксирует использование обхода, но не подтверждает человеческое разрешение.

**Адаптер Claude Code применим, но требует чётких границ.** `PreToolUse` действительно может отклонять вызовы. Однако файловые deny-правила не контролируют произвольный Python/Node-процесс, который самостоятельно пишет файлы; для такого ограничения нужен sandbox. Сам hook и его настройки тоже должны быть защищены от изменения агентом. Это следует из [документации Claude Code](https://code.claude.com/docs/en/permissions#read-and-edit).

С `CODEOWNERS` похожая оговорка: обязательное одобрение включается отдельными настройками GitHub. Для единственного сопровождающего оно требует продуманного процесса — автор PR не может одобрить собственный PR. [GitHub Docs](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews).

Аргумент про zero-dependency у аудитора по существу разумный: **stdlib-ядро совместимо с опциональным Gitleaks в CI**. Но это стоит явно закрепить в политике проекта. А телеметрию я бы сначала проверил на полезность: какие решения по ней принимаются и оправдывают ли они её ведение.

> Зафиксировал, теперь по поводу реализации части функционала в хуки:
> вот что предложил мне агент:
> "(закреп)"
>
> Норм тема или херню сморозил?

<details><summary>4 previous messages</summary>

> Прочитаю закреплённое предложение и сверю с устройством репо: что разумно вынести в хуки, где есть ограничения и насколько сложной получится поддержка.
>
> <details><summary>Explored a file, ran 2 commands, called 3 tools</summary>
>
> <details><summary>Explored a file</summary>
>
> - Read `./attachments/d955e8e8-4385-459d-a32b-4a37bd505032/Вставленный текст.txt`
>
> </details>
>
> MCP tool call
>
> codex_apps.cloud_environment.environment_status
>
> ```json
> {}
> ```
>
> ```text
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> ```json
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "response_length": "long",
>   "system2_search_query": [
>     {
>       "q": "site.cursor.com/docs hooks \".claude/settings.json\""
>     },
>     {
>       "q": "site.docs.github.com copilot hooks \".claude/settings.json\""
>     },
>     {
>       "q": "site.geminicli.com/docs hooks BeforeTool exit code"
>     },
>     {
>       "q": "site.developers.openai.com/codex hooks SessionStart PreToolUse"
>     }
>   ]
> }
> ```
>
> ```text
> Third Party Hooks | Cursor Docs (https://prod.cursor.com/docs/reference/third-party-hooks)
> 【turn725581search0】 [wordlim: 200] Crawled: yesterday; Cursor can load and execute hooks configured for Claude Code, allowing you to use the same hook scripts across both tools. ... Project  | `.claude/settings.json`  | Project-level hooks, checked into repo
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks)
> 【turn725581search1】 [wordlim: 200] Crawled: yesterday;                 "command": "python3 ~/.codex/hooks/session_start.py", ... `SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, and `Interrupt` also include `permission_mode`, which describes the current permission mode as `default`, `acceptEdits`, `plan`, `dontAsk`, or `bypassPermissions`. ... If a `PreToolUse` hook returns one of those unsupported fields, Codex marks that hook run as failed, reports the error, and continues the tool call.
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks?trk=article-ssr-frontend-pulse_little-text-block)
> 【turn725581search2】 [wordlim: 200] Crawled: 2 days ago;                 "command": "python3 ~/.codex/hooks/session_start.py", ... `SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, and `Interrupt` also include `permission_mode`, which describes the current permission mode as `default`, `acceptEdits`, `plan`, `dontAsk`, or `bypassPermissions`. ... If a `PreToolUse` hook returns one of those unsupported fields, Codex marks that hook run as failed, reports the error, and continues the tool call.
>
> --------------------------------------------------------------------------------
> vscode-copilot-chat/assets/prompts/skills/agent-customization/references/hooks.md at main · microsoft/vscode-copilot-chat · GitHub (https://github.com/microsoft/vscode-copilot-chat/blob/main/assets/prompts/skills/agent-customization/references/hooks.md)
> 【turn725581search3】 [wordlim: 200] Crawled: 3 weeks ago; `.github/hooks/*.json`  | Workspace (team-shared)
> `.claude/settings.local.json`  | Workspace local (not committed) ... ## Hook Events
>
> --------------------------------------------------------------------------------
> Hooks reference | Gemini CLI (https://geminicli.com/docs/hooks/reference/)
> 【turn725581search4】 [wordlim: 200] Published: 7 months ago; Crawled: 3 weeks ago; This document provides the technical specification for Gemini CLI hooks, including JSON schemas and API details. ... Each event (for example, `BeforeTool`) contains an array of hook definitions. ...   * Exit Code 2 (Block Tool): Prevents execution.
>
> --------------------------------------------------------------------------------
> Claude Code power user customization: How to configure hooks | Claude by Anthropic (https://claude.com/resources/articles/how-to-configure-hooks?aff=N6qyE)
> 【turn725581search5】 [wordlim: 200] Published: 11 months ago; Crawled: today; Local project hooks go in .claude/settings.local.json for personal configuration you don't want to commit. ... Matchers are how you filter which tools can trigger your hook.
>
> --------------------------------------------------------------------------------
> vscode-docs/docs/agent-customization/hooks.md at main · microsoft/vscode-docs · GitHub (https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/hooks.md)
> 【turn725581search6】 [wordlim: 200] Crawled: today; The Copilot harness reads inline hook settings in `.github/copilot/settings.json`, `.github/copilot/settings.local.json`, and `~/.copilot/settings.json`. It also reads repository `.claude/settings.json` and `.claude/settings.local.json`.
>
> --------------------------------------------------------------------------------
> Claude Code power user customization: How to configure hooks | Claude by Anthropic (https://claude.com/resources/articles/how-to-configure-hooks)
> 【turn725581search7】 [wordlim: 200] Published: 11 months ago; Crawled: 2 days ago; Local project hooks go in .claude/settings.local.json for personal configuration you don't want to commit. ... Matchers are how you filter which tools can trigger your hook.
>
> --------------------------------------------------------------------------------
> Configure agent hooks in Visual Studio Code (https://code.visualstudio.com/docs/agent-customization/hooks)
> 【turn725581search8】 [wordlim: 200] Published: yesterday; Crawled: today; The Copilot harness reads inline hook settings in `.github/copilot/settings.json`, `.github/copilot/settings.local.json`, and `~/.copilot/settings.json`. It also reads repository `.claude/settings.json` and `.claude/settings.local.json`.
>
> --------------------------------------------------------------------------------
> Settings files and precedence - Claude Code Docs (https://code.claude.com/docs/en/settings?_rsc=vr6dg)
> 【turn725581search9】 [wordlim: 200] Crawled: today; The `$schema` line points to the published JSON schema for Claude Code settings, which gives you autocomplete and inline validation in VS Code, Cursor, and any other editor that supports JSON schema. ... The reload covers user, project, local, and managed settings, and Claude Code runs the `ConfigChange` hook for each settings-file change it detects, not for managed settings that arrive from MDM or the claude.ai console.
>
> --------------------------------------------------------------------------------
> codex/codex-rs/core/src/hook_runtime.rs at main · openai/codex · GitHub (https://github.com/openai/codex/blob/main/codex-rs/core/src/hook_runtime.rs)
> 【turn725581search10】 [wordlim: 200] Crawled: 4 weeks ago; let preview_runs = hooks.preview_session_start(&request); ... "Command blocked by PreToolUse hook: {reason}.
>
> --------------------------------------------------------------------------------
> openai-mirror/developers.openai.com/codex/hooks.md at main · ai-native-engineer/openai-mirror · GitHub (https://github.com/ai-native-engineer/openai-mirror/blob/main/developers.openai.com/codex/hooks.md)
> 【turn725581search11】 [wordlim: 200] Crawled: last month; "hooks": { "SessionStart": [ "matcher": "startup|resume", "hooks": [ "type": "command", "command": "python3 ~/.codex/hooks/session_start.py", "statusMessage": "Loading session notes" ] ], "PreToolUse": [ "matcher": "Bash", "hooks": [ "type": "command", "command": "/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/pre_tool_use_policy.py"", "statusMessage": "Checking Bash command" ] ], "PermissionRequest": [ "matcher": "Bash", "hooks": [ "type": "command", "command": "/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/permission_request.py"", "statusMessage": "Checking approval request" ] ], "PostToolUse": [ "matcher": "Bash", "hooks": [ "type": "command", "command": "/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/post_tool_use_review.py"", "statusMessage": "Reviewing Bash output" ] ], "UserPromptSubmit": [ "hooks": [ "type": "command", "command": "/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/user_prompt_submit_data_flywheel.py"" ] ], "Stop": [ "hooks": [ "type": "command", "command": "/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/stop_continue.py"", "timeout": 30 ] ]
>
> --------------------------------------------------------------------------------
> codex/codex-rs/hooks/src/engine/dispatcher.rs at main · openai/codex · GitHub (https://github.com/openai/codex/blob/main/codex-rs/hooks/src/engine/dispatcher.rs)
> 【turn725581search12】 [wordlim: 200] Crawled: last week; HookEventName::SessionStart | HookEventName::SessionEnd | HookEventName::SubagentStart => { ... HookEventName::PreToolUse ... pub(crate) fn hook_event_name_label(event_name: HookEventName) -> &'static str {
>
> --------------------------------------------------------------------------------
> Migrate customizations to the Copilot harness in VS Code (https://afd-vscode-site-fd-prod-dvgdfjcmaka5a3fq.z01.azurefd.net/docs/agent-customization/migrate-customizations)
> 【turn725581search13】 [wordlim: 200] Published: yesterday; Crawled: today; Repository settings  | The Copilot harness reads an inline `hooks` map from `.github/copilot/settings.json` and `.github/copilot/settings.local.json`. ... Do not assume a Local hook in `~/.claude/settings.json` is discovered by Copilot.
>
> --------------------------------------------------------------------------------
> Automating with Hooks | GitHub Copilot Learning Hub (https://awesome-copilot.github.com/learning-hub/automating-with-hooks/)
> 【turn725581search14】 [wordlim: 200] Crawled: yesterday;   * Claude/Copilot project settings: `.claude/settings.json` and `.claude/settings.local.json` — hooks defined here are applied to the current repository without committing them to `.github/` ... For `userPromptSubmitted` events the prompt content is available via JSON input to the hook script.
>
> --------------------------------------------------------------------------------
> Submission blocked by hook - ERROR_HOOKS_BLOCKED (Session initialization failed: 400) - Bug Reports - Cursor - Community Forum (https://forum.cursor.com/t/submission-blocked-by-hook-error-hooks-blocked-session-initialization-failed-400/150594)
> 【turn725581search15】 [wordlim: 200] Published: 9 months ago; Crawled: 7 months ago; Hey, this is a known issue - Cursor is trying to execute hooks from the Claude Code configs (`~/.claude/`), and if there are plugins with a sessionStart hook, it results in this error. ... 원인은 `~/.claude/settings.json`에 `enabledPlugins`이 전역으로 선언되어있으면 위와 같이 Hook Error가 발생합니다.
>
> --------------------------------------------------------------------------------
> Claude Code project hooks (.claude/settings.json) are no longer run (3.24.9) - Bug Reports - Cursor - Community Forum (https://forum.cursor.com/t/claude-code-project-hooks-claude-settings-json-are-no-longer-run-3-24-9/174144)
> 【turn725581search16】 [wordlim: 200] Published: last month; Crawled: last month; Cursor currently only picks up a Claude settings file as a hooks config when the hook entries include a `matcher` key, and `UserPromptSubmit` / `SessionStart` entries usually don’t have one. ... About that line: it appears while .cursor/hooks.json doesn’t exist, so it looks like a missing file is reported as a parse error.
>
> --------------------------------------------------------------------------------
> hooks.md — Spybara (https://spybara.com/openai/codex/history/docs/en/2026-04-22-1829..2026-04-23-1831/hooks/)
> 【turn725581search17】 [wordlim: 200] Crawled: today; ### SessionStart ... JSON on `stdout` supports Common output fields and this hook-specific shape: ... ### PreToolUse ... Currently `PreToolUse` only supports Bash tool interception.
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks?site_variant=chatgpt&translationFallback=zh-Hans)
> 【turn725581search18】 [wordlim: 200] Crawled: last week; `SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, and `Interrupt` also include `permission_mode`, which describes the current permission mode as `default`, `acceptEdits`, `plan`, `dontAsk`, or `bypassPermissions`. ... If a `PreToolUse` hook returns one of those unsupported fields, Codex marks that hook run as failed, reports the error, and continues the tool call. ...       "command": "python3 ~/.codex/hooks/session_start.py",
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://developers.openai.com/de-DE/docs/hooks)
> 【turn725581search19】 [wordlim: 200] Crawled: last month; Daher kann kein Hook den Start eines anderen passenden Hooks verhindern. ...                 "command": "python3 ~/.codex/hooks/session_end.py", ...                 "command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/pre_tool_use_policy.py\"",
>
> --------------------------------------------------------------------------------
> Hooks Best Practices | Gemini CLI (https://geminicli.com/docs/hooks/best-practices/)
> 【turn725581search20】 [wordlim: 200] Published: 7 months ago; Crawled: 3 weeks ago;       "hook_event_name": "BeforeTool", ...     # Check exit code ...       "hook_event_name": "BeforeTool",
>
> --------------------------------------------------------------------------------
> hooks.md — Spybara (https://spybara.com/openai/codex/history/docs/en/2026-03-27-1823..2026-03-28-0626/hooks/)
> 【turn725581search21】 [wordlim: 200] Crawled: today; `PreToolUse`  | tool name  | Current Codex runtime only emits `Bash`.
> `SessionStart`  | start source  | Current runtime values are `startup` and `resume`. ... That last example is still a valid regex, but current Codex `PreToolUse` and `PostToolUse` events only emit `Bash`, so it will not match anything today. ... Every command hook receives one JSON object on `stdin`.
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks?translationFallback=zh-Hant)
> 【turn725581search22】 [wordlim: 200] Crawled: last month; After Codex compacts a root session, `SessionStart` hooks that match `source: "compact"` run before the next model request. This also applies when automatic compaction happens in the middle of a turn: Codex delivers the hook’s additional context to the immediate continuation instead of waiting for a later user turn.
>
> --------------------------------------------------------------------------------
> GitHub Copilot hooks reference - GitHub Docs (https://docs.github.com/en/copilot/reference/hooks-reference?utm_campaign=listing&utm_medium=referral&utm_source=claudeers.com)
> 【turn725581search23】 [wordlim: 200] Crawled: 2 days ago;     * Inline `hooks` block in repository settings — the `hooks` field at the top level of `.github/copilot/settings.json` (Git committed) or `.github/copilot/settings.local.json` (typically gitignored and user specific) in the repository. Cross-tool `.claude/settings.json` and `.claude/settings.local.json` files in the repository are also read. ... If a hook configuration file loaded from a directory (for example, `.github/hooks/`) contains a malformed hook item, only that item is dropped and logged—valid sibling hooks in the same file still load.
>
> --------------------------------------------------------------------------------
> GitHub Copilot hooks reference - GitHub Docs (https://docs.github.com/en/copilot/reference/hooks-reference)
> 【turn725581search24】 [wordlim: 200] Crawled: today; If a hook configuration file loaded from a directory (for example, `.github/hooks/`) contains a malformed hook item, only that item is dropped and logged—valid sibling hooks in the same file still load. ... Claude-format matchers (PascalCase `PreToolUse`): Hooks configured with the PascalCase event name `PreToolUse`—as used in Claude Code plugins and the Open Plugins format—apply Claude's matcher semantics instead of the native regex rule: ...   * At the top level of repository `settings.json` — Copilot CLI only.
>
> --------------------------------------------------------------------------------
> Gemini CLI configuration | Gemini CLI (https://geminicli.com/docs/reference/configuration/)
> 【turn725581search25】 [wordlim: 200] Crawled: 3 weeks ago;     * Description: List of hook names (commands) that should be disabled. ...   * `hooks.BeforeTool` (array):
>
> --------------------------------------------------------------------------------
> Claude hooks don't work - Bug Reports - Cursor - Community Forum (https://forum.cursor.com/t/claude-hooks-dont-work/153614)
> 【turn725581search26】 [wordlim: 200] Published: 8 months ago; Crawled: 7 months ago; The identical hook in `.cursor/hooks.json` loads immediately. ... Per docs, `.claude/settings.json` hooks should be loaded and mapped automatically.
>
> --------------------------------------------------------------------------------
> hooks.md — Spybara (https://spybara.com/openai/codex/history/docs/en/2026-05-14-2100..2026-05-18-2201/hooks/)
> 【turn725581search27】 [wordlim: 200] Crawled: today; `SessionStart`, `UserPromptSubmit`, and `Stop` support these shared JSON fields: ... `PostToolUse` supports `systemMessage`, `continue: false`, and `stopReason`. `suppressOutput` is parsed but not currently supported for that event. ... JSON on `stdout` supports Common output fields and this hook-specific shape: ... It's still a guardrail rather than a complete enforcement boundary because Codex can often perform equivalent work through another supported tool path.
>
> --------------------------------------------------------------------------------
> Hooks – Codex | OpenAI Developers (https://doc.jarvisuni.com/openai/codex/hooks)
> 【turn725581search28】 [wordlim: 200] Crawled: today;   * `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, and `Stop` run at turn scope. `SessionStart` and `SubagentStart` run at thread or subagent-start scope. ... If more than one hook source exists, Codex loads all matching hooks.
>
> --------------------------------------------------------------------------------
> Gemini CLI hooks | Gemini CLI (https://geminicli.com/docs/hooks/?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment-text)
> 【turn725581search29】 [wordlim: 200] Published: 7 months ago; Crawled: 3 weeks ago; Hooks run synchronously as part of the agent loop—when a hook event fires, Gemini CLI waits for all matching hooks to complete before continuing. ... Exit Code  | Label  | Behavioral Impact ...   * Tool events (`BeforeTool`, `AfterTool`): Matchers are Regular Expressions. (for example, `"write_.
>
> --------------------------------------------------------------------------------
> Cursor hooks: hooks.json setup, events and examples | Kipt (https://kipt.me/guides/cursor-hooks)
> 【turn725581search30】 [wordlim: 200] Crawled: today; When Include Third-Party Plugins, Skills, and Other Configs is turned on in Cursor Settings (it is on by default), Cursor loads hooks from .claude/settings.local.json, .claude/settings.json and ~/.claude/settings.json and maps Claude hook names to Cursor events.
>
> --------------------------------------------------------------------------------
> Third Party Hooks | Cursor Docs (https://docs.anyweb.dev/docs/reference/third-party-hooks)
> 【turn725581search31】 [wordlim: 200] Crawled: today; When using Claude Code hooks in Cursor, the following features are supported: ... Check that your `.claude/settings.json` file is valid JSON
>
> --------------------------------------------------------------------------------
> Hooks | Arantic Documentation (https://docs.arantic.com/de/cursor/hooks)
> 【turn725581search32】 [wordlim: 200] Crawled: today; Cursor also supports loading hooks written for Claude Code, so an existing `.claude/settings.json` hook set can run unchanged (see Third-party hooks below).
>
> --------------------------------------------------------------------------------
> docs/content/copilot/reference/hooks-reference.md at main · github/docs · GitHub (https://github.com/github/docs/blob/main/content/copilot/reference/hooks-reference.md)
> 【turn725581search33】 [wordlim: 200] Crawled: yesterday; Configuration discovery  | In a cloud agent job, the only hook configuration that exists by default is `.github/hooks/*.json` inside the cloned repository. ... Hooks defined inline in `settings.json` remain strict: any item-level validation error rejects the whole `hooks` field. ... See AUTOTITLE. {% data variables.copilot.copilot_cli_short %} does not inspect script files or expand a hook's access after it starts. ...   * Any other value is treated as a case-sensitive regex anchored as `^(?:PATTERN)$` tested against the Claude tool name (or the runtime name for tools with no Claude equivalent).
>
> --------------------------------------------------------------------------------
> Hooks  |  Gemini API  |  Google AI for Developers (https://ai.google.dev/gemini-api/docs/agent-hooks?hl=en)
> 【turn725581search34】 [wordlim: 200] Crawled: 2 months ago; `pre_tool_execution`  | Right before a tool runs  | Can approve (`allow`) or block (`deny`) the tool before it executes. ... When a hook denies a command, the tool call is skipped immediately. ...           "code": "python3 /workspace/app.py",
>
> --------------------------------------------------------------------------------
> eHub/docs/features/hooks-projection.md at main · SurfaceW/eHub · GitHub (https://github.com/SurfaceW/eHub/blob/main/docs/features/hooks-projection.md)
> 【turn725581search35】 [wordlim: 200] Published: 5 months ago; Crawled: 3 months ago; Let a user enable and disable shared agentic hooks from the Agentic Hub window and have them safely surface in each tool's native hook configuration file — Cursor's `hooks.json`, Claude Code's `settings.json`, and Codex's `hooks.json` — without ever overwriting hook entries the user authored by hand.
>
> --------------------------------------------------------------------------------
> Hooks in Claude Code, Cursor and Codex: enforce what rules can't - DEV Community (https://dev.to/eliran_kotzero_e1781dc487/hooks-in-claude-code-cursor-and-codex-enforce-what-rules-cant-4ni2)
> 【turn725581search36】 [wordlim: 200] Crawled: today; Cursor loads hooks from `.claude/settings.json`, `.claude/settings.local.json` and `~/.claude/settings.json` when Include Third-Party Plugins, Skills, and Other Configs is on (Cursor Settings → Agents → Third-Party Imports; on by default). ... The scripts should work on that path too, because every Cursor hook input includes `cursor_version`, but we tested only the native `.cursor/hooks.json` input format.
>
> --------------------------------------------------------------------------------
> Copilot hooks: CLI, cloud agent and VS Code setup and events (https://aftergradient.com/guides/copilot-hooks)
> 【turn725581search37】 [wordlim: 200] Published: last month; Crawled: yesterday; `hooks` field in `.github/copilot/settings.json` or `.github/copilot/settings.local.json`  | CLI  | That repository ... Because the CLI reads `.claude/settings.json`, hooks written for Claude Code in a repository are picked up too; our Claude Code hooks guide covers that format.
>
> --------------------------------------------------------------------------------
> Debugging: Cursor reads Claude Code hooks, not Claude Code plugins (2026-09-04) — Soul of demarkus (https://soul.demarkus.io/t/soul.demarkus.io%3A6309/d/debugging.md/~/soul.demarkus.io%3A6309/d/debugging/cursor-reads-claude-code-hooks-not-claude-code-plugins-2026-09-04.md)
> 【turn725581search38】 [wordlim: 200] Published: 2 months ago; Crawled: 5 days ago; It does not read `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, a plugin's `.mcp.json`, commands, or skills, so a Claude Code plugin cannot be installed into Cursor as is; the compat layer only covers user-level hook settings.
>
> --------------------------------------------------------------------------------
> GitHub Copilot hooks reference | GitHub Copilot & GitHub Copilot Enterprise (https://orange-desert-0467ab003.2.azurestaticapps.net/docs/reference/hooks-reference)
> 【turn725581search39】 [wordlim: 200] Crawled: last month;     * Inline `hooks` block in repository settings — the `hooks` field at the top level of `.github/copilot/settings.json` (Git committed) or `.github/copilot/settings.local.json` (typically gitignored and user specific) in the repository. ... Cross-tool `.claude/settings.json` and `.claude/settings.local.json` files in the repository are also read.
>
> --------------------------------------------------------------------------------
> Hooks  |  Gemini API  |  Google AI for Developers (https://ai.google.dev/gemini-api/docs/agent-hooks?authuser=3)
> 【turn725581search40】 [wordlim: 200] Crawled: last month; Hooks let you run custom scripts or external HTTP requests right before or after the agent executes code or modifies files inside its remote sandbox. ...   * Handling script crashes, HTTP errors, and timeouts: If a command script crashes (non-zero exit status), an HTTP hook returns a non-2xx status code (such as a 4xx or 5xx server error), or an operation times out or returns unrecognized JSON, the runtime treats it as an approval (`allow`). ...   * Automatic approval on errors: If a hook script crashes (non-zero exit status), times out, or fails, the runtime logs the failure and allows the tool call to continue.
>
> --------------------------------------------------------------------------------
> Writing hooks for Gemini CLI | Gemini CLI (https://geminicli.com/docs/hooks/writing-hooks/)
> 【turn725581search41】 [wordlim: 200] Crawled: 3 weeks ago; Let’s create a simple hook that logs all tool executions to understand the basics. ... Note that we use Exit Code 0 to provide a structured denial message to the agent. ... BeforeToolSelection: Filter tools based on intent.
>
> --------------------------------------------------------------------------------
> gemini-cli/docs/hooks/reference.md at main · google-gemini/gemini-cli · GitHub (https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md)
> 【turn725581search42】 [wordlim: 200] Crawled: 2 weeks ago;     * `hookSpecificOutput.tool_input`: An object that merges with and overrides the model's arguments before execution. ...   * Exit Code 2 (Block Tool): Prevents execution.
>
> --------------------------------------------------------------------------------
> Gemini CLI hooks: settings.json, BeforeTool, AfterTool, exit codes and /hooks | AgentAtlas (https://agentatlas.dev/guides/gemini-cli-hooks)
> 【turn725581search43】 [wordlim: 200] Crawled: last week; # Gemini CLI hooks: settings.json, BeforeTool, AfterTool, exit codes and /hooks ... The docs prefer this for all logic, including intentional blocks. ...   * Any other code: a non-fatal warning. ...   * hookSpecificOutput: event fields such as additionalContext or a rewritten tool_input for BeforeTool.
>
> --------------------------------------------------------------------------------
> Gemini CLI hooks: BeforeTool in settings.json | getagenttools (https://getagenttools.com/blog/gemini-cli-hooks/)
> 【turn725581search44】 [wordlim: 200] Published: last week; Crawled: 4 days ago; # Gemini CLI hooks: BeforeTool in settings.json, and why a hook is "not working" ... Docs and code differ here. ... In `hookRunner.ts` at v0.66.0, text output with exit 1 becomes `allow` plus a warning. ... Eleven events under `hooks` in `settings.json`, documented on geminicli.com and in `docs/hooks/` of the repository.
>
> --------------------------------------------------------------------------------
> gemini-cli/docs/hooks/index.md at main · google-gemini/gemini-cli · GitHub (https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/index.md)
> 【turn725581search45】 [wordlim: 200] Crawled: yesterday;         "BeforeTool": [ ...                 "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/security.sh", ... #### Hook configuration fields
>
> --------------------------------------------------------------------------------
> Gemini CLI Cheat Sheet & Quick Reference (https://cheatsheets.zip/gemini-cli)
> 【turn725581search46】 [wordlim: 200] Published: 7 months ago; Crawled: 3 weeks ago; `BeforeTool`  | Before tool runs  | Yes (exit 2) ...       "hook_event_name": "BeforeTool",
>
> --------------------------------------------------------------------------------
> AI Coding Workshop 13 / 45 (https://xingjianz.com/assets/talks/ai-coding-workshop.pdf)
> 【turn725581search48】 [wordlim: 200] Published: 6 months ago; - `SessionStart` — load node, env, today’s TODOs.
> - `PreToolUse` — block unsafe commands.
> - `PostToolUse` — format, log, notify.
>
> --------------------------------------------------------------------------------
> Codex CLI now supports 5 hooks after v0.117.0 — PreToolUse and PostToolUse just dropped (https://www.reddit.com/r/codex/comments/1s67o19/codex_cli_now_supports_5_hooks_after_v01170/)
> 【turn725581reddit49】 [wordlim: 200] Published: 7 months ago; Codex CLI v0.117.0 added PreToolUse and PostToolUse hooks (beta), bringing the total to 5: ... I made a wrapper that plays pre-recorded human sounds on each hook — so you hear audio feedback on session start, stop, prompt submit, and tool use.
>
> --------------------------------------------------------------------------------
> Finally got observability working for Claude Code and Cursor agents: here's how the hooks actually work (https://www.reddit.com/r/LocalLLaMA/comments/1qbgwkm/finally_got_observability_working_for_claude_code/)
> 【turn725581reddit50】 [wordlim: 200] Published: 10 months ago; so i've been using both claude code and cursor for a while now and one thing that was driving me crazy was having zero visibility into what these agents are actually doing. like yeah i can see the output but when something goes wrong or takes forever i had no idea where in the chain it was breaking. ... cursor has a proper hooks system at \~/.cursor/hooks.json. you get access to like 7 different lifecycle events:
>
> --------------------------------------------------------------------------------
> Some hooks not working in Claude Code (https://www.reddit.com/r/ClaudeCode/comments/1rn8nxf/some_hooks_not_working_in_claude_code/)
> 【turn725581reddit51】 [wordlim: 200] Published: 8 months ago; Certain hooks worked, such as Stop and SessionStart. ... Had similar issues — make sure your hook command returns valid JSON to stdout with the right shape. PreToolUse hooks need to return { "continue": true } (or false to block).
>
> --------------------------------------------------------------------------------
> Codex CLI now supports 5 hooks after v0.117.0 — PreToolUse and PostToolUse just dropped (https://www.reddit.com/r/OpenAI/comments/1s6wq47/codex_cli_now_supports_5_hooks_after_v01170/)
> 【turn725581reddit52】 [wordlim: 200] Published: 7 months ago; Codex CLI v0.117.0 added PreToolUse and PostToolUse hooks (beta), bringing the total to 5: ... I made a wrapper that plays pre-recorded human sounds on each hook — so you hear audio feedback on session start, stop, prompt submit, and tool use.
>
> --------------------------------------------------------------------------------
> Codex CLI hooks are now stable — new PermissionRequest hook added (6 total) (https://www.reddit.com/r/OpenAI/comments/1sw5cuw/codex_cli_hooks_are_now_stable_new/)
> 【turn725581reddit53】 [wordlim: 200] Published: 6 months ago; * `SessionStart` ... * `PreToolUse` ... 👉 https://github.com/shanraisshan/codex-cli-hooks
>
> --------------------------------------------------------------------------------
> Claude Code Cheatsheet - Printable High Contrast Version - undefined (https://awesomeclaude.ai/code-cheatsheet.pdf)
> 【turn725581search54】 [wordlim: 200] Published: 1.2 years ago; ~/.claude/settings.json ... .claude/settings.json ... Hook Events:
>
> --------------------------------------------------------------------------------
> README Injection: Repository Files Hijacking AI Coding Assistants (https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/03/CSA_research_note_readme_instruction_injection_ai_coding_agents_20260317-csa-styled.pdf)
> 【turn725581search55】 [wordlim: 200] Published: 7 months ago; mechanism, which allows .claude/settings.json  to define shell commands that execute on ... Because Claude Code processes .claude/settings.json  from the project
>
> --------------------------------------------------------------------------------
> Codex CLI now supports 5 hooks after v0.117.0 — PreToolUse and PostToolUse just dropped (https://www.reddit.com/r/ChatGPT/comments/1s6wqvn/codex_cli_now_supports_5_hooks_after_v01170/)
> 【turn725581reddit56】 [wordlim: 200] Published: 7 months ago; Codex CLI v0.117.0 added PreToolUse and PostToolUse hooks (beta), bringing the total to 5: ... I made a wrapper that plays pre-recorded human sounds on each hook — so you hear audio feedback on session start, stop, prompt submit, and tool use. ... Note: For any ChatGPT-related concerns, email support@openai.com - this subreddit is not part of OpenAI and is not a support channel.
>
> --------------------------------------------------------------------------------
> Codex CLI hooks are now stable — new PermissionRequest hook added (6 total) (https://www.reddit.com/r/ChatGPT/comments/1sw5cqc/codex_cli_hooks_are_now_stable_new/)
> 【turn725581reddit57】 [wordlim: 200] Published: 6 months ago; * `SessionStart` ... * `PreToolUse` ... 👉 https://github.com/shanraisshan/codex-cli-hooks ... Note: For any ChatGPT-related concerns, email support@openai.com - this subreddit is not part of OpenAI and is not a support channel.
>
> --------------------------------------------------------------------------------
> 第15章 实战：Harness-Cowork 对抗式开发框架 (https://claudeleakage.com/docs/harness-engineering-book.pdf)
> 【turn725581search58】 [wordlim: 200] Published: 7 months ago; A JSON code block labeled “JSON” on the left and “.claude/settings.json（Hook 配置）” on the right.
>
> --------------------------------------------------------------------------------
> CCCFG handout (https://claude-code-book-site-production.up.railway.app/handouts/handout-09-config-explorer.pdf)
> 【turn725581search59】 [wordlim: 200] Published: 5 months ago; CCCFG — Claude Code Config Explorer ... • 30 settings.json keys including managed-enterprise locks (allowManagedHooksOnly, ... • 11 slash commands and 10 hook events in one place.
>
> --------------------------------------------------------------------------------
> Engineering Tips (https://ehrenborg.dev/assets/engineering_tips_slides.pdf)
> 【turn725581search60】 [wordlim: 200] Published: 26.9 years ago; Useful permissions in .claude/settings.json ...   https://code.claude.com/docs/en/hooks
> ```
>
> - Ran `git ls-remote origin refs/heads/main && command -v codex && codex --version && rg --files /workspace/.codex -g '*hook*' -g '*schema*' -g '*README*' -g '*AGENTS*'`
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "open": [
>     {
>       "ref_id": "https://prod.cursor.com/docs/reference/third-party-hooks"
>     },
>     {
>       "ref_id": "https://docs.github.com/en/copilot/reference/hooks-reference"
>     },
>     {
>       "ref_id": "https://developers.openai.com/codex/hooks/"
>     },
>     {
>       "ref_id": "https://geminicli.com/docs/hooks/reference/"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ```text
> Third Party Hooks | Cursor Docs (https://prod.cursor.com/docs/reference/third-party-hooks)
> 【turn789832view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://prod.cursor.com/docs/reference/third-party-hooks","lineno":null}); Total lines: 546
> L0: 【0†Google Tag Manager†www.googletagmanager.com】
> L1: 
> L2: 【1†Skip to main content】
> L3: 
> L4: ## Command Palette
> L5: 
> L6: Search for a command to run...
> L7: 
> L8: ## Get Started
> L9: 
> L10: 【2†Welcome】【3†Quickstart】
> L11: 
> L12: Models & Pricing
> L13: 
> L14: 【4†Changelog†cursor.com】【5†Release Notes】
> L15: 
> L16: ## Agent
> L17: 
> L18: 【6†Overview】【7†Agents Window】【8†Projects】【9†Agent Review】【10†Planning】【11†Prompting】【12†Voice Chat】【13†Debugging】【14†Design Mode】
> L19: 
> L20: Tools
> L21: 
> L22: Security
> L23: 
> L24: ## Grok Bot
> L25: 
> L26: 【15†Overview】【16†Get Started】【17†Use Cases】【18†Work with Grok Bot】【19†Settings】
> L27: 
> L28: Teams and Enterprise
> L29: ## Customize
> L30: 
> L31: 【20†Overview】【21†Plugins】【22†Rules】【23†Skills】【24†Subagents】【25†Hooks】【26†MCP】
> L32: 
> L33: ## Cloud Agents
> L34: 
> L35: 【27†Overview】【28†Setup】【29†Builds】【30†Apps】
> L36: 
> L37: Capabilities
> L38: 
> L39: 【31†Best Practices】【32†Choose Where Cloud Agents Run】【33†Automations】【34†Bugbot】【35†Security Agents】【36†PR Routing & Approval】【37†Rollouts】【38†Mobile】
> L40: 
> L41: Security
> L42: 
> L43: Self-Hosted Machines
> L44: 
> L45: 【39†Settings】【40†API】
> L46: ## Origin
> L47: 
> L48: 【41†Overview】
> L49: 
> L50: CLI
> L51: 
> L52: 【42†Create a repository】【43†Mirror GitHub】【44†Clone, Push & Pull】【45†CloneKit in CI】【46†Pull requests】【47†Code Tours】【48†Browse & Search】【49†Agents and Automations】
> L53: 
> L54: Apps
> L55: 
> L56: 【50†Settings】
> L57: 
> L58: ## Integrations
> L59: 
> L60: 【51†Slack】【52†Microsoft Teams】【53†Jira】【54†Linear】【55†Notion】【56†GitHub】【57†GitLab】【58†Azure DevOps】【59†Bitbucket】【60†JetBrains】【61†Xcode】【62†Tailscale】【63†Deeplinks】
> L61: 
> L62: ## SDK
> L63: 
> L64: 【64†TypeScript】【65†Python】【66†Bridge】【67†Changelog】
> L65: ## Agent SDK
> L66: 
> L67: Getting started
> L68: 
> L69: Integrations
> L70: 
> L71: Extensions
> L72: 
> L73: Guides
> L74: 
> L75: Templates
> L76: 
> L77: Reference
> L78: 
> L79: ## CLI
> L80: 
> L81: 【68†Overview】【69†Installation】【70†Capabilities】【71†Changelog】【72†Shell Mode】【73†ACP】【74†Headless / CI】
> L82: 
> L83: Reference
> L84: 
> L85: ## Teams & Enterprise
> L86: 
> L87: Teams
> L88: 
> L89: Enterprise
> L90: 
> L91: Get Started
> L92: 
> L93: # Third Party Hooks
> L94: 
> L95: Cursor supports loading hooks from third-party tools, enabling compatibility with existing hook configurations from other AI coding assistants.
> L96: ## 【75†Claude Code Hooks】
> L97: 
> L98: Cursor can load and execute hooks configured for Claude Code, allowing you to use the same hook scripts across both tools.
> L99: 
> L100: ### 【76†Requirements】
> L101: 
> L102: Claude Code hooks load when Include Third-Party Plugins, Skills, and Other Configs is enabled in Cursor Settings → Agents → Third-Party Imports. The setting is on by default.
> L103: ### 【77†Configuration Locations】
> L104: 
> L105: Claude Code hooks are loaded from these locations (in priority order):
> L106: 
> L107: Location  | Path  | Description
> L108: --- | --- | ---
> L109: Project local  | `.claude/settings.local.json`  | Project-specific, gitignored overrides
> L110: Project  | `.claude/settings.json`  | Project-level hooks, checked into repo
> L111: User  | `~/.claude/settings.json`  | User-level hooks, apply globally
> L112: ### 【78†Priority Order】
> L113: 
> L114: When hooks are configured in multiple locations, they are merged in this priority order (highest to lowest):
> L115: 
> L116:   1. Enterprise hooks (managed deployment)
> L117:   2. Team hooks (dashboard-configured)
> L118:   3. Project hooks (`.cursor/hooks.json`)
> L119:   4. User hooks (`~/.cursor/hooks.json`)
> L120:   5. Claude project local (`.claude/settings.local.json`)
> L121:   6. Claude project (`.claude/settings.json`)
> L122:   7. Claude user (`~/.claude/settings.json`)
> L123: All matching hooks from every source run. When responses conflict, higher-priority sources take precedence during merge.
> L124: 
> L125: Enterprise-managed hooks and dashboard distribution require an Enterprise plan. 【79†Contact sales†cursor.com】 to learn more.
> L126: ### 【80†Claude Code Hook Format】
> L127: 
> L128: Claude Code hooks use a similar but slightly different format. Cursor automatically maps Claude hook names to their Cursor equivalents.
> L129: Example Claude Code settings.json:
> L130: 
> L131:     `{  "hooks": {    "PreToolUse": [      {        "matcher": "Shell",        "hooks": [          {            "type": "command",            "command": "./hooks/validate-shell.sh"          }        ]      }    ],    "PostToolUse": [      {        "matcher": ".*",        "hooks": [          {            "type": "command",            "command": "./hooks/audit.sh"          }        ]      }    ]  }}`
> L132: ### 【81†Response Format Compatibility】
> L133: 
> L134: Cursor supports both Claude Code's nested `hookSpecificOutput` response format and the older flat response format. Hook scripts written for Claude Code will work in Cursor regardless of which format they use.
> L135: #### 【82†`PreToolUse` Response Formats】
> L136: 
> L137: Nested format (Claude Code style):
> L138: 
> L139:     `{  "hookSpecificOutput": {    "hookEventName": "PreToolUse",    "permissionDecision": "deny",    "permissionDecisionReason": "Blocked by policy",    "updatedInput": { "command": "npm ci" }  }}`
> L140: 
> L141: Flat format (Cursor native style):
> L142: 
> L143:     `{  "permission": "deny",  "user_message": "Blocked by policy",  "updated_input": { "command": "npm ci" }}`
> L144: Both formats are equivalent. The nested `permissionDecision` maps to `permission`, `permissionDecisionReason` maps to `user_message`, and `updatedInput` maps to `updated_input`.
> L145: #### 【83†`Stop` / `SubagentStop` Response Formats】
> L146: 
> L147: Nested format (Claude Code style):
> L148: 
> L149:     `{  "hookSpecificOutput": {    "decision": "block",    "reason": "Tasks incomplete, continue working"  }}`
> L150: 
> L151: Flat format (Claude Code legacy style):
> L152: 
> L153:     `{  "decision": "block",  "reason": "Tasks incomplete, continue working"}`
> L154: 
> L155: Cursor native format:
> L156: 
> L157:     `{  "followup_message": "Tasks incomplete, continue working"}`
>
> --------------------------------------------------------------------------------
> GitHub Copilot hooks reference - GitHub Docs (https://docs.github.com/en/copilot/reference/hooks-reference)
> 【turn789832view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://docs.github.com/en/copilot/reference/hooks-reference","lineno":null}); Total lines: 862
> L0:   1.   2. 【0†GitHub Docs】
> L1: 
> L2: Search or ask Copilot/
> L3: 
> L4: Menu
> L5: 
> L6: Collapse sidebar
> L7: 
> L8: Expand sidebar
> L9: 
> L10:   1. 【0†Home】
> L11:   2. 【1†GitHub Copilot】
> L12:   3. 【2†Reference】
> L13:   4. Hooks reference
> L14: 
> L15: In this article
> L16: 
> L17: # GitHub Copilot hooks reference
> L18: 
> L19: Find hook events, configuration formats, and input payloads for hooks in Copilot CLI and Copilot in the cloud.
> L20: 
> L21: Copy markdown
> L22: ## In this article
> L23: 
> L24:   * 【3†Introduction】
> L25: 
> L26:   * 【4†Hooks locations】
> L27: 
> L28:   * 【5†Cloud agent execution environment】
> L29: 
> L30:   * 【6†Hook configuration format】
> L31: 
> L32:   * 【7†Hook events】
> L33: 
> L34:   * 【8†Hook event input payloads】
> L35: 
> L36:   * 【9†preToolUse decision control】
> L37: 
> L38:   * 【10†agentStop / subagentStop decision control】
> L39: 
> L40:   * 【11†postToolUse output】
> L41: 
> L42:   * 【12†permissionRequest decision control】
> L43: 
> L44:   * 【13†notification hook】
> L45: 
> L46:   * 【14†Matcher filtering】
> L47: 
> L48:   * 【15†Tool names for hook matching】
> L49: 
> L50:   * 【16†Exit codes for command hooks】
> L51:   * 【17†Disable all hooks】
> L52: 
> L53:   * 【18†Further reading】
> L54: ## 【3†Introduction】
> L55: 
> L56: Hooks are external commands that execute at specific lifecycle points during a session, enabling custom automation, security controls, and integrations.
> L57: 
> L58: Hooks are supported in two Copilot surfaces: Copilot CLI and Copilot in the cloud. Most of the configuration format and event payloads are identical, but the execution environment and the set of events that can fire differ.
> L59: Throughout this article, behavior that differs between the two surfaces is called out in "CLI only" and "Cloud agent only" notes. Anything not marked applies to both.
> L60: ## 【4†Hooks locations】
> L61: 
> L62: The locations where hooks run, and where you can store hook configuration files, depend on the surface:
> L63: 
> L64:   * Copilot CLI — hooks run on the developer's local machine in the same shell as the CLI. All hook events described in this article are supported by the CLI.
> L65: 
> L66: Hooks are loaded from the following sources in order (policy, then user, then project, then plugins) and combined. When the same event appears in multiple sources, all hook entries from all sources are run.
> L67:     * Policy-level hook files — JSON files in the platform-appropriate policy directory, loaded in alphabetical order. Policy hooks are machine-wide and load before all other hooks. They cannot be disabled by `disableAllHooks` and are available regardless of folder trust state. See 【19†Policy hooks】 below.
> L68:     * Repository-level hook files — `.github/hooks/*.json` in the repository root.
> L69:     * User-level hook files — `*.json` files in the user-level hooks directory. By default this is `~/.copilot/hooks/` on macOS and Linux, or `%USERPROFILE%\.copilot\hooks\` on Windows. If `COPILOT_HOME` is set, it is `$COPILOT_HOME/hooks/`.
> L70:     * Inline `hooks` block in repository settings — the `hooks` field at the top level of `.github/copilot/settings.json` (Git committed) or `.github/copilot/settings.local.json` (typically gitignored and user specific) in the repository. Cross-tool `.claude/settings.json` and `.claude/settings.local.json` files in the repository are also read.
> L71:     * Inline `hooks` block in user-level config — the `hooks` field at the top level of `~/.copilot/settings.json`. The CLI no longer reads `~/.copilot/config.json` for hooks.
> L72:     * Hooks contributed by installed plugins — declared by each plugin in its own `hooks.json` (or under `hooks/hooks.json`) inside the plugin's installation directory.
> L73:   * Copilot in the cloud — hooks run inside the ephemeral Linux sandbox that cloud agent provisions for each job. The sandbox is non-interactive, has a constrained network, and is destroyed when the job ends. A subset of events fires, and only `bash` (or `command`) entries are honored.
> L74: Hook configuration is loaded from `.github/hooks/*.json` files in the cloned repository.
> L75: ### 【19†Policy hooks】
> L76: 
> L77: Note
> L78: 
> L79: Copilot CLI only. Policy hooks are not supported under Copilot in the cloud.
> L80: 
> L81: Policy hooks are machine-wide hooks loaded by administrators. They load before all other hooks and cannot be disabled by `disableAllHooks`.
> L82: 
> L83: Policy hooks are discovered from two sources:
> L84:   * Filesystem: JSON files in the platform-appropriate policy directory, loaded in alphabetical order:
> L85:     * Linux/macOS: `/etc/github-copilot/policy.d/*.json`
> L86:     * Windows: `C:\ProgramData\GitHub\Copilot\policy.d\*.json`
> L87:   * Windows Registry: Values under `HKLM\Software\Policies\GitHub\Copilot` (each subkey holds a `Policy` REG_SZ value containing a JSON policy document).
> L88: Policy hook files use the same hook configuration format as user and project hooks (`{ "version": 1, "hooks": { ... } }`). On POSIX systems, policy files must be owned by root and must not be group- or world-writable.
> L89: 
> L90: Policy hooks are intended for use by enterprise IT administrators and require elevated privileges to install. End users cannot modify them. Policy hooks always run on the host, even when the session sandbox is enabled—see 【20†Sandboxed sessions】.
> L91: ### 【21†Agent-scoped hooks】
> L92: 
> L93: Note
> L94: 
> L95: Copilot CLI only.
> L96: Declare a `hooks` event map in a custom agent's frontmatter to run command or HTTP hooks only while that agent is selected. These hooks run in addition to session, user, repository, plugin, and policy hooks.
> L97: 
> L98:     `---
> L99:     name: formatter
> L100:     description: Formats changed files
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://developers.openai.com/codex/hooks/ ; rewritten summary of https://learn.chatgpt.com/docs/hooks)
> 【turn789832view2】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://developers.openai.com/codex/hooks/","lineno":null}); Redirected to URL: https://learn.chatgpt.com/docs/hooks; Total lines: 1748
> L0: For the complete documentation index, see 【0†llms.txt】. Markdown versions of documentation pages are available by appending `.md` to the page URL.
> L1: 
> L2: 【1†ChatGPT】
> L3: 
> L4: 【1†Home】
> L5: 
> L6: 【2†API】
> L7: 
> L8: 【3†ChatGPT】
> L9: 
> L10: 【4†Docs】
> L11: 
> L12: 【5†Use cases】
> L13: 
> L14: 【6†Training】
> L15: 
> L16: 【7†Resources】
> L17: 
> L18: 【8†Resources】
> L19: 
> L20: 【4†Overview】 【9†Features】 【10†Configuration】 【11†Developers】 【12†Security】 【13†Administration】 【5†Use Cases】 【7†Resources】
> L21: 
> L22: ## Search the docs
> L23: 
> L24: Search docs[Input: Start searching]
> L25: ### Suggested
> L26: 
> L27: [Button: responses create][Button: reasoning_effort][Button: realtime][Button: prompt caching]
> L28: 
> L29: Primary navigation
> L30: 
> L31: [Button: API ][Button: ChatGPT ][Button: Docs ][Button: Use cases ][Button: Training ][Button: Resources ][Button: Resources ]
> L32: 
> L33: Theme Light [Input] Dark [Input] System [Input]
> L34: 
> L35: Search docs[Input: Start searching]
> L36: ### Suggested
> L37: 
> L38: [Button: responses create][Button: reasoning_effort][Button: realtime][Button: prompt caching]
> L39: 
> L40: [Button: Overview ][Button: Models ][Button: Agents ][Button: Tools ][Button: Audio & voice ][Button: Production ][Button: API reference ]
> L41: 
> L42: Docs Overview
> L43: 
> L44:   * 【2†Home】
> L45: 
> L46: ### Get started
> L47: 
> L48:   * 【14†Quickstart】
> L49:   * 【15†Using GPT-6】
> L50:   * 【16†Key concepts】
> L51:   * 【17†API credits for ChatGPT subscribers】
> L52: ### Core concepts
> L53: 
> L54:   * 【18†Responses API】
> L55:   * 【19†Decisions API】
> L56:   * 【20†Conversation state】
> L57:   * 【21†Background mode】
> L58:   * 【22†Streaming】
> L59:   * 【23†WebSocket mode】
> L60:   * 【24†Mid-turn steering】
> L61:   * 【25†Multi-agent】
> L62:   * 【26†Webhooks】
> L63:   * 【27†File inputs】
> L64:   * 【28†Compaction】
> L65:   * 【29†Counting tokens】
> L66: 
> L67: ### SDKs and CLI
> L68: 
> L69:   * 【30†OpenAI SDK】
> L70:   * 【31†OpenAI CLI】
> L71: 
> L72: ### Cloud providers
> L73: 
> L74:   * 【32†Amazon Bedrock】
> L75:   * 【33†Google Cloud】
> L76: ### Resources
> L77: 
> L78:   * 【34†Changelog】
> L79:   * 【35†Deprecations】
> L80:   * 【36†Supported countries】
> L81:   * 【37†OpenAI Crawlers】
> L82:   * 【38†Terms and policies†openai.com】
> L83: ### Legacy APIs
> L84: 
> L85:   * Agent Builder
> L86:     * 【39†Overview】
> L87:     * 【40†Migration guide】
> L88:     * 【41†Node reference】
> L89:     * 【42†Safety in building agents】
> L90:   * Evals
> L91:     * 【43†Getting started】
> L92:     * 【44†Working with evals】
> L93:     * 【45†Prompt optimizer】
> L94:     * 【46†External models】
> L95:     * 【47†Graders】
> L96:   * Fine-tuning
> L97:     * 【48†Optimization cycle】
> L98:     * 【49†Supervised fine-tuning】
> L99:     * 【50†Vision fine-tuning】
> L100:     * 【51†Direct preference optimization】
> L101:     * 【52†Best practices】
> L102:   * Assistants API
> L103:     * 【53†Migration guide】
> L104:   * 【54†Model catalog】
> L105: ### Choose a model
> L106: 
> L107:   * 【55†Pricing】
> L108:   * 【56†Model selection】
> L109: 
> L110: ### Text and code
> L111: 
> L112:   * 【57†Text generation】
> L113:   * 【58†Code generation】
> L114:   * 【59†Structured output】
> L115: 
> L116: ### Prompting
> L117: 
> L118:   * 【60†Overview】
> L119:   * 【61†Prompt engineering】
> L120:   * 【62†Citation formatting】
> L121:   * 【63†Migration guide】
> L122:   * 【64†Prompt generation】
> L123:   * 【65†Frontend prompting】
> L124: 
> L125: ### Reasoning
> L126: 
> L127:   * 【66†Reasoning models】
> L128:   * 【67†Reasoning best practices】
> L129: ### Images
> L130: 
> L131:   * 【68†Images and vision】
> L132:     * 【69†Image input cost calculator】
> L133:   * 【70†Image generation】
> L134:     * 【70†Overview】
> L135:     * 【71†Image prompting】
> L136: 
> L137: ### Realtime and audio
> L138: 
> L139:   * 【72†Audio and speech】
> L140:   * 【73†Getting started】
> L141:   * 【74†Voice agents】
> L142: 
> L143: ### Specialized models
> L144: 
> L145:   * 【75†Embeddings】
> L146:   * 【76†Moderation】
> L147: 
> L148:   * 【77†Overview】
> L149: ### Agents API
> L150:   * 【78†Overview】
> L151:   * 【79†Quickstart】
> L152:   * 【80†Architecture】
> L153:   * 【81†Configuring Agents】
> L154:   * Sessions
> L155:     * 【82†Run and continue sessions】
> L156:     * 【83†Events and items】
> L157:     * 【84†Manage sessions】
> L158:     * 【85†Scheduled automations】
> L159:     * 【86†Automatic review】
> L160:     * 【87†Webhooks】
> L161:   * Environments and sandboxes
> L162:     * 【88†OpenAI-hosted sandboxes】
> L163:     * 【89†Self-hosted sandboxes】
> L164:     * 【90†Sandbox lifecycle】
> L165:     * 【91†Pre-warm sandboxes】
> L166:     * 【92†Sandbox security】
> L167:     * 【93†Files and artifacts】
> L168:   * Tools and integrations
> L169:     * 【94†Web search】
> L170:     * 【95†Computer use】
> L171:     * 【96†Functions】
> L172:     * 【97†MCP connections】
> L173:     * 【98†Plugins】
> L174:     * 【99†Vaults】
> L175:   * 【100†Multi-agent】
> L176:   * 【101†Observability and usage】
> L177:   * 【102†Tracing】
> L178:   * 【103†Errors and recovery】
> L179:   * 【104†API reference】
> L180:   * 【105†Bedrock Managed Agents】
> L181: ### Agents SDK
> L182: 
> L183:   * 【106†Overview】
> L184:   * 【107†Quickstart】
> L185:   * 【108†Agent definitions】
> L186:   * 【109†Models and providers】
> L187:   * 【110†Running agents】
> L188:   * 【111†Sandbox agents】
> L189:   * 【112†Orchestration】
> L190:   * 【113†Guardrails】
> L191:   * 【114†Results and state】
> L192:   * 【115†Integrations and observability】
> L193:   * 【116†Evaluate agent workflows】
> L194: 
> L195: ### ChatKit
> L196: 
> L197:   * 【117†Overview】
> L198:   * 【118†Customize】
> L199:   * 【119†Widgets】
> L200:   * 【120†Actions】
> L201:   * 【121†Advanced integrations】
> L202: 
> L203:   * 【122†Overview】
> L204:   * 【123†Function calling】
> L205: ### Search and retrieval
> L206: 
> L207:   * 【124†Web search】
> L208:   * 【125†File search】
> L209:   * 【126†Retrieval】
> L210: 
> L211: ### Connect tools and data
> L212: 
> L213:   * 【127†MCP servers】
> L214:   * 【128†Secure MCP Tunnel】
> L215: 
> L216: ### Build tool workflows
> L217: 
> L218:   * 【129†Skills】
> L219:   * 【130†Tool search】
> L220:   * 【131†Programmatic tool calling】
> L221:   * 【132†Async tool calling】
> L222: 
> L223: ### Computer and code
> L224: 
> L225:   * 【133†Shell】
> L226:   * 【134†Computer use】
> L227:     * 【135†Integration recipes】
> L228:     * 【136†Driver reference】
> L229:   * 【137†Apply Patch】
> L230:   * 【138†Code interpreter】
> L231: ### Media
> L232: 
> L233:   * 【139†Image generation】
> L234: 
> L235:   * 【72†Overview】
> L236: 
> L237: ### GPT-Live
> L238: 
> L239:   * 【140†Getting started】
> L240:   * 【141†Prompting】
> L241:   * 【142†Managing sessions】
> L242:   * 【143†Delegation and tools】
> L243:   * 【144†Migrate to GPT-Live】
> L244:   * 【145†Partner integrations】
> L245: 
> L246: ### Realtime API
> L247: 
> L248:   * 【73†Getting started】
> L249:   * 【146†Prompting】
> L250:   * 【147†Managing conversations】
> L251:   * 【148†Voice activity detection】
> L252:   * 【149†Tools and MCP】
>
> --------------------------------------------------------------------------------
> Hooks reference | Gemini CLI (https://geminicli.com/docs/hooks/reference/)
> 【turn789832view3】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://geminicli.com/docs/hooks/reference/","lineno":null}); Total lines: 571
> L0: 【0†Skip to content】
> L1: 
> L2: 【1†Gemini CLI】
> L3: 
> L4:   * 【1†Home】
> L5:   * Extensions
> L6:     * 【2†Browse extensions】
> L7:     * 【3†About Extensions】
> L8:   * 【4†Docs】
> L9:   * 【5†Reference】
> L10:   * 【6†Resources】
> L11:   * 【7†Changelog】
> L12: 
> L13: Search ` `Ctrl``K` `
> L14: 
> L15: [Button: Cancel ]
> L16: 
> L17: Select theme [Select]
> L18:   * 【1†Home】
> L19:   * Extensions
> L20:     * 【2†Browse extensions】
> L21:     * 【3†About Extensions】
> L22:   * Docs
> L23:     * Get started
> L24:       * 【4†Overview】
> L25:       * 【8†Quickstart】
> L26:       * 【9†Installation】
> L27:       * 【10†Authentication】
> L28:       * 【11†CLI cheatsheet】
> L29:       * 【12†Gemini 3 on Gemini CLI】
> L30:     * Use Gemini CLI
> L31:       * 【13†File management】
> L32:       * 【14†Get started with Agent Skills】
> L33:       * 【15†Manage context and memory】
> L34:       * 【16†Execute shell commands】
> L35:       * 【17†Manage sessions and history】
> L36:       * 【18†Plan tasks with todos】
> L37:       * 【19†Use Plan Mode with model steering 🔬】
> L38:       * 【20†Web search and fetch】
> L39:       * 【21†Set up an MCP server】
> L40:       * 【22†Automate tasks】
> L41:     * Features
> L42:       * Extensions
> L43:         * 【23†Overview】
> L44:         * 【24†User guide: Install and manage】
> L45:         * 【25†Developer guide: Build extensions】
> L46:         * 【26†Developer guide: Best practices】
> L47:         * 【27†Developer guide: Releasing】
> L48:         * 【28†Developer guide: Reference】
> L49:       * Agent Skills
> L50:         * 【29†Overview】
> L51:         * 【14†Get started with Agent Skills】
> L52:         * 【30†Creating Agent Skills】
> L53:         * 【31†Using Agent Skills】
> L54:         * 【32†Developer guide: Best practices】
> L55:       * 【33†Auto Memory 🔬】
> L56:       * 【34†Checkpointing】
> L57:       * 【35†Headless mode】
> L58:       * 【36†Git worktrees 🔬】
> L59:       * Hooks
> L60:         * 【37†Overview】
> L61:         * 【38†Reference】
> L62:       * IDE integration
> L63:         * 【39†Overview】
> L64:         * 【40†Developer guide: ACP mode】
> L65:       * MCP servers
> L66:         * 【41†Overview】
> L67:         * 【42†Resource tools】
> L68:       * 【43†Model routing】
> L69:       * 【44†Model selection】
> L70:       * 【45†Model steering 🔬】
> L71:       * 【46†Notifications 🔬】
> L72:       * 【47†Plan mode】
> L73:       * 【48†Subagents】
> L74:       * 【49†Remote subagents】
> L75:       * 【50†Rewind】
> L76:       * 【51†Sandboxing】
> L77:       * 【52†Settings】
> L78:       * 【53†Telemetry】
> L79:       * 【54†Token caching】
> L80:     * Configuration
> L81:       * 【55†Custom commands】
> L82:       * 【56†Enterprise configuration】
> L83:       * 【57†Ignore files (.geminiignore)】
> L84:       * 【58†Model configuration】
> L85:       * 【59†Project context (GEMINI.md)】
> L86:       * 【52†Settings】
> L87:       * 【60†System prompt override】
> L88:       * 【61†Themes】
> L89:       * 【62†Trusted folders】
> L90:     * Development
> L91:       * 【63†Behavioral evaluations】
> L92:       * 【64†Contribution guide】
> L93:       * 【65†Integration testing】
> L94:       * 【66†Issue and PR automation】
> L95:       * 【67†Local development】
> L96:       * 【68†NPM package structure】
> L97:   * Reference
> L98:     * 【69†Command reference】
> L99:     * 【70†Configuration reference】
> L100:     * 【71†Keyboard shortcuts】
> L101:     * 【72†Memory import processor】
> L102:     * 【73†Policy engine】
> L103:     * 【74†Tools reference】
> L104:   * Resources
> L105:     * 【75†FAQ】
> L106:     * 【76†Quota and pricing】
> L107:     * 【77†Terms and privacy】
> L108:     * 【78†Troubleshooting】
> L109:     * 【79†Uninstall】
> L110:   * Changelog
> L111:     * 【7†Release notes】
> L112:     * 【80†Stable release】
> L113:     * 【81†Preview release】
> L114:   * Get started
> L115:     * 【4†Overview】
> L116:     * 【8†Quickstart】
> L117:     * 【9†Installation】
> L118:     * 【10†Authentication】
> L119:     * 【11†CLI cheatsheet】
> L120:     * 【12†Gemini 3 on Gemini CLI】
> L121:   * Use Gemini CLI
> L122:     * 【13†File management】
> L123:     * 【14†Get started with Agent Skills】
> L124:     * 【15†Manage context and memory】
> L125:     * 【16†Execute shell commands】
> L126:     * 【17†Manage sessions and history】
> L127:     * 【18†Plan tasks with todos】
> L128:     * 【19†Use Plan Mode with model steering 🔬】
> L129:     * 【20†Web search and fetch】
> L130:     * 【21†Set up an MCP server】
> L131:     * 【22†Automate tasks】
> L132:   * Features
> L133:     * Extensions
> L134:       * 【23†Overview】
> L135:       * 【24†User guide: Install and manage】
> L136:       * 【25†Developer guide: Build extensions】
> L137:       * 【26†Developer guide: Best practices】
> L138:       * 【27†Developer guide: Releasing】
> L139:       * 【28†Developer guide: Reference】
> L140:     * Agent Skills
> L141:       * 【29†Overview】
> L142:       * 【14†Get started with Agent Skills】
> L143:       * 【30†Creating Agent Skills】
> L144:       * 【31†Using Agent Skills】
> L145:       * 【32†Developer guide: Best practices】
> L146:     * 【33†Auto Memory 🔬】
> L147:     * 【34†Checkpointing】
> L148:     * 【35†Headless mode】
> L149:     * 【36†Git worktrees 🔬】
> L150:     * Hooks
> L151:       * 【37†Overview】
> L152:       * 【38†Reference】
> L153:     * IDE integration
> L154:       * 【39†Overview】
> L155:       * 【40†Developer guide: ACP mode】
> L156:     * MCP servers
> L157:       * 【41†Overview】
> L158:       * 【42†Resource tools】
> L159:     * 【43†Model routing】
> L160:     * 【44†Model selection】
> L161:     * 【45†Model steering 🔬】
> L162:     * 【46†Notifications 🔬】
> L163:     * 【47†Plan mode】
> L164:     * 【48†Subagents】
> L165:     * 【49†Remote subagents】
> L166:     * 【50†Rewind】
> L167:     * 【51†Sandboxing】
> L168:     * 【52†Settings】
> L169:     * 【53†Telemetry】
> L170:     * 【54†Token caching】
> L171:   * Configuration
> L172:     * 【55†Custom commands】
> L173:     * 【56†Enterprise configuration】
> L174:     * 【57†Ignore files (.geminiignore)】
> L175:     * 【58†Model configuration】
> L176:     * 【59†Project context (GEMINI.md)】
> L177:     * 【52†Settings】
> L178:     * 【60†System prompt override】
> L179:     * 【61†Themes】
> L180:     * 【62†Trusted folders】
> L181:   * Development
> L182:     * 【63†Behavioral evaluations】
> L183:     * 【64†Contribution guide】
> L184:     * 【65†Integration testing】
> ```
>
> - Ran `ls -l /opt/codex/bin/codex && codex features list && rg -n 'unittest|pytest|lastfailed|Circuit Breaker' AGENTS.md .github/workflows/ci.yml skills/ground-meta-project/SKILL.md templates/team/system_prompt.md`
>
> </details>
>
> Часть предпосылок верна: Cursor и Copilot CLI действительно умеют читать Claude-конфиги. Но из этого не следует одинаковая работа всех событий. В самом плане уже видны две проблемы: границы изменений предлагается применять и к чтению файлов, а обычные повторные правки — считать основанием для блокировки. Такие хуки могут мешать нормальной работе.
>
> <details><summary>Explored 3 files, ran a command, called 2 tools</summary>
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "find": [
>     {
>       "pattern": "only supports",
>       "ref_id": "https://learn.chatgpt.com/docs/hooks"
>     },
>     {
>       "pattern": "hooks.json",
>       "ref_id": "https://learn.chatgpt.com/docs/hooks"
>     },
>     {
>       "pattern": "Read",
>       "ref_id": "https://prod.cursor.com/docs/reference/third-party-hooks"
>     },
>     {
>       "pattern": "Unsupported",
>       "ref_id": "https://prod.cursor.com/docs/reference/third-party-hooks"
>     },
>     {
>       "pattern": "Exit Code 2",
>       "ref_id": "https://geminicli.com/docs/hooks/reference/"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ```text
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks)
> 【turn384692view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://learn.chatgpt.com/docs/hooks","pattern":"only supports"}); Total lines: 1748
> No matching text found for "only supports"
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks)
> 【turn384692view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://learn.chatgpt.com/docs/hooks","pattern":"hooks.json"}); Total lines: 1748
> L966:   * Matching hooks from multiple files all run.
> L967:   * Multiple matching command hooks for the same event are launched concurrently, so one hook can’t prevent another matching hook from starting.
> L968:   * Non-managed hooks must be reviewed and trusted before they run.
> L969: 
> L970: Hooks run at different points in a conversation:
> L971: When  | Hooks
> L972: --- | ---
> L973: During a turn  | `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, `Stop`
> L974: For each model request attempt  | `PreModelRequest`, `PostModelRequest`
> L975: When you interrupt an active turn  | `Interrupt` (doesn’t run for subagents)
> L976: When a session or subagent starts  | `SessionStart`, `SubagentStart`
> L977: When the main thread ends  | `SessionEnd` (doesn’t run for subagents)
> L978: ## Where Codex looks for hooks
> L979: 
> L980: Codex discovers hooks next to active config layers in either of these forms:
> L981: 
> L982:   * `hooks.json`
> L983:   * inline `[hooks]` tables inside `config.toml`
> L984: 
> L985: Installed plugins can also bundle lifecycle config through their plugin manifest or a default `hooks/hooks.json` file. See 【552†Build plugins†developers.openai.com】 for the plugin packaging rules.
> L986: 
> L987: In practice, the four most useful locations are:
> L988:   * `~/.codex/hooks.json`
> L989:   * `~/.codex/config.toml`
> L990:   * `<repo>/.codex/hooks.json`
> L991:   * `<repo>/.codex/config.toml`
> L992: 
> L993: If more than one hook source exists, Codex loads all matching hooks. Higher-precedence config layers don’t replace lower-precedence hooks. If a single layer contains both `hooks.json` and inline `[hooks]`, Codex merges them and warns at startup. Prefer one representation per layer.
> L994: Codex can also discover hooks bundled with enabled plugins. Plugin-bundled hooks load alongside other hook sources and use the same trust-review flow as other non-managed hooks.
> L995: 
> L996: Project-local hooks load only when the project `.codex/` layer is trusted. In untrusted projects, Codex still loads user and system hooks from their own active config layers.
> L997: ## Review and trust hooks
> L998: 
> L999: Codex lists configured hooks before deciding which ones can run. Before a non-managed hook can run, Codex requires you to review and trust the exact hook definition. Codex records trust against the hook’s current hash, so new or changed hooks are marked for review and skipped until trusted.
> L1000: Use `/hooks` in the CLI to inspect hook sources, review new or changed hooks, trust hooks, or disable individual non-managed hooks. If hooks need review at startup, Codex prints a warning that tells you to open `/hooks`.
> L1001: 
> L1002: Managed hooks from system, MDM, cloud, or `requirements.toml` sources are marked as managed, trusted by policy, and can’t be disabled from the user hook browser.
> L1003: For one-off automation that already vets hook sources outside Codex, pass `--dangerously-bypass-hook-trust` to run enabled hooks without requiring persisted hook trust for that invocation.
> L1004: ## Config shape
> L1005: 
> L1006: Hooks are organized in three levels:
> L1007:   * A hook event such as `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, or `Stop`
> L1008:   * A matcher group that decides when that event matches
> L1009:   * One or more hook handlers that run when the matcher group matches
> L1010: 
> L1011:     `{
> L1012:       "description": "Optional lifecycle hooks for this workspace.",
> L1013:       "hooks": {
> L1014:         "SessionStart": [
> L1015:           {
> L1016:             "matcher": "startup|resume",
> L1017:             "hooks": [
> L1018:               {
> L1019:                 "type": "command",
> L1020:                 "command": "python3 ~/.codex/hooks/session_start.py",
> L1021:                 "statusMessage": "Loading session notes",
> L1022:                 "additionalContextLimit": 5000
> L1023:               }
> L1024:             ]
> L1025:           }
> L1026:         ],
> L1027:         "SessionEnd": [
> L1028:           {
> L1029:             "hooks": [
> L1030:               {
> L1031:                 "type": "command",
> L1032:                 "command": "python3 ~/.codex/hooks/session_end.py",
> L1033:                 "timeout": 3
> L1034:               }
> L1035:             ]
> L1036:           }
> L1037:         ],
> L1038:         "PreToolUse": [
> L1039:           {
> L1040:             "matcher": "Bash",
> L1041:             "hooks": [
> L1042:               {
> L1043:                 "type": "command",
> L1044:                 "command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/pre_tool_use_policy.py\"",
> L1045:                 "statusMessage": "Checking Bash command"
> L1046:               }
> L1047:             ]
> L1048:           }
> L1049:         ],
> L1050:         "PermissionRequest": [
> L1051:           {
> L1052:             "matcher": "Bash",
> L1053:             "hooks": [
> L1054:               {
> L1055:                 "type": "command",
> L1056:                 "command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/permission_request.py\"",
> L1057:                 "statusMessage": "Checking approval request"
> L1058:               }
> L1059:             ]
> L1060:           }
> L1061:         ],
> L1062:         "PostToolUse": [
> L1063:           {
> L1064:             "matcher": "Bash",
> L1065:             "hooks": [
> L1066:               {
> L1067:                 "type": "command",
> L1068:                 "command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/post_tool_use_review.py\"",
> L1069:                 "statusMessage": "Reviewing Bash output"
> L1070:               }
> L1071:             ]
> L1072:           }
> L1073:         ],
> L1074:         "UserPromptSubmit": [
> L1075:           {
> L1076:             "hooks": [
> L1077:               {
> L1078:                 "type": "command",
> L1079:                 "command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/user_prompt_submit_data_flywheel.py\""
> L1080:               }
> L1081:             ]
> L1082:           }
> L1083:         ],
> L1084:         "Stop": [
> L1085:           {
> L1086:             "hooks": [
> L1087:               {
> L1088:                 "type": "command",
> L1089:                 "command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/stop_continue.py\"",
> L1090:                 "timeout": 30
> L1091:               }
> L1092:             ]
> L1093:           }
> L1094:         ]
> L1095:       }
> L1096:     }`
> L1097: Notes:
> L1098:   * `description` is optional top-level metadata for a `hooks.json` file. It doesn’t change which hooks run.
> L1099:   * `timeout` is in seconds.
> L1100:   * If `timeout` is omitted, Codex uses `600` seconds for most hooks.
> L1101:     * `SessionEnd` and `Interrupt` use `1` second by default and support up to `3` seconds.
> L1102:   * `statusMessage` is optional.
> L1103:   * `additionalContextLimit` sets how much `additionalContext` a command hook can send to the model before Codex saves the full text to disk and sends a shorter preview instead. See 【553†Large hook output】.
> L1104:   * `commandWindows` is an optional Windows-only command override. In TOML, use `command_windows` or `commandWindows`.
> L1105:   * Set `async` to `true` to 【554†run a command hook in the background】.
> L1106:   * `command` and `mcp_tool` handlers are supported. `prompt` and `agent` handlers are parsed but skipped.
> L1107:   * Commands run with the session `cwd` as their working directory.
> L1108:   * For repo-local hooks, prefer resolving from the git root instead of using a relative path such as `.codex/hooks/...`. Codex may be started from a subdirectory, and a git-root-based path keeps the hook location stable.
> L1109: Equivalent inline TOML in `config.toml`:
> L1110: 
> L1111:     `[[hooks.SessionStart]]
> L1112:     matcher = "^compact$"
> L1113: 
> L1114:     [[hooks.SessionStart.hooks]]
> L1115:     type = "command"
> L1116:     command = '/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/session_start.py"'
> L1117:     additionalContextLimit = 5000
> L1118: 
> L1119:     [[hooks.PreToolUse]]
> L1120:     matcher = "^Bash$"
> L1121: 
> L1122:     [[hooks.PreToolUse.hooks]]
> L1123:     type = "command"
> L1124:     command = '/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/pre_tool_use_policy.py"'
> L1221:     windows_managed_dir = 'C:\enterprise\hooks'
> L1222: 
> L1223:     [[hooks.PreToolUse]]
> L1224:     matcher = "^Bash$"
> L1225: 
> L1226:     [[hooks.PreToolUse.hooks]]
> L1227:     type = "command"
> L1228:     command = "python3 /enterprise/hooks/pre_tool_use_policy.py"
> L1229:     command_windows = 'py -3 C:\enterprise\hooks\pre_tool_use_policy.py'
> L1230:     timeout = 30
> L1231:     statusMessage = "Checking managed Bash command"`
> L1232: Notes for managed hooks:
> L1233:   * `managed_dir` is used on macOS and Linux.
> L1234:   * `windows_managed_dir` is used on Windows.
> L1235:   * Codex doesn’t distribute the scripts in `managed_dir`; your enterprise tooling must install and update them separately.
> L1236:   * Managed hook commands should use absolute script paths under the configured managed directory.
> L1237:   * `allow_managed_hooks_only = true` skips hooks from user, project, session, and plugin sources, but still loads managed hooks from `requirements.toml` and other managed config layers.
> L1238: ## Plugin-bundled hooks
> L1239: 
> L1240: When a plugin is enabled, Codex can load lifecycle hooks from that plugin alongside user, project, and managed hooks.
> L1241: By default, Codex looks for `hooks/hooks.json` inside the plugin root. A plugin manifest can override that default with a `hooks` entry in `.codex-plugin/plugin.json`. The manifest entry can be a `./`-prefixed path, an array of `./`-prefixed paths, an inline hooks object, or an array of inline hooks objects.
> L1242: 
> L1243:     `{
> L1244:       "name": "repo-policy",
> L1245:       "hooks": "./hooks/hooks.json"
> L1246:     }`
> L1247: Manifest hook paths are resolved relative to the plugin root and must stay inside that root. If a manifest defines `hooks`, Codex uses those manifest entries instead of the default `hooks/hooks.json`.
> L1248: 
> L1249: Plugin hook commands receive these environment variables:
> L1250:   * `PLUGIN_ROOT` is a Codex-specific extension that points to the installed plugin root.
> L1251:   * `PLUGIN_DATA` is a Codex-specific extension that points to the plugin’s writable data directory.
> L1252:   * Codex also sets `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility with existing plugin hooks.
> L1253: Plugin hooks use the same event schema as other hooks. Review and trust them before they run. In the CLI, open `/hooks`. In the desktop app, select Review hooks in the composer or open Settings > Hooks. If a plugin update changes a bundled script, Codex requires a new review even if the hook definition stays the same.
> L1254: ## Matcher patterns
> L1255: 
> L1256: The `matcher` field is a regex string that filters when hooks fire. Use `"*"`, `""`, or omit `matcher` entirely to match every occurrence of a supported event.
> L1257: 
> L1258: Only some current Codex events honor `matcher`:
> L1259: Event  | What `matcher` filters  | Notes
> L1260: --- | --- | ---
> L1261: `PermissionRequest`  | tool name  | Support includes `Bash`, `apply_patch`*, and MCP tool names
> L1262: `PostToolUse`  | tool name  | See 【557†Tool coverage】
> L1263: `PostCompact`  | compaction trigger  | Values are `manual` or `auto`
> L1264: `PreModelRequest`, `PostModelRequest`  | not supported  | Both events run for each model request attempt
> L1265: `PreCompact`  | compaction trigger  | Values are `manual` or `auto`
> L1266: `PreToolUse`  | tool name  | See 【557†Tool coverage】
> L1267: `SessionEnd`  | end reason  | Currently only `other`
> L1268: `SessionStart`  | start source  | Values are `startup`, `resume`, `clear`, `compact`, and `fork`
> L1269: `SubagentStart`  | subagent type  | Values depend on the subagent that starts
> L1270: `SubagentStop`  | subagent type  | Values depend on the subagent that stops
> L1271: `UserPromptSubmit`  | not supported  | Any configured `matcher` is ignored for this event
> L1272: `Stop`  | not supported  | Any configured `matcher` is ignored for this event
> L1357: ### Configure a background hook
> L1358: 
> L1359: Add `"async": true` to a command handler in `hooks.json`:
> L1360: 
> L1361:     `{
> L1362:       "hooks": {
> L1363:         "PostToolUse": [
> L1364:           {
> L1365:             "matcher": "Bash",
> L1366:             "hooks": [
> L1367:               {
> L1368:                 "type": "command",
> L1369:                 "command": "python3 ~/.codex/hooks/post_tool_use.py",
> L1370:                 "async": true,
> L1371:                 "timeout": 120
> L1372:               }
> L1373:             ]
> L1374:           }
> L1375:         ]
> L1376:       }
> L1377:     }`
> L1378: For an inline hook in `config.toml`, set `async = true`:
> L1379: 
> L1380:     `[[hooks.PostToolUse]]
> L1381:     matcher = "Bash"
> L1382: 
> L1383:     [[hooks.PostToolUse.hooks]]
> L1384:     type = "command"
> L1385:     command = "python3 ~/.codex/hooks/post_tool_use.py"
> L1386:     async = true
> L1387:     timeout = 120`
> L1388: Background hooks use the same input, matcher, trust review, timeout, and 【553†large-output handling】 as synchronous command hooks. As with other command hooks, `timeout` is measured in seconds and defaults to `600`. `Interrupt` hooks use a one-second default and a three-second maximum, including when they run in the background.
>
> --------------------------------------------------------------------------------
> Third Party Hooks | Cursor Docs (https://prod.cursor.com/docs/reference/third-party-hooks)
> 【turn384692view2】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://prod.cursor.com/docs/reference/third-party-hooks","pattern":"Read"}); Total lines: 546
> L193: Claude Code Event  | Cursor Mapping  | Supported
> L194: --- | --- | ---
> L195: `PreToolUse`  | `preToolUse`  | Yes
> L196: `PostToolUse`  | `postToolUse`  | Yes
> L197: `Stop`  | `stop`  | Yes
> L198: `SubagentStop`  | `subagentStop`  | Yes
> L199: `SessionStart`  | `sessionStart`  | Yes
> L200: `SessionEnd`  | `sessionEnd`  | Yes
> L201: `PreCompact`  | `preCompact`  | Yes
> L202: `UserPromptSubmit`  | `beforeSubmitPrompt`  | Yes
> L203: `Notification`  | -  | No
> L204: `PermissionRequest`  | -  | No
> L205: 
> L206: Additional supported features:
> L207: Feature  | Supported
> L208: --- | ---
> L209: Command-based hooks (`type: "command"`)  | Yes
> L210: Prompt-based hooks (`type: "prompt"`)  | Yes
> L211: Nested `hookSpecificOutput` responses  | Yes
> L212: Exit code 2 blocking  | Yes
> L213: Tool matchers (regex patterns)  | Yes
> L214: Timeout configuration  | Yes
> L215: ### 【88†Tool Name Mapping】
> L216: 
> L217: Claude Code tool names are mapped to Cursor tool names:
> L218: 
> L219: Claude Code Tool  | Cursor Tool  | Supported
> L220: --- | --- | ---
> L221: `Bash`  | `Shell`  | Yes
> L222: `Read`  | `Read`  | Yes
> L223: `Write`  | `Write`  | Yes
> L224: `Edit`  | `Write`  | Yes
> L225: `Grep`  | `Grep`  | Yes
> L226: `Task`  | `Task`  | Yes
> L227: `WebFetch`  | `WebFetch`  | Yes
> L228: `WebSearch`  | `WebSearch`  | Yes
> L229: `Glob`  | -  | No
> L230: ### 【89†Limitations】
> L231: 
> L232: Some features are only available when using the native Cursor format:
> L233: 
> L234:   * `subagentStart` hook (Claude Code only has `SubagentStop`)
> L235:   * Loop limit configuration (`loop_limit`)
> L236:   * Team/Enterprise hook distribution via dashboard
> L237: ## 【90†Troubleshooting】
> L238: 
> L239: Claude Code hooks not loading
> L240: 
> L241:   1. Verify "Include Third-Party Plugins, Skills, and Other Configs" is enabled in Cursor Settings → Agents → Third-Party Imports
> L242:   2. Check that your `.claude/settings.json` file is valid JSON
> L243:   3. Cursor watches config files and reloads them automatically. If hooks still do not load, restart Cursor.
> L244: 
> L245: Hooks running but not blocking
> L246:   1. Ensure your hook script exits with code `2` to block actions
> L247:   2. Check the JSON output format matches the expected schema
> L248:   3. View the Hooks output channel in Cursor for error details
> L249: 
> L250: Different behavior between Cursor and Claude Code
> L251: 
> L252: Some behavior differences may exist due to different execution environments. Test your hooks in both tools to ensure compatibility.
> L253: 
> L254: Enterprise hook deployment
> L255: 
> L256: Use managed Enterprise hooks and team distribution from the dashboard.
> L257: 
> L258: 【79†Contact Sales†cursor.com】
> L465: Claude Code Event  | Cursor Mapping  | Supported
> L466: --- | --- | ---
> L467: `PreToolUse`  | `preToolUse`  | Yes
> L468: `PostToolUse`  | `postToolUse`  | Yes
> L469: `Stop`  | `stop`  | Yes
> L470: `SubagentStop`  | `subagentStop`  | Yes
> L471: `SessionStart`  | `sessionStart`  | Yes
> L472: `SessionEnd`  | `sessionEnd`  | Yes
> L473: `PreCompact`  | `preCompact`  | Yes
> L474: `UserPromptSubmit`  | `beforeSubmitPrompt`  | Yes
> L475: `Notification`  | -  | No
> L476: `PermissionRequest`  | -  | No
> L477: 
> L478: Additional supported features:
> L479: Feature  | Supported
> L480: --- | ---
> L481: Command-based hooks (`type: "command"`)  | Yes
> L482: Prompt-based hooks (`type: "prompt"`)  | Yes
> L483: Nested `hookSpecificOutput` responses  | Yes
> L484: Exit code 2 blocking  | Yes
> L485: Tool matchers (regex patterns)  | Yes
> L486: Timeout configuration  | Yes
> L487: ### 【88†Tool Name Mapping】
> L488: 
> L489: Claude Code tool names are mapped to Cursor tool names:
> L490: 
> L491: Claude Code Tool  | Cursor Tool  | Supported
> L492: --- | --- | ---
> L493: `Bash`  | `Shell`  | Yes
> L494: `Read`  | `Read`  | Yes
> L495: `Write`  | `Write`  | Yes
> L496: `Edit`  | `Write`  | Yes
> L497: `Grep`  | `Grep`  | Yes
> L498: `Task`  | `Task`  | Yes
> L499: `WebFetch`  | `WebFetch`  | Yes
> L500: `WebSearch`  | `WebSearch`  | Yes
> L501: `Glob`  | -  | No
> L502: ### 【89†Limitations】
> L503: 
> L504: Some features are only available when using the native Cursor format:
> L505: 
> L506:   * `subagentStart` hook (Claude Code only has `SubagentStop`)
> L507:   * Loop limit configuration (`loop_limit`)
> L508:   * Team/Enterprise hook distribution via dashboard
> L509: ## 【90†Troubleshooting】
> L510: 
> L511: Claude Code hooks not loading
> L512: 
> L513:   1. Verify "Include Third-Party Plugins, Skills, and Other Configs" is enabled in Cursor Settings → Agents → Third-Party Imports
> L514:   2. Check that your `.claude/settings.json` file is valid JSON
> L515:   3. Cursor watches config files and reloads them automatically. If hooks still do not load, restart Cursor.
> L516: 
> L517: Hooks running but not blocking
> L518:   1. Ensure your hook script exits with code `2` to block actions
> L519:   2. Check the JSON output format matches the expected schema
> L520:   3. View the Hooks output channel in Cursor for error details
> L521: 
> L522: Different behavior between Cursor and Claude Code
> L523: 
> L524: Some behavior differences may exist due to different execution environments. Test your hooks in both tools to ensure compatibility.
> L525: 
> L526: Enterprise hook deployment
> L527: 
> L528: Use managed Enterprise hooks and team distribution from the dashboard.
> L529: 
> L530: 【79†Contact Sales†cursor.com】
>
> --------------------------------------------------------------------------------
> Third Party Hooks | Cursor Docs (https://prod.cursor.com/docs/reference/third-party-hooks)
> 【turn384692view3】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://prod.cursor.com/docs/reference/third-party-hooks","pattern":"Unsupported"}); Total lines: 546
> No matching text found for "Unsupported"
> --------------------------------------------------------------------------------
> Hooks reference | Gemini CLI (https://geminicli.com/docs/hooks/reference/)
> 【turn384692view4】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://geminicli.com/docs/hooks/reference/","pattern":"Exit Code 2"}); Total lines: 571
> L360:   * Input Fields:
> L361:     * `tool_name`: (`string`) The name of the tool being called.
> L362:     * `tool_input`: (`object`) The raw arguments generated by the model.
> L363:     * `mcp_context`: (`object`) Optional metadata for MCP-based tools.
> L364:     * `original_request_name`: (`string`) The original name of the tool being called, if this is a tail tool call.
> L365:   * Relevant Output Fields:
> L366:     * `decision`: Set to `"deny"` (or `"block"`) to prevent the tool from executing.
> L367:     * `reason`: Required if denied. This text is sent to the agent as a tool error, allowing it to respond or retry.
> L368:     * `hookSpecificOutput.tool_input`: An object that merges with and overrides the model’s arguments before execution.
> L369:     * `continue`: Set to `false` to kill the entire agent loop immediately.
> L370:   * Exit Code 2 (Block Tool): Prevents execution. Uses `stderr` as the `reason` sent to the agent. The turn continues.
> L371: ### `AfterTool`
> L372: 
> L373: 【91†Section titled “AfterTool”】
> L374: 
> L375: Fires after a tool executes. Used for result auditing, context injection, or hiding sensitive output from the agent.
> L376:   * Input Fields:
> L377:     * `tool_name`: (`string`)
> L378:     * `tool_input`: (`object`) The original arguments.
> L379:     * `tool_response`: (`object`) The result containing `llmContent`, `returnDisplay`, and optional `error`.
> L380:     * `mcp_context`: (`object`)
> L381:     * `original_request_name`: (`string`) The original name of the tool being called, if this is a tail tool call.
> L382:   * Relevant Output Fields:
> L383:     * `decision`: Set to `"deny"` to hide the real tool output from the agent.
> L384:     * `reason`: Required if denied. This text replaces the tool result sent back to the model.
> L385:     * `hookSpecificOutput.additionalContext`: Text that is appended to the tool result for the agent.
> L386:     * `hookSpecificOutput.tailToolCallRequest`: (`{ name: string, args: object }`) A request to execute another tool immediately after this one. The result of this “tail call” will replace the original tool’s response. Ideal for programmatic tool routing.
> L387:     * `continue`: Set to `false` to kill the entire agent loop immediately.
> L388:   * Exit Code 2 (Block Result): Hides the tool result. Uses `stderr` as the replacement content sent to the agent. The turn continues.
> L389: * * *
> L390: ## Agent hooks
> L391: 
> L392: 【92†Section titled “Agent hooks”】
> L393: ### `BeforeAgent`
> L394: 
> L395: 【93†Section titled “BeforeAgent”】
> L396: 
> L397: Fires after a user submits a prompt, but before the agent begins planning. Used for prompt validation or injecting dynamic context.
> L398:   * Input Fields:
> L399:     * `prompt`: (`string`) The original text submitted by the user.
> L400:   * Relevant Output Fields:
> L401:     * `hookSpecificOutput.additionalContext`: Text that is appended to the prompt for this turn only.
> L402:     * `decision`: Set to `"deny"` to block the turn and discard the user’s message (it will not appear in history).
> L403:     * `continue`: Set to `false` to block the turn but save the message to history.
> L404:     * `reason`: Required if denied or stopped.
> L405:   * Exit Code 2 (Block Turn): Aborts the turn and erases the prompt from context. Same as `decision: "deny"`.
> L406: ### `AfterAgent`
> L407: 
> L408: 【94†Section titled “AfterAgent”】
> L409: 
> L410: Fires once per turn after the model generates its final response. Primary use case is response validation and automatic retries.
> L411:   * Input Fields:
> L412:     * `prompt`: (`string`) The user’s original request.
> L413:     * `prompt_response`: (`string`) The final text generated by the agent.
> L414:     * `stop_hook_active`: (`boolean`) Indicates if this hook is already running as part of a retry sequence.
> L415:   * Relevant Output Fields:
> L416:     * `decision`: Set to `"deny"` to reject the response and force a retry.
> L417:     * `reason`: Required if denied. This text is sent to the agent as a new prompt to request a correction.
> L418:     * `continue`: Set to `false` to stop the session without retrying.
> L419:     * `hookSpecificOutput.clearContext`: If `true`, clears conversation history (LLM memory) while preserving UI display.
> L420:   * Exit Code 2 (Retry): Rejects the response and triggers an automatic retry turn using `stderr` as the feedback prompt.
> L421: * * *
> L422: ## Model hooks
> L423: 
> L424: 【95†Section titled “Model hooks”】
> L425: ### `BeforeModel`
> L426: 
> L427: 【96†Section titled “BeforeModel”】
> L428: 
> L429: Fires before sending a request to the LLM. Operates on a stable, SDK-agnostic request format.
> L430:   * Input Fields:
> L431:     * `llm_request`: (`object`) Contains `model`, `messages`, and `config` (generation params).
> L432:   * Relevant Output Fields:
> L433:     * `hookSpecificOutput.llm_request`: An object that overrides parts of the outgoing request (for example, changing models or temperature).
> L434:     * `hookSpecificOutput.llm_response`: A Synthetic Response object. If provided, the CLI skips the LLM call entirely and uses this as the response.
> L435:     * `decision`: Set to `"deny"` to block the request and abort the turn.
> L436:   * Exit Code 2 (Block Turn): Aborts the turn and skips the LLM call. Uses `stderr` as the error message.
> L437: ### `BeforeToolSelection`
> L438: 
> L439: 【97†Section titled “BeforeToolSelection”】
> L440: 
> L441: Fires before the LLM decides which tools to call. Used to filter the available toolset or force specific tool modes.
> L442:   * Input Fields:
> L443:     * `llm_request`: (`object`) Same format as `BeforeModel`.
> L444:   * Relevant Output Fields:
> L445:     * `hookSpecificOutput.toolConfig.mode`: (`"AUTO" | "ANY" | "NONE"`)
> L446:       * `"NONE"`: Disables all tools (Wins over other hooks).
> L447:       * `"ANY"`: Forces at least one tool call.
> L448:     * `hookSpecificOutput.toolConfig.allowedFunctionNames`: (`string[]`) Whitelist of tool names.
> L449:   * Union Strategy: Multiple hooks’ whitelists are combined.
> L450:   * Limitations: Does not support `decision`, `continue`, or `systemMessage`.
> L451: ### `AfterModel`
> L452: 
> L453: 【98†Section titled “AfterModel”】
> L454: 
> L455: Fires immediately after an LLM response chunk is received. Used for real-time redaction or PII filtering.
> L456:   * Input Fields:
> L457:     * `llm_request`: (`object`) The original request.
> L458:     * `llm_response`: (`object`) The model’s response (or a single chunk during streaming).
> L459:   * Relevant Output Fields:
> L460:     * `hookSpecificOutput.llm_response`: An object that replaces the model’s response chunk.
> L461:     * `decision`: Set to `"deny"` to discard the response chunk and block the turn.
> L462:     * `continue`: Set to `false` to kill the entire agent loop immediately.
> L463:   * Note on Streaming: Fired for every chunk generated by the model. Modifying the response only affects the current chunk.
> L464:   * Exit Code 2 (Block Response): Aborts the turn and discards the model’s output. Uses `stderr` as the error message.
> L465: * * *
> L466: ## Lifecycle & system hooks
> L467: 
> L468: 【99†Section titled “Lifecycle & system hooks”】
> L469: ### `SessionStart`
> L470: 
> L471: 【100†Section titled “SessionStart”】
> L472: 
> L473: Fires on application startup, resuming a session, or after a `/clear` command. Used for loading initial context.
> L474:   * Input fields:
> L475:     * `source`: (`"startup" | "resume" | "clear"`)
> L476:   * Relevant output fields:
> L477:     * `hookSpecificOutput.additionalContext`: (`string`)
> L478:       * Interactive: Injected as the first turn in history.
> L479:       * Non-interactive: Prepended to the user’s prompt.
> L480:     * `systemMessage`: Shown at the start of the session.
> L481:   * Advisory only: `continue` and `decision` fields are ignored. Startup is never blocked.
> L482: ### `SessionEnd`
> L483: 
> L484: 【101†Section titled “SessionEnd”】
> L485: 
> L486: Fires when the CLI exits or a session is cleared. Used for cleanup or final telemetry.
> L487: 
> L488:   * Input Fields:
> L489:     * `reason`: (`"exit" | "clear" | "logout" | "prompt_input_exit" | "other"`)
> L490:   * Relevant Output Fields:
> L491:     * `systemMessage`: Displayed to the user during shutdown.
> L492:   * Best Effort: The CLI will not wait for this hook to complete and ignores all flow-control fields (`continue`, `decision`).
> L493: ### `Notification`
> L494: 
> L495: 【102†Section titled “Notification”】
> L496: 
> L497: Fires when the CLI emits a system alert (for example, Tool Permissions). Used for external logging or cross-platform alerts.
> L498:   * Input Fields:
> L499:     * `notification_type`: (`"ToolPermission"`)
> L500:     * `message`: Summary of the alert.
> L501:     * `details`: JSON object with alert-specific metadata (for example, tool name, file path).
> L502:   * Relevant Output Fields:
> L503:     * `systemMessage`: Displayed alongside the system alert.
> L504:   * Observability Only: This hook cannot block alerts or grant permissions automatically. Flow-control fields are ignored.
> ```
>
> - Ran `codex features list 2>/dev/null | rg -n 'hook|trust'`
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "find": [
>     {
>       "pattern": "Tool coverage",
>       "ref_id": "https://learn.chatgpt.com/docs/hooks"
>     },
>     {
>       "pattern": "unsupported fields",
>       "ref_id": "https://learn.chatgpt.com/docs/hooks"
>     },
>     {
>       "pattern": "stop_hook_active",
>       "ref_id": "https://code.claude.com/docs/en/hooks"
>     },
>     {
>       "pattern": "failClosed",
>       "ref_id": "https://code.claude.com/docs/en/hooks"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ```text
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks)
> 【turn139358view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://learn.chatgpt.com/docs/hooks","pattern":"Tool coverage"}); Total lines: 1748
> L1250:   * `PLUGIN_ROOT` is a Codex-specific extension that points to the installed plugin root.
> L1251:   * `PLUGIN_DATA` is a Codex-specific extension that points to the plugin’s writable data directory.
> L1252:   * Codex also sets `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility with existing plugin hooks.
> L1253: Plugin hooks use the same event schema as other hooks. Review and trust them before they run. In the CLI, open `/hooks`. In the desktop app, select Review hooks in the composer or open Settings > Hooks. If a plugin update changes a bundled script, Codex requires a new review even if the hook definition stays the same.
> L1254: ## Matcher patterns
> L1255: 
> L1256: The `matcher` field is a regex string that filters when hooks fire. Use `"*"`, `""`, or omit `matcher` entirely to match every occurrence of a supported event.
> L1257: 
> L1258: Only some current Codex events honor `matcher`:
> L1259: Event  | What `matcher` filters  | Notes
> L1260: --- | --- | ---
> L1261: `PermissionRequest`  | tool name  | Support includes `Bash`, `apply_patch`*, and MCP tool names
> L1262: `PostToolUse`  | tool name  | See 【557†Tool coverage】
> L1263: `PostCompact`  | compaction trigger  | Values are `manual` or `auto`
> L1264: `PreModelRequest`, `PostModelRequest`  | not supported  | Both events run for each model request attempt
> L1265: `PreCompact`  | compaction trigger  | Values are `manual` or `auto`
> L1266: `PreToolUse`  | tool name  | See 【557†Tool coverage】
> L1267: `SessionEnd`  | end reason  | Currently only `other`
> L1268: `SessionStart`  | start source  | Values are `startup`, `resume`, `clear`, `compact`, and `fork`
> L1269: `SubagentStart`  | subagent type  | Values depend on the subagent that starts
> L1270: `SubagentStop`  | subagent type  | Values depend on the subagent that stops
> L1271: `UserPromptSubmit`  | not supported  | Any configured `matcher` is ignored for this event
> L1272: `Stop`  | not supported  | Any configured `matcher` is ignored for this event
> L1273: `Interrupt`  | not supported  | Any configured `matcher` is ignored for this event
> L1274: *For `apply_patch`, `matcher` values can also use `Edit` or `Write`.
> L1275: 
> L1276: Examples:
> L1277: 
> L1278:   * `Bash`
> L1279:   * `^apply_patch$`
> L1280:   * `Edit|Write`
> L1281:   * `mcp__filesystem__read_file`
> L1282:   * `mcp__filesystem__.*`
> L1283:   * `startup|resume|clear|compact|fork`
> L1284:   * `manual|auto`
> L1285: ### Tool coverage
> L1286: 
> L1287: `PreToolUse` and `PostToolUse` can observe more than shell and MCP calls. Most local function tools use the same hook path, so you can match their tool name, inspect their JSON arguments, and, for `PreToolUse`, block or rewrite the call.
> L1288: Tool path  | `PreToolUse`  | `PostToolUse`  | Notes
> L1289: --- | --- | --- | ---
> L1290: Shell commands  | Yes  | Yes  | Match as `Bash`.
> L1291: Unified exec (`exec_command`)  | Yes  | Yes  | Match as `Bash`. A later `write_stdin` poll can deliver the original command’s `PostToolUse` when that command finishes.
> L1292: `apply_patch`  | Yes  | Yes  | Match as `apply_patch`, `Edit`, or `Write`.
> L1293: MCP tools  | Yes  | Yes  | Match the MCP tool name, such as `mcp__filesystem__read_file`.
> L1294: Other local function tools  | Yes  | Yes  | Match the function tool name, such as `update_plan`. `spawn_agent` also matches `Agent`.
> L1295: Hosted tools, such as `WebSearch`  | No  | No  | These don’t use the local function-tool hook path.
> L1296: `write_stdin` is transport for an existing unified-exec session. It doesn’t run `PreToolUse` again when it sends input or polls a command that already passed `PreToolUse`.
> L1297: 
> L1298: Some specialized tool paths can opt out of the default hook path. Treat tool hooks as a useful guardrail, not a complete enforcement boundary.
> L1299: ## Common input fields
> L1300: 
> L1301: Every command hook receives one JSON object on `stdin`.
> L1302: 
> L1303: These are the shared fields you will usually use:
> L1304: Field  | Type  | Meaning
> L1305: --- | --- | ---
> L1306: `session_id`  | `string`  | Current Codex session id. Subagent hooks use the parent session id.
> L1307: `transcript_path`  | `string | null`  | Path to the session transcript file, if any
> L1308: `cwd`  | `string`  | Working directory for the session
> L1309: `hook_event_name`  | `string`  | Current hook event name
> L1310: `model`  | `string`  | Codex-specific extension. Active model slug
> L1311: 
> L1312: Turn-scoped hooks list `turn_id` as a Codex-specific extension in their event-specific tables.
> L1313: `SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, and `Interrupt` also include `permission_mode`, which describes the current permission mode as `default`, `acceptEdits`, `plan`, `dontAsk`, or `bypassPermissions`.
> L1314: 
> L1315: `transcript_path` points to a chat transcript for convenience, but the transcript format isn’t a stable interface for hooks and may change over time.
> L1316: 
> L1317: If you need the full wire format, see 【558†Schemas】.
> L1318: ## Common output fields
> L1319: 
> L1320: `SessionStart`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, and `Stop` support these shared JSON fields. `SubagentStart` accepts the same shape for `systemMessage` and hook-specific context, but `continue: false` doesn’t stop the subagent:
> L1321: 
> L1322:     `{
> L1323:       "continue": true,
> L1324:       "stopReason": "optional",
> L1325:       "systemMessage": "optional",
> L1326:       "suppressOutput": false
> L1327:     }`
> L1467: JSON on `stdout` supports `systemMessage` and this hook-specific shape:
> L1468: 
> L1469:     `{
> L1470:       "hookSpecificOutput": {
> L1471:         "hookEventName": "SubagentStart",
> L1472:         "additionalContext": "Review the repository test conventions first."
> L1473:       }
> L1474:     }`
> L1475: 
> L1476: That `additionalContext` text is added as extra developer context for the subagent. `continue: false` is parsed for compatibility, but it doesn’t stop the subagent from starting.
> L1477: ### PreToolUse
> L1478: 
> L1479: `PreToolUse` can intercept Bash, file edits performed through `apply_patch`, MCP tool calls, and other local function tools. See 【557†Tool coverage】 for the supported paths and exceptions.
> L1480: 
> L1481: `matcher` is applied to `tool_name` and matcher aliases. For file edits through `apply_patch`, `matcher` values can use `apply_patch`, `Edit`, or `Write`; hook input still reports `tool_name: "apply_patch"`.
> L1482: 
> L1483: Fields in addition to 【559†Common input fields】:
> L1484: Field  | Type  | Meaning
> L1485: --- | --- | ---
> L1486: `turn_id`  | `string`  | Codex-specific extension. Active Codex turn id
> L1487: `tool_name`  | `string`  | Canonical hook tool name, such as `Bash`, `apply_patch`, or an MCP name like `mcp__fs__read`
> L1488: `tool_use_id`  | `string`  | Tool-call id for this invocation
> L1489: `tool_input`  | `JSON value`  | Tool-specific input. `Bash` and `apply_patch` use `tool_input.command`. MCP and other local function tools send their arguments.
> L1490: 
> L1491: Plain text on `stdout` is ignored.
> L1492: JSON on `stdout` can use `systemMessage`. To deny a supported tool call, return this hook-specific shape:
> L1493: 
> L1494:     `{
> L1495:       "hookSpecificOutput": {
> L1496:         "hookEventName": "PreToolUse",
> L1497:         "permissionDecision": "deny",
> L1498:         "permissionDecisionReason": "Destructive command blocked by hook."
> L1499:       }
> L1500:     }`
> L1501: 
> L1502: Codex also accepts this older block shape:
> L1503: 
> L1504:     `{
> L1505:       "decision": "block",
> L1506:       "reason": "Destructive command blocked by hook."
> L1507:     }`
> L1508: You can also use exit code `2` and write the blocking reason to `stderr`.
> L1509: 
> L1510: To add model-visible context without blocking, return `hookSpecificOutput.additionalContext`:
> L1511: 
> L1512:     `{
> L1513:       "hookSpecificOutput": {
> L1514:         "hookEventName": "PreToolUse",
> L1515:         "additionalContext": "The pending command touches generated files."
> L1516:       }
> L1517:     }`
> L1518: To rewrite a supported tool call without blocking, return `permissionDecision: "allow"` with `updatedInput`:
> L1519: 
> L1520:     `{
> L1521:       "hookSpecificOutput": {
> L1522:         "hookEventName": "PreToolUse",
> L1523:         "permissionDecision": "allow",
> L1524:         "updatedInput": {
> L1537: Field  | Type  | Meaning
> L1538: --- | --- | ---
> L1539: `turn_id`  | `string`  | Codex-specific extension. Active Codex turn id
> L1540: `tool_name`  | `string`  | Canonical hook tool name, such as `Bash`, `apply_patch`, or an MCP name like `mcp__fs__read`
> L1541: `tool_input`  | `JSON value`  | Tool-specific input. `Bash` and `apply_patch` use `tool_input.command` while MCP tools send all the arguments.
> L1542: `tool_input.description`  | `string | null`  | Human-readable approval reason, when Codex has one
> L1543: 
> L1544: Plain text on `stdout` is ignored.
> L1545: Some tool inputs may include a human-readable description, but don’t rely on a `tool_input.description` field for every tool.
> L1546: 
> L1547: To approve the request, return:
> L1548: 
> L1549:     `{
> L1550:       "hookSpecificOutput": {
> L1551:         "hookEventName": "PermissionRequest",
> L1552:         "decision": {
> L1553:           "behavior": "allow"
> L1554:         }
> L1555:       }
> L1556:     }`
> L1557: To deny the request, return:
> L1558: 
> L1559:     `{
> L1560:       "hookSpecificOutput": {
> L1561:         "hookEventName": "PermissionRequest",
> L1562:         "decision": {
> L1563:           "behavior": "deny",
> L1564:           "message": "Blocked by repository policy."
> L1565:         }
> L1566:       }
> L1567:     }`
> L1568: 
> L1569: If multiple matching hooks return decisions, any `deny` wins. Otherwise, an `allow` lets the request proceed without surfacing the approval prompt. If no matching hook decides, Codex uses the normal approval flow.
> L1570: Don’t return `updatedInput`, `updatedPermissions`, or `interrupt` for `PermissionRequest`; those fields are reserved for future behavior and fail closed today.
> L1571: ### PostToolUse
> L1572: 
> L1573: `PostToolUse` runs after supported tools produce output, including Bash, `apply_patch`, MCP tool calls, and other local function tools. For Bash, it also runs after commands that exit with a non-zero status. It can’t undo side effects from a tool that already ran. See 【557†Tool coverage】 for the supported paths and exceptions.
> L1574: `matcher` is applied to `tool_name` and matcher aliases. For file edits through `apply_patch`, `matcher` values can use `apply_patch`, `Edit`, or `Write`; hook input still reports `tool_name: "apply_patch"`.
> L1575: 
> L1576: Fields in addition to 【559†Common input fields】:
> L1577: Field  | Type  | Meaning
> L1578: --- | --- | ---
> L1579: `turn_id`  | `string`  | Codex-specific extension. Active Codex turn id
> L1580: `tool_name`  | `string`  | Canonical hook tool name, such as `Bash`, `apply_patch`, or an MCP name like `mcp__fs__read`
> L1581: `tool_use_id`  | `string`  | Tool-call id for this invocation
> L1582: `tool_input`  | `JSON value`  | Tool-specific input. `Bash` and `apply_patch` use `tool_input.command`. MCP and other local function tools send their arguments.
> L1583: `tool_response`  | `JSON value`  | Tool-specific output. MCP tools send the MCP call result. Other local function tools normally send their model-facing output.
> L1584: Plain text on `stdout` is ignored.
> L1585: 
> L1586: JSON on `stdout` can use `systemMessage` and this hook-specific shape:
> L1587: 
> L1588:     `{
> L1589:       "decision": "block",
> L1590:       "reason": "The Bash output needs review before continuing.",
> L1591:       "hookSpecificOutput": {
> L1592:         "hookEventName": "PostToolUse",
> L1593:         "additionalContext": "The command updated generated files."
> L1594:       }
> L1595:     }`
> L1596: 
> L1597: That `additionalContext` text is added as extra developer context.
> L1598: For this event, `decision: "block"` doesn’t undo the completed Bash command. Instead, Codex records the feedback, replaces the tool result with that feedback, and continues the model from the hook-provided message.
> L1599: 
> L1600: You can also use exit code `2` and write the feedback reason to `stderr`.
> L1601: 
> L1602: To stop normal processing of the original tool result after the command has already run, return `continue: false`. Codex will replace the tool result with your feedback or stop text and continue from there.
>
> --------------------------------------------------------------------------------
> Hooks | ChatGPT Learn (https://learn.chatgpt.com/docs/hooks)
> 【turn139358view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://learn.chatgpt.com/docs/hooks","pattern":"unsupported fields"}); Total lines: 1748
> L1318: ## Common output fields
> L1319: 
> L1320: `SessionStart`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, and `Stop` support these shared JSON fields. `SubagentStart` accepts the same shape for `systemMessage` and hook-specific context, but `continue: false` doesn’t stop the subagent:
> L1321: 
> L1322:     `{
> L1323:       "continue": true,
> L1324:       "stopReason": "optional",
> L1325:       "systemMessage": "optional",
> L1326:       "suppressOutput": false
> L1327:     }`
> L1328: Field  | Effect
> L1329: --- | ---
> L1330: `continue`  | If `false`, marks that hook run as stopped
> L1331: `stopReason`  | Recorded as the reason for stopping
> L1332: `systemMessage`  | Surfaced as a warning in the UI or event stream
> L1333: `suppressOutput`  | Parsed today but not yet implemented
> L1334: 
> L1335: Exit `0` with no output is treated as success and Codex continues.
> L1336: `PreToolUse` and `PermissionRequest` support `systemMessage`, but `continue`, `stopReason`, and `suppressOutput` aren’t currently supported for those events. If a `PreToolUse` hook returns one of those unsupported fields, Codex marks that hook run as failed, reports the error, and continues the tool call.
> L1337: 
> L1338: `PostToolUse` supports `systemMessage`, `continue: false`, and `stopReason`. `suppressOutput` is parsed but not currently supported for that event.
> L1339: ### Large hook output
> L1340: 
> L1341: By default, Codex limits each model-visible hook-output message to roughly 2,500 tokens. If a hook returns more, Codex saves the full text under `<temp_dir>/hook_outputs/<session_id>/<uuid>.txt` and gives the model a head-and-tail preview with the saved-file path. This behavior is called spilling: Codex stores oversized output on disk and replaces it with a shorter, model-visible preview. If the file can’t be written, the model still receives a truncated preview.
> L1342: Keep hook and plugin context concise. Context from multiple hooks and plugins adds up and can degrade model performance. Raising `additionalContextLimit` increases that risk. Avoid setting the limit to `0` unless the hook enforces a strict output cap; otherwise, a single hook can consume the entire context window.
> L1343: For any command hook that returns `additionalContext`, set `additionalContextLimit` on the handler to customize the approximate token threshold:
> L1344: 
> L1345:     `{
> L1346:       "type": "command",
> L1347:       "command": "python3 ~/.codex/hooks/session_start.py",
> L1348:       "additionalContextLimit": 5000
> L1349:     }`
> L1350: Omit `additionalContextLimit` to use the default `2500`-token threshold. Use a positive integer to select a different threshold, or `0` to pass the handler’s complete additional context directly to the model. Codex evaluates each matching handler independently. For events that can’t produce additional context, Codex ignores `additionalContextLimit` and reports a configuration warning.
> L1351: 
> L1352: The setting applies only to `additionalContext`. Tool feedback and continuation prompts keep the default limit.
>
> --------------------------------------------------------------------------------
> Hooks reference - Claude Code Docs (https://code.claude.com/docs/en/hooks)
> 【turn139358view2】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://code.claude.com/docs/en/hooks","pattern":"stop_hook_active"}); Total lines: 4119
> L2532: ###
> L2533: 
> L2534: 【93†​】
> L2535: 
> L2536: SubagentStop
> L2537: 
> L2538: Runs when a Claude Code subagent has finished responding. Matches on agent type, same values as SubagentStart.
> L2539: ####
> L2540: 
> L2541: 【94†​】
> L2542: 
> L2543: SubagentStop input
> L2544: In addition to the 【24†common input fields】, SubagentStop hooks receive `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, and `last_assistant_message`. The `agent_type` field is the value used for matcher filtering. The `transcript_path` is the main session’s transcript, while `agent_transcript_path` is the subagent’s own transcript stored in a nested `subagents/` folder.
> L2545: The `last_assistant_message` field contains the text content of the subagent’s final response, so hooks can access it without parsing the transcript file. Not every SubagentStop event comes from a subagent Claude spawned. Claude Code also runs internal agents for some of its own features, such as 【319†prompt suggestions】 and 【320†`/btw` side questions】, and SubagentStop fires when one of those finishes too.
> L2546: For those events, `agent_type` is the agent name the session itself runs as, such as one set with 【297†`--agent`】 or the 【321†`agent` setting】, and an empty string when the session runs without one. A `matcher` that names agent types doesn’t match an empty `agent_type`. A hook whose matcher is omitted, `""`, or `"*"`, or is a regular expression that matches an empty string, runs for events with an empty `agent_type` too.
> L2547: On Claude Code v2.1.271 or later, a subagent that runs with the 【277†`SubagentHandback`】 tool delivers its report through that tool before it stops. The `last_assistant_message` field then holds the subagent’s closing text, if any, which is not the delivered report. The report is that call’s `message` input, which a `PreToolUse` or `PostToolUse` hook matched on `SubagentHandback` receives as `tool_input.message`.
> L2548: SubagentStop hooks also receive the `background_tasks` and `session_crons` arrays described under 【102†Stop input】. Both arrays are scoped to the parent session, not the subagent.
> L2549: 
> L2550:     `{
> L2551:       "session_id": "abc123",
> L2552:       "transcript_path": "~/.claude/projects/.../abc123.jsonl",
> L2553:       "cwd": "/Users/...",
> L2554:       "permission_mode": "default",
> L2555:       "hook_event_name": "SubagentStop",
> L2556:       "stop_hook_active": false,
> L2557:       "agent_id": "def456",
> L2558:       "agent_type": "Explore",
> L2559:       "agent_transcript_path": "~/.claude/projects/.../abc123/subagents/agent-def456.jsonl",
> L2560:       "last_assistant_message": "Analysis complete. Found 3 potential issues...",
> L2561:       "background_tasks": [],
> L2562:       "session_crons": []
> L2563:     }
> L2564:     `
> L2565: SubagentStop hooks use the same decision control format as 【103†Stop hooks】, including `hookSpecificOutput.additionalContext` with `hookEventName` set to `"SubagentStop"`, for non-error feedback that keeps the subagent running. Returning `decision: "block"` with a `reason` keeps the subagent running and delivers `reason` to the subagent as its next instruction. A hook that blocks by exiting 2 delivers its stderr message the same way.
> L2566: To inject context into the parent session after a subagent returns, use a 【75†`PostToolUse`】 hook on the `Agent` tool instead.
> L2567: ###
> L2568: 
> L2569: 【95†​】
> L2570: 
> L2571: TaskCreated
> L2572: 
> L2573: Runs when a task is being created via the `TaskCreate` tool. Use this to enforce naming conventions, require task descriptions, or prevent certain tasks from being created. In a 【322†session without the Task tools】, this event doesn’t fire. TaskCreated hooks don’t support matchers and fire on every occurrence.
> L2574: ####
> L2575: 
> L2576: 【96†​】
> L2577: 
> L2578: TaskCreated input
> L2579: In addition to the 【24†common input fields】, TaskCreated hooks receive `task_id`, `task_subject`, and optionally `task_description`, `teammate_name`, and `team_name`.
> L2580: 
> L2581:     `{
> L2582:       "session_id": "abc123",
> L2583:       "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
> L2584:       "cwd": "/Users/...",
> L2585:       "hook_event_name": "TaskCreated",
> L2586:       "task_id": "task-001",
> L2587:       "task_subject": "Implement user authentication",
> L2665:   * Exit code 2: the task is not marked as completed and the stderr message is fed back to the model as feedback.
> L2666:   * JSON `{"continue": false, "stopReason": "..."}`: when a teammate finishing its turn triggered the event, stops the teammate entirely, matching `Stop` hook behavior. The `stopReason` is shown to the user. When the `TaskUpdate` tool triggered the event, Claude Code ignores `continue: false`; exit code 2 still blocks the completion.
> L2667: This example runs tests and blocks task completion if they fail:
> L2668: 
> L2669:     `#!/bin/bash
> L2670:     INPUT=$(cat)
> L2671:     TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')
> L2672: 
> L2673:     # Run the test suite
> L2674:     if ! npm test 2>&1; then
> L2675:       echo "Tests not passing. Fix failing tests before completing: $TASK_SUBJECT" >&2
> L2676:       exit 2
> L2677:     fi
> L2678: 
> L2679:     exit 0
> L2680:     `
> L2681: ###
> L2682: 
> L2683: 【101†​】
> L2684: 
> L2685: Stop
> L2686: 
> L2687: Runs when the main Claude Code agent has finished responding. Does not run if the stoppage occurred due to a user interrupt. API errors fire 【104†StopFailure】 instead.
> L2688: 
> L2689: The 【323†`/goal`】 command is a built-in shortcut for a session-scoped prompt-based Stop hook. Use it when you want Claude to keep working toward a condition without writing hook configuration.
> L2690: ####
> L2691: 
> L2692: 【102†​】
> L2693: 
> L2694: Stop input
> L2695: In addition to the 【24†common input fields】, Stop hooks receive `stop_hook_active`, `last_assistant_message`, `background_tasks`, and `session_crons`. The `stop_hook_active` field is `true` when Claude Code is already continuing as a result of a stop hook. Check this value or process the transcript to avoid blocking on a condition that will never resolve.
> L2696: Claude Code applies an 8-consecutive-continuation cap: after stop hooks have continued the turn eight times in a row, Claude Code overrides the next block and ends the turn. The count of consecutive continuations resets each time Claude calls a tool. To raise the cap, set 【202†`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`】. The `last_assistant_message` field contains the text content of Claude’s final response, so hooks can access it without parsing the transcript file.
> L2697: For hooks that act on the just-completed turn, such as read-aloud or notification hooks, use this field rather than reading `transcript_path`: the transcript file isn’t guaranteed to include the final message at Stop time on all versions. The `background_tasks` and `session_crons` arrays let hooks distinguish “session is done” from “session is paused waiting for background work to wake it back up”.
> L2698: Both arrays are present when the task registry is reachable and are empty when nothing is in flight or scheduled. Each entry in `background_tasks` describes one in-flight task and uses these fields:
> L2699: Field  | Description
> L2700: --- | ---
> L2701: `id`  | Task identifier
> L2702: `type`  | Friendly task-type label such as `shell`, `subagent`, `monitor`, `workflow`, `teammate`, `cloud session`, or `MCP task`. Each label identifies which Claude Code feature created the task. Falls back to the raw discriminant for unrecognized types
> L2703: `status`  | Current task status
> L2704: `description`  | Free-text description, capped at 1000 characters with an in-string `… [+N chars]` marker when clipped
> L2705: `command`  | Shell command line, capped at 1000 characters. Present only for `shell` tasks
> L2706: `agent_type`  | Subagent type name. Present only for `subagent` tasks
> L2707: `server`  | MCP server name. Present only for `monitor` and `MCP task` tasks
> L2708: `tool`  | MCP tool name. Present only for `monitor` and `MCP task` tasks
> L2709: `name`  | Workflow name. Present only for `workflow` tasks
> L2710: Each entry in `session_crons` describes one session-scoped scheduled wakeup, sourced from `CronCreate`, `ScheduleWakeup`, and `/loop`:
> L2711: 
> L2712: Field  | Description
> L2713: --- | ---
> L2714: `id`  | Cron task identifier
> L2715: `schedule`  | Cron expression, for example `0 9 * * 1-5`
> L2716: `recurring`  | `false` for one-shot wakeups whose schedule encodes a single fire time, `true` for tasks that re-fire on every match
> L2717: `prompt`  | Prompt submitted when the cron fires, capped at 1000 characters with the same `… [+N chars]` marker
> L2718: This example shows a Stop input with one in-flight shell task and one recurring cron:
> L2719: 
> L2720:     `{
> L2721:       "session_id": "abc123",
> L2722:       "transcript_path": "~/.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
> L2723:       "cwd": "/Users/...",
> L2724:       "permission_mode": "default",
> L2725:       "hook_event_name": "Stop",
> L2726:       "stop_hook_active": true,
> L2727:       "last_assistant_message": "I've completed the refactoring. Here's a summary...",
> L2728:       "background_tasks": [
> L2729:         {
> L2730:           "id": "task-001",
> L2731:           "type": "shell",
> L2732:           "status": "running",
> L2733:           "description": "tail logs",
> L2734:           "command": "tail -f /var/log/syslog"
> L2735:         }
> L2736:       ],
> L2737:       "session_crons": [
> L2738:         {
> L2739:           "id": "cron-001",
> L2740:           "schedule": "0 9 * * 1-5",
> L2741:           "recurring": true,
> L2742:           "prompt": "check the build"
> L2743:         }
> L2744:       ]
> L2745:     }
> L2746:     `
> L2747: ####
> L2748: 
> L2749: 【103†​】
> L2750: 
> L2751: Stop decision control
> L2752: 
> L2753: `Stop` and `SubagentStop` hooks can control whether Claude continues. In addition to the 【36†JSON output fields】 available to all hooks, your hook script can return these event-specific fields:
> L2754: Field  | Description
> L2755: --- | ---
> L2756: `decision`  | `"block"` prevents Claude from stopping. Omit to allow Claude to stop
> L2757: `reason`  | Required when `decision` is `"block"`. Tells Claude why it should continue
> L2758: `hookSpecificOutput.additionalContext`  | Non-error feedback for Claude. The conversation continues so Claude can act on it, but unlike `decision: "block"` it is shown in the transcript as hook feedback rather than a hook error
> L2759: A hook that blocks by exiting 2 routes the same way as `reason`: Claude receives the stderr message as the explanation for why it should continue.
> L2760: 
> L2761:     `{
> L2762:       "decision": "block",
> L2763:       "reason": "Must be provided when Claude is blocked from stopping"
> L2764:     }
> L2765:     `
> L2766: Use `additionalContext` when the hook is working as designed and giving Claude guidance, such as “run the test suite before finishing”. It keeps the conversation going through the same loop protections as `decision: "block"`, namely the `stop_hook_active` input and the 8-consecutive-continuation cap, but the transcript labels it `Stop hook feedback` and no hook error notification is shown:
> L2767: 
> L2768:     `{
> L2769:       "hookSpecificOutput": {
> L2770:         "hookEventName": "Stop",
> L2771:         "additionalContext": "Please run the test suite before finishing"
> L2772:       }
> L2773:     }
> L2774:     `
> L2775: ###
> L2776: 
> L2777: 【104†​】
> L2778: 
> L2779: StopFailure
> L2780: 
> L2781: Runs instead of 【101†Stop】 when the turn ends due to an API error. Claude Code ignores the hook’s output and exit code, apart from 【37†`terminalSequence`】. Use this to log failures, send alerts, or take recovery actions when Claude can’t complete a response due to rate limits, authentication problems, or other API errors.
> L2782: ####
> L2783: 
> L2784: 【105†​】
> L2785: 
> L2786: StopFailure input
> L2787: 
> L2788: In addition to the 【24†common input fields】, StopFailure hooks receive `error`, optional `error_details`, and optional `last_assistant_message`. The `error` field identifies the error type and is used for matcher filtering.
> L2789: Field  | Description
> L2790: --- | ---
> L2791: `error`  | Error type: `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error`, or `unknown`
> L2792: `error_details`  | Additional details about the error, when available
>
> --------------------------------------------------------------------------------
> Hooks reference - Claude Code Docs (https://code.claude.com/docs/en/hooks)
> 【turn139358view3】 [wordlim: 200] Crawled: today; Content type: text/html; Source: find({"ref_id":"https://code.claude.com/docs/en/hooks","pattern":"failClosed"}); Total lines: 4119
> No matching text found for "failClosed"
> ```
>
> <details><summary>Explored 3 files</summary>
>
> - Read `./skills/ground-meta-project/SKILL.md`
> - Read `./tests/test_check_boundaries.py`
> - Read `./.gitignore`
>
> </details>
>
> </details>
</details>

**Направление нормальное. Но этот план я бы существенно поправил перед реализацией:** полезные хуки смешаны с эвристиками, которым приписана слишком большая власть.

Хорошая основа здесь есть: общее Python-ядро, тонкие адаптеры, структурированный ввод/вывод, отсутствие LLM внутри хука, быстрые проверки перед действием и отдельные тесты. Это стоит сохранить.

По совместимости агент тоже не выдумал: [Cursor](https://prod.cursor.com/docs/reference/third-party-hooks) и [Copilot CLI](https://docs.github.com/en/copilot/reference/hooks-reference#hooks-locations) действительно читают Claude-конфиги; [Codex поддерживает хуки](https://learn.chatgpt.com/docs/hooks#tool-coverage), включая перехват `apply_patch`. **Но «конфиг загрузился» ещё не означает одинаковое поведение.** Например, Copilot cloud загружает конфигурацию из `.github/hooks/*.json`, а не из предложенного единственного канона. Общими должны быть правила и Python-логика, а конфиги — проверенными вариантами для конкретных сред.

Вот где план требует исправлений.

1. **`Read` нельзя автоматически подчинять границам изменений.** Red Zone запрещает самостоятельную правку, а читать критический код агенту обычно необходимо. Иначе он не сможет даже разобраться в задаче. Ограничения чтения — отдельная политика.

2. **«Третья правка → deny» — плохой автоматический Circuit Breaker.** Несколько небольших правок, исправление опечатки и возврат экспериментального изменения — нормальная разработка. Счётчик поощрит делать один огромный патч. Наблюдать повторные неудачи полезно; блокировать по числу записей файла я бы не стал. Сначала только предупреждения и измерение ложных срабатываний.

3. **Stop-гейт снова превращает слабые признаки в обязательные ритуалы.** Изменён код, но не `architecture.md` — ещё не нарушение. Тронут `architecture.md` — ещё не подтверждение актуальности. Телеметрия из Git по-прежнему не доказывает участие роли. Эти условия подходят для подсказок, но пока не для запрета завершить работу.

   Кроме того, `Stop` может означать конец ответа на промежуточный вопрос, а не сдачу всей задачи. Жёсткий DoD лучше привязать к явному действию «проверить готовность», а не к каждому ответу.

4. **Самозащита через хуки и regex команд не даёт полного принуждения.** Запрет `Edit/Write` не перекрывает запись из Python, Node или другого инструмента. Шим тоже можно обойти. Нужны ограничения самой среды и серверная защита Git — в зависимости от требуемой строгости. Даже документация Codex прямо называет tool hooks полезным ограничителем, а не полной границей защиты.

   Особенно важно: если хук работает с большими правами, он не должен импортировать Python-код из места, которое агент может менять. Защищать нужно весь загружаемый комплект, а не один `hook.py`.

5. **`lastfailed` здесь не годится как универсальная истина.** Репо использует `unittest`; это предложение завязано на pytest. Его кэш также не подтверждает состояние тестов на текущем коде. Нужен результат конкретного запуска с привязкой к проверенной версии файлов. Изменение падающего теста само по себе допустимо.

6. **Автокомпакцию на `SessionStart/Stop` пока нельзя включать.** Сначала исправить найденную потерю записей, обеспечить безопасную работу параллельных сессий и сделать автоматический режим явно включаемым. Иначе обычный запрос на чтение репо неожиданно меняет его память.

7. **В эксплуатации не хватает нескольких обязательных деталей.** Один общий `state.json` потребует изоляции сессий и worktree, блокировок и обработки повторных событий. Хэш рядом с изменяемыми файлами не доказывает их целостность. `try/except` не обеспечит запрет при таймауте или падении процесса — поведение нужно проверять в каждом харнессе. А после лимита Stop-повторов можно закончить с явным статусом «проверка не пройдена», сохранив запреты на защищённые операции.

И ещё: инъекция контекста **тоже расходует токены при каждом срабатывании**. Она гарантирует доставку текста, но не соблюдение правил. Краткий канонический протокол нужен и для сред без этих хуков.

**Для первого MVP я бы оставил только:**

- одну выбранную среду с настоящими интеграционными проверками;
- `PreToolUse` для проверки явно указанных путей записи;
- ограниченный по размеру контекст при старте сессии;
- журнал фактических событий без автоматического приписывания заслуг ролям;
- предупреждения при завершении;
- исправленный CI с проверкой diff и доверенной политикой.

Функции классификации уже импортируются тестами — отдельную библиотеку ради старта выделять необязательно. А блокировки по повторным правкам, полный Stop-DoD, автокомпакцию и набор из шести адаптеров я бы отложил до измерений на этом MVP.

> И как интегровать тогда версию без хуков и версию с ними? Одно общее репо или 2 раздельных?

**Одно репо, два режима установки: базовый и с хуками.** Отдельные репозитории сейчас создадут лишнюю синхронизацию правил, исправлений и релизов.

В обоих режимах остаются общие `AGENTS.md`, знания проекта, скиллы, CLI-утилиты и CI. Хуки подключаются как дополнительный способ выполнять те же проверки.

| Компонент | Без хуков среды | С хуками среды |
|---|---|---|
| Правила и границы | Общие | Те же |
| Проверка перед правкой | Агент вызывает CLI по протоколу | Харнесс вызывает проверку автоматически |
| Контекст проекта | Агент читает паспорт и нужные срезы | Хук дополнительно подаёт краткий контекст |
| Проверка готовности | Явный запуск проверки | Та же проверка плюс напоминание при завершении |
| CI | Обязательная проверка | Та же обязательная проверка |

Главное архитектурное правило: **логика проверки одна, точек вызова несколько.** CLI и хук должны обращаться к одной реализации классификации границ. Не должно появиться отдельно «как понимает правила скилл» и «как понимает правила хук».

Структуру можно развивать примерно так:

```text
meta-project/
├── templates/       # Общие шаблоны паспорта и знаний
├── skills/          # Общие процедуры работы
├── scripts/         # CLI и общая проверяющая логика
├── hooks/
│   ├── adapters/    # Особенности конкретных сред
│   └── install.py   # Подключение, проверка, отключение
└── tests/
```

Установщику нужны три операции: **подключить хуки, проверить работоспособность, отключить хуки**. При отключении паспорт и накопленные знания сохраняются. Существующие настройки харнесса аккуратно дополняются, а не перезаписываются.

В промптах стоит сохранять сами инварианты и их смысл. Подробные напоминания о ручном запуске проверок можно выбирать по режиму установки. Две независимые копии всех скиллов для этого заводить не нужно.

Ещё важно различать **«установлено» и «работает»**. Наличие `.claude/settings.json` не подтверждает активацию: могут требоваться доверие пользователя, настройка импорта или поддерживаемая версия среды. Если выбран режим с обязательными хуками, сломанный хук должен давать явную ошибку.

Общее репо также не требует хранить всё исполняемое внутри рабочего проекта: если хук получает больше прав, его код и зависимости устанавливаются в защищённое место, а состояние сессий хранится отдельно.

Делить на два репозитория имеет смысл позже, если интеграции получат отдельную команду, зависимости и цикл релизов. Сейчас достаточно **одного проекта, общей версии и опционального каталога `hooks/`**.

> Хорошо, теперь сравни проект с аналогами на рынке

<details><summary>4 previous messages</summary>

> Сравню с ближайшими аналогами по управлению контекстом, памяти, скиллам и контролю действий агента. Отдельно отмечу, что в meta-project уже реализовано, а что пока есть только в планах.
>
> <details><summary>Explored 7 files, ran 2 commands, called 3 tools</summary>
>
> MCP tool call
>
> codex_apps.cloud_environment.environment_status
>
> ```json
> {}
> ```
>
> ```text
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> ```json
> {
>   "capabilities": [
>     {
>       "remote_desktop": {
>         "description": "This environment supports a shared desktop and browser. In on-demand mode, use the desktop's NodeREPL js tool for your first action if it is available. A valid call such as js({\"code\":\"1 + 1\"}) starts the runtime. Connecting an authorized desktop viewer also starts it. Tool discovery and status polling leave it idle. To show the desktop in the Codex side panel, call open_in_codex with the cloud-desktop target if offered.",
>         "enabled": true,
>         "state": "unknown"
>       }
>     }
>   ],
>   "connectivity": "connected",
>   "desired_phase": "running",
>   "environment_id": "ccarenv_b64_Y2NhcmVudl9mNjBlN2QyNThhNjA4MTkxODA5NTU4YjI3NGI3NGNkYQ",
>   "failure": null,
>   "network_diagnostics": null,
>   "network_policy": {
>     "mode": "unrestricted",
>     "state": "enforced"
>   },
>   "observations_current": true,
>   "observed_phase": "running",
>   "observed_spec_revision": "1",
>   "outbound_identities": [],
>   "provider": "cloud",
>   "runtime_variables": [],
>   "secrets": [],
>   "source_config_id": null,
>   "source_config_version_id": null,
>   "spec_revision": "1"
> }
> ```
>
> - Ran `git ls-remote origin refs/heads/main && git log -1 --format='%H%n%s' && rg -n '^##|^###|Boundary|boundary|Zero|zero|skills/|project_knowledge|Work in Progress|Alpha|alpha' README.md && cat /etc/codex/network-policy.json`
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "response_length": "long",
>   "system2_search_query": [
>     {
>       "q": "site.github.com rulesync rulesync coding agents hooks rules"
>     },
>     {
>       "q": "site.docs.cline.bot memory bank"
>     },
>     {
>       "q": "site.github.com thedotmack claude-mem README"
>     },
>     {
>       "q": "site.github.com steveyegge beads README"
>     }
>   ]
> }
> ```
>
> ```text
> claude-mem/README.md at main · thedotmack/claude-mem · GitHub (https://github.com/thedotmack/claude-mem/blob/main/README.md)
> 【turn709584search0】 [wordlim: 200] Crawled: 2 days ago;     /plugin marketplace add thedotmack/claude-mem ...   * Hooks (`src/cli/hook-command.ts`, one adapter per agent in `src/cli/adapters/`): each agent event runs one shell-free command, such as `claude-mem hook claude-code <event>`. ...   * Repository: github.com/thedotmack/claude-mem
>
> --------------------------------------------------------------------------------
> GitHub - thedotmack/claude-mem: Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More · GitHub (https://github.com/thedotmack/claude-mem)
> 【turn709584search1】 [wordlim: 200] Crawled: last month; thedotmack / claude-mem Public ... README.md  | README.md  |    | ...   * Repository: github.com/thedotmack/claude-mem ... ai ai-agents ai-memory anthropic artificial-intelligence chromadb claude claude-agent-sdk claude-agents claude-code claude-code-plugin claude-skills embeddings long-term-memory mem0 memory-engine openmemory rag sqlite supermemory
>
> --------------------------------------------------------------------------------
> Supported Tools and Features | Rulesync (https://rulesync.dyoshikawa.com/reference/supported-tools.html)
> 【turn709584search2】 [wordlim: 200] Crawled: 2 days ago; Rulesync supports both generation and import for All of the major AI coding tools:
>
> Tool  | --targets  | rules  | ignore  | mcp  | commands  | subagents  | skills  | hooks  | permissions  | checks ... GitHub Copilot  | copilot  | ✅ 🌏  |  | ✅  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅  |
>
> --------------------------------------------------------------------------------
> claude-mem | thedotmack/claude-mem | Agent Tool Radar (https://agenttoolradar.com/resources/thedotmack/claude-mem/)
> 【turn709584search3】 [wordlim: 200] Crawled: today;     # See https://github.com/thedotmack/claude-mem for installation and usage.
>
> --------------------------------------------------------------------------------
> thedotmack-claude-mem/README.md at main · mbrukman/thedotmack-claude-mem · GitHub (https://github.com/mbrukman/thedotmack-claude-mem/blob/main/README.md)
> 【turn709584search4】 [wordlim: 200] Crawled: last week;     `> /plugin marketplace add thedotmack/claude-mem
>
> --------------------------------------------------------------------------------
> GitHub - thedotmack/claude-mem: Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More · GitHub (https://github.com/thedotmack/claude-mem?aid=recnsxtb3dgPFUksw)
> 【turn709584search5】 [wordlim: 200] Crawled: 2 days ago;     /plugin marketplace add thedotmack/claude-mem ...   * Hooks (`src/cli/hook-command.ts`, one adapter per agent in `src/cli/adapters/`): each agent event runs one shell-free command, such as `claude-mem hook claude-code <event>`.
>
> --------------------------------------------------------------------------------
> GitHub - thedotmack/claude-mem: Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More · GitHub (https://github.com/thedotmack/claude-mem?cmid=bef85c5e-6d39-4067-8525-4abb498f5cf7)
> 【turn709584search6】 [wordlim: 200] Crawled: today; Keep converted copies of tool screenshots under `~/.claude-mem/media-v1/` and show them in My Work, upload them to cmem.ai only when Cloud Sync is on, and send them to the observer model only when image inference is separately enabled.
>
> --------------------------------------------------------------------------------
> thedotmack/claude-mem — 20 AI agent skills | DevSly (https://devsly.io/git/thedotmack/claude-mem)
> 【turn709584search7】 [wordlim: 200] Crawled: today; `git clone https://github.com/thedotmack/claude-mem cp -r "claude-mem/openclaw" ~/.claude/skills/` Copy
>
> --------------------------------------------------------------------------------
> GitHub - thedotmack/claude-mem: Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More · GitHub (https://git.mitgai.net/thedotmack/claude-mem)
> 【turn709584search8】 [wordlim: 200] Crawled: today; ai ai-agents ai-memory anthropic artificial-intelligence chromadb claude claude-agent-sdk claude-agents claude-code claude-code-plugin claude-skills embeddings long-term-memory mem0 memory-engine openmemory rag sqlite supermemory ...   * Repository: github.com/thedotmack/claude-mem
>
> --------------------------------------------------------------------------------
> claude-mem/README.md at main · thedotmack/claude-mem · GitHub (https://safaia.net/thedotmack/claude-mem/blob/main/README.md)
> 【turn709584search9】 [wordlim: 200] Crawled: today; To include observations from every harness in Claude Code and Codex SessionStart context, set `"CLAUDE_MEM_SESSION_START_INCLUDE_ALL_SOURCES": "true"` in that file, or enable Include all sources at session start in the viewer settings.
>
> --------------------------------------------------------------------------------
> GitHub - thedotmack/claude-mem: Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More · GitHub (https://tvwatch.su/thedotmack/claude-mem)
> 【turn709584search10】 [wordlim: 200] Crawled: today;     /plugin marketplace add thedotmack/claude-mem
>
> --------------------------------------------------------------------------------
> thedotmack/claude-mem · FoxaMind (https://foxamind.com/repos/thedotmack-claude-mem/)
> 【turn709584search11】 [wordlim: 200] Crawled: today; # thedotmack/claude-mem ...   * ★ 116k GitHub stars
>
> --------------------------------------------------------------------------------
> cline/docs/best-practices/memory-bank.mdx at main · cline/cline · GitHub (https://github.com/cline/cline/blob/main/docs/best-practices/memory-bank.mdx)
> 【turn709584search12】 [wordlim: 200] Crawled: 4 days ago; Ask Cline to "update memory bank" to document the current state ... Memory Bank is a documentation methodology that works with any AI that can read docs.
>
> --------------------------------------------------------------------------------
> claude-mem/README.md at main · thedotmack/claude-mem · GitHub (https://ofs.ccwu.cc/thedotmack/claude-mem/blob/main/README.md)
> 【turn709584search13】 [wordlim: 200] Crawled: last month; Edit your settings file at `~/.claude-mem/settings.json`: ...     ls ~/.claude/plugins/marketplaces/thedotmack/plugin/modes/
>
> --------------------------------------------------------------------------------
> File Formats | Rulesync (https://rulesync.dyoshikawa.com/reference/file-formats.html)
> 【turn709584search14】 [wordlim: 200] Crawled: 2 days ago; Events use canonical camelCase in this file, and Rulesync translates them per tool: Cursor uses them as-is; Claude Code, Factory Droid, Codex CLI, Qwen Code, and Goose get PascalCase (with a few tool-specific name mappings) in their settings files; OpenCode and Kilo hooks are emitted as JavaScript plugins (`.opencode/plugins/rulesync-hooks.js`, `.kilo/plugins/rulesync-hooks.js`) — both share one event surface apart from `notification` (see below), in which `preToolUse`/`postToolUse` become named `tool.execute.before`/`tool.execute.after` hooks, `preCompact` becomes the named `experimental.session.compacting` hook, `beforeSubmitPrompt` the named `chat.message` hook and `preModelInvocation` the named `chat.params` hook (fired before every LLM request, for subagents too) — all three receive `(input, output)` and expose nothing to match on, so a `matcher` on any of them is dropped — while `userPromptExpansion` becomes the named `command.execute.before` hook, which fires only for slash commands (on the expanded prompt, right before it is submitted) and tests a `matcher` against the command name (`input.command`), `beforeShellExecution`/`afterShellExecution` also land in those named `tool.execute.*` hooks with an implicit `input.tool === "bash"` gate — OpenCode has no shell-execution lifecycle event (`command.executed`, which earlier Rulesync versions mapped `afterShellExecution` to, is a slash-command event, so the hook never fired on shell commands; regenerate to fix), and matchers on the shell events are dropped with a warning since the named hooks expose no command text, and the rest are `event.type` dispatches — `sessionStart` → `session.created`, `stop` → `session.idle`, `afterFileEdit` → `file.edited`, `permissionRequest` → `permission.asked`, `permissionDenied` → `permission.replied` (which fires for every reply, so the generated handler is gated on `event.properties.reply === "reject"`), `notification` → `tui.toast.show` (OpenCode only — Kilo's plugin docs document no TUI events, so `notification` is not part of its surface; note too that OpenCode's toast channel is broader than the canonical event, since every `info`/`success`/`warning`/`error` toast fires the hook rather than only the ones asking for your attention, and most toasts originate in the TUI client, so a headless `opencode run` rarely fires it at all), `postCompact` → `session.compacted`, `afterError` → `session.error`, `fileChanged` → `file.watcher.updated`, `sessionDelete` → `session.deleted`; Amp hooks are emitted as a TypeScript plugin (`.amp/plugins/rulesync-hooks.ts`, or `~/.config/amp/plugins/rulesync-hooks.ts` in global mode) using `session.start`, `tool.call`, `tool.result`, `agent.start`, and `agent.end` (plus the Amp-only `changes.prompt` from the `amp.hooks` override block); Pi Coding Agent hooks are emitted as a Rulesync-owned TypeScript extension (`.pi/extensions/rulesync-hooks.ts`, or `~/.pi/agent/extensions/rulesync-hooks.ts` in global mode) that subscribes to Pi's snake_case extension events (`sessionStart` → `session_start`, `stop` → `agent_before_settle` (added in Pi v0.87.0, so it needs Pi v0.87.0 or later — older Pi never fires it and stop hooks silently do not run there), `preToolUse` → `tool_call` with the matcher tested as a regex against the tool name, `preCompact` → `session_before_compact`, `postCompact` → `session_compact`, `postModelInvocation` → `message_end` gated on assistant messages so it runs once per finalized model response, `beforeSubmitPrompt` → `input`, `postToolUse` → `tool_result`, `postToolUseFailure` → the same `tool_result` gated on `event.isError` — Pi fires one event for every finished tool call and flags the failed ones, so the two canonical events share one subscription and only the failure handlers check the flag; `postToolUse` keeps firing for failed calls too, as it always has on Pi — and `notification` → `ui_prompt_start` (added in Pi v0.84.4), Pi's "waiting for user" signal: it fires when an extension opens a blocking `ctx.ui.select` / `confirm` / `input` / `editor` / `custom` prompt, so it covers prompts raised by extensions — Rulesync's own or third-party ones — and never core Pi, which has no built-in permission popup; it is notification-only (handlers are best-effort and not awaited, so the hook command can neither delay nor cancel the prompt), nested prompts coalesce into one span so it fires once per span, and a `matcher` on it is dropped because the handler tests nothing against it) — `tool_call` is Pi's only tool gate, so a `preToolUse` command that exits non-zero denies the call with `{ block: true, reason }` (the reason is the command's stderr, falling back to its stdout and then to its exit code, with terminal escape sequences, control and C1 characters, and format characters such as bidirectional overrides and zero-width joiners stripped, carriage returns folded into newlines so the text cannot overwrite an already printed line, the sanitized result capped at 2000 characters (and only the first 128000 characters of the command's output scanned at all) — sanitizing first so a reason that opens with a progress banner is still reported by its content — and a generic `Hook command failed.` used when nothing survives), and `input` is its prompt-submission gate, so a `beforeSubmitPrompt` command that exits non-zero cancels the prompt with `{ action: "handled" }` — that result carries no reason field, so the same text is reported through `ctx.ui.notify`, falling back to stderr in print (`-p`) and JSON modes where that channel is a no-op; three limits are worth knowing before relying on the prompt gate: Pi checks extension slash commands before the `input` event, so input consumed as a `/cmd` never reaches the gate, messages another extension injects via `sendUserMessage` (`event.source === "extension"`) are deliberately passed through because the canonical event covers prompts the user submits, and the hook command receives no prompt text (Pi's `input` event exposes it, but the generated handler runs the command with no stdin or arguments, unlike Claude Code's `UserPromptSubmit`), so the gate can only decide from ambient state; a `matcher` on `beforeSubmitPrompt` is dropped, since `input` exposes no tool name to test it against; `agent_before_settle` is Pi's last actionable boundary before a run settles (it fires after automatic retries and compaction, so a stop hook runs once per settle, unlike the notify-only `agent_end` earlier Rulesync versions mapped `stop` to), so a `stop` command that exits with code 2 asks the agent to keep going like a blocking Claude Code `Stop` hook (any other non-zero exit, including a command that cannot be run, never continues the agent, as Claude Code treats it as a non-blocking error; the handler rethrows it after the remaining stop commands run, so Pi reports it as an extension error): every configured stop command runs, and the same sanitized text from each command that exited with 2 is combined into one displayed `custom_message` (`Stop hook feedback: …`) appended after any entries other extensions proposed, with `continue: true` for one more model request — note that this sends the command's output to the model, so do not print secrets from a stop hook; to avoid the loop Pi warns about, this happens at most once per run (the guard resets on `agent_settled`, so the next prompt may continue again; later failures in the same run are only reported), never for a run that was aborted or ended in an error, and the hook command receives no event payload, so there is no equivalent of Claude Code's `stop_hook_active` to check; every other event, `postToolUse`/`tool_result` included, observes only and cannot block or mutate Pi events; a denied call deliberately leaves Pi's `terminate` flag unset so control returns to the model instead of ending the turn; Copilot and Copilot CLI map event names to their own camelCase (e.g.
>
> --------------------------------------------------------------------------------
> RuleSync — Sync CLAUDE.md Across Repos (https://www.rulesync.dev/docs)
> 【turn709584search15】 [wordlim: 200] Crawled: today;   * Fetches sync output from `/api/sync` and can handle either a single generated file or multiple files returned by the server. ...   * A `.rulesync.json` file may still exist in a repo from older setups, but the current CLI ignores it.
>
> --------------------------------------------------------------------------------
> rulesync (dyoshikawa) · Harness Hub (https://www.harness-hub.org/projects/rulesync)
> 【turn709584search16】 [wordlim: 200] Crawled: today; # rulesync ... CLI that keeps a single source of rules, commands, subagents and MCP config in sync across many coding agents. ... Stars≈1.6k(Oct 29, 2026 (GitHub API))
>
> --------------------------------------------------------------------------------
> RuleSync — Sync CLAUDE.md Across Repos (https://www.rulesync.dev/)
> 【turn709584search17】 [wordlim: 200] Crawled: 6 days ago; CLAUDE.md, AGENTS.md, .cursorrules, ~/.claude/settings.json, .github/copilot-instructions.md — you set the output path per file. ... The CLI also supports a rulesync check command to verify files are in sync without writing.
>
> --------------------------------------------------------------------------------
> File Formats | Rulesync (https://rulesync.dyoshikawa.com/reference/file-formats)
> 【turn709584search18】 [wordlim: 200] Crawled: 2 months ago; Events use canonical camelCase in this file, and Rulesync translates them per tool: Cursor uses them as-is; Claude Code, Factory Droid, Codex CLI, Qwen Code, and Goose get PascalCase (with a few tool-specific name mappings) in their settings files; OpenCode and Kilo hooks are emitted as JavaScript plugins (`.opencode/plugins/rulesync-hooks.js`, `.kilo/plugins/rulesync-hooks.js`) — both share one event surface apart from `notification` (see below), in which `preToolUse`/`postToolUse` become named `tool.execute.before`/`tool.execute.after` hooks, `preCompact` becomes the named `experimental.session.compacting` hook and `beforeSubmitPrompt` the named `chat.message` hook (both receive `(input, output)` and expose nothing to match on, so a `matcher` on either is dropped), `beforeShellExecution`/`afterShellExecution` also land in those named `tool.execute.*` hooks with an implicit `input.tool === "bash"` gate — OpenCode has no shell-execution lifecycle event (`command.executed`, which earlier Rulesync versions mapped `afterShellExecution` to, is a slash-command event, so the hook never fired on shell commands; regenerate to fix), and matchers on the shell events are dropped with a warning since the named hooks expose no command text, and the rest are `event.type` dispatches — `sessionStart` → `session.created`, `stop` → `session.idle`, `afterFileEdit` → `file.edited`, `permissionRequest` → `permission.asked`, `permissionDenied` → `permission.replied` (which fires for every reply, so the generated handler is gated on `event.properties.reply === "reject"`), `notification` → `tui.toast.show` (OpenCode only — Kilo's plugin docs document no TUI events, so `notification` is not part of its surface; note too that OpenCode's toast channel is broader than the canonical event, since every `info`/`success`/`warning`/`error` toast fires the hook rather than only the ones asking for your attention, and most toasts originate in the TUI client, so a headless `opencode run` rarely fires it at all), `postCompact` → `session.compacted`, `afterError` → `session.error`, `fileChanged` → `file.watcher.updated`; Amp hooks are emitted as a TypeScript plugin (`.amp/plugins/rulesync-hooks.ts`, or `~/.config/amp/plugins/rulesync-hooks.ts` in global mode) using `session.start`, `tool.call`, `tool.result`, `agent.start`, and `agent.end`; Pi Coding Agent hooks are emitted as a Rulesync-owned TypeScript extension (`.pi/extensions/rulesync-hooks.ts`, or `~/.pi/agent/extensions/rulesync-hooks.ts` in global mode) that subscribes to Pi's snake_case extension events (`sessionStart` → `session_start`, `stop` → `agent_end`, `preToolUse` → `tool_call` with the matcher tested as a regex against the tool name, `preCompact` → `session_before_compact`, `postCompact` → `session_compact`, `postModelInvocation` → `message_end` gated on assistant messages so it runs once per finalized model response, `beforeSubmitPrompt` → `input`) — `tool_call` is Pi's only tool gate, so a `preToolUse` command that exits non-zero denies the call with `{ block: true, reason }` (the reason is the command's stderr, falling back to its stdout and then to its exit code, with terminal escape sequences, control and C1 characters, and format characters such as bidirectional overrides and zero-width joiners stripped, carriage returns folded into newlines so the text cannot overwrite an already printed line, the sanitized result capped at 2000 characters (and only the first 128000 characters of the command's output scanned at all) — sanitizing first so a reason that opens with a progress banner is still reported by its content — and a generic `Hook command failed.` used when nothing survives), and `input` is its prompt-submission gate, so a `beforeSubmitPrompt` command that exits non-zero cancels the prompt with `{ action: "handled" }` — that result carries no reason field, so the same text is reported through `ctx.ui.notify`, falling back to stderr in print (`-p`) and JSON modes where that channel is a no-op; three limits are worth knowing before relying on the prompt gate: Pi checks extension slash commands before the `input` event, so input consumed as a `/cmd` never reaches the gate, messages another extension injects via `sendUserMessage` (`event.source === "extension"`) are deliberately passed through because the canonical event covers prompts the user submits, and the hook command receives no prompt text (Pi's `input` event exposes it, but the generated handler runs the command with no stdin or arguments, unlike Claude Code's `UserPromptSubmit`), so the gate can only decide from ambient state; a `matcher` on `beforeSubmitPrompt` is dropped, since `input` exposes no tool name to test it against; every other event, `postToolUse`/`tool_result` included, observes only and cannot block or mutate Pi events; a denied call deliberately leaves Pi's `terminate` flag unset so control returns to the model instead of ending the turn; Copilot and Copilot CLI map event names to their own camelCase (e.g.
>
> --------------------------------------------------------------------------------
> Configuration | Rulesync (https://rulesync.dyoshikawa.com/guide/configuration)
> 【turn709584search19】 [wordlim: 200] Crawled: 2 days ago;       "$schema": "https://github.com/dyoshikawa/rulesync/releases/latest/download/config-schema.json", ...       // To stay able to retract a hook it did write, Rulesync records what it
>       // generated in a `.rulesync-hooks-lock.json` next to each hooks file (e.g. ...       // Derive `agentsmd.subprojectPath` from each non-root rule's `globs`, so a
>
> --------------------------------------------------------------------------------
> GitHub - sheeeng/steveyegge-beads: Beads - A memory upgrade for your coding agent · GitHub (https://github.com/sheeeng/steveyegge-beads)
> 【turn709584search20】 [wordlim: 200] Crawled: today; Only need `git config beads.role maintainer` if using GitHub HTTPS without credentials but you have write access. ...         CGO_ENABLED=0 go install -tags gms_pure_go github.com/steveyegge/beads/cmd/bd@latest ... In releases after v1.3.2, sync matches, fetches and updates only beads whose issue URL points at the configured repository, so pulling issue 1313 from a second repository creates a new bead instead of overwriting the bead linked to the first repository's issue 1313.
>
> --------------------------------------------------------------------------------
> GitHub - nobug-project/rulesync: A Utility CLI for AI Coding Agents · GitHub (https://github.com/nobug-project/rulesync)
> 【turn709584search21】 [wordlim: 200] Crawled: last month; Tool  | rules  | ignore  | mcp  | commands  | subagents  | skills  | hooks  | permissions  | checks ... Existing ignore configurations remain supported throughout Rulesync 14.x; removal, if any, will be decided separately and will not occur before a future major release. ... For project-scope rules, both `antigravity-ide` and `antigravity-cli` emit the root rule as a plain cross-tool `AGENTS.md` at the project root (the Gemini-lineage discovery order is `AGENTS.md`, `CONTEXT.md`, `GEMINI.md`; the IDE has read `AGENTS.md` since v1.20.3) and non-root rules under `.agents/rules/`.
>
> --------------------------------------------------------------------------------
> steveyegge-beads/docs/getting-started/installation.md at main · PapiDee09/steveyegge-beads · GitHub (https://github.com/PapiDee09/steveyegge-beads/blob/main/docs/getting-started/installation.md)
> 【turn709584search22】 [wordlim: 200] Crawled: today;   * Server-mode only (nocgo, simplest): `CGO_ENABLED=0 go install github.com/steveyegge/beads/cmd/bd@latest`. ...   * Embedded-capable (cgo): `CGO_ENABLED=1 GOFLAGS=-tags=gms_pure_go go install github.com/steveyegge/beads/cmd/bd@latest`.
>
> --------------------------------------------------------------------------------
> rulesync/README.md at main · dyoshikawa/rulesync · GitHub (https://github.com/dyoshikawa/rulesync/blob/main/README.md)
> 【turn709584search23】 [wordlim: 200] Crawled: last month; Tool  | rules  | ignore  | mcp  | commands  | subagents  | skills  | hooks  | permissions  | checks ... GitHub Copilot  | ✅  |  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ... Pi Coding Agent  | ✅  |  |  | ✅  |  | ✅  | ✅  | ✅  |
>
> --------------------------------------------------------------------------------
> rulesync/rulesync.jsonc at main · dyoshikawa/rulesync · GitHub (https://cdn.hddj.top/dyoshikawa/rulesync/blob/main/rulesync.jsonc)
> 【turn709584search24】 [wordlim: 200] Crawled: today; # rulesync.jsonc
>
> # rulesync.jsonc ... "hooks": true
>
> --------------------------------------------------------------------------------
> RuleSync — ClaudeMod — ClaudeMod (https://www.claudemod.com/mods/rulesync)
> 【turn709584search25】 [wordlim: 200] Crawled: today; Tool  | rules  | ignore  | mcp  | commands  | subagents  | skills  | hooks  | permissions  | checks ... Existing ignore configurations remain supported throughout Rulesync 14.x; removal, if any, will be decided separately and will not occur before a future major release.
>
> --------------------------------------------------------------------------------
> steveyegge-beads/docs/QUICKSTART.md at main · tEhThing/steveyegge-beads · GitHub (https://github.com/tEhThing/steveyegge-beads/blob/main/docs/QUICKSTART.md)
> 【turn709584search26】 [wordlim: 200] Crawled: today; # Beads Quickstart ...     # Protected main branch (GitHub/GitLab) ... Note: Issue IDs are hash-based (e.g., `bd-a1b2`, `bd-f14c`) to prevent collisions when multiple agents/branches work concurrently.
>
> --------------------------------------------------------------------------------
> steveyegge/beads — GitHub Explorer (https://ghe.derekchia.com/repo/steveyegge/beads)
> 【turn709584search27】 [wordlim: 200] Crawled: today; # steveyegge/beads
>
> View on GitHub ↗Related repositories →[Button: ☆ Pin]
>
> --------------------------------------------------------------------------------
> CLI Commands | Rulesync (https://rulesync.dyoshikawa.com/reference/cli-commands.html)
> 【turn709584search28】 [wordlim: 200] Crawled: 2 days ago;     rulesync import --targets claudecode-plugin --features skills,hooks --output-root ./plugins/review-tools ...     rulesync fetch https://github.com/owner/repo --conflict skip ... Because `AGENTS.md` is a de facto standard file read by many AI tools regardless of the target set, its gitignore entries are emitted unconditionally to prevent accidental commits of generated rule files.
>
> --------------------------------------------------------------------------------
> steveyegge/beads v1.3.4-rc.1 | My Release Notes (https://www.myreleasenotes.ai/releases/KLceE5IkWsOwl0545Rhhq)
> 【turn709584search29】 [wordlim: 200] Published: last week; Crawled: yesterday;     `go install github.com/steveyegge/beads/cmd/[email protected]
>
> --------------------------------------------------------------------------------
> beads - Agent Skill | Skill Gallery (https://www.skill-gallery.jp/en/skills/steveyegge/beads)
> 【turn709584search30】 [wordlim: 200] Published: 9 months ago; Crawled: today; How do I write tests using beads? ... Use when work spans sessions, has blockers, or needs context recovery after compaction. allowed-tools: "Read,Bash(bd:*)" version: "0.47.1" author: "Steve Yegge https://github.com/steveyegge" license: "MIT"
>
> --------------------------------------------------------------------------------
> steveyegge/beads v1.3.3-rc.1 | My Release Notes (https://www.myreleasenotes.ai/releases/u6sqZZcGnmcKPampQ0BpA)
> 【turn709584search31】 [wordlim: 200] Published: last week; Crawled: 3 days ago;     `go install github.com/steveyegge/beads/cmd/[email protected]
>
> --------------------------------------------------------------------------------
> GitHub - tEhThing/steveyegge-beads: Beads - A memory upgrade for your coding agent · GitHub (https://github.com/tEhThing/steveyegge-beads)
> 【turn709584search32】 [wordlim: 200] Crawled: today;     curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash ...     # For protected branches (GitHub/GitLab):
>
> --------------------------------------------------------------------------------
> Memory Bank: How to Make Cline an AI Agent That Never Forgets (https://cline.bot/blog/memory-bank-how-to-make-cline-an-ai-agent-that-never-forgets)
> 【turn709584search33】 [wordlim: 200] Published: 1.8 years ago; Crawled: 2 weeks ago; Image In this case, projectbrief.md is the source of truth from which other docs come from ...   1. projectbrief.md: The foundation document that shapes everything else ... The full Memory Bank instructions are in the Cline documentation.
>
> --------------------------------------------------------------------------------
> GitHub - salewski/steveyegge--beads: Beads - A memory upgrade for your coding agent · GitHub (https://github.com/salewski/steveyegge--beads)
> 【turn709584search34】 [wordlim: 200] Crawled: today; Docs: https://gastownhall.github.io/beads/ ...     curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
>
> --------------------------------------------------------------------------------
> prompts/.clinerules/memory-bank.md at main · cline/prompts · GitHub (https://github.com/cline/prompts/blob/main/.clinerules/memory-bank.md?ref=cline.ghost.io)
> 【turn709584search35】 [wordlim: 200] Crawled: last month; description  | Describes Cline's Memory Bank system, its structure, and workflows for maintaining project knowledge across sessions. ... # Cline's Memory Bank ...      * Foundation document that shapes all other files
>
> --------------------------------------------------------------------------------
> steveyegge/beads v1.3.2-rc.2 | My Release Notes (https://www.myreleasenotes.ai/releases/v4Qgn_n9ueRVKP3hMRROG)
> 【turn709584search36】 [wordlim: 200] Published: last month; Crawled: today;     `go install github.com/steveyegge/beads/cmd/[email protected]
>
> --------------------------------------------------------------------------------
> Memory Bank - Cline 文档｜FunCoding (https://funcoding.ai/agents/cline/best-practices/memory-bank/)
> 【turn709584search37】 [wordlim: 200] Crawled: 2 days ago; Ask Cline to "update memory bank" to document the current state ... Memory Bank is a documentation methodology that works with any AI that can read docs.
>
> --------------------------------------------------------------------------------
> GitHub - richardsonjf/steveyegge-beads: Beads - A memory upgrade for your coding agent · GitHub (https://github.com/richardsonjf/steveyegge-beads)
> 【turn709584search38】 [wordlim: 200] Crawled: today; See integrations/beads-mcp/README.md for detailed MCP server documentation. ...     git clone https://github.com/steveyegge/beads
>
> --------------------------------------------------------------------------------
> beads by @steveyegge — Agent Skill | Agent Skills (https://www.agentskills.in/marketplace/%40steveyegge/beads)
> 【turn709584search39】 [wordlim: 200] Crawled: today; View on GitHub ... $npx agent-skills-cli install @steveyegge/beads
>
> --------------------------------------------------------------------------------
> cline_docs/prompting/custom instructions library/cline-memory-bank.md at main · nickbaumann98/cline_docs · GitHub (https://github.com/nickbaumann98/cline_docs/blob/main/prompting/custom%20instructions%20library/cline-memory-bank.md)
> 【turn709584search40】 [wordlim: 200] Crawled: last month; Please refer to https://docs.cline.bot/improving-your-prompting-skills/cline-memory-bank for the most recent version of Cline Memory Bank. ...        - Foundation document that shapes all other files
> ```
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "response_length": "long",
>   "system2_search_query": [
>     {
>       "q": "site.github.com obra superpowers agent skills README"
>     },
>     {
>       "q": "site.github.com bmad-code-org BMAD-METHOD README"
>     },
>     {
>       "q": "site.github.com github spec-kit README constitution"
>     },
>     {
>       "q": "site.github.com Fission-AI OpenSpec README"
>     }
>   ]
> }
> ```
>
> ````text
> GitHub - Fission-AI/OpenSpec: Spec-driven development (SDD) for AI coding assistants. · GitHub (https://github.com/Fission-AI/openspec)
> 【turn790488search0】 [wordlim: 200] Crawled: today; `npm install -g @fission-ai/openspec@latest` (needs Node.js 22.12.0 or higher) or the official Homebrew formula, `brew install openspec`. ... `/opsx:propose` is the canonical name; your tool may spell it `/opsx-propose` (Cursor, GitHub Copilot), `@opsx-propose` (Amazon Q) or `$openspec-propose` (Codex). `openspec init` prints the right form for the tools you picked — see Supported Tools.
>
> --------------------------------------------------------------------------------
> OpenSpec/README.md at main · Fission-AI/OpenSpec · GitHub (https://github.com/Fission-AI/OpenSpec/blob/main/README.md)
> 【turn790488search1】 [wordlim: 200] Crawled: 2 weeks ago;     curl -fsSL https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/scripts/binary/install.sh | sh ... `/opsx:propose` is the canonical name; your tool may spell it `/opsx-propose` (Cursor, GitHub Copilot), `@opsx-propose` (Amazon Q) or `$openspec-propose` (Codex). `openspec init` prints the right form for the tools you picked — see Supported Tools.
>
> --------------------------------------------------------------------------------
> obra/superpowers · Skills Docs (https://skillsdocs.com/obra/superpowers)
> 【turn790488search2】 [wordlim: 200] Published: last week; Crawled: today;     github.com/obra/superpowers ... From the README
>
> Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them.
>
> --------------------------------------------------------------------------------
> GitHub - obra/superpowers: An agentic skills framework & software development methodology that works. · GitHub (https://github.com/obra/superpowers)
> 【turn790488search3】 [wordlim: 200] Crawled: 2 months ago;     agy plugin install https://github.com/obra/superpowers ... Skill-behavior tests use the drill eval harness from superpowers-evals, cloned into `evals/` — see `evals/README.md` for setup. ... ai brainstorming coding obra sdlc skills subagent-driven-development superpowers
>
> --------------------------------------------------------------------------------
> OpenSpec/docs/README.md at main · Fission-AI/OpenSpec · GitHub (https://github.com/Fission-AI/OpenSpec/blob/main/docs/README.md)
> 【turn790488search4】 [wordlim: 200] Crawled: last month;   * GitHub Issues: github.com/Fission-AI/OpenSpec/issues for bugs and feature requests.
>
> --------------------------------------------------------------------------------
> spec-kit/templates/commands/constitution.md at main · github/spec-kit · GitHub (https://github.com/github/spec-kit/blob/main/templates/commands/constitution.md)
> 【turn790488search5】 [wordlim: 200] Crawled: yesterday; The active constitution scaffold is resolved at command time from `constitution-template` through the Spec Kit preset/template resolution stack. ... Run `{SCRIPT}` from the repository root and parse `TEMPLATE_CONTENT` as the active template. ...      * Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded). ... Produce a Sync Impact Report as an HTML comment at the top of the constitution file after update.
>
> --------------------------------------------------------------------------------
> spec-kit/templates/commands/constitution.md at main · github/spec-kit · GitHub (https://github.com/github/spec-kit/blob/main/templates/commands/constitution.md?plain=1)
> 【turn790488search6】 [wordlim: 200] Crawled: 2 weeks ago; py: scripts/python/resolve_template.py constitution-template --json ... List the original intent and suggest the appropriate follow-up Spec Kit command, such ... constitution scaffold is resolved at command time from `constitution-template` through the Spec Kit ... - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded). ... Produce a Sync Impact Report as an HTML comment at the top of the constitution file after update.
>
> --------------------------------------------------------------------------------
> spec-kit/README.md at main · github/spec-kit · GitHub (https://github.com/github/spec-kit/blob/main/README.md?plain=1)
> 【turn790488search7】 [wordlim: 200] Crawled: today; ## Capabilities Spec Kit combines ready-to-use processes with composable mechanisms: | Capability | Spec Kit mechanism | | --- | --- | | Connect to or switch between coding agents | [Integration](https://github.github.io/spec-kit/integrations/index.html) | | Add a command, quality gate, or complete process | [Extension](https://github.github.io/spec-kit/extensions/overview.html) | | Connect a process to an external tool or service | [Extension](https://github.github.io/spec-kit/extensions/overview.html) | | React to coding-agent lifecycle events | [Extension runtime event](https://github.github.io/spec-kit/extensions/api.html#extension-runtime-events) | | Run extension commands before or after Spec Kit commands | [Extension hook](https://github.github.io/spec-kit/extensions/api.html#hook-configuration) | | Adapt templates, commands, terminology, or methodology | [Preset](https://github.github.io/spec-kit/presets/overview.html) | | Enforce organizational or regulatory standards | [Preset](https://github.github.io/spec-kit/presets/overview.html) | | Override a template for one project | [Project-local override](https://github.github.io/spec-kit/how-to/customization.html#project-local-overrides-and-resolution) | | Automate prompts, commands, gates, and shell tasks | [Workflow](https://github.github.io/spec-kit/workflows/overview.html) | | Modify an installed workflow without forking it | [Workflow overlay](https://github.github.io/spec-kit/workflows/overlays.html) | | Add reusable executable behavior to workflows | [Workflow step](https://github.github.io/spec-kit/workflow-steps/developing.html#custom-step-packages) | | Install a curated setup for a role or team | [Bundle](https://github.github.io/spec-kit/bundles/overview.html) | | Discover community components | [Catalog](https://github.github.io/spec-kit/overview/catalogs.html) | | Host a private catalog of approved components | [Catalog](https://github.github.io/spec-kit/overview/catalogs.html) | | Access private catalogs and component downloads | [Authentication](https://github.github.io/spec-kit/reference/authentication.html) | | Work offline or behind a firewall | [Local sources and self-hosted catalogs](https://github.github.io/spec-kit/install/air-gapped.html) | | Inspect which layer supplies a command, template, or script | [Artifact inventory](https://github.github.io/spec-kit/overview/artifacts.html) | Search the active catalogs with commands such as `specify extension search`, `specify preset search`, `specify workflow search`, and `specify bundle search`. ... For another agent, use its [equivalent invocation syntax](https://github.github.io/spec-kit/integrations/cli.html#command-invocation). ```text /speckit-constitution Create principles focused on code quality, testing, and maintainability. /speckit-specify Build a photo organizer with albums grouped by date and a tile preview of each album. /speckit-plan Use Vite with vanilla JavaScript.
>
> --------------------------------------------------------------------------------
> GitHub - obra/superpowers: An agentic skills framework & software development methodology that works. · GitHub (https://github.com/obra/superpowers?pubDate=20260803)
> 【turn790488search8】 [wordlim: 200] Crawled: today; Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them. ...     agy plugin install https://github.com/obra/superpowers ... Skill-behavior tests use the drill eval harness from superpowers-evals, cloned into `evals/` — see `evals/README.md` for setup.
>
> --------------------------------------------------------------------------------
> OpenSpec/docs/faq.md at main · Fission-AI/OpenSpec · GitHub (https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md?plain=1)
> 【turn790488search9】 [wordlim: 200] Crawled: today; OpenSpec works with 30+ assistants, including Claude Code, Cursor, Devin Desktop, GitHub Copilot, Gemini CLI, Codex, and more. ... The README recommends models like Codex 5.5 and Opus 4.7 for both planning and implementation. ... Upgrade the package (`npm install -g @fission-ai/openspec@latest`), then run `openspec update` inside each project to refresh the generated skills and commands.
>
> --------------------------------------------------------------------------------
> spec-kit/presets/lean/commands/speckit.constitution.md at main · github/spec-kit · GitHub (https://github.com/github/spec-kit/blob/main/presets/lean/commands/speckit.constitution.md)
> 【turn790488search10】 [wordlim: 200] Crawled: 2 months ago;   * After updating the constitution, list each deferred intent in a `Next Actions` section with an appropriate follow-up Spec Kit command, such as `__SPECKIT_COMMAND_SPECIFY__`, but do not invoke it. ...      * Derive from user input and existing repo context (README, docs)
>
> --------------------------------------------------------------------------------
> OpenSpec/docs/getting-started.md at main · Fission-AI/OpenSpec · GitHub (https://github.com/Fission-AI/OpenSpec/blob/main/docs/getting-started.md)
> 【turn790488search11】 [wordlim: 200] Crawled: today; For installation instructions, see the main README or the Installation guide. ...     `TERMINAL   $ curl -fsSL https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/scripts/binary/install.sh | sh
>
> --------------------------------------------------------------------------------
> The Method | BMad Code (https://www.bmadcode.com/method)
> 【turn790488search12】 [wordlim: 200] Crawled: today; BMad Method v6.12.0 MIT licensed Free and open source Docs GitHub Discord ... No BMad runtime ever sees your code, prompts, or data. ... Required fields on an artifact, your own PRD template pinned org-wide, an internal compliance reference the workflow consults before drafting.
>
> --------------------------------------------------------------------------------
> The Method | BMad Code (https://bmadcode.com/method)
> 【turn790488search13】 [wordlim: 200] Crawled: today; BMad Method v6.12.0 MIT licensed Free and open source Docs GitHub Discord
>
> BMad Code ... Required fields on an artifact, your own PRD template pinned org-wide, an internal compliance reference the workflow consults before drafting.
>
> --------------------------------------------------------------------------------
> Upgrade Guide | Spec Kit Documentation (https://github.github.com/spec-kit/upgrade.html)
> 【turn790488search14】 [wordlim: 200] Crawled: today; More broadly, presets and extensions — not in-place file edits — are how Spec Kit now governs shared assets. ... Note that this edit-in-place propagation model conflicts with the composition model used by the rest of the SDD commands when they are preset/extension-managed — see the "Interaction with the resolution stack" section in `presets/constitution-sync/README.md` for the tradeoffs and when to prefer the default instead. ...   * Check documentation: Visit github.io/spec-kit for updated guides
>
> --------------------------------------------------------------------------------
> spec-kit/docs/reference/agentic-sdd.md at main · github/spec-kit · GitHub (https://github.mosekj.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md)
> 【turn790488search15】 [wordlim: 200] Crawled: 3 weeks ago; `/speckit.taskstoissues`  | `speckit-taskstoissues`  | Deprecated core command; use the `github` extension for GitHub issues ...     `/speckit.constitution This project follows a "Library-First" approach. ... This workflow may also maintain `checklists/requirements.md`, the built-in spec-quality checklist that `/speckit.specify` creates and `/speckit.clarify` re-evaluates.
>
> --------------------------------------------------------------------------------
> Using Superpowers — AI Agent Skill by obra | AgenticSkills (https://agenticskills.io/skills/using-superpowers)
> 【turn790488search16】 [wordlim: 200] Crawled: today;     `npx skills add obra/superpowers@using-superpowers` ...       https://raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md` ... Disciplined Development Your AI agent plans before coding, follows TDD, debugs systematically, and proves its work is correct.7 skills · 0 MCP
>
> --------------------------------------------------------------------------------
> Installation | OpenSpec (https://openspec.dev/docs/installation)
> 【turn790488search17】 [wordlim: 200] Crawled: today;     `Fetch https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/install.md and follow it. ...     `nix profile install github:Fission-AI/OpenSpec`
>
> --------------------------------------------------------------------------------
> BMad Code Org · GitHub (https://github.com/bmad-code-org)
> 【turn790488search18】 [wordlim: 200] Crawled: yesterday;   * https://www.bmadcode.com/ ... 43K+ GitHub stars. ... bmad-code-org/BMAD-METHOD's past year of commit activity
>
> --------------------------------------------------------------------------------
> GitHub - obra/superpowers: An agentic skills framework & software development methodology that works. · GitHub (https://github.masuit.org/obra/superpowers/tree/main)
> 【turn790488search19】 [wordlim: 200] Crawled: today; Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them. ...     agy plugin install https://github.com/obra/superpowers ... Skill-behavior tests use the drill eval harness from superpowers-evals, cloned into `evals/` — see `evals/README.md` for setup.
>
> --------------------------------------------------------------------------------
> GitHub Spec Kit | Spec Kit Documentation (https://github.github.com/spec-kit/)
> 【turn790488search20】 [wordlim: 200] Published: last week; Crawled: today; # GitHub Spec Kit ... Spec Kit's Agentic SDLC How this project assesses, builds, tests, ships, and repairs changes Spec-Driven Development Define, plan, implement, and converge on a feature Bug Fixing Assess the cause, apply a scoped fix, and verify the result Idea Assessment Research an idea and decide whether it deserves investment Adapt Spec Kit to your process Adapt a process, add capabilities, or package a role-based setup Existing Projects Adopt Spec Kit safely in an established codebase Upgrade Keep an existing Spec Kit project current across releases Core Commands Initialize projects, check tools, and inspect version and system information Community Community integrations, extensions, presets, workflows, steps, bundles, and companion resources Develop Spec Kit locally Run, debug, and check changes to Spec Kit itself How to Understand and apply Spec Kit practices to your project work History How Spec Kit grew from its SDD foundation into an extensible process harness
>
> --------------------------------------------------------------------------------
> OpenSpec: Lightweight spec-driven workflow for coding agents (scaffolds & templates) (https://insidethemachine.ai/setups/openspec)
> 【turn790488search21】 [wordlim: 200] Crawled: 2 weeks ago;   * READMEgithub.com/Fission-AI/OpenSpec · README (opens in a new tab)
>
> --------------------------------------------------------------------------------
> OpenSpec/docs/faq.md at main · Fission-AI/OpenSpec · GitHub (https://ofs.ccwu.cc/Fission-AI/OpenSpec/blob/main/docs/faq.md)
> 【turn790488search22】 [wordlim: 200] Crawled: 2 weeks ago; OpenSpec works with 30+ assistants, including Claude Code, Cursor, Devin Desktop, GitHub Copilot, Gemini CLI, Codex, and more. ... The README recommends models like Codex 5.5 and Opus 4.7 for both planning and implementation. ... Upgrade the package (`npm install -g @fission-ai/openspec@latest`), then run `openspec update` inside each project to refresh the generated skills and commands.
>
> --------------------------------------------------------------------------------
> obra/superpowers Agent Skills on GitHub | SkillsMP (https://skillsmp.com/creators/obra/superpowers)
> 【turn790488search23】 [wordlim: 200] Crawled: today;     `Follow https://skillsmp.com/skill-install/prompt.md to install Agent Skills from https://github.com/obra/superpowers.
>
> --------------------------------------------------------------------------------
> OpenSpec/docs/supported-tools.md at main · Fission-AI/OpenSpec · GitHub (https://ofs.ccwu.cc/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md)
> 【turn790488search24】 [wordlim: 200] Crawled: 3 days ago; OpenSpec works with many AI coding assistants.
>
> --------------------------------------------------------------------------------
> GitHub - bmad-code-org/BMAD-METHOD: Breakthrough Method for Agile Ai Driven Development · GitHub (https://github.com/bmad-code-org/bmad-method)
> 【turn790488search25】 [wordlim: 200] Crawled: 2 months ago; bmad-code-org / BMAD-METHOD Public ... .github  | .github  |    | ... README.md  | README.md  |    |
>
> --------------------------------------------------------------------------------
> OpenSpec/README.md at main · Fission-AI/OpenSpec · GitHub (https://opencode.terrychan.org/Fission-AI/OpenSpec/blob/main/README.md)
> 【turn790488search26】 [wordlim: 200] Crawled: today; # README.md ... `npm install -g @fission-ai/openspec@latest` (needs Node.js 22.12.0 or higher) or the official Homebrew formula, `brew install openspec`. ... `/opsx:propose` is the canonical name; your tool may spell it `/opsx-propose` (Cursor, GitHub Copilot), `@opsx-propose` (Amazon Q) or `$openspec-propose` (Codex). `openspec init` prints the right form for the tools you picked — see Supported Tools.
>
> --------------------------------------------------------------------------------
> obra Hermes AI Agent Skills | LLMBase (https://llmbase.ai/skills/obra/)
> 【turn790488search27】 [wordlim: 200] Crawled: today; GitHub source repository ... `npx skills add obra/superpowers --skill subagent-driven-development`Safe
>
> --------------------------------------------------------------------------------
> OpenSpec/docs/installation.md at main · Fission-AI/OpenSpec · GitHub (https://git.mitgai.net/Fission-AI/OpenSpec/blob/main/docs/installation.md)
> 【turn790488search28】 [wordlim: 200] Crawled: 2 weeks ago;     curl -fsSL https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/scripts/binary/install.sh | sh
>
> --------------------------------------------------------------------------------
> using-superpowers by @obra — Agent Skill | Agent Skills (https://www.agentskills.in/marketplace/%40obra/using-superpowers)
> 【turn790488search29】 [wordlim: 200] Crawled: today; View on GitHub ... $npx agent-skills-cli install @obra/using-superpowers ... Path skills/using-superpowers/SKILL.md
>
> --------------------------------------------------------------------------------
> Using Superpowers · Skills Hub (https://skill.tokentosea.com/en/skills/using-superpowers/)
> 【turn790488search30】 [wordlim: 200] Crawled: today;     `gemini skills install https://github.com/obra/superpowers.git --path skills/using-superpowers`
>
> --------------------------------------------------------------------------------
> GitHub - bmad-code-org/BMAD-METHOD at blog.bmadcode.com · GitHub (https://github.com/bmad-code-org/BMAD-METHOD?ref=blog.bmadcode.com)
> 【turn790488search31】 [wordlim: 200] Crawled: today;     npx skills add bmad-code-org/BMAD-METHOD --skill '*' ... Report preview problems in GitHub Issues or on Discord. ... Star the repository, buy me a coffee, or email contact@bmadcode.com for corporate sponsorship.
>
> --------------------------------------------------------------------------------
> How to Install BMad | BMad Method (https://docs.bmad-method.org/start/install-bmad/)
> 【turn790488search32】 [wordlim: 200] Crawled: today;     npx skills add bmad-code-org/BMAD-METHOD/skills/core-tools --skill '*' ... To choose skills instead, run `npx skills add bmad-code-org/BMAD-METHOD` and select your coding tool and skills.
>
> --------------------------------------------------------------------------------
> using-superpowers — obra/superpowers (https://www.skills.sh/obra/superpowers/using-superpowers)
> 【turn790488search33】 [wordlim: 200] Crawled: today; `$ npx skills add https://github.com/obra/superpowers --skill using-superpowers` ... Gen Agent Trust Hub Warn Socket Pass Snyk Pass
>
> --------------------------------------------------------------------------------
> @fission-ai/openspec - npm (https://www.npmjs.com/package/%40fission-ai/openspec)
> 【turn790488search34】 [wordlim: 200] Crawled: today; github.com/Fission-AI/OpenSpec
>
> --------------------------------------------------------------------------------
> Upgrade Guide | Spec Kit Documentation (https://github.github.io/spec-kit/upgrade.html)
> 【turn790488search35】 [wordlim: 200] Crawled: yesterday; Spec Kit uses runtime resolution: `plan`, `tasks`, and `analyze` read `.specify/memory/constitution.md` live on every run, and `analyze` is the dedicated drift checker. ... More broadly, presets and extensions — not in-place file edits — are how Spec Kit now governs shared assets. ... Note that this edit-in-place propagation model conflicts with the composition model used by the rest of the SDD commands when they are preset/extension-managed — see the "Interaction with the resolution stack" section in `presets/constitution-sync/README.md` for the tradeoffs and when to prefer the default instead.
>
> --------------------------------------------------------------------------------
> superpowers — Agent Skills Repository by obra | skills.rest (https://skills.rest/repo/obra/superpowers)
> 【turn790488search36】 [wordlim: 200] Crawled: 6 days ago; Run `npx skills add obra/superpowers --all -g -y` in your terminal to install the full skill suite globally for your coding agent. ... It works with Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, and several other agent harnesses.
>
> --------------------------------------------------------------------------------
> bmad-method - npm (https://www.npmjs.com/package/bmad-method)
> 【turn790488search37】 [wordlim: 200] Crawled: 2 months ago; github.com/bmad-code-org/BMAD-METHOD#readme
>
> --------------------------------------------------------------------------------
> Superpowers — Agent Skills: install, README & stats (https://aiticker.site/skills/obra/superpowers/)
> 【turn790488search38】 [wordlim: 200] Crawled: today;     `git clone --depth 1 https://github.com/obra/superpowers.git /tmp/superpowers ... brainstorming You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it (a talk, a business, a renovation).`skills/brainstorming`⬇ 5.4k installs diagnosing-superpowers Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, "it took too long", "why is it so expensive", "what is it doing" — or wants to build a bug report for the superpowers maintainers, for `skills/diagnosing-superpowers`dispatching-parallel-agents Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies`skills/dispatching-parallel-agents`⬇ 575 installs executing-plans Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available`skills/executing-plans`⬇ 665 installs finishing-a-development-branch Use when implementation is complete, all tests pass, and you need to decide how to integrate the work`skills/finishing-a-development-branch`⬇ 455 installs receiving-code-review Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation`skills/receiving-code-review`⬇ 487 installs requesting-code-review Use when completing tasks, implementing major features, or before merging to verify work meets requirements`skills/requesting-code-review`⬇ 662 installs subagent-driven-development Use when executing implementation plans with independent tasks in the current session`skills/subagent-driven-development`⬇ 1.2k installs systematic-debugging Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes`skills/systematic-debugging`⬇ 2.3k installs test-driven-development Use when implementing any feature or bugfix, before writing implementation code`skills/test-driven-development`⬇ 605 installs using-git-worktrees Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback`skills/using-git-worktrees`⬇ 553 installs using-superpowers Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions`skills/using-superpowers`⬇ 3.0k installs verification-before-completion Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always`skills/verification-before-completion`⬇ 646 installs writing-plans Use when you have a spec or requirements for a multi-step task, before touching code`skills/writing-plans`⬇ 1.1k installs writing-skills Use when creating new skills, editing existing skills, or verifying skills work before deployment`skills/writing-skills`⬇ 517 installs
>
> --------------------------------------------------------------------------------
> bmad-code-org/BMAD-METHOD Good First Issues | Good First Issue (https://www.goodfirstissue.org/bmad-code-org/BMAD-METHOD)
> 【turn790488search39】 [wordlim: 200] Crawled: today; Home / bmad-code-org / bmad-code-org/BMAD-METHOD ... Sign in to follow View on GitHub
>
> --------------------------------------------------------------------------------
> Presets | Spec Kit Documentation (https://github.github.com/spec-kit/presets/overview.html)
> 【turn790488search40】 [wordlim: 200] Crawled: yesterday; Initialization seeds `.specify/memory/constitution.md` once from the resolved `constitution-template`, preserving an existing constitution. ... ### How do I see which file is being used? ... Community catalog inclusion does not transfer maintenance or support responsibility to the Spec Kit maintainers.
>
> --------------------------------------------------------------------------------
> GitHub - bmad-code-org/BMAD-METHOD: Breakthrough Method for Agile Ai Driven Development · GitHub (https://opencode.terrychan.org/bmad-code-org/BMAD-METHOD)
> 【turn790488search41】 [wordlim: 200] Crawled: today; .github  | .github  |    | ... README.md  | README.md  |    | ...     npx skills add bmad-code-org/BMAD-METHOD --skill '*' ... BMad Method  | Plan and deliver software, from new prototypes to established codebases
>
> --------------------------------------------------------------------------------
> BMAD-METHOD/CHANGELOG.md at main · bmad-code-org/BMAD-METHOD · GitHub (https://opencode.terrychan.org/bmad-code-org/BMAD-METHOD/blob/main/CHANGELOG.md)
> 【turn790488search42】 [wordlim: 200] Crawled: today; It picks a note template by its description; core tools ship five, the BMad Method adds five for agile meetings and product discovery, and teams add their own from a folder, a GitHub URL or a module. ... Skills stop guessing and start reading evidence. `bmad-retrospective` judges an epic against its own artifacts, requires a source reference on every finding, and rejects an epic with unfinished stories instead of closing quietly. `bmad-sprint-planning` moves epic parsing, status merging, and summary computation into a tested Python script. `bmad-project-context` replaces generated documentation with one verified block in the repository's `AGENTS.md`. ... CIS (Creative Intelligence Suite)  | Published as npm package  | `bmad-code-org/bmad-module-creative-intelligence-suite` ...   * README overhaul with numbered command flows and prominent `bmad-help` callout
>
> --------------------------------------------------------------------------------
> GitHub - bmad-code-org/BMAD-METHOD at blog.ant.org · GitHub (https://github.com/bmad-code-org/BMAD-METHOD?ref=blog.ant.org)
> 【turn790488search43】 [wordlim: 200] Crawled: 2 days ago;     npx skills add bmad-code-org/BMAD-METHOD --skill '*' ...   * GitHub Issues — Report bugs and request features. ... Star the repository, buy me a coffee, or email contact@bmadcode.com for corporate sponsorship.
>
> --------------------------------------------------------------------------------
> GitHub - hannody/spec-kit: Spec-driven development kit: constitution + spec→plan→implement loop + ADRs + checkpoint-driven implementation. Language/domain-agnostic. · GitHub (https://github.com/hannody/spec-kit)
> 【turn790488search44】 [wordlim: 200] Crawled: last month;       adr/README.md  adr/0000-template.md                  # Architecture Decision Records ... > There is also a Unity/C# game-dev variant of this kit (`unity-spec-kit`) with the same loop and a constitution retargeted to game development (assembly-definition boundaries, EditMode/PlayMode tests, frame-time/GC budgets, ScriptableObject conventions).
>
> --------------------------------------------------------------------------------
> Add Modules | BMad Method (https://docs.bmad-method.org/customize/add-modules/)
> 【turn790488search45】 [wordlim: 200] Crawled: yesterday; Founder, code `founder`  | Nadia the Founder Advisor, an experienced founder who coaches you from idea to raise: seventeen business documents from a startup diagnostic to a board pack, the money math by script, customer evidence, investor pipeline and meetings, term sheets, and an investor pitch room, with the company’s facts kept in one record folder  | This repository: `npx skills add bmad-code-org/BMAD-METHOD --skill bmad-founder-agent-advisor --skill bmad-facilitate` ... Each repository’s README says which BMad version it supports.
>
> --------------------------------------------------------------------------------
> GitHub - github/spec-kit at ssp.sh · GitHub (https://github.com/github/spec-kit?ref=ssp.sh)
> 【turn790488search46】 [wordlim: 200] Crawled: today; Spec Kit is an open source toolkit that gives AI coding agents structured processes, reusable templates, and documented outcomes. ... This example uses GitHub Copilot's default skills syntax. ...     `/speckit-constitution Create principles focused on code quality, testing, and maintainability.
>
> --------------------------------------------------------------------------------
> spec-kit/README.md at main · github/spec-kit · GitHub (https://git.littlebell.top/github/spec-kit/blob/main/README.md)
> 【turn790488search47】 [wordlim: 200] Crawled: last week; Run these commands in your terminal to install Spec Kit and create a project. ... This example uses GitHub Copilot's default skills syntax. ...     `/speckit-constitution Create principles focused on code quality, testing, and maintainability.
>
> --------------------------------------------------------------------------------
> Give Claude Code Superpowers (https://assets.skool.com/f/b51c57150c70495899bf4bc8aaee8166/16214ebd3e0744be8f0272fec9208ae37b913ea08a9543de8ba6619272431c5c)
> 【turn790488search48】 [wordlim: 200] Lab skills exist. `github.com/obra/superpowers-lab` has 4 experimental skills: `finding-duplicate-functions` (semantic code deduplication via LLM clustering), `mcp-cli` (on-demand MCP server invocation without pre-loading), `using-tmux-for-interactive-commands` (automates interactive CLI tools via tmux), and `windows-vm` (creates headless Windows 11 VMs in Docker with SSH).
>
> Community skills repo. `github.com/obra/superpowers-skills`.
>
> --------------------------------------------------------------------------------
> OpenSpec: Spec-driven development (SDD) for AI coding assistants (72k stars) (https://www.reddit.com/r/BestGitHubRepos/comments/1x87kz9/openspec_specdriven_development_sdd_for_ai_coding/)
> 【turn790488reddit49】 [wordlim: 200] Published: 3 weeks ago; *All text below is quoted directly from the project README. ... https://github.com/Fission-AI/OpenSpec
>
> --------------------------------------------------------------------------------
> Spec Kit 346 Scholarly Output (https://topperlearning.motion.ac.in/42667918/oslidem/vconsistr/yassiste/spec%2Bkit%2B346%2Bscholarly%2Boutput%2Bassessment%2Bactivities.pdf)
> 【turn790488search50】 [wordlim: 200] Published: 10 months ago; Ever 5 minutes, 20 seconds - OpenSpec by Fission AI is simplifying spec ... GitHub Spec Kit now GETS ALL AGENTS - GitHub Spec Kit now GETS ALL
>
> --------------------------------------------------------------------------------
> The repos that give OpenAI Codex real superpowers (https://www.reddit.com/r/WebAfterAI/comments/1upze4z/the_repos_that_give_openai_codex_real_superpowers/)
> 【turn790488reddit51】 [wordlim: 200] Published: 4 months ago; Here are the repos that do each, grouped by the superpower they grant, with the catch on each because none of these is free of tradeoffs. ... Repo: https://github.com/obra/superpowers ... It packages composable markdown skills (brainstorming, planning, test-driven development, debugging, code review) that a coding agent follows automatically as mandatory workflows, and it ships plugin folders for many agents including Codex CLI and the Codex app.
>
> --------------------------------------------------------------------------------
> Spec-driven development is underhyped! Here's how you build better with Cursor! (https://www.reddit.com/r/cursor/comments/1nomd8t/specdriven_development_is_underhyped_heres_how/)
> 【turn790488reddit52】 [wordlim: 200] Published: 1.1 years ago; I have a section in the readme exactly for this: https://github.com/Fission-AI/OpenSpec?
>
> --------------------------------------------------------------------------------
> Obra Superpowers port for Antigravity 2.0 (https://www.reddit.com/r/google_antigravity/comments/1tr5xz5/obra_superpowers_port_for_antigravity_20/)
> 【turn790488reddit53】 [wordlim: 200] Published: 5 months ago; For full changes from the original superpowers check the RELEASE_NOTES.md file (URL)
>
> Instructions on how to set this up are on the GitHub repo below. ... * **No more tool mapping** — skills use `view_file`, `run_command`, `invoke_subagent` directly. ... * **New capabilities** — native `generate_image` mockups in brainstorming, `browser-testing` skill for UI verification, async subagent coordination with `manage_task` and `schedule`, rich plan formatting with Mermaid diagrams and diff blocks
> ````
>
> - Ran `mkdir -p /workspace/work/market-review && python - <<'PY'
> from concurrent.futures import ThreadPoolExecutor, as_completed
> from pathlib import Path
> import json
> import urllib.request
>
> root = Path('/workspace/work/market-review')
> repos = ['vlv-code/meta-project', 'obra/superpowers', 'bmad-code-org/BMAD-METHOD', 'github/spec-kit', 'Fission-AI/OpenSpec', 'dyoshikawa/rulesync', 'thedotmack/claude-mem', 'steveyegge/beads']
>
> def get(url):
>     req = urllib.request.Request(url, headers={'User-Agent': 'repository-comparison', 'Accept': 'application/vnd.github+json'})
>     with urllib.request.urlopen(req, timeout=20) as response:
>         return response.read()
>
> def inspect(repo):
>     try:
>         meta = json.loads(get('https://api.github.com/repos/' + repo))
>         name = repo.replace('/', '__')
>         md_url = 'https://raw.githubusercontent.com/' + meta['full_name'] + '/' + meta['default_branch'] + '/README.md'
>         readme = get(md_url).decode('utf-8')
>         (root / (name + '.md')).write_text(readme)
>         result = {k: meta.get(k) for k in ['full_name', 'html_url', 'description', 'stargazers_count', 'forks_count', 'archived', 'default_branch', 'pushed_at']}
>         result['license'] = (meta.get('license') or {}).get('spdx_id')
>         result['readme_url'] = md_url
>         (root / (name + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2))
>         headings = [line[:150] for line in readme.splitlines() if line.startswith(('# ', '## ', '### '))]
>         return {'metadata': result, 'readme_lines': len(readme.splitlines()), 'headings': headings[:32]}
>     except Exception as exc:
>         return {'repo': repo, 'error': str(exc)}
>
> with ThreadPoolExecutor(max_workers=4) as pool:
>     for result in as_completed([pool.submit(inspect, repo) for repo in repos]):
>         print(json.dumps(result.result(), ensure_ascii=False))
> PY`
>
> <details><summary>Explored 10 files</summary>
>
> - Read `./dyoshikawa__rulesync.md`
> - Read `./steveyegge__beads.md`
> - Read `./steveyegge__beads.md`
> - Read `./bmad-code-org__BMAD-METHOD.md`
> - Read `./obra__superpowers.md`
> - Read `./obra__superpowers.md`
> - Read `./github__spec-kit.md`
> - Read `./Fission-AI__OpenSpec.md`
> - Read `./thedotmack__claude-mem.md`
> - Read `./thedotmack__claude-mem.md`
>
> </details>
>
> </details>
>
> Ближайшие аналоги уже закрывают многие отдельные части идеи: Rulesync переносит правила и хуки между средами, Claude-Mem собирает память сессий, Superpowers и BMAD задают процесс разработки. Поэтому преимущество meta-project нужно искать в удобстве общей связки и проверяемых границах. Отдельно сравню цену этой связки в установке и сопровождении.
>
> <details><summary>Explored 4 files, ran a command, called 2 tools</summary>
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "open": [
>     {
>       "ref_id": "https://github.com/cline/cline/blob/main/docs/best-practices/memory-bank.mdx"
>     },
>     {
>       "ref_id": "https://github.com/buildermethods/agent-os"
>     },
>     {
>       "ref_id": "https://rulesync.dyoshikawa.com/reference/supported-tools.html"
>     }
>   ],
>   "response_length": "long"
> }
> ```
>
> ````text
> cline/docs/best-practices/memory-bank.mdx at main · cline/cline · GitHub (https://github.com/cline/cline/blob/main/docs/best-practices/memory-bank.mdx)
> 【turn384463view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://github.com/cline/cline/blob/main/docs/best-practices/memory-bank.mdx","lineno":null}); Total lines: 308
> L0: 【0†Skip to content】
> L1: ## Navigation Menu
> L2: 
> L3:   * Products
> L4: 
> L5:     *       * 【1†GitHub Repository hosting, code review, and collaboration】
> L6:       * 【2†Copilot AI coding agent for tasks, projects, and automated work】
> L7: 
> L8:     * Build & Ship
> L9:       * 【3†Actions CI/CD and automation】
> L10:       * 【4†Code Quality Quality analysis, fixes, and enforcement】
> L11:       * 【5†Codespaces Cloud development environments】
> L12:     * Secure
> L13:       * 【6†Code Security Vulnerability detection and remediation】
> L14:       * 【7†Secret Protection Secret scanning and leak prevention】
> L15: 
> L16: 【8†All Features】
> L17: 
> L18:   * Developers
> L19: 
> L20:     * Learn
> L21:       * 【9†Documentation†docs.github.com】
> L22:       * 【10†Training†learn.github.com】
> L23:       * 【11†Certifications†learn.github.com】
> L24: 
> L25:     * Build
> L26:       * 【12†Build with Copilot】
> L27:       * 【13†Customize Copilot†docs.github.com】
> L28:       * 【14†Integrations】
> L29:     * Explore
> L30:       * 【15†Trending repos】
> L31:       * 【16†GitHub Sponsors】
> L32:       * 【17†Developer articles】
> L33: 
> L34:     *       * 【18†Changelog Your source for the latest features, improvements, and fixes across GitHub products, all in one place.†github.blog】
> L35: 
> L36:   * Businesses
> L37: 
> L38:     * By Stage
> L39:       * 【19†Enterprises】
> L40:       * 【20†Team】
> L41:       * 【21†Startups】
> L42:       * 【22†Nonprofits】
> L43:     * By Industry
> L44:       * 【23†Healthcare】
> L45:       * 【24†Financial services】
> L46:       * 【25†Manufacturing】
> L47:       * 【26†Government】
> L48:       * 【27†See all industries】
> L49: 
> L50:     * Evaluate GitHub
> L51:       * 【28†Why GitHub】
> L52:       * 【29†Customer Stories】
> L53:       * 【30†Business insights】
> L54:       * 【31†Trust Center】
> L55: 
> L56:     * Add-ons
> L57:       * 【32†GitHub Advanced Security Enterprise-grade code security】
> L58:       * 【33†Copilot for business Enterprise-grade AI features】
> L59:       * 【34†Premium Support Enterprise-grade 24/7 support】
> L60:   * Resources
> L61: 
> L62:     * Learn & Connect
> L63:       * 【9†Documentation†docs.github.com】
> L64:       * 【35†Resource center】
> L65:       * 【36†Blog†github.blog】
> L66:       * 【37†Events & webinars】
> L67:       * 【38†Community Forum】
> L68:       * 【29†Customer Stories】
> L69:       * 【14†Integrations】
> L70: 
> L71:     * Support
> L72:       * 【39†Customer support†help.github.com】
> L73:       * 【10†Training†learn.github.com】
> L74:       * 【40†GitHub Status†www.githubstatus.com】
> L75: 
> L76:     * Company
> L77:       * 【41†About】
> L78:       * 【42†Partners】
> L79:       * 【18†Changelog†github.blog】
> L80:     *       * 【43†GitHub Universe The event for developers, by developers — talks, workshops, and what’s next for GitHub.†githubuniverse.com】
> L81: 
> L82:   * 【44†Pricing】
> L83: 
> L84: Search`/`
> L85: 
> L86: 【45†Sign in】
> L87: 
> L88: 【46†Sign up】
> L89: 
> L90: Appearance settings
> L91: 
> L92: You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert
> L93: 
> L94:   1. 【47†cline】
> L95:   2. 【48†cline】
> L96: ## Repository navigation
> L97: 
> L98:   *   * 【48†Code】
> L99:   * 【49†Issues 927 (927)】
> L100:   * 【50†Pull requests 831 (831)】
> L101:   * 【51†Discussions】
> L102:   * 【52†Actions】
> L103:   * 【53†Projects】
> L104:   * 【54†Wiki】
> L105:   * 【55†Security and quality 3 (3)】
> L106:   * 【56†Insights】
> L107: 
> L108: More items
> L109: 
> L110: ## Files Expand file tree
> L111: 
> L112: main
> L113: 
> L114: ## Breadcrumbs
> L115: 
> L116:   1. 【57†cline】
> L117:   2. /【58†docs】
> L118:   3. /【59†best-practices】
> L119: 
> L120: /
> L121: 
> L122: # memory-bank.mdx
> L123: 
> L124: Copy path
> L125: 
> L126: [Input: Go to file]
> L127: 
> L128: Blame More file actions
> L129: 
> L130: Blame More file actions
> L131: 
> L132: ## Latest commit
> L133: 
> L134: 
> L135: 
> L136: ## History
> L137: 
> L138: History
> L139: 
> L140: main
> L141: ## Breadcrumbs
> L142: 
> L143:   1. 【57†cline】
> L144:   2. /【58†docs】
> L145:   3. /【59†best-practices】
> L146: 
> L147: /
> L148: 
> L149: # memory-bank.mdx
> L150: 
> L151: Copy path
> L152: 
> L153: Top
> L154: ## File metadata and controls
> L155: 
> L156:   * Preview
> L157: 
> L158:   * Code
> L159: 
> L160:   * Blame
> L161: 
> L162: 163 lines (121 loc) · 7.08 KB
> L163: 
> L164: 【60†Raw】
> L165: 
> L166: Copy raw file
> L167: 
> L168: Download raw file
> L169: 
> L170: Outline
> L171: 
> L172: Edit and raw actions
> L173: 
> L174: title  | Memory Bank
> L175: sidebarTitle  | Memory Bank
> L176: description  | A structured documentation system that helps Cline maintain context across sessions.
> L177: Memory Bank is a documentation methodology that transforms Cline from a stateless assistant into a persistent development partner. Through structured markdown files, Cline can "remember" your project details across sessions.
> L178: ## Quick Setup
> L179: 
> L180:   1. Copy the 【61†custom instructions below】
> L181:   2. Add them to a 【62†Cline Rules file】, such as `.clinerules/memory-bank.md`
> L182:   3. Ask Cline to "initialize memory bank"
> L183: ## How It Works
> L184: Memory Bank files are regular markdown files in your project that both you and Cline can access. They're organized hierarchically to build a complete picture of your project:
> L185: 
> L186:     `memory-bank/
> L187:     ├── projectbrief.md      # Foundation document
> L188:     ├── productContext.md    # Why this project exists
> L189:     ├── activeContext.md     # Current work focus
> L190:     ├── systemPatterns.md    # Architecture & patterns
> L191:     ├── techContext.md       # Tech stack & setup
> L192:     └── progress.md          # Status & milestones
> L193:     `
> L194: ## Core Files
> L195: 
> L196: File  | Purpose
> L197: --- | ---
> L198: `projectbrief.md`  | Foundation document with core requirements and goals
> L199: `productContext.md`  | Why the project exists, problems it solves, UX goals
> L200: `activeContext.md`  | Current focus, recent changes, next steps (updates most frequently)
> L201: `systemPatterns.md`  | Architecture, design patterns, component relationships
> L202: `techContext.md`  | Tech stack, setup, constraints, dependencies
> L203: `progress.md`  | What works, what's left, known issues
> L204: ## Key Commands
> L205: 
> L206:   * "follow your custom instructions" - Tells Cline to read Memory Bank and continue where you left off
> L207:   * "initialize memory bank" - Creates the initial structure for a new project
> L208:   * "update memory bank" - Triggers a full documentation review and update
> L209: 
> L210: These work alongside Cline's built-in 【63†slash commands】. In particular, 【64†`/newtask`】 and 【65†`/smol`】 help you manage context windows without losing progress.
>
> --------------------------------------------------------------------------------
> GitHub - buildermethods/agent-os: Agent OS is a system for injecting your codebase standards and writing better specs for spec-driven development. · GitHub (https://github.com/buildermethods/agent-os)
> 【turn384463view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://github.com/buildermethods/agent-os","lineno":null}); Total lines: 273
> L0: 【0†Skip to content】
> L1: ## Navigation Menu
> L2: 
> L3:   * Products
> L4: 
> L5:     *       * 【1†GitHub Repository hosting, code review, and collaboration】
> L6:       * 【2†Copilot AI coding agent for tasks, projects, and automated work】
> L7: 
> L8:     * Build & Ship
> L9:       * 【3†Actions CI/CD and automation】
> L10:       * 【4†Code Quality Quality analysis, fixes, and enforcement】
> L11:       * 【5†Codespaces Cloud development environments】
> L12:     * Secure
> L13:       * 【6†Code Security Vulnerability detection and remediation】
> L14:       * 【7†Secret Protection Secret scanning and leak prevention】
> L15: 
> L16: 【8†All Features】
> L17: 
> L18:   * Developers
> L19: 
> L20:     * Learn
> L21:       * 【9†Documentation†docs.github.com】
> L22:       * 【10†Training†learn.github.com】
> L23:       * 【11†Certifications†learn.github.com】
> L24: 
> L25:     * Build
> L26:       * 【12†Build with Copilot】
> L27:       * 【13†Customize Copilot†docs.github.com】
> L28:       * 【14†Integrations】
> L29:     * Explore
> L30:       * 【15†Trending repos】
> L31:       * 【16†GitHub Sponsors】
> L32:       * 【17†Developer articles】
> L33: 
> L34:     *       * 【18†Changelog Your source for the latest features, improvements, and fixes across GitHub products, all in one place.†github.blog】
> L35: 
> L36:   * Businesses
> L37: 
> L38:     * By Stage
> L39:       * 【19†Enterprises】
> L40:       * 【20†Team】
> L41:       * 【21†Startups】
> L42:       * 【22†Nonprofits】
> L43:     * By Industry
> L44:       * 【23†Healthcare】
> L45:       * 【24†Financial services】
> L46:       * 【25†Manufacturing】
> L47:       * 【26†Government】
> L48:       * 【27†See all industries】
> L49: 
> L50:     * Evaluate GitHub
> L51:       * 【28†Why GitHub】
> L52:       * 【29†Customer Stories】
> L53:       * 【30†Business insights】
> L54:       * 【31†Trust Center】
> L55: 
> L56:     * Add-ons
> L57:       * 【32†GitHub Advanced Security Enterprise-grade code security】
> L58:       * 【33†Copilot for business Enterprise-grade AI features】
> L59:       * 【34†Premium Support Enterprise-grade 24/7 support】
> L60:   * Resources
> L61: 
> L62:     * Learn & Connect
> L63:       * 【9†Documentation†docs.github.com】
> L64:       * 【35†Resource center】
> L65:       * 【36†Blog†github.blog】
> L66:       * 【37†Events & webinars】
> L67:       * 【38†Community Forum】
> L68:       * 【29†Customer Stories】
> L69:       * 【14†Integrations】
> L70: 
> L71:     * Support
> L72:       * 【39†Customer support†help.github.com】
> L73:       * 【10†Training†learn.github.com】
> L74:       * 【40†GitHub Status†www.githubstatus.com】
> L75: 
> L76:     * Company
> L77:       * 【41†About】
> L78:       * 【42†Partners】
> L79:       * 【18†Changelog†github.blog】
> L80:     *       * 【43†GitHub Universe The event for developers, by developers — talks, workshops, and what’s next for GitHub.†githubuniverse.com】
> L81: 
> L82:   * 【44†Pricing】
> L83: 
> L84: Search`/`
> L85: 
> L86: 【45†Sign in】
> L87: 
> L88: 【46†Sign up】
> L89: 
> L90: Appearance settings
> L91: 
> L92: You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert
> L93: 
> L94:   1. 【47†buildermethods】
> L95:   2. 【48†agent-os】
> L96: ## Repository navigation
> L97: 
> L98:   *   * 【48†Code】
> L99:   * 【49†Issues】
> L100:   * 【50†Pull requests 1 (1)】
> L101:   * 【51†Discussions】
> L102:   * 【52†Actions】
> L103:   * 【53†Security and quality】
> L104:   * 【54†Insights】
> L105: 
> L106: More items
> L107: 
> L108: 【55†Image: buildermethods†avatars.githubusercontent.com】
> L109: 
> L110: 【48†agent-os】
> L111: 
> L112: Public
> L113: 
> L114:   * 【56†Notifications】You must be signed in to change notification settings
> L115:   * 【56†Fork 832 (832)】
> L116:   * 【56†Star 5.6k (5.6k)】You must be signed in to star a repository
> L117: ## About
> L118: 
> L119: Agent OS is a system for injecting your codebase standards and writing better specs for spec-driven development.
> L120: 
> L121: 【57†buildermethods.com/agent-os†buildermethods.com】
> L122: 
> L123: ### Resources
> L124: 
> L125: 【58†Readme】
> L126: 
> L127: 【59†MIT license】
> L128: 
> L129: ### Code of conduct
> L130: 
> L131: 【60†Code of conduct】
> L132: 
> L133: ### Contributing
> L134: 
> L135: 【61†Contributing】
> L136: 
> L137: 【62†Activity】
> L138: 
> L139: 【63†Custom properties】
> L140: 
> L141: ### Stars
> L142: 
> L143: 5.6k stars
> L144: 
> L145: ### Watchers
> L146: 
> L147: 103 watching
> L148: ### Forks
> L149: 
> L150: 【64†832 forks】
> L151: 
> L152: 【65†Report repository】
> L153: 
> L154: main
> L155: 
> L156: 【66†Branches】【67†Tags】
> L157: 
> L158: [Input: Go to file]
> L159: 
> L160: Go to file
> L161: 
> L162: Code
> L163: 
> L164: Open more actions menu
> L165: 
> L166: ## Latest commit
> L167: 
> L168: 
> L169: 
> L170: ## History
> L171: 
> L172: 132 Commits
> L173: ## Folders and files
> L174: Name  | Name  | Last commit message  | Last commit date
> L175: --- | --- | --- | ---
> L176: 【68†.github】  | 【68†.github】  |    |
> L177: 【69†commands/agent-os】  | 【69†commands/agent-os】  |    |
> L178: 【70†profiles/default/global】  | 【70†profiles/default/global】  |    |
> L179: 【71†scripts】  | 【71†scripts】  |    |
> L180: 【72†.gitignore】  | 【72†.gitignore】  |    |
> L181: 【73†CHANGELOG.md】  | 【73†CHANGELOG.md】  |    |
> L182: 【74†LICENSE】  | 【74†LICENSE】  |    |
> L183: 【75†README.md】  | 【75†README.md】  |    |
> L184: 【76†config.yml】  | 【76†config.yml】  |    |
> L185: ## Repository files navigation
> L186: 
> L187:   *   * 【77†README】
> L188:   * 【77†Code of conduct】
> L189:   * 【77†Contributing】
> L190:   * 【77†MIT license】
> L191: 
> L192: More items
> L193: ## Agents that build the way you would
> L194: 
> L195: 【57†Agent OS†buildermethods.com】 helps you shape better specs, keeps agents aligned in a lightweight system that fits how you already build.
> L196: 
> L197: Works alongside Claude Code, Cursor, Antigravity, and other AI tools. Any language, any framework.
> L198: 
> L199: Core capabilities:
> L200:   * Discover Standards — Extract patterns and conventions from your codebase into documented standards
> L201:   * Deploy Standards — Intelligently inject relevant standards based on what you're building
> L202:   * Shape Spec — Create better plans that lead to better builds
> L203:   * Index Standards — Keep your standards organized and discoverable
> L204: 
> L205: * * *
> L206: ### Documentation & Installation
> L207: 
> L208: Docs, installation, usage, & best practices 👉 【57†It's all here†buildermethods.com】
> L209: 
> L210: * * *
> L211: 
> L212: ### Follow updates & releases
> L213: 
> L214: Read the 【73†changelog】
> L215: 
> L216: 【57†Subscribe to be notified of major new releases of Agent OS†buildermethods.com】
> L217: 
> L218: * * *
> L219: ### Created by Brian Casel @ Builder Methods
> L220: 
> L221: Created by Brian Casel, the creator of 【78†Builder Methods†buildermethods.com】, where Brian helps professional software developers and teams build with AI.
> L222: 
> L223: Get Brian's free resources on building with AI:
> L224: 
> L225:   * 【78†Builder Briefing newsletter†buildermethods.com】
> L226:   * 【79†YouTube†youtube.com】
> L227: 
> L228: Join 【80†Builder Methods Pro†buildermethods.com】 for official support and connect with our community of AI-first builders:
>
> --------------------------------------------------------------------------------
> Supported Tools and Features | Rulesync (https://rulesync.dyoshikawa.com/reference/supported-tools.html)
> 【turn384463view2】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://rulesync.dyoshikawa.com/reference/supported-tools.html","lineno":null}); Total lines: 197
> L0: 【0†Rulesync】
> L1: 
> L2: Search```K`
> L3: 
> L4: 【1†Guide】【2†Reference】【3†API】
> L5: 
> L6: Links
> L7: 
> L8: 【4†npm†www.npmjs.com】
> L9: 
> L10: 【5†Changelog†github.com】
> L11: 
> L12: Appearance
> L13: 
> L14: Menu
> L15: 
> L16: [Button: Return to top]
> L17: 
> L18: ## Getting Started
> L19: 
> L20: 【1†Installation】
> L21: 
> L22: 【6†Quick Start】
> L23: 
> L24: ## Guide
> L25: 
> L26: 【7†Why Rulesync?】
> L27: 
> L28: 【8†Configuration】
> L29: 
> L30: 【9†Plugin Packaging】
> L31: 
> L32: 【10†Global Mode】
> L33: 
> L34: 【11†Separate Input Root】
> L35: 
> L36: 【12†Simulated Features】
> L37: 
> L38: 【13†Declarative Sources】
> L39: 
> L40: 【14†Official Skills】
> L41: 
> L42: 【15†Dry Run】
> L43: 
> L44: 【16†Case Studies】
> L45: ## Reference
> L46: 
> L47: 【2†Supported Tools】
> L48: 
> L49: 【17†CLI Commands】
> L50: 
> L51: 【18†File Formats】
> L52: 
> L53: 【19†Command Syntax】
> L54: 
> L55: 【20†MCP Server】
> L56: 
> L57: ## API
> L58: 
> L59: 【3†Programmatic API】
> L60: 
> L61: 【21†FAQ】
> L62: 
> L63: On this page
> L64: # Supported Tools and Features 【22†​】
> L65: 
> L66: Rulesync supports both generation and import for All of the major AI coding tools:
> L67: Tool  | --targets  | rules  | ignore  | mcp  | commands  | subagents  | skills  | hooks  | permissions  | checks
> L68: --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
> L69: AGENTS.md  | agentsmd  | ✅  |  |  | 🎮  | 🎮  | 🎮  |  |  |
> L70: AgentsSkills  | agentsskills  |  |  |  |  |  | ✅ 🌏  |  |  |
> L71: Amp  | amp  | ✅ 🌏  |  | ✅ 🌏  |  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏
> L72: IBM Bob  | bob  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  | 🌏  |
> L73: Claude Code  | claudecode  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L74: Claude Code plugin  | claudecode-plugin  |  |  | ✅  | ✅  | ✅  | ✅  | ✅  |  |
> L75: CodeBuddy Code  | codebuddy  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L76: Codewhale  | codewhale  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L77: Codex CLI  | codexcli  | ✅ 🌏  |  | ✅ 🌏 🔧  | 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L78: Command Code  | commandcode  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L79: GitHub Copilot  | copilot  | ✅ 🌏  |  | ✅  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅  |
> L80: GitHub Copilot CLI  | copilotcli  | ✅ 🌏  |  | ✅ 🌏 🔧  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L81: Crush  | crush  | ✅ 🌏  | ✅  | ✅ 🌏 🔧  |  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L82: Goose  | goose  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | 🌏  | 🌏
> L83: Hermes Agent  | hermesagent  | ✅  | ✅  | 🌏 🔧  | 🌏  | ✅ 🌏  | 🌏  | 🌏  | 🌏  | ✅
> L84: Grok CLI  | grokcli  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L85: Cursor  | cursor  | ✅  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅
> L86: deepagents-cli  | deepagents  | ✅ 🌏  |  | ✅ 🌏 🔧  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | 🌏  |
> L87: Factory Droid  | factorydroid  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅
> L88: Firebender  | firebender  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |  |
> L89: OpenCode  | opencode  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L90: OpenCode V1  | opencodev1  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L91: OpenClaw  | openclaw  | ✅ 🌏  |  | 🌏 🔧  |  |  |  |  |  |
> L92: MiMo Code  | mimocode  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L93: GitLab Duo CLI  | gitlabduo  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  |  | ✅
> L94: Cline  | cline  | ✅ 🌏  | ✅  | 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅  |
> L95: Kilo Code  | kilo  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅
> L96: Kimi Code  | kimi-code  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | 🌏  | 🌏  |
> L97: Kimi Code plugin  | kimi-code-plugin  | ✅  |  |  | ✅  | ✅  | ✅  |  |  |
> L98: Roo Code ⚠️  | roo  | ✅ 🌏  | ✅  | ✅ 🔧  | ✅ 🌏  | ✅  | ✅ 🌏  |  | ✅  |
> L99: Zoo Code  | zoocode  | ✅ 🌏  | ✅  | ✅ 🔧  | ✅ 🌏  | ✅  | ✅ 🌏  |  | ✅  |
> L100: Rovodev (Atlassian) ⚠️  | rovodev  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |  | ✅ 🌏  | ✅
> L101: Takt  | takt  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏
> L102: Trae  | trae  | ✅  | ✅  | ✅  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | 🌏  |
> L103: Tabnine CLI ⚠️  | tabnine  | ✅ 🌏  | ✅  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L104: Continue ⚠️  | continue  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | 🌏  |
> L105: Snowflake Cortex Code  | cortexcode  | ✅  |  | 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |  |
> L106: Vibe Code  | vibe  | ✅ 🌏  | ✅  | ✅ 🌏 🔧  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L107: Vibe Code plugin  | vibe-plugin  |  |  | ✅  |  | ✅  | ✅  | ✅  |  |
> L108: Qoder  | qoder  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L109: Qwen Code  | qwencode  | ✅ 🌏  | ✅  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅
> L110: Meta Muse Code  | musecode  | ✅  |  | 🌏  |  |  | ✅ 🌏  |  |  |
> L111: Reasonix  | reasonix  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L112: Codebuff (Freebuff)  | codebuff  | 🌏  | ✅  | ✅ 🌏  |  |  |  |  |  |
> L113: Kiro ⚠️  | kiro  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅  | ✅  | ✅  | ✅  | ✅  |
> L114: Kiro CLI  | kiro-cli  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L115: Kiro IDE  | kiro-ide  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L116: Letta Code  | lettacode  |  | ✅  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L117: Google Antigravity IDE  | antigravity-ide  | ✅ 🌏  |  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅  |
> L118: Google Antigravity CLI  | antigravity-cli  | ✅ 🌏  | ✅  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | 🌏  |
> L119: Google Antigravity plugin  | antigravity-plugin  | ✅  |  | ✅ 🔧  |  | ✅  | ✅  | ✅  |  |
> L120: JetBrains AI Assistant  | aiassistant  | ✅  | ✅  | ✅ 🌏  |  |  | ✅  |  |  |
> L121: Gemini in Android Studio  | androidstudio  |  | ✅  |  |  |  | ✅ 🌏  |  |  |
> L122: JetBrains Junie  | junie  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | 🌏  | 🌏  |
> L123: AugmentCode  | augmentcode  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅
> L124: AugmentCode plugin  | augmentcode-plugin  | ✅  |  | ✅  | ✅  | ✅  | ✅  | ✅  |  |
> L125: Devin Desktop  | devin  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏 🔧  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> L126: Devin plugin  | devin-plugin  | ✅  |  | ✅ 🔧  |  | ✅  | ✅  | ✅  |  |
> L127: Warp  | warp  | ✅ 🌏  | ✅  | ✅ 🌏  | ✅ 🌏  |  | ✅ 🌏  |  | 🌏  |
> L128: Warp Agent CLI  | warpcli  |  |  | 🌏  |  |  |  |  | 🌏  |
> L129: Xum  | xum  | ✅ 🌏  |  | ✅ 🌏 🔧  |  | ✅ 🌏  | ✅ 🌏  |  |  |
> L130: Replit  | replit  | ✅  |  |  |  |  | ✅ 🌏  |  |  |
> L131: Pi Coding Agent  | pi  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  |  | ✅ 🌏  | ✅ 🌏  | ✅ 🌏  |
> ````
>
> <details><summary>Explored 5 files</summary>
>
> - Read `./dyoshikawa__rulesync.md`
> - Read `./steveyegge__beads.md`
> - Read `./steveyegge__beads.md`
> - Read `./github__spec-kit.md`
> - Read `./Fission-AI__OpenSpec.md`
>
> </details>
>
> - Ran `python - <<'PY'
> from pathlib import Path
> import urllib.request
> root = Path('/workspace/work/market-review')
> refs = [
>  ('agent-os', 'https://raw.githubusercontent.com/buildermethods/agent-os/main/README.md'),
>  ('cline-memory-bank', 'https://raw.githubusercontent.com/cline/cline/main/docs/best-practices/memory-bank.mdx'),
> ]
> for name, url in refs:
>     req = urllib.request.Request(url, headers={'User-Agent': 'repository-comparison'})
>     with urllib.request.urlopen(req, timeout=20) as response:
>         value = response.read().decode('utf-8')
>     (root / (name + '.md')).write_text(value)
>     if name == 'agent-os':
>         print(name, '\n', value[:14000])
>     else:
>         print(name, '\n', '\n'.join(value.splitlines()[:95]))
> PY`
>
> MCP tool call
>
> codex_apps.search_service.web_run
>
> ```json
> {
>   "open": [
>     {
>       "ref_id": "https://agents.md/"
>     },
>     {
>       "ref_id": "https://buildermethods.com/agent-os"
>     }
>   ],
>   "response_length": "short"
> }
> ```
>
> ```text
> AGENTS.md (https://agents.md/)
> 【turn779988view0】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://agents.md/","lineno":null}); Total lines: 172
> L0: # AGENTS.md
> L1: 
> L2: A simple, open format for guiding coding agents, used by over 【0†60k open-source projects†github.com】.
> L3: 
> L4: Think of AGENTS.md as a README for agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project.
> L5: 【1†Explore Examples】【2†View on GitHub†github.com】
> L6: 
> L7:     `
> L8: 
> L9:     # AGENTS.md
> L10: 
> L11: 
> L12: 
> L13:     ## Setup commands
> L14: 
> L15:     - Install deps: `pnpm install`
> L16: 
> L17:     - Start dev server: `pnpm dev`
> L18: 
> L19:     - Run tests: `pnpm test`
> L20: 
> L21: 
> L22: 
> L23:     ## Code style
> L24: 
> L25:     - TypeScript strict mode
> L26: 
> L27:     - Single quotes, no semicolons
> L28: 
> L29:     - Use functional patterns where possible
> L30: 
> L31:     `
> L32: ## Why AGENTS.md?
> L33: 
> L34: README.md files are for humans: quick starts, project descriptions, and contribution guidelines.
> L35: 
> L36: AGENTS.md complements this by containing the extra, sometimes detailed context coding agents need: build steps, tests, and conventions that might clutter a README or aren’t relevant to human contributors.
> L37: 
> L38: We intentionally kept it separate to:
> L39: 
> L40: Give agents a clear, predictable place for instructions.
> L41: 
> L42: Keep READMEs concise and focused on human contributors.
> L43: Provide precise, agent-focused guidance that complements existing README and docs.
> L44: 
> L45: Rather than introducing another proprietary file, we chose a name and format that could work for anyone. If you’re building or using coding agents and find this helpful, feel free to adopt it.
> L46: ## One AGENTS.md works across many agents
> L47: 
> L48: Your agent definitions are compatible with a growing ecosystem of AI coding agents and tools:
> L49: 【3†Codex from OpenAI†openai.com】【4†Jules from Google†jules.google】【5†Factory†factory.ai】【6†Aider†aider.chat】【7†goose†github.com】【8†opencode†opencode.ai】【9†Zed†zed.dev】【10†Warp†docs.warp.dev】【11†VS Code†code.visualstudio.com】【12†Devin from Cognition†devin.ai】【13†Autopilot & Coded Agents from UiPath†uipath.github.io】【14†Junie from JetBrains†jetbrains.com】【3†Codex from OpenAI†openai.com】【4†Jules from Google†jules.google】【5†Factory†factory.ai】【6†Aider†aider.chat】【7†goose†github.com】【8†opencode†opencode.ai】【9†Zed†zed.dev】【10†Warp†docs.warp.dev】【11†VS Code†code.visualstudio.com】【12†Devin from Cognition†devin.ai】【13†Autopilot & Coded Agents from UiPath†uipath.github.io】【14†Junie from JetBrains†jetbrains.com】
> L50: 【15†Amp†ampcode.com】【16†Cursor†cursor.com】【17†RooCode†roocode.com】【18†Gemini CLI from Google†github.com】【19†Kilo Code†kilocode.ai】【20†Phoenix†phoenix.new】【21†Semgrep†semgrep.dev】【22†Coding agent from GitHub Copilot†gh.io】【23†Ona†ona.com】【24†Windsurf from Cognition†windsurf.com】【25†Augment Code†docs.augmentcode.com】【15†Amp†ampcode.com】【16†Cursor†cursor.com】【17†RooCode†roocode.com】【18†Gemini CLI from Google†github.com】【19†Kilo Code†kilocode.ai】【20†Phoenix†phoenix.new】【21†Semgrep†semgrep.dev】【22†Coding agent from GitHub Copilot†gh.io】【23†Ona†ona.com】【24†Windsurf from Cognition†windsurf.com】【25†Augment Code†docs.augmentcode.com】
> L51: [Button: View all supported agents]
> L52: ## Examples
> L53: 
> L54:     `
> L55: 
> L56:     # Sample AGENTS.md file
> L57: 
> L58: 
> L59: 
> L60:     ## Dev environment tips
> L61: 
> L62:     - Use `pnpm dlx turbo run where <project_name>` to jump to a package instead of scanning with `ls`.
> L63: 
> L64:     - Run `pnpm install --filter <project_name>` to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
> L65: 
> L66:     - Use `pnpm create vite@latest <project_name> -- --template react-ts` to spin up a new React + Vite package with TypeScript checks ready.
> L67:     - Check the name field inside each package's package.json to confirm the right name—skip the top-level one.
> L68: 
> L69: 
> L70: 
> L71:     ## Testing instructions
> L72: 
> L73:     - Find the CI plan in the .github/workflows folder.
> L74: 
> L75:     - Run `pnpm turbo run test --filter <project_name>` to run every check defined for that package.
> L76: 
> L77:     - From the package root you can just call `pnpm test`. The commit should pass all tests before you merge.
> L78:     - To focus on one step, add the Vitest pattern: `pnpm vitest run -t "<test name>"`.
> L79: 
> L80:     - Fix any test or type errors until the whole suite is green.
> L81: 
> L82:     - After moving files or changing imports, run `pnpm lint --filter <project_name>` to be sure ESLint and TypeScript rules still pass.
> L83: 
> L84:     - Add or update tests for the code you change, even if nobody asked.
> L85: 
> L86: 
> L87: 
> L88:     ## PR instructions
> L89: 
> L90:     - Title format: [<project_name>] <Title>
> L91:     - Always run `pnpm lint` and `pnpm test` before committing.
> L92: 
> L93:     `
> L94: 【26†openai/codex General-purpose CLI tooling for AI coding agents.Rust+ 722†github.com】【27†apache/airflow Platform to programmatically author, schedule, and monitor workflows.Python+ 4797†github.com】【28†temporalio/sdk-java Java SDK for Temporal, workflow orchestration defined in code.Java+ 164†github.com】【29†PlutoLang/Pluto A superset of Lua 5.4 with a focus on general-purpose programming.C+++ 8†github.com】
> L95: 
> L96: 【0†View 60k+ examples on GitHub†github.com】
> L97: ## How to use AGENTS.md?
> L98: 
> L99: ### 1. Add AGENTS.md
> L100: 
> L101: Create an AGENTS.md file at the root of the repository. Most coding agents can even scaffold one for you if you ask nicely.
> L102: 
> L103: ### 2. Cover what matters
> L104: 
> L105: Add sections that help an agent work effectively with your project. Popular choices:
> L106: 
> L107:   * Project overview
> L108:   * Build and test commands
> L109:   * Code style guidelines
> L110:   * Testing instructions
> L111:   * Security considerations
> L112: ### 3. Add extra instructions
> L113: 
> L114: Commit messages or pull request guidelines, security gotchas, large datasets, deployment steps: anything you’d tell a new teammate belongs here too.
> L115: ### 4. Large monorepo? Use nested AGENTS.md files for subprojects
> L116: 
> L117: Place another AGENTS.md inside each package. Agents automatically read the nearest file in the directory tree, so the closest one takes precedence and every subproject can ship tailored instructions. For example, at time of writing the main OpenAI repo has 88 AGENTS.md files.
> L118: ## About
> L119: 
> L120: AGENTS.md emerged from collaborative efforts across the AI software development ecosystem, including 【3†OpenAI Codex†openai.com】, 【15†Amp†ampcode.com】, 【4†Jules from Google†jules.google】, 【16†Cursor†cursor.com】, and 【5†Factory†factory.ai】.
> L121: 
> L122: We’re committed to helping maintain and evolve this as an open format that benefits the entire developer community, regardless of which coding agent you use.
> L123: AGENTS.md is now stewarded by the 【30†Agentic AI Foundation†aaif.io】 under the Linux Foundation. 【31†Learn more →†openai.com】
> L124: ## FAQ
> L125: 
> L126: ### Are there required fields?
> L127: 
> L128: No. AGENTS.md is just standard Markdown. Use any headings you like; the agent simply parses the text you provide.
> L129: 
> L130: ### What if instructions conflict?
> L131: 
> L132: The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything.
> L133: 
> L134: ### Will the agent run testing commands found in AGENTS.md automatically?
> L135: 
> L136: Yes—if you list them. The agent will attempt to execute relevant programmatic checks and fix failures before finishing the task.
> L137: ### Can I update it later?
> L138: 
> L139: Absolutely. Treat AGENTS.md as living documentation.
> L140: 
> L141: ### How do I migrate existing docs to AGENTS.md?
> L142: 
> L143: Rename existing files to AGENTS.md and create symbolic links for backward compatibility:
> L144: 
> L145:     `
> L146: 
> L147:     mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md
> L148: 
> L149:     `
> L150: 
> L151: ### How do I configure Aider?
> L152: 
> L153: Configure Aider to use AGENTS.md in `.aider.conf.yml`:
> L154: 
> L155:     `
> L156: 
> L157:     read: AGENTS.md
> L158: 
> L159:     `
> L160: ### How do I configure Gemini CLI?
> L161: 
> L162: Configure Gemini CLI to use AGENTS.md in `.gemini/settings.json`:
> L163: 
> L164:     `
> L165: 
> L166:     { "context": { "fileName": "AGENTS.md" }, }
>
> --------------------------------------------------------------------------------
> Agent OS | Coding standards for AI-powered development (https://buildermethods.com/agent-os)
> 【turn779988view1】 [wordlim: 200] Crawled: today; Content type: text/html; Source: open({"ref_id":"https://buildermethods.com/agent-os","lineno":null}); Total lines: 138
> L0:   * 【0†Workshops】
> L1:   * 【1†Community】
> L2:   * 【2†Tools】
> L3:   * 【3†Services】
> L4: 
> L5: 【4†Log in】【1†Join Pro】
> L6: 
> L7: Free Tool
> L8: # Agents that build the way you would
> L9: 
> L10: Agent OS helps you shape better specs, keeps agents aligned in a lightweight system that fits how you already build.
> L11: 
> L12: [Input: Your email address]
> L13: 
> L14: Free & open source. Enter your email for instant access.
> L15: 
> L16: Watch the demo
> L17: 
> L18: On this page / Introduction
> L19: 
> L20: Getting Started
> L21: 
> L22:   * 【5†Introduction】
> L23:   * 【6†Installation】
> L24:   * 【7†Profiles】
> L25:   * 【8†Updating】
> L26:   * 【9†What's New】
> L27: 
> L28: Workflow
> L29:   * 【10†Overview】
> L30:   * 【11†1 Discover standards】
> L31:   * 【12†2 Inject standards】
> L32:   * 【13†3 Product planning】
> L33:   * 【14†4 Shape Spec】
> L34: 
> L35: Concepts
> L36: 
> L37:   * 【15†Overview】
> L38:   * 【16†Standards】
> L39:   * 【17†Standards vs Skills】
> L40:   * 【18†File structure】
> L41:   * 【19†Adaptability】
> L42: 
> L43: Getting Started
> L44: 
> L45:   * 【5†Introduction】
> L46:   * 【6†Installation】
> L47:   * 【7†Profiles】
> L48:   * 【8†Updating】
> L49:   * 【9†What's New】
> L50: 
> L51: Workflow
> L52: 
> L53:   * 【10†Overview】
> L54:   * 【11†1 Discover standards】
> L55:   * 【12†2 Inject standards】
> L56:   * 【13†3 Product planning】
> L57:   * 【14†4 Shape Spec】
> L58: 
> L59: Concepts
> L60:   * 【15†Overview】
> L61:   * 【16†Standards】
> L62:   * 【17†Standards vs Skills】
> L63:   * 【18†File structure】
> L64:   * 【19†Adaptability】
> L65: ## What is Agent OS?
> L66: 
> L67: Every time you prompt an AI coding agent, you’re re-teaching it context that should already be known. The reasoning behind your conventions, the patterns your team refined over time, the architectural decisions that shape everything — none of that comes through when an agent scans your code.
> L68: 
> L69: Agent OS fills that gap. It’s a lightweight system for defining and managing your coding standards in AI-powered development — and in v3, it discovers and documents those standards for you.
> L70: It’s designed to complement tools like Claude Code, Cursor, and other AI coding assistants, not replace them.
> L71: ### Key benefits
> L72:   * Standards management — Maintain coding standards across all agentic work. Whether you’re writing specs, prompting agents, or creating custom Skills, inject your standards to keep work aligned.
> L73:   * Legacy codebase support — Bring pre-AI codebases into the modern era. Discover and document tribal knowledge that exists only in your code, making it easier to use AI agents going forward.
> L74:   * Better spec shaping — Enhanced shaping questions (run in plan mode) help you create stronger, more aligned specs that account for your product’s mission and all your standards.
> L75:   * Team alignment — Keep your entire organization aligned on a spec-driven approach with Claude Code or any AI coding tool.
> L76: ### How it works
> L77: 
> L78:   1. 【6†Install】 — Set up Agent OS in your project with a simple installation script
> L79:   2. 【11†Discover】 — Extract existing patterns from your codebase into documented standards
> L80:   3. 【12†Inject】 — Deploy relevant standards into your context when you need them
> L81:   4. 【14†Shape】 — Use enhanced shaping in plan mode to create specs aligned with your standards
> L82: ### Works with any tool
> L83: 
> L84: Agent OS is designed primarily for Claude Code, with slash commands that integrate directly into your workflow. However, since all outputs are markdown files, Agent OS works just as well with any AI coding tool:
> L85: 
> L86:   * Claude Code (recommended) — Full integration with slash commands
> L87:   * Cursor
> L88:   * Windsurf
> L89:   * Codex
> L90:   * Any AI coding assistant that can read files
> L91: 
> L92: For tools other than Claude Code, simply reference the underlying files in `agent-os/` directly.
> L93: ### Next steps
> L94: 
> L95:   * 【6†Installation guide】
> L96:   * 【7†Understanding profiles】
> L97:   * 【10†The workflow】
> L98: 
> L99: ### Get free access to Agent OS
> L100: 
> L101: Free & open source. Enter your email for instant access and setup instructions.
> L102: 
> L103: [Input: you@company.com][Button: Access Free]
> L104: 
> L105: Where builders stay ahead of how we build with AI.
> L106: 
> L107: [Input: Your email address]
> L108: 
> L109: Free tips to keep your craft sharp.
> L110: 
> L111: ### Learn
> L112: 
> L113:   * 【0†Workshops】
> L114:   * 【20†Courses】
> L115:   * 【0†Free Training】
> L116:   * 【21†YouTube†youtube.com】
> L117: ### Resources
> L118: 
> L119:   * 【22†Newsletter】
> L120:   * 【2†Free Tools】
> L121:   * 【23†Articles】
> L122:   * 【24†About】
> L123: 
> L124: ### Pro
> L125: 
> L126:   * 【1†Community】
> L127:   * 【1†Join Pro】
> L128:   * 【25†For Teams】
> L129:   * 【4†Log in】
> L130: 
> L131: ### Services
> L132: 
> L133:   * 【26†Coaching】
> L134:   * 【27†Projects】
> L135:   * 【3†All services】
> L136: 
> L137: © 2026 Builder Methods. Built by 【28†Brian Casel†briancasel.com】.【29†Contact】【30†Privacy】【31†Terms】
> ```
>
> </details>
</details>

**У meta-project есть перспективная ниша, но почти все отдельные составляющие уже представлены у аналогов.** Его преимущество стоит строить вокруг простой, переносимой организации знаний проекта и надёжных проверок границ.

Сравнил актуальные репозитории и документацию на **12 ноября 2026 года**. Для meta-project учитываю текущую alpha `398a171`; обсуждавшиеся хуки остаются планами. Это сравнение возможностей и архитектуры — общего замера эффективности агентов пока нет.

| Аналог | Что уже предлагает | Что это означает для meta-project |
|---|---|---|
| **[Cline Memory Bank](https://github.com/cline/cline/blob/main/docs/best-practices/memory-bank.mdx)** | Память проекта в Markdown: архитектура, стек, текущая работа, прогресс; процедуры обновления | Ближайший аналог `project_knowledge`. Само разделение знаний по файлам уже привычный подход. Дополнительная ценность Meta — границы, проверка согласованности и обслуживание памяти |
| **[Agent OS](https://buildermethods.com/agent-os)** | Извлечение соглашений из существующего кода, организация стандартов и подача релевантных правил агенту | **Один из самых близких конкурентов по замыслу.** Подготовка существующего репо и загрузка знаний по необходимости уже заняты. Нужно выигрывать качеством сопровождения и проверок |
| **[Superpowers](https://github.com/obra/superpowers)** | Скиллы для планирования, TDD, отладки, ревью и работы субагентов; интеграции с многочисленными средами | Полноценную методику разработки выгоднее использовать совместно с Meta. Собственные аналоги каждого скилла создадут много работы по поддержке |
| **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** | Роли, планирование продукта, архитектура, реализация и проверка; процесс адаптируется к размеру задачи | Ролевая команда и масштабирование процесса сами по себе уже не преимущество. Для Meta разумно сохранять их опциональными |
| **[GitHub Spec Kit](https://github.com/github/spec-kit)** | Конституция проекта, спецификации, планы, задачи; расширения, workflows и интеграции | North Stars и формализованный процесс уже есть у сильного аналога. Meta может сосредоточиться на постоянных знаниях и ограничениях конкретного репозитория |
| **[OpenSpec](https://github.com/Fission-AI/OpenSpec)** | Предложения изменений, требования, технический план, задачи и архив завершённых изменений | Структурированный учёт изменений развит дальше обычного `tasks.md`. Полезнее связывать знания Meta с этими артефактами, чем создавать ещё один параллельный процесс |
| **[Rulesync](https://github.com/dyoshikawa/rulesync)** | Общий источник правил с генерацией конфигов, команд, скиллов, субагентов, hooks и permissions для разных сред | **Самое существенное пересечение с планом адаптеров.** Прежде чем писать собственный универсальный экспортёр, стоит проверить возможность использовать Rulesync |
| **[Claude-Mem](https://github.com/thedotmack/claude-mem)** | Автоматический сбор событий, AI-наблюдатель, память между сессиями, поиск и подача контекста; локальный worker и БД | В автоматической памяти он существенно дальше. У Meta проще инфраструктура и прозрачнее редактируемая человеком база знаний |
| **[Beads](https://github.com/gastownhall/beads)** | Задачи с устойчивыми ID, зависимости, назначение исполнителей, постоянные факты проекта; хранение в Dolt | Учёт задач и координацию агентов необязательно разрабатывать самостоятельно. Преимущество Markdown у Meta — простота чтения, правки и обычного Git-review |

**Самый важный результат сравнения — пересмотреть объём собственных адаптеров.** У Rulesync уже есть подробная [матрица поддержки](https://rulesync.dyoshikawa.com/reference/supported-tools.html), включая хуки и permissions. Там заявлены и Antigravity IDE/CLI. Это повод отдельно проверить основную среду перед разработкой универсальных шимов. Поддержку генерации всё равно нужно подтверждать интеграционными тестами нужного поведения.

По существу meta-project сейчас соединяет три направления:

- **Memory Bank / Agent OS:** знания, соглашения и контекст репозитория.
- **Superpowers / BMAD:** процедурные навыки и роли.
- **Собственные CLI-проверки:** границы, синхронизация и обслуживание памяти.

У такой связки есть польза, если она заметно сокращает ручную настройку и сопровождение. Пока важная часть этой пользы зависит от дисциплины самого агента.

**Где у проекта сильная позиция:**

- Знания хранятся в обычных файлах рядом с проектом и доступны для ревью.
- Для текущих утилит достаточно Python и Git; не нужен отдельный worker, модель-наблюдатель или сервер БД.
- Архитектура, риски, наблюдения и границы изменений собраны в понятную общую структуру.
- Можно подготовить уже существующий репозиторий и постепенно подключать автоматизацию.

При этом лёгкость инфраструктуры особенно выгодна в сравнении с Claude-Mem и Beads. Рядом с Markdown-подходами Cline и Agent OS одного zero-dependency уже недостаточно для заметного отличия.

**Где проект пока уступает:** установка и обновление во многом описаны инструкциями агенту; проверенная матрица интеграций ещё отсутствует; автоматическая память и учёт задач проще специализированных решений. Найденные ошибки архиватора и гейтов также мешают обещать преимущество в надёжности.

Я бы выбрал такое позиционирование:

> **Локальная обвязка для существующих репозиториев: проверяемые границы изменений, компактные знания проекта и переносимый контекст между агентами.**

А развитие сосредоточил бы на трёх результатах: безопасная установка и обновление, отсутствие потери знаний, корректная работа границ в CLI, CI и выбранной среде. Для доказательства пользы стоит сравнить Meta с простым **[AGENTS.md](https://agents.md/)** и с Memory Bank на одинаковых задачах: расход контекста, повторное исследование кода, нарушения границ, ложные блокировки и число вмешательств пользователя. Именно эти результаты дадут весомую причину выбрать проект среди аналогов.

> А что из этого покроят предстоящие изменения?

**Предстоящие изменения сильнее всего улучшат контроль действий и автоматическую подачу контекста.** По сравнению с аналогами это заметный шаг, но охват зависит от этапа: MVP хуков и полный наблюдатель дадут разные результаты.

| Разрыв из сравнения | Что закроют изменения | Что останется |
|---|---|---|
| **Доставка знаний — Cline Memory Bank / Agent OS** | `SessionStart` автоматически подаст паспорт, задачи и риски | Качество самих знаний, обнаружение устаревших сведений и содержательное обновление |
| **Контроль границ изменений** | Проверки перед записью, защита политики, проверка diff в CI — при реализации обсуждённых поправок | Ограничения обходных путей через shell и другие инструменты; здесь нужны возможности самой среды |
| **Интеграции — Rulesync** | Установщик и адаптеры обеспечат работу в выбранных средах | Широкая матрица совместимости, сопровождение версий и особенности каждой среды |
| **Автоматическая память — Claude-Mem** | Полный наблюдатель соберёт историю действий, результаты проверок и признаки повторных неудач | Содержательные наблюдения, поиск по истории и выбор релевантных воспоминаний. Журнал событий этого ещё не обеспечивает |
| **Надёжность установки и обновления** | Можно автоматизировать подключение, диагностику и отключение хуков | Безопасное обновление всего фреймворка с сохранением локальных изменений — отдельная задача |
| **Учёт задач — Beads** | Появятся дополнительные факты о выполнении работы | Устойчивые ID, зависимости, назначение задач, согласованное состояние нескольких исполнителей |
| **Процесс разработки — Superpowers / BMAD / Spec Kit / OpenSpec** | Напоминания и механические проверки будут срабатывать регулярнее | Качество планирования, спецификации, ревью и содержательная проверка результата |

**Сохранность памяти закроют именно исправления архиватора и записи данных.** Автоматический запуск компакции имеет смысл подключать после этих исправлений. Аналогично исправление ложнозелёного `--check` — самостоятельная необходимая работа.

Из трёх приоритетов, которые я назвал в сравнении:

- **Корректные границы в CLI, CI и выбранной среде** — основной результат предстоящего этапа.
- **Отсутствие потери знаний** — достижимо, если включить исправления записи, архивации и проверки параллельных операций.
- **Безопасная установка и обновление** — установка хуков покроет часть; обновление общего комплекта ещё нужно спроектировать.

После этого meta-project станет убедительнее именно как **обвязка знаний и правил репозитория с автоматическими проверками**. Расширять его до собственного аналога Claude-Mem, Beads или полноценной методики разработки для этого не требуется.

> А с точки зрения самого концепта(Индивидуальная обвязка под рабочий проект, с разделенным менеджментом, который самообновляется по ходу работы. В которой инструкции для агентов позволяют решать задачи не теряя сути и концепта проекта(мета видение)), насколько далеко проект будет с учетом изменений?

**В этой рамке после обсуждаемых изменений проект может стать полноценной первой рабочей версией своего концепта.** Архитектурная основа уже собрана. Главный оставшийся вопрос — насколько хорошо она сохраняет смысл проекта на протяжении множества изменений.

Ты описываешь систему, которая поддерживает **актуальную модель конкретного проекта**: зачем он существует, какие решения уже приняты, какие ограничения существенны и как текущая задача связана со всем этим. По такому критерию сравнивать количество функций с Claude-Mem или Beads действительно недостаточно.

У meta-project уже есть основные части этой системы:

| Часть концепта | Что её обеспечивает | Что дадут изменения |
|---|---|---|
| **Индивидуальная настройка под проект** | Анализ кода, интервью, локальные принципы, архитектура и границы | Более надёжное применение полученных правил |
| **Разделённое управление** | Ответственности ролей, зоны изменений, отдельные процедуры исполнения и проверки | Автоматическая проверка части полномочий и фиксация фактических действий |
| **Непрерывная актуализация** | Обновление знаний по ходу работы, наблюдения, сканирование и пересмотр рисков | Регулярные триггеры, безопасная запись и меньше зависимости от памяти агента |
| **Сохранение общего замысла** | Паспорт, North Stars, архитектура, принятые решения и процедура grounding | Доставка нужного контекста в момент работы и обнаружение части отклонений |

В результате появится более устойчивый цикл:

**Модель проекта → постановка задачи → изменение → проверка последствий → обновление модели → следующая задача.**

Именно замкнутость этого цикла — сильная сторона концепта. Разделение ответственности помогает удерживать его: исполнитель решает задачу, проверка оценивает последствия, обновление знаний сохраняет результат для следующих сессий. Это разделение полезно даже при последовательной работе одного агента.

Но **актуальные документы ещё не гарантируют актуального мета-видения**. Агент способен аккуратно обновить архитектуру и при этом незаметно изменить направление проекта. Например, добавить облачный сервис в проект, важным свойством которого была локальная обработка данных. Пути файлов разрешены, тесты проходят, документация обновлена — исходный принцип потерян.

Поэтому самая важная недостающая связь — **между конкретным решением и причиной, по которой проект устроен именно так**. Для архитектурно значимого изменения стоит сохранять короткую цепочку:

- цель изменения;
- затронутые принципы и допущения;
- обоснование выбранного решения;
- результат проверки и последствия для проекта.

Это не требует отдельного отчёта на каждую мелкую правку. Но без такой связи самообновление может постепенно закреплять случайные решения как правильные.

Также нужны разные правила изменения знаний: факты о коде обновляются регулярно; гипотезы остаются обозначенными гипотезами; пересмотр целей и фундаментальных ограничений фиксируется как отдельное принятое решение.

**Относительно рынка концептуально проект окажется в одном поле с Agent OS и BMAD:** индивидуальные стандарты, сохранение контекста, разделение работы и сопровождение изменений. Его отличительной комбинацией могут стать компактная локальная модель проекта, явные границы и небольшой объём инфраструктуры. Преимущество здесь будет определяться качеством работы всей связки.

Я бы оценил ожидаемое состояние так: **основа концепта реализована, автоматизация существенно усилена, смысловая устойчивость требует проверки на практике.** Хороший критерий зрелости: после серии существенных доработок новый агент правильно объясняет цель проекта, причины ключевых решений и ограничения следующей задачи — а пользователь тратит всё меньше времени на восстановление этого понимания.
