# Costs & Scaling Guide

## Monthly costs breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Claude Max subscription | $100/mo | Includes Opus + Sonnet + Claude Code |
| macOS compute | $0 | Runs on your existing Mac |
| Docker (PostgreSQL) | $0 | Local containers |
| GitHub | $0 | Free for public repos, private included in Pro |
| Telegram | $0 | Bot API is free |
| **Total** | **~$103/mo** | With GitHub Pro ($4/mo) for private repos |

## Token budget

Claude Max provides approximately 5M tokens/month (varies by plan tier).

### Token usage by task

| Task | Approx tokens | Frequency |
|------|--------------|-----------|
| S story (build cycle) | 30-80K | Per story |
| M story (build cycle) | 100-250K | Per story |
| L story (build cycle) | 300-600K | Per story |
| Discovery cycle | 50-100K | Weekly |
| Morning brief | 10-20K | Daily |
| Retrospective | 20-40K | Weekly |
| Self-improvement | 50-150K | Weekly |

### Estimated monthly usage

| Projects | Stories/week | Monthly tokens | Fits in Max? |
|----------|-------------|----------------|-------------|
| 1 | 3-5 S/M | ~800K-1.5M | Comfortable |
| 2 | 5-8 S/M | ~1.5M-2.5M | Comfortable |
| 3 | 7-12 S/M | ~2M-3.5M | Tight |
| 5+ | 12-20 S/M | ~3.5M-5M+ | May hit limits |

### Saving tokens

- Use `Sonnet` for subagents (architect, research, UAT, security, devops)
- Use `/effort medium` for routine tasks
- Prefer S/M stories over L/XL (L stories use 4-8x more tokens)
- Break L/XL stories into smaller pieces
- Avoid deep research cycles when RESEARCH.md is fresh (<7 days old)

## Hardware requirements

### Minimum

- Apple Silicon Mac (M1/M2/M3) or Intel Mac
- 16 GB RAM
- 50 GB free disk space
- Stable internet connection (for GitHub, Telegram, Anthropic API)

### Recommended

- Apple Silicon Mac with 16+ GB RAM
- 100+ GB free disk space
- Wired ethernet (more stable than WiFi for 24/7 operation)
- UPS or similar power protection (prevents data loss on power outage)

### macOS settings for 24/7 operation

```bash
# Prevent sleep when display off
sudo pmset -a disablesleep 1

# Or use caffeinate (already in start.sh)
caffeinate -s &

# Check current power settings
pmset -g
```

## Scaling by project count

### 1-2 projects (sweet spot)

- Token budget is comfortable
- Nightly cycles complete one story each
- Discovery and retro have enough time
- Heartbeat monitors are fast

### 3-4 projects

- Token budget gets tighter — prefer S stories
- Some nights may not finish a story due to rate limits
- Consider increasing `project_weight` for priority projects
- Discovery may need to skip weeks for lower-priority projects

### 5+ projects

- Likely to hit token limits regularly
- Use project weights aggressively (weight 0 = paused)
- Consider running only 2-3 active projects + paused ones
- Monitor costs with morning brief tracking
- May need to upgrade Claude plan or add a second machine

## Cost optimization tips

1. **Right-size stories**: S stories have the best cost/value ratio
2. **Use project weights**: Focus tokens on high-priority projects
3. **Pause idle projects**: Set weight to 0 instead of keeping active
4. **Cache research**: Discovery skips research if RESEARCH.md is <7 days old
5. **Effort levels**: Use `/effort medium` by default, `/effort high` only for complex implementation
6. **Subagent model**: All subagents use Sonnet (set via `CLAUDE_CODE_SUBAGENT_MODEL`)
