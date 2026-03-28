---
description: "Build a story — design, implement, test, merge, deploy. Usage: /build [STORY-ID]"
argument-hint: "[STORY-ID]"
---

# Build Story

## Story Selection

If STORY-ID provided: build that specific story.
If no argument: pick the highest-priority "ready" story across all projects.
  - Score: priority × project_weight / effort_multiplier (S=1,M=2,L=4,XL=8)
  - Prefer stories in "ready" status.
  - Skip stories in "stuck" status.

## Process

1. **Read story** from BACKLOG.md. Update status to "in_progress".

2. **Architecture** — spawn architect subagent:
   - Reads story + codebase + CLAUDE.md
   - Writes design_notes into BACKLOG.md
   
3. **Implementation** — spawn Agent Team:
   - Create feature branch: `git checkout -b feature/{STORY-ID}-{slug}`
   - Lead agent: reads design_notes, coordinates teammates
   - Dev teammate (worktree): implements code following design
   - Test teammate (worktree): writes tests in parallel
   - Lead: merges worktrees, runs full test suite
   
4. **Ralph Loop** — if tests fail:
   - Analyze failure, fix code, re-run tests
   - Max 5 iterations
   - If still failing: mark "stuck", record error in AGENTS.md, report to Telegram, STOP.

5. **Push + PR**:
   ```bash
   git push -u origin feature/{STORY-ID}-{slug}
   gh pr create --title "[{STORY-ID}] {title}" --body "{story description + acceptance criteria}"
   ```

6. **Wait for CI** — monitor GitHub Actions:
   ```bash
   gh run watch   # wait for CI to complete
   ```

7. **Verification** (after CI passes):
   - Spawn uat-tester subagent (Playwright on staging URL if configured)
   - Spawn security-reviewer subagent (scan diff)
   - Both post results as PR comments

8. **Auto-merge** (if ALL green):
   ```bash
   gh pr merge --auto --squash
   ```

9. **Post-deploy** (after merge triggers deploy):
   - Wait for deploy workflow to complete
   - Run smoke test against production URL if configured
   - If smoke fails: alert Telegram IMMEDIATELY

10. **Wrap up**:
    - Update story status to "done" in BACKLOG.md
    - Record learnings in story's `learnings` field
    - Report to Telegram: "✅ [{STORY-ID}] {title} — merged and deployed"
