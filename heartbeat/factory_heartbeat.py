#!/usr/bin/env python3
"""
Genesis Factory Heartbeat — Clock + Sensors for Claude Code.

A lightweight daemon (zero LLM calls) that provides:
1. Clock — scheduled triggers to Claude Code via Telegram
2. Sensors — monitors external APIs/URLs, alerts on anomalies
3. Watchdog — restarts Claude Code if the session crashes
4. System health — monitors disk space

Requirements: pip install schedule requests pyyaml
"""

import ast
import os
import re
import sys
import time
import json
import shutil
import signal
import logging
import subprocess
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path

import schedule
import requests
import yaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = os.environ.get("HEARTBEAT_CONFIG", "config.yaml")
LOG_FILE = "heartbeat.log"

# Logging with rotation (max 5 MB per file, keep 3 backups)
log = logging.getLogger("heartbeat")
log.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
_file_handler.setFormatter(_formatter)
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_formatter)
log.addHandler(_file_handler)
log.addHandler(_stream_handler)


def load_config():
    """Load heartbeat configuration from YAML file."""
    if not os.path.exists(CONFIG_PATH):
        log.error(f"Config file not found: {CONFIG_PATH}")
        log.error("Copy config.example.yaml to config.yaml and fill in values.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            log.error(f"Invalid YAML in {CONFIG_PATH}: {e}")
            sys.exit(1)


config = load_config()

PROJECTS_DIR = os.path.expanduser(config.get("projects_dir", "~/projects"))
TELEGRAM_TOKEN = (
    config.get("telegram", {}).get("bot_token")
    or os.environ.get("TELEGRAM_BOT_TOKEN")
)
TELEGRAM_CHAT_ID = (
    config.get("telegram", {}).get("chat_id")
    or os.environ.get("TELEGRAM_CHAT_ID")
)

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    log.error("Telegram bot_token and chat_id required in config.yaml or env.")
    sys.exit(1)

if ":" not in TELEGRAM_TOKEN or len(TELEGRAM_TOKEN) < 20:
    log.error(
        f"TELEGRAM_BOT_TOKEN looks invalid (expected format: 123456789:ABCdef...)."
        f" Got: {TELEGRAM_TOKEN[:8]}..."
    )
    sys.exit(1)

ALERT_COOLDOWN = config.get("alert_cooldown_seconds", 900)  # 15 min default
DISK_WARNING_GB = config.get("disk_warning_gb", 10)
PAUSE_FILE = os.path.join(PROJECTS_DIR, ".factory_paused")

# Watchdog constants
WATCHDOG_FAILURE_THRESHOLD = 3
WATCHDOG_MAX_RESTARTS_PER_HOUR = 5
SUBPROCESS_TIMEOUT = 5
HTTP_TIMEOUT_POLL = 15
HTTP_TIMEOUT_HEALTH = 10


def is_paused():
    """Check if factory is paused via flag file."""
    return os.path.exists(PAUSE_FILE)


# ---------------------------------------------------------------------------
# Safe Expression Evaluator
# ---------------------------------------------------------------------------
# Replaces raw eval() for monitor alert_condition expressions.
# Validates the AST to block imports, exec, dunder access, and other
# dangerous operations while supporting comparisons, math, builtins,
# subscript/attribute access, and comprehensions.

ALLOWED_AST_NODES = frozenset({
    ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
    ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.In, ast.NotIn, ast.Is, ast.IsNot,
    ast.Call, ast.keyword,
    ast.Subscript, ast.Attribute, ast.Slice,
    ast.Dict, ast.List, ast.Tuple, ast.Set,
    ast.IfExp,
    ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp,
    ast.comprehension,
    ast.Starred,
})

BLOCKED_NAMES = frozenset({
    "__import__", "exec", "eval", "compile", "open", "input",
    "breakpoint", "globals", "locals", "vars", "dir",
    "getattr", "setattr", "delattr", "exit", "quit",
})

SAFE_BUILTINS = {
    "float": float, "int": int, "str": str, "bool": bool,
    "abs": abs, "len": len, "min": min, "max": max, "round": round,
    "any": any, "all": all, "sum": sum,
    "True": True, "False": False, "None": None,
}


def _validate_ast(node):
    """Recursively validate that an AST contains only allowed node types."""
    if type(node) not in ALLOWED_AST_NODES:
        raise ValueError(f"Disallowed expression: {type(node).__name__}")
    if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
        raise ValueError(f"Access to '{node.attr}' is not allowed")
    if isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
        raise ValueError(f"Name '{node.id}' is not allowed")
    for child in ast.iter_child_nodes(node):
        _validate_ast(child)


def safe_eval(expr_str, variables=None):
    """
    Evaluate a Python expression safely.

    Allows: comparisons, math, safe builtins (float/int/abs/any/all/...),
    subscript/attribute access (no dunders), comprehensions.
    Blocks: imports, exec, eval, open, dunder access, and other unsafe ops.
    """
    tree = ast.parse(expr_str, mode="eval")
    _validate_ast(tree.body)
    safe_globals = {"__builtins__": SAFE_BUILTINS}
    return eval(compile(tree, "<monitor>", "eval"), safe_globals, variables or {})


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram(message):
    """Send a message to the factory Telegram chat."""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
        if not resp.ok:
            log.error(f"Telegram send failed: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"Telegram send error: {e}")


def ping_claude(message):
    """
    Send a scheduled trigger to Claude Code via Telegram Channels.
    Respects the pause flag — monitors and watchdog use send_telegram directly.
    """
    if is_paused():
        log.info(f"PAUSED — skipping trigger: {message[:50]}...")
        return
    log.info(f"Trigger -> {message[:80]}...")
    send_telegram(message)


# ---------------------------------------------------------------------------
# Scheduled Triggers (clock function)
# ---------------------------------------------------------------------------

def trigger_nightly():
    """22:00 Mon-Fri: trigger nightly development cycle."""
    if datetime.now().weekday() >= 5:
        return
    ping_claude(
        "🌙 It's 22:00 — nightly cycle time. "
        "Run /nightly to pick the top story and implement it."
    )


def trigger_morning_brief():
    """07:00 daily: trigger morning brief."""
    ping_claude(
        "☀️ Good morning! Run /morning-brief to compile today's status report."
    )


def trigger_discovery():
    """02:00 Sunday: trigger weekly discovery."""
    if datetime.now().weekday() != 6:
        return
    ping_claude(
        "🔍 Weekly discovery time. Run /discover all to research competitors "
        "and generate new stories for all projects."
    )


def trigger_self_improvement():
    """23:00 Friday: trigger factory self-improvement."""
    if datetime.now().weekday() != 4:
        return
    ping_claude(
        "🔧 Self-improvement time. Run /upgrade to work on factory improvements."
    )


def trigger_retro():
    """Sunday 10:00: weekly retrospective."""
    if datetime.now().weekday() != 6:
        return
    ping_claude(
        "📝 Weekly retrospective time. Run /retro to analyze this week's cycles "
        "and update learnings."
    )


# ---------------------------------------------------------------------------
# Alert State (cooldown to prevent alert storms)
# ---------------------------------------------------------------------------

_alert_state = {}  # monitor_key -> last alert datetime
_service_down = set()  # monitor_keys currently in "down" state


def _should_alert(monitor_key):
    """Check if enough time has passed since last alert for this monitor."""
    last = _alert_state.get(monitor_key)
    if last is None:
        return True
    return (datetime.now() - last).total_seconds() >= ALERT_COOLDOWN


def _record_alert(monitor_key):
    """Record that an alert was sent for this monitor."""
    _alert_state[monitor_key] = datetime.now()
    _service_down.add(monitor_key)


def _record_recovery(monitor_key):
    """Record that a service recovered. Returns True if it was previously down."""
    was_down = monitor_key in _service_down
    _service_down.discard(monitor_key)
    _alert_state.pop(monitor_key, None)
    return was_down


# ---------------------------------------------------------------------------
# Monitors (sensor function)
# ---------------------------------------------------------------------------

def run_monitors():
    """
    Check project-specific monitors from heartbeat_config.yaml files.
    Monitors run even when paused (use send_telegram, not ping_claude).
    """
    projects_dir = Path(PROJECTS_DIR)
    if not projects_dir.exists():
        return

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        monitor_file = project_dir / "heartbeat_config.yaml"
        if not monitor_file.exists():
            continue

        try:
            with open(monitor_file) as f:
                project_config = yaml.safe_load(f)
        except Exception as e:
            log.error(f"Failed to read {monitor_file}: {e}")
            continue

        for monitor in project_config.get("monitors", []):
            try:
                run_single_monitor(monitor, project_dir.name)
            except Exception as e:
                log.error(f"Monitor '{monitor.get('name')}' error: {e}")


def _sanitize_log_data(text, max_len=200):
    """Truncate and strip potential secrets from log output."""
    text = str(text)[:max_len]
    return re.sub(
        r'(?i)(api[_-]?key|token|secret|password|authorization)["\s:=]+\S+',
        r'\1=***',
        text,
    )


def run_single_monitor(monitor, project_name):
    """Execute a single monitor check with alert cooldown."""
    monitor_type = monitor.get("type", "http_poll")
    name = monitor.get("name", "unnamed")
    monitor_key = f"{project_name}:{name}"

    # Validate required fields
    if monitor_type in ("http_poll", "url_health") and "url" not in monitor:
        log.error(f"Monitor '{name}' in {project_name}: missing 'url' field")
        return

    if monitor_type == "http_poll":
        url = monitor["url"]
        method = monitor.get("method", "GET").upper()
        body = monitor.get("body")
        headers = monitor.get("headers", {"Content-Type": "application/json"})

        # Expand only explicitly referenced environment variables
        if body and "${" in body:
            for var_name in re.findall(r'\$\{(\w+)\}', body):
                val = os.environ.get(var_name)
                if val is not None:
                    body = body.replace(f"${{{var_name}}}", val)
                else:
                    log.warning(
                        f"Monitor '{name}': env var ${{{var_name}}} not set"
                    )
            # Fail-fast if any env vars remain unresolved
            unresolved = re.findall(r'\$\{(\w+)\}', body)
            if unresolved:
                log.error(
                    f"Monitor '{name}': unresolved env vars: {unresolved}"
                )
                return

        try:
            if method == "POST":
                resp = requests.post(
                    url, data=body, headers=headers, timeout=HTTP_TIMEOUT_POLL
                )
            else:
                resp = requests.get(
                    url, headers=headers, timeout=HTTP_TIMEOUT_POLL
                )
        except requests.ConnectionError:
            if _should_alert(monitor_key):
                send_telegram(
                    f"[{project_name}] 🔴 {name}: Connection failed to {url}"
                )
                _record_alert(monitor_key)
            return
        except requests.Timeout:
            if _should_alert(monitor_key):
                send_telegram(
                    f"[{project_name}] 🔴 {name}: Timeout reaching {url}"
                )
                _record_alert(monitor_key)
            return

        alert_condition = monitor.get("alert_condition", "")
        if alert_condition:
            try:
                data = (
                    resp.json()
                    if resp.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else None
                )
            except (ValueError, TypeError):
                log.warning(f"Monitor '{name}': invalid JSON response")
                data = None

            response = resp

            try:
                should_fire = safe_eval(
                    alert_condition, {"data": data, "response": response}
                )
            except Exception as e:
                log.error(f"Monitor '{name}' alert_condition error: {e}")
                return

            if should_fire and _should_alert(monitor_key):
                alert_msg = monitor.get("alert_message", f"Alert from {name}")
                details = _sanitize_log_data(data) if data else str(resp.status_code)
                alert_msg = alert_msg.replace("{details}", details)
                send_telegram(f"[{project_name}] {alert_msg}")
                _record_alert(monitor_key)

    elif monitor_type == "url_health":
        url = monitor["url"]
        try:
            resp = requests.get(url, timeout=HTTP_TIMEOUT_HEALTH)
            if resp.status_code != 200:
                if _should_alert(monitor_key):
                    send_telegram(
                        f"[{project_name}] 🔴 {name}: "
                        f"HTTP {resp.status_code} at {url}"
                    )
                    _record_alert(monitor_key)
            else:
                # Service recovered — notify if it was previously down
                if _record_recovery(monitor_key):
                    send_telegram(
                        f"[{project_name}] ✅ {name}: recovered ({url})"
                    )
        except requests.ConnectionError:
            if _should_alert(monitor_key):
                send_telegram(
                    f"[{project_name}] 🔴 {name}: Connection failed to {url}"
                )
                _record_alert(monitor_key)
        except requests.Timeout:
            if _should_alert(monitor_key):
                send_telegram(
                    f"[{project_name}] 🔴 {name}: Timeout reaching {url}"
                )
                _record_alert(monitor_key)

    else:
        log.warning(
            f"Monitor '{name}' in {project_name}: "
            f"unknown type '{monitor_type}' (expected http_poll or url_health)"
        )


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------

def check_system_health():
    """Check disk space and alert if running low."""
    try:
        usage = shutil.disk_usage("/")
        free_gb = usage.free / (1024**3)
        monitor_key = "system:disk"
        if free_gb < DISK_WARNING_GB:
            if _should_alert(monitor_key):
                total_gb = usage.total / (1024**3)
                send_telegram(
                    f"⚠️ Low disk space: {free_gb:.1f} GB free "
                    f"of {total_gb:.0f} GB (threshold: {DISK_WARNING_GB} GB)"
                )
                _record_alert(monitor_key)
        else:
            if _record_recovery(monitor_key):
                send_telegram(
                    f"✅ Disk space recovered: {free_gb:.1f} GB free"
                )
    except Exception as e:
        log.error(f"System health check error: {e}")


# ---------------------------------------------------------------------------
# Watchdog — keep Claude Code alive
# ---------------------------------------------------------------------------

_watchdog_failures = 0
_watchdog_restarts = []  # timestamps of recent restarts


def watchdog_check():
    """
    Check if Claude Code session is alive in the factory tmux session.
    If missing for 3+ consecutive checks (~3 minutes), restart it.
    Limits restarts to WATCHDOG_MAX_RESTARTS_PER_HOUR to avoid loops.
    """
    global _watchdog_failures

    try:
        session_check = subprocess.run(
            ["tmux", "has-session", "-t", "factory"],
            capture_output=True, timeout=SUBPROCESS_TIMEOUT,
        )
        if session_check.returncode != 0:
            _watchdog_failures += 1
            log.warning(
                f"tmux session 'factory' not found "
                f"(failure #{_watchdog_failures})"
            )
            if _watchdog_failures >= WATCHDOG_FAILURE_THRESHOLD:
                _restart_claude_code(session_exists=False)
            return

        result = subprocess.run(
            ["tmux", "list-windows", "-t", "factory"],
            capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
        )
        if "claude" not in result.stdout:
            _watchdog_failures += 1
            log.warning(
                f"Claude Code window not found in tmux "
                f"(failure #{_watchdog_failures})"
            )
            if _watchdog_failures >= WATCHDOG_FAILURE_THRESHOLD:
                _restart_claude_code(session_exists=True)
        else:
            _watchdog_failures = 0
    except subprocess.TimeoutExpired:
        log.error("Watchdog: tmux command timed out")
    except Exception as e:
        log.error(f"Watchdog error: {e}")


def _restart_claude_code(session_exists=True):
    """Restart Claude Code in the factory tmux session."""
    global _watchdog_failures

    # Rate-limit restarts to prevent infinite loops
    now = datetime.now()
    cutoff = now - timedelta(hours=1)
    _watchdog_restarts[:] = [t for t in _watchdog_restarts if t > cutoff]

    if len(_watchdog_restarts) >= WATCHDOG_MAX_RESTARTS_PER_HOUR:
        log.error(
            f"Watchdog: {WATCHDOG_MAX_RESTARTS_PER_HOUR} restarts in the last "
            f"hour — backing off. Manual intervention needed."
        )
        if _should_alert("watchdog:restart_limit"):
            send_telegram(
                f"🔴 Claude Code restart limit reached "
                f"({WATCHDOG_MAX_RESTARTS_PER_HOUR}/hour). "
                f"Manual restart needed."
            )
            _record_alert("watchdog:restart_limit")
        _watchdog_failures = 0
        return

    log.error("Claude Code session dead — restarting...")

    try:
        if not session_exists:
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", "factory", "-n", "claude"],
                timeout=SUBPROCESS_TIMEOUT,
            )
        else:
            result = subprocess.run(
                ["tmux", "list-windows", "-t", "factory"],
                capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
            )
            if "claude" not in result.stdout:
                subprocess.run(
                    ["tmux", "new-window", "-t", "factory", "-n", "claude"],
                    timeout=SUBPROCESS_TIMEOUT,
                )

        subprocess.run(
            [
                "tmux", "send-keys", "-t", "factory:claude",
                f"cd {PROJECTS_DIR} && claude --channels", "Enter",
            ],
            timeout=SUBPROCESS_TIMEOUT,
        )
        send_telegram("🔧 Claude Code session crashed. Restarting...")
        _watchdog_failures = 0
        _watchdog_restarts.append(now)
    except subprocess.TimeoutExpired:
        log.error("Restart failed: tmux command timed out")
    except Exception as e:
        log.error(f"Failed to restart Claude Code: {e}")


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

schedule_config = config.get("schedule", {})

schedule.every().day.at(schedule_config.get("nightly", "22:00")).do(trigger_nightly)
schedule.every().day.at(schedule_config.get("morning_brief", "07:00")).do(
    trigger_morning_brief
)
schedule.every().day.at(schedule_config.get("discovery", "02:00")).do(
    trigger_discovery
)
schedule.every().day.at(schedule_config.get("self_improvement", "23:00")).do(
    trigger_self_improvement
)
schedule.every().day.at(schedule_config.get("retro", "10:00")).do(trigger_retro)

monitor_interval = config.get("monitor_interval_seconds", 300)
schedule.every(monitor_interval).seconds.do(run_monitors)

health_interval = config.get("health_check_interval_seconds", 3600)
schedule.every(health_interval).seconds.do(check_system_health)

schedule.every(60).seconds.do(watchdog_check)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


_shutdown = False


def handle_signal(sig, frame):
    global _shutdown
    log.info("Shutdown signal received, finishing current work...")
    _shutdown = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def main():
    log.info("=" * 60)
    log.info("Genesis Factory Heartbeat starting...")
    log.info(f"  Config: {CONFIG_PATH}")
    log.info(f"  Projects: {PROJECTS_DIR}")
    log.info(f"  Monitor interval: {monitor_interval}s")
    log.info(f"  Alert cooldown: {ALERT_COOLDOWN}s")
    log.info(f"  Disk warning: {DISK_WARNING_GB} GB")
    log.info("=" * 60)

    send_telegram("🏭 Genesis Factory Heartbeat started. All systems nominal.")

    while not _shutdown:
        try:
            schedule.run_pending()
        except Exception as e:
            log.error(f"Schedule error: {e}")
        time.sleep(30)

    log.info("Shutting down heartbeat...")
    send_telegram("💤 Heartbeat shutting down.")
    sys.exit(0)


if __name__ == "__main__":
    main()
