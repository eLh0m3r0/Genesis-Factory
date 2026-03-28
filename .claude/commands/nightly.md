---
description: "Full nightly development cycle — pick top story and build it. Triggered by heartbeat at 22:00."
---

# Nightly Development Cycle

This is the main autonomous cycle, typically triggered by the heartbeat at 22:00.

## Process

1. Check factory health:
   - Docker services running? If not, try `docker compose up -d`
   - Any urgent Telegram messages from human? Handle those first.

2. Check for urgent issues:
   - Any failed deploys? Fix first.
   - Any "in_progress" stories? Finish those first.

3. Pick what to build:
   - Scan ~/projects/*/BACKLOG.md for "ready" stories
   - If stories available: run /build on the top one
   - If NO stories available: run /discover for least-researched project
   - If everything is caught up: run /upgrade (self-improvement)

4. After completing one story, evaluate:
   - Is there time for another? (check rate limits, time)
   - If yes and a small (S) story is available: do another
   - If no: send summary and stop

5. Report nightly summary to Telegram:
   "🌙 Nightly cycle complete:
    ✅ [{ID}] {title} — merged
    ⚠️ [{ID}] {title} — stuck (selector changed)
    📊 Next in backlog: [{ID}] {title}
    💰 Estimated token usage: moderate"
