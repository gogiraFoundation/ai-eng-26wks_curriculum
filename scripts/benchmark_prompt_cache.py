#!/usr/bin/env python3
"""Day 17: Bedrock prompt cache vs uncached (Nova Micro, eu-north-1)."""

from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "day17"
FIXTURES = ROOT / "tests" / "week02" / "fixtures" / "invoices"

PROFILE = "agent-toolkit"
REGION = "eu-north-1"
MODEL_ID = "eu.amazon.nova-micro-v1:0"

# Document source/date in day17.md — rates USD per token (Nova Micro eu-north-1 ballpark).
# Prefer latest from https://aws.amazon.com/bedrock/pricing/
PRICE = {
    "input": 0.038 / 1_000_000,
    "output": 0.152 / 1_000_000,
    "cache_write": 0.038 / 1_000_000,   # confirm; often ~input or a write multiplier
    "cache_read": 0.0095 / 1_000_000,  # confirm cache-read rate for your Region
}

# Long static prefix (≥ ~1000 tokens for Nova checkpoint). Stable across calls.
STATIC_SYSTEM = (
    "You extract invoices into one JSON object only. No markdown fences.\n"
    "Required keys: invoice_id, invoice_date (YYYY-MM-DD), vendor, currency (USD|EUR|GBP),\n"
    "total (decimal string), line_items[{description, quantity, unit_price, total}].\n"
    + ("Always validate totals, prefer ISO dates, never invent vendors. " * 120)
)

N_CALLS = 20
MAX_TOKENS = 256


def invoice_texts() -> list[tuple[str, str]]:
    paths = sorted(FIXTURES.glob("*.txt"))
    if not paths:
        raise FileNotFoundError(FIXTURES)
    # Cycle fixtures to get N_CALLS documents
    out: list[tuple[str, str]] = []
    i = 0
    while len(out) < N_CALLS:
        p = paths[i % len(paths)]
        out.append((p.stem, p.read_text(encoding="utf-8")))
        i += 1
    return out


def system_blocks(cached: bool) -> list[dict]:
    blocks: list[dict] = [{"text": STATIC_SYSTEM}]
    if cached:
        blocks.append({"cachePoint": {"type": "default"}})
    return blocks


def one_call(client, *, cached: bool, document: str) -> dict:
    t0 = time.perf_counter()
    resp = client.converse(
        modelId=MODEL_ID,
        system=system_blocks(cached),
        messages=[
            {
                "role": "user",
                "content": [{"text": f"DOCUMENT:\n{document}"}],
            }
        ],
        inferenceConfig={"temperature": 0.0, "maxTokens": MAX_TOKENS},
    )
    wall_ms = (time.perf_counter() - t0) * 1000
    usage = resp.get("usage") or {}
    lat = float((resp.get("metrics") or {}).get("latencyMs", wall_ms))
    return {
        "input": int(usage.get("inputTokens", 0)),
        "output": int(usage.get("outputTokens", 0)),
        "cache_write": int(usage.get("cacheWriteInputTokens", 0) or 0),
        "cache_read": int(usage.get("cacheReadInputTokens", 0) or 0),
        "latency_ms": lat,
    }


def run_mode(client, mode: str, docs: list[tuple[str, str]]) -> dict:
    cached = mode == "cached"
    print(f"\n[{mode}] {len(docs)} calls (cached={cached})")
    logs = []
    totals = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    lats: list[float] = []

    for i, (case_id, text) in enumerate(docs, start=1):
        r = one_call(client, cached=cached, document=text)
        for k in totals:
            totals[k] += r[k]
        lats.append(r["latency_ms"])
        logs.append(
            {
                "mode": mode,
                "call": i,
                "case_id": case_id,
                "input_tokens": r["input"],
                "output_tokens": r["output"],
                "cache_write_tokens": r["cache_write"],
                "cache_read_tokens": r["cache_read"],
                "latency_ms": round(r["latency_ms"], 1),
            }
        )
        if i in (1, 2, 10, 20):
            print(
                f"  {i:02d} case={case_id} lat={r['latency_ms']:.0f}ms "
                f"in={r['input']} write={r['cache_write']} read={r['cache_read']} out={r['output']}"
            )

    n = len(docs)
    cost = (
        totals["input"] * PRICE["input"]
        + totals["cache_write"] * PRICE["cache_write"]
        + totals["cache_read"] * PRICE["cache_read"]
        + totals["output"] * PRICE["output"]
    )
    return {
        "mode": mode,
        "totals": totals,
        "latency_p50": statistics.median(lats),
        "cost_run": cost,
        "cost_per_1k": (cost / n) * 1000,
        "logs": logs,
    }


def export(results: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    u, c = results[0], results[1]
    headers = ["Metric", "Uncached", "Cached"]
    rows = [
        ["Fresh input tokens (sum)", f"{u['totals']['input']:,}", f"{c['totals']['input']:,}"],
        ["Cache write tokens (sum)", f"{u['totals']['cache_write']:,}", f"{c['totals']['cache_write']:,}"],
        ["Cache read tokens (sum)", f"{u['totals']['cache_read']:,}", f"{c['totals']['cache_read']:,}"],
        ["Output tokens (sum)", f"{u['totals']['output']:,}", f"{c['totals']['output']:,}"],
        ["Latency p50 (ms)", f"{u['latency_p50']:.0f}", f"{c['latency_p50']:.0f}"],
        ["Cost / 1k requests (USD)", f"${u['cost_per_1k']:.4f}", f"${c['cost_per_1k']:.4f}"],
    ]

    md = OUT_DIR / "benchmark_summary.md"
    with md.open("w", encoding="utf-8") as f:
        f.write("# Day 17 prompt caching (Nova Micro)\n\n")
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| :--- | ---: | ---: |\n")
        for row in rows:
            f.write("| " + " | ".join(row) + " |\n")

    with (OUT_DIR / "benchmark_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)

    logs = [e for r in results for e in r["logs"]]
    with (OUT_DIR / "benchmark_telemetry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(logs[0].keys()))
        w.writeheader()
        w.writerows(logs)

    print(f"\nWrote {md}")
    print(f"Wrote {OUT_DIR / 'benchmark_summary.csv'}")
    print(f"Wrote {OUT_DIR / 'benchmark_telemetry.csv'}")


def main() -> None:
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    client = session.client(
        "bedrock-runtime",
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )
    docs = invoice_texts()
    try:
        # Uncached first, then cached (same static prefix + cachePoint)
        results = [
            run_mode(client, "uncached", docs),
            run_mode(client, "cached", docs),
        ]
        export(results)
        print("\nPaste the markdown table into notes/week03/day_17/day17.md")
    except ClientError as err:
        print("Bedrock error:", err.response["Error"].get("Message", err))


if __name__ == "__main__":
    main()