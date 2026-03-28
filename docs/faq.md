# FAQ

**Cost?** ~$103/month (Claude Max $100 + electricity $3).

**Any tech stack?** Yes. Each project has its own CLAUDE.md.

**Will it break production?** Every change passes CI + UAT + security review.

**Session crash?** Heartbeat watchdog restarts within 2 minutes.

**Rate limits?** Uses Sonnet for subagents. Reports if limited.

**Pause?** Send /pause via Telegram.

**New project?** Send "/new my-project" via Telegram.

**Stuck story?** After 5 fails → marked stuck → you get Telegram alert.
