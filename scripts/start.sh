#!/bin/bash
set -e

FACTORY_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🏭 Starting Genesis Factory..."

# Ensure caffeinate is running (prevents sleep with lid closed)
if ! pgrep -x caffeinate > /dev/null 2>&1; then
    echo "  Starting caffeinate (prevents sleep)..."
    nohup caffeinate -s > /dev/null 2>&1 &
fi

# Start Docker services
echo "  Starting Docker services..."
cd "$FACTORY_DIR/docker"
docker compose up -d --wait 2>/dev/null || docker compose up -d

# Wait for PostgreSQL to be ready (max 30 seconds)
echo "  Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if docker compose exec -T postgres pg_isready -q 2>/dev/null; then
        echo "  PostgreSQL ready (${i}s)"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "  ⚠️  PostgreSQL not ready after 30s (continuing anyway)"
    fi
    sleep 1
done

# Create tmux session
if tmux has-session -t factory 2>/dev/null; then
    echo "  Factory session exists. Killing..."
    tmux kill-session -t factory
fi

echo "  Creating tmux session..."
tmux new-session -d -s factory -n claude
tmux send-keys -t factory:claude "cd ~/projects && claude --channels" Enter

tmux new-window -t factory -n heartbeat
tmux send-keys -t factory:heartbeat "cd $FACTORY_DIR/heartbeat && python3 factory_heartbeat.py" Enter

tmux new-window -t factory -n docker
tmux send-keys -t factory:docker "cd $FACTORY_DIR/docker && docker compose logs -f" Enter

echo ""
echo "✅ Genesis Factory started!"
echo "   Windows: claude | heartbeat | docker"
echo "   Attach:  tmux attach -t factory"
