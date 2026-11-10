# Day 6 notes: two-backend CLI with streaming and running totals

**Deliverable:** `llm-cli chat --provider bedrock|direct` with streaming and a running token/cost total  
**Lab log:** [day6.md](./day6.md)  
**Package:** `src/llm_cli/`  
**Context:** Bedrock Converse may still return `Error 002`. Prove `direct` (Ollama) end-to-end; keep Bedrock wired for when the account unblocks.

## Goal

One interactive chat loop that:

1. Accepts `--provider bedrock` or `--provider direct`
2. Streams assistant tokens to the terminal
3. Keeps running input/output token totals and a cost estimate across turns
4. Prints a per-turn footer and a session total on exit (`/exit` or Ctrl+C)

Reuse Day 3–4 ideas (answer, tokens, latency, `temperature` / `stream`) behind a thin provider interface. Do not paste Day 4 temperature tables here.

## The streaming accounting problem

Non-streaming responses usually include final usage in one JSON body (`usage`, or Ollama’s `prompt_eval_count` / `eval_count`).

While streaming, tokens arrive as small chunks. Exact provider usage often appears only on the **final** event. Show text live; set usage from that terminal frame after the stream ends.

| Phase | What you know | What to show |
|---|---|---|
| During stream | Text chunks only | Stream to stdout (`flush=True`) |
| Final chunk | Provider usage fields | Exact `in` / `out` / latency / cost |
| Multi-turn | Prior turns’ exact totals | Add this turn; print session running total |

## Token estimate vs exact count

Exact counts need the provider’s tokenizer (or fields the API returns).

Practical compromise for Day 6:

1. Prefer provider fields on the final event (`prompt_eval_count` / `eval_count` on Ollama; `usage` on Bedrock).
2. Fallback only if missing: `approx ≈ len(text) // 4` (rough heuristic; not billing-grade).
3. Cost: `0` for local `direct`; for Bedrock use documented rates × tokens (see `config.py`).

Never treat the character heuristic as the Bedrock bill.

## Provider shape

```text
stream(messages, *, temperature, top_p, max_tokens) -> yields text deltas
last_result -> TurnResult(text, input_tokens, output_tokens, latency_ms, cost_usd)
```

| Provider | Transport | Stream format | Usage on final frame |
|---|---|---|---|
| `direct` | Ollama `http://127.0.0.1:11434/api/chat` | NDJSON lines | `prompt_eval_count`, `eval_count` |
| `bedrock` | `bedrock-runtime` `converse_stream` | SDK event stream | `metadata.usage`, latency metrics |

Ollama native chat is NDJSON, not OpenAI `data: …` SSE (unless you call `/v1/chat/completions`).

## Running session totals

After each turn:

```text
session_input  += turn_input_tokens
session_output += turn_output_tokens
session_cost   += turn_cost_usd
```

Printed format:

```text
[turn] in=48 out=37 cost_usd=0.000000 latency_ms=1824
[session] in=96 out=74 cost_usd=0.000000
```

`Session` holds `messages` (including system), usage counters, and `/clear` (resets history + totals).

## Cost rules

| Provider | Cost line |
|---|---|
| `direct` | `cost_usd: 0` (local) |
| `bedrock` | `(in/1000)*BEDROCK_INPUT_USD_PER_1K + (out/1000)*BEDROCK_OUTPUT_USD_PER_1K` in `config.py`; document rates and date |

## Layout (as shipped)

```text
src/llm_cli/
  __init__.py
  __main__.py          # argparse chat loop (python -m llm_cli)
  config.py            # defaults, Bedrock rates
  session.py           # messages + running totals
  providers/
    __init__.py        # get_provider(...)
    base.py            # TurnResult / protocol
    ollama.py          # direct
    bedrock.py         # converse_stream
```

`python -m llm_cli` requires `__main__.py`. A lone `main.py` is not enough.

## How to run

From repo root, with Ollama serving `qwen2.5:7b`:

```bash
# PYTHONPATH so src/llm_cli is importable without install
PYTHONPATH=src python -m llm_cli chat --provider direct --stream

# when Bedrock works
PYTHONPATH=src python -m llm_cli chat --provider bedrock --stream
```

In-chat: `/clear` (reset history + totals), `/exit` (print session total and quit). Shell `CLEAR` is unrelated.

**Defaults (`config.py`):** `temperature=0.0`, `top_p=0.9`, `max_tokens=200`, Ollama `qwen2.5:7b`, Bedrock `eu.amazon.nova-micro-v1:0`, profile `agent-toolkit`, region `eu-north-1`.

## Behaviour notes from the lab

- Multi-turn context works: turn `in` rises as history grows.
- `out=200` means `num_predict` / max tokens hit the default cap; raise with `--max-tokens`.
- Weak system prompt (`You are a concise CLI assistant.`) plus a small local model can invent identity (e.g. claiming Anthropic). Optional tighten: name the real model (`qwen2.5:7b` via Ollama) and forbid inventing vendor/stack.
- Prefer `.venv/bin/python` after activate; earlier failures showed `/usr/local/bin/python3` missing the package on `PYTHONPATH`.

## Status

- [x] Provider interface + Ollama `direct` stream + usage from final NDJSON
- [x] Running session token/cost totals + `/clear` / `/exit`
- [x] Multi-turn chat loop (`python -m llm_cli` via `__main__.py`)
- [ ] Bedrock provider proven live (may still fail with `Error 002`)
- [x] Lab results recorded in [day6.md](./day6.md)