
---

### Paste-ready `notes/week04/day_25/day25_notes.md`

```markdown
# Day 25 notes: containers + deploy target

## Self-check: when is Lambda a poor fit for streaming LLM responses?

- **Long-lived SSE:** clients hold a connection while tokens arrive; Lambda bills for the full duration, has a 15 min max, and disconnect edge-cases are awkward.
- **Python SSE:** native response streaming is first-class on Node; Python needs a custom runtime or **Lambda Web Adapter**, not plain FastAPI/uvicorn.
- **Cold start:** first token latency spikes after idle; bad for interactive chat TTFB.
- **Sidecars / Redis:** Fargate co-locates Redis (or ElastiCache) more naturally; Lambda wants managed Redis outside the function.
- **Idle study project:** Lambda wins on *idle* cost (pay per invoke). Fargate wins on *streaming fit*. For Week 4, prefer Fargate and **tear down / scale to zero** after smoke tests.

## Decision summary (for ADR)

| | ECS Fargate | Lambda |
|---|---|---|
| FastAPI + uvicorn SSE | Natural | Needs Web Adapter / custom runtime |
| Cold start | Low once warm task | Higher after idle |
| Idle cost | Task bills while running | ~£0 idle |
| Redis | Sidecar or ElastiCache | External only |
| Study budget | Tear down after Day 27 | Cheaper idle, worse SSE shape |

**Choose:** ECS Fargate (ARM/Graviton) for the gateway; destroy the service when not testing.