# MLA-C02 exam map

Source: [AWS Certified Machine Learning Engineer – Associate (MLA-C02) exam guide](https://docs.aws.amazon.com/pdfs/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02.pdf). Weights are the share of scored questions. Fill the Week column each Sunday.

| Domain | Weight | Week |
| --- | ---: | --- |
| 1. Data Preparation for ML and AI | 28% | |
| 2. ML Model and Foundation Model (FM) Development | 24% | Week 1: Bedrock Converse, sampling, streaming CLI. Week 2: task-specific extract prompt + schema (2.2.8). Week 3: system / few-shot / CoT trade-offs |
| 3. Deployment and Orchestration of ML and AI Workflows | 24% | Week 2: recorded prompt tests + GitHub Actions pytest (3.3.9). Week 3: Prompt Management versioning (3.3.7). Week 4: Fargate ADR + OIDC deploy workflow (3.1.7, 3.3) |
| 4. Operating, Monitoring, and Securing ML and AI Solutions | 24% | Week 1: budgets, least-privilege IAM, session teardown. Week 3: token cost/latency harness + caching (4.2.9, 4.2.10). Week 4: credential types local / OIDC / task role (4.3.8) |

## Week 2 skills

| Skill | Statement (MLA-C02) | Evidence |
| --- | --- | --- |
| 2.2.8 | Apply customisation techniques for AI solutions (e.g. task-specific prompt engineering, fine-tuning) | Invoice JSON Schema / Pydantic (`extra=forbid`); extract contract; one repair turn for valid JSON |
| 3.3.9 | Implement AI model testing frameworks, including prompt testing | 15 `recorded/` vs `expected/`; field accuracy; retry unit tests; CI `pytest` with no live LLM |

## Week 3 skills

| Skill | Statement (MLA-C02) | Evidence |
| --- | --- | --- |
| 3.3.7 | Manage prompts (e.g. Amazon Bedrock Prompt Management) | YAML `extract/v1`–`v3`; Prompt Management `Q080HSE5OV:1` / `:2`; loader by name+version; rollback via ARN |
| 4.2.9 | Manage FM inference costs with usage optimisation | Day 20 3×2 harness; ship Micro over Lite; Day 17 cache cut cost/1k ~53% |
| 4.2.10 | Monitor AI-specific cost patterns (e.g. token usage optimisation, embedding costs, vector DB storage) | Converse usage → CSV (`input` / `output` / `cache_*` / `latency` / `cost_usd`); `reports/prompt-cost-latency.md` |

## Week 4 skills

| Skill | Statement (MLA-C02) | Evidence |
| --- | --- | --- |
| 3.1.7 | FM hosting / resource allocation | ADR-001: Fargate for SSE vs Lambda; Docker ARM → Graviton; Day 28 p95 ~305 ms on Nova Micro |
| 3.3 | CI/CD for AI solutions | `deploy-gateway.yml` OIDC → ECR → ECS; pytest gate; `infra/gateway/bootstrap-*.sh` |
| 4.3.8 | Credential types | Local `aws login` profile; GitHub OIDC deploy role; ECS task role (no keys in image); Day 28 notes |

## Skill Builder

| When | Course | Notes |
| --- | --- | --- |
| Day 14 | [Foundations of Prompt Engineering](https://skillbuilder.aws/learn/VF6H4SZ1BU/foundations-of-prompt-engineering) (first half) | FM basics, prompt essentials, zero-/few-shot → invoice extract |
| Day 21 | Same course (second half) | Advanced techniques, misuse/bias; log bullets in `notes/week03/day_21/` |
| Day 28 | Building Generative AI Applications Using Amazon Bedrock (APIs module) | Offline; Bedrock Converse/ConverseStream already used in gateway |