# Day 28 lab log: ship + review + exam hour

**Syllabus:** Day 28 · Sun 22 Nov 2026 · Ship + review + exam hour  
**Time:** 2 h (40m README · 40m Skill Builder Bedrock APIs · 20m exam-map · 20m review + budget)  
**Deliverable:** Tag `gateway-v1.0`; Phase 1 done; idle stack destroyed or desired count = 0  
**Depends on:** Day 27 deploy path · [ADR-001](../../../docs/adr-001-deploy-target.md)  
**Gateway docs:** [src/gateway/readme.md](../../../src/gateway/readme.md) · [infra/gateway/readme.md](../../../infra/gateway/readme.md)  
**Theory:** [day28_notes.md](./day28_notes.md)  
**Free resources:** [Skill Builder: Building GenAI apps on Bedrock](https://explore.skillbuilder.aws/) · [MLA-C02 exam guide](https://docs.aws.amazon.com/pdfs/machine-learning/latest/mla-c02-ug/mla-c02.pdf) · [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)

## Task status

- [x] README: features, how to run, architecture diagram, latency/cost numbers
- [x] Record gateway **p95 latency** and **cost per 1k requests** (check yourself)
- [ ] Skill Builder: Bedrock APIs module (40m) — complete offline
- [x] Exam-map notes: **3.1.7**, **3.3**, **4.3.8**
- [x] Confirm budget / spend limit has not fired
- [x] Tag `gateway-v1.0`
- [x] Destroy or scale gateway stack to zero — n/a (no ECS service; OIDC pending root)
- [x] Note Day 27 blocker: OIDC/IAM bootstrap requires root (`CreateOpenIDConnectProvider` denied for IAM user)
- [x] Ship evidence: Docker `gateway:day27` + Bedrock SSE smoke + workflow/bootstrap scripts in repo
- [x] Self-check answered below

## Check yourself

**What is your gateway’s p95 latency and cost per 1k requests?**

> p95 latency: **305 ms**  
> Cost / 1k requests: **~$0.00160 USD**  
> Method: 20 × `POST /chat` with Nova Micro (`eu.amazon.nova-micro-v1:0`), unique prompts; p95 of `usage.latency_ms`; cost from mean tokens × EU CRIS rates (~$0.046 / 1M in, ~$0.184 / 1M out, LiteLLM Nov 2026)

## README checklist (40m)

Ship these in `src/gateway/readme.md` (and link from root README if useful):

| Section | Content |
|---|---|
| Features | SSE stream, Ollama + Bedrock adapters, Redis cache (soft-fail), retries/fallback, idempotency key on non-stream |
| How to run | Local uvicorn / Docker; env vars (`LLM_PROVIDER`, region, models) |
| Deploy | OIDC → ECR → ECS Fargate ARM; tear-down command |
| Diagram | Mermaid in README (CI → ECR → Fargate → Bedrock) |
| Numbers | p95 latency; $/1k requests; model id used |

## Exam-map (20m)

| Task | One-line from this week |
|---|---|
| **3.1.7** FM hosting / resource allocation | ECS Fargate task for streaming gateway vs Lambda cold-start trade-off (ADR-001) |
| **3.3** CI/CD | GitHub Actions + OIDC → ECR push → ECS service update; no long-lived keys in CI |
| **4.3.8** Credential types | GitHub OIDC role assumption for deploy; IAM user / profile for local; task role for Bedrock at runtime |

## Budget review (20m)

```bash
# Confirm caller and budgets (root or budgets-read principal)
bash infra/iam-setup/scripts/auth.sh whoami
bash infra/iam-setup/scripts/iam-budgets.sh
# AWS Settings → Billing: spend limit not tripped
```

## Tag + tear-down

```bash
# After README + numbers are in place
git tag -a gateway-v1.0 -m "Phase 1: LLM gateway (local/Docker ship; ECS pending root OIDC)"
git push origin gateway-v1.0

# Stop idle Fargate billing (only if service exists)
aws ecs update-service --cluster gateway --service gateway --desired-count 0 \
  --region eu-north-1 --profile agent-toolkit
```

## Results

| Item | Value |
|---|---|
| Tag | `gateway-v1.0` |
| p95 latency (ms) | 305 |
| Cost / 1k req (USD) | ~0.00160 |
| Model | `eu.amazon.nova-micro-v1:0` (default) |
| Stack state | n/a — no ECS service (OIDC pending root) |
| Budget alarm | CLI `budgets:ViewBudget` denied for IAM user; confirm spend limit in AWS Settings → Billing (2026-11-22) |
