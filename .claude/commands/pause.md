---
description: "Pause all automated factory cycles. Heartbeat keeps running but won't send triggers."
---

# Pause Factory

Create the pause flag file:

```bash
touch ~/projects/.factory_paused
```

Confirm to Telegram: "⏸️ Factory paused. No automated cycles will run. Send /resume to restart."

The heartbeat daemon checks for this file before each trigger.
It stays running (watchdog, monitors still work) but skips all
scheduled triggers (nightly, discovery, morning brief, etc.).

Market monitors and health checks continue to run even when paused.
