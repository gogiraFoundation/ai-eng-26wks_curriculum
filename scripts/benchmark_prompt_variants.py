#!/usr/bin/env python3
"""Day 15: compare system / few-shot / CoT on hold-out invoice fixtures (live Bedrock)."""

from __future__ import annotations

import json
import time
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.config import Config

from extract.invoice_retry import strip_json_noise

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "week02" / "fixtures"
PROMPTS = ROOT / "src" / "prompts" / "invoice"

# Match src/llm_cli/config.py + tools_loop.py (eu-north-1 project Region).
MODEL_ID = "eu.amazon.nova-micro-v1:0"
PROFILE = "agent-toolkit"
REGION = "eu-north-1"
PRICE_IN_PER_1K = 0.000035
PRICE_OUT_PER_1K = 0.00014
MAX_TOKENS = 1024

HOLD_OUT_IDS = ("01", "04", "09")
FIELDS = (
    "invoice_id",
    "invoice_date",
    "vendor",
    "currency",
    "total",
    "line_items",
)


def _dec_str(value: object) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01")))


def normalise(obj: dict) -> dict:
    """Make model JSON comparable to expected/*.json."""
    lines = []
    for item in obj.get("line_items") or []:
        lines.append(
            {
                "description": str(item.get("description", "")).strip(),
                "quantity": int(item["quantity"]),
                "unit_price": _dec_str(item["unit_price"]),
                "total": _dec_str(item["total"]),
            }
        )
    return {
        "invoice_id": str(obj.get("invoice_id", "")).strip(),
        "invoice_date": str(obj.get("invoice_date", "")).strip(),
        "vendor": str(obj.get("vendor", "")).strip(),
        "currency": str(obj.get("currency", "")).strip().upper(),
        "total": _dec_str(obj["total"]) if "total" in obj else "",
        "line_items": lines,
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_few_shot_system() -> str:
    base = (PROMPTS / "few_shot.txt").read_text(encoding="utf-8").strip()
    blocks = [base, "", "Examples:"]
    for cid in HOLD_OUT_IDS:
        inv = (FIXTURES / "invoices" / f"{cid}.txt").read_text(encoding="utf-8").strip()
        exp = (FIXTURES / "expected" / f"{cid}.json").read_text(encoding="utf-8").strip()
        blocks.append(f"\n---\nINPUT:\n{inv}\n\nOUTPUT:\n{exp}")
    return "\n".join(blocks)


def system_for(variant: str) -> str:
    if variant == "few_shot":
        return build_few_shot_system()
    return (PROMPTS / f"{variant}.txt").read_text(encoding="utf-8")


def score_fields(predicted: dict, expected: dict) -> dict[str, bool]:
    p, e = normalise(predicted), normalise(expected)
    return {f: p.get(f) == e.get(f) for f in FIELDS}


def run_benchmark() -> None:
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    client = session.client(
        "bedrock-runtime",
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )

    score_ids = sorted(
        p.stem
        for p in (FIXTURES / "invoices").glob("*.txt")
        if p.stem not in HOLD_OUT_IDS
    )

    print(
        "| Variant | Cases scored | Fields correct / N | Mean in tok | "
        "Mean out tok | Mean latency ms | Est. cost / case |"
    )
    print("|---|---|---|---|---|---|---|")

    for variant in ("system", "few_shot", "cot"):
        system_prompt = system_for(variant)
        hits = {f: 0 for f in FIELDS}
        in_toks: list[int] = []
        out_toks: list[int] = []
        lats: list[float] = []

        for cid in score_ids:
            invoice_text = (FIXTURES / "invoices" / f"{cid}.txt").read_text(encoding="utf-8")
            expected = load_json(FIXTURES / "expected" / f"{cid}.json")

            t0 = time.perf_counter()
            resp = client.converse(
                modelId=MODEL_ID,
                system=[{"text": system_prompt}],
                messages=[
                    {"role": "user", "content": [{"text": f"DOCUMENT:\n{invoice_text}"}]}
                ],
                inferenceConfig={"temperature": 0.0, "maxTokens": MAX_TOKENS},
            )
            wall_ms = (time.perf_counter() - t0) * 1000

            usage = resp["usage"]
            in_toks.append(int(usage["inputTokens"]))
            out_toks.append(int(usage["outputTokens"]))
            lats.append(float(resp.get("metrics", {}).get("latencyMs", wall_ms)))

            raw = resp["output"]["message"]["content"][0]["text"]
            try:
                parsed = json.loads(strip_json_noise(raw))
                for field, ok in score_fields(parsed, expected).items():
                    if ok:
                        hits[field] += 1
            except Exception as exc:
                print(f"[{variant}] {cid} parse failed: {exc}", flush=True)

        n = len(score_ids)
        correct = sum(hits.values())
        possible = n * len(FIELDS)
        mean_in = sum(in_toks) / n
        mean_out = sum(out_toks) / n
        mean_lat = sum(lats) / n
        cost = (mean_in / 1000) * PRICE_IN_PER_1K + (mean_out / 1000) * PRICE_OUT_PER_1K

        print(
            f"| `{variant}` | {n} | {correct}/{possible} "
            f"({100 * correct / possible:.1f}%) | {mean_in:.1f} | {mean_out:.1f} | "
            f"{mean_lat:.0f} | ${cost:.5f} |"
        )
        # Optional field breakdown for day15.md
        parts = " | ".join(f"{hits[f]}/{n}" for f in FIELDS)
        print(f"# fields `{variant}`: {parts}", flush=True)


if __name__ == "__main__":
    run_benchmark()