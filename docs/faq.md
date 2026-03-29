# FAQ

**Cost?** ~$103/month (Claude Max $100 + electricity $3).

**Any tech stack?** Yes. Each project has its own CLAUDE.md.

**Will it break production?** Every change passes CI + UAT + security review.

**Session crash?** Heartbeat watchdog restarts within 3 minutes.

**Rate limits?** Uses Sonnet for subagents. Reports if limited.

**Pause?** Send /pause via Telegram.

**New project?** Send "/new-project my-project" via Telegram.

**Stuck story?** After 5 fails → marked stuck → you get Telegram alert.

**Is monitor eval() safe?** Yes. Alert conditions use AST-validated safe evaluation
that blocks imports, exec, dunder access, and arbitrary code execution. Only math,
comparisons, and safe builtins (float/abs/any/all/...) are allowed.

**Alert storm?** Monitors have a cooldown period (default 15 min). If a URL is down,
you get one alert per 15 minutes, not one every 5 minutes. Recovery is notified too.

**Disk full?** The heartbeat monitors disk space hourly and alerts via Telegram
when free space drops below the configured threshold (default 10 GB).

**Channels vs custom Telegram bot?** The factory uses both. Claude Code Channels
is the official Telegram plugin for two-way communication (commands, permission
relay from phone). The heartbeat daemon uses the Telegram Bot API directly for
alerts and triggers — this works independently, even when Claude Code is down.
Both use the same bot token.

**Auto Mode?** Auto Mode replaces manual permission approvals for nightly cycles.
A safety classifier AI reviews each tool call — safe actions (file reads/writes,
git, tests) proceed automatically, risky ones are blocked. Enable with
`claude --enable-auto-mode`.

**What about /loop?** Use `/loop 5m check deploy status` for recurring in-session
checks. It complements the heartbeat — `/loop` runs inside Claude Code with full
tool access, while the heartbeat runs independently as a Python daemon.
