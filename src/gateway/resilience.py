# src/gateway/resilience.py
from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RetryableError(Exception):
    """Transient failure worth retrying (throttle / 5xx / timeout)."""


class FatalError(Exception):
    """Do not retry (4xx / validation / auth)."""


def full_jitter_delay(attempt: int, *, base: float = 0.05, cap: float = 2.0) -> float:
    """Builders’ Library full jitter: sleep ∈ [0, min(cap, base * 2^attempt)]."""
    ceiling = min(cap, base * (2**attempt))
    return random.uniform(0.0, ceiling)


async def with_retries(
    op: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    per_attempt_timeout: float = 30.0,
    base: float = 0.05,
    cap: float = 2.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    last: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            return await asyncio.wait_for(op(), timeout=per_attempt_timeout)
        except FatalError:
            raise
        except (RetryableError, TimeoutError, asyncio.TimeoutError) as exc:
            last = exc
            if attempt >= max_attempts - 1:
                break
            await sleep(full_jitter_delay(attempt, base=base, cap=cap))
    assert last is not None
    raise last