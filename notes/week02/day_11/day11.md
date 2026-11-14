# Day 11 lab log: FastAPI service skeleton

**Topic:** Request/response models, `/extract`, 422 on unrecoverable output, structured JSON logging  
**Deliverable:** `uvicorn app:app` works locally; curl example in app README  
**Code:** `src/app/` (`app:app` via `src/app/__init__.py`)  
**Reuses:** `src/schemas/invoice.py`, `src/extract/invoice_retry.py`  
**Theory:** [day11_notes.md](./day11_notes.md)  
**Free resources:** [FastAPI docs](https://fastapi.tiangolo.com/), [Pydantic docs](https://docs.pydantic.dev/)

## Task status

- [x] FastAPI app with Pydantic request/response models
- [x] `POST /extract` calling `extract_with_retry` (stub `generate_fn`)
- [x] HTTP 422 path coded for exhausted retry (`HTTPException`); body errors use FastAPI 422
- [x] Structured JSON logs: `request_id`, `retries`
- [ ] Curl example copied into `src/app/app.md` / README
- [x] Self-check: why log a request id (see [day11_notes.md](./day11_notes.md))

## Results

| Check | Command / evidence | Pass? |
|---|---|---|
| Server starts | `PYTHONPATH=src .venv/bin/uvicorn app:app --app-dir src --reload --port 8000` | yes |
| Happy path | curl → 200 + stub invoice JSON | yes |
| `GET /` | 404 (no root route; use `/extract` or `/docs`) | expected |
| Logs | uvicorn shows `extract_ok` with `request_id` + `retries` | confirm in server terminal |
| Body 422 | `POST` with `{}` → FastAPI 422 | optional / fill when run |

Happy-path response:

```json
{
  "invoice_id": "INV-1001",
  "invoice_date": "2026-11-13",
  "vendor": "Acme Inc.",
  "currency": "USD",
  "total": "100.00",
  "line_items": [
    {
      "description": "Product A",
      "quantity": 1,
      "unit_price": "100.00",
      "total": "100.00"
    }
  ]
}