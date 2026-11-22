
---

### Paste-ready `notes/week04/day_24/day24_notes.md`

```markdown
# Day 24 notes: cache keys, fallback, inference profiles

## Safe cache key

Include everything that changes the answer:

`sha256(prompt_version | model | messages_json | temperature | max_tokens)`

Optional: provider. Do **not** key only on the user string.

## When caching is wrong

- `temperature > 0` (non-deterministic) unless you accept sticky creative answers
- Personal / PII / tenant-specific prompts without tenant in the key
- Streaming mid-flight (partial tokens)
- Tools / side effects (booking, writes)
- Rapidly changing ground truth (prices, stock)

Safe default for Day 24: cache only when `temperature == 0`.

## Fallback vs inference profiles

- **Fallback (gateway):** after N throttles on primary, call a cheaper model (`BEDROCK_FALLBACK_MODEL` / `OLLAMA_FALLBACK_MODEL`).
- **Inference profiles (Bedrock):** pass a profile ID/ARN as `modelId` to route / attribute cost. You already use a geo-style ID (`eu.amazon.nova-micro-v1:0`). Cross-Region profiles add capacity; your AWS project is single-Region for most resources, so treat CRIS as theory + use local model fallback in code today.

## Metrics line

One structured log per `/chat` request:

`cache_hit=false model_used=qwen2.5:7b fallback=false`