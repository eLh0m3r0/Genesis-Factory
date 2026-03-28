#!/bin/bash
echo "🛑 Stopping Genesis Factory..."
tmux kill-session -t factory 2>/dev/null && echo "  tmux killed" || echo "  tmux not running"
cd "$(dirname "$0")/../docker" && docker compose down && echo "  Docker stopped"
echo "✅ Factory stopped."
