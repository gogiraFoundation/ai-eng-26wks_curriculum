# tests/week04/test_retries.py
from __future__ import annotations

import pytest

from gateway.resilience import RetryableError, full_jitter_delay, with_retries


def test_full_jitter_bounds():
    for attempt in range(6):
        d = full_jitter_delay(attempt, base=0.05, cap=2.0)
        assert 0.0 <= d <= min(2.0, 0.05 * (2**attempt))


@pytest.mark.asyncio
async def test_two_throttles_then_success():
    calls = {"n": 0}
    sleeps: list[float] = []

    async def flaky():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise RetryableError("ThrottlingException")
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    result = await with_retries(
        flaky,
        max_attempts=3,
        per_attempt_timeout=1.0,
        base=0.05,
        cap=2.0,
        sleep=fake_sleep,
    )

    assert result == "ok"
    assert calls["n"] == 3  # 2 failures + 1 success
    assert len(sleeps) == 2
    assert all(0.0 <= s <= 2.0 for s in sleeps)
    # attempt 0 ceiling = 0.05; attempt 1 ceiling = 0.10
    assert sleeps[0] <= 0.05
    assert sleeps[1] <= 0.10