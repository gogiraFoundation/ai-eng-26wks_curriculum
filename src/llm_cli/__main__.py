# src/llm_cli/main.py

from __future__ import annotations

import argparse
import sys

from llm_cli.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROVIDER,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
)
from llm_cli.providers import get_provider
from llm_cli.session import Session


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-cli")
    sub = parser.add_subparsers(dest="command", required=True)
    chat = sub.add_parser("chat", help="Interactive chat")
    chat.add_argument("--provider", choices=("direct", "bedrock"), default=DEFAULT_PROVIDER)
    chat.add_argument("--model", default=None)
    chat.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    chat.add_argument("--top-p", type=float, default=DEFAULT_TOP_P)
    chat.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    return parser


def run_chat(args: argparse.Namespace) -> int:
    provider = get_provider(args.provider, args.model)
    session = Session()
    print("llm-cli v0.1  |  /clear  /exit")
    print(f"provider={args.provider}  stream=always")

    while True:
        try:
            user = input("\n>>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user == "/exit":
            break
        if user == "/clear":
            session.clear()
            print("history cleared")
            continue

        session.add_user(user)
        print()
        try:
            for piece in provider.stream(
                session.chat_messages(),
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
            ):
                print(piece, end="", flush=True)
            print()
        except Exception as exc:
            print(f"\n[error] {exc}", file=sys.stderr)
            session.messages.pop()  # drop failed user turn
            continue

        result = provider.last_result
        if result is None:
            continue
        session.add_assistant(result.text)
        session.add_usage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=result.cost_usd,
        )
        print(
            f"[turn] in={result.input_tokens} out={result.output_tokens} "
            f"cost_usd={result.cost_usd:.6f} latency_ms={result.latency_ms:.0f}"
        )
        print(
            f"[session] in={session.input_tokens} out={session.output_tokens} "
            f"cost_usd={session.cost_usd:.6f}"
        )

    print(
        f"session total: in={session.input_tokens} out={session.output_tokens} "
        f"cost_usd={session.cost_usd:.6f}"
    )
    return 0


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "chat":
        raise SystemExit(run_chat(args))


if __name__ == "__main__":
    main()