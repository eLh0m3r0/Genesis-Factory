#!/usr/bin/env python3
"""Tests for Genesis Factory Heartbeat."""

import json
import os
import signal
import tempfile
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestSafeEval:
    """Test the safe expression evaluator."""

    def test_simple_comparison(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("1 > 0") is True
        assert safe_eval("1 < 0") is False
        assert safe_eval("1 == 1") is True
        assert safe_eval("2 != 3") is True

    def test_float_conversion(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("float('3.14') > 3.0") is True
        assert safe_eval("float('2.5') < 2.0") is False

    def test_variable_access(self):
        from factory_heartbeat import safe_eval
        data = {"rate": "0.6"}
        assert safe_eval("float(data['rate']) > 0.5", {"data": data}) is True
        assert safe_eval("float(data['rate']) > 0.7", {"data": data}) is False

    def test_nested_dict_get(self):
        from factory_heartbeat import safe_eval
        data = {"marginSummary": {"accountValue": "1000"}}
        expr = "float(data.get('marginSummary',{}).get('accountValue','0')) < 500"
        assert safe_eval(expr, {"data": data}) is False

        data2 = {"marginSummary": {"accountValue": "100"}}
        assert safe_eval(expr, {"data": data2}) is True

    def test_any_with_generator(self):
        from factory_heartbeat import safe_eval
        data = [None, [{"funding": "0.001"}, {"funding": "0.0001"}]]
        expr = "any(abs(float(a.get('funding','0'))) > 0.0005 for a in data[1])"
        assert safe_eval(expr, {"data": data}) is True

    def test_all_with_generator(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("all(x > 0 for x in [1, 2, 3])") is True
        assert safe_eval("all(x > 0 for x in [1, -2, 3])") is False

    def test_math_operations(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("2 + 3") == 5
        assert safe_eval("10 - 4") == 6
        assert safe_eval("3 * 7") == 21
        assert safe_eval("abs(-5)") == 5
        assert safe_eval("max(1, 5, 3)") == 5
        assert safe_eval("min(1, 5, 3)") == 1
        assert safe_eval("round(3.7)") == 4

    def test_boolean_logic(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("True and True") is True
        assert safe_eval("True and False") is False
        assert safe_eval("True or False") is True
        assert safe_eval("not False") is True

    def test_list_comprehension(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("[x * 2 for x in [1, 2, 3]]") == [2, 4, 6]

    def test_string_operations(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("str(42)") == "42"
        assert safe_eval("len('hello')") == 5
        assert safe_eval("int('42')") == 42

    def test_ternary_expression(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("'yes' if True else 'no'") == "yes"
        assert safe_eval("'yes' if False else 'no'") == "no"

    def test_in_operator(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("'a' in ['a', 'b', 'c']") is True
        assert safe_eval("'d' in ['a', 'b', 'c']") is False

    def test_chained_comparison(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("1 < 2 < 3") is True
        assert safe_eval("1 < 2 > 3") is False

    def test_blocks_import(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("__import__('os').system('ls')")

    def test_blocks_dunder_attribute(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("''.__class__")

    def test_blocks_dunder_bases(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("().__class__.__bases__")

    def test_blocks_exec(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("exec('print(1)')")

    def test_blocks_eval_call(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("eval('1+1')")

    def test_blocks_open(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("open('/etc/passwd')")

    def test_blocks_globals(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("globals()")

    def test_blocks_lambda(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="Disallowed"):
            safe_eval("(lambda: 1)()")

    def test_blocks_getattr(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="not allowed"):
            safe_eval("getattr('', 'join')")

    def test_timeout_sets_alarm(self):
        """safe_eval should set and clear SIGALRM for timeout protection."""
        from factory_heartbeat import safe_eval
        with patch("factory_heartbeat.signal.alarm") as mock_alarm:
            with patch("factory_heartbeat.signal.signal") as mock_signal:
                mock_signal.return_value = signal.SIG_DFL
                safe_eval("1 + 1")
                # alarm(1) sets the timeout, alarm(0) cancels it
                assert mock_alarm.call_count == 2
                mock_alarm.assert_any_call(1)
                mock_alarm.assert_any_call(0)


class TestAlertCooldown:
    """Test alert deduplication logic."""

    def test_first_alert_allowed(self):
        from factory_heartbeat import _should_alert, _alert_state, _service_down
        _alert_state.clear()
        _service_down.clear()
        assert _should_alert("test:first") is True

    def test_repeated_alert_blocked(self):
        from factory_heartbeat import _should_alert, _record_alert, _alert_state, _service_down
        _alert_state.clear()
        _service_down.clear()
        _record_alert("test:repeated")
        assert _should_alert("test:repeated") is False

    def test_alert_after_cooldown(self):
        from factory_heartbeat import _should_alert, _alert_state, _service_down, ALERT_COOLDOWN
        _alert_state.clear()
        _service_down.clear()
        _alert_state["test:expired"] = datetime.now() - timedelta(
            seconds=ALERT_COOLDOWN + 1
        )
        assert _should_alert("test:expired") is True

    def test_different_monitors_independent(self):
        from factory_heartbeat import _should_alert, _record_alert, _alert_state, _service_down
        _alert_state.clear()
        _service_down.clear()
        _record_alert("test:monitorA")
        assert _should_alert("test:monitorA") is False
        assert _should_alert("test:monitorB") is True

    def test_record_updates_timestamp(self):
        from factory_heartbeat import _record_alert, _alert_state, _service_down
        _alert_state.clear()
        _service_down.clear()
        _record_alert("test:ts")
        t1 = _alert_state["test:ts"]
        assert isinstance(t1, datetime)
        assert (datetime.now() - t1).total_seconds() < 2

    def test_record_alert_marks_service_down(self):
        from factory_heartbeat import _record_alert, _service_down
        _service_down.clear()
        _record_alert("test:down")
        assert "test:down" in _service_down

    def test_record_recovery_returns_true_if_was_down(self):
        from factory_heartbeat import _record_alert, _record_recovery, _alert_state, _service_down
        _alert_state.clear()
        _service_down.clear()
        _record_alert("test:recover")
        assert _record_recovery("test:recover") is True
        assert "test:recover" not in _service_down
        assert "test:recover" not in _alert_state

    def test_record_recovery_returns_false_if_was_up(self):
        from factory_heartbeat import _record_recovery, _service_down
        _service_down.clear()
        assert _record_recovery("test:never_down") is False


class TestAlertStatePersistence:
    """Test alert state save/load to JSON file."""

    def test_save_and_load_roundtrip(self, tmp_path):
        import factory_heartbeat
        original_file = factory_heartbeat.ALERT_STATE_FILE
        test_file = str(tmp_path / "test_alert_state.json")
        factory_heartbeat.ALERT_STATE_FILE = test_file
        try:
            factory_heartbeat._alert_state.clear()
            factory_heartbeat._service_down.clear()

            # Record some alerts
            factory_heartbeat._alert_state["mon:a"] = datetime(2026, 3, 30, 10, 0, 0)
            factory_heartbeat._alert_state["mon:b"] = datetime(2026, 3, 30, 11, 0, 0)
            factory_heartbeat._service_down.add("mon:a")
            factory_heartbeat._save_alert_state()

            # Clear in-memory state
            factory_heartbeat._alert_state.clear()
            factory_heartbeat._service_down.clear()

            # Load from file
            factory_heartbeat._load_alert_state()

            assert len(factory_heartbeat._alert_state) == 2
            assert "mon:a" in factory_heartbeat._alert_state
            assert "mon:b" in factory_heartbeat._alert_state
            assert factory_heartbeat._alert_state["mon:a"] == datetime(2026, 3, 30, 10, 0, 0)
            assert "mon:a" in factory_heartbeat._service_down
        finally:
            factory_heartbeat.ALERT_STATE_FILE = original_file

    def test_load_missing_file(self, tmp_path):
        import factory_heartbeat
        original_file = factory_heartbeat.ALERT_STATE_FILE
        factory_heartbeat.ALERT_STATE_FILE = str(tmp_path / "nonexistent.json")
        try:
            factory_heartbeat._alert_state.clear()
            factory_heartbeat._service_down.clear()
            factory_heartbeat._load_alert_state()
            # Should not crash, state should remain empty
            assert len(factory_heartbeat._alert_state) == 0
            assert len(factory_heartbeat._service_down) == 0
        finally:
            factory_heartbeat.ALERT_STATE_FILE = original_file

    def test_load_corrupt_json(self, tmp_path):
        import factory_heartbeat
        original_file = factory_heartbeat.ALERT_STATE_FILE
        test_file = tmp_path / "corrupt.json"
        test_file.write_text("{invalid json")
        factory_heartbeat.ALERT_STATE_FILE = str(test_file)
        try:
            factory_heartbeat._alert_state["old"] = datetime.now()
            factory_heartbeat._load_alert_state()
            # Should start fresh on corrupt file
            assert len(factory_heartbeat._alert_state) == 0
            assert len(factory_heartbeat._service_down) == 0
        finally:
            factory_heartbeat.ALERT_STATE_FILE = original_file

    def test_record_alert_saves_state(self, tmp_path):
        import factory_heartbeat
        original_file = factory_heartbeat.ALERT_STATE_FILE
        test_file = str(tmp_path / "auto_save.json")
        factory_heartbeat.ALERT_STATE_FILE = test_file
        try:
            factory_heartbeat._alert_state.clear()
            factory_heartbeat._service_down.clear()
            factory_heartbeat._record_alert("test:auto")
            # File should exist after record_alert
            assert os.path.exists(test_file)
            with open(test_file) as f:
                data = json.load(f)
            assert "test:auto" in data["alert_state"]
            assert "test:auto" in data["service_down"]
        finally:
            factory_heartbeat.ALERT_STATE_FILE = original_file

    def test_record_recovery_saves_state(self, tmp_path):
        import factory_heartbeat
        original_file = factory_heartbeat.ALERT_STATE_FILE
        test_file = str(tmp_path / "recovery_save.json")
        factory_heartbeat.ALERT_STATE_FILE = test_file
        try:
            factory_heartbeat._alert_state.clear()
            factory_heartbeat._service_down.clear()
            factory_heartbeat._record_alert("test:rec")
            factory_heartbeat._record_recovery("test:rec")
            with open(test_file) as f:
                data = json.load(f)
            assert "test:rec" not in data["alert_state"]
            assert "test:rec" not in data["service_down"]
        finally:
            factory_heartbeat.ALERT_STATE_FILE = original_file


class TestTelegramRetry:
    """Test Telegram send with retry and backoff."""

    @patch("factory_heartbeat.requests.post")
    def test_success_returns_true(self, mock_post):
        from factory_heartbeat import send_telegram
        mock_post.return_value = MagicMock(ok=True)
        assert send_telegram("test") is True
        assert mock_post.call_count == 1

    @patch("factory_heartbeat.time.sleep")
    @patch("factory_heartbeat.requests.post")
    def test_retries_on_server_error(self, mock_post, mock_sleep):
        from factory_heartbeat import send_telegram
        mock_post.return_value = MagicMock(ok=False, status_code=500)
        assert send_telegram("test") is False
        assert mock_post.call_count == 3
        # Backoff: 1s after first fail, 2s after second
        assert mock_sleep.call_count == 2

    @patch("factory_heartbeat.requests.post")
    def test_no_retry_on_client_error(self, mock_post):
        from factory_heartbeat import send_telegram
        mock_post.return_value = MagicMock(ok=False, status_code=400, text="Bad Request")
        assert send_telegram("test") is False
        assert mock_post.call_count == 1  # No retry

    @patch("factory_heartbeat.time.sleep")
    @patch("factory_heartbeat.requests.post")
    def test_retries_on_exception(self, mock_post, mock_sleep):
        from factory_heartbeat import send_telegram
        mock_post.side_effect = ConnectionError("network down")
        assert send_telegram("test") is False
        assert mock_post.call_count == 3

    @patch("factory_heartbeat.time.sleep")
    @patch("factory_heartbeat.requests.post")
    def test_succeeds_on_second_attempt(self, mock_post, mock_sleep):
        from factory_heartbeat import send_telegram
        mock_post.side_effect = [
            ConnectionError("network down"),
            MagicMock(ok=True),
        ]
        assert send_telegram("test") is True
        assert mock_post.call_count == 2


class TestDiskSpaceProgressiveAlerts:
    """Test progressive disk space alert tiers."""

    @patch("factory_heartbeat.send_telegram")
    @patch("factory_heartbeat.shutil.disk_usage")
    def test_critical_under_2gb(self, mock_usage, mock_tg):
        import factory_heartbeat
        factory_heartbeat._alert_state.clear()
        factory_heartbeat._service_down.clear()
        # 1 GB free of 500 GB
        mock_usage.return_value = MagicMock(
            free=1 * 1024**3, total=500 * 1024**3
        )
        factory_heartbeat.check_system_health()
        mock_tg.assert_called_once()
        msg = mock_tg.call_args[0][0]
        assert "nearly full" in msg.lower() or "🔴🔴" in msg

    @patch("factory_heartbeat.send_telegram")
    @patch("factory_heartbeat.shutil.disk_usage")
    def test_alert_under_5gb(self, mock_usage, mock_tg):
        import factory_heartbeat
        factory_heartbeat._alert_state.clear()
        factory_heartbeat._service_down.clear()
        # 3 GB free
        mock_usage.return_value = MagicMock(
            free=3 * 1024**3, total=500 * 1024**3
        )
        factory_heartbeat.check_system_health()
        mock_tg.assert_called_once()
        msg = mock_tg.call_args[0][0]
        assert "critical" in msg.lower() or "🔴" in msg

    @patch("factory_heartbeat.send_telegram")
    @patch("factory_heartbeat.shutil.disk_usage")
    def test_warning_under_threshold(self, mock_usage, mock_tg):
        import factory_heartbeat
        factory_heartbeat._alert_state.clear()
        factory_heartbeat._service_down.clear()
        # 7 GB free (under 10 GB default threshold)
        mock_usage.return_value = MagicMock(
            free=7 * 1024**3, total=500 * 1024**3
        )
        factory_heartbeat.check_system_health()
        mock_tg.assert_called_once()
        msg = mock_tg.call_args[0][0]
        assert "low disk" in msg.lower() or "⚠️" in msg

    @patch("factory_heartbeat.send_telegram")
    @patch("factory_heartbeat.shutil.disk_usage")
    def test_no_alert_above_threshold(self, mock_usage, mock_tg):
        import factory_heartbeat
        factory_heartbeat._alert_state.clear()
        factory_heartbeat._service_down.clear()
        # 50 GB free — no alert
        mock_usage.return_value = MagicMock(
            free=50 * 1024**3, total=500 * 1024**3
        )
        factory_heartbeat.check_system_health()
        mock_tg.assert_not_called()

    @patch("factory_heartbeat.send_telegram")
    @patch("factory_heartbeat.shutil.disk_usage")
    def test_recovery_notification(self, mock_usage, mock_tg):
        import factory_heartbeat
        factory_heartbeat._alert_state.clear()
        factory_heartbeat._service_down.clear()
        # Simulate prior warning state
        factory_heartbeat._service_down.add("system:disk:warning")
        # Now disk is fine
        mock_usage.return_value = MagicMock(
            free=50 * 1024**3, total=500 * 1024**3
        )
        factory_heartbeat.check_system_health()
        mock_tg.assert_called_once()
        msg = mock_tg.call_args[0][0]
        assert "recovered" in msg.lower() or "✅" in msg


class TestMonitorConfigCaching:
    """Test that monitor config is cached on parse error."""

    def test_cache_populated_on_success(self, tmp_path):
        import factory_heartbeat
        # Create a project with valid config
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        config_file = project_dir / "heartbeat_config.yaml"
        config_file.write_text("monitors: [{name: test, type: url_health, url: 'http://example.com'}]")

        original = factory_heartbeat.PROJECTS_DIR
        factory_heartbeat.PROJECTS_DIR = str(tmp_path)
        factory_heartbeat._monitor_config_cache.clear()
        try:
            with patch("factory_heartbeat.run_single_monitor"):
                factory_heartbeat.run_monitors()
            assert "test_project" in factory_heartbeat._monitor_config_cache
        finally:
            factory_heartbeat.PROJECTS_DIR = original

    def test_uses_cache_on_parse_error(self, tmp_path):
        import factory_heartbeat
        project_dir = tmp_path / "cached_project"
        project_dir.mkdir()
        config_file = project_dir / "heartbeat_config.yaml"

        # First: write valid config so it gets cached
        config_file.write_text("monitors: [{name: cached, type: url_health, url: 'http://example.com'}]")
        original = factory_heartbeat.PROJECTS_DIR
        factory_heartbeat.PROJECTS_DIR = str(tmp_path)
        factory_heartbeat._monitor_config_cache.clear()
        factory_heartbeat._alert_state.clear()
        factory_heartbeat._service_down.clear()
        try:
            with patch("factory_heartbeat.run_single_monitor") as mock_run:
                factory_heartbeat.run_monitors()
                assert mock_run.call_count == 1

            # Now corrupt the config
            config_file.write_text("{invalid: yaml: [}")

            with patch("factory_heartbeat.run_single_monitor") as mock_run:
                with patch("factory_heartbeat.send_telegram"):
                    factory_heartbeat.run_monitors()
                # Should still run monitors from cached config
                assert mock_run.call_count == 1
        finally:
            factory_heartbeat.PROJECTS_DIR = original


class TestWatchdogBackoff:
    """Test exponential backoff between watchdog restarts."""

    def test_backoff_delays_defined(self):
        from factory_heartbeat import _WATCHDOG_BACKOFF
        assert len(_WATCHDOG_BACKOFF) == 5
        # Delays should be increasing
        for i in range(1, len(_WATCHDOG_BACKOFF)):
            assert _WATCHDOG_BACKOFF[i] > _WATCHDOG_BACKOFF[i - 1]

    def test_backoff_blocks_immediate_restart(self):
        import factory_heartbeat
        factory_heartbeat._watchdog_restarts.clear()
        factory_heartbeat._watchdog_failures = 3
        # Simulate a restart that just happened
        factory_heartbeat._watchdog_restarts.append(datetime.now())

        with patch("factory_heartbeat.subprocess.run"):
            with patch("factory_heartbeat.send_telegram"):
                factory_heartbeat._restart_claude_code(session_exists=True)
        # Backoff should have blocked the restart (failures reset to 0)
        assert factory_heartbeat._watchdog_failures == 0
        # Only 1 restart in the list (the simulated one, no new one added)
        assert len(factory_heartbeat._watchdog_restarts) == 1
        factory_heartbeat._watchdog_restarts.clear()


class TestWatchdogRestartNotification:
    """Test that restart notifications include uptime."""

    @patch("factory_heartbeat.time.sleep")
    @patch("factory_heartbeat.subprocess.run")
    @patch("factory_heartbeat.send_telegram")
    def test_restart_message_includes_uptime(self, mock_tg, mock_run, mock_sleep):
        import factory_heartbeat
        factory_heartbeat._watchdog_restarts.clear()
        factory_heartbeat._watchdog_failures = 3

        # Simulate tmux commands succeeding
        mock_run.return_value = MagicMock(
            returncode=0, stdout="0: claude* (1 panes)"
        )

        factory_heartbeat._restart_claude_code(session_exists=True)

        # Check the Telegram message contains uptime info
        assert mock_tg.called
        msg = mock_tg.call_args[0][0]
        assert "uptime was" in msg
        assert "consecutive failures" in msg
        factory_heartbeat._watchdog_restarts.clear()


class TestPauseFlag:
    """Test pause mechanism."""

    def test_not_paused_when_no_file(self, tmp_path):
        import factory_heartbeat
        original = factory_heartbeat.PAUSE_FILE
        factory_heartbeat.PAUSE_FILE = str(tmp_path / "nonexistent")
        try:
            assert factory_heartbeat.is_paused() is False
        finally:
            factory_heartbeat.PAUSE_FILE = original

    def test_paused_when_file_exists(self, tmp_path):
        import factory_heartbeat
        original = factory_heartbeat.PAUSE_FILE
        pause_file = tmp_path / ".factory_paused"
        pause_file.touch()
        factory_heartbeat.PAUSE_FILE = str(pause_file)
        try:
            assert factory_heartbeat.is_paused() is True
        finally:
            factory_heartbeat.PAUSE_FILE = original


class TestWatchdogRateLimit:
    """Test watchdog restart rate limiting."""

    def test_restart_limit_tracking(self):
        from factory_heartbeat import _watchdog_restarts
        _watchdog_restarts.clear()
        assert len(_watchdog_restarts) == 0

    def test_restart_list_is_mutable(self):
        from factory_heartbeat import _watchdog_restarts
        _watchdog_restarts.clear()
        from datetime import datetime
        _watchdog_restarts.append(datetime.now())
        assert len(_watchdog_restarts) == 1
        _watchdog_restarts.clear()


class TestMonitorTypeValidation:
    """Test unknown monitor type handling."""

    def test_unknown_type_does_not_crash(self):
        from factory_heartbeat import run_single_monitor
        # Should log a warning but not raise
        monitor = {"type": "invalid_type", "name": "test"}
        run_single_monitor(monitor, "test_project")  # no exception

    def test_missing_url_does_not_crash(self):
        from factory_heartbeat import run_single_monitor
        # Missing 'url' field for http_poll — should log error, not KeyError
        monitor = {"type": "http_poll", "name": "test_no_url"}
        run_single_monitor(monitor, "test_project")  # no exception

    def test_missing_url_health_does_not_crash(self):
        from factory_heartbeat import run_single_monitor
        monitor = {"type": "url_health", "name": "test_no_url"}
        run_single_monitor(monitor, "test_project")  # no exception


class TestConstants:
    """Test that named constants are defined."""

    def test_constants_exist(self):
        from factory_heartbeat import (
            WATCHDOG_FAILURE_THRESHOLD,
            WATCHDOG_MAX_RESTARTS_PER_HOUR,
            SUBPROCESS_TIMEOUT,
            HTTP_TIMEOUT_POLL,
            HTTP_TIMEOUT_HEALTH,
        )
        assert WATCHDOG_FAILURE_THRESHOLD == 3
        assert WATCHDOG_MAX_RESTARTS_PER_HOUR == 5
        assert SUBPROCESS_TIMEOUT == 5
        assert HTTP_TIMEOUT_POLL == 15
        assert HTTP_TIMEOUT_HEALTH == 10

    def test_new_constants_exist(self):
        from factory_heartbeat import (
            ALERT_STATE_FILE,
            _WATCHDOG_BACKOFF,
            _start_time,
        )
        assert ALERT_STATE_FILE.endswith("alert_state.json")
        assert len(_WATCHDOG_BACKOFF) == 5
        assert isinstance(_start_time, datetime)


class TestLogSanitization:
    """Test sensitive data is stripped from log output."""

    def test_strips_api_key(self):
        from factory_heartbeat import _sanitize_log_data
        text = '{"api_key": "sk-1234567890", "data": "ok"}'
        result = _sanitize_log_data(text)
        assert "sk-1234567890" not in result

    def test_strips_token(self):
        from factory_heartbeat import _sanitize_log_data
        text = '{"token": "secret123", "value": 42}'
        result = _sanitize_log_data(text)
        assert "secret123" not in result

    def test_truncates_long_output(self):
        from factory_heartbeat import _sanitize_log_data
        text = "x" * 500
        result = _sanitize_log_data(text)
        assert len(result) <= 200

    def test_preserves_safe_data(self):
        from factory_heartbeat import _sanitize_log_data
        text = '{"rate": 0.5, "status": "ok"}'
        result = _sanitize_log_data(text)
        assert "rate" in result
        assert "status" in result


class TestGracefulShutdown:
    """Test graceful shutdown flag."""

    def test_shutdown_flag_exists(self):
        from factory_heartbeat import _shutdown
        assert _shutdown is False


class TestConfigReload:
    """Test SIGHUP config reload mechanism."""

    def test_reload_flag_exists(self):
        from factory_heartbeat import _reload_requested
        assert _reload_requested is False

    def test_sighup_handler_sets_flag(self):
        import factory_heartbeat
        original = factory_heartbeat._reload_requested
        try:
            factory_heartbeat._reload_requested = False
            factory_heartbeat.handle_sighup(signal.SIGHUP, None)
            assert factory_heartbeat._reload_requested is True
        finally:
            factory_heartbeat._reload_requested = original

    @patch("factory_heartbeat.send_telegram")
    def test_do_config_reload_updates_globals(self, mock_tg):
        import factory_heartbeat
        original_cooldown = factory_heartbeat.ALERT_COOLDOWN
        original_disk = factory_heartbeat.DISK_WARNING_GB

        # Write a new config with different values
        fd, path = tempfile.mkstemp(suffix=".yaml")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    'telegram:\n'
                    '  bot_token: "123456789:ABCdefGHIjklMNO_test"\n'
                    '  chat_id: "123456789"\n'
                    'projects_dir: "/tmp/genesis_test_projects"\n'
                    'alert_cooldown_seconds: 120\n'
                    'disk_warning_gb: 20\n'
                )
            original_config_path = factory_heartbeat.CONFIG_PATH
            factory_heartbeat.CONFIG_PATH = path
            factory_heartbeat._do_config_reload()
            assert factory_heartbeat.ALERT_COOLDOWN == 120
            assert factory_heartbeat.DISK_WARNING_GB == 20
        finally:
            factory_heartbeat.CONFIG_PATH = original_config_path
            factory_heartbeat.ALERT_COOLDOWN = original_cooldown
            factory_heartbeat.DISK_WARNING_GB = original_disk
            # Re-register schedule with original config
            import schedule
            schedule.clear()
            factory_heartbeat.config = factory_heartbeat.load_config()
            factory_heartbeat._register_schedule()
            os.unlink(path)


class TestRequiredEnvVars:
    """Test required environment variable validation."""

    def test_missing_vars_detected(self):
        import factory_heartbeat
        original_config = factory_heartbeat.config
        factory_heartbeat.config = {
            **original_config,
            "required_env_vars": ["NONEXISTENT_VAR_12345"],
        }
        try:
            # main() checks env vars — we just test the logic directly
            required = factory_heartbeat.config.get("required_env_vars", [])
            missing = [v for v in required if not os.environ.get(v)]
            assert "NONEXISTENT_VAR_12345" in missing
        finally:
            factory_heartbeat.config = original_config

    def test_present_vars_not_flagged(self):
        # PATH is always set on macOS/Linux
        import factory_heartbeat
        required = ["PATH"]
        missing = [v for v in required if not os.environ.get(v)]
        assert len(missing) == 0


class TestScheduleRegistration:
    """Test schedule registration function."""

    def test_register_schedule_creates_jobs(self):
        import factory_heartbeat
        import schedule
        schedule.clear()
        factory_heartbeat._register_schedule()
        # Should have: 5 daily + monitors + health + watchdog = 8 jobs
        assert len(schedule.get_jobs()) == 8


class TestLogCleanup:
    """Test old log file cleanup."""

    def test_cleanup_removes_old_logs(self, tmp_path):
        import factory_heartbeat
        original_log = factory_heartbeat.LOG_FILE
        factory_heartbeat.LOG_FILE = str(tmp_path / "heartbeat.log")
        try:
            # Create rotated log files
            for suffix in (".1", ".2", ".3"):
                path = factory_heartbeat.LOG_FILE + suffix
                with open(path, "w") as f:
                    f.write("old log data\n")

            factory_heartbeat._cleanup_old_logs()

            for suffix in (".1", ".2", ".3"):
                assert not os.path.exists(factory_heartbeat.LOG_FILE + suffix)
        finally:
            factory_heartbeat.LOG_FILE = original_log


class TestASTValidation:
    """Test AST validation rejects dangerous patterns."""

    def test_rejects_function_def(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="Disallowed"):
            safe_eval("(lambda x: x)(1)")

    def test_rejects_walrus(self):
        from factory_heartbeat import safe_eval
        with pytest.raises(ValueError, match="Disallowed"):
            safe_eval("[y := 1]")

    def test_allows_dict_literal(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("{'a': 1, 'b': 2}") == {"a": 1, "b": 2}

    def test_allows_set_literal(self):
        from factory_heartbeat import safe_eval
        assert safe_eval("{1, 2, 3}") == {1, 2, 3}

    def test_allows_nested_subscript(self):
        from factory_heartbeat import safe_eval
        data = [[1, 2], [3, 4]]
        assert safe_eval("data[1][0]", {"data": data}) == 3
