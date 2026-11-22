# Day 23 lab log: timeouts, retries, backoff with jitter, idempotency

**Syllabus:** Day 23 · Tue 17 Nov 2026 · Timeouts, retries, backoff with jitter, idempotency  
**Time:** 75 min (30m Builders’ Library · 35m wrap calls · 10m idempotency header)  
**Deliverable:** Retry helper + unit test (2 throttles → success); `Idempotency-Key` on non-streaming chat  
**Code:** `src/gateway/resilience.py`, wire into non-stream path; `tests/week04/test_retries.py`  
**Theory:** [day23_notes.md](./day23_notes.md)  
**Free resource:** [Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

## Task status

- [ ] Read Builders’ Library (timeouts, retries, jitter, idempotency)
- [ ] `resilience.py`: per-attempt timeout, capped exp backoff + full jitter
- [ ] Retry only throttling / 5xx (never 4xx client errors)
- [ ] Non-streaming `POST /chat` + `Idempotency-Key` header
- [ ] Unit test: 2 throttles then success; assert attempts + delay bounds
- [ ] Self-check: why jitter; which errors never retry

## Rules of thumb

| Do | Do not |
|---|---|
| Per-attempt timeout | Infinite wait |
| Cap backoff (e.g. 2s) | Unbounded sleep |
| Full jitter: `random(0, cap)` | Sync retries (thundering herd) |
| Retry 429 / 5xx / throttle | Retry 400 / 401 / 403 / 404 / validation |
| Idempotency key on non-stream | Blindly retry after SSE tokens started |

## Commands

```bash
.venv/bin/python -m pip install pytest pytest-asyncio
PYTHONPATH=src .venv/bin/pytest tests/week04/test_retries.py -v