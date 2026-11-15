"""Local Ollama chat smoke test (Week 1 stand-in for Bedrock Converse metrics)."""

from __future__ import annotations

import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:7b"
KEEP_ALIVE = "10m"
PROMPT = "Explain idempotency in a backend API in three sentences."


def ns_to_ms(value: int | None) -> float | None:
    if value is None:
        return None
    return value / 1e6


def main() -> None:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False,
        "keep_alive": KEEP_ALIVE,
        "options": {"temperature": 0, "num_predict": 200},
    }
    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
    except URLError as exc:
        raise SystemExit(
            f"Ollama unreachable at {OLLAMA_URL}. Start `ollama serve` and retry.\n{exc}"
        ) from exc
    client_elapsed_ms = (time.perf_counter() - started) * 1000

    input_tokens = result.get("prompt_eval_count")
    output_tokens = result.get("eval_count")
    load_ms = ns_to_ms(result.get("load_duration"))
    prompt_ms = ns_to_ms(result.get("prompt_eval_duration"))
    eval_ms = ns_to_ms(result.get("eval_duration"))
    server_total_ms = ns_to_ms(result.get("total_duration"))
    cached = result.get("prompt_eval_cached_count", 0)

    print(result["message"]["content"])
    print()
    print(f"model: {MODEL}")
    print(f"input_tokens: {input_tokens}")
    print(f"output_tokens: {output_tokens}")
    print(f"prompt_eval_cached_count: {cached}")
    print(f"client_elapsed_ms: {client_elapsed_ms:.0f}")
    print(f"server_total_ms: {server_total_ms:.0f}" if server_total_ms is not None else "server_total_ms: unavailable")
    print(f"load_ms: {load_ms:.0f}" if load_ms is not None else "load_ms: unavailable")
    print(f"prompt_eval_ms: {prompt_ms:.0f}" if prompt_ms is not None else "prompt_eval_ms: unavailable")
    print(f"eval_ms: {eval_ms:.0f}" if eval_ms is not None else "eval_ms: unavailable")
    print("api_charge_usd: 0 (local; electricity not measured)")


if __name__ == "__main__":
    main()