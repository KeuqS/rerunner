"""Safe execution stubbing for external agent side-effects (DB writes, Slack, payments)."""

from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from rerunner.cassette import Cassette
from rerunner.models import CassetteEntry

if TYPE_CHECKING:
    from pathlib import Path

F = TypeVar("F", bound=Callable[..., Any])

_ACTIVE_SESSION_CASSETTE: Cassette | None = None
_ACTIVE_MODE: str = "replay"
_ACTIVE_FORK_STEP: int | None = None
_CURRENT_SIDE_EFFECT_STEP: int = 0


def set_active_cassette(
    cassette: Cassette | Path | str | None,
    mode: str = "replay",
    fork_step: int | None = None,
) -> None:
    """Set the active cassette context for side-effect recording and stubbing."""
    global _ACTIVE_SESSION_CASSETTE, _ACTIVE_MODE, _ACTIVE_FORK_STEP, _CURRENT_SIDE_EFFECT_STEP
    _ACTIVE_MODE = mode
    _ACTIVE_FORK_STEP = fork_step
    _CURRENT_SIDE_EFFECT_STEP = 0

    if cassette is None:
        _ACTIVE_SESSION_CASSETTE = None
    elif isinstance(cassette, Cassette):
        _ACTIVE_SESSION_CASSETTE = cassette
    else:
        _ACTIVE_SESSION_CASSETTE = Cassette.load(cassette) if mode == "replay" else Cassette(cassette)


def side_effect(name: str | None = None) -> Callable[[F], F]:
    """Decorator preventing destructive actions (DB writes, webhooks, payments) during replay.

    Example:
        @side_effect(name="charge_customer")
        def charge_credit_card(user_id: str, amount: float) -> str:
            # Only runs on live recording. During replay, returns recorded tx_id safely.
            return stripe.charge(user_id, amount)
    """

    def decorator(func: F) -> F:
        fn_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            global _CURRENT_SIDE_EFFECT_STEP
            _CURRENT_SIDE_EFFECT_STEP += 1
            step = _CURRENT_SIDE_EFFECT_STEP

            should_replay = (
                _ACTIVE_MODE == "replay"
                or (_ACTIVE_MODE == "fork" and _ACTIVE_FORK_STEP is not None and step <= _ACTIVE_FORK_STEP)
            )

            if should_replay and _ACTIVE_SESSION_CASSETTE is not None:
                # Look up recorded side-effect result
                for entry in _ACTIVE_SESSION_CASSETTE.entries:
                    if entry.entry_type == "side_effect" and entry.side_effect_name == fn_name:
                        return entry.side_effect_result

            # Live execution
            result = func(*args, **kwargs)

            if _ACTIVE_SESSION_CASSETTE is not None and _ACTIVE_MODE in ("record", "fork"):
                entry = CassetteEntry(
                    step=step,
                    entry_type="side_effect",
                    side_effect_name=fn_name,
                    side_effect_args=list(args),
                    side_effect_kwargs=kwargs,
                    side_effect_result=result,
                )
                _ACTIVE_SESSION_CASSETTE.append(entry)
                _ACTIVE_SESSION_CASSETTE.save()

            return result

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            global _CURRENT_SIDE_EFFECT_STEP
            _CURRENT_SIDE_EFFECT_STEP += 1
            step = _CURRENT_SIDE_EFFECT_STEP

            should_replay = (
                _ACTIVE_MODE == "replay"
                or (_ACTIVE_MODE == "fork" and _ACTIVE_FORK_STEP is not None and step <= _ACTIVE_FORK_STEP)
            )

            if should_replay and _ACTIVE_SESSION_CASSETTE is not None:
                for entry in _ACTIVE_SESSION_CASSETTE.entries:
                    if entry.entry_type == "side_effect" and entry.side_effect_name == fn_name:
                        return entry.side_effect_result

            result = await func(*args, **kwargs)

            if _ACTIVE_SESSION_CASSETTE is not None and _ACTIVE_MODE in ("record", "fork"):
                entry = CassetteEntry(
                    step=step,
                    entry_type="side_effect",
                    side_effect_name=fn_name,
                    side_effect_args=list(args),
                    side_effect_kwargs=kwargs,
                    side_effect_result=result,
                )
                _ACTIVE_SESSION_CASSETTE.append(entry)
                _ACTIVE_SESSION_CASSETTE.save()

            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return wrapper  # type: ignore[return-value]

    return decorator
