
# Day 9 lab log: validation + retry on parse failure

**Topic:** Validate model JSON with Pydantic; on failure, retry once with the error  
**Deliverable:** Unit tests inject malformed JSON and assert exactly one retry fixes it  
**Code:** `src/extract/invoice_retry.py`  
**Tests:** `tests/week02/test_invoice_retry.py`  
**Schema:** `src/schemas/invoice.py`  
**Theory:** [day_09_notes.md](./day_09_notes.md)  
**Pytest:** 9.2.0 · **Pydantic:** 2.14.3

## Task status

- [x] `parse_invoice`: strip noise → `json.loads` → `Invoice.model_validate`
- [x] `extract_with_retry`: at most one retry; second prompt includes `ERROR:` + previous output
- [x] `test_one_retry_fixes_malformed_json` — first bad, second valid → `retries == 1`
- [x] `test_exhausted_retries_raise` — two bad → raises; no unbounded loop
- [x] Results recorded below

## Results

| Test | First payload | Second payload | Retries | Outcome |
|---|---|---|---:|---|
| `test_one_retry_fixes_malformed_json` | `{'vendor': 'Acme'}` (invalid JSON) | valid invoice JSON | 1 | PASSED |
| `test_exhausted_retries_raise` | `{not json` | `{not json` | 1 (then raise) | PASSED |

```text
2 passed in 0.06s
```

## Commands

```bash
.venv/bin/python -m pip install pytest pydantic
PYTHONPATH=src .venv/bin/pytest tests/week02/test_invoice_retry.py -v
```

## Observation

- Retry belongs around **generate + parse**, not re-validating the same string.
- Fake `generate_fn` keeps tests offline (no Bedrock/Ollama).
- Day 8 failure modes feed the repair prompt via `format_parse_error`.
- Next (Day 10): Bedrock tool-use loop in `src/tools_loop.py`.
```