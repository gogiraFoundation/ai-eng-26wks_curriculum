# Day 6 lab log: two-backend CLI chatbot

**Deliverable:** `llm-cli chat --provider bedrock|direct` with streaming and a running token/cost total  
**Package:** `src/llm_cli/` (`PYTHONPATH=src .venv/bin/python -m llm_cli chat …`)  
**Models:** `direct` → `qwen2.5:7b` (Ollama); `bedrock` → `eu.amazon.nova-micro-v1:0`  
**Defaults held:** `temperature=0.0`, `top_p=0.9`, `max_tokens=200`  
**Caller (Bedrock):** `arn:aws:iam::767397880814:user/afrotyche@gmail.com`  
**Theory:** [day6_notes.md](./day6_notes.md)

## Task status

- [x] `direct` provider: stream + usage from final Ollama NDJSON event
- [x] Multi-turn chat loop with message history (`/clear`, `/exit`)
- [x] Running session token/cost totals after each turn
- [x] CLI flags: `--provider`, `--temperature`, `--top-p`, `--max-tokens` (stream always on)
- [x] `__main__.py` so `python -m llm_cli` works
- [x] `bedrock` provider live smoke (`converse_stream`; IAM user + CRT; former `Error 002` cleared)

## Results summary

| Provider | Stream | Turns logged | Session in | Session out | Session cost USD | Notes |
|---|:---:|---:|---:|---:|---:|---|
| `direct` | yes | 3 (fresh session) | 164 | 89 | 0.000000 | See table below; earlier long session reached in=967 out=615 |
| `bedrock` | yes | 2 | 121 | 107 | 0.000019 | Nova Micro EU profile; cost from `config.py` rates |

### Direct session (fresh process)

| Turn | User (abbrev.) | in | out | latency_ms | Notes |
|---:|---|---:|---:|---:|---|
| 1 | HI | 21 | 10 | 660 | Stream OK |
| 2 | WHAT IS YOUR NAME? | 45 | 37 | 1805 | Persona from system prompt |
| 3 | What stack were you built on? | 98 | 42 | 2152 | Invented “Anthropic” |

Sample direct footers:

```text
[turn] in=45 out=37 cost_usd=0.000000 latency_ms=1805
[session] in=66 out=47 cost_usd=0.000000
```

### Bedrock session (IAM user)

| Turn | User (abbrev.) | in | out | latency_ms | cost_usd | Notes |
|---:|---|---:|---:|---:|---:|---|
| 1 | what is your model? | 12 | 74 | 539 | 0.000011 | Amazon/Nova-style reply |
| 2 | Day 4 attic-key prompt | 109 | 33 | 408 | 0.000008 | Single poetic sentence; history raised `in` |

Sample Bedrock footers:

```text
[turn] in=12 out=74 cost_usd=0.000011 latency_ms=539
[session] in=12 out=74 cost_usd=0.000011

[turn] in=109 out=33 cost_usd=0.000008 latency_ms=408
[session] in=121 out=107 cost_usd=0.000019
```

## Observation

- Both providers stream and reconcile usage; session totals accumulate across turns.
- `direct` cost stays `0`; Bedrock cost is non-zero and rises with the session.
- Bedrock needed `botocore[crt]` for `aws login` credentials; use `.venv/bin/python` so CRT is found.
- Unset / remove `AWS_BEARER_TOKEN_BEDROCK` so profile auth wins.
- Local model still hallucinates identity; Bedrock names Amazon. Optional: tighten system prompt with the real model id.
- `Error 002` is obsolete for this account after the successful smoke.
- `PYTHONPATH=src` is required until the package is installed editable; `__main__.py` is required for `python -m llm_cli`.

## Commands used

```bash
# direct (Ollama must be up)
PYTHONPATH=src .venv/bin/python -m llm_cli chat --provider direct

# bedrock (after aws login as IAM user)
unset AWS_BEARER_TOKEN_BEDROCK
PYTHONPATH=src .venv/bin/python -m llm_cli chat --provider bedrock
```
