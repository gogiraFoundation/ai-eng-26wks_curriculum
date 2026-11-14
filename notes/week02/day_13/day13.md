# Day 13 lab log: extraction service with tests

**Topic:** Build day — synthetic invoices, finish `/extract`, pytest with recorded responses, field accuracy  
**Deliverable:** Accuracy table per field in README (e.g. `total 15/15`, `date 13/15`)  
**Code:** `src/app/`, `src/extract/`, `src/schemas/invoice.py`  
**Theory:** [day13_notes.md](./day13_notes.md)  
**Free resources:** pytest docs; FastAPI docs; Amazon Bedrock tool use  
**Depends on:** Days 8–11 (schema, retry, tool loop, FastAPI skeleton)

## Task status

- [ ] 15 synthetic invoice texts (vary format, currency, missing/noisy fields)
- [ ] `/extract` uses a real or recorded generator (not only the Day 11 fixed stub)
- [ ] Optional: tool loop stub for currency normalisation (GBP/USD/EUR)
- [ ] Pytest suite with **recorded** model responses (no live LLM in CI)
- [ ] Field-level accuracy table on the 15 cases → README
- [ ] Self-check: why record responses (answered in notes)

## Synthetic set (track as you build)

| # | File / id | Currency | Quirk | Notes |
|---|---|---|---|---|
| 1 | | | | |
| … | | | | |
| 15 | | | | |

## Accuracy (fill after eval)

| Field | Correct / 15 | Notes |
|---|---|---|
| `invoice_id` | /15 | |
| `invoice_date` | /15 | |
| `vendor` | /15 | |
| `currency` | /15 | |
| `total` | /15 | |
| `line_items` (structure) | /15 | |

Copy the finished table into the README.

## Results (tests)

| Suite | Command | Outcome |
|---|---|---|
| Retry unit tests | `PYTHONPATH=src .venv/bin/pytest tests/week02/test_invoice_retry.py -v` | |
| Extract / accuracy | `PYTHONPATH=src .venv/bin/pytest tests/week02/test_extract_accuracy.py -v` | |

## Commands

```bash
# keep Day 9 green
PYTHONPATH=src .venv/bin/pytest tests/week02/ -v

# API smoke (generator may still be stub or recorded)
PYTHONPATH=src .venv/bin/uvicorn app:app --app-dir src --reload --port 8000