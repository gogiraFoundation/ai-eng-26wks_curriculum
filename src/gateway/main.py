from __future__ import annotations

import os
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from gateway.providers import get_provider, sse_frame
from gateway.schemas import ChatStreamRequest

app = FastAPI(title="LLM gateway", version="0.1.0")


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

    