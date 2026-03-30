#!/bin/bash
# Genesis Factory — Config & Prerequisites Validator
# Run this to check if everything is set up correctly.

set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  ✅ $name"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name"
        FAIL=$((FAIL + 1))
    fi
}

warn() {
    local name="$1"
    echo "  ⚠️  $name"
    WARN=$((WARN + 1))
}

echo "🔍 Genesis Factory Validation"
echo ""

# --- Prerequisites ---
echo "Prerequisites:"
check "Python 3" python3 --version
check "Docker" docker --version
check "tmux" tmux -V
check "git" git --version

if command -v claude > /dev/null 2>&1; then
    CLAUDE_VER=$(claude --version 2>/dev/null || echo "0.0.0")
    echo "  ✅ Claude Code ($CLAUDE_VER)"
    PASS=$((PASS + 1))
else
    echo "  ❌ Claude Code (not installed: npm install -g @anthropic-ai/claude-code)"
    FAIL=$((FAIL + 1))
fi

if command -v bun > /dev/null 2>&1; then
    echo "  ✅ Bun ($(bun --version 2>/dev/null))"
    PASS=$((PASS + 1))
else
    warn "Bun not installed (optional, for plugins: brew install bun)"
fi

if command -v gh > /dev/null 2>&1; then
    check "GitHub CLI authenticated" gh auth status
else
    echo "  ❌ GitHub CLI (not installed: brew install gh)"
    FAIL=$((FAIL + 1))
fi

echo ""

# --- Docker ---
echo "Docker:"
if docker info > /dev/null 2>&1; then
    echo "  ✅ Docker Desktop running"
    PASS=$((PASS + 1))
    if [ -f "$FACTORY_DIR/docker/docker-compose.yml" ]; then
        if docker compose -f "$FACTORY_DIR/docker/docker-compose.yml" ps --quiet 2>/dev/null | grep -q .; then
            echo "  ✅ Docker services running"
            PASS=$((PASS + 1))
        else
            warn "Docker services not running (run: cd docker && docker compose up -d)"
        fi
    fi
else
    echo "  ❌ Docker Desktop not running"
    FAIL=$((FAIL + 1))
fi

echo ""

# --- Heartbeat ---
echo "Heartbeat:"
if [ -f "$FACTORY_DIR/heartbeat/config.yaml" ]; then
    echo "  ✅ config.yaml exists"
    PASS=$((PASS + 1))

    # Validate YAML syntax
    if python3 -c "import yaml; yaml.safe_load(open('$FACTORY_DIR/heartbeat/config.yaml'))" 2>/dev/null; then
        echo "  ✅ config.yaml valid YAML"
        PASS=$((PASS + 1))
    else
        echo "  ❌ config.yaml has YAML syntax errors"
        FAIL=$((FAIL + 1))
    fi

    # Check for real bot token (not the placeholder)
    if grep -q "YOUR_TELEGRAM" "$FACTORY_DIR/heartbeat/config.yaml" 2>/dev/null; then
        echo "  ❌ Telegram bot_token not configured (still placeholder)"
        FAIL=$((FAIL + 1))
    else
        echo "  ✅ Telegram bot_token configured"
        PASS=$((PASS + 1))
    fi
else
    echo "  ❌ config.yaml not found (cp config.example.yaml config.yaml)"
    FAIL=$((FAIL + 1))
fi

# Check Python dependencies
if python3 -c "import schedule, requests, yaml" 2>/dev/null; then
    echo "  ✅ Python dependencies installed"
    PASS=$((PASS + 1))
else
    echo "  ❌ Python dependencies missing (pip3 install -r heartbeat/requirements.txt)"
    FAIL=$((FAIL + 1))
fi

echo ""

# --- Projects ---
echo "Projects:"
PROJECTS_DIR="$HOME/projects"
if [ -d "$PROJECTS_DIR" ]; then
    echo "  ✅ ~/projects/ directory exists"
    PASS=$((PASS + 1))

    PROJECT_COUNT=$(find "$PROJECTS_DIR" -maxdepth 2 -name "VISION.md" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$PROJECT_COUNT" -gt 0 ]; then
        echo "  ✅ $PROJECT_COUNT project(s) found"
        PASS=$((PASS + 1))

        # Check each project
        for vision in "$PROJECTS_DIR"/*/VISION.md; do
            project_dir=$(dirname "$vision")
            project_name=$(basename "$project_dir")
            if [ -f "$project_dir/CLAUDE.md" ]; then
                echo "    ✅ $project_name (VISION.md + CLAUDE.md)"
            else
                warn "$project_name missing CLAUDE.md"
            fi
        done
    else
        warn "No projects found (run /new-project to create one)"
    fi
else
    warn "~/projects/ directory not found (mkdir -p ~/projects)"
fi

echo ""

# --- tmux session ---
echo "Runtime:"
if tmux has-session -t factory 2>/dev/null; then
    echo "  ✅ tmux session 'factory' exists"
    PASS=$((PASS + 1))
    WINDOWS=$(tmux list-windows -t factory 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✅ $WINDOWS window(s) in factory session"
else
    warn "tmux session 'factory' not running (run: ./scripts/start.sh)"
fi

# --- Disk space ---
FREE_GB=$(df -g / 2>/dev/null | awk 'NR==2{print $4}' || echo "0")
if [ "$FREE_GB" -gt 10 ] 2>/dev/null; then
    echo "  ✅ Disk space: ${FREE_GB} GB free"
    PASS=$((PASS + 1))
elif [ "$FREE_GB" -gt 5 ] 2>/dev/null; then
    warn "Disk space low: ${FREE_GB} GB free"
else
    echo "  ❌ Disk space critical: ${FREE_GB} GB free"
    FAIL=$((FAIL + 1))
fi

# --- Summary ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ $PASS passed"
[ "$WARN" -gt 0 ] && echo "  ⚠️  $WARN warnings"
[ "$FAIL" -gt 0 ] && echo "  ❌ $FAIL failed"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo "  Factory is ready! 🏭"
    exit 0
else
    echo "  Fix the issues above before starting."
    exit 1
fi
