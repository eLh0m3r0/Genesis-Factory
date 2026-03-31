---
description: "Run discovery cycle — research competitors and generate stories. Usage: /discover [project-name]"
argument-hint: "[project-name | all]"
---

# Discovery Cycle

## If project name provided:
Run discovery for that specific project.
If that project has `discovery` in `skip_phases` (VISION.md):
  Warn: "{project} has discovery in skip_phases. Run anyway? (Y/n)"

## If "all" or no argument:
Run discovery for all projects in ~/projects/ (excluding _factory).
Skip projects that have `discovery` in their VISION.md `skip_phases`.

## Process (per project)

1. Spawn research-analyst subagent:
   - Input: project's VISION.md
   - Output: updated RESEARCH.md
   - This agent uses web search to find competitive intelligence.

2. Spawn product-strategist subagent:
   - Input: VISION.md + RESEARCH.md + current codebase + AGENTS.md
   - Output: updated BACKLOG.md with new stories

3. Report to Telegram:
   "📋 Discovery complete for {project}:
    {N} new stories generated
    Top: [{ID}] {title} (priority {P}, effort {E})"

## Rules

- Don't regenerate stories that already exist (check BACKLOG.md).
- If RESEARCH.md is less than 7 days old, skip research-analyst (use cached).
- Subagents run on Sonnet to save tokens.
- Total discovery for one project should take 15-30 minutes.
