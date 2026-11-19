# Day 22 lab log: async I/O and SSE streaming

**Syllabus:** Day 22 · Mon 16 Nov 2026 · Async I/O and SSE streaming  
**Time:** 75 min (25m asyncio + MDN SSE · 40m FastAPI stream · 10m `curl -N`)  
**Deliverable:** `POST /chat/stream` → SSE `token` events, final `usage` (or `error`)  
**Code:** `src/gateway/`  
**Theory:** [day22_notes.md](./day22_notes.md)  
**Default provider today:** Ollama `qwen2.5:7b` · Bedrock adapter ready for later  
**Free resources:** [asyncio](https://docs.python.org/3/library/asyncio.html) · [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) · [FastAPI](https://fastapi.tiangolo.com/)

## Task status

- [ ] Read asyncio (tasks/timeouts) + MDN SSE
- [ ] `schemas.py` / `providers.py` / `main.py`
- [ ] Ollama stream via `httpx.AsyncClient` (`stream: true`, NDJSON)
- [ ] SSE frames: `event: token` … then `event: usage`
- [ ] `curl -N` smoke test
- [ ] Optional: offline pytest with mocks
- [ ] Self-check: SSE vs WebSockets

## SSE contract

```text
event: token
data: {"text":"<chunk>"}

event: usage
data: {"provider":"ollama","model":"qwen2.5:7b","input_tokens":N,"output_tokens":N,"latency_ms":N}

event: error
data: {"message":"..."}


### layout
src/gateway/
  __init__.py
  schemas.py
  providers.py
  main.py
tests/week04/test_gateway_streaming.py   # optional Day 22


ollama pull qwen2.5:7b
.venv/bin/python -m pip install httpx 'fastapi[standard]'
LLM_PROVIDER=ollama PYTHONPATH=src .venv/bin/uvicorn gateway.main:app --reload --port 8000

curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Say hello in five words."}]}'


Self-check
How does SSE differ from WebSockets for token streaming?

SSE is one-way (server → client) over normal HTTP (text/event-stream), easy with load balancers and curl -N, with browser reconnect/Last-Event-ID. WebSockets are full-duplex after an HTTP upgrade, better for mid-stream client control or binary/voice, but heavier ops. For “one prompt → stream tokens + usage”, SSE fits.

