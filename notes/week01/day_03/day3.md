# Day 03 notes: local Ollama API calls and metrics

Bedrock Converse is blocked on this account (`Error 002`). I practised the same measurement workflow against Ollama at `127.0.0.1:11434`: request an answer, inspect token usage, and measure latency.

This practises transferable concepts, not the Bedrock Converse request/response format or AWS authentication.

Prerequisite: start `ollama serve` if Ollama is not already running. Installed models: `llama3.2:latest` and `qwen2.5:7b`.

## Field map: Ollama `/api/chat`, `stream: false`

| Field | Meaning | Unit |
|---|---|---|
| `message.content` | Answer text | string |
| `prompt_eval_count` | Reported input-token count | tokens |
| `eval_count` | Generated output-token count | tokens |
| `prompt_eval_cached_count` | Reported cached prompt-token count, when available | tokens |
| `load_duration` | Reported model-loading duration | ns |
| `prompt_eval_duration` | Reported prompt-processing duration | ns |
| `eval_duration` | Reported output-generation duration | ns |
| `total_duration` | Ollama-reported request duration | ns |

Conversions:

- Seconds: `ns / 1e9`
- Milliseconds: `ns / 1e6`
- Generation rate: `eval_count / (eval_duration / 1e9)`

Generation rate excludes model loading and prompt processing. Ollama's `total_duration` is not a separate client-side measurement; measure elapsed time around the HTTP request to include client and network overhead.

Bedrock Converse reports service latency in `metrics.latencyMs`.

## Run 1: vague prompt

```bash
curl http://127.0.0.1:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Reply with one sentence."}],
    "stream": false
  }'
```

| Metric | Value |
|---|---:|
| Input tokens | 30 |
| Output tokens | 31 |
| Reported total duration | 2.64 s |
| Model-loading duration | 1.80 s |
| Approximate generation rate | 47 tokens/s |

Observation: the API returned a complete response, but the answer contained multiple sentences. Successful response delivery does not guarantee instruction-following.

The prompt also supplied no topic, so asking for clarification was reasonable; the sentence-count requirement was the part it missed.

## Run 2: same vague prompt again

| Metric | Value |
|---|---:|
| Input tokens | 30 |
| Output tokens | 21 |
| Cached prompt tokens | 0 |
| Reported total duration | 2.08 s |
| Model-loading duration | 1.55 s |
| Prompt-processing duration | 79 ms |
| Output-generation duration | 0.45 s |

Answer:

> I'm happy to help, but it seems like you didn't specify what you need assistance with.

Observation: this answer followed the one-sentence instruction and asked for clarification. It was not a refusal.

The substantial reported loading duration means this was not a clean low-load comparison. The response alone does not establish why loading took that long or confirm the model's residency before the call.

Model residency and prompt caching are separate mechanisms.

## Run 3: clearer prompt with explicit retention

I supplied a topic, set `temperature` to zero, and requested that Ollama keep the model loaded for ten minutes after the request.

```bash
curl http://127.0.0.1:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Explain API idempotency in exactly one sentence."}],
    "stream": false,
    "keep_alive": "10m",
    "options": {"temperature": 0}
  }'
```

### First call

| Metric | Value |
|---|---:|
| Input tokens | 37 |
| Output tokens | 51 |
| Cached prompt tokens | 0 |
| Model-loading duration | 1.05 s |
| Prompt-processing duration | 0.136 s |
| Output-generation duration | 1.08 s |
| Reported total duration | 2.27 s |

Recorded answer:

> API idempotency means repeating the same request has the same effect as a single request, without unintended extra side effects.

The answer met the one-sentence requirement. More precisely, idempotency concerns the intended effect on server state; repeated requests need not return identical responses.

### Second call, approximately three minutes later

| Metric | Value |
|---|---:|
| Input tokens | 37 |
| Output tokens | 51 |
| Cached prompt tokens | 36 of 37 |
| Model-loading duration | 2.7 ms |
| Prompt-processing duration | 0.037 s |
| Output-generation duration | 1.09 s |
| Reported total duration | 1.14 s |

The answer text matched the first call exactly in this experiment. Temperature zero reduces sampling variability, but does not guarantee identical output across all runs, hardware, or software versions.

## What changed between the two retention-test calls?

| Mechanism | Evidence |
|---|---|
| Model residency | Loading dropped from 1.05 s to 2.7 ms, consistent with model reuse |
| Prompt caching | Cached tokens increased from 0 to 36; prompt processing dropped from 136 ms to 37 ms |
| Output generation | Both calls generated 51 tokens; generation duration remained about 1.09 s |

Reported total duration roughly halved. The improvement came mainly from reduced loading and prompt processing, not faster output generation.

This is an observation from two calls, not a general performance benchmark. A stronger comparison would repeat each condition several times and report median and tail latency.

## Bridge to Bedrock Converse

Bedrock testing remains pending until account access is restored.

| Concept | Ollama | Bedrock Converse |
|---|---|---|
| Answer | `message.content` | Collect text blocks from `output.message.content` |
| Input tokens | `prompt_eval_count` | `usage.inputTokens` |
| Output tokens | `eval_count` | `usage.outputTokens` |
| Reported latency | `total_duration / 1e6` in ms | `metrics.latencyMs` |
| Usage cost | No per-token API charge; local electricity and hardware costs not measured | Estimate using applicable model prices and usage categories |

The token counts and latency fields are useful counterparts, but their accounting and measurement boundaries are not necessarily identical across providers. Token counts also depend on the model's tokenizer and chat template.

For an ordinary uncached, on-demand Bedrock text call, estimate input and output charges separately using the model's current rates. Include any additional applicable charges; do not reuse one model's prices for another.

Day 3 script deliverable:

- Print the answer and model name.
- Print input and output token counts.
- Print provider-reported latency in milliseconds.
- Measure client elapsed time separately.
- For local execution, state that there is no per-token API charge rather than claiming zero total cost.
- For Bedrock, print an estimated cost once the model, pricing, and usage are known.

## Takeaways

1. Separate model loading, prompt processing, and output generation; total duration alone hides the dominant phase.
2. `keep_alive` requests model retention. Prompt caching separately reuses prompt computation; retention does not guarantee a cache hit.
3. A clear prompt defines the task. Lower temperature reduces sampling variability, but does not guarantee correctness or instruction-following.
4. API success, task correctness, and performance are separate things to evaluate.
5. Ollama lets me practise the local model-client workflow while Bedrock is blocked. AWS authentication, Converse-specific handling, and managed-service behaviour still require later AWS practice.

## Tasks
## Python measurement results

Ran `src/day_03_chat.py` twice with `temperature: 0`.

| Metric | Call 1 | Call 2 |
|---|---:|---:|
| Input tokens | 43 | 43 |
| Output tokens | 71 | 71 |
| Cached prompt tokens | 0 | 42 |
| Model load | 3,563 ms | 2 ms |
| Prompt processing | 307 ms | 54 ms |
| Output generation | 3,342 ms | 3,378 ms |
| Client elapsed time | 7,254 ms | 3,456 ms |
| Server-reported total | 7,220 ms | 3,438 ms |

The answer text matched across both calls. This is an observation from this experiment, not a guarantee from temperature zero.

Call 2's client elapsed time fell by approximately 52%. Model-loading time dropped by 3,561 ms and prompt processing by 253 ms. Output generation was slightly slower, so faster generation did not explain the improvement.

The near-zero second loading duration is consistent with model residency. Separately, 42 of 43 prompt tokens were reported as cached, showing reuse of prompt computation.

Client elapsed time exceeded server-reported duration by 34 ms on Call 1 and 18 ms on Call 2. This gap includes overhead outside the server's reported timing; these measurements do not isolate its individual causes.

There was no per-token API charge. Electricity and hardware costs were not measured.

These Python runs used different token counts from the earlier curl runs, so they are a separate paired comparison, not a direct speed comparison against curl.

## Day 3 status

Completed locally: API calls, response inspection, token accounting, provider-reported timing, client elapsed timing, and a two-call comparison using `src/day_03_chat.py`.

Pending AWS access: repeat the exercise through Bedrock Converse, verify AWS authentication and response handling, and calculate estimated cost using the selected model's current prices.