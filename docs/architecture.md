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

## Why This Design

- **No OpenClaw/NanoClaw needed.** Claude Code Channels + Agent Teams cover it.
- **No extra API costs.** Everything runs on Max subscription.
- **Heartbeat is deliberately dumb.** All intelligence in Claude Code.
- **Self-improving.** The factory is a project that evolves itself.
