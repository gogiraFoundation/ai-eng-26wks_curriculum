# Day 15 lab log: system / few-shot / CoT trade-off

**Topic:** Prompt variants for invoice extract — accuracy vs tokens and latency  
**Deliverable:** Field accuracy + mean input/output tokens + latency per variant  
**Code:** `src/prompts/invoice/` + `scripts/benchmark_prompt_variants.py`  
**Theory:** [day15_notes.md](./day15_notes.md)  
**Depends on:** Week 2 fixtures (`tests/week02/fixtures/`) and Bedrock Converse usage logging

## Task status

- [x] Three versioned prompts: `system.txt`, `few_shot.txt`, `cot.txt`
- [x] Runner over invoices (hold-out IDs `01`, `04`, `09` excluded from scored set)
- [x] Field-level accuracy scored against `expected/*.json`
- [x] Log input tokens, output tokens, and latency (ms) per call
- [x] Results table populated below
- [x] Self-check answered: when is CoT not worth the output tokens?

## Experiment rules

- Ground truth: `tests/week02/fixtures/expected/*.json`
- Controls: one Bedrock model; `temperature=0`; same `maxTokens` for all variants
- Hold-outs: `01`, `04`, `09` used as few-shot examples and excluded from scoring (12 scored cases)
- Parsing: `strip_json_noise`; count all CoT output tokens
- Live Bedrock only; do not add this runner to CI

## Layout

```text
src/prompts/invoice/
  system.txt
  few_shot.txt
  cot.txt
scripts/benchmark_prompt_variants.py
```

## Results

- Hold-out example IDs: `01`, `04`, `09`
- Model / temperature: `eu.amazon.nova-micro-v1:0` / `0`
- Cases scored: 12

| Variant | Cases scored | Fields correct / N | Mean in tok | Mean out tok | Mean latency ms | Est. cost / case |
|---|---|---|---|---|---|---|
| `system` | 12 | 66/72 (91.7%) | 173.4 | 132.5 | 620 | $0.00002 |
| `few_shot` | 12 | 71/72 (98.6%) | 710.4 | 130.5 | 572 | $0.00004 |
| `cot` | 12 | 70/72 (97.2%) | 164.4 | 130.9 | 549 | $0.00002 |

### Field-level breakdown

| Variant | `invoice_id` | `invoice_date` | `vendor` | `currency` | `total` | `line_items` |
|---|---|---|---|---|---|---|
| `system` | 11/12 | 12/12 | 12/12 | 12/12 | 12/12 | 7/12 |
| `few_shot` | 11/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| `cot` | 11/12 | 12/12 | 12/12 | 12/12 | 12/12 | 11/12 |

### Reading

- **System:** scalars are strong; `line_items` is the weak spot (7/12).
- **Few-shot:** best overall (71/72); fixes line structure (12/12) at ~4× input tokens and ~2× cost vs system.
- **CoT:** better lines than system (11/12) but behind few-shot; output tokens barely moved (~131), so no classic CoT cost spike and no clear accuracy win on this set.
- Shared miss: all three miss one `invoice_id` (likely the same case).

## Self-check

**When is CoT not worth the output tokens?**

CoT is not worth it when few-shot (or system) already hits high field accuracy on clean invoices. Here few-shot is 98.6% and CoT is 97.2% with similar latency and output size, so extra reasoning adds no useful trade-off. Prefer system for cost on easy layouts; few-shot when `line_items` shape matters; reserve CoT for harder docs where math or conflicting numbers actually move the score.

## Commands

```bash
bash infra/iam-setup/scripts/auth.sh sign-in
PYTHONPATH=src .venv/bin/python scripts/benchmark_prompt_variants.py
```