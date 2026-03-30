# Your First Day with Genesis Factory

Setup is done. Here's what happens next.

## What happens tonight (22:00)

The heartbeat daemon sends a trigger at 22:00 (Mon-Fri). Claude Code
receives it via Telegram Channels and runs the `/nightly` cycle:

1. Scans all projects for "ready" stories in BACKLOG.md
2. Picks the highest-priority story
3. Designs, implements, tests, and creates a PR
4. If all checks pass: auto-merges and deploys
5. Sends a summary to Telegram

**If no stories exist yet**: Claude runs `/discover` instead — researching
competitors and generating stories for your project.

## Tomorrow morning (07:00)

You'll get a morning brief on Telegram:

```
📊 Morning Brief — 2026-03-31

Projects:
• my-project: 1 shipped, 4 in backlog, 0 stuck

PRs:
• ✅ #1 Add user dashboard — merged 23:47

Factory:
• Uptime: 9h 12m
• Disk: 45GB/500GB
• Next nightly: 22:00
```

## What to do now

### 1. Check factory status
Send `/status` in Telegram or run it in the Claude Code session.

### 2. Review your VISION.md
Open `~/projects/YOUR_PROJECT/VISION.md` and make sure it describes:
- What the project does
- Who it's for
- Technical priorities
- What to build next

This is the single most important file — it drives everything.

### 3. Generate stories
Run `/discover YOUR_PROJECT` to generate an initial backlog. This takes
10-15 minutes (it researches competitors, analyzes your codebase, and
creates scored stories with acceptance criteria).

### 4. Review the backlog
Check `~/projects/YOUR_PROJECT/BACKLOG.md` after discovery. The factory
generated stories automatically, but you can:
- Adjust priorities (lower number = higher priority)
- Edit acceptance criteria to be more specific
- Add stories manually following the same format

### 5. (Optional) Trigger a build manually
Don't want to wait until 22:00? Run `/build` to start immediately.

## Your first week

| Day | What happens |
|-----|-------------|
| Day 1 | Discovery generates stories. First nightly builds top story. |
| Day 2 | Morning brief shows results. Factory continues with next story. |
| Day 3-5 | Factory works through the backlog autonomously. |
| Day 6 (Fri) | Self-improvement cycle — factory upgrades itself. |
| Day 7 (Sun) | Discovery + retrospective. New stories generated. |

## Telegram commands

You can send these to the factory via Telegram:

| Command | What it does |
|---------|-------------|
| `/status` | Quick health check |
| `/backlog` | Show top stories across all projects |
| `/build` | Start building the top story now |
| `/discover PROJECT` | Research competitors, generate stories |
| `/pause` | Stop automated cycles |
| `/resume` | Resume automated cycles |

## Common questions

**"Nothing happened overnight"**
Check: Is the heartbeat running? Is Claude Code running in tmux?
Run `tmux attach -t factory` to see the windows.

**"A story got stuck"**
This happens when tests fail 5 times. Check the Telegram alert for details.
The factory moves on to the next story automatically.

**"I want to change what the factory works on"**
Edit the project's VISION.md or BACKLOG.md. The factory reads these
files at the start of every cycle.

**"How do I add a new project?"**
Run `/new-project my-new-project` and follow the wizard.

See also: [Troubleshooting](TROUBLESHOOTING.md) | [FAQ](faq.md) | [Architecture](architecture.md)
