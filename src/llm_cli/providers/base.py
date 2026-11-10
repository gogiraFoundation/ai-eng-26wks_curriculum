from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol


@dataclass
class TurnResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float


class Provider(Protocol):
    def stream(
        self,
        messages: list[dict],
        *,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> Iterator[str]:
        """Yield text deltas. After iteration, ``last_result`` is set."""

    @property
    def last_result(self) -> TurnResult | None: ...