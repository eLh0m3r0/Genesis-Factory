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

1. **Pre-build validation** — before starting, verify:
   - Story has acceptance criteria (at least 2 testable criteria)
   - Story effort is realistic for one cycle (warn if L/XL)
   - Story is not blocked (`blocked_by` field is empty or all dependencies done)
   - Required env vars are available (if listed in design_notes)
   If validation fails: set story status to "blocked", log reason, pick next story.

2. **Read story** from BACKLOG.md. Update status to "in_progress".

3. **Architecture** — spawn architect subagent:
   - Reads story + codebase + CLAUDE.md + AGENTS.md
   - Writes design_notes into BACKLOG.md (all fields required)

4. **Implementation** — spawn Agent Team:
   - Create feature branch: `git checkout -b feature/{STORY-ID}-{slug}`
   - Lead agent: reads design_notes, coordinates teammates
   - Dev teammate (worktree): implements code following design_notes ONLY
     (do NOT share acceptance_criteria with Dev — holdout validation)
   - Test teammate (worktree): writes tests from design_notes test_plan
   - Lead: merges worktrees, runs full test suite

5. **Ralph Loop** — if tests fail:
   - Analyze failure, fix code, re-run tests
   - Max 5 iterations
   - If still failing: mark "stuck", record error in AGENTS.md, report to Telegram, STOP.

6. **Merge conflict check** — before pushing:
   ```bash
   git fetch origin main
   git merge-base --is-ancestor origin/main HEAD
   ```
   If behind main: `git merge origin/main` in the feature branch.
   If conflicts: use Claude to resolve them intelligently.
   If conflicts are too complex: report to Telegram, don't auto-resolve.

7. **Push + PR**:
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

11. **Auto-document** (after successful merge):
    - Spawn doc-writer subagent to update project docs
    - Only if the story changes user-facing functionality or API

12. **Cost estimate**:
    - Note approximate token usage for this cycle in story's `learnings` field
    - Format: "~{N}K tokens (architect: ~{X}K, dev: ~{Y}K, test: ~{Z}K)"
    - Append to `~/projects/_factory/cost_log.md`:
      `{date} | {project} | {story_id} | {effort} | ~{tokens}K`

13. **Mini-retrospective** (after every story, done or stuck):
    - What was the hardest part?
    - Did the architect's design match reality? What was wrong?
    - Any new patterns or anti-patterns discovered?
    - Write findings to the project's AGENTS.md immediately
    - If a systematic issue is found, create a story in ~/projects/_factory/BACKLOG.md

## Story State Transitions

```
ready → in_progress → pr_open → done
                              → stuck  (after 5 Ralph failures)
                              → rejected (human decision)
```

Never move stories backwards. A "done" story stays done.
