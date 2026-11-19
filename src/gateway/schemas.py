# src/gateway/schemas.py
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatStreamRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    provider: Literal["ollama", "bedrock"] | None = None
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int = 200


class TokenEvent(BaseModel):
    text: str


class UsageEvent(BaseModel):
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


class ErrorEvent(BaseModel):
    message: str
    status_code: int | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    