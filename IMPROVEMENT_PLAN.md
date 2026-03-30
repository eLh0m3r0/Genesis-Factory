# Genesis Factory — Improvement Plan (v0.5 → v1.0)

Generated: 2026-03-30 by 5-agent hackathon swarm (UX, SRE, Agent Quality, Market Research, Architecture).

## Executive Summary

Genesis Factory occupies a unique position: the only open-source, self-hosted, self-improving,
fully autonomous software development system on consumer hardware at $103/month. Closest
competitors are either cloud-based and expensive (Devin $500/mo, Factory.ai enterprise) or
interactive rather than autonomous (Cursor, Copilot, Aider).

The system works. These improvements take it from "works" to "polished product."

---

## Phase 1: Visibility & Quick Wins (Week 1-2)

> Goal: Users can see what the factory is doing and fix problems when they occur.

### 1.1 `/health` command — Factory Health Dashboard
- **What**: Single command showing system status, recent activity, issues, next events
- **Why**: #1 user request — "Is the factory working? Why isn't it doing anything?"
- **Scope**: Telegram-formatted output (no web UI yet). Reads from heartbeat logs, git logs, BACKLOG.md files
- **Effort**: M

### 1.2 `docs/FIRST_DAY.md` — Post-Setup Guide
- **What**: "Your first day" guide — what happens tonight, tomorrow morning, what to do now
- **Why**: Setup ends abruptly. Users don't know what to do next.
- **Effort**: S

### 1.3 `docs/TROUBLESHOOTING.md` — Systematic Debug Guide
- **What**: Decision trees for common failures: factory won't start, heartbeat silent, story stuck, Docker broken, rate limited
- **Why**: Error recovery is currently tribal knowledge
- **Effort**: M

### 1.4 Heartbeat Alert State Persistence
- **What**: Persist `_alert_state` and `_service_down` to JSON file. Load on restart.
- **Why**: After heartbeat restart, cooldown is lost → alert storm. Also, recovery notifications lost.
- **Effort**: S

### 1.5 Watchdog Restart Notifications
- **What**: When Claude Code is restarted by watchdog, send Telegram notification with uptime and reason
- **Why**: Currently invisible. User doesn't know Claude crashed overnight.
- **Effort**: S

### 1.6 Telegram Send Retry with Backoff
- **What**: If `send_telegram()` fails, retry 3x with exponential backoff. Log persistent failures to stdout.
- **Why**: If Telegram is down, ALL notifications are silently lost. Operator is blind.
- **Effort**: S

### 1.7 LaunchAgent KeepAlive
- **What**: Change plist `KeepAlive` from `false` to `true` so heartbeat auto-restarts on crash
- **Why**: Currently a config error kills heartbeat permanently until manual restart
- **Effort**: S (one-line change)

---

## Phase 2: Agent Quality & Workflow (Week 3-4)

> Goal: The autonomous pipeline produces higher quality output with fewer stuck stories.

### 2.1 Explicit Lead Developer Agent
- **What**: Create `.claude/agents/lead-developer.md` with I/O contracts, teammate coordination protocol
- **Why**: Lead role exists implicitly but has no spec. Teammates don't know how to communicate.
- **Effort**: S

### 2.2 Architect I/O Contract
- **What**: Define explicit input/output schema for architect. Output MUST include: files_to_create, files_to_modify, test_plan, risks, dependencies
- **Why**: Incomplete designs → high stuck rate. Developer doesn't know what to build.
- **Effort**: M

### 2.3 Pre-Build Story Validation
- **What**: Before story moves to "ready", architect validates: testable acceptance criteria, realistic effort, no unmet dependencies
- **Why**: Low-quality stories waste entire nightly cycles. Catch problems early.
- **Effort**: M

### 2.4 Story Dependency Tracking
- **What**: Add `blocked_by` and `unblocks` fields to BACKLOG.md. `/nightly` skips blocked stories.
- **Why**: Factory picks stories that can't be completed because prerequisites are missing.
- **Effort**: M

### 2.5 AGENTS.md Feedback Loop
- **What**: All agent preambles include "Read project AGENTS.md before starting work" for selectors, patterns, anti-patterns
- **Why**: Retrospective writes learnings but agents never read them. Same mistakes repeat.
- **Effort**: S

### 2.6 Post-Story Mini-Retrospective
- **What**: After each story (done or stuck), quick retrospective captures what was hard and updates AGENTS.md
- **Why**: Weekly retro misses context. Daily incremental learning is faster.
- **Effort**: M

### 2.7 `/retry STORY-ID` Command
- **What**: Reset story status from "stuck" to "ready" and trigger `/build`
- **Why**: Currently requires manual BACKLOG.md editing
- **Effort**: S

### 2.8 Expand Post-Tool-Use Hooks
- **What**: Add hooks for: failed git push (rebase advice), npm install errors, Docker down, GitHub rate limit
- **Why**: Current hooks only cover pytest and Playwright. Common errors require manual debugging.
- **Effort**: M

---

## Phase 3: Robustness & Reliability (Week 5-6)

> Goal: The factory runs 30 days unattended without silent failures.

### 3.1 Disk Space Progressive Alerts
- **What**: Three tiers: warning (10GB), alert (5GB), critical (2GB). Critical triggers log cleanup.
- **Why**: Single threshold misses the urgency gradient. Disk full = system blind.
- **Effort**: M

### 3.2 Monitor Config Caching
- **What**: Cache last-good monitor config per project. On parse error, use cache + alert.
- **Why**: Corrupted YAML = monitor permanently dead until manual fix.
- **Effort**: S

### 3.3 Watchdog Restart Verification
- **What**: After sending tmux keys to restart Claude Code, verify the window exists and process is running
- **Why**: Race condition: restart can fail silently between check and send-keys
- **Effort**: S

### 3.4 Watchdog Exponential Backoff
- **What**: Instead of flat 5-per-hour limit, use 1min→2min→5min delays between retries
- **Why**: Prevents 5-minute restart storm. Gives operator time to react.
- **Effort**: M

### 3.5 Required Env Var Validation
- **What**: Add `required_env_vars` to heartbeat config. Validate at startup, alert on missing.
- **Why**: Missing env vars cause monitors to silently fail at runtime.
- **Effort**: S

### 3.6 Safe Eval Execution Timeout
- **What**: Wrap `safe_eval()` in 1-second timeout to catch infinite loops
- **Why**: Infinite generator expression blocks entire monitor cycle
- **Effort**: S

### 3.7 `scripts/validate-factory.sh` — Config Validator
- **What**: Checks all prerequisites: Claude Code version, Python, Docker, Telegram token, project structure
- **Why**: Silent failures during setup. User doesn't know what's wrong.
- **Effort**: S

### 3.8 Docker Startup Health Verification
- **What**: After `docker compose up`, verify all services healthy before starting Claude Code
- **Why**: PostgreSQL may still be initializing when Claude Code tries to connect
- **Effort**: S

---

## Phase 4: User Experience & Comfort (Week 7-8)

> Goal: New users onboard in 15 minutes. Daily users operate from their phone.

### 4.1 `/projects` Command — Multi-Project Overview
- **What**: Show all projects with weight, status counts, next story, health indicator
- **Why**: Users with 3+ projects can't see which is getting attention
- **Effort**: M

### 4.2 `/progress PROJECT` Command — Burndown
- **What**: Stories completed this month, velocity, average cycle time, upcoming
- **Why**: No way to measure if the factory is productive
- **Effort**: M

### 4.3 Interactive `/new-project` Wizard
- **What**: Ask questions, generate VISION.md + CLAUDE.md + GitHub repo + CI workflow
- **Why**: Manual template filling is error-prone and incomplete
- **Effort**: M

### 4.4 `/validate-project PROJECT` — Project Health Check
- **What**: Validate VISION.md sections, CLAUDE.md completeness, BACKLOG.md field coverage
- **Why**: Malformed project files cause agents to fail
- **Effort**: M

### 4.5 `scripts/install-launchagent.sh` — Automated Install
- **What**: Generates plist with correct path, copies, loads, verifies
- **Why**: Manual sed + cp + launchctl is error-prone
- **Effort**: S

### 4.6 `scripts/logs.sh` — Log Viewer
- **What**: `./scripts/logs.sh heartbeat --tail 20 --grep error`
- **Why**: Debugging requires manual log file navigation
- **Effort**: S

### 4.7 `docs/COSTS_AND_SCALE.md` — Scaling Guide
- **What**: Hardware requirements by project count, monthly costs breakdown, token budget guidance
- **Why**: Users don't know if they can run 5 projects or what it costs
- **Effort**: S

### 4.8 Config Hot-Reload via SIGHUP
- **What**: Heartbeat reloads config.yaml on SIGHUP without restart
- **Why**: Changing schedule or monitors requires manual heartbeat restart
- **Effort**: M

### 4.9 Natural Language Direction — "Operator Intent Engine"
- **What**: Operator gives direction via Telegram in natural language. Claude intelligently
  determines scope (one project vs all), edits the right files, confirms what it did.
- **Why**: Currently ALL direction changes require manual file editing on the MacBook.
  Operator must know which file to edit, what format to use, and log into the machine.
  This is the single biggest UX gap — the phone is the control plane but it can't
  actually control direction.
- **How it works**:
  1. Operator writes anything in Telegram (not a slash command)
  2. Claude classifies the intent:
     - **Add story**: "Přidej story: export do PDF" → create entry in BACKLOG.md
     - **Change direction**: "Soustřeď se na mobilní verzi" → update VISION.md priorities
     - **Add rule**: "Nepoužívej jQuery" → add to CLAUDE.md Critical Rules
     - **Change priority**: "Dej czechattend na váhu 5" → update project_weight
     - **Pause/unpause project**: "Dej side-project na pauzu" → set weight to 0 or create flag
     - **Ask question**: "Kolik stories je ready?" → query and respond, don't modify
  3. Claude determines **scope** by asking if ambiguous:
     - Explicit: "V czechattend nepoužívej jQuery" → project-specific CLAUDE.md
     - Explicit: "Nikde nepoužívej jQuery" → global .claude/CLAUDE.md
     - Ambiguous: "Nepoužívej jQuery" → Claude asks: "Myslíš jen pro konkrétní projekt, nebo pro všechny?"
  4. Claude makes the change and **confirms with diff**:
     ```
     ✅ Přidáno do czechattend/CLAUDE.md:
       Critical Rules:
     + 5. Never use jQuery — use vanilla JS or framework-native solutions

     Platí jen pro projekt czechattend. Chceš to i pro ostatní?
     ```
  5. Operator can reply "ano pro všechny" → Claude propagates to global CLAUDE.md
- **Scope intelligence rules**:
  - Story → always project-specific (asks which project if not obvious)
  - Technical rule → asks: project or global?
  - Direction change → always project-specific (which project?)
  - Priority/weight change → always project-specific
  - "Everywhere" / "nikde" / "všude" / "v celém systému" → global
  - Named project → that project's files
  - If only 1 project exists → skip the question, use that project
- **Safety**:
  - Never auto-apply destructive changes (removing stories, lowering all weights)
  - Always confirm before modifying VISION.md (it's the human's document)
  - Show what changed, ask "ok?" before committing to git
- **Implementation**: Primarily a CLAUDE.md section describing this behavior pattern,
  plus examples. No new code needed — Claude Code already has full file access.
  The key is teaching it the decision tree for scope and confirmation.
- **Effort**: M (mostly prompt engineering in CLAUDE.md + examples + testing)

---

## Phase 5: Competitive Edge (Month 2-3)

> Goal: Features that set Genesis Factory apart from competitors.

### 5.1 Web Dashboard (Read-Only)
- **What**: Lightweight localhost web UI: system status, backlog, recent cycles, agent activity
- **Why**: Every competitor (Devin, Cursor, OpenHands) has a GUI. Telegram is powerful but a dashboard helps.
- **Effort**: L

### 5.2 Parallel Project Cycles
- **What**: Nightly cycle works on 2-3 stories in parallel (one per project) using Agent Teams
- **Why**: Currently limited to 1 story per night. 2-3x throughput increase.
- **Effort**: L

### 5.3 GitHub Issues Sync
- **What**: Bidirectional sync: GitHub Issues → BACKLOG.md stories, completed stories → closed issues
- **Why**: External contributors can see and create work. Factory picks up human-created issues.
- **Effort**: M

### 5.4 Cost Tracking & Reporting
- **What**: Track token usage per cycle. Report in morning brief. Alert near budget limit.
- **Why**: Users run out of API tokens mid-cycle without warning
- **Effort**: M

### 5.5 Spec-as-Holdout Validation
- **What**: Behavioral specs held out from agent context during development. Agent doesn't see what it'll be tested against.
- **Why**: Prevents "test gaming" where agent writes code to pass its own tests. Dramatically improves code quality. (StrongDM Dark Factory pattern)
- **Effort**: M

### 5.6 Auto-Generated Project Documentation
- **What**: After each completed story, auto-update architecture docs and API docs
- **Why**: Devin has "Wiki" feature. Docs stay current without manual effort.
- **Effort**: M

### 5.7 AI Merge Conflict Resolution
- **What**: When feature branches diverge from main, use Claude to resolve conflicts
- **Why**: Long-running builds fail when main moves ahead. Auto-Claude has this.
- **Effort**: M

### 5.8 MCP Server for Factory Status
- **What**: Expose factory status, backlog, and commands as MCP tools
- **Why**: Positions Genesis Factory in the growing MCP ecosystem. Other agents can query the factory.
- **Effort**: M

---

## Phase 6: Architecture (Month 3+)

> Goal: Foundation for long-term scaling and community.

### 6.1 Unified Configuration Schema
- **What**: JSON Schema for all config files. Validation at load time. Single source of truth.
- **Why**: 8+ config file types with no schema = silent failures and confusion
- **Effort**: M

### 6.2 Plugin Architecture
- **What**: Standard interfaces for adding agents, monitors, commands. Discovery registry. Versioning.
- **Why**: Currently requires forking to extend. Blocks community contributions.
- **Effort**: L

### 6.3 State Persistence Layer
- **What**: SQLite or PostgreSQL for: alert state, watchdog history, cycle metrics, story status
- **Why**: In-memory state = data loss on restart. No historical analysis.
- **Effort**: M

### 6.4 Multi-Machine Federation
- **What**: Run factory on 2+ machines. Coordinator assigns projects. Shared state via DB.
- **Why**: Single machine = single point of failure + token limit ceiling
- **Effort**: L

### 6.5 Benchmark Suite
- **What**: Reproducible benchmark: VISION.md in → measure time to first deploy, stories/week, cost/story
- **Why**: Strongest possible marketing. Concrete numbers beat descriptions.
- **Effort**: M

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

---

## Priority Matrix

| Priority | Items | Theme |
|----------|-------|-------|
| P0 (do first) | 1.1-1.7 | Visibility — stop being blind |
| P1 (next) | 2.1-2.8 | Quality — fewer stuck stories |
| P2 (then) | 3.1-3.8 | Reliability — 30 days unattended |
| P3 (comfort) | 4.1-4.9 | UX — smooth daily operation + natural language direction |
| P4 (edge) | 5.1-5.8 | Competition — unique features |
| P5 (scale) | 6.1-6.5 | Architecture — long-term foundation |

Total: **46 improvements** across 6 phases.
Estimated timeline: 2-3 months for P0-P3, 3-6 months for P4-P5.
