#!/usr/bin/env python3
"""Tests for Genesis Factory Heartbeat."""

import os
import pytest
from datetime import datetime, timedelta


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
