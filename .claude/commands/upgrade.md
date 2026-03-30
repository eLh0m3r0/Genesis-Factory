---
description: "Self-improvement cycle — factory upgrades itself."
---

# Factory Self-Improvement

Work on the factory's own improvement (~/projects/_factory/).
Runs weekly on Fridays at 23:00.

## Process

### Step 1: Platform Scan — Check for new Claude/Anthropic features

Before working on stories, scan for platform updates:

1. Check current Claude Code version:
   ```bash
   claude --version
   ```

2. Search for recent Anthropic updates (web search):
   - "Anthropic Claude Code changelog"
   - "Anthropic blog new features" (last 2 weeks)
   - "Claude Code release notes"

3. Read `~/projects/_factory/PLATFORM_STATE.md` — tracks known features
   and last scan date. If it doesn't exist, create it.

4. Compare new findings against PLATFORM_STATE.md:
   - New CLI flags or commands?
   - New API features (models, tools, capabilities)?
   - New agent/team features?
   - Deprecated features that need migration?
   - Security updates that need attention?

5. For each genuinely new/useful feature not yet integrated:
   - Add a story to `~/projects/_factory/BACKLOG.md`:
     ```
     ### [FAC-xxx] Integrate {feature name}
     - status: ready
     - priority: {2-3 depending on impact}
     - effort: S
     - why: New Claude/Anthropic feature that could improve factory quality/speed
     - acceptance_criteria:
       1. Feature documented in docs/architecture.md or CLAUDE.md
       2. Factory commands/agents updated to use it where beneficial
       3. Config updated if new settings needed
     ```

6. Update `~/projects/_factory/PLATFORM_STATE.md`:
   ```markdown
   # Platform State
   Last scan: {date}
   Claude Code version: {version}

   ## Known Features (integrated)
   - Agent Teams (GA) — used in /build
   - Channels — used for Telegram communication
   - Auto Mode — documented in setup
   - ...

   ## Pending Integration
   - {new feature} — story [FAC-xxx] created
   ```

### Step 2: Build factory improvements

1. Read ~/projects/_factory/BACKLOG.md
2. Pick top priority "ready" story
3. Implement it using standard /build flow
4. NOTE: Changes to heartbeat require special care:
   - Test the new heartbeat code thoroughly
   - Run full test suite: `cd heartbeat && python3 -m pytest`
   - Send Telegram: "Heartbeat update ready. Restart needed."
   - The heartbeat watchdog will need manual restart for heartbeat changes.
5. Changes to .claude/ files (agents, commands) take effect on next session.
6. After implementing, check if there's time for another story (same logic
   as continuous mode — keep going if not rate-limited).

### Step 3: Report

Send summary to Telegram:
```
🔧 Self-improvement cycle complete

Platform scan:
• Claude Code version: {version}
• New features found: {N} ({list if any})
• Stories created: {M}

Implementation:
• ✅ [{FAC-xxx}] {title} — done
• 📋 {R} improvements remaining in backlog
```
