# Day 17 notes: prompt caching

**Lab log:** [day17.md](./day17.md)  
**Code:** `scripts/benchmark_prompt_cache.py` · `reports/day17/`

## Idea

Prompt caching stores a repeated **prefix** (system rules, schema, few-shot examples) so later calls pay a **cache-read** rate instead of re-processing the full input. That cuts cost when the same long block is reused across many requests.

## Prompt engineering vs token layout

- **Prompt engineering:** wording of instructions.
- **Cache layout:** which tokens sit **before** the `cachePoint` (stable) vs **after** it (per request).

Wrong layout (editing the static prefix, or putting the invoice before the checkpoint) prevents hits even if the wording is good.

## Nova notes (this project)

- Micro / Lite: explicit caching via Converse `system` + `{"cachePoint": {"type": "default"}}`
- Aim for ≥ ~1,000 tokens in the cached prefix
- TTL is short (~5 minutes): measure in one session
- This run: **one write** (~1,638 tokens), then **reads** on calls 2–20; cost / 1k requests roughly **halved**; latency p50 almost unchanged

## What maximises hits

1. Large, byte-stable system block first  
2. `cachePoint` immediately after it  
3. Only the document / user turn after the checkpoint  
4. Do not shuffle examples or tweak the static text between calls  

## Link to Day 20

Harness schema fields `cache_read_tokens` / `cache_write_tokens` are real after this lab. Use them when a Day 20 cell enables `cachePoint`; otherwise leave them 0.