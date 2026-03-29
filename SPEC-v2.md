# Genesis Factory — Specification v2.0

## Universal Autonomous IT Team

---

## 1. Executive Summary

Genesis Factory is an autonomous software development system that runs 24/7
on a dedicated Apple Silicon MacBook. It manages any number of software projects
simultaneously — discovering what to build, designing solutions, writing code,
testing in real browsers, reviewing for security, merging to main, and deploying
to production.

The system consists of three components:

1. **Claude Code session with Channels** — the brain. Claude Opus 4.6 on a Max
   subscription makes all intelligent decisions. Receives commands via Telegram.
   Uses Agent Teams for parallel development, Playwright for browser testing,
   Auto Mode for safe autonomous execution, and Computer Use for visual tasks.

2. **Heartbeat daemon** — the clock and sensors. A lightweight Python process
   (~600 lines, zero LLM calls) that sends scheduled triggers and monitoring
   alerts to Claude Code via Telegram. Includes a watchdog that restarts Claude
   Code if the session crashes.

3. **Docker stack** — the infrastructure. PostgreSQL for databases, project-specific
   staging containers, and Playwright browser instances for headless UAT.

The human operator writes VISION.md files (project direction, ~10 lines each)
and reviews Telegram notifications. Everything else is autonomous.

---

## 2. Design Principles

**Model decides, not code.** The heartbeat provides triggers ("it's 22:00")
and sensory data ("funding rate spiked"). Claude Code decides what to do with
them. There is no hardcoded business logic in the orchestration layer.

**Universal, not project-specific.** Any project with a VISION.md can be onboarded.
The factory adapts to any tech stack, domain, or deployment target. Project-specific
knowledge lives in each project's CLAUDE.md, not in the factory configuration.

**Self-improving.** The factory itself is a project (`~/projects/_factory/`) with
its own backlog. It evolves its own agents, commands, heartbeat, and workflows.
Friday night cycles implement factory improvements.

**Convention over configuration.** Every project follows the same directory contract.
No per-project orchestrator config is needed. The factory discovers projects by
scanning `~/projects/` for directories containing VISION.md.

**Safety-first autonomy.** Auto-merge and auto-deploy are enabled, but ONLY when
all quality gates pass (CI green + UAT pass + security review clean). When the
system is uncertain, it asks the human via Telegram rather than guessing.

---

## 3. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Dedicated MacBook (Apple Silicon, 16GB+)       │
│                   macOS, lid closed, 24/7, caffeinate            │
│                                                                   │
│  tmux session "factory"                                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Window 1: Claude Code + Channels                           │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ claude --channels                                     │  │  │
│  │  │                                                       │  │  │
│  │  │ Model: Claude Opus 4.6 (Max subscription)             │  │  │
│  │  │ Subagent model: Claude Sonnet 4.6 (cost efficient)    │  │  │
│  │  │                                                       │  │  │
│  │  │ Features used:                                        │  │  │
│  │  │  • Channels — Telegram control plane                  │  │  │
│  │  │  • Agent Teams — parallel Dev + Test in worktrees     │  │  │
│  │  │  • Auto Mode — safe autonomous execution              │  │  │
│  │  │  • Computer Use — visual verification, desktop apps   │  │  │
│  │  │  • Ralph plugin — iterative loops until tests pass    │  │  │
│  │  │  • Playwright MCP — browser UAT with screenshots      │  │  │
│  │  │  • Custom agents — 7 specialized roles                │  │  │
│  │  │  • Custom commands — 12 slash commands                │  │  │
│  │  │  • Hooks — auto-fix patterns on test failures         │  │  │
│  │  │  • /memory — persistent learnings across sessions     │  │  │
│  │  │  • Git worktrees — isolation per agent teammate       │  │  │
│  │  │  • Scheduled Tasks — cloud backup for critical crons  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │ Window 2: Heartbeat                                        │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ python3 factory_heartbeat.py                          │  │  │
│  │  │                                                       │  │  │
│  │  │ Zero LLM calls. Pure Python automation:               │  │  │
│  │  │  • Scheduled triggers → Telegram → Claude Code        │  │  │
│  │  │  • Per-project API/URL monitoring                     │  │  │
│  │  │  • Watchdog: restart Claude Code if session dies      │  │  │
│  │  │  • Pause/resume via file flag                         │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │ Window 3: Docker                                           │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ docker compose up                                     │  │  │
│  │  │  • PostgreSQL 16 (shared dev/test databases)          │  │  │
│  │  │  • Per-project staging containers (as needed)         │  │  │
│  │  │  • Playwright Chromium (headless browser for UAT)     │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ~/projects/                                                      │
│  ├── project-alpha/        ← any project with VISION.md           │
│  ├── project-beta/         ← any project with VISION.md           │
│  ├── ...                   ← unlimited projects                   │
│  └── _factory/             ← the factory improves itself          │
│                                                                   │
│  External Services:                                               │
│  ├── GitHub — repos, CI/CD (Actions), auto-merge, deploy          │
│  ├── Telegram — human control plane, bidirectional via Channels   │
│  └── Anthropic Cloud — Scheduled Tasks as backup cron             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Hardware & Environment

### Machine Requirements

| Resource | Minimum | Notes |
|----------|---------|-------|
| CPU | Apple M1 or newer | Efficiency cores handle idle; performance cores for builds |
| RAM | 16 GB | Docker ~4GB, Claude Code ~2GB, OS ~3GB, ~7GB headroom |
| Disk | 256 GB SSD | Projects, Docker images, Playwright browsers, git history |
| Network | Stable broadband | Claude Code API, GitHub, Telegram. Port forwarding optional. |
| Power | Always connected | `caffeinate -s` prevents sleep with lid closed |

### Software Dependencies

| Software | Version | Purpose | Install |
|----------|---------|---------|---------|
| Node.js | 20+ | Claude Code runtime | `brew install node` |
| Python | 3.12+ | Heartbeat daemon | `brew install python@3.12` |
| Git | Any recent | Version control | `brew install git` |
| Docker Desktop | Latest | Container runtime | `brew install --cask docker` |
| tmux | Any | Session persistence | `brew install tmux` |
| Claude Code | 2.1.80+ | Core agent | `npm install -g @anthropic-ai/claude-code` |
| Bun | Latest | Channels plugin runtime | `brew install oven-sh/bun/bun` |
| Playwright | Latest | Browser automation | `npx playwright install chromium` |

### Claude Code Configuration

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_CODE_SUBAGENT_MODEL": "claude-sonnet-4-6"
  }
}
```

### Plugins Required

| Plugin | Source | Purpose |
|--------|--------|---------|
| Telegram channel | `claude-plugins-official` | Bidirectional Telegram messaging |
| Ralph Wiggum | `claude-plugins-official` | Autonomous iteration loops |
| Playwright MCP | `@executeautomation/playwright-mcp-server` | Browser control |

### macOS Persistence

The factory auto-starts on login via a LaunchAgent plist installed to
`~/Library/LaunchAgents/com.genesis.factory.plist`. This calls `scripts/start.sh`
which creates the tmux session with all three windows.

---

## 5. Project Contract

Every managed project MUST follow this structure. The factory discovers projects
by scanning `~/projects/` for directories containing a VISION.md file.

```
~/projects/<project-name>/
├── VISION.md                  # REQUIRED. Human-written. Direction & priorities.
├── CLAUDE.md                  # REQUIRED. Technical context for Claude Code.
├── BACKLOG.md                 # Auto-generated. Scored stories with acceptance criteria.
├── RESEARCH.md                # Auto-generated. Competitive intelligence.
├── AGENTS.md                  # Auto-generated. Accumulated learnings.
├── heartbeat_config.yaml      # Optional. Per-project monitors (API polling, uptime).
├── docker-compose.yml         # Optional. Staging services for this project.
├── .github/workflows/
│   ├── ci.yml                 # Build + test on every PR.
│   └── deploy.yml             # Deploy on merge to main.
├── src/                       # Source code (any language/framework).
└── tests/                     # Test suites.
```

### VISION.md (human writes)

The only file the human must create. Provides direction, priorities, constraints,
and competitive context. Updated monthly or as direction changes. Contains a
`project_weight` field (1-5) that the factory uses to prioritize across projects.

### CLAUDE.md (human + factory maintain)

Technical context: stack, architecture, conventions, critical rules, staging URL,
test credentials, UAT critical flows, domain terminology. Claude Code reads this
before any work on the project. The factory updates it as the codebase evolves.

### BACKLOG.md (factory generates)

Structured stories with ID, status, priority, effort estimate, business justification,
acceptance criteria, design notes, PR reference, and learnings. Stories progress
through: `ready → in_progress → pr_open → done` (or `stuck` / `rejected`).

### RESEARCH.md (factory generates)

Competitive intelligence with dated entries. Competitor analysis, user feedback,
market trends, opportunities ranked by impact. Refreshed weekly by the discovery cycle.

### AGENTS.md (factory generates)

Accumulated learnings specific to this project. What patterns work, what fails,
known-good Playwright selectors, model preferences, common failure modes.
Grows over time. The retrospective agent prunes outdated entries.

---

## 6. Agent Roles

The factory operates as a team of 7 specialized agents plus a global orchestrator.
Each agent is a markdown file in `.claude/agents/` with a defined role, model
preference, allowed tools, and behavioral instructions.

### 6.1 Research Analyst

**Model:** Sonnet (cost-efficient for web research)
**Tools:** Web search, web fetch, file read/write
**Job:** Given a project's VISION.md, research its competitive landscape. Visit
competitor websites, check changelogs, search for user complaints and reviews,
identify market trends. Output: structured RESEARCH.md with dated, sourced findings.

### 6.2 Product Strategist

**Model:** Sonnet
**Tools:** File read/write, codebase search
**Job:** Transform VISION.md + RESEARCH.md + codebase analysis into a prioritized
backlog. Generate 10-20 ideas, score by impact/effort/urgency/risk formula, write
top 5-7 as structured stories with testable acceptance criteria to BACKLOG.md.

### 6.3 Architect

**Model:** Opus (complex reasoning needed for design)
**Tools:** File read, codebase search, file write
**Job:** For a given story, analyze the codebase and design the implementation.
List files to create/modify, database changes, new endpoints, template changes,
test plan (unit + integration + UAT scenarios). Output: design_notes in BACKLOG.md.

### 6.4 Security Reviewer

**Model:** Sonnet
**Tools:** Git diff, grep, file read
**Job:** Review PR code changes for vulnerabilities. Check for injection, auth
bypass, secrets in code, XSS, CSRF, multi-tenant leaks, GDPR violations.
Findings posted as PR comments. CRITICAL findings block auto-merge.

### 6.5 UAT Tester

**Model:** Sonnet
**Tools:** Playwright MCP, Computer Use (fallback), file read
**Job:** After code is deployed to staging, verify it works in a real browser.
Navigate the UI, test each acceptance criterion, test regression flows, test
desktop + mobile viewports, test edge cases. Screenshot every step. Post
results as PR comment. FAIL verdict blocks auto-merge.

### 6.6 DevOps

**Model:** Sonnet
**Tools:** Bash, file read/write, web fetch
**Job:** Manage CI/CD pipelines, Docker services, deployment, and monitoring.
Create GitHub Actions workflows for new projects. Run post-deploy smoke tests.
Manage Docker service health.

### 6.7 Retrospective

**Model:** Sonnet
**Tools:** Git log, GitHub API, file read/write
**Job:** After development cycles, analyze what went well and what didn't.
Update AGENTS.md with learnings. If systematic issues are found, create
improvement stories in `_factory/BACKLOG.md`.

### 6.8 Global Orchestrator (CLAUDE.md)

Not a separate agent file but the global context in `.claude/CLAUDE.md`.
Defines the factory's identity, decision framework, auto-merge/deploy policies,
communication style, cost awareness, error recovery, and routing rules.
Claude Code reads this automatically for every session.

---

## 7. Slash Commands

Commands are markdown files in `.claude/commands/` that Claude Code exposes as
`/command-name` in the terminal and Telegram interface.

| Command | Trigger | What It Does |
|---------|---------|-------------|
| `/setup` | Human, once | Guided onboarding: prerequisites, Telegram, Docker, first project |
| `/new-project` | Human | Create project from template, init git, create GitHub repo |
| `/discover` | Heartbeat (Sun 02:00) or human | Research competitors, generate stories |
| `/build` | Heartbeat (22:00) or human | Full cycle: design → implement → test → merge → deploy |
| `/nightly` | Heartbeat (22:00) | Pick top story, run /build, report summary |
| `/morning-brief` | Heartbeat (07:00) | Compile and send status report via Telegram |
| `/status` | Human | Quick factory health check |
| `/backlog` | Human | Show top stories across all projects |
| `/retro` | Heartbeat (Sun 10:00) | Retrospective: analyze cycles, update learnings |
| `/upgrade` | Heartbeat (Fri 23:00) | Self-improvement: pick factory backlog story, implement |
| `/pause` | Human | Create pause flag, stop automated triggers |
| `/resume` | Human | Remove pause flag, resume automation |

---

## 8. Heartbeat Daemon

### Purpose

A lightweight Python process (~600 lines) that provides four functions:

1. **Clock** — sends scheduled triggers to Claude Code via Telegram at configured times.
2. **Sensors** — polls external APIs/URLs per project configuration and alerts Claude
   Code when anomalies are detected. Uses safe expression evaluation (AST-validated,
   no raw eval) and alert cooldown to prevent notification storms.
3. **Watchdog** — monitors Claude Code session health, restarts if crashed.
4. **System health** — monitors disk space and alerts when running low.

The heartbeat has zero intelligence. It does not decide what to do — it tells Claude
Code what time it is and what's happening in the world. Claude Code decides the rest.

### Schedule

| Trigger | Default Time | Frequency | What It Sends |
|---------|-------------|-----------|---------------|
| Nightly dev cycle | 22:00 | Mon-Fri | "Run /nightly" |
| Morning brief | 07:00 | Daily | "Run /morning-brief" |
| Discovery | 02:00 | Sunday | "Run /discover for all projects" |
| Self-improvement | 23:00 | Friday | "Run /upgrade" |
| Retrospective | 10:00 | Sunday | "Run /retro" |
| Monitors | */5 min | Continuous | Alert on anomaly |
| Watchdog | */1 min | Continuous | Restart CC if dead |

All times are configurable in `heartbeat/config.yaml`.

### Per-Project Monitors

Each project can optionally define monitors in `heartbeat_config.yaml`:

- **`http_poll`** — Fetch a URL, evaluate a Python expression against the response,
  send alert if condition is true. Used for market data, API health, business metrics.
  Alert conditions are evaluated safely via AST validation (no raw eval).
- **`url_health`** — Simple HTTP GET, alert if status code != 200 or connection fails.
  Used for uptime monitoring of production/staging URLs. Sends recovery notification
  when a previously failing service comes back online.

The heartbeat reads these configs from `~/projects/*/heartbeat_config.yaml` and
runs them at the configured interval. Repeated alerts for the same monitor are
suppressed by a configurable cooldown (default 15 minutes).

### Watchdog

Every 60 seconds, the heartbeat checks if the Claude Code tmux window exists.
If Claude Code is not found after 3 consecutive checks (3 minutes), it:

1. Sends a Telegram alert: "Claude Code crashed, restarting..."
2. Recreates the tmux session or window if missing.
3. Restarts the Claude Code session in the tmux window.

### Pause Mechanism

The heartbeat checks for `~/projects/.factory_paused` before each trigger.
If the file exists, scheduled triggers are skipped. Market monitors and the
watchdog continue running even when paused. Claude Code creates/removes this
file via `/pause` and `/resume` commands.

---

## 9. Autonomous Workflow Cycles

### 9.1 Discovery Cycle

**Trigger:** Heartbeat Sunday 02:00, or human `/discover` via Telegram.
**Frequency:** Weekly per project. Skips research if RESEARCH.md < 7 days old.
**Duration:** 15-30 minutes per project.

```
For each project:
  1. research-analyst subagent → RESEARCH.md
     (web search: competitors, reviews, trends)
  2. product-strategist subagent → BACKLOG.md
     (ideas, scoring, structured stories)
  3. Report to Telegram:
     "📋 Discovery: N new stories for {project}"
```

### 9.2 Development Cycle (Nightly)

**Trigger:** Heartbeat Mon-Fri 22:00, or human `/build [STORY-ID]` via Telegram.
**Frequency:** Nightly, one story per cycle (limited by Max plan token budget).
**Duration:** 30-120 minutes depending on story complexity.

```
1. Select story
   (highest priority "ready" across all projects)

2. Architecture — architect subagent
   (analyze codebase, write design_notes)

3. Implementation — Agent Team
   ├── Lead: creates feature branch, coordinates
   ├── Dev teammate: implements in isolated worktree
   └── Test teammate: writes tests in parallel worktree
   Lead merges worktrees, runs full test suite.

4. Ralph Loop (if tests fail)
   Retry up to 5 times. Analyze failure, fix, re-test.
   If stuck after 5: mark story "stuck", report, stop.

5. Push + Create PR
   git push, gh pr create with story description.

6. Wait for CI
   GitHub Actions: build, lint, test.

7. Verification (after CI passes)
   ├── uat-tester subagent: Playwright on staging
   │   (acceptance criteria + regression + screenshots)
   └── security-reviewer subagent: scan diff
       (findings as PR comments, CRITICAL blocks merge)

8. Auto-merge (if ALL gates pass)
   gh pr merge --auto --squash

9. Post-deploy
   Wait for deploy workflow, run smoke test.
   If smoke fails: alert Telegram, do NOT auto-revert.

10. Wrap up
    Update story → "done", record learnings, report to Telegram.
```

### 9.3 Morning Brief

**Trigger:** Heartbeat daily 07:00.
**Duration:** 2-3 minutes.

Compiles: GitHub PR status, story counts per project, recent deploys,
heartbeat alerts, factory health. Sent as concise Telegram message.

### 9.4 Retrospective

**Trigger:** Heartbeat Sunday 10:00.
**Duration:** 10-15 minutes.

The retrospective agent analyzes the past week: completed stories (success
patterns), stuck stories (failure patterns), flaky tests, security findings.
Updates AGENTS.md for each active project. Creates improvement stories in
`_factory/BACKLOG.md` for systematic issues.

### 9.5 Self-Improvement

**Trigger:** Heartbeat Friday 23:00.
**Duration:** 30-60 minutes.

The factory works on its own backlog (`~/projects/_factory/BACKLOG.md`).
Examples: improve scoring algorithm, add new monitor type, better morning
brief format, cost tracking, new agent specialization. Uses the same
/build cycle as any other project.

---

## 10. Auto-Merge & Auto-Deploy Policy

### Auto-Merge Conditions (ALL must be true)

1. GitHub Actions CI passes (build + lint + tests green)
2. Unit and integration tests pass
3. Playwright UAT passes (if project has staging URL configured)
4. Security reviewer found zero CRITICAL issues

If ANY condition fails: PR stays open, Telegram alert sent with details.

### Auto-Deploy

Deploy is triggered by merge to main via project-specific GitHub Actions
workflow (`.github/workflows/deploy.yml`). Each project defines its own
deploy strategy — Docker push, SSH deploy, Vercel/Railway CLI, etc.

After deploy: smoke test runs against production URL (if configured).
If smoke test fails: immediate Telegram alert. No auto-revert — human decides.

### Exception: Factory Self-Project

Changes to `_factory/` auto-merge like any other project. However, changes
to the heartbeat daemon require a manual restart. The factory sends a Telegram
notification: "Heartbeat updated. Restart heartbeat process to activate."

---

## 11. Telegram Interface

### Human → Factory (commands)

| Input | Response |
|-------|----------|
| `/status` | Factory health, project counts, open PRs |
| `/discover` | Starts discovery cycle, reports new stories |
| `/discover <project>` | Discovery for specific project only |
| `/build <STORY-ID>` | Implements specific story immediately |
| `/build` | Auto-picks highest priority story |
| `/backlog` | Shows top 5 stories across all projects |
| `/morning-brief` | Generates and sends morning report |
| `/retro` | Runs retrospective analysis |
| `/pause` | Pauses all automated cycles |
| `/resume` | Resumes automated cycles |
| `/new-project <name>` | Creates new project from template |
| `/upgrade` | Runs factory self-improvement cycle |
| Free text | Claude Code interprets intent and acts |

### Factory → Human (notifications)

| Event | Format |
|-------|--------|
| Story completed | ✅ [ID] title — merged, deployed, {link} |
| Story stuck | ⚠️ [ID] title — stuck after 5 attempts: {error} |
| Deploy success | 🚀 project deployed: {url} (smoke ✅) |
| Deploy failure | 🔴 project deploy failed: {error} |
| Security block | 🔒 CRITICAL in [ID]: {issue} — merge blocked |
| Market alert | ⚡ {project}: {alert message from monitor} |
| Discovery done | 📋 N new stories across M projects |
| Morning brief | 📊 Structured daily report |
| Session crash | 🔧 Claude Code crashed, restarting... |
| Factory paused | ⏸️ Paused. /resume to restart. |
| Factory resumed | ▶️ Resumed. Cycles active. |

### Communication Rules

- One message per event (not a stream of updates).
- Concise — use emoji status indicators.
- Never more than 3 messages without waiting for human response.
- If human asks a question, answer directly before taking action.

---

## 12. New Project Onboarding

When the human sends `/new-project <name>` via Telegram:

1. Create `~/projects/<name>/` directory.
2. Copy VISION.template.md, CLAUDE.template.md, BACKLOG.template.md.
3. Replace `{PROJECT_NAME}` placeholders.
4. Create empty RESEARCH.md and AGENTS.md.
5. Initialize git repo.
6. Ask user: "Tell me about this project — what is it, who is it for, what stack?"
7. Fill VISION.md and CLAUDE.md from user's description.
8. Create GitHub repo: `gh repo create <name> --private --source=. --push`
9. Create basic CI workflow stub.
10. Report: "Project created. Run /discover to generate stories."

On the next scheduled discovery cycle, the factory picks it up automatically.

---

## 13. Docker Infrastructure

### Global Stack (genesis-factory/docker/docker-compose.yml)

- **PostgreSQL 16** — shared database server. Each project gets its own databases
  (e.g., `factory_<project>_dev`, `factory_<project>_test`). The factory user has
  CREATEDB rights and creates databases as needed.

### Per-Project Stacks (~/projects/<name>/docker-compose.yml)

Each project can optionally define its own Docker services for staging.
Claude Code starts/stops these as needed during development and testing.

### Playwright

Playwright browsers (Chromium) are installed locally via `npx playwright install`.
The Playwright MCP server runs as needed during UAT cycles. Headless mode is
default; headed mode available when MacBook lid is open for debugging.

---

## 14. Security & Safety

### Quality Gates (defense in depth)

```
Code written by agent
  └→ Unit tests (pytest/jest/go test/etc.)
      └→ CI pipeline (GitHub Actions)
          └→ UAT browser tests (Playwright screenshots)
              └→ Security review (injection, auth, secrets, XSS)
                  └→ Auto-merge (only if ALL above pass)
                      └→ Deploy (GitHub Actions)
                          └→ Smoke test (Playwright on production)
                              └→ Human notification (Telegram)
```

### Guardrails

- **No production database access.** Agents work with staging/dev DBs only.
- **Git branch protection.** Main requires CI pass before merge.
- **Post-deploy smoke test.** Catches issues immediately after deploy.
- **No auto-revert.** If production breaks, human decides what to do.
- **Secrets management.** API keys in env vars or Docker secrets. Never in code.
  Security reviewer checks for exposed secrets in every PR.
- **Rate limit awareness.** Factory uses Sonnet for subagents to conserve tokens.
  Reports to Telegram if rate-limited.
- **Docker isolation.** Staging apps run in containers with limited host access.
- **Heartbeat is minimal.** ~600 lines, no LLM, negligible attack surface.
  Monitor alert conditions use AST-validated safe evaluation — no raw `eval()`.
- **Pause capability.** `/pause` stops all automation immediately.
- **Alert cooldown.** Monitor alerts are deduplicated with configurable cooldown
  to prevent notification storms when a service is down.

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Buggy code merged | CI + UAT + security review must ALL pass |
| Production broken after deploy | Post-deploy smoke test + immediate Telegram alert |
| Claude Code session dies | Heartbeat watchdog restarts within 3 minutes |
| Rate limit hit | Sonnet for subagents, report via Telegram, slow down |
| Infinite loop | Ralph max 5 iterations, then "stuck" |
| Bad story quality | Acceptance criteria must be testable by Playwright |
| Security vulnerability | security-reviewer blocks CRITICAL findings |
| MacBook offline | Scheduled Tasks on Anthropic cloud as backup |
| Heartbeat crashes | tmux keeps process, LaunchAgent restarts on reboot |
| Alert storm | Cooldown per monitor (default 15 min), recovery notifications |
| Disk full | System health check alerts at configurable threshold (default 10 GB) |
| Unsafe monitor expression | AST-validated safe_eval blocks imports, exec, dunder access |

---

## 15. Cost Model

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Claude Max subscription | $100 | Opus 4.6 + all Claude Code features |
| GitHub | $0 | Free for public repos, free CI minutes |
| Telegram | $0 | Free |
| Docker | $0 | Docker Desktop free for personal use |
| Electricity | ~$3 | MacBook Air M1 ~15W average |
| **Total** | **~$103** | |

### What $103/month Gets You

- 20-25 merged stories per month across all projects
- Weekly competitive research and story generation
- 24/7 market/API monitoring
- Automated browser testing with screenshot evidence
- Security review of every code change
- Auto-deploy to production
- Daily morning brief
- Self-improving system that gets better over time

### Token Budget Considerations

The $100 Max plan has generous but finite token limits. The factory optimizes:
- Main reasoning and complex implementation: Opus 4.6
- Subagents (research, security, UAT, testing): Sonnet 4.6
- Nightly cycles: one M-effort story per night (reliable completion)
- If rate-limited: slow down, skip to next night, report to Telegram

---

## 16. Implementation Phases

### Phase 1: Foundation (Day 1-3)

| Day | Tasks |
|-----|-------|
| 1 | Install software (Node, Python, Docker, tmux, Claude Code). Configure macOS sleep prevention. Set up tmux. Authenticate Claude Code. Enable Agent Teams. Install Telegram Channels plugin. Test bidirectional Telegram messaging. |
| 2 | Clone genesis-factory repo. Create `~/projects/_factory/`. Create global CLAUDE.md. Set up Docker (PostgreSQL). Install Playwright MCP. Install Ralph plugin. Test browser automation. |
| 3 | Write heartbeat config. Test heartbeat → Telegram → Claude Code flow. Test watchdog. Create first project with VISION.md. Run `/discover` — verify RESEARCH.md and BACKLOG.md generated. |

### Phase 2: Development Loop (Day 4-7)

| Day | Tasks |
|-----|-------|
| 4 | Set up first project's Docker staging (if web app). Write project CLAUDE.md. Test Claude Code UAT on staging (open page, screenshot). |
| 5 | Pick simple story from backlog. Run `/build` manually. Observe full cycle. Debug agent/test failures. Iterate on CLAUDE.md and agent definitions. |
| 6 | Run `/build` on second story. Test auto-merge flow. Test deploy flow. Add post-deploy smoke test. |
| 7 | Enable nightly heartbeat trigger. Let it run overnight. Morning: review Telegram messages, check merged PRs. Update AGENTS.md based on what happened. |

### Phase 3: Full Autonomy (Week 2)

| Tasks |
|-------|
| Enable all heartbeat schedules (nightly, discovery, morning brief, retro). |
| Add second project to ~/projects/. |
| Run full week of autonomous cycles. |
| Daily: 10 min review of Telegram + PRs. |
| End of week: major CLAUDE.md update based on learnings. |
| Enable self-improvement cycle (Friday night). |
| Install LaunchAgent for auto-start on reboot. |

### Phase 4: Hardening (Week 3-4)

| Tasks |
|-------|
| Add error recovery patterns to heartbeat. |
| Improve UAT agent based on failure patterns (data-testid strategy, stable selectors). |
| Add per-project heartbeat monitors (uptime, API health, market data). |
| Stress test: add 3-4 projects, observe prioritization and token usage. |
| Add Scheduled Tasks as cloud backup for critical crons. |
| Document operational runbook for your specific setup. |

---

## 17. Repository Structure

```
genesis-factory/
│
├── README.md                          # Product landing page, quickstart
├── LICENSE                            # MIT
├── .gitignore
│
├── .claude/
│   ├── CLAUDE.md                      # Global brain: identity, policies, routing
│   │
│   ├── agents/
│   │   ├── research-analyst.md        # Competitive intelligence
│   │   ├── product-strategist.md      # Story generation from research
│   │   ├── architect.md               # Technical design per story
│   │   ├── security-reviewer.md       # PR security review
│   │   ├── uat-tester.md              # Browser testing with Playwright + Computer Use
│   │   ├── devops.md                  # CI/CD, Docker, deployment
│   │   └── retrospective.md           # Weekly learning analysis
│   │
│   ├── commands/
│   │   ├── setup.md                   # /setup — guided onboarding
│   │   ├── new-project.md             # /new — create project from template
│   │   ├── discover.md                # /discover — research + generate stories
│   │   ├── build.md                   # /build — full dev cycle for one story
│   │   ├── nightly.md                 # /nightly — autonomous nightly cycle
│   │   ├── morning-brief.md           # /morning-brief — daily status report
│   │   ├── status.md                  # /status — quick health check
│   │   ├── retro.md                   # /retro — weekly retrospective
│   │   ├── upgrade.md                 # /upgrade — factory self-improvement
│   │   ├── backlog.md                 # /backlog — top stories overview
│   │   ├── pause.md                   # /pause — stop automation
│   │   └── resume.md                  # /resume — restart automation
│   │
│   └── hooks/
│       └── post-tool-use.yaml         # Auto-fix for pytest/Playwright failures
│
├── heartbeat/
│   ├── factory_heartbeat.py           # Main daemon (~600 lines, zero LLM)
│   ├── config.example.yaml            # Template configuration
│   ├── requirements.txt               # schedule, requests, pyyaml
│   ├── test_heartbeat.py              # Unit tests (safe_eval, cooldown, pause)
│   └── conftest.py                    # Pytest config for isolated testing
│
├── docker/
│   ├── docker-compose.yml             # PostgreSQL global stack
│   └── init-db.sql                    # Database initialization
│
├── scripts/
│   ├── start.sh                       # Start factory (tmux + Docker)
│   ├── stop.sh                        # Stop factory
│   └── com.genesis.factory.plist      # macOS LaunchAgent for auto-start
│
├── templates/
│   ├── VISION.template.md             # Template for new projects
│   ├── CLAUDE.template.md             # Template for project technical context
│   ├── BACKLOG.template.md            # Template for project backlog
│   └── factory-project/               # Pre-filled _factory self-project
│       ├── VISION.md
│       ├── CLAUDE.md
│       └── BACKLOG.md                 # Initial factory improvement stories
│
└── docs/
    ├── architecture.md                # How it works
    ├── faq.md                         # Common questions
    └── examples/
        ├── dochazka-heartbeat.yaml    # Example: SaaS uptime monitoring
        └── trading-heartbeat.yaml     # Example: market data monitoring
```

---

## 18. Extensibility

### Adding New Agent Roles

Create a markdown file in `.claude/agents/` with YAML frontmatter (name, model,
tools) and behavioral instructions. The agent becomes available to all commands
as a subagent. No code changes needed.

### Adding New Commands

Create a markdown file in `.claude/commands/`. It appears as a slash command
in Claude Code and is accessible via Telegram. Describe what it should do in
natural language — Claude Code interprets and executes.

### Adding New Monitor Types

Extend `heartbeat_config.yaml` schema. Currently supports `http_poll` and
`url_health`. New types (RSS polling, email checking, file watching) can be
added to `factory_heartbeat.py` — or the factory can add them via
self-improvement cycles.

### Adding New Hooks

Create YAML entries in `.claude/hooks/`. Hooks fire after tool use (e.g.,
after running pytest, after Playwright tests). They inject guidance into
Claude Code's context to auto-handle common failure patterns.

### Scaling to More Projects

Just create `~/projects/<name>/VISION.md`. The factory discovers it on the
next cycle. The heartbeat reads its `heartbeat_config.yaml` if present.
No configuration changes to the factory itself.

---

## 19. Limitations & Known Constraints

| Constraint | Detail |
|------------|--------|
| Max plan token limits | ~1 M-effort story per nightly cycle. L/XL stories may need multiple nights. |
| Session persistence | Channels requires an active Claude Code session. If session dies, 1-3 min gap. |
| No true parallelism across projects | Factory works on one project per nightly cycle. Within a story, Agent Teams parallelize. |
| Headless browser only on remote | If MacBook lid is closed, Playwright runs headless. Screenshots are available but real-time visual debugging requires opening the lid. |
| No auto-revert | If deploy breaks production, human must intervene. This is intentional (auto-revert can be worse than the bug). |
| Research preview features | Channels, Auto Mode, Computer Use are research previews — APIs may change. |
| Internet dependency | Claude Code requires API connectivity. Offline = no factory. |

---

## Appendix A: Daily Rhythm Visualization

```
  00  01  02  03  04  05  06  07  08  09  10  11  12  ...  22  23  00
  │   │   │   │   │   │   │   │   │   │   │   │   │       │   │   │
  │   │   │   │   │   │   │   │   │   │   │   │   │       │   │   │
  ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ───   ─── ─── ───
Sun          🔍                  ☀️      📝                          
Mon                              ☀️                      🌙         
Tue                              ☀️                      🌙         
Wed                              ☀️                      🌙         
Thu                              ☀️                      🌙         
Fri                              ☀️                      🌙  🔧    
Sat                              ☀️                                 

🔍 Discovery (Sun 02:00)    ☀️ Morning Brief (daily 07:00)
📝 Retro (Sun 10:00)        🌙 Nightly Dev (Mon-Fri 22:00)
🔧 Self-Improve (Fri 23:00)

Monitors: ───── continuous every 5 min ─────
Watchdog: ───── continuous every 1 min ─────
Telegram: ───── always listening ─────
```

---

## Appendix B: Technology Stack Summary

| Component | Technology | Role |
|-----------|-----------|------|
| Core Agent | Claude Code (Opus 4.6) | All intelligent decisions |
| Subagent Model | Claude Sonnet 4.6 | Cost-efficient for focused tasks |
| Communication | Telegram via Channels plugin | Bidirectional human-factory interface |
| Parallel Dev | Agent Teams + Git Worktrees | Isolated Dev + Test teammates |
| Autonomous Loops | Ralph Wiggum plugin | Iterate until tests pass |
| Browser Testing | Playwright MCP (headless Chromium) | Real browser UAT with screenshots |
| Visual Verification | Computer Use | Desktop interaction, visual checks |
| Safe Autonomy | Auto Mode | AI-judged permission decisions |
| Cloud Backup | Scheduled Tasks | Critical crons when machine offline |
| Orchestration | Python heartbeat (~600 lines) | Clock + sensors + watchdog |
| Infrastructure | Docker (PostgreSQL, staging apps) | Database and service isolation |
| Version Control | Git + GitHub | Repos, PRs, CI/CD, auto-merge |
| CI/CD | GitHub Actions | Build, test, deploy pipelines |
| Persistence | /memory + AGENTS.md | Learnings across sessions |
| macOS Persistence | LaunchAgent + caffeinate | Auto-start, prevent sleep |
