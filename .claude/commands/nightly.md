---
description: "Build cycle — pick stories and build them. Triggered by heartbeat."
---

# Build Cycle

The main autonomous cycle, triggered by the heartbeat at configured times.

## Build Modes

Check the trigger message for the mode:

- **Single** (default): Build one story, then stop.
- **Continuous**: Keep building stories until backlog is empty or rate-limited.

## Context Continuity

At the start, read `~/projects/_factory/last_cycle.md` if it exists.
It contains a summary of the previous cycle — what was built, where it
stopped, and what's next. Use this to orient yourself, especially after
a rate-limit pause in continuous mode.

At the end, write/overwrite `~/projects/_factory/last_cycle.md`:
```markdown
# Last Build Cycle
- **When**: {datetime}
- **Mode**: single / continuous
- **Stories completed**: [{ID}] {title}, [{ID}] {title}, ...
- **Stories stuck**: [{ID}] {title} — {reason}
- **Stopped because**: backlog empty / rate-limited / single mode
- **In progress**: [{ID}] {title} (if interrupted mid-build)
- **Next up**: [{ID}] {title} (top ready story)
- **Notes**: {anything the next cycle should know}
```

## Process

1. Read `~/projects/_factory/last_cycle.md` for previous cycle context.

2. Check factory health:
   - Docker services running? If not, try `docker compose up -d`
   - Any urgent Telegram messages from human? Handle those first.

3. Check for urgent issues:
   - Any failed deploys? Fix first.
   - Any "in_progress" stories? Finish those first.

4. Pick what to build:
   - Scan ~/projects/*/BACKLOG.md for "ready" stories
   - Skip stories with `blocked_by` fields where the blocking story is not "done"
   - If stories available: run /build on the top unblocked one
   - If NO stories available:
     - Find projects NOT skipping discovery (check VISION.md skip_phases)
     - If eligible projects: run /discover for least-researched eligible project
     - If none eligible: run /upgrade (self-improvement)
   - If everything is caught up: run /upgrade (self-improvement)

5. After completing a story:

   **Single mode**: send summary and stop.

   **Continuous mode**:
   - Check for rate-limit errors. If rate-limited:
     Report to Telegram: "⏸️ Rate-limited after {N} stories. Will resume next cycle."
     Stop. The next scheduled build trigger picks up automatically.
   - Check backlog for more "ready" stories.
   - If stories available: go back to step 4.
   - If backlog empty:
     Report: "✅ Backlog clear — {N} stories completed this cycle."
     Stop.

6. Write `~/projects/_factory/last_cycle.md` with cycle summary (see format above).

7. Report build cycle summary to Telegram:
   "🔨 Build cycle complete:
    ✅ [{ID}] {title} — merged
    ⚠️ [{ID}] {title} — stuck (selector changed)
    📊 Stories this cycle: {N} done, {M} stuck
    📋 Remaining in backlog: {R} ready
    💰 Estimated token usage: {estimate}"
