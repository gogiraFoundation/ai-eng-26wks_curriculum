# Day 6 lab log: two-backend CLI chatbot

**Deliverable:** `llm-cli chat --provider bedrock|direct` with streaming and a running token/cost total  
**Package:** `src/llm_cli/` (`PYTHONPATH=src python -m llm_cli chat …`)  
**Models:** `direct` → `qwen2.5:7b` (Ollama); `bedrock` → `eu.amazon.nova-micro-v1:0` (blocked by `Error 002`)  
**Defaults held:** `temperature=0.0`, `top_p=0.9`, `max_tokens=200`, `keep_alive=10m`  
**Theory:** [day6_notes.md](./day6_notes.md)

## Task status

- [x] `direct` provider: stream + usage from final Ollama NDJSON event
- [x] Multi-turn chat loop with message history (`/clear`, `/exit`)
- [x] Running session token/cost totals after each turn
- [x] CLI flags: `--provider`, `--temperature`, `--top-p`, `--max-tokens`, `--stream`
- [x] `__main__.py` so `python -m llm_cli` works
- [ ] `bedrock` provider live smoke (`converse_stream`; may fail until Support clears entitlement)

## Results summary

| Provider | Stream | Turns logged | Session in | Session out | Session cost USD | Notes |
|---|:---:|---:|---:|---:|---:|---|
| `direct` | yes | 3 (fresh session) | 164 | 89 | 0.000000 | End of table below; earlier long session before Ctrl+C reached in=967 out=615 |
| `bedrock` | — | 0 | — | — | — | Not run; account still returns `Error 002` |

### Direct session (fresh process)

| Turn | User (abbrev.) | in | out | latency_ms | Notes |
|---:|---|---:|---:|---:|---|
| 1 | HI | 21 | 10 | 660 | Stream OK |
| 2 | WHAT IS YOUR NAME? | 45 | 37 | 1805 | Persona from system prompt (“CLI assistant”) |
| 3 | What stack were you built on? | 98 | 42 | 2152 | Model invented “Anthropic AI platform” |

Footer format observed:

```text
[turn] in=45 out=37 cost_usd=0.000000 latency_ms=1805
[session] in=66 out=47 cost_usd=0.000000
```

On Ctrl+C / `/exit`:

```text
session total: in=… out=… cost_usd=…
```

## Observation

- `PYTHONPATH=src` is required until the package is installed editable; bare `python -m llm_cli` failed with `No module named llm_cli`.
- Missing `__main__.py` first caused: `No module named llm_cli.__main__`; rename/add fixed it.
- `cost_usd=0` for `direct` is correct.
- Turn `in` rises across turns (21 → 45 → 98): history is accumulating.
- Several longer answers hit `out=200` (default `max_tokens`); raise with `--max-tokens` if needed.
- Session counters reset on process restart; use `/clear` inside chat to reset without quitting.
- Small local model + vague system prompt → identity hallucinations; metrics path is still correct.
- Bedrock path not exercised live while the account returns `Error 002`.

## Commands used

```bash
# from repo root; Ollama must be up for direct
ollama serve   # separate terminal if needed

# failed: package not on PYTHONPATH
python -m llm_cli chat --provider direct --stream

# failed until __main__.py existed
PYTHONPATH=src python -m llm_cli chat --provider direct --stream

# success
PYTHONPATH=src python -m llm_cli chat --provider direct --stream

# when Bedrock works
PYTHONPATH=src python -m llm_cli chat --provider bedrock --stream
```

Do not use Day 4 temperature-sweep commands as the Day 6 proof; this lab is multi-turn streaming + running totals.