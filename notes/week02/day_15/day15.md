# Day 15 Lab Log: System vs. Few-Shot vs. CoT Trade-off

**Topic:** Prompt variants for invoice extraction — accuracy vs. tokens and latency  
**Deliverable:** Field accuracy + mean input/output tokens + latency per variant  
**Code:** `src/prompts/invoice/` + `scripts/benchmark_prompt_variants.py`  
**Theory:** [day15_notes.md](./day15_notes.md)  
**Depends on:** Week 2 fixtures (`tests/week02/fixtures/`) and Bedrock Converse usage logging  

## Task Status

- [ ] Three versioned prompts: `system.txt`, `few_shot.txt`, `cot.txt`
- [ ] Runner over invoices (hold-out IDs `01`, `04`, `09` excluded from scored set)
- [ ] Field-level accuracy scored against `expected/*.json`
- [ ] Log input tokens, output tokens, and latency (`ms`) per call
- [ ] Results table populated below
- [ ] Self-check answered: *When is CoT not worth the output tokens?*

## Experiment Rules

- **Ground truth:** `tests/week02/fixtures/expected/*.json`
- **Controls:** Single Bedrock model; `temperature=0`; identical `maxTokens` across variants
- **Hold-out set:** IDs `01`, `04`, `09` used as few-shot examples and **excluded** from scoring (12 scored cases)
- **Parsing & Accounting:** Reuse `strip_json_noise` / `parse_invoice`; count **all** generated tokens for CoT (including reasoning)
- **Execution:** Live Bedrock only — **do not** add this benchmark runner to CI

## Repository Layout

```text
src/prompts/invoice/
  system.txt
  few_shot.txt
  cot.txt
scripts/
  benchmark_prompt_variants.py
```

## Results

- **Hold-out example IDs:** `01`, `04`, `09`
- **Model / Temperature:** `________________` / `0`

| Variant | Cases Scored | Fields Correct / N | Mean In Tok | Mean Out Tok | Mean Latency (ms) | Est. Cost / Case |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `system` | 12 | | | | | |
| `few_shot` | 12 | | | | | |
| `cot` | 12 | | | | | |

### Field-Level Breakdown (Optional)

| Variant | `invoice_id` | `invoice_date` | `vendor` | `currency` | `total` | `line_items` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `system` | | | | | | |
| `few_shot` | | | | | | |
| `cot` | | | | | | |

## Self-Check

**When is CoT not worth the output tokens?**  
> *(Fill in after the run: e.g., when `system` or `few_shot` already achieves ~95–100% field accuracy on clean/single-line invoices, or when the marginal accuracy gain on edge cases does not justify the 2x–4x output token cost and latency penalty.)*

## Commands

```bash
aws login
PYTHONPATH=src .venv/bin/python scripts/benchmark_prompt_variants.py
```
