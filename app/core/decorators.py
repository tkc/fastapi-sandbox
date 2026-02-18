import functools
import inspect
import time
from collections.abc import Callable
from typing import Any

import structlog
from pydantic import BaseModel

from app.core.constants import (
    LOG_ACTION_ERROR,
    LOG_ACTION_START,
    LOG_ACTION_SUCCESS,
    NS_PER_MS,
    REDACTED,
)


def _build_safe_args(
    sig: inspect.Signature,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    exclude_args: frozenset[str],
) -> dict[str, Any]:
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    safe: dict[str, Any] = {}
    for name, value in bound.arguments.items():
        if name == "self":
            continue
        if name in exclude_args:
            safe[name] = REDACTED
        elif isinstance(value, BaseModel):
            safe[name] = f"<{type(value).__name__}>"
        else:
            safe[name] = value
    return safe


def _summarize_result(result: Any) -> dict[str, Any]:
    if result is None:
        return {}
    if isinstance(result, list):
        return {"result_count": len(result)}
    return {"result_type": type(result).__name__}


def log_action(
    *,
    action_name: str | None = None,
    exclude_args: frozenset[str] = frozenset(),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        _action = action_name or getattr(func, "__qualname__", str(func))
        _logger = structlog.stdlib.get_logger(func.__module__)
        _sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = _build_safe_args(_sig, args, kwargs, exclude_args)
            _logger.info(LOG_ACTION_START, action=_action, **bound_args)
            start = time.perf_counter_ns()
            try:
                result = func(*args, **kwargs)
            except Exception:
                duration_ms = (time.perf_counter_ns() - start) / NS_PER_MS
                _logger.exception(
                    LOG_ACTION_ERROR,
                    action=_action,
                    duration_ms=round(duration_ms, 2),
                )
                raise
            duration_ms = (time.perf_counter_ns() - start) / NS_PER_MS
            _logger.info(
                LOG_ACTION_SUCCESS,
                action=_action,
                duration_ms=round(duration_ms, 2),
                **_summarize_result(result),
            )
            return result

        return wrapper

    return decorator
