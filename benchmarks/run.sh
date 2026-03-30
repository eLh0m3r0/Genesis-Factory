#!/bin/bash
# Genesis Factory Benchmark — Collect and report performance metrics
set -euo pipefail

PROJECTS_DIR="${PROJECTS_DIR:-$HOME/projects}"
WEEKS="${2:-4}"
OUTPUT="text"

# Parse args
while [ $# -gt 0 ]; do
    case "$1" in
        --project) PROJECT="$2"; shift 2 ;;
        --weeks) WEEKS="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

SINCE_DATE=$(date -v-"${WEEKS}w" "+%Y-%m-%d" 2>/dev/null || date -d "${WEEKS} weeks ago" "+%Y-%m-%d")
TODAY=$(date "+%Y-%m-%d")

echo "📊 Genesis Factory Benchmark — $TODAY"
echo ""
echo "Period: last $WEEKS weeks ($SINCE_DATE to $TODAY)"
echo ""

# Count stories by status across all projects
TOTAL_DONE=0
TOTAL_STUCK=0
TOTAL_READY=0
TOTAL_PROGRESS=0

for backlog in "$PROJECTS_DIR"/*/BACKLOG.md; do
    [ -f "$backlog" ] || continue
    project=$(basename "$(dirname "$backlog")")

    if [ -n "${PROJECT:-}" ] && [ "$project" != "$PROJECT" ]; then
        continue
    fi

    done_count=$(grep -c "status.*done" "$backlog" 2>/dev/null || echo 0)
    stuck_count=$(grep -c "status.*stuck" "$backlog" 2>/dev/null || echo 0)
    ready_count=$(grep -c "status.*ready" "$backlog" 2>/dev/null || echo 0)
    progress_count=$(grep -c "status.*in_progress" "$backlog" 2>/dev/null || echo 0)

    TOTAL_DONE=$((TOTAL_DONE + done_count))
    TOTAL_STUCK=$((TOTAL_STUCK + stuck_count))
    TOTAL_READY=$((TOTAL_READY + ready_count))
    TOTAL_PROGRESS=$((TOTAL_PROGRESS + progress_count))

    echo "  $project: ${done_count}D ${stuck_count}S ${ready_count}R ${progress_count}P"
done

echo ""
echo "Throughput:"
echo "  Stories completed: $TOTAL_DONE"
echo "  Stories stuck: $TOTAL_STUCK"
TOTAL=$((TOTAL_DONE + TOTAL_STUCK))
if [ "$TOTAL" -gt 0 ]; then
    RATE=$((TOTAL_DONE * 100 / TOTAL))
    echo "  Completion rate: ${RATE}%"
fi
if [ "$WEEKS" -gt 0 ]; then
    VEL=$(echo "scale=1; $TOTAL_DONE / $WEEKS" | bc 2>/dev/null || echo "N/A")
    echo "  Velocity: $VEL stories/week"
fi

echo ""
echo "Backlog:"
echo "  Ready: $TOTAL_READY"
echo "  In progress: $TOTAL_PROGRESS"

# Git activity
echo ""
echo "Git activity (last $WEEKS weeks):"
for project_dir in "$PROJECTS_DIR"/*/; do
    [ -d "$project_dir/.git" ] || continue
    project=$(basename "$project_dir")
    if [ -n "${PROJECT:-}" ] && [ "$project" != "$PROJECT" ]; then
        continue
    fi
    commits=$(git -C "$project_dir" log --since="$SINCE_DATE" --oneline 2>/dev/null | wc -l | tr -d ' ')
    prs=$(git -C "$project_dir" log --since="$SINCE_DATE" --oneline --grep="Merge pull request" 2>/dev/null | wc -l | tr -d ' ')
    echo "  $project: $commits commits, $prs PRs merged"
done

# Cost log
COST_LOG="$PROJECTS_DIR/_factory/cost_log.md"
if [ -f "$COST_LOG" ]; then
    echo ""
    echo "Cost tracking:"
    entries=$(wc -l < "$COST_LOG" | tr -d ' ')
    echo "  $entries entries in cost_log.md"
fi

echo ""
echo "Done."
