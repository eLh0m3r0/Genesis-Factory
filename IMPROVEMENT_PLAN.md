# Genesis Factory — Implementation Plan (v0.5 → v1.0)

Generated: 2026-03-30 by 5-agent hackathon swarm.
Implementation plan: 2026-03-30.

---

## Progress

**41 / 41 items complete.**

| Wave | Focus | Items | Done |
|------|-------|-------|------|
| 1 | Heartbeat hardening | 10 | 10 |
| 2 | Docs & scripts | 8 | 8 |
| 3 | Agent & command system | 13 | 13 |
| 4 | Operator experience | 1 | 1 |
| 5 | Competitive features | 5 | 5 |
| 6 | Architecture foundation | 3 | 3 |

Deferred (5): 5.1 Web Dashboard, 5.2 Parallel Cycles, 5.8 MCP Server,
6.2 Plugin Architecture, 6.4 Multi-Machine Federation.

---

## Wave 1: Heartbeat Hardening

> All changes to `heartbeat/factory_heartbeat.py` in one batch.
> Run tests once at the end. ~200 lines of Python changes.

- [x] **1.4** Alert State Persistence · S
  - Save `_alert_state` and `_service_down` to `heartbeat/alert_state.json`
  - Load on startup, save after each `_record_alert()` / `_record_recovery()`
  - Graceful fallback if JSON is corrupt (log warning, start fresh)
  - **Files**: `heartbeat/factory_heartbeat.py`, `heartbeat/.gitignore` (ignore alert_state.json)

- [x] **1.5** Watchdog Restart Notifications · S
  - Track `_last_start_time = datetime.now()` at startup
  - In `_restart_claude_code()`: include uptime and failure count in Telegram message
  - Message: "🔧 Claude Code restarted (was up {uptime}, {failures} consecutive failures)"
  - **Files**: `heartbeat/factory_heartbeat.py`

- [x] **1.6** Telegram Send Retry with Backoff · S
  - In `send_telegram()`: retry 3x with delays 1s → 2s → 4s
  - Log each retry attempt, log permanent failure to stdout
  - Don't retry on 4xx errors (bad request = won't work on retry)
  - **Files**: `heartbeat/factory_heartbeat.py`

- [x] **3.1** Disk Space Progressive Alerts · M
  - Three tiers in `check_system_health()`:
    - Warning (< 10 GB): "⚠️ Disk space low"
    - Alert (< 5 GB): "🔴 Disk space critical"
    - Critical (< 2 GB): "🔴🔴 Disk nearly full!" + trigger log cleanup
  - Log cleanup: delete `heartbeat.log.1`, `heartbeat.log.2`, `heartbeat.log.3`
  - Separate cooldown keys per tier: `system:disk:warning`, `system:disk:alert`, `system:disk:critical`
  - **Files**: `heartbeat/factory_heartbeat.py`, `heartbeat/config.example.yaml` (add tier thresholds)

- [x] **3.2** Monitor Config Caching · S
  - Cache last-good `heartbeat_config.yaml` content per project in memory dict
  - On YAML parse error: use cached config + send alert "⚠️ Config parse error for {project}, using cached config"
  - **Files**: `heartbeat/factory_heartbeat.py`

- [x] **3.3** Watchdog Restart Verification · S
  - After `tmux send-keys` in `_restart_claude_code()`: `time.sleep(3)` then verify window exists
  - If verification fails: log error, don't count as successful restart
  - **Files**: `heartbeat/factory_heartbeat.py`

- [x] **3.4** Watchdog Exponential Backoff · M
  - Replace flat `WATCHDOG_MAX_RESTARTS_PER_HOUR = 5` with exponential delays
  - Delays between consecutive restarts: 1min → 2min → 5min → 10min → 30min
  - Track `_watchdog_last_restart` timestamp, enforce minimum gap
  - Reset backoff to 1min after 1 hour of stability
  - **Files**: `heartbeat/factory_heartbeat.py`

- [x] **3.5** Required Env Var Validation · S
  - Add `required_env_vars` list to `config.example.yaml` (e.g., `GITHUB_TOKEN`)
  - At startup: check each var exists in `os.environ`, alert on missing (don't crash — they might not be needed by all monitors)
  - **Files**: `heartbeat/factory_heartbeat.py`, `heartbeat/config.example.yaml`

- [x] **3.6** Safe Eval Execution Timeout · S
  - Wrap `safe_eval()` body in `signal.alarm(1)` (1-second timeout)
  - Catch `TimeoutError`, log "Monitor alert_condition timed out"
  - Note: `signal.alarm` works on Unix only — fine for macOS target
  - **Files**: `heartbeat/factory_heartbeat.py`

- [x] **4.8** Config Hot-Reload via SIGHUP · M
  - Add `SIGHUP` handler that re-reads `config.yaml` and updates:
    - `ALERT_COOLDOWN`, `DISK_WARNING_GB`, monitor interval, health interval
  - Re-register schedule jobs with new times (clear + re-add)
  - Send Telegram: "🔄 Config reloaded via SIGHUP"
  - Don't reload Telegram credentials (requires restart for security)
  - **Files**: `heartbeat/factory_heartbeat.py`

**Tests**: Update `heartbeat/test_heartbeat.py` for all new functionality.
Expect ~15-20 new test cases.

---

## Wave 2: Documentation & Scripts

> New files only — no changes to existing Python/command code.
> Can be implemented in any order.

- [x] **1.2** `docs/FIRST_DAY.md` — Post-Setup Guide · S
  - Sections: "What happens tonight" (nightly at 22:00), "Tomorrow morning"
    (brief at 07:00), "What to do now" (review VISION.md, try /status, /discover),
    "Your first week" (what to expect), "Common questions"
  - Cross-reference: /setup, /status, /discover, /nightly
  - **Files**: Create `docs/FIRST_DAY.md`

- [x] **1.3** `docs/TROUBLESHOOTING.md` — Systematic Debug Guide · M
  - Decision trees for:
    - Factory won't start (Docker? tmux? claude? heartbeat?)
    - Heartbeat silent (config? Telegram token? process running?)
    - Story stuck (which phase? architect? dev? tests? CI?)
    - Docker broken (disk space? port conflict? image pull?)
    - Rate limited (which API? backoff strategy?)
    - Telegram not working (token? chat_id? network?)
  - Each tree: symptom → check command → fix → verify
  - **Files**: Create `docs/TROUBLESHOOTING.md`

- [x] **1.7** LaunchAgent KeepAlive · S
  - Change `<key>KeepAlive</key><false/>` to `<true/>` in plist
  - Heartbeat auto-restarts on crash instead of staying dead
  - **Files**: `scripts/com.genesis.factory.plist`

- [x] **3.7** `scripts/validate-factory.sh` — Config Validator · S
  - Check: Claude Code version ≥ 2.1.80, Python ≥ 3.12, Docker running,
    tmux installed, bun installed, Telegram token set, projects dir exists,
    heartbeat config valid YAML, all required files present
  - Output: ✅/❌ per check, summary at end
  - Exit code 0 if all pass, 1 if any fail
  - **Files**: Create `scripts/validate-factory.sh`

- [x] **3.8** Docker Startup Health Verification · S
  - In `scripts/start.sh`: after `docker compose up -d`, wait for PostgreSQL
    to be ready before launching Claude Code
  - Use `docker compose exec postgres pg_isready` in a loop (max 30s)
  - If timeout: warn but continue (Claude Code can work without DB)
  - **Files**: `scripts/start.sh`

- [x] **4.5** `scripts/install-launchagent.sh` — Automated Install · S
  - Detect FACTORY_DIR, generate plist with correct paths
  - Copy to `~/Library/LaunchAgents/`, load with launchctl
  - Verify: `launchctl list | grep genesis`
  - Uninstall option: `./scripts/install-launchagent.sh --uninstall`
  - **Files**: Create `scripts/install-launchagent.sh`

- [x] **4.6** `scripts/logs.sh` — Log Viewer · S
  - Usage: `./scripts/logs.sh [heartbeat|docker|claude] [--tail N] [--grep PATTERN]`
  - Heartbeat: reads `heartbeat/heartbeat.log`
  - Docker: `docker compose -f docker/docker-compose.yml logs`
  - Claude: reads tmux capture output
  - Default: heartbeat, last 50 lines
  - **Files**: Create `scripts/logs.sh`

- [x] **4.7** `docs/COSTS_AND_SCALE.md` — Scaling Guide · S
  - Monthly costs breakdown: Claude Max ($100), compute (free), Docker (free)
  - Scaling by project count: 1-3 projects comfortable, 5+ needs token management
  - Token budget guidance: ~5M tokens/month on Max plan, S story ≈ 50K tokens,
    M story ≈ 150K tokens, L story ≈ 400K tokens
  - Hardware requirements: Apple Silicon recommended, 16GB RAM minimum
  - **Files**: Create `docs/COSTS_AND_SCALE.md`

---

## Wave 3: Agent & Command System

> All changes in `.claude/` directory — commands, agents, hooks.
> These are markdown specs interpreted by Claude Code, not traditional code.

- [x] **1.1** `/health` command — Factory Health Dashboard · M
  - Comprehensive status check, more detailed than `/status`:
    - Docker services: `docker compose ps` with health status
    - Per-project: story counts, last commit, last PR, open issues
    - Heartbeat: last 10 log entries, any errors in last hour
    - System: disk space, uptime, CPU/memory
    - Schedule: next trigger time, last trigger result
    - Monitors: list all active monitors, last check result
  - Output: Telegram-formatted multi-section message
  - **Files**: Create `.claude/commands/health.md`

- [x] **2.1** Explicit Lead Developer Agent · S
  - Agent that coordinates Agent Teams during /build
  - I/O contract: receives design_notes from architect, outputs merged code
  - Coordination protocol: how to communicate with dev/test teammates
  - Reads AGENTS.md for project-specific patterns
  - **Files**: Create `.claude/agents/lead-developer.md`

- [x] **2.2** Architect I/O Contract · M
  - Update architect output to be strict schema:
    - `files_to_create`: list with purpose
    - `files_to_modify`: list with specific changes
    - `test_plan`: unit, integration, UAT scenarios
    - `risks`: what could go wrong, mitigation
    - `dependencies`: external libs, APIs, env vars needed
    - `estimated_effort`: S/M/L with justification
  - Add validation: architect must fill ALL fields or explain why N/A
  - **Files**: `.claude/agents/architect.md`

- [x] **2.3** Pre-Build Story Validation · M
  - Add validation gate before architecture phase in /build:
    - Acceptance criteria present and testable?
    - Effort realistic for one nightly cycle?
    - Dependencies met? (check `blocked_by` field)
    - Required env vars/APIs available?
  - If validation fails: mark story "blocked", pick next story
  - **Files**: `.claude/commands/build.md`

- [x] **2.4** Story Dependency Tracking · M
  - Add `blocked_by` and `unblocks` fields to BACKLOG.md format
  - Update `/nightly` and `/build` to skip blocked stories
  - Update `/backlog` to show dependency chains
  - Update product-strategist to set dependencies when creating stories
  - **Files**: `templates/BACKLOG.template.md`, `.claude/commands/build.md`,
    `.claude/commands/nightly.md`, `.claude/commands/backlog.md`,
    `.claude/agents/product-strategist.md`

- [x] **2.5** AGENTS.md Feedback Loop · S
  - Add to ALL 7 agent preambles: "Before starting, read the project's
    AGENTS.md for known patterns, selectors, and failure modes."
  - Each agent should check if AGENTS.md exists for the current project
  - **Files**: `.claude/agents/architect.md`, `.claude/agents/product-strategist.md`,
    `.claude/agents/research-analyst.md`, `.claude/agents/uat-tester.md`,
    `.claude/agents/security-reviewer.md`, `.claude/agents/devops.md`,
    `.claude/agents/retrospective.md`

- [x] **2.6** Post-Story Mini-Retrospective · M
  - After each story (done or stuck), add a quick retro step to /build:
    - What was hard? What took longest?
    - Did the design match reality?
    - Any new patterns or anti-patterns?
  - Write findings to project's AGENTS.md immediately
  - If pattern is systematic, create story in _factory/BACKLOG.md
  - **Files**: `.claude/commands/build.md`

- [x] **2.7** `/retry STORY-ID` Command · S
  - Reset story status from "stuck" → "ready" in BACKLOG.md
  - Clear previous design_notes and learnings (fresh attempt)
  - Optionally trigger `/build STORY-ID` immediately
  - **Files**: Create `.claude/commands/retry.md`

- [x] **2.8** Expand Post-Tool-Use Hooks · M
  - Add hooks for:
    - `Bash(git push*)` — if fails, suggest rebase: `git pull --rebase && git push`
    - `Bash(npm install*)` / `Bash(pip install*)` — if fails, check network, disk, versions
    - `Bash(docker*)` — if fails, check Docker Desktop running, disk space
    - `Bash(gh *)` — if rate limited, wait and retry; if auth error, check token
  - **Files**: `.claude/hooks/post-tool-use.yaml`

- [x] **4.1** `/projects` Command — Multi-Project Overview · M
  - Show all projects with: name, weight, story counts (ready/progress/done/stuck),
    last activity date, health indicator (green/yellow/red)
  - Health based on: stories stuck? monitors failing? last commit age?
  - Sort by weight (highest first)
  - **Files**: Create `.claude/commands/projects.md`

- [x] **4.2** `/progress PROJECT` Command — Burndown · M
  - For a given project (or all projects): stories completed this month,
    velocity (stories/week), average cycle time, completion rate (done vs stuck),
    upcoming stories with effort estimate
  - Optional: simple ASCII burndown chart
  - **Files**: Create `.claude/commands/progress.md`

- [x] **4.3** Interactive `/new-project` Wizard Enhancement · M
  - Enhance existing command with:
    - Interactive Q&A: "What tech stack?", "Deploy target?", "Has a database?"
    - Auto-generate CI workflow based on stack (Python/Node/etc.)
    - Create heartbeat_config.yaml with sensible defaults for the stack
    - Run `/discover` automatically after creation
  - **Files**: `.claude/commands/new-project.md`

- [x] **4.4** `/validate-project PROJECT` — Project Health Check · M
  - Validate: VISION.md has all required sections, CLAUDE.md is complete,
    BACKLOG.md stories have required fields, heartbeat_config.yaml valid,
    GitHub repo exists and CI is configured
  - Report: ✅/⚠️/❌ per check with fix suggestions
  - **Files**: Create `.claude/commands/validate-project.md`

---

## Wave 4: Operator Experience

> CLAUDE.md prompt engineering for natural language direction.

- [x] **4.9** Operator Intent Engine · M
  - Add section to `.claude/CLAUDE.md` teaching Claude to handle natural language
    direction from Telegram
  - Intent classification:
    - **Add story**: "Add a PDF export feature" → BACKLOG.md entry
    - **Change direction**: "Focus on mobile version" → VISION.md priorities
    - **Add rule**: "Don't use jQuery" → CLAUDE.md Critical Rules
    - **Change priority**: "Set project-x weight to 5" → VISION.md project_weight
    - **Pause/unpause**: "Pause side-project" → weight to 0 or flag
    - **Ask question**: "How many stories are ready?" → query and respond
  - Scope intelligence:
    - Named project → that project's files
    - "Everywhere" / "globally" → global .claude/CLAUDE.md
    - Ambiguous → ask which project or all
    - If only 1 project → skip the question
  - Safety: confirm before VISION.md changes, show diff, ask "ok?"
  - **Files**: `.claude/CLAUDE.md`

---

## Wave 5: Competitive Features

> New capabilities. Each is relatively independent.
> Implementation may involve new commands, agents, or heartbeat changes.

- [x] **5.3** GitHub Issues Sync · M
  - Bidirectional: GitHub Issues → BACKLOG.md stories, completed stories → closed issues
  - New command `/sync-issues PROJECT` or integrate into /discover
  - Map issue labels to story priority/effort
  - Auto-close issues when story status is "done"
  - **Files**: Create `.claude/commands/sync-issues.md`, update `.claude/commands/discover.md`

- [x] **5.4** Cost Tracking & Reporting · M
  - Track token usage per cycle (approximate from model + context size)
  - Add to morning brief: estimated tokens used last 24h, budget remaining
  - Alert when approaching monthly limit (80%, 90%, 95%)
  - Store estimates in `~/projects/_factory/cost_log.md` (append-only)
  - **Files**: Update `.claude/commands/morning-brief.md`, `.claude/commands/build.md`,
    `.claude/CLAUDE.md`

- [x] **5.5** Spec-as-Holdout Validation · M
  - During /build: acceptance criteria are NOT passed to dev teammates
  - Dev implements from design_notes only
  - After implementation: UAT tester validates against holdout acceptance criteria
  - Prevents "teaching to the test" — dramatically improves code quality
  - **Files**: Update `.claude/commands/build.md`, `.claude/agents/lead-developer.md`

- [x] **5.6** Auto-Generated Project Documentation · M
  - After each completed story, update project docs:
    - Architecture overview (component diagram in text)
    - API endpoints (if web project)
    - Database schema summary
    - Deployment guide
  - Store in `~/projects/{name}/docs/` or update existing README
  - **Files**: Update `.claude/commands/build.md`, create `.claude/agents/doc-writer.md`

- [x] **5.7** AI Merge Conflict Resolution · M
  - When feature branch diverges from main, auto-resolve conflicts
  - Strategy: `git merge main` in feature branch, use Claude to resolve conflicts
  - Add check to /build before PR creation: "is branch behind main?"
  - If conflicts are non-trivial, report to Telegram instead of auto-resolving
  - **Files**: Update `.claude/commands/build.md`

---

## Wave 6: Architecture Foundation

> Structural changes. Benefit from having real usage data from Waves 1-5.

- [x] **6.1** Unified Configuration Schema · M
  - JSON Schema for: config.yaml, heartbeat_config.yaml, VISION.md fields,
    BACKLOG.md story fields, CLAUDE.md sections
  - Validation at load time in heartbeat and in /validate-project
  - Single schema file: `schemas/factory.schema.json`
  - **Files**: Create `schemas/factory.schema.json`, update `heartbeat/factory_heartbeat.py`,
    `.claude/commands/validate-project.md`

- [x] **6.3** State Persistence Layer · M
  - SQLite database for: alert state, watchdog history, cycle metrics,
    story status transitions, cost tracking
  - Replace in-memory dicts with DB queries
  - Schema: `heartbeat/schema.sql`, auto-create on first run
  - Enable historical analysis: "how many stories completed this month?"
  - **Files**: Create `heartbeat/schema.sql`, update `heartbeat/factory_heartbeat.py`,
    `heartbeat/requirements.txt`

- [x] **6.5** Benchmark Suite · M
  - Reproducible benchmark: feed a standard VISION.md, measure:
    - Time to first story generated (discovery)
    - Time to first merge (build cycle)
    - Stories completed per week
    - Cost per story (tokens)
    - Stuck rate (stuck / total)
  - Compare across factory versions
  - **Files**: Create `benchmarks/README.md`, `benchmarks/run.sh`,
    `benchmarks/sample-vision.md`

---

## Deferred Items

These items are excluded from the current plan. Revisit after v1.0.

| Item | Reason |
|------|--------|
| **5.1** Web Dashboard (L) | Requires separate frontend project (React/Vue). Do after core stabilizes. |
| **5.2** Parallel Project Cycles (L) | Needs real-world single-project cycle data first. Agent Teams coordination at scale is unproven. |
| **5.8** MCP Server for Factory Status (M) | MCP ecosystem is too early. No external consumers yet. |
| **6.2** Plugin Architecture (L) | Premature — no community or extension requests yet. Internal .claude/ structure suffices. |
| **6.4** Multi-Machine Federation (L) | Requires 6.3 (state persistence) first. User runs single machine. |

---

## Competitive Position

```
                    Autonomous (24/7)
                         |
           Genesis       |    Devin ($500/mo)
           Factory       |    Blitzy (enterprise)
           ($103/mo,     |    Factory.ai ($$$$)
            open source) |
                         |
  Local ─────────────────┼──────────────── Cloud
                         |
           Aider         |    Copilot ($19/mo)
           Cline         |    Cursor ($20/mo)
           Goose         |    Codex ($20/mo)
           (interactive) |    (on-demand)
                         |
                   Interactive/On-Demand
```

**Genesis Factory is the only system in the "local + autonomous" quadrant.**

Key differentiators to amplify:
1. **Self-improving** — no competitor has this
2. **External monitoring** — heartbeat watches the world, not just code
3. **Phone control** — Telegram as primary interface
4. **$103/month** — 5x cheaper than Devin Team
5. **Data sovereignty** — never leaves your machine
