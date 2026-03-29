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
