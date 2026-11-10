from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Session:
    system_prompt: str = "You are a concise CLI assistant."
    messages: list[dict] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    def __post_init__(self) -> None:
        if self.system_prompt:
            self.messages = [{"role": "system", "content": self.system_prompt}]

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})

    def clear(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost_usd = 0.0

    def add_usage(self, *, input_tokens: int, output_tokens: int, cost_usd: float) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cost_usd += cost_usd

    def chat_messages(self) -> list[dict]:
        """Messages suitable for chat APIs (may still include system)."""
        return list(self.messages)