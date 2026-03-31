---
description: "Multi-project overview with health indicators."
---

# Projects Overview

Show all managed projects with status and health.

## Process

1. Scan `~/projects/` for directories containing VISION.md.
2. For each project, gather:
   - Name and title from VISION.md
   - `project_weight` from VISION.md (default: 1)
   - `skip_phases` from VISION.md (default: [])
   - Story counts from BACKLOG.md: ready / in_progress / done / stuck
   - Last commit: `git log -1 --format="%ar"` (age)
   - Health indicator based on:
     - 🟢 Green: has ready stories, no stuck, recent activity
     - 🟡 Yellow: no ready stories OR stuck stories exist OR no activity >3 days
     - 🔴 Red: all stories stuck OR no BACKLOG.md OR no recent activity >7 days

3. Sort by weight (highest first), then by name.

## Output Format

```
📋 Projects Overview

🟢 project-alpha (weight: 5)
   4 ready, 1 in progress, 12 done, 0 stuck
   Last: "Add user dashboard" (2 hours ago)

🟡 side-project (weight: 2, skip: uat, auto_deploy)
   0 ready, 0 in progress, 3 done, 1 stuck
   Last: "Fix login page" (3 days ago)

🔴 experiment (weight: 1)
   0 ready, 0 in progress, 0 done, 2 stuck
   Last: "Initial commit" (2 weeks ago)

Summary: 3 projects, weight total: 8
         4 ready, 1 in progress, 15 done, 3 stuck
```

If no projects found:
"No projects found. Run /new-project to create one."
