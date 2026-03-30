-- Genesis Factory Heartbeat — State Persistence Schema
-- SQLite database for persisting state across restarts.
-- Auto-created on first run if it doesn't exist.

-- Alert state (replaces alert_state.json)
CREATE TABLE IF NOT EXISTS alert_state (
    monitor_key   TEXT PRIMARY KEY,
    last_alert_at TEXT NOT NULL,  -- ISO 8601 datetime
    is_down       INTEGER NOT NULL DEFAULT 0  -- boolean: 1 = currently down
);

-- Watchdog restart history
CREATE TABLE IF NOT EXISTS watchdog_restarts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    restarted_at TEXT NOT NULL,  -- ISO 8601 datetime
    uptime_seconds INTEGER,
    failure_count  INTEGER,
    reason         TEXT
);

-- Build cycle metrics (populated by /build via cost_log)
CREATE TABLE IF NOT EXISTS cycle_metrics (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    completed_at TEXT NOT NULL,  -- ISO 8601 datetime
    project      TEXT NOT NULL,
    story_id     TEXT NOT NULL,
    effort       TEXT NOT NULL,  -- S, M, L, XL
    status       TEXT NOT NULL,  -- done, stuck
    tokens_approx INTEGER,      -- approximate token usage
    duration_minutes INTEGER    -- wall clock time
);

-- Story status transitions (audit trail)
CREATE TABLE IF NOT EXISTS story_transitions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    changed_at  TEXT NOT NULL,  -- ISO 8601 datetime
    project     TEXT NOT NULL,
    story_id    TEXT NOT NULL,
    from_status TEXT,
    to_status   TEXT NOT NULL
);

-- Monitor config cache (replaces in-memory dict)
CREATE TABLE IF NOT EXISTS monitor_config_cache (
    project_name TEXT PRIMARY KEY,
    config_yaml  TEXT NOT NULL,
    cached_at    TEXT NOT NULL  -- ISO 8601 datetime
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_cycle_project ON cycle_metrics(project);
CREATE INDEX IF NOT EXISTS idx_cycle_date ON cycle_metrics(completed_at);
CREATE INDEX IF NOT EXISTS idx_transitions_story ON story_transitions(story_id);
CREATE INDEX IF NOT EXISTS idx_watchdog_date ON watchdog_restarts(restarted_at);
