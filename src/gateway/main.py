# src/gateway/main.py
from __future__ import annotations

import hashlib
import logging
import os
from collections.abc import AsyncIterator

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse

from gateway.cache import ResponseCache, make_cache_key
from gateway.providers import get_provider, sse_frame
from gateway.resilience import FatalError, RetryableError, with_retries
from gateway.schemas import ChatStreamRequest

logger = logging.getLogger("gateway")
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI(title="LLM gateway", version="0.1.0")

# Day 23: request idempotency (client retries of the same write)
_IDEMPOTENCY: dict[str, dict] = {}

# Day 24: Redis response cache (shared across clients)
_cache: ResponseCache | None = None


def _get_cache() -> ResponseCache:
    global _cache
    if _cache is None:
        _cache = ResponseCache()
    return _cache


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


def _primary_model(provider: str, override: str | None) -> str:
    if override:
        return override
    if provider == "bedrock":
        return os.getenv("BEDROCK_MODEL", "eu.amazon.nova-micro-v1:0")
    return os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


def _fallback_model(provider: str) -> str:
    if provider == "bedrock":
        return os.getenv(
            "BEDROCK_FALLBACK_MODEL",
            os.getenv("BEDROCK_MODEL", "eu.amazon.nova-micro-v1:0"),
        )
    return os.getenv(
        "OLLAMA_FALLBACK_MODEL",
        os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    )


async def _collect_chat(
    provider_name: str,
    req: ChatStreamRequest,
    *,
    model: str,
) -> dict:
    provider = get_provider(provider_name)

    async def once() -> dict:
        text_parts: list[str] = []
        usage: dict | None = None
        async for kind, payload in provider.stream(
            req.messages,
            model=model,
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
        return {"text": "".join(text_parts), "usage": usage, "model_used": model}

    return await with_retries(once, max_attempts=3, per_attempt_timeout=60.0)


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
    # --- Day 23 idempotency (same key + same body) ---
    body_hash = hashlib.sha256(req.model_dump_json().encode()).hexdigest()
    idem_key = f"{idempotency_key}:{body_hash}" if idempotency_key else None
    if idem_key and idem_key in _IDEMPOTENCY:
        return _IDEMPOTENCY[idem_key]

    name = req.provider or os.getenv("LLM_PROVIDER", "ollama")
    try:
        get_provider(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    primary = _primary_model(name, req.model)
    messages = [m.model_dump() for m in req.messages]
    use_cache = req.temperature == 0.0
    resp_key = (
        make_cache_key(
            model=primary,
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        if use_cache
        else None
    )

    # --- Day 24 Redis response cache ---
    if resp_key:
        try:
            cached = _get_cache().get(resp_key)
        except Exception as exc:  # noqa: BLE001
            logger.warning("redis_get_failed err=%s", exc)
            cached = None
        if cached is not None:
            logger.info(
                "cache_hit=true model_used=%s fallback=false",
                cached.get("model_used", primary),
            )
            if idem_key:
                _IDEMPOTENCY[idem_key] = cached
            return cached

    fallback_used = False
    try:
        result = await _collect_chat(name, req, model=primary)
    except FatalError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (RetryableError, TimeoutError):
        # repeated throttle / timeout → cheaper (or alternate) model
        fb = _fallback_model(name)
        try:
            result = await _collect_chat(name, req, model=fb)
            fallback_used = True
        except FatalError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (RetryableError, TimeoutError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    logger.info(
        "cache_hit=false model_used=%s fallback=%s",
        result.get("model_used", primary),
        str(fallback_used).lower(),
    )

    if resp_key:
        try:
            _get_cache().set(resp_key, result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("redis_set_failed err=%s", exc)

    if idem_key:
        _IDEMPOTENCY[idem_key] = result
    return result