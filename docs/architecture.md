# Architecture

## Three Components

1. **Claude Code + Channels** = brain. Makes all decisions. Runs in tmux.
2. **Heartbeat** = clock + sensors. Python daemon, zero LLM, sends triggers via Telegram.
3. **Docker** = infrastructure. PostgreSQL, staging apps, Playwright browsers.

## Data Flow

```
Human (Telegram) → Claude Code Channels → Claude Code session
Heartbeat → Telegram → Claude Code Channels → Claude Code session
                                                    │
                                    ┌───────────────┼────────────┐
                                    ▼               ▼            ▼
                              Agent Teams      Subagents    Playwright
                              (worktrees)     (research,    (browser)
                                              security)
                                    │               │            │
                                    ▼               ▼            ▼
                               Git push       PR comments   Screenshots
                                    │
                                    ▼
                             GitHub Actions → Auto-merge → Deploy
```

## Heartbeat Safety Features

- **Safe expression evaluation.** Monitor alert conditions are validated via AST
  analysis before execution — no raw `eval()`. Blocks imports, exec, dunder access.
- **Alert cooldown.** Repeated alerts for the same monitor are suppressed for a
  configurable period (default 15 min), preventing notification storms.
- **Recovery notifications.** When a failing url_health monitor recovers, a
  recovery message is sent automatically.
- **Log rotation.** Heartbeat log files rotate at 5 MB, keeping 3 backups.
- **Disk monitoring.** System health checks alert when disk space drops below threshold.
- **Robust watchdog.** If the tmux session or Claude Code window is missing, the
  watchdog recreates it before restarting Claude Code.

## Communication Architecture

The factory uses two Telegram paths — both through the same bot:

1. **Claude Code Channels** (brain → human, human → brain):
   Official Telegram channel plugin. Provides two-way conversation, permission
   relay (approve/deny tool calls from your phone), and command handling.
   Started with `claude --channels`.

2. **Heartbeat Bot API** (sensors → human):
   Direct `requests.post()` to Telegram Bot API. Used by the heartbeat daemon
   for alerts, triggers, and health notifications. Works independently of
   Claude Code — sends alerts even if the Claude session is down.

Both use the same `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

## Useful Claude Code Features

- **Auto Mode**: Safety classifier AI reviews each tool call. Safe actions
  proceed automatically, risky ones are blocked. Use for nightly cycles.
- **Agent Teams**: Lead + Dev + Test teammates with shared task list and
  mailbox. Each teammate works in an isolated worktree.
- **Effort levels** (`/effort low|medium|high`): Control how much the model
  thinks. Use medium for routine tasks, high for complex implementation.
- **`/loop`**: Run recurring checks during active sessions (e.g.,
  `/loop 5m check deploy status`). Complements the heartbeat.
- **Scheduled Tasks** (`/schedule`): Cloud-based recurring tasks that run
  even when the MacBook is offline. Backup for CI monitoring and PR reviews.
- **Computer Use**: Direct macOS desktop interaction for visual verification.
  Prefer Playwright MCP for structured testing.

## Why This Design

- **No OpenClaw/NanoClaw needed.** Claude Code Channels + Agent Teams cover it.
- **No extra API costs.** Everything runs on Max subscription.
- **Heartbeat is deliberately dumb.** All intelligence in Claude Code.
- **Self-improving.** The factory is a project that evolves itself.
