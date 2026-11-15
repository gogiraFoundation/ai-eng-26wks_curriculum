# src/tools_loop.py
"""Bedrock Converse tool loop: max 5 iterations, print each tool call."""

from __future__ import annotations

import json

import boto3
from botocore.config import Config

MODEL_ID = "eu.amazon.nova-micro-v1:0"
PROFILE = "agent-toolkit"
REGION = "eu-north-1"
MAX_ITERS = 5

TOOLS = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get a fake weather reading for a city.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"},
                        },
                        "required": ["city"],
                    }
                },
            }
        }
    ]
}


def run_tool(name: str, tool_input: dict) -> dict:
    if name == "get_weather":
        city = tool_input.get("city", "unknown")
        return {"city": city, "celsius": 18, "condition": "cloudy"}
    return {"error": f"unknown tool: {name}"}


def main() -> None:
    client = boto3.Session(profile_name=PROFILE, region_name=REGION).client(
        "bedrock-runtime",
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )
    messages: list[dict] = [
        {
            "role": "user",
            "content": [{"text": "What is the weather in Stockholm? Use the tool."}],
        }
    ]

    for i in range(1, MAX_ITERS + 1):
        print(f"\n=== iteration {i} ===")
        resp = client.converse(
            modelId=MODEL_ID,
            messages=messages,
            toolConfig=TOOLS,
            inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        )
        stop = resp["stopReason"]
        assistant = resp["output"]["message"]
        messages.append(assistant)
        print(f"stopReason={stop}")

        if stop == "end_turn":
            for block in assistant.get("content", []):
                if "text" in block:
                    print("assistant:", block["text"])
            break

        if stop != "tool_use":
            print("unexpected stopReason; exiting")
            break

        tool_results = []
        for block in assistant.get("content", []):
            if "toolUse" not in block:
                continue
            tu = block["toolUse"]
            name, tid, inp = tu["name"], tu["toolUseId"], tu.get("input") or {}
            print(f"tool_call name={name} input={json.dumps(inp)}")
            result = run_tool(name, inp)
            print(f"tool_result={json.dumps(result)}")
            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId": tid,
                        "content": [{"json": result}],
                    }
                }
            )
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"hit max iterations ({MAX_ITERS})")


if __name__ == "__main__":
    main()