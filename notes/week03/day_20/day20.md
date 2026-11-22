# Day 20 lab log: prompt library + measurement harness

**Syllabus:** Day 20 · Build day: prompt library + measurement harness  
**Time:** 3 h (30m log schema · 90m harness → CSV · 40m 3×2 runs · 20m report)  
**Deliverable:** `reports/prompt-cost-latency.md` comparing 6 runs + recommendation  
**Theory:** [day20_notes.md](./day20_notes.md)  
**Depends on:** Day 15 fixtures, Day 18 `load_prompt`, Bedrock Converse usage  
**Run id:** `0c597a3e`

## Task status

- [x] Log schema designed (see below)
- [x] Harness: any prompt name+version × model → CSV/JSONL
- [x] Run 3 versions × 2 models (6 cells)
- [x] `reports/prompt-cost-latency.md` with table + recommendation
- [x] Self-check: which variable most moved cost?

## Log schema (one row per call)

| Field | Meaning |
|---|---|
| `run_id` | uuid for the 6-cell batch |
| `prompt_id` | e.g. `extract` |
| `prompt_version` | `v1` / `v2` / `v3` |
| `model` | inference profile id |
| `case_id` | invoice fixture id |
| `input_tokens` | from Converse `usage` |
| `output_tokens` | from Converse `usage` |
| `cache_read_tokens` | 0 if unused |
| `cache_write_tokens` | 0 if unused |
| `latency_ms` | `metrics.latencyMs` or wall clock |
| `cost_usd` | priced from in/out (+ cache if any) |
| `fields_correct` | 0–6 vs `expected/` |
| `parse_ok` | bool |

## Matrix

Hold-outs: `01`, `04`, `09` · temp `0` · scored cases: 12

| Cell | Prompt | Model |
|---|---|---|
| 1 | extract/v1 | nova-micro |
| 2 | extract/v2 | nova-micro |
| 3 | extract/v3 | nova-micro |
| 4 | extract/v1 | nova-lite |
| 5 | extract/v2 | nova-lite |
| 6 | extract/v3 | nova-lite |

## Results

Artefacts: `reports/runs/0c597a3e.csv`, [prompt-cost-latency.md](../../../reports/prompt-cost-latency.md)

| Prompt | Model | Mean in | Mean out | Mean lat ms | Cost / case | Fields % | Notes |
|---|---|---|---|---|---|---|---|
| v1 | micro | 132 | 132 | 531 | $0.000025 | 93.1% | parse_ok 12/12 |
| v2 | micro | 149 | 132 | 518 | $0.000026 | 94.4% | parse_ok 12/12 |
| v3 | micro | 159 | 153 | 602 | $0.000029 | 95.8% | parse_ok 12/12 |
| v1 | lite | 132 | 132 | 545 | $0.000043 | 90.3% | parse_ok 12/12 |
| v2 | lite | 149 | 133 | 526 | $0.000044 | 93.1% | parse_ok 12/12 |
| v3 | lite | 159 | 186 | 734 | $0.000059 | 93.1% | parse_ok 12/12 |

### Recommendation

Default to **`v3` + `eu.amazon.nova-micro-v1:0`**: only cell ≥95% fields (95.8%) at ~$0.000029/case. Lite is ~1.7–2× costlier with equal or worse accuracy. Prefer `v2`+micro only if you want slightly lower cost/latency and can accept 94.4%.

### Self-check — which variable most moved cost?

**Model unit price** (micro → lite), not prompt version. v1→v3 adds little input; Lite’s higher $/token (and v3’s extra output on Lite) dominate. Prompt choice mainly moved accuracy (and some latency on v3).

## Layout

```text
src/prompts/extract/v1.yaml v2.yaml v3.yaml
scripts/prompt_harness.py
reports/runs/<run_id>.csv
reports/prompt-cost-latency.md
```

## Commands

```bash
bash infra/iam-setup/scripts/auth.sh sign-in
PYTHONPATH=src .venv/bin/python scripts/prompt_harness.py
```