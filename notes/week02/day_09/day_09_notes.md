
# Day 9 notes: validation + retry on parse failure
**Lab log:** [day9.md](./day9.md)  
**Depends on:** Day 8 `Invoice` schema and failure modes
## Idea
Prompts alone do not guarantee schema-valid JSON. Day 9 adds a **bounded repair loop**:
1. Generate text that should be JSON.
2. Parse (`json.loads`) and validate (`Invoice.model_validate`).
3. On failure, call the generator **once more** with a short error summary (missing field, literal_error, etc.).
4. If the second attempt fails, raise. Never retry unbounded.
“Exactly one retry” means: first failure triggers one more generate+parse; the test asserts the generate function was called twice when the first payload was bad and the second was good.
## What to retry vs not
| Failure | Retry? | Why |
|---|---|---|
| Trailing comma / markdown fence / missing key | Yes (once) | Often fixed by feeding the validator error back |
| Wrong vendor name but valid shape | No (as parse retry) | Semantic; needs better extraction or human review |
| Persistent schema refusal after one retry | Raise | Bound cost and latency |
## Test strategy
Do not call a real LLM in unit tests. Pass a fake `generate_fn` that returns a queue of strings. Assert call count and final `Invoice`.
