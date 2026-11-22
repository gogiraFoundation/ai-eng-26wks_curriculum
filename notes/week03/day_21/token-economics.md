
---

### One-pager outline → `notes/week03/day_21/token-economics.md`

```markdown
# Token economics (Week 3)

## In one line

You pay for **tokens processed** (input, output, and sometimes cache write/read). Model price × token mix sets $/request; prompt design and caching change the mix.

## Billable pieces

| Kind | What it is | This week |
|---|---|---|
| Input | Fresh prompt tokens | Uncached Day 17 ~1.7k/call; Day 20 ~130–160 |
| Output | Generated tokens | Often pricier per token than input |
| Cache write | First store of a stable prefix | Day 17: 1,638 once |
| Cache read | Reuse of that prefix | Day 17: ~1,636 × 19 calls; cheaper than full input |

## Evidence

**Day 17 (caching):** uncached cost/1k req **$0.0835** vs cached **$0.0392** (~53% cheaper). Latency p50 almost flat. Layout: long static system → `cachePoint` → short document.

**Day 20 (harness `0c597a3e`):** **model unit price** moved cost more than prompt version. Lite ~1.7–2× Micro cost with worse/equal accuracy. Default: **v3 + Nova Micro** (95.8% fields, ~$0.000029/case).

## PM takeaway

Spend where accuracy moves; do not buy a larger model when a clearer prompt + Micro wins. Cache long stable instructions; keep per-request text after the checkpoint.