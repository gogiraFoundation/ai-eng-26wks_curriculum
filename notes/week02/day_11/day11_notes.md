
# Day 11 notes: FastAPI extract skeleton

**Lab log:** [day11.md](./day11.md)  
**Week 2 goal:** FastAPI `/extract` with Pydantic + retry (full accuracy table is Day 13)

## What to build

| Piece | Role |
|---|---|
| Request model | e.g. `ExtractRequest(text: str)` — body FastAPI validates automatically |
| `POST /extract` | Call `extract_with_retry(text, generate_fn)` |
| Response | Return `Invoice` (Pydantic serialises dates/Decimals) |
| 422 | Raise `HTTPException(status_code=422, detail=...)` when retry is exhausted |
| Logging | One JSON log per request: `request_id`, `retries`, optional token fields |

Request-body mistakes (missing `text`) already yield FastAPI’s built-in **422**. Day 11’s extra 422 is for **model output** that still fails after Day 9’s single retry.

## Self-check: why log a request id?

So you can **correlate** one client call across logs (handler → generate → retry → response) without grepping timestamps. When tokens or latency look wrong, the same `request_id` ties the story together for debugging and later observability (Day 13+).

## Stub vs real model

For the skeleton, `generate_fn` can return fixed valid JSON derived from nothing fancy, or alternate bad→good to prove retries in logs. Wire Bedrock/Ollama on Day 13 if needed; keep Day 11 focused on HTTP + logging.

## Status

- [ ] Notes (this file)
- [ ] `app:app` + `/extract`
- [ ] curl in README

curl -sS -X POST 'http://127.0.0.1:8000/extract' \
  -H 'Content-Type: application/json' \
  -d '{"text":"Invoice INV-1 from Acme for 100.00 USD"}'



- [ ] Lab evidence in [day11.md](./day11.md)