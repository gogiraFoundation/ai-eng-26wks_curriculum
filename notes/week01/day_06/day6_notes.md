# Day 6 notes: two-backend CLI with streaming and running totals

**Deliverable:** `llm-cli chat --provider bedrock|direct` with streaming and a running token/cost total  
**Lab log:** [day6.md](./day6.md)  
**Context:** Bedrock Converse may still return `Error 002`. Build both paths; prove `direct` (local Ollama) end-to-end; keep Bedrock ready when the account is unblocked.

## Goal

One interactive chat loop that:

1. Accepts `--provider bedrock` or `--provider direct`
2. Streams assistant tokens to the terminal
3. Keeps a running input/output token total and cost estimate across turns
4. Prints a session footer after each reply (or on exit)

Reuse Day 3–4 ideas (answer, tokens, latency, `temperature` / `stream`) behind a thin provider interface. Do not paste Day 4 temperature tables here.

## The streaming accounting problem

Non-streaming responses usually include final usage in one JSON body (`usage`, or Ollama’s `prompt_eval_count` / `eval_count`).

While streaming, tokens arrive as small chunks. Exact provider usage often appears only on the **final** event. A live running total therefore needs a local estimate during the stream, then a **reconcile** step when the terminal frame arrives.

| Phase | What you know | What to show |
|---|---|---|
| During stream | Text chunks only | Optional live estimate (chars or words) |
| Final chunk | Provider usage fields | Replace estimate with exact counts |
| Multi-turn | Prior turns’ exact totals | Add this turn; print session running total |

## Token estimate vs exact count

Exact counts need the provider’s tokenizer (or fields the API returns). Shipping a heavy tokenizer in a lean CLI adds friction.

Practical compromise for Day 6:

1. While streaming: estimate from generated text, e.g. `approx_out ≈ len(text) // 4` (rough English heuristic; not billing-grade).
2. On the final event: set `output_tokens` from the provider (`eval_count` on Ollama; `usage.outputTokens` on Bedrock).
3. Input tokens: from the final event, or estimate from the prompt/history the same way until the final event arrives.
4. Cost: `0` for local `direct`; for Bedrock use constants from the current pricing page × tokens (per 1K or per 1M, consistently).

Never treat the character heuristic as the Bedrock bill. It is a UX stand-in until reconcile.

## Provider shape

```text
complete(messages, *, temperature, max_tokens) -> {text, input_tokens, output_tokens, latency_ms}
stream(messages, *, temperature, max_tokens)  -> yields text deltas; returns same usage dict at end
```

| Provider | Transport | Stream format | Usage on final frame |
|---|---|---|---|
| `direct` | Ollama `http://127.0.0.1:11434/api/chat` | NDJSON lines | `prompt_eval_count`, `eval_count`, `*duration` |
| `bedrock` | `bedrock-runtime` `converse_stream` | SDK event stream | `metadata.usage`, `metadata.metrics.latencyMs` |

Parse the format that provider actually sends. Ollama native chat is not OpenAI `data: …` SSE unless you call `/v1/chat/completions`.

## Running session totals

After each turn:

```text
session_input  += turn_input_tokens
session_output += turn_output_tokens
session_cost   += turn_cost_usd
```

Print something like:

```text
[turn] in=48 out=37 cost_usd=0.000000  latency_ms=1824
[session] in=96 out=74 cost_usd=0.000000
```

Keep `messages` history for multi-turn. Append the user message, then the assistant message assembled from the stream.

## Cost rules

| Provider | Cost line |
|---|---|
| `direct` | `api_charge_usd: 0` (local; electricity not measured) |
| `bedrock` | `(in/1000)*INPUT_RATE + (out/1000)*OUTPUT_RATE` for the chosen model; document rates and date |

## Suggested layout

```text
src/llm_cli/
  __main__.py          # argparse: chat --provider --temperature --stream
  providers/
    base.py
    ollama.py          # direct
    bedrock.py         # converse / converse_stream
  session.py           # messages + running totals
```

Minimum CLI:

```bash
python -m llm_cli chat --provider direct --stream
python -m llm_cli chat --provider bedrock --stream
```

## Status

- [ ] Provider interface + Ollama `direct` stream + reconcile
- [ ] Running session token/cost totals
- [ ] Bedrock provider (may fail with `Error 002` until Support clears)
- [ ] Multi-turn chat loop
- [ ] Lab results recorded in [day6.md](./day6.md)