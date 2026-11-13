
### `notes/week02/day_08/day8.md` (lab log only)

```markdown
# Day 8 lab log: JSON Schema and format failures

**Schema:** `src/schemas/invoice.py`  
**Theory:** [day8_notes.md](./day8_notes.md)  
**Pydantic:** 2.14.3  
**Smoke:** valid sample via `.venv/bin/python src/schemas/invoice.py`

## Task status

- [x] Invoice schema: currency literal, line/invoice totals, `extra="forbid"`
- [x] Observed validation failures + fix idea for each
- [x] Theory notes in [day8_notes.md](./day8_notes.md)

## Smoke (valid)

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
```

## Failure log

| Observed failure | Pydantic signal | Fix idea (pipeline) |
|---|---|---|
| Missing `vendor` | `missing` @ `('vendor',)` | Required in schema; list required keys in prompt; reject before DB |
| `currency: "BTC"` | `literal_error` @ `('currency',)` | `Literal["USD","EUR","GBP"]`; prompt allowed set; retry with error text |
| Line `qty=2`, `unit_price=10`, `total=10` | `value_error` @ `('line_items', 0)` | Validator: `total == qty * unit_price`; retry or recompute on drift |
| Extra `confidence: 0.9` | `extra_forbidden` @ `('confidence',)` | `extra="forbid"`; do not silently drop keys unless a staging model allows it |

## Commands

```bash
.venv/bin/python -m pip install 'pydantic>=2'
.venv/bin/python src/schemas/invoice.py
PYTHONPATH=src .venv/bin/python - <<'PY'
# raw-dict cases + Invoice.model_validate in try/except
PY
```

## Observation

- Eager `LineItem(...)` in a test dict raises before the harness loop; use raw dicts.
- Schema validation ≠ semantic truth (wrong but well-typed vendor still passes).
- Next (Day 9): one retry on parse failure, asserted in unit tests.
```
