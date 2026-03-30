---
description: "Reset a stuck story and retry. Usage: /retry <STORY-ID>"
argument-hint: "<STORY-ID>"
---

# Retry Stuck Story

## Process

1. Parse the STORY-ID from the argument.
2. Find the story in the appropriate project's BACKLOG.md.
3. Verify the story has status "stuck".
4. Reset the story:
   - Change status from "stuck" to "ready"
   - Clear `design_notes` (architect will redesign)
   - Clear `learnings` from the failed attempt
   - Add a note: `retry_count: {N}` (increment if already present)
5. Read the story's previous `learnings` (if any) before clearing.
   Add key failure info to the project's AGENTS.md so the retry
   avoids the same mistake.
6. Report to Telegram:
   ```
   🔄 [{STORY-ID}] {title} — reset to ready (retry #{N})
   Previous failure: {brief reason from learnings}
   ```
7. Ask: "Want me to start building it now? (/build {STORY-ID})"

## Rules

- Only reset stories with status "stuck".
- If the story has been retried 3+ times, warn:
  "⚠️ This story has failed {N} times. Consider simplifying the
  acceptance criteria or breaking it into smaller stories."
- Never auto-retry without the story being explicitly retried.
