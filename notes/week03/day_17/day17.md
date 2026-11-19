# Day 17 lab log: prompt caching and token economics

**Syllabus:** Day 17 · Wed 11 Nov 2026 · Prompt caching and token economics  
**Time:** 75 min (20m docs · 40m cached vs uncached over 20 calls · 15m cost per 1k requests)  
**Deliverable:** Table of tokens, cache read/write, latency p50, cost per 1k requests  
**Theory:** [day17_notes.md](./day17_notes.md)  
**Code:** `scripts/benchmark_prompt_cache.py` → `reports/day17/`  
**Region:** `eu-north-1` · model: `eu.amazon.nova-micro-v1:0`  
**Free resources:** [Bedrock prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) · Claude prompt caching docs · [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)

## Task status

- [x] Read Bedrock + Claude prompt caching docs
- [x] Long static instruction block placed first, then a `cachePoint`
- [x] 20 calls uncached vs 20 calls cached (same static prefix)
- [x] Table: tokens, cache read/write, latency p50, cost per 1k requests
- [x] Self-check: what prompt layout maximises cache hits?

## Experiment rules

- Model: `eu.amazon.nova-micro-v1:0`; `temperature=0`; fixed `maxTokens`
- Nova explicit cache: aim ≥ ~1,000 tokens before `{"cachePoint": {"type": "default"}}`
- Vary only the per-call invoice text so the system prefix can hit
- Live Bedrock only; not CI; finish both runs within cache TTL (~5 min)

## Converse shape (cached)

```python
system = [
    {"text": LONG_STATIC_PREFIX},  # rules; aim ≥ 1000 tokens
    {"cachePoint": {"type": "default"}},
]
messages = [{"role": "user", "content": [{"text": f"DOCUMENT:\n{invoice_text}"}]}]
```

Uncached control: same `LONG_STATIC_PREFIX` in `system` without `cachePoint`.

## Results

- Model / temp: `eu.amazon.nova-micro-v1:0` / `0`
- N = 20 per condition
- Artefacts: [benchmark_summary.md](../../../reports/day17/benchmark_summary.md), `benchmark_summary.csv`, `benchmark_telemetry.csv`
- Pricing: rates in `scripts/benchmark_prompt_cache.py` (confirm against Bedrock pricing page + date when you ran)

| Metric | Uncached | Cached |
|---|---|---|
| Fresh input tokens (sum) | 33,789 | 1,031 |
| Cache write tokens (sum) | 0 | 1,638 |
| Cache read tokens (sum) | 0 | 31,120 |
| Output tokens (sum) | 2,544 | 2,551 |
| Latency p50 (ms) | 558 | 587 |
| Cost / 1k requests (USD) | $0.0835 | $0.0392 |

### Reading

- Cached ≈ **53% cheaper** per 1k requests on this pricing.
- Latency p50 almost flat (558 → 587 ms): win is **token economics**, not speed.
- Uncached: every call ~1,680 input tokens (full prefix + document).
- Cached call 1: `write=1638`, `in=51` (prefix stored).
- Cached calls 2–20: `read≈1636`, `write=0`, `in≈40–70` (prefix reused).

### Cost formula used

```text
cost_per_1k = mean_cost_per_call * 1000
```

## Self-check

**What prompt layout maximises cache hits?**

Put a large, **byte-stable** static block first (system rules, schema, examples). Place `cachePoint` immediately after it. Keep per-request content (invoice text) **after** the checkpoint. Do not edit or reorder the static prefix between calls. This run: one write, then consistent reads across 20 varied documents.

## Commands

```bash
bash infra/iam-setup/scripts/auth.sh sign-in
PYTHONPATH=src .venv/bin/python scripts/benchmark_prompt_cache.py
```

