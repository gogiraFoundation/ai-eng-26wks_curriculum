# Day 20 notes: prompt library + measurement harness

**Lab log:** [day20.md](./day20.md)  
**Deliverable:** [reports/prompt-cost-latency.md](../../../reports/prompt-cost-latency.md)  
**Code:** `scripts/prompt_harness.py` · `src/prompts/extract/v1.yaml`–`v3.yaml`  
**Run id:** `0c597a3e`

## What this day is for

Week 3 closes by measuring **prompt version × model** on a fixed dataset, then choosing a default for `/extract` from data (accuracy, latency, $/case), not habit.

## Harness design

Reuses:

- Day 15: fixtures, hold-outs `01`/`04`/`09`, field normalisation / scoring  
- Day 18: `load_prompt` + `render_user` (`{{document}}`)  
- Day 17: log columns for `cache_read_tokens` / `cache_write_tokens` (0 unless `cachePoint` is on)

For each cell `(version, model)`: Converse → one CSV row per case → cell means → `reports/runs/<run_id>.csv` + markdown summary.

Matrix: `extract` **v1 / v2 / v3** × Nova **Micro / Lite** (`eu-north-1`).

## Results snapshot (`0c597a3e`)

| Prompt | Model | Mean in | Mean out | Lat ms | Cost / case | Fields % |
|---|---|---|---|---|---|---|
| v1 | micro | 132 | 132 | 531 | $0.000025 | 93.1% |
| v2 | micro | 149 | 132 | 518 | $0.000026 | 94.4% |
| v3 | micro | 159 | 153 | 602 | $0.000029 | 95.8% |
| v1 | lite | 132 | 132 | 545 | $0.000043 | 90.3% |
| v2 | lite | 149 | 133 | 526 | $0.000044 | 93.1% |
| v3 | lite | 159 | 186 | 734 | $0.000059 | 93.1% |

All cells: `parse_ok 12/12`.

## Recommendation

Default: **`v3` + `eu.amazon.nova-micro-v1:0`**. Only cell ≥95% fields (95.8%) at ~$0.000029/case. Lite is ~1.7–2× costlier with equal or worse accuracy. Use `v2`+micro only if you accept 94.4% for slightly lower cost/latency.

## Self-check

**Which variable most moved cost?**

**Model unit price** (micro → lite), not prompt version. v1→v3 adds little input; Lite’s higher $/token (and v3’s extra output on Lite) dominate. Prompt choice mainly moved **accuracy** (and some latency on v3).

## Lessons

1. Measure before upgrading model size: Lite did not buy accuracy here.  
2. Small prompt edits (v2 schema clarity, v3 light CoT) moved fields % more than they moved cost.  
3. Keep pricing constants dated in the harness; re-check [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) when you re-run.  
4. Optional next: enable Day 17 `cachePoint` on a long static system and refill cache columns.