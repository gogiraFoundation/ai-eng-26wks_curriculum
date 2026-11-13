from __future__ import annotations

import time
from typing import Iterator

import boto3
from botocore.config import Config

from llm_cli.config import (
    BEDROCK_INPUT_USD_PER_1K,
    BEDROCK_OUTPUT_USD_PER_1K,
    DEFAULT_AWS_PROFILE,
    DEFAULT_AWS_REGION,
    DEFAULT_BEDROCK_MODEL,
)
from llm_cli.providers.base import TurnResult


class BedrockProvider:
    def __init__(
        self,
        model: str = DEFAULT_BEDROCK_MODEL,
        profile: str = DEFAULT_AWS_PROFILE,
        region: str = DEFAULT_AWS_REGION,
    ) -> None:
        self.model = model
        session = boto3.Session(profile_name=profile, region_name=region)
        self.client = session.client(
            "bedrock-runtime",
            config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
        )
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
        system = [{"text": m["content"]} for m in messages if m["role"] == "system"]
        converse_messages = [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages
            if m["role"] in ("user", "assistant")
        ]
        kwargs: dict = {
            "modelId": self.model,
            "messages": converse_messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p,
            },
        }
        if system:
            kwargs["system"] = system

        started = time.perf_counter()
        text = ""
        in_tok: int | None = None
        out_tok: int | None = None
        latency_ms: float | None = None
        response = self.client.converse_stream(**kwargs)
        for event in response["stream"]:
            if "contentBlockDelta" in event:
                piece = event["contentBlockDelta"]["delta"].get("text") or ""
                if piece:
                    text += piece
                    yield piece
            elif "metadata" in event:
                # Usage arrives on a terminal metadata event, not with text deltas.
                usage = event["metadata"].get("usage") or {}
                if "inputTokens" in usage:
                    in_tok = int(usage["inputTokens"])
                if "outputTokens" in usage:
                    out_tok = int(usage["outputTokens"])
                metrics = event["metadata"].get("metrics") or {}
                if "latencyMs" in metrics:
                    latency_ms = float(metrics["latencyMs"])

        # Stream ends when the event iterator is exhausted; last_result is set below.
        if latency_ms is None:
            latency_ms = (time.perf_counter() - started) * 1000
        if in_tok is None:
            # Estimate only when Bedrock omitted usage; keep a reported zero.
            in_tok = max(1, len(str(messages)) // 4)
        if out_tok is None:
            out_tok = max(1, len(text) // 4) if text else 0
        cost = (in_tok / 1000) * BEDROCK_INPUT_USD_PER_1K + (out_tok / 1000) * BEDROCK_OUTPUT_USD_PER_1K
        self._last = TurnResult(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=cost,
        )