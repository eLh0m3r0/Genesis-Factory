#!/bin/bash
echo "🛑 Stopping Genesis Factory..."
tmux kill-session -t factory 2>/dev/null && echo "  tmux session killed" || echo "  tmux not running"
cd "$(dirname "$0")/../docker" && docker compose down && echo "  Docker stopped"
pkill -x caffeinate 2>/dev/null && echo "  caffeinate stopped" || true
echo "✅ Factory stopped."
