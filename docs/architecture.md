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

## Why This Design

- **No OpenClaw/NanoClaw needed.** Claude Code Channels + Agent Teams cover it.
- **No extra API costs.** Everything runs on Max subscription.
- **Heartbeat is deliberately dumb.** All intelligence in Claude Code.
- **Self-improving.** The factory is a project that evolves itself.
