# Day 16 notes: context engineering

**Lab log:** [day16.md](./day16.md)  
**Deliverable:** [src/prompts/README.md](../../../../src/prompts/README.md)

## Prompt engineering vs context engineering

- **Prompt engineering:** wording of instructions (often the system prompt).
- **Context engineering:** which tokens are present at inference — system, user, tools, retrieval, history — under a finite attention budget.

Goal: smallest high-signal context that still produces the desired behaviour.

## Layer map (this repo)

| Layer | Invoice extract today | Later (agents / RAG) |
|---|---|---|
| System | `invoice/system.txt` (or few_shot / cot variants) | Policies, tool-use rules |
| User | `DOCUMENT:\n` + invoice text | User question |
| Examples | Hold-out pairs in few-shot build | Optional static demos |
| Retrieved | (not wired yet) | Vendor handbook, KB chunks |
| Tools | Day 10 weather loop pattern | Currency, normalise currency |

## Self-check

System prompt: stable contract. Retrieved context: per-request facts. Mixing them makes prompts huge, stale, and hard to eval.