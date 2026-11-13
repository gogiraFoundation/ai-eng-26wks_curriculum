# Day 10 notes: Bedrock tool use (Converse)

**Lab log:** [day10.md](./day10.md)  
**Deliverable:** `src/tools_loop.py` — loop until `end_turn`, max 5 iterations, print each tool call  
**API:** `bedrock-runtime` `converse` (non-stream is enough for the tool loop)  
**Model:** `eu.amazon.nova-micro-v1:0` · profile `agent-toolkit` · region `eu-north-1`  
**Exam angle:** tool / function calling as controlled side effects, not free-form text

## Why tools

The model should not invent weather, database rows, or calculator results. It emits a structured **tool request**; your code runs the function and returns a **tool result**; the model then continues or finishes with `end_turn`.

## Converse pieces

| Piece | Role |
|---|---|
| `toolConfig.tools[]` | JSON Schema per tool (`toolSpec.name`, `description`, `inputSchema`) |
| `stopReason` | `tool_use` → you must return results; `end_turn` → done |
| Assistant content | May include `toolUse` blocks (`toolUseId`, `name`, `input`) |
| Follow-up user message | `toolResult` content blocks matching each `toolUseId` |

Echo the same `toolUseId` from the request when you send the result.

## Loop (as shipped)

```text
messages = [user]
for iteration in 1..5:
  response = converse(..., toolConfig=...)
  append assistant message
  if stopReason == end_turn: break
  if stopReason == tool_use:
    print each tool call; run stub; append user message with toolResults
  else: break
```

Lab evidence: Stockholm weather → one `get_weather` call → `end_turn` on iteration 2 ([day10.md](./day10.md)).

## Guardrails

- **Max 5 iterations** — avoid infinite tool loops.
- **Print every tool call** — required lab evidence.
- **Stub tools locally** — fixed weather dict is enough for Day 10.
- **Reuse Week 1 auth** — IAM user on `agent-toolkit`; `botocore[crt]`; unset `AWS_BEARER_TOKEN_BEDROCK`.
- **Fresh `aws login`** — do not reuse old browser authorize URLs (causes 400).

## Day 9 vs Day 10

| Day 9 | Day 10 |
|---|---|
| Text generator returns JSON; you parse/validate | Model selects a **named tool** with JSON arguments |
| Retry once on `JSONDecodeError` / `ValidationError` | Run the tool, return `toolResult`, continue Converse |
| Offline unit tests with a fake `generate_fn` | Live Bedrock loop (stub tool body still local) |

Later you can expose invoice parse as a tool; Day 10 only proves the control loop.

## How to run

```bash
bash infra/iam-setup/scripts/auth.sh sign-in
unset AWS_BEARER_TOKEN_BEDROCK
PYTHONPATH=src .venv/bin/python src/tools_loop.py
```

## Status

- [x] Notes: Converse tool use vs free-form text
- [x] `src/tools_loop.py` with max 5 iterations and printed tool calls
- [x] Lab run recorded in [day10.md](./day10.md)