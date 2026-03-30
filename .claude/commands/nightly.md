---
description: "Build cycle — pick stories and build them. Triggered by heartbeat."
---

# Build Cycle

The main autonomous cycle, triggered by the heartbeat at configured times.

## Build Modes

Check the trigger message for the mode:

- **Single** (default): Build one story, then stop.
- **Continuous**: Keep building stories until backlog is empty or rate-limited.

## Process

1. Check factory health:
   - Docker services running? If not, try `docker compose up -d`
   - Any urgent Telegram messages from human? Handle those first.

2. Check for urgent issues:
   - Any failed deploys? Fix first.
   - Any "in_progress" stories? Finish those first.

3. Pick what to build:
   - Scan ~/projects/*/BACKLOG.md for "ready" stories
   - Skip stories with `blocked_by` fields where the blocking story is not "done"
   - If stories available: run /build on the top unblocked one
   - If NO stories available: run /discover for least-researched project
   - If everything is caught up: run /upgrade (self-improvement)

4. After completing a story:

   **Single mode**: send summary and stop.

   **Continuous mode**:
   - Check for rate-limit errors. If rate-limited:
     Report to Telegram: "⏸️ Rate-limited after {N} stories. Will resume next cycle."
     Stop. The next scheduled build trigger picks up automatically.
   - Check backlog for more "ready" stories.
   - If stories available: go back to step 3.
   - If backlog empty:
     Report: "✅ Backlog clear — {N} stories completed this cycle."
     Stop.

5. Report build cycle summary to Telegram:
   "🔨 Build cycle complete:
    ✅ [{ID}] {title} — merged
    ⚠️ [{ID}] {title} — stuck (selector changed)
    📊 Stories this cycle: {N} done, {M} stuck
    📋 Remaining in backlog: {R} ready
    💰 Estimated token usage: {estimate}"
