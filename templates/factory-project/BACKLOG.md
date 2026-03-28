# Backlog — Genesis Factory

## Active Stories

### [FACT-001] Add cost tracking to morning brief
- **status**: ready
- **priority**: 2
- **effort**: M
- **why**: Need visibility into token usage per nightly cycle
- **acceptance_criteria**:
  - Morning brief includes estimated token cost for last 24h
  - Shows trend vs previous day
  - Warns if approaching rate limits

### [FACT-002] Add /pause and /resume Telegram commands
- **status**: ready
- **priority**: 1
- **effort**: S
- **why**: Need ability to pause factory during vacations
- **acceptance_criteria**:
  - /pause stops all heartbeat triggers
  - /resume restarts them
  - Status shows paused/active state

### [FACT-003] Improve story prioritization algorithm
- **status**: ready
- **priority**: 3
- **effort**: M
- **why**: Current scoring doesn't account for story age or dependencies
- **acceptance_criteria**:
  - Stories that have been "ready" for >7 days get priority boost
  - Stories with dependencies are sorted after their dependencies
  - Scoring formula is documented in product-strategist agent

## Completed

## Rejected
