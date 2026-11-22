# Day 25 lab log: containerise and pick a deploy target

**Syllabus:** Day 25 · Thu 19 Nov 2026 · Containerise and pick a deployment target  
**Time:** 75 min (20m Docker refresh · 30m multi-stage Dockerfile · 25m ADR)  
**Deliverable:** `Dockerfile` (non-root) + `docs/adr-001-deploy-target.md`  
**Theory:** [day25_notes.md](./day25_notes.md)  
**Free resources:** [Docker Get started](https://docs.docker.com/get-started/) · [ECS developer guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html) · [Lambda developer guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)  
**Note:** Nothing today depends on Bedrock. Deploy on Day 27.

## Task status

- [ ] Docker Get started refresh
- [ ] Multi-stage `Dockerfile` + `.dockerignore`; run as non-root
- [ ] Local smoke: `docker build` + `docker run` (Ollama via `host.docker.internal`)
- [ ] ADR: ECS Fargate vs Lambda (streaming, cold start, idle cost)
- [ ] Self-check: when Lambda is a poor fit for streaming LLM responses

## Platform notes

- Default image arch is **ARM64** → matches Graviton on ECS.
- For x86-only targets: `docker buildx build --platform linux/amd64 …`
- From container → Ollama on Mac: `OLLAMA_URL=http://host.docker.internal:11434/api/chat`

## Commands

```bash
# start Docker Desktop first if docker.sock was missing
docker compose up -d redis

docker build -t gateway:day25 .
docker run --rm -p 8000:8000 \
  -e LLM_PROVIDER=ollama \
  -e OLLAMA_URL=http://host.docker.internal:11434/api/chat \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  gateway:day25

curl -s http://127.0.0.1:8000/health