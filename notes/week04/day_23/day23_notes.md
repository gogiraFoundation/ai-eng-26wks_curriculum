# 

---

### Paste-ready `notes/week04/day_23/day23_notes.md`

```markdown
# Day 23 notes: timeouts, retries, jitter, idempotency

## Why jitter?

Without jitter, every client that fails at the same instant retries at the same delay (2^n). That recreates a load spike (thundering herd). Full jitter spreads retries: `sleep = random(0, min(cap, base * 2^attempt))`.

## Which errors never retry?

- Client / validation: 400, 401, 403, 404, 422
- Permanent model / payload errors
- Anything after a non-idempotent side effect without an idempotency key
- Mid-stream SSE after the first `token` (client already saw partial output)

Retry: throttling (`429`, `ThrottlingException`, `TooManyRequestsException`) and transient 5xx / timeouts.

## Idempotency

`Idempotency-Key` lets the gateway dedupe retries of the same non-streaming request (same key + same body hash → same response). Streaming (`/chat/stream`) stays fire-and-forget for Day 23; retries belong on setup or on `POST /chat`.