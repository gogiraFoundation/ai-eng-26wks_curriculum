

### `day13_notes.md`

```markdown
# Day 13 notes: extraction service build day

**Lab log:** [day13.md](./day13.md)  
**Week 2 ship target (Day 14):** green CI + tag `extract-v0.1`

## Plan (3 h box)

| Block | Focus |
|---|---|
| 30m | Write 15 synthetic invoices under e.g. `tests/week02/fixtures/invoices/` |
| 90m | Wire extract path: recorded responses → `extract_with_retry` → `Invoice`; optional currency tool |
| 40m | Score field-level accuracy on all 15 |
| 20m | README: how to run + accuracy table |

## Self-check: why record responses instead of calling the model in CI?

Live model calls are **slow, flaky, and paid**. Recorded fixtures make tests **deterministic**: same input → same model text → assert parse/accuracy. You still test retry and schema logic; you are not retesting Bedrock sampling every push.

## Suggested layout

```text
tests/week02/
  fixtures/invoices/01.txt … 15.txt
  fixtures/recorded/01.json …   # raw model output strings (or JSON)
  test_invoice_retry.py         # Day 9
  test_extract_accuracy.py      # Day 13