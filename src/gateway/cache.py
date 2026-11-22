# src/gateway/cache.py
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import redis

PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
CACHE_TTL_S = int(os.getenv("CACHE_TTL_S", "3600"))


def make_cache_key(
    *,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    max_tokens: int,
    prompt_version: str = PROMPT_VERSION,
) -> str:
    payload = {
        "prompt_version": prompt_version,
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    return f"llm:resp:{digest}"


class ResponseCache:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        self._r = redis.Redis.from_url(self.url, decode_responses=True)

    def get(self, key: str) -> dict[str, Any] | None:
        raw = self._r.get(key)
        return json.loads(raw) if raw else None

    def set(self, key: str, value: dict[str, Any], ttl: int = CACHE_TTL_S) -> None:
        self._r.setex(key, ttl, json.dumps(value, ensure_ascii=False))