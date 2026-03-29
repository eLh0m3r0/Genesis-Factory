"""Pytest configuration for heartbeat tests."""

import os
import tempfile

_config_path = None


def pytest_configure():
    """Create minimal config before any test imports."""
    global _config_path
    config_content = """\
telegram:
  bot_token: "123456789:ABCdefGHIjklMNO_test"
  chat_id: "123456789"
projects_dir: "/tmp/genesis_test_projects"
alert_cooldown_seconds: 60
disk_warning_gb: 10
"""
    fd, path = tempfile.mkstemp(suffix=".yaml", prefix="heartbeat_test_")
    with os.fdopen(fd, "w") as f:
        f.write(config_content)
    os.environ["HEARTBEAT_CONFIG"] = path
    _config_path = path


def pytest_unconfigure():
    """Clean up temporary config file."""
    if _config_path and os.path.exists(_config_path):
        os.unlink(_config_path)
    os.environ.pop("HEARTBEAT_CONFIG", None)
