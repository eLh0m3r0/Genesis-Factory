# Genesis Factory Benchmark Suite

Reproducible benchmarks measuring factory performance.

## Metrics

| Metric | What it measures |
|--------|-----------------|
| Time to first story | Discovery → first "ready" story in BACKLOG.md |
| Time to first merge | Build cycle → first PR merged |
| Stories per week | Throughput (rolling 4-week average) |
| Cost per story | Approximate tokens per story (by effort size) |
| Stuck rate | stuck / (done + stuck) as percentage |
| Completion rate | done / total as percentage |

## Running

```bash
./benchmarks/run.sh [--project PROJECT] [--weeks N]
```

### Options

- `--project PROJECT` — benchmark a specific project (default: all)
- `--weeks N` — look back N weeks (default: 4)
- `--output json` — output as JSON instead of text

## Sample Output

```
📊 Genesis Factory Benchmark — 2026-03-30

Period: last 4 weeks (2026-03-02 to 2026-03-30)

Throughput:
  Stories completed: 14
  Stories stuck: 3
  Completion rate: 82%
  Velocity: 3.5 stories/week

Cycle Time (median):
  S stories: 1.5 hours
  M stories: 5.2 hours
  L stories: 12.8 hours

Cost (approximate):
  S stories: ~45K tokens avg
  M stories: ~130K tokens avg
  L stories: ~380K tokens avg
  Total this period: ~1.8M tokens

Reliability:
  Watchdog restarts: 3
  Heartbeat uptime: 99.7%
  Silent failures: 0
```

## Comparing Versions

Run benchmarks before and after factory upgrades to measure improvement:

```bash
# Before upgrade
./benchmarks/run.sh --output json > benchmarks/results/before-v0.6.json

# After upgrade
./benchmarks/run.sh --output json > benchmarks/results/after-v0.6.json

# Compare
diff benchmarks/results/before-v0.6.json benchmarks/results/after-v0.6.json
```
