# Day 15 notes: system / few-shot / CoT trade-offs

**Lab log:** [day15.md](./day15.md)  
**Week 3 theme:** Prompting and context engineering  
**Exam link:** 2.2.8 (task-specific prompt engineering), 3.3.9 (prompt testing)

## Why compare prompt variants

The same schema and fixtures can be driven by different prompts. Accuracy is not free: each style shifts **input tokens**, **output tokens**, **latency**, and **cost**. Measure before picking a default for `/extract`.

## The three styles

| Style | Idea | Cost pattern |
|---|---|---|
| System (zero-shot) | Rules + schema in the system message; no examples | Lowest input; short output if JSON-only |
| Few-shot | Same rules plus a few full input → JSON pairs | High **input** every call; output stays short |
| Chain-of-thought (CoT) | Ask for step-by-step checks, then JSON | Often high **output** (reasoning is generated text) |

Providers usually price **output tokens higher than input**, so long CoT can dominate spend even when the system prompt is short.

## Fair experiment design

1. One model, fixed temperature (`0`), fixed `maxTokens`.
2. Score against fixed `expected/` labels.
3. Hold out few-shot example ids from the scored set (otherwise you inflate few-shot accuracy).
4. Count **all** output tokens for CoT, including any reasoning before JSON.
5. Keep the live runner out of CI (flaky, paid); CI stays on recorded fixtures.

## Expected trade-off (hypothesis)

| Variant | Input | Output | Latency | Accuracy (typical) |
|---|---|---|---|---|
| System | Low | Lowest | Fastest | Enough on clean, uniform docs |
| Few-shot | High | Low | Fast | Better format / edge-case shape |
| CoT | Low–medium | Highest (if it actually reasons) | Slowest | Helps when math or conflicts matter |

On **clean synthetic invoices**, system or few-shot often saturates accuracy; CoT then buys little.

## What this run showed (Nova Micro)

See the numbers in [day15.md](./day15.md).

- Few-shot won (98.6% fields) by fixing `line_items`; input tokens ~4× system.
- CoT beat system on lines but not few-shot; **output tokens barely rose**, so the model did not produce a long reasoning tax (and did not earn a clear win).
- One shared `invoice_id` miss across all variants points at label/extraction ambiguity, not prompt style alone.

## Production heuristic

- Default to **system** when docs are uniform and scalars matter most.
- Use **few-shot** when nested structure (`line_items`) drifts.
- Add **CoT** (or a short bounded reasoning field) only when evals show hard cases move; otherwise you pay for tokens you do not need.
- Version prompts as files; log tokens and latency per variant so you can defend the choice.

## Free resources

- [Foundations of Prompt Engineering](https://skillbuilder.aws/learn/VF6H4SZ1BU/foundations-of-prompt-engineering) (Skill Builder)
- Bedrock Converse usage (`inputTokens` / `outputTokens` / `latencyMs`)