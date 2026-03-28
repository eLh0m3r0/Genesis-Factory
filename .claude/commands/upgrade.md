---
description: "Self-improvement cycle — factory upgrades itself."
---

# Factory Self-Improvement

Work on the factory's own backlog (~/projects/_factory/).

1. Read ~/projects/_factory/BACKLOG.md
2. Pick top priority "ready" story  
3. Implement it using standard /build flow
4. NOTE: Changes to heartbeat require special care:
   - Test the new heartbeat code thoroughly
   - Send Telegram message: "Heartbeat update ready. Restart needed."
   - The heartbeat watchdog will need manual restart for heartbeat changes.
5. Changes to .claude/ files (agents, commands) take effect on next session.

Examples of factory improvements:
- Better scoring algorithm for story prioritization
- New heartbeat monitor type
- Improved UAT agent selectors strategy  
- Cost tracking dashboard
- Better morning brief format
- New agent specialization
