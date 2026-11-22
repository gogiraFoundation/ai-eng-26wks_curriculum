# Day 24 lab log: caching and fallback models

**Syllabus:** Day 24 · Wed 18 Nov 2026 · Caching and fallback models  
**Time:** 75 min (20m Redis + inference profiles · 40m cache + fallback · 15m hit-rate log)  
**Deliverable:** `docker-compose` Redis; cache key `hash(prompt_version, model, input)`; metrics: `cache_hit`, `model_used`, `fallback`  
**Code:** `src/gateway/cache.py`, extend `main.py` `/chat`; `docker-compose.yml`  
**Theory:** [day24_notes.md](./day24_notes.md)  
**Free resources:** [Redis strings](https://redis.io/docs/latest/develop/data-types/strings/) · [Inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) · [Intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html)

## Task status

- [ ] Read Redis TTL + Bedrock inference profiles
- [ ] `docker compose up -d redis`
- [ ] `cache.py`: key = hash(prompt_version, model, messages, temperature, max_tokens); TTL 3600
- [ ] Fallback model after repeated throttling on `/chat`
- [ ] Log metrics line: `cache_hit=… model_used=… fallback=…`
- [ ] Self-check: safe cache key; when caching is wrong

## Defaults (this project)

| Role | Model |
|---|---|
| Primary (Bedrock) | `eu.amazon.nova-micro-v1:0` |
| Fallback (cheaper / local) | Ollama `qwen2.5:0.5b` or keep Micro and fall back provider→ollama |
| Cache TTL | 3600 s |
| Cache only when | `temperature == 0` |

## Commands

```bash
docker compose up -d redis
.venv/bin/python -m pip install redis
REDIS_URL=redis://127.0.0.1:6379/0 \
LLM_PROVIDER=ollama \
PYTHONPATH=src .venv/bin/uvicorn gateway.main:app --reload --port 8000

# miss then hit
curl -s -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Say hello in five words."}],"temperature":0}'

curl -s -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Say hello in five words."}],"temperature":0}'