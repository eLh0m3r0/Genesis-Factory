# Genesis Factory — Technical Context

## Stack
- Claude Code (agents, commands, hooks — markdown files)
- Python 3.12 (heartbeat daemon)
- Bash (scripts, tmux management)
- Docker Compose (infrastructure)
- YAML (configuration)

## Architecture
- .claude/agents/ — specialized AI agent definitions
- .claude/commands/ — slash command definitions
- .claude/hooks/ — automatic post-action triggers
- heartbeat/ — Python daemon (clock + sensors)
- scripts/ — start/stop shell scripts
- docker/ — Docker Compose for infrastructure
- templates/ — project templates

## Critical Rules
1. Heartbeat must have zero LLM dependencies (pure Python + HTTP)
2. All agent changes take effect on next Claude Code session restart
3. Heartbeat changes require manual restart (watchdog handles CC, not itself)
4. Never break the /setup command — it's the onboarding experience
5. Keep agents focused: one role per agent, clear boundaries
