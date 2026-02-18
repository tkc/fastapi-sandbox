import pytest
import structlog.testing

from app.core.constants import (
    LOG_ACTION_ERROR,
    LOG_ACTION_START,
    LOG_ACTION_SUCCESS,
    REDACTED,
)
from app.core.decorators import log_action


class TestLogAction:
    def test_start_and_success_logged(self):
        @log_action()
        def greet(name: str) -> str:
            return f"hello {name}"

        with structlog.testing.capture_logs() as logs:
            result = greet("Alice")

        assert result == "hello Alice"
        events = [entry["event"] for entry in logs]
        assert LOG_ACTION_START in events
        assert LOG_ACTION_SUCCESS in events

    def test_error_logged_on_exception(self):
        @log_action()
        def fail() -> None:
            raise ValueError("boom")

        with structlog.testing.capture_logs() as logs, pytest.raises(ValueError, match="boom"):
            fail()

        events = [entry["event"] for entry in logs]
        assert LOG_ACTION_START in events
        assert LOG_ACTION_ERROR in events

    def test_exception_is_reraised(self):
        @log_action()
        def fail() -> None:
            raise RuntimeError("original")

        with pytest.raises(RuntimeError, match="original"):
            fail()

    def test_functools_wraps_preserves_metadata(self):
        @log_action()
        def my_func() -> None:
            """My docstring."""

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_exclude_args_redacts_values(self):
        @log_action(exclude_args=frozenset({"secret"}))
        def login(user: str, secret: str) -> str:
            return "ok"

        with structlog.testing.capture_logs() as logs:
            login("alice", secret="p@ssw0rd")

        start_entry = next(e for e in logs if e["event"] == LOG_ACTION_START)
        assert start_entry["secret"] == REDACTED
        assert start_entry["user"] == "alice"

    def test_custom_action_name(self):
        @log_action(action_name="custom.op")
        def do_thing() -> None:
            pass

        with structlog.testing.capture_logs() as logs:
            do_thing()

        start_entry = next(e for e in logs if e["event"] == LOG_ACTION_START)
        assert start_entry["action"] == "custom.op"

    def test_result_summary_for_list(self):
        @log_action()
        def get_items() -> list[int]:
            return [1, 2, 3]

        with structlog.testing.capture_logs() as logs:
            get_items()

        success_entry = next(e for e in logs if e["event"] == LOG_ACTION_SUCCESS)
        assert success_entry["result_count"] == 3

    def test_result_summary_for_non_list(self):
        @log_action()
        def get_value() -> str:
            return "hello"

        with structlog.testing.capture_logs() as logs:
            get_value()

        success_entry = next(e for e in logs if e["event"] == LOG_ACTION_SUCCESS)
        assert success_entry["result_type"] == "str"
