
```markdown
# Day 03 notes: local Ollama Converse-shaped metrics

Bedrock Converse is blocked on this account (`Error 002`). Practised the same measurement loop against Ollama on `127.0.0.1:11434` so Day 3 still produces answer, tokens, and latency numbers.

Prerequisite: `ollama serve` in one terminal. Models present: `llama3.2:latest`, `qwen2.5:7b`.

## Field map (Ollama `/api/chat`, `stream: false`)

| Field | Meaning | Unit |
|---|---|---|
| `message.content` | Answer text | string |
| `prompt_eval_count` | Input tokens | count |
| `eval_count` | Output tokens | count |
| `prompt_eval_cached_count` | Input tokens served from prompt cache | count |
| `load_duration` | Time to load or attach the model in memory | ns |
| `prompt_eval_duration` | Time to process the prompt | ns |
| `eval_duration` | Time to generate output tokens | ns |
| `total_duration` | End-to-end wall time | ns |

Convert with `seconds = ns / 1e9`. Bedrock reports `metrics.latencyMs` in milliseconds instead.

## Run 1: vague prompt (cold-ish)

```bash
curl http://127.0.0.1:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Reply with one sentence."}],
  "stream": false
}'
```

| Metric | Value |
|---|---:|
| Input tokens (`prompt_eval_count`) | 30 |
| Output tokens (`eval_count`) | 31 |
| Total wall time | ~2.64 s |
| Of which model load | ~1.80 s |
| Approx. generation rate | ~47 tok/s (`eval_count / eval_duration`) |

Observation: the HTTP call succeeded, but the model did not obey “one sentence”. A 200 with healthy latency does not mean the task passed.

## Run 2: same vague prompt again

Raw result (trimmed):

- Answer: refused / asked for clarification rather than one sentence.
- `prompt_eval_count` 30, `eval_count` 21
- `total_duration` ~2.08 s
- `load_duration` ~1.55 s (still loading; not held in memory)
- `prompt_eval_duration` ~79 ms
- `eval_duration` ~0.45 s

`prompt_eval_cached_count` was 0. Warm weights and prompt cache are different things.

## Run 3: clearer prompt, `temperature: 0`, `keep_alive: 10m`

```bash
curl http://127.0.0.1:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Explain API idempotency in exactly one sentence."}],
  "stream": false,
  "keep_alive": "10m",
  "options": {"temperature": 0}
}'
```

### First call (after `keep_alive`)

| Metric | Value |
|---|---:|
| Input tokens | 37 |
| Output tokens | 51 |
| Cached prompt tokens | 0 |
| `load_duration` | 1.05 s |
| `prompt_eval_duration` | 0.136 s |
| `eval_duration` | 1.08 s |
| `total_duration` | 2.27 s |

Answer (one sentence, as requested): API idempotency means repeating the same request has the same effect as a single request, without unintended extra side effects.

### Second call (~3 minutes later, model still kept)

| Metric | Value |
|---|---:|
| Input tokens | 37 |
| Output tokens | 51 |
| Cached prompt tokens | 36 / 37 |
| `load_duration` | 0.0027 s |
| `prompt_eval_duration` | 0.037 s |
| `eval_duration` | 1.09 s |
| `total_duration` | 1.14 s |

Answer text matched the first call exactly (`temperature: 0`).

## What changed between the two `keep_alive` calls

| Effect | Evidence |
|---|---|
| Model residency | `load_duration` 1.05 s → 2.7 ms |
| Prompt cache | `prompt_eval_cached_count` 0 → 36; prompt eval 136 ms → 37 ms |
| Generation work | Still ~51 new tokens; `eval_duration` stayed ~1.09 s |

`total_duration` roughly halved mainly because load disappeared and prompt eval got cheaper, not because generation got faster.

## Bridge to Bedrock Converse (blocked until Error 002 clears)

| Concept | Ollama | Bedrock Converse |
|---|---|---|
| Answer | `message.content` | `output.message.content[0].text` |
| Input tokens | `prompt_eval_count` | `usage.inputTokens` |
| Output tokens | `eval_count` | `usage.outputTokens` |
| Latency | `total_duration` (ns → ms) | `metrics.latencyMs` |
| Cost | £0 locally | pricing × tokens |

Day 3 deliverable shape for both backends: print answer, input tokens, output tokens, latency in ms, and (Bedrock only) estimated cost.

## Takeaways

1. Measure load, prompt eval, and generation separately; wall time alone hides which phase dominates.
2. `keep_alive` controls weight residency; `prompt_eval_cached_count` is a second optimisation.
3. Specific prompts plus `temperature: 0` improve instruction-following and make repeats comparable.
4. Local Ollama stands in for the Week 1 `direct` provider until Bedrock invoke is unblocked.
```