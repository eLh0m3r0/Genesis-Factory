# 🏭 Genesis Factory

**Your autonomous IT team, running on a MacBook.**

Genesis Factory is a complete autonomous software development system. It discovers
what to build, designs solutions, writes code, tests in real browsers, reviews for
security, merges to main, and deploys — across any number of projects simultaneously.

You provide direction. It does the rest.

## How It Works

```
You: "Build the best Czech attendance SaaS for small companies"
        ↓ (write VISION.md, walk away)

Factory: researches competitors → generates stories → designs architecture
         → implements code → runs tests → browser UAT → security review
         → auto-merges PR → deploys → sends you Telegram summary

You: (next morning, on phone) "✅ 2 stories shipped. 1 stuck. Here's why..."
```

## Quickstart

```bash
git clone https://github.com/youruser/genesis-factory.git
cd genesis-factory
claude
```

Then type:

```
/setup
```

Claude guides you through everything — Telegram bot, Docker, macOS config,
your first project. Takes about 15 minutes.

## Requirements

| What | Why |
|------|-----|
| MacBook with 16GB+ RAM (Apple Silicon) | Dedicated factory machine, runs 24/7 lid-closed |
| Claude Code Max subscription ($100/month) | Opus 4.6 for coding, Agent Teams, Channels, Auto Mode |
| GitHub account | Repos, CI/CD, auto-merge |
| Telegram account | Your control plane — command the factory from your phone |

## What It Does

| Role | What | How |
|------|------|-----|
| 🔍 **Product Analyst** | Discovers what to build | Researches competitors, analyzes trends, reads user feedback |
| 📋 **Product Owner** | Prioritizes work | Generates scored stories with acceptance criteria |
| 🏗️ **Architect** | Designs solutions | Analyzes codebase, writes technical design per story |
| 💻 **Developer** | Writes code | Agent Teams with parallel Dev + Test in isolated worktrees |
| 🧪 **QA Engineer** | Tests everything | pytest + Playwright browser UAT with screenshots |
| 🔒 **Security** | Reviews every change | Scans for injection, auth bypass, data leaks, secrets |
| 🚀 **DevOps** | Ships to production | Auto-merge when green, deploy via GitHub Actions |
| 📊 **Ops Monitor** | Watches production | Post-deploy smoke tests, uptime monitoring, alerts |
| 🔄 **Retrospective** | Learns & improves | Records what worked/failed, improves agents over time |

## Commands

| Command | What happens |
|---------|-------------|
| `/setup` | Guided first-time onboarding (15 min) |
| `/new-project <name>` | Create a new project from template |
| `/discover` | Research competitors, generate new stories |
| `/build [STORY-ID]` | Implement a story (or auto-pick top priority) |
| `/nightly` | Full development cycle (auto-triggered at 22:00) |
| `/morning-brief` | Status report across all projects |
| `/status` | Quick factory health check |
| `/backlog` | Show top stories across all projects |
| `/retro` | Run retrospective, update learnings |
| `/upgrade` | Self-improvement cycle on the factory itself |
| `/pause` | Pause all automated cycles |
| `/resume` | Resume automated cycles |
| Any text via Telegram | Claude interprets and acts |

## Architecture

```
MacBook Air M1 (lid closed, 24/7)
│
├── tmux "factory"
│   ├── Claude Code + Channels (Telegram)     ← the brain
│   ├── Heartbeat (Python, no LLM)            ← clock + sensors
│   └── Docker (PostgreSQL, staging, browser)  ← infrastructure
│
├── ~/projects/
│   ├── your-project/     ← any project with VISION.md
│   ├── another-project/
│   └── _factory/          ← the factory improves itself
│
├── GitHub                 ← PRs, CI/CD, auto-merge, deploy
└── Telegram               ← your phone = remote control
```

The **heartbeat** is a lightweight Python daemon (~600 lines, zero LLM calls).
It's a clock that tells Claude "it's 22:00, time to code" and sensors
that watch markets/APIs and alert Claude when something needs attention.

All intelligence lives in Claude Code — the heartbeat just provides triggers.

## Daily Rhythm

| Time | What | Your involvement |
|------|------|-----------------|
| 02:00 Sun | Discovery: competitor research, new stories | None |
| 07:00 Daily | Morning brief sent to Telegram | Read on phone (2 min) |
| 10:00 Sun | Retrospective: analyze cycles, update learnings | None |
| 22:00 Mon-Fri | Nightly: implement top story, test, merge, deploy | None |
| 23:00 Fri | Self-improvement: factory upgrades itself | None |
| Anytime | Market alerts, deploy notifications | Glance at Telegram |

## Cost

| Item | Monthly |
|------|---------|
| Claude Max subscription | $100 |
| GitHub | Free |
| Telegram | Free |
| Docker | Free |
| Electricity (MacBook ~15W) | ~$3 |
| **Total** | **~$103** |

## FAQ

**Can it work on any tech stack?**
Yes. Each project has its own CLAUDE.md describing the stack. Python, Node,
Go, Rust, whatever. The factory adapts.

**Will it break my production?**
Every change goes through: unit tests → integration tests → browser UAT →
security review → CI/CD. Only auto-merges when ALL pass. Post-deploy smoke
test catches issues immediately.

**What if it gets stuck?**
After 5 failed attempts, it marks the story as "stuck" and moves on. You get
a Telegram notification with the error. Fix it manually or add guidance to
CLAUDE.md and it'll retry next cycle.

**Can I pause it?**
Send `/pause` via Telegram. Send `/resume` to restart.

**Does it really improve itself?**
Yes. The factory is a project in `~/projects/_factory/`. Its own backlog
includes improvements to agents, heartbeat, and workflows. Friday night
cycles implement these improvements.

## License

MIT — free for any use.

## Credits

Built with [Claude Code](https://code.claude.com) by Anthropic.
Inspired by Karpathy's autoresearch, BMAD Method, Ralph Wiggum Loop,
and the KellyClaude software factory concept.
