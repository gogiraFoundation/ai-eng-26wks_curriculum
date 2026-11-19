# src/gateway/main.py
from __future__ import annotations

import hashlib
import os
from collections.abc import AsyncIterator

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse

from gateway.providers import get_provider, sse_frame
from gateway.resilience import FatalError, RetryableError, with_retries
from gateway.schemas import ChatStreamRequest

app = FastAPI(title="LLM gateway", version="0.1.0")

# Day 23 in-memory idempotency; Day 24 can move to Redis
_IDEMPOTENCY: dict[str, dict] = {}


def _is_retryable_message(msg: str) -> bool:
    lower = msg.lower()
    needles = (
        "429",
        "503",
        "502",
        "504",
        "throttl",
        "too many requests",
        "timeout",
        "timed out",
        "temporarily unavailable",
    )
    return any(n in lower for n in needles)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "default_provider": os.getenv("LLM_PROVIDER", "ollama")}


@app.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest) -> StreamingResponse:
    name = req.provider or os.getenv("LLM_PROVIDER", "ollama")
    try:
        provider = get_provider(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def event_gen() -> AsyncIterator[str]:
        async for kind, payload in provider.stream(
            req.messages,
            model=req.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ):
            yield sse_frame(kind, payload)

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/chat")
async def chat(
    req: ChatStreamRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    body_hash = hashlib.sha256(req.model_dump_json().encode()).hexdigest()
    cache_key = f"{idempotency_key}:{body_hash}" if idempotency_key else None
    if cache_key and cache_key in _IDEMPOTENCY:
        return _IDEMPOTENCY[cache_key]

    name = req.provider or os.getenv("LLM_PROVIDER", "ollama")
    try:
        provider = get_provider(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def once() -> dict:
        text_parts: list[str] = []
        usage: dict | None = None
        async for kind, payload in provider.stream(
            req.messages,
            model=req.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ):
            if kind == "token":
                text_parts.append(payload["text"])
            elif kind == "usage":
                usage = payload
            elif kind == "error":
                msg = str(payload.get("message", "error"))
                if _is_retryable_message(msg):
                    raise RetryableError(msg)
                raise FatalError(msg)
        return {"text": "".join(text_parts), "usage": usage}

    try:
        result = await with_retries(once, max_attempts=3, per_attempt_timeout=60.0)
    except FatalError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (RetryableError, TimeoutError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if cache_key:
        _IDEMPOTENCY[cache_key] = result
    return result