#!/usr/bin/env python3
"""Day 20: 3 prompt versions × 2 Nova models over invoice fixtures → CSV + report."""

from __future__ import annotations

import csv
import json
import statistics
import time
import uuid
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from extract.invoice_retry import strip_json_noise
from prompts.loader import load_prompt, render_user

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "week02" / "fixtures"
RUNS_DIR = ROOT / "reports" / "runs"
REPORT_PATH = ROOT / "reports" / "prompt-cost-latency.md"

PROFILE = "agent-toolkit"
REGION = "eu-north-1"
PROMPT_ID = "extract"
VERSIONS = ("v1", "v2", "v3")
HOLD_OUTS = {"01", "04", "09"}
MAX_TOKENS = 1024

# EU inference profiles (IAM: bedrock-invoke-nova). Pricing USD per 1M — cite Bedrock page + date.
MODELS = {
    "micro": {
        "id": "eu.amazon.nova-micro-v1:0",
        "in_1m": 0.038,
        "out_1m": 0.152,
        "cache_read_1m": 0.0095,
        "cache_write_1m": 0.038,
    },
    "lite": {
        "id": "eu.amazon.nova-lite-v1:0",
        "in_1m": 0.065,
        "out_1m": 0.260,
        "cache_read_1m": 0.01625,
        "cache_write_1m": 0.065,
    },
}

FIELDS = (
    "invoice_id",
    "invoice_date",
    "vendor",
    "currency",
    "total",
    "line_items",
)

LOG_COLUMNS = [
    "run_id",
    "prompt_id",
    "prompt_version",
    "model",
    "case_id",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "latency_ms",
    "cost_usd",
    "fields_correct",
    "parse_ok",
]


def _dec_str(value: object) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01")))


def normalise(obj: dict) -> dict:
    """Same contract as scripts/benchmark_prompt_variants.py."""
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


def score_fields(predicted: dict, expected: dict) -> int:
    p, e = normalise(predicted), normalise(expected)
    return sum(1 for f in FIELDS if p.get(f) == e.get(f))


def discover_cases() -> list[dict]:
    cases = []
    for path in sorted((FIXTURES / "invoices").glob("*.txt")):
        cid = path.stem
        if cid in HOLD_OUTS:
            continue
        exp = FIXTURES / "expected" / f"{cid}.json"
        if not exp.is_file():
            continue
        cases.append(
            {
                "case_id": cid,
                "input_text": path.read_text(encoding="utf-8"),
                "expected": json.loads(exp.read_text(encoding="utf-8")),
            }
        )
    return cases


def compute_cost(usage: dict, rates: dict) -> float:
    return (
        int(usage.get("inputTokens", 0)) * rates["in_1m"]
        + int(usage.get("outputTokens", 0)) * rates["out_1m"]
        + int(usage.get("cacheReadInputTokens", 0) or 0) * rates["cache_read_1m"]
        + int(usage.get("cacheWriteInputTokens", 0) or 0) * rates["cache_write_1m"]
    ) / 1_000_000


def run_harness() -> None:
    run_id = str(uuid.uuid4())[:8]
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    client = session.client(
        "bedrock-runtime",
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )
    cases = discover_cases()
    if not cases:
        raise RuntimeError(f"No scored cases under {FIXTURES}")

    print(
        f"run_id={run_id} cases={len(cases)} "
        f"hold_outs={sorted(HOLD_OUTS)} versions={list(VERSIONS)}"
    )

    all_rows: list[dict] = []
    summaries: list[dict] = []

    for model_alias, model_cfg in MODELS.items():
        for version in VERSIONS:
            prompt_spec = load_prompt(PROMPT_ID, version)
            cell_rows: list[dict] = []

            for case in cases:
                user_text = render_user(prompt_spec, document=case["input_text"])
                system_blocks = [{"text": prompt_spec["system"]}]

                t0 = time.perf_counter()
                resp = client.converse(
                    modelId=model_cfg["id"],
                    system=system_blocks,
                    messages=[
                        {"role": "user", "content": [{"text": user_text}]}
                    ],
                    inferenceConfig={
                        "temperature": float(prompt_spec.get("temperature", 0.0)),
                        "maxTokens": int(prompt_spec.get("max_tokens", MAX_TOKENS)),
                    },
                )
                wall_ms = (time.perf_counter() - t0) * 1000
                usage = resp.get("usage") or {}
                latency_ms = float(
                    (resp.get("metrics") or {}).get("latencyMs", wall_ms)
                )
                raw = resp["output"]["message"]["content"][0]["text"]

                parse_ok = False
                fields_correct = 0
                try:
                    parsed = json.loads(strip_json_noise(raw))
                    parse_ok = True
                    fields_correct = score_fields(parsed, case["expected"])
                except Exception:
                    pass

                row = {
                    "run_id": run_id,
                    "prompt_id": PROMPT_ID,
                    "prompt_version": version,
                    "model": model_cfg["id"],
                    "case_id": case["case_id"],
                    "input_tokens": int(usage.get("inputTokens", 0)),
                    "output_tokens": int(usage.get("outputTokens", 0)),
                    "cache_read_tokens": int(
                        usage.get("cacheReadInputTokens", 0) or 0
                    ),
                    "cache_write_tokens": int(
                        usage.get("cacheWriteInputTokens", 0) or 0
                    ),
                    "latency_ms": round(latency_ms, 1),
                    "cost_usd": round(compute_cost(usage, model_cfg), 7),
                    "fields_correct": fields_correct,
                    "parse_ok": parse_ok,
                }
                cell_rows.append(row)
                all_rows.append(row)

            n = len(cell_rows)
            mean_in = statistics.mean(r["input_tokens"] for r in cell_rows)
            mean_out = statistics.mean(r["output_tokens"] for r in cell_rows)
            mean_lat = statistics.mean(r["latency_ms"] for r in cell_rows)
            mean_cost = statistics.mean(r["cost_usd"] for r in cell_rows)
            total_fields = sum(r["fields_correct"] for r in cell_rows)
            max_fields = n * len(FIELDS)
            fields_pct = 100.0 * total_fields / max_fields
            parse_ok_n = sum(1 for r in cell_rows if r["parse_ok"])

            summaries.append(
                {
                    "version": version,
                    "model": model_alias,
                    "mean_in": f"{mean_in:.0f}",
                    "mean_out": f"{mean_out:.0f}",
                    "mean_lat": f"{mean_lat:.0f}",
                    "cost_case": f"${mean_cost:.6f}",
                    "fields_pct": f"{fields_pct:.1f}%",
                    "notes": f"parse_ok {parse_ok_n}/{n}",
                }
            )
            print(
                f"  [{version} | {model_alias:<5}] "
                f"in={mean_in:.0f} out={mean_out:.0f} lat={mean_lat:.0f}ms "
                f"cost/case=${mean_cost:.6f} fields={fields_pct:.1f}%"
            )

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RUNS_DIR / f"{run_id}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    lines = [
        f"# Prompt cost and latency (`run_id: {run_id}`)\n",
        f"- Scored cases: {len(cases)} (hold-outs: `{', '.join(sorted(HOLD_OUTS))}`)",
        f"- Raw CSV: `reports/runs/{run_id}.csv`",
        f"- Region / profile: `{REGION}` / `{PROFILE}`",
        "- Pricing: Nova Micro/Lite eu-north-1 rates in script (confirm on Bedrock pricing page)\n",
        "## Results\n",
        "| Prompt | Model | Mean in | Mean out | Mean lat ms | Cost / case | Fields % | Notes |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for s in summaries:
        lines.append(
            f"| {s['version']} | {s['model']} | {s['mean_in']} | {s['mean_out']} | "
            f"{s['mean_lat']} | {s['cost_case']} | {s['fields_pct']} | {s['notes']} |"
        )
    lines.extend(
        [
            "\n## Recommendation\n",
            "_(Pick the cheapest cell that meets your accuracy bar, e.g. ≥95% fields.)_\n",
            "## Self-check — which variable most moved cost?\n",
            "_(Model unit price micro→lite vs token growth v1→v3 / output size.)_\n",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved:\n  {csv_path}\n  {REPORT_PATH}")


if __name__ == "__main__":
    try:
        run_harness()
    except ClientError as err:
        print("Bedrock error:", err.response["Error"].get("Message", err))