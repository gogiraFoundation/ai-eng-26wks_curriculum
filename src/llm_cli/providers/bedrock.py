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
        in_tok = out_tok = 0
        latency_ms = 0.0
        response = self.client.converse_stream(**kwargs)
        for event in response["stream"]:
            if "contentBlockDelta" in event:
                piece = event["contentBlockDelta"]["delta"].get("text") or ""
                if piece:
                    text += piece
                    yield piece
            elif "metadata" in event:
                usage = event["metadata"].get("usage", {})
                in_tok = int(usage.get("inputTokens") or 0)
                out_tok = int(usage.get("outputTokens") or 0)
                latency_ms = float(event["metadata"].get("metrics", {}).get("latencyMs") or 0)

        if not latency_ms:
            latency_ms = (time.perf_counter() - started) * 1000
        cost = (in_tok / 1000) * BEDROCK_INPUT_USD_PER_1K + (out_tok / 1000) * BEDROCK_OUTPUT_USD_PER_1K
        self._last = TurnResult(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=cost,
        )