# Day 03: Local Ollama API Calls and Metrics

## Objective

Bedrock Converse is blocked on this account (`Error 002`). I practised the equivalent measurement workflow using Ollama at `127.0.0.1:11434`: request an answer, inspect token usage, and measure latency.

This develops transferable skills, but does not replace practice with AWS authentication or the Bedrock Converse request/response format.

## Setup

- Start `ollama serve` if Ollama is not already running.
- Installed models: `llama3.2:latest` and `qwen2.5:7b`.
- Python script: `src/local/day_3_chats.py`.
- Endpoint: `/api/chat`, with `stream: false`.

## Understanding the response fields

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

Generation rate excludes model loading and prompt processing. Only calculate it when `eval_duration` is greater than zero.

Ollama's `total_duration` is server-reported. Measure client elapsed time separately around the HTTP request to include overhead outside that reported duration.

## Run 1: Vague prompt with `llama3.2`

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

The API returned a complete response, but the answer contained multiple sentences. Successful delivery does not guarantee instruction-following.

The prompt supplied no topic, so asking for clarification was reasonable. The sentence-count requirement was the part the model missed.

## Run 2: Repeat of the vague prompt

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

This answer followed the one-sentence instruction and asked for clarification. It was not a refusal.

The substantial reported loading duration means this was not a clean warm-model comparison. The timing alone does not establish why loading took that long.

## Run 3: Clearer prompt with explicit retention

I supplied a topic, set `temperature` to zero, and requested ten minutes of model retention with `keep_alive`.

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

### Results

The second call was made approximately three minutes after the first.

| Metric | Call 1 | Call 2 |
|---|---:|---:|
| Input tokens | 37 | 37 |
| Output tokens | 51 | 51 |
| Cached prompt tokens | 0 | 36 |
| Model-loading duration | 1.05 s | 0.0027 s |
| Prompt-processing duration | 0.136 s | 0.037 s |
| Output-generation duration | 1.08 s | 1.09 s |
| Reported total duration | 2.27 s | 1.14 s |

Recorded answer:

> API idempotency means repeating the same request has the same effect as a single request, without unintended extra side effects.

The answer met the one-sentence requirement. More precisely, idempotency concerns the intended effect on server state; repeated requests need not return identical responses.

The answer text matched across these two calls. Temperature zero reduces sampling variability, but does not guarantee identical output across all runs, hardware, or software versions.

### Interpretation

| Mechanism | Evidence |
|---|---|
| Model residency | Loading fell from 1.05 s to 2.7 ms, consistent with model reuse |
| Prompt caching | Cached tokens increased from 0 to 36; prompt processing fell from 136 ms to 37 ms |
| Output generation | Both calls generated 51 tokens; generation duration stayed near 1.09 s |

Reported total duration roughly halved because loading and prompt processing became cheaper, not because generation became faster.

These are observations from two calls, not a general performance benchmark.

## Run 4: Python client with `qwen2.5:7b`

I ran `src/local/day_3_chats.py` twice using `temperature: 0` and explicit `keep_alive`.

This used a different model and different token counts from the curl runs. It is a separate paired comparison, not a controlled model-to-model benchmark.

| Metric | Call 1 | Call 2 |
|---|---:|---:|
| Input tokens | 43 | 43 |
| Output tokens | 71 | 71 |
| Cached prompt tokens | 0 | 42 |
| Model-loading duration | 3,563 ms | 2 ms |
| Prompt-processing duration | 307 ms | 54 ms |
| Output-generation duration | 3,342 ms | 3,378 ms |
| Client elapsed time | 7,254 ms | 3,456 ms |
| Server-reported total | 7,220 ms | 3,438 ms |

### Interpretation

- Answer text matched across both calls in this experiment.
- Client elapsed time fell by approximately 52%.
- Model-loading duration fell by 3,561 ms.
- Prompt-processing duration fell by 253 ms, with 42 of 43 prompt tokens reported as cached.
- Output generation took 36 ms longer, so faster generation did not explain the overall improvement.

The near-zero loading duration is consistent with model residency. Prompt caching is separate evidence of reused prompt computation.

Client elapsed time exceeded server-reported duration by 34 ms on Call 1 and 18 ms on Call 2. This gap includes overhead outside the server's reported timing; the experiment does not isolate its individual causes.

There was no per-token API charge. Electricity and hardware costs were not measured.

## Bridge to Bedrock Converse

Live Bedrock testing remains pending until account access is restored.

| Concept | Ollama | Bedrock Converse |
|---|---|---|
| Answer | `message.content` | Collect text blocks from `output.message.content` |
| Input tokens | `prompt_eval_count` | `usage.inputTokens` |
| Output tokens | `eval_count` | `usage.outputTokens` |
| Reported latency | `total_duration / 1e6` in ms | `metrics.latencyMs` |
| Usage cost | No per-token API charge; local costs not measured | Estimate using current model prices and applicable usage categories |

Tokenizers, token accounting, and timing boundaries can differ across providers. Treat these fields as conceptual counterparts, not guaranteed identical measurements.

For an ordinary uncached, on-demand Bedrock text call, estimate input and output charges separately using the selected model's current rates. Include any additional applicable charges, and do not reuse another model's prices.

### What does Converse provide over InvokeModel?

Converse provides a consistent conversation interface across supported Bedrock models, including common message structures and inference parameters. InvokeModel generally requires model-specific request and response bodies.

Model capabilities still vary, and some features require model-specific fields even when using Converse.

## Script requirements

The local script should:

- Print the answer and model identifier.
- Print input and output token counts.
- Print provider-reported latency in milliseconds.
- Measure client elapsed time separately.
- Report loading, prompt processing, generation, and cached tokens when available.
- State that local execution has no per-token API charge, rather than claiming zero total cost.

The later Bedrock version should preserve the common output fields and add an estimated cost once model pricing and usage are known.

## Takeaways

1. Separate model loading, prompt processing, and output generation; total duration alone hides the dominant phase.
2. `keep_alive` requests model retention. Prompt caching is a separate mechanism and is not guaranteed by retention alone.
3. Clear prompts define the task. Lower temperature reduces sampling variability, not the need to check correctness.
4. API success, task correctness, and performance are separate checks.
5. Two calls illustrate behaviour but are insufficient for a reliable benchmark.
6. Ollama supports local practice while Bedrock is blocked. AWS authentication and Converse-specific behaviour still require live AWS exercises.

## Day 3 status

Completed locally:

- Curl and Python API calls.
- Response inspection and token accounting.
- Provider-reported timings and Python client elapsed timing.
- Paired observations of loading and prompt caching for both models.
- Conceptual comparison of Converse and InvokeModel.

Remaining local comparison:

- Run the same prompt on `llama3.2` and `qwen2.5:7b` using the same generation settings.
- Warm each model before its measured runs and record loading and cache status.
- Compare answer quality, instruction-following, token counts, and timing.
- Keep cached and uncached results separate. Different tokenizers and output lengths limit direct speed comparisons.

Pending AWS access:

- Repeat the exercise through Bedrock Converse.
- Verify AWS authentication and response handling.
- Estimate cost using the selected model's current prices.