from __future__ import annotations

import json
import time
from typing import Iterator

import requests

from llm_cli.config import (
    DEFAULT_KEEP_ALIVE,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
)
from llm_cli.providers.base import TurnResult


def _reported_count(value: object, fallback: int) -> int:
    """Keep a reported token count of zero. Estimate only when the field is absent."""
    if value is None:
        return fallback
    return int(value)


class OllamaProvider:
    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_MODEL,
        url: str = DEFAULT_OLLAMA_URL,
        keep_alive: str = DEFAULT_KEEP_ALIVE,
    ) -> None:
        self.model = model
        self.url = url
        self.keep_alive = keep_alive
        self._last: TurnResult | None = None

    @property
    def last_result(self) -> TurnResult | None:
        return self._last

    def stream(
        self,
        messages: list[dict],
        *,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> Iterator[str]:
        # Ollama /api/chat: system can be a top-level field; keep simple and pass all roles.
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            },
        }
        started = time.perf_counter()
        text = ""
        final: dict = {}
        with requests.post(self.url, json=payload, stream=True, timeout=180) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                event = json.loads(line)
                piece = event.get("message", {}).get("content") or ""
                if piece:
                    text += piece
                    yield piece
                if event.get("done"):
                    final = event
                    break

        latency_ms = (time.perf_counter() - started) * 1000
        in_tok = _reported_count(
            final.get("prompt_eval_count"),
            max(1, len(str(messages)) // 4),
        )
        out_tok = _reported_count(
            final.get("eval_count"),
            max(1, len(text) // 4),
        )
        self._last = TurnResult(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=0.0,
        )