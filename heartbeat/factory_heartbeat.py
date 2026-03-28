#!/usr/bin/env python3
"""
Genesis Factory Heartbeat — Clock + Sensors for Claude Code.

This script has NO intelligence. It's a timer that sends triggers to Claude Code
via Telegram, and a sensor array that monitors external APIs/URLs and alerts
when something needs attention.

All decision-making happens in Claude Code. The heartbeat just provides triggers.

Requirements: pip install schedule requests pyyaml
"""

import os
import sys
import time
import json
import signal
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import schedule
import requests
import yaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = os.environ.get("HEARTBEAT_CONFIG", "config.yaml")
PROJECTS_DIR = os.path.expanduser("~/projects")
LOG_FILE = "heartbeat.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("heartbeat")

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------

def load_config():
    if not os.path.exists(CONFIG_PATH):
        log.error(f"Config file not found: {CONFIG_PATH}")
        log.error("Copy config.example.yaml to config.yaml and fill in your values.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

config = load_config()

TELEGRAM_TOKEN = config.get("telegram", {}).get("bot_token") or os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config.get("telegram", {}).get("chat_id") or os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    log.error("Telegram bot_token and chat_id are required in config.yaml or environment.")
    sys.exit(1)

# Paused flag — controlled via pause file
# Claude Code creates/removes ~/projects/.factory_paused via Telegram commands
PAUSE_FILE = os.path.expanduser("~/projects/.factory_paused")

def is_paused():
    return os.path.exists(PAUSE_FILE)

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram(message: str):
    """Send a message to the factory Telegram chat."""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
        if not resp.ok:
            log.error(f"Telegram send failed: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"Telegram send error: {e}")

def ping_claude(message: str):
    """
    Send a trigger message to Claude Code via Telegram Channels.
    Claude Code session (running with --channels) picks this up automatically.
    """
    if is_paused():
        log.info(f"PAUSED — skipping trigger: {message[:50]}...")
        return
    log.info(f"Trigger → {message[:80]}...")
    send_telegram(message)

# ---------------------------------------------------------------------------
# Scheduled Triggers (clock function)
# ---------------------------------------------------------------------------

def trigger_nightly():
    """22:00 Mon-Fri: trigger nightly development cycle."""
    if datetime.now().weekday() >= 5:  # skip weekends
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
    if datetime.now().weekday() != 6:  # Sunday only
        return
    ping_claude(
        "🔍 Weekly discovery time. Run /discover all to research competitors "
        "and generate new stories for all projects."
    )

def trigger_self_improvement():
    """23:00 Friday: trigger factory self-improvement."""
    if datetime.now().weekday() != 4:  # Friday only
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
# Monitors (sensor function)
# ---------------------------------------------------------------------------

def run_monitors():
    """
    Check project-specific monitors defined in heartbeat_config.yaml files.
    Each project can define its own monitors (API polling, uptime checks, etc.)
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

def run_single_monitor(monitor: dict, project_name: str):
    """Execute a single monitor check."""
    monitor_type = monitor.get("type", "http_poll")
    name = monitor.get("name", "unnamed")

    if monitor_type == "http_poll":
        url = monitor["url"]
        method = monitor.get("method", "GET").upper()
        body = monitor.get("body")
        headers = monitor.get("headers", {"Content-Type": "application/json"})

        # Expand environment variables in body
        if body and "${" in body:
            for key, val in os.environ.items():
                body = body.replace(f"${{{key}}}", val)

        if method == "POST":
            resp = requests.post(url, data=body, headers=headers, timeout=15)
        else:
            resp = requests.get(url, headers=headers, timeout=15)

        # Evaluate alert condition
        alert_condition = monitor.get("alert_condition", "")
        if alert_condition:
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
            response = resp  # make available to eval

            try:
                should_alert = eval(alert_condition)
            except Exception as e:
                log.error(f"Monitor '{name}' alert_condition eval error: {e}")
                return

            if should_alert:
                alert_msg = monitor.get("alert_message", f"Alert from {name}")
                alert_msg = alert_msg.replace("{details}", str(data)[:200] if data else str(resp.status_code))
                ping_claude(f"[{project_name}] {alert_msg}")

    elif monitor_type == "url_health":
        url = monitor["url"]
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                ping_claude(f"[{project_name}] 🔴 {name}: HTTP {resp.status_code} at {url}")
        except requests.ConnectionError:
            ping_claude(f"[{project_name}] 🔴 {name}: Connection failed to {url}")
        except requests.Timeout:
            ping_claude(f"[{project_name}] 🔴 {name}: Timeout reaching {url}")

# ---------------------------------------------------------------------------
# Watchdog — keep Claude Code alive
# ---------------------------------------------------------------------------

WATCHDOG_LAST_CHECK = datetime.now()
WATCHDOG_FAILURES = 0

def watchdog_check():
    """
    Check if Claude Code session is alive by looking for the tmux window.
    If dead, restart it.
    """
    global WATCHDOG_FAILURES

    try:
        result = subprocess.run(
            ["tmux", "list-windows", "-t", "factory"],
            capture_output=True, text=True, timeout=5,
        )
        if "claude" not in result.stdout:
            WATCHDOG_FAILURES += 1
            log.warning(f"Claude Code not found in tmux (failure #{WATCHDOG_FAILURES})")

            if WATCHDOG_FAILURES >= 3:
                log.error("Claude Code session dead — restarting...")
                subprocess.run(
                    ["tmux", "send-keys", "-t", "factory:claude",
                     "cd ~/projects && claude --channels", "Enter"],
                    timeout=5,
                )
                send_telegram("🔧 Claude Code session crashed. Restarting...")
                WATCHDOG_FAILURES = 0
        else:
            WATCHDOG_FAILURES = 0
    except Exception as e:
        log.error(f"Watchdog error: {e}")

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

schedule_config = config.get("schedule", {})

schedule.every().day.at(schedule_config.get("nightly", "22:00")).do(trigger_nightly)
schedule.every().day.at(schedule_config.get("morning_brief", "07:00")).do(trigger_morning_brief)
schedule.every().day.at(schedule_config.get("discovery", "02:00")).do(trigger_discovery)
schedule.every().day.at(schedule_config.get("self_improvement", "23:00")).do(trigger_self_improvement)
schedule.every().day.at(schedule_config.get("retro", "10:00")).do(trigger_retro)

monitor_interval = config.get("monitor_interval_seconds", 300)
schedule.every(monitor_interval).seconds.do(run_monitors)

schedule.every(60).seconds.do(watchdog_check)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def handle_signal(sig, frame):
    log.info("Shutting down heartbeat...")
    send_telegram("💤 Heartbeat shutting down.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def main():
    log.info("=" * 60)
    log.info("Genesis Factory Heartbeat starting...")
    log.info(f"Config: {CONFIG_PATH}")
    log.info(f"Projects dir: {PROJECTS_DIR}")
    log.info(f"Monitor interval: {monitor_interval}s")
    log.info("=" * 60)

    send_telegram("🏭 Genesis Factory Heartbeat started. All systems nominal.")

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            log.error(f"Schedule error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    main()
