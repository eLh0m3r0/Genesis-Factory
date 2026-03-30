#!/bin/bash
# Genesis Factory — Log Viewer
# Usage: ./scripts/logs.sh [heartbeat|docker|claude] [--tail N] [--grep PATTERN]

set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPONENT="${1:-heartbeat}"
shift 2>/dev/null || true

# Parse flags
TAIL_N=50
GREP_PATTERN=""

while [ $# -gt 0 ]; do
    case "$1" in
        --tail|-n)
            TAIL_N="$2"
            shift 2
            ;;
        --grep|-g)
            GREP_PATTERN="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [component] [options]"
            echo ""
            echo "Components:"
            echo "  heartbeat  (default) Heartbeat daemon log"
            echo "  docker     Docker compose service logs"
            echo "  claude     Claude Code tmux window output"
            echo ""
            echo "Options:"
            echo "  --tail N   Show last N lines (default: 50)"
            echo "  --grep P   Filter lines matching pattern P"
            echo "  --help     Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1 (try --help)"
            exit 1
            ;;
    esac
done

case "$COMPONENT" in
    heartbeat|hb)
        LOG_FILE="$FACTORY_DIR/heartbeat/heartbeat.log"
        if [ ! -f "$LOG_FILE" ]; then
            echo "No heartbeat log found at $LOG_FILE"
            exit 1
        fi
        if [ -n "$GREP_PATTERN" ]; then
            tail -n "$TAIL_N" "$LOG_FILE" | grep --color=auto -i "$GREP_PATTERN" || echo "(no matches)"
        else
            tail -n "$TAIL_N" "$LOG_FILE"
        fi
        ;;

    docker|dk)
        if [ -n "$GREP_PATTERN" ]; then
            docker compose -f "$FACTORY_DIR/docker/docker-compose.yml" logs --tail "$TAIL_N" 2>/dev/null | grep --color=auto -i "$GREP_PATTERN" || echo "(no matches)"
        else
            docker compose -f "$FACTORY_DIR/docker/docker-compose.yml" logs --tail "$TAIL_N" 2>/dev/null
        fi
        ;;

    claude|cl)
        if tmux has-session -t factory 2>/dev/null; then
            # Capture tmux pane content
            OUTPUT=$(tmux capture-pane -t factory:claude -p -S -"$TAIL_N" 2>/dev/null || echo "(could not capture claude window)")
            if [ -n "$GREP_PATTERN" ]; then
                echo "$OUTPUT" | grep --color=auto -i "$GREP_PATTERN" || echo "(no matches)"
            else
                echo "$OUTPUT"
            fi
        else
            echo "tmux session 'factory' not running"
            exit 1
        fi
        ;;

    *)
        echo "Unknown component: $COMPONENT"
        echo "Use: heartbeat, docker, or claude"
        exit 1
        ;;
esac
