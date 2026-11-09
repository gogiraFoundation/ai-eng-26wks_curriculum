# Day 4 notes: sampling and streaming

**Topic:** temperature, top-p, max tokens, streaming  
**Context:** Bedrock Converse is still blocked (`Error 002`). Practise against local Ollama (OpenAI-compatible endpoint `http://127.0.0.1:11434/v1`).

Flags control *how* the model samples the next token and *how* the client receives tokens. They do not change the model weights.

## Temperature (`--temperature`)

A non-negative float (commonly `0.0`–`2.0`) that reshapes the next-token distribution before sampling.

For each step the model produces raw scores (logits) for candidate tokens, for example roughly: `the: 12.5`, `a: 10.2`, `apple: -2.1`. Those logits are scaled by temperature, then turned into probabilities (softmax), then a token is sampled.

| Setting | Effect |
|---|---|
| Low (`0.0`–`0.3`) | Sharpens the distribution. The top token dominates. At `0.0` many APIs use greedy decoding: always pick the highest-probability token (most deterministic). |
| Medium (`~0.7`) | Mild variety; useful for prose without total chaos. |
| High (`1.0`–`1.5+`) | Flattens the distribution. Lower-ranked tokens get more probability mass; output varies more and can drift off brief. |

Notes:

- Temperature is not “creativity” as a separate brain mode; it is a sampling knob on the same logits.
- Factual or tightly constrained prompts often look similar across temperatures. Use a **style-sensitive** prompt for the variance table (see Task).
- Spelling of the flag: `--temperature` (not `--temprature`).

## Top-p (`top_p` / nucleus sampling)

Usually a float in `(0, 1]`. After temperature scaling, keep only the smallest set of tokens whose cumulative probability ≥ `top_p`, then sample from that truncated set.

- `top_p = 1.0`: effectively no nucleus truncation (full distribution, still shaped by temperature).
- `top_p = 0.9`: drop the long tail of unlikely tokens; often more stable than raising temperature alone.

For Day 4, hold `top_p` fixed (for example `1.0` or `0.9`) while you vary temperature, so the variance table has one changing variable.

## Max tokens (`max_tokens` / Ollama `num_predict`)

Hard cap on how many **new** tokens the model may generate. Protects latency and cost (and local wait time). Too low truncates mid-sentence; too high wastes time if the model rambles. Day 3 already used `num_predict: 200`; keep a fixed cap for the temperature table.

## Streaming (`--stream`)

Controls **delivery**, not sampling.

| Mode | Behaviour |
|---|---|
| Off (default) | One request; wait until the full completion; print once. |
| On | Read incremental chunks as they arrive; print each fragment immediately. |

On Ollama’s OpenAI-compatible API, streaming typically uses **newline-delimited JSON** chunks over a persistent HTTP response (`stream: true`), not always browser-style SSE with `text/event-stream`. Native Ollama `/api/chat` also streams NDJSON. Either way: open the connection, decode each event, flush text to the terminal, and read until a final chunk carries usage / done metadata (token counts, finish reason).

Streaming improves time-to-first-token in the UI. Total generation work is similar; you still need the final chunk (or a second accounting path) for token totals.

## Task

1. Write `src/llm_client.py` with the standard library plus `requests` (or `urllib`): `argparse`, `time`, target Ollama’s OpenAI-compatible chat endpoint.
2. Add `--temperature` and `--stream` flags (and a fixed `--max-tokens` / top-p so the table stays fair).
3. Use a high-sensitivity prompt (stylistic, many plausible paths), not a single-answer math fact.
4. Run the same prompt at several temperatures (for example `0`, `0.5`, `1.0`), three times each if practical. Save a short variance table below.

### Sample prompt

```text
Write a single sentence describing a mysterious old key found in an attic, using highly poetic imagery.