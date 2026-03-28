---
description: "First-time factory setup. Guides you through prerequisites, configuration, and first project creation."
---

# Factory Setup

You are guiding a new user through Genesis Factory setup. Be friendly, clear,
and handle errors gracefully. Ask questions one at a time.

## Step 1: Check Prerequisites

Run these checks and report status:

```bash
node --version        # Need 20+
python3 --version     # Need 3.10+
git --version         # Any recent
docker --version      # Docker Desktop
tmux -V               # tmux
claude --version      # Claude Code 2.1.80+
bun --version         # Bun runtime for plugins
```

If anything is missing, provide the exact brew/npm install command.
Wait for user to install before proceeding.

## Step 2: Claude Code Configuration

Check and enable required features:

```bash
# Check if Agent Teams is enabled
cat ~/.claude/settings.json 2>/dev/null | grep AGENT_TEAMS
```

If not enabled, add it:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_CODE_SUBAGENT_MODEL": "claude-sonnet-4-6"
  }
}
```

## Step 3: Telegram Bot

Ask: "Do you have a Telegram bot token? If not, I'll guide you through creating one."

If no:
1. Tell them to open @BotFather in Telegram
2. Send /newbot
3. Choose a name (e.g., "My Genesis Factory")
4. Choose a username (e.g., "my_genesis_factory_bot")
5. Copy the token

Ask them to paste the token. Save it.

Then set up Channels:
```
/plugin marketplace add anthropics/claude-plugins-official
/plugin install telegram@claude-plugins-official
/telegram:configure
```

Test by asking them to send a message to the bot from their phone.

## Step 4: GitHub

Ask: "Paste your GitHub personal access token (needs 'repo' scope)."

If they don't have one, guide them:
1. Go to github.com → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select 'repo' scope
4. Copy and paste

Save as GITHUB_TOKEN in ~/.zshrc.

Test: `gh auth status`

## Step 5: Docker Services

Start the Docker stack from the genesis-factory repo:

```bash
cd /path/to/genesis-factory/docker
docker compose up -d
docker compose ps   # verify all running
```

## Step 6: macOS Configuration

Guide them through:
1. System Settings → Energy Saver → Prevent sleep when display is off
2. Or run: `caffeinate -s &` (keeps machine awake with lid closed)
3. Recommend: `pmset -g` to verify settings

## Step 7: Create Projects Directory

```bash
mkdir -p ~/projects
```

## Step 8: First Project

Ask: "What's your first project? Give me a name and a one-sentence description."

Create project from template:
```bash
mkdir -p ~/projects/{name}
```

Copy templates (VISION.template.md, CLAUDE.template.md, BACKLOG.template.md)
and fill in the project name. Guide the user to edit VISION.md with their
project's actual direction.

## Step 9: Factory Self-Project

Create ~/projects/_factory/ with:
- VISION.md describing the factory's self-improvement goals
- CLAUDE.md with factory-specific technical context
- BACKLOG.md with initial improvement ideas

## Step 10: Heartbeat

```bash
cd /path/to/genesis-factory/heartbeat
pip3 install -r requirements.txt
cp config.example.yaml config.yaml
```

Guide them to edit config.yaml with their Telegram bot token and chat ID.

## Step 11: Playwright MCP (Browser Testing)

Install Playwright browsers on the machine:

```bash
npx playwright install chromium
```

Then add Playwright MCP server to Claude Code:

```bash
claude mcp add playwright -- npx @executeautomation/playwright-mcp-server
```

Test: ask Claude to "open https://example.com and take a screenshot."
If it works, Playwright is ready for UAT testing.

## Step 12: Ralph Plugin (Iterative Loops)

Install the Ralph Wiggum plugin for autonomous iteration:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin install ralph-wiggum@claude-plugins-official
```

Test: `/ralph-loop --help` should show usage.
Ralph enables Claude to keep working on a story until tests pass,
automatically retrying and fixing issues.

## Step 13: Start the Factory

Use the included startup script:

```bash
cd /path/to/genesis-factory
./scripts/start.sh
```

This creates a tmux session with 3 windows: claude, heartbeat, docker.

For auto-start on login, install the LaunchAgent:

```bash
cp scripts/com.genesis.factory.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.genesis.factory.plist
```

## Step 14: Verify

1. Send a test message via Telegram → should get response
2. Run `/status` → should show the new project
3. Run `/discover {project}` → should generate RESEARCH.md and BACKLOG.md

Tell the user: "Factory is running! Your first discovery cycle will generate
stories for {project}. Tomorrow morning you'll get a brief on Telegram.
Type /nightly to trigger a development cycle manually, or wait until 22:00."
