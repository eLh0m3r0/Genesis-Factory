---
description: "Show top stories across all projects. Quick backlog overview."
---

# Backlog Overview

Show the top-priority stories across all managed projects.

## Process

1. Scan ~/projects/ for all directories containing BACKLOG.md.
2. Parse stories with status "ready" or "in_progress".
3. Read each project's VISION.md for `project_weight` (default 1).
4. Score each story: `priority * project_weight / effort_multiplier`
   - Effort multiplier: S=1, M=2, L=4, XL=8
5. Check `blocked_by` field — mark blocked stories with 🔒.
6. Sort by score (highest first), blocked stories at the bottom.
7. Display top 10 stories.

## Output Format

```
📋 Top Stories Across All Projects

1. [PROJ-001] Add user dashboard (project-alpha)
   Priority: 1 | Effort: M | Status: ready | Score: 2.5

2. [FACT-002] Add cost tracking (factory)
   Priority: 1 | Effort: S | Status: in_progress | Score: 5.0

3. [PROJ-003] Improve onboarding (project-alpha)
   Priority: 2 | Effort: S | Status: ready | Score: 2.0

...

Total: {N} ready, {M} in progress across {P} projects.
```

If no stories are in "ready" or "in_progress" status:
"No actionable stories. Run /discover to generate new ones."
