# llm-cli

Week 1 Day 6: `chat --provider direct|bedrock` with streaming and running token/cost totals.

```bash
# from repo root; streaming is always on
PYTHONPATH=src python -m llm_cli chat --provider direct
PYTHONPATH=src python -m llm_cli chat --provider bedrock
```