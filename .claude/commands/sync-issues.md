---
description: "Sync GitHub Issues with BACKLOG.md. Usage: /sync-issues <project-name>"
argument-hint: "<project-name>"
---

# GitHub Issues Sync

Bidirectional sync between GitHub Issues and BACKLOG.md.

## Process

### 1. Import: GitHub Issues → BACKLOG.md

```bash
gh issue list --repo {owner}/{repo} --state open --json number,title,body,labels --limit 50
```

For each open issue NOT already in BACKLOG.md:
- Create a new story: `[PROJ-{NNN}] {issue title}`
- Map labels to priority: `bug` = priority 1, `enhancement` = priority 2, `feature` = priority 3
- Map labels to effort: `small` = S, `medium` = M, `large` = L
- Extract acceptance criteria from issue body (look for checklist items)
- Add `github_issue: #{number}` field to story
- Status: "ready"

### 2. Export: Completed stories → Close issues

For each story with status "done" that has a `github_issue` field:
```bash
gh issue close {number} --repo {owner}/{repo} --comment "Completed in PR #{pr_number}"
```

### 3. Report

```
🔄 Issues sync for {project}:
  Imported: {N} new stories from GitHub Issues
  Closed: {M} issues (completed stories)
  Skipped: {K} issues already in backlog
```

## Rules

- Never create duplicate stories (match by issue number OR title)
- Don't import issues with label "wontfix" or "duplicate"
- Preserve manually-added acceptance criteria in BACKLOG.md
- If issue has no body, create minimal acceptance criteria from title
