---
description: "Comprehensive factory health dashboard. More detailed than /status."
---

# Factory Health Dashboard

Deep health check across all factory systems. Report to Telegram.

## Gather Data

### 1. System Health
```bash
uptime
df -h /
docker compose -f ~/genesis-factory/docker/docker-compose.yml ps 2>/dev/null
```

### 2. Factory Processes
```bash
tmux list-windows -t factory 2>/dev/null    # claude, heartbeat, docker windows
pgrep -f factory_heartbeat                  # heartbeat PID
```

### 3. Heartbeat Status
```bash
tail -20 ~/genesis-factory/heartbeat/heartbeat.log   # recent activity
grep -c "ERROR" ~/genesis-factory/heartbeat/heartbeat.log  # error count
```

Check `heartbeat/alert_state.json` for currently-down services.

### 4. Per-Project Status
For each project in `~/projects/*/VISION.md`:
- Story counts from BACKLOG.md: ready / in_progress / done / stuck
- Last commit: `git -C ~/projects/{name} log -1 --format="%h %s (%ar)"`
- Open PRs: `gh pr list --repo {owner}/{repo} --state open --json number,title`
- Monitor status from heartbeat_config.yaml (if configured)

### 5. Schedule
- Current time
- Next scheduled trigger (nightly 22:00, morning 07:00, etc.)
- Is factory paused? Check `~/projects/.factory_paused`

## Output Format

Send via Telegram (split into 2 messages if too long):

```
🏭 Factory Health — {datetime}

System:
• Uptime: {uptime}
• Disk: {used}/{total} ({free} free)
• Docker: {running}/{total} services up

Processes:
• Claude Code: {running/stopped}
• Heartbeat: {running/stopped} (PID {pid})
• Paused: {yes/no}

Projects:
• {project1}: {ready}R {progress}P {done}D {stuck}S — last: {commit_msg} ({age})
• {project2}: ...

Monitors:
• {count} active, {down_count} currently alerting
{if any down}
  🔴 {monitor_key}: down since {time}
{endif}

Schedule:
• Next trigger: {next_event} at {time}
• Nightly: 22:00 Mon-Fri
• Discovery: 02:00 Sunday
```
