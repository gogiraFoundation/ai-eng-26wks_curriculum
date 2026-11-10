# Day 4 notes: sampling and streaming

**Topic:** temperature, top-p, max tokens, streaming  
**Lab log (measured runs):** [day4.md](./day4.md)  
**Script:** `src/local/llm_client.py` (Ollama native `/api/chat`; Bedrock still blocked with `Error 002`)

Flags control *how* the model samples the next token and *how* the client receives tokens. They do not change the model weights.

## Temperature (`--temperature`)

A non-negative float (commonly `0.0`–`2.0`; some stacks allow higher) that reshapes the next-token distribution before sampling.

For each step the model produces raw scores (logits) for candidate tokens, for example roughly: `the: 12.5`, `a: 10.2`, `apple: -2.1`. Those logits are scaled by temperature, then turned into probabilities (softmax), then a token is sampled.

| Setting | Effect | What we saw (lab) |
|---|---|---|
| Low (`0.0`–`0.3`) | Sharpens the distribution; near-greedy at `0.0` | Three runs at `0.0`: identical sentence and `37` output tokens |
| Mid (`~0.5`–`0.7`) | Mild variety | `0.5`: leaf → finger; still on brief |
| High (`1.0`–`1.5`) | Flatter distribution; more drift | `1.0`: ornate metaphors; still English one-liners |
| Very high (`2.0`–`3.0`) | Heavy tail mass; unstable | Language mixing (EN/ZH), typos (`aitime`), token count swing 36–83 |

Temperature is a sampling knob on the same logits, not a separate “creativity mode.” Style-sensitive prompts show variance; tight factual prompts often look similar across temperatures.

## Top-p (`--top-p` / nucleus sampling)

Float in `(0, 1]`. After temperature scaling, keep the smallest set of tokens whose cumulative probability ≥ `top_p`, then sample from that set.

- `1.0`: no nucleus truncation (full distribution, still shaped by temperature)
- `0.9`: drop the long tail; often stabler than raising temperature alone

**Lab:** held `top_p=0.9` fixed so temperature was the only sampling variable.

## Max tokens (`--max-tokens` / Ollama `num_predict`)

Hard cap on new tokens. Protects latency and local wait time. **Lab:** fixed at `200` for every row in the variance table.

## Streaming (`--stream`)

Controls **delivery**, not sampling.

| Mode | Behaviour |
|---|---|
| Off | Wait for the full completion; print once |
| On | Print each chunk as it arrives |

This client streams Ollama **NDJSON** lines from `/api/chat` (`stream: true`). Open the connection, decode each event, flush text, stop when `done` is true (usage fields live on that final event).

**Lab:** `--stream` at temperature `1.0` still produced a *new* variant versus the non-stream `1.0` run. Streaming changed how text appeared, not the fact that high temperature samples differently each call.

## Task (completed locally)

1. Client with `argparse`, `time`, `requests`: `src/local/llm_client.py`
2. Flags: `--temperature`, `--stream`, plus fixed `--max-tokens` and `--top-p`
3. High-sensitivity poetic prompt (attic key)
4. Variance table across `0`, `0.5`, `1.0`, then explorative `1.5`–`3.0` (see [day4.md](./day4.md))

### Prompt

```text
Write a single sentence describing a mysterious old key found in an attic, using highly poetic imagery.

### Commands

python src/local/llm_client.py --temperature 0
python src/local/llm_client.py --temperature 0.5
python src/local/llm_client.py --temperature 1.0
python src/local/llm_client.py --temperature 1.0 --stream
python src/local/llm_client.py --temperature 1.5
python src/local/llm_client.py --temperature 2.0
python src/local/llm_client.py --temperature 2.5
python src/local/llm_client.py --temperature 3.0


### Results  
    
    Full table and quotes: [day4.md](./day4.md)
    
    Band	                Finding
    0.0                     Deterministic for this stack and prompt
    0.5–1.0                 Useful stylistic variance; brief still held
    1.5+                    Variance rises; reliability falls (EN/ZH bleed, nonsense tokens)
    Latency                 Cold load_ms (~3 s) is not a temperature effect; warm runs ~1.7–2.5 s


### Observation

    At temperature 0, three successive calls matched text and output token count. Raising temperature moved imagery (leaf → finger → metal tongue / gnarled hand) while staying on the attic-key brief until about 1.0. Beyond that, “more creative” sampling produced language mixing and typos, so product-facing copy should stay low-to-mid temperature. Separate load, prompt eval, and generation when reading wall clocks. Streaming is orthogonal to sampling.

    




