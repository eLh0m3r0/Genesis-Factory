---
description: "Show project velocity and burndown. Usage: /progress [project-name]"
argument-hint: "[project-name]"
---

# Project Progress & Velocity

Show how the factory is performing on a project (or all projects).

## Process

1. If project name given: show that project only.
   If no argument: show summary for all projects.

2. For each project, analyze BACKLOG.md and git history:
   - Stories completed this month (status: done)
   - Stories completed this week
   - Average cycle time (time from in_progress to done)
   - Completion rate: done / (done + stuck)
   - Current velocity: stories per week (rolling 4-week average)

3. Analyze git log for more context:
   ```bash
   git -C ~/projects/{name} log --since="30 days ago" --oneline | wc -l
   ```

4. List upcoming stories (ready, sorted by priority).

## Output Format

```
📊 Progress — {project-name}

This Month:
• Completed: 8 stories (5S, 2M, 1L)
• Stuck: 2 stories
• Completion rate: 80%
• Commits: 47

Velocity (rolling 4 weeks):
• Week 1: 3 stories
• Week 2: 2 stories
• Week 3: 4 stories
• Week 4: 2 stories (so far)
• Average: 2.8 stories/week

Cycle Time:
• S stories: ~2 hours avg
• M stories: ~6 hours avg
• L stories: ~14 hours avg

Upcoming (ready):
1. [PROJ-015] Add export feature (M, priority 1)
2. [PROJ-016] Improve search (S, priority 2)
3. [PROJ-017] Add email notifications (M, priority 2)
```
