# Troubleshooting Guide

Systematic decision trees for common Genesis Factory problems.

---

## Factory won't start

```
Is Docker Desktop running?
├── No → Start Docker Desktop, then run ./scripts/start.sh
└── Yes
    Is tmux installed?
    ├── No → brew install tmux
    └── Yes
        Does ./scripts/start.sh give an error?
        ├── Docker compose error → Check docker/docker-compose.yml
        │   Is port 5432 in use? → lsof -i :5432 → kill the process or change port
        ├── tmux error → kill existing session: tmux kill-session -t factory
        └── Claude Code error → Check: claude --version (need 2.1.80+)
            Not installed? → npm install -g @anthropic-ai/claude-code
```

**Quick fix**: `./scripts/stop.sh && ./scripts/start.sh`

---

## Heartbeat is silent (no Telegram messages)

```
Is the heartbeat process running?
├── No
│   Check tmux: tmux attach -t factory → switch to heartbeat window
│   Is there an error?
│   ├── "Config file not found" → cp config.example.yaml config.yaml and fill in values
│   ├── "TELEGRAM_BOT_TOKEN looks invalid" → Check bot_token format: 123456789:ABCdef...
│   ├── "Invalid YAML" → Fix syntax in config.yaml (check indentation)
│   └── Python error → pip3 install -r requirements.txt
│
└── Yes (process running but no messages)
    Is the Telegram bot token correct?
    ├── Test: curl "https://api.telegram.org/bot<TOKEN>/getMe"
    │   ├── Returns bot info → Token is fine, check chat_id
    │   └── Returns error → Token is wrong, get new one from @BotFather
    │
    Is the chat_id correct?
    ├── Send a message to the bot from Telegram
    ├── Check: curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
    ├── Find your chat_id in the response
    └── Update config.yaml with correct chat_id
    │
    Is the factory paused?
    ├── Check: ls ~/projects/.factory_paused
    ├── If exists → rm ~/projects/.factory_paused (or send /resume)
    └── If not → Check heartbeat.log for errors
```

---

## Story got stuck

```
Check Telegram alert for the stuck story details.

What phase did it fail in?
├── Architecture → Design was incomplete
│   Fix: Edit BACKLOG.md, add clearer acceptance criteria, /retry STORY-ID
│
├── Implementation → Code errors
│   Check: git log --oneline -10 in the project repo
│   Check: Any partial PR? gh pr list
│   Fix: Review the error in Telegram, fix manually or /retry
│
├── Tests → Test failures after 5 Ralph loop iterations
│   Check: What test failed? (Telegram shows the error)
│   ├── Missing dependency → Add to requirements.txt/package.json
│   ├── Database issue → Is Docker/PostgreSQL running?
│   ├── Playwright timeout → Selector changed, update AGENTS.md
│   └── Flaky test → Check AGENTS.md for known patterns
│
├── CI → GitHub Actions failed
│   Check: gh run list --repo owner/repo --limit 3
│   Check: gh run view <run-id> --log-failed
│   Fix: Fix the CI issue, push, re-run
│
└── UAT → Browser test failed
    Check: PR comments for UAT report with screenshots
    Fix: Review screenshots, fix UI issue, /retry
```

**Quick fix**: `/retry STORY-ID` resets the story and tries again.

---

## Docker service is down

```
Check Docker status:
  docker compose -f docker/docker-compose.yml ps

Is Docker Desktop running?
├── No → Start Docker Desktop
└── Yes
    Are containers running?
    ├── No → docker compose -f docker/docker-compose.yml up -d
    │   Still failing?
    │   ├── Port conflict → lsof -i :5432 → change port in docker-compose.yml
    │   ├── Disk full → df -h / → clean up (docker system prune)
    │   └── Image pull error → Check internet, try: docker compose pull
    │
    └── Yes but unhealthy
        Check logs: docker compose -f docker/docker-compose.yml logs --tail 50
        ├── PostgreSQL crash → docker compose restart postgres
        ├── Out of memory → Increase Docker memory in Docker Desktop settings
        └── Corrupted data → docker compose down -v && docker compose up -d
            (WARNING: this deletes database data)
```

---

## Rate limited

```
Which API is rate limited?
├── Claude Code (Anthropic API)
│   Message: "rate_limit_error" or slow responses
│   Fix: Wait 5-10 minutes. The factory automatically slows down.
│   Prevent: Use /effort medium for routine tasks, use Sonnet for subagents
│
├── GitHub API
│   Message: "API rate limit exceeded"
│   Fix: Wait until the rate limit resets (check X-RateLimit-Reset header)
│   Prevent: Cache API responses, reduce gh command frequency
│
├── Telegram API
│   Message: "Too Many Requests: retry after X"
│   Fix: Heartbeat auto-retries with backoff
│   Prevent: Reduce alert frequency (increase alert_cooldown_seconds)
│
└── Other API (project-specific monitor)
    Check heartbeat.log for details
    Fix: Increase monitor_interval_seconds in config.yaml
```

---

## Claude Code keeps crashing/restarting

```
Check Telegram for watchdog alerts.

How often is it restarting?
├── Every few minutes
│   The watchdog uses exponential backoff (1m→2m→5m→10m→30m)
│   After 5 restarts/hour it stops and alerts you
│   Check: tmux attach -t factory → claude window → read the error
│   ├── "rate_limit_error" → Wait. Reduce usage.
│   ├── "context_window_exceeded" → Session too long. Normal restart is fine.
│   ├── "connection_error" → Check internet connection
│   └── Crash/segfault → Update Claude Code: npm update -g @anthropic-ai/claude-code
│
├── Once overnight → Normal. Claude Code sessions have limited lifetime.
│   The watchdog restarts it automatically.
│
└── Never → Good. Everything is working.
```

---

## LaunchAgent not starting on boot

```
Check if the plist is loaded:
  launchctl list | grep genesis

├── Not found
│   Install: ./scripts/install-launchagent.sh
│   Or manually:
│     cp scripts/com.genesis.factory.plist ~/Library/LaunchAgents/
│     Edit the plist: replace __FACTORY_DIR__ with your actual path
│     launchctl load ~/Library/LaunchAgents/com.genesis.factory.plist
│
├── Found but not running (PID = -)
│   Check status: launchctl print gui/$(id -u)/com.genesis.factory
│   ├── "Could not find service" → launchctl load the plist again
│   └── Exit code shown → Check the error, fix, then:
│       launchctl unload ~/Library/LaunchAgents/com.genesis.factory.plist
│       launchctl load ~/Library/LaunchAgents/com.genesis.factory.plist
│
└── Found and running → LaunchAgent is fine, check tmux session
```

---

## Quick diagnostics

Run these commands to check overall health:

```bash
# Factory processes
tmux ls                              # Should show "factory" session
tmux list-windows -t factory         # Should show: claude, heartbeat, docker

# Docker
docker compose -f docker/docker-compose.yml ps  # All services "Up"

# Heartbeat
tail -20 heartbeat/heartbeat.log     # Recent activity, any errors?

# Disk
df -h /                              # Check free space

# Claude Code
claude --version                     # Should be 2.1.80+

# GitHub
gh auth status                       # Should be authenticated
```

Or use the validation script: `./scripts/validate-factory.sh`
