# Day 20 Notes



### Harness Shape 


---

### Harness shape (`scripts/prompt_harness.py`)

Reuse Day 15 scoring + Day 18 `load_prompt` / `render_user`. For each `(version, model)`:

1. Load YAML; override `model` from the matrix (ignore YAML model if you want a clean 2×3).  
2. `converse(system=…, messages=user doc, inferenceConfig={temperature:0, maxTokens:1024})`.  
3. Append one CSV row per case; after each cell, print aggregate means.  
4. Write `reports/runs/<run_id>.csv` and print a markdown summary you can paste into the report.

`cache_*` columns stay `0` until Day 17 caching is wired; still include them in the schema.

---

### Deliverable skeleton `reports/prompt-cost-latency.md`

```markdown
# Prompt cost and latency (Week 3)

**Run id:** …  
**Date:** …  
**Dataset:** 12 invoices (hold-outs 01, 04, 09)  
**Pricing:** Bedrock eu-north-1 Nova Micro/Lite (cite page + date)

## Six-run summary

(paste harness table)

## Recommendation

Pick default prompt+model for `/extract` and why (accuracy vs $/case vs latency).

## Self-check

Which variable most moved cost across the 6 runs?


### Time box
Block	Focus
30m
Schema + v3.yaml + report stub
90m
prompt_harness.py → CSV
40m
Live 6 cells (auth first; watch spend)
20m
Fill report + README excerpt