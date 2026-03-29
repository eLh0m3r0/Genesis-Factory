# Contributing to Genesis Factory

## Getting Started

1. Fork and clone the repo
2. Run `/setup` in Claude Code for guided onboarding
3. Or manually: install prerequisites, copy `heartbeat/config.example.yaml` to `config.yaml`

## Running Tests

```bash
cd heartbeat
pip install -r requirements.txt
pip install pytest
pytest test_heartbeat.py -v
```

## Project Structure

- `.claude/agents/` — AI agent definitions (one role per file)
- `.claude/commands/` — Slash commands (one command per file)
- `.claude/hooks/` — Post-tool-use hooks for auto-fix patterns
- `heartbeat/` — Heartbeat daemon (Python, zero LLM calls)
- `docker/` — Shared infrastructure (PostgreSQL)
- `scripts/` — Start/stop scripts, LaunchAgent plist
- `templates/` — Project templates for `/new-project`
- `docs/` — Architecture, FAQ, examples

## Making Changes

### Agents & Commands
- Edit the markdown file directly
- Changes take effect on next Claude Code session
- Keep agents focused: one role per agent

### Heartbeat
- Edit `heartbeat/factory_heartbeat.py`
- Run tests: `pytest test_heartbeat.py -v`
- Heartbeat changes require manual restart of the daemon

### Adding a New Command
1. Create `.claude/commands/your-command.md` with YAML frontmatter
2. Add to SPEC-v2.md Section 7 table
3. Add to README.md commands table if user-facing

### Adding a New Monitor Type
1. Add handler in `run_single_monitor()` in `factory_heartbeat.py`
2. Add tests in `test_heartbeat.py`
3. Add example in `docs/examples/`
4. Document in SPEC-v2.md Section 8

## Code Style

- Python: follow existing patterns, no external linters enforced
- Markdown: use ATX headers (`#`), fenced code blocks
- Keep heartbeat minimal — every line should earn its place

## License

MIT. By contributing, you agree your contributions are licensed under MIT.
