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
        from factory_heartbeat import _should_alert, _alert_state
        _alert_state.clear()
        assert _should_alert("test:first") is True

    def test_repeated_alert_blocked(self):
        from factory_heartbeat import _should_alert, _record_alert, _alert_state
        _alert_state.clear()
        _record_alert("test:repeated")
        assert _should_alert("test:repeated") is False

    def test_alert_after_cooldown(self):
        from factory_heartbeat import _should_alert, _alert_state, ALERT_COOLDOWN
        _alert_state.clear()
        _alert_state["test:expired"] = datetime.now() - timedelta(
            seconds=ALERT_COOLDOWN + 1
        )
        assert _should_alert("test:expired") is True

    def test_different_monitors_independent(self):
        from factory_heartbeat import _should_alert, _record_alert, _alert_state
        _alert_state.clear()
        _record_alert("test:monitorA")
        assert _should_alert("test:monitorA") is False
        assert _should_alert("test:monitorB") is True

    def test_record_updates_timestamp(self):
        from factory_heartbeat import _record_alert, _alert_state
        _alert_state.clear()
        _record_alert("test:ts")
        t1 = _alert_state["test:ts"]
        assert isinstance(t1, datetime)
        assert (datetime.now() - t1).total_seconds() < 2


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
