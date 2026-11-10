# Day 4 lab log: temperature variance (local Ollama)

**Script:** `src/local/llm_client.py`  
**Model:** `qwen2.5:7b`  
**Prompt:** Write a single sentence describing a mysterious old key found in an attic, using highly poetic imagery.  
**Held constant:** `top_p=0.9`, `max_tokens=200`, `keep_alive=10m`  
**Theory:** see [day4_notes.md](./day4_notes.md)

## Task status

- [x] `--temperature` and `--stream` flags
- [x] Variance table across temperatures
- [x] Streaming smoke test at temperature 1.0
- [ ] Repeat on Bedrock Converse when `Error 002` clears

## Results summary

    | Temp | Run | Stream | Imagery / quirk | Out tok | Load ms | Client ms |
    |---:|---:|:---:|---|---:|---:|---:|
    | 0.0 | 1 | no | ghostly leaf (cold start) | 37 | 3831 | 6057 |
    | 0.0 | 2 | no | ghostly leaf (identical) | 37 | 1 | 1719 |
    | 0.0 | 3 | no | ghostly leaf (identical) | 37 | 2 | 1792 |
    | 0.5 | 1 | no | ghostly finger | 40 | 4 | 1883 |
    | 1.0 | 1 | no | metal tongue; velvet hands of time | 39 | 2 | 1824 |
    | 1.0 | 2 | yes | gnarled key; ghostly hand | 44 | 2 | 2114 |
    | 1.5 | 1 | no | silver heart; time's gnarled teeth (cold-ish load) | 43 | 3094 | 5316 |
    | 1.5 | 2 | no | English then sudden Chinese mid-answer | 83 | 4 | 3821 |
    | 1.5 | 3 | no | ghostly crescent moon | 36 | 2 | 1653 |
    | 2.0 | 1 | no | silent leaf on a breathless gust | 53 | 1 | 2423 |
    | 2.0 | 2 | no | shadowed specter; gnarled bow | 43 | 1 | 1975 |
    | 2.5 | 1 | no | tarnished whisper of silver; vines of lore | 54 | 1 | 2471 |
    | 2.5 | 2 | no | ghostly finger reaching through the years | 42 | 2 | 1929 |
    | 3.0 | 1 | no | tarnished tongue; secret gardens | 41 | 2 | 1887 |
    | 3.0 | 2 | no | English/Chinese mix (`gnarled指纹们…`) | 61 | 1 | 2783 |
    | 3.0 | 3 | no | rusty whisper; typo `aitime` | 43 | 2 | 1976 |

Full answer texts for selected runs are below where useful; the table is the Day 4 deliverable.

### Temperature 0 (deterministic)

All three runs (after the first warm pair) used the same sentence:

> In the musty attic, a key hung like a ghostly leaf, its tarnished surface whispering secrets of long-forgotten doors and the shadows that lingered within.

### Temperature 0.5

> In the musty attic, a weathered key dangled like a ghostly finger, its tarnished surface whispering secrets of long-forgotten doors and the shadows that lingered within.

### Temperature 1.0 (non-stream)

> In the musty embrace of an attic's shadows, a key dangles limply, its ancient metal tongue whispering secrets of doors long silenced by the damp, velvet hands of time.

### Temperature 1.0 (`--stream`)

> In the musty attic, a gnarled key lingered like a ghostly hand, its tarnished surface whispering tales of doors long closed and secrets softly locked away in the shadowed embrace of time.

### High temperature failure modes (1.5–3.0)

At `1.5` and `3.0`, some runs left English and injected Chinese mid-sentence, or produced near-nonsense (`aitime`). Output token counts also swung more (36–83). Higher temperature increased variance and reduced reliability for a constrained English one-liner.

## Observation

1. **Temperature 0:** three matching answers and matching output token counts → near-deterministic sampling for this prompt and stack.
2. **0.5 → 1.0:** imagery changes while the attic-key brief still holds (leaf → finger → metal tongue / gnarled hand).
3. **1.5+:** variance keeps rising, but quality collapses: language mixing, typos, looser one-sentence discipline. For product copy, prefer low-to-mid temperature even if high temperature “sounds more creative.”
4. **Latency:** cold `load_ms` (~3 s) dominates early runs. Warm runs cluster near `1.7`–`2.5` s client elapsed; do not attribute Call-1 wall time to temperature.
5. **Streaming:** at temperature 1.0, `--stream` only changes delivery; sampling still produces a new variant.

## Commands used

```bash
python src/local/llm_client.py --temperature 0
python src/local/llm_client.py --temperature 0.5
python src/local/llm_client.py --temperature 1.0
python src/local/llm_client.py --temperature 1.0 --stream
python src/local/llm_client.py --temperature 1.5
python src/local/llm_client.py --temperature 2.0
python src/local/llm_client.py --temperature 2.5
python src/local/llm_client.py --temperature 3.0