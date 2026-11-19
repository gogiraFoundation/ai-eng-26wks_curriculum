# Day 20 lab log: prompt library + measurement harness

**Syllabus:** Day 20 · Build day: prompt library + measurement harness  
**Time:** 3 h (30m log schema · 90m harness → CSV · 40m 3×2 runs · 20m report)  
**Deliverable:** `reports/prompt-cost-latency.md` comparing 6 runs + recommendation  
**Theory:** [day20_notes.md](./day20_notes.md)  
**Depends on:** Day 15 fixtures, Day 18 `load_prompt`, Bedrock Converse usage

## Task status

- [ ] Log schema designed (see below)
- [ ] Harness: any prompt name+version × model → CSV/JSONL
- [ ] Run 3 versions × 2 models (6 cells)
- [ ] `reports/prompt-cost-latency.md` with table + recommendation
- [ ] Self-check: which variable most moved cost?

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
| `cache_read_tokens` | 0 / null if unused |
| `cache_write_tokens` | 0 / null if unused |
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

## Results (fill after run)

| Prompt | Model | Mean in | Mean out | Mean lat ms | Cost / case | Fields % | Notes |
|---|---|---|---|---|---|---|---|
| v1 | micro | | | | | | |
| v2 | micro | | | | | | |
| v3 | micro | | | | | | |
| v1 | lite | | | | | | |
| v2 | lite | | | | | | |
| v3 | lite | | | | | | |

**Recommendation:** _(one paragraph)_  

**Self-check — which variable most moved cost?**  

> _(after the run: usually model unit price or output tokens; few-shot/v3 input size if that version is much longer)_

## Layout

```text
src/prompts/extract/v1.yaml v2.yaml v3.yaml
scripts/prompt_harness.py
reports/runs/<run_id>.csv
reports/prompt-cost-latency.md


### Commands
bash infra/iam-setup/scripts/auth.sh sign-in
PYTHONPATH=src .venv/bin/python scripts/prompt_harness.py

