# src/gateway/providers.py
from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator
from typing import Any, Protocol

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import ClientError

from gateway.schemas import ChatMessage, UsageEvent


class StreamProvider(Protocol):
    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        """Yields ('token' | 'usage' | 'error', payload)."""
        ...


def sse_frame(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


class OllamaProvider:
    def __init__(self, base_url: str | None = None) -> None:
        self.url = base_url or os.getenv(
            "OLLAMA_URL", "http://127.0.0.1:11434/api/chat"
        )
        self.default_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        model_id = model or self.default_model
        payload = {
            "model": model_id,
            "messages": [m.model_dump() for m in messages],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream("POST", self.url, json=payload) as resp:
                    try:
                        resp.raise_for_status()
                    except httpx.HTTPStatusError as exc:
                        yield (
                            "error",
                            {"message": f"Ollama HTTP error: {exc.response.status_code}"},
                        )
                        return

                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        chunk = json.loads(line)
                        text = (chunk.get("message") or {}).get("content") or ""
                        if text:
                            yield ("token", {"text": text})
                        if chunk.get("done"):
                            latency_ms = (
                                float(chunk.get("total_duration") or 0) / 1e6
                                or (time.perf_counter() - t0) * 1000
                            )
                            usage = UsageEvent(
                                provider="ollama",
                                model=chunk.get("model") or model_id,
                                input_tokens=int(chunk.get("prompt_eval_count") or 0),
                                output_tokens=int(chunk.get("eval_count") or 0),
                                latency_ms=latency_ms,
                            )
                            yield ("usage", usage.model_dump())
                            return
        except httpx.HTTPError as exc:
            yield ("error", {"message": f"Ollama request failed: {exc}"})


class BedrockProvider:
    """ConverseStream via asyncio.to_thread (boto3 is sync; buffers until done)."""

    def __init__(self) -> None:
        self.profile = os.getenv("AWS_PROFILE", "agent-toolkit")
        self.region = os.getenv("AWS_REGION", "eu-north-1")
        self.default_model = os.getenv(
            "BEDROCK_MODEL", "eu.amazon.nova-micro-v1:0"
        )

    def _collect_events(
        self,
        messages: list[ChatMessage],
        *,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> list[tuple[str, dict[str, Any]]]:
        out: list[tuple[str, dict[str, Any]]] = []
        try:
            session = boto3.Session(
                profile_name=self.profile, region_name=self.region
            )
            client = session.client(
                "bedrock-runtime",
                config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
            )
            system = [{"text": m.content} for m in messages if m.role == "system"]
            converse_messages = [
                {"role": m.role, "content": [{"text": m.content}]}
                for m in messages
                if m.role in ("user", "assistant")
            ]
            kwargs: dict[str, Any] = {
                "modelId": model_id,
                "messages": converse_messages,
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                },
            }
            if system:
                kwargs["system"] = system

            resp = client.converse_stream(**kwargs)
            for event in resp["stream"]:
                if "contentBlockDelta" in event:
                    text = (
                        event["contentBlockDelta"].get("delta", {}).get("text") or ""
                    )
                    if text:
                        out.append(("token", {"text": text}))
                elif "metadata" in event:
                    usage = event["metadata"].get("usage") or {}
                    metrics = event["metadata"].get("metrics") or {}
                    out.append(
                        (
                            "usage",
                            UsageEvent(
                                provider="bedrock",
                                model=model_id,
                                input_tokens=int(usage.get("inputTokens") or 0),
                                output_tokens=int(usage.get("outputTokens") or 0),
                                latency_ms=float(metrics.get("latencyMs") or 0),
                                cache_read_tokens=int(
                                    usage.get("cacheReadInputTokens") or 0
                                ),
                                cache_write_tokens=int(
                                    usage.get("cacheWriteInputTokens") or 0
                                ),
                            ).model_dump(),
                        )
                    )
        except ClientError as exc:
            err = exc.response.get("Error", {})
            out.append(
                (
                    "error",
                    {
                        "message": (
                            f"{err.get('Code', 'ClientError')}: "
                            f"{err.get('Message', str(exc))}"
                        )
                    },
                )
            )
        except Exception as exc:  # noqa: BLE001
            out.append(("error", {"message": str(exc)}))
        return out

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        model_id = model or self.default_model
        events = await asyncio.to_thread(
            self._collect_events,
            messages,
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        for event in events:
            yield event


def get_provider(name: str) -> StreamProvider:
    if name == "ollama":
        return OllamaProvider()
    if name == "bedrock":
        return BedrockProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {name}")

    