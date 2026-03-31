---
description: "Generate and send morning status report via Telegram."
---

# Morning Brief

Compile a concise status report across all factory operations.

## Gather Data

1. **GitHub** (for each project):
   ```bash
   gh pr list --repo {owner}/{repo} --state open --json number,title,mergeable
   gh pr list --repo {owner}/{repo} --state merged --json number,title,mergedAt --limit 5
   gh run list --repo {owner}/{repo} --limit 3 --json status,conclusion,name
   ```

2. **Backlogs**:
   - Count stories by status (ready, in_progress, done, stuck) per project
   - Identify what was completed in last 24h

3. **Heartbeat monitors** (if configured):
   - Read latest alerts from heartbeat log
   - Trading P&L if trading project exists

4. **Factory health**:
   - Docker: `docker compose ps`
   - Disk: `df -h /`
   - Uptime: `uptime`

5. **Cost tracking** (if `~/projects/_factory/cost_log.md` exists):
   - Sum tokens used in last 24h from cost_log.md
   - Estimate remaining budget for the month

## Format

Send via Telegram:

```
📊 Morning Brief — {date}

Projects:
• {project1}: {done_24h} shipped, {ready} in backlog, {stuck} stuck
• {project2}: {done_24h} shipped, {ready} in backlog{, skip: {phases} if any}

PRs:
• ✅ #{N} {title} — merged {time}
• 🔄 #{N} {title} — open, CI {status}

{if trading}
Trading:
• P&L 24h: {amount}
• Open positions: {count}
• Notable: {alerts}
{endif}

Factory:
• Uptime: {uptime}
• Disk: {used}/{total}
• Next nightly: 22:00
```
