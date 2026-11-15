"""Day 4 local LLM client: temperature + optional streaming via Ollama."""

from __future__ import annotations

import argparse
import json
import sys
import time

import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:7b"
KEEP_ALIVE = "10m"
DEFAULT_PROMPT = (
    "Write a single sentence describing a mysterious old key found in an attic, "
    "using highly poetic imagery."
)
DEFAULT_MAX_TOKENS = 200
DEFAULT_TOP_P = 0.9


def ns_to_ms(value: int | None) -> float | None:
    if value is None:
        return None
    return value / 1e6


def build_payload(
    *,
    prompt: str,
    temperature: float,
    stream: bool,
    max_tokens: int,
    top_p: float,
) -> dict:
    return {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens,
        },
    }


def complete(payload: dict, timeout: float = 180.0) -> dict:
    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def stream(payload: dict, timeout: float = 180.0) -> dict:
    """Print tokens as they arrive; return the final Ollama event (usage fields)."""
    with requests.post(
        OLLAMA_URL, json=payload, stream=True, timeout=timeout
    ) as response:
        response.raise_for_status()
        final: dict = {}
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            event = json.loads(line)
            piece = event.get("message", {}).get("content") or ""
            if piece:
                print(piece, end="", flush=True)
            if event.get("done"):
                final = event
                break
        print()
        return final


def print_metrics(result: dict, *, client_elapsed_ms: float) -> None:
    print()
    print(f"model: {MODEL}")
    print(f"input_tokens: {result.get('prompt_eval_count')}")
    print(f"output_tokens: {result.get('eval_count')}")
    print(f"prompt_eval_cached_count: {result.get('prompt_eval_cached_count', 0)}")
    print(f"client_elapsed_ms: {client_elapsed_ms:.0f}")
    total_ms = ns_to_ms(result.get("total_duration"))
    load_ms = ns_to_ms(result.get("load_duration"))
    prompt_ms = ns_to_ms(result.get("prompt_eval_duration"))
    eval_ms = ns_to_ms(result.get("eval_duration"))
    print(f"server_total_ms: {total_ms:.0f}" if total_ms is not None else "server_total_ms: unavailable")
    print(f"load_ms: {load_ms:.0f}" if load_ms is not None else "load_ms: unavailable")
    print(f"prompt_eval_ms: {prompt_ms:.0f}" if prompt_ms is not None else "prompt_eval_ms: unavailable")
    print(f"eval_ms: {eval_ms:.0f}" if eval_ms is not None else "eval_ms: unavailable")
    print("api_charge_usd: 0 (local; electricity not measured)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Ollama chat client (Day 4)")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--top-p", type=float, default=DEFAULT_TOP_P)
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT)
    args = parser.parse_args()

    payload = build_payload(
        prompt=args.prompt,
        temperature=args.temperature,
        stream=args.stream,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
    )

    print(f"temperature: {args.temperature}")
    print(f"stream: {args.stream}")
    print(f"top_p: {args.top_p}")
    print(f"max_tokens: {args.max_tokens}")
    print()

    started = time.perf_counter()
    try:
        if args.stream:
            result = stream(payload)
        else:
            result = complete(payload)
            print(result["message"]["content"])
    except requests.RequestException as exc:
        print(f"Ollama request failed. Is `ollama serve` running?\n{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    client_elapsed_ms = (time.perf_counter() - started) * 1000

    print_metrics(result, client_elapsed_ms=client_elapsed_ms)


if __name__ == "__main__":
    main()