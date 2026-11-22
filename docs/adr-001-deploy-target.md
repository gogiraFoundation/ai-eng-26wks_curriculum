# ADR-001: Deploy target for the LLM gateway

**Status:** Accepted  
**Date:** 2026-11-19 (Day 25)  
**Context:** Week 4 gateway serves FastAPI SSE (`/chat/stream`) and buffered `/chat` with Redis cache. Traffic is study/demo (low RPS). Region: `eu-north-1`. Host arch: Apple Silicon → prefer ARM64 / Graviton.

## Options

### A — Amazon ECS on AWS Fargate
- Run the container as a long-lived task behind an ALB (or public IP for lab).
- SSE over normal HTTP works like local uvicorn.
- Idle cost: task CPU/memory billed while the service desired count > 0.
- Cold start: image pull + task start (mitigate with min tasks = 0 when not studying).

### B — AWS Lambda
- Pay per invoke; near-zero idle cost.
- Response streaming exists, but native path is Node; Python needs Lambda Web Adapter or a custom runtime.
- 15-minute max; cold starts hurt first-token latency; Redis is external-only.
- Function URLs can stream; API Gateway historically buffered (newer proxy streaming exists but adds complexity).

## Decision

**ECS Fargate (ARM64 / Graviton)** for the production-shaped gateway.

## Reasons

1. Matches the Day 22–24 shape: FastAPI + uvicorn + SSE without a Lambda adapter layer.
2. Predictable long-lived streams (Bedrock/Ollama token sessions) without fighting invoke timeouts as the primary design constraint.
3. Redis (`docker compose` locally; ElastiCache or sidecar later) fits the container model.
4. M4 local builds align with Graviton (no forced `amd64` unless a dependency requires it).
5. Study cost controlled by **desired count = 0 / tear down after Day 27 smoke**, not by choosing a worse runtime.

## Consequences

- Must add ECR + task definition + (minimal) networking on Day 27.
- Must remember to stop/scale to zero; Fargate idle is not free.
- Lambda remains a valid pattern for short non-streaming `/chat` workers later; not the primary SSE edge.

## Self-check answer

Lambda is a poor fit when you need long-lived Python SSE, low TTFB after idle, co-located Redis, or streams that may approach the 15-minute limit. Prefer Fargate (or another always-on container) for that shape; use Lambda when idle cost dominates and responses are short or non-streaming.