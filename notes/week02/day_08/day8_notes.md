
### `notes/week02/day_08/day8_notes.md`

```markdown
# Day 8 notes: JSON Schema and why models break format

**Deliverable:** `src/schemas/invoice.py` plus a failure log with observed breaks and a fix idea for each  
**Lab log:** [day8.md](./day8.md)  
**Week 2 goal:** FastAPI `/extract` with Pydantic validation, retry-on-parse-failure, and tests  
**Exam link:** 2.2.8 (task-specific prompt engineering), 3.3.9 (prompt testing)

## What JSON Schema is

JSON Schema is a declarative vocabulary (itself written in JSON) that defines, documents, and validates the structure, types, and constraints of JSON data. In software pipelines it is a contract: reject or repair payloads that do not match before the app trusts them.

Language models do not treat that contract as law. Generation is probabilistic. Unless the decoder is constrained, JSON shape is only a statistical preference.

## What a schema enforces

| Concern | Typical keywords | Effect |
|---|---|---|
| Types | `type` | Value must be string, integer, number, boolean, object, or array |
| Required keys | `required` | Named properties cannot be omitted |
| Value limits | `enum`, `minimum` / `maximum`, `pattern` | Fixed options, numeric bounds, regex for strings |
| Nesting | `properties`, `items`, `$ref` | Nested objects and array element rules |

Useful for LLM outputs: `additionalProperties: false` (Pydantic `extra="forbid"`), clear property names, shallow nesting.

## Why models break JSON

1. **Probabilistic sampling** — without grammar-level constraints, valid JSON is a learned habit; larger schemas raise drift risk.
2. **Wrappers and syntax noise** — markdown fences, preamble text, trailing commas, comments, unescaped quotes, Python literals (`True`, `None`).
3. **JSON mode ≠ schema compliance** — syntactic JSON only; required keys, types, and enums are not guaranteed.
4. **Token-limit truncation** — `max_tokens` cuts mid-object; unclosed brackets.
5. **Weak schema / naming** — ambiguous fields or deep nesting encourage structural hallucination.
6. **Semantic failure** — valid JSON can still hold wrong totals, dates, or vendors. Validation is necessary, not sufficient.

## How to prevent format breaks (Week 2 stack)

| Layer | What to do | Role this week |
|---|---|---|
| Schema | Pydantic models for invoice fields | `src/schemas/invoice.py` |
| Prompt | Descriptive names, shallow shape | Task-specific prompting |
| Decode / API | Prefer structured outputs / tool schemas; do not rely on JSON mode alone | Bedrock tool use (Day 10) |
| Validate | `model_validate`; on failure, retry with the error | Day 9 |
| Bound retries | Cap attempts; fail loudly | Days 9 and 13 |

Rule of thumb: **prompt for shape, constrain if you can, always validate, retry narrowly, fail loudly.**

## Invoice shape (as shipped)

```text
Invoice
  invoice_id: str
  invoice_date: date
  vendor: str
  currency: Literal["USD", "EUR", "GBP"]
  total: Decimal  # must equal sum(line_items.total)
  line_items: list[LineItem]  # min_length=1

LineItem
  description: str
  quantity: int > 0
  unit_price: Decimal > 0
  total: Decimal > 0  # must equal quantity * unit_price
```

`extra="forbid"` on both models. Harness tip: build failure cases as **raw dicts**; constructing invalid `LineItem(...)` while filling a test dict raises before your `try` loop.

## Status

- [x] Notes: schema vs probabilistic generation (this file)
- [x] `src/schemas/invoice.py` with required fields and constraints
- [x] Failure log: each observed break + one fix idea ([day8.md](./day8.md))
- [x] Lab results in [day8.md](./day8.md)
```
