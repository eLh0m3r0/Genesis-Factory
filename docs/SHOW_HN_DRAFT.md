# Show HN Draft — Genesis Factory

> For founder review before posting. Target: Show HN on Hacker News.
> Suggested title + body below.

---

## Title

**Show HN: Genesis Factory – autonomous dev team running 24/7 on a $100/month Mac**

---

## Body

I built a system that runs on a spare MacBook, connects to Claude Code via Telegram, and autonomously ships software while I sleep.

It's three things glued together:

1. **Claude Code with Channels** – the brain. Claude Opus 4.6 on a Max subscription. It researches what to build, writes code, runs tests in a real browser, reviews for security, and merges to main. Controlled entirely via Telegram from my phone.

2. **A heartbeat daemon** – 840 lines of Python, zero LLM calls. It's just a clock and a sensor array: sends "it's 22:00, build time" to Claude via Telegram, monitors uptime, watches disk, and restarts Claude Code if the session dies.

3. **Docker** – PostgreSQL, staging containers, Playwright for browser UAT.

The workflow:

```
You: write VISION.md ("Build a Czech attendance SaaS for SMBs")
     Walk away.

Factory: researches competitors → generates scored stories
         → implements → runs pytest + Playwright → security review
         → auto-merges when CI green → deploys → Telegram summary

You (next morning): "✅ 2 stories shipped. 1 stuck. Here's why..."
```

Total cost: ~$103/month (Claude Max subscription + electricity). No cloud orchestration, no new infra, no agents-as-a-service. The intelligence lives entirely in Claude Code – the heartbeat is just a cron job that knows how to send Telegram messages.

What surprised me: the "model decides, not code" constraint forced good architecture. The heartbeat sends triggers, Claude decides what to do. No hardcoded business logic in the orchestration layer. And since the factory manages itself as a project (`~/projects/_factory/`), it's been improving its own agents and workflows.

It's been running for a few weeks managing three projects simultaneously. Current velocity: 2-3 stories per day on a single Mac mini.

**What it's not:** this isn't a product or a hosted service. It's an open-source pattern for running Claude Code as an autonomous factory on hardware you own. The setup takes about 15 minutes.

GitHub: https://github.com/eLh0m3r0/Genesis-Factory

Happy to discuss the architecture, especially the Telegram-as-control-plane pattern and the Auto Mode safety classifier config.

---

## Notes for founder review

- Adjust "a few weeks" / "three projects" to match reality
- You may want to add a specific project result ("shipped X features to [real project]") as social proof
- The Show HN body can be up to ~600 words; this is ~320 — room to add one concrete story if you have one
- Suggested posting time: Tuesday or Wednesday, 9–11am ET (peak HN traffic)
- Tag to watch: the post goes to /newest first; upvoting within the first 30 min matters most for front page
