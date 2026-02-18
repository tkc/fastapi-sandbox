import functools
import inspect
import time
from collections.abc import Callable
from typing import Any

import structlog
from pydantic import BaseModel


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
            safe[name] = "[REDACTED]"
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
        _action = action_name or func.__qualname__
        _logger = structlog.stdlib.get_logger(func.__module__)
        _sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = _build_safe_args(_sig, args, kwargs, exclude_args)
            _logger.info("action.start", action=_action, **bound_args)
            start = time.perf_counter_ns()
            try:
                result = func(*args, **kwargs)
            except Exception:
                duration_ms = (time.perf_counter_ns() - start) / 1_000_000
                _logger.exception(
                    "action.error",
                    action=_action,
                    duration_ms=round(duration_ms, 2),
                )
                raise
            duration_ms = (time.perf_counter_ns() - start) / 1_000_000
            _logger.info(
                "action.success",
                action=_action,
                duration_ms=round(duration_ms, 2),
                **_summarize_result(result),
            )
            return result

        return wrapper

    return decorator
