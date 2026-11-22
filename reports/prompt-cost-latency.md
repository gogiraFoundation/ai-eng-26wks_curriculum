# Prompt cost and latency (`run_id: 0c597a3e`)

- Scored cases: 12 (hold-outs: `01, 04, 09`)
- Raw CSV: `reports/runs/0c597a3e.csv`
- Region / profile: `eu-north-1` / `agent-toolkit`
- Pricing: Nova Micro/Lite eu-north-1 rates in script (confirm on Bedrock pricing page)

## Results

| Prompt | Model | Mean in | Mean out | Mean lat ms | Cost / case | Fields % | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| v1 | micro | 132 | 132 | 531 | $0.000025 | 93.1% | parse_ok 12/12 |
| v2 | micro | 149 | 132 | 518 | $0.000026 | 94.4% | parse_ok 12/12 |
| v3 | micro | 159 | 153 | 602 | $0.000029 | 95.8% | parse_ok 12/12 |
| v1 | lite | 132 | 132 | 545 | $0.000043 | 90.3% | parse_ok 12/12 |
| v2 | lite | 149 | 133 | 526 | $0.000044 | 93.1% | parse_ok 12/12 |
| v3 | lite | 159 | 186 | 734 | $0.000059 | 93.1% | parse_ok 12/12 |

## Recommendation

Default to v3 + eu.amazon.nova-micro-v1:0: only cell ≥95% fields (95.8%) at ~$0.000029/case. Lite is ~1.7–2× costlier with equal or worse accuracy. Prefer v2+micro only if you want slightly lower cost/latency and can accept 94.4%.

## Self-check — which variable most moved cost?

_(Model unit price micro→lite vs token growth v1→v3 / output size.)_

Model unit price (micro → lite), not prompt version. v1→v3 adds little input; Lite’s higher $/token (and v3’s extra output on Lite) dominate. Prompt choice mainly moved accuracy (and a bit of latency on v3).